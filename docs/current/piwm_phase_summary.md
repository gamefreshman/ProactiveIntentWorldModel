# PIWM 阶段总结：数据、训练与 World Model

更新：2026-05-08
读者：项目成员、导师、非工程合作者

---

## 0. 当前阶段速览

我们已经做完一条端到端的数据 + 训练管线：

- **数据**：72 条 source-linked 销售规则 → 受控 Kling 视频 → 3 帧关键画面 → 多任务 JSONL → 共 **3339** 条 SFT 样本
- **训练**：Qwen2.5-VL-7B-Instruct + ms-swift + LoRA SFT，最新有效 checkpoint 为 **step 834 / epoch 2.0 / loss 0.00082 / token_acc 0.9992**
- **World Model**：44 条 continuation 视频 + 84 条 Future Verification 样本，用于验证“动作之后顾客是否会出现符合预期的未来反应”

模型训练目标不是只输出一个状态标签，而是学习：

```text
多帧顾客观察
→ 视觉状态描述
→ 顾客购买阶段和心理状态
→ 候选导购动作
→ 具体导购动作和话术
→ 不同动作导致的下一状态 / 风险 / 收益 / 奖励 / 可见反应
```

PIWM 当前不生成未来视频。World Model 输出的是结构化未来判断。

---

## 1. 数据怎么来的

### 1.1 标签源头：72 条 source-linked 规则

我们不做“看一帧人工写一个标签”。当前标签主要由两类知识来源派生：

| 来源 | 支撑什么 | 代表来源 |
|---|---|---|
| 销售/营销理论 | 销售阶段、视觉线索、导购策略、动作后果 | AIDA、SPIN Selling、Personal Selling、消费者购买决策、非语言沟通 |
| Agent 建模 | belief / desire / intention 字段格式，World Model 任务形式 | BDI agents、World Model、preference learning |

规则覆盖度：

| 项 | 数量 |
|---|---:|
| 规则总数 | 72 |
| 已链接来源 | 72 |
| `manual_supported` | 32 |
| `theory_anchored` | 40 |
| `expert_reviewed` | 0 |

当前对外措辞必须谨慎：规则是 **source-linked seed rules**，有理论/教材来源锚点，但还没有销售专家逐条最终审定。

### 1.2 规则的六种用途

| 类型 | 数量 | 作用 | 例子 |
|---|---:|---|---|
| `cue_to_state_prior` | 10 | 视觉线索 → 顾客状态 | 长时间看价格 → 高犹豫 |
| `persona_state_to_intent` | 14 | persona + 状态 → 意图 | 价格敏感 + 犹豫 → 比较性价比 |
| `state_fallback_intent` | 9 | 无 persona 时的默认意图 | 高犹豫 → 寻求 reassurance |
| `state_to_proactive_score` | 9 | 状态 → 介入强度，旧兼容字段 | 不作为核心解释 |
| `state_aida_to_candidates` | 9 | 状态 + AIDA → 候选动作 | 高犹豫 + desire → 价值对比 / 开放问题 / 等待 / 强推荐 |
| `transition` | 21 | 状态 + 动作 → 下一状态 / 风险 / 收益 / 奖励 | 高犹豫 + 强推荐 → 防御性退缩 |

一条规则链的形态是：

```text
target_cue
→ latent_state
→ candidate_actions
→ best_action
→ next_state_by_action[action]
```

### 1.3 视频生成流程

```text
scenario_sampler → prompt_builder → Kling 10s video → extract_frames K=3
→ qa_gate → archive_loader → exporters → ms-swift JSONL
```

| 步骤 | 产物 | 内容 |
|---|---|---|
| `scenario_sampler` | `scenario_manifest.jsonl` | 从商品、persona、视觉线索、AIDA 阶段、视角中采样受控场景 |
| `prompt_builder` | `prompt.json` | 把场景写成 Kling 视频 prompt |
| Kling | `video.mp4` | 10 秒店内顾客行为视频 |
| `extract_frames` | `frames/000.jpg` 等 | 抽 3 张关键帧 |
| `qa_gate` | `qa_report.json` | 检查文件、标签泄露、物理一致性、视角 |
| `archive_loader` | `MainSchemaRecord` | 合成主数据 |
| `exporters` | 多个 JSONL | 拆成训练任务 |

