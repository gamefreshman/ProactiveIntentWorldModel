# 数据部分中文审阅稿

> 对应英文稿：`paper/data_section_emnlp.tex`  
> 用途：先给项目负责人中文审阅，确认叙事、数字和口径后，再回写英文论文版本。

## 数据

PIWM 需要的数据不同于普通视觉问答数据，也不同于普通对话回复数据。一条训练样本不能只问“图里有什么”或者“下一句话怎么说”，而必须把一段短视觉观察、顾客当前状态、可选主动动作，以及每个动作可能带来的后果连接起来。因此，我们构建了一套 **general-to-target** 数据体系：general 数据用于学习通用零售导购能力，target 数据用于检验这些能力能否迁移到设备前置摄像头视角下的智能售货终端场景。

### 设计原则：低资源 target 专项适配，而不是 target 大规模预训练

target 数据集有意保持紧凑。它的作用不是用几百条额外视频替代 general 数据，而是制造一个清晰、可控的目标域迁移问题：模型先从 general 数据中学习主动导购能力，再用少量 target-frontcam 数据适配到固定安装在智能售货终端上的前置摄像头视角。

这个设定更贴近真实部署：一个主动服务代理不可能为每个门店、每个设备、每个商品线都重新采集大规模视频；更合理的目标是先学习通用导购知识，再用少量目标域数据完成专项适配。因此，本文的数据主张不是“target 域视频规模很大”，而是 **少量 target 数据是否足以带来有效的目标域专项适配**。

## 从专家知识到结构化输出

PIWM 的输出不是逐条视频临时手写出来的自由标签，也不是让模型凭空生成的答案。它们来自一层可审计的专家知识库。我们先从销售学和消费者行为研究中整理知识来源，包括 AIDA、OpenStax 营销学章节、SPIN Selling、心理抗拒理论，以及关于 hedonic / utilitarian / recreational / gift shopping 的消费者动机研究。对有版权限制的书籍或论文，只保留 citation-level anchor 和 compact paraphrase，不把长篇原文放入训练数据。

这套专家知识库分三步工作。

第一步，把来源材料蒸馏成简短原则。例如：什么时候应该问开放式问题，什么时候推荐应该保持低压力，什么时候强推荐会触发顾客的抗拒感。

第二步，把这些原则提升成条件规则。当前专家库中有 **27 条 distilled principles** 和 **78 条 source-linked conditional rules**。这些规则包括：视觉线索如何映射到顾客状态，persona 如何映射到 intent tier，某个 state + AIDA 阶段下有哪些候选动作，以及某个动作会带来什么下一状态和 reward。

第三步，把规则编译成每条数据里的确定性字段。生成链路可以概括为：

```text
scene cues
  -> customer state
  -> intent tier
  -> candidate actions
  -> action outcomes
  -> training targets
```

其中，customer state 包括 AIDA 阶段和 BDI 摘要。BDI 是 belief / desire / intention，简单说就是“顾客现在相信什么、想要什么、下一步打算做什么”。candidate-action 规则会生成有限候选动作集合；transition 规则会为每个候选动作生成 next state、reward、risk level、benefit level 和可选 failure mode。最后，系统用确定性排序选择 best action。Realization 则由动作模板填充：general 数据里对应真人导购的表达，target 数据里对应终端屏幕、语音、灯效或等待状态。

这条链路对论文很重要。它说明 PIWM 的监督不是黑箱标注：如果一个 label 错了，可以追溯到具体规则和来源链接；如果规则需要修正，也可以由领域专家改规则，而不是重新猜测模型为什么输出错。同时，它让同一个视觉状态可以展开成多个候选动作的反事实结果，因此模型不仅学习“该选哪个动作”，也学习“其他动作会导致什么后果”。

## 数据来源与划分

当前 EMNLP 版本使用的数据如下。

