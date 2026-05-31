5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# PIWM 论文写作素材包（论文同事版）

这份文档面向论文写作同学，目标是让不了解项目内部代号的人也能直接理解：PIWM 做什么、数据怎么来、模型怎么训练、目前结果如何、论文还缺哪些数字。

## 一句话项目介绍

我们训练一个能“看视频判断顾客状态 + 选择最佳导购动作”的 AI 模型。模型有两个核心能力：

1. **顾客理解能力**：看销售视频，判断顾客当前在销售漏斗哪个阶段、心里在想什么、想要什么。
2. **导购决策能力**：判断“现在该不该介入”，如果介入，应该选哪个导购动作。

## 模型决策的 5 个动作

| 动作 | 含义 | 销售场景示例 |
| --- | --- | --- |
| Greet | 主动招呼 | 顾客刚走近时打招呼 |
| Elicit | 主动询问需求 | “您主要想了解哪方面？” |
| Inform | 主动提供信息 | “这款的特点是……” |
| Recommend | 主动推荐产品 | “我推荐您看看这一款。” |
| Hold | 主动等待，不介入 | 顾客在自己看，给他空间 |

关键设计：把 `Hold`（不介入）当成和其他动作平等的选择。这样模型在同一个动作空间里同时学习“要不要介入”和“如何介入”。

## Part 1：主结果数字

### 表 1：核心结果，模型在 30 条测试视频上的表现

测试集说明：30 条智能售货机前置摄像头风格测试视频，每个动作类型 6 条，均已通过人工 QA 复核。

| 模型 | 主指标 macro F1 | 备注 |
| --- | ---: | --- |
| 随机基线，在候选动作里随机选 | 0.414 | 任何模型都必须超过这个数字才有意义 |
| 总是选 Greet/Elicit/Inform/Recommend/Hold | 0.067 | 5 个 always-X 基线都是 0.067 |
| 基础视觉语言模型不训练直接用 | 0.313 | Qwen2.5-VL-7B 不加载项目训练权重 |
| 只学顾客状态与动作后果，不学动作选择 | 0.240 | 模型还不会可靠选动作 |
| 小规模动作选择训练，少量目标场景数据 | 0.390 | 方向有效，但还不够 |
| **完整动作选择训练，均衡数据** | **0.641** | **当前主结果** |

主结果 `0.641` 显著超过随机基线 `0.414`，绝对提升 `+0.227`，相对提升约 `54.8%`。

### 表 2：主模型在每个动作上的表现

| 动作 | F1 | 精确率 | 召回率 | 该动作测试样本数 | 模型预测次数 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet（主动招呼） | 0.800 | 1.000 | 0.667 | 6 | 4 |
| Elicit（主动询问） | 0.750 | 0.600 | 1.000 | 6 | 10 |
| Inform（主动告知） | 0.714 | 0.625 | 0.833 | 6 | 8 |
| Recommend（主动推荐） | 0.600 | 0.750 | 0.500 | 6 | 4 |
| Hold（主动等待） | 0.250 | 0.500 | 0.167 | 6 | 2 |

解读：

- 4 个主动介入动作（Greet / Elicit / Inform / Recommend）都达到 `0.6+` F1。
- `Hold` 是当前最弱类别，说明模型倾向于“介入”，对“什么时候该等一等”的判断还不够稳。

### 表 3：要不要介入这个二元决策

把 `Hold` 看作“不介入”，其他 4 个动作看作“介入”。这是 proactive decision 的核心问题。

| 指标 | 数值 |
| --- | ---: |
| 不介入决策的精确率 | 0.500 |
| 不介入决策的召回率 | 0.200 |
| 不介入决策的 F1 | 0.286 |
| 介入 vs 不介入的整体 macro F1 | **0.592** |

解读：模型识别“该介入”的样本比识别“该等一等”的样本好。这个问题需要在 limitation 里主动说明。

### 表 4：数据组成的影响

| 训练数据组成 | 主指标 macro F1 |
| --- | ---: |
| 不做动作选择训练 | 0.240 |
| 71 条目标场景数据 + 15 条 Greet 增强 | 0.390 |
| 上面 + 额外 104 条均衡数据 = 190 条总监督 | **0.641** |

解读：增加均衡数据后，主指标从 `0.390` 提升到 `0.641`。这说明类别均衡对动作选择训练非常关键，不只是“数据越多越好”。

### 表 5：候选动作策略消融

测试时给模型看的候选动作列表有两种设计。

| 候选策略 | 主指标 macro F1 |
| --- | ---: |
| 直接给 5 个动作让模型选 | 0.504 |
| 按销售漏斗阶段过滤候选动作（推荐） | **0.641** |
| 按销售漏斗阶段过滤 + Hold 倾向校正 | 0.633 |
| 推理时反事实规划，按阶段推进打分 | 0.171 |
| 推理时反事实规划，按模型预测 reward 打分 | 0.265 |

