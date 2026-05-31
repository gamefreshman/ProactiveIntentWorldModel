from __future__ import annotations

import json
from pathlib import Path

import pytest

from piwm_infer.decision_loop import PIWMDecisionLoop
from piwm_train import config

from .fixtures.mock_vlm import MockVLM, default_outputs


ROOT = Path(__file__).resolve().parents[2]


def _state_row() -> dict:
    with (ROOT / "data/piwm_dataset_pilot30/state_inference.jsonl").open(encoding="utf-8") as handle:
        return json.loads(next(line for line in handle if line.strip()))


def test_decision_loop_runs_four_heads_and_selects_action() -> None:
    vlm = MockVLM()
    decision = PIWMDecisionLoop(vlm).decide(_state_row())
    assert decision.chosen_action == "A2_offer_value_comparison"
    assert decision.per_candidate["A2_offer_value_comparison"].reaction_caption == "the customer turns toward the salesperson"
    roles = [call["role"] for call in vlm.calls]
    assert roles == [
        "perception",
        "deliberation:A1_silent_observe",
        "continuation:A1_silent_observe",
        "deliberation:A2_offer_value_comparison",
        "continuation:A2_offer_value_comparison",
        "action",
    ]


def test_decision_loop_perception_parse_failure_falls_back() -> None:
    outputs = default_outputs()
    outputs["perception"] = f"{config.TAG_STAGE_OPEN}bad{config.TAG_STAGE_CLOSE}"
    decision = PIWMDecisionLoop(MockVLM(outputs)).decide(_state_row())
    assert decision.used_fallback is True
    assert decision.chosen_action == "A6_acknowledge_and_wait"
    assert decision.errors


def test_decision_loop_all_deliberation_failures_fallback_to_candidate() -> None:
    outputs = default_outputs()
    outputs["deliberation:A1_silent_observe"] = "bad"
    outputs["deliberation:A2_offer_value_comparison"] = "bad"
    decision = PIWMDecisionLoop(MockVLM(outputs)).decide(_state_row())
    assert decision.used_fallback is True
    assert decision.chosen_action == "A1_silent_observe"
    assert len(decision.errors) == 2


def test_decision_loop_action_parse_failure_fallback_to_highest_reward() -> None:
    outputs = default_outputs()
    outputs["action"] = "\n".join(
        [
            f"{config.TAG_RATIONALE_OPEN}bad choice{config.TAG_RATIONALE_CLOSE}",
            f"{config.TAG_CHOSEN_OPEN}A3_strong_recommend{config.TAG_CHOSEN_CLOSE}",
            f"{config.TAG_INTERVENTION_ACTION_OPEN}point to one product{config.TAG_INTERVENTION_ACTION_CLOSE}",
            f"{config.TAG_INTERVENTION_UTTERANCE_OPEN}I recommend this one.{config.TAG_INTERVENTION_UTTERANCE_CLOSE}",
        ]
    )
    decision = PIWMDecisionLoop(MockVLM(outputs)).decide(_state_row())
    assert decision.used_fallback is True
    assert decision.chosen_action == "A2_offer_value_comparison"


