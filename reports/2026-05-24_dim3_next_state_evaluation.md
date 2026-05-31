5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# Dim 3 Next-state Evaluation

## Summary

80 条 covered candidates 上，next-stage macro F1=0.592，strict macro F1=0.559，parse rate=0.887，reward MAE=0.497。

## Metrics

```json
{
  "parse_rate": 0.8875,
  "next_stage_macro_f1": 0.592036568244325,
  "next_stage_strict_macro_f1": 0.5590510366826156,
  "accuracy": 0.647887323943662,
  "reward_mae": 0.49676056338028174,
  "per_candidate_act": {
    "Elicit": {
      "n": 12,
      "macro_f1": 0.1764705882352941,
      "accuracy": 0.5
    },
    "Greet": {
      "n": 6,
      "macro_f1": 0.0,
      "accuracy": 0.0
    },
    "Hold": {
      "n": 33,
      "macro_f1": 0.816323417238749,
      "accuracy": 0.8181818181818182
    },
    "Inform": {
      "n": 21,
      "macro_f1": 0.40705128205128205,
      "accuracy": 0.47619047619047616
    },
    "Recommend": {
      "n": 8,
      "macro_f1": 0.2142857142857143,
      "accuracy": 0.375
    }
  },
  "per_gold_stage": {
    "action": {
      "n": 24,
      "macro_f1": 0.11290322580645161,
      "accuracy": 0.2916666666666667
    },
    "attention": {
      "n": 6,
      "macro_f1": 0.2,
      "accuracy": 0.6666666666666666
    },
    "desire": {
      "n": 19,
      "macro_f1": 0.20312500000000003,
      "accuracy": 0.6842105263157895
    },
    "interest": {
      "n": 31,
      "macro_f1": 0.20754716981132076,
      "accuracy": 0.7096774193548387
    }
  }
}
```

## Coverage Limitation

- scored candidates: 80
- unscored placeholder candidates: 27
- unscored by act: `{'Elicit': 1, 'Greet': 3, 'Inform': 4, 'Recommend': 19}`

27 条无 gold 的候选只用于 Trick 6 planning，不进入 next-stage F1 / reward MAE。