当前视觉输入不是完整视频，而是：

```text
10 秒视频 → 3 张关键帧
```

K=3 表示一个最小行为片段：

```text
onset / peak / resolution
```

也就是动作开始、关键瞬间、稳定状态。

---

## 2. 当前数据字段：真实样本穿透

下面用真实样本 `piwm_09df40aae2` 说明当前字段到底长什么样。这个样本来自主训练 synthetic split：

```text
商品：jewelry / 珠宝
视角：salesperson_observable / 导购可观察视角
线索：asking_companion_opinion / 向同伴寻求意见
persona：first_time_high_consideration / 首次高考虑购买者
AIDA 阶段：interest
当前状态：active_evaluation
最佳动作：A5_provide_demonstration / 短演示
```

### 2.1 主表字段含义

| 字段 | 真实值 | 含义 |
|---|---|---|
| `state_id` | `piwm_09df40aae2` | 一条顾客场景的唯一 ID |
| `images` | 3 张 frame | 从 10 秒视频抽出的关键帧 |
| `product_category` | `jewelry` | 商品类别 |
| `visual_state` | 三轴视觉描述 | 模型应先描述“顾客看起来怎样” |
| `observable_cues` | `asking_companion_opinion` | 视觉线索标签 |
| `persona` | `first_time_high_consideration` | 顾客类型 |
| `aida_stage` | `interest` | 当前购买阶段 |
| `latent_state` | `active_evaluation` | 当前行为/心理子状态 |
| `bdi` | belief / desire / intention | 顾客心理摘要 |
| `candidate_actions` | A4 / A5 / A1 / A3 | 当前状态下可选导购动作 |
| `best_action` | `A5_provide_demonstration` | 规则选出的最佳动作 |
| `best_action_realization` | 话术 + 动作 + 时机 + 理由 | 让输出从“标签”变成“可执行导购方案” |
| `next_state_by_action` | 每个动作的后果 | World Model 的基础监督 |
| `reward_by_action` | 每个动作的奖励 | 用于排序和 policy preference |
| `provenance` | prompt / rule-derived | 字段来源记录 |

### 2.2 主表真实样本

```json
{
  "state_id": "piwm_09df40aae2",
  "images": [
    {
      "index": 0,
      "relative_path": "Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg",
      "timestamp_sec": null
    },
    {
      "index": 1,
      "relative_path": "Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg",
      "timestamp_sec": null
    },
    {
      "index": 2,
      "relative_path": "Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg",
      "timestamp_sec": null
    }
  ],
  "product_category": "jewelry",
  "split": "train",
  "visual_state": {
    "summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。",
    "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
    "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
    "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。"
  },
  "observable_cues": ["asking_companion_opinion"],
  "viewpoint": "salesperson_observable",
  "persona": {
    "type": "first_time_high_consideration",
    "description": "A first-time buyer considering a higher-stakes purchase and needing reassurance."
  },
  "aida_stage": "interest",
  "latent_state": "active_evaluation",
  "intent": "request_demonstration",
  "bdi": {
    "belief": "A companion's approval may influence whether the choice feels safe.",
    "desire": "see how the product works",
    "intention": "ask for a demonstration"
  },
  "proactive_score": 3,
  "candidate_actions": [
    "A4_open_with_question",
    "A5_provide_demonstration",
    "A1_silent_observe",
    "A3_strong_recommend"
  ],
  "best_action": "A5_provide_demonstration",
  "best_action_realization": {
    "utterance": "我只演示一个最关键的地方：上身比例、光泽变化、扣合方式或证书信息。您看这个细节是不是符合您的使用习惯。",
    "physical_action": "只展示上身比例、光泽变化、扣合方式或证书信息中的一个最相关细节；演示后把观察权交还给顾客，不继续扩展完整卖点。",
    "timing": "顾客主动评估但仍不确定时，提供短演示。",
    "rationale": "顾客在听取同伴意见。短演示能把珠宝的抽象卖点变成可观察体验。"
  }
}
```

