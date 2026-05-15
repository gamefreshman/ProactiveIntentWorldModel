# PIWM v2.2 Phase 2 Preflight Review

更新时间：2026-05-15

本报告用于进入 Phase 2 前审阅。目标是检查 `persona_to_intent_tier`、`failure_mode`、trigger DSL、source provenance 和 legacy 兼容策略是否足够稳，避免把未审清的专家规则直接接入 runtime。

当前结论：可以进入 Phase 2。原先两个 source 风险已经做了 hardening：

1. `gift_buyer_uncertain -> exploring` 已补 `SRC_SALES_BABIN_GIFT_SHOPPING_VALUE_2007` 和 `P_GIFT_SHOPPING_001`。
2. Bellenger 1980 已从当前可执行规则链路中移除；`browser_low_intent` 改由 Babin 1994 + Arnold/Reynolds 2003 支撑。Bellenger 只保留为历史候选 source/principle，不作为 Phase 2 runtime 规则依据。
3. 已确认当前数据中的 `gift_buyer_uncertain` persona 定义是 “A shopper buying for someone else and unsure which option fits best.”，因此 `uncertain` 边界成立。

## 1. Persona 分布与 PIT 实际影响

数据文件：

```text
data/official/piwm_train_synth_v1/main_schema.jsonl
```

该路径当前是 symlink：

```text
data/official/piwm_train_synth_v1 -> ../piwm_dataset_priority1000_unreviewed_compact_v2
```

统计结果：

| persona_type | count | percent | PIT |
|---|---:|---:|---|
| `experienced_brand_loyal` | 101 | 18.60% | `ready_to_buy` |
| `price_sensitive_cautious` | 97 | 17.86% | `exploring` |
| `browser_low_intent` | 94 | 17.31% | `low_intent_browsing` |
| `first_time_high_consideration` | 89 | 16.39% | `exploring` |
| `price_insensitive_decisive` | 89 | 16.39% | `ready_to_buy` |
| `gift_buyer_uncertain` | 73 | 13.44% | `exploring` |

PIT 后 tier 分布：

| intent_tier | count | percent |
|---|---:|---:|
| `exploring` | 259 | 47.70% |
| `ready_to_buy` | 190 | 34.99% |
| `low_intent_browsing` | 94 | 17.31% |

覆盖检查：

```text
browser_low_intent
experienced_brand_loyal
first_time_high_consideration
gift_buyer_uncertain
price_insensitive_decisive
price_sensitive_cautious
```

所有出现的 persona 都被 `PIT_001`-`PIT_006` 覆盖，没有第 7 类 fallback 漏洞。

判断：

- 没有单一 persona 超过 50%，最大为 18.60%，分布没有明显失衡。
- `ready_to_buy` 合计 34.99%，这部分不会触发最严格的跨阶段过滤；因此 v2.2 不能假设 Inform 占比会从 78% 直接大幅跌落。
- `browser_low_intent` 占 17.31%，低意图过滤机制会真实生效；如果旧视频画面表现得过度投入，这部分可能贡献较多 `red`。
- 进入 Phase 5/7 后，应预期整体 `red` 至少有 8-10% 的底线风险，不应把这视为迁移失败。

## 2. Source Hardening 结果

新增 `batch_005_source_hardening`，不保存长原文，只保存 source locator 和 compact paraphrase。

新增 source：

| source_id | 用途 | 判断 |
|---|---|---|
| `SRC_SALES_BABIN_GIFT_SHOPPING_VALUE_2007` | gift-shopping / recipient-fit / intent tier | 确认 Barry J. Babin 为第一作者；直接讨论 gift shopping value and satisfaction |
| `SRC_SALES_ARNOLD_REYNOLDS_HEDONIC_MOTIVATIONS_2003` | hedonic motivation / browsing behavior / intent tier | 比 Bellenger 1980 更适合作为可追溯的 browsing motivation 支撑 |

