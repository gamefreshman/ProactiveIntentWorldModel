from __future__ import annotations

import json
from pathlib import Path

from scripts.apply_target_frontcam_qa_review import apply_target_frontcam_qa_review
from scripts.build_piwm_target_promptready_index import build_piwm_target_promptready_index


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_apply_target_frontcam_qa_review_promotes_30_test_records(tmp_path: Path) -> None:
    main_rows = [
        {
            "state_id": f"target_piwm_{800 + index}",
            "source_session_id": f"piwm_{800 + index}",
            "split": "test",
            "qa_status": "synthetic_unreviewed",
            "best_action_spec": {"act": "Greet", "params": {"phase": "open"}},
        }
        for index in range(30)
    ]
    swift_rows = []
    for row in main_rows:
        state_id = row["state_id"]
        swift_rows.append({"source_id": state_id, "task": "perception", "meta": {"split": "test"}})
        swift_rows.append({"source_id": state_id, "task": "action_selection", "meta": {"split": "test"}})
        for action_index in range(4):
            swift_rows.append({"source_id": f"{state_id}#A{action_index}", "task": "deliberation", "meta": {"split": "test"}})

    main_schema = tmp_path / "main_schema.jsonl"
    ms_swift = tmp_path / "target.jsonl"
    qa_dir = tmp_path / "qa"
    eval_dir = tmp_path / "eval"
    _write_jsonl(main_schema, main_rows)
    _write_jsonl(ms_swift, swift_rows)

    summary = apply_target_frontcam_qa_review(main_schema, ms_swift, qa_dir, eval_dir)

    assert summary["reviewed_test_records"] == 30
    assert summary["qa_reviewed_pass_records"] == 30
    assert summary["qa_reviewed_fail_records"] == 0
    assert summary["reviewed_ms_swift_rows"] == 180
    assert (qa_dir / "main_schema_test_qa_reviewed_pass.jsonl").exists()
    assert (eval_dir / "target_frontcam_test_qa_reviewed_all.jsonl").exists()


def test_build_piwm_target_promptready_index_marks_video_pending(tmp_path: Path) -> None:
    piwm_root = tmp_path / "piwm"
    for name in ["labeled", "manifest", "seed", "prompts", "video"]:
        (piwm_root / "data" / name).mkdir(parents=True)
    record = {
        "session_id": "piwm_999",
        "persona": "周末路过商场、只是随便看看的普通消费者。",
        "aida_stage": "interest",
        "candidate_actions": ["hold_silent", "elicit_need_focus_open", "inform_attributes_brief", "inform_price_brief"],
        "best_action": "elicit_need_focus_open",
    }
    (piwm_root / "data" / "labeled" / "piwm_999.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    (piwm_root / "data" / "manifest" / "piwm_999.json").write_text("{}", encoding="utf-8")
    (piwm_root / "data" / "seed" / "piwm_999.txt").write_text("seed", encoding="utf-8")
    (piwm_root / "data" / "prompts" / "piwm_999.md").write_text("prompt", encoding="utf-8")

    summary = build_piwm_target_promptready_index(piwm_root, tmp_path / "official")

    assert summary["records"] == 1
    assert summary["video_backed_records"] == 0
    assert summary["video_pending_records"] == 1
    assert summary["best_dialogue_act_counts"] == {"Elicit": 1}
