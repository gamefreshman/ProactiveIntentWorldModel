from piwm_data import rules


def test_each_cue_prior_maps_to_expected_state():
    for cue, expected_state in rules.CUE_TO_STATE_PRIOR.items():
        assert rules.derive_latent_state([cue]) == expected_state


def test_multi_cue_priority_ready_to_decide_is_strongest():
    assert rules.derive_latent_state(["no_eye_contact_avoidant", "approaching_counter"]) == "ready_to_decide"
    assert rules.derive_latent_state(["brief_glance_walking_past", "looking_around_for_help"]) == "ready_to_decide"


def test_multi_cue_priority_active_evaluation_before_long_dwell():
    assert rules.derive_latent_state(["long_dwell_with_price_check", "comparing_two_products"]) == "active_evaluation"


def test_multi_cue_priority_long_dwell_before_disengaged():
    assert rules.derive_latent_state(["no_eye_contact_avoidant", "long_dwell_with_price_check"]) == "high_hesitation"


def test_low_intensity_cues_map_to_early_browsing():
    assert rules.derive_latent_state(["brief_glance_walking_past"]) == "early_browsing"


def test_derive_intent_hits_persona_state_mapping():
    assert rules.derive_intent("price_sensitive_cautious", "high_hesitation") == "compare_value_for_money"


def test_derive_intent_uses_state_fallback():
    assert rules.derive_intent("browser_low_intent", "active_evaluation") == "explore_options"


def test_derive_intent_tier_uses_v2_persona_prior():
    assert rules.derive_intent_tier("browser_low_intent") == "low_intent_browsing"
    assert rules.derive_intent_tier("gift_buyer_uncertain") == "exploring"
    assert rules.derive_intent_tier("unknown_persona") == "exploring"


def test_derive_bdi_returns_explicit_three_part_summary():
    bdi = rules.derive_bdi(
        "price_sensitive_cautious",
        "high_hesitation",
        "compare_value_for_money",
        ["long_dwell_with_price_check"],
    )
    assert set(bdi) == {"belief", "desire", "intention"}
    assert all(bdi.values())
    assert "long_dwell_with_price_check" not in bdi["belief"]
    assert "Observable cue" not in bdi["belief"]


def test_derive_action_outcome_adds_world_model_fields():
    outcome = rules.derive_action_outcome(
        "high_hesitation",
        "interest",
        "price_sensitive_cautious",
        "A2_offer_value_comparison",
    )
    assert outcome["next_state"] == "engaged_dialogue"
    assert outcome["next_aida_stage"] == "desire"
    assert outcome["next_bdi"]["belief"]
    assert outcome["reward_components"]["final_reward"] == outcome["reward"]
    assert outcome["rationale"]


def test_reward_components_preserve_scalar_reward_formula():
    components = rules.derive_reward_components("interest", "desire", "A2_offer_value_comparison", 0.8)
    reconstructed = (
        components["alpha"] * components["delta_stage"]
        + components["beta"] * components["delta_mental"]
        - components["gamma"] * components["action_cost"]
    )
    assert abs(reconstructed - 0.8) < 1e-9


def test_pick_best_action_uses_highest_reward():
    assert (
        rules.pick_best_action(
            "high_hesitation",
            ["A1_silent_observe", "A2_offer_value_comparison", "A4_open_with_question", "A3_strong_recommend"],
        )
        == "A2_offer_value_comparison"
    )


def test_candidate_sets_include_negative_intervention_contrast():
    assert "A3_strong_recommend" in rules.derive_candidate_actions("high_hesitation", "interest")
    assert "A3_strong_recommend" in rules.derive_candidate_actions("active_evaluation", "interest")
    assert "A3_strong_recommend" in rules.derive_candidate_actions("early_browsing", "attention")
    assert "A1_silent_observe" in rules.derive_candidate_actions("ready_to_decide", "action")


def test_low_intent_candidate_filter_removes_firm_recommendation():
    candidates = rules.derive_candidate_actions(
        "early_browsing",
        "attention",
        intent_tier="low_intent_browsing",
    )
    assert candidates == ["A1_silent_observe", "A6_acknowledge_and_wait"]
    specs = rules.derive_candidate_action_specs(
        "early_browsing",
        "attention",
        intent_tier="low_intent_browsing",
    )
    assert specs == [
        {"act": "Hold", "params": {"mode": "silent"}},
        {
            "act": "Reassure",
            "params": {
                "focus": "time",
                "supporting_acts": [{"type": "Hold", "params": {"mode": "ambient"}}],
            },
        },
    ]


