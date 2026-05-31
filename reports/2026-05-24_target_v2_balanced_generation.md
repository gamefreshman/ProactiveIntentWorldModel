本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Target v2 Balanced Stage-2 数据生成报告

生成时间：2026-05-24  
执行范围：只完成数据生成与验证；未启动 A3 训练；未启动 A4；未覆盖 Path C / A3_minimal checkpoint。  
生成脚本：`scripts/build_stage2_target_v2_balanced.py`

## 1. 一句话结论

`target_v2_balanced` 已按新口径重新生成：**完全排除同事 `piwm_1001-1118` video-pending 批次**，只使用当前已有视频/抽帧的数据入口：

- 完整保留 `target 71 + GreetAug-v2 15`，共 86 条；
- 从 `PIWM-Train-Synth-v2` general 543 parent 中抽取 104 条 action-selection 监督；
- Stage-2 action-selection 监督从 86 条扩展到 **190 条**；
- joint 训练入口为 Stage-1 2544 条 + Stage-2 190 条 = **2734 条**。

最终 Stage-2 best act 分布：

| Act | Count |
|---|---:|
| Greet | 26 |
| Elicit | 41 |
| Inform | 41 |
| Recommend | 41 |
| Hold | 41 |

Greet 不能补到 41，因为 general 543 parent 中 `best_act=Greet` 为 0。本轮没有做 Greet 重复采样或复制增强。

## 2. 输出文件

| 文件 | 行数 | sha256 |
|---|---:|---|
| `data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl` | 190 | `d1f919d04a98378471ecc9a2c38490d75cc6feb025ee9ae19ae9fe7416139267` |
| `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` | 2734 | `1bc93963018bc3bed32a98815549cd4c0c3963b32a946fb9a732bb72132299a9` |
| `data/official/ms_swift/piwm_train_stage2_target_v2_balanced_summary.json` | - | `4b6b1ee1186559fa010ef6c101bec0408757fae9cd9b53206239e293a982ce06` |
| `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced_summary.json` | - | `9fff8a0865e3b8575f9f4f103258923dee1aa4c53ffee78c85a7d6f5e1da6539` |

## 3. 数据来源组成

| 来源 | 数量 | 说明 |
|---|---:|---|
| 现有 target train | 71 | 来自 `PIWM-Target-Frontcam-v1` 清洗后 Stage-2 train |
| GreetAug-v2 | 15 | 已有 Greet 增强样本，有图片路径 |
| general Elicit 抽样 | 27 | 从 general 252 条 Elicit 中按 `state_id` 稳定均匀抽样 |
| general Recommend 抽样 | 36 | 从 general 125 条 Recommend 中按 `state_id` 稳定均匀抽样 |
| general Hold 抽样 | 41 | 从 general 61 条 Hold 中按 `state_id` 稳定均匀抽样 |
| 合计 | 190 | 全部为 operational 5-act |

本轮明确排除：

| 排除来源 | 原因 |
|---|---|
| 同事 `piwm_1001-1118` | 只有 seed / manifest / prompts / labeled；没有对应 `piwm_1001-1118.mp4` 或抽帧 |
| Reassure | 不属于当前 operational 5-act |

## 4. 平衡策略

完整保留 86 条后，base 分布是：

| Act | Base count |
|---|---:|
| Greet | 26 |
| Elicit | 14 |
| Inform | 41 |
| Recommend | 5 |
| Hold | 0 |

因为 `Inform=41` 是完整保留 base 后的最高类，本轮把 general 可补的类别补到 41：

| Act | Base | General added | Final |
|---|---:|---:|---:|
| Greet | 26 | 0 | 26 |
| Elicit | 14 | 27 | 41 |
| Inform | 41 | 0 | 41 |
| Recommend | 5 | 36 | 41 |
| Hold | 0 | 41 | 41 |

这个策略的含义：不牺牲已有 target/GreetAug 数据，不引入无视频同事批次，也不复制 Greet；在这些约束下做到最接近均衡。

## 5. General 抽样方法

general 543 parent 的 best act 可用分布：

| Act | Available |
|---|---:|
| Greet | 0 |
| Elicit | 252 |
| Inform | 105 |
| Recommend | 125 |
| Hold | 61 |

抽样方法固定、可复现：

1. 按 act 过滤 general `policy_preference.jsonl`；
2. 每个 act 内按 `state_id` 稳定排序；
3. 用 `round(i * (n - 1) / (k - 1))` 取均匀位置；
4. 写入 `augmentation_policy=target_v2_general_<act>_balance_to_41_v2`；
5. 标记 `qa_status=synthetic_unreviewed`。

## 6. 验证结果

已通过：

| 检查 | 结果 |
|---|---|
| Stage-2 行数 | 190 |
| joint 行数 | 2734 |
| joint task 分布 | user_intent=543 / next_state_prediction=2001 / action_selection_5act=190 |
| `Reassure` / `reassure_` 残留 | 0 |
| best_act 是否在候选集中 | 190 / 190 |
| bad candidate act | 0 |
| Stage-2 with images | 190 / 190 |
| summary JSON 可解析 | 通过 |
| `py_compile` 生成脚本 | 通过 |
| `pytest piwm_data/tests/test_5act_invariant.py -q` | 7 passed |
| `git diff --check` 指定新文件 | 通过 |

候选集大小分布：

| candidate count | rows |
|---:|---:|
| 2 | 42 |
| 3 | 26 |
| 4 | 87 |
| 5 | 35 |

candidate act slot 总量：

| Act | Candidate slots |
|---|---:|
| Elicit | 127 |
| Greet | 38 |
| Hold | 186 |
| Inform | 164 |
| Recommend | 170 |

## 7. 与上一版 215 条的差异

上一版错误地导入了同事 `piwm_1001-1118` 的 89 条 Hold/Recommend video-pending rows，因此 Stage-2 是 215 条，并且有 89 条 `images=[]`。

本版修正后：

| 项 | 上一版 | 本版 |
|---|---:|---:|
| Stage-2 rows | 215 | 190 |
| Joint rows | 2759 | 2734 |
| 同事 `1001-1118` rows | 89 | 0 |
| General balancing rows | 40 | 104 |
| Rows with images | 126 | 190 |
| Rows without images | 89 | 0 |

本版更适合作为正式 A3 full 训练入口，因为不存在无图 action-selection 行。

## 8. 对 A3 训练的影响

如果 PI 验收通过，A3 full target_v2 应使用：

`data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl`

这不是 A4：target_repeat 仍为 1。

和 A3_minimal 旧数据相比，Stage-2 监督变化如下：

| Act | A3_minimal 86 | target_v2 190 | 变化 |
|---|---:|---:|---:|
| Greet | 26 | 26 | 0 |
| Elicit | 14 | 41 | +27 |
| Inform | 41 | 41 | 0 |
| Recommend | 5 | 41 | +36 |
| Hold | 0 | 41 | +41 |

预期影响：

- Hold 从 0 变为 41，是本轮最大结构性修复；
- Recommend 从 5 变为 41，应该能缓解 Recommend 学不到的问题；
- Elicit 从 14 变为 41，动作选择监督更稳；
- Inform 不变；
- Greet 没新增，仍可能是瓶颈，但至少保留全部 26 条。

## 9. 当前停止点

任务 1 已完成。  
任务 2：完整 A3 训练 **尚未启动**。

需要 PI 确认后再启动训练：

1. 是否接受本版 `target_v2_balanced`：190 条 Stage-2，全部有图片，无同事 video-pending 批次；
2. 是否用 `piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` 作为 A3 full target_v2 的训练入口。