解读：把销售学知识融入候选设计，比让模型自由从 5 个动作里选更有效。Hold 倾向校正没有带来额外收益。推理时反事实规划目前没有超过直接动作选择，因此论文主结果应继续使用直接动作选择；反事实规划更适合作为 ablation 或 future work。

## Part 1A：2026-05-25 best-action 60 条补充评估包

这部分是为了补论文 closed-source / local baseline 对比而整理的补充评估。它不替代表 1 的 target-only 主结果，而是把 target 30 和 general 30 放在同一 best-action 任务上做 apple-to-apple 对比。

### 评估集口径

| 项目 | 口径 |
| --- | --- |
| eval set | `reports/closed_model_eval_set_60.jsonl` |
| 样本数 | target 30 + general 30 = 60 |
| 输入 | 3 帧视频 + gold customer state 文本 + candidate actions |
| 输出 | chosen action，动作空间为 Greet / Elicit / Inform / Recommend / Hold |
| target 30 来源 | `data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl` |
| general 30 gold 来源 | `data/official/piwm_train_synth_v2/policy_preference.jsonl` / full source corpus cross-match |
| general 图片恢复 | 6 条缺失帧已从 A100 的 `archives/Archive_generated_synth_core/<source_id>/frames/` 恢复 |
| parse 失败处理 | 计入分母，按错误算 |

重要口径说明：

- target 30 复用历史 PIWM `0.641` 的来源文件。PIWM 在 target 30 上的历史 parsed-only macro F1 已复现为 `0.641`，对应 `28/30` parsed outputs。
- 本补充表使用更保守的 strict macro F1：parse failure 也算错。因此 PIWM target 30 显示为 `0.623`。
- combined 60 F1 是把 60 条 pooled 后计算 5-class macro F1，不是 target F1 和 general F1 的算术平均。
- general 30 的 gold 分布为 Elicit 13 / Hold 7 / Inform 6 / Recommend 4 / Greet 0，因此 combined per-class 的 Greet support 只来自 target 30。

### 表 5A：本地模型与 closed-model best-action 评估

| 模型 | target 30 F1 | general 30 F1 | combined 60 F1 | parse rate | modal prediction |
| --- | ---: | ---: | ---: | ---: | --- |
| PIWM 主模型 | 0.623 | 0.603 | 0.734 | 0.933 | Elicit / 23 / 60 |
| Stage-1 only | 0.227 | 0.299 | 0.259 | 0.917 | Hold / 34 / 60 |
| Zero-shot Qwen2.5-VL-7B | 0.154 | 0.116 | 0.142 | 0.433 | PARSE_FAIL / 34 / 60 |
| GPT-4o | 未跑 | 未跑 | 未跑 | - | OpenRouter HTTP 402，余额不足 |
| Gemini 2.5 Flash | 未跑 | 未跑 | 未跑 | - | OpenRouter HTTP 402，余额不足 |
| Claude Sonnet 4.6 | 未跑 | 未跑 | 未跑 | - | OpenRouter HTTP 402，余额不足 |
| Grok-3 | 未跑 | 未跑 | 未跑 | - | OpenRouter HTTP 404，该型号 deprecated |
| Random | 0.414 | 0.421 | 0.466 | 1.000 | Hold / 20 / 60 |

### 表 5A-extra：GPT-5.5 / Codex CLI 诊断项，不并入论文主表

这行是按 PI 要求额外跑的“Codex 自评”。它调用本机 `codex exec`，当时本机配置为 `model = "gpt-5.5"`、`model_reasoning_effort = "xhigh"`。由于这是 agent surface，不是 OpenRouter/API role-separated inference path，所以只能作为诊断项，不能和 mid-tier closed-model baseline 做 apple-to-apple 主表比较。

| 模型 | target 30 F1 | general 30 F1 | combined 60 F1 | parse rate | modal prediction |
| --- | ---: | ---: | ---: | ---: | --- |
| GPT-5.5 / Codex CLI self diagnostic | 0.622 | 0.573 | 0.648 | 1.000 | Hold / 17 / 60 |

记录见 `reports/2026-05-25_codex_self_best_action_eval.md`；raw outputs 见 `reports/closed_model_eval_20260525/codex_self/raw_outputs.jsonl`。

解读：

