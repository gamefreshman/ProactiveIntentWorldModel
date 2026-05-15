"""Audit PIWM action-space distributions for a main_schema JSONL file."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from piwm_data import rules


DEFAULT_MAIN_SCHEMA = Path("data/official/piwm_train_synth_v1/main_schema.jsonl")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit PIWM action and DialogueAct distribution.")
    parser.add_argument("--main-schema", type=Path, default=DEFAULT_MAIN_SCHEMA)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = audit_main_schema(args.main_schema)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


def audit_main_schema(path: Path) -> dict[str, Any]:
    records = _read_jsonl(path)
    legacy_best = Counter()
    dialogue_acts = Counter()
    candidate_acts = Counter()
    candidate_dialogue_acts = Counter()
    supporting_acts = Counter()
    missing_v2_fields = Counter()

    for row in records:
        legacy_best[row.get("best_action", "<missing>")] += 1
        dialogue_acts[row.get("dialogue_act", "<missing>")] += 1
        for action in row.get("candidate_actions", []):
            candidate_acts[action] += 1
            try:
                spec = rules.legacy_action_to_act(action)
                candidate_dialogue_acts[spec["act"]] += 1
            except ValueError:
                candidate_dialogue_acts["<invalid>"] += 1
        params = rules.merge_supporting_acts(row.get("act_params", {}), row.get("co_acts", row.get("legacy_co_acts", [])))
        for support in rules.supporting_acts_from_params(params):
            supporting_acts[support["type"]] += 1
        for field in ("dialogue_act", "act_params", "realization"):
            if field not in row:
                missing_v2_fields[field] += 1

    return {
        "artifact": "piwm_action_space_audit",
        "schema_policy": rules.ACTION_SCHEMA_VERSION,
        "main_schema": path.as_posix(),
        "n_records": len(records),
        "best_action_counts": dict(sorted(legacy_best.items())),
        "dialogue_act_counts": dict(sorted(dialogue_acts.items())),
        "candidate_action_counts": dict(sorted(candidate_acts.items())),
        "candidate_dialogue_act_counts": dict(sorted(candidate_dialogue_acts.items())),
        "supporting_act_counts": dict(sorted(supporting_acts.items())),
        "missing_v2_fields": dict(sorted(missing_v2_fields.items())),
        "diagnostics": _diagnostics(dialogue_acts),
    }


def _diagnostics(dialogue_acts: Counter[str]) -> list[str]:
    diagnostics: list[str] = []
    if dialogue_acts.get("Recommend", 0) == 0:
        diagnostics.append("No Recommend best-actions; keep Recommend as candidate/negative unless building a balanced policy dataset.")
    if dialogue_acts.get("Greet", 0) == 0:
        diagnostics.append("No Greet best-actions; expected for PIWM-Train-Synth-v1 because it is not a transaction/closing dataset.")
    if dialogue_acts.get("Inform", 0) > sum(dialogue_acts.values()) * 0.6:
        diagnostics.append("Inform dominates best-actions; future generation should balance scenes or reward priors if training a balanced policy head.")
    return diagnostics


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
