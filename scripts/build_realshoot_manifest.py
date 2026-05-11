"""Build the PIWM real-shooting manifest template/sample JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from piwm_data import rules
from piwm_data.schemas import ShootingClipRecord


DEFAULT_PRODUCTS = [
    "luxury_watch",
    "electronics_phone",
    "electronics_laptop",
    "cosmetics_skincare",
    "apparel_premium",
    "home_appliance",
    "jewelry",
    "footwear",
]

DEFAULT_PERSONAS = [
    "browser_low_intent",
    "first_time_high_consideration",
    "price_sensitive_cautious",
    "gift_buyer_uncertain",
    "experienced_brand_loyal",
    "price_insensitive_decisive",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create PIWM-RealShoot-v1 manifest sample files.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/official/piwm_realshoot_v1"))
    parser.add_argument("--group-id", default="G001")
    args = parser.parse_args(argv)

    rows = build_rows(args.group_id)
    write_manifest(args.output_dir, rows)
    print(json.dumps(summary(rows, args.output_dir), ensure_ascii=False, indent=2))
    return 0


def build_rows(group_id: str) -> list[ShootingClipRecord]:
    rows: list[ShootingClipRecord] = []
    for index, state in enumerate(rules.SHOOTING_CUSTOMER_STATES, start=1):
        product = DEFAULT_PRODUCTS[(index - 1) % len(DEFAULT_PRODUCTS)]
        persona = DEFAULT_PERSONAS[(index - 1) % len(DEFAULT_PERSONAS)]
        for version in ("A", "B"):
            rows.append(
                ShootingClipRecord(
                    clip_id=f"{group_id}_S{index:02d}_{version}",
                    group_id=group_id,
                    shooting_state=state,
                    version=version,
                    product_category=product,
                    persona_type=persona,
                    post_compose_ui=state in rules.SHOOTING_CORE_STATES,
                )
            )
    return rows


def write_manifest(output_dir: Path, rows: list[ShootingClipRecord]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "realshoot_manifest_sample.jsonl"
    with manifest.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False, sort_keys=True) + "\n")

    template = output_dir / "realshoot_manifest_template.json"
    template.write_text(
        json.dumps(rows[0].model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    readme = output_dir / "README.md"
    readme.write_text(_readme(), encoding="utf-8")
    (output_dir / "realshoot_manifest_summary.json").write_text(
        json.dumps(summary(rows, output_dir), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def summary(rows: list[ShootingClipRecord], output_dir: Path) -> dict[str, Any]:
    return {
        "artifact": "PIWM-RealShoot-v1 manifest sample",
        "output_dir": output_dir.as_posix(),
        "n_rows": len(rows),
        "n_states": len({row.shooting_state for row in rows}),
        "versions": sorted({row.version for row in rows}),
        "core_states_require_hero": sorted(rules.SHOOTING_CORE_STATES),
        "schema": "ShootingClipRecord",
        "action_space": "DialogueAct v2 + TerminalRealization",
    }


def _readme() -> str:
    return """# PIWM-RealShoot-v1 Manifest Sample

This directory contains the real-shooting manifest template and a 12-state A/B sample.

Files:

- `realshoot_manifest_template.json`: one filled `ShootingClipRecord` example.
- `realshoot_manifest_sample.jsonl`: 24 rows, S01-S12 with A/B versions.
- `realshoot_manifest_summary.json`: counts and schema summary.

This is a manifest template, not a QA-reviewed real dataset. Keep `qa.overall_pass=false`
until actual video, audio, UI recording, transcript, and QA fields are filled.
"""


if __name__ == "__main__":
    raise SystemExit(main())
