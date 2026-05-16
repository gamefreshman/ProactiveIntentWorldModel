"""Generate deterministic prompt-ready PIWM target-domain expansion records.

This fills the lightweight ``guochenmeinian/piwm`` pipeline up to 300+ labeled
records without pretending that the new records already have Kling videos. It
writes seed, manifest, labeled, and prompt files only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_PIWM_ROOT = Path("/Users/mutsumi/Desktop/WorkSpace/piwm")
DEFAULT_START_ID = 818
DEFAULT_COUNT = 200


TARGET_ADDITIONS: list[str] = (
    ["elicit_need_focus_open"] * 33
    + ["inform_comparison_brief", "inform_demo_brief", "inform_attributes_brief", "inform_price_brief"] * 1
    + ["inform_comparison_brief", "inform_price_brief"]
    + ["greet_open", "greet_close"] * 18
    + ["reassure_time_wait", "reassure_decision"] * 18
    + ["recommend_soft", "recommend_firm"] * 21
    + ["hold_silent"] * 24
    + ["hold_ambient"] * 23
)

PERSONAS = [
    {
        "type": "browser_low_intent",
        "persona": "周末路过商场、只是随便看看的普通消费者。",
        "visual": "一名 25–35 岁亚洲女性，穿着简洁休闲服，背小包，神情自然克制。",
    },
    {
        "type": "price_sensitive_cautious",
        "persona": "对价格和优惠较敏感、购买前会反复确认性价比的谨慎消费者。",
        "visual": "一名 30–45 岁亚洲男性，穿着干净日常衬衫或外套，手持手机，表情认真。",
    },
    {
        "type": "first_time_high_consideration",
        "persona": "第一次使用这类智能售货设备、需要理解流程和商品差异的消费者。",
        "visual": "一名 20–30 岁亚洲学生或年轻职员，穿浅色上衣，动作谨慎，视线会短暂停顿。",
    },
    {
        "type": "experienced_brand_loyal",
        "persona": "熟悉该类设备和品牌、已有偏好但仍会做最后确认的消费者。",
        "visual": "一名 28–40 岁亚洲消费者，穿着利落，持手机靠近设备，动作稳定。",
    },
    {
        "type": "gift_buyer_uncertain",
        "persona": "准备给别人买东西但不确定对方偏好、需要比较适合场景的礼物购买者。",
        "visual": "一名 25–40 岁亚洲女性，穿柔和色外套，手持手机或小包，表情思考。",
    },
    {
        "type": "price_insensitive_decisive",
        "persona": "预算压力较低、目标明确、希望快速完成选择的消费者。",
        "visual": "一名 30–45 岁亚洲男性，穿简洁商务休闲装，站姿稳定，动作干脆。",
    },
]

RESPONSE_STAGE = {
    "greet_open": "attention",
    "greet_close": "action",
    "elicit_need_focus_open": "interest",
    "inform_comparison_brief": "interest",
    "inform_demo_brief": "interest",
    "inform_attributes_brief": "interest",
    "inform_price_brief": "desire",
    "recommend_soft": "desire",
    "recommend_firm": "desire",
    "reassure_time_wait": "desire",
    "reassure_decision": "desire",
    "hold_silent": "interest",
    "hold_ambient": "interest",
}

AIDA_ALLOWED_RESPONSES = {
    "attention": ["hold_silent", "hold_ambient", "greet_open", "elicit_need_focus_open", "inform_demo_brief"],
    "interest": [
        "hold_silent",
        "hold_ambient",
        "elicit_need_focus_open",
        "inform_attributes_brief",
        "inform_price_brief",
        "inform_comparison_brief",
        "inform_demo_brief",
        "recommend_soft",
    ],
    "desire": [
        "hold_silent",
        "hold_ambient",
        "inform_price_brief",
        "inform_comparison_brief",
        "reassure_decision",
        "reassure_time_wait",
        "recommend_soft",
        "recommend_firm",
    ],
    "action": ["hold_silent", "hold_ambient", "reassure_time_wait", "reassure_decision", "greet_close"],
}

ACTION_PROFILES = {
    "greet_open": {"act": "Greet:open", "benefit": "medium", "risk": "low"},
    "greet_close": {"act": "Greet:close", "benefit": "high", "risk": "low"},
    "elicit_need_focus_open": {"act": "Elicit:need_focus", "benefit": "high", "risk": "medium"},
    "inform_comparison_brief": {"act": "Inform:comparison", "benefit": "high", "risk": "low"},
    "inform_demo_brief": {"act": "Inform:demo", "benefit": "high", "risk": "medium"},
    "inform_attributes_brief": {"act": "Inform:attributes", "benefit": "medium", "risk": "low"},
    "inform_price_brief": {"act": "Inform:price", "benefit": "medium", "risk": "low"},
    "recommend_soft": {"act": "Recommend:soft", "benefit": "high", "risk": "medium"},
    "recommend_firm": {"act": "Recommend:firm", "benefit": "high", "risk": "medium"},
    "reassure_time_wait": {"act": "Reassure:time", "benefit": "high", "risk": "low"},
    "reassure_decision": {"act": "Reassure:decision", "benefit": "high", "risk": "low"},
    "hold_silent": {"act": "Hold:silent", "benefit": "medium", "risk": "low"},
    "hold_ambient": {"act": "Hold:ambient", "benefit": "medium", "risk": "low"},
}


def generate_expansion(
    piwm_root: Path,
    *,
    start_id: int,
    count: int,
    overwrite: bool = False,
) -> dict[str, Any]:
    if count > len(TARGET_ADDITIONS):
        raise ValueError(f"count={count} exceeds available deterministic additions {len(TARGET_ADDITIONS)}")
    _load_lightweight_helpers(piwm_root)
    from action_space import enrich_labeled_record
    from gen_prompt import render_prompt

    dirs = {name: piwm_root / "data" / name for name in ["seed", "manifest", "labeled", "prompts"]}
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    written = []
    skipped = []
    for offset, best_action in enumerate(TARGET_ADDITIONS[:count]):
        session_id = f"piwm_{start_id + offset}"
        paths = {
            "seed": dirs["seed"] / f"{session_id}.txt",
            "manifest": dirs["manifest"] / f"{session_id}.json",
            "labeled": dirs["labeled"] / f"{session_id}.json",
            "prompt": dirs["prompts"] / f"{session_id}.md",
        }
        if not overwrite and any(path.exists() for path in paths.values()):
            skipped.append(session_id)
            continue
        persona = PERSONAS[offset % len(PERSONAS)]
        stage = _stage_for(best_action, offset)
        manifest = _build_manifest(session_id, persona, stage, best_action, offset)
        labeled = enrich_labeled_record(_build_labeled(manifest, best_action, offset))
        seed = _seed_text(stage, persona, best_action, manifest)
        prompt = render_prompt(manifest)

        paths["seed"].write_text(seed + "\n", encoding="utf-8")
        paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["labeled"].write_text(json.dumps(labeled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["prompt"].write_text(prompt, encoding="utf-8")
        written.append({"session_id": session_id, "best_action": best_action, "aida_stage": stage, "persona_type": persona["type"]})

    summary = {
        "artifact": "piwm_target_promptready_expansion",
        "piwm_root": piwm_root.as_posix(),
        "start_id": start_id,
        "requested_count": count,
        "written_count": len(written),
        "skipped_count": len(skipped),
        "status": "prompt_ready_video_pending",
        "video_generation": "not_run_missing_kling_credentials",
        "records": written,
        "skipped": skipped,
        "counts_after_generation": _counts_after_generation(piwm_root),
    }
    summary_dir = piwm_root / "data" / "expansion"
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / f"promptready_{start_id}_{start_id + count - 1}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def _load_lightweight_helpers(piwm_root: Path) -> None:
    script_dir = piwm_root / "script"
    if not script_dir.exists():
        raise FileNotFoundError(f"missing lightweight script directory: {script_dir}")
    if script_dir.as_posix() not in sys.path:
        sys.path.insert(0, script_dir.as_posix())


def _stage_for(best_action: str, offset: int) -> str:
    if best_action == "elicit_need_focus_open" and offset % 3 == 0:
        return "attention"
    if best_action in {"hold_silent", "hold_ambient"} and offset % 2 == 0:
        return "desire"
    return RESPONSE_STAGE[best_action]


def _build_manifest(session_id: str, persona: dict[str, str], stage: str, best_action: str, offset: int) -> dict[str, Any]:
    behavior = _behavior(stage, best_action, offset)
    return {
        "session_id": session_id,
        "persona": persona["persona"],
        "persona_visual": persona["visual"],
        "aida_stage": stage,
        "bdi": _bdi(stage, best_action),
        "observable_behavior": behavior["observable_behavior"],
        "facial_expression": behavior["facial_expression"],
        "body_posture": behavior["body_posture"],
        "timeline": behavior["timeline"],
        "generation_status": "prompt_ready_video_pending",
        "target_act": ACTION_PROFILES[best_action]["act"],
    }


def _build_labeled(manifest: dict[str, Any], best_action: str, offset: int) -> dict[str, Any]:
    stage = manifest["aida_stage"]
    candidates = _candidate_set(stage, best_action, offset)
    outcomes = {response_id: _outcome_for(response_id, best_action, stage) for response_id in candidates}
    return {
        **manifest,
        "candidate_actions": candidates,
        "outcomes": outcomes,
        "best_action": best_action,
        "response_id": best_action,
        "generation_status": "prompt_ready_video_pending",
        "expansion_batch": "2026-05-16_promptready_200",
    }


def _candidate_set(stage: str, best_action: str, offset: int) -> list[str]:
    candidates = ["hold_silent"]
    stage_pool = [item for item in AIDA_ALLOWED_RESPONSES[stage] if item != "hold_silent"]
    if best_action not in candidates:
        candidates.append(best_action)
    for candidate in stage_pool:
        if candidate not in candidates:
            candidates.append(candidate)
        if len(candidates) == 4:
            break
    if len(candidates) < 4:
        for candidate in AIDA_ALLOWED_RESPONSES["interest"]:
            if candidate not in candidates:
                candidates.append(candidate)
            if len(candidates) == 4:
                break
    return candidates[:4]


def _outcome_for(response_id: str, best_action: str, stage: str) -> dict[str, Any]:
    is_best = response_id == best_action
    profile = ACTION_PROFILES[response_id]
    if is_best:
        delta_stage, delta_mental = _best_delta(response_id)
        risk = profile["risk"]
        benefit = profile["benefit"]
        next_stage = _next_stage(stage, positive=True)
        rationale = f"{profile['act']} matches the visible {stage} state and improves the shopper's next step without breaking target-frontcam timing."
    else:
        delta_stage, delta_mental = _nonbest_delta(response_id, best_action)
        risk = "medium" if response_id.startswith("recommend") and not best_action.startswith("recommend") else profile["risk"]
        benefit = "low" if response_id == "hold_silent" else "medium"
        next_stage = stage if delta_stage <= 0.12 else _next_stage(stage, positive=True)
        rationale = f"{profile['act']} is plausible but less aligned than {ACTION_PROFILES[best_action]['act']} for this sampled state."
    return {
        "next_aida_stage": next_stage,
        "next_bdi": _next_bdi(response_id, next_stage, is_best),
        "risk": risk,
        "benefit": benefit,
        "delta_stage": round(delta_stage, 3),
        "delta_mental": round(delta_mental, 3),
        "rationale": rationale,
    }


def _best_delta(response_id: str) -> tuple[float, float]:
    if response_id.startswith("hold_"):
        return 0.08, 0.22
    if response_id == "recommend_firm":
        return 0.42, 0.46
    if response_id == "greet_close":
        return 0.32, 0.30
    if response_id.startswith("recommend"):
        return 0.36, 0.42
    if response_id.startswith("reassure"):
        return 0.22, 0.36
    if response_id.startswith("greet"):
        return 0.24, 0.24
    if response_id.startswith("elicit"):
        return 0.28, 0.36
    return 0.26, 0.34


def _nonbest_delta(response_id: str, best_action: str) -> tuple[float, float]:
    if response_id == "hold_silent":
        return 0.0, 0.03 if not best_action.startswith("hold") else 0.18
    if response_id.startswith("recommend") and not best_action.startswith("recommend"):
        return 0.05, -0.08
    if best_action.startswith("hold"):
        return -0.02, -0.06
    return 0.08, 0.10


def _next_stage(stage: str, *, positive: bool) -> str:
    if not positive:
        return stage
    order = ["attention", "interest", "desire", "action"]
    idx = order.index(stage) if stage in order else 1
    return order[min(idx + 1, len(order) - 1)]


def _bdi(stage: str, best_action: str) -> dict[str, str]:
    act = ACTION_PROFILES[best_action]["act"]
    if stage == "attention":
        return {
            "belief": "设备前方可能有值得了解的商品或服务，但当前仍处于刚接近、尚未明确需求的阶段。",
            "desire": "希望先轻松确认这里是否有自己感兴趣的选项。",
            "intention": "短暂停留并观察设备反馈，再决定是否继续浏览。",
        }
    if stage == "interest":
        return {
            "belief": "当前商品信息值得继续看，但还需要筛选关注点或比较基础信息。",
            "desire": "希望更快理解哪些选项与自己的预算、功能或场景相关。",
            "intention": f"继续观察并等待与 {act} 相匹配的低压力帮助。",
        }
    if stage == "desire":
        return {
            "belief": "已有若干候选商品接近需求，但仍需要降低时间、选择或后悔风险。",
            "desire": "希望得到清晰但不过度施压的确认，从而缩小选择范围。",
            "intention": f"围绕当前偏好做最后权衡，并对 {act} 类型响应保持开放。",
        }
    return {
        "belief": "选择或操作已经接近完成，当前主要需要顺畅收尾或确认流程。",
        "desire": "希望快速、无压力地完成当前交互。",
        "intention": "完成确认、等待出货或自然离开设备前方。",
    }


def _next_bdi(response_id: str, next_stage: str, is_best: bool) -> dict[str, str]:
    if is_best:
        return {
            "belief": "设备响应与当前状态匹配，信息或节奏上的不确定性下降。",
            "desire": "愿意继续沿当前路径推进，因为选择压力和理解成本降低。",
            "intention": f"进入或维持 {next_stage} 阶段，并继续与设备进行低压力互动。",
        }
    return {
        "belief": "设备响应有一定帮助，但没有完全击中当前最需要解决的问题。",
        "desire": "仍希望继续确认更相关的信息。",
        "intention": f"暂时停留在 {next_stage} 附近，继续观察或比较。",
    }


def _behavior(stage: str, best_action: str, offset: int) -> dict[str, Any]:
    focus = {
        "greet_open": "刚进入设备前方，步伐放慢，视线开始转向屏幕区域",
        "greet_close": "已经完成选择或操作，视线从手机和设备之间自然切换，表情放松",
        "elicit_need_focus_open": "停在设备前，视线在几个区域之间切换，像是在寻找优先关注点",
        "inform_comparison_brief": "反复看向两个相邻区域，头部轻微左右切换，正在比较差异",
        "inform_demo_brief": "靠近设备观察，眉头轻微收紧，像是在理解功能如何使用",
        "inform_attributes_brief": "稳定看向屏幕主区域，短暂停顿后再次确认信息",
        "inform_price_brief": "视线多次下移到同一位置，像是在确认价格或优惠",
        "recommend_soft": "已经停留较久，视线集中在一个候选区域，仍保留轻微犹豫",
        "recommend_firm": "身体朝向稳定，手部准备操作，表现出只差最后确认的状态",
        "reassure_time_wait": "看着手机或屏幕等待，动作克制，明显不希望被催促",
        "reassure_decision": "在候选间短暂停顿，表情谨慎，像是在担心选错",
        "hold_silent": "正在顺畅自主浏览，没有明显求助信号，任何主动打断都可能破坏节奏",
        "hold_ambient": "注意力稳定但不希望继续被打扰，身体略微后收，适合设备退到背景",
    }[best_action]
    return {
        "observable_behavior": f"顾客{focus}。整体动作缓慢、连续、真实，没有夸张表演。",
        "facial_expression": "表情自然克制，带有轻微思考或确认感，没有明显焦躁、惊讶或防御。",
        "body_posture": "身体正面对向设备，站姿稳定，双手自然放在手机、包带或设备前方可见区域。",
        "timeline": {
            "t_0_2": "顾客进入或已经停留在设备前方，视线先稳定看向前方区域。",
            "t_2_5": f"顾客继续{focus}，头部和视线变化幅度较小。",
            "t_5_8": "顾客保持自然停顿，短暂下移视线后再回到前方，表现出比较或确认。",
            "t_8_10": "顾客仍停留在原位，动作节奏平稳，没有突然离开、付款界面展示或夸张动作。",
        },
    }


def _seed_text(stage: str, persona: dict[str, str], best_action: str, manifest: dict[str, Any]) -> str:
    return (
        f"{stage} 阶段，{persona['persona']}，"
        f"{manifest['observable_behavior']}，target_act={ACTION_PROFILES[best_action]['act']}，"
        "生成 prompt-ready 扩展样本，video_pending"
    )


def _counts_after_generation(piwm_root: Path) -> dict[str, int]:
    data = piwm_root / "data"
    return {
        name: len(list((data / name).glob("piwm_*.*")))
        for name in ["seed", "manifest", "labeled", "prompts", "video"]
        if (data / name).exists()
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--piwm-root", type=Path, default=DEFAULT_PIWM_ROOT)
    parser.add_argument("--start-id", type=int, default=DEFAULT_START_ID)
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_expansion(
        args.piwm_root,
        start_id=args.start_id,
        count=args.count,
        overwrite=args.overwrite,
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "records"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
