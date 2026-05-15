import json
from pathlib import Path

import pytest

from piwm_data import rules
from piwm_data.exporters import main_schema_record_payload
from piwm_data.tests.test_exporters import make_record
from scripts import refresh_official_v2_exports


def test_refresh_official_v2_exports_can_write_independent_output_dir(tmp_path: Path):
    source = tmp_path / "source_dataset"
    target = tmp_path / "piwm_train_synth_v2"
    summary = tmp_path / "summary.json"
    source.mkdir()
    source_row = main_schema_record_payload(make_record())
    for outcome in source_row["next_state_by_action"].values():
        outcome["dialogue_act"] = None
        outcome["act_params"] = {}
        outcome["intent_tier"] = None
        outcome["risk_tags"] = []
        outcome["failure_mode"] = None
        outcome["outcome_type"] = "success"
    (source / "main_schema.jsonl").write_text(json.dumps(source_row, ensure_ascii=False) + "\n", encoding="utf-8")
    (source / "_stats.json").write_text("{}\n", encoding="utf-8")
    source_before = (source / "main_schema.jsonl").read_text(encoding="utf-8")

    exit_code = refresh_official_v2_exports.main(
        [
            "--dataset",
            str(source),
            "--output-dir",
            str(target),
            "--summary-out",
            str(summary),
        ]
    )

    assert exit_code == 0
    assert (source / "main_schema.jsonl").read_text(encoding="utf-8") == source_before
    assert (target / "main_schema.jsonl").exists()
    assert (target / "transition_modeling.jsonl").exists()
    assert summary.exists()
    target_row = json.loads((target / "main_schema.jsonl").read_text(encoding="utf-8").splitlines()[0])
    best_key = rules.action_spec_key("Inform", {"content_type": "comparison", "depth": "brief"})
    assert best_key in target_row["next_state_by_action_v2"]
    target_transition = json.loads((target / "transition_modeling.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert target_transition["output"]["dialogue_act"] in rules.DIALOGUE_ACTS
    assert target_transition["output"]["act_params"]
    summary_payload = json.loads(summary.read_text(encoding="utf-8"))
    assert summary_payload["datasets"][0]["output_path"] == target.as_posix()


def test_refresh_official_v2_exports_rejects_output_dir_with_multiple_sources(tmp_path: Path):
    with pytest.raises(SystemExit):
        refresh_official_v2_exports.main(
            [
                "--dataset",
                str(tmp_path / "one"),
                "--dataset",
                str(tmp_path / "two"),
                "--output-dir",
                str(tmp_path / "target"),
            ]
        )


def test_refresh_official_v2_exports_dry_run_output_diff_does_not_rewrite_source(tmp_path: Path):
    source = tmp_path / "source_dataset"
    diff_out = tmp_path / "diff.md"
    source.mkdir()
    source_row = main_schema_record_payload(make_record())
    (source / "main_schema.jsonl").write_text(json.dumps(source_row, ensure_ascii=False) + "\n", encoding="utf-8")
    (source / "_stats.json").write_text("{}\n", encoding="utf-8")
    source_before = (source / "main_schema.jsonl").read_text(encoding="utf-8")

    exit_code = refresh_official_v2_exports.main(
        [
            "--dataset",
            str(source),
            "--dry-run",
            "--output-diff",
            str(diff_out),
        ]
    )

    assert exit_code == 0
    assert (source / "main_schema.jsonl").read_text(encoding="utf-8") == source_before
    assert not (source / "state_inference.jsonl").exists()
    assert "PIWM v2.2 Re-export Diff Preview" in diff_out.read_text(encoding="utf-8")
