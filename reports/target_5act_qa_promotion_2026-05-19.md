# Target 5-Act QA Promotion Report

Date: 2026-05-19

## Summary

The revised balanced 30-record target-frontcam 5-act test split has been promoted from `qa_pending_project_lead_review` to `qa_reviewed_pass` after project-lead review.

No commit was made.

## Reviewed Split

- source dataset: `PIWM-Target-Frontcam-v1`
- QA packet: `data/official/piwm_target_v1/qa_review_target30_5act/`
- reviewer: `Project lead human QA`
- reviewed_at: `2026-05-19`
- review_type: `project_lead_human_review_after_5act_rebalance`
- reviewed records: 30
- pass records: 30
- fail records: 0
- warning records: 0

Balanced test distribution:

| Act | Records |
|---|---:|
| Greet | 6 |
| Elicit | 6 |
| Inform | 6 |
| Recommend | 6 |
| Hold | 6 |
| Reassure | 0 |

## Data Surfaces Updated

| File | Updated QA surface |
|---|---|
| `data/official/piwm_target_v1/main_schema.jsonl` | 30 test records -> `qa_reviewed_pass` |
| `data/official/piwm_target_v1/state_inference.jsonl` | 30 test rows -> `qa_reviewed_pass` |
| `data/official/piwm_target_v1/transition_modeling.jsonl` | 120 test transition rows -> `qa_reviewed_pass` |
| `data/official/piwm_target_v1/policy_preference.jsonl` | 30 test policy rows -> `qa_reviewed_pass` |
| `data/official/ms_swift/piwm_train_target_specialization_v1.jsonl` | 180 legacy target test rows -> `qa_reviewed_pass` |
| `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl` | 90 current eval rows -> `qa_reviewed_pass` |
| `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl` | 30 current action-eval rows -> `qa_reviewed_pass` |

Generated QA outputs:

- `data/official/piwm_target_v1/qa_review_target30_5act/qa_review_results.json`
- `data/official/piwm_target_v1/qa_review_target30_5act/qa_review_results.md`
- `data/official/piwm_target_v1/qa_review_target30_5act/main_schema_test_reviewed.jsonl`
- `data/official/piwm_target_v1/qa_review_target30_5act/main_schema_test_qa_reviewed_pass.jsonl`
- `data/official/domain_specialization_eval_v2/target_frontcam_test_qa_reviewed_all.jsonl`

## Documentation Updated

- `data/official/DATASET_MANIFEST.json`
- `configs/domain_specialization_v1.json`
- `data/official/README.md`
- `docs/README.md`
- `docs/current/dataset_inventory.md`
- `docs/current/domain_specialization_experiment_plan.md`
- `docs/current/paper_data_section_blueprint.md`
- `docs/current/claude_project_brief_2026-05-18.md`
- `docs/current/project_progress_report_2026-05-17.md`
- `paper/data_section_emnlp_zh.md`
- `paper/data_section_emnlp.tex`

## Remaining Boundary

Only the balanced 30-record target test split is now project-lead QA-reviewed pass. The 71 Stage-2 target training records remain synthetic training data and should not be described as a human-QA-reviewed benchmark. The full 118-record target corpus is also not a fully human-QA-reviewed corpus.

## Verification

Passed:

```bash
python3 -m scripts.apply_target_frontcam_qa_review --qa-dir data/official/piwm_target_v1/qa_review_target30_5act --domain-eval-dir data/official/domain_specialization_eval_v2 --reviewed-at 2026-05-19 --review-type project_lead_human_review_after_5act_rebalance --merge-target-data
python3 -m scripts.build_two_stage_training_and_eval
python3 -m scripts.run_action_selection_baselines
python3 -m scripts.check_target_frontcam_split
python3 -m pytest piwm_data/tests piwm_train/tests piwm_infer/tests
```

Full test result: `244 passed in 51.11s`.