- PIWM 主模型在 target 和 general 上都高于 Stage-1 only 与 zero-shot Qwen，说明 Stage-2 best-action 监督确实贡献了动作选择能力。
- Stage-1 only 明显偏向 Hold，modal prediction 为 Hold 34/60；它能理解状态/后果，但没有学好最终动作选择。
- Zero-shot Qwen 在这个严格 prompt 上 parse rate 只有 0.433，说明直接用 base VLM 作为结构化 best-action selector 不稳定。
- 4 个 closed-source mid-tier baseline 当前不能写成已完成实验：OpenRouter 余额不足导致 GPT-4o / Gemini / Claude 第一通即失败；Grok-3 在 OpenRouter 上已 deprecated。没有替换成 frontier 或其他型号。

### 表 5B：combined 60 per-class breakdown

| 模型 | Greet F1 | Elicit F1 | Inform F1 | Recommend F1 | Hold F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| PIWM 主模型 | 0.800 | 0.905 | 0.571 | 0.667 | 0.727 |
| Stage-1 only | 0.000 | 0.286 | 0.190 | 0.308 | 0.511 |
| Zero-shot Qwen2.5-VL-7B | 0.000 | 0.160 | 0.000 | 0.182 | 0.370 |
| Random | 0.500 | 0.611 | 0.435 | 0.300 | 0.485 |

### 表 5B-extra：GPT-5.5 / Codex CLI 诊断项 per-class breakdown

| 模型 | Greet F1 | Elicit F1 | Inform F1 | Recommend F1 | Hold F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-5.5 / Codex CLI self diagnostic | 0.364 | 0.533 | 0.714 | 0.762 | 0.867 |

注意：这张表的 Greet support 只有 6，因为 general 30 没有 Greet gold。论文里如果引用 combined 60，应同时说明这个 label distribution。

### 文件索引

| 文件 | 内容 |
| --- | --- |
| `reports/2026-05-25_closed_model_eval_step0.md` | Step 0 数据可用性预检，确认 general gold 可从 full source 恢复 |
| `reports/closed_model_eval_set_60.jsonl` | 最终 60 条 best-action eval set |
| `reports/closed_model_eval_set_60.summary.json` | eval set summary，包含 target/general 分布和 missing_images |
| `reports/2026-05-25_closed_model_best_action_main_table.md` | 本次主表与 per-class breakdown |
| `reports/closed_model_eval_20260525/summary.json` | 机器可读汇总 |
| `reports/closed_model_eval_20260525/piwm_main/raw_outputs.jsonl` | PIWM 主模型 60 条 raw outputs |
| `reports/closed_model_eval_20260525/stage1_only/raw_outputs.jsonl` | Stage-1 only 60 条 raw outputs |
| `reports/closed_model_eval_20260525/zero_shot_qwen25vl7b/raw_outputs.jsonl` | Zero-shot Qwen2.5-VL-7B 60 条 raw outputs，确认 no_lora / checkpoint=None |
| `reports/closed_model_eval_20260525/openrouter_run_summary.json` | OpenRouter 调用失败原因：402 / 404 |
| `reports/2026-05-25_codex_self_best_action_eval.md` | GPT-5.5 / Codex CLI self diagnostic 结果，不并入论文主表 |
| `reports/closed_model_eval_20260525/codex_self/raw_outputs.jsonl` | GPT-5.5 / Codex CLI self diagnostic 60 条 raw outputs |
| `reports/2026-05-25_closed_model_eval_blocker.md` | 图片缺失、恢复路径和后续状态记录 |

论文写作建议：

- 可以写：PIWM 在 60 条 target+general best-action 补充评估上，strict combined macro F1 为 `0.734`，高于 Stage-1 only `0.259`、zero-shot Qwen `0.142` 和 random `0.466`。
- 可以写：target-only 历史主结果仍按 parsed-only macro F1 报 `0.641`；如果使用 strict 口径则是 `0.623`。
- 可以作为诊断附注写：GPT-5.5 / Codex CLI self diagnostic 在同一 60 条上 strict combined macro F1 为 `0.648`，parse rate 为 `1.000`；但它是 Codex agent surface，不是论文 closed-model API baseline。
- 暂时不要写：closed-source mid-tier baseline 已完成；当前只能写作“计划评估但因 OpenRouter 余额/型号不可用未跑”。
- 不要写：PIWM 已证明 inference-time online planning 优于 direct action selection；当前反事实规划 ablation 仍低于 direct best-action。

## Part 1A-2：2026-05-26 端到端 best-action 评估

这部分回答 reviewer 可能问的 oracle-state 问题：不提供 gold customer state 时，PIWM 是否还能从 3 帧视频先自推 state，再选 best_action。

| Setting | Macro F1 | Parse rate (step 1) | Parse rate (step 2) |
| --- | ---: | ---: | ---: |
| PIWM with gold state (Dim 4 original) | 0.641 | - | 0.933 |
| PIWM end-to-end (target 30，自推 state) | 0.295 | 0.800 | 0.533 |
| Random | 0.414 | - | - |

