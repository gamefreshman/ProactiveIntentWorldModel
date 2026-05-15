# PIWM v2.2 Phase 5 Schema Increment Report

更新时间：2026-05-15

本页记录 Phase 5 的安全 schema increment。此步把 Phase 2 runtime 已经产生的 v2 字段纳入 schema，并补齐 candidate action 的 `(act, params)` 镜像字段；仍不删除旧字段、不重导 official 数据。

## 已完成

### Persona intent tier

`Persona` 新增：

```python
intent_tier: Optional[IntentTier]
```

行为：

- 若输入未提供，schema 自动根据 `persona.type` 调用 `rules.derive_intent_tier()` 填充。
- 当前 `gift_buyer_uncertain` 自动得到 `exploring`。
- 当前 `browser_low_intent` 自动得到 `low_intent_browsing`。

### ActionOutcome v2 fields

`ActionOutcome` 新增：

```python
dialogue_act: Optional[str]
act_params: dict[str, Any]
intent_tier: Optional[IntentTier]
risk_tags: list[str]
failure_mode: Optional[str]
outcome_type: Literal["success", "failure"]
```

校验：

- `dialogue_act` 存在时，必须通过 `rules.validate_dialogue_act(dialogue_act, act_params)`。
- `outcome_type="failure"` 时必须有 `failure_mode`。
- reward consistency 仍然保持旧校验：`reward_components.final_reward == reward`。

### archive_loader 影响

`archive_loader.load_session()` 已经在 Phase 2 接入 v2 outcome context，因此现在生成的 `ActionOutcome` 会保留：

- `dialogue_act`
- `act_params`
- `intent_tier`
- `risk_tags`
- `failure_mode`
- `outcome_type`

同时 `MainSchemaRecord.candidate_actions` 和 `MainSchemaRecord.best_action` 仍然保留旧 A-label 字符串，保证 exporter/training 当前兼容。

### CandidateAction v2 mirror

新增 canonical v2 action object：

```python
class CandidateAction(BaseModel):
    act: str
    params: dict[str, Any]
```

`MainSchemaRecord` 新增：

```python
candidate_action_specs: list[CandidateAction]
best_action_spec: Optional[CandidateAction]
compatibility_tier: Literal["green", "yellow", "red"]
legacy_mismatch_flags: list[str]
```

行为：

- 输入仍可带旧 `candidate_actions` / `best_action` 字符串；schema 自动生成 v2 mirror。
- `CandidateAction` 不包含 `legacy_action` 字段，旧 A-label 只在迁移 adapter 入口转成 `(act, params)`。
- `compatibility_tier` 当前按 mirror mismatch 和 intent-tier visual mismatch 分级。
- `docs/v2_validation/compatibility_report.md` 已基于 official v1 `main_schema.jsonl` 生成当前分级统计。

当前 official v1 主数据兼容性结果：

| Tier | Count | Ratio |
|---|---:|---:|
| green | 462 | 85.08% |
| yellow | 0 | 0.00% |
| red | 81 | 14.92% |

`red` 当前全部来自 `intent_tier_visual_mismatch`，说明低意图 persona 与高投入视觉 cue 存在 81 条冲突样本。

## 暂不做

- 暂不把旧 `candidate_actions` 原字段替换成 `List[CandidateAction]`，先用 `candidate_action_specs` 作为 v2 canonical mirror。
- 暂不删除 `best_action`。
- 暂不删除 `legacy_action` 兼容字段。
- 暂不把 `next_state_by_action` key 改成 v2 action key。

这些属于后续老数据重推导和 official v2 re-export，必须配合 dry-run 报告执行。

## 验证

已通过：

```text
python3 -m pytest piwm_data/tests/test_schemas.py piwm_data/tests/test_archive_loader.py piwm_data/tests/test_exporters.py
```

结果：

```text
49 passed
```
