# PIWM 数据资产与模型对比投入说明

更新时间：2026-05-01 CST

## 1. 一句话结论

PIWM 当前已经不是“只有想法”的阶段：我们已经完成了 **视频生成 -> 抽帧 -> QA gate -> 结构化数据 -> ms-swift SFT -> 多项评估** 的闭环。现有结果显示，经过 PIWM 数据训练后，通用 VLM 可以被训练成一个能稳定输出结构化导购判断、能推演导购动作后果、能验证未来顾客反应的 AI 导购原型。下一步继续投入 OpenRouter 的价值，是用同一套数据和评测协议横向比较更多商用/开源 VLM，找出最适合产品化和论文发表的基座模型。

## 2. 公司视角结论

| 公司关心的问题 | 当前判断 | 依据 | 下一步投入价值 |
|---|---|---|---|
| 这个 AI 导购现在能不能用？ | **可以做受控场景 Demo / POC，不建议直接上线无人值守** | 已能稳定输出结构化判断，Behavior QA set 上状态识别和动作后果推理已明显优于 zero-shot | 扩大 QA-reviewed eval，选择更强基座模型，提高真实场景稳定性 |
| 它是不是只是 prompt demo？ | **不是，已经有数据闭环和训练闭环** | 已完成 260 条 synthetic parent videos、1321 条 SFT examples、QA-reviewed eval、ms-swift LoRA 训练 | 继续投入可以直接扩大数据和做多模型对比，不是从零研发 |
| 有没有科研成果占位价值？ | **有，适合包装成“主动导购 World Model + 合成视频数据闭环 + 未来反应验证”方向** | 已有 action-conditioned transition、continuation videos、Future Verification full84 结果 | 用 OpenRouter 补强模型横评，可形成更完整实验表 |
| 现在最大短板是什么？ | **当前状态识别和候选动作预测仍需提升** | 行为评估集上候选动作约 75%，未来反应集更难 | 需要扩 QA 数据、做模型对比和定向数据增强 |
| 为什么还要投 OpenRouter？ | **为了选模型，而不是验证方向是否存在** | 方向已由 Qwen2.5-VL SFT 跑通；下一步要比较更强 VLM 的上限和成本 | 找到“效果/成本”最优模型，支持产品路线和论文表格 |

## 3. 当前数据资产总览

本文后面统一使用以下展示名称，避免暴露内部目录名：

| 展示名称 | 对应含义 | 内部数据来源 |
|---|---|---|
| High-throughput synthetic train set | 大批量合成训练集，用于 SFT，不写成 QA-pass | `data/piwm_dataset_priority280_unreviewed` |
| Behavior QA set | 人工审阅过的顾客行为评估集，评估当前状态识别和动作后果推理 | `data/piwm_dataset_priority40_qareviewed_sample` |
| Future-reaction QA set | 人工审阅过的未来反应评估集，包含 continuation 视频 | `data/piwm_dataset_pilot30_with_continuations` |
| Future Verification set | 动作与候选未来反应视频是否匹配的验证集 | `future_verification.jsonl` |

| 数据资产 | 当前规模 | 主要内容 | 当前用途 | 对外口径 |
|---|---:|---|---|---|
| High-throughput synthetic train set | 260 parent videos | 多视角店内顾客行为视频、3 帧抽样、规则标签 | 主 SFT 训练 | synthetic train split，未全量人工审阅 |
| QA-reviewed behavior eval set | 40 reviewed / 36 pass | 从主生产数据中分层抽样人工 QA | 可信评估集 | QA-reviewed evaluation sample |
| QA-reviewed future-reaction eval set | 30 reviewed / 24 pass | parent video + best/worst continuation video | World Model / Future Verification | QA-reviewed pilot continuation set |
| Continuation videos | 44 pass | 动作后的未来反应视频，best 21 / worst 23 | 未来反应证据与训练监督 | 可审计 future reaction evidence |
| Future Verification | 84 pairs | 44 positive / 40 negative action-future matching pairs | 验证 future frames 是否真的被模型使用 | pilot-scale world-model verification |
| 当前主 SFT 数据 | 1321 examples / 3963 images | perception + deliberation + continuation caption | ms-swift LoRA 训练 | sprint-scale synthetic SFT |

## 4. 当前训练数据构成

