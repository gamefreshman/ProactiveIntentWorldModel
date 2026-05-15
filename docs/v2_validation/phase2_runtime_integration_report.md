# PIWM v2.2 Phase 2 Runtime Integration Report

更新时间：2026-05-15

本页记录 Phase 2 已落地的 runtime 改动。目标是让 `(act, params)`、intent tier 和 failure mode 可以进入可执行路径，同时不把 `legacy_action` 污染进 v2 schema。

## 已完成

### 1. Migration adapter

新增：

```text
piwm_data/migration/legacy_action_mapping.py
```

约束：

- 文件头明确标注：`v2.2 migration-only; delete in v2.3 after old archives are retired.`
- A1-A8 到 `(act, params)` 使用完整 explicit dict。
- `legacy_action_to_act_params_for_comparison()` 只用于迁移期对照。
- `act_params_to_legacy_for_comparison()` 只对 exact canonical mapping 返回旧 A-label；`Recommend(pressure=soft)` 不伪装成旧动作。

测试覆盖：

```text
piwm_data/tests/test_legacy_action_mapping.py
```

### 2. Intent tier runtime prior

`piwm_data/rules.py` 新增：

```python
PERSONA_TO_INTENT_TIER
derive_intent_tier(persona_type)
```

当前映射：

| persona_type | intent_tier |
|---|---|
| `price_sensitive_cautious` | `exploring` |
| `first_time_high_consideration` | `exploring` |
| `experienced_brand_loyal` | `ready_to_buy` |
| `browser_low_intent` | `low_intent_browsing` |
| `gift_buyer_uncertain` | `exploring` |
| `price_insensitive_decisive` | `ready_to_buy` |

fallback：未知 persona 默认 `exploring`，但 official 数据已确认 6 类全部覆盖。

### 3. Candidate filtering

`derive_candidate_actions()` 增加可选参数：

```python
derive_candidate_actions(state, aida, intent_tier=None)
```

行为：

- 默认不传 `intent_tier` 时保持旧行为。
- `intent_tier="low_intent_browsing"` 时过滤 `Recommend(pressure=firm)` 这类 aggressive close。

新增：

```python
derive_candidate_action_specs(state, aida, intent_tier=None)
```

输出 canonical v2:

```json
[
  {"act": "Hold", "params": {"mode": "silent"}},
  {"act": "Reassure", "params": {"focus": "time", "supporting_acts": [{"type": "Hold", "params": {"mode": "ambient"}}]}}
]
```

### 4. Failure mode matcher

`piwm_data/rules.py` 新增：

```python
derive_failure_mode(...)
infer_risk_tags_from_failure(...)
```

实现原则：

- matcher 只支持 DSL v0.1：`=` 和 `!=`。
- 未知 lhs/op 直接报错，不静默忽略。
- `visible_cue=<x>` 按 membership 判断。
- 缺失上下文不会触发 failure。
- 不使用 `eval`。

当前 context accessors：

| lhs | runtime 来源 |
|---|---|
| `intent_tier` | `derive_intent_tier()` 或显式参数 |
| `pressure` | `act_params.pressure` |
| `visible_cue` | `visible_cues` |
| `state` | 当前 latent state |
| `push_sensitivity` | persona prior |
| `explicit_purchase_question` | `approaching_counter` / `looking_around_for_help` |
| `private_comparison` | `asking_companion_opinion` |
| `interaction_signal` | `brief_glance_walking_past` / `no_eye_contact_avoidant` 视为 absent |

### 5. Action outcome v2 path

`derive_action_outcome()` 保留旧调用方式：

```python
derive_action_outcome(state, aida_stage, persona_type, action)
```

同时支持 v2 keyword path：

```python
derive_action_outcome(
    state,
    aida_stage,
    persona_type,
    act="Recommend",
    params={"target": "item", "pressure": "firm"},
    intent_tier="low_intent_browsing",
    visible_cues=["brief_glance_walking_past"],
)
```

新增输出字段：

```text
dialogue_act
act_params
intent_tier
risk_tags
failure_mode
outcome_type
```

这些字段已在后续 Phase 5 schema increment 中正式纳入 `ActionOutcome`，见
`docs/v2_validation/phase5_schema_increment_report.md`。

### 6. archive_loader 接入 adapter

`load_session()` 现在会：

1. 根据 persona 推导 `intent_tier`。
2. 调用 `derive_candidate_actions(..., intent_tier=intent_tier)`。
3. 通过 `legacy_to_v2()` 把候选 A-label 转成 `(act, params)`。
4. 用 v2 action context 调用 `derive_action_outcome()`。

注意：

- main schema 当前仍输出旧 `candidate_actions` / `best_action` 字符串，以保证现有 official v1 和测试兼容。
- `legacy_action` 没有新增进 v2 schema。
- Phase 5 已新增 `CandidateAction` mirror 字段；main schema 当前仍保留旧
  `candidate_actions` / `best_action` 字符串作为迁移键。

## 已知未完成

- transition table 还没有真正拆成 `(act, params)` key；目前 soft Recommend 仍临时落到旧 recommendation transition family。
- reward calibration 还没开始；动作分布修复要等 Phase 3/4 的 candidate/outcome 规则和模拟报告。
- 当前动作分布诊断见 `docs/v2_validation/action_distribution.md`；`Recommend` 仍为 0，是下一步 reward calibration 的核心问题。
- Prompt label leakage 策略见 `docs/v2_validation/label_leakage_policy.md`；QA gate 已有显式 `check_label_leakage()` 入口。
- Phase 5 schema increment 见 `docs/v2_validation/phase5_schema_increment_report.md`；`Persona.intent_tier`、`ActionOutcome` v2 fields、`candidate_action_specs`、`best_action_spec`、`compatibility_tier` 已纳入 schema。
- `next_state_by_action` 仍未迁移为 v2 action key；旧 A-label key 暂时作为迁移兼容键保留。
- official dataset 尚未重导；当前只是 runtime 能走 v2 path。

## 验证

已通过：

```text
python3 -m pytest piwm_data/tests/test_legacy_action_mapping.py piwm_data/tests/test_rules.py piwm_data/tests/test_archive_loader.py
```

结果：

```text
46 passed
```
