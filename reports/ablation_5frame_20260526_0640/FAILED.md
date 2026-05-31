# 5-Frame Ablation Failure Report

Date: 2026-05-26

## Data Recovery

- Local source videos were synced from `/Users/mutsumi/Desktop/WorkSpace/piwm/data/videos/synth/` to `/root/lanyun-fs/piwm/data/videos/synth/`.
- A100 source-video coverage after sync: 118/118 target videos.
- Rebuilt 5-frame mirror on A100:
  - train: `data/ablation_5frame/piwm_train_stage1_plus_stage2_target_v2_balanced.5frame.server_resolved.jsonl`
  - val user-intent: `data/ablation_5frame/piwm_train_stage1_user_intent_val_v1.5frame.jsonl`
  - val next-state: `data/ablation_5frame/piwm_train_stage1_next_state_prediction_val_v1.5frame.jsonl`
- Build summary: `BUILD_SUMMARY.json`.
- Build result: train 2734/2734 rows, validation 50/50 and 185/185 rows, `image_count=5`, `skipped_rows=0`, `frame_error_count=0`.

## Training Attempt

- Timestamp: `20260526_0640`
- GPUs: 4,5
- Output root: `checkpoints/ablation_5frame_20260526_0640/`
- Log: `5frame.log`
- Hyperparameters: same as PIWM batch-2 ablations; no batch-size or max-pixels changes.

## Failure

Training failed at the first training step with CUDA OOM:

```text
torch.cuda.OutOfMemoryError: CUDA out of memory. Tried to allocate 16.07 GiB.
GPU 1 has a total capacity of 79.25 GiB of which 15.17 GiB is free.
```

Per task constraints, this run was not restarted with changed hyperparameters.
