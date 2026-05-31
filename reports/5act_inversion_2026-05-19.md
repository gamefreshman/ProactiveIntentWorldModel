# PIWM 5-Act Inversion Report

Date: 2026-05-19

## 1. Inversion Summary

The previous 5-act operational policy definition was wrong.

| Item | Before inversion | After inversion |
|---|---|---|
| 5-act operational set | Elicit / Inform / Recommend / Reassure / Hold | Greet / Elicit / Inform / Recommend / Hold |
| Excluded act | Greet | Reassure |
| Main train/eval behavior | Greet filtered out; Reassure retained | Reassure filtered out; Greet retained |
| Macro-F1 reporting | Did not report Greet | Reports Greet; does not report Reassure |

No deeper expert-rule generation logic was changed. This pass only changed filtering, splitting, derived entrypoints, baselines, and documentation.

## 2. Target Data Accounting

Raw target-frontcam source remains 118 video-backed records.

```text
118 total target records
- 17 rows with best_act=Reassure
- 0 rows whose candidate set degenerates after removing Reassure candidates
= 101 clean 5-act records
101 - 30 balanced test records = 71 Stage-2 target train records
```

Additional candidate-level cleanup:

- 39 clean rows had Reassure in the candidate list; those candidate entries were removed.
- No non-Reassure row became empty after Reassure filtering.
- Raw `PIWM-Target-Frontcam-v1` still keeps all 118 records for audit/source compatibility.

## 3. New Balanced Eval

New target 5-act test size: 30 records.

| Best act | Count |
|---|---:|
| Greet | 6 |
| Elicit | 6 |
| Inform | 6 |
| Recommend | 6 |
| Hold | 6 |
| Reassure | 0 |

QA status:

- Historical at split time: all 30 new target test records were `qa_pending_project_lead_review`. Updated later on 2026-05-19: all 30 passed project-lead QA and were promoted to `qa_reviewed_pass`.
- The previous wrong 5-act eval files were archived under `data/official/domain_specialization_eval_v1/_legacy_wrong_5act/`.
- The only remaining human boundary is project-lead QA for this new 30-record balanced test.

## 4. Regenerated Entrypoints

| Artifact | Result |
|---|---:|
| `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | 71 rows |
| `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl` | 30 rows |
| `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl` | 90 rows |
| `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl` | 2625 rows |

Sanity check:

- Stage-2 train best acts: Elicit=14, Greet=11, Inform=41, Recommend=5.
- Target eval best acts: Greet=6, Elicit=6, Inform=6, Recommend=6, Hold=6.
- Stage-2/eval candidate lists contain no Reassure.

## 5. Baselines

Computed on `target_frontcam_5act_test_action_selection.jsonl`, n=30.

| Baseline | Accuracy | Macro F1 |
|---|---:|---:|
| always-Greet | 0.200 | 0.067 |
| always-Inform | 0.200 | 0.067 |
| always-Hold | 0.200 | 0.067 |
| random-candidate, seed=42 | 0.267 | 0.281 |

The baseline table was also written into `data/official/domain_specialization_eval_v2/two_stage_eval_summary.md`.

## 6. Main Files Touched

Code and filters:

- `piwm_train/data_collator.py`
- `piwm_train/prompts.py`
- `piwm_train/ms_swift_adapter.py`
- `piwm_infer/parsers.py`
- `piwm_infer/decision_loop.py`
- `scripts/target_frontcam_split.py`
- `scripts/rebalance_target_frontcam_split.py`
- `scripts/check_target_frontcam_split.py`
- `scripts/build_two_stage_training_and_eval.py`
- `scripts/run_action_selection_baselines.py`
- `scripts/import_piwm_target_dataset.py`

Tests:

- `piwm_train/tests/test_data_collator.py`
- `piwm_infer/tests/test_parsers.py`
- `piwm_infer/tests/test_decision_loop.py`
- `piwm_data/tests/test_target_frontcam_qa_and_promptready.py`

Data and generated artifacts:

- `data/official/piwm_target_v1/*`
- `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl`
- `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl`
- `data/official/domain_specialization_eval_v2/*`
- `data/piwm_results/domain_specialization_eval/target_5act_action_baselines.*`
- `data/official/domain_specialization_eval_v1/_legacy_wrong_5act/*`

Docs and manifests:

- `data/official/DATASET_MANIFEST.json`
- `data/README.md`
- `data/official/README.md`
- `docs/README.md`
- `docs/current/dataset_inventory.md`
- `docs/current/domain_specialization_experiment_plan.md`
- `docs/current/claude_project_brief_2026-05-18.md`
- `docs/current/paper_data_section_blueprint.md`
- `docs/current/project_progress_report_2026-05-17.md`
- `docs/contracts/action_space_realization_contract.md`
- `docs/contracts/data_schema_v2_contract.md`
- `docs/contracts/data_generation_chain_v2_1_contract.md`
- `docs/v2_validation/action_distribution.md`
- `docs/v2_validation/piwm_target_frontcam_import.md`
- `docs/v2_validation/v2_2_release_notes.md`
- `paper/data_section_emnlp_zh.md`
- `paper/data_section_emnlp.tex`
- `piwm_data/expert_corpus/README.md`
- `RESEARCH_LOG.md`
- `configs/domain_specialization_v1.json`

## 7. Verification

All requested verification commands passed:

```text
python3 -m scripts.check_target_frontcam_split
python3 -m scripts.build_two_stage_training_and_eval
python3 -m scripts.run_action_selection_baselines
python3 -m pytest piwm_data/tests piwm_train/tests piwm_infer/tests
python3 -m json.tool data/official/DATASET_MANIFEST.json
git diff --check
```

Full pytest result:

```text
232 passed in 10.06s
```

## 8. Remaining Boundary

Current remaining human boundary:

- Project lead must re-QA the new 30 balanced target test records.

Not started in this pass:

- Feishu annotation digitization.
- Survey/questionnaire digitization.
- Stage-1 model training.
- Stage-2 target training.
- Any model result claim beyond the simple baselines above.
