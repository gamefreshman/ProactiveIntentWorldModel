"""Tests for the PIWM expert corpus layer.

The contract:

1. ``conditional_rules.jsonl`` parses without error.
2. The compiled tables exactly match the literal tables in :mod:`piwm_data.rules`.
3. Counts match the documented baseline plus v2.2 intent-tier rules.
4. Every rule entry carries an explicit, non-empty rationale.
5. The first batch is honestly tagged ``seed_rule``, never as pedagogy text.
6. No conflicts: each (rule_type, key) maps to exactly one value.
7. The compiler refuses unknown enums and reports duplicate rule_ids.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from piwm_data import rules as runtime_rules
from piwm_data.expert_corpus.compile import (
    DEFAULT_JSONL,
    compile_corpus,
)
from piwm_data.expert_corpus.schemas import CorpusValidationError


# ---------------------------------------------------------------------------
# 1. JSONL is well-formed and complete


def test_jsonl_exists_and_has_78_entries() -> None:
    assert DEFAULT_JSONL.exists(), f"{DEFAULT_JSONL} missing"
    lines = [
        line for line in DEFAULT_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(lines) == 78


def test_jsonl_compiles_without_error() -> None:
    out = compile_corpus()
    assert out.conflicts == []
    assert out.counts() == {
        "cue_to_state_prior": 10,
        "persona_to_intent_tier": 6,
        "persona_state_to_intent": 14,
        "state_fallback_intent": 9,
        "state_to_proactive_score": 9,
        "state_aida_to_candidates": 9,
        "transition_table": 21,
    }


# ---------------------------------------------------------------------------
# 2. Compiled tables == literal tables in rules.py (the central guarantee)


def test_cue_to_state_matches_literal() -> None:
    out = compile_corpus()
    assert out.cue_to_state_prior == runtime_rules.CUE_TO_STATE_PRIOR


def test_persona_state_to_intent_matches_literal() -> None:
    out = compile_corpus()
    assert out.persona_state_to_intent == runtime_rules.PERSONA_STATE_TO_INTENT


def test_persona_to_intent_tier_matches_v2_2_contract() -> None:
    out = compile_corpus()
    assert out.persona_to_intent_tier == {
        "price_sensitive_cautious": "exploring",
        "first_time_high_consideration": "exploring",
        "experienced_brand_loyal": "ready_to_buy",
        "browser_low_intent": "low_intent_browsing",
        "gift_buyer_uncertain": "exploring",
        "price_insensitive_decisive": "ready_to_buy",
    }


def test_state_fallback_intent_matches_literal() -> None:
    out = compile_corpus()
    assert out.state_fallback_intent == runtime_rules.STATE_FALLBACK_INTENT


def test_state_to_proactive_score_matches_literal() -> None:
    out = compile_corpus()
    assert out.state_to_proactive_score == runtime_rules.STATE_TO_PROACTIVE_SCORE


def test_state_aida_to_candidates_matches_literal() -> None:
    out = compile_corpus()
    assert out.state_aida_to_candidates == runtime_rules.STATE_AIDA_TO_CANDIDATES


def test_transition_table_matches_literal() -> None:
    out = compile_corpus()
    # Compare key by key so a mismatch tells us which (state, action) drifted.
    assert set(out.transition_table.keys()) == set(runtime_rules.TRANSITION_TABLE.keys())
    for key, expected in runtime_rules.TRANSITION_TABLE.items():
        actual = out.transition_table[key]
        for field_name in ("next_state", "reward", "risk", "benefit"):
            assert actual[field_name] == expected[field_name], (
                f"transition[{key}].{field_name}: jsonl={actual[field_name]} literal={expected[field_name]}"
            )


def test_transition_failure_modes_compile() -> None:
    out = compile_corpus()
    failure_modes = [
        value["failure_mode"]
        for value in out.transition_table.values()
        if value.get("failure_mode") is not None
    ]
    null_failure_modes = [
        value for value in out.transition_table.values() if value.get("failure_mode") is None
    ]

    assert len(out.transition_table) == 21
    assert len(failure_modes) == 17
    assert len(null_failure_modes) == 4
    assert all(value.get("failure_mode_rationale") for value in null_failure_modes)
    assert any(
        any("pressure" in condition for condition in fm["trigger_conditions"])
        for fm in failure_modes
    )
    assert all(fm["principle_refs"] for fm in failure_modes)


# ---------------------------------------------------------------------------
# 3. Provenance is honest and complete


def test_every_rule_has_provenance() -> None:
    out = compile_corpus()
    assert len(out.rule_provenance) == 78
    for rule_id, info in out.rule_provenance.items():
        prov = info["provenance"]
        assert prov["rationale"], f"{rule_id}: empty rationale"
        assert prov["author"], f"{rule_id}: empty author"
        assert prov["added_at"], f"{rule_id}: empty added_at"
        assert prov["source_kind"] in {
            "seed_rule",
            "manual_distillation",
            "pedagogy_text",
            "expert_review",
        }


def test_first_batch_is_honestly_seed() -> None:
    """The first 72 rules are project-authored seeds. They MUST NOT claim to be
    distilled from real pedagogy text. This is the core honesty guarantee that
    keeps the v6 paper claim ``pedagogy-derived`` from becoming a lie."""

    out = compile_corpus()
    for rule_id, info in out.rule_provenance.items():
        kind = info["provenance"]["source_kind"]
        if rule_id.startswith("PIT_"):
            assert kind == "manual_distillation", f"{rule_id}: expected v2.2 distillation"
        else:
            assert kind == "seed_rule", (
                f"{rule_id}: first-batch rule must be tagged seed_rule, got {kind}"
            )


# ---------------------------------------------------------------------------
# 4. Compiler rejects malformed corpus


def test_compiler_rejects_unknown_enum(tmp_path: Path) -> None:
    bad = {
        "rule_id": "BAD_001",
        "rule_type": "cue_to_state_prior",
        "version": "v1.0",
        "key": {"cue": "not_a_real_cue"},
        "value": {"state": "high_hesitation"},
        "provenance": {
            "source_kind": "seed_rule",
            "source_ref": "test",
            "rationale": "test",
            "author": "test",
            "added_at": "2026-04-29",
        },
    }
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps(bad) + "\n", encoding="utf-8")
    with pytest.raises(CorpusValidationError, match="unknown cue"):
        compile_corpus(jsonl_path=p, write_conflict_log=False)


def test_compiler_rejects_duplicate_rule_id(tmp_path: Path) -> None:
    entry = {
        "rule_id": "DUP_001",
        "rule_type": "state_fallback_intent",
        "version": "v1.0",
        "key": {"state": "high_hesitation"},
        "value": {"intent": "seek_reassurance"},
        "provenance": {
            "source_kind": "seed_rule",
            "source_ref": "test",
            "rationale": "test",
            "author": "test",
            "added_at": "2026-04-29",
        },
    }
    p = tmp_path / "dup.jsonl"
    line = json.dumps(entry) + "\n"
    p.write_text(line + line, encoding="utf-8")
    with pytest.raises(CorpusValidationError, match="duplicate rule_id"):
        compile_corpus(jsonl_path=p, write_conflict_log=False)


def test_compiler_detects_value_conflict(tmp_path: Path) -> None:
    # Same (rule_type, key) but different values -> conflict.
    entry_a = {
        "rule_id": "CONFLICT_A",
        "rule_type": "state_fallback_intent",
        "version": "v1.0",
        "key": {"state": "high_hesitation"},
        "value": {"intent": "seek_reassurance"},
        "provenance": {
            "source_kind": "seed_rule",
            "source_ref": "test",
            "rationale": "test",
            "author": "test",
            "added_at": "2026-04-29",
        },
    }
    entry_b = dict(entry_a)
    entry_b["rule_id"] = "CONFLICT_B"
    entry_b["value"] = {"intent": "explore_options"}
    p = tmp_path / "conflict.jsonl"
    p.write_text(
        json.dumps(entry_a) + "\n" + json.dumps(entry_b) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(CorpusValidationError, match="conflict"):
        compile_corpus(jsonl_path=p, write_conflict_log=False)
