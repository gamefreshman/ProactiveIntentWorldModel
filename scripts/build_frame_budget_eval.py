"""Build PIWM perception eval JSONL for frame-budget ablations.

The default PIWM setting samples K=3 frames from a 10s generated video. This
script creates comparable ms-swift eval files for K=1/K=3/K=5 without changing
the source dataset. It extracts additional frames into a sibling directory such
as ``frame_budget/k5`` under each video session and rewrites only the perception
input rows.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_train.ms_swift_adapter import build_ms_swift_record
from piwm_train.data_collator import SFTExample
from piwm_train.prompts import build_perception_prompt
from piwm_train.targets import build_perception_target

FRAME_PLANS: dict[int, list[tuple[float, str]]] = {
    1: [(5.0, "cue_peak")],
    3: [(2.0, "cue_onset"), (5.0, "cue_peak"), (8.0, "cue_resolution")],
    5: [
        (1.0, "pre_onset"),
        (3.0, "cue_onset"),
        (5.0, "cue_peak"),
        (7.0, "cue_settle"),
        (9.0, "post_settle"),
    ],
}


def build_frame_budget_eval(
    data_dir: Path,
    out_jsonl: Path,
    *,
    frame_budget: int,
    root: Path,
    overwrite_frames: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    if frame_budget not in FRAME_PLANS:
        raise ValueError(f"unsupported frame budget K={frame_budget}; expected one of {sorted(FRAME_PLANS)}")

    rows = _read_jsonl(data_dir / "state_inference.jsonl")
    if limit is not None:
        rows = rows[:limit]

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0
    n_extracted = 0
    skipped: list[dict[str, str]] = []
    with out_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            try:
                frames, extracted = _frames_for_budget(row, frame_budget, root=root, overwrite=overwrite_frames)
            except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
                skipped.append({"state_id": row.get("state_id", "unknown"), "error": str(exc)})
                continue
            n_extracted += extracted
            patched = json.loads(json.dumps(row, ensure_ascii=False))
            patched["input"]["frames"] = frames
            target = build_perception_target(patched)
            example = SFTExample(
                task="perception",
                source_id=f"{patched['state_id']}#k{frame_budget}",
                prompt=build_perception_prompt(patched),
                target=target,
                images=frames,
                meta={
                    "source_state_id": patched["state_id"],
                    "frame_budget": frame_budget,
                    "split": patched.get("meta", {}).get("split"),
                    "viewpoint": patched.get("meta", {}).get("viewpoint"),
                },
            )
            handle.write(json.dumps(build_ms_swift_record(example, root=root), ensure_ascii=False) + "\n")
            n_written += 1

    summary = {
        "artifact": "frame_budget_eval_jsonl",
        "data_dir": str(data_dir),
        "output_jsonl": str(out_jsonl),
        "frame_budget": frame_budget,
        "frame_plan": [
            {"index": index, "timestamp_sec": ts, "role": role}
            for index, (ts, role) in enumerate(FRAME_PLANS[frame_budget])
        ],
        "n_input_rows": len(rows),
        "n_written": n_written,
        "n_skipped": len(skipped),
        "n_frames_extracted": n_extracted,
        "skipped": skipped[:20],
    }
    out_jsonl.with_suffix(".summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def _frames_for_budget(row: dict[str, Any], frame_budget: int, *, root: Path, overwrite: bool) -> tuple[list[str], int]:
    session_dir = _session_dir_from_row(row, root=root)
    video = session_dir / "video.mp4"
    if not video.exists():
        raise FileNotFoundError(f"missing video.mp4 for {row.get('state_id')}: {video}")

    frames_dir = session_dir / "frame_budget" / f"k{frame_budget}"
    frames_dir.mkdir(parents=True, exist_ok=True)
    extracted = 0
    frame_refs: list[str] = []
    for index, (timestamp_sec, _role) in enumerate(FRAME_PLANS[frame_budget]):
        rel = session_dir.relative_to(root) / "frame_budget" / f"k{frame_budget}" / f"{index:03d}.jpg"
        out = root / rel
        if overwrite or not out.exists():
            _extract_one_frame(video, out, timestamp_sec)
            extracted += 1
        frame_refs.append(rel.as_posix())
    return frame_refs, extracted


def _session_dir_from_row(row: dict[str, Any], *, root: Path) -> Path:
    frames = row.get("input", {}).get("frames") or []
    if not frames:
        raise FileNotFoundError(f"row has no input frames: {row.get('state_id')}")
    first = Path(frames[0])
    if not first.is_absolute():
        first = root / first
    # Archive_generated_x/session_id/frames/000.jpg -> session_id dir.
    return first.resolve().parents[1]


def _extract_one_frame(video: Path, out: Path, timestamp_sec: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{timestamp_sec:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(out),
    ]
    subprocess.run(cmd, check=True)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, required=True)
    parser.add_argument("--frame-budget", type=int, required=True, choices=sorted(FRAME_PLANS))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--overwrite-frames", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_frame_budget_eval(
        args.data_dir,
        args.out_jsonl,
        frame_budget=args.frame_budget,
        root=args.root.resolve(),
        overwrite_frames=args.overwrite_frames,
        limit=args.limit,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
