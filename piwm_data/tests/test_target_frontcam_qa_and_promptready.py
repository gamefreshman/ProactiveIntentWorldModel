from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.apply_target_frontcam_qa_review import apply_target_frontcam_qa_review
from scripts.build_two_stage_training_and_eval import (
    _candidate_action_acts as two_stage_candidate_action_acts,
    _clean_5act_policy_rows,
)
from scripts.build_piwm_target_promptready_index import build_piwm_target_promptready_index
from scripts.rebalance_target_frontcam_split import rebalance_target_frontcam_split
from scripts.target_frontcam_split import (
    EXPECTED_5ACT_TEST_COUNTS,
    TARGET_FRONT_CAM_5ACT_TEST_IDS,
    best_act_from_row,
    split_for_target_frontcam_session,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_pass_templates(qa_dir: Path, state_ids: list[str]) -> None:
    templates = qa_dir / "manual_review_templates"
    templates.mkdir(parents=True, exist_ok=True)
    checks = {
        "frontcam_view_pass": True,
        "customer_visible": True,
        "gaze_or_head_direction_visible": True,
        "body_posture_visible": True,
        "screen_or_cabinet_context_visible": True,
        "timeline_consistent_across_frames": True,
        "no_extra_subject_confusion": True,
        "label_matches_visual_evidence": True,
        "action_realization_reasonable": True,
    }
    for state_id in state_ids:
        (templates / f"{state_id}.qa_manual_review.json").write_text(
            json.dumps(
                {
                    "state_id": state_id,
                    "checks": checks,
                    "overall_pass": True,
                    "warning_flags": [],
                    "reviewer": "Project lead human QA",
                    "reviewed_at": "2026-05-19",
                    "review_type": "project_lead_human_review_after_5act_rebalance",
                    "notes": "Pass after 5-act split rebalance review.",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def test_target_frontcam_5act_split_policy_has_expected_distribution() -> None:
    assert len(TARGET_FRONT_CAM_5ACT_TEST_IDS) == 30
    assert split_for_target_frontcam_session("piwm_700") == "test"
    assert split_for_target_frontcam_session("piwm_791") == "train"
    assert EXPECTED_5ACT_TEST_COUNTS == {
        "Greet": 6,
        "Elicit": 6,
        "Inform": 6,
        "Recommend": 6,
        "Hold": 6,
    }


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
    main_rows.append(
        {
            "state_id": "target_piwm_train",
            "source_session_id": "piwm_train",
            "split": "train",
            "qa_status": "synthetic_unreviewed",
            "best_action_spec": {"act": "Hold", "params": {"mode": "silent"}},
        }
    )
    swift_rows = []
    for row in main_rows:
        state_id = row["state_id"]
        split = row["split"]
        swift_rows.append({"source_id": state_id, "task": "perception", "meta": {"split": split}})
        if split == "test":
            swift_rows.append({"source_id": state_id, "task": "action_selection", "meta": {"split": split}})
            for action_index in range(4):
                swift_rows.append({"source_id": f"{state_id}#A{action_index}", "task": "deliberation", "meta": {"split": split}})

    main_schema = tmp_path / "main_schema.jsonl"
    ms_swift = tmp_path / "target.jsonl"
    qa_dir = tmp_path / "qa"
    eval_dir = tmp_path / "eval"
    _write_jsonl(main_schema, main_rows)
    _write_jsonl(ms_swift, swift_rows)
    _write_pass_templates(qa_dir, [row["state_id"] for row in main_rows if row["split"] == "test"])

    summary = apply_target_frontcam_qa_review(main_schema, ms_swift, qa_dir, eval_dir, merge_target_data=True)

    assert summary["reviewed_test_records"] == 30
    assert summary["qa_reviewed_pass_records"] == 30
    assert summary["qa_reviewed_fail_records"] == 0
    assert summary["reviewed_ms_swift_rows"] == 180
    assert summary["merged_main_schema_rows"] == 31
    assert summary["merged_ms_swift_rows"] == 181
    assert (qa_dir / "main_schema_test_qa_reviewed_pass.jsonl").exists()
    assert (eval_dir / "target_frontcam_test_qa_reviewed_all.jsonl").exists()

    merged_main = [json.loads(line) for line in main_schema.read_text(encoding="utf-8").splitlines()]
    assert sum(row["qa_status"] == "qa_reviewed_pass" for row in merged_main) == 30
    assert sum(row["qa_status"] == "synthetic_unreviewed" for row in merged_main) == 1

    merged_swift = [json.loads(line) for line in ms_swift.read_text(encoding="utf-8").splitlines()]
    test_meta = [row["meta"] for row in merged_swift if row["meta"]["split"] == "test"]
    train_meta = [row["meta"] for row in merged_swift if row["meta"]["split"] == "train"]
    assert {meta["qa_status"] for meta in test_meta} == {"qa_reviewed_pass"}
    assert all("qa_status" not in meta for meta in train_meta)


def test_apply_target_frontcam_qa_review_requires_filled_manual_templates(tmp_path: Path) -> None:
    main_rows = [
        {
            "state_id": f"target_piwm_{800 + index}",
            "source_session_id": f"piwm_{800 + index}",
            "split": "test",
            "qa_status": "qa_pending_project_lead_review",
            "best_action_spec": {"act": "Inform", "params": {"content_type": "comparison"}},
        }
        for index in range(30)
    ]
    swift_rows = [{"source_id": row["state_id"], "task": "perception", "meta": {"split": "test"}} for row in main_rows]
    main_schema = tmp_path / "main_schema.jsonl"
    ms_swift = tmp_path / "target.jsonl"
    _write_jsonl(main_schema, main_rows)
    _write_jsonl(ms_swift, swift_rows)

    with pytest.raises(FileNotFoundError):
        apply_target_frontcam_qa_review(main_schema, ms_swift, tmp_path / "qa", tmp_path / "eval")


def test_rebalance_target_frontcam_split_writes_5act_test_and_pending_qa(tmp_path: Path) -> None:
    target_dir = tmp_path / "piwm_target_v1"
    target_dir.mkdir()
    main_rows = []
    for numeric_id in range(700, 818):
        session_id = f"piwm_{numeric_id}"
        row = {
            "state_id": f"target_{session_id}",
            "source_session_id": session_id,
            "split": "train",
            "qa_status": "synthetic_unreviewed",
            "best_action_spec": {"act": "Greet", "params": {"phase": "close"}},
        }
        main_rows.append(row)
    act_by_session = {
        "piwm_700": "Elicit",
        "piwm_701": "Elicit",
        "piwm_703": "Elicit",
        "piwm_704": "Elicit",
        "piwm_705": "Elicit",
        "piwm_706": "Elicit",
        "piwm_702": "Inform",
        "piwm_707": "Inform",
        "piwm_708": "Inform",
        "piwm_712": "Inform",
        "piwm_713": "Inform",
        "piwm_714": "Inform",
        "piwm_760": "Recommend",
        "piwm_762": "Recommend",
        "piwm_763": "Recommend",
        "piwm_764": "Recommend",
        "piwm_765": "Recommend",
        "piwm_766": "Recommend",
        "piwm_717": "Reassure",
        "piwm_771": "Reassure",
        "piwm_772": "Reassure",
        "piwm_773": "Reassure",
        "piwm_774": "Reassure",
        "piwm_775": "Reassure",
        "piwm_810": "Hold",
        "piwm_811": "Hold",
        "piwm_812": "Hold",
        "piwm_813": "Hold",
        "piwm_816": "Hold",
        "piwm_817": "Hold",
    }
    for row in main_rows:
        act = act_by_session.get(row["source_session_id"])
        if act:
            row["best_action_spec"] = {"act": act, "params": {}}
    _write_jsonl(target_dir / "main_schema.jsonl", main_rows)
    _write_jsonl(target_dir / "state_inference.jsonl", [{"state_id": "target_piwm_700", "meta": {"split": "train"}}])
    ms_swift = tmp_path / "target.jsonl"
    _write_jsonl(ms_swift, [{"source_id": row["state_id"], "task": "perception", "meta": {"split": "train"}} for row in main_rows])
    general_eval = tmp_path / "general.jsonl"
    _write_jsonl(general_eval, [{"task": "perception", "source_id": "general_1"}])

    summary = rebalance_target_frontcam_split(
        target_dir=target_dir,
        ms_swift=ms_swift,
        general_eval=general_eval,
        domain_eval_dir=tmp_path / "eval",
        qa_dir=tmp_path / "qa",
        repo_root=tmp_path,
        build_qa_packet=False,
    )

    assert summary["target_summary"]["split_counts"] == {"test": 30, "train": 88}
    assert summary["target_summary"]["best_act_by_split"]["test"] == EXPECTED_5ACT_TEST_COUNTS
    rebalanced = [json.loads(line) for line in (target_dir / "main_schema.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(best_act_from_row(row) != "Reassure" for row in rebalanced if row["split"] == "test")
    assert {row["qa_status"] for row in rebalanced if row["split"] == "test"} == {"qa_pending_project_lead_review"}


def test_two_stage_5act_rows_use_clean_balanced_subset_and_excludes_reassure_candidates() -> None:
    rows = [
        {
            "state_id": "target_piwm_790",
            "meta": {
                "split": "train",
                "candidate_block": [
                    {"action": "Inform_5ac252a82695", "action_spec": {"act": "Inform", "params": {}}},
                    {"action": "Greet_4f8123f9f15e", "action_spec": {"act": "Greet", "params": {"phase": "open"}}},
                ],
            },
            "chosen_json": {"action": "Inform_5ac252a82695", "action_spec": {"act": "Inform", "params": {}}},
            "rejected_json": {"action": "Greet_4f8123f9f15e", "action_spec": {"act": "Greet", "params": {"phase": "open"}}},
        },
        {
            "state_id": "target_piwm_791",
            "meta": {
                "split": "train",
                "candidate_block": [
                    {"action": "Greet_889a5021015d", "action_spec": {"act": "Greet", "params": {"phase": "close"}}},
                    {"action": "Hold_4be678e68ebf", "action_spec": {"act": "Hold", "params": {"mode": "silent"}}},
                ],
            },
            "chosen_json": {"action": "Greet_889a5021015d", "action_spec": {"act": "Greet", "params": {"phase": "close"}}},
            "rejected_json": {"action": "Hold_4be678e68ebf", "action_spec": {"act": "Hold", "params": {"mode": "silent"}}},
        },
        {
            "state_id": "target_piwm_794",
            "meta": {
                "split": "train",
                "candidate_block": [
                    {"action": "Reassure_dbe6016c33c1", "action_spec": {"act": "Reassure", "params": {"focus": "time"}}},
                    {"action": "Hold_4be678e68ebf", "action_spec": {"act": "Hold", "params": {"mode": "silent"}}},
                ],
            },
            "chosen_json": {"action": "Reassure_dbe6016c33c1", "action_spec": {"act": "Reassure", "params": {"focus": "time"}}},
            "rejected_json": {"action": "Hold_4be678e68ebf", "action_spec": {"act": "Hold", "params": {"mode": "silent"}}},
        },
        {
            "state_id": "target_piwm_700",
            "meta": {
                "split": "test",
                "candidate_block": [
                    {"action": "Elicit_1cf6762e4f2f", "action_spec": {"act": "Elicit", "params": {}}},
                    {"action": "Reassure_dbe6016c33c1", "action_spec": {"act": "Reassure", "params": {"focus": "time"}}},
                ],
            },
            "chosen_json": {"action": "Elicit_1cf6762e4f2f", "action_spec": {"act": "Elicit", "params": {}}},
            "rejected_json": {"action": "Reassure_dbe6016c33c1", "action_spec": {"act": "Reassure", "params": {"focus": "time"}}},
        },
        {
            "state_id": "target_piwm_empty",
            "meta": {
                "split": "train",
                "candidate_block": [
                    {"action": "Reassure_dbe6016c33c1", "action_spec": {"act": "Reassure", "params": {"focus": "time"}}},
                ],
            },
            "chosen_json": {"action": "Hold_4be678e68ebf", "action_spec": {"act": "Hold", "params": {"mode": "silent"}}},
            "rejected_json": {"action": "Reassure_dbe6016c33c1", "action_spec": {"act": "Reassure", "params": {"focus": "time"}}},
        },
    ]

    clean_rows, excluded = _clean_5act_policy_rows(rows)

    assert [row["state_id"] for row in clean_rows] == ["target_piwm_790", "target_piwm_791", "target_piwm_700"]
    assert excluded == {
        "best_non_5act": 1,
        "candidate_non_5act": 2,
        "candidate_stage_conditioned_filtered": 0,
        "empty_5act_candidates": 1,
    }
    assert two_stage_candidate_action_acts(clean_rows[0]) == {
        "Inform_5ac252a82695": "Inform",
        "Greet_4f8123f9f15e": "Greet",
    }
    assert "Reassure" not in set(two_stage_candidate_action_acts(clean_rows[-1]).values())


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
