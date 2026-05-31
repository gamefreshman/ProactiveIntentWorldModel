5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# PIWM 主模型 4 维度完整评估

## 1. Headline

维度 3 的 next-state 指标只在有 transition gold 的 80 条候选动作上评分；另有 27 条 stage-conditioned placeholder candidate 无 gold，仅作为 coverage limitation 记录。

| Model | Dim 1 AIDA F1 | Dim 2 intent F1 core | Dim 3 next-state F1 | Dim 4 best-act F1 |
| --- | ---: | ---: | ---: | ---: |
| Simple baseline | 0.134 | 0.167 | 0.140 | 0.414 |
| Qwen2.5-VL-7B zero-shot | 0.230 | 0.125 | 0.184 | 0.313 |
| Customer-state-and-effect training only | 0.384 | 0.088 | 0.155 | 0.240 |
| PIWM main model | 0.264 | 0.074 | 0.190 | 0.641 |

**PIWM 主模型 next-state macro F1（80 条有 gold 的候选动作）：0.190。**

## 2. Next-state Coverage

- stage-conditioned candidate 总数：107
- 有 transition gold 并参与评分：80
- 无 transition gold、不参与评分：27
- 无 gold 候选按 act 分布：`{'Elicit': 1, 'Greet': 3, 'Inform': 4, 'Recommend': 19}`

这 27 条缺口来自 stage-conditioned candidate 补齐逻辑生成的 placeholder candidate；它们没有精确的 `transition_modeling` gold，因此不纳入 F1/MAE，避免用规则补标签污染论文数字。该限制应写入论文 limitation 正文。

## 3. Per-class Results

### Qwen2.5-VL-7B zero-shot

- AIDA stage: macro F1=0.230; accuracy=0.320; parse=0.833.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| attention | 0.000 | 0.000 | 0.000 | 2 | 4 |
| interest | 0.522 | 0.375 | 0.857 | 7 | 16 |
| desire | 0.000 | 0.000 | 0.000 | 11 | 0 |
| action | 0.400 | 0.400 | 0.400 | 5 | 5 |

- Intent full: macro F1=0.125; accuracy=0.280; parse=0.833.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 5 | 0 |
| confirm_choice | 0.000 | 0.000 | 0.000 | 5 | 0 |
| explore_options | 0.500 | 0.467 | 0.538 | 13 | 15 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 2 | 5 |

- Intent core, excluding seek_reassurance and negotiate_price: macro F1=0.125; accuracy=0.280; parse=0.833.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 5 | 0 |
| confirm_choice | 0.000 | 0.000 | 0.000 | 5 | 0 |
| explore_options | 0.500 | 0.467 | 0.538 | 13 | 15 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 2 | 5 |

- Next stage, 80 scored candidates: macro F1=0.184; accuracy=0.293; parse=0.938; reward MAE=0.482.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| attention | 0.174 | 0.100 | 0.667 | 6 | 40 |
| interest | 0.562 | 0.514 | 0.621 | 29 | 35 |
| desire | 0.000 | 0.000 | 0.000 | 17 | 0 |
| action | 0.000 | 0.000 | 0.000 | 23 | 0 |

- Best act: macro F1=0.313; accuracy=0.429; parse=0.233.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 0.000 | 0.000 | 0.000 | 1 | 0 |
| Elicit | 0.500 | 1.000 | 0.333 | 3 | 1 |
| Inform | 0.000 | 0.000 | 0.000 | 0 | 1 |
| Recommend | 0.667 | 1.000 | 0.500 | 2 | 1 |
| Hold | 0.400 | 0.250 | 1.000 | 1 | 4 |

### Customer-state-and-effect training only

- AIDA stage: macro F1=0.384; accuracy=0.333; parse=1.000.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| attention | 0.800 | 1.000 | 0.667 | 3 | 2 |
| interest | 0.476 | 0.455 | 0.500 | 10 | 11 |
| desire | 0.000 | 0.000 | 0.000 | 11 | 0 |
| action | 0.261 | 0.176 | 0.500 | 6 | 17 |

