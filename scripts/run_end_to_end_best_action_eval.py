"""Run PIWM end-to-end best-action evaluation.

Pipeline:
1. infer customer state from video frames with the user_intent prompt;
2. inject the predicted state into the existing best-action prompt;
3. score best_action against gold labels, counting parse failures as wrong.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_infer.parsers import MalformedOutputError, parse_action_output, parse_user_intent_output


FIVE_ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")
DEFAULT_MODEL = Path("/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct")
DEFAULT_CHECKPOINT = Path(
    "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/"
    "a3_full_targetv2_balanced_3epoch_v1/"
    "a3full-20260522-220941-px1003520-ml8192/"
    "v0-20260522-220953/checkpoint-500"
)
DEFAULT_USER_INTENT = REPO_ROOT / "reports/rerun_eval_20260525/user_intent_target30_general30_seed42.archive_resolved.server.jsonl"
DEFAULT_ACTION = REPO_ROOT / "reports/closed_model_eval_set_60.jsonl"
DEFAULT_OUT_DIR = REPO_ROOT / "reports/end_to_end_eval_20260525"
DEFAULT_REPORT = REPO_ROOT / "reports/2026-05-26_end_to_end_main_result.md"
LOCAL_REPO_PREFIX = "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel"
REMOTE_REPO_PREFIX = "/root/lanyun-fs/ProactiveIntentWorldModel"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def primary_structured_block(raw: str) -> str:
    return raw.split("\n[recap]", 1)[0].strip()


def normalize_messages(row: dict[str, Any], images: list[str], max_pixels: int | None) -> list[dict[str, Any]]:
    user_text = str(row["messages"][1]["content"]).replace("<image>", "").strip()
    content: list[dict[str, Any]] = []
    for image in images:
        item: dict[str, Any] = {"type": "image", "image": image}
        if max_pixels is not None:
            item["max_pixels"] = max_pixels
        content.append(item)
    content.append({"type": "text", "text": user_text})
    return [{"role": "system", "content": row["messages"][0]["content"]}, {"role": "user", "content": content}]


def resolve_images(images: list[str], *, source_id: str) -> list[str]:
    resolved = []
    for index, image in enumerate(images):
        path = resolve_image(Path(image), source_id=source_id, frame_index=index)
        if not path.exists():
            raise FileNotFoundError(f"image not found for {source_id}: {path}")
        resolved.append(path.resolve().as_posix())
    if len(resolved) != 3:
        raise ValueError(f"{source_id}: expected 3 images, got {len(resolved)}")
    return resolved


def resolve_image(path: Path, *, source_id: str, frame_index: int) -> Path:
    for candidate in image_candidates(path, source_id=source_id, frame_index=frame_index):
        if candidate.exists():
            return candidate
    return repo_relative(path)


def image_candidates(path: Path, *, source_id: str, frame_index: int) -> list[Path]:
    frame_name = f"{frame_index:03d}{path.suffix or '.jpg'}"
    candidates = [path, repo_relative(path)]
    if source_id:
        candidates.extend(
            [
                REPO_ROOT / "data/official/ms_swift_5frame/frames" / source_id / frame_name,
                REPO_ROOT / "archives/Archive_generated_synth_core" / source_id / "frames" / frame_name,
                REPO_ROOT / "archives/Archive_generated_evalqa_seed" / source_id / "frames" / frame_name,
                REPO_ROOT / "archives/Archive_generated_synth_extended" / source_id / "frames" / frame_name,
                REPO_ROOT / "archives/Archive_generated_synth_remaining" / source_id / "frames" / frame_name,
                REPO_ROOT / "Archive_generated_priority24" / source_id / "frames" / frame_name,
                REPO_ROOT / "Archive_generated_priority256" / source_id / "frames" / frame_name,
                REPO_ROOT / "Archive_generated_priority500_new_after280" / source_id / "frames" / frame_name,
                REPO_ROOT / "Archive_generated_priority1000_remaining_after500" / source_id / "frames" / frame_name,
                REPO_ROOT / "data/official/piwm_target_v1/frames" / source_id.replace("target_", "") / frame_name,
            ]
        )
    return candidates


def repo_relative(path: Path) -> Path:
    text = path.as_posix()
    for prefix in (LOCAL_REPO_PREFIX, REMOTE_REPO_PREFIX):
        if text.startswith(prefix + "/"):
            return REPO_ROOT / text[len(prefix) + 1 :]
    if path.is_absolute():
        try:
            return REPO_ROOT / path.relative_to(REPO_ROOT)
        except ValueError:
            return path
    return REPO_ROOT / path


def generate_one(model, processor, row: dict[str, Any], images: list[str], args: argparse.Namespace, *, max_new_tokens: int) -> str:
    import torch
    from qwen_vl_utils import process_vision_info

    messages = normalize_messages(row, images, args.max_pixels)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt")
    inputs = inputs.to(model.device)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


def state_block(parsed: dict[str, Any]) -> str:
    visual = parsed["visual_state"]
    bdi = parsed["bdi"]
    return "\n".join(
        [
            f"- stage: {parsed['aida_stage']}",
            f"- intent_label: {parsed['intent_label']}",
            f"- visible evidence: {visual.get('summary', 'not provided')}",
            f"- engagement pattern: {visual.get('engagement_pattern', 'not provided')}",
            f"- gaze and attention: {visual.get('gaze_and_attention', 'not provided')}",
            f"- body and hands: {visual.get('body_and_hands', 'not provided')}",
            f"- belief: {bdi['belief']}",
            f"- desire: {bdi['desire']}",
            f"- intention: {bdi['intention']}",
        ]
    )


def action_row_with_predicted_state(action_row: dict[str, Any], parsed_state: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(action_row, ensure_ascii=False))
    prompt = out["messages"][1]["content"]
    replacement = "The Stage-1 customer-state representation is:\n" + state_block(parsed_state)
    new_prompt, n_repl = re.subn(
        r"The Stage-1 customer-state representation is:\n.*?\n\nCandidate interventions are listed below\.",
        replacement + "\n\nCandidate interventions are listed below.",
        prompt,
        flags=re.S,
    )
    if n_repl != 1:
        raise RuntimeError(f"failed to replace state block for {action_row.get('source_id')}; replacements={n_repl}")
    out["messages"][1]["content"] = new_prompt
    return out


def action_to_act(action: str | None, mapping: dict[str, str]) -> str | None:
    if not action:
        return None
    if action in mapping:
        return mapping[action]
    if "_" in action:
        prefix = action.split("_", 1)[0]
        if prefix in FIVE_ACTS:
            return prefix
    return action if action in FIVE_ACTS else None


def gold_stage(user_row: dict[str, Any]) -> str | None:
    try:
        return parse_user_intent_output(primary_structured_block(user_row["messages"][2]["content"]))["aida_stage"]
    except MalformedOutputError:
        return None


def load_eval_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    user_rows = {row["source_id"]: row for row in read_jsonl(args.user_intent_jsonl)}
    rows = []
    wanted_domains = set(args.domains.split(",")) if args.domains else None
    for action in read_jsonl(args.action_jsonl):
        domain = action.get("domain") or ("target" if str(action.get("source_id", "")).startswith("target_") else "general")
        if wanted_domains and domain not in wanted_domains:
            continue
        source_id = action["source_id"]
        if source_id not in user_rows:
            raise RuntimeError(f"missing user_intent row for {source_id}")
        rows.append({"source_id": source_id, "domain": domain, "eval_id": action.get("eval_id") or source_id, "user": user_rows[source_id], "action": action})
    if args.limit is not None:
        rows = rows[: args.limit]
    return rows


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
    model = PeftModel.from_pretrained(base, args.checkpoint)
    model.eval()
    return model, processor


def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_eval_rows(args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    model, processor = load_model(args)

    step1_rows: list[dict[str, Any]] = []
    step2_rows: list[dict[str, Any]] = []
    start = time.time()

    for index, item in enumerate(rows, start=1):
        source_id = item["source_id"]
        user_row = item["user"]
        action_row = item["action"]
        domain = item["domain"]
        eval_id = item["eval_id"]
        gold_act = action_row["gold_best_action"]
        gold_aida_stage = gold_stage(user_row)

        step1_record: dict[str, Any] = {
            "sample_id": eval_id,
            "source_id": source_id,
            "domain": domain,
            "gold_stage": gold_aida_stage,
            "raw_output": None,
            "parse_success": False,
        }
        step2_record: dict[str, Any] = {
            "sample_id": eval_id,
            "source_id": source_id,
            "domain": domain,
            "gold_best_action": gold_act,
            "gold_stage": gold_aida_stage,
            "step1_parse_success": False,
            "step1_stage_correct": False,
            "raw_output": None,
            "parse_success": False,
            "pred_act": None,
            "correct": False,
        }

        try:
            images = resolve_images(user_row["images"], source_id=source_id)
            raw_state = generate_one(model, processor, user_row, images, args, max_new_tokens=args.max_new_tokens_state)
            parsed_state = parse_user_intent_output(primary_structured_block(raw_state))
            visual = parsed_state["visual_state"]
            bdi = parsed_state["bdi"]
            step1_record.update(
                {
                    "raw_output": raw_state,
                    "predicted_stage": parsed_state["aida_stage"],
                    "predicted_intent_label": parsed_state["intent_label"],
                    "predicted_belief": bdi["belief"],
                    "predicted_desire": bdi["desire"],
                    "predicted_intention": bdi["intention"],
                    "predicted_observable_evidence": visual["summary"],
                    "predicted_engagement_pattern": visual["engagement_pattern"],
                    "predicted_gaze_and_attention": visual["gaze_and_attention"],
                    "predicted_body_and_hands": visual["body_and_hands"],
                    "parse_success": True,
                    "stage_correct": parsed_state["aida_stage"] == gold_aida_stage,
                }
            )
            step2_record["step1_parse_success"] = True
            step2_record["step1_stage_correct"] = parsed_state["aida_stage"] == gold_aida_stage
        except Exception as exc:  # noqa: BLE001 - persisted run artifact
            step1_record["error"] = f"{type(exc).__name__}: {exc}"
            step2_record["error"] = "step1_parse_failed"
            step1_rows.append(step1_record)
            step2_rows.append(step2_record)
            maybe_write_partials(args, step1_rows, step2_rows)
            log_progress(index, len(rows), start, step1_rows, step2_rows)
            if step1_parse_rate(step1_rows, processed=index) < 0.5 and index >= min(10, len(rows)):
                raise RuntimeError("Step 1 parse rate below 0.5; stopping") from exc
            continue

        try:
            action_images = resolve_images(action_row["images"], source_id=source_id)
            e2e_action_row = action_row_with_predicted_state(action_row, parsed_state)
            raw_action = generate_one(model, processor, e2e_action_row, action_images, args, max_new_tokens=args.max_new_tokens_action)
            mapping = action_row.get("meta", {}).get("candidate_action_acts", {})
            parsed_action = parse_action_output(primary_structured_block(raw_action), valid_actions=mapping.keys(), five_act_only=True)
            pred_act = action_to_act(parsed_action.get("chosen"), mapping)
            step2_record.update(
                {
                    "raw_output": raw_action,
                    "parsed": parsed_action,
                    "parse_success": pred_act in FIVE_ACTS,
                    "pred_act": pred_act,
                    "correct": pred_act == gold_act,
                }
            )
        except Exception as exc:  # noqa: BLE001 - persisted run artifact
            step2_record["error"] = f"{type(exc).__name__}: {exc}"
            if step2_parse_rate(step2_rows + [step2_record], processed=index) < 0.5 and index >= min(10, len(rows)):
                step1_rows.append(step1_record)
                step2_rows.append(step2_record)
                maybe_write_partials(args, step1_rows, step2_rows)
                raise RuntimeError("Step 2 parse rate below 0.5; stopping") from exc

        step1_rows.append(step1_record)
        step2_rows.append(step2_record)
        maybe_write_partials(args, step1_rows, step2_rows)
        log_progress(index, len(rows), start, step1_rows, step2_rows)
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

    summary = summarize(rows, step1_rows, step2_rows, args)
    write_jsonl(args.out_dir / "step1_predicted_state.jsonl", step1_rows)
    write_jsonl(args.out_dir / "step2_predicted_action.jsonl", step2_rows)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(summary), encoding="utf-8")
    return summary


def maybe_write_partials(args: argparse.Namespace, step1_rows: list[dict[str, Any]], step2_rows: list[dict[str, Any]]) -> None:
    if not args.partial_every:
        return
    if len(step1_rows) % args.partial_every == 0:
        write_jsonl(args.out_dir / "step1_predicted_state.jsonl.partial", step1_rows)
        write_jsonl(args.out_dir / "step2_predicted_action.jsonl.partial", step2_rows)


def log_progress(index: int, total: int, start: float, step1_rows: list[dict[str, Any]], step2_rows: list[dict[str, Any]]) -> None:
    if index == 1 or index % 5 == 0 or index == total:
        print(
            json.dumps(
                {
                    "event": "e2e_progress",
                    "index": index,
                    "total": total,
                    "step1_parse_rate": step1_parse_rate(step1_rows, processed=index),
                    "step2_parse_rate": step2_parse_rate(step2_rows, processed=index),
                    "elapsed_sec": round(time.time() - start, 1),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )


def step1_parse_rate(rows: list[dict[str, Any]], *, processed: int | None = None) -> float:
    denom = processed if processed is not None else len(rows)
    return sum(1 for row in rows if row.get("parse_success")) / denom if denom else 0.0


def step2_parse_rate(rows: list[dict[str, Any]], *, processed: int | None = None) -> float:
    denom = processed if processed is not None else len(rows)
    return sum(1 for row in rows if row.get("parse_success")) / denom if denom else 0.0


def summarize(eval_rows: list[dict[str, Any]], step1_rows: list[dict[str, Any]], step2_rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    domains = sorted({row["domain"] for row in eval_rows})
    summary: dict[str, Any] = {
        "artifact": "piwm_end_to_end_best_action_eval",
        "model": str(args.model),
        "checkpoint": str(args.checkpoint),
        "user_intent_jsonl": str(args.user_intent_jsonl),
        "action_jsonl": str(args.action_jsonl),
        "n_samples": len(eval_rows),
        "domains": domains,
        "step1_parse_rate": step1_parse_rate(step1_rows),
        "step2_parse_rate": step2_parse_rate(step2_rows),
        "by_domain": {},
        "stage_error_propagation": {},
    }
    for domain in domains + ["combined"]:
        action_rows = step2_rows if domain == "combined" else [row for row in step2_rows if row["domain"] == domain]
        state_rows = step1_rows if domain == "combined" else [row for row in step1_rows if row["domain"] == domain]
        summary["by_domain"][domain] = metrics_for_rows(action_rows)
        summary["by_domain"][domain]["step1_parse_rate"] = step1_parse_rate(state_rows)
    for value, name in [(True, "stage_correct"), (False, "stage_incorrect")]:
        rows = [row for row in step2_rows if row.get("step1_parse_success") and row.get("step1_stage_correct") is value]
        summary["stage_error_propagation"][name] = {
            "n_samples": len(rows),
            "best_action_f1": macro_f1([(row.get("pred_act") if row.get("parse_success") else None, row["gold_best_action"]) for row in rows], FIVE_ACTS)
            if rows
            else None,
        }
    return summary


def metrics_for_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [(row.get("pred_act") if row.get("parse_success") else None, row["gold_best_action"]) for row in rows]
    return {
        "n_samples": len(rows),
        "macro_f1": macro_f1(pairs, FIVE_ACTS),
        "parse_rate": step2_parse_rate(rows),
        "prediction_counts": dict(sorted(Counter(pred or "PARSE_FAIL" for pred, _ in pairs).items())),
        "per_class": per_class_metrics(pairs, FIVE_ACTS),
    }


def per_class_metrics(pairs: list[tuple[str | None, str]], labels: tuple[str, ...]) -> dict[str, dict[str, float]]:
    out = {}
    for label in labels:
        tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
        fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
        fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        out[label] = {"precision": precision, "recall": recall, "f1": f1, "support": float(sum(1 for _, gold in pairs if gold == label))}
    return out


def macro_f1(pairs: list[tuple[str | None, str]], labels: tuple[str, ...]) -> float | None:
    if not pairs:
        return None
    f1s = [per_class_metrics(pairs, labels)[label]["f1"] for label in labels]
    return sum(f1s) / len(f1s)


def fmt(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def render_report(summary: dict[str, Any]) -> str:
    target = summary["by_domain"].get("target") or summary["by_domain"].get("combined")
    combined = summary["by_domain"].get("combined")
    lines = [
        "# PIWM End-to-End Best-Action Evaluation",
        "",
        f"- eval date: 2026-05-26",
        f"- samples: {summary['n_samples']} ({', '.join(summary['domains'])})",
        f"- checkpoint: `{summary['checkpoint']}`",
        f"- Step 1 raw: `reports/end_to_end_eval_20260525/step1_predicted_state.jsonl`",
        f"- Step 2 raw: `reports/end_to_end_eval_20260525/step2_predicted_action.jsonl`",
        "",
        "## Main Target Result",
        "",
        "| Setting | Macro F1 | Parse rate (step 1) | Parse rate (step 2) |",
        "|---|---:|---:|---:|",
        "| PIWM with gold state (Dim 4 original) | 0.641 | - | 0.933 |",
        f"| PIWM end-to-end (自推 state) | {fmt(target['macro_f1'])} | {fmt(target['step1_parse_rate'])} | {fmt(target['parse_rate'])} |",
        "| Random | 0.414 | - | - |",
        "",
        "## Error Propagation",
        "",
        "| Subset | N samples | Best-action F1 |",
        "|---|---:|---:|",
    ]
    for key, label in [("stage_correct", "Step 1 stage 预测正确"), ("stage_incorrect", "Step 1 stage 预测错误")]:
        row = summary["stage_error_propagation"][key]
        lines.append(f"| {label} | {row['n_samples']} | {fmt(row['best_action_f1'])} |")
    lines.extend(
        [
            "",
            "## Per-Action Breakdown (Combined Evaluated Set)",
            "",
            "| act | precision | recall | F1 | support |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for act in FIVE_ACTS:
        row = combined["per_class"][act]
        lines.append(f"| {act} | {row['precision']:.3f} | {row['recall']:.3f} | {row['f1']:.3f} | {int(row['support'])} |")
    if "general" in summary["by_domain"]:
        lines.extend(
            [
                "",
                "## Optional 60-Sample Breakdown",
                "",
                "| Domain | N | Macro F1 | Step 1 parse rate | Step 2 parse rate | Modal prediction |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        for domain in ["target", "general", "combined"]:
            row = summary["by_domain"][domain]
            counts = Counter(row["prediction_counts"])
            modal, count = counts.most_common(1)[0] if counts else ("-", 0)
            lines.append(
                f"| {domain} | {row['n_samples']} | {fmt(row['macro_f1'])} | "
                f"{fmt(row['step1_parse_rate'])} | {fmt(row['parse_rate'])} | {modal} / {count} / {row['n_samples']} |"
            )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--user-intent-jsonl", type=Path, default=DEFAULT_USER_INTENT)
    parser.add_argument("--action-jsonl", type=Path, default=DEFAULT_ACTION)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--domains", default="target,general", help="Comma-separated domains to evaluate, e.g. target or target,general.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-new-tokens-state", type=int, default=256)
    parser.add_argument("--max-new-tokens-action", type=int, default=256)
    parser.add_argument("--max-pixels", type=int, default=None)
    parser.add_argument("--torch-dtype", choices=["bfloat16", "float16"], default="bfloat16")
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--partial-every", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    summary = run_eval(parse_args())
    print(json.dumps({k: v for k, v in summary.items() if k not in {"by_domain", "stage_error_propagation"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
