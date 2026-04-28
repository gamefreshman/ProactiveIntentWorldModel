"""One-shot seed JSONL generator.

This script reads the runtime tables in ``piwm_data/rules.py`` and emits a
``distilled/conditional_rules.jsonl`` file in which each entry carries explicit
provenance. The intent is to convert the existing hardcoded tables into a
traceable expert corpus *without changing their values*.

Run once:

    python3 -m piwm_data.expert_corpus._seed_generator

Subsequent edits should be made directly to the JSONL file. Re-running this
generator overwrites the JSONL, so do not rely on it after the first commit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .. import rules

ADDED_AT = "2026-04-29"
AUTHOR = "piwm-bootstrap"
SOURCE_REF = "data_pipeline_spec.md v1 + piwm_data/rules.py v1.0"

# Short, honest rationales. They are NOT pedagogy citations; they explain the
# inferential link the rule encodes so a future reviewer can audit it.
_CUE_RATIONALES: dict[str, str] = {
    "long_dwell_with_price_check": "Repeated price checking with long dwell typically indicates price-driven hesitation rather than feature evaluation.",
    "repeated_product_handling": "Hands-on repetition signals the customer is actively evaluating the product.",
    "comparing_two_products": "Side-by-side comparison is a defining behavior of active evaluation.",
    "looking_around_for_help": "Searching for staff suggests the customer is approaching a decision and needs assistance.",
    "checking_phone_likely_research": "Phone usage during shopping is most often product or price research, an active evaluation behavior.",
    "brief_glance_walking_past": "A short glance without engagement is consistent with early browsing.",
    "trying_on_or_testing": "Trying or testing is a hands-on evaluation behavior.",
    "asking_companion_opinion": "Soliciting a companion's opinion happens during active evaluation, not at decision close.",
    "no_eye_contact_avoidant": "Avoidant body language indicates disengagement.",
    "approaching_counter": "Walking up to the counter indicates the customer is ready to act.",
}

_PERSONA_STATE_RATIONALES: dict[tuple[str, str], str] = {
    ("price_sensitive_cautious", "high_hesitation"): "A cautious shopper who hesitates is mostly weighing price against value.",
    ("price_sensitive_cautious", "active_evaluation"): "Active evaluation for a price-sensitive shopper typically targets a price negotiation.",
    ("price_sensitive_cautious", "ready_to_decide"): "When ready to decide, the cautious shopper still wants reassurance the choice is sound.",
    ("first_time_high_consideration", "high_hesitation"): "First-time high-consideration buyers seek reassurance to overcome uncertainty.",
    ("first_time_high_consideration", "active_evaluation"): "Active evaluation by a novice buyer often turns into a request for demonstration.",
    ("first_time_high_consideration", "ready_to_decide"): "Once ready, the novice buyer wants to confirm the choice is correct.",
    ("experienced_brand_loyal", "active_evaluation"): "Brand-loyal experienced buyers evaluate to confirm rather than to switch.",
    ("experienced_brand_loyal", "ready_to_decide"): "Brand-loyal buyers in decision mode are confirming the chosen item.",
    ("browser_low_intent", "early_browsing"): "Low-intent browsers are exploring options without committing.",
    ("browser_low_intent", "disengaged"): "Disengaged browsing usually ends with leaving without purchase.",
    ("gift_buyer_uncertain", "high_hesitation"): "Gift buyers under hesitation seek reassurance the recipient will be pleased.",
    ("gift_buyer_uncertain", "active_evaluation"): "Gift buyers in active mode commonly request demonstrations to compare options.",
    ("price_insensitive_decisive", "active_evaluation"): "Decisive shoppers evaluate quickly to confirm rather than to delay.",
    ("price_insensitive_decisive", "ready_to_decide"): "Decisive shoppers in decision mode are confirming, not negotiating.",
}

_FALLBACK_INTENT_RATIONALES: dict[str, str] = {
    "high_hesitation": "Default intent for hesitation is reassurance-seeking when persona context is missing.",
    "active_evaluation": "Default intent for active evaluation is option exploration when persona context is missing.",
    "ready_to_decide": "Default intent at decision time is confirmation when persona context is missing.",
    "early_browsing": "Default intent for early browsing is exploration.",
    "disengaged": "Default intent for disengaged customers is to leave without purchase.",
    "defensive_withdrawal": "Defensive withdrawal usually leads to leaving without purchase.",
    "engaged_dialogue": "Engaged dialogue still aligns with exploration when no other signal is given.",
    "continued_hesitation": "Continued hesitation defaults to seeking reassurance.",
    "post_decision_reassurance": "After deciding, the dominant intent is to confirm the choice.",
}

_PROACTIVE_SCORE_RATIONALES: dict[str, str] = {
    "high_hesitation": "Hesitation is a high-leverage moment for proactive intervention but not the highest.",
    "active_evaluation": "Active evaluation tolerates light proactive support.",
    "ready_to_decide": "Decision moment is the highest-leverage point for a well-timed prompt.",
    "early_browsing": "Early browsing rewards minimal proactive intervention.",
    "post_decision_reassurance": "Post-decision reassurance benefits from proactive confirmation.",
    "disengaged": "Disengaged customers should not be pushed; proactive score is minimal.",
    "defensive_withdrawal": "Defensive withdrawal explicitly punishes further intervention.",
    "engaged_dialogue": "An engaged dialogue is already proceeding; proactive score is moderate.",
    "continued_hesitation": "Sustained hesitation rewards continued, gentle proactive support.",
}

_CANDIDATES_RATIONALES: dict[tuple[str, str], str] = {
    ("high_hesitation", "interest"): "Under hesitation in interest, observe-or-offer-value-or-question covers the safe range.",
    ("high_hesitation", "desire"): "Under hesitation in desire, value-comparison or open-question with backstop wait covers conversion-safe options.",
    ("active_evaluation", "interest"): "Active interest pairs well with open question, demonstration, or quiet observation.",
    ("active_evaluation", "desire"): "Active desire benefits from value comparison plus demonstration, falling back to a question.",
    ("ready_to_decide", "desire"): "Ready desire favors value reinforcement, a clarifying question, or a recommendation in that order.",
    ("ready_to_decide", "action"): "At action time, recommendation or a confirming question are the dominant choices.",
    ("early_browsing", "attention"): "Early browsing is best handled with silence or a polite acknowledgement.",
    ("disengaged", "attention"): "Disengaged customers warrant disengage or, at most, silent observation.",
    ("defensive_withdrawal", "interest"): "Defensive withdrawal is best handled with disengage or polite acknowledgement to avoid pressure.",
}

_TRANSITION_RATIONALES: dict[tuple[str, str], str] = {
    ("high_hesitation", "A1_silent_observe"): "Silence preserves hesitation but does not advance it.",
    ("high_hesitation", "A2_offer_value_comparison"): "Value comparison directly addresses price-driven hesitation and tends to start dialogue.",
    ("high_hesitation", "A3_strong_recommend"): "A strong push during hesitation triggers defensive withdrawal.",
    ("high_hesitation", "A4_open_with_question"): "An open question lowers pressure and tends to start dialogue.",
    ("high_hesitation", "A6_acknowledge_and_wait"): "Acknowledgement preserves rapport without advancing hesitation.",
    ("active_evaluation", "A1_silent_observe"): "Silence preserves active evaluation but yields no information.",
    ("active_evaluation", "A2_offer_value_comparison"): "Value comparison during evaluation typically converts to dialogue.",
    ("active_evaluation", "A4_open_with_question"): "Questions during evaluation invite dialogue.",
    ("active_evaluation", "A5_provide_demonstration"): "Demonstration converts evaluation to dialogue with high payoff.",
    ("active_evaluation", "A3_strong_recommend"): "A premature push during evaluation pushes the customer to defensive withdrawal.",
    ("ready_to_decide", "A2_offer_value_comparison"): "Value reinforcement at decision time aids commitment.",
    ("ready_to_decide", "A3_strong_recommend"): "Recommendation at decision time is high-payoff but mid-risk.",
    ("ready_to_decide", "A4_open_with_question"): "A clarifying question at decision time is the lowest-risk way to confirm.",
    ("ready_to_decide", "A1_silent_observe"): "Silence at decision time risks losing the customer to disengagement.",
    ("early_browsing", "A1_silent_observe"): "Silence supports early browsing without disturbance.",
    ("early_browsing", "A6_acknowledge_and_wait"): "Acknowledgement supports early browsing without pressure.",
    ("early_browsing", "A3_strong_recommend"): "Strong push during early browsing causes disengagement.",
    ("disengaged", "A7_disengage"): "Disengaging stays in disengagement but preserves rapport for later.",
    ("disengaged", "A1_silent_observe"): "Silent observation also stays in disengagement.",
    ("defensive_withdrawal", "A7_disengage"): "Disengaging is the recovery path from defensive withdrawal.",
    ("defensive_withdrawal", "A6_acknowledge_and_wait"): "Acknowledgement can de-escalate defensive withdrawal back to hesitation.",
}


def _provenance(rationale: str) -> dict[str, str]:
    return {
        "source_kind": "seed_rule",
        "source_ref": SOURCE_REF,
        "rationale": rationale,
        "author": AUTHOR,
        "added_at": ADDED_AT,
    }


def build_entries() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    for i, (cue, state) in enumerate(rules.CUE_TO_STATE_PRIOR.items(), start=1):
        out.append(
            {
                "rule_id": f"CUE2STATE_{i:03d}",
                "rule_type": "cue_to_state_prior",
                "version": "v1.0",
                "key": {"cue": cue},
                "value": {"state": state},
                "provenance": _provenance(_CUE_RATIONALES[cue]),
            }
        )

    for i, ((persona, state), intent) in enumerate(rules.PERSONA_STATE_TO_INTENT.items(), start=1):
        out.append(
            {
                "rule_id": f"PSI_{i:03d}",
                "rule_type": "persona_state_to_intent",
                "version": "v1.0",
                "key": {"persona": persona, "state": state},
                "value": {"intent": intent},
                "provenance": _provenance(_PERSONA_STATE_RATIONALES[(persona, state)]),
            }
        )

    for i, (state, intent) in enumerate(rules.STATE_FALLBACK_INTENT.items(), start=1):
        out.append(
            {
                "rule_id": f"FALLBACK_{i:03d}",
                "rule_type": "state_fallback_intent",
                "version": "v1.0",
                "key": {"state": state},
                "value": {"intent": intent},
                "provenance": _provenance(_FALLBACK_INTENT_RATIONALES[state]),
            }
        )

    for i, (state, score) in enumerate(rules.STATE_TO_PROACTIVE_SCORE.items(), start=1):
        out.append(
            {
                "rule_id": f"PROSCORE_{i:03d}",
                "rule_type": "state_to_proactive_score",
                "version": "v1.0",
                "key": {"state": state},
                "value": {"score": score},
                "provenance": _provenance(_PROACTIVE_SCORE_RATIONALES[state]),
            }
        )

    for i, ((state, aida), candidates) in enumerate(rules.STATE_AIDA_TO_CANDIDATES.items(), start=1):
        out.append(
            {
                "rule_id": f"CAND_{i:03d}",
                "rule_type": "state_aida_to_candidates",
                "version": "v1.0",
                "key": {"state": state, "aida_stage": aida},
                "value": {"candidate_actions": list(candidates)},
                "provenance": _provenance(_CANDIDATES_RATIONALES[(state, aida)]),
            }
        )

    for i, ((state, action), transition) in enumerate(rules.TRANSITION_TABLE.items(), start=1):
        out.append(
            {
                "rule_id": f"TRANS_{i:03d}",
                "rule_type": "transition",
                "version": "v1.0",
                "key": {"state": state, "action": action},
                "value": {
                    "next_state": transition["next_state"],
                    "reward": transition["reward"],
                    "risk": transition["risk"],
                    "benefit": transition["benefit"],
                },
                "provenance": _provenance(_TRANSITION_RATIONALES[(state, action)]),
            }
        )

    return out


def main() -> None:
    target = Path(__file__).parent / "distilled" / "conditional_rules.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    entries = build_entries()
    with target.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"wrote {len(entries)} rule entries to {target}")


if __name__ == "__main__":
    main()
