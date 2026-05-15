from __future__ import annotations

import json
from pathlib import Path

from scripts.build_sft_ablation_variants import build_all_variants


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data/piwm_dataset_pilot30"


def test_build_ablation_variants_writes_expected_task_profiles(tmp_path: Path) -> None:
    index = build_all_variants(
        [DATA_DIR],
        tmp_path,
        root=ROOT,
        variants=["full_piwm_v2", "b1_perception_only", "b3_no_deliberation", "b4_no_continuation"],
        validate_images=False,
    )

    assert set(index["variants"]) == {
        "full_piwm_v2",
        "b1_perception_only",
        "b3_no_deliberation",
        "b4_no_continuation",
    }
    expected = {
        "full_piwm_v2": {"perception", "deliberation", "action_selection"},
        "b1_perception_only": {"perception"},
        "b3_no_deliberation": {"perception", "action_selection"},
        "b4_no_continuation": {"perception", "deliberation", "action_selection"},
    }
    for variant, tasks in expected.items():
        rows = [
            json.loads(line)
            for line in (tmp_path / variant / "ms_swift_sft.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        assert {row["task"] for row in rows} == tasks
        assert all(row["images"] for row in rows)
