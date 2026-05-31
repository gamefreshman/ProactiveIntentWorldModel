"""Evaluate closed-source VLMs on PIWM four-scenario best-action tasks.

This runner uses the 302.ai OpenAI-compatible chat-completions API. It reuses
the PIWM prompt text already serialized in local eval JSONL files, replacing
``<image>`` placeholders with API-native image inputs and preserving the same
structured XML output parsers.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_infer.parsers import MalformedOutputError, parse_action_output, parse_user_intent_output

FIVE_ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")
AIDA = ("attention", "interest", "desire", "action")
API_BASE = "https://api.302.ai"

CROSS_ACTION = REPO_ROOT / "reports/closed_model_eval_set_60.jsonl"
USER60 = REPO_ROOT / "reports/rerun_eval_20260525/user_intent_target30_general30_seed42.archive_resolved.server.jsonl"
REAL_ACTION = REPO_ROOT / "reports/real_eval_20260525/real_action_selection_5act.jsonl"
DEFAULT_OUT = REPO_ROOT / "reports/closed_model_eval_full_20260526"
LOCAL_ABS_PREFIX = "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel"
REMOTE_ABS_PREFIX = "/root/lanyun-fs/ProactiveIntentWorldModel"

MODELS = {
    "gemini_2.5_flash": "gemini-2.5-flash",
    "gpt_4o": "gpt-4o",
    "claude_sonnet_4.6": "claude-sonnet-4-6",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith(LOCAL_ABS_PREFIX + "/"):
        return REPO_ROOT / text[len(LOCAL_ABS_PREFIX) + 1 :]
    if text.startswith(REMOTE_ABS_PREFIX + "/"):
        return REPO_ROOT / text[len(REMOTE_ABS_PREFIX) + 1 :]
    p = Path(text)
    if p.is_absolute():
        return p
    return REPO_ROOT / p


def normalize_images(row: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(row, ensure_ascii=False))
    out["images"] = [str(repo_path(path)) for path in out.get("images", [])]
    return out


def data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def api_messages(row: dict[str, Any]) -> list[dict[str, Any]]:
    messages = row["messages"]
    system = messages[0]["content"]
    text = str(messages[1]["content"]).replace("<image>", "").strip()
    content: list[dict[str, Any]] = []
    for image in row.get("images", []):
        image_path = repo_path(image)
        content.append({"type": "image_url", "image_url": {"url": data_url(image_path)}})
    content.append({"type": "text", "text": text})
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": content},
    ]


def call_302ai(
    *,
    api_key: str,
    model_id: str,
    row: dict[str, Any],
    max_tokens: int,
    timeout: int,
    temperature: float,
) -> dict[str, Any]:
    payload = {
        "model": model_id,
        "stream": False,
        "messages": api_messages(row),
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/v1/chat/completions",
        data=data,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
        headers = dict(response.headers.items())
    message = body["choices"][0]["message"]
    return {
        "id": body.get("id"),
        "model": body.get("model") or model_id,
        "raw_output": message.get("content") or "",
        "usage": body.get("usage"),
        "headers": {
            key: value
            for key, value in headers.items()
            if key.lower().startswith(("x-", "cf-", "openai-", "anthropic-", "google-"))
        },
        "response_created": body.get("created"),
        "response_object": body.get("object"),
    }


def call_with_retry(**kwargs: Any) -> dict[str, Any]:
    delay = 2.0
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            return call_302ai(**kwargs)
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {exc.code}: {text[:1200]}")
            if exc.code in {408, 409, 425, 429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise last_error from exc
        except urllib.error.URLError as exc:
            last_error = RuntimeError(str(exc))
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise last_error from exc
    raise RuntimeError(f"retry exhausted: {last_error}")


def action_to_act(chosen: str | None, mapping: dict[str, str]) -> str | None:
    if not chosen:
        return None
    if chosen in mapping:
        return mapping[chosen]
    if "_" in chosen:
        prefix = chosen.split("_", 1)[0]
        if prefix in FIVE_ACTS:
            return prefix
    return chosen if chosen in FIVE_ACTS else None


def gold_action(row: dict[str, Any]) -> str | None:
    if row.get("gold_best_action"):
        return row["gold_best_action"]
    if row.get("meta", {}).get("best_act"):
        return row["meta"]["best_act"]
    if len(row.get("messages", [])) >= 3:
        mapping = row.get("meta", {}).get("candidate_action_acts", {})
        parsed = parse_action_output(row["messages"][2]["content"], valid_actions=mapping.keys(), five_act_only=True)
        return action_to_act(parsed["chosen"], mapping)
    return None


def parse_action_prediction(raw: str, row: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    mapping = row.get("meta", {}).get("candidate_action_acts", {})
    parsed = parse_action_output(raw, valid_actions=mapping.keys(), five_act_only=True)
    pred = action_to_act(parsed.get("chosen"), mapping)
    if pred not in FIVE_ACTS:
        raise MalformedOutputError(f"chosen action maps to invalid act: {pred}")
    return parsed, pred


def macro_f1(pairs: list[tuple[str | None, str | None]], labels: tuple[str, ...] | list[str]) -> float:
    if not labels:
        return 0.0
    return sum(per_label(pairs, label)["f1"] for label in labels) / len(labels)


def per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float]:
    tp = sum(pred == label and gold == label for pred, gold in pairs)
    fp = sum(pred == label and gold != label for pred, gold in pairs)
    fn = sum(pred != label and gold == label for pred, gold in pairs)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "support": sum(1 for _, gold in pairs if gold == label)}


def summarize_action(outputs: list[dict[str, Any]], labels: tuple[str, ...] = FIVE_ACTS) -> dict[str, Any]:
    strict_pairs = [(row.get("pred_act") if row.get("parse_ok") else None, row.get("gold_act")) for row in outputs]
    parsed_pairs = [(row.get("pred_act"), row.get("gold_act")) for row in outputs if row.get("parse_ok")]
    parse_count = sum(bool(row.get("parse_ok")) for row in outputs)
    return {
        "n": len(outputs),
        "parse_rate": parse_count / len(outputs) if outputs else 0.0,
        "macro_f1_strict": macro_f1(strict_pairs, labels),
        "macro_f1_parsed": macro_f1(parsed_pairs, labels) if parsed_pairs else 0.0,
        "prediction_counts": dict(Counter((row.get("pred_act") if row.get("parse_ok") else "PARSE_FAIL") for row in outputs)),
        "per_class_strict": {label: per_label(strict_pairs, label) for label in labels},
    }


def api_usage_sum(outputs: list[dict[str, Any]]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in outputs:
        usage = row.get("usage") or {}
        for key, value in usage.items():
            if isinstance(value, int):
                totals[key] += value
    return dict(totals)


def run_action_scenario(
    *,
    rows: list[dict[str, Any]],
    scenario_name: str,
    out_path: Path,
    model_key: str,
    model_id: str,
    api_key: str,
    max_tokens: int,
    timeout: int,
    temperature: float,
    labels: tuple[str, ...],
    force: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    existing = load_existing(out_path) if not force else {}
    outputs: list[dict[str, Any]] = []
    with out_path.open("a" if not force else "w", encoding="utf-8") as handle:
        for index, base in enumerate(rows, start=1):
            row = normalize_images(base)
            eval_id = row.get("eval_id") or row.get("source_id")
            if eval_id in existing:
                outputs.append(existing[eval_id])
                continue
            record = base_record(row, model_key, model_id, scenario_name, index=index)
            try:
                result = call_with_retry(
                    api_key=api_key,
                    model_id=model_id,
                    row=row,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    temperature=temperature,
                )
                parsed, pred = parse_action_prediction(result["raw_output"], row)
                record.update(result)
                record.update({"status": "ok", "parse_ok": True, "parsed": parsed, "pred_act": pred, "correct": pred == record["gold_act"]})
            except MalformedOutputError as exc:
                record.update({"status": "parse_failed", "parse_ok": False, "error": str(exc)})
            except Exception as exc:  # noqa: BLE001 - raw artifact should capture row failure
                record.update({"status": "api_failed", "parse_ok": False, "error": f"{type(exc).__name__}: {exc}"})
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            outputs.append(record)
            log_progress(model_key, scenario_name, index, len(rows), outputs)
    summary = summarize_action(outputs, labels=labels)
    summary["usage"] = api_usage_sum(outputs)
    return outputs, summary


def base_record(row: dict[str, Any], model_key: str, model_id: str, scenario_name: str, *, index: int) -> dict[str, Any]:
    return {
        "timestamp_utc": now_iso(),
        "scenario": scenario_name,
        "index": index,
        "eval_id": row.get("eval_id") or row.get("source_id"),
        "source_id": row.get("source_id"),
        "domain": row.get("domain"),
        "model_key": model_key,
        "requested_model_id": model_id,
        "api_provider": "302ai",
        "images": [str(repo_path(path)) for path in row.get("images", [])],
        "gold_act": gold_action(row),
        "candidate_action_acts": row.get("meta", {}).get("candidate_action_acts", {}),
        "parse_ok": False,
        "pred_act": None,
    }


def load_existing(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        rows[str(row.get("eval_id"))] = row
    return rows


def log_progress(model_key: str, scenario: str, index: int, total: int, outputs: list[dict[str, Any]]) -> None:
    if index == 1 or index % 10 == 0 or index == total:
        print(
            json.dumps(
                {
                    "event": "closed_model_progress",
                    "model": model_key,
                    "scenario": scenario,
                    "index": index,
                    "total": total,
                    "parse_ok": sum(bool(row.get("parse_ok")) for row in outputs),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )


def tag(raw: str, name: str) -> str | None:
    match = re.search(rf"<{re.escape(name)}>(.*?)</{re.escape(name)}>", raw or "", flags=re.S)
    return match.group(1).strip() if match else None


def parse_state(raw: str) -> dict[str, Any]:
    return parse_user_intent_output(raw)


def state_block(parsed: dict[str, Any]) -> str:
    visual = parsed.get("visual_state") or {}
    bdi = parsed.get("bdi") or {}
    return "\n".join(
        [
            f"- stage: {parsed.get('aida_stage', '')}",
            f"- intent_label: {parsed.get('intent_label', '')}",
            f"- visible evidence: {visual.get('summary', '')}",
            f"- engagement pattern: {visual.get('engagement_pattern', '')}",
            f"- gaze and attention: {visual.get('gaze_and_attention', '')}",
            f"- body and hands: {visual.get('body_and_hands', '')}",
            f"- belief: {bdi.get('belief', '')}",
            f"- desire: {bdi.get('desire', '')}",
            f"- intention: {bdi.get('intention', '')}",
        ]
    )


def replace_state(action_row: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    row = json.loads(json.dumps(action_row, ensure_ascii=False))
    prompt = row["messages"][1]["content"]
    replacement = "The Stage-1 customer-state representation is:\n" + state_block(parsed)
    new_prompt, count = re.subn(
        r"The Stage-1 customer-state representation is:\n.*?\n\nCandidate interventions are listed below\.",
        replacement + "\n\nCandidate interventions are listed below.",
        prompt,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"state replacement failed for {row.get('source_id')}: {count}")
    row["messages"][1]["content"] = new_prompt
    return row


def run_e2e(
    *,
    action_rows: list[dict[str, Any]],
    user_rows: list[dict[str, Any]],
    out_path: Path,
    model_key: str,
    model_id: str,
    api_key: str,
    max_tokens_state: int,
    max_tokens_action: int,
    timeout: int,
    temperature: float,
    force: bool,
) -> dict[str, Any]:
    existing = load_existing(out_path) if not force else {}
    user_by_source = {row["source_id"]: normalize_images(row) for row in user_rows}
    outputs: list[dict[str, Any]] = []
    with out_path.open("a" if not force else "w", encoding="utf-8") as handle:
        for index, base_action in enumerate(action_rows, start=1):
            action = normalize_images(base_action)
            eval_id = action.get("eval_id") or action.get("source_id")
            if eval_id in existing:
                outputs.append(existing[eval_id])
                continue
            source_id = action["source_id"]
            record = base_record(action, model_key, model_id, "target_test_e2e_30", index=index)
            record.update({"step1_parse_ok": False, "step2_parse_ok": False, "step1_stage_correct": False})
            user = user_by_source[source_id]
            try:
                state_result = call_with_retry(
                    api_key=api_key,
                    model_id=model_id,
                    row=user,
                    max_tokens=max_tokens_state,
                    timeout=timeout,
                    temperature=temperature,
                )
                parsed_state = parse_state(state_result["raw_output"])
                gold_stage = tag(user["messages"][2]["content"], "stage") if len(user.get("messages", [])) >= 3 else None
                record.update(
                    {
                        "step1": state_result,
                        "predicted_state": parsed_state,
                        "gold_stage": gold_stage,
                        "step1_parse_ok": True,
                        "step1_stage_correct": parsed_state.get("aida_stage") == gold_stage,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                record.update({"status": "step1_failed", "error": f"{type(exc).__name__}: {exc}"})
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
                outputs.append(record)
                log_progress(model_key, "target_test_e2e_30", index, len(action_rows), outputs)
                continue
            try:
                action_with_state = replace_state(action, parsed_state)
                action_result = call_with_retry(
                    api_key=api_key,
                    model_id=model_id,
                    row=action_with_state,
                    max_tokens=max_tokens_action,
                    timeout=timeout,
                    temperature=temperature,
                )
                parsed_action, pred = parse_action_prediction(action_result["raw_output"], action_with_state)
                record.update(
                    {
                        "status": "ok",
                        "step2": action_result,
                        "step2_parse_ok": True,
                        "parse_ok": True,
                        "parsed": parsed_action,
                        "pred_act": pred,
                        "correct": pred == record["gold_act"],
                    }
                )
            except MalformedOutputError as exc:
                record.update({"status": "step2_parse_failed", "step2_parse_ok": False, "parse_ok": False, "error": str(exc)})
            except Exception as exc:  # noqa: BLE001
                record.update({"status": "step2_failed", "step2_parse_ok": False, "parse_ok": False, "error": f"{type(exc).__name__}: {exc}"})
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            outputs.append(record)
            log_progress(model_key, "target_test_e2e_30", index, len(action_rows), outputs)
    strict_pairs = [(row.get("pred_act") if row.get("parse_ok") else None, row.get("gold_act")) for row in outputs]
    parsed_pairs = [(row.get("pred_act"), row.get("gold_act")) for row in outputs if row.get("parse_ok")]
    return {
        "n": len(outputs),
        "step1_parse_rate": sum(bool(row.get("step1_parse_ok")) for row in outputs) / len(outputs) if outputs else 0.0,
        "step2_parse_rate": sum(bool(row.get("step2_parse_ok")) for row in outputs) / len(outputs) if outputs else 0.0,
        "macro_f1_strict": macro_f1(strict_pairs, FIVE_ACTS),
        "macro_f1_parsed": macro_f1(parsed_pairs, FIVE_ACTS) if parsed_pairs else 0.0,
        "prediction_counts": dict(Counter((row.get("pred_act") if row.get("parse_ok") else "PARSE_FAIL") for row in outputs)),
        "usage": e2e_usage(outputs),
    }


def e2e_usage(outputs: list[dict[str, Any]]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in outputs:
        for key in ("step1", "step2"):
            usage = (row.get(key) or {}).get("usage") or {}
            for usage_key, value in usage.items():
                if isinstance(value, int):
                    totals[usage_key] += value
    return dict(totals)


def get_balance(api_key: str) -> dict[str, Any]:
    req = urllib.request.Request(f"{API_BASE}/dashboard/balance", headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return {"ok": True, "body": json.loads(response.read().decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "body": exc.read().decode("utf-8", errors="replace")[:1000]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def model_list(api_key: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{API_BASE}/v1/models?llm=1&include_custom_models=1",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    ids = [item.get("id") for item in body.get("data", []) if isinstance(item, dict)]
    return {
        "count": len(ids),
        "selected": {key: model_id for key, model_id in MODELS.items() if model_id in ids},
        "missing": {key: model_id for key, model_id in MODELS.items() if model_id not in ids},
    }


def load_eval_rows() -> dict[str, list[dict[str, Any]]]:
    cross = [normalize_images(row) for row in read_jsonl(CROSS_ACTION)]
    target = [row for row in cross if row.get("domain") == "target"]
    user = [normalize_images(row) for row in read_jsonl(USER60) if str(row.get("source_id", "")).startswith("target_")]
    real = [
        normalize_images(row)
        for row in read_jsonl(REAL_ACTION)
        if row.get("meta", {}).get("label_source") == "human_json_annotation"
    ]
    for row in real:
        row["eval_id"] = f"real_store_{row['source_id']}"
        row["domain"] = "real_store"
        row["gold_best_action"] = gold_action(row)
    return {"cross": cross, "target": target, "user_target": user, "real": real}


def assert_images(rows_by_name: dict[str, list[dict[str, Any]]]) -> None:
    missing: list[str] = []
    for rows in rows_by_name.values():
        for row in rows:
            for image in row.get("images", []):
                path = repo_path(image)
                if not path.exists():
                    missing.append(str(path))
    if missing:
        preview = "\n".join(missing[:30])
        raise RuntimeError(f"missing images before API calls:\n{preview}")


def run_model(args: argparse.Namespace, model_key: str, model_id: str, rows: dict[str, list[dict[str, Any]]], api_key: str) -> dict[str, Any]:
    model_dir = args.out_dir / model_key
    model_dir.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    summary: dict[str, Any] = {
        "model_key": model_key,
        "requested_model_id": model_id,
        "api_provider": "302ai",
        "started_at_utc": now_iso(),
        "scenarios": {},
    }

    cross_outputs, cross_summary = run_action_scenario(
        rows=rows["cross"],
        scenario_name="cross_domain_60",
        out_path=model_dir / "cross_domain_60.jsonl",
        model_key=model_key,
        model_id=model_id,
        api_key=api_key,
        max_tokens=args.max_tokens_action,
        timeout=args.timeout,
        temperature=args.temperature,
        labels=FIVE_ACTS,
        force=args.force,
    )
    write_jsonl(model_dir / "cross_domain_60.jsonl", cross_outputs)
    target_outputs = [row for row in cross_outputs if row.get("domain") == "target"]
    write_jsonl(model_dir / "target_test_30.jsonl", target_outputs)
    summary["scenarios"]["target_test_30_oracle"] = summarize_action(target_outputs, labels=FIVE_ACTS)
    summary["scenarios"]["target_test_30_oracle"]["derived_from"] = "cross_domain_60 target subset"
    summary["scenarios"]["cross_domain_60_oracle"] = cross_summary

    e2e_summary = run_e2e(
        action_rows=rows["target"],
        user_rows=rows["user_target"],
        out_path=model_dir / "target_test_e2e_30.jsonl",
        model_key=model_key,
        model_id=model_id,
        api_key=api_key,
        max_tokens_state=args.max_tokens_state,
        max_tokens_action=args.max_tokens_action,
        timeout=args.timeout,
        temperature=args.temperature,
        force=args.force,
    )
    summary["scenarios"]["target_test_e2e_30"] = e2e_summary

    _real_outputs, real_summary = run_action_scenario(
        rows=rows["real"],
        scenario_name="real_store_20",
        out_path=model_dir / "real_store_20.jsonl",
        model_key=model_key,
        model_id=model_id,
        api_key=api_key,
        max_tokens=args.max_tokens_action,
        timeout=args.timeout,
        temperature=args.temperature,
        labels=("Greet", "Elicit", "Inform", "Recommend"),
        force=args.force,
    )
    summary["scenarios"]["real_store_20"] = real_summary
    summary["finished_at_utc"] = now_iso()
    summary["elapsed_sec"] = round(time.time() - start_time, 1)
    (model_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def fmt(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def cell(metric: dict[str, Any], key: str = "macro_f1_strict") -> str:
    parse = metric.get("parse_rate")
    if parse is None and "step2_parse_rate" in metric:
        parse = metric.get("step2_parse_rate")
    return f"{fmt(metric.get(key))} (parse {fmt(parse)})"


def aggregate(out_dir: Path, summaries: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# Closed-Source Four-Scenario Evaluation",
        "",
        "| Model | Target-Test (n=30) Oracle | Cross-Domain (n=60) Oracle | Target-Test E2E (n=30) | Real-Store Pilot (n=20) |",
        "|---|---:|---:|---:|---:|",
    ]
    display = {
        "gemini_2.5_flash": "Gemini 2.5 Flash",
        "gpt_4o": "GPT-4o",
        "claude_sonnet_4.6": "Claude Sonnet 4.6",
    }
    for key, name in display.items():
        summary = summaries.get(key) or {}
        scenarios = summary.get("scenarios", {})
        if not scenarios:
            lines.append(f"| {name} | - | - | - | - |")
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    cell(scenarios.get("target_test_30_oracle", {})),
                    cell(scenarios.get("cross_domain_60_oracle", {})),
                    cell(scenarios.get("target_test_e2e_30", {})),
                    cell(scenarios.get("real_store_20", {})),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Notes", "", "- API provider: 302ai `/v1/chat/completions`.", "- Target-Test oracle is derived from the target subset of the Cross-Domain oracle calls because the prompt and inputs are identical."])
    text = "\n".join(lines) + "\n"
    (out_dir / "aggregate_summary.md").write_text(text, encoding="utf-8")
    return text


def changelog(out_dir: Path, summaries: dict[str, dict[str, Any]], preflight: dict[str, Any]) -> None:
    lines = [
        "# Closed Model Eval Changelog",
        "",
        "Date: 2026-05-26",
        "",
        "## Scope",
        "",
        "- Provider: 302ai only; OpenRouter was not attempted per PI instruction.",
        "- Models: Gemini 2.5 Flash (`gemini-2.5-flash`), GPT-4o (`gpt-4o`), Claude Sonnet 4.6 (`claude-sonnet-4-6`).",
        "- Prompts: reused serialized PIWM system/user prompt text and XML parsers; `<image>` placeholders were replaced with API-native `image_url` inputs.",
        "- Target-Test oracle metrics are derived from Cross-Domain target-subset outputs to avoid duplicate identical API calls.",
        "",
        "## API Preflight",
        "",
        f"- Model-list result: `{json.dumps(preflight.get('models'), ensure_ascii=False)}`",
        f"- Balance endpoint result: `{json.dumps(preflight.get('balance'), ensure_ascii=False)}`",
        "",
        "## Results",
        "",
        "| Model | Target Oracle | Cross-Domain Oracle | E2E | Real-Store |",
        "|---|---:|---:|---:|---:|",
    ]
    display = {
        "gemini_2.5_flash": "Gemini 2.5 Flash",
        "gpt_4o": "GPT-4o",
        "claude_sonnet_4.6": "Claude Sonnet 4.6",
    }
    for key, name in display.items():
        scenarios = summaries.get(key, {}).get("scenarios", {})
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    cell(scenarios.get("target_test_30_oracle", {})),
                    cell(scenarios.get("cross_domain_60_oracle", {})),
                    cell(scenarios.get("target_test_e2e_30", {})),
                    cell(scenarios.get("real_store_20", {})),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Usage / Cost Tracking",
            "",
            "- 302ai balance endpoint returned 403 for this API key, so balance-delta cost could not be queried from the API in this run.",
            "- Raw `usage` objects returned by the chat-completions API are stored per request in each scenario JSONL and summed in each model `summary.json`.",
            "- If 302ai dashboard access is enabled later, cost can be reconciled against the request ids stored in raw outputs.",
            "",
            "## Real-Store Pilot Frame Transmission Log",
            "",
            "Real-Store Pilot uses 20 fully human-annotated sessions. For each completed model run, 20 sessions x 3 frames = 60 real-store images were transmitted to 302ai via HTTPS POST. PI confirmed participant release-form coverage for public release/API transmission. Request timestamps, image paths, and response ids are logged in each model's `real_store_20.jsonl`.",
            "",
            "## Parse Warnings",
            "",
        ]
    )
    for key, name in display.items():
        scenarios = summaries.get(key, {}).get("scenarios", {})
        for scenario_name, metrics in scenarios.items():
            parse = metrics.get("parse_rate", metrics.get("step2_parse_rate"))
            if parse is not None and parse < 0.70:
                lines.append(f"- {name} `{scenario_name}` parse rate below 0.70: {parse:.3f}.")
    if lines[-1] == "## Parse Warnings":
        lines.append("")
        lines.append("- None.")
    (REPO_ROOT / "reports/2026-05-26_closed_model_eval_changelog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--models", nargs="*", default=list(MODELS), choices=sorted(MODELS))
    parser.add_argument("--api-key-env", default="AI302_API_KEY")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--max-tokens-state", type=int, default=512)
    parser.add_argument("--max-tokens-action", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise RuntimeError(f"{args.api_key_env} is not set")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_eval_rows()
    assert_images(rows)
    preflight = {"models": model_list(api_key), "balance": get_balance(api_key)}
    (args.out_dir / "preflight.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summaries: dict[str, dict[str, Any]] = {}
    for model_key in args.models:
        summaries[model_key] = run_model(args, model_key, MODELS[model_key], rows, api_key)
    (args.out_dir / "summary.json").write_text(json.dumps({"preflight": preflight, "models": summaries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    aggregate(args.out_dir, summaries)
    changelog(args.out_dir, summaries, preflight)


if __name__ == "__main__":
    main()
