import pytest

from piwm_data.migration.legacy_action_mapping import (
    LEGACY_ACTION_TO_ACT_PARAMS,
    act_params_to_legacy_for_comparison,
    legacy_action_to_act_params_for_comparison,
    legacy_to_v2,
)


def test_legacy_mapping_covers_all_a1_a8_labels():
    assert set(LEGACY_ACTION_TO_ACT_PARAMS) == {
        "A1_silent_observe",
        "A2_offer_value_comparison",
        "A3_strong_recommend",
        "A4_open_with_question",
        "A5_provide_demonstration",
        "A6_acknowledge_and_wait",
        "A7_disengage",
        "A8_offer_companion_invite",
    }


@pytest.mark.parametrize("legacy_action", sorted(LEGACY_ACTION_TO_ACT_PARAMS))
def test_each_legacy_action_maps_to_valid_v2_shape(legacy_action):
    spec = legacy_to_v2(legacy_action)
    assert set(spec) == {"act", "params", "co_acts"}
    assert spec["act"]
    assert isinstance(spec["params"], dict)
    assert isinstance(spec["co_acts"], list)


def test_legacy_mapping_is_copy_safe():
    spec = legacy_to_v2("A6_acknowledge_and_wait")
    spec["params"]["focus"] = "decision"
    assert legacy_to_v2("A6_acknowledge_and_wait")["params"]["focus"] == "time"


def test_comparison_helpers_round_trip_exact_canonical_actions():
    act, params = legacy_action_to_act_params_for_comparison("A3_strong_recommend")
    assert (act, params) == ("Recommend", {"target": "item", "pressure": "firm"})
    assert act_params_to_legacy_for_comparison(act, params) == "A3_strong_recommend"
    assert act_params_to_legacy_for_comparison("Recommend", {"target": "item", "pressure": "soft"}) is None
