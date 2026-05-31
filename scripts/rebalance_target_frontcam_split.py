"""Rebalance PIWM-Target-Frontcam-v1 to a balanced 5-act train/test split."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.build_domain_specialization_eval_sets import build_domain_specialization_eval_sets
from scripts.build_target_frontcam_qa_review import build_target_frontcam_qa_review
from scripts.target_frontcam_split import (
    EXPECTED_5ACT_TEST_COUNTS,
    TARGET_FRONT_CAM_5ACT_TEST_IDS,
    best_act_from_row,
    source_session_id_from_state_id,
    split_for_target_frontcam_session,
    summarize_target_split,
)


DEFAULT_TARGET_DIR = Path("data/official/piwm_target_v1")
DEFAULT_MS_SWIFT = Path("data/official/ms_swift/piwm_train_target_specialization_v1.jsonl")
DEFAULT_GENERAL_EVAL = Path("data/official/ms_swift/piwm_eval_qa_all_v1.jsonl")
DEFAULT_DOMAIN_EVAL_DIR = Path("data/official/domain_specialization_eval_v1")
DEFAULT_QA_DIR = Path("data/official/piwm_target_v1/qa_review_target30_5act")
QA_PENDING = "qa_pending_project_lead_review"
HUMAN_REVIEW_PENDING = "pending_project_lead_review"

TARGET_DATASET_FILES = (
    "state_inference.jsonl",
    "state_inference_with_cue.jsonl",
    "transition_modeling.jsonl",
    "policy_preference.jsonl",
    "world_model_continuation.jsonl",
)

STALE_REVIEWED_EVAL_FILES = (
    "target_frontcam_test_qa_reviewed_all.jsonl",
    "target_frontcam_test_qa_reviewed_perception.jsonl",
    "target_frontcam_test_qa_reviewed_deliberation.jsonl",
    "target_frontcam_test_qa_reviewed_action_selection.jsonl",
)


def rebalance_target_frontcam_split(
    *,
    target_dir: Path,
    ms_swift: Path,
    general_eval: Path,
    domain_eval_dir: Path,
    qa_dir: Path,
    repo_root: Path,
    build_qa_packet: bool = True,
) -> dict[str, Any]:
    main_schema = target_dir / "main_schema.jsonl"
    main_rows = _read_jsonl(main_schema)
    _validate_source_ids(main_rows)

    updated_main = [_with_main_split(row) for row in main_rows]
    _validate_main_split(updated_main)
    _write_jsonl(updated_main, main_schema)

    updated_target_files: dict[str, int] = {}
    for filename in TARGET_DATASET_FILES:
        path = target_dir / filename
        if path.exists():
            rows = [_with_meta_split(row) for row in _read_jsonl(path)]
            _write_jsonl(rows, path)
            updated_target_files[filename] = len(rows)

    swift_rows = [_with_swift_split(row) for row in _read_jsonl(ms_swift)]
    _write_jsonl(swift_rows, ms_swift)

    legacy_eval_dir = _archive_stale_reviewed_eval_files(domain_eval_dir)
    eval_summary = build_domain_specialization_eval_sets(
        ms_swift,
        general_eval,
        domain_eval_dir,
        target_split="test",
    )

    qa_summary = None
    if build_qa_packet:
        qa_summary = build_target_frontcam_qa_review(
            main_schema,
            qa_dir,
            repo_root=repo_root,
            split="test",
        )

    _write_legacy_qa_note(target_dir / "qa_review_target30")

    summary = {
        "artifact": "piwm_target_frontcam_5act_split_rebalance",
        "target_dir": target_dir.as_posix(),
        "main_schema": main_schema.as_posix(),
        "ms_swift": ms_swift.as_posix(),
        "domain_eval_dir": domain_eval_dir.as_posix(),
        "qa_dir": qa_dir.as_posix(),
        "split_policy": "balanced_5act_operational_test_ids",
        "qa_status": "new_5act_test_requires_independent_review_before_promotion",
        "expected_test_best_act_counts": EXPECTED_5ACT_TEST_COUNTS,
        "target_summary": summarize_target_split(updated_main),
        "updated_target_files": updated_target_files,
        "ms_swift_rows": len(swift_rows),
        "ms_swift_split_counts": _swift_split_counts(swift_rows),
        "archived_legacy_reviewed_eval_dir": legacy_eval_dir.as_posix() if legacy_eval_dir else None,
        "eval_summary": eval_summary,
        "qa_packet_summary": qa_summary,
    }
    (target_dir / "split_rebalance_5act_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (target_dir / "split_rebalance_5act_summary.md").write_text(
        _markdown(summary),
        encoding="utf-8",
    )
    return summary


def _with_main_split(row: dict[str, Any]) -> dict[str, Any]:
    updated = dict(row)
    session_id = str(updated.get("source_session_id") or source_session_id_from_state_id(str(updated["state_id"])))
    split = split_for_target_frontcam_session(session_id)
    updated["split"] = split
    if split == "test":
        updated["qa_status"] = QA_PENDING
        updated["human_review_status"] = HUMAN_REVIEW_PENDING
        updated.pop("qa_review", None)
    else:
        updated["qa_status"] = "synthetic_unreviewed"
        updated.pop("human_review_status", None)
        updated.pop("qa_review", None)
    return updated


def _with_meta_split(row: dict[str, Any]) -> dict[str, Any]:
    updated = dict(row)
    meta = dict(updated.get("meta") or {})
    state_id = str(meta.get("parent_state_id") or updated.get("state_id", ""))
    session_id = source_session_id_from_state_id(state_id)
    split = split_for_target_frontcam_session(session_id)
    meta["split"] = split
    _set_or_clear_pending_qa(meta, split)
    updated["meta"] = meta
    return updated


def _with_swift_split(row: dict[str, Any]) -> dict[str, Any]:
    updated = dict(row)
    meta = dict(updated.get("meta") or {})
    source_id = str(updated.get("source_id", ""))
    session_id = source_session_id_from_state_id(source_id)
    split = split_for_target_frontcam_session(session_id)
    meta["split"] = split
    _set_or_clear_pending_qa(meta, split)
    updated["meta"] = meta
    return updated


def _set_or_clear_pending_qa(meta: dict[str, Any], split: str) -> None:
    if split == "test":
        meta["qa_status"] = QA_PENDING
        meta["human_review_status"] = HUMAN_REVIEW_PENDING
        for key in ("qa_reviewer", "qa_reviewed_at", "qa_review_type", "qa_warning_flags"):
            meta.pop(key, None)
        return
    for key in (
        "qa_status",
        "human_review_status",
        "qa_reviewer",
        "qa_reviewed_at",
        "qa_review_type",
        "qa_warning_flags",
    ):
        meta.pop(key, None)


def _validate_source_ids(rows: list[dict[str, Any]]) -> None:
    seen = {str(row.get("source_session_id") or source_session_id_from_state_id(str(row["state_id"]))) for row in rows}
    missing = sorted(TARGET_FRONT_CAM_5ACT_TEST_IDS - seen)
    if missing:
        raise ValueError(f"missing required 5-act test session ids: {missing}")


def _validate_main_split(rows: list[dict[str, Any]]) -> None:
    split_counts = Counter(str(row.get("split")) for row in rows)
    if split_counts != {"train": 88, "test": 30}:
        raise ValueError(f"expected split counts train=88/test=30, got {dict(split_counts)}")
    test_counts = Counter(best_act_from_row(row) for row in rows if row.get("split") == "test")
    if dict(test_counts) != EXPECTED_5ACT_TEST_COUNTS:
        raise ValueError(f"expected 5-act test counts {EXPECTED_5ACT_TEST_COUNTS}, got {dict(test_counts)}")
    if test_counts.get("Reassure", 0):
        raise ValueError("Reassure must not appear in the 5-act target test split")


def _archive_stale_reviewed_eval_files(domain_eval_dir: Path) -> Path | None:
    legacy_dir = domain_eval_dir / "_legacy_wrong_5act"
    moved = []
    for filename in STALE_REVIEWED_EVAL_FILES:
        path = domain_eval_dir / filename
        if path.exists():
            legacy_dir.mkdir(parents=True, exist_ok=True)
            destination = legacy_dir / filename
            if destination.exists():
                destination.unlink()
            shutil.move(path.as_posix(), destination.as_posix())
            moved.append(filename)
    if moved:
        (legacy_dir / "README.md").write_text(
            "# Legacy Target QA Eval Files\n\n"
            "These files belong to the previous last-30 target test split. "
            "After the 2026-05-19 5-act rebalance they are kept only as history "
            "and must not be used as the current target-frontcam QA-reviewed eval set.\n",
            encoding="utf-8",
        )
        return legacy_dir
    return legacy_dir if legacy_dir.exists() else None


def _write_legacy_qa_note(old_qa_dir: Path) -> None:
    if not old_qa_dir.exists():
        return
    (old_qa_dir / "LEGACY_SPLIT_NOTE.md").write_text(
        "# Legacy QA Review Packet\n\n"
        "This folder documents the previous last-30 target test split. "
        "The current target test split is the 5-act operational split under "
        "`../qa_review_target30_5act/` and must be reviewed separately before "
        "being called QA-reviewed.\n",
        encoding="utf-8",
    )


def _swift_split_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str((row.get("meta") or {}).get("split", "unknown")) for row in rows).items()))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _markdown(summary: dict[str, Any]) -> str:
    test_counts = summary["target_summary"]["best_act_by_split"]["test"]
    train_counts = summary["target_summary"]["best_act_by_split"]["train"]
    lines = [
        "# PIWM Target Frontcam 5-Act Split Rebalance",
        "",
        f"- qa_status: `{summary['qa_status']}`",
        f"- main_schema: `{summary['main_schema']}`",
        f"- ms_swift_rows: {summary['ms_swift_rows']}",
        f"- archived_legacy_reviewed_eval_dir: `{summary['archived_legacy_reviewed_eval_dir']}`",
        "",
        "## Test Best-Act Counts",
        "",
        "| Act | Count |",
        "|---|---:|",
    ]
    for act, count in sorted(test_counts.items()):
        lines.append(f"| `{act}` | {count} |")
    lines.extend(["", "## Train Best-Act Counts", "", "| Act | Count |", "|---|---:|"])
    for act, count in sorted(train_counts.items()):
        lines.append(f"| `{act}` | {count} |")
    lines.extend([
        "",
        "## QA Boundary",
        "",
        "The new 5-act test split must be reviewed independently from the old split. "
        "Do not use the old reviewed eval files as current QA-reviewed target eval.",
        "",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, default=DEFAULT_TARGET_DIR)
    parser.add_argument("--ms-swift", type=Path, default=DEFAULT_MS_SWIFT)
    parser.add_argument("--general-eval", type=Path, default=DEFAULT_GENERAL_EVAL)
    parser.add_argument("--domain-eval-dir", type=Path, default=DEFAULT_DOMAIN_EVAL_DIR)
    parser.add_argument("--qa-dir", type=Path, default=DEFAULT_QA_DIR)
    parser.add_argument("--no-qa-packet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path.cwd().resolve()
    summary = rebalance_target_frontcam_split(
        target_dir=args.target_dir,
        ms_swift=args.ms_swift,
        general_eval=args.general_eval,
        domain_eval_dir=args.domain_eval_dir,
        qa_dir=args.qa_dir,
        repo_root=repo_root,
        build_qa_packet=not args.no_qa_packet,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
