本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Stage-1 数据版本快照取证

日期：2026-05-21

## 结论

旧 4 小时 checkpoint `v5-20260520-180808/checkpoint-432` 不是用当前 A3+ 文件训练的。它训练时实际加载的是服务器上的 `data/official/ms_swift_server_resolved/*.jsonl` 四个文件；这些文件仍在服务器上，并且没有 `loss_weight` 字段。

当前 A3+ 数据是本地重建后的 `data/official/ms_swift/*.jsonl` 和 `data/official/piwm_train_synth_v2/*.jsonl`，包含 `loss_weight` 字段，sha256 与旧 checkpoint 数据不同。

所以关系是：

```text
旧 checkpoint 数据 != 当前 A3+ 数据
旧 checkpoint exact files：仍在服务器 /root/lanyun-fs/.../ms_swift_server_resolved/
本地旧 data/official/ms_swift/*.jsonl：已被 A3+ 重建覆盖
```

## A. 当前 Stage-1 JSONL 文件快照

### 当前训练入口文件

| path | rows | sha256 | mtime |
|---|---:|---|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 | `2b0e3b7aa4a3c542dcf6794db844f823b978934c0992fc44210906964e6d4e1e` | `2026-05-21T16:38:06+08:00` |
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | `6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6` | `2026-05-21T16:36:52+08:00` |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | `3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702` | `2026-05-21T16:36:52+08:00` |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | `d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456` | `2026-05-21T16:36:52+08:00` |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | `36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68` | `2026-05-21T16:36:52+08:00` |

### 当前 mirrored split 文件

这些文件与上面的 split 文件内容相同，只是同时写在 `piwm_train_synth_v2` 目录下，便于按数据集源目录查看。

| path | rows | sha256 | mtime |
|---|---:|---|---|
| `data/official/piwm_train_synth_v2/user_intent_train.jsonl` | 493 | `6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6` | `2026-05-21T16:36:51+08:00` |
| `data/official/piwm_train_synth_v2/next_state_prediction_train.jsonl` | 1816 | `3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702` | `2026-05-21T16:36:51+08:00` |
| `data/official/piwm_train_synth_v2/user_intent_val.jsonl` | 50 | `d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456` | `2026-05-21T16:36:51+08:00` |
| `data/official/piwm_train_synth_v2/next_state_prediction_val.jsonl` | 185 | `36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68` | `2026-05-21T16:36:51+08:00` |

### 当前 Stage-1 eval 辅助文件

| path | rows | sha256 | mtime |
|---|---:|---|---|
| `data/official/domain_specialization_eval_v2/general_qa_stage1_all.jsonl` | 162 | `291e0ceda30b66b12bb5c43f8074cb412a35a8c09f80eb5bd45ca1f53b7db683` | `2026-05-21T16:38:07+08:00` |

### A3+ 字段状态

当前 A3+ 文件中：

- `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl`
  - rows: 493
  - `loss_weight` rows: 493
  - low-weight rows: 132
- `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl`
  - rows: 1816
  - `loss_weight` rows: 1816
  - low-weight rows: 0

全量 Stage-1 文件：

```text
data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
rows = 2544
low-weight rows = 146
seek_reassurance = 91
negotiate_price = 55
```

## B. 4 小时 checkpoint 实际加载的数据

Checkpoint:

```text
/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1/v5-20260520-180808/checkpoint-432
```

读取来源：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1/v5-20260520-180808/args.json
```

`args.json` 里的实际数据路径：

```text
dataset = [
  "data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_train_v1.jsonl",
  "data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_train_v1.jsonl"
]