这一段说明当前数据已经不是简单的：

```text
label = active_evaluation
```

而是包含：

```text
画面描述
→ 顾客心理
→ 候选动作
→ 最佳动作
→ 具体说什么、做什么、什么时候做
```

### 2.3 同一条样本的动作后果表

同一个当前状态下，4 个候选动作会得到不同后果：

| 动作 | 具体含义 | 下一状态 | 风险 | 收益 | 奖励 | 解释 |
|---|---|---|---|---|---:|---|
| `A4_open_with_question` | 开放式询问 | `engaged_dialogue` | low | high | 0.70 | 低压力获得需求信息 |
| `A5_provide_demonstration` | 短演示 | `engaged_dialogue` | low | high | 0.80 | 最能把珠宝抽象卖点变成可观察体验 |
| `A1_silent_observe` | 继续观察 | `active_evaluation` | low | low | 0.20 | 不打扰，但推动有限 |
| `A3_strong_recommend` | 强推荐 | `defensive_withdrawal` | medium | low | -0.30 | 对仍在评估的顾客可能形成压力 |

真实 `next_state_by_action` 的关键内容：

```json
{
  "A5_provide_demonstration": {
    "next_state": "engaged_dialogue",
    "next_aida_stage": "desire",
    "next_bdi": {
      "belief": "The salesperson may help resolve the decision.",
      "desire": "explore available options",
      "intention": "continue browsing and comparing"
    },
    "reward": 0.8,
    "risk": "low",
    "benefit": "high",
    "rationale": "Rule-derived expectation: A5_provide_demonstration from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.80."
  },
  "A3_strong_recommend": {
    "next_state": "defensive_withdrawal",
    "next_aida_stage": "attention",
    "next_bdi": {
      "belief": "The salesperson may be applying too much pressure.",
      "desire": "avoid further engagement",
      "intention": "leave without buying"
    },
    "reward": -0.3,
    "risk": "medium",
    "benefit": "low",
    "rationale": "Rule-derived expectation: A3_strong_recommend from active_evaluation leads to defensive_withdrawal with medium risk, low benefit, and reward -0.30."
  }
}
```

这就是 World Model 监督的核心：不是只判断当前状态，而是比较动作会如何改变未来状态。

### 2.4 同一条样本导出的训练题

同一个 `main_schema` 会被拆成多种训练视图。

**A. Perception 题：看图判断当前状态**

```json
{
  "state_id": "piwm_09df40aae2",
  "input": {
    "frames": [
      "Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg",
      "Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg",
      "Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"
    ],
    "persona_summary": "first_time_high_consideration: A first-time buyer considering a higher-stakes purchase and needing reassurance.",
    "history_summary": null
  },
  "output": {
    "visual_state": {
      "summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。",
      "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
      "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
      "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。"
    },
    "aida_stage": "interest",
    "state_subtype": "active_evaluation",
    "intent": "request_demonstration",
    "bdi": {
      "belief": "A companion's approval may influence whether the choice feels safe.",
      "desire": "see how the product works",
      "intention": "ask for a demonstration"
    },
    "candidate_actions": [
      "A4_open_with_question",
      "A5_provide_demonstration",
      "A1_silent_observe",
      "A3_strong_recommend"
    ],
    "best_action": "A5_provide_demonstration",
    "best_action_realization": {
      "utterance": "我只演示一个最关键的地方：上身比例、光泽变化、扣合方式或证书信息。您看这个细节是不是符合您的使用习惯。",
      "physical_action": "只展示上身比例、光泽变化、扣合方式或证书信息中的一个最相关细节；演示后把观察权交还给顾客，不继续扩展完整卖点。",
      "timing": "顾客主动评估但仍不确定时，提供短演示。",
      "rationale": "顾客在听取同伴意见。短演示能把珠宝的抽象卖点变成可观察体验。"
    }
  }
}
```

**B. Transition 题：给定动作，预测下一状态**