- Intent full: macro F1=0.088; accuracy=0.200; parse=1.000.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.353 | 0.214 | 1.000 | 6 | 28 |
| explore_options | 0.000 | 0.000 | 0.000 | 15 | 2 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |

- Intent core, excluding seek_reassurance and negotiate_price: macro F1=0.088; accuracy=0.200; parse=1.000.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.353 | 0.214 | 1.000 | 6 | 28 |
| explore_options | 0.000 | 0.000 | 0.000 | 15 | 2 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |

- Next stage, 80 scored candidates: macro F1=0.155; accuracy=0.175; parse=1.000; reward MAE=0.478.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| attention | 0.227 | 0.132 | 0.833 | 6 | 38 |
| interest | 0.195 | 0.400 | 0.129 | 31 | 10 |
| desire | 0.196 | 0.156 | 0.263 | 19 | 32 |
| action | 0.000 | 0.000 | 0.000 | 24 | 0 |

- Best act: macro F1=0.240; accuracy=0.308; parse=0.867.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 0.000 | 0.000 | 0.000 | 5 | 0 |
| Elicit | 0.286 | 1.000 | 0.167 | 6 | 1 |
| Inform | 0.250 | 0.200 | 0.333 | 3 | 5 |
| Recommend | 0.250 | 0.500 | 0.167 | 6 | 2 |
| Hold | 0.417 | 0.278 | 0.833 | 6 | 18 |

### PIWM main model

- AIDA stage: macro F1=0.264; accuracy=0.267; parse=1.000.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| attention | 0.500 | 1.000 | 0.333 | 3 | 1 |
| interest | 0.444 | 0.353 | 0.600 | 10 | 17 |
| desire | 0.000 | 0.000 | 0.000 | 11 | 0 |
| action | 0.111 | 0.083 | 0.167 | 6 | 12 |

- Intent full: macro F1=0.074; accuracy=0.167; parse=1.000.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.294 | 0.179 | 0.833 | 6 | 28 |
| explore_options | 0.000 | 0.000 | 0.000 | 15 | 1 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |

- Intent core, excluding seek_reassurance and negotiate_price: macro F1=0.074; accuracy=0.167; parse=1.000.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.294 | 0.179 | 0.833 | 6 | 28 |
| explore_options | 0.000 | 0.000 | 0.000 | 15 | 1 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |

- Next stage, 80 scored candidates: macro F1=0.190; accuracy=0.200; parse=1.000; reward MAE=0.421.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| attention | 0.270 | 0.161 | 0.833 | 6 | 31 |
| interest | 0.250 | 0.353 | 0.194 | 31 | 17 |
| desire | 0.163 | 0.133 | 0.211 | 19 | 30 |
| action | 0.077 | 0.500 | 0.042 | 24 | 2 |

- Best act: macro F1=0.641; accuracy=0.679; parse=0.933.

| Label | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 0.800 | 1.000 | 0.667 | 6 | 4 |
| Elicit | 0.750 | 0.600 | 1.000 | 6 | 10 |
| Inform | 0.769 | 0.625 | 1.000 | 5 | 8 |
| Recommend | 0.600 | 0.750 | 0.500 | 6 | 4 |
| Hold | 0.286 | 0.500 | 0.200 | 5 | 2 |

## 4. Failure Chain Analysis

### 表 A：链路条件成功率

| Condition | Rate | Numerator / Denominator |
| --- | ---: | ---: |
| P(intent 对 | stage 对) | 0.125 | 1 / 8 |
| P(intent 对 | stage 错) | 0.182 | 4 / 22 |
| P(next_state 对 | stage+intent 对) | 0.000 | 0 / 1 |
| P(next_state 对 | stage 或 intent 错) | 0.241 | 7 / 29 |
| P(best_act 对 | stage+intent+next_state 全对) | 待补 | 0 / 0 |
| P(best_act 对 | 其他情况) | 0.633 | 19 / 30 |

