5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# 2026-05-25 4 维度重跑评估附录

## Intent taxonomy

- Full intent label space observed: `compare_value_for_money, confirm_choice, explore_options, leave_without_purchase, negotiate_price, no_clear_intent, request_demonstration, seek_reassurance`
- Core intent label space excludes `seek_reassurance` and `negotiate_price`: `compare_value_for_money, confirm_choice, explore_options, leave_without_purchase, no_clear_intent, request_demonstration`

## PIWM 主模型

### target user_intent summary

- n=30, parse_rate=0.800
- stage macro F1=0.245, modal=interest 12/30
- intent full macro F1=0.069, intent core macro F1=0.046, modal=confirm_choice 23/30

### target AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 1.000 | 0.333 | 0.500 | 3 | 1 |
| interest | 0.333 | 0.400 | 0.364 | 10 | 12 |
| desire | 0.000 | 0.000 | 0.000 | 11 | 0 |
| action | 0.091 | 0.167 | 0.118 | 6 | 11 |

### target intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.174 | 0.667 | 0.276 | 6 | 23 |
| explore_options | 0.000 | 0.000 | 0.000 | 15 | 1 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 0 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 0 | 0 |

### general user_intent summary

- n=30, parse_rate=0.533
- stage macro F1=0.442, modal=action 8/30
- intent full macro F1=0.213, intent core macro F1=0.231, modal=confirm_choice 12/30

### general AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.750 | 0.750 | 0.750 | 4 | 4 |
| interest | 0.750 | 0.231 | 0.353 | 13 | 4 |
| desire | 0.000 | 0.000 | 0.000 | 6 | 0 |
| action | 0.625 | 0.714 | 0.667 | 7 | 8 |

### general intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 0 | 0 |
| confirm_choice | 0.636 | 0.636 | 0.636 | 11 | 11 |
| explore_options | 1.000 | 0.600 | 0.750 | 5 | 3 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 4 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 0 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 2 | 0 |

### combined user_intent summary

- n=60, parse_rate=0.667
- stage macro F1=0.350, modal=action 19/60
- intent full macro F1=0.083, intent core macro F1=0.114, modal=confirm_choice 35/60

### combined AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.800 | 0.571 | 0.667 | 7 | 5 |
| interest | 0.438 | 0.304 | 0.359 | 23 | 16 |
| desire | 0.000 | 0.000 | 0.000 | 17 | 0 |
| action | 0.316 | 0.462 | 0.375 | 13 | 19 |

### combined intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.324 | 0.647 | 0.431 | 17 | 34 |
| explore_options | 0.750 | 0.150 | 0.250 | 20 | 4 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 4 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 2 | 0 |

### Dim 3 next_state summary

- n=80, parse_rate=0.887, next-stage macro F1=0.565, reward MAE=0.491

### Dim 3 next-stage per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.308 | 0.667 | 0.421 | 6 | 13 |
| interest | 0.913 | 0.677 | 0.778 | 31 | 23 |
| desire | 0.520 | 0.684 | 0.591 | 19 | 25 |
| action | 0.800 | 0.333 | 0.471 | 24 | 10 |

### Dim 3 by candidate act

| candidate act | n | macro F1 | accuracy |
|---|---:|---:|---:|
| Elicit | 12 | 0.176 | 0.500 |
| Greet | 6 | 0.000 | 0.000 |
| Hold | 33 | 0.804 | 0.788 |
| Inform | 21 | 0.407 | 0.476 |
| Recommend | 8 | 0.268 | 0.500 |

### Trick 6 Reward A: stage_advance

- macro F1=0.171, candidate parse rate=0.907, modal=Elicit 11/30, candidates=97/107

| act | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| Greet | 0.500 | 0.167 | 0.250 | 6 | 2 |
| Elicit | 0.364 | 0.667 | 0.471 | 6 | 11 |
| Inform | 0.111 | 0.167 | 0.133 | 6 | 9 |
| Recommend | 0.000 | 0.000 | 0.000 | 6 | 7 |
| Hold | 0.000 | 0.000 | 0.000 | 6 | 1 |

