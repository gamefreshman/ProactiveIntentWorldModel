# PIWM Data Generation Chain v2.2 Contract

更新时间：2026-05-19 CST

本文定义后续更新动作、场景、label 和专家规则时的唯一链路。目标是避免只改某个 JSONL 或某个文档，导致规则、数据、训练和论文口径再次分叉。

## 1. Dataset Boundary

当前保留两条数据线：

| 数据线 | 主体 | 用途 | 当前状态 |
|---|---|---|---|
| `PIWM-Train-Synth-v1` | 真人导购逻辑 | frozen 训练顾客状态识别、真人导购介入策略、话术和动作 | 已有 543 parent；保留 `best_action_realization` |
| `PIWM-Train-Synth-v2` | 真人导购逻辑 | schema v2.2 训练入口 | 已写出独立 v2.2 目录；同一批 543 parent，不新增视频 |
| `PIWM-PolicySlice-v2` | 专家规则 policy manifest | 动作均衡、后续生成和 policy-head 数据规划 | 已写出 864 条 explicit candidate-rule scenarios；不是视频数据 |
| target terminal dataset | 智能导购终端 / 数字人售货柜 | 训练或评估终端屏幕、语音、灯效、柜体动作 | 后续单独建设 |

当前 5-act operational policy space 为：`Greet / Elicit / Inform / Recommend / Hold`。`Reassure` 不进入当前 5-act action-selection 训练、推理或 macro-F1 口径；历史 `PIWM-Train-Synth-v2` / `PIWM-PolicySlice-v2` 中的 `Reassure` 只能作为 source/compatibility 分析对象。

## 2. Source Of Truth

任何动作、场景、label 变更必须按以下顺序维护：

1. `piwm_data/expert_corpus/distilled/conditional_rules.jsonl`
   规则知识库：cue -> state、persona/state -> intent、state/AIDA -> candidates、transition/reward。
2. `piwm_data/expert_corpus/distilled/rule_source_links.jsonl`
   规则来源、支持强度、是否需要人工专家审阅。
3. `piwm_data/rules.py`
   runtime fast path；必须与专家库编译结果保持一致。
4. `piwm_data/archive_loader.py`
   把 prompt/session 变成 `MainSchemaRecord`。
5. `piwm_data/schemas.py`
   读写兼容层；v2.2 读旧 `co_acts`，写新 `act_params.supporting_acts`，并保留 `candidate_action_specs / best_action_spec / next_state_by_action_v2`。
6. `piwm_data/exporters.py`
   从母记录切出 state inference、transition modeling、policy preference、World Model 任务。
7. `scripts/scenario_sampler.py`
   新数据生成前的场景采样；v2.2 policy slice 必须优先使用 `--candidate-rule-only`。
8. `scripts/refresh_official_v2_exports.py`
   重导 official datasets；必须先跑 `--dry-run`，正式输出必须写入独立 v2 目录，不覆盖 frozen v1。
9. `data/official/DATASET_MANIFEST.json` 和 `docs/current/dataset_inventory.md`
   更新对外规模、字段版本、红线。

不得直接手工修改 official JSONL 后跳过上述链路。

## 3. v2.2 Action Label Policy

### 3.1 Canonical act payload

新 canonical act payload：

```json
{
  "act": "Reassure",
  "params": {
    "focus": "time",
    "supporting_acts": [
      {"type": "Hold", "params": {"mode": "ambient"}}
    ]
  }
}
```

`legacy_action` 不进入 v2.2 canonical action object。旧 A-label 只作为迁移键，写在旧 `candidate_actions / best_action` 字段中；新语义字段是 `candidate_action_specs / best_action_spec`。

### 3.2 Distribution policy

当前 `PIWM-Train-Synth-v1` 的 best-act 分布偏斜：

| DialogueAct | 当前 best count |
|---|---:|
| `Inform` | 407 |
| `Elicit` | 69 |
| `Hold` | 59 |
| `Reassure` | 8 |
| `Recommend` | 0 |
| `Greet` | 0 |

解释：

