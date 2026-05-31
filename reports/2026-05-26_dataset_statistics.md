# B1 Dataset Statistics (2026-05-26)

Read-only statistics for the requested B1.1-B1.7 items. Counts are integers; percentages use one decimal place. No data files, training scripts, or 5-act definitions were modified.

## Data Sources

| Source | Role |
| --- | --- |
| data/official/piwm_train_synth_v2/state_inference.jsonl | 543 general user_intent scenes and BDI/intent/stage fields |
| data/official/piwm_train_synth_v2/transition_modeling.jsonl | 2001 next_state_prediction candidate rows |
| data/official/piwm_train_synth_v2/main_schema.jsonl | general scene lookup for action_selection imports |
| data/official/piwm_target_v1/main_schema.jsonl | target scene lookup for target train/test stage fields |
| data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl | 71 original unbalanced target train action_selection rows |
| data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl | 190 balanced action_selection train rows |
| data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl | 30 target test action_selection rows |
| data/official/domain_specialization_eval_v2/target_frontcam_5act_test_user_intent.jsonl | 30 target test user_intent stage/intent rows |
| reports/real_eval_20260525/manifest.json | 50 real-store before-video-filter stage/action counts |

## B1.1 AIDA Stage Distribution

This section counts AIDA stages for the requested six dataset surfaces. Target action rows are stage-filled from `data/official/piwm_target_v1/main_schema.jsonl` when the ms-swift action row does not carry `meta.stage`.

| Dataset | AIDA stage | count | percentage |
| --- | --- | --- | --- |
| 543 general scenes (user_intent training data) | action | 77 | 14.2% |
| 543 general scenes (user_intent training data) | attention | 49 | 9.0% |
| 543 general scenes (user_intent training data) | desire | 128 | 23.6% |
| 543 general scenes (user_intent training data) | interest | 289 | 53.2% |
| 2001 next_state_prediction samples (current stage) | action | 268 | 13.4% |
| 2001 next_state_prediction samples (current stage) | attention | 98 | 4.9% |
| 2001 next_state_prediction samples (current stage) | desire | 532 | 26.6% |
| 2001 next_state_prediction samples (current stage) | interest | 1103 | 55.1% |
| 71 target train videos | action | 5 | 7.0% |
| 71 target train videos | attention | 18 | 25.4% |
| 71 target train videos | desire | 17 | 23.9% |
| 71 target train videos | interest | 31 | 43.7% |
| 30 target test videos | action | 6 | 20.0% |
| 30 target test videos | attention | 3 | 10.0% |
| 30 target test videos | desire | 11 | 36.7% |
| 30 target test videos | interest | 10 | 33.3% |
| 50 real-store videos | action | 5 | 10.0% |
| 50 real-store videos | attention | 16 | 32.0% |
| 50 real-store videos | desire | 19 | 38.0% |
| 50 real-store videos | interest | 10 | 20.0% |
| 190 balanced action_selection training samples | action | 23 | 12.1% |
| 190 balanced action_selection training samples | attention | 63 | 33.2% |
| 190 balanced action_selection training samples | desire | 44 | 23.2% |
| 190 balanced action_selection training samples | interest | 60 | 31.6% |

Key observation: the 543 general scenes and 2001 next-state rows share the same parent-scene stage support, but next-state rows weight scenes by candidate count. The real-store 50-row counts come from the manifest before video filtering, not the 30 runnable-video subset.

## B1.2 best_action Distribution

This section reports the operational best action labels for target train, balanced train, target test, and real-store surfaces. Real-store uses manifest-level before-video-filter counts because the runnable JSONL contains only 30 rows.

| Dataset | best_action | count | percentage |
| --- | --- | --- | --- |
| 71 target train original unbalanced | Elicit | 14 | 19.7% |
| 71 target train original unbalanced | Greet | 11 | 15.5% |
| 71 target train original unbalanced | Inform | 41 | 57.7% |
| 71 target train original unbalanced | Recommend | 5 | 7.0% |
| 190 balanced action_selection train | Elicit | 41 | 21.6% |
| 190 balanced action_selection train | Greet | 26 | 13.7% |
| 190 balanced action_selection train | Hold | 41 | 21.6% |
| 190 balanced action_selection train | Inform | 41 | 21.6% |
| 190 balanced action_selection train | Recommend | 41 | 21.6% |
| 30 target test | Elicit | 6 | 20.0% |
| 30 target test | Greet | 6 | 20.0% |
| 30 target test | Hold | 6 | 20.0% |
| 30 target test | Inform | 6 | 20.0% |
| 30 target test | Recommend | 6 | 20.0% |
| 50 real-store | Elicit | 10 | 20.0% |
| 50 real-store | Greet | 10 | 20.0% |
| 50 real-store | Hold | 10 | 20.0% |
| 50 real-store | Inform | 10 | 20.0% |
| 50 real-store | Recommend | 10 | 20.0% |

Key observation: the 30 target test and 50 real-store manifest are both balanced at 20.0% per action. The 190-row balanced training set keeps Greet below the other four actions because no general Greet parent records were available in its source summary.

