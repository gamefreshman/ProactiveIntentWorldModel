# PIWM v2.2 Action Distribution Diagnostics

更新时间：2026-05-15

本页记录 Phase 2/3 之后的动作分布诊断。结论先写清楚：旧 official `best_action` 分布仍然 `Recommend=0`，但 v2-native policy path 已能通过 `Recommend(pressure=soft)` 产生推荐正样本。两者不是同一个口径，不能混用。

## Official v1 Backing Data

输入：

```text
data/official/piwm_train_synth_v1/main_schema.jsonl
```

该路径当前指向 backing dataset：

```text
data/official/piwm_train_synth_v1 -> ../piwm_dataset_priority1000_unreviewed_compact_v2
```

共 543 条 parent records。

| DialogueAct | count | percent |
|---|---:|---:|
| `Inform` | 407 | 74.95% |
| `Elicit` | 69 | 12.71% |
| `Hold` | 59 | 10.87% |
| `Reassure` | 8 | 1.47% |
| `Recommend` | 0 | 0.00% |
| `Greet` | 0 | 0.00% |

旧 best_action 分布：

| Legacy action | count |
|---|---:|
| `A5_provide_demonstration` | 314 |
| `A2_offer_value_comparison` | 93 |
| `A4_open_with_question` | 69 |
| `A1_silent_observe` | 59 |
| `A6_acknowledge_and_wait` | 8 |

用当前 v2 intent-tier filter 检查旧 best_action：

```text
best filtered by tier/action: {}
```

解释：543 条旧数据的 best_action 没有被 low-intent filter 直接判为非法；问题不是“旧 best 被过滤”，而是 reward/candidate 体系从未让 Recommend/Greet 成为 best。

## Official 543 Re-derived With v2 Policy Path

这是把同一批 official 543 条重新通过 `derive_policy_candidate_specs()` + `pick_best_action_spec()` 推导后的结果。它回答的是“当前 official 数据在 v2.2 规则下会变成什么分布”，不是新生成的 balanced policy slice。

Candidate rule coverage：

| Coverage | Count |
|---|---:|
| explicit | 518 |
| default_fallback | 25 |

Re-derived v2 policy best 分布：

| DialogueAct | count | percent |
|---|---:|---:|
| `Elicit` | 252 | 46.41% |
| `Recommend` | 119 | 21.92% |
| `Inform` | 105 | 19.34% |
| `Reassure` | 42 | 7.73% |
| `Hold` | 25 | 4.60% |
| `Greet` | 0 | 0.00% |

主要 policy drift：

| Old best act | Re-derived v2 best act | Count |
|---|---|---:|
| `Inform` | `Elicit` | 240 |
| `Inform` | `Recommend` | 62 |
| `Elicit` | `Recommend` | 57 |
| `Hold` | `Reassure` | 34 |

这解释了 compatibility report 中的 extended `yellow=353`：大量样本视觉与 schema 可以保留，但旧 best action 与 v2 policy best 不一致，应该作为 policy-migration yellow，而不是误写成 green。

## Full Rule Space Simulation

输入：

```text
scripts.scenario_sampler.build_all_scenarios(seed=42)
```

共 1920 个 state/persona/cue/aida/product 组合。

Intent tier 分布：

| intent_tier | count | percent |
|---|---:|---:|
| `exploring` | 960 | 50.00% |
| `ready_to_buy` | 640 | 33.33% |
| `low_intent_browsing` | 320 | 16.67% |

legacy-compatible best DialogueAct 分布：

| DialogueAct | count | percent |
|---|---:|---:|
| `Hold` | 864 | 45.00% |
| `Inform` | 576 | 30.00% |
| `Reassure` | 288 | 15.00% |
| `Elicit` | 192 | 10.00% |
| `Recommend` | 0 | 0.00% |
| `Greet` | 0 | 0.00% |

