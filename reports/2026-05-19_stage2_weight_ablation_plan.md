本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Stage-2 Target Weight Ablation Plan

## Impact Estimate Before Execution

This is a plan-only task. No training was started and no dataset was modified.

Expected future touched files if PI approves:

- Training configs or launch scripts for Stage-2 / joint training.
- Result logs under `logs/` and checkpoints under `checkpoints/`.
- Evaluation summaries under `data/piwm_results/` or `reports/`.

## Ablation Setting

Problem:

```text
Stage-2 target train = 71 action-selection rows
Stage-1 general = 2544 rows
```

If mixed naively, target examples can be overwhelmed by the general corpus.

Lightweight ablation:

| Run | Target weight | Stage-1 checkpoint | Stage-2 data | Purpose |
|---|---:|---|---|---|
| W1 | 1 | state+transition checkpoint | general policy/action + target 71 | Unweighted baseline |
| W4 | 4 | state+transition checkpoint | general policy/action + target 71 | Mild target upweight |
| W8 | 8 | state+transition checkpoint | general policy/action + target 71 | Medium target upweight |
| W16 | 16 | state+transition checkpoint | general policy/action + target 71 | Strong target upweight |

This ablation belongs under A4, not A0-A3.

## Metrics

Primary metric on the 30-record balanced target test:

- 5-act macro F1
- per-class F1:
  - `Greet`
  - `Elicit`
  - `Inform`
  - `Recommend`
  - `Hold`

Priority diagnostics:

- `Greet F1`: whether the model learns proactive opening/closing behavior from target data.
- `Hold F1`: whether the model learns non-intervention/go-no-go behavior.
- General QA score after Stage-2: check whether target weighting causes forgetting.

## Expected Runtime

Stage-1 full training script estimates `4-6 hours` on 8 x RTX 4090 for the current Stage-1 setup.

Stage-2 target adaptation should be much shorter because the target set is only 71 rows. Conservative estimate:

```text
single Stage-2 LoRA run: ~0.5-1.5 hours
4 weights x single run: ~2-6 hours total
```

This is an estimate, not a measured result. Actual runtime depends on image decoding, remote disk throughput, ms-swift version, and whether the run starts from a local cached Qwen2.5-VL-7B checkpoint.

## Execution Gate

Do not start these runs until PI confirms:

1. whether A4 should mix general policy/action rows or use target-only weighted oversampling;
2. whether `weight=16` is acceptable or should be replaced by a smaller upper bound such as `12`;
3. whether general QA forgetting check must run after every weight or only after the best target result.

