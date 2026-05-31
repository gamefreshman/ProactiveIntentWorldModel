# PIWM Official Dataset Aliases

更新时间：2026-05-19

Kling API 已耗尽，本轮不会再新增视频。因此当前已落盘视频规模固定；v2.2 只做 schema、policy 和导出层迁移，不重生成 Kling 视频。

这里的目录是**正式名字入口**，不是重新复制视频数据。v1 目录保留为冻结兼容入口；v2.2 使用独立目录，避免训练脚本和结果文件被无提示替换。

对外说明、论文、汇报、示例数据展示和新脚本默认只引用 `data/official/` 下的 canonical path。`data/piwm_dataset_*` 这类目录只是 backing/source path，只能在 manifest lineage、复现实验路径或维护脚本中出现。

当前 official 数据已有 DialogueAct v2.1/v2.2 human-salesperson schema，同时保留旧 `A1-A8 / T-state` alias。`PIWM-Train-Synth-v1` 明确保留真人导购逻辑；`best_action_realization` 是主监督，`realization / terminal_realization` 是后续 target terminal 数据集的草案字段。顶层 `co_acts` 已从 official 主表输出中移出；旧输入仍可读，兼容输出使用 `legacy_co_acts`，新字段使用 `act_params.supporting_acts`。2026-05-15 已新增独立 v2.2 导出：`PIWM-Train-Synth-v2` 和 `PIWM-PolicySlice-v2`。当前 operational 5-act 主口径为 `Greet / Elicit / Inform / Recommend / Hold`；`Recommend` 保留 `pressure=soft/firm` 参数；`Reassure` 只保留为 source/compatibility 分析边界，不进入当前主 macro-F1。2026-05-16 已导入轻量 `piwm` target 域数据为 `PIWM-Target-Frontcam-v1`，并新增 `PIWM-Target-PromptReady-v1` 作为 318 条 target 上游生成索引。2026-05-19 已新增 revised two-stage 入口：Stage-1 使用 leakage-free `user_intent + next_state_prediction`，Stage-2 使用 target 5-act no-leak action selection；balanced target 5-act test 为 30 条、每个 operational act 6 条，已由项目负责人 QA 复核通过。

## Canonical Names

| 正式名 | 本目录入口 | Backing/source path（维护用） | 用途 | 口径 |
|---|---|---|---|---|
| `PIWM-Train-Synth-v1` | `piwm_train_synth_v1` | `../piwm_dataset_priority1000_unreviewed_compact_v2` | frozen 主 SFT 训练 | synthetic train, pending visual QA, human-salesperson logic, legacy-compatible action fields |
| `PIWM-Train-Synth-v2` | `piwm_train_synth_v2` | `piwm_train_synth_v1` | schema v2.2 主训练导出 | 543 parent / 2001 transition / 543 policy rows；5-act operational policy；`Recommend(pressure=soft/firm)`；`Reassure=0` in main training/eval/inference/runtime export；不覆盖 v1 |
| `PIWM-PolicySlice-v2` | `piwm_policy_slice_v2` | `scripts.scenario_sampler --candidate-rule-only` | explicit candidate-rule policy manifest | 864 rule-supported policy scenarios；5-act operational policy；不是视频数据，不是 QA-reviewed |
| `PIWM-Target-Frontcam-v1` | `piwm_target_v1` | `/Users/mutsumi/Desktop/WorkSpace/piwm` | target 域智能售货柜前置摄像头数据 | 118 records / 354 frames；主实验使用 101 条 clean 5-act records：71 train / 30 balanced test，test 已按新名单 QA-reviewed pass |
| `PIWM-Stage1-UserIntent-v1` | `ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | `piwm_train_synth_v2` | revised Stage-1 训练入口 | 2544 examples：user_intent=543 / next_state_prediction=2001；user_intent prompt 不含动作、reward 或候选 |
| `PIWM-Stage2-Target-5Act-v1` | `ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | `piwm_target_v1` clean 5-act rows | revised Stage-2 target 训练入口 | 71 action_selection_5act examples；排除 best=`Reassure`，并过滤候选中的 `Reassure`；prompt 不含 gold reward / risk / benefit / predicted next-state |
| `PIWM-Stage2-Target-5Act-GreetAug-v2` | `ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl` | `piwm_target_v1` clean 5-act rows + `piwm_train_synth_v2` attention rows | Stage-2 prelaunch Greet patch | 86 action_selection_5act examples；71 canonical target rows + 15 synthetic general `Greet` rows；stage-conditioned candidates；augmentation rows are not QA-reviewed target data |
| `PIWM-Stage1PlusStage2-Target5Act-GreetAugTargetX8-v1` | `ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl` | Stage-1 + `GreetAug-v2` | A4 weighted adaptation candidate | 3232 examples；target action rows repeated 8x for weighting，不代表新增视频 |
| `PIWM-Target-PromptReady-v1` | `piwm_target_promptready_v1` | `/Users/mutsumi/Desktop/WorkSpace/piwm/data/{seed,manifest,labeled,prompts}` | target 域上游生成索引 | 318 prompt-ready records；118 video-backed，200 video-pending；不是 ms-swift SFT 文件 |
| `PIWM-Eval-QA-v1` | `piwm_eval_qa_v1` | `../piwm_dataset_priority40_qareviewed_sample_compact_v2_exact` | 主表与 e2e 评估 | QA-reviewed eval subset, compact visual-state/action-realization schema |
| `PIWM-WorldModel-v1` | `piwm_world_model_v1` | `../piwm_dataset_pilot30_with_continuations_compact_v2` | continuation / Future Verification | QA-reviewed pilot evidence, shared three-axis current/future visual schema |
| `PIWM-FutureVerification-v1` | `piwm_world_model_v1/future_verification.jsonl` | same | action-conditioned future verification | derived from QA-reviewed continuations |
| `PIWM-RealShoot-v1` | `piwm_realshoot_v1` | `docs/current/piwm_real_shooting_scripts_S01_S12.md` | real-shooting manifest template | template/sample only, not filmed, not QA-reviewed |

