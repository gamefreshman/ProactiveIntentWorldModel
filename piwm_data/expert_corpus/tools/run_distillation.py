"""Create draft principles for an expert-corpus distillation batch.

The v2.2 workflow must be auditable before it is automated. This tool therefore
does not call an external LLM by default. It turns reviewed paraphrase notes in
``source_excerpts.jsonl`` into ``extracted_draft.jsonl`` and records the prompt
hash and run settings in ``run_log.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BATCH_ROOT = Path(__file__).resolve().parents[1] / "distillation_batches"


def resolve_batch(batch: str) -> Path:
    """Resolve a batch id or path to a directory."""

    candidate = Path(batch)
    if candidate.exists():
        return candidate
    candidate = DEFAULT_BATCH_ROOT / batch
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"distillation batch not found: {batch}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSONL, ignoring blank lines."""

    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]], overwrite: bool) -> None:
    """Write JSONL rows, refusing to overwrite unless requested."""

    if path.exists() and path.read_text(encoding="utf-8").strip() and not overwrite:
        raise FileExistsError(f"{path} already has content; pass --overwrite")
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def make_draft(batch_id: str, row: dict[str, Any], index: int, method: str) -> dict[str, Any]:
    """Convert one source note into a draft principle row."""

    principle = row.get("principle_hint") or row.get("draft_principle") or row.get("paraphrase_note")
    if not principle:
        raise ValueError(f"{row.get('excerpt_id', index)} has no principle_hint or paraphrase_note")

    usable_for = row.get("usable_for")
    if not isinstance(usable_for, list) or not usable_for:
        raise ValueError(f"{row.get('excerpt_id', index)} must provide non-empty usable_for")

    return {
        "principle_id": row.get(
            "principle_id",
            f"DRAFT_{batch_id.upper().replace('-', '_')}_{index:03d}",
        ),
        "source_id": row["source_id"],
        "principle": principle,
        "usable_for": usable_for,
        "extraction_method": method,
        "copyright_note": row.get(
            "copyright_note",
            "compact paraphrase from source locator; no source text stored",
        ),
        "confidence": float(row.get("confidence", 0.6)),
        "review_status": row.get("review_status", "pending"),
        "distillation_batch": batch_id,
        "source_excerpt_id": row.get("excerpt_id"),
        "source_locator": row.get("source_locator"),
        "notes": row.get("paraphrase_note"),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    batch_dir = resolve_batch(args.batch)
    batch_id = batch_dir.name
    prompt_path = batch_dir / args.prompt
    excerpts_path = batch_dir / args.source_excerpts
    output_path = batch_dir / args.output
    run_log_path = batch_dir / args.run_log

    prompt = prompt_path.read_text(encoding="utf-8")
    excerpts = read_jsonl(excerpts_path)
    drafts = [
        make_draft(batch_id=batch_id, row=row, index=index, method=args.method)
        for index, row in enumerate(excerpts, start=1)
    ]

    write_jsonl(output_path, drafts, overwrite=args.overwrite)

    run_log = {
        "batch_id": batch_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": "piwm_data.expert_corpus.tools.run_distillation",
        "mode": "local_paraphrase_note_to_draft",
        "model": args.model,
        "temperature": args.temperature,
        "extraction_method": args.method,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "source_excerpts": str(excerpts_path),
        "draft_output": str(output_path),
        "n_source_notes": len(excerpts),
        "n_drafts": len(drafts),
        "copyright_policy": "compact paraphrases and source locators only",
    }
    run_log_path.write_text(json.dumps(run_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return run_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", help="Batch id under distillation_batches/ or a batch path")
    parser.add_argument("--prompt", default="extraction_prompt.md")
    parser.add_argument("--source-excerpts", default="source_excerpts.jsonl")
    parser.add_argument("--output", default="extracted_draft.jsonl")
    parser.add_argument("--run-log", default="run_log.json")
    parser.add_argument("--model", default="manual-local")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--method",
        choices=["human_paraphrase", "llm_assisted_paraphrase"],
        default="human_paraphrase",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    log = run(args)
    print(json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
