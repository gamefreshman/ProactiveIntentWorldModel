"""Export PIWM main schema records into the three training JSONL formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from . import reaction_templates, rules
from .schemas import ActionRealization, MainSchemaRecord

WORTH_DOING_THRESHOLD = 0.0


def export_state_inference(
    records: Iterable[MainSchemaRecord],
    out: Path,
    include_observable_cues: bool = False,
) -> int:
    rows = [
        _state_inference_row(record, include_observable_cues=include_observable_cues)
        for record in records
    ]
    return _write_jsonl(rows, out)


def export_state_inference_with_cue(records: Iterable[MainSchemaRecord], out: Path) -> int:
    return export_state_inference(records, out, include_observable_cues=True)


def export_transition_modeling(records: Iterable[MainSchemaRecord], out: Path) -> int:
    rows: list[dict[str, Any]] = []
    for record in records:
        rows.extend(_transition_rows(record))
    return _write_jsonl(rows, out)


def export_policy_preference(records: Iterable[MainSchemaRecord], out: Path) -> int:
    rows = []
    for record in records:
        row = build_policy_preference_row(record)
        if row is not None:
            rows.append(row)
    return _write_jsonl(rows, out)


def export_world_model_continuation(records: Iterable[MainSchemaRecord], out: Path) -> int:
    rows: list[dict[str, Any]] = []
    for record in records:
        rows.extend(_world_model_continuation_rows(record))
    return _write_jsonl(rows, out)


def build_policy_preference_row(record: MainSchemaRecord) -> dict[str, Any] | None:
    if len(record.candidate_actions) < 2:
        return None

    best_action = record.best_action
    best_reward = record.reward_by_action[best_action]
    rejected_pool = [
        action
        for action in record.candidate_actions
        if record.reward_by_action[action] < best_reward
    ]
    if not rejected_pool:
        return None

    rejected = min(
        rejected_pool,
        key=lambda action: (
            record.reward_by_action[action],
            rules.ACTIONS.index(action),
        ),
    )
    rejected_reward = record.reward_by_action[rejected]
    return {
        "state_id": record.state_id,
        "prompt": _policy_prompt(record),
        "chosen": best_action,
        "rejected": rejected,
        "chosen_json": {
            "action": best_action,
            "dialogue_act": _act_spec(best_action),
            "rationale": _outcome_rationale(record, best_action),
            "action_realization": _action_realization(record, best_action).model_dump(),
            "terminal_realization": _terminal_realization(record, best_action),
        },
        "rejected_json": {
            "action": rejected,
            "dialogue_act": _act_spec(rejected),
            "rationale": _outcome_rationale(record, rejected),
            "action_realization": _action_realization(record, rejected).model_dump(),
            "terminal_realization": _terminal_realization(record, rejected),
        },
        "reward_gap": best_reward - rejected_reward,
        "meta": {
            "product_category": record.product_category,
            "split": record.split,
            "viewpoint": record.viewpoint,
            "frames": _frame_paths(record),
            "is_anchor": record.is_anchor,
            "rule_version": rules.RULE_VERSION,
            "state_summary": _state_summary(record),
            "candidate_block": _candidate_block(record),
        },
    }


def count_policy_preference_skipped_no_pair(records: Iterable[MainSchemaRecord]) -> int:
    return sum(1 for record in records if build_policy_preference_row(record) is None)


def _state_inference_row(record: MainSchemaRecord, include_observable_cues: bool = False) -> dict[str, Any]:
    input_payload: dict[str, Any] = {
        "frames": _frame_paths(record),
        "persona_summary": _persona_summary(record),
        "history_summary": None,
    }
    if include_observable_cues:
        input_payload["observable_cues"] = record.observable_cues
    return {
        "state_id": record.state_id,
        "input": input_payload,
        "output": {
            "visual_state": record.visual_state.model_dump(),
            "aida_stage": record.aida_stage,
            "state_subtype": record.latent_state,
            "current_state": record.latent_state,
            "intent": record.intent,
            "bdi": record.bdi.model_dump(),
            "proactive_score": record.proactive_score,
            "candidate_actions": record.candidate_actions,
            "best_action": record.best_action,
            "dialogue_act": record.dialogue_act,
            "act_params": record.act_params,
            "co_acts": record.co_acts,
            "best_action_realization": record.best_action_realization.model_dump(),
            "terminal_realization": record.realization.model_dump() if record.realization else None,
            "rationale": record.rationale,
        },
        "meta": {
            "product_category": record.product_category,
            "split": record.split,
            "viewpoint": record.viewpoint,
            "observable_cues": record.observable_cues,
            "visual_only_input": not include_observable_cues,
            "aida_stage": record.aida_stage,
            "deprecated_calibration_fields": ["proactive_score"],
            "is_anchor": record.is_anchor,
            "rule_version": rules.RULE_VERSION,
        },
    }


def _transition_rows(record: MainSchemaRecord) -> list[dict[str, Any]]:
    rows = []
    for action in record.candidate_actions:
        outcome = record.next_state_by_action[action]
        rows.append(
            {
                "state_id": f"{record.state_id}#{action}",
                "input": {
                    "frames": _frame_paths(record),
                    "current_state_summary": _state_summary(record),
                    "candidate_action": action,
                    "candidate_dialogue_act": _act_spec(action),
                    "candidate_action_realization": _action_realization(record, action).model_dump(),
                    "candidate_terminal_realization": _terminal_realization(record, action),
                },
                "output": {
                    "next_aida_stage": outcome.next_aida_stage,
                    "next_state_subtype": outcome.next_state,
                    "next_state": outcome.next_state,
                    "next_bdi": outcome.next_bdi.model_dump(),
                    "risk": outcome.risk,
                    "benefit": outcome.benefit,
                    "reward": outcome.reward,
                    "reward_components": outcome.reward_components.model_dump(),
                    "worth_doing": outcome.reward > WORTH_DOING_THRESHOLD,
                    "rationale": outcome.rationale,
                },
                "meta": {
                    "product_category": record.product_category,
                    "split": record.split,
                    "viewpoint": record.viewpoint,
                    "parent_state_id": record.state_id,
                    "is_anchor": record.is_anchor,
                    "rule_version": rules.RULE_VERSION,
                },
            }
        )
    return rows


def _world_model_continuation_rows(record: MainSchemaRecord) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for action in record.candidate_actions:
        continuation = record.continuations.get(action)
        if continuation is None or continuation.qa_overall_pass is not True:
            continue
        outcome = record.next_state_by_action[action]
        template = reaction_templates.REACTION_TEMPLATES[continuation.reaction_template_id]
        rows.append(
            {
                "state_id": continuation.continuation_id,
                "input": {
                    "current_frames": _frame_paths(record),
                    "candidate_action": action,
                    "current_state_summary": _state_summary(record),
                },
                "output": {
                    "next_aida_stage": outcome.next_aida_stage,
                    "next_state_subtype": outcome.next_state,
                    "next_state": outcome.next_state,
                    "reward": outcome.reward,
                    "risk": outcome.risk,
                    "benefit": outcome.benefit,
                    "reaction_caption": template["reaction_caption"],
                    "visible_reaction": reaction_templates.visible_reaction_axes(template),
                    "continuation_frames": [
                        frame.model_dump()
                        for frame in continuation.frames
                    ],
                },
                "meta": {
                    "product_category": record.product_category,
                    "split": record.split,
                    "viewpoint": record.viewpoint,
                    "continuation_role": continuation.continuation_role.value,
                    "reaction_template_id": continuation.reaction_template_id,
                    "parent_state_id": record.state_id,
                    "rule_version": rules.RULE_VERSION,
                },
            }
        )
    return rows


def _policy_prompt(record: MainSchemaRecord) -> str:
    candidates = ", ".join(record.candidate_actions)
    return (
        f"顾客状态：{record.latent_state}；"
        f"意图：{record.intent}；"
        f"视觉观察：{record.visual_state.summary}；"
        f"persona：{record.persona.type}；"
        f"候选动作：[{candidates}]。请选择最合适的动作并给出理由。"
    )


def _state_summary(record: MainSchemaRecord) -> dict[str, Any]:
    return {
        "aida_stage": record.aida_stage,
        "product_category": record.product_category,
        "state_subtype": record.latent_state,
        "state": record.latent_state,
        "visual_state": record.visual_state.model_dump(),
        "intent": record.intent,
        "bdi": record.bdi.model_dump(),
        "proactive_score": record.proactive_score,
        "persona_type": record.persona.type,
        "observable_cues": record.observable_cues,
        "dialogue_act": record.dialogue_act,
        "act_params": record.act_params,
        "co_acts": record.co_acts,
        "terminal_realization": record.realization.model_dump() if record.realization else None,
    }


def _candidate_block(record: MainSchemaRecord) -> list[dict[str, Any]]:
    return [
        {
            "action": action,
            "reward": record.reward_by_action[action],
            "next_state": record.next_state_by_action[action].next_state,
            "next_aida_stage": record.next_state_by_action[action].next_aida_stage,
            "risk": record.next_state_by_action[action].risk,
            "benefit": record.next_state_by_action[action].benefit,
            "dialogue_act": _act_spec(action),
            "action_realization": _action_realization(record, action).model_dump(),
            "terminal_realization": _terminal_realization(record, action),
        }
        for action in record.candidate_actions
    ]


def _persona_summary(record: MainSchemaRecord) -> str:
    if record.persona.description:
        return f"{record.persona.type}: {record.persona.description}"
    return record.persona.type


def _outcome_rationale(record: MainSchemaRecord, action: str) -> str | None:
    outcome = record.next_state_by_action[action]
    return outcome.rationale or record.rationale


def _action_realization(record: MainSchemaRecord, action: str) -> ActionRealization:
    if action == record.best_action:
        return record.best_action_realization
    return ActionRealization(
        **rules.derive_action_realization(
            action,
            record.latent_state,
            record.persona.type,
            record.product_category,
            record.observable_cues,
        )
    )


def _act_spec(action: str) -> dict[str, Any]:
    spec = rules.legacy_action_to_act(action)
    return {
        "act": spec["act"],
        "params": spec["params"],
        "co_acts": spec.get("co_acts", []),
    }


def _terminal_realization(record: MainSchemaRecord, action: str) -> dict[str, Any]:
    if action == record.best_action and record.realization is not None:
        return record.realization.model_dump()
    return rules.derive_terminal_realization(
        action,
        record.latent_state,
        record.persona.type,
        record.product_category,
        record.observable_cues,
    )


def _frame_paths(record: MainSchemaRecord) -> list[str]:
    return [frame.relative_path for frame in record.images]


def _write_jsonl(rows: list[dict[str, Any]], out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")
    return len(rows)
