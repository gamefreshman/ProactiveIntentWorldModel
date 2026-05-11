"""Refresh official PIWM JSONL exports with the v2 action/realization fields."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from piwm_data import rules
from piwm_data.exporters import (
    export_policy_preference,
    export_state_inference,
    export_state_inference_with_cue,
    export_transition_modeling,
    export_world_model_continuation,
)
from piwm_data.schemas import MainSchemaRecord


DEFAULT_DATASETS = [
    "data/official/piwm_train_synth_v1",
    "data/official/piwm_eval_qa_v1",
    "data/official/piwm_world_model_v1",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rewrite official PIWM dataset JSONL files with schema v2 fields.")
    parser.add_argument("--dataset", action="append", type=Path, help="Dataset directory; may be a symlink.")
    parser.add_argument("--summary-out", type=Path, default=Path("data/official/V2_REEXPORT_SUMMARY.json"))
    args = parser.parse_args(argv)

    dataset_paths = args.dataset or [Path(path) for path in DEFAULT_DATASETS]
    summaries = [refresh_dataset(path) for path in dataset_paths]
    payload = {
        "artifact": "piwm_official_v2_reexport_summary",
        "timestamp_utc": _now(),
        "schema_version": "v2",
        "rule_version": rules.RULE_VERSION,
        "datasets": summaries,
    }
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def refresh_dataset(dataset_dir: Path) -> dict[str, Any]:
    resolved = dataset_dir.resolve()
    main_schema = resolved / "main_schema.jsonl"
    if not main_schema.exists():
        raise FileNotFoundError(main_schema)
    records = load_records(main_schema)

    write_main_schema(records, main_schema)
    n_state = export_state_inference(records, resolved / "state_inference.jsonl")
    n_state_cue = export_state_inference_with_cue(records, resolved / "state_inference_with_cue.jsonl")
    n_transition = export_transition_modeling(records, resolved / "transition_modeling.jsonl")
    n_policy = export_policy_preference(records, resolved / "policy_preference.jsonl")
    n_continuation = export_world_model_continuation(records, resolved / "world_model_continuation.jsonl")

    stats_path = resolved / "_stats.json"
    stats = _read_json(stats_path) if stats_path.exists() else {}
    stats.update(
        {
            "schema_version": "v2",
            "action_space": "DialogueAct v2 + TerminalRealization",
            "v2_reexported_at_utc": _now(),
            "rule_version": rules.RULE_VERSION,
            "n_state_inference_rows": n_state,
            "n_state_inference_with_cue_rows": n_state_cue,
            "n_transition_modeling_rows": n_transition,
            "n_policy_preference_rows": n_policy,
            "n_world_model_continuation_rows": n_continuation,
            "v2_fields": ["dialogue_act", "act_params", "co_acts", "realization"],
        }
    )
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "dataset_path": dataset_dir.as_posix(),
        "resolved_path": resolved.as_posix(),
        "n_records": len(records),
        "n_state_inference_rows": n_state,
        "n_transition_modeling_rows": n_transition,
        "n_policy_preference_rows": n_policy,
        "n_world_model_continuation_rows": n_continuation,
    }


def load_records(path: Path) -> list[MainSchemaRecord]:
    records: list[MainSchemaRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(MainSchemaRecord(**json.loads(line)))
    return records


def write_main_schema(records: list[MainSchemaRecord], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False, sort_keys=True) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