## Schema v2.1 Re-export

2026-05-13 已运行：

```bash
python3 -m scripts.refresh_official_v2_exports --summary-out data/official/V2_REEXPORT_SUMMARY.json
python3 -m scripts.build_realshoot_manifest --output-dir data/official/piwm_realshoot_v1
```

重导结果：

- `PIWM-Train-Synth-v1`: 543 parent, 2011 transition rows, 543 policy rows.
- `PIWM-Eval-QA-v1`: 36 parent, 126 transition rows, 36 policy rows.
- `PIWM-WorldModel-v1`: 24 parent, 66 transition rows, 24 policy rows, 44 continuation rows.
- `PIWM-RealShoot-v1`: 24 manifest sample rows, covering S01-S12 A/B.

主数据 JSONL 现在包含 `schema_version=dialogue_act_human_salesperson_v2.1`、`actor_profile=human_salesperson_logic`、`dialogue_act / act_params.supporting_acts / best_action_realization / realization`。旧 `co_acts` 仍可被 schema 读入，但 official 主表输出不再使用顶层 `co_acts`；需要回溯兼容时使用 `legacy_co_acts`。Transition rows 包含 `candidate_dialogue_act / candidate_terminal_realization`。

## Schema v2.2 Export Status

v2.2 已完成 schema/runtime 增量、写回预演和独立导出。当前审计入口：

- `docs/v2_validation/compatibility_report.md`
- `docs/v2_validation/action_distribution.md`
- `docs/v2_validation/v2_2_reexport_dry_run.md`
- `docs/v2_validation/v2_2_reexport_diff_preview.md`
- `docs/v2_validation/v2_2_test_coverage.md`

关键结论：

