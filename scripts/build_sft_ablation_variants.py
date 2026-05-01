"""Build ms-swift SFT JSONL variants for PIWM ablation experiments.

The sprint ablations differ only in which supervision tasks are included.
This script writes one ms-swift-compatible JSONL per variant so four LoRA runs
can be launched in parallel on remote GPUs:

* ``full_piwm_v2``: perception + deliberation + continuation caption + action
* ``b1_perception_only``: perception only
* ``b3_no_deliberation``: perception + direct action selection
* ``b4_no_continuation``: perception + deliberation + action selection

By default future-verification rows are excluded because B1/B3/B4 are meant to
isolate the continuation-caption head, not the later audit-verification task.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from piwm_train.data_collator import SFTExample, build_sft_examples
from piwm_train.ms_swift_adapter import build_ms_swift_record


@dataclass(frozen=True)
class VariantSpec:
    name: str
    include_perception: bool
    include_deliberation: bool
    include_continuation: bool
    include_action: bool


VARIANTS: dict[str, VariantSpec] = {
    "full_piwm_v2": VariantSpec(
        name="full_piwm_v2",
        include_perception=True,
        include_deliberation=True,
        include_continuation=True,
        include_action=True,
    ),
    "b1_perception_only": VariantSpec(
        name="b1_perception_only",
        include_perception=True,
        include_deliberation=False,
        include_continuation=False,
        include_action=False,
    ),
    "b3_no_deliberation": VariantSpec(
        name="b3_no_deliberation",
        include_perception=True,
        include_deliberation=False,
        include_continuation=False,
        include_action=True,
    ),
    "b4_no_continuation": VariantSpec(
        name="b4_no_continuation",
        include_perception=True,
        include_deliberation=True,
        include_continuation=False,
        include_action=True,
    ),
}

DEFAULT_VARIANTS = tuple(VARIANTS)


def build_variant_examples(
    data_dirs: list[Path],
    spec: VariantSpec,
    *,
    include_future_verification: bool = False,
    max_examples_per_dir: int | None = None,
) -> list[SFTExample]:
    examples: list[SFTExample] = []
    for data_dir in data_dirs:
        dir_examples = build_sft_examples(
            data_dir,
            include_perception=spec.include_perception,
            include_deliberation=spec.include_deliberation,
            include_continuation=spec.include_continuation,
            include_future_verification=include_future_verification,
            include_action=spec.include_action,
        )
        if max_examples_per_dir is not None:
            dir_examples = dir_examples[:max_examples_per_dir]
        for example in dir_examples:
            example.meta = {**example.meta, "source_data_dir": str(data_dir)}
        examples.extend(dir_examples)
    return examples


def write_variant(
    examples: list[SFTExample],
    output_jsonl: Path,
    *,
    root: Path,
    variant: str,
    data_dirs: list[Path],
    validate_images: bool = True,
) -> dict:
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    task_counts: dict[str, int] = {}
    image_path_count = 0
    with output_jsonl.open("w", encoding="utf-8") as handle:
        for example in examples:
            row = build_ms_swift_record(example, root=root, validate_images=validate_images)
            task_counts[example.task] = task_counts.get(example.task, 0) + 1
            image_path_count += len(row["images"])
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "artifact": "piwm_ablation_ms_swift_variant",
        "is_training_result": False,
        "variant": variant,
        "data_dirs": [str(path) for path in data_dirs],
        "output_jsonl": str(output_jsonl),
        "n_examples": len(examples),
        "task_counts": task_counts,
        "image_path_count": image_path_count,
        "format": "ms-swift messages + images",
    }
    output_jsonl.with_name("summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def build_all_variants(
    data_dirs: list[Path],
    output_root: Path,
    *,
    root: Path,
    variants: Iterable[str] = DEFAULT_VARIANTS,
    include_future_verification: bool = False,
    max_examples_per_dir: int | None = None,
    validate_images: bool = True,
) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for variant in variants:
        spec = VARIANTS[variant]
        examples = build_variant_examples(
            data_dirs,
            spec,
            include_future_verification=include_future_verification,
            max_examples_per_dir=max_examples_per_dir,
        )
        output_jsonl = output_root / variant / "ms_swift_sft.jsonl"
        summaries[variant] = write_variant(
            examples,
            output_jsonl,
            root=root,
            variant=variant,
            data_dirs=data_dirs,
            validate_images=validate_images,
        )

    index = {
        "artifact": "piwm_ablation_ms_swift_variants",
        "is_training_result": False,
        "output_root": str(output_root),
        "variants": summaries,
    }
    (output_root / "_variant_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, action="append", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--variant", choices=sorted(VARIANTS), action="append", default=None)
    parser.add_argument("--include-future-verification", action="store_true")
    parser.add_argument("--allow-missing-images", action="store_true", help="Write paths under --root without checking that images exist locally.")
    parser.add_argument("--max-examples-per-dir", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    index = build_all_variants(
        args.data_dir,
        args.output_root,
        root=args.root,
        variants=args.variant or DEFAULT_VARIANTS,
        include_future_verification=args.include_future_verification,
        max_examples_per_dir=args.max_examples_per_dir,
        validate_images=not args.allow_missing_images,
    )
    print(json.dumps(index, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
