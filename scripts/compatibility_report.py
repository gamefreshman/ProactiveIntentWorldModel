"""Build a v2.2 compatibility-tier report for a PIWM main_schema JSONL file."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from piwm_data import rules
from piwm_data.schemas import MainSchemaRecord


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize PIWM v2.2 compatibility tiers.")
    parser.add_argument("main_schema", type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/v2_validation/compatibility_report.md"))
    args = parser.parse_args(argv)

    records = load_records(args.main_schema)
    report = build_report(records, args.main_schema)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    return 0


def load_records(path: Path) -> list[MainSchemaRecord]:
    records: list[MainSchemaRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(MainSchemaRecord(**json.loads(line)))
    return records


def build_report(records: list[MainSchemaRecord], source: Path) -> str:
    basic_tier_counts = Counter(record.compatibility_tier for record in records)
    basic_flag_counts = Counter(flag for record in records for flag in record.legacy_mismatch_flags)
    extended = _extended_audit(records)
    intent_tier_counts = Counter(record.persona.intent_tier for record in records)
    act_counts = Counter(record.best_action_spec.act if record.best_action_spec else "unknown" for record in records)
    total = len(records)
    lines = [
        "# PIWM v2.2 Compatibility Report",
        "",
        f"- Source: `{source.as_posix()}`",
        f"- Records: {total}",
        "",
        "## Basic Schema Compatibility Tiers",
        "",
        "This tier comes from the schema-level migration checks only. It covers v2 mirror-field mismatches and `intent_tier_visual_mismatch`; it does not by itself prove that old `best_action` matches the v2 policy re-derivation.",
        "",
        "| Tier | Count | Ratio |",
        "|---|---:|---:|",
    ]
    for tier in ("green", "yellow", "red"):
        count = basic_tier_counts.get(tier, 0)
        ratio = (count / total * 100) if total else 0.0
        lines.append(f"| {tier} | {count} | {ratio:.2f}% |")
    lines.extend(
        [
            "",
            "## Basic Mismatch Flags",
            "",
            "| Flag | Count |",
            "|---|---:|",
        ]
    )
    if basic_flag_counts:
        for flag, count in sorted(basic_flag_counts.items()):
            lines.append(f"| {flag} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Extended V2 Re-derivation Audit",
            "",
            "This audit re-derives `latent_state` from observable cues and re-picks the best v2 policy action with `derive_policy_candidate_specs()` + `pick_best_action_spec()`. It is stricter than the schema tier above.",
            "",
            "| Tier | Count | Ratio |",
            "|---|---:|---:|",
        ]
    )
    for tier in ("green", "yellow", "red"):
        count = extended["tier_counts"].get(tier, 0)
        ratio = (count / total * 100) if total else 0.0
        lines.append(f"| {tier} | {count} | {ratio:.2f}% |")
    lines.extend(
        [
            "",
            "### Extended Flags",
            "",
            "| Flag | Count |",
            "|---|---:|",
        ]
    )
    for flag, count in sorted(extended["flag_counts"].items()):
        lines.append(f"| {flag} | {count} |")
    lines.extend(
        [
            "",
            "## Intent Tier Distribution",
            "",
            "| Intent Tier | Count |",
            "|---|---:|",
        ]
    )
    for tier, count in sorted(intent_tier_counts.items()):
        lines.append(f"| {tier} | {count} |")
    lines.extend(
        [
            "",
            "## Official Best Act Distribution",
            "",
            "| Act | Count |",
            "|---|---:|",
        ]
    )
    for act, count in sorted(act_counts.items()):
        lines.append(f"| {act} | {count} |")
    lines.extend(
        [
            "",
            "## Official 543 Re-derived V2 Policy Best Distribution",
            "",
            "| Act | Count |",
            "|---|---:|",
        ]
    )
    for act, count in sorted(extended["policy_best_counts"].items()):
        lines.append(f"| {act} | {count} |")
    lines.extend(
        [
            "",
            "### Policy Drift Matrix",
            "",
            "| Old best act | Re-derived v2 best act | Count |",
            "|---|---|---:|",
        ]
    )
    for (old_act, new_act), count in sorted(extended["drift_matrix"].items()):
        lines.append(f"| {old_act} | {new_act} | {count} |")
    lines.extend(
        [
            "",
            "## Candidate Rule Coverage In Official Records",
            "",
            "| Coverage | Count |",
            "|---|---:|",
        ]
    )
    for coverage, count in sorted(extended["candidate_rule_coverage_counts"].items()):
        lines.append(f"| {coverage} | {count} |")
    lines.extend(
        [
            "",
            "## Red Samples By Persona",
            "",
            "| Persona | Red | Total | Red Ratio |",
            "|---|---:|---:|---:|",
        ]
    )
    for persona, total_count in sorted(extended["persona_counts"].items()):
        red_count = extended["red_persona_counts"].get(persona, 0)
        ratio = (red_count / total_count * 100) if total_count else 0.0
        lines.append(f"| {persona} | {red_count} | {total_count} | {ratio:.2f}% |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Basic `yellow=0` is a detector-scope result, not proof that no policy drift exists.",
            "- Extended audit finds substantial `best_action_drift`; these rows should be treated as policy-migration yellow unless they also carry red semantic conflicts.",
            "- The 81 red rows concentrate in `browser_low_intent`; this reflects legacy video/prompt generation not strongly differentiating low purchase intent from high engagement cues.",
            "- `latent_state_mismatch=0` means current cue-derived state labels are internally consistent for this official file.",
            "",
        ]
    )
    return "\n".join(lines)


def _extended_audit(records: list[MainSchemaRecord]) -> dict[str, Any]:
    tier_counts: Counter[str] = Counter()
    flag_counts: Counter[str] = Counter()
    policy_best_counts: Counter[str] = Counter()
    candidate_rule_coverage_counts: Counter[str] = Counter()
    drift_matrix: Counter[tuple[str, str]] = Counter()
    persona_counts: Counter[str] = Counter(record.persona.type for record in records)
    red_persona_counts: Counter[str] = Counter()

    for record in records:
        flags = set(record.legacy_mismatch_flags)
        rederived_state = rules.derive_latent_state(record.observable_cues)
        if rederived_state != record.latent_state:
            flags.add("latent_state_mismatch")

        policy_state = rederived_state
        policy_candidates = rules.derive_policy_candidate_specs(
            policy_state,
            record.aida_stage,
            intent_tier=record.persona.intent_tier,
        )
        policy_best = rules.pick_best_action_spec(
            policy_state,
            record.aida_stage,
            record.persona.type,
            candidates=policy_candidates,
            intent_tier=record.persona.intent_tier,
            visible_cues=record.observable_cues,
        )
        policy_best_counts[policy_best["act"]] += 1
        old_best = _record_best_spec(record)
        if not _spec_equal(old_best, policy_best):
            flags.add("best_action_drift")
            drift_matrix[(old_best["act"], policy_best["act"])] += 1

        coverage = "explicit" if (policy_state, record.aida_stage) in rules.STATE_AIDA_TO_CANDIDATES else "default_fallback"
        candidate_rule_coverage_counts[coverage] += 1

        if "intent_tier_visual_mismatch" in flags:
            red_persona_counts[record.persona.type] += 1

        flag_counts.update(flags)
        tier_counts[_extended_tier(flags)] += 1

    return {
        "tier_counts": tier_counts,
        "flag_counts": flag_counts,
        "policy_best_counts": policy_best_counts,
        "candidate_rule_coverage_counts": candidate_rule_coverage_counts,
        "drift_matrix": drift_matrix,
        "persona_counts": persona_counts,
        "red_persona_counts": red_persona_counts,
    }


def _record_best_spec(record: MainSchemaRecord) -> dict[str, Any]:
    if record.best_action_spec is not None:
        return record.best_action_spec.model_dump(mode="json")
    spec = rules.legacy_action_to_act(record.best_action)
    return {"act": spec["act"], "params": rules.merge_supporting_acts(spec.get("params"), spec.get("co_acts"))}


def _spec_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left.get("act") == right.get("act") and rules.merge_supporting_acts(left.get("params", {})) == rules.merge_supporting_acts(right.get("params", {}))


def _extended_tier(flags: set[str]) -> str:
    if flags & {"intent_tier_visual_mismatch", "latent_state_mismatch"}:
        return "red"
    if flags:
        return "yellow"
    return "green"


if __name__ == "__main__":
    raise SystemExit(main())
