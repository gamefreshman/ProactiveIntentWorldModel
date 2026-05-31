from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CHOSEN_RE = re.compile(r"<chosen>\s*(.*?)\s*</chosen>", re.DOTALL)


def inspect_path(path: Path) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    missing_rows: list[int] = []
    n_rows = 0

    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            n_rows += 1
            row = json.loads(line)
            best_act = best_act_from_row(row)
            if best_act:
                counts[best_act] += 1
            else:
                missing_rows.append(line_no)

    return {
        "artifact": "act_balance",
        "input_path": str(path),
        "n_rows": n_rows,
        "best_act_counts": dict(sorted(counts.items())),
        "inverse_freq_weights": _inverse_freq_weights(counts),
        "missing_best_act_rows": missing_rows,
    }


def best_act_from_row(row: dict[str, Any]) -> str:
    return _policy_preference_best_act(row) or _ms_swift_best_act(row)


def _policy_preference_best_act(row: dict[str, Any]) -> str:
    chosen = row.get("chosen_json")
    if not isinstance(chosen, dict):
        return ""

    action_spec = chosen.get("action_spec")
    if isinstance(action_spec, dict) and action_spec.get("act"):
        return str(action_spec["act"])

    dialogue_act = chosen.get("dialogue_act")
    if isinstance(dialogue_act, dict) and dialogue_act.get("act"):
        return str(dialogue_act["act"])

    return ""


def _ms_swift_best_act(row: dict[str, Any]) -> str:
    meta = row.get("meta")
    if not isinstance(meta, dict):
        meta = {}

    if meta.get("best_act"):
        return str(meta["best_act"])

    chosen_action = _chosen_action_from_messages(row.get("messages"))
    if not chosen_action:
        return ""

    candidate_action_acts = meta.get("candidate_action_acts")
    if isinstance(candidate_action_acts, dict) and candidate_action_acts.get(chosen_action):
        return str(candidate_action_acts[chosen_action])

    return chosen_action.split("_", 1)[0] if "_" in chosen_action else ""


def _chosen_action_from_messages(messages: Any) -> str:
    if not isinstance(messages, list):
        return ""

    for message in reversed(messages):
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, str):
            continue
        match = CHOSEN_RE.search(content)
        if match:
            return match.group(1).strip()
    return ""


def _inverse_freq_weights(counts: Counter[str]) -> dict[str, float]:
    total = sum(counts.values())
    num_classes = len(counts)
    if not total or not num_classes:
        return {}
    return {act: round(total / (num_classes * count), 6) for act, count in sorted(counts.items())}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect best act distribution and inverse-frequency weights for a JSONL file.")
    parser.add_argument("jsonl_path", type=Path)
    args = parser.parse_args(argv)

    summary = inspect_path(args.jsonl_path)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