| 来源 | Parent sessions | SFT examples | 任务组成 | 说明 |
|---|---:|---:|---|---|
| High-throughput synthetic train set | 260 | 1187 | perception 260 / deliberation 927 | 主训练数据来源，覆盖产品/人物/视角/动作对照 |
| QA-reviewed future-reaction set | 24 | 134 | perception / deliberation / continuation caption | QA-pass continuation pilot 数据 |
| 当前 combined SFT | 约 284 parent 来源 | 1321 | 多任务混合 SFT | 当前主 checkpoint 使用的数据 |
| Future Verification observed | 24 | 218 | perception 24 / deliberation 66 / continuation 44 / future verification 84 | 单独训练 Future Verification 头 |

## 5. 数据覆盖情况

### 5.1 已生成主训练集：High-throughput synthetic train set

| 维度 | 覆盖 |
|---|---|
| Parent videos | 260 |
| Transition rows | 927 |
| Policy preference rows | 260 |
| 平均候选动作数 | 3.57 / state |
| Action contrast | 260 / 260 有 action contrast |
| Viewpoint | salesperson 192 / surveillance 68 |
| Product categories | 8 类全覆盖 |
| Split | train 199 / dev 8 / test 6 / ood_product 26 / ood_persona 21 |

### 5.2 QA-reviewed 行为评估集：QA-reviewed behavior eval set

| 指标 | 数值 |
|---|---:|
| 人工审阅样本 | 40 |
| QA pass | 36 |
| QA pass rate | 90% |
| Transition rows | 126 |
| Viewpoint | salesperson 18 / surveillance 18 |
| Action contrast | 36 / 36 |

### 5.3 QA-reviewed 未来反应评估集：QA-reviewed future-reaction eval set

| 指标 | 数值 |
|---|---:|
| QA-pass parent | 24 |
| Continuation videos | 44 |
| Best / worst continuation | 21 / 23 |
| Future Verification pairs | 84 |
| Positive / negative pairs | 44 / 40 |
| Negative reward continuations | 12 |

## 6. 当前模型结果

### 6.1 主表：Zero-shot vs PIWM-SFT

为便于阅读，下面使用直观评估集名称：

| 展示名称 | 内部数据来源 | 评估内容 |
|---|---|---|
| Behavior QA set | `data/piwm_dataset_priority40_qareviewed_sample` | 当前顾客状态识别 + 动作后果推理 |
| Future-reaction QA set | `data/piwm_dataset_pilot30_with_continuations` | 当前状态 + continuation 未来反应视频 |

#### 6.1.1 公司可读版：现在有什么突破

| 能力项 | 公司关心的问题 | 原始 Qwen2.5-VL | PIWM-SFT 后 | 提升/含义 |
|---|---|---:|---:|---|
| 稳定按业务格式输出 | 模型回答能不能被系统直接读取，而不是一段散文 | Behavior QA set：23.5% 可解析；Future-reaction QA set：55.2% 可解析 | 两个评估集都是 100% 可解析 | 从“经常不能接系统”变成“稳定可接系统” |
| 看懂顾客当前状态 | 能不能判断顾客处于什么购买阶段、是否值得主动介入、候选动作有哪些 | 原始模型没有稳定结构化字段，难以可靠读取 | Behavior QA set：购买阶段 88.9%，主动分数 75.0%，候选动作 75.0% | 已经能作为导购决策前端，但仍是主要提升空间 |
| 推演导购动作后果 | 给定“当前顾客状态 + 导购动作”，能不能判断下一步风险/收益/reward | Behavior QA set 平均约 26.3%；Future-reaction QA set 平均约 36.7% | Behavior QA set：100%；Future-reaction QA set：平均约 98.9% | 动作后果推理从基本不可用提升到接近稳定可用 |
| 识别未来反应描述 | 能不能按业务协议描述“动作之后顾客会怎样反应” | zero-shot 未能稳定按本项目的结构化协议输出 | Future-reaction QA set：100% | continuation 视频提供的未来反应监督已经被模型学到 |
| 依赖视觉而不是瞎猜 | 模型是不是真的看图，还是只背规则 | 去掉视觉后 Behavior QA set 的 stage/candidates 都降到 11.1% | 带 3 帧时 stage 88.9%、candidates 75.0% | 视觉对“看懂当前顾客”是必要信号 |

一句话解释：

```text
PIWM-SFT 的突破不是单纯把分数调高，而是把通用 VLM 变成了一个可接入业务系统的主动导购模型原型：它能看顾客状态、给出候选导购动作、推演动作风险收益，并利用未来反应视频做验证。
```