60 条扩展结果：target `0.295`，general `0.438`，combined `0.380`；combined Step 1 parse rate `0.683`，Step 2 parse rate `0.533`。

错误传播分析：

| Subset | N samples | Best-action F1 |
| --- | ---: | ---: |
| Step 1 stage 预测正确 | 18 | 0.531 |
| Step 1 stage 预测错误 | 23 | 0.359 |

注意：上面两行只覆盖 Step 1 parse 成功的 41 条；Step 1 parse 失败的 19 条已按 best-action 错误计入主分母。

文件索引：

| 文件 | 内容 |
| --- | --- |
| `reports/2026-05-26_end_to_end_main_result.md` | A1 端到端 best-action 主结果 |
| `reports/end_to_end_eval_20260525/step1_predicted_state.jsonl` | Step 1 自推 customer state raw output |
| `reports/end_to_end_eval_20260525/step2_predicted_action.jsonl` | Step 2 自推 state 注入后的 best_action raw output |
| `reports/end_to_end_eval_20260525/summary.json` | 机器可读指标汇总 |
| `scripts/run_end_to_end_best_action_eval.py` | A1 只推理评估脚本 |

写作建议：可以写这个结果作为 limitation / reviewer-facing sanity check，说明当前 PIWM 的 direct best-action 能力依赖较稳定的 state representation；端到端链路主要受 Step 1/Step 2 parse 稳定性和旧式 action label 解析失败影响。不要把 `0.295` 与 `0.641` 写成同一 prompt 条件下的模型退化，二者输入条件不同。

## Part 1A-3：2026-05-26 Dataset 统计分析

B1 统计已整理到 `reports/2026-05-26_dataset_statistics.md`，用于补论文 Section 5.3。它覆盖 AIDA stage、best_action、intent label、candidate set size、outcome reward、BDI 字段长度、同 scene 跨任务覆盖 7 个小节。

关键可引用数字：

| Item | Value |
| --- | ---: |
| general user_intent scenes | 543 |
| next_state_prediction rows | 2001 |
| next_state parent-scene mean candidate size | 3.685 |
| balanced action_selection train rows | 190 |
| user_intent + next_state general-scene overlap | 543 / 543 |
| user_intent + action_selection_5act general-scene overlap | 110 / 543 |

注意：B1.5 请求的 `score_1_5` 字段在 `transition_modeling.jsonl` 中不可用；当前可统计的是 `output.reward` in `[-1, 1]`，报告里已明确标注，不能写成 1-5 outcome score 分布。

## Part 1B：4 维度链路评估

这部分用于把 PIWM 的方法故事从单一 best-act 指标扩展为完整链路：视觉观察 → 意图理解 → 效果预测 → 综合决策。数字来自 `reports/2026-05-25_rerun_evaluation_main_table.md`，raw output 保存在 `reports/rerun_eval_20260525/`。

主表采用 **strict macro F1**：parse 失败样本按错误计入分母。这个口径更保守，适合论文 discussion 中解释“模型是否稳定输出可解析结构”。

| Model | Dim 1 AIDA F1 | Dim 2 intent F1 core | Dim 3 next-state F1 | Dim 4 best-act F1 |
| --- | ---: | ---: | ---: | ---: |
| Uniform/random baseline | 0.235 | 0.138 | 0.233 | 0.414 |
| Qwen2.5-VL-7B 不训练直接用 | 0.190 | 0.053 | 0.108 | 0.313 |
| 只做顾客状态与动作后果训练 | 0.349 | 0.111 | 0.587 | 0.240 |
| PIWM 主模型 | 0.350 | 0.114 | 0.565 | 0.641 |

说明：

- Dim 1/2 使用 60 条评估样本：30 条 target test + 30 条 general seed=42 样本。表中是 combined 60 的 strict macro F1。
- Dim 2 的 core intent 口径排除 `seek_reassurance` 和 `negotiate_price`，因为此前 taxonomy audit 判定这两类在纯视觉模态下不可稳定识别。
- Dim 3 使用带 current state 的 deliberation prompt，只对 80 条有 transition gold 的 stage-conditioned candidates 评分；另有 27 条 placeholder candidates 无 gold，不参与 F1/MAE，作为 next-state evaluation coverage limitation 写入论文限制。Zero-shot Dim 3 已在 2026-05-25 修复 no-lora 逻辑后重跑，strict macro F1=0.108，parse rate=0.250。
- Dim 4 复用已有 direct best-act 主结果。本轮没有重跑 direct Dim 4；本轮重跑的是 Dim 1/2、Dim 3 和推理时反事实规划。
- Dim 1/2 的 PIWM 主模型 parse rate 只有 `0.667`，低于 0.7；因此这些数字应作为诊断指标，而不是强主结果。

### 错误传播分析框架

