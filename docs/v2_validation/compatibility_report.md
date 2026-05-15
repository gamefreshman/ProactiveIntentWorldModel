# PIWM v2.2 Compatibility Report

- Source: `data/official/piwm_train_synth_v2/main_schema.jsonl`
- Records: 543

## Basic Schema Compatibility Tiers

This tier comes from the schema-level migration checks only. It covers v2 mirror-field mismatches and `intent_tier_visual_mismatch`; it does not by itself prove that old `best_action` matches the v2 policy re-derivation.

| Tier | Count | Ratio |
|---|---:|---:|
| green | 462 | 85.08% |
| yellow | 0 | 0.00% |
| red | 81 | 14.92% |

## Basic Mismatch Flags

| Flag | Count |
|---|---:|
| intent_tier_visual_mismatch | 81 |

## Extended V2 Re-derivation Audit

This audit re-derives `latent_state` from observable cues and re-picks the best v2 policy action with `derive_policy_candidate_specs()` + `pick_best_action_spec()`. It is stricter than the schema tier above.

| Tier | Count | Ratio |
|---|---:|---:|
| green | 109 | 20.07% |
| yellow | 353 | 65.01% |
| red | 81 | 14.92% |

### Extended Flags

| Flag | Count |
|---|---:|
| best_action_drift | 393 |
| intent_tier_visual_mismatch | 81 |

## Intent Tier Distribution

| Intent Tier | Count |
|---|---:|
| exploring | 259 |
| low_intent_browsing | 94 |
| ready_to_buy | 190 |

## Official Best Act Distribution

| Act | Count |
|---|---:|
| Elicit | 69 |
| Hold | 59 |
| Inform | 407 |
| Reassure | 8 |

## Official 543 Re-derived V2 Policy Best Distribution

| Act | Count |
|---|---:|
| Elicit | 252 |
| Hold | 25 |
| Inform | 105 |
| Reassure | 42 |
| Recommend | 119 |

### Policy Drift Matrix

| Old best act | Re-derived v2 best act | Count |
|---|---|---:|
| Elicit | Recommend | 57 |
| Hold | Reassure | 34 |
| Inform | Elicit | 240 |
| Inform | Recommend | 62 |

## Candidate Rule Coverage In Official Records

| Coverage | Count |
|---|---:|
| default_fallback | 25 |
| explicit | 518 |

## Red Samples By Persona

| Persona | Red | Total | Red Ratio |
|---|---:|---:|---:|
| browser_low_intent | 81 | 94 | 86.17% |
| experienced_brand_loyal | 0 | 101 | 0.00% |
| first_time_high_consideration | 0 | 89 | 0.00% |
| gift_buyer_uncertain | 0 | 73 | 0.00% |
| price_insensitive_decisive | 0 | 89 | 0.00% |
| price_sensitive_cautious | 0 | 97 | 0.00% |

## Interpretation

- Basic `yellow=0` is a detector-scope result, not proof that no policy drift exists.
- Extended audit finds substantial `best_action_drift`; these rows should be treated as policy-migration yellow unless they also carry red semantic conflicts.
- The 81 red rows concentrate in `browser_low_intent`; this reflects legacy video/prompt generation not strongly differentiating low purchase intent from high engagement cues.
- `latent_state_mismatch=0` means current cue-derived state labels are internally consistent for this official file.
