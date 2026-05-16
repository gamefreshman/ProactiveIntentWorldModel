"""Index lightweight PIWM target-domain prompt-ready records for the main repo."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from piwm_data.migration.piwm_response_mapping import (
    piwm_response_to_action_key,
    piwm_response_to_action_spec,
)


DEFAULT_PIWM_ROOT = Path("/Users/mutsumi/Desktop/WorkSpace/piwm")
DEFAULT_OUTPUT_DIR = Path("data/official/piwm_target_promptready_v1")


def build_piwm_target_promptready_index(piwm_root: Path, output_dir: Path) -> dict[str, Any]:
    labeled_paths = sorted((piwm_root / "data" / "labeled").glob("piwm_*.json"))
    if not labeled_paths:
        raise FileNotFoundError(f"no labeled files under {piwm_root / 'data' / 'labeled'}")
    rows = []
    for path in labeled_paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        session_id = record["session_id"]
        video_path = piwm_root / "data" / "video" / f"{session_id}.mp4"
        prompt_path = piwm_root / "data" / "prompts" / f"{session_id}.md"
        manifest_path = piwm_root / "data" / "manifest" / f"{session_id}.json"
        seed_path = piwm_root / "data" / "seed" / f"{session_id}.txt"
        best_response = record["best_action"]
        rows.append(
            {
                "session_id": session_id,
                "source_labeled_path": path.as_posix(),
                "source_manifest_path": manifest_path.as_posix() if manifest_path.exists() else None,
                "source_seed_path": seed_path.as_posix() if seed_path.exists() else None,
                "source_prompt_path": prompt_path.as_posix() if prompt_path.exists() else None,
                "source_video_path": video_path.as_posix() if video_path.exists() else None,
                "media_status": "video_backed" if video_path.exists() else "video_pending",
                "generation_status": record.get("generation_status", "video_backed_existing" if video_path.exists() else "video_pending"),
                "qa_status": "synthetic_unreviewed" if not video_path.exists() else "video_backed_pending_or_separate_qa",
                "aida_stage": record.get("aida_stage"),
                "persona": record.get("persona"),
                "persona_type": _infer_persona_type(record.get("persona", "")),
                "best_response_id": best_response,
                "best_action_spec": piwm_response_to_action_spec(best_response),
                "best_action_key": piwm_response_to_action_key(best_response),
                "candidate_response_ids": record.get("candidate_actions", []),
                "candidate_action_specs": [
                    piwm_response_to_action_spec(response_id)
                    for response_id in record.get("candidate_actions", [])
                ],
                "candidate_action_keys": [
                    piwm_response_to_action_key(response_id)
                    for response_id in record.get("candidate_actions", [])
                ],
                "has_prompt": prompt_path.exists(),
                "has_manifest": manifest_path.exists(),
                "has_seed": seed_path.exists(),
                "has_labeled": path.exists(),
                "has_video": video_path.exists(),
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(rows, output_dir / "promptready_index.jsonl")
    summary = _summary(rows, piwm_root, output_dir)
    (output_dir / "_stats.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    return summary


def _summary(rows: list[dict[str, Any]], piwm_root: Path, output_dir: Path) -> dict[str, Any]:
    act_counts = Counter(row["best_action_spec"]["act"] for row in rows)
    return {
        "artifact": "piwm_target_promptready_index",
        "piwm_root": piwm_root.as_posix(),
        "output_dir": output_dir.as_posix(),
        "records": len(rows),
        "video_backed_records": sum(1 for row in rows if row["media_status"] == "video_backed"),
        "video_pending_records": sum(1 for row in rows if row["media_status"] == "video_pending"),
        "seed_records": sum(1 for row in rows if row["has_seed"]),
        "manifest_records": sum(1 for row in rows if row["has_manifest"]),
        "labeled_records": sum(1 for row in rows if row["has_labeled"]),
        "prompt_records": sum(1 for row in rows if row["has_prompt"]),
        "video_records": sum(1 for row in rows if row["has_video"]),
        "aida_stage_counts": dict(sorted(Counter(row["aida_stage"] for row in rows).items())),
        "best_dialogue_act_counts": dict(sorted(act_counts.items())),
        "best_response_id_counts": dict(sorted(Counter(row["best_response_id"] for row in rows).items())),
        "generation_status_counts": dict(sorted(Counter(row["generation_status"] for row in rows).items())),
        "red_lines": [
            "video_pending records are not multimodal training rows until Kling videos and sampled frames exist.",
            "promptready_index.jsonl is an upstream generation index, not an ms-swift SFT file.",
            "Only the existing 118 video-backed records can be imported into PIWM-Target-Frontcam-v1 today.",
        ],
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# PIWM Target Prompt-Ready Index",
        "",
        f"- records: {summary['records']}",
        f"- video_backed_records: {summary['video_backed_records']}",
        f"- video_pending_records: {summary['video_pending_records']}",
        f"- prompt_records: {summary['prompt_records']}",
        "",
        "## Best Dialogue Act Counts",
        "",
        "| Act | Count |",
        "|---|---:|",
    ]
    for act, count in summary["best_dialogue_act_counts"].items():
        lines.append(f"| {act} | {count} |")
    lines.extend([
        "",
        "## Red Lines",
        "",
    ])
    for item in summary["red_lines"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _infer_persona_type(text: str) -> str:
    if "价格" in text or "优惠" in text or "性价比" in text:
        return "price_sensitive_cautious"
    if "第一次" in text or "流程" in text:
        return "first_time_high_consideration"
    if "熟悉" in text or "品牌" in text:
        return "experienced_brand_loyal"
    if "给别人" in text or "礼物" in text:
        return "gift_buyer_uncertain"
    if "快速" in text or "目标明确" in text:
        return "price_insensitive_decisive"
    return "browser_low_intent"


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--piwm-root", type=Path, default=DEFAULT_PIWM_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = build_piwm_target_promptready_index(args.piwm_root, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
