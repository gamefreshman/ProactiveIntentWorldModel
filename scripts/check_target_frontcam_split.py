"""Validate the derived PIWM target-frontcam 71/30 balanced 5-act split."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.target_frontcam_split import (
    EXPECTED_5ACT_TEST_COUNTS,
    TARGET_FRONT_CAM_5ACT_TEST_IDS,
    source_session_id_from_state_id,
)


DEFAULT_STAGE2_TRAIN = Path("data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl")
DEFAULT_ACTION_EVAL = Path("data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl")
EXPECTED_TRAIN_ROWS = 71
EXPECTED_TEST_ROWS = 30


def check_target_frontcam_split(stage2_train: Path, action_eval: Path) -> dict[str, Any]:
    train_rows = _read_jsonl(stage2_train)
    test_rows = _read_jsonl(action_eval)
    test_ids = {source_session_id_from_state_id(str(row["source_id"])) for row in test_rows}
    test_act_counts = Counter(_best_act(row) for row in test_rows)
    train_act_counts = Counter(_best_act(row) for row in train_rows)

    errors: list[str] = []
    if len(train_rows) != EXPECTED_TRAIN_ROWS:
        errors.append(f"stage2 train rows expected {EXPECTED_TRAIN_ROWS}, got {len(train_rows)}")
    if len(test_rows) != EXPECTED_TEST_ROWS:
        errors.append(f"target action eval rows expected {EXPECTED_TEST_ROWS}, got {len(test_rows)}")
    if dict(test_act_counts) != EXPECTED_5ACT_TEST_COUNTS:
        errors.append(f"test best-act counts expected {EXPECTED_5ACT_TEST_COUNTS}, got {dict(test_act_counts)}")
    if test_ids != TARGET_FRONT_CAM_5ACT_TEST_IDS:
        missing = sorted(TARGET_FRONT_CAM_5ACT_TEST_IDS - test_ids)
        extra = sorted(test_ids - TARGET_FRONT_CAM_5ACT_TEST_IDS)
        errors.append(f"test id mismatch; missing={missing}, extra={extra}")
    for label, rows in (("train", train_rows), ("test", test_rows)):
        leaked = [_leaked_candidates(row) for row in rows]
        leaked = [item for item in leaked if item]
        if leaked:
            errors.append(f"{label} rows contain non-5-act candidate labels: {leaked[:5]}")

    summary = {
        "artifact": "piwm_target_frontcam_derived_71_30_split_check",
        "stage2_train": stage2_train.as_posix(),
        "action_eval": action_eval.as_posix(),
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "test_ids": sorted(test_ids),
        "test_best_act_counts": dict(sorted(test_act_counts.items())),
        "train_best_act_counts": dict(sorted(train_act_counts.items())),
        "errors": errors,
    }
    if errors:
        raise AssertionError(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def _best_act(row: dict[str, Any]) -> str:
    meta = row.get("meta", {})
    if meta.get("best_act"):
        return str(meta["best_act"])
    target = row.get("messages", [{}, {}, {"content": ""}])[2].get("content", "")
    marker = "<chosen>"
    if marker in target:
        chosen = target.split(marker, 1)[1].split("</chosen>", 1)[0].strip()
        return str(row.get("meta", {}).get("candidate_action_acts", {}).get(chosen, chosen.split("_", 1)[0]))
    return "unknown"


def _leaked_candidates(row: dict[str, Any]) -> list[str]:
    acts = row.get("meta", {}).get("candidate_action_acts", {})
    return sorted({str(act) for act in acts.values()} - set(EXPECTED_5ACT_TEST_COUNTS))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage2-train", type=Path, default=DEFAULT_STAGE2_TRAIN)
    parser.add_argument("--action-eval", type=Path, default=DEFAULT_ACTION_EVAL)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(json.dumps(check_target_frontcam_split(args.stage2_train, args.action_eval), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
