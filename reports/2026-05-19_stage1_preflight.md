本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Stage-1 Training Preflight

## Impact Estimate Before Execution

This task only checks launch readiness. It does not start training and does not commit.

Commands run:

```bash
python3 -m pytest piwm_data/tests/test_5act_invariant.py
bash scripts/train/stage1_train.sh
```

Remote server checks were attempted but did not complete because SSH closed the connection.

## Stage-1 Combined JSONL

| Field | Value |
|---|---|
| path | `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` |
| total rows | 2544 |
| task counts | `user_intent=543`, `next_state_prediction=2001` |
| mtime | `2026-05-20 14:19:08 CST` |
| sha256 | `68f37965030cf7cb4fa79ee25da7259d42d11b47d1200b19392948aebd6093a7` |

## Actual Files Used by `stage1_train.sh`

The launch script does not directly train on the combined JSONL. It uses four split files:

| File | Rows | mtime | sha256 |
|---|---:|---|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | `2026-05-19 21:29:27 CST` | `9e98a875906efc909ddaea3a6342f8ea42ab63342189f52d76e2eccd363a699f` |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | `2026-05-19 21:29:28 CST` | `e6acf951a22593f05f15b1981407ec49a07e5da45a93e4315e081cefb0be30b1` |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | `2026-05-19 21:29:27 CST` | `34bac504a3498e57bbfb5e6e9f1e1ccb7b2fee55c6d7dde52f291b0e6e4ea3d0` |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | `2026-05-19 21:29:28 CST` | `3a2fc367461e1df6327ca48b3af30b2ef47c581b70d6cde4ffd7318a9abbdd31` |

Important warning:

```text
These four split files have mtime earlier than the 5-act rollback report timestamp.
```

They are Stage-1 state/world-model files and do not contain action-selection 5-act candidates, but this mtime should be explicitly accepted by PI or the split files should be regenerated before training.

## Stage-1 Training Script

| Field | Value |
|---|---|
| path | `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/train/stage1_train.sh` |
| repo HEAD | `7b6b58d6c0d2a63fbcdcc5307c7e4bcc1ff995f4` |
| tracked in HEAD | no; currently untracked |
| mtime | `2026-05-19 21:46:02 CST` |
| sha256 | `cf3c4443027eff8d7b54195ea38fb0dc4201ca55fb43d8f3d19fce58525557f0` |
| diff vs HEAD | not applicable because the file is untracked |

## ms-swift 4.1.3 Path

Requested server path:

```text
/root/lanyun-fs/venvs/piwm-train-fast/bin/swift
```

Status:

```text
not confirmed in this run
```

Reason:

```text
ssh -p 37150 root@qhdlink.lanyun.net closed the connection during password-based check.
```

Local `/usr/bin/swift` exists, but that is Apple Swift, not ms-swift.

## Qwen2.5-VL-7B Weights

Local Mac search result:

```text
No Qwen2.5-VL-7B / Qwen2.5-VL-7B-Instruct directory found under /Users/mutsumi with maxdepth 6.
```

Server result:

```text
not confirmed because SSH connection closed.
```

Current launch config uses:

```text
MODEL_ID=Qwen/Qwen2.5-VL-7B-Instruct
```

If the server has no cached model, ms-swift will need to download it or the path must be overridden with `MODEL_ID=/path/to/local/model`.

## 5-act Invariant Test

Command:

```bash
python3 -m pytest piwm_data/tests/test_5act_invariant.py
```

Result:

```text
4 passed
```

## Dry-run Launch Command

Command:

```bash
bash scripts/train/stage1_train.sh
```

Result:

```text
Dry-run only. Re-run with --run to start training.
```

Resolved dry-run configuration:

```text
MODEL_ID=Qwen/Qwen2.5-VL-7B-Instruct
SWIFT_BIN=swift
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
NPROC_PER_NODE=8
ACT_BALANCING=none
TRAIN=data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl,data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
VAL=data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl,data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
OUTPUT_DIR=checkpoints/stage1_qwen25vl_7b_v1
LOG_DIR=logs/stage1_qwen25vl_7b_v1
```

Full command:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 NPROC_PER_NODE=8 swift sft --model Qwen/Qwen2.5-VL-7B-Instruct --dataset data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl,data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl --val_dataset data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl,data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl --output_dir checkpoints/stage1_qwen25vl_7b_v1 --train_type lora --lora_rank 16 --lora_alpha 32 --target_modules all-linear --learning_rate 2e-5 --num_train_epochs 3 --per_device_train_batch_size 4 --per_device_eval_batch_size 4 --gradient_accumulation_steps 2 --max_length 4096 --torch_dtype bfloat16 --gradient_checkpointing true --logging_dir logs/stage1_qwen25vl_7b_v1
```

## Estimated Runtime and Outputs

Script header estimate:

```text
4-6 hours on 8 x RTX 4090 24GB
```

Checkpoint output path:

```text
checkpoints/stage1_qwen25vl_7b_v1
```

Log path:

```text
logs/stage1_qwen25vl_7b_v1/train.log
```

## Go / No-go

No-go until PI acknowledges:

1. the split-file mtime warning;
2. server ms-swift path could not be confirmed;
3. server/local Qwen2.5-VL-7B weights could not be confirmed.

