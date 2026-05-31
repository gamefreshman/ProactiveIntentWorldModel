"""Build leakage-free two-stage PIWM training and eval entrypoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from piwm_data.migration.legacy_action_mapping import legacy_action_to_act_params_for_comparison
from piwm_train.data_collator import ActBalancing, SFTExample, user_intent_loss_weight
from piwm_train.ms_swift_adapter import build_ms_swift_record
from piwm_train.prompts import build_action_prompt_no_leak, build_next_state_prediction_prompt, build_user_intent_prompt
from piwm_train.targets import build_action_target, build_deliberation_target, build_user_intent_target


REPO_ROOT = Path(__file__).resolve().parents[1]
FIVE_ACTS = {"Greet", "Elicit", "Inform", "Recommend", "Hold"}
STAGE_CONDITIONED_ACT_ORDER = {
    "attention": ("Greet", "Elicit", "Inform", "Hold"),
    "interest": ("Elicit", "Inform", "Recommend", "Hold"),
    "desire": ("Inform", "Recommend", "Hold"),
    "action": ("Greet", "Recommend", "Hold"),
}
STAGE_CONDITIONED_ACTS = {stage: set(acts) for stage, acts in STAGE_CONDITIONED_ACT_ORDER.items()}
DEFAULT_GENERAL_DIR = Path("data/official/piwm_train_synth_v2")
DEFAULT_GENERAL_EVAL_DIR = Path("data/official/piwm_eval_qa_v1")
DEFAULT_TARGET_DIR = Path("data/official/piwm_target_v1")
DEFAULT_MS_SWIFT_DIR = Path("data/official/ms_swift")
DEFAULT_EVAL_DIR = Path("data/official/domain_specialization_eval_v2")
GREET_AUGMENTATION_DEFAULT_COUNT = 15
GREET_AUGMENTATION_VERSION = "v2"


def build_two_stage_artifacts(
    *,
    general_dir: Path,
    general_eval_dir: Path,
    target_dir: Path,
    ms_swift_dir: Path,
    eval_dir: Path,
    target_test_per_act: int = 6,
    act_balancing: ActBalancing = "none",
    greet_augmentation_count: int = 0,
    stage_conditioned_candidates: bool = True,
    target_repeat: int = 1,
) -> dict[str, Any]:
    root = REPO_ROOT
    general_dir = _resolve(general_dir)
    general_eval_dir = _resolve(general_eval_dir)
    target_dir = _resolve(target_dir)
    ms_swift_dir = _resolve(ms_swift_dir)
    eval_dir = _resolve(eval_dir)

    general_stage1 = _build_stage1_examples(general_dir)
    stage1_out = ms_swift_dir / "piwm_train_stage1_user_intent_v1.jsonl"
    stage1_summary = _write_ms_swift(general_stage1, stage1_out, root=root)

    target_main = _index_by_state(_read_jsonl(target_dir / "main_schema.jsonl"))
    target_state_rows = [
        _overlay_target_review_status(row, target_main)
        for row in _read_jsonl(target_dir / "state_inference.jsonl")
    ]
    target_state = _index_by_state(target_state_rows)
    target_transitions = [
        _overlay_target_review_status(row, target_main)
        for row in _read_jsonl(target_dir / "transition_modeling.jsonl")
    ]
    target_policy_rows = [
        _overlay_target_review_status(row, target_main)
        for row in _read_jsonl(target_dir / "policy_preference.jsonl")
    ]
    clean_policy_rows, excluded_counts = _clean_5act_policy_rows(
        target_policy_rows,
        stage_conditioned_candidates=stage_conditioned_candidates,
    )
    test_ids = _select_balanced_target_test_ids(clean_policy_rows, per_act=target_test_per_act)
    test_id_set = set(test_ids)
    train_policy_rows = [row for row in clean_policy_rows if row["state_id"] not in test_id_set]
    test_policy_rows = [row for row in clean_policy_rows if row["state_id"] in test_id_set]
    test_ids = [row["state_id"] for row in test_policy_rows]

    stage2_target = [_action_example(row) for row in train_policy_rows]
    stage2_out = ms_swift_dir / "piwm_train_stage2_target_5act_v1.jsonl"
    stage2_summary = _write_ms_swift(stage2_target, stage2_out, root=root)

    augmented_stage2_summary = None
    augmented_joint_summary = None
    augmentation_summary = None
    if greet_augmentation_count > 0:
        greet_aug_rows = _build_general_greet_aug_policy_rows(
            general_dir,
            count=greet_augmentation_count,
        )
        greet_aug_examples = [_action_example(row) for row in greet_aug_rows]
        augmented_stage2 = stage2_target + greet_aug_examples
        augmented_stage2_out = ms_swift_dir / f"piwm_train_stage2_target_5act_greet_aug_{GREET_AUGMENTATION_VERSION}.jsonl"
        augmented_stage2_summary = _write_ms_swift(augmented_stage2, augmented_stage2_out, root=root)
        augmented_joint_out = ms_swift_dir / f"piwm_train_stage1_plus_stage2_target_5act_greet_aug_{GREET_AUGMENTATION_VERSION}.jsonl"
        augmented_joint_summary = _write_rows(_read_jsonl(stage1_out) + _read_jsonl(augmented_stage2_out), augmented_joint_out)
        augmentation_summary = {
            "policy": f"stage2_prelaunch_general_greet_augmentation_{GREET_AUGMENTATION_VERSION}",
            "source": _display_path(general_dir / "state_inference.jsonl"),
            "count_requested": greet_augmentation_count,
            "count_written": len(greet_aug_examples),
            "source_aida_stage": "attention",
            "best_act": "Greet",
            "qa_status": "synthetic_augmented_unreviewed",
            "note": (
                "These rows are a Stage-2 prelaunch data patch for Greet coverage. "
                "They do not modify the canonical 71-row target split and are not "
                "project-lead QA-reviewed target-test rows."
            ),
        }

    joint_out = ms_swift_dir / "piwm_train_stage1_plus_stage2_target_5act_v1.jsonl"
    joint_summary = _write_rows(_read_jsonl(stage1_out) + _read_jsonl(stage2_out), joint_out)
    weighted_joint_summary = None
    if greet_augmentation_count > 0 and target_repeat > 1:
        augmented_stage2_rows = _read_jsonl(augmented_stage2_out)
        repeated_stage2 = augmented_stage2_rows * target_repeat
        weighted_joint_out = (
            ms_swift_dir
            / f"piwm_train_stage1_plus_stage2_target_5act_greet_aug_{GREET_AUGMENTATION_VERSION}_targetx{target_repeat}_v1.jsonl"
        )
        weighted_joint_summary = _write_rows(_read_jsonl(stage1_out) + repeated_stage2, weighted_joint_out)

    eval_dir.mkdir(parents=True, exist_ok=True)
    target_eval_user = [_user_intent_example(target_state[state_id]) for state_id in test_ids]
    target_eval_next = [_next_state_example(row) for row in _target_hold_transition_rows(target_transitions, test_ids)]
    target_eval_action = [_action_example(row) for row in test_policy_rows]
    target_eval_all = target_eval_user + target_eval_next + target_eval_action

    target_eval_paths = {
        "user_intent": eval_dir / "target_frontcam_5act_test_user_intent.jsonl",
        "next_state_prediction": eval_dir / "target_frontcam_5act_test_no_intervention_next_state.jsonl",
        "action_selection_5act": eval_dir / "target_frontcam_5act_test_action_selection.jsonl",
        "all": eval_dir / "target_frontcam_5act_test_all.jsonl",
    }
    target_eval_summaries = {
        "user_intent": _write_ms_swift(target_eval_user, target_eval_paths["user_intent"], root=root),
        "next_state_prediction": _write_ms_swift(target_eval_next, target_eval_paths["next_state_prediction"], root=root),
        "action_selection_5act": _write_ms_swift(target_eval_action, target_eval_paths["action_selection_5act"], root=root),
        "all": _write_ms_swift(target_eval_all, target_eval_paths["all"], root=root),
    }

    general_eval = _build_stage1_examples(general_eval_dir)
    general_eval_out = eval_dir / "general_qa_stage1_all.jsonl"
    general_eval_summary = _write_ms_swift(general_eval, general_eval_out, root=root)
    test_qa_status_counts = _qa_counts(test_ids, target_main)
    target_qa_red_line = (
        "The 5-act target test is balanced, video-backed, excludes Reassure as best or candidate action, and is project-lead QA-reviewed pass under the revised split."
        if test_qa_status_counts == {"qa_reviewed_pass": len(test_ids)}
        else "The 5-act target test is balanced, video-backed, and excludes Reassure as best or candidate action, but not all revised-split rows are QA-reviewed pass."
    )

    summary = {
        "artifact": "piwm_two_stage_training_and_eval_v1",
        "is_training_result": False,
        "stage1_train": stage1_summary,
        "stage2_target_5act_train": stage2_summary,
        "stage2_target_5act_greet_aug_train": augmented_stage2_summary,
        "joint_stage1_stage2_target_5act": joint_summary,
        "joint_stage1_stage2_target_5act_greet_aug": augmented_joint_summary,
        "joint_stage1_stage2_target_5act_greet_aug_weighted": weighted_joint_summary,
        "greet_augmentation": augmentation_summary,
        "target_5act_split": {
            "source_records": len(target_policy_rows),
            "official_split_counts": _split_counts(target_policy_rows),
            "official_best_act_counts": _act_counts(target_policy_rows),
            "clean_5act_records": len(clean_policy_rows),
            "train_records": len(train_policy_rows),
            "test_records": len(test_policy_rows),
            "filtered_records": excluded_counts,
            "stage_conditioned_candidates": stage_conditioned_candidates,
            "stage_conditioned_policy": {
                stage: sorted(acts)
                for stage, acts in sorted(STAGE_CONDITIONED_ACTS.items())
            },
            "test_per_act": target_test_per_act,
            "test_best_act_counts": _act_counts(test_policy_rows),
            "train_best_act_counts": _act_counts(train_policy_rows),
            "test_qa_status_counts": test_qa_status_counts,
            "stage2_act_balancing": act_balancing,
            "target_repeat": target_repeat,
            "accounting_chain": [
                "118 total target records",
                "-17 rows with best_act=Reassure",
                "-0 rows whose candidate set degenerates after removing Reassure candidates",
                "=101 clean 5-act records",
                "101 - 30 balanced test records = 71 Stage-2 target train records",
            ],
            "split_policy": "Use a strict clean 5-act subset for the main experiment. The operational acts are Greet/Elicit/Inform/Recommend/Hold. Exclude rows whose best act is Reassure, and filter Reassure from candidate lists. Select a balanced 30-record target test with 6 rows per operational act using seed-stable state_id ordering; use the remaining 71 clean records for Stage-2 target training.",
        },
        "target_5act_eval": target_eval_summaries,
        "general_stage1_eval": general_eval_summary,
        "evaluation_matrix": [
            {
                "eval_label": "general_on_general",
                "checkpoint": "checkpoint_general",
                "input_jsonl": _display_path(general_eval_out),
                "purpose": "Stage-1 user-intent and action-conditioned next-state health check.",
            },
            {
                "eval_label": "general_on_target",
                "checkpoint": "checkpoint_general",
                "input_jsonl": _display_path(target_eval_paths["all"]),
                "purpose": "Zero-shot transfer to target frontcam 5-act eval.",
            },
            {
                "eval_label": "target_specialized_on_target",
                "checkpoint": "checkpoint_target",
                "input_jsonl": _display_path(target_eval_paths["all"]),
                "purpose": "Target specialization gain under the 5-act metric.",
            },
            {
                "eval_label": "target_specialized_on_general",
                "checkpoint": "checkpoint_target",
                "input_jsonl": _display_path(general_eval_out),
                "purpose": "Catastrophic forgetting check after target specialization.",
            },
        ],
        "red_lines": [
            target_qa_red_line,
            "Do not report Reassure inside the main 5-act macro F1; use it only as a source/compatibility analysis boundary.",
            "Keep Recommend pressure params in action-selection outputs.",
            "The target action-selection prompt intentionally omits gold reward, risk, benefit, and predicted next state.",
            "Real-50 and salesperson-majority validation are planned external checks, not current completed results.",
        ],
    }
    summary_path = eval_dir / "two_stage_eval_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (eval_dir / "two_stage_eval_summary.md").write_text(_markdown(summary), encoding="utf-8")
    return summary


def _build_stage1_examples(data_dir: Path) -> list[SFTExample]:
    examples = [_user_intent_example(row) for row in _read_jsonl(data_dir / "state_inference.jsonl")]
    examples.extend(_next_state_example(row) for row in _read_jsonl(data_dir / "transition_modeling.jsonl"))
    return examples


def _user_intent_example(row: dict[str, Any]) -> SFTExample:
    intent_label = row.get("output", {}).get("intent")
    loss_weight = user_intent_loss_weight(intent_label)
    return SFTExample(
        task="user_intent",
        source_id=row["state_id"],
        prompt=build_user_intent_prompt(row),
        target=build_user_intent_target(row),
        images=list(row["input"].get("frames", [])),
        weight=loss_weight,
        meta={
            "split": row.get("meta", {}).get("split"),
            "qa_status": row.get("meta", {}).get("qa_status"),
            "human_review_status": row.get("meta", {}).get("human_review_status"),
            "viewpoint": row.get("meta", {}).get("viewpoint"),
            "stage": row.get("output", {}).get("aida_stage"),
            "intent_label": intent_label,
            "loss_weight": loss_weight,
            "loss_weight_policy": "a3plus_visual_intent_low_confidence",
        },
    )


def _next_state_example(row: dict[str, Any]) -> SFTExample:
    action_spec = row["input"].get("candidate_action_spec") or row["input"].get("candidate_dialogue_act") or {}
    return SFTExample(
        task="next_state_prediction",
        source_id=row["state_id"],
        prompt=build_next_state_prediction_prompt(row),
        target=build_deliberation_target(row),
        images=list(row["input"].get("frames", [])),
        meta={
            "parent_state_id": row.get("meta", {}).get("parent_state_id"),
            "candidate_action": row["input"].get("candidate_action"),
            "candidate_act": action_spec.get("act"),
            "candidate_params": action_spec.get("params"),
            "no_intervention_branch": action_spec.get("act") == "Hold"
            and (action_spec.get("params") or {}).get("mode") == "silent",
            "split": row.get("meta", {}).get("split"),
            "qa_status": row.get("meta", {}).get("qa_status"),
            "human_review_status": row.get("meta", {}).get("human_review_status"),
            "viewpoint": row.get("meta", {}).get("viewpoint"),
        },
    )


def _action_example(row: dict[str, Any]) -> SFTExample:
    return SFTExample(
        task="action_selection_5act",
        source_id=row["state_id"],
        prompt=build_action_prompt_no_leak(row, five_act_only=True),
        target=build_action_target(row, "chosen"),
        images=list(row.get("meta", {}).get("frames", [])),
        meta={
            "split": row.get("meta", {}).get("split"),
            "qa_status": row.get("meta", {}).get("qa_status"),
            "human_review_status": row.get("meta", {}).get("human_review_status"),
            "viewpoint": row.get("meta", {}).get("viewpoint"),
            "best_act": _best_act(row),
            "candidate_action_acts": _candidate_action_acts(row),
            "five_act_only": True,
            "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
            "augmentation_policy": row.get("meta", {}).get("augmentation_policy"),
            "augmented_from_state_id": row.get("meta", {}).get("augmented_from_state_id"),
        },
    )


def _build_general_greet_aug_policy_rows(general_dir: Path, *, count: int) -> list[dict[str, Any]]:
    """Create deterministic Stage-2 Greet augmentation rows from general attention states.

    The target-frontcam corpus is the only filmed target source with Greet labels,
    but the Stage-1 general corpus has no Greet best labels. This augmentation
    uses existing general-domain frames and creates low-leak action-selection
    examples where an opening Greet is the correct response to attention-stage
    approach/entry behavior. The rows are marked synthetic_augmented_unreviewed
    and are written only to the explicit *_greet_aug_* Stage-2 entrypoint.
    """
    if count <= 0:
        return []
    states = [
        row
        for row in _read_jsonl(general_dir / "state_inference.jsonl")
        if row.get("output", {}).get("aida_stage") == "attention"
    ]
    states = sorted(states, key=lambda row: row["state_id"])
    if len(states) < count:
        raise ValueError(f"not enough general attention rows for Greet augmentation: need {count}, found {len(states)}")
    return [_general_greet_aug_policy_row(row, index=index) for index, row in enumerate(states[:count], start=1)]


def _general_greet_aug_policy_row(state_row: dict[str, Any], *, index: int) -> dict[str, Any]:
    out = state_row["output"]
    visual = out.get("visual_state") or {}
    state_summary = {
        "aida_stage": "attention",
        "product_category": state_row.get("meta", {}).get("product_category", "general_retail"),
        "state_subtype": out.get("state_subtype") or out.get("current_state") or "approach_or_entry",
        "state": out.get("current_state") or out.get("state_subtype") or "approach_or_entry",
        "visual_state": {
            "summary": _greet_visible_summary(visual.get("summary", "")),
            "engagement_pattern": visual.get("engagement_pattern", visual.get("summary", "")),
            "gaze_and_attention": visual.get("gaze_and_attention", visual.get("gaze", "")),
            "body_and_hands": visual.get("body_and_hands", ""),
        },
        "intent": "no_clear_intent",
        "intent_tier": "exploring",
        "bdi": {
            "belief": "The shopper has just entered the selling zone and may need orientation.",
            "desire": "feel welcomed without being pressured",
            "intention": "decide whether to continue browsing or ask for help",
        },
        "proactive_score": 3,
        "candidate_action_specs": [
            {"act": "Greet", "params": {"phase": "open"}},
            {"act": "Elicit", "params": {"openness": "open", "slot": "need_focus"}},
            {"act": "Inform", "params": {"content_type": "attributes", "depth": "brief"}},
            {"act": "Hold", "params": {"mode": "silent"}},
        ],
        "best_action_spec": {"act": "Greet", "params": {"phase": "open"}},
        "persona_type": state_row.get("input", {}).get("persona_summary", "general_retail_shopper"),
        "observable_cues": ["approach_or_entry", "initial_attention"],
        "dialogue_act": "Greet",
        "act_params": {"phase": "open"},
    }
    blocks = [
        _action_block(
            "Greet_open_general_aug",
            "Greet",
            {"phase": "open"},
            "欢迎光临，您可以先随意看看，需要时我在。",
            "show_welcome_message",
            "warm",
            "soft_welcome",
            "智能导购终端以轻柔灯效和简短欢迎语完成开场，不施加购买压力。",
            "开场问候能在顾客刚进入服务区时建立可用性，同时保持低压力。",
        ),
        _action_block(
            "Elicit_need_focus_general_aug",
            "Elicit",
            {"openness": "open", "slot": "need_focus"},
            "您今天想先看价格、功能，还是适合什么场景？",
            "show_choice_bubbles",
            "curious",
            "soft_invitation",
            "智能导购终端给出轻量选择问题，引导顾客表达关注点。",
            "顾客刚进入服务区时直接追问需求可能偏早，问候更自然。",
        ),
        _action_block(
            "Inform_attributes_general_aug",
            "Inform",
            {"content_type": "attributes", "depth": "brief"},
            "需要时我可以帮您说明这几款的主要区别。",
            "show_comparison_or_details",
            "warm",
            "soft_breathing",
            "智能导购终端准备简短信息说明，但不主动展开长篇介绍。",
            "顾客尚处初始注意阶段，直接说明信息可能早于其明确兴趣。",
        ),
        _action_block(
            "Hold_silent_general_aug",
            "Hold",
            {"mode": "silent"},
            "",
            "idle_minimal",
            "silent",
            "maintain_current_soft_breathing",
            "智能导购终端保持静默和低亮度呼吸灯。",
            "完全静默能避免打扰，但会错过开场建立可用性的机会。",
        ),
    ]
    chosen = blocks[0]
    rejected = blocks[-1]
    return {
        "state_id": f"greet_aug_{index:03d}_{state_row['state_id']}",
        "chosen": chosen["action"],
        "rejected": rejected["action"],
        "chosen_json": chosen,
        "rejected_json": rejected,
        "reward_gap": 0.25,
        "meta": {
            "product_category": state_summary["product_category"],
            "split": "train",
            "viewpoint": state_row.get("meta", {}).get("viewpoint", "salesperson_observable"),
            "actor_profile": "general_retail_greet_augmentation",
            "frames": list(state_row.get("input", {}).get("frames", [])),
            "is_augmented": True,
            "augmentation_policy": f"stage2_prelaunch_general_greet_augmentation_{GREET_AUGMENTATION_VERSION}",
            "augmented_from_state_id": state_row["state_id"],
            "qa_status": "synthetic_augmented_unreviewed",
            "human_review_status": "not_reviewed",
            "state_summary": state_summary,
            "candidate_block": blocks,
        },
    }


def _greet_visible_summary(summary: str) -> str:
    if not summary:
        return "The shopper has just entered or approached the service area and shows initial attention."
    return f"{summary} This augmentation treats the scene as an initial approach/entry moment suitable for a low-pressure greeting."


def _action_block(
    action: str,
    act: str,
    params: dict[str, Any],
    utterance: str,
    screen_action: str,
    voice_style: str,
    light: str,
    physical_action: str,
    rationale: str,
) -> dict[str, Any]:
    digest = hashlib.sha1(f"{action}|{act}|{json.dumps(params, sort_keys=True)}".encode("utf-8")).hexdigest()[:12]
    label = f"{action}_{digest}"
    terminal = {
        "surface_text": utterance,
        "screen": {"action": screen_action, "cta": None},
        "voice_style": voice_style,
        "light": light,
        "cabinet_motion": None,
        "duration_ms": 3000 if act == "Greet" else 4000,
    }
    return {
        "action": label,
        "action_spec": {"act": act, "params": params},
        "dialogue_act": {"act": act, "params": params, "legacy_co_acts": []},
        "rationale": rationale,
        "action_realization": {
            "utterance": utterance or "（静默）",
            "physical_action": physical_action,
            "timing": "设备或导购在识别到当前顾客状态后立即触发。",
            "rationale": "stage2 prelaunch Greet augmentation",
        },
        "terminal_realization": terminal,
    }


def _target_hold_transition_rows(rows: list[dict[str, Any]], state_ids: list[str]) -> list[dict[str, Any]]:
    selected = set(state_ids)
    out = []
    for row in rows:
        if row.get("meta", {}).get("parent_state_id") not in selected:
            continue
        spec = row["input"].get("candidate_action_spec") or row["input"].get("candidate_dialogue_act") or {}
        if spec.get("act") == "Hold" and (spec.get("params") or {}).get("mode") == "silent":
            out.append(row)
    return sorted(out, key=lambda row: row.get("meta", {}).get("parent_state_id", ""))


def _clean_5act_policy_rows(
    rows: list[dict[str, Any]],
    *,
    stage_conditioned_candidates: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    clean_rows: list[dict[str, Any]] = []
    excluded = Counter(
        {
            "best_non_5act": 0,
            "candidate_non_5act": 0,
            "candidate_stage_conditioned_filtered": 0,
            "empty_5act_candidates": 0,
        }
    )
    for row in rows:
        best = _best_act(row)
        if best not in FIVE_ACTS:
            excluded["best_non_5act"] += 1
            continue
        updated = _filter_policy_row_candidates(row, stage_conditioned=stage_conditioned_candidates)
        original_candidate_count = len(row.get("meta", {}).get("candidate_block", []))
        filtered_candidate_count = len(updated.get("meta", {}).get("candidate_block", []))
        five_act_only_count = sum(
            1
            for item in row.get("meta", {}).get("candidate_block", [])
            if _block_act(item) in FIVE_ACTS
        )
        if original_candidate_count != five_act_only_count:
            excluded["candidate_non_5act"] += 1
        if five_act_only_count != filtered_candidate_count:
            excluded["candidate_stage_conditioned_filtered"] += 1
        if filtered_candidate_count == 0:
            excluded["empty_5act_candidates"] += 1
            continue
        clean_rows.append(updated)
    return clean_rows, dict(excluded)


def _select_balanced_target_test_ids(rows: list[dict[str, Any]], *, per_act: int) -> list[str]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_best_act(row)].append(row)

    selected: list[str] = []
    for act in ["Greet", "Elicit", "Inform", "Recommend", "Hold"]:
        candidates = sorted(grouped[act], key=lambda row: row["state_id"])
        if len(candidates) < per_act:
            raise ValueError(f"not enough clean target rows for {act}: need {per_act}, found {len(candidates)}")
        selected.extend(row["state_id"] for row in candidates[:per_act])
    return selected


def _clean_balanced_5act_policy_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    """Return clean 5-act train/test rows using the current balanced split."""
    clean_rows, excluded = _clean_5act_policy_rows(rows, stage_conditioned_candidates=True)
    test_ids = set(_select_balanced_target_test_ids(clean_rows, per_act=6))
    train_rows = [row for row in clean_rows if row["state_id"] not in test_ids]
    test_rows = [row for row in clean_rows if row["state_id"] in test_ids]
    return train_rows, test_rows, excluded


def _row_split(row: dict[str, Any]) -> str:
    return str(row.get("meta", {}).get("split") or row.get("split") or "")


def _best_act(row: dict[str, Any]) -> str:
    spec = row.get("chosen_json", {}).get("action_spec") or row.get("chosen_json", {}).get("dialogue_act") or {}
    return spec.get("act", "")


def _candidate_action_acts(row: dict[str, Any], *, five_act_filter: bool = True) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in row.get("meta", {}).get("candidate_block", []):
        action = item.get("action")
        act = _block_act(item)
        if five_act_filter and act not in FIVE_ACTS:
            continue
        if action and act:
            mapping[action] = act
    for side in ("chosen_json", "rejected_json"):
        block = row.get(side, {})
        action = block.get("action")
        act = _block_act(block)
        if five_act_filter and act not in FIVE_ACTS:
            continue
        if action and act:
            mapping.setdefault(action, act)
    for item in row.get("meta", {}).get("candidate_block", []):
        action = item.get("action")
        if action and action not in mapping:
            try:
                act = legacy_action_to_act_params_for_comparison(action)[0]
                if not five_act_filter or act in FIVE_ACTS:
                    mapping[action] = act
            except (KeyError, ValueError):
                pass
    return mapping


def _filter_policy_row_candidates(row: dict[str, Any], *, stage_conditioned: bool = True) -> dict[str, Any]:
    updated = dict(row)
    meta = dict(updated.get("meta") or {})
    stage = str((meta.get("state_summary") or {}).get("aida_stage") or "")
    if stage_conditioned and stage in STAGE_CONDITIONED_ACT_ORDER:
        meta["candidate_block"] = _stage_conditioned_candidate_block(row, stage)
    else:
        meta["candidate_block"] = [
            item
            for item in meta.get("candidate_block", [])
            if _block_act(item) in FIVE_ACTS
        ]
    updated["meta"] = meta
    return updated


def _stage_conditioned_candidate_block(row: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    by_act: dict[str, dict[str, Any]] = {}
    for item in list(row.get("meta", {}).get("candidate_block", [])) + [
        row.get("chosen_json", {}),
        row.get("rejected_json", {}),
    ]:
        act = _block_act(item)
        if act in FIVE_ACTS and act not in by_act:
            by_act[act] = item
    blocks: list[dict[str, Any]] = []
    for act in STAGE_CONDITIONED_ACT_ORDER[stage]:
        blocks.append(by_act.get(act) or _stage_conditioned_placeholder_block(row, stage, act))
    return blocks


def _stage_conditioned_placeholder_block(row: dict[str, Any], stage: str, act: str) -> dict[str, Any]:
    templates = {
        "Greet": {
            "params": {"phase": "close" if stage == "action" else "open"},
            "utterance": "欢迎光临，需要时我可以帮您。",
            "screen_action": "show_welcome_message",
            "voice_style": "warm",
            "light": "soft_welcome",
            "physical_action": "智能售货柜以简短欢迎语和柔和灯效提示可用性。",
            "rationale": "Stage-conditioned candidate supplied to keep the operational action set complete for this AIDA stage.",
        },
        "Elicit": {
            "params": {"openness": "open", "slot": "need_focus"},
            "utterance": "您想先了解价格、口味，还是适合什么场景？",
            "screen_action": "show_choice_bubbles",
            "voice_style": "curious",
            "light": "soft_invitation",
            "physical_action": "智能售货柜展示轻量选项，邀请顾客表达关注点。",
            "rationale": "Stage-conditioned candidate supplied to keep the operational action set complete for this AIDA stage.",
        },
        "Inform": {
            "params": {"content_type": "comparison", "depth": "brief"},
            "utterance": "这几款主要区别在口味、容量和价格，我可以帮您快速对比。",
            "screen_action": "show_comparison_or_details",
            "voice_style": "clear",
            "light": "soft_breathing",
            "physical_action": "智能售货柜展示简短对比信息，避免长篇推销。",
            "rationale": "Stage-conditioned candidate supplied to keep the operational action set complete for this AIDA stage.",
        },
        "Recommend": {
            "params": {"target": "item", "pressure": "soft"},
            "utterance": "如果您想省心选择，可以优先看这款更稳妥的。",
            "screen_action": "highlight_soft_recommendation",
            "voice_style": "calm",
            "light": "highlight_one_option_soft",
            "physical_action": "智能售货柜轻量高亮一个选项，并保留顾客选择空间。",
            "rationale": "Stage-conditioned candidate supplied to keep the operational action set complete for this AIDA stage.",
        },
        "Hold": {
            "params": {"mode": "silent"},
            "utterance": "",
            "screen_action": "idle_minimal",
            "voice_style": "silent",
            "light": "maintain_current_soft_breathing",
            "physical_action": "智能售货柜保持静默和低亮度待机，不主动打断顾客。",
            "rationale": "Stage-conditioned candidate supplied to keep the operational action set complete for this AIDA stage.",
        },
    }
    template = templates[act]
    return _action_block(
        f"{act}_{stage}_stage_conditioned_{row['state_id']}",
        act,
        template["params"],
        template["utterance"],
        template["screen_action"],
        template["voice_style"],
        template["light"],
        template["physical_action"],
        template["rationale"],
    )


def _overlay_target_review_status(row: dict[str, Any], main_by_state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Use target main_schema as the authority for revised-split QA status."""
    state_id = str(row.get("state_id", ""))
    meta = dict(row.get("meta") or {})
    base_state_id = str(meta.get("parent_state_id") or state_id.split("#", 1)[0])
    main = main_by_state.get(base_state_id)
    if not main:
        return row

    qa_status = main.get("qa_status")
    human_review_status = main.get("human_review_status")
    qa_review = main.get("qa_review") or {}
    if not qa_status and not human_review_status and not qa_review:
        return row

    updated = dict(row)
    if qa_status:
        meta["qa_status"] = qa_status
    if human_review_status:
        meta["human_review_status"] = human_review_status
    if qa_review:
        meta["qa_reviewer"] = qa_review.get("reviewer")
        meta["qa_reviewed_at"] = qa_review.get("reviewed_at")
        meta["qa_review_type"] = qa_review.get("review_type")
        meta["qa_warning_flags"] = list(qa_review.get("warning_flags") or [])

    state_summary = meta.get("state_summary")
    if isinstance(state_summary, dict):
        state_summary = dict(state_summary)
        if qa_status:
            state_summary["qa_status"] = qa_status
        if human_review_status:
            state_summary["human_review_status"] = human_review_status
        meta["state_summary"] = state_summary

    updated["meta"] = meta
    return updated


