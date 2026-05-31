5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# Representation Collapse 机制诊断（只读）

## 0. 执行范围

- 本报告只读分析现有 target test raw output；未重训，未改模型，未改 official 数据，未改 5-act。
- 分析 1 已完成：PIWM 主模型在 target test 30 条上的 Dim 1/2/3 confusion 与 modal prediction concentration。
- 分析 2 的输入集已按 seed=42 准备，但当前没有可用 GPU 执行 PIWM 主模型 train-subset inference：A100 可 SSH 但处于无卡状态，4090 已按节省成本要求关机。因此 train-vs-test 数字不能伪造。
- 分析 3 依赖同一 GPU 条件，本轮未执行。

## 1. Confusion Pattern：PIWM 主模型，target test
### Dim 1 AIDA confusion matrix

| gold \ pred | action | attention | interest |
| --- | ---: | ---: | ---: |
| attention | 2 | 1 | 0 |
| interest | 4 | 0 | 6 |
| desire | 5 | 0 | 6 |
| action | 1 | 0 | 5 |

### Dim 2 intent_label confusion matrix

| gold \ pred | confirm_choice | explore_options | seek_reassurance |
| --- | ---: | ---: | ---: |
| compare_value_for_money | 6 | 0 | 0 |
| confirm_choice | 5 | 0 | 1 |
| explore_options | 15 | 0 | 0 |
| no_clear_intent | 2 | 1 | 0 |

### Dim 3 next_state confusion matrix

| gold \ pred | action | attention | desire | interest |
| --- | ---: | ---: | ---: | ---: |
| attention | 0 | 5 | 1 | 0 |
| interest | 0 | 5 | 20 | 6 |
| desire | 1 | 8 | 4 | 6 |
| action | 1 | 13 | 5 | 5 |

## 2. Modal Prediction Concentration

| 维度 | 最高频预测类 | 次数 | 占比 | 判定 | 预测分布 |
| --- | --- | ---: | ---: | --- | --- |
| Dim 1 AIDA | interest | 17/30 | 0.567 | >0.5，强 systematic collapse，支持 H1 | `{'action': 12, 'interest': 17, 'attention': 1}` |
| Dim 2 intent | confirm_choice | 28/30 | 0.933 | >0.5，强 systematic collapse，支持 H1 | `{'confirm_choice': 28, 'explore_options': 1, 'seek_reassurance': 1}` |
| Dim 3 next_state | attention | 31/80 | 0.388 | 0.3-0.5，混合模式 | `{'desire': 30, 'attention': 31, 'interest': 17, 'action': 2}` |

解读：Dim 1 和 Dim 2 都有明显集中预测。Dim 1 主要集中到 `interest`，但也大量预测 `action`；Dim 2 几乎坍塌到 `confirm_choice`。Dim 3 则没有单一类超过 0.5，更像混合错误而不是单点坍塌。

## 3. Train vs Test 对比状态

| 项目 | 状态 |
| --- | --- |
| Stage-1 user_intent train 文件 | `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl`，可读 493 条 |
| Stage-1 next_state train 文件 | `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl`，可读 1816 条 |
| seed=42 user_intent probe | `reports/representation_collapse_probe_20260524/stage1_train_user_intent_seed42_30.jsonl`，30 条 |
| seed=42 next_state probe | `reports/representation_collapse_probe_20260524/stage1_train_next_state_seed42_30.jsonl`，30 条 |
| PIWM 主模型 train-subset inference | 未执行：当前无可用 GPU；不能用 CPU 慢跑伪造时限内结果 |

已知 target test 分数：

| 维度 | Target test macro F1 |
| --- | ---: |
| Dim 1 AIDA | 0.264 |
| Dim 2 intent core | 0.074 |
| Dim 3 next_state | 0.190 |

由于 train-subset inference 未执行，H2 vs H3 不能在本轮给最终判定。需要在任一 GPU 开机后，对上述两个 probe JSONL 跑同一 evaluation pipeline。

## 4. 对三个假设的当前证据

| 假设 | 当前证据 | 当前判断 |
| --- | --- | --- |
| H1 Internalized/systematic collapse | Dim 1 modal concentration=0.567；Dim 2 modal concentration=0.933；raw output 合法但偏向 `confirm_choice` | 强支持，尤其 Dim 2 |
| H2 Catastrophic forgetting | Sanity check 已显示 PIWM 在 target Dim1 低于 Stage-1；但还没有 PIWM 在 Stage-1 train subset 上的数字 | 可疑但未闭合 |
| H3 Distribution shift | 需要 train subset vs target test gap；本轮缺 GPU，不能定量 | 未闭合 |

## 5. 下一步最小 GPU 任务

开任一 GPU 后，只需要跑以下最小任务，不需要重训：

1. 用 PIWM 主模型 checkpoint 对 `stage1_train_user_intent_seed42_30.jsonl` 推理，评分 Dim 1/2。
2. 用 PIWM 主模型 checkpoint 对 `stage1_train_next_state_seed42_30.jsonl` 推理，评分 Dim 3。
3. 可选：用 Stage-1 checkpoint 对同两份 probe 推理，和 PIWM 主模型对比。

判定规则保持原任务定义：train 也低则 H2 主导；train 显著高于 target 则 H3 主导；中间为混合。

## 6. 明确总结

主要机制当前已能确认的是 **H1：systematic representation collapse**，证据是 Dim 1 `interest` 预测占 0.567、Dim 2 `confirm_choice` 预测占 0.933，且 parse rate 已在上一轮 sanity check 排除 parser 问题。H2/H3 需要 train-subset inference 才能区分；本轮因 GPU 已关或无卡，不能给最终定量。对论文 Analysis section 的含义是：当前 PIWM 的动作选择能力强，但中间 state/intent 表征存在系统性坍塌，不能把模型叙述成完整可靠的显式四步 reasoning chain。
