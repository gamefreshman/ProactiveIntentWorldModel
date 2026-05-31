# Stage-1 Training Runbook

更新时间：2026-05-19 CST

本文是 `User Intent World Modeling` 的训练操作手册。Stage-1 的目标不是学导购动作，而是让模型先学会从 3 张帧判断顾客当前状态，并预测给定动作后的下一阶段。

## 1. 启动前 Checklist

1. 数据文件存在：
   - `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl`
   - `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl`
   - `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl`
   - `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl`
2. general frames 完整可读。当前 Stage-1 样本使用 3 张帧，服务器上至少要有这些目录对应的图片：
   - `Archive_generated_priority24/`
   - `Archive_generated_priority256/`
   - `Archive_generated_priority500_new_after280/`
   - `Archive_generated_priority1000_remaining_after500/`
3. ms-swift 可用：
   - 运行 `swift --version` 或 `python3 -m pip show ms-swift`。
   - 当前服务器默认 shell 不带 `swift`；已发现可用入口为 `/root/lanyun-fs/venvs/piwm-train-fast/bin/swift`，`ms-swift=4.1.3`。
4. GPU 就绪：
   - 运行 `nvidia-smi`，确认 8 张 RTX 4090 可见。
   - 默认使用 `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`。
   - 当前 `root@qhdlink.lanyun.net:37150` 的默认登录环境没有返回 GPU 信息；如果训练机确实已切到 8 卡节点，需要先进入对应容器/节点后再启动。
5. 磁盘空间：
   - `checkpoints/stage1_qwen25vl_7b_v1/` 至少预留数十 GB。
   - `logs/stage1_qwen25vl_7b_v1/` 要可写。

如果 Stage-1 split 文件缺失，先运行：

```bash
python3 -m scripts.build_stage1_general_split
```

## 2. 启动命令

先做 dry-run，确认命令和数据路径：

```bash
bash scripts/train/stage1_train.sh --dry-run
```

确认无误后，由项目负责人手动启动：

```bash
mkdir -p logs/stage1_qwen25vl_7b_v1
nohup bash scripts/train/stage1_train.sh --run > logs/stage1_qwen25vl_7b_v1/nohup.out 2>&1 &
```

如果使用当前服务器上的 venv，启动前设置：

```bash
export SWIFT_BIN=/root/lanyun-fs/venvs/piwm-train-fast/bin/swift
```

默认配置：

| 项 | 值 |
|---|---|
| 模型 | `Qwen/Qwen2.5-VL-7B-Instruct` |
| 训练方式 | LoRA |
| LoRA rank / alpha | `16 / 32` |
| target modules | `all-linear`（ms-swift 4.1.3 的宽 LoRA 目标模块设置；如新环境支持可用 `TARGET_MODULES=auto` 覆盖） |
| epoch | `3` |
| learning rate | `2e-5` |
| per-device batch size | `4` |
| gradient accumulation | `2` |
| GPU | 8 卡 DDP，`NPROC_PER_NODE=8` |
| 输入帧数 | `3`，由 JSONL 每条样本的 3 张图片保证，不向 ms-swift 4.1.3 传 `--max_frames` |
| max length | `4096` |
| act balancing | `none`，Stage-1 不训练动作选择 |
| checkpoint | `checkpoints/stage1_qwen25vl_7b_v1/` |
| logs | `logs/stage1_qwen25vl_7b_v1/` |

8 卡 4090 预计训练 4-6 小时。若显存有余，可以把 `PER_DEVICE_BATCH_SIZE=8` 作为后续调参，不建议第一次直接改。

## 3. 中途监控

训练过程中看三类信号：

1. loss 曲线：期望平稳下降；如果很快变成 `nan`，优先检查学习率、batch size、图片读取。
2. 显存峰值：用 `nvidia-smi` 看 8 张卡是否都在跑，是否接近 24GB 上限。
3. validation：ms-swift 日志中如出现 val loss，要确认没有突然上升或解析错误。

建议监控命令：

```bash
tail -f logs/stage1_qwen25vl_7b_v1/train.log
nvidia-smi
```

## 4. 训完评估

训练完成后运行 Stage-1 评估。先 dry-run：

```bash
python3 -m scripts.train.stage1_eval \
  --checkpoint checkpoints/stage1_qwen25vl_7b_v1 \
  --dry-run
```

正式评估：

```bash
python3 -m scripts.train.stage1_eval \
  --checkpoint checkpoints/stage1_qwen25vl_7b_v1
```

评估输出：

- `data/piwm_results/stage1_qwen25vl_7b_v1/stage1_val_metrics.json`
- `data/piwm_results/stage1_qwen25vl_7b_v1/stage1_val_metrics.md`

训完判定：

| 任务 | 指标 | 阈值 |
|---|---|---:|
| 任务 A：AIDA stage 分类 | macro F1 | > 0.6 |
| 任务 B：intention 分类 | accuracy | 暂只报告，不作为硬门槛 |
| 任务 C：next-stage 预测 | macro F1 | > 0.6 |

任务 A 和任务 C 都过阈值后，再进入 Stage-2 target action model。

## 5. 已知风险

1. general data 里 `Greet=0`。这意味着 Stage-1 几乎没有 Greet 信号；这是当前设计边界，不在 Stage-1 修。
2. general data 的 best 分布并不均衡：`Elicit 46% / Recommend 23% / Inform 19% / Hold 11%`。这会影响 Stage-2 行为倾向，但 Stage-1 主要学状态和 next-state，不在此阶段做 act balancing。
3. Stage-1 next-state 是动作条件预测，不是自然时间演化预测。`Hold(mode=silent)` 是“不干预”分支。
4. 当前 target balanced test 已按新 30 条名单写回 `qa_reviewed_pass=30`；不要复用旧 last-30 QA 结论，也不要把 test QA 结论扩展到 71 条 target train。
