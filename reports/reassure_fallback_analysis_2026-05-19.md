# Reassure Fallback Analysis for Operational 5-Act Policy

Date: 2026-05-19

Scope: read-only Phase 1.5 analysis before introducing `Recommend(pressure=soft)`. Source/compatibility Reassure remains untouched; this only analyzes what happens if operational policy candidates filter it out.

Status after implementation: this is a historical pre-soft diagnostic. The current runtime/export policy now distinguishes `Recommend(pressure=soft|firm)`, keeps `Reassure` only in source/compatibility history, and requires `Reassure=0` in training, eval, inference, and runtime export.

## Summary

- State/AIDA/intent-tier combinations currently emitting `Reassure`: 90
- Degenerate after removing `Reassure`: 0
- Candidate count <= 2 after removing `Reassure`: 88 / 90

Fallback distribution after removing `Reassure`, selecting the highest current v2 outcome reward among remaining candidates:

| Fallback act | Count |
|---|---:|
| `Hold(silent)` | 84 |
| `Inform(comparison)` | 3 |
| `Hold(ambient)` | 3 |

Remaining candidate-count distribution:

| Remaining candidate count | Combinations |
|---:|---:|
| 1 | 85 |
| 2 | 3 |
| 3 | 2 |

By AIDA stage:

| AIDA | Reassure combos | <=2 candidates | Dominant fallback |
|---|---:|---:|---|
| `attention` | 24 | 24 | `Hold(silent)`=24 |
| `interest` | 21 | 21 | `Hold(silent)`=18, `Hold(ambient)`=3 |
| `desire` | 21 | 19 | `Hold(silent)`=18, `Inform(comparison)`=3 |
| `action` | 24 | 24 | `Hold(silent)`=24 |

## Full Combination Table

| State | AIDA | Intent tier | Original candidates | Remaining after removing Reassure | Candidate count | Fallback |
|---|---|---|---|---|---:|---|
| `high_hesitation` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `high_hesitation` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `high_hesitation` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `high_hesitation` | `desire` | `exploring` | `Inform(comparison)`<br>`Elicit(need_focus)`<br>`Reassure(time)`<br>`Recommend(firm)` | `Inform(comparison)`<br>`Elicit(need_focus)`<br>`Recommend(firm)` | 3 | `Inform(comparison)` |
| `high_hesitation` | `desire` | `low_intent_browsing` | `Inform(comparison)`<br>`Elicit(need_focus)`<br>`Reassure(time)` | `Inform(comparison)`<br>`Elicit(need_focus)` | 2 | `Inform(comparison)` |
| `high_hesitation` | `desire` | `ready_to_buy` | `Inform(comparison)`<br>`Elicit(need_focus)`<br>`Reassure(time)`<br>`Recommend(firm)` | `Inform(comparison)`<br>`Elicit(need_focus)`<br>`Recommend(firm)` | 3 | `Inform(comparison)` |
| `high_hesitation` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `high_hesitation` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `high_hesitation` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `active_evaluation` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `active_evaluation` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `active_evaluation` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `active_evaluation` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `active_evaluation` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `active_evaluation` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `ready_to_decide` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `ready_to_decide` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `ready_to_decide` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `ready_to_decide` | `interest` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `ready_to_decide` | `interest` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `ready_to_decide` | `interest` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)`<br>`Recommend(firm)` | `Hold(silent)`<br>`Recommend(firm)` | 2 | `Hold(silent)` |
| `early_browsing` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)`<br>`Recommend(firm)` | `Hold(silent)`<br>`Recommend(firm)` | 2 | `Hold(silent)` |
| `early_browsing` | `interest` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `interest` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `interest` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `desire` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `desire` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `desire` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `early_browsing` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `interest` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `interest` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `interest` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `desire` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `desire` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `desire` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `post_decision_reassurance` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `interest` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `interest` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `interest` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `desire` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `desire` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `desire` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `disengaged` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `interest` | `exploring` | `Hold(ambient)`<br>`Reassure(time)` | `Hold(ambient)` | 1 | `Hold(ambient)` |
| `defensive_withdrawal` | `interest` | `low_intent_browsing` | `Hold(ambient)`<br>`Reassure(time)` | `Hold(ambient)` | 1 | `Hold(ambient)` |
| `defensive_withdrawal` | `interest` | `ready_to_buy` | `Hold(ambient)`<br>`Reassure(time)` | `Hold(ambient)` | 1 | `Hold(ambient)` |
| `defensive_withdrawal` | `desire` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `desire` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `desire` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `defensive_withdrawal` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `interest` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `interest` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `interest` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `desire` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `desire` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `desire` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `engaged_dialogue` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `attention` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `attention` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `attention` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `interest` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `interest` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `interest` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `desire` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `desire` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `desire` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `action` | `exploring` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `action` | `low_intent_browsing` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |
| `continued_hesitation` | `action` | `ready_to_buy` | `Hold(silent)`<br>`Reassure(time)` | `Hold(silent)` | 1 | `Hold(silent)` |

## Implication for Recommend(soft)

- Many Reassure-emitting combinations collapse to `Hold` only or `Hold` plus one task action after filtering; this is operationally safe but under-expressive.
- `attention` and `interest` combinations are the main place where a low-pressure `Recommend(soft)` can be considered only if it preserves choice and does not behave like firm closing.
- If `Recommend(soft)` is added to these low-candidate combinations, it should remain stage-gated and reward-calibrated so it does not replace `Hold` for low-intent browsing or disengagement.