这里的表是旧 selection/reward 口径下的全规则空间诊断，不是后文的 v2-native policy helper 结果。真正的 v2 policy 分布见上面的 official 543 re-derivation 和下面的 explicit candidate-rule slice。

旧 best_action 分布：

| Legacy action | count |
|---|---:|
| `A1_silent_observe` | 816 |
| `A5_provide_demonstration` | 480 |
| `A6_acknowledge_and_wait` | 288 |
| `A4_open_with_question` | 192 |
| `A2_offer_value_comparison` | 96 |
| `A7_disengage` | 48 |

按 intent tier 展开：

| intent_tier | Hold | Inform | Reassure | Elicit | Recommend | Greet |
|---|---:|---:|---:|---:|---:|---:|
| `exploring` | 432 | 288 | 144 | 96 | 0 | 0 |
| `low_intent_browsing` | 144 | 96 | 48 | 32 | 0 | 0 |
| `ready_to_buy` | 288 | 192 | 96 | 64 | 0 | 0 |

Intent-tier filter 影响：

```text
state_aida_to_candidates->intent_tier_filter_removed:A3_strong_recommend = 136
```

解释：136 个 low-intent scenario 中 firm recommendation 被候选过滤移除。但因为当前 reward table 中 `A3_strong_recommend` 原本也不会赢，所以过滤本身不会让 Recommend 分布改善；它只修正候选合法性。

## 当前判断

- `Inform` 在 official 543 条中仍然过强：74.95%。
- legacy-compatible rule-space simulation 中 `Inform` 降到 30%，但这是全规则空间均匀组合，不代表 official 数据，也不是最终 v2-native policy path。
- 旧 official best 中 `Recommend=0` 是当前最大动作均衡问题；v2 policy path 已把 official 543 重推导到 `Recommend=119`，把 explicit policy slice 推到 `Recommend=360`。
- `Greet=0` 是设计选择，本期不修。
- 真正需要下一步修的是 v2-native candidate/outcome reward calibration，而不是 persona intent-tier mapping。

## Recommend Zero Root Cause

当前 legacy candidate 表里，Recommend 只通过 `A3_strong_recommend` 出现，共 7 个 state/aida 组合：

| state | aida | best legacy action | A3 reward | winning reward |
|---|---|---|---:|---:|
| `high_hesitation` | `interest` | `A2_offer_value_comparison` | -0.5 | 0.8 |
| `high_hesitation` | `desire` | `A2_offer_value_comparison` | -0.5 | 0.8 |
| `active_evaluation` | `interest` | `A5_provide_demonstration` | -0.3 | 0.8 |
| `active_evaluation` | `desire` | `A5_provide_demonstration` | -0.3 | 0.8 |
| `ready_to_decide` | `desire` | `A4_open_with_question` | 0.6 | 0.8 |
| `ready_to_decide` | `action` | `A4_open_with_question` | 0.6 | 0.8 |
| `early_browsing` | `attention` | `A1_silent_observe` | -0.6 | 0.5 |

结论：

- 不是“Recommend 没进入候选集”；它在 legacy candidate space 中出现过。
- 真正问题是当前只有 `A3_strong_recommend = Recommend(pressure=firm)`，没有 `Recommend(pressure=soft)` 作为正向推荐候选。
- 不能简单把 `A3_strong_recommend` reward 抬高，否则会把“强势推荐”变成 best label，和 Phase 0/1 的 reactance / pressure 规则冲突。
- 正确修法是引入 v2-native candidate specs，让 `Recommend(pressure=soft)` 和 `Recommend(pressure=firm)` 同时存在，soft 可以赢，firm 多数作为负样本或 risky option。

额外诊断：若直接用当前 v2 failure-aware outcome 在全组合上选 best，`Recommend` 只赢 8 次，但 `Reassure` 会异常膨胀到 1354 次。这说明不能只把 selection 函数切到 v2 outcome，还必须同步校准 default transition 与 soft/firm recommend reward。

