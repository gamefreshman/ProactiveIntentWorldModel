# Recommend Soft Introduction and Operational 5-Act Refresh

Date: 2026-05-19

## Scope

This pass implements the current operational five-act policy:

```text
Greet / Elicit / Inform / Recommend / Hold
```

`Reassure` remains in the source and compatibility layer, but is not allowed in training, eval, inference, or runtime export. `Recommend` is now parameterized as `pressure=soft|firm`.

No commit was made.

## Phase 1 / 1.5 Checks

- Source/compatibility definitions still include `Reassure`; this layer was not deleted.
- Before the fix, `PIWM-Train-Synth-v2` still had stored `Reassure` in operational fields: best rows, candidate specs, next-state outputs, and policy preferences.
- Phase 1.5 fallback analysis found 90 state/AIDA/intent-tier combinations where runtime candidates emitted `Reassure`.
- Removing `Reassure` created no empty candidate sets.
- 88 / 90 combinations degraded to two or fewer candidates, mostly `Hold`, which justified adding low-pressure `Recommend(pressure=soft)` for suitable hesitation/evaluation states.

Report:

```text
reports/reassure_fallback_analysis_2026-05-19.md
```

## Candidate and Best-Action Refresh

`derive_policy_candidate_specs(...)` now emits strict operational candidates:

- `Greet`
- `Elicit`
- `Inform`
- `Recommend(pressure=soft)`
- `Recommend(pressure=firm)` where stage allows it
- `Hold`

It filters out `Reassure` and adds `Recommend(pressure=soft)` in appropriate Reassure-fallback states. `attention` / `interest` paths only use soft recommendation; `desire` / `action` paths can include soft and firm where a recommendation candidate is rule-supported.

`data/official/piwm_train_synth_v2` was re-exported with operational 5-act policy mode:

```text
records: 543
state rows: 543
transition rows: 2001
policy rows: 543
```

New best-action distribution:

| Act | Count |
|---|---:|
| Elicit | 252 |
| Recommend | 125 |
| Inform | 105 |
| Hold | 61 |
| Greet | 0 |
| Reassure | 0 |

Recommend candidate pressure distribution:

| Pressure | Candidate count |
|---|---:|
| soft | 437 |
| firm | 158 |

All 125 `Recommend` best rows are `pressure=soft`.

## Training Entry Points

Refreshed official ms-swift files:

| File | Rows | Tasks |
|---|---:|---|
| `data/official/ms_swift/piwm_train_synth_v2.jsonl` | 2544 | perception=543, deliberation=2001 |
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 | user_intent=543, next_state_prediction=2001 |
| `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | 71 | action_selection_5act=71 |
| `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl` | 2615 | Stage-1 + Stage-2 |

Stage-1 seed=42 split was refreshed:

| Split | Parents | User intent | Next-state | Total examples |
|---|---:|---:|---:|---:|
| train | 493 | 493 | 1816 | 2309 |
| val | 50 | 50 | 185 | 235 |

Target 5-act split remains:

```text
118 total target records
- 17 best=Reassure
- 0 candidate-degenerate after removing Reassure
= 101 clean 5-act records
101 - 30 balanced test = 71 Stage-2 train
```

Balanced target test distribution:

```text
Greet=6 / Elicit=6 / Inform=6 / Recommend=6 / Hold=6 / Reassure=0
```

The revised 30-record target test has been promoted to `qa_reviewed_pass` after project-lead QA.

## Label Balancing

Added action-label balancing support:

```text
act_balancing = none | inverse_freq | oversample_minority
default = inverse_freq
```

Stage-2 train best-act counts and inverse-frequency weights:

| Act | Count | Weight |
|---|---:|---:|
| Inform | 41 | 0.432927 |
| Elicit | 14 | 1.267857 |
| Greet | 11 | 1.613636 |
| Recommend | 5 | 3.55 |

Added inspection utility:

```bash
python3 -m scripts.inspect_act_balance <jsonl_path>
```

General v2 policy-preference weights after refresh:

| Act | Count | Weight |
|---|---:|---:|
| Elicit | 252 | 0.53869 |
| Recommend | 125 | 1.086 |
| Inform | 105 | 1.292857 |
| Hold | 61 | 2.22541 |

## Baselines

Target balanced 5-act action-selection eval:

| Baseline | Accuracy | Macro F1 |
|---|---:|---:|
| always-Greet | 0.200 | 0.067 |
| always-Elicit | 0.200 | 0.067 |
| always-Inform | 0.200 | 0.067 |
| always-Recommend | 0.200 | 0.067 |
| always-Hold | 0.200 | 0.067 |
| random-candidate, seed=42 | 0.267 | 0.281 |

## Files Touched in This Pass

Core code:

- `piwm_data/rules.py`
- `scripts/refresh_official_v2_exports.py`
- `piwm_train/data_collator.py`
- `piwm_train/ms_swift_adapter.py`
- `scripts/build_two_stage_training_and_eval.py`
- `scripts/run_action_selection_baselines.py`
- `scripts/inspect_act_balance.py`

Tests:

- `piwm_data/tests/test_5act_invariant.py`
- `piwm_data/tests/test_phase3_scripts.py`
- `piwm_data/tests/test_rules.py`
- `piwm_data/tests/test_refresh_official_v2_exports.py`
- `piwm_train/tests/test_data_collator.py`
- `piwm_train/tests/test_inspect_act_balance.py`

Data and generated artifacts:

- `data/official/piwm_train_synth_v2/*`
- `data/official/ms_swift/piwm_train_synth_v2.jsonl`
- `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl`
- `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl`
- `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl`
- `data/official/domain_specialization_eval_v2/*`
- `data/piwm_results/domain_specialization_eval/target_5act_action_baselines.*`

Docs updated:

- `data/official/DATASET_MANIFEST.json`
- `data/official/README.md`
- `docs/contracts/data_schema_v2_contract.md`
- `docs/current/dataset_inventory.md`
- `docs/current/domain_specialization_experiment_plan.md`
- `docs/current/paper_data_section_blueprint.md`
- `docs/v2_validation/v2_2_release_notes.md`
- `paper/data_section_emnlp_zh.md`
- `paper/data_section_emnlp.tex`

## Verification Status

Passed:

```bash
python3 -m pytest piwm_data/tests/test_5act_invariant.py
python3 -m scripts.build_two_stage_training_and_eval
python3 -m scripts.run_action_selection_baselines
python3 -m scripts.check_target_frontcam_split
python3 -m scripts.inspect_act_balance data/official/piwm_train_synth_v2/policy_preference.jsonl
python3 -m scripts.inspect_act_balance data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl
python3 -m pytest piwm_train/tests/test_inspect_act_balance.py
python3 -m pytest piwm_data/tests piwm_train/tests piwm_infer/tests
python3 -m json.tool data/official/DATASET_MANIFEST.json >/dev/null
python3 -m json.tool configs/domain_specialization_v1.json >/dev/null
git diff --check
```

Full suite result: `244 passed in 5.02s`.

## Remaining Human Boundary

The revised balanced 30-record target test has now passed project-lead QA. Feishu annotation, questionnaire digitization, and real Stage-1/Stage-2 training are still not started.
