# 5-Frame 6-GPU Attempt: Aborted Non-DDP Launch

Date: 2026-05-26

This attempt was started after stopping the 2-GPU 5-frame retry, but it did not enter distributed training.

## Diagnosis

- Launch timestamp: `20260526_1121_6gpu`
- Command used the `swift sft` wrapper with `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5`.
- The log showed `world_size=1` and `4101` training steps, meaning it was a single-process launch rather than 6-GPU DDP.
- This run was stopped immediately and is not used for paper results.

## Replacement

The valid replacement run is `reports/ablation_5frame_20260526_1126_6gpu_ddp/`, launched with explicit `torch.distributed.run --nproc_per_node 6`.