```json
{
  "state_id": "piwm_09df40aae2#A5_provide_demonstration",
  "input": {
    "frames": [
      "Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg",
      "Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg",
      "Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"
    ],
    "current_state_summary": {
      "aida_stage": "interest",
      "product_category": "jewelry",
      "state_subtype": "active_evaluation",
      "visual_state": {
        "summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。",
        "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
        "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
        "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。"
      },
      "intent": "request_demonstration",
      "bdi": {
        "belief": "A companion's approval may influence whether the choice feels safe.",
        "desire": "see how the product works",
        "intention": "ask for a demonstration"
      }
    },
    "candidate_action": "A5_provide_demonstration",
    "candidate_action_realization": {
      "utterance": "我只演示一个最关键的地方：上身比例、光泽变化、扣合方式或证书信息。您看这个细节是不是符合您的使用习惯。",
      "physical_action": "只展示上身比例、光泽变化、扣合方式或证书信息中的一个最相关细节；演示后把观察权交还给顾客，不继续扩展完整卖点。"
    }
  },
  "output": {
    "next_aida_stage": "desire",
    "next_state": "engaged_dialogue",
    "next_bdi": {
      "belief": "The salesperson may help resolve the decision.",
      "desire": "explore available options",
      "intention": "continue browsing and comparing"
    },
    "risk": "low",
    "benefit": "high",
    "reward": 0.8
  }
}
```

**C. Policy Preference 题：选择更好的动作**

```json
{
  "state_id": "piwm_09df40aae2",
  "chosen": "A5_provide_demonstration",
  "rejected": "A3_strong_recommend",
  "reward_gap": 1.1,
  "chosen_json": {
    "action": "A5_provide_demonstration",
    "action_realization": {
      "utterance": "我只演示一个最关键的地方：上身比例、光泽变化、扣合方式或证书信息。您看这个细节是不是符合您的使用习惯。",
      "physical_action": "只展示上身比例、光泽变化、扣合方式或证书信息中的一个最相关细节；演示后把观察权交还给顾客，不继续扩展完整卖点。",
      "timing": "顾客主动评估但仍不确定时，提供短演示。",
      "rationale": "顾客在听取同伴意见。短演示能把珠宝的抽象卖点变成可观察体验。"
    }
  },
  "rejected_json": {
    "action": "A3_strong_recommend",
    "action_realization": {
      "utterance": "如果您希望我直接给建议，我会优先看这款，因为它在材质、证书、佩戴场景和送礼适配度上更贴近您刚才关注的点。当然您也可以再比较一下。",
      "physical_action": "只指向一个珠宝选项，用一个理由收束选择；说完立刻给顾客退路，避免连续追问。",
      "timing": "只在顾客明确要求推荐或已经接近购买确认时使用；当前若仍犹豫，应谨慎。",
      "rationale": "强推荐能帮助临门决策，但对犹豫或价格敏感状态有较高压迫风险。"
    }
  }
}
```

这三种训练题共同回答：

```text
看见什么？
→ 当前顾客是什么状态？
→ 如果做某个动作，顾客会怎么变？
→ 哪个动作更值得做？
→ 实际导购应该说什么、做什么？
```

---

## 3. 当前数据集规模

| 数据集 | 规模 | 用途 | 性质 |
|---|---:|---|---|
| `PIWM-Train-Synth-v1` | 543 parent / 2554 SFT | 主训练 | synthetic train，未全 QA |
| `PIWM-Eval-QA-v1` | 36 parent / 162 eval | 主评估 | QA 通过子集 |
| `PIWM-WorldModel-v1` | 24 parent / 44 continuation | 视觉证据 | QA 通过 pilot |
| `PIWM-FutureVerification-v1` | 84 rows | 动作-未来匹配 | QA 通过 |
| `PIWM-Train-Full-v2` | 3339 SFT | 最新完整训练入口 | 合成训练 + 多任务 |

数据口径：

- `Train-Synth-v1` 可以训练，但不能说成 QA 通过。
- `Eval-QA-v1` 是当前最干净评估，但只有 36 parent。
- `WorldModel-v1` 是 pilot-scale 视觉证据集，不是主训练规模来源。

---

## 4. 训练

### 4.1 框架与 checkpoint