def test_policy_candidate_specs_split_soft_and_firm_recommendation():
    specs = rules.derive_policy_candidate_specs(
        "ready_to_decide",
        "action",
        intent_tier="ready_to_buy",
    )

    recommend_specs = [spec for spec in specs if spec["act"] == "Recommend"]
    assert recommend_specs == [
        {"act": "Recommend", "params": {"target": "item", "pressure": "soft"}},
        {"act": "Recommend", "params": {"target": "item", "pressure": "firm"}},
    ]


def test_policy_candidate_specs_keep_low_intent_filter():
    specs = rules.derive_policy_candidate_specs(
        "early_browsing",
        "attention",
        intent_tier="low_intent_browsing",
    )

    assert all(spec["act"] != "Recommend" for spec in specs)


def test_negative_intervention_transitions_cross_zero():
    assert rules.derive_transition("high_hesitation", "A3_strong_recommend")["reward"] < 0
    assert rules.derive_transition("active_evaluation", "A3_strong_recommend")["reward"] < 0
    assert rules.derive_transition("early_browsing", "A3_strong_recommend")["reward"] < 0
    assert rules.derive_transition("ready_to_decide", "A1_silent_observe")["reward"] < 0


def test_pick_best_action_tie_breaks_by_lower_risk(monkeypatch):
    monkeypatch.setitem(
        rules.TRANSITION_TABLE,
        ("early_browsing", "A1_silent_observe"),
        {"next_state": "early_browsing", "reward": 0.5, "risk": "medium", "benefit": "high"},
    )
    monkeypatch.setitem(
        rules.TRANSITION_TABLE,
        ("early_browsing", "A6_acknowledge_and_wait"),
        {"next_state": "early_browsing", "reward": 0.5, "risk": "low", "benefit": "low"},
    )
    assert (
        rules.pick_best_action("early_browsing", ["A1_silent_observe", "A6_acknowledge_and_wait"])
        == "A6_acknowledge_and_wait"
    )


def test_pick_best_action_tie_breaks_by_higher_benefit(monkeypatch):
    monkeypatch.setitem(
        rules.TRANSITION_TABLE,
        ("early_browsing", "A1_silent_observe"),
        {"next_state": "early_browsing", "reward": 0.5, "risk": "low", "benefit": "medium"},
    )
    monkeypatch.setitem(
        rules.TRANSITION_TABLE,
        ("early_browsing", "A6_acknowledge_and_wait"),
        {"next_state": "early_browsing", "reward": 0.5, "risk": "low", "benefit": "high"},
    )
    assert (
        rules.pick_best_action("early_browsing", ["A1_silent_observe", "A6_acknowledge_and_wait"])
        == "A6_acknowledge_and_wait"
    )


def test_pick_best_action_tie_breaks_by_global_action_order():
    assert (
        rules.pick_best_action("early_browsing", ["A6_acknowledge_and_wait", "A1_silent_observe"])
        == "A1_silent_observe"
    )


def test_failure_mode_triggers_from_v2_context():
    failure = rules.derive_failure_mode(
        "early_browsing",
        "attention",
        "Recommend",
        {"target": "item", "pressure": "firm"},
        "browser_low_intent",
        "low_intent_browsing",
        ["brief_glance_walking_past"],
    )
    assert failure is not None
    assert failure["reward_override"] == -0.7
    outcome = rules.derive_action_outcome(
        "early_browsing",
        "attention",
        "browser_low_intent",
        act="Recommend",
        params={"target": "item", "pressure": "firm"},
        intent_tier="low_intent_browsing",
        visible_cues=["brief_glance_walking_past"],
    )
    assert outcome["outcome_type"] == "failure"
    assert outcome["reward"] == -0.7
    assert outcome["failure_mode"]
    assert "pressure_reactance" in outcome["risk_tags"]


def test_failure_mode_does_not_trigger_when_context_is_not_matched():
    assert rules.derive_failure_mode(
        "early_browsing",
        "attention",
        "Recommend",
        {"target": "item", "pressure": "firm"},
        "price_insensitive_decisive",
        "ready_to_buy",
        ["approaching_counter"],
    ) is None


def test_soft_recommend_uses_recommend_transition_family_without_pressure_failure():
    outcome = rules.derive_action_outcome(
        "ready_to_decide",
        "action",
        "price_insensitive_decisive",
        act="Recommend",
        params={"target": "item", "pressure": "soft"},
        intent_tier="ready_to_buy",
        visible_cues=["approaching_counter"],
    )
    assert outcome["dialogue_act"] == "Recommend"
    assert outcome["act_params"]["pressure"] == "soft"
    assert outcome["reward"] == 0.85
    assert outcome["outcome_type"] == "success"


