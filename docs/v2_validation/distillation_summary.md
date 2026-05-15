# PIWM v2.2 Distillation Summary

更新时间：2026-05-15

本页记录 v2.2 专家蒸馏基础设施。当前阶段已完成 Phase 0A-0B，并进入 Phase 1A-1B：建立 batch 机制和 dry-run 工具，将技术审阅通过的 source/principle additions promote 到主 expert corpus，新增 `persona_to_intent_tier` 规则类型，并为 transition 规则加入 failure-mode 字段。2026-05-15 又完成 `batch_005_source_hardening`，用于补齐 gift buyer 和 hedonic browsing 的 source 链路。仍未改 `piwm_data/rules.py` runtime policy，未重导 official 数据。

## 当前结论

- `distilled/conditional_rules.jsonl` 现有 78 条：72 条 seed/runtime rules + 6 条 v2.2 `persona_to_intent_tier` rules。
- 21 条 transition rules 均带有 `failure_mode` 字段：17 条有显式 failure mode，4 条为 `null` 且均带 `failure_mode_rationale`；覆盖边界见 `docs/v2_validation/failure_mode_coverage.md`。
- `sources/sales_source_registry.jsonl` 已从 6 条增至 11 条。
- `distilled/extracted_principles.jsonl` 已从 14 条增至 27 条。
- `distilled/rule_source_links.jsonl` 现有 78 条；新增 intent-tier rules 已 source-linked。
- 新增 `piwm_data/expert_corpus/distillation_batches/` 作为所有新专家知识的入口。
- 新增四个 v2.2 batch：`intent_tier`、`failure_mode`、`recommend_pressure`、`source_hardening`。
- 新增三支工具：`run_distillation.py`、`review_helper.py`、`promote_to_corpus.py`。
- `promote_to_corpus.py` 默认 dry-run；本次已按 batch dependency 顺序 commit 通过项。

## Batch 状态

| Batch | 目标 | Source additions | Draft principles | Finalized | 状态 |
|---|---|---:|---:|---:|---|
| `batch_001_seed` | 记录现有 72 条 seed rules | 0 | 0 | 0 | 不运行 extraction |
| `batch_002_intent_tier` | 三档 intent tier | 2 | 4 | 4 | 技术审阅通过，已 promote |
| `batch_003_failure_mode` | premature closing / feature dump / reactance / intrusion | 1 | 4 | 4 | 技术审阅通过，已 promote |
| `batch_004_recommend_pressure` | soft vs firm Recommend | 0 | 3 | 3 | 技术审阅通过，已 promote |
| `batch_005_source_hardening` | gift buyer / hedonic browsing source 加固 | 2 | 2 | 2 | 技术审阅通过，已 promote |

## Source 候选

这些条目已经写入 `sources/sales_source_registry.jsonl`。

- `SRC_SALES_BABIN_HEDONIC_UTILITARIAN_1994`: Babin, Darden, and Griffin (1994), hedonic/utilitarian shopping value. 用于 `intent_tier`。
- `SRC_SALES_BELLENGER_RECREATIONAL_SHOPPER_1980`: Bellenger and Korgaonkar (1980), recreational shopper profile. 只保留为历史候选 source；当前 v2.2 规则链路不再依赖它。
- `SRC_SALES_REACTANCE_BREHM_1966`: Brehm (1966), psychological reactance. 用于 `failure_mode` 和 pressure risk。
- `SRC_SALES_BABIN_GIFT_SHOPPING_VALUE_2007`: Babin, Gonzalez, and Watts (2007), gift shopping value and satisfaction. 用于 `gift_buyer_uncertain` 的 source hardening。
- `SRC_SALES_ARNOLD_REYNOLDS_HEDONIC_MOTIVATIONS_2003`: Arnold and Reynolds (2003), hedonic shopping motivations. 用于 `browser_low_intent` / browsing behavior 的 source hardening。

版权规则：这些 source 都按 `citation_only` 处理，只允许 compact paraphrase 和 source locator，不保存长原文。

## Promoted Principles

新增 13 条 principle：

- `P_INTENT_TIER_001` - `P_INTENT_TIER_004`
- `P_FAILURE_MODE_001` - `P_FAILURE_MODE_004`
- `P_RECOMMEND_PRESSURE_001` - `P_RECOMMEND_PRESSURE_003`
- `P_GIFT_SHOPPING_001`
- `P_HEDONIC_MOTIVATION_001`

这些 principle 只是专家知识层输入；其中 `P_INTENT_TIER_*`、`P_GIFT_SHOPPING_001` 和 `P_HEDONIC_MOTIVATION_001` 已进入 `persona_to_intent_tier` 或相关 retained_seed source links。它们尚未自动改变 candidate generation、transition reward 或 official export。

## 审阅入口

人工审阅时只需要打开：

- `piwm_data/expert_corpus/distillation_batches/batch_002_intent_tier/review_log.md`
- `piwm_data/expert_corpus/distillation_batches/batch_003_failure_mode/review_log.md`
- `piwm_data/expert_corpus/distillation_batches/batch_004_recommend_pressure/review_log.md`
- `piwm_data/expert_corpus/distillation_batches/batch_005_source_hardening/review_log.md`
- `docs/v2_validation/failure_mode_coverage.md`

后续新增 batch 时，把对应 draft 的 `review_status` 改为 `approved`，再运行：

```bash
python3 -m piwm_data.expert_corpus.tools.review_helper batch_002_intent_tier --write-finalized
python3 -m piwm_data.expert_corpus.tools.promote_to_corpus batch_002_intent_tier
```

确认 dry-run 没有 duplicate id 后，才允许：

```bash
python3 -m piwm_data.expert_corpus.tools.promote_to_corpus batch_002_intent_tier --commit
```

## 后续规则

1. Phase 1 不能绕过 batch 直接改 `conditional_rules.jsonl`。
2. `transition.failure_mode` 已进入 expert corpus；下一步才接入 runtime outcome calculation。
3. 下一步需要拆分 `Recommend(pressure=soft)` 与 `Recommend(pressure=firm)` 的 candidate/outcome 规则。
4. `legacy_action` 删除属于 schema/migration 阶段，不能在 Phase 1B 发生。
5. official 数据重导必须另走 dry-run 报告，不在本页执行。
