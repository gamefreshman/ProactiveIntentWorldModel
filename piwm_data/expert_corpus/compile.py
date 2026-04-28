"""Compile ``distilled/conditional_rules.jsonl`` into runtime lookup tables.

The compiled output is the canonical source for the six runtime mappings used
in :mod:`piwm_data.rules`. The compiler also emits a conflict log if any
``(rule_type, key)`` combination is mapped to more than one ``value``.

This module is intentionally read-only with respect to ``rules.py``: the
literal tables there remain the runtime fast-path. A unit test asserts that
the compiled tables are byte-for-byte equivalent to the literal tables, so any
divergence fails fast.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter, ValidationError

from .schemas import RuleEntry, cross_check_enums, CorpusValidationError

DEFAULT_JSONL = Path(__file__).parent / "distilled" / "conditional_rules.jsonl"
DEFAULT_CONFLICT_LOG = Path(__file__).parent / "distilled" / "_conflict_log.jsonl"

_RULE_ADAPTER: TypeAdapter[RuleEntry] = TypeAdapter(RuleEntry)


@dataclass
class CompiledCorpus:
    """Result of compiling ``conditional_rules.jsonl``.

    The six attribute dicts mirror the runtime tables in ``piwm_data/rules.py``.
    ``provenance`` allows tracing every compiled cell back to a rule_id.
    ``conflicts`` is non-empty only when more than one rule maps to the same
    typed key with different values; in that case compilation fails.
    """

    cue_to_state_prior: dict[str, str] = field(default_factory=dict)
    persona_state_to_intent: dict[tuple[str, str], str] = field(default_factory=dict)
    state_fallback_intent: dict[str, str] = field(default_factory=dict)
    state_to_proactive_score: dict[str, int] = field(default_factory=dict)
    state_aida_to_candidates: dict[tuple[str, str], list[str]] = field(default_factory=dict)
    transition_table: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)

    rule_provenance: dict[str, dict[str, Any]] = field(default_factory=dict)
    conflicts: list[dict[str, Any]] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        return {
            "cue_to_state_prior": len(self.cue_to_state_prior),
            "persona_state_to_intent": len(self.persona_state_to_intent),
            "state_fallback_intent": len(self.state_fallback_intent),
            "state_to_proactive_score": len(self.state_to_proactive_score),
            "state_aida_to_candidates": len(self.state_aida_to_candidates),
            "transition_table": len(self.transition_table),
        }


def _load_entries(path: Path) -> list[RuleEntry]:
    if not path.exists():
        raise FileNotFoundError(f"conditional_rules.jsonl not found: {path}")
    entries: list[RuleEntry] = []
    seen_ids: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CorpusValidationError(f"line {line_no}: invalid JSON: {exc}") from exc
            try:
                entry = _RULE_ADAPTER.validate_python(raw)
            except ValidationError as exc:
                raise CorpusValidationError(f"line {line_no}: schema error: {exc}") from exc
            if entry.rule_id in seen_ids:
                raise CorpusValidationError(f"line {line_no}: duplicate rule_id {entry.rule_id}")
            seen_ids.add(entry.rule_id)
            err = cross_check_enums(entry)
            if err is not None:
                raise CorpusValidationError(f"line {line_no} ({entry.rule_id}): {err}")
            entries.append(entry)
    return entries


def compile_corpus(
    jsonl_path: Path | None = None,
    write_conflict_log: bool = True,
) -> CompiledCorpus:
    """Parse the JSONL corpus and produce runtime tables plus provenance index.

    Raises :class:`CorpusValidationError` on schema, enum, or conflict errors.
    """

    path = jsonl_path or DEFAULT_JSONL
    entries = _load_entries(path)
    out = CompiledCorpus()

    # Track (rule_type, normalized_key) -> first rule_id
    seen_keys: dict[tuple[str, tuple[str, ...]], str] = {}

    for entry in entries:
        out.rule_provenance[entry.rule_id] = {
            "rule_type": entry.rule_type,
            "version": entry.version,
            "provenance": entry.provenance.model_dump(),
        }

        norm_key = entry.key.normalize()
        seen_id = (entry.rule_type, norm_key)

        if seen_id in seen_keys:
            out.conflicts.append(
                {
                    "rule_type": entry.rule_type,
                    "key": entry.key.model_dump(),
                    "first_rule_id": seen_keys[seen_id],
                    "conflicting_rule_id": entry.rule_id,
                }
            )
            continue
        seen_keys[seen_id] = entry.rule_id

        if entry.rule_type == "cue_to_state_prior":
            out.cue_to_state_prior[entry.key.cue] = entry.value.state
        elif entry.rule_type == "persona_state_to_intent":
            out.persona_state_to_intent[(entry.key.persona, entry.key.state)] = entry.value.intent
        elif entry.rule_type == "state_fallback_intent":
            out.state_fallback_intent[entry.key.state] = entry.value.intent
        elif entry.rule_type == "state_to_proactive_score":
            out.state_to_proactive_score[entry.key.state] = entry.value.score
        elif entry.rule_type == "state_aida_to_candidates":
            out.state_aida_to_candidates[(entry.key.state, entry.key.aida_stage)] = list(
                entry.value.candidate_actions
            )
        elif entry.rule_type == "transition":
            out.transition_table[(entry.key.state, entry.key.action)] = {
                "next_state": entry.value.next_state,
                "reward": entry.value.reward,
                "risk": entry.value.risk,
                "benefit": entry.value.benefit,
            }

    if write_conflict_log:
        DEFAULT_CONFLICT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DEFAULT_CONFLICT_LOG.open("w", encoding="utf-8") as f:
            for entry in out.conflicts:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if out.conflicts:
        raise CorpusValidationError(
            f"{len(out.conflicts)} rule conflict(s) detected; see {DEFAULT_CONFLICT_LOG}"
        )

    return out


def main() -> None:
    """CLI for ad-hoc inspection: compile and print counts."""

    out = compile_corpus()
    counts = out.counts()
    print(json.dumps({"counts": counts, "rule_count": len(out.rule_provenance)}, indent=2))


if __name__ == "__main__":
    main()
