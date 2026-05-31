# Closed Model Best-Action Eval Step 0 Precheck

Date: 2026-05-25

Scope: only Step 0 data availability checks. No closed-model or local-model inference was run.

## Summary

| Check | Result |
|---|---|
| target 30 best_action gold | Available |
| general 30 best_action gold, eval slice only | Not present in `reports/general_domain_eval_seed42.jsonl` |
| general 30 best_action gold, full source backtrace | Available: 30/30 in `data/official/piwm_train_synth_v2/main_schema.jsonl` |
| general 30 policy_preference verification | Available: 30/30 in `data/official/piwm_train_synth_v2/policy_preference.jsonl` |
| general 30 cross-match action_selection_5act 190 | Partial only: 5/30 by normalized scene_id; 0/30 by exact source_id |
| Recommended option | Use the current general 30 with full-source recovered gold; no need to reduce to the 5 cross-matched rows |

## Files Checked

- `reports/general_domain_eval_seed42.jsonl`
  - 30 rows, not 60.
  - All rows have `task=user_intent`.
  - Fields are `order`, `source_id`, `task`, `stage`, `intent_label`, `images`, `source_split`, `sha256_line`.
  - No `best_action`, `best_act`, `gold_best_action`, candidate-action, or assistant chosen-action field.

- `data/official/piwm_train_synth_v2/main_schema.jsonl`
  - 543 rows.
  - The 30 `source_id` values from `reports/general_domain_eval_seed42.jsonl` all match `state_id` rows here.
  - All 30 matched rows have `best_action` and `best_action_spec.act`.
  - All candidate acts in the matched 30 are within the operational 5-act set Elicit / Inform / Recommend / Greet / Hold.

- `data/official/piwm_train_synth_v2/policy_preference.jsonl`
  - 543 rows.
  - The 30 `source_id` values from `reports/general_domain_eval_seed42.jsonl` all match `state_id` rows here.
  - All 30 matched rows have recoverable act-level gold via `chosen_json.action_spec.act`.
  - The recovered distribution matches `main_schema.jsonl`.

- `reports/rerun_eval_20260525/user_intent_target30_general30_seed42.jsonl`
  - 60 rows.
  - All rows have `task=user_intent`.
  - 30 target + 30 general by `source_id` prefix.
  - 0/60 rows have best-action gold.

- `data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl`
  - 190 rows.
  - All rows have `task=action_selection_5act`.
  - All 190 rows have `meta.best_act`.
  - Used as the requested action_selection_5act training source for cross-match.

- `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`
  - 30 rows.
  - All rows have `task=action_selection_5act`.
  - All 30 rows have `meta.best_act`.
  - The assistant `<chosen>` candidate maps back to `meta.best_act` via `meta.candidate_action_acts` for all 30 rows.
  - Gold distribution is balanced: Elicit 6, Inform 6, Greet 6, Recommend 6, Hold 6.

## General 30 Direct Gold

Direct best-action gold is not available in `reports/general_domain_eval_seed42.jsonl`.
The file is a user-intent evaluation slice, not an action-selection slice.

Result for slice-only file: unavailable.

## General 30 Full-Source Gold

Full-source backtrace by `source_id` found all 30 rows in:

`data/official/piwm_train_synth_v2/main_schema.jsonl`

Gold field locations:

- `best_action`: full action key, for example `Inform_5ac252a82695`.
- `best_action_spec.act`: act-level gold label for evaluation, one of Elicit / Inform / Recommend / Greet / Hold.
- `candidate_actions`: full candidate labels.
- `candidate_action_specs`: act-level candidate specs.

Cross-check source:

`data/official/piwm_train_synth_v2/policy_preference.jsonl`

- `chosen_json.action_spec.act` recovers the same act-level best-action labels for all 30 rows.

Recovered general 30 act-level gold distribution:

| best_act | count |
|---|---:|
| Elicit | 13 |
| Hold | 7 |
| Inform | 6 |
| Recommend | 4 |
| Greet | 0 |

All matched rows have candidate acts within Elicit / Inform / Recommend / Greet / Hold. The current general 30 simply contains no Greet gold label.

Result from full source: available, 30/30.

## General 30 Cross-Match

Exact `source_id` match against `data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl`:

- Matched with gold: 0/30

Normalized scene-id match, stripping action prefixes such as `general_hold_` and matching the underlying `piwm_*` id:

- Matched with gold: 5/30

Matched rows:

| general source_id | matched action_selection source_id | gold best_act |
|---|---|---|
| `piwm_4b087bc1ec` | `general_hold_piwm_4b087bc1ec` | Hold |
| `piwm_f5d9f82742` | `general_recommend_piwm_f5d9f82742` | Recommend |
| `piwm_ffe9d89f49` | `general_hold_piwm_ffe9d89f49` | Hold |
| `piwm_4f49d74b17` | `general_hold_piwm_4f49d74b17` | Hold |
| `piwm_bf4c6a7c0c` | `general_elicit_piwm_bf4c6a7c0c` | Elicit |

Unmatched rows: 25/30.

Interpretation: this 190-row file is a balanced action-selection training source, not the complete source for the sampled general 30 user-intent slice. It should not be used as the only recovery path for these 30 rows.

## Target 30 Gold

Target best-action gold is available in:

`data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`

Gold field location:

- `meta.best_act`: canonical act-level gold label, one of Elicit / Inform / Greet / Recommend / Hold.
- `messages[-1].content` contains `<chosen>...</chosen>` as the full candidate label.
- `meta.candidate_action_acts` maps the full candidate label back to the act-level label.

Result: available.

## Recommendation

Recommended option: proceed with the current general 30 using the full-source recovered gold.

Updated after full-source backtrace: the current general 30 can recover best-action gold for all 30 rows from `data/official/piwm_train_synth_v2/main_schema.jsonl`, with `data/official/piwm_train_synth_v2/policy_preference.jsonl` as an independent policy-preference check.

PI still needs to confirm before Step 1, but the data availability blocker is resolved:

1. Use target 30 from `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`.
2. Use general 30 from `reports/general_domain_eval_seed42.jsonl`, with gold/candidates backfilled from `data/official/piwm_train_synth_v2/main_schema.jsonl` by `source_id == state_id`.
3. Evaluate act-level F1 using `best_action_spec.act`.

Stopped after Step 0 as requested.