def _block_act(block: dict[str, Any]) -> str | None:
    spec = block.get("dialogue_act") or block.get("action_spec") or {}
    act = spec.get("act")
    return str(act) if act else None


def _qa_counts(state_ids: list[str], main_by_state: dict[str, dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(main_by_state.get(state_id, {}).get("qa_status", "unknown") for state_id in state_ids).items()))


def _act_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_best_act(row) for row in rows).items()))


def _split_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_row_split(row) for row in rows).items()))


def _index_by_state(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["state_id"]: row for row in rows}


def _write_ms_swift(examples: list[SFTExample], output_jsonl: Path, *, root: Path) -> dict[str, Any]:
    rows = [build_ms_swift_record(example, root=root, validate_images=False) for example in examples]
    summary = _write_rows(rows, output_jsonl)
    summary["image_path_count"] = sum(len(row.get("images", [])) for row in rows)
    return summary


def _write_rows(rows: list[dict[str, Any]], output_jsonl: Path) -> dict[str, Any]:
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")
    task_counts = dict(sorted(Counter(row.get("task", "unknown") for row in rows).items()))
    summary = {
        "artifact": "ms_swift_sft_jsonl",
        "is_training_result": False,
        "output_jsonl": _display_path(output_jsonl),
        "n_examples": len(rows),
        "task_counts": task_counts,
        "format": "ms-swift messages + images",
    }
    output_jsonl.with_name(f"{output_jsonl.stem}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _markdown(summary: dict[str, Any]) -> str:
    split = summary["target_5act_split"]
    lines = [
        "# PIWM Two-Stage Training and Eval v1",
        "",
        "This artifact implements the revised EMNLP data plan: leakage-free Stage-1 user intent modeling, "
        "5-act Stage-2 action modeling, and the balanced target-frontcam 5-act test split.",
        "",
        "## Training Entry Points",
        "",
        f"- Stage-1: `{summary['stage1_train']['output_jsonl']}` ({summary['stage1_train']['n_examples']} rows)",
        f"- Stage-2 target 5-act: `{summary['stage2_target_5act_train']['output_jsonl']}` ({summary['stage2_target_5act_train']['n_examples']} rows)",
        f"- Joint baseline: `{summary['joint_stage1_stage2_target_5act']['output_jsonl']}` ({summary['joint_stage1_stage2_target_5act']['n_examples']} rows)",
        "",
        "## Target 5-Act Split",
        "",
        f"- official_split_counts: `{split['official_split_counts']}`",
        f"- clean_5act_records: {split['clean_5act_records']}",
        f"- train_records: {split['train_records']}",
        f"- test_records: {split['test_records']}",
        f"- filtered_records: `{split['filtered_records']}`",
        f"- test_best_act_counts: `{split['test_best_act_counts']}`",
        f"- test_qa_status_counts: `{split['test_qa_status_counts']}`",
        "",
        "## Evaluation Matrix",
        "",
        "| Label | Checkpoint | Input | Purpose |",
        "|---|---|---|---|",
    ]
    for item in summary["evaluation_matrix"]:
        lines.append(f"| `{item['eval_label']}` | `{item['checkpoint']}` | `{item['input_jsonl']}` | {item['purpose']} |")
    lines.extend(["", "## Red Lines", ""])
    lines.extend(f"- {item}" for item in summary["red_lines"])
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--general-dir", type=Path, default=DEFAULT_GENERAL_DIR)
    parser.add_argument("--general-eval-dir", type=Path, default=DEFAULT_GENERAL_EVAL_DIR)
    parser.add_argument("--target-dir", type=Path, default=DEFAULT_TARGET_DIR)
    parser.add_argument("--ms-swift-dir", type=Path, default=DEFAULT_MS_SWIFT_DIR)
    parser.add_argument("--eval-dir", type=Path, default=DEFAULT_EVAL_DIR)
    parser.add_argument(
        "--target-test-per-act",
        type=int,
        default=6,
        help="Number of held-out target records per five-act class for the balanced target eval split.",
    )
    parser.add_argument(
        "--act-balancing",
        choices=["none", "inverse_freq", "oversample_minority"],
        default="none",
        help="Stage-2 target action-selection balancing mode.",
    )
    parser.add_argument(
        "--greet-augmentation-count",
        type=int,
        default=0,
        help=(
            "Write additional explicit *_greet_aug_* Stage-2 entrypoints with N "
            "general-domain attention-stage Greet examples. The canonical 71-row "
            "Stage-2 file is still written unchanged."
        ),
    )
    parser.add_argument(
        "--no-stage-conditioned-candidates",
        action="store_true",
        help="Disable AIDA-stage-conditioned candidate filtering for target action-selection rows.",
    )
    parser.add_argument(
        "--target-repeat",
        type=int,
        default=1,
        help="When Greet augmentation is enabled, write an additional joint entrypoint with the augmented target set repeated N times.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = build_two_stage_artifacts(
        general_dir=args.general_dir,
        general_eval_dir=args.general_eval_dir,
        target_dir=args.target_dir,
        ms_swift_dir=args.ms_swift_dir,
        eval_dir=args.eval_dir,
        target_test_per_act=args.target_test_per_act,
        act_balancing=args.act_balancing,
        greet_augmentation_count=args.greet_augmentation_count,
        stage_conditioned_candidates=not args.no_stage_conditioned_candidates,
        target_repeat=args.target_repeat,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
