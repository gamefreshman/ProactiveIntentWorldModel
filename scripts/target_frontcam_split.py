"""Balanced 5-act split policy for PIWM-Target-Frontcam-v1."""

from __future__ import annotations

from collections import Counter
from typing import Any


OPERATIONAL_5ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")

TARGET_FRONT_CAM_5ACT_TEST_IDS_BY_ACT: dict[str, tuple[str, ...]] = {
    "Greet": ("piwm_718", "piwm_719", "piwm_720", "piwm_721", "piwm_789", "piwm_790"),
    "Elicit": ("piwm_700", "piwm_701", "piwm_703", "piwm_704", "piwm_705", "piwm_706"),
    "Inform": ("piwm_702", "piwm_707", "piwm_708", "piwm_712", "piwm_713", "piwm_714"),
    "Recommend": ("piwm_760", "piwm_762", "piwm_763", "piwm_764", "piwm_765", "piwm_766"),
    "Hold": ("piwm_810", "piwm_811", "piwm_812", "piwm_813", "piwm_816", "piwm_817"),
}

TARGET_FRONT_CAM_5ACT_TEST_IDS = frozenset(
    session_id
    for ids in TARGET_FRONT_CAM_5ACT_TEST_IDS_BY_ACT.values()
    for session_id in ids
)

EXPECTED_5ACT_TEST_COUNTS = {
    act: len(ids)
    for act, ids in TARGET_FRONT_CAM_5ACT_TEST_IDS_BY_ACT.items()
}


def split_for_target_frontcam_session(session_id: str) -> str:
    """Return the balanced target-frontcam split for a piwm source session id."""
    return "test" if session_id in TARGET_FRONT_CAM_5ACT_TEST_IDS else "train"


def best_act_from_row(row: dict[str, Any]) -> str:
    spec = row.get("best_action_spec")
    if isinstance(spec, dict) and spec.get("act"):
        return str(spec["act"])
    if row.get("dialogue_act"):
        return str(row["dialogue_act"])
    return "unknown"


def source_session_id_from_state_id(state_id: str) -> str:
    base = state_id.split("#", 1)[0]
    if base.startswith("target_"):
        base = base.removeprefix("target_")
    return base


def summarize_target_split(rows: list[dict[str, Any]]) -> dict[str, Any]:
    split_counts = Counter(str(row.get("split", "unknown")) for row in rows)
    best_by_split: dict[str, Counter[str]] = {"train": Counter(), "test": Counter()}
    for row in rows:
        split = str(row.get("split", "unknown"))
        if split in best_by_split:
            best_by_split[split][best_act_from_row(row)] += 1
    return {
        "split_counts": dict(sorted(split_counts.items())),
        "best_act_by_split": {
            split: dict(sorted(counter.items()))
            for split, counter in best_by_split.items()
        },
    }
