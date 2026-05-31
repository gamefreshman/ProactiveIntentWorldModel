本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

# Path C Claude Prerequisite Actions

## Verdict

Claude 第二轮反馈中的 Stage-2 前置条件已完成到可复核状态，但还没有启动任何 Stage-2 main experiment。

已完成：

1. `Greet` augmentation 从 v1 的 40 条降到 v2 的 15 条。
2. Stage-2 action-selection candidate list 已改为 AIDA stage-conditioned。
3. Stage-2 eval/inference 已加入 Hold prior calibration 参数和 runtime 钩子。
4. A4 weighted target entrypoint 已生成，target repeat = 8。
5. 30 条 balanced target test 仍是 `qa_reviewed_pass`，没有被 build 重置回 pending。
6. operational output 中 `Reassure=0`。

尚未完成：

1. 3 条 Path C quick probe parse-error 原始输出没有取回；SSH 二次尝试被远端关闭。
2. Stage-2 A0-A4 尚未启动，等待 Claude/PI 对本报告下一步确认。

## 1. Greet Augmentation v2

Claude 指出 v1 的 `Greet=51 / Hold=0` 过度倾斜，因此本轮把 augmentation count 从 40 改为 15，并保留 v1 作为 audit artifact。

当前推荐入口：

```text
data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl
```

统计：

| Item | Value |
|---|---:|
| rows | 86 |
| canonical target rows | 71 |
| synthetic Greet augmentation rows | 15 |
| sha256 | `ee9fac6411a60234aaac36bae01ec9e8926ab42001bf34e1418804161af421fa` |

Best-act distribution:

| act | count |
|---|---:|
| `Inform` | 41 |
| `Greet` | 26 |
| `Elicit` | 14 |
| `Recommend` | 5 |
| `Hold` | 0 |

QA status:

| status | count |
|---|---:|
| `synthetic_unreviewed` | 71 |
| `synthetic_augmented_unreviewed` | 15 |

Interpretation: this is a training patch only. The 15 Greet rows are not target-frontcam QA-reviewed test data.

## 2. Stage-Conditioned Candidate Lists

The global 5-act definition did not change. Only per-stage candidate exposure changed.

| AIDA stage | Candidate acts |
|---|---|
| `attention` | `Greet / Elicit / Inform / Hold` |
| `interest` | `Elicit / Inform / Recommend / Hold` |
| `desire` | `Inform / Recommend / Hold` |
| `action` | `Greet / Recommend / Hold` |

Current Stage-2 v2 candidate-size distribution:

| dataset | candidate sizes |
|---|---|
| Stage-2 GreetAug-v2 train | `{4: 64, 3: 22}` |
| Target 30 action eval | `{4: 13, 3: 17}` |

Best action is inside the candidate set for every Stage-2 train/eval row.

## 3. Hold Prior Calibration

Claude said prompt guardrail alone was not enough because Path C quick probe over-predicted `Hold` (`16/30`) while the balanced test prior is `6/30`.

Implemented in:

- `scripts/eval_ms_swift_checkpoint.py`
  - adds generation-time candidate-token bias via:
    - `--hold-prior-lambda`
    - `--hold-prior-target`
    - `--hold-prior-observed`
  - formula: subtract `lambda * log(observed_hold_prior / target_hold_prior)` from Hold candidate-label token logits.
- `piwm_infer/decision_loop.py`
  - adds runtime Hold prior calibration hook.
  - default is disabled (`hold_prior_lambda=0.0`) so old behavior is unchanged unless explicitly enabled.
- `piwm_infer/tests/test_decision_loop.py`
  - adds coverage that over-predicted Hold can be demoted under calibration.

Planned eval sweep:

```text
lambda = 0.5 / 1.0 / 1.5
target_hold_prior = 0.2
observed_hold_prior = 16/30
```

This is an inference-time mitigation, not a fix for missing natural Hold rows in Stage-2 train.

## 4. A4 Targetx8 Entry Point

Generated A4 weighted adaptation candidate:

```text
data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl
```

Stats:

| Item | Value |
|---|---:|
| rows | 3232 |
| Stage-1 rows | 2544 |
| action_selection_5act rows | 688 |
| target repeat | 8 |
| sha256 | `e2c2879fe04371a4cdfefda241e1dc9b8f3af769286ae9d2c12c51bc50418824` |

Repeated target rows are training weight, not new unique videos.

## 5. Target Eval Status

Current action-selection eval:

```text
data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl
```

Stats:

| Item | Value |
|---|---:|
| rows | 30 |
| sha256 | `a4c3de07178961be5cd7b519d223c369686ddf7933be35cb7217c5a3fb0194c4` |
| QA status | `qa_reviewed_pass=30` |
| `Reassure` rows | 0 |
| best missing from candidates | 0 |

