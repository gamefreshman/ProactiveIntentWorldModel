"""Build action-conditioned future-verification rows from continuation data.

This converts Phase-7 continuation videos from an audit-only artifact into a
multimodal supervision task:

    current_frames + candidate_action + continuation_frames -> match / mismatch

Positive pairs use the continuation generated for the same action. Negative
pairs swap in another continuation from the same parent state only when the two
continuations have different expected next states.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from piwm_data import reaction_templates, rules

FUTURE_VERIFICATION_JSONL = "future_verification.jsonl"
FUTURE_VERIFICATION_STATS = "_future_verification_stats.json"


def build_future_verification_rows(
    continuation_rows: list[dict[str, Any]],
    *,
    max_negative_per_positive: int = 1,
) -> list[dict[str, Any]]:
    by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in continuation_rows:
        by_parent[row["meta"]["parent_state_id"]].append(row)

    rows: list[dict[str, Any]] = []
    for parent_id in sorted(by_parent):
        group = sorted(by_parent[parent_id], key=lambda item: item["state_id"])
        for anchor in group:
            rows.append(_positive_row(anchor))
            negatives = [
                other
                for other in group
                if other["state_id"] != anchor["state_id"]
                and other["output"]["next_state"] != anchor["output"]["next_state"]
            ]
            for other in negatives[:max_negative_per_positive]:
                rows.append(_negative_row(anchor, other))
    return rows


def summarize_future_verification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n_positive = sum(1 for row in rows if row["meta"]["is_positive_pair"])
    n_negative = len(rows) - n_positive
    by_split: dict[str, int] = {}
    by_viewpoint: dict[str, int] = {}
    by_match: dict[str, int] = {}
    for row in rows:
        split = row["meta"].get("split") or "unknown"
        viewpoint = row["meta"].get("viewpoint") or "unknown"
        match = row["output"]["match"]
        by_split[split] = by_split.get(split, 0) + 1
        by_viewpoint[viewpoint] = by_viewpoint.get(viewpoint, 0) + 1
        by_match[match] = by_match.get(match, 0) + 1
    return {
        "artifact": "future_verification_dataset",
        "n_rows": len(rows),
        "n_positive_pairs": n_positive,
        "n_negative_pairs": n_negative,
        "n_rows_by_match": by_match,
        "n_rows_by_split": dict(sorted(by_split.items())),
        "n_rows_by_viewpoint": dict(sorted(by_viewpoint.items())),
        "requires_future_frames_as_input": True,
        "negative_pair_policy": "same_parent_swapped_continuation_with_different_expected_next_state",
    }


def _positive_row(anchor: dict[str, Any]) -> dict[str, Any]:
    action = anchor["input"]["candidate_action"]
    expected_state = anchor["output"]["next_state"]
    return _base_row(
        anchor=anchor,
        continuation=anchor,
        state_id=f"{anchor['state_id']}#verify_positive",
        match="yes",
        expected_state=expected_state,
        reason=(
            "The visible future reaction matches the expert-rule expectation "
            f"for {action} under this customer state."
        ),
        is_positive_pair=True,
    )


def _negative_row(anchor: dict[str, Any], swapped: dict[str, Any]) -> dict[str, Any]:
    action = anchor["input"]["candidate_action"]
    expected_state = anchor["output"]["next_state"]
    swapped_action = swapped["input"]["candidate_action"]
    return _base_row(
        anchor=anchor,
        continuation=swapped,
        state_id=f"{anchor['state_id']}#verify_negative_with_{swapped_action}",
        match="no",
        expected_state=expected_state,
        reason=(
            "The visible future reaction differs from the expert-rule expectation "
            f"for {action} under this customer state."
        ),
        is_positive_pair=False,
    )


def _base_row(
    *,
    anchor: dict[str, Any],
    continuation: dict[str, Any],
    state_id: str,
    match: str,
    expected_state: str,
    reason: str,
    is_positive_pair: bool,
) -> dict[str, Any]:
    expected_template_id, _expected_template = reaction_templates.template_for_next_state(expected_state)
    observed_state = continuation["output"]["next_state"]
    observed_template_id, observed_template = reaction_templates.template_for_next_state(observed_state)
    return {
        "state_id": state_id,
        "input": {
            "current_frames": list(anchor["input"]["current_frames"]),
            "candidate_action": anchor["input"]["candidate_action"],
            "continuation_frames": _continuation_frame_paths(continuation),
            "current_state_summary": dict(anchor["input"]["current_state_summary"]),
        },
        "output": {
            "match": match,
            "expected_next_state": expected_state,
            "visible_reaction": {
                "body_change": observed_template["physical_change"],
                "gaze_change": observed_template["head_gaze"],
                "hand_change": observed_template["hands"],
                "movement_change": observed_template["movement"],
            },
            "reason": reason,
        },
        "meta": {
            "parent_state_id": anchor["meta"]["parent_state_id"],
            "continuation_id": continuation["state_id"],
            "anchor_continuation_id": anchor["state_id"],
            "candidate_action": anchor["input"]["candidate_action"],
            "continuation_action": continuation["input"]["candidate_action"],
            "anchor_expected_next_state": anchor["output"]["next_state"],
            "continuation_expected_next_state": continuation["output"]["next_state"],
            "visible_reaction_next_state": observed_state,
            "expected_reaction_template_id": expected_template_id,
            "observed_reaction_template_id": observed_template_id,
            "continuation_reaction_template_id": continuation["meta"].get("reaction_template_id"),
            "label_source": "expert_rule_plus_continuation_qa",
            "is_positive_pair": is_positive_pair,
            "split": anchor["meta"].get("split"),
            "viewpoint": anchor["meta"].get("viewpoint"),
            "product_category": anchor["meta"].get("product_category"),
            "rule_version": anchor["meta"].get("rule_version", rules.RULE_VERSION),
        },
    }


def _continuation_frame_paths(row: dict[str, Any]) -> list[str]:
    frames = row["output"].get("continuation_frames", [])
    paths: list[str] = []
    for frame in frames:
        if isinstance(frame, str):
            paths.append(frame)
        else:
            paths.append(frame["relative_path"])
    return paths


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_jsonl(rows: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--input-jsonl", type=Path, default=None)
    parser.add_argument("--output-jsonl", type=Path, default=None)
    parser.add_argument("--stats-out", type=Path, default=None)
    parser.add_argument("--max-negative-per-positive", type=int, default=1)
    parser.add_argument("--preview", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_jsonl = args.input_jsonl or args.data_dir / "world_model_continuation.jsonl"
    output_jsonl = args.output_jsonl or args.data_dir / FUTURE_VERIFICATION_JSONL
    stats_out = args.stats_out or args.data_dir / FUTURE_VERIFICATION_STATS
    continuation_rows = _read_jsonl(input_jsonl)
    rows = build_future_verification_rows(
        continuation_rows,
        max_negative_per_positive=args.max_negative_per_positive,
    )
    _write_jsonl(rows, output_jsonl)
    summary = summarize_future_verification(rows)
    summary.update(
        {
            "data_dir": str(args.data_dir),
            "input_jsonl": str(input_jsonl),
            "output_jsonl": str(output_jsonl),
        }
    )
    stats_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.preview:
        for row in rows[: args.preview]:
            print(json.dumps(row, ensure_ascii=False, indent=2)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
