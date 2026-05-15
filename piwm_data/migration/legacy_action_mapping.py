"""v2.2 migration-only; delete in v2.3 after old archives are retired.

This module is the only place where old A1-A8 labels are converted into the
canonical v2 ``(act, params)`` action representation for migration and
compatibility comparison. New data generation must use ``act`` and ``params``
directly.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


LEGACY_ACTION_TO_ACT_PARAMS: dict[str, dict[str, Any]] = {
    "A1_silent_observe": {
        "act": "Hold",
        "params": {"mode": "silent"},
        "co_acts": [],
    },
    "A2_offer_value_comparison": {
        "act": "Inform",
        "params": {"content_type": "comparison", "depth": "brief"},
        "co_acts": [],
    },
    "A3_strong_recommend": {
        "act": "Recommend",
        "params": {"target": "item", "pressure": "firm"},
        "co_acts": [],
    },
    "A4_open_with_question": {
        "act": "Elicit",
        "params": {"openness": "open", "slot": "need_focus"},
        "co_acts": [],
    },
    "A5_provide_demonstration": {
        "act": "Inform",
        "params": {"content_type": "demo", "depth": "brief"},
        "co_acts": [],
    },
    "A6_acknowledge_and_wait": {
        "act": "Reassure",
        "params": {"focus": "time"},
        "co_acts": [{"act": "Hold", "params": {"mode": "ambient"}}],
    },
    "A7_disengage": {
        "act": "Hold",
        "params": {"mode": "ambient"},
        "co_acts": [],
    },
    "A8_offer_companion_invite": {
        "act": "Elicit",
        "params": {"openness": "open", "slot": "companion_opinion"},
        "co_acts": [],
    },
}

ACT_PARAMS_TO_LEGACY_ACTION: dict[tuple[str, tuple[tuple[str, Any], ...]], str] = {
    ("Hold", (("mode", "silent"),)): "A1_silent_observe",
    ("Inform", (("content_type", "comparison"), ("depth", "brief"))): "A2_offer_value_comparison",
    ("Recommend", (("pressure", "firm"), ("target", "item"))): "A3_strong_recommend",
    ("Elicit", (("openness", "open"), ("slot", "need_focus"))): "A4_open_with_question",
    ("Inform", (("content_type", "demo"), ("depth", "brief"))): "A5_provide_demonstration",
    ("Reassure", (("focus", "time"),)): "A6_acknowledge_and_wait",
    ("Hold", (("mode", "ambient"),)): "A7_disengage",
    ("Elicit", (("openness", "open"), ("slot", "companion_opinion"))): "A8_offer_companion_invite",
}


def legacy_to_v2(legacy_action: str) -> dict[str, Any]:
    """Return a copied v2 action spec for an old A1-A8 action label."""

    if legacy_action not in LEGACY_ACTION_TO_ACT_PARAMS:
        raise ValueError(f"unknown legacy action: {legacy_action}")
    return deepcopy(LEGACY_ACTION_TO_ACT_PARAMS[legacy_action])


def legacy_action_to_act_params_for_comparison(legacy_action: str) -> tuple[str, dict[str, Any]]:
    """Migration-only comparison helper for old archive labels."""

    spec = legacy_to_v2(legacy_action)
    return spec["act"], spec["params"]


def act_params_to_legacy_for_comparison(act: str, params: dict[str, Any]) -> str | None:
    """Return an old A-label only for exact migration equivalence checks."""

    comparable_params = {
        key: value
        for key, value in (params or {}).items()
        if key != "supporting_acts"
    }
    key = (act, tuple(sorted(comparable_params.items())))
    return ACT_PARAMS_TO_LEGACY_ACTION.get(key)
