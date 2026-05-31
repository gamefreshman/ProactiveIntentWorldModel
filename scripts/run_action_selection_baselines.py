"""Compute simple 5-act action-selection baselines for PIWM eval rows."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from piwm_infer.parsers import parse_action_output


DEFAULT_INPUT = Path("data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl")
DEFAULT_OUT_JSON = Path("data/piwm_results/domain_specialization_eval/target_5act_action_baselines.json")
DEFAULT_OUT_MD = Path("data/piwm_results/domain_specialization_eval/target_5act_action_baselines.md")
DEFAULT_TWO_STAGE_SUMMARY_MD = Path("data/official/domain_specialization_eval_v2/two_stage_eval_summary.md")


def run_baselines(input_jsonl: Path, *, seed: int = 42) -> dict[str, Any]:
    rows = _read_jsonl(input_jsonl)
    gold = [_gold_act(row) for row in rows]
    candidate_acts = [list(row.get("meta", {}).get("candidate_action_acts", {}).values()) for row in rows]
    rng = random.Random(seed)
    baselines = {
        "always_greet": ["Greet" for _ in rows],
        "always_elicit": ["Elicit" for _ in rows],
        "always_inform": ["Inform" for _ in rows],
        "always_recommend": ["Recommend" for _ in rows],
        "always_hold": ["Hold" for _ in rows],
        "random_candidate": [rng.choice(acts) if acts else "Hold" for acts in candidate_acts],
    }
    return {
        "artifact": "piwm_5act_action_selection_baselines",
        "input_jsonl": input_jsonl.as_posix(),
        "n_rows": len(rows),
        "seed": seed,
        "gold_act_counts": _counts(gold),
        "baselines": {
            name: _metrics(pred, gold)
            for name, pred in baselines.items()
        },
    }


def write_outputs(summary: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(_markdown(summary), encoding="utf-8")
    _update_two_stage_summary_md(summary, DEFAULT_TWO_STAGE_SUMMARY_MD)


def _gold_act(row: dict[str, Any]) -> str:
    target = row["messages"][2]["content"]
    chosen = parse_action_output(target)["chosen"]
    mapping = row.get("meta", {}).get("candidate_action_acts", {})
    if chosen in mapping:
        return mapping[chosen]
    return chosen.split("_", 1)[0]


def _metrics(pred: list[str], gold: list[str]) -> dict[str, Any]:
    pairs = list(zip(pred, gold))
    return {
        "action_accuracy": _accuracy(pairs),
        "action_macro_f1": _macro_f1(pairs),
        "go_precision": _precision(_go_pairs(pairs), positive="go"),
        "go_recall": _recall(_go_pairs(pairs), positive="go"),
        "no_go_precision": _precision(_go_pairs(pairs), positive="no_go"),
        "no_go_recall": _recall(_go_pairs(pairs), positive="no_go"),
        "prediction_counts": _counts(pred),
    }


def _go_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(_go_no_go(pred), _go_no_go(gold)) for pred, gold in pairs]


def _go_no_go(act: str) -> str:
    return "no_go" if act == "Hold" else "go"


def _accuracy(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    return sum(int(pred == gold) for pred, gold in pairs) / len(pairs)


def _macro_f1(pairs: list[tuple[str, str]]) -> float | None:
    labels = sorted({item for pair in pairs for item in pair})
    if not labels:
        return None
    scores = []
    for label in labels:
        tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
        fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
        fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append((2 * precision * recall / (precision + recall)) if precision + recall else 0.0)
    return sum(scores) / len(scores)


def _precision(pairs: list[tuple[str, str]], *, positive: str) -> float | None:
    pred_pos = sum(1 for pred, _ in pairs if pred == positive)
    if pred_pos == 0:
        return None
    return sum(1 for pred, gold in pairs if pred == positive and gold == positive) / pred_pos


def _recall(pairs: list[tuple[str, str]], *, positive: str) -> float | None:
    gold_pos = sum(1 for _, gold in pairs if gold == positive)
    if gold_pos == 0:
        return None
    return sum(1 for pred, gold in pairs if pred == positive and gold == positive) / gold_pos


def _counts(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# PIWM Target 5-Act Action Baselines",
        "",
        f"- input_jsonl: `{summary['input_jsonl']}`",
        f"- n_rows: {summary['n_rows']}",
        f"- gold_act_counts: `{summary['gold_act_counts']}`",
        "",
        "| Baseline | Action accuracy | Action macro F1 | Go precision | Go recall | No-go precision | No-go recall |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in summary["baselines"].items():
        lines.append(
            f"| `{name}` | {_fmt(metrics['action_accuracy'])} | {_fmt(metrics['action_macro_f1'])} | "
            f"{_fmt(metrics['go_precision'])} | {_fmt(metrics['go_recall'])} | "
            f"{_fmt(metrics['no_go_precision'])} | {_fmt(metrics['no_go_recall'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _update_two_stage_summary_md(summary: dict[str, Any], path: Path) -> None:
    if not path.exists():
        return
    marker = "## Action-Selection Baselines"
    text = path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    path.write_text(text + "\n\n" + _baseline_section(summary), encoding="utf-8")


def _baseline_section(summary: dict[str, Any]) -> str:
    lines = [
        "## Action-Selection Baselines",
        "",
        "These baselines are computed on the current balanced 5-act target action-selection eval. "
        "The five operational acts are Greet, Elicit, Inform, Recommend, and Hold; Reassure is filtered out.",
        "",
        f"- input_jsonl: `{summary['input_jsonl']}`",
        f"- n_rows: {summary['n_rows']}",
        f"- gold_act_counts: `{summary['gold_act_counts']}`",
        "",
        "| Baseline | Action accuracy | Action macro F1 | Prediction counts |",
        "|---|---:|---:|---|",
    ]
    for name, metrics in summary["baselines"].items():
        lines.append(
            f"| `{name}` | {_fmt(metrics['action_accuracy'])} | "
            f"{_fmt(metrics['action_macro_f1'])} | `{metrics['prediction_counts']}` |"
        )
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
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_baselines(args.input_jsonl, seed=args.seed)
    write_outputs(summary, args.out_json, args.out_md)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
