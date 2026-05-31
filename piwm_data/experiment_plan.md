# PIWM Experiment Plan

## 1. Scope

This file records the current training/evaluation experiment design for the PIWM data pipeline. The operational 5-act set is fixed as `Greet / Elicit / Inform / Recommend / Hold`; `Reassure` is excluded from the current main training/evaluation path and retained only for source/compatibility analysis.

## 2. A0-A4 Ablation Design

| ID | Stage-1 training | Stage-2 training | Evaluation | Purpose |
|---|---|---|---|---|
| A0 | None | Target 71 only | 30 balanced target test | Direct small-data target baseline. Shows how weak/strong the target-only action learner is without general state/world-model pretraining. |
| A1 | State-only general checkpoint | Target 71 only | 30 balanced target test + general QA check | Tests whether visual state recognition alone helps target action selection. |
| A2 | State + transition general checkpoint | Target 71 only | 30 balanced target test + general QA check | Tests whether action-conditioned next-state/world-model supervision helps beyond state recognition. |
| A3 | State + transition general checkpoint | General policy/action data + target 71 | 30 balanced target test + general QA check | Tests whether general retail policy transfer improves target action selection. |
| A4 | State + transition general checkpoint | General policy/action data + weighted target 71 | 30 balanced target test + general QA check | Main model. Tests whether target-weighted adaptation improves low-resource target performance without losing general ability. |

Primary target metric:

- 5-act macro F1 on the 30-record balanced target test.
- Per-act F1 for `Greet`, `Elicit`, `Inform`, `Recommend`, and `Hold`.

Special attention:

- `Greet` and `Hold` F1 should be reported separately because they are the most important go/no-go and proactive-opening signals in the target domain.
- General QA evaluation should be rerun for A2-A4 to check catastrophic forgetting.

## 3. Current Data Entrypoints

| Role | Path | Current count |
|---|---|---:|
| Stage-1 combined general SFT | `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 |
| Stage-1 user-intent train split | `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 |
| Stage-1 next-state train split | `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 |
| Stage-1 user-intent val split | `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 |
| Stage-1 next-state val split | `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 |
| Stage-2 target train | `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | 71 |
| Target balanced action-selection eval | `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl` | 30 |

## 4. Candidate-Set Policy Pending PI Confirmation

The PI-approved direction is to move Stage-2 candidates from current imported candidate lists to stage-conditioned candidates:

| AIDA stage | Candidate acts |
|---|---|
| attention | `Greet / Elicit / Inform / Hold` |
| interest | `Elicit / Inform / Recommend / Hold` |
| desire | `Inform / Recommend / Hold` |
| action | `Greet / Recommend / Hold` |

This file records the decision, but the code/data change should only be applied after the separate dry-run impact report is reviewed.