#### 6.1.2 技术指标版：论文/工程追溯表

注意：下表里的 Reaction Caption 是严格结构化协议匹配，不是普通自然语言主观评分。zero-shot 如果没有按本项目定义的标签协议输出，会记为未命中；这不等价于“模型语义上完全不会描述顾客反应”。

| Eval set | Rows | Model | Parse | Stage | Score | Candidates | Next Stage | Risk | Benefit | Reward | Reaction Caption |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Future-reaction QA set | 134 | Qwen2.5-VL zero-shot | 0.552 | -- | -- | -- | 0.333 | 0.500 | 0.600 | 0.033 | 未按协议输出 |
| Future-reaction QA set | 134 | PIWM-SFT | 1.000 | 0.417 | 0.792 | 0.333 | 0.985 | 1.000 | 1.000 | 0.970 | 1.000 |
| Behavior QA set | 162 | Qwen2.5-VL zero-shot | 0.235 | -- | -- | -- | 0.211 | 0.553 | 0.289 | 0.000 | -- |
| Behavior QA set | 162 | PIWM-SFT | 1.000 | 0.889 | 0.750 | 0.750 | 1.000 | 1.000 | 1.000 | 1.000 | -- |

技术解读：

- 结构化输出能力从 zero-shot 的不稳定状态提升到 `1.000` parse。
- 规则条件转移和 reward 已经基本站住，Behavior QA set 上 next stage / risk / benefit / reward 均为 `1.000`。
- 当前主要短板是 perception/candidate，不是训练闭环本身。

### 6.2 视觉输入是否真的有用

同一 PIWM-SFT checkpoint，移除视觉帧后：

| Eval set | Condition | Stage | Score | Candidates | Next Stage | Reward |
|---|---|---:|---:|---:|---:|---:|
| Future-reaction QA set | visual 3-frame | 0.417 | 0.792 | 0.333 | 0.985 | 0.970 |
| Future-reaction QA set | no visual frames | 0.333 | 0.042 | 0.042 | 0.955 | 0.970 |
| Behavior QA set | visual 3-frame | 0.889 | 0.750 | 0.750 | 1.000 | 1.000 |
| Behavior QA set | no visual frames | 0.111 | 0.111 | 0.111 | 1.000 | 1.000 |

解读：

- 视觉帧对 perception/candidate 是必要的。
- transition/reward 在 no-image 下仍高，是因为这些任务给定了结构化 state/action，按专家规则本来就是 deterministic。
- 这说明任务拆分是清楚的：视觉主要负责“看懂当前顾客状态”，规则监督负责“给定状态和动作后推演后果”。

### 6.3 为什么默认 K=3 帧

| Frame budget | Rows | Parse | Stage | Score | Candidates |
|---:|---:|---:|---:|---:|---:|
| K=1 | 36 | 1.000 | 0.722 | 0.694 | 0.694 |
| K=3 | 36 | 1.000 | 0.861 | 0.722 | 0.722 |
| K=5 | 36 | 1.000 | 0.861 | 0.722 | 0.722 |

解读：K=3 比单帧明显更好，K=5 没有进一步收益。因此当前 3 帧 onset / peak / resolution 是成本与信息量之间的合理折中。

### 6.4 Future Verification：未来反应视频是否真正进入训练

这个实验单独评估“给模型看当前顾客状态 + 一个动作 + 一段候选未来反应视频，模型能否判断这段未来反应是否匹配该动作后果”。它比 `Future-reaction QA set` 更细：不是让模型选动作，而是验证未来视频是否符合动作条件下的专家预期。

| Input condition | Rows | Parse | Match | Expected State | Body | Gaze | Hand | Movement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current behavior frames + future reaction frames | 84 | 1.000 | 0.595 | 0.988 | 0.667 | 0.667 | 0.667 | 0.667 |
| Current behavior frames only | 84 | 1.000 | 0.488 | 0.988 | 0.583 | 0.583 | 0.583 | 0.583 |

解读：

- continuation frames 加入输入后，`match` 从 `0.488` 提升到 `0.595`。
- visible reaction fields 从 `0.583` 提升到 `0.667`。
- 这说明 continuation 视频不只是展示材料，已经能作为 action-conditioned future verification 的视觉证据进入监督。

## 7. 已准备好的扩展队列

我们已经准备好把 parent synthetic 从 260 扩到 500 或 1000，但尚未把新增样本写成 QA-reviewed。

