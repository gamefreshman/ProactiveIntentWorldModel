"""Promote reviewed distillation-batch outputs into the main expert corpus.

The default mode is dry-run. Use ``--commit`` only after the batch review log
has been checked and the finalized principles have been approved.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from piwm_data.expert_corpus.provenance import (
    DEFAULT_EXTRACTED_PRINCIPLES,
    DEFAULT_SALES_SOURCE_REGISTRY,
    load_extracted_principles,
    load_source_registry,
)
from piwm_data.expert_corpus.schemas import ExtractedPrinciple, SourceRegistryEntry
from piwm_data.expert_corpus.tools.run_distillation import read_jsonl, resolve_batch

_SOURCE_ADAPTER: TypeAdapter[SourceRegistryEntry] = TypeAdapter(SourceRegistryEntry)
_PRINCIPLE_ADAPTER: TypeAdapter[ExtractedPrinciple] = TypeAdapter(ExtractedPrinciple)


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def validate_new_sources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_SOURCE_ADAPTER.validate_python(row).model_dump() for row in rows]


def validate_new_principles(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_PRINCIPLE_ADAPTER.validate_python(row).model_dump() for row in rows]


def run(args: argparse.Namespace) -> dict[str, Any]:
    batch_dir = resolve_batch(args.batch)
    source_path = batch_dir / args.source_additions
    finalized_path = batch_dir / args.finalized

    source_rows = validate_new_sources(read_jsonl(source_path)) if source_path.exists() else []
    principle_rows = validate_new_principles(read_jsonl(finalized_path)) if finalized_path.exists() else []

    existing_source_ids = {
        item.source_id for item in load_source_registry(DEFAULT_SALES_SOURCE_REGISTRY)
    }
    existing_principle_ids = {
        item.principle_id for item in load_extracted_principles(DEFAULT_EXTRACTED_PRINCIPLES)
    }
    duplicate_sources = sorted(
        row["source_id"] for row in source_rows if row["source_id"] in existing_source_ids
    )
    duplicate_principles = sorted(
        row["principle_id"]
        for row in principle_rows
        if row["principle_id"] in existing_principle_ids
    )
    if duplicate_sources or duplicate_principles:
        raise ValueError(
            "duplicate ids: "
            f"sources={duplicate_sources or []}, principles={duplicate_principles or []}"
        )

    available_source_ids = existing_source_ids | {row["source_id"] for row in source_rows}
    missing_principle_sources = sorted(
        {
            row["source_id"]
            for row in principle_rows
            if row["source_id"] not in available_source_ids
        }
    )
    if missing_principle_sources:
        raise ValueError(f"principles reference unknown source_ids: {missing_principle_sources}")

    if args.commit:
        if source_rows:
            append_jsonl(DEFAULT_SALES_SOURCE_REGISTRY, source_rows)
        if principle_rows:
            append_jsonl(DEFAULT_EXTRACTED_PRINCIPLES, principle_rows)

    return {
        "batch_id": batch_dir.name,
        "mode": "commit" if args.commit else "dry_run",
        "source_additions": len(source_rows),
        "finalized_principles": len(principle_rows),
        "sales_source_registry": str(DEFAULT_SALES_SOURCE_REGISTRY),
        "extracted_principles": str(DEFAULT_EXTRACTED_PRINCIPLES),
        "note": "rule_source_links are intentionally not updated by source/principle promotion",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", help="Batch id under distillation_batches/ or a batch path")
    parser.add_argument("--source-additions", default="source_additions.jsonl")
    parser.add_argument("--finalized", default="finalized.jsonl")
    parser.add_argument("--commit", action="store_true")
    return parser


def main() -> None:
    result = run(build_parser().parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
