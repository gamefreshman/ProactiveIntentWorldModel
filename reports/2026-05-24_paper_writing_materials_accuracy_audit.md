5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# PIWM 论文写作素材包数据准确性核对

本报告核对对象是 `reports/2026-05-24_paper_writing_materials.md`。核对原则是：论文素材包里的数字必须能从当前仓库数据文件、评估输出或明确报告中追溯；当前仓库不能核到的内容不能写成已确认事实。

## 结论

论文素材包的大部分核心实验数字可以核实，尤其是 5-act 集合、训练/评测样本数、目标测试集均衡分布、主结果 `0.641`、每类 F1、以及 190 条动作选择训练数据组成。

需要修正的主要问题有两处：

1. “只学顾客理解”表述不精确。实际第一阶段训练包括两类任务：`user_intent` 顾客状态理解和 `next_state_prediction` 动作后果预测。因此已改为“只学顾客状态与动作后果，不学动作选择”。
2. “真实视频已收集 40 条”当前仓库未核到可评测 index。当前检查路径 `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/eval/real/index.json` 不存在，因此素材包已改为“待确认可评测 index 路径”。

## 已核实数字

### 1. 第一阶段训练数据

来源文件：

`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl`

核对结果：

| 项目 | 数值 |
| --- | ---: |
| 总行数 | 2544 |
| `user_intent` 任务 | 543 |
| `next_state_prediction` 任务 | 2001 |

这支持素材包里“543 个场景投影出 2544 条多任务样本”的说法。

### 2. 反事实监督覆盖

核对文件：

- `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_train_synth_v2/main_schema.jsonl`
- `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_train_synth_v2/transition_modeling.jsonl`

核对结果：

| 项目 | 数值 |
| --- | ---: |
| parent scene 数 | 543 |
| next-state 样本数 | 2001 |
| 平均每个 scene 的候选动作展开数 | 3.685 |
| candidate 覆盖不一致 scene 数 | 0 |

每个 parent scene 的 next-state 样本数分布：

| 每个 scene 展开条数 | scene 数 |
| ---: | ---: |
| 2 | 87 |
| 3 | 59 |
| 4 | 335 |
| 5 | 62 |

这支持素材包里“同一场景下多个候选动作形成反事实监督”的说法。

### 3. 目标测试集

来源文件：

`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`

核对结果：

| 项目 | 数值 |
| --- | ---: |
| 总条数 | 30 |
| QA 状态 | 30 条 `qa_reviewed_pass` |
| Greet | 6 |
| Elicit | 6 |
| Inform | 6 |
| Recommend | 6 |
| Hold | 6 |

这支持素材包里“30 条测试视频，每类 6 条，人工 QA 通过”的说法。

### 4. 动作选择训练数据

来源文件：

`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl`

核对结果：

| 动作 | 条数 |
| --- | ---: |
| Greet | 26 |
| Elicit | 41 |
| Inform | 41 |
| Recommend | 41 |
| Hold | 41 |
| **总计** | **190** |

来源组成来自：

`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage2_target_v2_balanced_summary.json`

| 来源 | 条数 |
| --- | ---: |
| target 原始 71 条 | 71 |
| Greet 增强 15 条 | 15 |
| general policy balancing | 104 |

这支持素材包里“190 条均衡动作选择训练数据”的说法。

### 5. 主结果指标

来源文件：

`/tmp/a3_full_targetv2_eval/stage_conditioned_lambda0.json`

核对结果：

| 指标 | 数值 |
| --- | ---: |
| parsed macro F1 | 0.640989 |
| strict macro F1 | 0.622857 |
| parse rate | 28 / 30 = 0.933 |
| go/no-go macro F1 | 0.591837 |
| no-go precision | 0.500 |
| no-go recall | 0.200 |

每类动作 F1：

| 动作 | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 0.800 | 1.000 | 0.667 | 6 | 4 |
| Elicit | 0.750 | 0.600 | 1.000 | 6 | 10 |
| Inform | 0.714 | 0.625 | 0.833 | 6 | 8 |
| Recommend | 0.600 | 0.750 | 0.500 | 6 | 4 |
| Hold | 0.250 | 0.500 | 0.167 | 6 | 2 |