新增 principle：

| principle_id | 支撑 |
|---|---|
| `P_GIFT_SHOPPING_001` | gift shopping 是 recipient-oriented shopping mission，不只是购买者自用场景 |
| `P_HEDONIC_MOTIVATION_001` | hedonic motivations 与 browsing behavior 有直接关联 |

规则链路更新：

| rule_id | 更新后 source/principle |
|---|---|
| `PIT_004 browser_low_intent` | `P_INTENT_TIER_003; P_HEDONIC_MOTIVATION_001` |
| `PIT_005 gift_buyer_uncertain` | `P_INTENT_TIER_001; P_INTENT_TIER_002; P_FACTORS_002; P_GIFT_SHOPPING_001` |
| `PSI_009 browser_low_intent + early_browsing` | 增补 Arnold/Reynolds source link |
| `PSI_011 gift_buyer_uncertain + high_hesitation` | 增补 Babin gift-shopping source link |
| `TRANS_002 / TRANS_009 / TRANS_016` | 移除 Bellenger 依赖，必要处改用 Arnold/Reynolds |

persona 定义核查：

```text
gift_buyer_uncertain:
A shopper buying for someone else and unsure which option fits best.
```

判断：该定义明确包含 “unsure which option fits best”，不包含“已经决定买什么，只是在找具体型号”的 ready-to-buy 礼物购买者。因此 `PIT_005 -> exploring` 通过人工审阅。

Bellenger 处理：

- `SRC_SALES_BELLENGER_RECREATIONAL_SHOPPER_1980` 仍保留在 registry，`P_INTENT_TIER_004` 仍保留在 extracted principles。
- 当前 `conditional_rules.jsonl` 和 `rule_source_links.jsonl` 不再引用 Bellenger。
- 原因：目前只拿到二手引用，不适合作为 Phase 2 runtime 规则的必要支撑。

## 3. `failure_mode=null` 的 4 条 transition

4 条 `null` 如下：

| rule_id | state | legacy_action | act | params | reward | risk | 判断 |
|---|---|---|---|---|---:|---|---|
| `TRANS_015` | `early_browsing` | `A1_silent_observe` | `Hold` | `{"mode":"silent"}` | 0.5 | low | 合理 null，早期浏览下静默观察本身是低风险动作 |
| `TRANS_018` | `disengaged` | `A7_disengage` | `Hold` | `{"mode":"ambient"}` | 0.4 | low | 合理 null，已经 disengaged 时背景退出是去压迫 |
| `TRANS_019` | `disengaged` | `A1_silent_observe` | `Hold` | `{"mode":"silent"}` | 0.3 | low | 合理 null，静默不升级压力 |
| `TRANS_020` | `defensive_withdrawal` | `A7_disengage` | `Hold` | `{"mode":"ambient"}` | 0.5 | low | 合理 null，防御状态下退出是恢复动作 |

已落地约束：

- 4 条规则现在都有 `failure_mode_rationale`。
- `TransitionValue` schema 已强制：如果 `failure_mode` 为 `null`，必须提供 `failure_mode_rationale`。
- `compile.py` 会把 rationale 编译进 transition table。
- 单测检查 21 条 transition 中 17 条有 failure mode，4 条 null 均有 rationale。

统一 rationale：

```text
Low-intervention or disengagement actions in this state are not associated with distinct failure branches in the current source-backed taxonomy.
```

覆盖边界已单独写入 `docs/v2_validation/failure_mode_coverage.md`。v2.2 只覆盖主动干预失败；under-engagement、premature withdrawal 等被动失败需要 service failure / service recovery source batch，留到后续版本。

## 4. Trigger Conditions DSL v0.1

当前 17 条 failure mode 的 trigger 条件去重后共 15 个：