旧版错误传播表来自 `reports/2026-05-24_pi_4dim_evaluation.md`，但其中 Dim 3 使用的是不带 current state 的 prompt，不再作为论文主分析数字。新的错误传播分析应基于 `reports/rerun_eval_20260525/` 的 raw output 重新计算。论文结构可以先保留下面 4 张表的框架，数字待补。

**表 A：链路条件成功率（待基于 2026-05-25 raw output 重算）**

| 条件 | 正确率 | 分子 / 分母 |
| --- | ---: | ---: |
| P(intent 对 \| stage 对) | 待补 | 待补 |
| P(intent 对 \| stage 错) | 待补 | 待补 |
| P(next_state 对 \| stage+intent 对) | 待补 | 待补 |
| P(next_state 对 \| stage 或 intent 错) | 待补 | 待补 |
| P(best_act 对 \| stage+intent+next_state 全对) | 待补 | 待补 |

**表 B：动作错误类型分布（待基于 2026-05-25 raw output 重算）**

| 错误类型 | 数量 | 占 action 错误比例 |
| --- | ---: | ---: |
| stage 错误传播 | 待补 | 待补 |
| stage 对但 intent 错 | 待补 | 待补 |
| stage+intent 对但 next_state 错 | 待补 | 待补 |
| 前 3 维度对但 action 错 | 待补 | 待补 |

**表 C：stage 错误对决策候选集的影响（待补）**

| 指标 | 数值 |
| --- | ---: |
| stage 预测错误样本数 | 待补 |
| stage 错误样本中的 action accuracy | 待补 |
| 典型候选集变化 | 待补 |

**表 D：per-act 错误归因（待补）**

| Gold act | Total errors | Stage error | Intent error | Next-state error | Strategy bottleneck |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 待补 | 待补 | 待补 | 待补 | 待补 |
| Elicit | 待补 | 待补 | 待补 | 待补 | 待补 |
| Inform | 待补 | 待补 | 待补 | 待补 | 待补 |
| Recommend | 待补 | 待补 | 待补 | 待补 | 待补 |
| Hold | 待补 | 待补 | 待补 | 待补 | 待补 |

## Part 1C：2026-05-25 真实视频 sim-to-real 小规模评估

这部分回应“模型在真实视频上能不能跑”的问题。当前真实集不是完整 50 条 benchmark：仓库/索引侧共有 50 条候选，其中 30 条有本地/仓库视频可评估，20 条缺视频文件。可评估的 30 条里，20 条有完整逐 session 人工 JSON 标注，10 条只有 `index.json` 组级弱标签。

### 评估集口径

| 项目 | 口径 |
| --- | --- |
| 输入文件 | `reports/real_eval_20260525/real_all_scored.jsonl` |
| 样本数 | 30 个真实视频 × 2 个任务 = 60 rows |
| 任务 | `user_intent` + `action_selection_5act` |
| 完整人标 | 20 个视频，40 rows |
| index 弱标 | 10 个视频，20 rows |
| 缺视频跳过 | 20 个候选 session |
| 输入 | 每个视频抽 3 帧，action 任务额外给 gold current state + candidate actions |
| 输出 | AIDA stage / intent tags；或 5-act chosen action |
| 主要指标 | Stage Acc / Stage Macro F1；Action Acc / Action Macro F1 |

口径说明：

- `Intent Acc` 只作次要诊断，因为当前真实集的 intent label 是从 best action 启发式派生，不是独立人工意图分类。
- 总体 30 条结果可以写成 sim-to-real pilot；正式强结论建议优先引用 20 条完整人标口径。
- 10 条 `index_group_weak_label` 只适合补充诊断，不能当作高可信逐视频人工标注。

### 表 5C：真实视频 30 条整体结果

| 模型 | Parse | Stage Acc | Stage Macro F1 | Action Acc | Action Macro F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-VL-7B 不训练直接用 | 0.600 | 0.120 | 0.056 | 0.364 | 0.333 |
| 只做顾客状态与动作后果训练 | 0.933 | 0.167 | 0.175 | 0.346 | 0.292 |
| **PIWM 主模型** | **0.933** | **0.214** | **0.241** | **0.679** | **0.520** |

解读：在 30 条真实视频 pilot 上，PIWM 主模型的 action selection 明显高于 Stage-1 only 和 zero-shot Qwen。Action Macro F1 从 Stage-1 only 的 `0.292` 提升到 `0.520`，说明 Stage-2 best-action 监督在真实视频上仍带来动作选择收益。Stage 指标仍低，说明视觉状态识别迁移还不稳。

### 表 5D：完整人标 20 条 vs index 弱标 10 条

