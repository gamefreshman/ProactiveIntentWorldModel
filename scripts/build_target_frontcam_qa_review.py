"""Build QA review sheets for PIWM-Target-Frontcam-v1 test rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_MAIN_SCHEMA = Path("data/official/piwm_target_v1/main_schema.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/official/piwm_target_v1/qa_review_target30_5act")
DEFAULT_FRAME_WIDTH = 260


def build_target_frontcam_qa_review(
    main_schema: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    split: str = "test",
    frame_width: int = DEFAULT_FRAME_WIDTH,
) -> dict[str, Any]:
    records = [row for row in _read_jsonl(main_schema) if row.get("split") == split]
    output_dir.mkdir(parents=True, exist_ok=True)
    templates_dir = output_dir / "manual_review_templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    review_rows = []
    for record in records:
        template_path = templates_dir / f"{record['state_id']}.qa_manual_review.json"
        template = _manual_review_template(record)
        template_path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        review_rows.append(_review_row(record, repo_root, template_path))

    sheets = _write_contact_sheets(review_rows, output_dir, frame_width=frame_width)
    report = {
        "artifact": "piwm_target_frontcam_qa_review",
        "main_schema": main_schema.as_posix(),
        "output_dir": output_dir.as_posix(),
        "split": split,
        "n_records": len(review_rows),
        "n_records_with_all_frames": sum(1 for row in review_rows if row["all_frames_exist"]),
        "n_missing_frames": sum(row["n_missing_frames"] for row in review_rows),
        "qa_status_before_review": "qa_pending_project_lead_review",
        "sheets": sheets,
        "review_rows": review_rows,
        "manual_review_instruction": "Fill each template, then promote passing rows to qa_reviewed in a later audited step.",
    }
    (output_dir / "qa_review_index.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "qa_review_index.md").write_text(_markdown(report, output_dir), encoding="utf-8")
    _write_jsonl(review_rows, output_dir / "qa_review_rows.jsonl")
    return report


def _review_row(record: dict[str, Any], repo_root: Path, template_path: Path) -> dict[str, Any]:
    frames = []
    for image in record["images"]:
        path = repo_root / image["relative_path"]
        frames.append(
            {
                "index": image["index"],
                "timestamp_sec": image.get("timestamp_sec"),
                "relative_path": image["relative_path"],
                "path": path.as_posix(),
                "exists": path.exists(),
            }
        )
    missing = sum(1 for frame in frames if not frame["exists"])
    return {
        "state_id": record["state_id"],
        "source_session_id": record.get("source_session_id"),
        "split": record.get("split"),
        "viewpoint": record.get("viewpoint"),
        "actor_profile": record.get("actor_profile"),
        "qa_status": record.get("qa_status"),
        "aida_stage": record.get("aida_stage"),
        "best_action": record.get("best_action"),
        "best_action_spec": record.get("best_action_spec"),
        "surface_text": (record.get("realization") or {}).get("surface_text", ""),
        "visual_summary": (record.get("visual_state") or {}).get("summary", ""),
        "frames": frames,
        "n_missing_frames": missing,
        "all_frames_exist": missing == 0,
        "manual_review_template": template_path.as_posix(),
    }


def _manual_review_template(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "state_id": record["state_id"],
        "source_session_id": record.get("source_session_id"),
        "qa_status_before_review": record.get("qa_status", "synthetic_unreviewed"),
        "viewpoint": record.get("viewpoint"),
        "checks": {
            "frontcam_view_pass": None,
            "customer_visible": None,
            "gaze_or_head_direction_visible": None,
            "body_posture_visible": None,
            "screen_or_cabinet_context_visible": None,
            "timeline_consistent_across_frames": None,
            "no_extra_subject_confusion": None,
            "label_matches_visual_evidence": None,
            "action_realization_reasonable": None,
        },
        "overall_pass": None,
        "warning_flags": [],
        "reviewer": "",
        "reviewed_at": "",
        "review_type": "",
        "notes": "",
    }


def _write_contact_sheets(rows: list[dict[str, Any]], output_dir: Path, *, frame_width: int) -> list[dict[str, Any]]:
    if not rows:
        return []
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.load_default()
    frame_height = round(frame_width * 9 / 16)
    padding = 12
    text_height = 78
    gap = 8
    per_sheet = 10
    panel_width = padding * 2 + 3 * frame_width + 2 * gap
    panel_height = padding * 2 + text_height + frame_height
    sheets = []
    for sheet_index, start in enumerate(range(0, len(rows), per_sheet)):
        chunk = rows[start:start + per_sheet]
        image = Image.new("RGB", (panel_width, panel_height * len(chunk)), "white")
        draw = ImageDraw.Draw(image)
        for row_index, row in enumerate(chunk):
            top = row_index * panel_height
            draw.rectangle([0, top, panel_width - 1, top + panel_height - 1], outline=(210, 210, 210))
            lines = [
                f"{row['state_id']} | {row['source_session_id']} | {row['aida_stage']} | {row['best_action_spec']['act']}",
                f"action={row['best_action']}",
                f"text={row['surface_text'][:100]}",
                f"review={Path(row['manual_review_template']).name}",
            ]
            for i, line in enumerate(lines):
                draw.text((padding, top + padding + i * 16), line, fill=(20, 20, 20), font=font)
            frame_top = top + padding + text_height
            for col, frame in enumerate(row["frames"][:3]):
                left = padding + col * (frame_width + gap)
                box = (left, frame_top, left + frame_width, frame_top + frame_height)
                if frame["exists"]:
                    with Image.open(frame["path"]) as frame_image:
                        thumb = _letterbox(frame_image.convert("RGB"), (frame_width, frame_height))
                    image.paste(thumb, (left, frame_top))
                else:
                    draw.rectangle(box, fill=(245, 245, 245), outline=(180, 180, 180))
                    draw.text((left + 8, frame_top + 8), "missing", fill=(160, 0, 0), font=font)
                draw.text(
                    (left + 4, frame_top + frame_height - 16),
                    f"{frame['index']} @{frame.get('timestamp_sec')}s",
                    fill=(255, 255, 255),
                    font=font,
                )
        sheet_path = output_dir / f"target_frontcam_qa_sheet_{sheet_index:02d}.jpg"
        image.save(sheet_path, quality=90)
        for row in chunk:
            row["contact_sheet"] = sheet_path.as_posix()
        sheets.append({"sheet_index": sheet_index, "path": sheet_path.as_posix(), "n_records": len(chunk)})
    return sheets


def _letterbox(image, size: tuple[int, int]):
    from PIL import Image

    image.thumbnail(size)
    canvas = Image.new("RGB", size, (30, 30, 30))
    left = (size[0] - image.width) // 2
    top = (size[1] - image.height) // 2
    canvas.paste(image, (left, top))
    return canvas


def _markdown(report: dict[str, Any], output_dir: Path) -> str:
    lines = [
        "# PIWM Target Frontcam QA Review",
        "",
        f"- split: `{report['split']}`",
        f"- records: {report['n_records']}",
        f"- records_with_all_frames: {report['n_records_with_all_frames']}",
        f"- missing_frames: {report['n_missing_frames']}",
        "",
        "## Contact Sheets",
        "",
    ]
    for sheet in report["sheets"]:
        path = Path(sheet["path"])
        rel = path.relative_to(output_dir).as_posix()
        lines.extend([f"### Sheet {sheet['sheet_index']:02d}", "", f"![{path.name}]({rel})", ""])
    lines.extend(["## Review Rows", "", "| state_id | source | act | template |", "|---|---|---|---|"])
    for row in report["review_rows"]:
        template = Path(row["manual_review_template"]).relative_to(output_dir).as_posix()
        lines.append(f"| `{row['state_id']}` | `{row['source_session_id']}` | `{row['best_action_spec']['act']}` | `{template}` |")
    lines.append("")
    return "\n".join(lines)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
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
    parser.add_argument("--main-schema", type=Path, default=DEFAULT_MAIN_SCHEMA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--split", default="test")
    parser.add_argument("--frame-width", type=int, default=DEFAULT_FRAME_WIDTH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_target_frontcam_qa_review(
        args.main_schema,
        args.output_dir,
        repo_root=Path.cwd(),
        split=args.split,
        frame_width=args.frame_width,
    )
    print(json.dumps({k: v for k, v in report.items() if k != "review_rows"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