### Trick 6 Reward B: model_score

- macro F1=0.265, candidate parse rate=0.907, modal=Elicit 8/30, candidates=97/107

| act | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| Greet | 0.667 | 0.333 | 0.444 | 6 | 3 |
| Elicit | 0.375 | 0.500 | 0.429 | 6 | 8 |
| Inform | 0.167 | 0.167 | 0.167 | 6 | 6 |
| Recommend | 0.250 | 0.333 | 0.286 | 6 | 8 |
| Hold | 0.000 | 0.000 | 0.000 | 6 | 5 |

## 仅顾客状态与动作后果训练

### target user_intent summary

- n=30, parse_rate=0.567
- stage macro F1=0.279, modal=action 13/30
- intent full macro F1=0.071, intent core macro F1=0.048, modal=confirm_choice 15/30

### target AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 1.000 | 0.667 | 0.800 | 3 | 2 |
| interest | 0.000 | 0.000 | 0.000 | 10 | 2 |
| desire | 0.000 | 0.000 | 0.000 | 11 | 0 |
| action | 0.231 | 0.500 | 0.316 | 6 | 13 |

### target intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.200 | 0.500 | 0.286 | 6 | 15 |
| explore_options | 0.000 | 0.000 | 0.000 | 15 | 2 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 0 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 0 | 0 |

### general user_intent summary

- n=30, parse_rate=0.567
- stage macro F1=0.403, modal=interest 7/30
- intent full macro F1=0.194, intent core macro F1=0.220, modal=confirm_choice 13/30

### general AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.750 | 0.750 | 0.750 | 4 | 4 |
| interest | 0.571 | 0.308 | 0.400 | 13 | 7 |
| desire | 0.000 | 0.000 | 0.000 | 6 | 0 |
| action | 0.500 | 0.429 | 0.462 | 7 | 6 |

### general intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 0 | 0 |
| confirm_choice | 0.600 | 0.545 | 0.571 | 11 | 10 |
| explore_options | 1.000 | 0.600 | 0.750 | 5 | 3 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 4 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 0 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 2 | 0 |

### combined user_intent summary

- n=60, parse_rate=0.567
- stage macro F1=0.349, modal=action 19/60
- intent full macro F1=0.079, intent core macro F1=0.111, modal=confirm_choice 28/60

### combined AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.833 | 0.714 | 0.769 | 7 | 6 |
| interest | 0.444 | 0.174 | 0.250 | 23 | 9 |
| desire | 0.000 | 0.000 | 0.000 | 17 | 0 |
| action | 0.316 | 0.462 | 0.375 | 13 | 19 |

### combined intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.360 | 0.529 | 0.429 | 17 | 25 |
| explore_options | 0.600 | 0.150 | 0.240 | 20 | 5 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 4 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 2 | 0 |

### Dim 3 next_state summary

- n=80, parse_rate=1.000, next-stage macro F1=0.587, reward MAE=0.458

### Dim 3 next-stage per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.353 | 1.000 | 0.522 | 6 | 17 |
| interest | 0.875 | 0.903 | 0.889 | 31 | 32 |
| desire | 0.556 | 0.789 | 0.652 | 19 | 27 |
| action | 1.000 | 0.167 | 0.286 | 24 | 4 |

### Dim 3 by candidate act

| candidate act | n | macro F1 | accuracy |
|---|---:|---:|---:|
| Elicit | 12 | 0.214 | 0.750 |
| Greet | 6 | 0.000 | 0.000 |
| Hold | 33 | 0.908 | 0.939 |
| Inform | 21 | 0.444 | 0.524 |
| Recommend | 8 | 0.100 | 0.250 |

### Trick 6 Reward A: stage_advance

- macro F1=0.165, candidate parse rate=0.981, modal=Elicit 11/30, candidates=105/107