val_dataset = [
  "data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl",
  "data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl"
]
```

其他关键训练参数：

| key | value |
|---|---|
| model | `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct` |
| output_dir | `/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1/v5-20260520-180808` |
| logging_dir | `/root/lanyun-fs/ProactiveIntentWorldModel/logs/stage1_qwen25vl_7b_a100_2gpu_v1` |
| num_train_epochs | `3.0` |
| learning_rate | `2e-05` |
| per_device_train_batch_size | `4` |
| gradient_accumulation_steps | `2` |
| max_length | `8192` |
| lora_rank | `16` |
| lora_alpha | `32` |
| data_seed | `42` |
| dataset_shuffle | `True` |
| val_dataset_shuffle | `False` |

### 旧 checkpoint 数据文件当前仍在服务器上

| field | path | rows | sha256 | mtime |
|---|---|---:|---|---|
| dataset | `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | `33871d33f802e6ade7c84354fd5934c052b91c0696533dd3b775faceac1ad685` | `2026-05-20T18:03:53+08:00` |
| dataset | `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | `51d4b24f333cf79b64dac575a75e37504c241ca5eaa027e7e01e1c3f82e3c4d7` | `2026-05-20T18:03:54+08:00` |
| val_dataset | `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | `18257faf817c097f40dc8a198e34e1d443a62c92fb216cf2c4e46dc74dc5ed31` | `2026-05-20T18:03:55+08:00` |
| val_dataset | `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | `20c04c28bd0d7e481afa5c2cfb26eed351f73c2ba7c0a8fb900a7916ff8b1ec6` | `2026-05-20T18:03:55+08:00` |

字段检查：

| file group | `weight` rows | `loss_weight` rows | low-weight rows |
|---|---:|---:|---:|
| old server user_intent train | 493 | 0 | 0 |
| old server next_state train | 1816 | 0 | 0 |
| old server user_intent val | 50 | 0 | 0 |
| old server next_state val | 185 | 0 | 0 |

结论：旧 checkpoint 数据不是 A3+ 数据。它只有 `weight`，没有 `loss_weight`。

## C. 当前 A3+ 数据路径列表和关系判断

当前准备给路径 C 重训的 A3+ Stage-1 split 文件是：

```text
data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
```

当前 `scripts/train/stage1_train.sh` 默认也指向这四个路径：

```bash
TRAIN_USER=data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
TRAIN_NEXT=data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
VAL_USER=data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl
VAL_NEXT=data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
```

关系判断：

| 问题 | 判断 |
|---|---|
| 旧 checkpoint 和当前 A3+ 是同一份文件吗？ | 不是。路径不同，sha256 不同，字段也不同。 |
| 旧 checkpoint 是否实际用 A3+ 数据训过？ | 不是。旧 server-resolved 文件没有 `loss_weight`。 |
| 旧文件在哪？ | 旧 checkpoint exact files 仍在服务器 `data/official/ms_swift_server_resolved/`。 |
| 本地旧文件是否还在？ | 本地 `data/official/ms_swift/*.jsonl` 已被 A3+ 重建覆盖；本地没有旧 sha 文件副本。 |
| 当前 A3+ 是否已经同步成旧 checkpoint 那种 server_resolved 路径？ | 本次取证未做同步；服务器旧 `ms_swift_server_resolved` 文件仍是 pre-A3+。 |

## D. 可复现性评估

### 当前 A3+ 数据

当前 A3+ 数据可以从当前工作区复现，前提是保留当前 dirty worktree，因为关键脚本仍未进入 git 跟踪：

| artifact | path | tracked? | sha256 | mtime |
|---|---|---|---|---|
| split builder | `scripts/build_stage1_general_split.py` | no | `27d884b5b2fde12335b491d925f865fc966a052605255bddd67ec6066f50bb65` | `2026-05-19T21:10:03+08:00` |
| two-stage builder | `scripts/build_two_stage_training_and_eval.py` | no | `6b9f83ee1ba4fbcf0fdcbb6829d3d2d4a0594bef7f4079049abf6767089b75eb` | `2026-05-21T16:32:49+08:00` |
| split manifest | `data/official/piwm_train_synth_v2/general_split_seed42.json` | no | `246d3f5d31f929287e77a1134f3e3a14d5d102b01fe37d4b6af50795612da198` | `2026-05-21T16:36:52+08:00` |

`general_split_seed42.json` 记录了：

```json
{
  "artifact": "piwm_stage1_general_split_seed42",
  "seed": 42,
  "stratification": "AIDA stage",
  "total_parent_count": 543,
  "train_parent_count": 493,
  "val_parent_count": 50,
  "stage1_train_examples": 2309,
  "stage1_val_examples": 235,
  "task_counts": {
    "train": {
      "user_intent": 493,
      "next_state_prediction": 1816
    },
    "val": {
      "user_intent": 50,
      "next_state_prediction": 185
    }
  }
}
```

评估：当前 A3+ 数据“工作区内可复现”，但“干净 git checkout 不可复现”，因为关键生成脚本和 split manifest 仍是 untracked / ignored 状态。

### 旧 4 小时 checkpoint 数据

旧 checkpoint exact files 目前仍在服务器上，可以直接复制回来做对比或复跑旧基线。它们不是从本地当前 A3+ 文件推导出来的。

如果服务器文件未来被删，当前本地 git 不能保证恢复旧文件；旧报告只保留了行数和 sha256，不包含完整 JSONL 内容。

## E. 能否从代码 + seed 重新生成旧文件

### 当前 A3+ 文件

可以从当前 dirty worktree + seed 42 重新生成，依据是：

- `scripts/build_stage1_general_split.py`
- `scripts/build_two_stage_training_and_eval.py`
- `data/official/piwm_train_synth_v2/general_split_seed42.json`
- source data: `data/official/piwm_train_synth_v2/state_inference.jsonl` 和 `transition_modeling.jsonl`

但这些生成脚本 / split manifest 当前不在 git history 中稳定保存。因此如果只看 git history，不能保证复现。

### 旧 pre-A3+ 文件

旧 checkpoint 用的 server-resolved 文件仍在服务器，可以恢复；如果服务器文件丢失，则只能尝试用旧报告中的生成路径和旧代码状态重建，但当前取证未发现一个已提交的 git commit 可以完整代表当时的 pre-A3+ loader 状态。

简言之：

```text
旧 exact files: 当前服务器可恢复
旧 exact files from clean git: 目前不可保证
当前 A3+ files: 当前 dirty worktree 可复现
当前 A3+ files from clean git: 目前不可保证
```

## 取证建议

1. 立刻把旧 checkpoint 使用的四个 `ms_swift_server_resolved` 文件复制/归档到一个只读快照目录，例如：

```text
data/snapshots/stage1_pre_a3plus_checkpoint432/
```

2. 为当前 A3+ 也生成一个 task-id manifest，至少保存：

```text
task
source_id
task_id = task + "::" + source_id
file path
line index
sha256
```

3. 在启动路径 C 重训前，先把当前 A3+ 四个 split 文件同步到服务器新目录，不要覆盖旧 `ms_swift_server_resolved`，例如：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_a3plus_20260521/
```

这样旧 checkpoint 和 A3+ 重训能并排对比，不会互相污染。
