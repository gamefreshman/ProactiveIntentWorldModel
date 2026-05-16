"""Build fixed eval-set entrypoints for PIWM domain specialization experiments."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_TARGET_MS_SWIFT = Path("data/official/ms_swift/piwm_train_target_specialization_v1.jsonl")
DEFAULT_GENERAL_EVAL = Path("data/official/ms_swift/piwm_eval_qa_all_v1.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/official/domain_specialization_eval_v1")


def build_domain_specialization_eval_sets(
    target_ms_swift: Path,
    general_eval: Path,
    output_dir: Path,
    *,
    target_split: str = "test",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    target_rows = [
        row for row in _read_jsonl(target_ms_swift)
        if row.get("meta", {}).get("split") == target_split
    ]
    general_rows = _read_jsonl(general_eval)

    target_all = output_dir / "target_frontcam_test_all.jsonl"
    general_all = output_dir / "general_qa_all.jsonl"
    _write_jsonl(target_rows, target_all)
    _write_jsonl(general_rows, general_all)

    target_task_paths: dict[str, str] = {}
    for task in sorted({row.get("task", "unknown") for row in target_rows}):
        task_rows = [row for row in target_rows if row.get("task", "unknown") == task]
        path = output_dir / f"target_frontcam_test_{task}.jsonl"
        _write_jsonl(task_rows, path)
        target_task_paths[task] = path.as_posix()

    summary = {
        "artifact": "piwm_domain_specialization_eval_sets_v1",
        "target_source": target_ms_swift.as_posix(),
        "general_source": general_eval.as_posix(),
        "output_dir": output_dir.as_posix(),
        "target_split": target_split,
        "eval_sets": {
            "target_frontcam_test_all": {
                "path": target_all.as_posix(),
                "rows": len(target_rows),
                "task_counts": dict(sorted(Counter(row.get("task", "unknown") for row in target_rows).items())),
                "qa_status": "templates_generated_pending_manual_review",
            },
            "general_qa_all": {
                "path": general_all.as_posix(),
                "rows": len(general_rows),
                "task_counts": dict(sorted(Counter(row.get("task", "unknown") for row in general_rows).items())),
                "qa_status": "qa_reviewed_pass_subset",
            },
        },
        "target_task_paths": target_task_paths,
        "evaluation_matrix": _evaluation_matrix(target_all, general_all),
    }
    (output_dir / "eval_sets_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "eval_sets_summary.md").write_text(_markdown(summary), encoding="utf-8")
    return summary


def _evaluation_matrix(target_all: Path, general_all: Path) -> list[dict[str, str]]:
    return [
        {
            "eval_label": "general_on_general",
            "checkpoint": "checkpoint_general",
            "input_jsonl": general_all.as_posix(),
            "purpose": "general performance after stage-1 SFT",
        },
        {
            "eval_label": "general_on_target",
            "checkpoint": "checkpoint_general",
            "input_jsonl": target_all.as_posix(),
            "purpose": "zero-shot target transfer",
        },
        {
            "eval_label": "target_on_target",
            "checkpoint": "checkpoint_target",
            "input_jsonl": target_all.as_posix(),
            "purpose": "target specialization gain",
        },
        {
            "eval_label": "target_on_general",
            "checkpoint": "checkpoint_target",
            "input_jsonl": general_all.as_posix(),
            "purpose": "catastrophic forgetting check",
        },
        {
            "eval_label": "joint_on_target",
            "checkpoint": "checkpoint_joint_general_target",
            "input_jsonl": target_all.as_posix(),
            "purpose": "joint SFT target-domain ablation",
        },
    ]


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# PIWM Domain Specialization Eval Sets",
        "",
        f"- target_split: `{summary['target_split']}`",
        f"- output_dir: `{summary['output_dir']}`",
        "",
        "## Eval Sets",
        "",
        "| Name | Rows | QA status | Tasks |",
        "|---|---:|---|---|",
    ]
    for name, info in summary["eval_sets"].items():
        tasks = ", ".join(f"{task}={count}" for task, count in info["task_counts"].items())
        lines.append(f"| `{name}` | {info['rows']} | `{info['qa_status']}` | {tasks} |")

    lines.extend([
        "",
        "## Evaluation Matrix",
        "",
        "| Label | Checkpoint | Input | Purpose |",
        "|---|---|---|---|",
    ])
    for item in summary["evaluation_matrix"]:
        lines.append(
            f"| `{item['eval_label']}` | `{item['checkpoint']}` | `{item['input_jsonl']}` | {item['purpose']} |"
        )

    lines.extend([
        "",
        "## Command Template",
        "",
        "Replace `<MODEL>` and `<CHECKPOINT>` with the concrete base model and LoRA checkpoint path:",
        "",
        "```bash",
        "python3 -m scripts.eval_ms_swift_checkpoint \\",
        "  --model <MODEL> \\",
        "  --checkpoint <CHECKPOINT> \\",
        "  --eval-label general_on_target \\",
        "  --input-jsonl data/official/domain_specialization_eval_v1/target_frontcam_test_all.jsonl \\",
        "  --out data/piwm_results/domain_specialization_eval/general_on_target.json \\",
        "  --image-limit 3",
        "```",
        "",
    ])
    return "\n".join(lines)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-ms-swift", type=Path, default=DEFAULT_TARGET_MS_SWIFT)
    parser.add_argument("--general-eval", type=Path, default=DEFAULT_GENERAL_EVAL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--target-split", default="test")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = build_domain_specialization_eval_sets(
        args.target_ms_swift,
        args.general_eval,
        args.output_dir,
        target_split=args.target_split,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
