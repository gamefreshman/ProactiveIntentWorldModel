"""Build a small general-corpus salesperson annotation probe pack.

This pack complements the target-frontcam annotation pack with general retail
synthetic scenes. It uses the same Chinese annotation columns and hides PIWM
theory labels from annotators.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from piwm_data.annotation_act_terms import EN_TO_CN_ACT, OPERATIONAL_5ACTS
from scripts.build_salesperson_annotation_pack_v2 import (
    ANNOTATOR_COLUMNS,
    build_scene_description,
    write_csv,
    write_xlsx,
)


DEFAULT_MAIN_SCHEMA = ROOT / "data/official/piwm_train_synth_v2/main_schema.jsonl"
DEFAULT_OUT_DIR = ROOT / "data/official/annotation_pack_general_probe_v1"
DEFAULT_VIDEO_DIR = ROOT / "piwm_videos_review/main"
DEFAULT_PER_ACT = 5
GENERAL_PROBE_ACTS = ("Elicit", "Inform", "Recommend", "Hold")
SOURCE_SAMPLING_POLICY = (
    "deterministic_balanced_probe_from_general_v2_main_schema_state_id_order_"
    "5_per_available_4act_with_local_video"
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def resolve_image_paths(record: dict[str, Any]) -> list[Path]:
    resolved: list[Path] = []
    for image in record.get("images") or []:
        relative_path = image.get("relative_path") or image.get("path")
        if not relative_path:
            return []
        path = Path(relative_path)
        candidates = [path] if path.is_absolute() else [
            ROOT / path,
            ROOT / "local_artifacts/generated_videos" / path,
            ROOT / "local_artifacts" / path,
        ]
        found = next((candidate for candidate in candidates if candidate.exists()), None)
        if not found:
            return []
        resolved.append(found)
    return resolved[:3] if len(resolved) >= 3 else []


def extract_video_frames(video_path: Path, output_dir: Path, sample_id: str) -> list[Path]:
    try:
        import cv2  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "General probe image frames are missing and video extraction requires cv2. "
            "Run with: uv run --with opencv-python-headless --with openpyxl python "
            "scripts/build_general_probe_annotation_pack_v1.py"
        ) from exc

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"cannot open video: {video_path}")
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if frame_count <= 0:
        raise RuntimeError(f"video has no readable frames: {video_path}")

    positions = [max(0, min(frame_count - 1, int(frame_count * ratio))) for ratio in (0.2, 0.5, 0.8)]
    output_paths: list[Path] = []
    for index, position in enumerate(positions):
        capture.set(cv2.CAP_PROP_POS_FRAMES, position)
        ok, frame = capture.read()
        if not ok:
            raise RuntimeError(f"failed reading frame {position} from {video_path}")
        output_path = output_dir / f"{sample_id}_{index}.jpg"
        if not cv2.imwrite(str(output_path), frame):
            raise RuntimeError(f"failed writing frame: {output_path}")
        output_paths.append(output_path)
    capture.release()
    return output_paths


def select_records(records: list[dict[str, Any]], per_act: int) -> list[dict[str, Any]]:
    by_act: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in sorted(records, key=lambda item: item["state_id"]):
        act = (record.get("best_action_spec") or {}).get("act")
        if act in GENERAL_PROBE_ACTS and (DEFAULT_VIDEO_DIR / f"{record['state_id']}.mp4").exists():
            by_act[act].append(record)

    missing = {act: per_act - len(by_act.get(act, [])) for act in GENERAL_PROBE_ACTS if len(by_act.get(act, [])) < per_act}
    if missing:
        raise RuntimeError(f"not enough general records with videos for balanced probe: {missing}")

    selected: list[dict[str, Any]] = []
    for act in GENERAL_PROBE_ACTS:
        selected.extend(by_act[act][:per_act])
    return selected


def build_rows(main_schema: Path, out_dir: Path, per_act: int) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    records = select_records(read_jsonl(main_schema), per_act)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    annotator_rows: list[dict[str, str]] = []
    holdout_rows: list[dict[str, Any]] = []
    for record in records:
        sample_id = record["state_id"]
        source_frames = resolve_image_paths(record)
        if not source_frames:
            video_path = DEFAULT_VIDEO_DIR / f"{sample_id}.mp4"
            source_frames = extract_video_frames(video_path, frames_dir, sample_id)

        copied_frames: list[str] = []
        for index, source in enumerate(source_frames[:3]):
            destination = frames_dir / f"{sample_id}_{index}.jpg"
            if source != destination:
                shutil.copy2(source, destination)
            copied_frames.append(f"frames/{destination.name}")

        act = (record.get("best_action_spec") or {}).get("act")
        candidate_acts = sorted({item.get("act") for item in record.get("candidate_action_specs", []) if item.get("act") in OPERATIONAL_5ACTS})
        annotator_rows.append(
            {
                "样本ID": sample_id,
                "第1张图": copied_frames[0],
                "第2张图": copied_frames[1],
                "第3张图": copied_frames[2],
                "场景描述": build_scene_description(record, scene_prefix="顾客在普通零售导购场景中"),
            }
        )
        holdout_rows.append(
            {
                "sample_id": sample_id,
                "dataset_split": "general_probe",
                "source_dataset": "PIWM-Train-Synth-v2/main_schema",
                "source_sampling_policy": SOURCE_SAMPLING_POLICY,
                "source_role": "synthetic_general_training_corpus_probe_not_heldout_eval",
                "annotation_analysis_role": "general_schema_transfer_probe",
                "kappa_report_groups": "general_4act_without_greet",
                "system_stage_label": record.get("aida_stage"),
                "system_intent_label": record.get("intent"),
                "system_best_act": act,
                "system_best_act_zh": EN_TO_CN_ACT[act],
                "theory_go_no_go": "不介入" if act == "Hold" else "介入",
                "candidate_acts": "|".join(candidate_acts),
                "candidate_acts_zh": "|".join(EN_TO_CN_ACT[act] for act in candidate_acts if act in EN_TO_CN_ACT),
                "visual_summary": (record.get("visual_state") or {}).get("summary"),
                "engagement_pattern": (record.get("visual_state") or {}).get("engagement_pattern"),
                "gaze_and_attention": (record.get("visual_state") or {}).get("gaze_and_attention"),
                "body_and_hands": (record.get("visual_state") or {}).get("body_and_hands"),
            }
        )

    return annotator_rows, holdout_rows


def write_readme(out_dir: Path, per_act: int) -> None:
    text = f"""# PIWM General Probe 售货员标注包 v1