- basic schema compatibility：`green=462`、`yellow=0`、`red=81`。这里的 `yellow=0` 不是 policy 无漂移，只是基础检测器没有非阻断 mismatch。
- extended v2 re-derivation audit：`green=109`、`yellow=353`、`red=81`。
- official 543 已按 operational 5-act v2 reward 重新写出 best action：`Elicit=252`、`Recommend=125`、`Inform=105`、`Hold=61`、`Greet=0`、`Reassure=0`。`Recommend` 候选保留 `pressure=soft/firm` 参数，其中成为 best 的 125 条均为 `pressure=soft`。
- red 样本集中在 `browser_low_intent`：81 / 94 条，属于 legacy Kling prompt 未显式区分低意图视觉表现的历史包袱。
- `next_state_by_action` 仍保留 legacy A-label key；v2.2 已新增 `next_state_by_action_v2` 作为 v2 action-keyed alias。
- `PIWM-Train-Synth-v2` 已写出到 `data/official/piwm_train_synth_v2/`，`PIWM-PolicySlice-v2` 已写出到 `data/official/piwm_policy_slice_v2/`。
- `PIWM-Target-Frontcam-v1` 已写出到 `data/official/piwm_target_v1/`。它来自 `guochenmeinian/piwm` 的 118 条设备前置摄像头样本，使用 `target_frontcam` 和 `actor_profile=target_terminal_logic`。2026-05-19 5-act 反转后，主实验从 118 条中排除 17 条 best=`Reassure`，并过滤候选中的 `Reassure`，得到 101 条 clean 5-act records：71 条 Stage-2 target train，30 条 balanced 5-act target eval。test 分布为 `Greet=6 / Elicit=6 / Inform=6 / Recommend=6 / Hold=6 / Reassure=0`。新 test 已按新名单 QA-reviewed pass；旧错误 5-act eval 已归档到 `data/official/domain_specialization_eval_v1/_legacy_wrong_5act/`。
- `PIWM-Target-PromptReady-v1` 已写出到 `data/official/piwm_target_promptready_v1/`。它索引轻量 `piwm` 的 318 条 `seed / manifest / labeled / prompts`，其中新增 200 条是 `video_pending`，不能当作已成片多模态训练样本。

v2.2 不覆盖 `PIWM-Train-Synth-v1`。v1 是冻结兼容入口；v2.2 新实验应显式使用 v2 路径。

## ms-swift Entrypoints

| 用途 | JSONL |
|---|---|
| frozen 主 SFT 训练 | `ms_swift/piwm_train_synth_v1.jsonl` |
| schema v2.2 主 SFT 训练 | `ms_swift/piwm_train_synth_v2.jsonl` |
| 旧 target 域专项 SFT | `ms_swift/piwm_train_target_specialization_v1.jsonl` |
| Stage-1 user-intent/world-model SFT | `ms_swift/piwm_train_stage1_user_intent_v1.jsonl` |
| Stage-2 target 5-act no-leak SFT | `ms_swift/piwm_train_stage2_target_5act_v1.jsonl` |
| revised two-stage joint baseline | `ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl` |
| target 域 prompt-ready 上游索引 | `piwm_target_promptready_v1/promptready_index.jsonl` |
| mixed-view joint SFT 对照 | `ms_swift/piwm_train_general_plus_target_v1.jsonl` |
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

这版用于训练模型输出更细的 `visual_state`、具体真人导购动作和话术，以及
action-conditioned future verification。旧 `piwm_train_synth_v1.jsonl`
仍保留为只含主训练 perception / deliberation 的轻量入口。

`piwm_train_synth_v2.jsonl` 来自 `PIWM-Train-Synth-v2`，当前是 2544 examples：perception 543 / deliberation 2001。它的价值是 schema v2.2 字段完整，而不是新增视频规模。

`piwm_train_target_specialization_v1.jsonl` 是旧 target 全量入口，共 708 examples：perception 118 / deliberation 472 / action_selection 118。它保留用于回溯，不再作为 EMNLP 主实验入口。

当前 EMNLP 主实验使用 revised two-stage 入口：

- `piwm_train_stage1_user_intent_v1.jsonl`：2544 examples，user_intent=543 / next_state_prediction=2001。
- `piwm_train_stage2_target_5act_v1.jsonl`：71 examples，全部是 no-leak `action_selection_5act`，prompt / target / meta 均无 `Reassure`。
- `piwm_train_stage2_target_5act_greet_aug_v2.jsonl`：86 examples，71 canonical target rows + 15 synthetic general attention-stage `Greet` rows；best 分布为 `Greet=26 / Inform=41 / Elicit=14 / Recommend=5 / Hold=0`，用于 Stage-2 prelaunch patch。
- `piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl`：3232 examples，用于 A4 weighted adaptation；target action rows 重复 8 次，不代表新增 unique video。
- `piwm_train_stage1_plus_stage2_target_5act_v1.jsonl`：2615 examples，作为 joint baseline。
- `domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl`：90 eval rows，来自 30 条 balanced target 5-act records；已按新名单 QA-reviewed pass。

