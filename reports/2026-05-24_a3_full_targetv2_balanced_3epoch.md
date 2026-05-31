5-act self-check: Greet/Elicit/Inform/Recommend/Hold; Reassure is excluded from operational training/eval.
# A3 Full Target-v2 Balanced 3-Epoch Evaluation
## Run
- Training run: `a3full-20260522-220941-px1003520-ml8192`
- Selected checkpoint for eval: `checkpoint-500` (trainer best_model_checkpoint; final `checkpoint-513` also exists)
- Train completed: 513/513 steps, final train_loss 0.03957246, final eval_loss 0.01179329; best eval_loss at checkpoint-500 was 0.01173102.
- Eval set: 30 balanced target frontcam action-selection rows, QA-reviewed pass.
- 5-act set: `Greet / Elicit / Inform / Recommend / Hold`; no A4 was started.

## Summary
| Eval config | Parse | Parsed action macro F1 | Action accuracy | Go/no-go macro F1 |
|---|---:|---:|---:|---:|
| stage-conditioned, Hold prior lambda=0.0 | 28/30 (0.933) | 0.641 | 0.679 | 0.592 |
| stage-conditioned, Hold prior lambda=1.0 | 27/30 (0.900) | 0.633 | 0.667 | 0.590 |
| all-5-act explicit | 29/30 (0.967) | 0.504 | 0.552 | 0.442 |

Best observed config is **stage-conditioned with Hold prior lambda=0.0**, with parsed action macro F1 **0.641**. This is above A3_minimal parsed macro F1 0.390, Path C probe 0.227, and random-candidate baseline 0.414.

## Stage-conditioned, lambda=0.0
- Remote JSON: `/root/lanyun-fs/ProactiveIntentWorldModel/reports/a3_full_targetv2_balanced_20260523/stage_conditioned_lambda0.json`
- Parse: 28/30 (0.933)

| Act | F1 | Precision | Recall | Support | Pred count | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Greet | 0.800 | 1.000 | 0.667 | 6 | 4 | 4 | 0 | 2 |
| Elicit | 0.750 | 0.600 | 1.000 | 6 | 10 | 6 | 4 | 0 |
| Inform | 0.714 | 0.625 | 0.833 | 6 | 8 | 5 | 3 | 1 |
| Recommend | 0.600 | 0.750 | 0.500 | 6 | 4 | 3 | 1 | 3 |
| Hold | 0.250 | 0.500 | 0.167 | 6 | 2 | 1 | 1 | 5 |

Parse errors:
- `target_piwm_714`: <rationale>对比式推荐满足顾客对价格差异的直接需求，同时降低决策成本，提升信任感。</rationale> <chosen>Recommend_price_difference_814_0624a17ced7a</chosen> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action> <intervention_utterance>我帮您把
- `target_piwm_812`: <rationale>直接推荐降低其决策成本，但可能增加压力。</rationale> <chosen>Recommend_8d7f8993e333</chosen> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action> <intervention_utterance>这款可以作为一个参考选项。</introduction>

## Stage-conditioned, lambda=1.0
- Remote JSON: `/root/lanyun-fs/ProactiveIntentWorldModel/reports/a3_full_targetv2_balanced_20260523/stage_conditioned_lambda1.json`
- Parse: 27/30 (0.900)

| Act | F1 | Precision | Recall | Support | Pred count | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Greet | 0.800 | 1.000 | 0.667 | 6 | 4 | 4 | 0 | 2 |
| Elicit | 0.750 | 0.600 | 1.000 | 6 | 10 | 6 | 4 | 0 |
| Inform | 0.615 | 0.571 | 0.667 | 6 | 7 | 4 | 3 | 2 |
| Recommend | 0.600 | 0.750 | 0.500 | 6 | 4 | 3 | 1 | 3 |
| Hold | 0.250 | 0.500 | 0.167 | 6 | 2 | 1 | 1 | 5 |

Parse errors:
- `target_piwm_713`: <rationale>对比式沟通降低决策压力，帮助她主动确认差异，提升信任感。</rationale> <chosen>Inform_desire_with_detail_difference_542ba586daa0</chosen> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action> <intervention_utterance>我详细说明
- `target_piwm_714`: <rationale>对比式推荐满足顾客对价格差异的直接需求，同时降低决策成本，提升信任感。</rationale> <chosen>Recommend_price_difference_803955055</chosen> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action> <intervention_utterance>我帮您把价格差和优惠信
- `target_piwm_812`: <rationale>直接推荐降低其决策成本，但可能增加压力。</rationale> <chosen>Recommend_8d7f8993e333</chosen> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action> <intervention_utterance>这款可以作为一个参考选项。</introduction>

## All-5-act explicit
- Remote JSON: `/root/lanyun-fs/ProactiveIntentWorldModel/reports/a3_full_targetv2_balanced_20260523/all5_explicit.json`
- Parse: 29/30 (0.967)

| Act | F1 | Precision | Recall | Support | Pred count | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Greet | 0.667 | 1.000 | 0.500 | 6 | 3 | 3 | 0 | 3 |
| Elicit | 0.545 | 0.375 | 1.000 | 6 | 16 | 6 | 10 | 0 |
| Inform | 0.364 | 0.400 | 0.333 | 6 | 5 | 2 | 3 | 4 |
| Recommend | 0.909 | 1.000 | 0.833 | 6 | 5 | 5 | 0 | 1 |
| Hold | 0.000 | 0.000 | 0.000 | 6 | 0 | 0 | 0 | 6 |

Parse errors:
- `target_piwm_713`: <rationale>对比式引导帮助顾客主动确认差异，降低决策成本，提升信任感。</rationale> <chosen>Compare_desire_stage_conditioned_target_piwm_713_50053014d173cc</chosen> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action> <intervention_

## Interpretation
- The target_v2 balancing changed the result from a marginal A3_minimal signal into a viable A3 signal on the 30-row target test.
- Hold prior calibration did not help here: lambda=1.0 slightly lowered macro F1 compared with lambda=0.0.
- Stage-conditioned candidates are materially better than all-5 explicit candidates in this run.
- Remaining decision point for PI/Claude: whether to run full A4 with target repeat or first inspect per-act errors, especially parse failures and low-recall classes.