| act | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| Greet | 0.000 | 0.000 | 0.000 | 6 | 2 |
| Elicit | 0.364 | 0.667 | 0.471 | 6 | 11 |
| Inform | 0.273 | 0.500 | 0.353 | 6 | 11 |
| Recommend | 0.000 | 0.000 | 0.000 | 6 | 5 |
| Hold | 0.000 | 0.000 | 0.000 | 6 | 1 |

### Trick 6 Reward B: model_score

- macro F1=0.418, candidate parse rate=0.981, modal=Inform 9/30, candidates=105/107

| act | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| Greet | 0.625 | 0.833 | 0.714 | 6 | 8 |
| Elicit | 0.667 | 0.333 | 0.444 | 6 | 3 |
| Inform | 0.333 | 0.500 | 0.400 | 6 | 9 |
| Recommend | 0.250 | 0.167 | 0.200 | 6 | 4 |
| Hold | 0.333 | 0.333 | 0.333 | 6 | 6 |

## Zero-shot Qwen2.5-VL-7B

### target user_intent summary

- n=30, parse_rate=0.833
- stage macro F1=0.206, modal=interest 16/30
- intent full macro F1=0.093, intent core macro F1=0.078, modal=explore_options 15/30

### target AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.000 | 0.000 | 0.000 | 3 | 4 |
| interest | 0.375 | 0.600 | 0.462 | 10 | 16 |
| desire | 0.000 | 0.000 | 0.000 | 11 | 0 |
| action | 0.400 | 0.333 | 0.364 | 6 | 5 |

### target intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.000 | 0.000 | 0.000 | 6 | 0 |
| explore_options | 0.467 | 0.467 | 0.467 | 15 | 15 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 0 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 5 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 0 | 5 |

### general user_intent summary

- n=30, parse_rate=0.800
- stage macro F1=0.153, modal=interest 23/30
- intent full macro F1=0.012, intent core macro F1=0.017, modal=explore_options 22/30

### general AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.000 | 0.000 | 0.000 | 4 | 0 |
| interest | 0.478 | 0.846 | 0.611 | 13 | 23 |
| desire | 0.000 | 0.000 | 0.000 | 6 | 0 |
| action | 0.000 | 0.000 | 0.000 | 7 | 1 |

### general intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 0 | 0 |
| confirm_choice | 0.000 | 0.000 | 0.000 | 11 | 0 |
| explore_options | 0.067 | 0.200 | 0.100 | 5 | 15 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 4 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 0 | 0 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 2 | 2 |

### combined user_intent summary

- n=60, parse_rate=0.817
- stage macro F1=0.190, modal=interest 39/60
- intent full macro F1=0.035, intent core macro F1=0.053, modal=explore_options 37/60

### combined AIDA per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.000 | 0.000 | 0.000 | 7 | 4 |
| interest | 0.436 | 0.739 | 0.548 | 23 | 39 |
| desire | 0.000 | 0.000 | 0.000 | 17 | 0 |
| action | 0.333 | 0.154 | 0.211 | 13 | 6 |

### combined intent core per-class F1

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| compare_value_for_money | 0.000 | 0.000 | 0.000 | 6 | 0 |
| confirm_choice | 0.000 | 0.000 | 0.000 | 17 | 0 |
| explore_options | 0.267 | 0.400 | 0.320 | 20 | 30 |
| leave_without_purchase | 0.000 | 0.000 | 0.000 | 4 | 0 |
| no_clear_intent | 0.000 | 0.000 | 0.000 | 3 | 5 |
| request_demonstration | 0.000 | 0.000 | 0.000 | 2 | 7 |

### Dim 3 next_state summary

- 已修复 zero-shot no-lora bug 后重跑。
- n=80, parse_rate=0.250, strict next-stage macro F1=0.108, parsed-only next-stage macro F1=0.269, reward MAE=0.542。
- raw output: `reports/rerun_eval_20260525/zero_shot_qwen_dim3_fixed.json`

### Dim 3 next-stage per-class F1 (strict, parse failure counted as wrong)