Stage-2 action-selection candidates follow the stage-conditioned policy: `attention -> Greet/Elicit/Inform/Hold`，`interest -> Elicit/Inform/Recommend/Hold`，`desire -> Inform/Recommend/Hold`，`action -> Greet/Recommend/Hold`。Stage-2 eval also supports an inference-time Hold prior calibration (`--hold-prior-lambda`, default planned value 1.0) because Path C quick probe over-predicted `Hold` before Stage-2 training.

`piwm_target_promptready_v1/promptready_index.jsonl` 来自轻量 `piwm` 扩展后的 318 条上游记录。其中 200 条没有视频，必须先生成 Kling 视频并抽帧，才能进入 `PIWM-Target-Frontcam-v1` 或 ms-swift 多模态训练。该队列可继续用于补充后续 target extension 的 `Greet` 覆盖，但不能用来声称 200 条 video-pending 已经是 filmed multimodal data。

`piwm_train_general_plus_target_v1.jsonl` 是早期 general v2 + target frontcam 的 mixed-view joint SFT 对照入口，共 3262 examples：general=2554，target=708。它保留用于回溯，不代表当前 refreshed operational 5-act 导出。当前 revised two-stage specialization 使用 `piwm_train_stage1_user_intent_v1.jsonl`、`piwm_train_stage2_target_5act_v1.jsonl` 和 `piwm_train_stage1_plus_stage2_target_5act_v1.jsonl`。

## Reporting Rule

论文和汇报中优先使用正式名：

- 写 `PIWM-Train-Synth-v1`，默认引用 `data/official/piwm_train_synth_v1/` 或 `data/official/ms_swift/piwm_train_synth_v1.jsonl`，不要用 `priority1000_unreviewed*` 当公开数据名。
- 写 v2.2 数据格式时，引用 `PIWM-Train-Synth-v2` 和 `data/official/piwm_train_synth_v2/`。
- 写平衡动作空间或 policy 生成入口时，引用 `PIWM-PolicySlice-v2`；不要把它写成 filmed dataset。
- 写 target 域设备前置摄像头数据时，引用 `PIWM-Target-Frontcam-v1`；当前主实验使用 71 条 clean 5-act train + 30 条 balanced 5-act test；test 已按新名单 QA-reviewed pass，旧 split 的 QA pass 结论仍只作为历史记录。
- 写 target 扩展生成队列时，引用 `PIWM-Target-PromptReady-v1`；不要把其中 200 条 video-pending 样本写成 filmed multimodal dataset。
- 写 `PIWM-Eval-QA-v1`，不要写 `priority40_qareviewed_sample`。
- 写 `PIWM-WorldModel-v1` / `PIWM-FutureVerification-v1`，不要写 `pilot30_with_continuations`。
- `PIWM-RealShoot-v1` 目前只能写成 planned real-shooting protocol and manifest schema，不能写成已采集真实数据。

旧名只在复现实验路径、脚本路径或附录 manifest 中出现。

旧 manifest 副本已移到 `data/official/archive/`。当前有效 manifest 只有 `DATASET_MANIFEST.json`。

## Red Lines

- `PIWM-Train-Synth-v1` 不是 QA-pass 数据。
- `PIWM-Train-Synth-v1` 不是 target terminal 数据集；不要把其中的真人导购动作写成终端硬件已采集行为。
- 不能写“1000 条视频已完成”；当前 v2 operational 训练入口是 543 loaded parent / 2544 SFT examples。
- `smoke`、`early pilot`、`DPO adapter`、`missing retry queue` 不属于正式数据集。
- `FutureVerification` 的 `visible_reaction` 使用 `engagement_pattern_change / gaze_and_attention_change / body_and_hands_change` 三轴，不再使用旧的四字段 reaction schema。
- `PIWM-RealShoot-v1` 在视频、音频、UI 录屏、转写和 QA 字段填齐前，不得进入 QA-reviewed eval。
- revised 30 条 balanced 5-act target test 已按新名单 QA-reviewed pass；不要把这个结论扩展到 71 条 target train 或全量 118 条 corpus。
- `PIWM-Target-Frontcam-v1` 的 88 条 train records 仍是 `synthetic_unreviewed`，不要写成 human QA-reviewed。
- `PIWM-Target-PromptReady-v1` 的 200 条扩展样本没有 Kling 视频和抽帧，不得进入多模态 SFT 统计。
