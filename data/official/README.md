# PIWM Official Dataset Aliases

更新时间：2026-05-11

Kling API 已耗尽，本轮不会再新增视频。因此当前已落盘数据固定为 PIWM v1 正式数据集。

这里的目录是**正式名字入口**，不是重新复制视频数据。旧目录保留，`data/official/` 用软链接指向当前正式 JSONL 目录，避免训练脚本和结果文件失效。

当前 official 数据已重导出为 DialogueAct v2 + TerminalRealization 兼容 schema，同时保留旧 `A1-A8 / T-state` alias。视觉状态描述会结合商品类别和可见线索，BDI belief 会结合 cue，终端响应会输出 `surface_text / screen / voice_style / light / cabinet_motion / duration_ms`。

## Canonical Names

| 正式名 | 本目录入口 | 来源目录 | 用途 | 口径 |
|---|---|---|---|---|
| `PIWM-Train-Synth-v1` | `piwm_train_synth_v1` | `../piwm_dataset_priority1000_unreviewed_compact_v2` | 主 SFT 训练 | synthetic train, pending visual QA, compact visual-state/action-realization schema |
| `PIWM-Eval-QA-v1` | `piwm_eval_qa_v1` | `../piwm_dataset_priority40_qareviewed_sample_compact_v2_exact` | 主表与 e2e 评估 | QA-reviewed eval subset, compact visual-state/action-realization schema |
| `PIWM-WorldModel-v1` | `piwm_world_model_v1` | `../piwm_dataset_pilot30_with_continuations_compact_v2` | continuation / Future Verification | QA-reviewed pilot evidence, shared three-axis current/future visual schema |
| `PIWM-FutureVerification-v1` | `piwm_world_model_v1/future_verification.jsonl` | same | action-conditioned future verification | derived from QA-reviewed continuations |
| `PIWM-RealShoot-v1` | `piwm_realshoot_v1` | `docs/current/piwm_real_shooting_scripts_S01_S12.md` | real-shooting manifest template | template/sample only, not filmed, not QA-reviewed |

## Schema v2 Re-export

2026-05-11 已运行：

```bash
python3 -m scripts.refresh_official_v2_exports --summary-out data/official/V2_REEXPORT_SUMMARY.json
python3 -m scripts.build_realshoot_manifest --output-dir data/official/piwm_realshoot_v1
```

重导结果：

- `PIWM-Train-Synth-v1`: 543 parent, 2011 transition rows, 543 policy rows.
- `PIWM-Eval-QA-v1`: 36 parent, 126 transition rows, 36 policy rows.
- `PIWM-WorldModel-v1`: 24 parent, 66 transition rows, 24 policy rows, 44 continuation rows.
- `PIWM-RealShoot-v1`: 24 manifest sample rows, covering S01-S12 A/B.

主数据 JSONL 现在包含 `dialogue_act / act_params / co_acts / realization`。Transition rows 包含 `candidate_dialogue_act / candidate_terminal_realization`。

## ms-swift Entrypoints

| 用途 | JSONL |
|---|---|
| 主 SFT 训练 | `ms_swift/piwm_train_synth_v1.jsonl` |
| 新版 full-v2 SFT 训练 | `ms_swift/piwm_train_full_v2.jsonl` |
| 主 QA eval | `ms_swift/piwm_eval_qa_all_v1.jsonl` |
| World Model / FV SFT | `ms_swift/piwm_world_model_sft_v1.jsonl` |
| Future Verification eval | `ms_swift/piwm_future_verification_eval_all_v1.jsonl` |

`piwm_train_full_v2.jsonl` 是下一次从 base 重新八卡训练的推荐入口。它在
`PIWM-Train-Synth-v1` 的 perception / deliberation 基础上加入
action-selection rows，并合并 `PIWM-WorldModel-v1` 的 continuation caption
与 Future Verification rows：

- 3339 SFT examples
- perception 567
- deliberation 2077
- action_selection 567
- continuation_caption 44
- future_verification 84

这版用于训练模型输出更细的 `visual_state`、具体导购动作和话术，以及
action-conditioned future verification。旧 `piwm_train_synth_v1.jsonl`
仍保留为只含主训练 perception / deliberation 的轻量入口。

## Reporting Rule

论文和汇报中优先使用正式名：

- 写 `PIWM-Train-Synth-v1`，不要写 `priority1000_unreviewed`。
- 写 `PIWM-Eval-QA-v1`，不要写 `priority40_qareviewed_sample`。
- 写 `PIWM-WorldModel-v1` / `PIWM-FutureVerification-v1`，不要写 `pilot30_with_continuations`。
- `PIWM-RealShoot-v1` 目前只能写成 planned real-shooting protocol and manifest schema，不能写成已采集真实数据。

旧名只在复现实验路径、脚本路径或附录 manifest 中出现。

旧 manifest 副本已移到 `data/official/archive/`。当前有效 manifest 只有 `DATASET_MANIFEST.json`。

## Red Lines

- `PIWM-Train-Synth-v1` 不是 QA-pass 数据。
- 不能写“1000 条视频已完成”；当前正式训练集是 543 loaded parent / 2554 SFT examples。
- `smoke`、`early pilot`、`DPO adapter`、`missing retry queue` 不属于正式数据集。
- `FutureVerification` 的 `visible_reaction` 使用 `engagement_pattern_change / gaze_and_attention_change / body_and_hands_change` 三轴，不再使用旧的四字段 reaction schema。
- `PIWM-RealShoot-v1` 在视频、音频、UI 录屏、转写和 QA 字段填齐前，不得进入 QA-reviewed eval。
