# PIWM Data Schema v2 Contract

更新时间：2026-05-11 CST

本文定义当前 PIWM 数据格式的成熟口径。目标是让 synthetic 数据、真实拍摄素材、World Model continuation、训练 JSONL 和论文数据叙述都指向同一套字段，而不是各自维护一套标签。

## 1. Canonical Layers

```text
Current observation
  -> visual_state
  -> AIDA + BDI + state_subtype
  -> candidate legacy actions + v2 dialogue acts
  -> terminal realization
  -> action-conditioned next state / visible reaction
  -> reward / preference / QA status
```

核心规则：

- `visual_state` 是画面事实，先于心理标签。
- `aida_stage / bdi / latent_state` 是当前顾客状态。
- `candidate_actions / best_action` 是旧兼容字段，仍用于历史数据和已有训练任务。
- `dialogue_act / act_params / co_acts` 是 v2 policy 语义层。
- `realization` 是终端响应：屏幕、语音、灯效、柜内动作、时长。
- `best_action_realization` 继续保留，用来兼容旧导购话术和训练样本。

## 2. MainSchemaRecord v2

主记录仍使用 `MainSchemaRecord`。新增字段：

| 字段 | 用途 |
|---|---|
| `dialogue_act` | 最优动作对应的 6-act policy label |
| `act_params` | act 参数，如 `{"content_type": "comparison", "depth": "brief"}` |
| `co_acts` | 非 Task 维度共现动作，如 `Reassure + Hold` |
| `realization` | `TerminalRealization`，终端实际执行包 |

兼容字段：

| 字段 | 状态 |
|---|---|
| `candidate_actions` | 保留，旧 `A1-A8` label |
| `best_action` | 保留，旧最优动作 label |
| `best_action_realization` | 保留，旧导购动作/话术字段 |
| `proactive_score` | 保留但 deprecated，不作为论文核心解释 |

## 3. TerminalRealization

```json
{
  "surface_text": "我把这两款的差别帮您列清楚...",
  "screen": {"action": "show_comparison_or_details", "target": "{candidate_items}", "cta": null},
  "voice_style": "neutral",
  "light": "soft_focus_on_comparison_cards",
  "cabinet_motion": null,
  "duration_ms": 4000,
  "dialogue_act": "Inform",
  "act_params": {"content_type": "comparison", "depth": "brief"},
  "co_acts": [],
  "legacy_action": "A2_offer_value_comparison"
}
```

终端响应不写内部 enum 给观众看。`screen.action` 是给 UI/终端团队的控制动作，`surface_text` 才是顾客听到或看到的自然语言。

## 4. ShootingClipRecord

真实拍摄素材使用 `ShootingClipRecord` 对齐现场、后期和训练入库。

最小字段：

```json
{
  "clip_id": "G001_S05_A",
  "group_id": "G001",
  "shooting_state": "S05_BROWSE_UNC",
  "version": "A",
  "product_category": "electronics_phone",
  "persona_type": "price_sensitive_cautious"
}
```

系统会按拍摄方案自动补：

- `state_name_zh`
- `response_type_zh`
- `legacy_action`
- `t_state`
- `dialogue_act`
- `act_params`
- `co_acts`
- `terminal_realization`
- `expected_reaction`
- `requires_hero_view`

素材路径和 QA 后续补入：

| 字段 | 内容 |
|---|---|
| `assets.fpv_video_path` | 训练主视角视频 |
| `assets.hero_video_path` | 核心状态第三人称宣发视角 |
| `assets.ui_recording_path` | 终端 UI 录屏 |
| `assets.audio_path` | 话筒/顾客音频 |
| `assets.transcript_path` | 转写文本 |
| `qa.overall_pass` | 是否进入 QA-reviewed 集 |

## 5. Export Policy

导出 JSONL 时必须同时保留新旧字段：

- state inference：输出 `dialogue_act / act_params / terminal_realization`。
- transition modeling：输入包含 `candidate_action` 和 `candidate_dialogue_act / candidate_terminal_realization`。
- policy preference：`chosen_json / rejected_json / candidate_block` 同时包含旧 action 和新 act。

这样旧 checkpoint 和旧评测可以继续跑，新论文和新真实数据可以使用 v2 语义。

## 6. Versioning and Maintenance

- v2 contract 源头见 `docs/contracts/action_space_realization_contract.md`。
- 附件副本见 `docs/source_materials/2026-05-action-space/`。
- 新增拍摄脚本必须先登记到单文件脚本 `docs/current/piwm_real_shooting_scripts_S01_S12.md`，并保证 `shooting_state + version + response_type_zh + dialogue_act + terminal_realization` 一致。
- 新增终端能力优先新增 realization 模板；只有 policy 语义确实无法表达时，才讨论新增 DialogueAct。
- 任何 official dataset 重导出必须在 `docs/current/dataset_inventory.md` 记录字段版本和导出命令。
- 当前重导脚本是 `python3 -m scripts.refresh_official_v2_exports --summary-out data/official/V2_REEXPORT_SUMMARY.json`；真实拍摄 manifest 样例脚本是 `python3 -m scripts.build_realshoot_manifest --output-dir data/official/piwm_realshoot_v1`。
