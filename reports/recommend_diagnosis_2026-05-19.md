# PIWM-Train-Synth-v2 Recommend Diagnosis

Date: 2026-05-19

Scope: read-only diagnosis of `data/official/piwm_train_synth_v2/main_schema.jsonl` and `policy_preference.jsonl`. This report does not modify data or generation code.

Status after implementation: this report records the pre-fix state. The current official/runtime export has since introduced `Recommend(pressure=soft|firm)`, reselected `best_action` by v2 reward, and enforces operational `Reassure=0`. Do not treat the diagnosis below as the current manifest state.

## Executive Summary

`Recommend=0` in the stored best-action field is not caused by candidate coverage. Recommend appears in 518 / 543 records, but every such candidate is `Recommend(pressure=firm)`, inherited from the legacy `A3_strong_recommend` action. There is no `Recommend(pressure=soft)` candidate in the current `PIWM-Train-Synth-v2` records.

The root cause is a hybrid export path:

1. `best_action` remains the legacy A-label selection produced by `pick_best_action(...)`.
2. v2.2 re-derives outcome rewards, failure modes, and `next_state_by_action_v2`.
3. The export does not reselect `best_action` from the v2.2 rewards.

As a result, even the 23 action-stage rows where current v2.2 outcomes make `Recommend` the highest-reward candidate still keep `Elicit` as the stored best label.

## Phase 1: Reward Distribution

Data source: `data/official/piwm_train_synth_v2/main_schema.jsonl`.

Overall counts:

| Metric | Count |
|---|---:|
| Total records | 543 |
| Records with Recommend candidate | 518 |
| Stored best=`Recommend` | 0 |
| `policy_preference` chosen=`Recommend` | 0 |
| `policy_preference` rejected=`Recommend` | 449 |
| Recommend params in current records | 518 x `{"target": "item", "pressure": "firm"}` |
| Recommend params `pressure=soft` | 0 |

Stored best-action distribution:

| Stored best act | Count |
|---|---:|
| Inform | 407 |
| Elicit | 69 |
| Hold | 59 |
| Reassure | 8 |
| Recommend | 0 |

If best is reselected by current `next_state_by_action_v2.reward`, without changing any file:

| Reward-selected act | Count |
|---|---:|
| Elicit | 286 |
| Inform | 167 |
| Reassure | 42 |
| Hold | 25 |
| Recommend | 23 |

Stage-bucketed Recommend reward table:

| AIDA stage | n_samples | Recommend reward mean | Reward median | Reward min/max | Best act top-3, stored field | Reward-selected top-3 | Avg reward gap vs stored best |
|---|---:|---:|---:|---:|---|---|---:|
| attention | 42 | -0.619 | -0.600 | -0.700 / -0.600 | Hold=42 | Reassure=34, Hold=8 | 1.119 |
| interest | 286 | -0.427 | -0.450 | -0.600 / -0.300 | Inform=286 | Elicit=240, Inform=46 | 1.227 |
| desire | 121 | -0.453 | -0.450 | -0.600 / -0.300 | Inform=121 | Inform=121 | 1.253 |
| action | 69 | 0.067 | -0.200 | -0.200 / 0.600 | Elicit=69 | Elicit=46, Recommend=23 | 0.533 |

Reward gap means `stored_best_reward - recommend_reward`. In action stage the minimum gap is `-0.4`, meaning Recommend already beats the stored best reward in 23 records under the v2.2 outcome table, but the stored label was not refreshed.

Recommend next-state outcomes:

| AIDA stage | Dominant Recommend next state | Outcome type | Risk |
|---|---|---|---|
| attention | `attention / disengaged` | success=34, failure=8 | high=42 |
| interest | `attention / defensive_withdrawal` | failure=190, success=96 | medium=240, high=46 |
| desire | `attention / defensive_withdrawal` | failure=71, success=50 | medium=74, high=47 |
| action | `attention / defensive_withdrawal` for 46; `action / engaged_dialogue` for 23 | failure=46, success=23 | medium=69 |

Interpretation: Recommend is mostly predicted as regression to attention or withdrawal because the current Recommend candidate is firm/high-pressure. Only a subset of action-stage, ready-to-buy rows gets a positive recommendation outcome.

## Phase 2: Code Location

### Candidate generation

`piwm_data/rules.py:708-747`

The legacy candidate table inserts `A3_strong_recommend` into seven state/AIDA combinations. This is why coverage is high.

Relevant combinations:

| State | AIDA | Recommend form |
|---|---|---|
| high_hesitation | interest | A3 strong recommend |
| high_hesitation | desire | A3 strong recommend |
| active_evaluation | interest | A3 strong recommend |
| active_evaluation | desire | A3 strong recommend |
| ready_to_decide | desire | A3 strong recommend |
| ready_to_decide | action | A3 strong recommend |
| early_browsing | attention | A3 strong recommend |

### Legacy reward table

`piwm_data/rules.py:760-887`

Key reward rows:

