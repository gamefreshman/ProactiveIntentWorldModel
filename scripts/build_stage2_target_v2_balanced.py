#!/usr/bin/env python3
"""Build target_v2 Stage-2 data without video-pending colleague rows.

Operational 5-act:
Greet / Elicit / Inform / Recommend / Hold. Reassure is excluded.

The current target/GreetAug source has no Hold rows and no general Greet rows
exist. We therefore preserve all 86 target rows and use general parent records
only to fill Elicit/Recommend/Hold up to the existing Inform count.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from piwm_train.ms_swift_adapter import build_ms_swift_record

from scripts.build_two_stage_training_and_eval import (
    _action_example,
    _block_act,
    _read_jsonl,
    _write_rows,
)

FIVE_ACTS = ["Greet", "Elicit", "Inform", "Recommend", "Hold"]
FIVE_ACT_SET = set(FIVE_ACTS)

DEFAULT_STAGE1 = REPO_ROOT / "data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl"
DEFAULT_BASE_STAGE2 = REPO_ROOT / "data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl"
DEFAULT_GENERAL_POLICY = REPO_ROOT / "data/official/piwm_train_synth_v2/policy_preference.jsonl"
DEFAULT_OUTPUT_STAGE2 = REPO_ROOT / "data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl"
DEFAULT_OUTPUT_JOINT = REPO_ROOT / "data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl"


def main() -> None:
    args = parse_args()
    summary = build_target_v2(
        base_stage2=args.base_stage2,
        stage1=args.stage1,
        general_policy=args.general_policy,
        output_stage2=args.output_stage2,
        output_joint=args.output_joint,
        balance_target=args.balance_target,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def build_target_v2(
    *,
    base_stage2: Path,
    stage1: Path,
    general_policy: Path,
    output_stage2: Path,
    output_joint: Path,
    balance_target: int | None,
) -> dict[str, Any]:
    base_rows = _read_jsonl(base_stage2)
    validate_stage2_rows(base_rows)

    base_counts = Counter(best_act(row) for row in base_rows)
    target_count = balance_target if balance_target is not None else max(base_counts.values())

    general_rows, general_summary = build_general_balancing_rows(
        general_policy=general_policy,
        base_counts=base_counts,
        target_count=target_count,
    )

    target_v2_rows = base_rows + general_rows
    validate_stage2_rows(target_v2_rows)

    stage2_summary = _write_rows(target_v2_rows, output_stage2)
    stage1_rows = _read_jsonl(stage1)
    joint_rows = stage1_rows + target_v2_rows
    joint_summary = _write_rows(joint_rows, output_joint)

    summary = {
        "artifact": "piwm_stage2_target_v2_balanced_generation",
        "is_training_result": False,
        "five_act": FIVE_ACTS,
        "policy": {
            "exclude_external_video_pending_batch": "piwm_1001-piwm_1118",
            "base_rows_preserved": len(base_rows),
            "base_balance_target": target_count,
            "balancing_rule": (
                "Preserve all current target/GreetAug rows, then fill each "
                "general-available act below the target count using stable "
                "state_id-sorted evenly spaced general samples."
            ),
            "greet_limitation": (
                "Greet has no general parent records, so it remains at the "
                "base count unless explicit duplication or new Greet data is approved."
            ),
        },
        "outputs": {
            "stage2_jsonl": display_path(output_stage2),
            "stage2_sha256": sha256_file(output_stage2),
            "stage2_rows": len(target_v2_rows),
            "joint_jsonl": display_path(output_joint),
            "joint_sha256": sha256_file(output_joint),
            "joint_rows": len(joint_rows),
            "summary_json": display_path(output_stage2.with_name(f"{output_stage2.stem}_summary.json")),
            "stage2_write_summary": stage2_summary,
            "joint_write_summary": joint_summary,
        },
        "inputs": {
            "base_stage2": display_path(base_stage2),
            "base_stage2_rows": len(base_rows),
            "stage1": display_path(stage1),
            "stage1_rows": len(stage1_rows),
            "general_policy": display_path(general_policy),
        },
        "source_counts": source_counts(target_v2_rows),
        "base_best_act_counts": dict(sorted(base_counts.items())),
        "best_act_counts": act_counts(target_v2_rows),
        "candidate_act_slot_counts": candidate_slot_counts(target_v2_rows),
        "image_rows": {
            "with_images": sum(1 for row in target_v2_rows if row.get("images")),
            "without_images": sum(1 for row in target_v2_rows if not row.get("images")),
            "image_path_count": sum(len(row.get("images", [])) for row in target_v2_rows),
        },
        "general_import": general_summary,
        "validation": validation_summary(target_v2_rows),
        "notes": [
            "All 86 target/GreetAug rows are preserved.",
            "No piwm_1001-1118 rows are imported because that batch is video-pending and has no matching frames.",
            "No Reassure rows or Reassure candidate acts are allowed in operational Stage-2 rows.",
            "General rows are synthetic_unreviewed and should be described as general-to-target balancing supervision, not target frontcam QA data.",
        ],
    }
    output_stage2.with_name(f"{output_stage2.stem}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def build_general_balancing_rows(
    *,
    general_policy: Path,
    base_counts: Counter[str],
    target_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    available: dict[str, list[dict[str, Any]]] = {act: [] for act in FIVE_ACTS}
    for row in _read_jsonl(general_policy):
        act = _block_act(row.get("chosen_json", {}))
        if act in available:
            available[act].append(row)
    for rows in available.values():
        rows.sort(key=lambda row: row["state_id"])

    requested: dict[str, int] = {}
    selected_by_act: dict[str, list[dict[str, Any]]] = {}
    shortfalls: dict[str, int] = {}
    for act in FIVE_ACTS:
        need = max(0, target_count - int(base_counts.get(act, 0)))
        requested[act] = need
        if need == 0:
            selected_by_act[act] = []
            continue
        if len(available[act]) < need:
            selected = available[act]
            shortfalls[act] = need - len(selected)
        else:
            selected = evenly_spaced(available[act], need)
        selected_by_act[act] = selected

    imported: list[dict[str, Any]] = []
    selected_source_ids: dict[str, list[str]] = {}
    for act in FIVE_ACTS:
        selected_source_ids[act] = [row["state_id"] for row in selected_by_act[act]]
        for row in selected_by_act[act]:
            imported.append(convert_general_policy_row(row, act))

    return imported, {
        "available_best_act_counts": {act: len(available[act]) for act in FIVE_ACTS},
        "requested_rows_by_act": requested,
        "imported_rows_by_act": {act: len(selected_by_act[act]) for act in FIVE_ACTS},
        "shortfalls_by_act": shortfalls,
        "imported_rows_total": len(imported),
        "selection": "state_id sorted, evenly spaced indices round(i*(n-1)/(k-1)) per act",
        "selected_source_ids": selected_source_ids,
        "qa_status": "synthetic_unreviewed",
    }


def convert_general_policy_row(row: dict[str, Any], act: str) -> dict[str, Any]:
    updated = json.loads(json.dumps(row, ensure_ascii=False))
    meta = dict(updated.get("meta") or {})
    state_summary = dict(meta.get("state_summary") or {})
    candidate_specs = state_summary.get("candidate_action_specs") or meta.get("candidate_action_specs")
    if candidate_specs:
        state_summary["candidate_action_specs"] = [
            spec for spec in candidate_specs if spec.get("act") in FIVE_ACT_SET
        ]
    state_summary["source_dataset"] = "PIWM-Train-Synth-v2/policy_preference"
    state_summary["balancing_source_act"] = act

    meta["split"] = "train"
    meta["source_dataset"] = "PIWM-Train-Synth-v2/policy_preference"
    meta["source_session_id"] = row["state_id"]
    meta["is_augmented"] = True
    meta["augmentation_policy"] = f"target_v2_general_{act.lower()}_balance_to_41_v2"
    meta["qa_status"] = "synthetic_unreviewed"
    meta["human_review_status"] = "not_reviewed"
    meta["state_summary"] = state_summary
    updated["state_id"] = f"general_{act.lower()}_{row['state_id']}"
    updated["meta"] = meta
    example = _action_example(updated)
    return build_ms_swift_record(example, root=REPO_ROOT, validate_images=False)


def evenly_spaced(rows: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if count <= 0:
        return []
    if len(rows) < count:
        raise ValueError(f"not enough rows for even sample: need {count}, found {len(rows)}")
    if count == 1:
        return [rows[0]]
    indices = [round(i * (len(rows) - 1) / (count - 1)) for i in range(count)]
    if len(set(indices)) != len(indices):
        raise ValueError("even sampling produced duplicate indices")
    return [rows[index] for index in indices]


def validate_stage2_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("no rows generated")
    source_ids = [row.get("source_id") for row in rows]
    duplicates = [item for item, n in Counter(source_ids).items() if n > 1]
    if duplicates:
        raise ValueError(f"duplicate source_id values: {duplicates[:10]}")
    errors: list[str] = []
    for row in rows:
        if row.get("task") != "action_selection_5act":
            errors.append(f"{row.get('source_id')}: task={row.get('task')}")
            continue
        meta = row.get("meta") or {}
        best = meta.get("best_act")
        candidates = meta.get("candidate_action_acts") or {}
        text = json.dumps(row, ensure_ascii=False)
        if best not in FIVE_ACT_SET:
            errors.append(f"{row.get('source_id')}: non-5-act best={best}")
        if "Reassure" in text or "reassure_" in text:
            errors.append(f"{row.get('source_id')}: contains operational Reassure string")
        if best not in set(candidates.values()):
            errors.append(f"{row.get('source_id')}: best={best} not in candidates={candidates}")
        if not candidates:
            errors.append(f"{row.get('source_id')}: empty candidate_action_acts")
        for label, act in candidates.items():
            if act not in FIVE_ACT_SET:
                errors.append(f"{row.get('source_id')}: candidate {label} has act={act}")
    if errors:
        raise ValueError("stage2 validation failed:\n" + "\n".join(errors[:50]))


def validation_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_sizes = Counter(len((row.get("meta") or {}).get("candidate_action_acts") or {}) for row in rows)
    best_in_candidate = 0
    for row in rows:
        meta = row.get("meta") or {}
        if meta.get("best_act") in set((meta.get("candidate_action_acts") or {}).values()):
            best_in_candidate += 1
    return {
        "rows": len(rows),
        "reassure_string_hits": sum(
            1
            for row in rows
            if "Reassure" in json.dumps(row, ensure_ascii=False)
            or "reassure_" in json.dumps(row, ensure_ascii=False)
        ),
        "best_act_in_candidate_set": best_in_candidate,
        "candidate_size_counts": dict(sorted(candidate_sizes.items())),
    }


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        source_id = str(row.get("source_id", ""))
        policy = (row.get("meta") or {}).get("augmentation_policy")
        if source_id.startswith("target_"):
            counts["target_existing_71"] += 1
        elif source_id.startswith("greet_aug_"):
            counts["general_greet_aug_existing_15"] += 1
        elif isinstance(policy, str) and policy.startswith("target_v2_general_"):
            counts["general_policy_balancing"] += 1
        else:
            counts["unknown"] += 1
    return dict(sorted(counts.items()))


def act_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(best_act(row) for row in rows).items()))


def best_act(row: dict[str, Any]) -> str:
    return str((row.get("meta") or {}).get("best_act"))


def candidate_slot_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for act in ((row.get("meta") or {}).get("candidate_action_acts") or {}).values():
            counts[act] += 1
    return dict(sorted(counts.items()))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-stage2", type=Path, default=DEFAULT_BASE_STAGE2)
    parser.add_argument("--stage1", type=Path, default=DEFAULT_STAGE1)
    parser.add_argument("--general-policy", type=Path, default=DEFAULT_GENERAL_POLICY)
    parser.add_argument("--output-stage2", type=Path, default=DEFAULT_OUTPUT_STAGE2)
    parser.add_argument("--output-joint", type=Path, default=DEFAULT_OUTPUT_JOINT)
    parser.add_argument(
        "--balance-target",
        type=int,
        default=None,
        help="Per-act target for general-backed filling. Default: max base act count.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
