"""Generate a human-review sheet for a distillation batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter, ValidationError

from piwm_data.expert_corpus.schemas import ExtractedPrinciple
from piwm_data.expert_corpus.tools.run_distillation import read_jsonl, resolve_batch

_PRINCIPLE_ADAPTER: TypeAdapter[ExtractedPrinciple] = TypeAdapter(ExtractedPrinciple)

APPROVED_STATUSES = {"approved", "expert_reviewed", "reviewed"}


def strip_to_principle(row: dict[str, Any]) -> dict[str, Any]:
    """Keep only fields accepted by ExtractedPrinciple."""

    return {
        "principle_id": row["principle_id"],
        "source_id": row["source_id"],
        "principle": row["principle"],
        "usable_for": row["usable_for"],
        "extraction_method": row["extraction_method"],
        "copyright_note": row["copyright_note"],
        "confidence": row["confidence"],
    }


def validate_principle_row(row: dict[str, Any]) -> str:
    try:
        _PRINCIPLE_ADAPTER.validate_python(strip_to_principle(row))
    except (KeyError, ValidationError) as exc:
        return f"schema_error: {exc}"
    if len(str(row["principle"]).split()) > 45:
        return "principle_too_long"
    return "ok"


def markdown_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_review_log(batch_id: str, rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# Review Log: {batch_id}",
        "",
        "Status vocabulary: `pending`, `approved`, `revise`, `reject`.",
        "",
        "Checklist for each principle:",
        "",
        "- faithful to the source locator and paraphrase note;",
        "- compact enough to be auditable;",
        "- operationalizable as a rule or schema condition;",
        "- no long copyrighted source text;",
        "- not duplicative or conflicting with existing principles.",
        "",
        "| ID | Source | Draft principle | Usable for | Schema | Decision | Notes |",
        "|----|--------|-----------------|------------|--------|----------|-------|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(row.get("principle_id")),
                    markdown_escape(row.get("source_id")),
                    markdown_escape(row.get("principle")),
                    markdown_escape(", ".join(row.get("usable_for", []))),
                    validate_principle_row(row),
                    markdown_escape(row.get("review_status", "pending")),
                    markdown_escape(row.get("review_note") or row.get("reviewer_notes") or ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Notes",
            "",
            "- Pending review. Do not promote this batch until decisions are changed",
            "  to `approved` in `extracted_draft.jsonl` or copied into `finalized.jsonl`.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_finalized(path: Path, rows: list[dict[str, Any]]) -> int:
    finalized = [
        strip_to_principle(row)
        for row in rows
        if row.get("review_status") in APPROVED_STATUSES
    ]
    with path.open("w", encoding="utf-8") as handle:
        for row in finalized:
            _PRINCIPLE_ADAPTER.validate_python(row)
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(finalized)


def run(args: argparse.Namespace) -> dict[str, Any]:
    batch_dir = resolve_batch(args.batch)
    rows = read_jsonl(batch_dir / args.input)
    review_log = render_review_log(batch_dir.name, rows)
    review_path = batch_dir / args.review_log
    review_path.write_text(review_log, encoding="utf-8")

    finalized_count = None
    if args.write_finalized:
        finalized_count = write_finalized(batch_dir / args.finalized, rows)

    return {
        "batch_id": batch_dir.name,
        "drafts": len(rows),
        "review_log": str(review_path),
        "finalized": finalized_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", help="Batch id under distillation_batches/ or a batch path")
    parser.add_argument("--input", default="extracted_draft.jsonl")
    parser.add_argument("--review-log", default="review_log.md")
    parser.add_argument("--finalized", default="finalized.jsonl")
    parser.add_argument("--write-finalized", action="store_true")
    return parser


def main() -> None:
    result = run(build_parser().parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