| 模型 | 标注口径 | Rows | Videos | Parse | Stage Acc | Stage Macro F1 | Action Acc | Action Macro F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-VL-7B 不训练直接用 | 完整人标 | 40 | 20 | 0.575 | 0.200 | 0.088 | 0.125 | 0.111 |
| Qwen2.5-VL-7B 不训练直接用 | index 弱标 | 20 | 10 | 0.650 | 0.000 | 0.000 | 1.000 | 1.000 |
| Stage-1 only | 完整人标 | 40 | 20 | 0.925 | 0.250 | 0.200 | 0.235 | 0.217 |
| Stage-1 only | index 弱标 | 20 | 10 | 0.950 | 0.000 | 0.000 | 0.556 | 0.444 |
| **PIWM 主模型** | **完整人标** | **40** | **20** | **1.000** | **0.300** | **0.262** | **0.600** | **0.579** |
| PIWM 主模型 | index 弱标 | 20 | 10 | 0.800 | 0.000 | 0.000 | 0.875 | 0.600 |

注意：弱标 action 指标的可解析样本数很小，尤其 zero-shot Qwen 在弱标 action 上只有 3 个 parsed samples，因此弱标分数不能作为稳健比较。论文正文推荐写完整人标 20 条：PIWM action macro F1 `0.579`，高于 Stage-1 only `0.217` 和 zero-shot Qwen `0.111`。

### 文件索引

| 文件 | 内容 |
| --- | --- |
| `reports/real_eval_20260525/manifest.json` | 真实视频候选、缺视频、完整人标/弱标数量统计 |
| `reports/real_eval_20260525/real_all_scored.jsonl` | 60-row ms-swift eval 输入 |
| `reports/real_eval_20260525/model_runs_gpu1/summary.md` | 30 条整体结果 |
| `reports/real_eval_20260525/model_runs_gpu1/label_source_summary.md` | 完整人标 vs index 弱标拆分 |
| `reports/real_eval_20260525/model_runs_gpu1/*.json` | 三个本地模型的 raw outputs 与 metrics |

## Part 2：数据集说明

### 表 6：数据来源

| 数据来源 | 数量 | 用途 |
| --- | ---: | --- |
| 销售学理论与规则 | 78 条规则 + 27 条原理 | 设计动作空间、候选规则和状态转移 |
| 通用零售场景合成视频 | 543 个场景 → 2544 条训练样本 | 教模型理解顾客状态和动作后果 |
| 目标场景合成视频，智能售货机前置摄像头风格 | 71 训练 + 30 测试 | 教模型在目标场景选动作 + 评测 |
| Greet 动作增强合成数据 | 15 条 | 补充 Greet 类样本不足 |
| 均衡动作选择数据 | 190 条总监督 | 主模型动作选择训练数据 |
| 真实视频 sim-to-real 评测集 | 候选 50 条；当前可跑 30 条，其中 20 条完整人标 + 10 条 index 弱标 | sim-to-real pilot 评测 |
| 资深销售员专家材料 | 3 位从业者问卷已入库；Fleiss κ 评测未完成 | 专家共识评测，计划中 |

### 表 7：主模型动作选择训练数据的均衡组成

| 来源 | 数量 | 该来源贡献的动作 |
| --- | ---: | --- |
| 目标场景原始数据 | 71 | Inform 41 / Elicit 14 / Greet 11 / Recommend 5 / Hold 0 |
| Greet 增强数据 | 15 | Greet 15 |
| 通用数据均衡补充 | 104 | Elicit 27 / Recommend 36 / Hold 41 |
| **总计** | **190** | **Greet 26 / Elicit 41 / Inform 41 / Recommend 41 / Hold 41** |

关键设计：通过从通用数据池抽样 + Greet 增强，把每个动作的训练样本从严重不均衡（最少 0，最多 41）变成相对均衡（每类 26 到 41 条）。

### 表 8：反事实监督的覆盖度

每个销售场景，模型都会看到“如果选不同动作，顾客状态会怎么变化”的多个版本。

| 项目 | 数值 |
| --- | ---: |
| 总场景数 | 543 |
| 总样本数，场景 × 候选动作 | 2001 |
| 平均每个场景被展开几次 | 3.685 |
| 是否覆盖每个场景所有候选动作 | 是，100% 覆盖 |

意义：模型见过同一个场景下“选 A 会怎样、选 B 会怎样、选 C 会怎样”的完整对比。这是 PIWM 世界模型训练的核心。

## Part 3：方法描述，论文章节可直接改写

### 3.1 任务定义

我们把零售导购的主动决策问题形式化为：

```text
输入：稀疏视频帧序列，当前使用 3 帧抽样
输出：(best_action, intervention_utterance)
best_action ∈ {Greet, Elicit, Inform, Recommend, Hold}
```

