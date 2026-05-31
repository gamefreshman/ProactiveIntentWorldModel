"""Prepare, run, and summarize PIWM closed-model best-action evaluation."""

from __future__ import annotations

import argparse
import base64
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_infer.parsers import MalformedOutputError, parse_action_output
from piwm_train.ms_swift_adapter import build_ms_swift_record

from scripts.build_two_stage_training_and_eval import _action_example


LEGACY_TARGET_INPUT = (
    REPO_ROOT
    / "data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl"
)
TARGET_INPUT = REPO_ROOT / "data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl"
GENERAL_SLICE = REPO_ROOT / "reports/general_domain_eval_seed42.jsonl"
GENERAL_POLICY = REPO_ROOT / "data/official/piwm_train_synth_v2/policy_preference.jsonl"
EVAL_SET = REPO_ROOT / "reports/closed_model_eval_set_60.jsonl"
RAW_ROOT = REPO_ROOT / "reports/closed_model_eval_20260525"
MAIN_TABLE = REPO_ROOT / "reports/2026-05-25_closed_model_best_action_main_table.md"
LOCAL_STATUS = REPO_ROOT / "reports/closed_model_eval_20260525/local_model_status.json"
LOCAL_ABS_PREFIX = "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel"
LOCAL_RUN_FILES = {
    "piwm_main": RAW_ROOT / "local_model_runs/piwm_main_best_action_60.json",
    "stage1_only": RAW_ROOT / "local_model_runs/stage1_only_best_action_60.json",
    "zero_shot_qwen25vl7b": RAW_ROOT / "local_model_runs/zero_shot_qwen25vl7b_best_action_60.json",
}

FIVE_ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")
MODEL_IDS = {
    "gpt-4o": "openai/gpt-4o",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "claude-sonnet-4.6": "anthropic/claude-sonnet-4-6",
    "grok-3": "x-ai/grok-3",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def tag_value(text: str, tag: str) -> str | None:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text or "", flags=re.S)
    return match.group(1).strip() if match else None


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


def gold_act(row: dict[str, Any]) -> str | None:
    meta = row.get("meta") or {}
    if meta.get("best_act"):
        return str(meta["best_act"])
    target = row["messages"][2]["content"]
    parsed = parse_action_output(target, valid_actions=meta.get("candidate_action_acts", {}).keys(), five_act_only=True)
    return action_to_act(parsed.get("chosen"), meta.get("candidate_action_acts", {}))


