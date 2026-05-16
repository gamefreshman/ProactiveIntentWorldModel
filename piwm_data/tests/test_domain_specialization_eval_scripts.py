from __future__ import annotations

import json
from pathlib import Path

from scripts.build_domain_specialization_eval_sets import build_domain_specialization_eval_sets
from scripts.summarize_domain_specialization_results import summarize_domain_specialization_results


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_build_domain_specialization_eval_sets_filters_target_test_split(tmp_path: Path) -> None:
    target = tmp_path / "target.jsonl"
    general = tmp_path / "general.jsonl"
    out = tmp_path / "eval"
    _write_jsonl(
        target,
        [
            {"task": "perception", "meta": {"split": "train"}, "source_id": "train_1"},
            {"task": "perception", "meta": {"split": "test"}, "source_id": "test_p"},
            {"task": "deliberation", "meta": {"split": "test"}, "source_id": "test_d"},
            {"task": "action_selection", "meta": {"split": "test"}, "source_id": "test_a"},
        ],
    )
    _write_jsonl(general, [{"task": "perception", "source_id": "general_1"}])

    summary = build_domain_specialization_eval_sets(target, general, out)

    assert summary["eval_sets"]["target_frontcam_test_all"]["rows"] == 3
    assert summary["eval_sets"]["target_frontcam_test_all"]["task_counts"] == {
        "action_selection": 1,
        "deliberation": 1,
        "perception": 1,
    }
    assert summary["eval_sets"]["general_qa_all"]["rows"] == 1
    assert (out / "target_frontcam_test_all.jsonl").read_text(encoding="utf-8").count("\n") == 3
    assert (out / "target_frontcam_test_perception.jsonl").read_text(encoding="utf-8").count("\n") == 1
    assert (out / "eval_sets_summary.md").exists()


def test_summarize_domain_specialization_results_reads_checkpoint_eval_json(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    (results_dir / "general_on_target.json").write_text(
        json.dumps(
            {
                "artifact": "ms_swift_checkpoint_eval",
                "eval_label": "general_on_target",
                "checkpoint": "checkpoint_general",
                "input_jsonl": "target_frontcam_test_all.jsonl",
                "n_records": 3,
                "task_counts": {"perception": 1, "deliberation": 1, "action_selection": 1},
                "parse_rate": 1.0,
                "metrics": {"stage_exact": 0.5},
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_domain_specialization_results(results_dir)

    assert summary["n_results"] == 1
    row = summary["results"][0]
    assert row["eval_label"] == "general_on_target"
    assert row["parse_rate"] == 1.0
    assert row["metrics"]["stage_exact"] == 0.5
