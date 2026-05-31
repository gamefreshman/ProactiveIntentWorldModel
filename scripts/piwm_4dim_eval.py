"""Prepare and summarize PIWM 4-dimension target-test evaluation artifacts."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
RAW_DIR = REPO_ROOT / "reports" / "4dim_eval_raw_20260524"
REPORT_PATH = REPO_ROOT / "reports" / "2026-05-24_pi_4dim_evaluation.md"
MATERIALS_PATH = REPO_ROOT / "reports" / "2026-05-24_paper_writing_materials.md"

FIVE_ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")
AIDA_STAGES = ("attention", "interest", "desire", "action")
STAGE_CONDITIONED = {
    "attention": ("Greet", "Elicit", "Inform", "Hold"),
    "interest": ("Elicit", "Inform", "Recommend", "Hold"),
    "desire": ("Inform", "Recommend", "Hold"),
    "action": ("Greet", "Recommend", "Hold"),
}
LOW_CONFIDENCE_INTENTS = {"seek_reassurance", "negotiate_price"}
REMOTE_ROOT = "/root/lanyun-fs/ProactiveIntentWorldModel"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def tag_value(text: str, tag: str) -> str | None:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text or "", flags=re.S)
    return match.group(1).strip() if match else None


def prepare_inputs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    user_rows = read_jsonl(REPO_ROOT / "data/official/domain_specialization_eval_v2/target_frontcam_5act_test_user_intent.jsonl")
    action_rows = read_jsonl(REPO_ROOT / "data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl")
    transition_rows = read_jsonl(REPO_ROOT / "data/official/piwm_target_v1/transition_modeling.jsonl")

    transition_by_parent_action: dict[tuple[str, str], dict[str, Any]] = {}
    for row in transition_rows:
        parent = row.get("meta", {}).get("parent_state_id")
        action = row.get("input", {}).get("candidate_action")
        if parent and action:
            transition_by_parent_action[(parent, action)] = row

    covered: list[dict[str, Any]] = []
    unscored: list[dict[str, Any]] = []
    for action_row in action_rows:
        scene_id = action_row["source_id"]
        mapping = action_row.get("meta", {}).get("candidate_action_acts", {})
        for candidate_action, act in mapping.items():
            transition = transition_by_parent_action.get((scene_id, candidate_action))
            if transition is None:
                unscored.append(
                    {
                        "scene_id": scene_id,
                        "candidate_action": candidate_action,
                        "candidate_act": act,
                        "reason": "stage-conditioned placeholder candidate has no exact transition_modeling gold",
                    }
                )
                continue
            covered.append(_transition_to_ms_swift(transition))

    write_jsonl(RAW_DIR / "target_user_intent.jsonl", user_rows)
    write_jsonl(RAW_DIR / "target_action_selection.jsonl", action_rows)
    write_jsonl(RAW_DIR / "next_state_covered80.jsonl", covered)
    write_jsonl(RAW_DIR / "next_state_unscored27.jsonl", unscored)
    write_jsonl(RAW_DIR / "target_user_intent.server.jsonl", [_server_row(row) for row in user_rows])
    write_jsonl(RAW_DIR / "target_action_selection.server.jsonl", [_server_row(row) for row in action_rows])
    write_jsonl(RAW_DIR / "next_state_covered80.server.jsonl", [_server_row(row) for row in covered])
    all_scored = user_rows + covered + action_rows
    user_next_scored = user_rows + covered
    write_jsonl(RAW_DIR / "target_all_4dim_scored.jsonl", all_scored)
    write_jsonl(RAW_DIR / "target_all_4dim_scored.server.jsonl", [_server_row(row) for row in all_scored])
    write_jsonl(RAW_DIR / "target_user_next_scored.jsonl", user_next_scored)
    write_jsonl(RAW_DIR / "target_user_next_scored.server.jsonl", [_server_row(row) for row in user_next_scored])

    manifest = {
        "artifact": "piwm_4dim_eval_inputs",
        "five_act": list(FIVE_ACTS),
        "reassure_operational_count": _count_reassure(user_rows + action_rows + covered),
        "user_intent_rows": len(user_rows),
        "action_selection_rows": len(action_rows),
        "stage_conditioned_candidate_total": len(covered) + len(unscored),
        "next_state_scored_rows": len(covered),
        "next_state_unscored_rows": len(unscored),
        "next_state_unscored_by_act": dict(sorted(Counter(row["candidate_act"] for row in unscored).items())),
        "server_inputs": {
            "user_intent": str(RAW_DIR / "target_user_intent.server.jsonl"),
            "next_state": str(RAW_DIR / "next_state_covered80.server.jsonl"),
            "action_selection": str(RAW_DIR / "target_action_selection.server.jsonl"),
            "all_scored": str(RAW_DIR / "target_all_4dim_scored.server.jsonl"),
            "user_next_scored": str(RAW_DIR / "target_user_next_scored.server.jsonl"),
        },
    }
    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def _transition_to_ms_swift(row: dict[str, Any]) -> dict[str, Any]:
    from piwm_train.data_collator import SFTExample
    from piwm_train.ms_swift_adapter import build_ms_swift_record
    from piwm_train.prompts import build_next_state_prediction_prompt
    from piwm_train.targets import build_deliberation_target

    spec = row["input"].get("candidate_action_spec") or row["input"].get("candidate_dialogue_act") or {}
    example = SFTExample(
        task="next_state_prediction",
        source_id=row["state_id"],
        prompt=build_next_state_prediction_prompt(row),
        target=build_deliberation_target(row),
        images=list(row["input"].get("frames", [])),
        meta={
            "parent_state_id": row.get("meta", {}).get("parent_state_id"),
            "candidate_action": row["input"].get("candidate_action"),
            "candidate_act": spec.get("act"),
            "candidate_params": spec.get("params"),
            "qa_status": row.get("meta", {}).get("qa_status"),
            "human_review_status": row.get("meta", {}).get("human_review_status"),
            "viewpoint": row.get("meta", {}).get("viewpoint"),
        },
    )
    return build_ms_swift_record(example, root=REPO_ROOT, validate_images=False)


def _server_row(row: dict[str, Any]) -> dict[str, Any]:
    cloned = json.loads(json.dumps(row, ensure_ascii=False))
    prefix = str(REPO_ROOT)
    cloned["images"] = [
        str(path).replace(prefix, REMOTE_ROOT)
        for path in cloned.get("images", [])
    ]
    return cloned


def _count_reassure(rows: list[dict[str, Any]]) -> int:
    text = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    return len(re.findall(r"\bReassure\b", text))


def summarize() -> None:
    manifest = json.loads((RAW_DIR / "manifest.json").read_text(encoding="utf-8"))
    eval_inputs = {
        "user_intent": read_jsonl(RAW_DIR / "target_user_intent.jsonl"),
        "next_state": read_jsonl(RAW_DIR / "next_state_covered80.jsonl"),
        "action": read_jsonl(RAW_DIR / "target_action_selection.jsonl"),
    }
    models = {
        "simple_baseline": _simple_baseline(eval_inputs),
        "base_qwen25vl7b": _load_model_metrics("base_qwen25vl7b", eval_inputs),
        "customer_state_effect_only": _load_model_metrics("customer_state_effect_only", eval_inputs),
        "piwm_main": _load_model_metrics("piwm_main", eval_inputs),
    }
    report = _render_report(manifest, models)
    REPORT_PATH.write_text(report, encoding="utf-8")
    update_paper_materials()
    print(str(REPORT_PATH))


def _load_eval_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_model_metrics(prefix: str, eval_inputs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    all_tasks = _load_eval_json(RAW_DIR / f"{prefix}_all_tasks.json")
    user_next = _load_eval_json(RAW_DIR / f"{prefix}_user_next.json")
    user = _load_eval_json(RAW_DIR / f"{prefix}_user_intent.json") or _filter_result(all_tasks or user_next, {"user_intent"})
    next_state = _load_eval_json(RAW_DIR / f"{prefix}_next_state.json") or _filter_result(all_tasks or user_next, {"next_state_prediction"})
    action = _load_eval_json(RAW_DIR / f"{prefix}_action_selection.json") or _filter_result(all_tasks, {"action_selection_5act"})
    return {
        "user_intent": _score_user_intent(user, eval_inputs["user_intent"]) if user else None,
        "next_state": _score_next_state(next_state, eval_inputs["next_state"]) if next_state else None,
        "action": _score_action(action, eval_inputs["action"]) if action else None,
        "raw_available": {
            "user_intent": user is not None,
            "next_state": next_state is not None,
            "action": action is not None,
        },
    }


def _filter_result(result: dict[str, Any] | None, tasks: set[str]) -> dict[str, Any] | None:
    if result is None:
        return None
    outputs = [row for row in result.get("outputs", []) if row.get("task") in tasks]
    if not outputs:
        return None
    cloned = dict(result)
    cloned["outputs"] = outputs
    cloned["n_records"] = len(outputs)
    cloned["parse_success"] = sum(1 for row in outputs if row.get("parse_ok"))
    cloned["parse_rate"] = cloned["parse_success"] / len(outputs) if outputs else None
    cloned["task_counts"] = dict(sorted(Counter(row.get("task") for row in outputs).items()))
    return cloned


def _simple_baseline(eval_inputs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    stage_gold = [tag_value(row["messages"][2]["content"], "stage") for row in eval_inputs["user_intent"]]
    intent_gold = [tag_value(row["messages"][2]["content"], "intent_label") for row in eval_inputs["user_intent"]]
    next_gold = [tag_value(row["messages"][2]["content"], "next_stage") for row in eval_inputs["next_state"]]
    action_gold = [_gold_act(row) for row in eval_inputs["action"]]
    return {
        "user_intent": {
            "parse_rate": 1.0,
            "stage": _baseline_bundle(stage_gold, list(AIDA_STAGES)),
            "intent": _baseline_bundle(intent_gold, sorted(set(intent_gold))),
            "intent_core": _baseline_bundle([x for x in intent_gold if x not in LOW_CONFIDENCE_INTENTS], sorted({x for x in intent_gold if x not in LOW_CONFIDENCE_INTENTS})),
        },
        "next_state": {
            "parse_rate": 1.0,
            "next_stage": _baseline_bundle(next_gold, list(AIDA_STAGES)),
            "reward_mae": None,
        },
        "action": {
            "parse_rate": 1.0,
            "action": {
                "macro_f1": 0.414,
                "strict_macro_f1": 0.414,
                "per_class": {},
                "note": "random-candidate baseline from existing action-selection baseline report",
            },
            "always_x_macro_f1": 0.067,
        },
    }


def _baseline_bundle(gold: list[str | None], labels: list[str]) -> dict[str, Any]:
    gold = [g for g in gold if g is not None]
    majority = Counter(gold).most_common(1)[0][0] if gold else None
    majority_pairs = [(majority, g) for g in gold] if majority else []
    uniform_expected = _uniform_random_macro_f1(gold, labels)
    return {
        "majority_label": majority,
        "majority_macro_f1": _macro_f1(majority_pairs, labels),
        "uniform_random_expected_macro_f1": uniform_expected,
        "support": dict(sorted(Counter(gold).items())),
    }


def _uniform_random_macro_f1(gold: list[str], labels: list[str]) -> float | None:
    if not gold or not labels:
        return None
    n = len(gold)
    k = len(labels)
    f1s = []
    for label in labels:
        gold_rate = sum(1 for g in gold if g == label) / n
        pred_rate = 1 / k
        if gold_rate + pred_rate == 0:
            f1s.append(0.0)
        else:
            f1s.append(2 * pred_rate * gold_rate / (pred_rate + gold_rate))
    return sum(f1s) / len(f1s)


def _score_user_intent(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    stage_pairs = []
    intent_pairs = []
    strict_stage_pairs = []
    strict_intent_pairs = []
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold_stage = tag_value(row["messages"][2]["content"], "stage")
        gold_intent = tag_value(row["messages"][2]["content"], "intent_label")
        if out.get("parse_ok"):
            parsed = out.get("parsed") or {}
            stage_pairs.append((parsed.get("aida_stage"), gold_stage))
            intent_pairs.append((parsed.get("intent_label"), gold_intent))
            strict_stage_pairs.append((parsed.get("aida_stage"), gold_stage))
            strict_intent_pairs.append((parsed.get("intent_label"), gold_intent))
        else:
            strict_stage_pairs.append(("__parse_error__", gold_stage))
            strict_intent_pairs.append(("__parse_error__", gold_intent))
    core_pairs = [(p, g) for p, g in intent_pairs if g not in LOW_CONFIDENCE_INTENTS]
    strict_core_pairs = [(p, g) for p, g in strict_intent_pairs if g not in LOW_CONFIDENCE_INTENTS]
    full_labels = sorted({g for _, g in intent_pairs if g})
    core_labels = sorted({g for _, g in core_pairs if g})
    return {
        "parse_rate": result.get("parse_rate"),
        "stage": _classification_metrics(stage_pairs, list(AIDA_STAGES)),
        "stage_strict": _classification_metrics(strict_stage_pairs, list(AIDA_STAGES)),
        "intent": _classification_metrics(intent_pairs, full_labels),
        "intent_strict": _classification_metrics(strict_intent_pairs, full_labels),
        "intent_core": _classification_metrics(core_pairs, core_labels),
        "intent_core_strict": _classification_metrics(strict_core_pairs, core_labels),
        "outputs_by_scene": _scene_output_map(result, "user_intent"),
    }


def _score_next_state(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    pairs = []
    strict_pairs = []
    reward_errors = []
    by_act: dict[str, list[tuple[str, str]]] = defaultdict(list)
    by_act_reward: dict[str, list[float]] = defaultdict(list)
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold_stage = tag_value(row["messages"][2]["content"], "next_stage")
        gold_reward = _float_or_none(tag_value(row["messages"][2]["content"], "reward"))
        act = row.get("meta", {}).get("candidate_act")
        if out.get("parse_ok"):
            parsed = out.get("parsed") or {}
            pred_stage = parsed.get("next_aida_stage")
            pairs.append((pred_stage, gold_stage))
            strict_pairs.append((pred_stage, gold_stage))
            if act:
                by_act[act].append((pred_stage, gold_stage))
            pred_reward = _float_or_none(parsed.get("reward"))
            if pred_reward is not None and gold_reward is not None:
                err = abs(pred_reward - gold_reward)
                reward_errors.append(err)
                if act:
                    by_act_reward[act].append(err)
        else:
            strict_pairs.append(("__parse_error__", gold_stage))
    return {
        "parse_rate": result.get("parse_rate"),
        "next_stage": _classification_metrics(pairs, list(AIDA_STAGES)),
        "next_stage_strict": _classification_metrics(strict_pairs, list(AIDA_STAGES)),
        "reward_mae": sum(reward_errors) / len(reward_errors) if reward_errors else None,
        "by_candidate_act": {
            act: {
                **_classification_metrics(items, list(AIDA_STAGES)),
                "reward_mae": (sum(by_act_reward[act]) / len(by_act_reward[act]) if by_act_reward.get(act) else None),
                "n": len(items),
            }
            for act, items in sorted(by_act.items())
        },
        "outputs_by_candidate": _candidate_output_map(result),
    }


def _score_action(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    pairs = []
    strict_pairs = []
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold = _gold_act(row)
        if out.get("parse_ok"):
            mapping = row.get("meta", {}).get("candidate_action_acts", {})
            pred = _action_to_act((out.get("parsed") or {}).get("chosen"), mapping)
            pairs.append((pred, gold))
            strict_pairs.append((pred, gold))
        else:
            strict_pairs.append(("__parse_error__", gold))
    return {
        "parse_rate": result.get("parse_rate"),
        "action": _classification_metrics(pairs, list(FIVE_ACTS)),
        "action_strict": _classification_metrics(strict_pairs, list(FIVE_ACTS)),
        "outputs_by_scene": _scene_output_map(result, "action"),
    }


def _classification_metrics(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> dict[str, Any]:
    clean = [(p, g) for p, g in pairs if g is not None]
    return {
        "macro_f1": _macro_f1(clean, labels),
        "accuracy": _accuracy(clean),
        "per_class": {
            label: _per_label(clean, label)
            for label in labels
        },
        "support": dict(sorted(Counter(g for _, g in clean).items())),
        "pred_count": dict(sorted(Counter(p for p, _ in clean if p is not None).items())),
        "n": len(clean),
    }


def _macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(_per_label(pairs, label)["f1"] for label in labels) / len(labels)


def _accuracy(pairs: list[tuple[str | None, str | None]]) -> float | None:
    if not pairs:
        return None
    return sum(1 for pred, gold in pairs if pred == gold) / len(pairs)


def _per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }


def _gold_act(row: dict[str, Any]) -> str | None:
    chosen = tag_value(row["messages"][2]["content"], "chosen")
    return _action_to_act(chosen, row.get("meta", {}).get("candidate_action_acts", {}))


def _action_to_act(action: str | None, mapping: dict[str, str]) -> str | None:
    if action is None:
        return None
    if action in mapping:
        return mapping[action]
    if "_" in action:
        prefix = action.split("_", 1)[0]
        if prefix in FIVE_ACTS:
            return prefix
    return action


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _scene_output_map(result: dict[str, Any], task: str) -> dict[str, dict[str, Any]]:
    out = {}
    for item in result.get("outputs", []):
        scene_id = str(item.get("source_id", "")).split("#", 1)[0]
        out[scene_id] = {
            "parse_ok": bool(item.get("parse_ok")),
            "parsed": item.get("parsed") or {},
            "prediction": item.get("prediction"),
            "task": task,
        }
    return out


def _candidate_output_map(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for item in result.get("outputs", []):
        out[item.get("source_id")] = {
            "parse_ok": bool(item.get("parse_ok")),
            "parsed": item.get("parsed") or {},
            "prediction": item.get("prediction"),
        }
    return out


def _render_report(manifest: dict[str, Any], models: dict[str, Any]) -> str:
    piwm = models["piwm_main"]
    lines = [
        "5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。",
        "",
        "# PIWM 主模型 4 维度完整评估",
        "",
        "## 1. Headline",
        "",
        "维度 3 的 next-state 指标只在有 transition gold 的 80 条候选动作上评分；另有 27 条 stage-conditioned placeholder candidate 无 gold，仅作为 coverage limitation 记录。",
        "",
        "| Model | Dim 1 AIDA F1 | Dim 2 intent F1 core | Dim 3 next-state F1 | Dim 4 best-act F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    labels = [
        ("simple_baseline", "Simple baseline"),
        ("base_qwen25vl7b", "Qwen2.5-VL-7B zero-shot"),
        ("customer_state_effect_only", "Customer-state-and-effect training only"),
        ("piwm_main", "PIWM main model"),
    ]
    for key, label in labels:
        model = models[key]
        if key == "simple_baseline":
            aida = _fmt(model["user_intent"]["stage"]["majority_macro_f1"])
            intent = _fmt(model["user_intent"]["intent_core"]["majority_macro_f1"])
            next_stage = _fmt(model["next_state"]["next_stage"]["majority_macro_f1"])
            action = "0.414"
        else:
            aida = _fmt(_get(model, "user_intent", "stage", "macro_f1"))
            intent = _fmt(_get(model, "user_intent", "intent_core", "macro_f1"))
            next_stage = _fmt(_get(model, "next_state", "next_stage", "macro_f1"))
            action = _fmt(_get(model, "action", "action", "macro_f1"))
        lines.append(f"| {label} | {aida} | {intent} | {next_stage} | {action} |")

    piwm_next = _get(piwm, "next_state", "next_stage", "macro_f1")
    lines.extend(
        [
            "",
            f"**PIWM 主模型 next-state macro F1（80 条有 gold 的候选动作）：{_fmt(piwm_next)}。**",
            "",
            "## 2. Next-state Coverage",
            "",
            f"- stage-conditioned candidate 总数：{manifest['stage_conditioned_candidate_total']}",
            f"- 有 transition gold 并参与评分：{manifest['next_state_scored_rows']}",
            f"- 无 transition gold、不参与评分：{manifest['next_state_unscored_rows']}",
            f"- 无 gold 候选按 act 分布：`{manifest['next_state_unscored_by_act']}`",
            "",
            "这 27 条缺口来自 stage-conditioned candidate 补齐逻辑生成的 placeholder candidate；它们没有精确的 `transition_modeling` gold，因此不纳入 F1/MAE，避免用规则补标签污染论文数字。该限制应写入论文 limitation 正文。",
            "",
        ]
    )
    lines.extend(_render_model_detail_sections(models))
    lines.extend(_render_failure_chain(models, manifest))
    lines.extend(
        [
            "",
            "## 6. Raw Output Index",
            "",
            f"- Raw directory: `{RAW_DIR}`",
            "- 输入集：`target_user_intent.jsonl` / `next_state_covered80.jsonl` / `next_state_unscored27.jsonl` / `target_action_selection.jsonl`",
            "- 每个模型的推理输出按 `base_qwen25vl7b_*`、`customer_state_effect_only_*`、`piwm_main_*` 命名。",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_model_detail_sections(models: dict[str, Any]) -> list[str]:
    lines = ["## 3. Per-class Results", ""]
    for key, label in [
        ("base_qwen25vl7b", "Qwen2.5-VL-7B zero-shot"),
        ("customer_state_effect_only", "Customer-state-and-effect training only"),
        ("piwm_main", "PIWM main model"),
    ]:
        model = models[key]
        lines.extend([f"### {label}", ""])
        if not all(model["raw_available"].values()):
            lines.extend([f"- raw availability: `{model['raw_available']}`", "- 指标待补。", ""])
            continue
        lines.extend(_metric_line("AIDA stage", model["user_intent"]["stage"], model["user_intent"]["parse_rate"]))
        lines.extend(_metric_line("Intent full", model["user_intent"]["intent"], model["user_intent"]["parse_rate"]))
        lines.extend(_metric_line("Intent core, excluding seek_reassurance and negotiate_price", model["user_intent"]["intent_core"], model["user_intent"]["parse_rate"]))
        lines.extend(_metric_line("Next stage, 80 scored candidates", model["next_state"]["next_stage"], model["next_state"]["parse_rate"], mae=model["next_state"]["reward_mae"]))
        lines.extend(_metric_line("Best act", model["action"]["action"], model["action"]["parse_rate"]))
    return lines


def _metric_line(name: str, metric: dict[str, Any], parse_rate: float | None, mae: float | None = None) -> list[str]:
    bits = [f"- {name}: macro F1={_fmt(metric.get('macro_f1'))}", f"accuracy={_fmt(metric.get('accuracy'))}", f"parse={_fmt(parse_rate)}"]
    if mae is not None:
        bits.append(f"reward MAE={_fmt(mae)}")
    lines = ["; ".join(bits) + "."]
    lines.append("")
    lines.append("| Label | F1 | Precision | Recall | Support | Pred count |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for label, stats in metric.get("per_class", {}).items():
        lines.append(
            f"| {label} | {_fmt(stats['f1'])} | {_fmt(stats['precision'])} | {_fmt(stats['recall'])} | {stats['support']} | {stats['pred_count']} |"
        )
    lines.append("")
    return lines


def _render_failure_chain(models: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    model = models["piwm_main"]
    if not all(model["raw_available"].values()):
        return [
            "## 4. Failure Chain Analysis",
            "",
            "PIWM 主模型三个维度 raw output 尚未全部就绪，失败链路分析待补。",
        ]
    action_inputs = read_jsonl(RAW_DIR / "target_action_selection.jsonl")
    next_inputs = read_jsonl(RAW_DIR / "next_state_covered80.jsonl")
    chain = _chain_records(model, action_inputs, next_inputs)
    lines = ["## 4. Failure Chain Analysis", ""]
    lines.extend(_chain_table_a(chain))
    lines.extend(_chain_table_b(chain))
    lines.extend(_chain_table_c(chain))
    lines.extend(_chain_table_d(chain))
    return lines


def _chain_records(model: dict[str, Any], action_inputs: list[dict[str, Any]], next_inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ui = model["user_intent"]["outputs_by_scene"]
    act_out = model["action"]["outputs_by_scene"]
    next_by_candidate = model["next_state"]["outputs_by_candidate"]
    next_input_by_parent_action = {
        (row.get("meta", {}).get("parent_state_id"), row.get("meta", {}).get("candidate_action")): row
        for row in next_inputs
    }
    records = []
    for row in action_inputs:
        scene_id = row["source_id"]
        gold_stage = _gold_user_stage(scene_id)
        gold_intent = _gold_user_intent(scene_id)
        pred_stage = (ui.get(scene_id, {}).get("parsed") or {}).get("aida_stage")
        pred_intent = (ui.get(scene_id, {}).get("parsed") or {}).get("intent_label")
        gold_act = _gold_act(row)
        pred_act = _action_to_act((act_out.get(scene_id, {}).get("parsed") or {}).get("chosen"), row.get("meta", {}).get("candidate_action_acts", {}))
        gold_action_label = tag_value(row["messages"][2]["content"], "chosen")
        next_row = next_input_by_parent_action.get((scene_id, gold_action_label))
        next_ok = None
        if next_row:
            next_out = next_by_candidate.get(next_row["source_id"])
            if next_out and next_out["parse_ok"]:
                pred_next = (next_out["parsed"] or {}).get("next_aida_stage")
                gold_next = tag_value(next_row["messages"][2]["content"], "next_stage")
                next_ok = pred_next == gold_next
            elif next_out:
                next_ok = False
        records.append(
            {
                "scene_id": scene_id,
                "gold_stage": gold_stage,
                "pred_stage": pred_stage,
                "stage_ok": pred_stage == gold_stage,
                "gold_intent": gold_intent,
                "pred_intent": pred_intent,
                "intent_ok": pred_intent == gold_intent,
                "gold_act": gold_act,
                "pred_act": pred_act,
                "action_ok": pred_act == gold_act,
                "next_ok": next_ok,
            }
        )
    return records


def _gold_user_stage(scene_id: str) -> str | None:
    for row in read_jsonl(RAW_DIR / "target_user_intent.jsonl"):
        if row["source_id"] == scene_id:
            return tag_value(row["messages"][2]["content"], "stage")
    return None


def _gold_user_intent(scene_id: str) -> str | None:
    for row in read_jsonl(RAW_DIR / "target_user_intent.jsonl"):
        if row["source_id"] == scene_id:
            return tag_value(row["messages"][2]["content"], "intent_label")
    return None


def _chain_table_a(records: list[dict[str, Any]]) -> list[str]:
    lines = ["### 表 A：链路条件成功率", "", "| Condition | Rate | Numerator / Denominator |", "| --- | ---: | ---: |"]
    specs = [
        ("P(intent 对 | stage 对)", lambda r: r["stage_ok"], lambda r: r["intent_ok"]),
        ("P(intent 对 | stage 错)", lambda r: not r["stage_ok"], lambda r: r["intent_ok"]),
        ("P(next_state 对 | stage+intent 对)", lambda r: r["stage_ok"] and r["intent_ok"] and r["next_ok"] is not None, lambda r: r["next_ok"] is True),
        ("P(next_state 对 | stage 或 intent 错)", lambda r: (not r["stage_ok"] or not r["intent_ok"]) and r["next_ok"] is not None, lambda r: r["next_ok"] is True),
        ("P(best_act 对 | stage+intent+next_state 全对)", lambda r: r["stage_ok"] and r["intent_ok"] and r["next_ok"] is True, lambda r: r["action_ok"]),
        ("P(best_act 对 | 其他情况)", lambda r: not (r["stage_ok"] and r["intent_ok"] and r["next_ok"] is True), lambda r: r["action_ok"]),
    ]
    for label, cond, ok in specs:
        denom = [r for r in records if cond(r)]
        num = [r for r in denom if ok(r)]
        lines.append(f"| {label} | {_fmt(len(num) / len(denom) if denom else None)} | {len(num)} / {len(denom)} |")
    lines.append("")
    return lines


def _chain_table_b(records: list[dict[str, Any]]) -> list[str]:
    action_errors = [r for r in records if not r["action_ok"]]
    buckets = Counter(_error_type(r) for r in action_errors)
    lines = ["### 表 B：错误类型分布", "", "| Error type | Count | Percent of action errors |", "| --- | ---: | ---: |"]
    for key in ["Type 1 stage error propagation", "Type 2 intent error after correct stage", "Type 3 next-state error after stage+intent", "Type 4 strategy bottleneck", "Unknown next-state coverage"]:
        count = buckets.get(key, 0)
        lines.append(f"| {key} | {count} | {_fmt(count / len(action_errors) if action_errors else None)} |")
    lines.append("")
    return lines


def _error_type(record: dict[str, Any]) -> str:
    if not record["stage_ok"]:
        return "Type 1 stage error propagation"
    if not record["intent_ok"]:
        return "Type 2 intent error after correct stage"
    if record["next_ok"] is False:
        return "Type 3 next-state error after stage+intent"
    if record["next_ok"] is True:
        return "Type 4 strategy bottleneck"
    return "Unknown next-state coverage"


def _chain_table_c(records: list[dict[str, Any]]) -> list[str]:
    wrong = [r for r in records if not r["stage_ok"]]
    lines = ["### 表 C：stage 错误对决策候选集的影响", "", "| Scene | Gold stage | Pred stage | Gold candidates | Pred candidates | Action correct |", "| --- | --- | --- | --- | --- | ---: |"]
    for r in wrong:
        gold_set = "/".join(STAGE_CONDITIONED.get(r["gold_stage"], ()))
        pred_set = "/".join(STAGE_CONDITIONED.get(r["pred_stage"], ()))
        lines.append(f"| {r['scene_id']} | {r['gold_stage']} | {r['pred_stage']} | {gold_set} | {pred_set} | {str(r['action_ok'])} |")
    lines.append("")
    lines.append(f"stage 错误样本 action accuracy：{_fmt(sum(1 for r in wrong if r['action_ok']) / len(wrong) if wrong else None)} ({sum(1 for r in wrong if r['action_ok'])}/{len(wrong)})")
    lines.append("")
    return lines


def _chain_table_d(records: list[dict[str, Any]]) -> list[str]:
    lines = ["### 表 D：per-act 错误归因", "", "| Gold act | Total errors | Stage error | Intent error | Next-state error | Strategy bottleneck | Unknown next-state |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for act in FIVE_ACTS:
        errors = [r for r in records if r["gold_act"] == act and not r["action_ok"]]
        buckets = Counter(_error_type(r) for r in errors)
        lines.append(
            f"| {act} | {len(errors)} | {buckets['Type 1 stage error propagation']} | {buckets['Type 2 intent error after correct stage']} | {buckets['Type 3 next-state error after stage+intent']} | {buckets['Type 4 strategy bottleneck']} | {buckets['Unknown next-state coverage']} |"
        )
    lines.append("")
    return lines


def _get(mapping: dict[str, Any], *keys: str) -> Any:
    cur: Any = mapping
    for key in keys:
        if cur is None:
            return None
        cur = cur.get(key)
    return cur


def _fmt(value: Any) -> str:
    if value is None:
        return "待补"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def update_paper_materials() -> None:
    if not MATERIALS_PATH.exists():
        return
    text = MATERIALS_PATH.read_text(encoding="utf-8")
    marker = "## Part 2：数据集说明"
    section = """## Part 1B：4 维度链路评估框架（待填数字）\n\n这部分用于把 PIWM 的方法故事从单一 best-act 指标扩展为完整链路：视觉观察 → 意图理解 → 效果预测 → 综合决策。当前先放论文表格框架，具体数字由 `reports/2026-05-24_pi_4dim_evaluation.md` 生成后填入。\n\n| Model | Dim 1 AIDA F1 | Dim 2 intent F1 core | Dim 3 next-state F1 | Dim 4 best-act F1 |\n| --- | ---: | ---: | ---: | ---: |\n| Simple baseline | 待补 | 待补 | 待补 | 0.414 |\n| Qwen2.5-VL-7B zero-shot | 待补 | 待补 | 待补 | 待补 |\n| 只做顾客状态与动作后果训练 | 待补 | 待补 | 待补 | 待补 |\n| PIWM 主模型 | 待补 | 待补 | 待补，80 条有 gold 的候选动作 | 0.641 |\n\n说明：Dim 3 只对 80 条有 transition gold 的 stage-conditioned candidates 评分；另有 27 条 placeholder candidates 无 gold，不参与 F1/MAE，作为 next-state evaluation coverage limitation 写入论文限制。\n\n### 错误传播分析框架\n\n最终报告需要补 4 张 discussion 表：\n\n| 表 | 内容 | 论文用途 |\n| --- | --- | --- |\n| A | 链路条件成功率：上游正确时，下游是否更容易正确 | 支撑视觉观察是后续判断基础 |\n| B | 错误类型分布：stage / intent / next-state / strategy 四类瓶颈 | 说明主要失败来自哪一层 |\n| C | stage 错误导致候选集如何变化 | 解释 stage-conditioned 候选策略的收益和风险 |\n| D | per-act 错误归因，重点看 Hold | 解释 Hold 召回低是上游问题还是策略问题 |\n\n"""
    if "## Part 1B：4 维度链路评估框架" in text:
        text = re.sub(r"## Part 1B：4 维度链路评估框架（待填数字）.*?(?=## Part 2：数据集说明)", section, text, flags=re.S)
    elif marker in text:
        text = text.replace(marker, section + marker, 1)
    MATERIALS_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "summarize", "update-materials"])
    args = parser.parse_args()
    if args.command == "prepare":
        prepare_inputs()
    elif args.command == "summarize":
        summarize()
    elif args.command == "update-materials":
        update_paper_materials()


if __name__ == "__main__":
    main()