这支持素材包里的主结果表和 per-act 表。

### 6. 消融与 baseline 数字

候选策略消融来自同一组评估输出：

| 文件 | parsed macro F1 | parse rate |
| --- | ---: | ---: |
| `/tmp/a3_full_targetv2_eval/stage_conditioned_lambda0.json` | 0.641 | 0.933 |
| `/tmp/a3_full_targetv2_eval/stage_conditioned_lambda1.json` | 0.633 | 0.900 |
| `/tmp/a3_full_targetv2_eval/all5_explicit.json` | 0.504 | 0.967 |

小规模目标场景动作选择训练结果来自：

`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/2026-05-23_a3_minimal_reality_check.md`

其中 stage-conditioned λ=0.0 的 parsed macro F1 为 `0.390`。

不做动作选择训练的动作选择 probe 来自：

`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/2026-05-22_pathC_probe_stage_conditioned.md`

其中 parsed-only macro F1 为 `0.240`，strict macro F1 为 `0.227`，random-candidate baseline 为 `0.414`。

always-X baseline 的 `0.067` 来自 balanced 30 条测试集的闭式计算：每类 6 条、共 5 类，永远预测某一类时，该类 precision=0.2、recall=1.0、F1=0.333，macro F1=`0.333/5=0.067`。

### 7. 专家知识库计数

来源文件：

- `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/piwm_data/expert_corpus/distilled/conditional_rules.jsonl`
- `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/piwm_data/expert_corpus/distilled/extracted_principles.jsonl`

核对结果：

| 项目 | 数值 |
| --- | ---: |
| conditional rules | 78 |
| extracted principles | 27 |

这支持素材包里“78 条规则 + 27 条原理”的说法。

## 已修正内容

| 原写法 | 问题 | 已改为 |
| --- | --- | --- |
| 只学顾客理解，不学动作选择 | 少说了 `next_state_prediction` 动作后果预测 | 只学顾客状态与动作后果，不学动作选择 |
| 真实门店视频已收集 40 条 | 当前仓库未核到可评测 index | 目标 50 条；当前仓库未核到可评测 index |
| 3 位销售员 Fleiss κ 标注包已就绪 | 当前可核到专家材料来源，但 Fleiss κ 未完成 | 专家材料已入库，Fleiss κ 未完成 |

## 仍需确认

1. **真实视频 40 条的路径**：如果要在论文里写“已收集 40 条”，需要补充当前仓库或服务器上的可追溯 index 路径，例如包含视频 ID、文件路径、动作标签、QA 状态的 JSON/CSV。
2. **Zero-shot 动作选择 baseline**：素材包中仍是“待补”，不能写成已完成实验。
3. **推理时反事实规划数字**：当前素材包把它写为待补实验，这是正确的，不能写成已完成主结果。

## 当前可安全引用的论文数字

可以直接引用：

- 5-act：Greet / Elicit / Inform / Recommend / Hold。
- Stage-1 数据：543 scenes → 2544 examples，其中 543 user-intent、2001 next-state。
- 反事实监督：平均每个 scene 3.685 个候选动作展开，candidate 覆盖一致性 100%。
- Stage-2 动作选择训练：190 rows，分布为 Greet 26 / 其余四类各 41。
- 目标测试集：30 rows，每类 6 条，30 条 QA pass。
- 主结果：parsed macro F1 = 0.641，strict macro F1 = 0.623，parse rate = 0.933。
- per-act F1：Greet 0.800 / Elicit 0.750 / Inform 0.714 / Recommend 0.600 / Hold 0.250。
- 候选策略消融：all-5 = 0.504，stage-conditioned = 0.641，stage-conditioned + Hold prior = 0.633。
- 数据组成消融：不做动作选择训练 = 0.240，小规模目标场景动作选择训练 = 0.390，均衡动作选择训练 = 0.641。
- 理论来源计数：78 条规则 + 27 条原理。

暂时不能直接引用为事实：

- “真实视频已收集 40 条”。
- “Fleiss κ 标注已完成”。
- “推理时反事实规划已带来提升”。