本目录是 target-frontcam 30 条标注包之外的 general retail 对照标注包，用于检查同一套中文 5-act 标注表在普通零售导购场景中的适用性。

## 范围

- 样本数：{per_act * len(GENERAL_PROBE_ACTS)} 条。
- 当前 general v2 数据中没有 `Greet` 作为 best act，因此本 probe 覆盖：询问需求 / 介绍信息 / 推荐商品 / 继续观察等待。
- 本包不替代 target 评测集，只作为专家行为验证和论文分析补充。

## 来源与抽样

- 来源文件：`data/official/piwm_train_synth_v2/main_schema.jsonl`。
- 来源角色：这是 general synthetic training corpus 的 probe 抽样，不是 held-out general test，也不是重新生成的新数据。
- 抽样方式：按 `state_id` 稳定排序，在有本地 mp4 可抽帧的样本中，对 Elicit / Inform / Recommend / Hold 各取前 {per_act} 条。
- 解读边界：本包的 κ 只能说明“销售员在这批 general synthetic 场景上的标注一致性”，不能当作模型 general-domain held-out 评测结论。

## κ 报告口径

- 本包只覆盖 4 个动作：询问需求 / 介绍信息 / 推荐商品 / 继续观察等待。
- 因为 target 包含 Greet，而本包不包含 Greet，跨域对比时应使用 target 的 `target_4act_without_greet` 子集，而不是直接拿 target 全 5-act κ 与 general 4-act κ 比。
- target 仍应单独报告 `target_5act_all`，用于说明完整 target 评测集中的专家一致性。

## 标注负担

- target 包 30 条 + general probe 20 条 = 每位售货员 50 条。
- 如果公司接口人反馈负担过重，优先保留 target 30 条；general probe 可以降到每 act 3 条，即 12 条。

## 文件

- `annotation_template_three_annotators.xlsx`：三位售货员填写模板。
- `annotation_template_three_annotators_with_images.xlsx`：已嵌入图片的版本。
- `annotation_template_single_annotator.csv`：单人 CSV 模板。
- `frames/`：每条 3 张图。
- `theory_labels_holdout.csv/jsonl`：系统理论标签，不给售货员看。
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    annotator_rows, holdout_rows = build_rows(args.main_schema, args.output_dir, args.per_act)
    write_csv(args.output_dir / "annotation_template_single_annotator.csv", annotator_rows, ANNOTATOR_COLUMNS)
    xlsx_generated = write_xlsx(args.output_dir / "annotation_template_three_annotators.xlsx", annotator_rows, ANNOTATOR_COLUMNS)
    xlsx_with_images_generated = write_xlsx(
        args.output_dir / "annotation_template_three_annotators_with_images.xlsx",
        annotator_rows,
        ANNOTATOR_COLUMNS,
        embed_images=True,
        image_base_dir=args.output_dir,
    )
    columns = [
        "sample_id",
        "dataset_split",
        "source_dataset",
        "source_sampling_policy",
        "source_role",
        "annotation_analysis_role",
        "kappa_report_groups",
        "system_stage_label",
        "system_intent_label",
        "system_best_act",
        "system_best_act_zh",
        "theory_go_no_go",
        "candidate_acts",
        "candidate_acts_zh",
        "visual_summary",
        "engagement_pattern",
        "gaze_and_attention",
        "body_and_hands",
    ]
    write_csv(args.output_dir / "theory_labels_holdout.csv", holdout_rows, columns)
    with (args.output_dir / "theory_labels_holdout.jsonl").open("w", encoding="utf-8") as handle:
        for row in holdout_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    write_readme(args.output_dir, args.per_act)
    return {
        "output_dir": str(args.output_dir),
        "samples": len(annotator_rows),
        "frames": len(list((args.output_dir / "frames").glob("*.jpg"))),
        "xlsx": str(args.output_dir / "annotation_template_three_annotators.xlsx"),
        "xlsx_generated": xlsx_generated,
        "xlsx_with_images": str(args.output_dir / "annotation_template_three_annotators_with_images.xlsx"),
        "xlsx_with_images_generated": xlsx_with_images_generated,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-schema", type=Path, default=DEFAULT_MAIN_SCHEMA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--per-act", type=int, default=DEFAULT_PER_ACT)
    return parser


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