| Split | 领域 / 视角 | Records | Frames | Examples | QA 状态 | 作用 |
|---|---|---:|---:|---:|---|---|
| General train | 零售导购，第三人称 / 导购可观察视角 | 543 | - | 2544 | synthetic train | Stage-1 用户状态 + next-state SFT |
| Target train | 智能售货终端，前置摄像头视角 | 71 | 213 | 71 | synthetic train | Stage-2 5-act target adaptation |
| Target eval | 智能售货终端，前置摄像头视角 | 30 | 90 | 90 | 项目负责人 QA-reviewed pass | balanced 5-act in-domain test |
| General eval | 零售导购，第三人称视角 | 36 | - | 162 | QA-reviewed subset | forgetting check |

General 训练入口 `PIWM-Stage1-UserIntent-v1` 包含 543 条 synthetic video-backed parent states，导出为 2544 条监督样本：543 条 `user_intent` 和 2001 条 `next_state_prediction`。Target 数据源 `PIWM-Target-Frontcam-v1` 包含 118 条智能售货终端前置摄像头记录。当前主实验采用 5-act 口径：`Greet / Elicit / Inform / Recommend / Hold`。排除 17 条 best=`Reassure` 样本，并过滤候选中的 `Reassure` 且无候选集退化，得到 101 条 clean 5-act records，其中 71 条用于 target adaptation，30 条作为 balanced target test。新 test 分布为 `Greet=6 / Elicit=6 / Inform=6 / Recommend=6 / Hold=6`。因为 test 名单已经变化，旧 split 的 QA 结论不能沿用；当前新 test 已按新名单写回为项目负责人 QA-reviewed pass。

### General 零售导购语料

General 数据覆盖普通店内导购场景，视角接近第三人称或真人导购可观察视角。Stage-1 的 `user_intent` 输入只包含 3 张图和朴素场景描述，例如“顾客在零售店内”，不提供候选动作、best action、reward 或推荐信息。输出是 AIDA 阶段、intent label、可见证据和 BDI。Stage-1 还包含 action-conditioned next-state prediction：给定一个候选动作，预测 next BDI 和 next stage；其中 `Hold(mode=silent)` 表示“不干预会怎样”的分支。

### Target 前置摄像头语料

Target 数据来自固定在智能售货终端上的前置摄像头。这带来两个变化：第一，视觉域发生变化，模型不再从真人导购或第三方视角观察顾客，而是从终端设备视角观察；第二，动作主体发生变化，响应不再是真人导购的肢体和话术，而是智能终端的屏幕、语音、灯效等行为。

每条 target record 抽取 3 张关键帧，并映射到与 general 数据一致的 v2.2 动作 schema。当前主实验只使用 5-act clean split：71 条 train 和 30 条 test，按 record 划分，保证 test 里的 record 不出现在 adaptation training 中。`Greet / Elicit / Inform / Recommend / Hold` 是当前主实验 5-act；`Reassure` 只作为历史/source 记录和兼容分析边界，不进入主 5-act macro F1。

## 监督格式

每条 record 会根据训练任务导出为一条或多条监督样本。当前主要有三类任务：

1. **User intent**：根据 3 张图和朴素场景描述判断顾客当前状态、AIDA 阶段、intent label 和 BDI，不输出动作。
2. **Next-state prediction**：给定当前状态和一个候选动作，预测这个动作可能导致的下一阶段和 next BDI；`Hold(mode=silent)` 作为不干预分支。
3. **Action selection 5-act**：在 5-act 候选动作中选择最合适的主动响应。输入只给 act、params 和 realization，不给 reward、risk、benefit、predicted_next_stage 或 next_state。

当前任务拆分如下：

| Split | User intent | Next-state prediction | Action selection | Total |
|---|---:|---:|---:|---:|
| General train | 543 | 2001 | 0 | 2544 |
| Target train | 0 | 0 | 71 | 71 |
| Target eval | 30 | 30 | 30 | 90 |
| General eval | 36 | 126 | 0 | 162 |

Next-state 样本数量会多于 parent record，因为同一个当前状态会展开到多个候选动作；模型需要分别判断每个动作可能带来的后果。Target eval 的 next-state 行只使用 `Hold` 不干预分支，便于回答“如果完全不干预会怎样”。

