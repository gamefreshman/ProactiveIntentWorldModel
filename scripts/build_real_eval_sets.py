"""Build ms-swift evaluation rows for the PIWM real-video eval set.

The public real annotations are one JSON file per session.  This script adapts
those annotations to the existing PIWM evaluators by extracting video frames and
emitting leakage-free Stage-1 user-intent rows plus Stage-2 5-act action rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import cv2

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from piwm_train import config
from piwm_train.prompts import PIWM_SYSTEM_PROMPT, build_action_prompt_no_leak, build_user_intent_prompt

DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "real_eval_20260525"
STAGE_CONDITIONED_ACT_ORDER = {
    "attention": ("Greet", "Elicit", "Inform", "Hold"),
    "interest": ("Elicit", "Inform", "Recommend", "Hold"),
    "desire": ("Inform", "Recommend", "Hold"),
    "action": ("Greet", "Recommend", "Hold"),
}
BEST_ACTION_TO_ACT = {
    "greet": "Greet",
    "elicit": "Elicit",
    "inform": "Inform",
    "recommend": "Recommend",
    "hold": "Hold",
}
BEST_ACTION_TO_INTENT = {
    "greet": "no_clear_intent",
    "elicit": "explore_options",
    "inform": "compare_value_for_money",
    "recommend": "confirm_choice",
    "hold": "no_clear_intent",
}
ACTION_TEMPLATES = {
    "Greet": {
        "params": {"phase": "open"},
        "utterance": "欢迎光临，需要时我可以帮您。",
        "screen_action": "show_welcome_message",
        "voice_style": "warm",
        "light": "soft_welcome",
        "physical_action": "智能售货柜以简短欢迎语和柔和灯效提示可用性。",
    },
    "Elicit": {
        "params": {"openness": "open", "slot": "need_focus"},
        "utterance": "您想先了解价格、口味，还是适合什么场景？",
        "screen_action": "show_choice_bubbles",
        "voice_style": "curious",
        "light": "soft_invitation",
        "physical_action": "智能售货柜展示轻量选项，邀请顾客表达关注点。",
    },
    "Inform": {
        "params": {"content_type": "comparison", "depth": "brief"},
        "utterance": "这几款主要区别在口味、容量和价格，我可以帮您快速对比。",
        "screen_action": "show_comparison_or_details",
        "voice_style": "clear",
        "light": "soft_breathing",
        "physical_action": "智能售货柜展示简短对比信息，避免长篇推销。",
    },
    "Recommend": {
        "params": {"target": "item", "pressure": "soft"},
        "utterance": "如果您想省心选择，可以优先看这款更稳妥的。",
        "screen_action": "highlight_soft_recommendation",
        "voice_style": "calm",
        "light": "highlight_one_option_soft",
        "physical_action": "智能售货柜轻量高亮一个选项，并保留顾客选择空间。",
    },
    "Hold": {
        "params": {"mode": "silent"},
        "utterance": "",
        "screen_action": "idle_minimal",
        "voice_style": "silent",
        "light": "maintain_current_soft_breathing",
        "physical_action": "智能售货柜保持静默和低亮度待机，不主动打断顾客。",
    },
}


def main() -> int:
    args = parse_args()
    real_dir = resolve_real_dir(args.real_dir)
    out_dir = resolve_path(args.out_dir)
    timestamps = parse_timestamps(args.timestamps)

    human_records = read_real_records(real_dir)
    media_roots = resolve_media_roots(args.media_root, real_dir)
    derived_records = (
        derive_index_records(real_dir, media_roots, {record["session_id"] for record in human_records})
        if args.include_index_derived_missing
        else []
    )
    records = sorted(human_records + derived_records, key=session_sort_key)
    frame_dir = out_dir / "frames"

    user_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    runnable_records: list[dict[str, Any]] = []
    skipped_missing_video: list[dict[str, str]] = []

    for record in records:
        video = find_video(record, media_roots)
        if video is None:
            skipped_missing_video.append(
                {
                    "session_id": record["session_id"],
                    "video_path": str(record.get("video_path", "")),
                }
            )
            continue
        images = extract_frames(video, frame_dir / record["session_id"], timestamps, overwrite=args.overwrite_frames)
        image_paths = [display_path(path) for path in images]
        runnable_records.append(record)
        user_rows.append(build_user_row(record, image_paths))
        action_rows.append(build_action_row(record, image_paths))

    out_dir.mkdir(parents=True, exist_ok=True)
    user_path = out_dir / "real_user_intent.jsonl"
    action_path = out_dir / "real_action_selection_5act.jsonl"
    all_path = out_dir / "real_all_scored.jsonl"
    write_jsonl(user_path, user_rows)
    write_jsonl(action_path, action_rows)
    write_jsonl(all_path, user_rows + action_rows)

    manifest = {
        "artifact": "piwm_real_eval_ms_swift",
        "is_training_result": False,
        "source_real_dir": display_path(real_dir),
        "out_dir": display_path(out_dir),
        "frame_timestamps_sec": timestamps,
        "human_annotation_records": len(human_records),
        "index_derived_weak_label_records": len(derived_records),
        "total_eval_records_before_video_filter": len(records),
        "runnable_records_with_video": len(runnable_records),
        "skipped_missing_video_count": len(skipped_missing_video),
        "skipped_missing_video": skipped_missing_video,
        "stage_counts_before_video_filter": dict(sorted(Counter(row["aida_stage"] for row in records).items())),
        "best_action_counts_before_video_filter": dict(sorted(Counter(row["best_action"] for row in records).items())),
        "stage_counts_runnable": dict(sorted(Counter(row["aida_stage"] for row in runnable_records).items())),
        "best_action_counts_runnable": dict(sorted(Counter(row["best_action"] for row in runnable_records).items())),
        "label_source_counts_runnable": dict(sorted(Counter(label_source(row) for row in runnable_records).items())),
        "intent_label_policy": "heuristic_from_best_action; stage/action metrics are the primary real-set metrics",
        "jsonl": {
            "user_intent": display_path(user_path),
            "action_selection_5act": display_path(action_path),
            "all_scored": display_path(all_path),
        },
        "task_counts": {
            "user_intent": len(user_rows),
            "action_selection_5act": len(action_rows),
            "all_scored": len(user_rows) + len(action_rows),
        },
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(render_readme(manifest), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--real-dir",
        type=Path,
        default=None,
        help="Directory containing index.json and real_*.json. Defaults to data/eval/real, then references/piwm_lightweight/data/eval/real.",
    )
    parser.add_argument(
        "--media-root",
        type=Path,
        action="append",
        default=None,
        help="Root used to resolve record video_path values. Can be passed multiple times.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timestamps", default="0,5,10", help="Comma-separated frame timestamps in seconds.")
    parser.add_argument("--overwrite-frames", action="store_true")
    parser.add_argument(
        "--include-index-derived-missing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use index.json group labels for videos that exist but lack per-session real_*.json annotations.",
    )
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def resolve_real_dir(path: Path | None) -> Path:
    candidates = [path] if path else [
        REPO_ROOT / "data" / "eval" / "real",
        REPO_ROOT / "references" / "piwm_lightweight" / "data" / "eval" / "real",
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        resolved = resolve_path(candidate)
        if (resolved / "index.json").exists():
            return resolved
    tried = ", ".join(str(resolve_path(candidate)) for candidate in candidates if candidate is not None)
    raise FileNotFoundError(f"could not find real eval directory; tried: {tried}")


def resolve_media_roots(paths: list[Path] | None, real_dir: Path) -> list[Path]:
    roots = [resolve_path(path) for path in paths] if paths else []
    roots.extend(
        [
            REPO_ROOT,
            REPO_ROOT / "references" / "piwm_lightweight",
            real_dir.parents[2] if len(real_dir.parents) >= 3 else real_dir,
        ]
    )
    unique: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in unique:
            unique.append(resolved)
    return unique


def parse_timestamps(raw: str) -> list[float]:
    timestamps = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if not timestamps:
        raise ValueError("--timestamps must contain at least one value")
    return timestamps


def read_real_records(real_dir: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(real_dir.glob("real_*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        record.setdefault("label_source", "human_json_annotation")
        records.append(record)
    if not records:
        raise FileNotFoundError(f"no real_*.json files found in {real_dir}")
    return records


def derive_index_records(real_dir: Path, media_roots: list[Path], existing_session_ids: set[str]) -> list[dict[str, Any]]:
    index_path = real_dir / "index.json"
    if not index_path.exists():
        return []
    index = json.loads(index_path.read_text(encoding="utf-8"))
    derived: list[dict[str, Any]] = []
    for group_id, group in sorted((index.get("groups") or {}).items(), key=lambda item: item[0]):
        start, end = parse_id_range(str(group["shooting_ids"]))
        for number in range(start, end + 1):
            session_id = f"real_{number:03d}"
            if session_id in existing_session_ids:
                continue
            record = index_group_record(session_id, number, group_id, group)
            if find_video(record, media_roots) is not None:
                derived.append(record)
    return derived


def parse_id_range(raw: str) -> tuple[int, int]:
    start, end = raw.split("-", 1)
    return int(start), int(end)


def index_group_record(session_id: str, number: int, group_id: str, group: dict[str, Any]) -> dict[str, Any]:
    stage = group.get("aida_stage")
    stage_candidates = group.get("aida_stages")
    if stage is None and stage_candidates:
        stage = stage_candidates[0]
    if not isinstance(stage, str):
        raise ValueError(f"could not derive aida_stage for index group {group_id}")
    best_action = str(group["best_action"]).lower()
    bdi = weak_bdi(stage, best_action)
    label = str(group.get("label", "real video group"))
    return {
        "session_id": session_id,
        "video_path": f"data/videos/real/{number}.mp4",
        "persona": f"index-derived weak label: {label}",
        "persona_visual": "",
        "aida_stage": stage,
        "aida_stage_candidates": stage_candidates or [stage],
        "bdi": bdi,
        "observable_behavior": f"Index group label indicates: {label}. Per-session visual annotation is not available.",
        "facial_expression": "Per-session facial-expression annotation is not available; evaluate primarily on stage/action labels.",
        "body_posture": "Per-session body-posture annotation is not available; evaluate primarily on stage/action labels.",
        "timeline": {},
        "best_action": best_action,
        "label_source": "index_group_weak_label",
        "weak_label_reason": "video exists in data/videos/real but per-session data/eval/real JSON is missing",
        "index_group_id": group_id,
        "index_group_label": label,
    }


def weak_bdi(stage: str, best_action: str) -> dict[str, str]:
    templates = {
        "greet": {
            "belief": "The customer has noticed the terminal but has not formed a clear purchase goal.",
            "desire": "The customer may want a low-pressure introduction.",
            "intention": "The customer is likely to briefly observe before deciding whether to engage.",
        },
        "elicit": {
            "belief": "The customer sees possible options but has not clarified the main need.",
            "desire": "The customer wants help narrowing the choice space.",
            "intention": "The customer is likely to keep browsing unless prompted with a light question.",
        },
        "inform": {
            "belief": "The customer is comparing options and needs concrete product differences.",
            "desire": "The customer wants useful information before deciding.",
            "intention": "The customer is likely to continue evaluating options.",
        },
        "recommend": {
            "belief": "The customer has narrowed attention to a plausible choice but still hesitates.",
            "desire": "The customer wants confidence to make a decision.",
            "intention": "The customer is close to deciding but may benefit from a soft recommendation.",
        },
        "hold": {
            "belief": "The customer is occupied or not seeking assistance.",
            "desire": "The customer wants to continue without interruption.",
            "intention": "The customer is likely to proceed independently or disengage.",
        },
    }
    return templates.get(best_action) or {
        "belief": f"The customer appears to be in the {stage} stage.",
        "desire": "The customer wants to continue the current interaction naturally.",
        "intention": "The customer is likely to keep following the current behavior.",
    }


def find_video(record: dict[str, Any], media_roots: list[Path]) -> Path | None:
    session_num = int(str(record["session_id"]).split("_", 1)[1])
    rel = Path(record.get("video_path", ""))
    candidates = [rel]
    candidates.extend(
        [
            Path("data") / "videos" / "real" / f"{session_num}.mp4",
            Path("data") / "videos" / "real" / f"{session_num:02d}.mp4",
        ]
    )
    for root in media_roots:
        for candidate in candidates:
            path = candidate if candidate.is_absolute() else root / candidate
            if path.exists():
                return path.resolve()
    return None


def extract_frames(video: Path, out_dir: Path, timestamps: list[float], *, overwrite: bool) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f"could not open video: {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if fps else 0.0
    outputs: list[Path] = []
    try:
        for index, timestamp in enumerate(timestamps):
            out_path = out_dir / f"{index:03d}.jpg"
            outputs.append(out_path)
            if out_path.exists() and not overwrite:
                continue
            target_ts = min(max(timestamp, 0.0), max(duration - 0.05, 0.0)) if duration else max(timestamp, 0.0)
            frame_index = int(round(target_ts * fps)) if fps else 0
            if frame_count:
                frame_index = min(max(frame_index, 0), frame_count - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError(f"could not read frame {frame_index} at {timestamp}s from {video}")
            if not cv2.imwrite(str(out_path), frame):
                raise RuntimeError(f"could not write frame: {out_path}")
    finally:
        cap.release()
    return outputs


def build_user_row(record: dict[str, Any], images: list[str]) -> dict[str, Any]:
    intent = intent_label(record)
    prompt_record = {
        "input": {"frames": images},
        "meta": {"viewpoint": "target_frontcam", "product_category": "smart_vending_retail"},
    }
    return {
        "messages": [
            {"role": "system", "content": PIWM_SYSTEM_PROMPT},
            {"role": "user", "content": clean_prompt_text(build_user_intent_prompt(prompt_record))},
            {"role": "assistant", "content": build_user_target(record, intent)},
        ],
        "images": images,
        "task": "user_intent",
        "source_id": record["session_id"],
        "weight": 1.0,
        "loss_weight": 1.0,
        "meta": {
            "split": "real_eval",
            "viewpoint": "real_frontcam",
            "stage": record["aida_stage"],
            "intent_label": intent,
            "best_action": record["best_action"],
            "label_source": label_source(record),
            "weak_label_reason": record.get("weak_label_reason"),
            "intent_label_policy": "heuristic_from_best_action",
        },
    }


def build_action_row(record: dict[str, Any], images: list[str]) -> dict[str, Any]:
    state_summary = state_summary_from_record(record)
    candidate_block = candidate_blocks(record)
    chosen = chosen_candidate(candidate_block, best_act(record))
    prompt_record = {"meta": {"frames": images, "state_summary": state_summary, "candidate_block": candidate_block}}
    return {
        "messages": [
            {"role": "system", "content": PIWM_SYSTEM_PROMPT},
            {"role": "user", "content": clean_prompt_text(build_action_prompt_no_leak(prompt_record, five_act_only=True))},
            {"role": "assistant", "content": build_action_target(chosen)},
        ],
        "images": images,
        "task": "action_selection_5act",
        "source_id": record["session_id"],
        "weight": 1.0,
        "loss_weight": 1.0,
        "meta": {
            "split": "real_eval",
            "viewpoint": "real_frontcam",
            "stage": record["aida_stage"],
            "best_act": best_act(record),
            "candidate_action_acts": {item["action"]: item["dialogue_act"]["act"] for item in candidate_block},
            "five_act_only": True,
            "label_source": label_source(record),
            "weak_label_reason": record.get("weak_label_reason"),
            "leakage_control": "gold_state_given_no_reward_no_predicted_outcome_in_prompt",
        },
    }


def state_summary_from_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "aida_stage": record["aida_stage"],
        "intent": intent_label(record),
        "visual_state": {
            "summary": record.get("observable_behavior", ""),
            "engagement_pattern": record.get("observable_behavior", ""),
            "gaze_and_attention": record.get("facial_expression", ""),
            "body_and_hands": record.get("body_posture", ""),
        },
        "bdi": record["bdi"],
    }


def build_user_target(record: dict[str, Any], intent: str) -> str:
    visual = state_summary_from_record(record)["visual_state"]
    bdi = record["bdi"]
    return "\n".join(
        [
            f"{config.TAG_STAGE_OPEN}{record['aida_stage']}{config.TAG_STAGE_CLOSE}",
            f"{config.TAG_INTENT_LABEL_OPEN}{intent}{config.TAG_INTENT_LABEL_CLOSE}",
            f"{config.TAG_VISUAL_SUMMARY_OPEN}{visual['summary']}{config.TAG_VISUAL_SUMMARY_CLOSE}",
            f"{config.TAG_ENGAGEMENT_PATTERN_OPEN}{visual['engagement_pattern']}{config.TAG_ENGAGEMENT_PATTERN_CLOSE}",
            f"{config.TAG_GAZE_AND_ATTENTION_OPEN}{visual['gaze_and_attention']}{config.TAG_GAZE_AND_ATTENTION_CLOSE}",
            f"{config.TAG_BODY_AND_HANDS_OPEN}{visual['body_and_hands']}{config.TAG_BODY_AND_HANDS_CLOSE}",
            f"{config.TAG_BELIEF_OPEN}{bdi['belief']}{config.TAG_BELIEF_CLOSE}",
            f"{config.TAG_DESIRE_OPEN}{bdi['desire']}{config.TAG_DESIRE_CLOSE}",
            f"{config.TAG_INTENTION_OPEN}{bdi['intention']}{config.TAG_INTENTION_CLOSE}",
        ]
    )


def build_action_target(chosen: dict[str, Any]) -> str:
    realization = chosen["action_realization"]
    act = chosen["dialogue_act"]["act"]
    utterance = realization.get("utterance") or "（静默）"
    return "\n".join(
        [
            f"{config.TAG_RATIONALE_OPEN}Real-set gold action is {act} for this visible customer state.{config.TAG_RATIONALE_CLOSE}",
            f"{config.TAG_CHOSEN_OPEN}{chosen['action']}{config.TAG_CHOSEN_CLOSE}",
            f"{config.TAG_INTERVENTION_ACTION_OPEN}{realization['physical_action']}{config.TAG_INTERVENTION_ACTION_CLOSE}",
            f"{config.TAG_INTERVENTION_UTTERANCE_OPEN}{utterance}{config.TAG_INTERVENTION_UTTERANCE_CLOSE}",
        ]
    )


def candidate_blocks(record: dict[str, Any]) -> list[dict[str, Any]]:
    stage = record["aida_stage"]
    acts = STAGE_CONDITIONED_ACT_ORDER.get(stage)
    if acts is None:
        raise ValueError(f"unsupported aida_stage: {stage}")
    best = best_act(record)
    if best not in acts:
        acts = tuple(dict.fromkeys([best, *acts]))
    return [action_block(record["session_id"], stage, act) for act in acts]


def action_block(session_id: str, stage: str, act: str) -> dict[str, Any]:
    template = dict(ACTION_TEMPLATES[act])
    params = template["params"]
    action_seed = f"{act}_{stage}_real_{session_id}"
    digest = hashlib.sha1(f"{action_seed}|{act}|{json.dumps(params, sort_keys=True)}".encode("utf-8")).hexdigest()[:12]
    label = f"{action_seed}_{digest}"
    utterance = template["utterance"]
    return {
        "action": label,
        "action_spec": {"act": act, "params": params},
        "dialogue_act": {"act": act, "params": params, "legacy_co_acts": []},
        "action_realization": {
            "utterance": utterance or "（静默）",
            "physical_action": template["physical_action"],
            "timing": "设备在识别到当前顾客状态后触发。",
            "rationale": "real eval stage-conditioned candidate",
        },
        "terminal_realization": {
            "surface_text": utterance,
            "screen": {"action": template["screen_action"], "cta": None},
            "voice_style": template["voice_style"],
            "light": template["light"],
            "cabinet_motion": None,
            "duration_ms": 3000 if act == "Greet" else 4000,
        },
    }


def chosen_candidate(blocks: list[dict[str, Any]], act: str) -> dict[str, Any]:
    for block in blocks:
        if block["dialogue_act"]["act"] == act:
            return block
    raise ValueError(f"candidate block does not contain best act: {act}")


def best_act(record: dict[str, Any]) -> str:
    best = str(record["best_action"]).strip().lower()
    if best not in BEST_ACTION_TO_ACT:
        raise ValueError(f"unsupported best_action: {record['best_action']}")
    return BEST_ACTION_TO_ACT[best]


def intent_label(record: dict[str, Any]) -> str:
    return BEST_ACTION_TO_INTENT[str(record["best_action"]).strip().lower()]


def label_source(record: dict[str, Any]) -> str:
    return str(record.get("label_source") or "human_json_annotation")


def session_sort_key(record: dict[str, Any]) -> int:
    return int(str(record["session_id"]).split("_", 1)[1])


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def clean_prompt_text(text: str) -> str:
    """Remove inline image placeholders; evaluator supplies images separately."""
    return text.replace("<image>", "").replace(config.IMAGE_PLACEHOLDER, "").strip()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def render_readme(manifest: dict[str, Any]) -> str:
    skipped = manifest["skipped_missing_video_count"]
    return "\n".join(
        [
            "# PIWM Real Eval Inputs",
            "",
            "Generated ms-swift rows for the real-video PIWM eval set.",
            "",
            f"- source: `{manifest['source_real_dir']}`",
            f"- human_annotation_records: {manifest['human_annotation_records']}",
            f"- index_derived_weak_label_records: {manifest['index_derived_weak_label_records']}",
            f"- runnable_records_with_video: {manifest['runnable_records_with_video']}",
            f"- label_source_counts_runnable: `{manifest['label_source_counts_runnable']}`",
            f"- skipped_missing_video_count: {skipped}",
            f"- frame_timestamps_sec: `{manifest['frame_timestamps_sec']}`",
            f"- all_scored_jsonl: `{manifest['jsonl']['all_scored']}`",
            "",
            "Primary metrics: Stage-1 `stage_accuracy` and Stage-2 `action_accuracy` / `action_macro_f1`.",
            "Rows marked `index_group_weak_label` use group-level labels from `index.json` because per-session annotation JSON is missing.",
            "The `intent_label` field is a deterministic heuristic derived from `best_action`, so treat intent metrics as secondary.",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
