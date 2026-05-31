# Server Training Environment Configuration

本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

## Summary

服务器训练环境已配置到可启动前的状态：代码工作目录、Python 环境、ms-swift、Stage-1 数据、模型权重和 2GPU 启动包装脚本都已就绪。

当前唯一阻塞是服务器处于无卡模式：`torch.cuda.is_available()` 返回 `False`，`torch.cuda.device_count()` 返回 `0`。因此现在不能实际启动 GPU 训练；切回有卡模式后可直接运行本文末尾命令。

## Server Paths

- Project: `/root/lanyun-fs/ProactiveIntentWorldModel`
- Python env: `/root/lanyun-fs/venvs/piwm-train-fast/bin/python`
- Swift bin: `/root/lanyun-fs/venvs/piwm-train-fast/bin/swift`
- Local model: `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct`
- 2GPU launcher: `/root/lanyun-fs/ProactiveIntentWorldModel/scripts/train/stage1_train_a100_2gpu.sh`

## Model Decision

Qwen3-VL is the newer model family, but it is not safe to switch in this server environment now.

Reason:
- Official Qwen3-VL documentation/repository states that Qwen3-VL requires `transformers >= 4.57.0`.
- Current server has `transformers=4.51.3`.
- Current server `transformers` package has `qwen2_5_vl` support but no `qwen3_vl` module.
- Current ms-swift setup is already validated for Qwen2.5-VL-style training entrypoints.

Decision for this run:
- Use `Qwen/Qwen2.5-VL-7B-Instruct`.
- Downloaded local weights to `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct`.
- Do not upgrade the active training environment in-place before Stage-1, because that would add new dependency risk.

## Environment Check

Observed in `/root/lanyun-fs/venvs/piwm-train-fast`:

- `swift=4.1.3`
- `modelscope=1.36.3`
- `transformers=4.51.3`
- `torch=2.2.1+cu121`
- `qwen_vl_utils` importable
- `has_qwen2_5_vl=True`
- `has_qwen3_vl=False`
- Current no-card mode:
  - `cuda_available=False`
  - `cuda_device_count=0`

## Model Files

`/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct`:

- Size: `16G`
- File count: `18`
- Required files present:
  - `config.json`
  - `model.safetensors.index.json`
  - `model-00001-of-00005.safetensors`
  - `model-00002-of-00005.safetensors`
  - `model-00003-of-00005.safetensors`
  - `model-00004-of-00005.safetensors`
  - `model-00005-of-00005.safetensors`
  - tokenizer/preprocessor files

## Launcher

Created:

`/root/lanyun-fs/ProactiveIntentWorldModel/scripts/train/stage1_train_a100_2gpu.sh`

SHA256:

`8399aed8db504f0de9d307ac25f677257a539fe7768e23fac1b6bf129063eeb4`

It only wraps the canonical Stage-1 launcher and overrides server-specific settings:

- `MODEL_ID=/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct`
- `SWIFT_BIN=/root/lanyun-fs/venvs/piwm-train-fast/bin/swift`
- `NPROC_PER_NODE=2`
- `CUDA_VISIBLE_DEVICES=0,1`
- `OUTPUT_DIR=checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1`
- `LOG_DIR=logs/stage1_qwen25vl_7b_a100_2gpu_v1`

Dry-run passed and printed the expected ms-swift command.

## Start Command After GPU Mode Is Restored

Do not run while `cuda_device_count=0`.

```bash
cd /root/lanyun-fs/ProactiveIntentWorldModel
bash scripts/train/stage1_train_a100_2gpu.sh --run
```

Dry-run command:

```bash
cd /root/lanyun-fs/ProactiveIntentWorldModel
bash scripts/train/stage1_train_a100_2gpu.sh --dry-run
```

## References

- Qwen3-VL official repository: https://github.com/QwenLM/Qwen3-VL
- Qwen3-VL basic usage documentation notes `transformers >= 4.57.0`: https://www.mintlify.com/QwenLM/Qwen3-VL/inference/basic-usage
