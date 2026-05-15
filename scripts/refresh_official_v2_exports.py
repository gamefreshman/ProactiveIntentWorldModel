"""Refresh official PIWM JSONL exports with the v2.2 action/realization fields."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from piwm_data import rules
from piwm_data.exporters import (
    build_policy_preference_row,
    export_policy_preference,
    export_state_inference,
    export_state_inference_with_cue,
    export_transition_modeling,
    export_world_model_continuation,
    main_schema_record_payload,
)
from piwm_data.schemas import MainSchemaRecord


DEFAULT_DATASETS = [
    "data/official/piwm_train_synth_v1",
    "data/official/piwm_eval_qa_v1",
    "data/official/piwm_world_model_v1",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rewrite official PIWM dataset JSONL files with schema v2.2 fields.")
    parser.add_argument("--dataset", action="append", type=Path, help="Dataset directory; may be a symlink.")
    parser.add_argument("--summary-out", type=Path, default=Path("data/official/V2_REEXPORT_SUMMARY.json"))
    parser.add_argument("--dry-run", action="store_true", help="Load and summarize records without rewriting official files.")
    parser.add_argument("--output-diff", type=Path, default=None, help="With --dry-run, write a planned file-diff summary without modifying official files.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Write one dataset to an independent directory instead of rewriting the source dataset.")
    args = parser.parse_args(argv)
    if args.output_diff is not None and not args.dry_run:
        parser.error("--output-diff requires --dry-run")

    dataset_paths = args.dataset or [Path(path) for path in DEFAULT_DATASETS]
    if args.output_dir is not None and len(dataset_paths) != 1:
        parser.error("--output-dir requires exactly one --dataset")
    summaries = [
        refresh_dataset(
            path,
            dry_run=args.dry_run,
            include_diff=args.output_diff is not None,
            output_dir=args.output_dir if len(dataset_paths) == 1 else None,
        )
        for path in dataset_paths
    ]
    payload = {
        "artifact": "piwm_official_v2_2_reexport_summary",
        "timestamp_utc": _now(),
        "schema_version": "v2.2",
        "rule_version": rules.RULE_VERSION,
        "dry_run": args.dry_run,
        "datasets": summaries,
    }
    if not args.dry_run:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.output_diff is not None:
        args.output_diff.parent.mkdir(parents=True, exist_ok=True)
        args.output_diff.write_text(_reexport_diff_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def refresh_dataset(
    dataset_dir: Path,
    dry_run: bool = False,
    include_diff: bool = False,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    resolved = dataset_dir.resolve()
    write_dir = (output_dir or resolved).resolve()
    main_schema = resolved / "main_schema.jsonl"
    if not main_schema.exists():
        raise FileNotFoundError(main_schema)
    records = _records_with_rederived_v2_outcomes(load_records(main_schema))

    if dry_run:
        n_state = len(records)
        n_state_cue = len(records)
        n_transition = sum(len(record.candidate_actions) for record in records)
        n_policy = sum(1 for record in records if build_policy_preference_row(record) is not None)
        n_continuation = sum(
            1
            for record in records
            for action in record.candidate_actions
            if record.continuations.get(action) is not None and record.continuations[action].qa_overall_pass is True
        )
    else:
        write_dir.mkdir(parents=True, exist_ok=True)
        write_main_schema(records, write_dir / "main_schema.jsonl")
        n_state = export_state_inference(records, write_dir / "state_inference.jsonl")
        n_state_cue = export_state_inference_with_cue(records, write_dir / "state_inference_with_cue.jsonl")
        n_transition = export_transition_modeling(records, write_dir / "transition_modeling.jsonl")
        n_policy = export_policy_preference(records, write_dir / "policy_preference.jsonl")
        n_continuation = export_world_model_continuation(records, write_dir / "world_model_continuation.jsonl")

    stats_path = resolved / "_stats.json"
    stats = _read_json(stats_path) if stats_path.exists() else {}
    stats.update(
        {
            "schema_version": "v2.2",
            "action_space": "DialogueAct v2.2 + human-salesperson realization compatibility",
            "v2_2_reexported_at_utc": _now(),
            "rule_version": rules.RULE_VERSION,
            "n_state_inference_rows": n_state,
            "n_state_inference_with_cue_rows": n_state_cue,
            "n_transition_modeling_rows": n_transition,
            "n_policy_preference_rows": n_policy,
            "n_world_model_continuation_rows": n_continuation,
            "v2_2_fields": [
                "dialogue_act",
                "act_params.supporting_acts",
                "candidate_action_specs",
                "best_action_spec",
                "next_state_by_action_v2",
                "compatibility_tier",
                "legacy_mismatch_flags",
                "realization",
                "legacy_co_acts",
            ],
        }
    )
    if not dry_run:
        (write_dir / "_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "dataset_path": dataset_dir.as_posix(),
        "resolved_path": _display_path(resolved),
        "output_path": _display_path(write_dir),
        "dry_run": dry_run,
        "n_records": len(records),
        "n_state_inference_rows": n_state,
        "n_transition_modeling_rows": n_transition,
        "n_policy_preference_rows": n_policy,
        "n_world_model_continuation_rows": n_continuation,
    }
    if dry_run and include_diff:
        summary["planned_file_diffs"] = _planned_file_diffs(records, resolved, stats)
    return summary


def load_records(path: Path) -> list[MainSchemaRecord]:
    records: list[MainSchemaRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(MainSchemaRecord(**json.loads(line)))
    return records


def _records_with_rederived_v2_outcomes(records: list[MainSchemaRecord]) -> list[MainSchemaRecord]:
    return [_record_with_rederived_v2_outcomes(record) for record in records]


def _record_with_rederived_v2_outcomes(record: MainSchemaRecord) -> MainSchemaRecord:
    data = record.model_dump(mode="json")
    outcomes: dict[str, dict[str, Any]] = {}
    for action in record.candidate_actions:
        outcomes[action] = rules.derive_action_outcome(
            record.latent_state,
            record.aida_stage,
            record.persona.type,
            action,
            intent_tier=record.persona.intent_tier,
            visible_cues=record.observable_cues,
        )
    data["next_state_by_action"] = outcomes
    data["reward_by_action"] = {action: outcome["reward"] for action, outcome in outcomes.items()}
    data.pop("next_state_by_action_v2", None)
    return MainSchemaRecord(**data)


def write_main_schema(records: list[MainSchemaRecord], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(main_schema_record_payload(record), ensure_ascii=False, sort_keys=True) + "\n")


def _planned_file_diffs(records: list[MainSchemaRecord], resolved: Path, stats: dict[str, Any]) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="piwm_v2_2_reexport_") as tmp:
        tmp_dir = Path(tmp)
        write_main_schema(records, tmp_dir / "main_schema.jsonl")
        export_state_inference(records, tmp_dir / "state_inference.jsonl")
        export_state_inference_with_cue(records, tmp_dir / "state_inference_with_cue.jsonl")
        export_transition_modeling(records, tmp_dir / "transition_modeling.jsonl")
        export_policy_preference(records, tmp_dir / "policy_preference.jsonl")
        export_world_model_continuation(records, tmp_dir / "world_model_continuation.jsonl")
        (tmp_dir / "_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return [
            _file_diff_summary(resolved / name, tmp_dir / name)
            for name in [
                "main_schema.jsonl",
                "state_inference.jsonl",
                "state_inference_with_cue.jsonl",
                "transition_modeling.jsonl",
                "policy_preference.jsonl",
                "world_model_continuation.jsonl",
                "_stats.json",
            ]
        ]


def _file_diff_summary(old_path: Path, new_path: Path) -> dict[str, Any]:
    old_text = old_path.read_text(encoding="utf-8") if old_path.exists() else ""
    new_text = new_path.read_text(encoding="utf-8")
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=old_path.as_posix(), tofile=new_path.name))
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    return {
        "file": _display_path(old_path),
        "exists": old_path.exists(),
        "changed": old_text != new_text,
        "old_lines": len(old_lines),
        "new_lines": len(new_lines),
        "added_lines": added,
        "removed_lines": removed,
    }


def _reexport_diff_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# PIWM v2.2 Re-export Diff Preview",
        "",
        f"- Generated at UTC: `{payload['timestamp_utc']}`",
        f"- Dry run: `{payload['dry_run']}`",
        "",
        "This preview is computed in a temporary directory. It does not modify official JSONL files.",
        "",
        "| Dataset | File | Changed | Old Lines | New Lines | Added | Removed |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for dataset in payload["datasets"]:
        for item in dataset.get("planned_file_diffs", []):
            lines.append(
                "| {dataset} | `{file}` | {changed} | {old_lines} | {new_lines} | {added} | {removed} |".format(
                    dataset=dataset["dataset_path"],
                    file=item["file"],
                    changed="yes" if item["changed"] else "no",
                    old_lines=item["old_lines"],
                    new_lines=item["new_lines"],
                    added=item["added_lines"],
                    removed=item["removed_lines"],
                )
            )
    lines.append("")
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
