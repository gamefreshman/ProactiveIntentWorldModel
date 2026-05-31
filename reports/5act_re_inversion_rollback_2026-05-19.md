# 5-act Re-inversion Rollback Report

Date: 2026-05-19

## 1. Final Decision Restored

The only valid operational 5-act set for the current main path is:

```text
Greet / Elicit / Inform / Recommend / Hold
```

`Reassure` is excluded from current operational training, evaluation, inference, runtime export, and main macro-F1. It remains available only in source, historical compatibility, and analysis layers.

This restores the state recorded in `reports/5act_inversion_2026-05-19.md`.

## 2. What Went Wrong

During the previous Stage-1 / QA / documentation pass, I let a stale and wrong "5-act unification" assumption leak into the action-space wording and generated artifacts. That wrongly stated or implied:

```text
Elicit / Inform / Recommend / Reassure / Hold
```

and treated `Greet` as outside the main macro-F1 path. That was an unauthorized reversal of the PI-locked decision. The error was not caused by a new PI decision; it was an agent-side governance failure.

Root cause:

- I treated "general data has Greet=0" as if it were an action-space definition, instead of only a coverage gap.
- I did not anchor every 5-act change back to the locked inversion report before editing docs and generated outputs.
- I allowed Stage-1 training configuration work to bleed into action-space governance, which should have been out of scope.

Future guardrail:

- Any change to the core action set requires explicit PI instruction.
- `reports/5act_inversion_2026-05-19.md` is the current lockfile for the operational set until the PI replaces it.
- Stage/train-script changes must not rewrite action-space definitions unless the task explicitly says so.

## 3. Group A: Work Preserved

These changes were preserved because they are not the source of the 5-act reversal and are still useful:

- Stage-1 training scripts and runbook:
  - `scripts/train/stage1_train.sh`
  - `scripts/train/stage1_eval.py`
  - `docs/current/stage1_training_runbook.md`
  - `scripts/build_stage1_general_split.py`
- ms-swift / training compatibility:
  - `piwm_train/config.py`
  - `piwm_train/ms_swift_adapter.py`
  - `piwm_train/targets.py`
  - `piwm_train/tests/test_targets.py`
  - `piwm_train/tests/test_inspect_act_balance.py`
  - `scripts/inspect_act_balance.py`
- QA apply work:
  - `scripts/apply_target_frontcam_qa_review.py`
  - `reports/target_5act_qa_promotion_2026-05-19.md`
  - target QA status remains `qa_reviewed_pass` for the 30 balanced test records.

## 4. Group B: Rolled Back / Corrected

These files or artifacts were checked and corrected back to the locked 5-act set:

### Core filtering / export code

- `scripts/target_frontcam_split.py`
  - Restored test split to include `Greet` and exclude `Reassure`.
- `scripts/check_target_frontcam_split.py`
  - Restored expected train/test accounting to `71 / 30`.
- `scripts/rebalance_target_frontcam_split.py`
  - Restored validation to reject `Reassure` in the 5-act test.
- `scripts/build_two_stage_training_and_eval.py`
  - Restored `FIVE_ACTS = Greet/Elicit/Inform/Recommend/Hold`.
  - Excludes rows whose best act is `Reassure`.
  - Filters `Reassure` from candidate lists.
  - Drops rows only if candidate list becomes empty after filtering.
- `scripts/run_action_selection_baselines.py`
  - Restored `always_greet` baseline.
  - Main eval excludes `Reassure`, not `Greet`.
- `scripts/refresh_official_v2_exports.py`
  - Help text restored to "no Reassure".
- `scripts/import_piwm_target_dataset.py`
  - Import notes restored to keep `Reassure` only in raw/source compatibility.

### Runtime / training filters

- `piwm_train/data_collator.py`
  - `five_act_only=True` now filters `Reassure` and preserves `Greet`.
- `piwm_train/prompts.py`
  - No-leak candidate block filters `Reassure`.
- `piwm_infer/parsers.py`
  - `parse_action_output(..., five_act_only=True)` allows `Greet` and rejects `Reassure`.
- `piwm_infer/decision_loop.py`
  - Runtime candidates filter `Reassure`, not `Greet`.

### Invariant tests

- `piwm_data/tests/test_5act_invariant.py`
  - Operational output invariant is "Reassure must be 0".
- `piwm_data/tests/test_target_frontcam_qa_and_promptready.py`
  - Target test must contain `Greet=6 / Elicit=6 / Inform=6 / Recommend=6 / Hold=6`.
