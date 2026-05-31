# PIWM Expert Corpus

更新时间：2026-05-19

本目录维护动作、场景、label 生成链路的专家规则来源。它不是历史备份，后续改 `piwm_data/rules.py` 前必须先检查这里。

当前状态：

- `distilled/conditional_rules.jsonl`: 78 条 rules；其中 72 条是旧 runtime seed rules，6 条是 v2.2 `persona_to_intent_tier`。
- `sources/sales_source_registry.jsonl`: 12 个 sales source，其中 `SRC_SALES_MAOTAI_GOLD_QUESTIONNAIRE_2026_05` 是 2026-05 新接入的茅台金牌导购问卷内部专家来源。
- `distilled/extracted_principles.jsonl`: 27 条 compact principles；其中 11 条来自 v2.2 Phase 0B。茅台问卷原则目前仍在 batch draft，尚未进入该文件。
- `distilled/rule_source_links.jsonl`: 78 条规则均已链接来源。
- `distilled/_provenance_coverage.json`: 38 条 `manual_supported`，40 条 `theory_anchored`，0 条 `expert_reviewed`。
- `distillation_batches/`: v2.2 起新增的蒸馏批次机制。新专家知识必须先进入 batch，完成审阅后再 promote 到 `distilled/`。
- `sources/maotai_gold_sales_questionnaire_2026_05/`: 三份茅台销售员问卷的结构化来源包，包含 `structured_records.json` 和 `source_manifest.json`。
- `distillation_batches/batch_006_maotai_gold_sales/`: 茅台问卷候选蒸馏批次，含 10 条 source excerpts 和 10 条 candidate principles；`finalized.jsonl` 暂时为空，等待项目负责人审阅。

v2.1 更新口径：

- `PIWM-Train-Synth-v1` 保留真人导购逻辑，不把 terminal behavior 当作已采集 target。
- Source 层仍保留六个 `DialogueAct` 便于溯源和兼容分析：`Greet / Elicit / Inform / Recommend / Reassure / Hold`；当前 operational 5-act 训练、推理和 macro-F1 只使用 `Greet / Elicit / Inform / Recommend / Hold`，过滤 `Reassure`。
- 顶层 `co_acts` 不再作为规则层主字段；辅助动作写入 `act_params.supporting_acts`。
- 当前 best-action 分布偏向 `Inform`，不能作为均衡动作空间证据。

下一轮专家库重点：

0. 审阅 `batch_006_maotai_gold_sales/extracted_draft.jsonl`，决定哪些茅台一线销售经验可以 promote 为正式 compact principles。
1. 基于 `P_RECOMMEND_PRESSURE_*` 拆分 `Recommend(pressure=soft)` 与 `Recommend(pressure=firm)`。
2. 审阅 `state_aida_to_candidates`：增加能够支持 `Recommend(pressure=soft)` 正样本的场景，不再让推荐只等同强推负样本。
3. 审阅 `Greet`：它已进入当前 5-act 主口径，但 opening / closing 问候仍需要更多 general/realshoot 证据支撑。
4. 补足 `Greet` 在 general/realshoot/target terminal 中的正样本覆盖，避免只由 target-frontcam 支撑当前 5-act 口径。

v2.2 蒸馏工具：

```bash
python3 -m piwm_data.expert_corpus.tools.run_distillation batch_002_intent_tier --overwrite
python3 -m piwm_data.expert_corpus.tools.review_helper batch_002_intent_tier --write-finalized
python3 -m piwm_data.expert_corpus.tools.promote_to_corpus batch_002_intent_tier
```

`promote_to_corpus` 默认是 dry-run；只有审阅通过后才允许加 `--commit`。
当前 Phase 1B 已更新 source/principle corpus、`persona_to_intent_tier` 规则类型和 transition `failure_mode` 字段，但不改变旧 72 条 runtime seed tables。

维护命令：

```bash
python3 -m piwm_data.expert_corpus.compile
python3 -m piwm_data.expert_corpus.provenance
python3 -m pytest piwm_data/tests/test_provenance.py piwm_data/tests/test_expert_corpus.py
```