def test_decision_loop_five_act_mode_filters_reassure_candidates_and_rejects_reassure_output() -> None:
    outputs = default_outputs()
    outputs["perception"] = outputs["perception"].replace(
        "A1_silent_observe, A2_offer_value_comparison",
        "Reassure_dbe6016c33c1, Greet_4f8123f9f15e, Inform_5ac252a82695",
    )
    outputs["deliberation:Greet_4f8123f9f15e"] = "\n".join(
        [
            f"{config.TAG_NEXT_STAGE_OPEN}interest{config.TAG_NEXT_STAGE_CLOSE}",
            f"{config.TAG_NEXT_BELIEF_OPEN}the terminal can provide help{config.TAG_NEXT_BELIEF_CLOSE}",
            f"{config.TAG_NEXT_DESIRE_OPEN}understand available support{config.TAG_NEXT_DESIRE_CLOSE}",
            f"{config.TAG_NEXT_INTENTION_OPEN}stay open to interaction{config.TAG_NEXT_INTENTION_CLOSE}",
            f"{config.TAG_RISK_OPEN}low{config.TAG_RISK_CLOSE}",
            f"{config.TAG_BENEFIT_OPEN}medium{config.TAG_BENEFIT_CLOSE}",
            f"{config.TAG_REWARD_OPEN}0.40{config.TAG_REWARD_CLOSE}",
        ]
    )
    outputs["continuation:Greet_4f8123f9f15e"] = (
        f"{config.TAG_REACTION_CAPTION_OPEN}the customer notices the greeting"
        f"{config.TAG_REACTION_CAPTION_CLOSE}"
    )
    outputs["deliberation:Inform_5ac252a82695"] = "\n".join(
        [
            f"{config.TAG_NEXT_STAGE_OPEN}desire{config.TAG_NEXT_STAGE_CLOSE}",
            f"{config.TAG_NEXT_BELIEF_OPEN}comparison is clearer{config.TAG_NEXT_BELIEF_CLOSE}",
            f"{config.TAG_NEXT_DESIRE_OPEN}choose confidently{config.TAG_NEXT_DESIRE_CLOSE}",
            f"{config.TAG_NEXT_INTENTION_OPEN}continue comparing{config.TAG_NEXT_INTENTION_CLOSE}",
            f"{config.TAG_RISK_OPEN}low{config.TAG_RISK_CLOSE}",
            f"{config.TAG_BENEFIT_OPEN}high{config.TAG_BENEFIT_CLOSE}",
            f"{config.TAG_REWARD_OPEN}0.70{config.TAG_REWARD_CLOSE}",
        ]
    )
    outputs["continuation:Inform_5ac252a82695"] = (
        f"{config.TAG_REACTION_CAPTION_OPEN}the customer looks at the comparison"
        f"{config.TAG_REACTION_CAPTION_CLOSE}"
    )
    outputs["action"] = "\n".join(
        [
            f"{config.TAG_RATIONALE_OPEN}reassurance is outside the main path{config.TAG_RATIONALE_CLOSE}",
            f"{config.TAG_CHOSEN_OPEN}Reassure_dbe6016c33c1{config.TAG_CHOSEN_CLOSE}",
            f"{config.TAG_INTERVENTION_ACTION_OPEN}offer reassurance{config.TAG_INTERVENTION_ACTION_CLOSE}",
            f"{config.TAG_INTERVENTION_UTTERANCE_OPEN}No rush.{config.TAG_INTERVENTION_UTTERANCE_CLOSE}",
        ]
    )

    vlm = MockVLM(outputs)
    decision = PIWMDecisionLoop(vlm, five_act_only=True).decide(_state_row())

    assert decision.candidates == ["Greet_4f8123f9f15e", "Inform_5ac252a82695"]
    assert "Reassure_dbe6016c33c1" not in decision.per_candidate
    assert "Greet_4f8123f9f15e" in decision.per_candidate
    assert decision.chosen_action == "Inform_5ac252a82695"
    assert all("Reassure_" not in str(call["role"]) for call in vlm.calls)
    assert any("Greet_" in str(call["role"]) for call in vlm.calls)