其中，`Hold` 表示“等待 / 暂不介入”，其他 4 个动作表示不同形式的主动介入。将 `Hold` 设计为一等动作，让模型把“介入与否”和“如何介入”放在同一动作空间里联合学习。

### 3.2 双世界模型架构

PIWM 用单个视觉语言模型基座（Qwen2.5-VL-7B + LoRA）同时建模两个“世界”：

**用户意图世界（User Intent World）**

- 输入：3 帧视频。
- 输出：当前顾客的销售漏斗阶段（attention / interest / desire / action）、意图标签，以及 belief / desire / intention 三维内部状态。

**销售动作世界（Sales Action World）**

- 输入：3 帧视频 + 候选动作。
- 输出：执行该动作后，顾客的下一步状态。

两个世界共享同一个 LoRA 适配器，联合训练。

### 3.3 两阶段训练

**第一阶段：训练顾客理解与动作后果预测**

- 使用通用零售场景数据。
- 543 个场景投影出 2544 条多任务样本。
- 同时训练顾客理解和动作后果预测。
- 训练时长约 6 小时。

**第二阶段：训练目标场景动作选择**

- 使用均衡的目标场景动作选择数据。
- 190 条均衡样本，每个动作 26 到 41 条。
- 在第一阶段模型基础上继续训练。
- 训练时长约 5 到 6 小时。

### 3.4 反事实监督，核心创新

PIWM 的世界模型监督通过数据组织方式实现反事实学习。

对每个销售场景，数据集生成多条样本：同一组视频帧重复出现，但配对的候选动作不同，监督的 next_state、belief/desire/intention 变化和 reward 也不同。

例子：在“顾客看着商品犹豫”这个场景中：

| 候选动作 | 监督的下一状态 | reward |
| --- | --- | ---: |
| Elicit | 顾客进入 desire 阶段 | 0.83 |
| Inform | 顾客进入 desire 阶段 | 0.80 |
| Hold | 顾客停留在 interest 阶段 | 0.20 |
| Recommend | 顾客后退到 attention 阶段 | -0.30 |

模型由此学习“不同动作 → 不同后果”的因果映射。

### 3.5 销售阶段约束候选过滤

测试时按销售漏斗阶段限制候选动作：

| 销售漏斗阶段 | 可选动作 |
| --- | --- |
| attention，注意 | Greet / Elicit / Inform / Hold |
| interest，兴趣 | Elicit / Inform / Recommend / Hold |
| desire，欲望 | Inform / Recommend / Hold |
| action，行动 | Greet / Recommend / Hold |

依据：心理学反抗理论提示早期不应过早推荐；SPIN 销售理论提示应先理解需求，再推荐或促成行动。

### 3.6 推理时反事实规划，已完成消融

当前主结果是直接动作选择：模型一次输出 best action。我们也测试了“推理时反事实规划”：让模型在选动作前先预测每个候选动作的后果，再按 reward 选最优。

```text
for each candidate action a:
    predicted_next_state = model.predict(image, current_state, a)
    reward[a] = R(current_state, predicted_next_state)
best_act = argmax(reward)
```

实验结果显示，推理时反事实规划目前没有超过直接动作选择：

| 决策方式 | macro F1 |
| --- | ---: |
| 直接动作选择 | **0.641** |
| 反事实规划，按阶段推进打分 | 0.171 |
| 反事实规划，按模型预测 reward 打分 | 0.265 |

论文建议：主结果继续使用直接动作选择；反事实规划作为 ablation 说明“世界模型用于决策时规划”目前仍受 next-state 预测和 reward 函数设计限制。

## Part 4：已知限制，论文必写

1. **训练数据全合成，真实评测仍是小规模 pilot**：所有训练视频由 Kling 生成。当前已完成 30 条真实视频 sim-to-real 评估，但其中只有 20 条有完整逐 session 人工 JSON 标注，另外 10 条来自 `index.json` 组级弱标签；仍不能写成完整 50 条真实 benchmark。

2. **目标场景动作选择监督规模有限**：主模型只用了 190 条动作选择监督样本。

3. **Greet 类依赖增强数据**：26 条 Greet 训练样本中，15 条是合成增强。目标场景原始数据本身只有 11 条 Greet。

4. **Hold 是当前最弱类别**：Hold F1=0.250，召回率 0.167，说明模型对“该等一等”的判断还不够稳定。

5. **3 帧视频输入信息有限**：5 帧或更密集时序输入的 ablation 是 future work。

6. **专家验证待补**：3 位资深销售员的 Fleiss κ 评测尚未完成，可在 appendix 或 limitation 中说明。

7. **类别加权机制实施细节**：原计划用 ms-swift 框架的 row-level loss_weight 字段降权视觉难分类类别，但该框架没有自动消费这个字段。后续应通过 custom trainer 或数据重采样实现。

