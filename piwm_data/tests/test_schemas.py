import pytest
from pydantic import ValidationError

from piwm_data import rules
from piwm_data.schemas import (
    ActionContinuation,
    ActionOutcome,
    FrameRef,
    MainSchemaRecord,
    Persona,
    Provenance,
    ReactionFrameRef,
    ShootingClipRecord,
)


def make_outcome(action: str, **overrides):
    data = rules.derive_action_outcome("high_hesitation", "interest", "price_sensitive_cautious", action)
    data.update(overrides)
    return ActionOutcome(**data)


def make_record(**overrides):
    intent = "compare_value_for_money"
    data = {
        "state_id": "session_test_001",
        "images": [FrameRef(index=0, relative_path="Archive/session_test_001/frames/000.jpg")],
        "product_category": "luxury_watch",
        "split": "train",
        "observable_cues": ["long_dwell_with_price_check"],
        "persona": Persona(type="price_sensitive_cautious", description="测试用 persona"),
        "aida_stage": "interest",
        "latent_state": "high_hesitation",
        "intent": intent,
        "bdi": rules.derive_bdi("price_sensitive_cautious", "high_hesitation", intent, ["long_dwell_with_price_check"]),
        "proactive_score": 4,
        "candidate_actions": [
            "A1_silent_observe",
            "A2_offer_value_comparison",
            "A4_open_with_question",
        ],
        "best_action": "A2_offer_value_comparison",
        "next_state_by_action": {
            "A1_silent_observe": make_outcome("A1_silent_observe"),
            "A2_offer_value_comparison": make_outcome("A2_offer_value_comparison"),
            "A4_open_with_question": make_outcome("A4_open_with_question"),
        },
        "reward_by_action": {
            "A1_silent_observe": 0.3,
            "A2_offer_value_comparison": 0.8,
            "A4_open_with_question": 0.6,
        },
        "rationale": None,
        "provenance": [Provenance(field_name="latent_state", source="rule_derived", rule_version="v1.0")],
        "is_anchor": False,
    }
    data.update(overrides)
    return MainSchemaRecord(**data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("observable_cues", ["not_a_cue"]),
        ("product_category", "not_a_product"),
        ("split", "not_a_split"),
        ("latent_state", "not_a_state"),
        ("intent", "not_an_intent"),
        ("candidate_actions", ["A1_silent_observe", "not_an_action"]),
        ("best_action", "not_an_action"),
        ("aida_stage", "not_a_stage"),
        ("viewpoint", "not_a_viewpoint"),
        ("proactive_score", 6),
    ],
)
def test_main_schema_rejects_invalid_enum_values(field, value):
    with pytest.raises(ValidationError):
        make_record(**{field: value})


def test_persona_rejects_invalid_type():
    with pytest.raises(ValidationError):
        Persona(type="not_a_persona")


def test_action_outcome_rejects_invalid_next_state():
    data = rules.derive_action_outcome("high_hesitation", "interest", "price_sensitive_cautious", "A1_silent_observe")
    data["next_state"] = "not_a_state"
    with pytest.raises(ValidationError):
        ActionOutcome(**data)


def test_action_outcome_rejects_reward_out_of_range():
    data = rules.derive_action_outcome("high_hesitation", "interest", "price_sensitive_cautious", "A1_silent_observe")
    data["reward"] = 1.1
    data["reward_components"] = rules.derive_reward_components("interest", data["next_aida_stage"], "A1_silent_observe", 1.1)
    with pytest.raises(ValidationError):
        ActionOutcome(**data)


def test_action_outcome_rejects_inconsistent_reward_components():
    data = rules.derive_action_outcome("high_hesitation", "interest", "price_sensitive_cautious", "A1_silent_observe")
    data["reward_components"] = rules.derive_reward_components(
        "interest",
        data["next_aida_stage"],
        "A1_silent_observe",
        0.9,
    )
    with pytest.raises(ValidationError):
        ActionOutcome(**data)


def test_next_state_keys_must_cover_candidate_actions():
    record = make_record()
    next_state_by_action = dict(record.next_state_by_action)
    next_state_by_action.pop("A4_open_with_question")
    with pytest.raises(ValidationError):
        make_record(next_state_by_action=next_state_by_action)


def test_reward_by_action_must_match_next_state_rewards():
    reward_by_action = {
        "A1_silent_observe": 0.3,
        "A2_offer_value_comparison": 0.7,
        "A4_open_with_question": 0.6,
    }
    with pytest.raises(ValidationError):
        make_record(reward_by_action=reward_by_action)