| 目标规模 | 新增 parent | 新增 prompt index | 视角分布 | 静态 QA |
|---:|---:|---|---|---|
| 500 parent | 248 | `prompt_index_priority500_new_after280.jsonl` | sales 183 / surveillance 65 | prompt 100% 存在，label leakage = 0 |
| 1000 parent | 748 | `prompt_index_priority1000_new_after280.jsonl` | sales 558 / surveillance 190 | prompt 100% 存在，label leakage = 0 |

| 目标规模 | 产品覆盖 | Persona 覆盖 | Cue 覆盖 | Median reward gap | Strict next-state contrast |
|---:|---|---|---|---:|---:|
| 500 parent | 8 / 8 | 6 / 6 | 10 / 10 | 1.1 | 500 / 500 |
| 1000 parent | 8 / 8 | 6 / 6 | 10 / 10 | 1.1 | 967 / 1000 |

这意味着：继续投入视频/API 后，不需要重新设计 pipeline，直接可以进入更大规模数据生产和模型对比。

## 8. 为什么下一笔钱应该投 OpenRouter 模型对比

当前已经解决的是“有没有数据闭环”和“单一基座模型能不能被 PIWM 数据拉起来”。下一步要回答的是：

```text
同一套 PIWM 数据和评测协议下，哪个 VLM 基座最适合主动导购 world model？
```

OpenRouter 投入可以直接产出：

| 对比方向 | 要回答的问题 | 对公司价值 |
|---|---|---|
| 多模型 zero-shot | 商用强 VLM 是否天然更懂销售场景 | 快速判断是否值得用更强 API 模型做产品原型 |
| 多模型 SFT 前后对比 | 哪些模型吃 PIWM 数据最有效 | 避免盲目押单一模型 |
| 视觉依赖 ablation | 哪些模型真的看图，而不是只猜文本规则 | 评估真实部署可靠性 |
| Future Verification | 哪些模型能判断动作后的顾客视觉反应是否合理 | 支撑 World Model / proactive assistant 卖点 |
| 成本-效果曲线 | 小模型、本地模型、商用模型谁性价比最高 | 帮助确定产品化部署路线 |

## 9. 建议的下一阶段预算使用方式

| 阶段 | 投入对象 | 产出 |
|---|---|---|
| Phase A | OpenRouter zero-shot 横评 | 4-8 个 VLM 在同一 eval set 上的表格 |
| Phase B | 扩 QA-reviewed eval 到 80-120 parent | 更可信的模型排名 |
| Phase C | 扩 parent synthetic 到 500 | 更强 SFT 训练基线 |
| Phase D | 对 Top-2 基座做 PIWM-SFT / adapter 对比 | 给公司选模型路线 |
| Phase E | Future Verification 扩大样本 | 强化 World Model 叙事和产品差异化 |

## 10. 风险边界

| 风险 | 当前处理 |
|---|---|
| 未审阅 synthetic 不能当 benchmark | 明确只作为 training split |
| QA-reviewed eval 目前还小 | 已有 36 + 24 QA-pass，可扩到 80-120 |
| perception/candidate 是短板 | 已通过 text-only / frame-budget 定位，下一步定向补数据 |
| DPO 暂停 | 当前 SFT 已能支撑主实验，短期不让 DPO 阻塞进度 |
| Future Verification 仍是 pilot-scale | 已有 full84 结果，下一步扩 visually distinct pairs |

## 11. 对公司方的结论

当前 PIWM 已经具备继续投入的基础：

1. 数据生产闭环已跑通，不是纸面方案；
2. 已有 260 条 high-throughput synthetic parent videos 和 1321 条 SFT examples；
3. 已有 QA-reviewed eval subset，能做可信评估；
4. SFT 后相对 zero-shot 有明确提升；
5. continuation / Future Verification 已经证明未来反应视频可以进入监督；
6. 500 / 1000 parent 扩展队列已经准备好；
7. 下一笔 OpenRouter 投入可以直接换来多模型横评，而不是继续从零搭 pipeline。

建议对外口径：

```text
PIWM has completed an end-to-end synthetic data and evaluation loop for proactive in-store assistance. The current Qwen2.5-VL SFT baseline already shows large gains in structured parsing and action-conditioned transition reasoning. Additional OpenRouter budget will be used for controlled multi-model comparison under the same QA-reviewed evaluation protocol, helping identify the best foundation model for PIWM before larger-scale data expansion.
```