## v2.2 Policy Candidate Path

本轮新增了不改旧 official 导出的 v2-native policy path：

- `derive_policy_candidate_specs(state, aida, intent_tier)`：在合适场景把 legacy `A3` 拆为 `Recommend(pressure=soft)` 与 `Recommend(pressure=firm)`。
- `pick_best_action_spec(...)`：按 v2 outcome reward 选择 `(act, params)`，不回写旧 `best_action`。
- `Recommend(pressure=soft)` 在 `ready_to_decide/desire|action` 和 `active_evaluation/desire` 中有正向 reward calibration。
- `scripts.scenario_sampler --candidate-rule-only`：只保留有显式 candidate rule 的 state/AIDA 组合，避免 default fallback 放大低干预动作。

显式 candidate-rule slice dry-run：

```bash
python3 -m scripts.scenario_sampler \
  --candidate-rule-only \
  --out /tmp/piwm_policy_explicit.jsonl \
  --stats-out /tmp/piwm_policy_explicit_stats.json
```

显式 slice 共 864 条场景，v2 policy best 分布：

| DialogueAct | count | percent |
|---|---:|---:|
| `Recommend` | 360 | 41.67% |
| `Elicit` | 272 | 31.48% |
| `Inform` | 136 | 15.74% |
| `Hold` | 56 | 6.48% |
| `Reassure` | 40 | 4.63% |
| `Greet` | 0 | 0.00% |

这说明 `Recommend` 已能通过 soft recommendation 进入 v2 policy best，且没有把 `A3_strong_recommend` 直接抬成正样本。`Elicit` 也通过 `active_evaluation + interest` 的开放式澄清问题校准进入 10% 以上。

全笛卡尔积仍会让 `Hold/Reassure` 偏高，原因是 1056 条 state/AIDA 组合没有显式 candidate rule，只能走 `DEFAULT_CANDIDATES`。因此后续新生成 policy 数据应使用 explicit candidate-rule slice；不要把全规则空间 fallback 组合直接当平衡训练分布。

## 864 vs 1920 Filtering Logic

1920 是完整笛卡尔积：

```text
8 product categories × 6 personas × 10 cues × 4 AIDA stages = 1920
```

864 是只保留 `(latent_state, aida_stage)` 命中 `STATE_AIDA_TO_CANDIDATES` 的场景。过滤条件是：

```python
scenario["derived"]["candidate_rule_coverage"] == "explicit"
```

显式规则覆盖分布：

| Coverage | Count |
|---|---:|
| explicit | 864 |
| default_fallback | 1056 |

显式 slice 的结构：

| Dimension | Distribution |
|---|---|
| AIDA | `attention=96`, `interest=288`, `desire=384`, `action=96` |
| intent tier | `exploring=432`, `low_intent_browsing=144`, `ready_to_buy=288` |
| state | `active_evaluation=480`, `ready_to_decide=192`, `high_hesitation=96`, `early_browsing=48`, `disengaged=48` |

被过滤的 1056 条不是随机缺失；它们主要是当前专家规则没有显式定义的 state/AIDA 组合。因此 explicit slice 不能代表“全部理论状态空间”，但更适合作为近期 policy 数据生成入口，因为每条都有 candidate rule 支撑。

## 下一步

后续应做：

1. 将 v2-native policy path 的规则从 runtime helper 进一步沉淀回 expert corpus，而不是长期只放在 `rules.py`。
2. 已导出独立 `data/official/piwm_train_synth_v2/` 和 `data/official/piwm_policy_slice_v2/`，不要覆盖 `PIWM-Train-Synth-v1`。
3. 已新增 `next_state_by_action_v2`，旧 `next_state_by_action` 继续作为 A-label compatibility alias。
4. 保持 `Greet=0` 为本期设计选择，只在真实拍摄 manifest / terminal scripts 中保留。