- `piwm_train/tests/test_data_collator.py`
  - Greet rows are kept; Reassure-best rows are skipped.
- `piwm_infer/tests/test_parsers.py`
  - Greet accepted; Reassure rejected in five-act mode.
- `piwm_infer/tests/test_decision_loop.py`
  - Reassure runtime outputs fail parse and fallback.
- `piwm_data/tests/test_rules.py`
  - Strict operational policy excludes Reassure.

### Data artifacts regenerated

- `data/official/piwm_target_v1/main_schema.jsonl`
- `data/official/piwm_target_v1/state_inference.jsonl`
- `data/official/piwm_target_v1/transition_modeling.jsonl`
- `data/official/piwm_target_v1/policy_preference.jsonl`
- `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl`
- `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl`
- `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`
- `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl`
- `data/official/domain_specialization_eval_v2/two_stage_eval_summary.json`
- `data/official/domain_specialization_eval_v2/two_stage_eval_summary.md`
- `data/piwm_results/domain_specialization_eval/target_5act_action_baselines.json`
- `data/piwm_results/domain_specialization_eval/target_5act_action_baselines.md`

### Documentation / manifest corrected

- `data/official/DATASET_MANIFEST.json`
- `configs/domain_specialization_v1.json`
- `data/official/README.md`
- `docs/README.md`
- `docs/contracts/action_space_realization_contract.md`
- `docs/contracts/data_generation_chain_v2_1_contract.md`
- `docs/contracts/data_schema_v2_contract.md`
- `docs/current/dataset_inventory.md`
- `docs/current/domain_specialization_experiment_plan.md`
- `docs/current/claude_project_brief_2026-05-18.md`
- `docs/current/paper_data_section_blueprint.md`
- `docs/current/project_progress_report_2026-05-17.md`
- `docs/current/stage1_training_runbook.md`
- `docs/v2_validation/action_distribution.md`
- `docs/v2_validation/v2_2_release_notes.md`
- `paper/data_section_emnlp.tex`
- `paper/data_section_emnlp_zh.md`
- `piwm_data/expert_corpus/README.md`

## 5. Final Target Accounting

Current target-frontcam source records:

```text
118 total target records
-17 rows with best_act=Reassure
-0 rows whose candidate set degenerates after removing Reassure candidates
=101 clean 5-act records
101 - 30 balanced test records = 71 Stage-2 target train records
```

Current balanced target test distribution:

| Act | Count |
|---|---:|
| Greet | 6 |
| Elicit | 6 |
| Inform | 6 |
| Recommend | 6 |
| Hold | 6 |
| Reassure | 0 |

Current Stage-2 train distribution:

| Act | Count |
|---|---:|
| Inform | 41 |
| Elicit | 14 |
| Greet | 11 |
| Recommend | 5 |
| Hold | 0 |
| Reassure | 0 |

The Stage-2 train set still has `Hold=0`; that is a data distribution issue, not a 5-act definition issue. It is not changed in this rollback.

## 6. Baseline Results After Rollback

Input: `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`

| Baseline | Accuracy | Macro F1 |
|---|---:|---:|
| always-Greet | 0.200 | 0.0667 |
| always-Elicit | 0.200 | 0.0667 |
| always-Inform | 0.200 | 0.0667 |
| always-Recommend | 0.200 | 0.0667 |
| always-Hold | 0.200 | 0.0667 |
| random-candidate | 0.2667 | 0.2811 |

## 7. Verification

Commands run:

```bash
python3 -m scripts.check_target_frontcam_split
python3 -m scripts.build_two_stage_training_and_eval
python3 -m scripts.run_action_selection_baselines
python3 -m pytest piwm_data/tests piwm_train/tests piwm_infer/tests
python3 -m json.tool data/official/DATASET_MANIFEST.json >/dev/null
git diff --check
```

Results:

- `check_target_frontcam_split`: passed
- `build_two_stage_training_and_eval`: passed
- `run_action_selection_baselines`: passed
- `pytest`: `244 passed`
- `DATASET_MANIFEST.json`: valid JSON
- `git diff --check`: passed

## 8. Current Remaining Human Boundary

- The worktree is intentionally left dirty.
- No commit was made.
- The 30 balanced target test rows are already marked `qa_reviewed_pass` from PI review.
- Flying-book annotation, questionnaire digitization, and Stage-1/Stage-2 model training are still not started in this rollback.