### 表 B：错误类型分布

| Error type | Count | Percent of action errors |
| --- | ---: | ---: |
| Type 1 stage error propagation | 8 | 0.727 |
| Type 2 intent error after correct stage | 3 | 0.273 |
| Type 3 next-state error after stage+intent | 0 | 0.000 |
| Type 4 strategy bottleneck | 0 | 0.000 |
| Unknown next-state coverage | 0 | 0.000 |

### 表 C：stage 错误对决策候选集的影响

| Scene | Gold stage | Pred stage | Gold candidates | Pred candidates | Action correct |
| --- | --- | --- | --- | --- | ---: |
| target_piwm_700 | interest | action | Elicit/Inform/Recommend/Hold | Greet/Recommend/Hold | True |
| target_piwm_702 | interest | action | Elicit/Inform/Recommend/Hold | Greet/Recommend/Hold | True |
| target_piwm_704 | attention | action | Greet/Elicit/Inform/Hold | Greet/Recommend/Hold | True |
| target_piwm_705 | attention | action | Greet/Elicit/Inform/Hold | Greet/Recommend/Hold | True |
| target_piwm_708 | interest | action | Elicit/Inform/Recommend/Hold | Greet/Recommend/Hold | True |
| target_piwm_712 | desire | interest | Inform/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |
| target_piwm_713 | desire | interest | Inform/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |
| target_piwm_714 | desire | action | Inform/Recommend/Hold | Greet/Recommend/Hold | False |
| target_piwm_719 | action | interest | Greet/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |
| target_piwm_720 | action | interest | Greet/Recommend/Hold | Elicit/Inform/Recommend/Hold | False |
| target_piwm_721 | action | interest | Greet/Recommend/Hold | Elicit/Inform/Recommend/Hold | False |
| target_piwm_760 | desire | action | Inform/Recommend/Hold | Greet/Recommend/Hold | False |
| target_piwm_762 | desire | action | Inform/Recommend/Hold | Greet/Recommend/Hold | False |
| target_piwm_763 | desire | interest | Inform/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |
| target_piwm_764 | desire | interest | Inform/Recommend/Hold | Elicit/Inform/Recommend/Hold | False |
| target_piwm_765 | desire | action | Inform/Recommend/Hold | Greet/Recommend/Hold | True |
| target_piwm_766 | desire | action | Inform/Recommend/Hold | Greet/Recommend/Hold | True |
| target_piwm_789 | action | interest | Greet/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |
| target_piwm_790 | action | interest | Greet/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |
| target_piwm_812 | desire | interest | Inform/Recommend/Hold | Elicit/Inform/Recommend/Hold | False |
| target_piwm_813 | interest | action | Elicit/Inform/Recommend/Hold | Greet/Recommend/Hold | False |
| target_piwm_817 | desire | interest | Inform/Recommend/Hold | Elicit/Inform/Recommend/Hold | True |

stage 错误样本 action accuracy：0.636 (14/22)

### 表 D：per-act 错误归因

| Gold act | Total errors | Stage error | Intent error | Next-state error | Strategy bottleneck | Unknown next-state |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Greet | 2 | 2 | 0 | 0 | 0 | 0 |
| Elicit | 0 | 0 | 0 | 0 | 0 | 0 |
| Inform | 1 | 1 | 0 | 0 | 0 | 0 |
| Recommend | 3 | 3 | 0 | 0 | 0 | 0 |
| Hold | 5 | 2 | 3 | 0 | 0 | 0 |


## 6. Raw Output Index

- Raw directory: `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/4dim_eval_raw_20260524`
- 输入集：`target_user_intent.jsonl` / `next_state_covered80.jsonl` / `next_state_unscored27.jsonl` / `target_action_selection.jsonl`
- 每个模型的推理输出按 `base_qwen25vl7b_*`、`customer_state_effect_only_*`、`piwm_main_*` 命名。
