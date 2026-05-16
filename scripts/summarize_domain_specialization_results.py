"""Summarize PIWM domain-specialization checkpoint evaluation JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_RESULTS_DIR = Path("data/piwm_results/domain_specialization_eval")
DEFAULT_OUT_JSON = DEFAULT_RESULTS_DIR / "summary.json"
DEFAULT_OUT_MD = DEFAULT_RESULTS_DIR / "summary.md"


def summarize_domain_specialization_results(results_dir: Path) -> dict[str, Any]:
    rows = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name in {"summary.json"}:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.append(_result_row(path, payload))
    return {
        "artifact": "piwm_domain_specialization_eval_summary",
        "results_dir": results_dir.as_posix(),
        "n_results": len(rows),
        "results": rows,
    }


def write_summary(summary: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(_markdown(summary), encoding="utf-8")


def _result_row(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    metrics = payload.get("metrics", {})
    return {
        "path": path.as_posix(),
        "artifact": payload.get("artifact"),
        "eval_label": payload.get("eval_label"),
        "checkpoint": payload.get("checkpoint"),
        "input_jsonl": payload.get("input_jsonl"),
        "n_records": payload.get("n_records"),
        "task_counts": payload.get("task_counts", {}),
        "parse_rate": payload.get("parse_rate"),
        "metrics": metrics,
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# PIWM Domain Specialization Eval Summary",
        "",
        f"- results_dir: `{summary['results_dir']}`",
        f"- n_results: {summary['n_results']}",
        "",
    ]
    if not summary["results"]:
        lines.extend([
            "No checkpoint evaluation JSON files were found yet.",
            "",
            "Expected inputs are outputs from `scripts.eval_ms_swift_checkpoint` or compatible evaluation scripts.",
            "",
        ])
        return "\n".join(lines)

    metric_names = sorted({name for row in summary["results"] for name in row.get("metrics", {})})
    lines.extend([
        "| Label | Records | Parse rate | Input | Checkpoint |",
        "|---|---:|---:|---|---|",
    ])
    for row in summary["results"]:
        parse_rate = _fmt(row.get("parse_rate"))
        lines.append(
            f"| `{row.get('eval_label')}` | {row.get('n_records')} | {parse_rate} | "
            f"`{row.get('input_jsonl')}` | `{row.get('checkpoint')}` |"
        )
    if metric_names:
        lines.extend(["", "## Metrics", "", "| Label | " + " | ".join(metric_names) + " |", "|---" + "|---:" * len(metric_names) + "|"])
        for row in summary["results"]:
            values = " | ".join(_fmt(row.get("metrics", {}).get(name)) for name in metric_names)
            lines.append(f"| `{row.get('eval_label')}` | {values} |")
    lines.append("")
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if value is None:
        return "-"
    return str(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = summarize_domain_specialization_results(args.results_dir)
    write_summary(summary, args.out_json, args.out_md)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
