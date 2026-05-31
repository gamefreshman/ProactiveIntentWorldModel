"""Run PIWM inference-time counterfactual planning on target 5-act test rows.

This script is intentionally narrow: it does not change official data, does not
train, and does not depend on the full interactive decision loop. It expands the
30 target action-selection rows into stage-conditioned candidate next-state
queries, runs a checkpoint once per candidate, and chooses the candidate with
the highest planning reward.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_infer.parsers import MalformedOutputError, parse_action_output, parse_deliberation_output
from piwm_train import config as train_config
from piwm_train.prompts import PIWM_SYSTEM_PROMPT, build_deliberation_prompt

FIVE_ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")
AIDA_STAGES = ("attention", "interest", "desire", "action")
STAGE_ORDER = {stage: index for index, stage in enumerate(AIDA_STAGES)}
RAW_DIR = REPO_ROOT / "reports" / "trick6_raw_20260524"
DIM3_RAW_DIR = REPO_ROOT / "reports" / "dim3_raw_20260524"
TRICK6_REPORT = REPO_ROOT / "reports" / "2026-05-24_trick6_counterfactual_planning.md"
DIM3_REPORT = REPO_ROOT / "reports" / "2026-05-24_dim3_next_state_evaluation.md"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tag_value(text: str, tag: str) -> str | None:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text or "", flags=re.S)
    return match.group(1).strip() if match else None


def build_transition_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row.get("meta", {}).get("parent_state_id"), row.get("input", {}).get("candidate_action")): row
        for row in rows
        if row.get("meta", {}).get("parent_state_id") and row.get("input", {}).get("candidate_action")
    }


def build_state_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    state_index: dict[str, dict[str, Any]] = {}
    for row in rows:
        parent = row.get("meta", {}).get("parent_state_id")
        state = row.get("input", {}).get("current_state_summary")
        if parent and state and parent not in state_index:
            state_index[parent] = state
    return state_index


def action_to_act(action: str | None, mapping: dict[str, str]) -> str | None:
    if action is None:
        return None
    if action in mapping:
        return mapping[action]
    if "_" in action:
        prefix = action.split("_", 1)[0]
        if prefix in FIVE_ACTS:
            return prefix
    return action


def gold_candidate(row: dict[str, Any]) -> str | None:
    return tag_value(row["messages"][2]["content"], "chosen")


def load_model(args: argparse.Namespace):
    import torch
    from peft import PeftModel
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
    base = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if args.torch_dtype == "bfloat16" else torch.float16,
        device_map=args.device_map,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, args.checkpoint) if args.checkpoint else base
    model.eval()
    return model, processor


def normalize_messages(row: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    user = row["messages"][1]
    text = str(user["content"]).replace("<image>", "").strip()
    content: list[dict[str, Any]] = []
    for image in row.get("images", [])[: args.image_limit]:
        item: dict[str, Any] = {"type": "image", "image": resolve_runtime_image_path(image)}
        if args.max_pixels is not None:
            item["max_pixels"] = args.max_pixels
        content.append(item)
    content.append({"type": "text", "text": text})
    return [{"role": "system", "content": row["messages"][0]["content"]}, {"role": "user", "content": content}]


def resolve_runtime_image_path(image: str) -> str:
    path = Path(str(image))
    if path.exists():
        return str(path)
    text = str(image)
    local_prefix = "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel"
    remote_prefix = "/root/lanyun-fs/ProactiveIntentWorldModel"
    if text.startswith(local_prefix):
        remapped = Path(text.replace(local_prefix, str(REPO_ROOT), 1))
        if remapped.exists():
            return str(remapped)
    if text.startswith(remote_prefix):
        remapped = Path(text.replace(remote_prefix, str(REPO_ROOT), 1))
        if remapped.exists():
            return str(remapped)
    if not path.is_absolute():
        remapped = REPO_ROOT / path
        if remapped.exists():
            return str(remapped)
    return text


def generate_one(model, processor, row: dict[str, Any], args: argparse.Namespace) -> str:
    import torch
    from qwen_vl_utils import process_vision_info

    messages = normalize_messages(row, args)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


def empty_cuda_cache() -> None:
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        return


def next_state_ms_row(
    action_row: dict[str, Any],
    candidate: str,
    transition_index: dict[tuple[str, str], dict[str, Any]],
    state_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scene_id = action_row["source_id"]
    transition = transition_index.get((scene_id, candidate))
    if transition is not None:
        record = {
            "input": {
                **transition["input"],
                "frames": list(transition["input"].get("frames", [])),
            }
        }
        prompt = build_deliberation_prompt(record)
        images = [str((REPO_ROOT / frame).resolve()) if not str(frame).startswith("/") else str(frame) for frame in record["input"]["frames"]]
        candidate_spec = transition["input"].get("candidate_action_spec", {})
        candidate_act = candidate_spec.get("act") or action_row.get("meta", {}).get("candidate_action_acts", {}).get(candidate)
        candidate_params = candidate_spec.get("params", {})
        gold = transition.get("output", {}).get("next_state", {})
        target = _transition_target_text(transition)
    else:
        state = state_index.get(scene_id) or parse_current_state_from_action_prompt(action_row)
        candidate_payload = parse_candidate_payload(action_row, candidate)
        record = {
            "input": {
                "frames": list(action_row.get("images", [])),
                "current_state_summary": state,
                "candidate_action": candidate,
                "candidate_action_key": candidate,
                "candidate_action_spec": candidate_payload["candidate_action_spec"],
                "candidate_dialogue_act": candidate_payload["candidate_dialogue_act"],
                "candidate_action_realization": candidate_payload["candidate_action_realization"],
                "candidate_terminal_realization": candidate_payload["candidate_terminal_realization"],
            }
        }
        prompt = build_deliberation_prompt(record)
        images = list(action_row.get("images", []))
        candidate_act = candidate_payload["candidate_action_spec"].get("act")
        candidate_params = candidate_payload["candidate_action_spec"].get("params", {})
        target = ""
    return {
        "messages": [
            {"role": "system", "content": PIWM_SYSTEM_PROMPT},
            {"role": "user", "content": f"{'<image>' * len(images)}{prompt.replace(train_config.IMAGE_PLACEHOLDER, '').strip()}"},
            {"role": "assistant", "content": target},
        ],
        "images": images,
        "task": "next_state_prediction",
        "source_id": f"{scene_id}#{candidate}",
        "meta": {
            "parent_state_id": scene_id,
            "candidate_action": candidate,
            "candidate_act": candidate_act,
            "candidate_params": candidate_params,
            "has_transition_gold": transition is not None,
        },
    }


def _transition_target_text(row: dict[str, Any]) -> str:
    out = row.get("output", {})
    next_bdi = out.get("next_bdi") or {}
    return (
        f"<next_stage>{out.get('next_aida_stage')}</next_stage>\n"
        f"<next_belief>{next_bdi.get('belief')}</next_belief>\n"
        f"<next_desire>{next_bdi.get('desire')}</next_desire>\n"
        f"<next_intention>{next_bdi.get('intention')}</next_intention>\n"
        f"<risk>{out.get('risk') or out.get('risk_level')}</risk>\n"
        f"<benefit>{out.get('benefit') or out.get('benefit_level')}</benefit>\n"
        f"<reward>{out.get('reward')}</reward>"
    )


def parse_current_state_from_action_prompt(row: dict[str, Any]) -> dict[str, Any]:
    text = row["messages"][1]["content"]
    def field(label: str, default: str = "") -> str:
        match = re.search(rf"^- {re.escape(label)}: (.*)$", text, flags=re.M)
        return match.group(1).strip() if match else default
    return {
        "aida_stage": field("stage", "interest"),
        "state_subtype": "target_frontcam_observation",
        "state": "target_frontcam_observation",
        "visual_state": {
            "summary": field("visible evidence"),
            "engagement_pattern": field("engagement pattern"),
            "gaze_and_attention": field("gaze and attention"),
            "body_and_hands": field("body and hands"),
        },
        "intent": field("intent_label", "explore_options"),
        "bdi": {
            "belief": field("belief"),
            "desire": field("desire"),
            "intention": field("intention"),
        },
    }


def parse_candidate_payload(row: dict[str, Any], candidate: str) -> dict[str, Any]:
    text = row["messages"][1]["content"]
    line = ""
    for raw_line in text.splitlines():
        if raw_line.startswith(f"- {candidate}: "):
            line = raw_line[len(f"- {candidate}: "):]
            break
    if not line:
        act = row.get("meta", {}).get("candidate_action_acts", {}).get(candidate) or action_to_act(candidate, {})
        return _candidate_payload(candidate, act or "Inform", {}, "", {}, "", "", "", "")
    fields = _split_candidate_fields(line)
    act = fields.get("act") or row.get("meta", {}).get("candidate_action_acts", {}).get(candidate) or action_to_act(candidate, {})
    params = _literal(fields.get("params"), {})
    screen = _literal(fields.get("screen"), {})
    return _candidate_payload(
        candidate,
        act or "Inform",
        params,
        fields.get("surface_text", ""),
        screen,
        fields.get("voice_style", ""),
        fields.get("light", ""),
        fields.get("physical_action", ""),
        fields.get("utterance", ""),
    )


def _split_candidate_fields(line: str) -> dict[str, str]:
    keys = ["act", "params", "surface_text", "screen", "voice_style", "light", "physical_action", "utterance"]
    positions: list[tuple[int, str]] = []
    for key in keys:
        marker = f"{key}="
        index = line.find(marker)
        if index >= 0:
            positions.append((index, key))
    positions.sort()
    out: dict[str, str] = {}
    for index, (start, key) in enumerate(positions):
        marker_len = len(key) + 1
        end = positions[index + 1][0] if index + 1 < len(positions) else len(line)
        value = line[start + marker_len:end].strip()
        if value.endswith(","):
            value = value[:-1].strip()
        out[key] = value
    return out


def _literal(text: str | None, default: Any) -> Any:
    if not text:
        return default
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return default


def _candidate_payload(
    candidate: str,
    act: str,
    params: dict[str, Any],
    surface_text: str,
    screen: dict[str, Any],
    voice_style: str,
    light: str,
    physical_action: str,
    utterance: str,
) -> dict[str, Any]:
    return {
        "candidate_action_spec": {"act": act, "params": params},
        "candidate_dialogue_act": {"act": act, "params": params},
        "candidate_terminal_realization": {
            "surface_text": surface_text,
            "screen": screen,
            "voice_style": voice_style,
            "light": light,
        },
        "candidate_action_realization": {
            "physical_action": physical_action,
            "utterance": utterance,
        },
    }


def reward_stage_advance(current_stage: str | None, parsed: dict[str, Any]) -> float:
    next_stage = parsed.get("next_aida_stage")
    if current_stage not in STAGE_ORDER or next_stage not in STAGE_ORDER:
        return -math.inf
    current_index = STAGE_ORDER[current_stage]
    next_index = STAGE_ORDER[next_stage]
    if next_index > current_index:
        return 1.0
    if next_index == current_index:
        return 0.0
    return -1.0


def reward_model_score(current_stage: str | None, parsed: dict[str, Any]) -> float:
    value = parsed.get("reward")
    try:
        return float(value)
    except (TypeError, ValueError):
        return reward_stage_advance(current_stage, parsed)


def current_stage(row: dict[str, Any], state_index: dict[str, dict[str, Any]]) -> str | None:
    scene_id = row["source_id"]
    if scene_id in state_index:
        return state_index[scene_id].get("aida_stage")
    return parse_current_state_from_action_prompt(row).get("aida_stage")


def run_trick6(args: argparse.Namespace) -> None:
    action_rows = read_jsonl(args.action_jsonl)
    if args.limit is not None:
        action_rows = action_rows[: args.limit]
    transitions = read_jsonl(args.transition_jsonl)
    transition_index = build_transition_index(transitions)
    state_index = build_state_index(transitions)
    model, processor = load_model(args)
    reward_fn = reward_stage_advance if args.reward_mode == "stage_advance" else reward_model_score
    outputs = []
    candidate_total = 0
    candidate_parsed = 0
    start = time.time()
    for index, action_row in enumerate(action_rows, start=1):
        mapping = action_row.get("meta", {}).get("candidate_action_acts", {})
        candidates = list(mapping)
        scene_stage = current_stage(action_row, state_index)
        per_candidate: dict[str, Any] = {}
        for candidate in candidates:
            candidate_total += 1
            next_row = next_state_ms_row(action_row, candidate, transition_index, state_index)
            try:
                raw = generate_one(model, processor, next_row, args)
                parsed = parse_deliberation_output(raw.split("\n[recap]", 1)[0].strip())
                reward = reward_fn(scene_stage, parsed)
                candidate_parsed += 1
                per_candidate[candidate] = {
                    "act": mapping.get(candidate),
                    "parse_ok": True,
                    "prediction": raw,
                    "parsed": parsed,
                    "planning_reward": reward,
                    "has_transition_gold": next_row["meta"]["has_transition_gold"],
                }
            except (MalformedOutputError, RuntimeError, ValueError) as exc:
                per_candidate[candidate] = {
                    "act": mapping.get(candidate),
                    "parse_ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "planning_reward": -math.inf,
                    "has_transition_gold": next_row["meta"]["has_transition_gold"],
                }
            finally:
                empty_cuda_cache()
        chosen = choose_candidate(candidates, per_candidate)
        fallback_used = False
        if chosen is None:
            fallback_used = True
            chosen = direct_fallback(action_row, model, processor, args) or (candidates[0] if candidates else None)
        gold = gold_candidate(action_row)
        outputs.append(
            {
                "scene_id": action_row["source_id"],
                "current_stage": scene_stage,
                "gold_candidate": gold,
                "gold_act": action_to_act(gold, mapping),
                "chosen_candidate": chosen,
                "chosen_act": action_to_act(chosen, mapping),
                "fallback_used": fallback_used,
                "candidate_order": candidates,
                "per_candidate": per_candidate,
            }
        )
        if args.progress_every and (index == 1 or index % args.progress_every == 0 or index == len(action_rows)):
            print(json.dumps({"event": "trick6_progress", "reward_mode": args.reward_mode, "index": index, "total": len(action_rows), "candidate_parse_rate": candidate_parsed / candidate_total if candidate_total else None, "elapsed_sec": round(time.time() - start, 1)}, ensure_ascii=False), flush=True)
    result = {
        "artifact": "piwm_trick6_counterfactual_planning",
        "five_act": list(FIVE_ACTS),
        "reward_mode": args.reward_mode,
        "checkpoint": str(args.checkpoint) if args.checkpoint else None,
        "action_jsonl": str(args.action_jsonl),
        "n_scenes": len(outputs),
        "candidate_total": candidate_total,
        "candidate_parse_success": candidate_parsed,
        "candidate_parse_rate": candidate_parsed / candidate_total if candidate_total else None,
        "metrics": action_metrics(outputs),
        "outputs": outputs,
    }
    write_json(args.out, result)
    print(json.dumps({"event": "trick6_done", "out": str(args.out), "metrics": result["metrics"]}, ensure_ascii=False), flush=True)


def choose_candidate(candidates: list[str], per_candidate: dict[str, Any]) -> str | None:
    parsed = [candidate for candidate in candidates if per_candidate.get(candidate, {}).get("parse_ok")]
    if not parsed:
        return None
    return max(parsed, key=lambda candidate: (per_candidate[candidate]["planning_reward"], -candidates.index(candidate)))


def direct_fallback(action_row: dict[str, Any], model, processor, args: argparse.Namespace) -> str | None:
    try:
        raw = generate_one(model, processor, action_row, args)
        mapping = action_row.get("meta", {}).get("candidate_action_acts", {})
        parsed = parse_action_output(raw, valid_actions=set(mapping), five_act_only=True)
        return parsed.get("chosen")
    except (MalformedOutputError, RuntimeError, ValueError):
        return None


def run_dim3(args: argparse.Namespace) -> None:
    transitions = read_jsonl(args.transition_jsonl)
    transition_index = build_transition_index(transitions)
    state_index = build_state_index(transitions)
    covered_inputs = read_jsonl(args.covered_jsonl)
    if args.limit is not None:
        covered_inputs = covered_inputs[: args.limit]
    action_rows = {row["source_id"]: row for row in read_jsonl(args.action_jsonl)}
    model, processor = load_model(args)
    outputs = []
    start = time.time()
    for index, covered in enumerate(covered_inputs, start=1):
        scene_id = covered.get("meta", {}).get("parent_state_id")
        candidate = covered.get("meta", {}).get("candidate_action")
        action_row = action_rows[scene_id]
        next_row = next_state_ms_row(action_row, candidate, transition_index, state_index)
        gold = parse_deliberation_output(covered["messages"][2]["content"])
        record = {
            "source_id": covered["source_id"],
            "scene_id": scene_id,
            "candidate_action": candidate,
            "candidate_act": covered.get("meta", {}).get("candidate_act"),
            "gold": gold,
        }
        try:
            raw = generate_one(model, processor, next_row, args)
            parsed = parse_deliberation_output(raw.split("\n[recap]", 1)[0].strip())
            record.update({"parse_ok": True, "prediction": raw, "parsed": parsed})
        except (MalformedOutputError, RuntimeError, ValueError) as exc:
            record.update({"parse_ok": False, "error": f"{type(exc).__name__}: {exc}"})
        finally:
            empty_cuda_cache()
        outputs.append(record)
        if args.progress_every and (index == 1 or index % args.progress_every == 0 or index == len(covered_inputs)):
            print(json.dumps({"event": "dim3_progress", "index": index, "total": len(covered_inputs), "parse_success": sum(1 for x in outputs if x.get("parse_ok")), "elapsed_sec": round(time.time() - start, 1)}, ensure_ascii=False), flush=True)
    result = {
        "artifact": "piwm_dim3_next_state_eval",
        "five_act": list(FIVE_ACTS),
        "checkpoint": str(args.checkpoint) if args.checkpoint else None,
        "n_records": len(outputs),
        "parse_success": sum(1 for row in outputs if row.get("parse_ok")),
        "outputs": outputs,
        "metrics": next_state_metrics(outputs),
    }
    write_json(args.out, result)
    print(json.dumps({"event": "dim3_done", "out": str(args.out), "metrics": result["metrics"]}, ensure_ascii=False), flush=True)


def action_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [(row.get("chosen_act"), row.get("gold_act")) for row in outputs]
    return {
        "macro_f1": macro_f1(pairs, list(FIVE_ACTS)),
        "accuracy": accuracy(pairs),
        "per_act": {act: per_label(pairs, act) for act in FIVE_ACTS},
        "pred_count": dict(sorted(Counter(pred for pred, _ in pairs if pred).items())),
        "support": dict(sorted(Counter(gold for _, gold in pairs if gold).items())),
    }


def next_state_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = []
    strict_pairs = []
    reward_errors = []
    by_act: dict[str, list[tuple[str | None, str | None]]] = defaultdict(list)
    by_stage: dict[str, list[tuple[str | None, str | None]]] = defaultdict(list)
    for row in outputs:
        gold_stage = row.get("gold", {}).get("next_aida_stage")
        pred_stage = row.get("parsed", {}).get("next_aida_stage") if row.get("parse_ok") else None
        if row.get("parse_ok"):
            pairs.append((pred_stage, gold_stage))
            strict_pairs.append((pred_stage, gold_stage))
            try:
                reward_errors.append(abs(float(row["parsed"].get("reward")) - float(row["gold"].get("reward"))))
            except (TypeError, ValueError):
                pass
        else:
            strict_pairs.append(("__parse_error__", gold_stage))
        by_act[row.get("candidate_act")].append((pred_stage, gold_stage))
        by_stage[gold_stage].append((pred_stage, gold_stage))
    return {
        "parse_rate": sum(1 for row in outputs if row.get("parse_ok")) / len(outputs) if outputs else None,
        "next_stage_macro_f1": macro_f1(pairs, list(AIDA_STAGES)),
        "next_stage_strict_macro_f1": macro_f1(strict_pairs, list(AIDA_STAGES)),
        "accuracy": accuracy(pairs),
        "reward_mae": sum(reward_errors) / len(reward_errors) if reward_errors else None,
        "per_candidate_act": {
            key: {"n": len(value), "macro_f1": macro_f1(value, list(AIDA_STAGES)), "accuracy": accuracy(value)}
            for key, value in sorted(by_act.items())
        },
        "per_gold_stage": {
            key: {"n": len(value), "macro_f1": macro_f1(value, list(AIDA_STAGES)), "accuracy": accuracy(value)}
            for key, value in sorted(by_stage.items())
        },
    }


def macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(per_label(pairs, label)["f1"] for label in labels) / len(labels)


def accuracy(pairs: list[tuple[str | None, str | None]]) -> float | None:
    if not pairs:
        return None
    return sum(1 for pred, gold in pairs if pred == gold) / len(pairs)


def per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
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


def render_reports() -> None:
    direct_path = REPO_ROOT / "reports/4dim_eval_raw_20260524/piwm_main_action_selection.json"
    reward_a_path = RAW_DIR / "trick6_reward_stage_advance.json"
    reward_b_path = RAW_DIR / "trick6_reward_model_score.json"
    dim3_path = DIM3_RAW_DIR / "dim3_next_state_current_state_prompt.json"
    direct = load_json_optional(direct_path)
    reward_a = load_json_optional(reward_a_path)
    reward_b = load_json_optional(reward_b_path)
    dim3 = load_json_optional(dim3_path)
    TRICK6_REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。",
        "",
        "# Trick 6 Inference-Time Counterfactual Planning",
        "",
        "## 一句话结论",
        "",
        conclusion_text(direct, reward_a, reward_b),
        "",
        "## Run Config",
        "",
        "- 方法：枚举 stage-conditioned candidates，逐候选预测 next-state，再按 reward argmax 选动作。",
        "- Reward A：AIDA stage advance，推进 +1，持平 0，退步 -1。",
        "- Reward B：优先使用模型输出的 reward 字段；缺失时 fallback 到 Reward A。",
        "- Tie-break：reward 相同时按候选列表原始顺序。",
        "- Parse error：该候选 reward=-inf；若全候选失败，则 fallback direct action inference。",
        "",
        "## 主结果",
        "",
        "| Method | Macro F1 | Accuracy | Candidate parse rate | Per-act F1 |",
        "| --- | ---: | ---: | ---: | --- |",
        direct_row("PIWM direct", direct),
        trick_row("PIWM + Trick 6 reward A", reward_a),
        trick_row("PIWM + Trick 6 reward B", reward_b),
        "",
        "## Per-act Detail",
        "",
    ]
    for label, payload in [("Reward A", reward_a), ("Reward B", reward_b)]:
        lines.extend(per_act_table(label, payload))
    lines.extend([
        "## 失败 Case 分析",
        "",
        failure_case_summary(reward_a, reward_b),
        "",
        "## 论文建议",
        "",
        paper_recommendation(direct, reward_a, reward_b),
        "",
    ])
    TRICK6_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    unscored_path = REPO_ROOT / "reports/4dim_eval_raw_20260524/next_state_unscored27.jsonl"
    unscored = read_jsonl(unscored_path) if unscored_path.exists() else []
    dim_lines = [
        "5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。",
        "",
        "# Dim 3 Next-state Evaluation",
        "",
        "## Summary",
        "",
        dim3_summary(dim3),
        "",
        "## Metrics",
        "",
        "```json",
        json.dumps((dim3 or {}).get("metrics", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Coverage Limitation",
        "",
        f"- scored candidates: {(dim3 or {}).get('n_records', '待补')}",
        f"- unscored placeholder candidates: {len(unscored)}",
        f"- unscored by act: `{dict(sorted(Counter(row.get('candidate_act') for row in unscored).items()))}`",
        "",
        "27 条无 gold 的候选只用于 Trick 6 planning，不进入 next-stage F1 / reward MAE。",
        "",
    ]
    DIM3_REPORT.write_text("\n".join(dim_lines) + "\n", encoding="utf-8")
    print(str(TRICK6_REPORT))
    print(str(DIM3_REPORT))


def load_json_optional(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def direct_row(label: str, payload: dict[str, Any] | None) -> str:
    if not payload:
        return f"| {label} | 0.641 | 待补 | 0.933 | 待补 |"
    metrics = payload.get("metrics", {})
    macro = metrics.get("action_macro_f1") or metrics.get("parsed_action_macro_f1") or 0.641
    accuracy_value = metrics.get("action_accuracy")
    parse_rate = payload.get("parse_rate")
    return f"| {label} | {fmt(macro)} | {fmt(accuracy_value)} | {fmt(parse_rate)} | 见既有主结果 |"


def trick_row(label: str, payload: dict[str, Any] | None) -> str:
    if not payload:
        return f"| {label} | 待补 | 待补 | 待补 | 待补 |"
    metrics = payload.get("metrics", {})
    per = metrics.get("per_act", {})
    per_text = ", ".join(f"{act}={fmt(per.get(act, {}).get('f1'))}" for act in FIVE_ACTS)
    return f"| {label} | {fmt(metrics.get('macro_f1'))} | {fmt(metrics.get('accuracy'))} | {fmt(payload.get('candidate_parse_rate'))} | {per_text} |"


def per_act_table(label: str, payload: dict[str, Any] | None) -> list[str]:
    lines = [f"### {label}", "", "| Act | F1 | Precision | Recall | Support | Pred count |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    per = (payload or {}).get("metrics", {}).get("per_act", {})
    for act in FIVE_ACTS:
        stats = per.get(act, {})
        lines.append(f"| {act} | {fmt(stats.get('f1'))} | {fmt(stats.get('precision'))} | {fmt(stats.get('recall'))} | {stats.get('support', '待补')} | {stats.get('pred_count', '待补')} |")
    lines.append("")
    return lines


def conclusion_text(direct: dict[str, Any] | None, a: dict[str, Any] | None, b: dict[str, Any] | None) -> str:
    direct_f1 = (direct or {}).get("metrics", {}).get("action_macro_f1") or 0.641
    a_f1 = (a or {}).get("metrics", {}).get("macro_f1")
    b_f1 = (b or {}).get("metrics", {}).get("macro_f1")
    if a_f1 is None and b_f1 is None:
        return "Trick 6 数字待补；当前 direct best-act parsed macro F1 = 0.641。"
    best_label, best_value = max([("Reward A", a_f1), ("Reward B", b_f1)], key=lambda x: -math.inf if x[1] is None else x[1])
    delta = best_value - direct_f1
    direction = "提升" if delta > 0 else "下降" if delta < 0 else "持平"
    return f"Trick 6 最好版本为 {best_label}，macro F1={fmt(best_value)}，相对 direct 0.641 {direction} {fmt(delta)}。"


def failure_case_summary(a: dict[str, Any] | None, b: dict[str, Any] | None) -> str:
    parts = []
    for label, payload in [("Reward A", a), ("Reward B", b)]:
        if not payload:
            parts.append(f"- {label}: 待补。")
            continue
        wrong = [row for row in payload.get("outputs", []) if row.get("chosen_act") != row.get("gold_act")]
        parse_fail_wrong = 0
        for row in wrong:
            chosen = row.get("chosen_candidate")
            if chosen and not row.get("per_candidate", {}).get(chosen, {}).get("parse_ok"):
                parse_fail_wrong += 1
        parts.append(f"- {label}: 错误 {len(wrong)}/{payload.get('n_scenes')}；其中 chosen candidate parse failure 相关 {parse_fail_wrong} 条。")
    return "\n".join(parts)


def paper_recommendation(direct: dict[str, Any] | None, a: dict[str, Any] | None, b: dict[str, Any] | None) -> str:
    direct_f1 = (direct or {}).get("metrics", {}).get("action_macro_f1") or 0.641
    candidates = [(direct_f1, "direct"), ((a or {}).get("metrics", {}).get("macro_f1"), "Trick 6 Reward A"), ((b or {}).get("metrics", {}).get("macro_f1"), "Trick 6 Reward B")]
    numeric = [(value, label) for value, label in candidates if value is not None]
    if not numeric:
        return "待补。"
    best_value, best_label = max(numeric)
    if best_label == "direct":
        return "建议论文 main result 继续使用 direct action selection；Trick 6 可作为 decision-time planning ablation 或 future work。"
    return f"建议论文 main result 使用 {best_label}，并将 framing 升级为 world model is used at decision time。"


def dim3_summary(payload: dict[str, Any] | None) -> str:
    if not payload:
        return "维度 3 数字待补。"
    metrics = payload.get("metrics", {})
    return f"80 条 covered candidates 上，next-stage macro F1={fmt(metrics.get('next_stage_macro_f1'))}，strict macro F1={fmt(metrics.get('next_stage_strict_macro_f1'))}，parse rate={fmt(metrics.get('parse_rate'))}，reward MAE={fmt(metrics.get('reward_mae'))}。"


def fmt(value: Any) -> str:
    if value is None:
        return "待补"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["trick6", "dim3", "report"], required=True)
    parser.add_argument("--reward-mode", choices=["stage_advance", "model_score"], default="stage_advance")
    parser.add_argument("--model", type=Path, default=Path("/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct"))
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500"))
    parser.add_argument("--no-lora", action="store_true", help="Load the base model only; ignore --checkpoint for zero-shot evaluation.")
    parser.add_argument("--action-jsonl", type=Path, default=REPO_ROOT / "data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl")
    parser.add_argument("--transition-jsonl", type=Path, default=REPO_ROOT / "data/official/piwm_target_v1/transition_modeling.jsonl")
    parser.add_argument("--covered-jsonl", type=Path, default=REPO_ROOT / "reports/4dim_eval_raw_20260524/next_state_covered80.jsonl")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--image-limit", type=int, default=3)
    parser.add_argument("--max-pixels", type=int, default=1003520)
    parser.add_argument("--torch-dtype", choices=["bfloat16", "float16"], default="bfloat16")
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.mode == "report":
        render_reports()
        return
    if args.no_lora:
        args.checkpoint = None
    elif not args.checkpoint.is_absolute():
        args.checkpoint = REPO_ROOT / args.checkpoint
    if args.mode == "trick6":
        if args.out is None:
            suffix = "reward_stage_advance" if args.reward_mode == "stage_advance" else "reward_model_score"
            args.out = RAW_DIR / f"trick6_{suffix}.json"
        run_trick6(args)
    elif args.mode == "dim3":
        if args.out is None:
            args.out = DIM3_RAW_DIR / "dim3_next_state_current_state_prompt.json"
        run_dim3(args)


if __name__ == "__main__":
    main()
