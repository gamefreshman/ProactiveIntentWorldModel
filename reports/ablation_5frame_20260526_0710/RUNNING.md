# 5-Frame Ablation Retry

Date: 2026-05-26

## Input Data

- Train JSONL: `data/ablation_5frame/piwm_train_stage1_plus_stage2_target_v2_balanced.5frame.server_resolved.jsonl`
- Validation JSONLs:
  - `data/ablation_5frame/piwm_train_stage1_user_intent_val_v1.5frame.jsonl`
  - `data/ablation_5frame/piwm_train_stage1_next_state_prediction_val_v1.5frame.jsonl`
- Data build: 2734/2734 train rows, 50/50 and 185/185 validation rows, `image_count=5`, no skipped rows.

## Retry Configuration

- GPUs: 4,5
- Checkpoint root: `checkpoints/ablation_5frame_20260526_0710/`
- Training log: `logs/batch2_ablation_20260526_0710/5frame.log`
- Eval waiter log: `logs/batch2_ablation_20260526_0710/5frame_eval_waiter.log`
- Change from unchanged-hyperparameter OOM attempt:
  - `per_device_train_batch_size=2`
  - `gradient_accumulation_steps=4`
- Rationale: keep effective global batch close to the original 2-GPU ablation setting while reducing per-GPU memory enough for five image frames.

## Current Monitoring Note

- At 2026-05-26 11:08 CST, training was at 185/513 with no CUDA OOM in the retry log.
- GPUs 0-3 became free after no-BDI/no-evidence evaluation completed. I did not launch a second 5-frame run on those GPUs because it would create duplicate 5-frame provenance with only marginal expected wall-time gain.

## Superseded

- At 2026-05-26 11:20 CST, PI approved switching the current 5-frame run to 6 GPUs.
- This 2-GPU run was stopped at approximately 195/513 before any checkpoint was written (`save_steps=500`), so it is not used for paper results.
