# PIWM End-to-End Best-Action Evaluation

- eval date: 2026-05-26
- samples: 60 (general, target)
- checkpoint: `/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500`
- Step 1 raw: `reports/end_to_end_eval_20260525/step1_predicted_state.jsonl`
- Step 2 raw: `reports/end_to_end_eval_20260525/step2_predicted_action.jsonl`

## Main Target Result

| Setting | Macro F1 | Parse rate (step 1) | Parse rate (step 2) |
|---|---:|---:|---:|
| PIWM with gold state (Dim 4 original) | 0.641 | - | 0.933 |
| PIWM end-to-end (自推 state) | 0.295 | 0.800 | 0.533 |
| Random | 0.414 | - | - |

## Error Propagation

| Subset | N samples | Best-action F1 |
|---|---:|---:|
| Step 1 stage 预测正确 | 18 | 0.531 |
| Step 1 stage 预测错误 | 23 | 0.359 |

Note: the two rows above include only the 41 samples where Step 1 state parsing succeeded. The 19 Step 1 parse-failed samples are counted as best-action errors in the main F1 denominator.

## Per-Action Breakdown (Combined Evaluated Set)

| act | precision | recall | F1 | support |
|---|---:|---:|---:|---:|
| Greet | 0.000 | 0.000 | 0.000 | 6 |
| Elicit | 0.900 | 0.474 | 0.621 | 19 |
| Inform | 0.500 | 0.083 | 0.143 | 12 |
| Recommend | 0.583 | 0.700 | 0.636 | 10 |
| Hold | 0.714 | 0.385 | 0.500 | 13 |

## Optional 60-Sample Breakdown

| Domain | N | Macro F1 | Step 1 parse rate | Step 2 parse rate | Modal prediction |
|---|---:|---:|---:|---:|---|
| target | 30 | 0.295 | 0.800 | 0.533 | PARSE_FAIL / 14 / 30 |
| general | 30 | 0.438 | 0.567 | 0.533 | PARSE_FAIL / 14 / 30 |
| combined | 60 | 0.380 | 0.683 | 0.533 | PARSE_FAIL / 28 / 60 |
