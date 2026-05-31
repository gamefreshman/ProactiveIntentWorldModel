"""Run a diagnostic Codex CLI self-eval on PIWM best-action rows.

This is not an API baseline. It invokes the local Codex CLI once per sample,
attaching only the three image frames and the original prompt text. Gold labels
are used only by this wrapper after the Codex subprocess returns.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_infer.parsers import MalformedOutputError, parse_action_output
from scripts.closed_model_best_action_eval import FIVE_ACTS, action_to_act, metrics_for_outputs, read_jsonl


DEFAULT_CODEX = Path("/Applications/Codex.app/Contents/Resources/codex")
DEFAULT_EVAL_SET = REPO_ROOT / "reports/closed_model_eval_set_60.jsonl"
DEFAULT_OUT_DIR = REPO_ROOT / "reports/closed_model_eval_20260525/codex_self"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def validate_row(row: dict[str, Any]) -> None:
    images = row.get("images", [])
    if len(images) != 3:
        raise ValueError(f"{row.get('eval_id')}: expected 3 images, got {len(images)}")
    missing = [image for image in images if not Path(image).exists()]
    if missing:
        raise FileNotFoundError(f"{row.get('eval_id')}: missing images: {missing}")


def prompt_for_row(row: dict[str, Any]) -> str:
    system = row["messages"][0]["content"].strip()
    user = row["messages"][1]["content"].replace("<image>", "").strip()
    return (
        "You are being evaluated as a multimodal PIWM best-action selector.\n"
        "Use only the three attached images and the prompt below. Do not inspect files. Do not use tools.\n"
        "Return only the requested structured tags, with no Markdown fences and no extra commentary.\n\n"
        "[System instruction]\n"
        f"{system}\n\n"
        "[User prompt]\n"
        f"{user}\n"
    )


def run_one(args: argparse.Namespace, row: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    last_message = out_dir / "messages" / f"{row['eval_id']}.txt"
    last_message.parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="piwm_codex_self_eval_"))
    result: subprocess.CompletedProcess[str] | None = None
    timeout_exc: subprocess.TimeoutExpired | None = None

    try:
        command = [
            str(args.codex_bin),
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--ignore-rules",
            "-C",
            str(workspace),
            "-s",
            "read-only",
            "-o",
            str(last_message),
        ]
        for image in row["images"]:
            command.extend(["-i", image])
        if args.model:
            command.extend(["--model", args.model])
        command.append("-")

        prompt = prompt_for_row(row)
        try:
            result = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=args.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            timeout_exc = exc
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    raw = last_message.read_text(encoding="utf-8") if last_message.exists() else (result.stdout if result is not None else "")
    record: dict[str, Any] = {
        "eval_id": row["eval_id"],
        "source_id": row["source_id"],
        "domain": row["domain"],
        "model_name": args.model or "codex_cli_default",
        "gold_act": row["gold_best_action"],
        "raw_output": raw,
        "returncode": result.returncode if result is not None else None,
        "stderr_tail": (result.stderr if result is not None else str(timeout_exc.stderr or ""))[-4000:],
    }
    if timeout_exc is not None:
        record.update({"status": "codex_timeout", "parse_ok": False, "pred_act": None, "error": f"codex timeout after {args.timeout}s"})
        return record
    if result.returncode != 0:
        record.update({"status": "codex_failed", "parse_ok": False, "pred_act": None, "error": f"codex exit {result.returncode}"})
        return record
    try:
        parsed = parse_action_output(raw, valid_actions=row.get("meta", {}).get("candidate_action_acts", {}).keys(), five_act_only=True)
        pred_act = action_to_act(parsed.get("chosen"), row.get("meta", {}).get("candidate_action_acts", {}))
        record.update(
            {
                "status": "ok",
                "parsed": parsed,
                "parse_ok": pred_act in FIVE_ACTS,
                "pred_act": pred_act,
                "correct": pred_act == row["gold_best_action"],
            }
        )
    except MalformedOutputError as exc:
        record.update({"status": "parse_failed", "parse_ok": False, "pred_act": None, "error": str(exc)})
    return record


def existing_outputs(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return {row["eval_id"]: row for row in read_jsonl(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-set", type=Path, default=DEFAULT_EVAL_SET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--codex-bin", type=Path, default=DEFAULT_CODEX)
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    rows = read_jsonl(args.eval_set)
    selected = rows[args.start :]
    if args.limit is not None:
        selected = selected[: args.limit]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.out_dir / "raw_outputs.jsonl"
    existing = {} if args.force else existing_outputs(raw_path)

    with raw_path.open("w" if args.force else "a", encoding="utf-8") as handle:
        for offset, row in enumerate(selected, start=args.start + 1):
            if not args.force and row["eval_id"] in existing:
                print(json.dumps({"event": "skip_existing", "index": offset, "eval_id": row["eval_id"]}), flush=True)
                continue
            validate_row(row)
            record = run_one(args, row, args.out_dir)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(
                json.dumps(
                    {
                        "event": "codex_self_progress",
                        "index": offset,
                        "total": len(rows),
                        "eval_id": row["eval_id"],
                        "status": record["status"],
                        "pred_act": record.get("pred_act"),
                        "gold_act": row["gold_best_action"],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    outputs = list(existing_outputs(raw_path).values())
    metrics = metrics_for_outputs({row["eval_id"]: row for row in rows}, outputs)
    summary = {
        "artifact": "codex_self_eval",
        "is_paper_baseline": False,
        "note": "Diagnostic local Codex CLI self-eval; not an API/OpenRouter closed-model baseline.",
        "eval_set": display_path(args.eval_set),
        "raw_outputs": display_path(raw_path),
        "n_outputs": len(outputs),
        "metrics": metrics,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
