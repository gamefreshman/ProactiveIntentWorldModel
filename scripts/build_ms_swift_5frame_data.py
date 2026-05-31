"""Build 5-frame ms-swift JSONL mirrors without touching frozen 3-frame data."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = [
    (1.0, "pre_onset"),
    (3.0, "cue_onset"),
    (5.0, "cue_peak"),
    (7.0, "cue_settle"),
    (9.0, "post_settle"),
]

TRAIN_FILES = [
    "piwm_train_stage1_user_intent_train_v1.jsonl",
    "piwm_train_stage1_next_state_prediction_train_v1.jsonl",
    "piwm_train_stage1_user_intent_val_v1.jsonl",
    "piwm_train_stage1_next_state_prediction_val_v1.jsonl",
    "piwm_train_stage2_target_5act_greet_aug_v2.jsonl",
    "piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2.jsonl",
    "piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl",
]

EVAL_FILES = [
    "target_frontcam_5act_test_action_selection.jsonl",
    "target_frontcam_5act_test_all.jsonl",
]


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    out_dir = args.out_dir.resolve()
    eval_out_dir = args.eval_out_dir.resolve()
    frames_dir = out_dir / "frames"
    video_index = build_video_index(root, args.video_root)

    outputs: list[dict[str, Any]] = []
    for name in TRAIN_FILES:
        src = args.ms_swift_dir / name
        if src.exists():
            outputs.append(convert_jsonl(src, out_dir / name, frames_dir, video_index, root, args.overwrite_frames))
    for name in EVAL_FILES:
        src = args.eval_dir / name
        if src.exists():
            outputs.append(convert_jsonl(src, eval_out_dir / name, frames_dir, video_index, root, args.overwrite_frames))

    summary = {
        "artifact": "ms_swift_5frame_data",
        "frame_plan": [
            {"index": i, "timestamp_sec": ts, "role": role}
            for i, (ts, role) in enumerate(DEFAULT_PLAN)
        ],
        "source_ms_swift_dir": str(args.ms_swift_dir),
        "source_eval_dir": str(args.eval_dir),
        "output_ms_swift_dir": str(out_dir),
        "output_eval_dir": str(eval_out_dir),
        "outputs": outputs,
    }
    (out_dir / "BUILD_5FRAME_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--ms-swift-dir", type=Path, default=REPO_ROOT / "data/official/ms_swift")
    parser.add_argument("--eval-dir", type=Path, default=REPO_ROOT / "data/official/domain_specialization_eval_v2")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data/official/ms_swift_5frame")
    parser.add_argument(
        "--eval-out-dir",
        type=Path,
        default=REPO_ROOT / "data/official/domain_specialization_eval_v2_5frame",
    )
    parser.add_argument("--video-root", type=Path, action="append", default=[])
    parser.add_argument("--overwrite-frames", action="store_true")
    return parser.parse_args()


def build_video_index(root: Path, extra_roots: Iterable[Path]) -> dict[str, Path]:
    candidates = [
        root / "piwm_videos_review/main",
        root / "local_artifacts/generated_videos",
        root / "archives",
        root.parent / "piwm/data/videos/synth",
    ]
    candidates.extend(extra_roots)
    index: dict[str, Path] = {}
    for base in candidates:
        if not base.exists():
            continue
        for video in base.rglob("*.mp4"):
            session_id = video.stem if video.parent == base else video.parent.name
            if SESSION_RE.fullmatch(session_id) and session_id not in index:
                index[session_id] = video.resolve()
    return index


SESSION_RE = re.compile(r"piwm_(?:[0-9a-f]{10}|\d{3})")


def convert_jsonl(
    src: Path,
    out: Path,
    frames_dir: Path,
    video_index: dict[str, Path],
    root: Path,
    overwrite_frames: bool,
) -> dict[str, Any]:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    missing_video: Counter[str] = Counter()
    frame_errors: Counter[str] = Counter()
    bad_sessions: set[str] = set()
    image_count: Counter[int] = Counter()
    task_count: Counter[str] = Counter()
    written = 0
    with src.open(encoding="utf-8") as inp, out.open("w", encoding="utf-8") as handle:
        for line in inp:
            if not line.strip():
                continue
            rows += 1
            row = json.loads(line)
            session_id = infer_session_id(row)
            video = video_index.get(session_id)
            if video is None:
                missing_video[session_id] += 1
                continue
            if session_id in bad_sessions:
                frame_errors[f"{session_id}: previous frame extraction failure"] += 1
                continue
            try:
                frame_paths = extract_frames(video, frames_dir / session_id, overwrite_frames)
            except Exception as exc:
                bad_sessions.add(session_id)
                frame_errors[f"{session_id}: {type(exc).__name__}: {exc}"] += 1
                continue
            patched = patch_row(row, frame_paths, root)
            handle.write(json.dumps(patched, ensure_ascii=False, separators=(",", ":")) + "\n")
            written += 1
            image_count[len(frame_paths)] += 1
            task_count[str(patched.get("task", "<missing>"))] += 1

    summary = {
        "source": str(src),
        "output": str(out),
        "input_rows": rows,
        "written_rows": written,
        "skipped_missing_video_rows": sum(missing_video.values()),
        "skipped_frame_error_rows": sum(frame_errors.values()),
        "missing_video_sessions": dict(missing_video.most_common(20)),
        "frame_error_examples": dict(frame_errors.most_common(20)),
        "image_count": dict(image_count),
        "task_count": dict(task_count),
        "sha256": sha256(out) if out.exists() else None,
    }
    out.with_suffix(".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def infer_session_id(row: dict[str, Any]) -> str:
    for image in row.get("images", []):
        match = SESSION_RE.search(str(image))
        if match:
            return match.group(0)
    source_id = str(row.get("source_id", ""))
    match = SESSION_RE.search(source_id)
    if match:
        return match.group(0)
    raise ValueError(f"cannot infer session id for row: {source_id}")


def extract_frames(video: Path, out_dir: Path, overwrite: bool) -> list[Path]:
    cv2 = load_cv2()
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise ValueError(f"failed to open video: {video}")
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
        duration = frame_count / fps if fps else 10.0
        paths: list[Path] = []
        for index, (timestamp, _role) in enumerate(DEFAULT_PLAN):
            timestamp = min(max(timestamp, 0.0), max(duration - 0.05, 0.0))
            out = out_dir / f"{index:03d}.jpg"
            if overwrite or not out.exists():
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
                ok, frame = cap.read()
                if not ok:
                    raise ValueError(f"failed to read frame at {timestamp:.3f}s from {video}")
                if not cv2.imwrite(str(out), frame):
                    raise ValueError(f"failed to write frame: {out}")
            paths.append(out.resolve())
        return paths
    finally:
        cap.release()


def patch_row(row: dict[str, Any], frames: list[Path], root: Path) -> dict[str, Any]:
    patched = json.loads(json.dumps(row, ensure_ascii=False))
    patched["images"] = [str(path) for path in frames]
    for message in patched.get("messages", []):
        if message.get("role") != "user":
            continue
        content = str(message.get("content", ""))
        content = re.sub(r"^(?:<image>)+", "<image>" * len(frames), content)
        content = re.sub(r"Below are \d+ frames", f"Below are {len(frames)} frames", content)
        content = re.sub(r"Below are \d+ frame", f"Below are {len(frames)} frame", content)
        content = content.replace("3 frames sampled", f"{len(frames)} frames sampled")
        content = content.replace("three frames", f"{len(frames)} frames")
        message["content"] = content
    meta = patched.setdefault("meta", {})
    meta["frame_budget"] = len(frames)
    meta["frame_sampling_plan"] = [
        {"index": i, "timestamp_sec": ts, "role": role}
        for i, (ts, role) in enumerate(DEFAULT_PLAN)
    ]
    meta["frame_budget_source"] = "derived_from_frozen_3frame_jsonl"
    return patched


def load_cv2():
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("OpenCV is required for 5-frame extraction") from exc
    return cv2


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    main()
