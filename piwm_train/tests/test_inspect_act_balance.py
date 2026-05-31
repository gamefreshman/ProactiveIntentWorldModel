from __future__ import annotations

import json
from pathlib import Path

from scripts.inspect_act_balance import inspect_path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_inspect_policy_preference_best_act_distribution(tmp_path: Path) -> None:
    input_path = tmp_path / "policy_preference.jsonl"
    _write_jsonl(
        input_path,
        [
            {"chosen_json": {"action_spec": {"act": "Inform"}}},
            {"chosen_json": {"dialogue_act": {"act": "Inform"}}},
            {"chosen_json": {"action_spec": {"act": "Recommend"}}},
            {"chosen_json": {}},
        ],
    )

    summary = inspect_path(input_path)

    assert summary == {
        "artifact": "act_balance",
        "input_path": str(input_path),
        "n_rows": 4,
        "best_act_counts": {"Inform": 2, "Recommend": 1},
        "inverse_freq_weights": {"Inform": 0.75, "Recommend": 1.5},
        "missing_best_act_rows": [4],
    }


def test_inspect_ms_swift_best_act_distribution(tmp_path: Path) -> None:
    input_path = tmp_path / "ms_swift.jsonl"
    _write_jsonl(
        input_path,
        [
            {"meta": {"best_act": "Hold"}},
            {
                "messages": [
                    {"role": "system", "content": ""},
                    {"role": "user", "content": ""},
                    {"role": "assistant", "content": "<chosen>Inform_abc</chosen>"},
                ],
                "meta": {"candidate_action_acts": {"Inform_abc": "Inform"}},
            },
            {
                "messages": [
                    {"role": "assistant", "content": "<chosen>Recommend_xyz</chosen>"},
                ],
                "meta": {"candidate_action_acts": {"Recommend_xyz": "Recommend"}},
            },
            {"messages": [{"role": "assistant", "content": "no chosen tag"}], "meta": {}},
        ],
    )

    summary = inspect_path(input_path)

    assert summary == {
        "artifact": "act_balance",
        "input_path": str(input_path),
        "n_rows": 4,
        "best_act_counts": {"Hold": 1, "Inform": 1, "Recommend": 1},
        "inverse_freq_weights": {"Hold": 1.0, "Inform": 1.0, "Recommend": 1.0},
        "missing_best_act_rows": [4],
    }