8. **next-state 评估覆盖不完整**：stage-conditioned candidates 共 107 条，其中 80 条有 transition gold，27 条无 gold，不能纳入 next-state F1/MAE。论文正文需要明确写出 `80/107` 的 coverage limitation。

9. **推理时反事实规划暂未超过直接动作选择**：反事实规划最好的 reward 版本 macro F1=0.265，低于直接动作选择的 0.641。说明当前 world model 更适合作为训练监督和分析工具，decision-time planning 仍需更好的 next-state 预测和 reward 设计。

10. **真实集 intent label 不是独立人工意图标注**：真实评估中的 intent label 由 best action 启发式派生，不能作为强意图分类结论；论文中应把 Stage 和 Action 指标作为主口径。

## Part 5：还没做完但写论文时要预留位置的事

| 事项 | 状态 | 论文章节预留 |
| --- | --- | --- |
| 基础模型不训练直接用的动作选择 baseline | 已完成，macro F1=0.313 | Table 1 已填 |
| 推理时反事实规划数字 | 已完成，最好版本 macro F1=0.265，未超过直接动作选择 | Section 3.6 + Table 5 已填 |
| 4 维度链路评估 | 主表已完成，错误传播表待按 2026-05-25 raw output 重算 | Experiments / Discussion |
| 真实视频 sim-to-real 评测 | 已完成 30 条 pilot；20 条完整人标 + 10 条 index 弱标 | Section 4.6 sim-to-real validation |
| 3 位销售员 Fleiss κ 标注 | 专家材料已入库，Fleiss κ 未完成 | Appendix 或 limitation |
| 目标场景重复加权训练 | 待跑，预计 6 到 7 小时 | 可选 ablation |

## 给论文写作同学的建议

### 今天立刻可以写

这些部分不依赖新实验，可以先写：

- Introduction，约 1.5 页。
- Related Work，约 0.75 页。
- Method 3.1 到 3.5，可直接基于 Part 3 改写。
- Figure 1，整体架构图。
- Figure 2，数据 pipeline。
- Figure 3，销售阶段候选动作决策树。
- Section 4.6，真实视频 sim-to-real pilot 验证，可基于 Part 1C 先写小规模结果与口径限制。

### 仍需补充或扩大后再写

这些部分需要等后续材料或更大规模评测：

- 更强真实视频 benchmark 口径：需要补齐缺视频的 20 条或扩大完整人标规模。
- Appendix：专家一致性评测。
- Optional ablation：目标场景重复加权训练。

### 建议论文结构

```text
1. Introduction (1.5 页)
2. Related Work (0.75 页)
3. Method (2 页)
   3.1 任务定义
   3.2 双世界模型架构
   3.3 两阶段训练
   3.4 反事实监督
   3.5 销售阶段约束候选
   3.6 推理时反事实规划
4. Experiments (2.5 页)
   4.1 实验设置
   4.2 主结果
   4.3 数据组成消融
   4.4 候选策略消融
   4.5 介入决策分析，Hold vs 非 Hold
   4.6 sim-to-real pilot 验证
5. Limitations (0.5 页)
6. Conclusion (0.25 页)
```

## Source Index

| 编号 | 含义 |
| --- | --- |
| S1 | 仅训练顾客理解与动作后果预测后的目标动作选择评估报告 |
| S2 | 5-act balanced baseline 重算报告 |
| S3 | 小规模目标域动作选择训练报告 |
| S4 | 均衡目标域动作选择训练报告与对应 all-row 评估输出 |
| S5 | 专家知识库规则与 principle 文件 |
| S6 | 通用零售合成视频主数据与训练入口 |
| S7 | 目标场景 split 与 action-selection eval 汇总 |
| S8 | Greet 增强训练入口 |
| S9 | 均衡动作选择数据生成报告与 summary 文件 |
| S10 | next-state transition 数据 |
| S11 | `reports/2026-05-25_rerun_evaluation_main_table.md`：4 维度重跑主表，Dim 3 使用带 current-state 的 deliberation prompt |
| S12 | `reports/2026-05-25_rerun_evaluation_appendix.md`：per-class、confusion matrix 和 Trick 6 附录 |
| S13 | `reports/rerun_eval_20260525/`：A100 重跑 raw output 与 prompt 证据 |
| S14 | `reports/2026-05-24_pi_4dim_evaluation.md`：旧版 4 维度评估，仅作历史参考，不再作为主表来源 |
| S15 | Zero-shot no-lora bug fix：`reports/2026-05-25_zero_shot_bug_audit.md` 和 `reports/rerun_eval_20260525/zero_shot_qwen_*_fixed.json` |
| S16 | `reports/real_eval_20260525/`：30 条真实视频 sim-to-real pilot 输入、三模型输出、整体 summary 与人标/弱标拆分 |