| label | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| attention | 0.000 | 0.000 | 0.000 | 6 | 6 |
| interest | 0.500 | 0.194 | 0.279 | 31 | 12 |
| desire | 0.000 | 0.000 | 0.000 | 19 | 0 |
| action | 1.000 | 0.083 | 0.154 | 24 | 2 |

### Dim 3 by candidate act

| candidate act | n | macro F1 | accuracy |
|---|---:|---:|---:|
| Elicit | 12 | 0.133 | 0.333 |
| Greet | 6 | 0.000 | 0.000 |
| Hold | 33 | 0.125 | 0.061 |
| Inform | 21 | 0.077 | 0.095 |
| Recommend | 8 | 0.000 | 0.000 |

### Trick 6 Reward A: stage_advance

- 已修复 zero-shot no-lora bug 后重跑。
- macro F1=0.247, candidate parse rate=0.262, modal=Inform 10/30, candidates=28/107。
- raw output: `reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_a_fixed.json`

| act | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| Greet | 0.500 | 0.500 | 0.500 | 6 | 6 |
| Elicit | 0.250 | 0.333 | 0.286 | 6 | 8 |
| Inform | 0.200 | 0.333 | 0.250 | 6 | 10 |
| Recommend | 0.000 | 0.000 | 0.000 | 6 | 2 |
| Hold | 0.250 | 0.167 | 0.200 | 6 | 4 |

### Trick 6 Reward B: model_score

- 已修复 zero-shot no-lora bug 后重跑。
- macro F1=0.372, candidate parse rate=0.262, modal=Elicit 11/30, candidates=28/107。
- raw output: `reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_b_fixed.json`

| act | precision | recall | f1 | support | pred_count |
|---|---:|---:|---:|---:|---:|
| Greet | 1.000 | 0.667 | 0.800 | 6 | 4 |
| Elicit | 0.455 | 0.833 | 0.588 | 6 | 11 |
| Inform | 0.200 | 0.333 | 0.250 | 6 | 10 |
| Recommend | 0.000 | 0.000 | 0.000 | 6 | 2 |
| Hold | 0.333 | 0.167 | 0.222 | 6 | 3 |

## PIWM 主模型 confusion matrix

### Dim 1 AIDA combined

| gold \ pred | attention | interest | desire | action | UNPARSED | OTHER |
|---|---:|---:|---:|---:|---:|---:|
| attention | 4 | 0 | 0 | 3 | 0 | 0 |
| interest | 0 | 7 | 0 | 3 | 13 | 0 |
| desire | 1 | 6 | 0 | 7 | 3 | 0 |
| action | 0 | 3 | 0 | 6 | 4 | 0 |

### Dim 2 intent combined

| gold \ pred | compare_value_for_money | confirm_choice | explore_options | leave_without_purchase | negotiate_price | no_clear_intent | request_demonstration | seek_reassurance | UNPARSED | OTHER |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| compare_value_for_money | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| confirm_choice | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| explore_options | 0 | 12 | 3 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| leave_without_purchase | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| negotiate_price | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| no_clear_intent | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| request_demonstration | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| seek_reassurance | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |

### Dim 3 next-stage

| gold \ pred | attention | interest | desire | action | UNPARSED | OTHER |
|---|---:|---:|---:|---:|---:|---:|
| attention | 4 | 1 | 1 | 0 | 0 | 0 |
| interest | 2 | 21 | 5 | 0 | 3 | 0 |
| desire | 0 | 1 | 13 | 2 | 3 | 0 |
| action | 7 | 0 | 6 | 8 | 3 | 0 |

## Coverage 与 prompt 证据

- Dim 3 scored rows: 80 covered candidates。
- Dim 3 prompt evidence file: `reports/rerun_eval_20260525/dim3_deliberation_prompt_evidence.json`。
- 当前报告未补 27 条无 gold placeholder；该 coverage limitation 仍应保留在论文素材包 limitation 中。