def test_pick_best_action_spec_prefers_soft_recommend_at_decision_time():
    best = rules.pick_best_action_spec(
        "ready_to_decide",
        "action",
        "price_insensitive_decisive",
        intent_tier="ready_to_buy",
        visible_cues=["approaching_counter"],
    )

    assert best == {"act": "Recommend", "params": {"target": "item", "pressure": "soft"}}


def test_v2_reward_calibration_boosts_open_elicitation_during_active_interest():
    outcome = rules.derive_action_outcome(
        "active_evaluation",
        "interest",
        "gift_buyer_uncertain",
        act="Elicit",
        params={"openness": "open", "slot": "need_focus"},
        intent_tier="exploring",
        visible_cues=["comparing_two_products"],
    )

    assert outcome["reward"] == 0.83
    assert outcome["risk"] == "low"


def test_dialogue_act_schema_contains_six_policy_acts():
    assert rules.DIALOGUE_ACTS == ["Greet", "Elicit", "Inform", "Recommend", "Reassure", "Hold"]
    assert rules.DIALOGUE_ACT_DIMENSION["Inform"] == "Task"
    assert rules.DIALOGUE_ACT_DIMENSION["Hold"] == "Turn Management"


def test_legacy_action_to_dialogue_act_mapping_is_compatible():
    assert rules.legacy_action_to_act("A1_silent_observe")["act"] == "Hold"
    assert rules.legacy_action_to_act("A2_offer_value_comparison")["params"]["content_type"] == "comparison"
    assert rules.legacy_action_to_act("A3_strong_recommend")["params"]["pressure"] == "firm"
    a6 = rules.legacy_action_to_act("A6_acknowledge_and_wait")
    assert a6["params"]["supporting_acts"][0]["type"] == "Hold"
    assert a6["co_acts"][0]["act"] == "Hold"


def test_supporting_acts_are_validated_as_act_params():
    params = {
        "focus": "time",
        "supporting_acts": [{"type": "Hold", "params": {"mode": "ambient"}}],
    }
    rules.validate_dialogue_act("Reassure", params)
    assert rules.legacy_co_acts_from_params(params) == [{"act": "Hold", "params": {"mode": "ambient"}}]


def test_dialogue_act_to_legacy_action_round_trip_defaults():
    spec = rules.legacy_action_to_act("A5_provide_demonstration")
    assert rules.act_to_legacy_action(spec["act"], spec["params"]) == "A5_provide_demonstration"
    assert rules.act_to_legacy_action("Recommend", {"target": "item", "pressure": "firm"}) == "A3_strong_recommend"
    assert rules.act_to_legacy_action("Hold", {"mode": "silent"}) == "A1_silent_observe"


def test_t_state_and_s05_shooting_mapping_follow_new_contract():
    assert rules.t_state_to_act("T2_VALUE_COMPARE")["act"] == "Inform"
    assert rules.response_type_to_act("提供信息-比较两件")["params"]["content_type"] == "comparison"
    assert rules.S05_AB_DIALOGUE_ACTS["G001_S05_A"]["legacy_action"] == "A2_offer_value_comparison"
    assert rules.S05_AB_DIALOGUE_ACTS["G001_S05_B"]["params"]["pressure"] == "firm"


def test_all_shooting_state_response_priors_resolve_to_dialogue_acts():
    assert len(rules.SHOOTING_STATE_RESPONSE_PRIOR) == 24
    for state in rules.SHOOTING_CUSTOMER_STATES:
        for version in ("A", "B"):
            prior = rules.shooting_state_response_prior(state, version)
            assert prior["act"] in rules.DIALOGUE_ACTS
            assert prior["response_type_zh"]
            assert prior["expected_reaction"]
    assert rules.shooting_state_response_prior("S03_HOVER", "A")["requires_hero_view"] is True
    assert rules.shooting_state_response_prior("S01_PASSBY", "A")["requires_hero_view"] is False


def test_terminal_realization_has_default_template_for_each_legacy_action():
    for action in rules.ACTIONS:
        realization = rules.derive_terminal_realization(
            action,
            "active_evaluation",
            "price_sensitive_cautious",
            "luxury_watch",
            ["comparing_two_products"],
        )
        assert realization["dialogue_act"] in rules.DIALOGUE_ACTS
        assert realization["screen"]["action"]
        assert realization["voice_style"]
        assert realization["duration_ms"] >= 0