```text
explicit_purchase_question=true
intent_tier!=ready_to_buy
intent_tier=exploring
intent_tier=low_intent_browsing
intent_tier=ready_to_buy
interaction_signal=absent
pressure=firm
private_comparison=true
push_sensitivity=high
state=defensive_withdrawal
visible_cue=approaching_counter
visible_cue=brief_glance_walking_past
visible_cue=comparing_two_products
visible_cue=looking_around_for_help
visible_cue=no_eye_contact_avoidant
```

固定 DSL v0.1：

```text
condition := lhs op rhs
op        := "=" | "!="
lhs       := intent_tier | pressure | visible_cue | state |
             push_sensitivity | explicit_purchase_question |
             private_comparison | interaction_signal
rhs       := ASCII enum token or boolean token true/false
```

暂不支持：

```text
in
not_in
>
<
AND / OR 嵌套
括号
eval
```

运行时语义：

- 一个 `failure_mode.trigger_conditions` 列表内部默认 AND。
- `visible_cue=<x>` 表示 `<x>` in visible_cues。
- 缺失字段默认 false，不触发。
- 任何未知 lhs/op 都应该 raise 或进入 QA fail，不能静默忽略。

未来扩展规则：

- 新增 trigger condition 必须先扩展 DSL 白名单。
- 每个新增 lhs 必须有对应 runtime accessor 函数。
- 每个新增 op 必须有 parser/matcher 单测。
- 禁止在 Phase 2 私自加入 `>` / `<` 等数值比较；数值阈值需要新的 source/formalization 论证，留到后续版本。

## 5. retained_seed 分层抽样审计

这次不是随机抽样，而是按规则类型分层抽 10 条：3 条 candidates、3 条 transitions、2 条 cue-to-state、2 条 persona-state-to-intent。每条看两层：规则 source link 是否支撑规则，source/principle 是否支撑 formalization。

| rule_id | 类型 | 核查结论 | 风险 |
|---|---|---|---|
| `CAND_001` | candidate | 信息搜索/评估阶段下，观察、价值比较、开放提问作为低中压选项有支撑；`A3` 作为负例对照也合理 | 需要 Phase 2 用 `(act, params)` 重写后再验证排序 |
| `CAND_006` | candidate | action stage 下 recommendation/question 属于 closing-oriented action，有 AIDA/personal selling 支撑 | `needs_manual_support=true` 合理，精确排序仍需专家审 |
| `CAND_008` | candidate | disengaged attention 不应升级，退场/观察方向合理 | 低强度 theory anchored，不是强 SOP |
| `TRANS_003` | transition | strong recommend during hesitation 的 pressure/reactance 风险由 SPIN + Brehm 支撑 | reward 数值仍是工程校准 |
| `TRANS_012` | transition | action-stage recommendation 有收益，但 high push sensitivity 失败分支由 reactance 支撑 | 成功 reward 与 pressure 参数要在 Phase 2 校准 |
| `TRANS_017` | transition | early browsing 下 strong recommend 属于 premature closing，失败分支有支撑 | reward 数值仍需分布模拟验证 |
| `CUE2STATE_001` | cue-to-state | price check + long dwell 映射到 value uncertainty / alternative evaluation 有支撑 | 视觉 cue 到 state 是工程 formalization |
| `CUE2STATE_010` | cue-to-state | approaching counter 作为 purchase-decision readiness 合理 | 需要 retail SOP 或真实拍摄数据继续加固 |
| `PSI_009` | persona-state-intent | low-intent browsing -> explore_options 已增补 Arnold/Reynolds browsing support | 通过 |
| `PSI_011` | persona-state-intent | gift-buyer hesitation -> seek_reassurance 已增补 Babin gift-shopping support | 通过 |

审计结论：

- 未发现 blocker。
- 10 条中需要继续人工审的主要是排序、reward 数值和 cue->state 的视觉 formalization，不是 source 假引用问题。
- 这支持进入 Phase 2，但 Phase 2 的分布校准报告不能把 retained_seed 的 reward 当成已验证常数。