## B1.3 Intent Label Distribution

This section counts intent labels for the 543 general scenes and 30 target-test user_intent rows. The general count uses `output.intent`; the target-test count uses ms-swift `meta.intent_label`.

| Dataset | intent_label | count | percentage |
| --- | --- | --- | --- |
| 543 general scenes | compare_value_for_money | 16 | 2.9% |
| 543 general scenes | confirm_choice | 177 | 32.6% |
| 543 general scenes | explore_options | 94 | 17.3% |
| 543 general scenes | leave_without_purchase | 17 | 3.1% |
| 543 general scenes | negotiate_price | 55 | 10.1% |
| 543 general scenes | request_demonstration | 93 | 17.1% |
| 543 general scenes | seek_reassurance | 91 | 16.8% |
| 30 target test | compare_value_for_money | 6 | 20.0% |
| 30 target test | confirm_choice | 6 | 20.0% |
| 30 target test | explore_options | 15 | 50.0% |
| 30 target test | no_clear_intent | 3 | 10.0% |

Key observation: the general set has the requested 7 intent labels. The target test set uses a narrower label subset in its current 30-row evaluation file.

## B1.4 Candidate Set Size

This section summarizes candidate-set sizes for next_state and balanced action_selection. The `next_state parent scenes` row is the parent-scene view that confirms 2001 / 543 = 3.685.

| Dataset/view | n | mean | median | mode | hist_2 | hist_3 | hist_4 | hist_5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| next_state parent scenes | 543 | 3.685 | 4.0 | 4 | 87 | 59 | 335 | 62 |
| next_state sample rows | 2001 | 3.893 | 4.0 | 4 | 174 | 177 | 1340 | 310 |
| balanced action_selection rows | 190 | 3.605 | 4.0 | 4 | 42 | 26 | 87 | 35 |
| next_state sample rows + action_selection rows | 2191 | 3.868 | 4.0 | 4 | 216 | 203 | 1427 | 345 |

Key observation: the parent-scene next_state mean is 3.685, matching the requested check. The 190 action-selection rows have a separate row-level candidate-size distribution from `meta.candidate_action_acts`.

## B1.5 Outcome Score

The requested 1-5 candidate outcome score field is not present in `data/official/piwm_train_synth_v2/transition_modeling.jsonl`; the available outcome numeric field is `output.reward` in [-1, 1].

| act | candidate_rows_with_reward | percentage | reward_min | reward_mean | reward_max |
| --- | --- | --- | --- | --- | --- |
| Elicit | 476 | 23.8% | 0.20 | 0.732 | 0.83 |
| Hold | 449 | 22.4% | -0.25 | 0.165 | 0.50 |
| Inform | 481 | 24.0% | 0.70 | 0.785 | 0.80 |
| Recommend | 595 | 29.7% | -0.60 | -0.091 | 0.85 |
| ALL | 2001 | 100.0% | -0.60 | 0.373 | 0.85 |

Key observation: field `score_1_5` is unavailable for 2001 / 2001 next_state rows in the source file. The table above is the available reward field by act type, so it should not be read as a 1-5 score distribution.

## B1.6 BDI Field Lengths

This section reports character lengths for the 543 general-scene BDI fields. Lengths are measured directly from `output.bdi.{belief,desire,intention}` strings.

| BDI field | mean_chars | median_chars | min_chars | max_chars |
| --- | --- | --- | --- | --- |
| belief | 73.1 | 73.0 | 53 | 90 |
| desire | 26.8 | 27.0 | 21 | 32 |
| intention | 30.7 | 33.0 | 20 | 37 |

Key observation: `belief` is the longest BDI field on average, while `desire` and `intention` are shorter clause-like fields. All 543 rows contain the three requested BDI fields.

## B1.7 Same-Scene Cross-Task Coverage

This section checks how many of the 543 general scene IDs appear in both user_intent and next_state training, and how many appear in balanced action_selection training. For greet augmentation, `meta.augmented_from_state_id` is counted as the general parent scene.

| Coverage | overlapping_general_scenes | general_scene_total | percentage |
| --- | --- | --- | --- |
| user_intent + next_state_prediction | 543 | 543 | 100.0% |
| user_intent + action_selection_5act train | 110 | 543 | 20.3% |

Key observation: every general user_intent scene appears as a next_state parent. Balanced action_selection uses a subset of general scenes plus target rows, so its overlap with the 543 general scenes is smaller.

## Missing Fields / Assumptions

| Item | Status |
| --- | --- |
| B1.5 `score_1_5` | 字段 score_1_5 在 source data/official/piwm_train_synth_v2/transition_modeling.jsonl 里不可用；available numeric field is output.reward [-1,1]. |
| real-store 50 rows | Used reports/real_eval_20260525/manifest.json before-video-filter counts; runnable real JSONL has 30 rows after missing-video filtering. |
| target action stage | Filled from data/official/piwm_target_v1/main_schema.jsonl when action JSONL rows lack meta.stage. |
