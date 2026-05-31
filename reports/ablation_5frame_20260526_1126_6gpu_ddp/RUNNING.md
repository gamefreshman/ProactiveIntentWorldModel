# 5-Frame Ablation 6-GPU DDP Run

Date: 2026-05-26

Status: completed after juwei evaluation resume.

## Input Data

- Train JSONL: `data/ablation_5frame/piwm_train_stage1_plus_stage2_target_v2_balanced.5frame.server_resolved.jsonl`
- Validation JSONLs:
  - `data/ablation_5frame/piwm_train_stage1_user_intent_val_v1.5frame.jsonl`
  - `data/ablation_5frame/piwm_train_stage1_next_state_prediction_val_v1.5frame.jsonl`
- Data build: 2734/2734 train rows, 50/50 and 185/185 validation rows, `image_count=5`, no skipped rows.

## Launch Configuration

- GPUs: 0,1,2,3,4,5
- Launcher: `torch.distributed.run --nproc_per_node 6`
- Checkpoint root: `checkpoints/ablation_5frame_20260526_1126_6gpu_ddp/`
- Training log: `logs/batch2_ablation_20260526_1126_6gpu_ddp/5frame.log`
- Eval waiter log: `logs/batch2_ablation_20260526_1126_6gpu_ddp/5frame_eval_waiter.log`
- `per_device_train_batch_size=2`
- `gradient_accumulation_steps=1`
- Effective global batch: 12

## Notes

- This replaces the interrupted 2-GPU retry (`20260526_0710`) and the aborted non-DDP 6-GPU launch (`20260526_1121_6gpu`).
- Exact original effective global batch 16 is not representable with 6 GPUs and integer gradient accumulation. This run uses global batch 12 to satisfy PI's instruction to utilize all six A100 GPUs.
- Startup verification at 2026-05-26 11:30 CST: `world_size=6`, step `5/684`, no CUDA OOM, all six GPUs at 100% utilization.
- Monitoring at 2026-05-26 13:13 CST: step `330/684`, no CUDA OOM, no checkpoint yet, all six GPUs active.

## Last Confirmed State Before Server Access Loss

- Training completed at `684/684` with no CUDA OOM.
- `checkpoint-500` and `checkpoint-684` were confirmed on the remote server.
- The automatic evaluator started from `checkpoint-684` and reached at least Cross-Domain oracle plus user-intent evaluation before SSH access became unavailable.
- Final A100 access was lost before E2E evaluation completed.

## Completion After A100 Credit Exhaustion

- The checkpoint adapter, base model, evaluation frames, and existing A100 raw outputs were copied to juwei.
- The remaining 30-sample E2E evaluation was split into two shards:
  - shard 0: `GPU0`, target rows 1-15
  - shard 1: `GPU1+GPU2`, target rows 16-30
- The shard outputs were merged into `summary.json`.

## Final Metrics

| Metric | Value |
|---|---:|
| Target-Test F1 | 0.627 |
| Cross-Domain F1 | 0.770 |
| E2E F1 | 0.234 |
| AIDA F1 | 0.412 |
| Intent F1 | 0.115 |
| Next-State F1 | 0.222 |
| E2E Step 1 parse | 1.000 |
| E2E Step 2 parse | 0.867 |
