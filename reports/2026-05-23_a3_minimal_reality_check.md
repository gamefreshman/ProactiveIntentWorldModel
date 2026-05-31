5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入 operational training/eval/inference/runtime。

# A3_minimal Reality Check Report

## Verdict

**综合判定：not viable as main run。**

A3_minimal 比 Path C probe 有明显提升，但没有超过 random-candidate baseline，而且最关键的 `Greet` 仍然没有命中：`Greet F1=0.000`。它说明混合数据方向有帮助，但不能直接作为主实验结论。

## Training Setup

- Stage-1 backbone:
  `/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432`
- A3_minimal checkpoint:
  `/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_minimal_qwen25vl_7b_a100_2gpu_v1/a3min-20260522-170732-px1003520-venvshim2/v0-20260522-170817/checkpoint-164`
- Adapter SHA256:
  `b5e43415755bd552d4aa5d0ca709cc23f98e8d075c6f1c1ec73857117a1db467`
- Training data:
  `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_a3_minimal_20260523/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2.jsonl`
- Training data SHA256:
  `a4f14429e45152992e404fd11497beaed90408dc0005e9efec700a2008444a9b`
- Rows: 2630 total = 543 `user_intent` + 2001 `next_state_prediction` + 86 `action_selection_5act`
- Epoch: 1
- Target repeat: 1
- LoRA: same as Path C (`rank=16`, `alpha=32`, `target_modules=all-linear`, `lr=2e-5`)
- Final training eval loss: `0.01564447`
- Final training eval token accuracy: `0.99420843`

Note: remote ms-swift/PEFT environment required a local venv compatibility shim for `transformers.integrations.tensor_parallel.ALL_PARALLEL_STYLES`; this changed only the remote Python environment, not repo code.

## Evaluation Inputs

- Stage-conditioned eval:
  `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl`
- All-5 explicit eval:
  `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection_all5_explicit.server_resolved.jsonl`
- Target test distribution:
  `Greet=6 / Elicit=6 / Inform=6 / Recommend=6 / Hold=6`

## Headline Results

| Eval config | Parse | Strict macro F1 | Parsed macro F1 | Greet F1 | Hold F1 | Hold pred_count | Compare |
|---|---:|---:|---:|---:|---:|---:|---|
| stage-conditioned, Hold prior λ=0.0 | 29/30 | 0.384 | 0.390 | 0.000 | 0.471 | 11 | best A3_minimal |
| stage-conditioned, Hold prior λ=1.0 | 28/30 | 0.361 | 0.374 | 0.000 | 0.400 | 9 | calibration hurts macro F1 |
| all-5-act sanity | 29/30 | 0.311 | 0.316 | 0.000 | 0.375 | 10 | worse than stage-conditioned |

Baselines:
- Path C probe parserfix: `0.227 strict / 0.240 parsed`
- Random-candidate baseline: `0.414`

Interpretation:
- A3_minimal improves over Path C by about `+0.157 strict` and `+0.150 parsed`.
- But the best A3_minimal setting (`0.390 parsed`) is still below random baseline (`0.414`).
- Greet is no longer absent from predictions, but all predicted Greet cases are wrong, so `Greet F1=0.000`.
- Hold overprediction is reduced relative to the old Path C pattern, but still high: best setting predicts Hold 11 times for only 6 gold Hold rows.

## Per-Act F1

| Eval config | Greet | Elicit | Inform | Recommend | Hold |
|---|---:|---:|---:|---:|---:|
| stage-conditioned, λ=0.0 strict | 0.000 | 0.545 | 0.462 | 0.444 | 0.471 |
| stage-conditioned, λ=0.0 parsed | 0.000 | 0.545 | 0.462 | 0.444 | 0.500 |
| stage-conditioned, λ=1.0 strict | 0.000 | 0.545 | 0.462 | 0.400 | 0.400 |
| stage-conditioned, λ=1.0 parsed | 0.000 | 0.545 | 0.462 | 0.400 | 0.462 |
| all-5 explicit strict | 0.000 | 0.167 | 0.615 | 0.400 | 0.375 |
| all-5 explicit parsed | 0.000 | 0.167 | 0.615 | 0.400 | 0.400 |

## Prediction Counts

| Eval config | Greet | Elicit | Inform | Recommend | Hold | Parse error |
|---|---:|---:|---:|---:|---:|---:|
| stage-conditioned, λ=0.0 | 3 | 5 | 7 | 3 | 11 | 1 |
| stage-conditioned, λ=1.0 | 3 | 5 | 7 | 4 | 9 | 2 |
| all-5 explicit | 2 | 6 | 7 | 4 | 10 | 1 |

## Parse Errors

- stage-conditioned λ=0.0:
  - `target_piwm_811`: missing `intervention_utterance` tag.
- stage-conditioned λ=1.0:
  - `target_piwm_811`: missing `intervention_utterance` tag.
  - `target_piwm_812`: generated `Hold`, but the valid candidate labels are exact candidate ids, not bare act names.
- all-5 explicit:
  - `target_piwm_817`: missing `rationale` tag.

## Diagnosis

1. Mixed data helps: the model is no longer fully stuck in the old Path C behavior, and macro F1 improves by roughly 0.15.
2. Mixed data does not solve `Greet`: the model predicts Greet a few times, but never on the correct six Greet rows.
3. Hold prior λ=1.0 is not useful here: it reduces Hold pred_count from 11 to 9, but also lowers macro F1 and parse rate.
4. Stage-conditioned candidate lists help more than all-5 candidate lists: all-5 sanity drops to 0.316 parsed macro F1.

## Recommendation

Do not promote A3_minimal as the main result. Use it as a diagnostic checkpoint only.

Next useful options:
- Debug Greet rows specifically: compare the six gold Greet rows against the three false-positive Greet predictions.
- Add Greet-focused contrastive negatives before running full A0-A4.
- Keep stage-conditioned candidates for target eval; all-5 candidate setting is a useful sanity check but not the best operational mode.
- Do not use Hold prior λ=1.0 by default for this checkpoint.

## Remote Result Files

- `/root/lanyun-fs/ProactiveIntentWorldModel/reports/a3_minimal_20260523/stage_conditioned_lambda0.json`
  - SHA256 `dd7ae1276fea38d8d57abc54edb1618b72e625762850b96d0e3bf981f26a4f71`
- `/root/lanyun-fs/ProactiveIntentWorldModel/reports/a3_minimal_20260523/stage_conditioned_lambda1.json`
  - SHA256 `1b5cb1f7324807caff7878bbe31da84fa2b78650a8782bee986c5ccff23572ee`
- `/root/lanyun-fs/ProactiveIntentWorldModel/reports/a3_minimal_20260523/all5_explicit.json`
  - SHA256 `61d399d2377c9909e1a892c4470cc8b1102c7f00b1f22b6fec464ffd996d73cf`