Best-act distribution:

| act | count |
|---|---:|
| `Greet` | 6 |
| `Elicit` | 6 |
| `Inform` | 6 |
| `Recommend` | 6 |
| `Hold` | 6 |

All eval rows:

```text
data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl
```

Stats:

| Item | Value |
|---|---:|
| rows | 90 |
| sha256 | `9c922d5969b9dbbe8a6ddc5a8eb70350576788a8dc88f7b9ede138f633846335` |
| QA status | `qa_reviewed_pass=90` |

## 6. Baselines After Stage-Conditioned Candidates

Command:

```bash
python3 -m scripts.run_action_selection_baselines
```

Output summary:

| Baseline | Action accuracy | Macro F1 |
|---|---:|---:|
| always-Greet | 0.200 | 0.067 |
| always-Elicit | 0.200 | 0.067 |
| always-Inform | 0.200 | 0.067 |
| always-Recommend | 0.200 | 0.067 |
| always-Hold | 0.200 | 0.067 |
| random-candidate, seed 42 | 0.433 | 0.414 |

Note: random-candidate increased from the older 0.281 because stage-conditioned candidates shrink the candidate set. This is expected and should be reported with the new candidate policy.

## 7. Parse Error Diagnostics

Claude requested quick diagnosis for:

```text
target_piwm_721
target_piwm_760
target_piwm_813
```

Local structural check:

| state_id | stage | best_act | stage-conditioned candidates |
|---|---|---|---|
| `target_piwm_721` | `action` | `Greet` | `Greet / Recommend / Hold` |
| `target_piwm_760` | `desire` | `Recommend` | `Inform / Recommend / Hold` |
| `target_piwm_813` | `interest` | `Hold` | `Elicit / Inform / Recommend / Hold` |

All three gold labels are valid under the stage-conditioned policy. Therefore the earlier parse errors were likely generation-format errors, not candidate-set mismatch.

Remote raw-output fetch:

```text
ssh -p 14149 root@qhdlink.lanyun.net
```

Result: connection closed by remote host before the raw JSON could be read. Raw parse-error outputs remain pending until remote access is stable.

## 8. Files Updated

Code:

- `scripts/build_two_stage_training_and_eval.py`
  - GreetAug-v2 default count = 15.
  - Stage-conditioned candidate rebuilding.
  - target repeat support for A4.
  - QA status overlay from target `main_schema` so rebuilds do not downgrade reviewed test rows.
- `scripts/eval_ms_swift_checkpoint.py`
  - Hold prior token-bias controls for action-selection generation.
- `piwm_infer/decision_loop.py`
  - runtime Hold prior calibration hook.

Tests:

- `piwm_infer/tests/test_decision_loop.py`
  - added Hold prior calibration test.
- `piwm_data/tests/test_target_frontcam_qa_and_promptready.py`
  - updated expected split diagnostics for stage-conditioned filtering count.

Docs/config:

- `data/official/DATASET_MANIFEST.json`
- `configs/domain_specialization_v1.json`
- `data/official/README.md`
- `docs/current/dataset_inventory.md`
- `docs/current/domain_specialization_experiment_plan.md`

Generated data:

- `data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl`
- `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2.jsonl`
- `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl`
- regenerated `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_*.jsonl` with `qa_reviewed_pass` preserved.

## 9. Validation

Passed:

```bash
python3 -m py_compile scripts/build_two_stage_training_and_eval.py scripts/eval_ms_swift_checkpoint.py piwm_infer/decision_loop.py
python3 -m json.tool data/official/DATASET_MANIFEST.json >/dev/null
python3 -m json.tool configs/domain_specialization_v1.json >/dev/null
python3 -m scripts.check_target_frontcam_split
python3 -m scripts.build_two_stage_training_and_eval --greet-augmentation-count 15 --target-repeat 8
python3 -m scripts.run_action_selection_baselines
python3 -m pytest piwm_data/tests piwm_train/tests piwm_infer/tests
git diff --check
```

Test result:

```text
251 passed
```

## 10. Recommended Next Ask To Claude

Ask Claude to confirm the Stage-2 startup order using:

1. A0 direct Stage-2 only on `piwm_train_stage2_target_5act_greet_aug_v2.jsonl`.
2. A1/A2 Path C-based Stage-2 using the same GreetAug-v2 input.
3. A4 using `piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl`.
4. Eval all target-action checkpoints with Hold prior sweep `lambda=0.5/1.0/1.5`.

No Stage-2 training has been started yet.
