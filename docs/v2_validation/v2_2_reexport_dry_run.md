# PIWM v2.2 Official Re-export and Independent Export

更新时间：2026-05-15

dry-run / diff preview 命令：

```bash
python3 scripts/refresh_official_v2_exports.py --dry-run
python3 scripts/refresh_official_v2_exports.py --dry-run --output-diff docs/v2_validation/v2_2_reexport_diff_preview.md
```

结论：dry-run 只读取并统计 official datasets，没有重写 JSONL 或 `_stats.json`。

| Dataset | Records | State | Transition | Policy | Continuation |
|---|---:|---:|---:|---:|---:|
| `data/official/piwm_train_synth_v1` | 543 | 543 | 2011 | 543 | 0 |
| `data/official/piwm_eval_qa_v1` | 36 | 36 | 126 | 36 | 0 |
| `data/official/piwm_world_model_v1` | 24 | 24 | 66 | 23 | 44 |

当前 dry-run 证明三套 official 数据都能被 v2.2 schema/runtime 读取，并能计算出重导后的任务行数。WorldModel 的 policy row 从 24 变成 23，是因为 v2.2 重新推导 outcome reward 后有 1 条不再形成严格 chosen/rejected reward pair。

文件级 diff preview 见：

- `docs/v2_validation/v2_2_reexport_diff_preview.md`

该 preview 在临时目录生成候选输出，不修改 official JSONL。当前预览显示如果原地写回，三套 official 的主要 JSONL 都会逐行变化，原因是 v2.2 会补 `candidate_action_specs / best_action_spec / compatibility_tier / legacy_mismatch_flags / outcome_type` 等字段。因此正式迁移不应直接覆盖 v1。

## Independent Export

已执行独立 v2.2 导出，不覆盖 `PIWM-Train-Synth-v1`：

```bash
python3 scripts/refresh_official_v2_exports.py \
  --dataset data/official/piwm_train_synth_v1 \
  --output-dir data/official/piwm_train_synth_v2 \
  --summary-out data/official/V2_2_EXPORT_SUMMARY.json

python3 -m piwm_train.ms_swift_adapter \
  --data-dir data/official/piwm_train_synth_v2 \
  --output-jsonl data/official/ms_swift/piwm_train_synth_v2.jsonl \
  --allow-missing-images

python3 -m scripts.scenario_sampler \
  --candidate-rule-only \
  --out data/official/piwm_policy_slice_v2/policy_manifest.jsonl \
  --stats-out data/official/piwm_policy_slice_v2/_stats.json
```

输出：

| Artifact | Rows |
|---|---:|
| `data/official/piwm_train_synth_v2/main_schema.jsonl` | 543 |
| `data/official/piwm_train_synth_v2/state_inference.jsonl` | 543 |
| `data/official/piwm_train_synth_v2/transition_modeling.jsonl` | 2011 |
| `data/official/piwm_train_synth_v2/policy_preference.jsonl` | 543 |
| `data/official/ms_swift/piwm_train_synth_v2.jsonl` | 2554 |
| `data/official/piwm_policy_slice_v2/policy_manifest.jsonl` | 864 |

## Compatibility Boundary

`next_state_by_action` 仍保留旧 A-label key，保证 continuation 和旧 loader 不断。v2.2 已新增：

```text
next_state_by_action_v2
```

该字段使用 `rules.action_spec_key(act, params)` 生成 v2 action-keyed outcome map。v2.3 的清理任务是等待下游 loader 切到 `next_state_by_action_v2` 后，再删除迁移期 A-key 依赖。

## Commit Boundary

本次没有原地执行：

```bash
python3 scripts/refresh_official_v2_exports.py
```

也没有覆盖 `data/official/piwm_train_synth_v1`。v1 保持 frozen compatibility alias；v2.2 新实验使用独立 v2 路径。