- **基座**：Qwen2.5-VL-7B-Instruct
- **方法**：ms-swift + LoRA SFT
- **最新 checkpoint**：`full_v2_len8192_8gpu/v0-20260502-193050/checkpoint-834`

| 训练指标 | 值 |
|---|---:|
| step | 834 |
| epoch | 2.0 |
| 最后 loss | 0.00082 |
| 最后 token_acc | 0.9992 |

### 4.2 训练入口与任务构成

入口文件：

```text
data/official/ms_swift/piwm_train_full_v2.jsonl
```

规模：

```text
3339 SFT 样本
10269 张图路径
```

| 任务 | 样本数 | 学什么 |
|---|---:|---|
| `perception` | 567 | 当前帧 → 视觉描述 + AIDA + BDI + 候选动作 + 导购方案 |
| `deliberation` | 2077 | 当前状态 + 某动作 → 下一状态 / 风险 / 收益 / 奖励 |
| `action_selection` | 567 | 候选动作中选最佳 + 输出具体行为话术 |
| `continuation_caption` | 44 | 当前状态 + 动作 → 描述顾客后续反应 |
| `future_verification` | 84 | 判断一组未来画面是否符合该动作的预期后果 |

### 4.3 训练样本格式

ms-swift 训练行长这样：

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "<image><image><image>..."},
    {"role": "assistant", "content": "<stage>...</stage>..."}
  ],
  "images": [".../frames/000.jpg", ".../001.jpg", ".../002.jpg"],
  "task": "perception"
}
```

模型看到的是：

```text
多张图 + 任务说明 → 结构化标签 + 导购输出
```

### 4.4 为什么这样训

模型要学的是一条 6 步决策链，不是单标签分类：

1. 看见什么：`visual_state`
2. 顾客在 AIDA 哪一阶段
3. 顾客的 `belief / desire / intention`
4. 当前合理候选导购动作
5. 最佳动作的具体执行：怎么做、何时做、说什么
6. 不同动作下顾客可能的下一状态

`proactive_score` 在新版数据里是兼容字段，对外解释优先使用：

```text
visual_state + best_action_realization + risk / benefit / reward + visible_reaction
```

---

## 5. World Model

### 5.1 PIWM 里的 World Model 指什么

PIWM 的 World Model 指：

```text
给定当前顾客状态和候选导购动作，预测顾客的下一状态。
```

形式：

```text
o_t 当前观察 + s_t 当前状态 + a 候选动作
→ s_{t+1} 下一状态
```

输出对象是结构化文本，不是视频像素：

```text
next_aida_stage
next_state_subtype
next_bdi
risk
benefit
reward
visible_reaction
```

### 5.2 Transition：文字版未来状态

`transition_modeling.jsonl` 训练的核心对照是：

```text
同一当前状态 + 不同动作 → 不同未来后果
```

以 `piwm_09df40aae2` 为例：

```text
当前状态: active_evaluation

A5_provide_demonstration
→ next: engaged_dialogue
→ risk: low
→ benefit: high
→ reward: +0.80

