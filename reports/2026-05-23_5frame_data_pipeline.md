5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入 operational training/eval/inference/runtime。

# 5-Frame Data Pipeline Report

## Summary

本轮已新增 5 帧数据生成脚本，并在不覆盖现有 3 帧 frozen 数据的前提下生成了本地 5 帧版本。target-frontcam 相关数据已经完整生成；general Stage-1 相关数据在本地不完整，原因是本机缺少部分 general 源视频，另有 1 个本地视频在 5 秒位置无法读取。远端补齐 general 的抽帧进程一度启动，但进入磁盘 I/O 卡顿状态；为保护优先级更高的 A3_minimal GPU 训练，已暂停远端 5 帧补齐。

结论：5 帧 pipeline 已准备好，target 5 帧数据可用；完整 5 帧 Stage-1/general 数据还需要在 A3_minimal 训练与评估结束后，在服务器上单独重跑补齐。

## Sampling Rule

推荐采用固定时间点抽帧：`1s / 3s / 5s / 7s / 9s`。

理由：
- 现有视频主要是 10 秒左右短片，这 5 个点能覆盖顾客行为的开始、发展、峰值、稳定和收尾。
- 不取 `0s` 和最后一帧，避免黑场、转场或生成视频末尾不稳定画面。
- 比只用 3 帧更适合区分“短暂停留”和“真实推进”等动态线索。

## New Script

- 新增脚本：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/build_ms_swift_5frame_data.py`
- 默认输出目录：
  - `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift_5frame/`
  - `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/domain_specialization_eval_v2_5frame/`
- 行为：
  - 从源视频抽取 5 张 JPG。
  - 将 JSONL 中 `images` 从 3 条路径替换为 5 条路径。
  - 将 prompt 里的 `<image>` 数量和 “Below are 3 frames” 改为 5 帧口径。
  - 增加 `meta.frame_budget=5`、`meta.frame_sampling_plan`、`meta.frame_budget_source`。

## Local Output Inventory

| File | Rows | SHA256 | Notes |
|---|---:|---|---|
| `data/official/ms_swift_5frame/piwm_train_stage1_user_intent_train_v1.jsonl` | 373 | `14fabcfd76c8fe3cf8d526ceee7b7e4cc3981babc85b36fb770c1ba50f7c599d` | 本地缺 119 条源视频，另 1 条视频读帧失败 |
| `data/official/ms_swift_5frame/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1369 | `038acc775ae283721326cca813f6e0df141f34a5e707f4bc69566662bb4a1f36` | 本地缺 444 条源视频，另 3 条读帧失败 |
| `data/official/ms_swift_5frame/piwm_train_stage1_user_intent_val_v1.jsonl` | 39 | `bfb6719d28d479226a4c6916730655cb0bacfb437e5e5dea02819163eebaf36e` | 本地缺 11 条源视频 |
| `data/official/ms_swift_5frame/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 143 | `dc7de8b205132ad6dd9714799af583bbfef6f959dbadbfb8625944a418900e46` | 本地缺 42 条源视频 |
| `data/official/ms_swift_5frame/piwm_train_stage2_target_5act_greet_aug_v2.jsonl` | 86 | `8c7c8615b07841f2e7f1ceeeb25fc7840957ea5abb8af06f8d415efc4b391a99` | target 5 帧完整 |
| `data/official/ms_swift_5frame/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2.jsonl` | 2010 | `7551e44040a7fd1b4b726253fbdc77fb272a626a091d7944515cb68b3996f83f` | joint 版本受 general 缺视频影响 |
| `data/official/ms_swift_5frame/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl` | 2612 | `c65f66a2b14bccd4dbd297655508a3be2d08834bdc1da8a5db76053bce470a37` | A4 targetx8 版本受 general 缺视频影响 |
| `data/official/domain_specialization_eval_v2_5frame/target_frontcam_5act_test_action_selection.jsonl` | 30 | `15dba03c931cbb5b9ce312c1f548fc662a2ca42b2482375500053ff36333f1bb` | target test 5 帧完整 |
| `data/official/domain_specialization_eval_v2_5frame/target_frontcam_5act_test_all.jsonl` | 90 | `a5e324d89ab466041f65205ae3324c343c47097c7aefaf5e1cd4ef2bd59797bc` | target test all-task 5 帧完整 |

## Validation

- 所有已写出的本地 5 帧 JSONL 行都满足 `len(images)=5`。
- prompt 中 `<image>` token 数量和 `images` 数量一致。
- action-selection operational rows 中 `Reassure` 残留为 0。
- 重新运行 invariant test：`python3 -m pytest piwm_data/tests/test_5act_invariant.py -q`，结果 `7 passed`。

## Diff vs 3-Frame Data

- target-frontcam 数据：从每条 3 帧升级为每条 5 帧，行数不变。
- general Stage-1 数据：本地当前不是完整镜像，原因是源视频缺失，不应直接用于训练。
- 3 帧 frozen 数据未被覆盖，仍保留在 `data/official/ms_swift/` 与 `data/official/domain_specialization_eval_v2/`。

## Server Completion Status

远端补齐任务曾启动于：

`/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_5frame_server/`

但抽帧进程进入磁盘 I/O 卡顿状态。为避免影响 A3_minimal 训练和后续 eval，我已停止该进程。完整 general 5 帧补齐建议在 A3_minimal 训练和三组 eval 结束后单独重跑。

## To Launch 5-Frame Training Later

还需要：
- 在服务器上补齐完整 general 5 帧 JSONL，使 Stage-1 行数回到 2544。
- 重新做 server-resolved image path，避免本地绝对路径进入远端训练。
- 用 5 帧数据重新估算 `max_pixels` 和显存占用；5 帧会显著增加视觉 token 数。
- 先跑 30 条 target eval smoke test，再启动完整 5 帧 ablation。