| State | Legacy action | Reward | Competing winner in legacy path |
|---|---|---:|---|
| high_hesitation | A3_strong_recommend | -0.5 | A2_offer_value_comparison = 0.8 |
| active_evaluation | A3_strong_recommend | -0.3 | A5_provide_demonstration = 0.8 |
| ready_to_decide | A3_strong_recommend | 0.6 | A4_open_with_question = 0.8 |
| early_browsing | A3_strong_recommend | -0.6 | A1/A6 = 0.5 |

This legacy table structurally prevents `A3_strong_recommend` from winning.

### Best-action selection

`piwm_data/rules.py:2006-2016`

`pick_best_action(...)` ranks legacy actions by `derive_transition(state, action)`. It does not use AIDA-specific failure branches, persona, visible cues, or v2.2 soft/firm recommendation calibration.

### v2.2 outcome calculation

`piwm_data/rules.py:1714-1776`

`derive_action_outcome(...)` applies failure-mode logic and then v2 reward calibration, but only for the outcome table.

### v2.2 Recommend calibration

`piwm_data/rules.py:1779-1807`

The positive calibration exists only for `Recommend(pressure=soft)`:

| Condition | Soft Recommend reward |
|---|---:|
| `ready_to_decide` + `desire/action` | 0.85 |
| `active_evaluation` + `desire` | 0.82 |
| `low_intent_browsing` | capped at <= -0.2 |

Current `PIWM-Train-Synth-v2` records do not contain soft Recommend candidates, so this calibration cannot help the stored labels.

### Transitional mapping

`piwm_data/rules.py:1671-1680`

All v2 `Recommend` actions map to the legacy `A3_strong_recommend` transition family until the transition table is fully split by `(act, params)`.

### Export mismatch

`scripts/refresh_official_v2_exports.py:170-185`

The v2 refresh re-derives `next_state_by_action` and `reward_by_action`, but it does not recompute `best_action`.

`piwm_data/exporters.py:76-119`

`policy_preference.jsonl` uses `record.best_action` as `chosen`, then picks the lowest-reward alternative as `rejected`. Therefore `Recommend` can appear as rejected, but cannot become chosen unless `record.best_action` is refreshed.

## Phase 3: Rule Provenance

### Candidate rules involving Recommend

| Rule ID | Type | Role | Source IDs | Support |
|---|---|---|---|---|
| CAND_001 | state_aida_to_candidates | high_hesitation/interest includes A3 | AIDA, consumer decision, personal selling | manual_supported |
| CAND_002 | state_aida_to_candidates | high_hesitation/desire includes A3 | AIDA, consumer decision, personal selling | manual_supported |
| CAND_003 | state_aida_to_candidates | active_evaluation/interest includes A3 | AIDA, consumer decision, personal selling, SPIN | manual_supported |
| CAND_004 | state_aida_to_candidates | active_evaluation/desire includes A3 | AIDA, consumer decision, personal selling, SPIN | manual_supported |
| CAND_005 | state_aida_to_candidates | ready_to_decide/desire includes A3 | AIDA, consumer decision, personal selling | manual_supported |
| CAND_006 | state_aida_to_candidates | ready_to_decide/action includes A3 | AIDA, personal selling | manual_supported; ordering still needs expert review |
| CAND_007 | state_aida_to_candidates | early_browsing/attention includes A3 | AIDA, consumer decision, personal selling | manual_supported |

These rules add Recommend as a contrast candidate, but most descriptions frame safe alternatives as lower pressure.

### Transition rules involving strong Recommend

| Rule ID | State | Reward | Failure mode | Source IDs |
|---|---|---:|---|---|
| TRANS_003 | high_hesitation | -0.5, failure override -0.6 | pressure/reactance before discovery | personal selling, Brehm reactance, SPIN |
| TRANS_010 | active_evaluation | -0.3, failure override -0.45 | strong recommend replaces discovery | personal selling, Brehm reactance, SPIN |
| TRANS_012 | ready_to_decide | 0.6, failure override -0.2 for high push sensitivity | can close, but still pressure risk | AIDA, personal selling, Brehm reactance |
| TRANS_017 | early_browsing | -0.6, failure override -0.7 | premature closing during low intent | personal selling, Brehm reactance |

### Distilled principles

Relevant principle IDs:

| Principle ID | Source | Effect on Recommend |
|---|---|---|
| P_PERSONAL_SELLING_001 | OpenStax personal selling | Closing exists as a sales process step |
| P_PERSONAL_SELLING_002 | OpenStax personal selling | Approach/presentation should fit readiness |
| P_SPIN_001 | SPIN Selling | Questions before pushing solution |
| P_FAILURE_MODE_001 | OpenStax personal selling | Closing must fit readiness |
| P_FAILURE_MODE_002 | SPIN Selling | Recommendation before need discovery increases mismatch/trust risk |
| P_FAILURE_MODE_003 | Brehm reactance | High-pressure recommendation threatens autonomy |
| P_RECOMMEND_PRESSURE_001 | SPIN Selling | Soft recommendation can preserve choice |
| P_RECOMMEND_PRESSURE_002 | OpenStax personal selling | Firm recommendation is for commitment cues |
| P_RECOMMEND_PRESSURE_003 | Brehm reactance | Firm recommendation during low intent is pressure-reactance risk |