- `Greet=0` 是 synthetic train 的覆盖缺口；当前 5-act 主路径需要通过 target-frontcam / realshoot 补充 `Greet`。
- `Recommend=0` 说明现有 reward/candidate 规则过度把推荐当负样本或候选对照，不适合作为平衡 policy-head 数据。
- `Inform` 过高，说明 active evaluation 场景与演示/比较奖励过强。

后续如果要训练更平衡的动作选择，不能简单复制当前分布。v2.2 已新增 policy slice 路径：

```bash
python3 -m scripts.scenario_sampler \
  --candidate-rule-only \
  --out data/official/piwm_policy_slice_v2/policy_manifest.jsonl \
  --stats-out data/official/piwm_policy_slice_v2/_stats.json
```

该路径只保留有显式 `state_aida_to_candidates` 规则支撑的 state/AIDA 组合，避免让全笛卡尔积中的 default fallback 放大 `Hold/Reassure`。

当前 explicit policy slice dry-run 分布：

| DialogueAct | v2 policy best count |
|---|---:|
| `Recommend` | 360 |
| `Elicit` | 272 |
| `Inform` | 136 |
| `Hold` | 56 |
| `Reassure` | 40 |
| `Greet` | 0 |

继续维护目标：

| 目标 | 做法 |
|---|---|
| 增加 `Recommend(pressure=soft)` 正样本 | 已在 v2 policy path 拆出，并落到 `PIWM-PolicySlice-v2` |
| 保留 `Recommend(pressure=firm)` 负样本 | 只作为强推反例，不混成推荐整体反例 |
| 处理 `Reassure` 历史样本 | 当前 5-act 过滤掉 `Reassure`；如果未来恢复，需要先重开动作口径决策 |
| 保留 `Greet` 在 target/realshoot | `Greet` 是当前 5-act 成员；target/realshoot 是补充该 act 覆盖的主要来源 |
| 降低 `Inform` 独占 | 在 active evaluation 中区分“需要提问”和“需要演示/比较”的视觉 cue |

## 4. Scene And Label Refresh

后续场景 label 不再只靠单个 `target_cue` 决定。推荐生成顺序：

```text
scene_spec
  -> product_category
  -> persona
  -> observable_cues[]
  -> visual_state
  -> latent_state
  -> aida_stage
  -> intent
  -> bdi
  -> candidate_actions
  -> candidate_dialogue_acts
  -> transition/reward
  -> best_action
  -> best_action_realization
```

`observable_cues[]` 应允许多个 cue，并记录主 cue 与辅助 cue。当前 runtime 已支持多 cue priority，但现有生成数据大多是单 cue，需要在下一轮 prompt manifest 中补齐。

## 5. Expert Knowledge Update Policy

专家知识库当前状态：

- 72 条 runtime rules 已全部有 source links。
- 38 条为 `manual_supported`。
- 40 条仍是 `theory_anchored`。
- 0 条为 `expert_reviewed`。

下一轮更新重点不是增加更多 seed rule，而是：

1. 审阅 `state_aida_to_candidates` 和 `transition`，解决 best-act 分布偏斜。
2. 把 `Recommend(pressure=soft)` 从 `A3_strong_recommend` 中拆出正向推荐规则。
3. 为 `Greet` 增加更多正样本依据；`Reassure` 如需重新进入主动作空间，必须先重新决策动作口径并重跑过滤、切分、评测和文档。
4. 更新 `_provenance_coverage.json`，不能声称 expert-reviewed。

## 6. Required Checks

每次改动作/场景/label 规则后必须跑：

```bash
python3 -m pytest piwm_data/tests/test_rules.py piwm_data/tests/test_schemas.py piwm_data/tests/test_exporters.py
python3 -m scripts.audit_action_space --main-schema data/official/piwm_train_synth_v1/main_schema.jsonl
python3 -m scripts.scenario_sampler --candidate-rule-only --out /tmp/piwm_policy_explicit.jsonl --stats-out /tmp/piwm_policy_explicit_stats.json
```

重导 official 数据前还要跑：

```bash
python3 -m scripts.refresh_official_v2_exports --dry-run
```

重导完成后更新：

- `data/official/DATASET_MANIFEST.json`
- `data/official/README.md`
- `docs/current/dataset_inventory.md`
- `RESEARCH_LOG.md`
