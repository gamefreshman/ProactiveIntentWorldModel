5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# Trick 6 Inference-Time Counterfactual Planning

## 一句话结论

Trick 6 最好版本为 Reward B，macro F1=0.360，相对 direct 0.641 下降 -0.281。

## Run Config

- 方法：枚举 stage-conditioned candidates，逐候选预测 next-state，再按 reward argmax 选动作。
- Reward A：AIDA stage advance，推进 +1，持平 0，退步 -1。
- Reward B：优先使用模型输出的 reward 字段；缺失时 fallback 到 Reward A。
- Tie-break：reward 相同时按候选列表原始顺序。
- Parse error：该候选 reward=-inf；若全候选失败，则 fallback direct action inference。

## 主结果

| Method | Macro F1 | Accuracy | Candidate parse rate | Per-act F1 |
| --- | ---: | ---: | ---: | --- |
| PIWM direct | 0.641 | 0.679 | 0.933 | 见既有主结果 |
| PIWM + Trick 6 reward A | 0.263 | 0.300 | 0.879 | Greet=0.286, Elicit=0.444, Inform=0.250, Recommend=0.000, Hold=0.333 |
| PIWM + Trick 6 reward B | 0.360 | 0.333 | 0.879 | Greet=0.286, Elicit=0.333, Inform=0.545, Recommend=0.444, Hold=0.190 |

## Per-act Detail

### Reward A

| Act | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 0.286 | 1.000 | 0.167 | 6 | 1 |
| Elicit | 0.444 | 0.667 | 0.333 | 6 | 3 |
| Inform | 0.250 | 0.500 | 0.167 | 6 | 2 |
| Recommend | 0.000 | 0.000 | 0.000 | 6 | 0 |
| Hold | 0.333 | 0.208 | 0.833 | 6 | 24 |

### Reward B

| Act | F1 | Precision | Recall | Support | Pred count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greet | 0.286 | 1.000 | 0.167 | 6 | 1 |
| Elicit | 0.333 | 0.333 | 0.333 | 6 | 6 |
| Inform | 0.545 | 0.600 | 0.500 | 6 | 5 |
| Recommend | 0.444 | 0.667 | 0.333 | 6 | 3 |
| Hold | 0.190 | 0.133 | 0.333 | 6 | 15 |

## 失败 Case 分析

- Reward A: 错误 21/30；其中 chosen candidate parse failure 相关 1 条。
- Reward B: 错误 20/30；其中 chosen candidate parse failure 相关 1 条。

## 论文建议

建议论文 main result 继续使用 direct action selection；Trick 6 可作为 decision-time planning ablation 或 future work。

