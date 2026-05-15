# PIWM v2.2 Test Coverage Notes

更新时间：2026-05-15

本页记录 v2.2 迁移新增或直接覆盖的测试点，避免只用总测试通过数掩盖新逻辑是否被测。

## Core Rule Tests

| File | Test | Coverage |
|---|---|---|
| `piwm_data/tests/test_rules.py` | `test_derive_intent_tier_uses_v2_persona_prior` | persona -> intent tier |
| `piwm_data/tests/test_rules.py` | `test_policy_candidate_specs_split_soft_and_firm_recommendation` | soft/firm Recommend split |
| `piwm_data/tests/test_rules.py` | `test_policy_candidate_specs_keep_low_intent_filter` | low-intent filter removes firm recommend |
| `piwm_data/tests/test_rules.py` | `test_failure_mode_triggers_from_v2_context` | failure DSL trigger path |
| `piwm_data/tests/test_rules.py` | `test_soft_recommend_uses_recommend_transition_family_without_pressure_failure` | soft Recommend outcome path |
| `piwm_data/tests/test_rules.py` | `test_pick_best_action_spec_prefers_soft_recommend_at_decision_time` | v2 policy best action selection |
| `piwm_data/tests/test_rules.py` | `test_v2_reward_calibration_boosts_open_elicitation_during_active_interest` | Elicit reward calibration |

## Schema And Migration Tests

| File | Test | Coverage |
|---|---|---|
| `piwm_data/tests/test_legacy_action_mapping.py` | `test_each_legacy_action_maps_to_valid_v2_shape` | all A1-A8 explicit migration mapping |
| `piwm_data/tests/test_schemas.py` | `test_candidate_action_normalizes_legacy_label_without_legacy_field` | `CandidateAction` canonical object excludes `legacy_action` |
| `piwm_data/tests/test_schemas.py` | `test_action_outcome_keeps_v2_policy_fields` | `risk_tags / failure_mode / outcome_type` preserved |
| `piwm_data/tests/test_schemas.py` | `test_main_schema_fills_v2_dialogue_act_and_terminal_realization` | `candidate_action_specs / best_action_spec` auto fill |
| `piwm_data/tests/test_schemas.py` | `test_main_schema_fills_next_state_by_action_v2_with_stable_action_keys` | v2 action-keyed next-state map |
| `piwm_data/tests/test_schemas.py` | `test_main_schema_flags_v2_action_spec_mismatch_without_rejecting` | yellow mirror mismatch path |
| `piwm_data/tests/test_schemas.py` | `test_main_schema_marks_low_intent_high_engagement_as_red` | red `intent_tier_visual_mismatch` path |
| `piwm_data/tests/test_archive_loader.py` | `test_load_session_applies_intent_tier_candidate_filter` | archive loader v2 filter path |

## Export And Scenario Tests

| File | Test | Coverage |
|---|---|---|
| `piwm_data/tests/test_exporters.py` | `test_state_inference_exports_one_row` | v2 action specs and compatibility tier in state export |
| `piwm_data/tests/test_exporters.py` | `test_main_schema_record_payload_serializes_next_state_by_action_v2` | canonical main-schema payload includes v2 next-state map |
| `piwm_data/tests/test_exporters.py` | `test_transition_modeling_exports_one_row_per_candidate` | transition rows include action spec and outcome fields |
| `piwm_data/tests/test_compatibility_report.py` | `test_compatibility_report_includes_extended_rederivation_audit` | compatibility report includes extended policy re-derivation audit |
| `piwm_data/tests/test_refresh_official_v2_exports.py` | `test_refresh_official_v2_exports_can_write_independent_output_dir` | independent v2 export does not overwrite source dataset |
| `piwm_data/tests/test_refresh_official_v2_exports.py` | `test_refresh_official_v2_exports_rejects_output_dir_with_multiple_sources` | guardrail for ambiguous independent output |
| `piwm_data/tests/test_refresh_official_v2_exports.py` | `test_refresh_official_v2_exports_dry_run_output_diff_does_not_rewrite_source` | `--output-diff` dry-run writes preview without rewriting source |
| `piwm_data/tests/test_phase3_scripts.py` | `test_scenario_sampler_writes_v2_action_specs_and_intent_tier_filter` | scenario manifest v2 fields |
| `piwm_data/tests/test_phase3_scripts.py` | `test_scenario_sampler_policy_path_can_select_soft_recommend` | policy path can select soft Recommend |
| `piwm_data/tests/test_phase3_scripts.py` | `test_scenario_sampler_candidate_rule_only_filters_default_fallbacks` | explicit candidate-rule slice |
| `piwm_data/tests/test_qa_gate.py` | `test_check_label_leakage_flags_internal_v2_labels` | Kling prompt label leakage guard |

## Current Gaps

- `next_state_by_action_v2` exists and is tested. v2.3 still needs cleanup tests before removing legacy A-key dependencies.
- v2.3 cleanup should add negative tests proving downstream loaders no longer require legacy A-key maps before removing them.