## 6. retained_seed source_link 历史

`rule_source_links.jsonl` 的 git 历史显示，72 条 retained_seed links 来自 2026-04-29 的已有提交：

```text
d4b0e64 docs: update research log and audit documents for Phase 2 data contract upgrade
Date: Wed Apr 29 20:59:49 2026 +0800
```

当前工作区对该文件的变化来自本轮 v2.2 hardening：

- 新增 6 条 PIT source links。
- 给 transition links 增补 failure-mode 相关 source ids / formalization note。
- 本轮又把 Bellenger 从当前可执行规则链路中移除，并为 gift/browser 相关 retained_seed link 增补更直接 source。

判断：

- 72 条 retained_seed source links 不是本轮凭空生成。
- 但它们本身是一次性 backfill，所以后续仍建议按批次继续抽审。

## 7. Phase 2 兼容层方案

强制采用实现 B：legacy adapter，不污染 v2 schema。

实现规范：

```text
file: piwm_data/migration/legacy_action_mapping.py
```

要求：

- 文件头必须写明：`v2.2 migration-only; delete in v2.3 after old archives are retired.`
- 必须用完整 explicit dict 映射 A1-A8，不允许 if/elif 推导。
- archive_loader 加载旧 session 时调用 adapter，把 A1-A8 转为 `(act, params)`。
- v2 schema 中不得新增 `legacy_action` 字段。
- 单测必须覆盖 A1-A8 全部映射。
- adapter 只能用于迁移入口和兼容性对照，不允许进入新数据生成主链路。

避免实现 A：

```python
class CandidateAction:
    legacy_action: Optional[str]
    act: Optional[str]
    params: Optional[dict]
```

原因：

- 会把 legacy 污染进 v2 schema。
- 容易让 `legacy_action` 长期残留。
- 与“v2.2 废弃 legacy_action 字段”的方向冲突。

## 8. RESEARCH_LOG 与 current docs 衔接

当前 `RESEARCH_LOG.md` 已记录 Phase 0A/0B、Phase 1A/1B 和 Phase 2 preflight source-hardening。

Phase 7 上线后必须补：

```text
docs/current/dataset_inventory.md 新增 v2 entry，并标注 v1 进入 _legacy。
data/official/DATASET_MANIFEST.json 新增 schema_version=v2.2 entry。
data/official/README.md 指向新的 v2 official dataset。
```

现在不改 `dataset_inventory.md` 是合理的，因为 official v2 尚未重导。

## Claude 审阅重点

1. 是否接受 `PIT_003/PIT_006 -> ready_to_buy` 合计约 35% 的 ready tier prior。
2. 是否接受 `low_intent_browsing` 约 17% 会贡献较多 red/yellow compatibility drift。
3. 是否接受 `failure_mode=null` 的 4 条均为 Hold 类动作，且已由 schema 强制 rationale。
4. 是否接受 trigger DSL v0.1 只支持 `=` / `!=`，并禁止 Phase 2 私自扩展数值比较。
5. 是否接受 Bellenger 从 runtime 规则链路中移除、保留为历史候选 source。
6. Phase 2 是否强制采用实现 B：迁移 adapter，不污染 v2 schema。

## 外部核查链接

- Babin, Darden, Griffin (1994), RePEc/DOI record: https://ideas.repec.org/a/oup/jconrs/v20y1994i4p644-56.html
- Babin, Gonzalez, Watts (2007), gift-shopping value source locator: https://aquila.usm.edu/fac_pubs/1909/
- Arnold and Reynolds (2003), DOI record: https://doi.org/10.1016/S0022-4359(03)00007-1
- Bellenger and Korgaonkar (1980) secondary reference in SAGE recreational shopper article: https://journals.sagepub.com/doi/10.1177/009207038501300321
- Brehm/reactance review discussion: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2015.00632/full