The provenance chain is not merely biased against all recommendation. It is specifically biased against firm, premature recommendation. The problem is that the current general records only instantiate Recommend as firm.

## Phase 4: Counterfactual Checks

### Add +0.1 to Recommend reward

Using the current `next_state_by_action_v2` candidates and reselecting by reward in memory only:

| Recommend reward delta | Recommend best count | Stage concentration |
|---:|---:|---|
| +0.0 | 23 | action=23 |
| +0.1 | 23 | action=23 |
| +0.3 | 23 | action=23 |
| +0.5 | 23 | action=23 |
| +1.0 | 69 | action=69 |

Conclusion: a light +0.1 reward tweak would not fix the distribution. The reward gaps in attention/interest/desire are about 1.1-1.4 because firm Recommend is modeled as a pressure-risk action.

### Only allow Recommend in desire/action

Records with a Recommend candidate in desire/action:

| Scope | Count | Percent of total |
|---|---:|---:|
| desire/action Recommend candidates | 190 | 34.99% |
| current reward-selected Recommend winners | 23 | 4.24% |

Stage gating alone is not enough. Desire-stage Recommend is still negative because it is firm Recommend. Action-stage Recommend only wins when the customer is ready-to-buy and not high push-sensitive.

### Existing v2-native soft Recommend path

Using existing runtime helper functions only, without changing files:

| Path | Recommend best count |
|---|---:|
| Stored `PIWM-Train-Synth-v2.best_action` | 0 |
| Current v2 outcome rewards over stored candidates | 23 |
| Existing `derive_policy_candidate_specs(...)` with soft/firm split | 119 |

This confirms the main missing piece: the stored general train records did not move to the v2-native policy candidate path.

## Root Cause Judgment

Primary root cause: rule/export architecture mismatch.

Secondary root causes:

1. Data representation bias: current records instantiate Recommend only as `pressure=firm`.
2. Rule constraint: firm Recommend is intentionally high risk under SPIN/reactance-derived rules.
3. Export bug or unfinished migration: v2.2 outcome rewards are rederived, but `best_action` is not reselected from those rewards.

It is not mainly a candidate coverage problem. It is not mainly a single-turn ban. I found no explicit hardcoded rule saying "single-turn must not Recommend." The practical effect comes from the combination of firm-only Recommend, readiness/reactance failure modes, and stale legacy best labels.

## Fix Options

### Light fix: refresh best from current v2 outcomes

Change scope:

- Recompute `best_action_spec` from `next_state_by_action_v2.reward`.
- Keep existing candidates; do not introduce soft Recommend.

Expected effect:

- Recommend rises from 0 to about 23 / 543, all concentrated in action-stage ready-to-buy rows.
- It fixes the label/reward inconsistency but does not solve broader Recommend undercoverage.

Estimated effort: 0.5 day.

Risk:

- Current 5-act policy excludes Reassure, but v2 reward reselection would also pick Reassure in 42 records unless filtered for the operational path.

### Medium fix: switch action-selection export to v2-native policy candidates

Change scope:

- Use `derive_policy_candidate_specs(...)`.
- Include both `Recommend(pressure=soft)` and `Recommend(pressure=firm)` where stage/state allows.
- Export action-selection rows from `(act, params)` instead of legacy A-label best fields.
- Keep firm Recommend as risky/negative; let soft Recommend become positive.

Expected effect:

- Existing helper simulation gives about 119 / 543 Recommend best rows.
- Recommend becomes learnable without turning high-pressure firm recommendation into a positive label.

Estimated effort: 1-2 days including tests and manifest/doc updates.

Risk:

- Requires careful 5-act filtering because current operational path excludes `Reassure`.
- Must avoid mixing v2-native policy labels with legacy `policy_preference.jsonl` names.

### Heavy fix: rebuild single-turn recommendation semantics

Change scope:

- Split transition rules fully by `(act, params)`.
- Make `Recommend(pressure=soft)` a first-class single-turn action with explicit source-backed stage rules.
- Keep `Recommend(pressure=firm)` mostly for negative contrast or very late action-stage cases.
- Regenerate official general action-selection data and re-run distribution/baseline reports.

Expected effect:

- Clean conceptual model: recommendation is not synonymous with pressure.
- Supports paper narrative better because "recommend" becomes a pedagogical action, not only a bad intervention.

Estimated effort: 3-5 days for rules, exporter, tests, docs, and validation; longer if expert review must be repeated.

Risk:

- Changes official labels and may require revalidating old training/eval claims.

## Recommended Next Step

Do not simply raise `A3_strong_recommend` reward. That would make high-pressure recommendation a positive label and conflict with the expert-corpus rationale.

Recommended path: medium fix. Build a separate v2-native 5-act action-selection export for general data that uses soft/firm Recommend split, filters the current operational 5-act correctly, and leaves the existing legacy `PIWM-Train-Synth-v2` files auditable as historical schema exports.