## 动作空间

当前论文和主训练口径使用 5-act operational policy schema：

- `Greet`：开场或收尾问候，建立低压力交互入口。
- `Elicit`：询问需求，澄清顾客意图。
- `Inform`：提供信息，例如比较、演示、属性说明、价格说明。
- `Recommend`：推荐商品，并区分 soft / firm 压力强度。
- `Hold`：保持等待或低干预。

这套动作空间不是扁平标签，而是 `act + params` 的参数化结构。例如 `Recommend` 会区分 `pressure=soft` 和 `pressure=firm`，`Inform` 会区分 `content_type=comparison/demo/attributes/price`。这样既能保持动作空间可审计，又能保留实际导购行为差异。

这次口径已经反转：当前 5-act operational policy 是 `Greet / Elicit / Inform / Recommend / Hold`。`Reassure` 仍可在历史/source 数据中出现，但不作为当前主动作空间成员。

`Reassure` 仍保留为历史/source 标签与兼容分析边界，但不计入当前主训练、评估、推理、runtime export 和 macro-F1 的 operational action-space claim。

Target 数据对动作覆盖尤其重要。按当前 5-act 口径，它补充了设备前置摄像头下的 `Greet`、`Recommend` 和 `Hold` 行为；General v2 则通过 `Recommend(pressure=soft/firm)` 重新写出可训练的参数化推荐候选。

| Target raw best act | Records | Percent |
|---|---:|---:|
| `Inform` | 47 | 39.8 |
| `Elicit` | 20 | 16.9 |
| `Greet` | 17 | 14.4 |
| `Reassure`（当前 5-act 排除） | 17 | 14.4 |
| `Recommend` | 11 | 9.3 |
| `Hold` | 6 | 5.1 |

Target 数据里没有任何一个 operational 动作类型完全垄断。最大的 `Inform` 也只占 47 / 118。另有 17 条 target 记录使用 `Reassure`，这些样本保留为兼容和错误分析来源，不作为当前主 5-act 动作空间的覆盖证据。

## QA 与数据质量控制

我们把 QA 作为 split 级别属性，而不是给整个 corpus 一刀切贴标签。换句话说，不说“118 条 target 全部 QA-reviewed”，而是精确说明：

- 30 条 target test records：balanced 5-act test，已按新名单 QA-reviewed pass。
- 71 条 target train records：synthetic training data，尚不是人工 QA-reviewed benchmark。

target eval 的 QA 通过 contact sheet 完成。每条记录展示 3 张抽帧图。通过标准包括：

1. 顾客主体可见。
2. 头部方向或视线方向可解释。
3. 身体姿态可见。
4. 终端或柜体上下文可见。
5. 三张图在时间上连续一致。
6. 结构化动作标签能被视觉证据支撑。

新 test 的评估入口已经生成在 `data/official/domain_specialization_eval_v2/`。QA 状态以当前 30 条 balanced test 的落盘字段为准：当前已写回 `qa_reviewed_pass=30`。旧的 QA pass 结果只作为历史 split 证据，不能用来代表当前 balanced 5-act test。

## 实验用途

这套数据支持四组实验：

1. **General on target**：只用 general 数据训练，然后直接测 balanced 5-act target split，衡量 zero-shot target transfer；该 split 需要先完成项目负责人 QA。
2. **Target-specialized**：先 general 训练，再用 71 条 target 5-act train 继续训练，衡量低资源 target specialization 是否带来提升。
3. **Joint baseline**：把 general 和 target 混合训练，测试简单 pooling 是否能达到 staged specialization 的效果。
4. **Forgetting check**：把 target-specialized 模型重新测回 general QA eval，检查是否因为适配 target 而遗忘 general 导购能力。

因此，target split 虽然紧凑，但它的作用是明确的：制造一个可被 QA 复核的目标域迁移评测，而不是充当大规模 target 预训练语料。本文的强主会故事应围绕这一点展开：**PIWM 是否能把 general proactive retail guidance 迁移到低资源 target-frontcam 智能终端场景中。**