def test_decision_loop_hold_prior_calibration_demotes_overpredicted_hold() -> None:
    outputs = default_outputs()
    outputs["perception"] = outputs["perception"].replace(
        "A1_silent_observe, A2_offer_value_comparison",
        "Hold_eda24b4bb712, Inform_5ac252a82695",
    )
    outputs["deliberation:Hold_eda24b4bb712"] = "\n".join(
        [
            f"{config.TAG_NEXT_STAGE_OPEN}interest{config.TAG_NEXT_STAGE_CLOSE}",
            f"{config.TAG_NEXT_BELIEF_OPEN}the terminal waits silently{config.TAG_NEXT_BELIEF_CLOSE}",
            f"{config.TAG_NEXT_DESIRE_OPEN}continue browsing alone{config.TAG_NEXT_DESIRE_CLOSE}",
            f"{config.TAG_NEXT_INTENTION_OPEN}stay with the display{config.TAG_NEXT_INTENTION_CLOSE}",
            f"{config.TAG_RISK_OPEN}low{config.TAG_RISK_CLOSE}",
            f"{config.TAG_BENEFIT_OPEN}low{config.TAG_BENEFIT_CLOSE}",
            f"{config.TAG_REWARD_OPEN}0.30{config.TAG_REWARD_CLOSE}",
        ]
    )
    outputs["continuation:Hold_eda24b4bb712"] = (
        f"{config.TAG_REACTION_CAPTION_OPEN}the customer keeps browsing silently"
        f"{config.TAG_REACTION_CAPTION_CLOSE}"
    )
    outputs["deliberation:Inform_5ac252a82695"] = "\n".join(
        [
            f"{config.TAG_NEXT_STAGE_OPEN}desire{config.TAG_NEXT_STAGE_CLOSE}",
            f"{config.TAG_NEXT_BELIEF_OPEN}brief comparison is available{config.TAG_NEXT_BELIEF_CLOSE}",
            f"{config.TAG_NEXT_DESIRE_OPEN}compare options{config.TAG_NEXT_DESIRE_CLOSE}",
            f"{config.TAG_NEXT_INTENTION_OPEN}review the comparison{config.TAG_NEXT_INTENTION_CLOSE}",
            f"{config.TAG_RISK_OPEN}low{config.TAG_RISK_CLOSE}",
            f"{config.TAG_BENEFIT_OPEN}medium{config.TAG_BENEFIT_CLOSE}",
            f"{config.TAG_REWARD_OPEN}0.10{config.TAG_REWARD_CLOSE}",
        ]
    )
    outputs["continuation:Inform_5ac252a82695"] = (
        f"{config.TAG_REACTION_CAPTION_OPEN}the customer reads the comparison"
        f"{config.TAG_REACTION_CAPTION_CLOSE}"
    )
    outputs["action"] = "\n".join(
        [
            f"{config.TAG_RATIONALE_OPEN}hold seems safest{config.TAG_RATIONALE_CLOSE}",
            f"{config.TAG_CHOSEN_OPEN}Hold_eda24b4bb712{config.TAG_CHOSEN_CLOSE}",
            f"{config.TAG_INTERVENTION_ACTION_OPEN}stay silent{config.TAG_INTERVENTION_ACTION_CLOSE}",
            f"{config.TAG_INTERVENTION_UTTERANCE_OPEN}（静默）{config.TAG_INTERVENTION_UTTERANCE_CLOSE}",
        ]
    )

    decision = PIWMDecisionLoop(
        MockVLM(outputs),
        five_act_only=True,
        hold_prior_lambda=1.0,
        hold_prior_target=0.2,
        hold_prior_observed=16 / 30,
    ).decide(_state_row())

    assert decision.chosen_action == "Inform_5ac252a82695"
    assert "Hold was demoted by inference-time prior calibration" in decision.rationale


def test_decision_loop_low_score_returns_silent_candidate_without_deliberation() -> None:
    outputs = default_outputs()
    outputs["perception"] = outputs["perception"].replace(
        f"{config.TAG_SCORE_OPEN}3{config.TAG_SCORE_CLOSE}",
        f"{config.TAG_SCORE_OPEN}1{config.TAG_SCORE_CLOSE}",
    )
    vlm = MockVLM(outputs)
    decision = PIWMDecisionLoop(vlm).decide(_state_row())
    assert decision.used_fallback is True
    assert decision.chosen_action == "A1_silent_observe"
    assert [call["role"] for call in vlm.calls] == ["perception"]


def test_decision_loop_raises_no_exceptions_on_fixture_batch() -> None:
    rows = []
    with (ROOT / "data/piwm_dataset_pilot30/state_inference.jsonl").open(encoding="utf-8") as handle:
        for _, line in zip(range(3), handle):
            rows.append(json.loads(line))
    loop = PIWMDecisionLoop(MockVLM())
    assert [loop.decide(row).chosen_action for row in rows] == ["A2_offer_value_comparison"] * 3