def make_continuation(**overrides):
    data = {
        "continuation_id": "session_test_001#best_A2_offer_value_comparison",
        "parent_state_id": "session_test_001",
        "candidate_action": "A2_offer_value_comparison",
        "continuation_role": "best",
        "continuation_viewpoint": "salesperson_observable",
        "video_relative_path": "Archive/session_test_001/continuations/best_A2_offer_value_comparison/video.mp4",
        "frames": [
            ReactionFrameRef(index=0, relative_path="Archive/session_test_001/continuations/best_A2_offer_value_comparison/frames/000.jpg", role="reaction_onset"),
            ReactionFrameRef(index=1, relative_path="Archive/session_test_001/continuations/best_A2_offer_value_comparison/frames/001.jpg", role="reaction_peak"),
        ],
        "duration_seconds": 5,
        "expected_next_state": "engaged_dialogue",
        "expected_next_aida_stage": "desire",
        "expected_reward": 0.8,
        "expected_risk": "low",
        "expected_benefit": "high",
        "reaction_template_id": "REACT_ENGAGED_DIALOGUE_001",
        "qa_overall_pass": True,
        "reaction_visible": True,
        "reaction_matches_expected_state": True,
        "pre_action_continuity_pass": True,
    }
    data.update(overrides)
    return ActionContinuation(**data)


def test_main_schema_default_continuations_is_empty():
    record = make_record()
    assert record.continuations == {}


def test_main_schema_fills_v2_dialogue_act_and_terminal_realization():
    record = make_record()
    assert record.dialogue_act == "Inform"
    assert record.act_params == {"content_type": "comparison", "depth": "brief"}
    assert record.realization is not None
    assert record.realization.dialogue_act == "Inform"
    assert record.realization.screen["action"] == "show_comparison_or_details"


def test_main_schema_rejects_invalid_dialogue_act_params():
    with pytest.raises(ValidationError):
        make_record(dialogue_act="Inform", act_params={"content_type": "not_valid", "depth": "brief"})


def test_shooting_clip_record_fills_v2_action_contract_from_prior():
    record = ShootingClipRecord(
        clip_id="G001_S05_A",
        group_id="G001",
        shooting_state="S05_BROWSE_UNC",
        version="A",
        product_category="electronics_phone",
        persona_type="price_sensitive_cautious",
    )
    assert record.state_name_zh == "犹豫比较"
    assert record.response_type_zh == "提供信息-比较两件"
    assert record.legacy_action == "A2_offer_value_comparison"
    assert record.t_state == "T2_VALUE_COMPARE"
    assert record.dialogue_act == "Inform"
    assert record.act_params["content_type"] == "comparison"
    assert record.terminal_realization is not None
    assert record.terminal_realization.dialogue_act == "Inform"
    assert record.terminal_realization.screen["action"] == "show_comparison_or_details"
    assert record.expected_reaction == "进入澄清，犹豫缓解"
    assert record.requires_hero_view is True


def test_shooting_clip_record_supports_transaction_without_legacy_action():
    record = ShootingClipRecord(
        clip_id="G001_S12_A",
        group_id="G001",
        shooting_state="S12_EXIT_POST",
        version="A",
        product_category="luxury_watch",
        persona_type="price_insensitive_decisive",
    )
    assert record.legacy_action is None
    assert record.t_state == "T_TRANSACT"
    assert record.dialogue_act == "Greet"
    assert record.act_params == {"phase": "close"}
    assert record.terminal_realization is not None
    assert record.terminal_realization.legacy_action is None
    assert record.terminal_realization.surface_text == "感谢惠顾，祝您使用愉快。"


def test_shooting_clip_record_rejects_response_contract_mismatch():
    with pytest.raises(ValidationError):
        ShootingClipRecord(
            clip_id="G001_S05_A",
            group_id="G001",
            shooting_state="S05_BROWSE_UNC",
            version="A",
            product_category="electronics_phone",
            persona_type="price_sensitive_cautious",
            response_type_zh="建议推荐-力度强势",
        )


def test_shooting_clip_record_rejects_response_param_mismatch():
    with pytest.raises(ValidationError):
        ShootingClipRecord(
            clip_id="G001_S05_A",
            group_id="G001",
            shooting_state="S05_BROWSE_UNC",
            version="A",
            product_category="electronics_phone",
            persona_type="price_sensitive_cautious",
            response_type_zh="提供信息-演示一件",
            legacy_action="A5_provide_demonstration",
            t_state="T5_DEMO",
            dialogue_act="Inform",
            act_params={"content_type": "comparison", "depth": "brief"},
        )


def test_main_schema_accepts_valid_action_continuation():
    continuation = make_continuation()
    record = make_record(continuations={"A2_offer_value_comparison": continuation})
    assert record.continuations["A2_offer_value_comparison"].qa_overall_pass is True


def test_main_schema_rejects_continuation_not_in_candidates():
    continuation = make_continuation(candidate_action="A3_strong_recommend")
    with pytest.raises(ValidationError):
        make_record(continuations={"A3_strong_recommend": continuation})


def test_main_schema_rejects_continuation_viewpoint_mismatch():
    continuation = make_continuation(continuation_viewpoint="surveillance_oblique")
    with pytest.raises(ValidationError):
        make_record(continuations={"A2_offer_value_comparison": continuation})
