本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Server Stage-1 Preflight

## Server

SSH:

```text
ssh -p 14149 root@qhdlink.lanyun.net
```

Project path:

```text
/root/lanyun-fs/ProactiveIntentWorldModel
```

Status:

```text
not a git repo
```

This server directory is a data/code working copy, not a full Git checkout.

## Synced Reports

The following local reports were copied to the server:

```text
/root/lanyun-fs/ProactiveIntentWorldModel/reports/2026-05-19_stage1_split_validation.md
/root/lanyun-fs/ProactiveIntentWorldModel/reports/2026-05-19_target_test_stage_act_matrix.md
```

Remote hashes:

```text
bd5297e885533958c046ead97ed073021c77d4eb2b4c1dc88d94d819291fa709  reports/2026-05-19_stage1_split_validation.md
bc5b3482d00de30258711af31304f662e189364bd6b512f9d35a141802a9247e  reports/2026-05-19_target_test_stage_act_matrix.md
```

## Data Files on Server

| File | Rows | sha256 |
|---|---:|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 | `68f37965030cf7cb4fa79ee25da7259d42d11b47d1200b19392948aebd6093a7` |
| `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | 71 | `c9d0d67f35df4f8ce6971b873b40af186a62937713c714b2533a830dc2ea6ddb` |
| `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl` | 30 | `dc7f2a4111645e617ae330ed75c7df74c59775413cab5fa565b78b5692c0c861` |

These match the local hashes checked earlier.

## Stage-1 Split Files on Server

| File | Rows | mtime | sha256 |
|---|---:|---|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | `2026-05-19 21:29:27 CST` | `9e98a875906efc909ddaea3a6342f8ea42ab63342189f52d76e2eccd363a699f` |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | `2026-05-19 21:29:28 CST` | `e6acf951a22593f05f15b1981407ec49a07e5da45a93e4315e081cefb0be30b1` |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | `2026-05-19 21:29:27 CST` | `34bac504a3498e57bbfb5e6e9f1e1ccb7b2fee55c6d7dde52f291b0e6e4ea3d0` |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | `2026-05-19 21:29:28 CST` | `3a2fc367461e1df6327ca48b3af30b2ef47c581b70d6cde4ffd7318a9abbdd31` |

## Python / ms-swift Environment

Python:

```text
/root/lanyun-fs/venvs/piwm-train-fast/bin/python
```

Packages:

```text
ms-swift 4.1.3
modelscope 1.36.3
transformers 4.51.3
torch 2.2.1+cu121
qwen-vl-utils 0.0.14
```

CUDA from torch:

```text
torch.cuda.is_available() = True
torch.cuda.device_count() = 2
torch.cuda.get_device_name(0) = NVIDIA A100-SXM4-80GB
```

Swift entrypoint:

```text
/root/lanyun-fs/venvs/piwm-train-fast/bin/swift
```

Wrapper head:

```python
#!/root/lanyun-fs/venvs/piwm-train-fast/bin/python
import sys
from swift.cli.main import cli_main
if __name__ == '__main__':
    sys.argv[0] = sys.argv[0].removesuffix('.exe')
    sys.exit(cli_main())
```

`swift --version` and `swift --help` did not produce useful output under timeout, but the package import and wrapper are present.

## GPU

`nvidia-smi`:

```text
2 x NVIDIA A100-SXM4-80GB
memory: 0MiB / 81920MiB on both GPUs
no running processes
driver: 570.172.08
CUDA: 12.8
```

## Model Weights

Limited search under common paths found no local `Qwen2.5-VL-7B` candidate:

```text
/root/.cache/huggingface/hub
/root/.cache/modelscope/hub
/root/lanyun-fs/models
/root/lanyun-fs/model
/root/lanyun-fs
```

Current script uses:

```text
MODEL_ID=Qwen/Qwen2.5-VL-7B-Instruct
```

If the model is not already cached in a path not searched here, first training launch may try to download it.

## Remote Dry-run

Command shape:

```bash
SWIFT_BIN=/root/lanyun-fs/venvs/piwm-train-fast/bin/swift bash scripts/train/stage1_train.sh
```

Dry-run passed and printed the expected ms-swift command without launching training.

## Critical Launch Adjustment

The script default is currently:

```text
NPROC_PER_NODE=8
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
```

But this server has only:

```text
2 GPUs: 0,1
```

Therefore the actual run command must override:

```bash
cd /root/lanyun-fs/ProactiveIntentWorldModel
SWIFT_BIN=/root/lanyun-fs/venvs/piwm-train-fast/bin/swift \
NPROC_PER_NODE=2 \
CUDA_VISIBLE_DEVICES=0,1 \
bash scripts/train/stage1_train.sh --run
```

Without this override, launch will likely fail because GPUs `2-7` do not exist.

## Current Go / No-go

Data is ready on the server.

Remaining launch risks:

1. model weights were not found in the checked local caches;
2. script defaults must be overridden for 2 GPUs;
3. `swift --version/help` did not print under timeout, although Python package import and dry-run wrapper are present.