def candidate_actions(row: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = row.get("meta", {}).get("candidate_action_acts", {})
    out = []
    for label, act in mapping.items():
        out.append({"label": label, "act": act})
    return out


def customer_state_from_prompt(row: dict[str, Any]) -> dict[str, str | None]:
    prompt = row["messages"][1]["content"].replace("<image>", "")
    fields = {
        "stage": r"- stage:\s*(.*)",
        "intent_label": r"- intent_label:\s*(.*)",
        "visible_evidence": r"- visible evidence:\s*(.*)",
        "engagement_pattern": r"- engagement pattern:\s*(.*)",
        "gaze_and_attention": r"- gaze and attention:\s*(.*)",
        "body_and_hands": r"- body and hands:\s*(.*)",
        "belief": r"- belief:\s*(.*)",
        "desire": r"- desire:\s*(.*)",
        "intention": r"- intention:\s*(.*)",
    }
    values: dict[str, str | None] = {}
    for key, pattern in fields.items():
        match = re.search(pattern, prompt)
        values[key] = match.group(1).strip() if match else None
    return values


def prepare_eval_set() -> dict[str, Any]:
    target_input = LEGACY_TARGET_INPUT if LEGACY_TARGET_INPUT.exists() else TARGET_INPUT
    target_rows = read_jsonl(target_input)
    for row in target_rows:
        row["images"] = _remap_images(row)
        row["domain"] = "target"
        row["gold_best_action"] = gold_act(row)
        row["candidate_actions"] = candidate_actions(row)
        row["gold_customer_state"] = customer_state_from_prompt(row)

    general_ids = [row["source_id"] for row in read_jsonl(GENERAL_SLICE)]
    general_id_set = set(general_ids)
    policy_by_id: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(GENERAL_POLICY):
        state_id = row.get("state_id")
        if state_id in general_id_set:
            policy_by_id[state_id] = row
    missing = [state_id for state_id in general_ids if state_id not in policy_by_id]
    if missing:
        raise RuntimeError(f"missing general policy rows: {missing}")

    general_rows: list[dict[str, Any]] = []
    for state_id in general_ids:
        example = _action_example(policy_by_id[state_id])
        row = build_ms_swift_record(example, root=REPO_ROOT, validate_images=False)
        row["images"] = _remap_images(row)
        row["domain"] = "general"
        row["gold_best_action"] = gold_act(row)
        row["candidate_actions"] = candidate_actions(row)
        row["gold_customer_state"] = customer_state_from_prompt(row)
        general_rows.append(row)

    rows = target_rows + general_rows
    for index, row in enumerate(rows, start=1):
        row["eval_id"] = f"{row['domain']}_{index:03d}_{row['source_id']}"

    _validate_eval_rows(rows)
    write_jsonl(EVAL_SET, rows)
    summary = {
        "artifact": "closed_model_best_action_eval_set",
        "output_jsonl": str(EVAL_SET.relative_to(REPO_ROOT)),
        "target_input": str(target_input.relative_to(REPO_ROOT)),
        "n_rows": len(rows),
        "domain_counts": dict(sorted(Counter(row["domain"] for row in rows).items())),
        "gold_by_domain": {
            domain: dict(sorted(Counter(row["gold_best_action"] for row in rows if row["domain"] == domain).items()))
            for domain in sorted({row["domain"] for row in rows})
        },
        "missing_images": _missing_images(rows),
    }
    summary_path = EVAL_SET.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def _validate_eval_rows(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 60:
        raise RuntimeError(f"expected 60 rows, found {len(rows)}")
    for row in rows:
        if row.get("task") != "action_selection_5act":
            raise RuntimeError(f"non action_selection_5act row: {row.get('source_id')} {row.get('task')}")
        if len(row.get("images", [])) != 3:
            raise RuntimeError(f"expected 3 images for {row.get('source_id')}, found {len(row.get('images', []))}")
        if row.get("gold_best_action") not in FIVE_ACTS:
            raise RuntimeError(f"bad gold act for {row.get('source_id')}: {row.get('gold_best_action')}")
        acts = [item["act"] for item in row.get("candidate_actions", [])]
        if not acts or any(act not in FIVE_ACTS for act in acts):
            raise RuntimeError(f"bad candidates for {row.get('source_id')}: {acts}")
        if row["gold_best_action"] not in acts:
            raise RuntimeError(f"gold not in candidates for {row.get('source_id')}: {row['gold_best_action']} not in {acts}")


def _missing_images(rows: list[dict[str, Any]]) -> list[str]:
    missing = []
    for row in rows:
        for image in row.get("images", []):
            if not Path(image).exists():
                missing.append(image)
    return missing


def _remap_images(row: dict[str, Any]) -> list[str]:
    source_id = str(row.get("source_id") or "")
    images = row.get("images") or []
    return [_resolve_image(image, source_id=source_id, frame_index=index) for index, image in enumerate(images)]


def _resolve_image(image: str, *, source_id: str, frame_index: int) -> str:
    path = Path(image)
    for candidate in _image_candidates(path, source_id=source_id, frame_index=frame_index):
        if candidate.exists():
            return candidate.resolve().as_posix()
    return _repo_relative_candidate(path).resolve().as_posix()


def _image_candidates(path: Path, *, source_id: str, frame_index: int) -> list[Path]:
    candidates = [path]
    candidates.append(_repo_relative_candidate(path))
    frame_name = f"{frame_index:03d}{path.suffix or '.jpg'}"
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


def _repo_relative_candidate(path: Path) -> Path:
    text = path.as_posix()
    if text.startswith(LOCAL_ABS_PREFIX + "/"):
        return REPO_ROOT / text[len(LOCAL_ABS_PREFIX) + 1 :]
    if path.is_absolute():
        try:
            return REPO_ROOT / path.relative_to(REPO_ROOT)
        except ValueError:
            return path
    return REPO_ROOT / path


def openrouter_messages(row: dict[str, Any]) -> list[dict[str, Any]]:
    system = row["messages"][0]["content"]
    text = row["messages"][1]["content"].replace("<image>", "").strip()
    content: list[dict[str, Any]] = []
    for image in row["images"]:
        content.append({"type": "image_url", "image_url": {"url": image_data_url(Path(image))}})
    content.append({"type": "text", "text": text})
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": content},
    ]


def image_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def call_openrouter(
    *,
    model_id: str,
    row: dict[str, Any],
    api_key: str,
    max_tokens: int,
    timeout: int,
) -> dict[str, Any]:
    payload = {
        "model": model_id,
        "messages": openrouter_messages(row),
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/piwm-local/eval",
            "X-Title": "PIWM closed model best-action eval",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    raw = body["choices"][0]["message"]["content"]
    return {
        "raw": raw,
        "usage": body.get("usage"),
        "id": body.get("id"),
        "model": body.get("model") or model_id,
        "response": body,
    }


def run_openrouter(args: argparse.Namespace) -> dict[str, Any]:
    rows = read_jsonl(args.eval_set)
    _assert_image_files_available(rows)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    models = args.models or list(MODEL_IDS)
    summary: dict[str, Any] = {}
    for model_name in models:
        model_id = MODEL_IDS.get(model_name, model_name)
        model_dir = RAW_ROOT / safe_name(model_name)
        model_dir.mkdir(parents=True, exist_ok=True)
        raw_path = model_dir / "raw_outputs.jsonl"
        existing = _load_existing_outputs(raw_path)
        outputs: list[dict[str, Any]] = [existing[row["eval_id"]] for row in rows if row["eval_id"] in existing]
        if len(outputs) == len(rows) and not args.force:
            summary[model_name] = {"status": "already_complete", "raw_outputs": str(raw_path.relative_to(REPO_ROOT))}
            continue

        with raw_path.open("a", encoding="utf-8") as handle:
            for index, row in enumerate(rows, start=1):
                if not args.force and row["eval_id"] in existing:
                    continue
                record = {
                    "eval_id": row["eval_id"],
                    "source_id": row["source_id"],
                    "domain": row["domain"],
                    "model_name": model_name,
                    "requested_model": model_id,
                    "gold_act": row["gold_best_action"],
                    "candidate_action_acts": row.get("meta", {}).get("candidate_action_acts", {}),
                }
                try:
                    result = _call_with_rate_limit_retry(
                        model_id=model_id,
                        row=row,
                        api_key=api_key,
                        max_tokens=args.max_tokens,
                        timeout=args.timeout,
                    )
                    raw = result["raw"]
                    parsed = parse_action_output(
                        raw,
                        valid_actions=row.get("meta", {}).get("candidate_action_acts", {}).keys(),
                        five_act_only=True,
                    )
                    pred_act = action_to_act(parsed.get("chosen"), row.get("meta", {}).get("candidate_action_acts", {}))
                    record.update(
                        {
                            "status": "ok",
                            "actual_model": result["model"],
                            "raw_output": raw,
                            "parsed": parsed,
                            "pred_act": pred_act,
                            "parse_ok": True,
                            "correct": pred_act == row["gold_best_action"],
                            "usage": result.get("usage"),
                            "openrouter_id": result.get("id"),
                        }
                    )
                except MalformedOutputError as exc:
                    record.update({"status": "parse_failed", "parse_ok": False, "pred_act": None, "error": str(exc)})
                except Exception as exc:  # noqa: BLE001 - stored as per-row run artifact
                    record.update({"status": "api_failed", "parse_ok": False, "pred_act": None, "error": f"{type(exc).__name__}: {exc}"})
                    if index == 1:
                        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                        summary[model_name] = {
                            "status": "model_unavailable_or_first_call_failed",
                            "raw_outputs": str(raw_path.relative_to(REPO_ROOT)),
                            "error": record["error"],
                        }
                        break
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                if args.progress_every and (index == 1 or index % args.progress_every == 0 or index == len(rows)):
                    print(json.dumps({"event": "openrouter_progress", "model": model_name, "index": index, "total": len(rows)}, ensure_ascii=False), flush=True)
                if args.sleep:
                    time.sleep(args.sleep)
            else:
                summary[model_name] = {"status": "complete", "raw_outputs": str(raw_path.relative_to(REPO_ROOT))}
    summary_path = RAW_ROOT / "openrouter_run_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def _assert_image_files_available(rows: list[dict[str, Any]]) -> None:
    missing = _missing_images(rows)
    if missing:
        preview = "\n".join(missing[:20])
        suffix = "" if len(missing) <= 20 else f"\n... {len(missing) - 20} more"
        raise RuntimeError(f"missing image files; aborting before OpenRouter calls:\n{preview}{suffix}")


def _call_with_rate_limit_retry(**kwargs: Any) -> dict[str, Any]:
    delay = 3.0
    for attempt in range(1, 4):
        try:
            return call_openrouter(**kwargs)
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"HTTP {exc.code}: {text[:1000]}") from exc
        except urllib.error.URLError as exc:
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(str(exc)) from exc
    raise RuntimeError("unreachable retry state")


def _load_existing_outputs(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out = {}
    for row in read_jsonl(path):
        out[row["eval_id"]] = row
    return out


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def summarize(args: argparse.Namespace) -> dict[str, Any]:
    rows = read_jsonl(args.eval_set)
    row_by_id = {row["eval_id"]: row for row in rows}
    model_rows: dict[str, list[dict[str, Any]]] = {}
    for model_name in args.models or list(MODEL_IDS):
        raw_path = RAW_ROOT / safe_name(model_name) / "raw_outputs.jsonl"
        model_rows[model_name] = read_jsonl(raw_path) if raw_path.exists() else []

    local_status = json.loads(LOCAL_STATUS.read_text(encoding="utf-8")) if LOCAL_STATUS.exists() else {}
    local_model_rows = {name: local_outputs_for_model(rows, path) for name, path in LOCAL_RUN_FILES.items()}
    openrouter_status_path = RAW_ROOT / "openrouter_run_summary.json"
    openrouter_status = json.loads(openrouter_status_path.read_text(encoding="utf-8")) if openrouter_status_path.exists() else {}
    random_summary = random_baseline(rows, seed=42)
    report = render_report(rows, row_by_id, model_rows, local_status, local_model_rows, openrouter_status, random_summary)
    MAIN_TABLE.write_text(report, encoding="utf-8")
    summary = {
        "artifact": "closed_model_best_action_summary",
        "main_table": str(MAIN_TABLE.relative_to(REPO_ROOT)),
        "models": {name: metrics_for_outputs(row_by_id, outs) for name, outs in model_rows.items()},
        "local_models": {name: metrics_for_outputs(row_by_id, outs) for name, outs in local_model_rows.items()},
        "openrouter_status": openrouter_status,
        "random": random_summary,
        "local_status": local_status,
    }
    (RAW_ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def local_outputs_for_model(rows: list[dict[str, Any]], path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    result = json.loads(path.read_text(encoding="utf-8"))
    row_by_source = {row["source_id"]: row for row in rows}
    outputs: list[dict[str, Any]] = []
    for record in result.get("outputs", []):
        row = row_by_source.get(record.get("source_id"))
        if row is None:
            continue
        pred_act = None
        if record.get("parse_ok"):
            pred_act = action_to_act((record.get("parsed") or {}).get("chosen"), row.get("meta", {}).get("candidate_action_acts", {}))
        outputs.append(
            {
                "eval_id": row["eval_id"],
                "pred_act": pred_act,
                "parse_ok": bool(record.get("parse_ok") and pred_act in FIVE_ACTS),
                "raw_output": record.get("prediction"),
                "source_result": str(path.relative_to(REPO_ROOT)),
            }
        )
    return outputs


def random_baseline(rows: list[dict[str, Any]], *, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    outputs = []
    for row in rows:
        acts = [item["act"] for item in row.get("candidate_actions", [])]
        pred = rng.choice(acts) if acts else "Hold"
        outputs.append({"eval_id": row["eval_id"], "pred_act": pred, "parse_ok": True})
    return metrics_for_outputs({row["eval_id"]: row for row in rows}, outputs)


def metrics_for_outputs(row_by_id: dict[str, dict[str, Any]], outputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {row.get("eval_id"): row for row in outputs}
    pairs_by_domain: dict[str, list[tuple[str | None, str]]] = {"target": [], "general": [], "combined": []}
    parse_ok = 0
    total = 0
    pred_counts: Counter[str] = Counter()
    for eval_id, gold_row in row_by_id.items():
        out = by_id.get(eval_id, {})
        pred = out.get("pred_act") if out.get("parse_ok") else None
        gold = gold_row["gold_best_action"]
        domain = gold_row["domain"]
        pairs_by_domain[domain].append((pred, gold))
        pairs_by_domain["combined"].append((pred, gold))
        total += 1
        if out.get("parse_ok"):
            parse_ok += 1
        pred_counts[pred or "PARSE_FAIL"] += 1
    return {
        "target_macro_f1": macro_f1(pairs_by_domain["target"], labels=FIVE_ACTS),
        "general_macro_f1": macro_f1(pairs_by_domain["general"], labels=FIVE_ACTS),
        "combined_macro_f1": macro_f1(pairs_by_domain["combined"], labels=FIVE_ACTS),
        "parse_rate": parse_ok / total if total else None,
        "prediction_counts": dict(sorted(pred_counts.items())),
        "per_class": per_class_metrics(pairs_by_domain["combined"], labels=FIVE_ACTS),
        "n_outputs": len(outputs),
    }


def macro_f1(pairs: list[tuple[str | None, str]], *, labels: tuple[str, ...]) -> float:
    scores = [per_label(pairs, label)["f1"] for label in labels]
    return sum(scores) / len(scores)


def per_class_metrics(pairs: list[tuple[str | None, str]], *, labels: tuple[str, ...]) -> dict[str, dict[str, float]]:
    return {label: per_label(pairs, label) for label in labels}


def per_label(pairs: list[tuple[str | None, str]], label: str) -> dict[str, float]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "support": float(sum(1 for _, gold in pairs if gold == label))}


def render_report(
    rows: list[dict[str, Any]],
    row_by_id: dict[str, dict[str, Any]],
    model_rows: dict[str, list[dict[str, Any]]],
    local_status: dict[str, Any],
    local_model_rows: dict[str, list[dict[str, Any]]],
    openrouter_status: dict[str, Any],
    random_summary: dict[str, Any],
) -> str:
    lines = [
        "# Closed Model Best-Action Main Table",
        "",
        f"- eval set: `{EVAL_SET.relative_to(REPO_ROOT)}`",
        f"- n: {len(rows)} (target 30 + general 30)",
        "- closed-model inference: temperature=0, one call per sample, parse failures counted as wrong",
        "",
        "| 模型 | target 30 F1 | general 30 F1 | combined 60 F1 | parse rate | modal prediction |",
        "|---|---:|---:|---:|---:|---|",
    ]
    display = [
        ("PIWM 主模型", None, "piwm_main"),
        ("Stage-1 only", None, "stage1_only"),
        ("Zero-shot Qwen2.5-VL-7B", None, "zero_shot_qwen25vl7b"),
        ("GPT-4o", "gpt-4o", None),
        ("Gemini 2.5 Flash", "gemini-2.5-flash", None),
        ("Claude Sonnet 4.6", "claude-sonnet-4.6", None),
        ("Grok-3", "grok-3", None),
        ("Random", None, None),
    ]
    for label, closed_name, local_name in display:
        if label == "Random":
            metrics = random_summary
            note = modal_prediction(metrics, total=60)
            lines.append(f"| {label} | {fmt(metrics['target_macro_f1'])} | {fmt(metrics['general_macro_f1'])} | {fmt(metrics['combined_macro_f1'])} | {fmt(metrics['parse_rate'])} | {note} |")
            continue
        if closed_name:
            status = openrouter_status.get(closed_name, {})
            outs = model_rows.get(closed_name, [])
            if status.get("status") == "model_unavailable_or_first_call_failed" and len(outs) < len(rows):
                lines.append(f"| {label} | 未跑 | 未跑 | 未跑 | - | {status_note(status)} |")
            else:
                metrics = metrics_for_outputs(row_by_id, outs)
                note = modal_prediction(metrics, total=60) if outs else "未跑或无 raw_outputs"
                lines.append(f"| {label} | {fmt(metrics['target_macro_f1'])} | {fmt(metrics['general_macro_f1'])} | {fmt(metrics['combined_macro_f1'])} | {fmt(metrics['parse_rate'])} | {note} |")
            continue
        outs = local_model_rows.get(local_name or "", [])
        if outs:
            metrics = metrics_for_outputs(row_by_id, outs)
            note = modal_prediction(metrics, total=60)
            lines.append(f"| {label} | {fmt(metrics['target_macro_f1'])} | {fmt(metrics['general_macro_f1'])} | {fmt(metrics['combined_macro_f1'])} | {fmt(metrics['parse_rate'])} | {note} |")
        else:
            status = local_status.get(local_name or "", {})
            reason = status.get("reason", "未跑：本地模型环境不可用")
            lines.append(f"| {label} | 未跑 | 未跑 | 未跑 | - | {reason} |")
    lines.extend(["", "## Per-Class Breakdown", ""])
    for label, closed_name, local_name in display:
        if label == "Random":
            metrics = random_summary
        elif closed_name:
            status = openrouter_status.get(closed_name, {})
            if status.get("status") == "model_unavailable_or_first_call_failed" and len(model_rows.get(closed_name, [])) < len(rows):
                continue
            metrics = metrics_for_outputs(row_by_id, model_rows.get(closed_name, []))
            if not model_rows.get(closed_name):
                continue
        else:
            outs = local_model_rows.get(local_name or "", [])
            if not outs:
                continue
            metrics = metrics_for_outputs(row_by_id, outs)
        lines.extend([f"### {label}", "", "| act | precision | recall | F1 | support |", "|---|---:|---:|---:|---:|"])
        for act, values in metrics["per_class"].items():
            lines.append(
                f"| {act} | {fmt(values['precision'])} | {fmt(values['recall'])} | {fmt(values['f1'])} | {int(values['support'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def status_note(status: dict[str, Any]) -> str:
    error = str(status.get("error") or status.get("status") or "API 不可用")
    if "HTTP 402" in error:
        return "未跑：OpenRouter 余额不足 / HTTP 402"
    if "deprecated" in error or "HTTP 404" in error:
        return "未跑：OpenRouter 型号不可用 / HTTP 404"
    return f"未跑：{error[:120]}"


def modal_prediction(metrics: dict[str, Any], *, total: int) -> str:
    counts = metrics.get("prediction_counts") or {}
    if not counts:
        return "-"
    act, count = max(counts.items(), key=lambda item: item[1])
    return f"{act} / {count} / {total}"


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def check_local_status() -> dict[str, Any]:
    import importlib.util

    torch_available = importlib.util.find_spec("torch") is not None
    piwm_ck = Path("/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500")
    stage1_ck = Path("/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432")
    status = {
        "piwm_main": {
            "status": "not_run",
            "reason": "未跑：当前工作机缺少 torch，且 PIWM checkpoint 路径不可用" if not torch_available or not piwm_ck.exists() else "ready_but_not_run",
            "checkpoint": str(piwm_ck),
        },
        "stage1_only": {
            "status": "not_run",
            "reason": "未跑：当前工作机缺少 torch，且 Stage-1 checkpoint 路径不可用" if not torch_available or not stage1_ck.exists() else "ready_but_not_run",
            "checkpoint": str(stage1_ck),
        },
        "zero_shot_qwen25vl7b": {
            "status": "not_run",
            "reason": "未跑：当前工作机缺少 torch/transformers 本地推理环境；zero-shot 需要 --no-lora/checkpoint=None 方式在可用 GPU 环境运行",
            "checkpoint": None,
        },
    }
    LOCAL_STATUS.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare")
    run = sub.add_parser("run-openrouter")
    run.add_argument("--eval-set", type=Path, default=EVAL_SET)
    run.add_argument("--models", nargs="*", default=None)
    run.add_argument("--max-tokens", type=int, default=512)
    run.add_argument("--timeout", type=int, default=120)
    run.add_argument("--sleep", type=float, default=0.0)
    run.add_argument("--progress-every", type=int, default=10)
    run.add_argument("--force", action="store_true")
    sub.add_parser("check-local")
    summ = sub.add_parser("summarize")
    summ.add_argument("--eval-set", type=Path, default=EVAL_SET)
    summ.add_argument("--models", nargs="*", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "prepare":
        print(json.dumps(prepare_eval_set(), ensure_ascii=False, indent=2))
    elif args.cmd == "run-openrouter":
        print(json.dumps(run_openrouter(args), ensure_ascii=False, indent=2))
    elif args.cmd == "check-local":
        print(json.dumps(check_local_status(), ensure_ascii=False, indent=2))
    elif args.cmd == "summarize":
        print(json.dumps(summarize(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