A3_strong_recommend
→ next: defensive_withdrawal
→ risk: medium
→ benefit: low
→ reward: -0.30
```

这不是“哪个 label 更好看”，而是在训练模型：

```text
如果导购这样介入，顾客接下来更可能怎么变化？
```

### 5.3 Continuation：未来后果的视觉证据

为部分样本生成 5 秒 continuation 视频：

```text
parent video       当前 10 秒顾客状态
├─ best continuation   采取最佳动作后
└─ worst continuation  采取高风险动作后
```

当前规模：

```text
24 parent / 44 continuation
```

这部分不是主训练规模来源，作用是：

```text
QA 审阅未来反应是否合理
把动作后果变成可看的视觉证据
支撑 Future Verification
```

### 5.4 Future Verification：动作-未来匹配判断

这是目前最能体现视觉 World Model 的任务。

输入：

```text
current_frames + candidate_action + continuation_frames
```

输出：

```text
match: yes / no
expected_next_state
visible_reaction
reason
```

正例：

```text
当前: 高犹豫
动作: A3_strong_recommend
未来画面: 顾客后退、收手、视线回避
match: yes
expected_next_state: defensive_withdrawal
```

负例：

```text
当前: 高犹豫
动作: A3_strong_recommend
未来画面: 顾客继续互动、姿态打开
match: no
```

模型要回答：

```text
这段未来画面，是否符合该动作在当前顾客状态下的合理后果？
```

当前规模：

```text
84 行
44 正样本
40 负样本
```

### 5.5 World Model 输出示例

模型最终输出的 World Model 判断长这样：

```json
{
  "next_aida_stage": "attention",
  "next_state_subtype": "defensive_withdrawal",
  "next_bdi": {
    "belief": "The salesperson may be applying too much pressure.",
    "desire": "avoid further engagement",
    "intention": "leave without buying"
  },
  "risk": "medium",
  "benefit": "low",
  "reward": -0.30,
  "visible_reaction": {
    "engagement_pattern_change": "顾客从围绕商品和同伴沟通，转为减少互动或后撤。",
    "gaze_and_attention_change": "视线从商品和同伴反馈中移开，降低继续交流意愿。",
    "body_and_hands_change": "身体不再朝向商品做评估，手部从展示或指向商品的状态收回。"
  }
}
```

---

## 6. 当前阶段成果与边界

### 6.1 已完成

| 模块 | 状态 |
|---|---|
| 数据生成闭环 | scenario → Kling → frames → QA → JSONL 全跑通 |
| 专家规则 | 72 条全部 source-linked |
| 主训练数据 | 543 parent / 2554 SFT |
| QA 评估数据 | 36 parent / 162 eval |
| World Model 视觉证据 | 24 parent / 44 continuation |
| Future Verification | 84 行 |
| 完整训练入口 | 3339 SFT |
| 训练 | ms-swift + Qwen2.5-VL-7B + LoRA，checkpoint-834 |

### 6.2 对外措辞红线

| 不要这样说 | 应该这样说 |
|---|---|
| 所有训练样本都经过人工 QA | 主训练是 synthetic；评估子集和 World Model 子集 QA 通过 |
| 规则已经专家审定 | 规则是 source-linked seed rules，`expert_reviewed=0` |
| PIWM 生成未来视频 | PIWM 预测和验证动作导致的未来状态与可见反应 |
| 主训练数据 = 真实门店数据 | 主训练是合成视频；真实门店数据是后续扩展 |
| 用 `proactive_score` 做主要解释 | 用 `visual_state` + `action realization` + `future reaction` |

### 6.3 已知缺口

- 规则尚未经销售专家逐条审定，`expert_reviewed=0`。
- 主训练数据 543 parent 未全人工 QA。
- 真实门店视频 zero-shot 测试尚未完成。
- Continuation 视觉证据仍是 pilot 规模，24 parent，未扩展到主训练规模。

---

## 7. 一段话给非工程读者

我们把销售经验和营销理论整理成 72 条可审计规则。例如，顾客向同伴寻求意见说明决策受到社交反馈影响；首次购买高考虑商品的顾客通常需要 reassurance；在珠宝柜台，如果顾客正在和同伴确认而不是准备付款，短演示比强推荐更合适。然后我们用这些规则控制 Kling 生成 10 秒店内顾客视频，每段抽 3 帧关键画面，并把画面转成结构化训练数据。模型训练后要做三件事：先描述顾客在画面里做什么，再判断顾客处于什么购买阶段和心理状态，最后给出导购应该怎么做、什么时候做、说什么。World Model 部分进一步让模型预测：如果导购采取某个动作，顾客下一步可能会继续互动、保持犹豫，还是防御性退缩。

---

## 8. 一行结论

PIWM 当前是一条：

```text
pedagogy-anchored rules
→ synthetic videos
→ 3-frame observations
→ compact visual-state / action-realization schema
→ multi-task SFT
→ action-conditioned future prediction
```

的端到端管线。

核心不是视频生成，而是把：

```text
看见什么
→ 顾客什么状态
→ 该不该介入
→ 怎么介入
→ 介入后顾客如何变
```

训练成一个可评估的多模态导购决策模型。
