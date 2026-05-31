本报告 5-act = Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入 operational 输出。

# Path C probe with stage-conditioned candidates

## Executive verdict

Path C checkpoint **不能直接作为 Stage-2 启动依据**。在新的 stage-conditioned candidate policy 下，修复评估器逐样本候选校验后，30 条 balanced target test 的 strict macro F1 只有 **0.227**，低于新的 random-candidate baseline **0.414**，差值 **-0.187**。

只看可解析的 26 条，parsed-only macro F1 也只有 **0.240**，仍低于 random baseline，差值 **-0.173**。

这说明之前 all-5-act candidate probe 的 `0.438` 不能再作为健康信号使用。切换到 stage-conditioned candidates 后，Path C 的 target action selection 表现变成 **低于随机候选基线**。

## Run setup

Checkpoint:

```text
/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432
```

Model:

```text
/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct
```

Input:

```text
data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection_stage_conditioned_server_resolved.jsonl
```

This is a server-resolved copy of the local stage-conditioned eval file. The local source file is:

```text
data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl
sha256=a4c3de07178961be5cd7b519d223c369686ddf7933be35cb7217c5a3fb0194c4
```

The server-resolved copy only changes image paths from macOS absolute paths to `/root/lanyun-fs/ProactiveIntentWorldModel/...`.

Raw output after parser valid-actions fix:

```text
data/piwm_results/domain_specialization_eval/pathC_probe_stage_conditioned_parserfix.json
sha256=56b018f3cb32040bf4ba6019091d154adc7ff25f26c9ab50caed28ad798afcc0
```

Parser fix note: the first run incorrectly treated 3 generated stage-conditioned candidate keys as invalid because the evaluator did not pass each row's `meta.candidate_action_acts` into `parse_action_output`. The evaluator has now been corrected to validate against the row-local candidate list.

Command:

```bash
cd /root/lanyun-fs/ProactiveIntentWorldModel
/root/lanyun-fs/venvs/piwm-train-fast/bin/python scripts/eval_ms_swift_checkpoint.py \
  --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct \
  --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432 \
  --eval-label pathC_probe_stage_conditioned_parserfix \
  --input-jsonl data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection_stage_conditioned_server_resolved.jsonl \
  --out data/piwm_results/domain_specialization_eval/pathC_probe_stage_conditioned_parserfix.json \
  --max-new-tokens 256 \
  --image-limit 3 \
  --max-pixels 1003520 \
  --torch-dtype bfloat16 \
  --device-map auto \
  --progress-every 1 \
  --partial-out-every 5
```

## Candidate policy check

Gold distribution remains balanced:

| Act | Count |
|---|---:|
| Greet | 6 |
| Elicit | 6 |
| Inform | 6 |
| Recommend | 6 |
| Hold | 6 |

AIDA stage distribution:

| Stage | Count |
|---|---:|
| attention | 3 |
| interest | 10 |
| desire | 11 |
| action | 6 |

Gold act by stage:

| Stage | Greet | Elicit | Inform | Recommend | Hold |
|---|---:|---:|---:|---:|---:|
| attention | 0 | 3 | 0 | 0 | 0 |
| interest | 0 | 3 | 3 | 0 | 4 |
| desire | 0 | 0 | 3 | 6 | 2 |
| action | 6 | 0 | 0 | 0 | 0 |

The candidate acts are stage-conditioned and contain no Reassure. Candidate instance counts vary because some stages can include multiple parameterized instances of the same act.

## Main metrics

| Metric | Value |
|---|---:|
| n_records | 30 |
| parse_success | 26 |
| parse_rate | 0.867 |
| strict all-row accuracy | 0.267 |
| strict all-row macro F1 | 0.227 |
| parsed-only accuracy | 0.308 |
| parsed-only macro F1 | 0.240 |
| random-candidate baseline macro F1 | 0.414 |
| strict delta vs random | -0.187 |
| parsed-only delta vs random | -0.173 |

## Per-act F1

Strict all-row, parse failures counted as wrong:

| Act | Support | Pred count | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Greet | 6 | 0 | 0.000 | 0.000 | 0.000 |
| Elicit | 6 | 1 | 1.000 | 0.167 | 0.286 |
| Inform | 6 | 5 | 0.200 | 0.167 | 0.182 |
| Recommend | 6 | 2 | 0.500 | 0.167 | 0.250 |
| Hold | 6 | 18 | 0.278 | 0.833 | 0.417 |

Parsed-only:

| Act | Support | Pred count | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Greet | 5 | 0 | 0.000 | 0.000 | 0.000 |
| Elicit | 6 | 1 | 1.000 | 0.167 | 0.286 |
| Inform | 3 | 5 | 0.200 | 0.333 | 0.250 |
| Recommend | 6 | 2 | 0.500 | 0.167 | 0.250 |
| Hold | 6 | 18 | 0.333 | 1.000 | 0.500 |

## Prediction pattern

Strict prediction counts:

| Predicted act | Count |
|---|---:|
| Hold | 18 |
| Inform | 5 |
| parse_error | 4 |
| Recommend | 2 |
| Elicit | 1 |
| Greet | 0 |

The same two problems remain:

1. **Greet is never predicted.** All 6 gold Greet rows are missed.
2. **Hold is overpredicted.** Hold is predicted 18 times for only 6 gold Hold rows.

The stage-conditioned candidate set did not fix these two behaviors. It made the comparison cleaner, but it also showed that Path C is below the random baseline under the new candidate policy.

## Parse errors

After the parser valid-actions fix, 4 rows failed parsing:

| Row | source_id | Gold | Error summary |
|---:|---|---|---|
| 9 | target_piwm_708 | Inform | missing `intervention_utterance` closing tag |
| 10 | target_piwm_712 | Inform | missing `intervention_utterance` closing tag |
| 11 | target_piwm_713 | Inform | missing `intervention_utterance` closing tag |
| 13 | target_piwm_718 | Greet | malformed `rationale` closing tag (`</rationationale>`) |

The remaining errors are real structured-output failures. Three earlier invalid-candidate errors were evaluation artifacts and are not counted here after the row-local candidate validation fix.

## Interpretation

The Stage-2 launch condition is **not satisfied** under the corrected stage-conditioned comparison.

The previous optimistic signal:

```text
all-5-act quick probe macro F1 = 0.438
old random baseline = 0.281
```

is not comparable to the current stage-conditioned setting.

The corrected comparison is:

```text
stage-conditioned quick probe strict macro F1 = 0.227
stage-conditioned random baseline macro F1 = 0.414
delta = -0.187
```

Therefore, launching A0-A4 now would likely produce noisy or misleading results. The immediate bottleneck is not just target data size; it is that the current Path C checkpoint is still biased toward Hold and cannot select Greet.

## Recommended next action

Do not start Stage-2 main ablations yet.

Minimum next fixes before Stage-2:

1. Run a prompt-format repair pass for action selection so the model always copies one exact candidate key from the candidate list.
2. Add an inference-time or training-time anti-collapse mechanism for Hold.
3. Add a targeted Greet-recognition probe or small Greet-specific adaptation check, because current Greet F1 is still 0.
4. Re-run this exact stage-conditioned probe after the fix. Stage-2 should start only if strict macro F1 is clearly above random baseline or if PI explicitly decides to proceed despite this result.

