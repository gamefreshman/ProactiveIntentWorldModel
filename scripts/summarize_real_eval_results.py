"""Summarize PIWM real-eval result JSON files into a compact table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> int:
    args = parse_args()
    result_paths = collect_paths(args.inputs)
    rows = [summarize_result(path) for path in result_paths]
    summary = {
        "artifact": "piwm_real_eval_summary",
        "is_training_result": False,
        "n_results": len(rows),
        "results": rows,
    }
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = render_markdown(rows)
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="Result JSON files or directories containing *.json.")
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    return parser.parse_args()


def collect_paths(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if not item.exists():
            continue
        if item.is_dir():
            paths.extend(
                path
                for path in sorted(item.glob("*_real_all_scored.json"))
                if not path.name.endswith(".partial")
            )
        else:
            paths.append(item)
    return sorted(dict.fromkeys(paths))


def summarize_result(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    metrics = result.get("metrics", {})
    return {
        "path": path.as_posix(),
        "eval_label": result.get("eval_label") or path.stem,
        "n_records": result.get("n_records"),
        "parse_rate": result.get("parse_rate"),
        "task_counts": result.get("task_counts", {}),
        "stage_accuracy": metrics.get("stage_accuracy"),
        "stage_macro_f1": metrics.get("stage_macro_f1"),
        "intent_accuracy": metrics.get("intent_accuracy"),
        "action_accuracy": metrics.get("action_accuracy"),
        "action_macro_f1": metrics.get("action_macro_f1"),
        "chosen_exact": metrics.get("chosen_exact"),
        "go_precision": metrics.get("go_precision"),
        "go_recall": metrics.get("go_recall"),
        "no_go_precision": metrics.get("no_go_precision"),
        "no_go_recall": metrics.get("no_go_recall"),
    }


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# PIWM Real Eval Summary",
        "",
        "| Model | N | Parse | Stage Acc | Stage Macro F1 | Intent Acc | Action Acc | Action Macro F1 | Chosen Exact |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {model} | {n} | {parse} | {stage_acc} | {stage_f1} | {intent_acc} | {action_acc} | {action_f1} | {chosen} |".format(
                model=row["eval_label"],
                n=row.get("n_records") or 0,
                parse=fmt(row.get("parse_rate")),
                stage_acc=fmt(row.get("stage_accuracy")),
                stage_f1=fmt(row.get("stage_macro_f1")),
                intent_acc=fmt(row.get("intent_accuracy")),
                action_acc=fmt(row.get("action_accuracy")),
                action_f1=fmt(row.get("action_macro_f1")),
                chosen=fmt(row.get("chosen_exact")),
            )
        )
    lines.extend(
        [
            "",
            "Primary metrics are Stage Acc and Action Macro F1. Intent labels in the generated real set are heuristic, so Intent Acc is secondary.",
            "",
        ]
    )
    return "\n".join(lines)


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
