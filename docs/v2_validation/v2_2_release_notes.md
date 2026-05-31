# PIWM Schema v2.2 Release Notes

更新时间：2026-05-15

## Release Scope

v2.2 completes the action-space and data-format migration without overwriting frozen v1 aliases.

Delivered artifacts:

| Artifact | Path | Status |
|---|---|---|
| `PIWM-Train-Synth-v2` | `data/official/piwm_train_synth_v2/` | exported |
| v2.2 ms-swift train JSONL | `data/official/ms_swift/piwm_train_synth_v2.jsonl` | exported |
| `PIWM-PolicySlice-v2` | `data/official/piwm_policy_slice_v2/policy_manifest.jsonl` | exported |
| compatibility audit | `docs/v2_validation/compatibility_report.md` | regenerated |
| diff preview | `docs/v2_validation/v2_2_reexport_diff_preview.md` | regenerated |
| test coverage notes | `docs/v2_validation/v2_2_test_coverage.md` | updated |

## Key Schema Changes

- Added canonical v2 action specs: `candidate_action_specs` and `best_action_spec`.
- Added stable v2 action keys through `rules.action_spec_key(act, params)`.
- Added `next_state_by_action_v2`, while keeping legacy `next_state_by_action` for old A-label compatibility.
- Added transition-row `candidate_action_key`.
- Re-derived v2.2 transition outcomes during independent export so `dialogue_act`, `act_params`, `intent_tier`, `risk_tags`, `failure_mode`, and `outcome_type` are populated in exported transition rows.

## Dataset Counts

| Dataset | Rows |
|---|---:|
| `data/official/piwm_train_synth_v2/main_schema.jsonl` | 543 |
| `data/official/piwm_train_synth_v2/state_inference.jsonl` | 543 |
| `data/official/piwm_train_synth_v2/transition_modeling.jsonl` | 2001 |
| `data/official/piwm_train_synth_v2/policy_preference.jsonl` | 543 |
| `data/official/ms_swift/piwm_train_synth_v2.jsonl` | 2544 |
| `data/official/piwm_policy_slice_v2/policy_manifest.jsonl` | 864 |

## Compatibility Result

Basic schema compatibility:

| Tier | Count |
|---|---:|
| green | 462 |
| yellow | 0 |
| red | 81 |

Extended v2 re-derivation audit:

| Tier | Count |
|---|---:|
| green | 109 |
| yellow | 353 |
| red | 81 |

Interpretation: basic `yellow=0` is a detector-scope result. Extended audit shows 353 policy-migration yellow rows caused by `best_action_drift`. The 81 red rows are concentrated in `browser_low_intent`.

## Validation

Verified commands:

```bash
python3 -m pytest piwm_data/tests piwm_train/tests piwm_infer/tests
python3 -m piwm_data.expert_corpus.compile
python3 -m piwm_data.expert_corpus.provenance
python3 -m json.tool data/official/DATASET_MANIFEST.json
git diff --check
```

Latest full test result: `213 passed`.

## Known Boundaries

- `PIWM-Train-Synth-v2` is still synthetic train pending visual QA.
- `PIWM-Train-Synth-v2` does not mean new Kling videos were generated.
- `PIWM-PolicySlice-v2` is a rule-space policy manifest, not a filmed or QA-reviewed dataset.
- Current 5-act definition is `Greet / Elicit / Inform / Recommend / Hold`; `Recommend` is represented with `pressure=soft/firm` params in current v2-native policy paths. `Reassure` is excluded from training/eval/inference/runtime export and remains source/compat only. `Greet=0` in older general/policy-slice artifacts is a coverage gap, not the action-space definition.
- v2.3 should remove migration-only A-key dependencies only after downstream loaders switch to `next_state_by_action_v2`.
