本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# A3+ 数据生成可复现性冻结报告

日期：2026-05-21

## 结论

A3+ Stage-1 数据生成链路已经冻结到 git 分支 `codex/a3plus-reproducibility`。

冻结提交：

```text
5d3239c2d81502cf2184232cb80176afff1a6428
```

提交信息：

```text
freeze A3+ data generation pipeline for reproducibility
- loss_weight config: seek_reassurance=0.1, negotiate_price=0.1
- split: 2309 train + 235 val (seed=42, AIDA stratified)
- 5-act = Greet/Elicit/Inform/Recommend/Hold (no Reassure)
```

我没有启动训练。

## A. 已冻结的文件

### 1. A3+ loss_weight 来源

这些文件定义并应用 A3+ 的低置信视觉意图标签权重：

```text
piwm_train/config.py
piwm_train/data_collator.py
piwm_train/ms_swift_adapter.py
piwm_train/a3plus_metrics.py
piwm_train/prompts.py
piwm_train/targets.py
```

冻结规则：

```text
seek_reassurance: loss_weight = 0.1
negotiate_price: loss_weight = 0.1
其他 intent_label: loss_weight = 1.0
```

### 2. Stage-1 数据生成入口

```text
scripts/build_stage1_general_split.py
scripts/build_two_stage_training_and_eval.py
scripts/eval_ms_swift_checkpoint.py
scripts/train/stage1_eval.py
```

`build_stage1_general_split.py` 额外修复了一个可复现性问题：如果 `general_split_seed42.json` 已存在，脚本会复用已有 `created_at_cst`，避免同样 seed 重跑时只因时间戳造成 manifest 变化。

### 3. split manifest 和父样本名单

```text
data/official/piwm_train_synth_v2/general_split_seed42.json
data/official/piwm_train_synth_v2/general_train_parents.txt
data/official/piwm_train_synth_v2/general_val_parents.txt
```

固定划分：

```text
seed = 42
stratification = AIDA stage
train = 2309 examples
val = 235 examples
train parent states = 493
val parent states = 50
```

### 4. Stage-1 源数据和输出数据

源数据：

```text
data/official/piwm_train_synth_v2/state_inference.jsonl
data/official/piwm_train_synth_v2/transition_modeling.jsonl
```

生成输出：

```text
data/official/piwm_train_synth_v2/user_intent_train.jsonl
data/official/piwm_train_synth_v2/user_intent_val.jsonl
data/official/piwm_train_synth_v2/next_state_prediction_train.jsonl
data/official/piwm_train_synth_v2/next_state_prediction_val.jsonl

data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
```

对应 summary JSON 也已纳入同一提交。

### 5. 测试

```text
piwm_train/tests/test_data_collator.py
piwm_train/tests/test_stage1_a3plus_metrics.py
piwm_train/tests/test_targets.py
```

验证结果：

```text
29 passed
```

## B. 可复现性验证

执行方式：

```text
git stash push -u -m "codex-a3plus-reproducibility-clean-simulation-2"
git checkout codex/a3plus-reproducibility
python3 -m scripts.build_stage1_general_split
python3 -m scripts.build_two_stage_training_and_eval
```

说明：第一次 clean simulation 暴露了漏冻结依赖 `piwm_train/prompts.py` / `piwm_train/targets.py`，随后我把这两个文件和对应测试补进同一个提交并重新验证。最终验证通过。

### sha256 对比

| 文件 | 当前 A3+ sha256 | 重跑后 sha256 | 结果 |
|---|---|---|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | `2b0e3b7aa4a3c542dcf6794db844f823b978934c0992fc44210906964e6d4e1e` | `2b0e3b7aa4a3c542dcf6794db844f823b978934c0992fc44210906964e6d4e1e` | match |
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | `6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6` | `6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6` | match |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | `3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702` | `3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702` | match |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | `d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456` | `d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456` | match |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | `36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68` | `36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68` | match |
| `data/official/piwm_train_synth_v2/general_split_seed42.json` | `246d3f5d31f929287e77a1134f3e3a14d5d102b01fe37d4b6af50795612da198` | `246d3f5d31f929287e77a1134f3e3a14d5d102b01fe37d4b6af50795612da198` | match |
| `data/official/piwm_train_synth_v2/general_train_parents.txt` | `dede2cc0cfdb2d91198fad63ea76be6127e4d6a291204e86972d91eef068b9ba` | `dede2cc0cfdb2d91198fad63ea76be6127e4d6a291204e86972d91eef068b9ba` | match |
| `data/official/piwm_train_synth_v2/general_val_parents.txt` | `217e2f068291ec8540dd894767ffb10ceef976aeb45229d05a26f46c0833f6c2` | `217e2f068291ec8540dd894767ffb10ceef976aeb45229d05a26f46c0833f6c2` | match |

结论：A3+ Stage-1 数据可以从当前提交稳定重生成，关键训练 JSONL 和 split manifest sha256 完全一致。

## C. 服务器旧训练数据 snapshot

服务器旧训练数据目录：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/data/official/ms_swift_server_resolved/
```

已打包为：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/archives/stage1_baseline_data_2026-05-20.tar.gz
```

tar 包 sha256：

```text
707a81e2161deac483ee0365382a60b9441b2ab7c24d5cdbf27eda3b811ba677
```

包内文件：

```text
ms_swift_server_resolved/
ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_train_v1.jsonl
ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl
ms_swift_server_resolved/piwm_train_stage1_user_intent_train_v1.jsonl
ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl
```

源文件 sha256 和行数：

| 文件 | rows | sha256 |
|---|---:|---|
| `piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | `51d4b24f333cf79b64dac575a75e37504c241ca5eaa027e7e01e1c3f82e3c4d7` |
| `piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | `20c04c28bd0d7e481afa5c2cfb26eed351f73c2ba7c0a8fb900a7916ff8b1ec6` |
| `piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | `33871d33f802e6ade7c84354fd5934c052b91c0696533dd3b775faceac1ad685` |
| `piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | `18257faf817c097f40dc8a198e34e1d443a62c92fb216cf2c4e46dc74dc5ed31` |

旧服务器数据共 2544 行。它是旧 4 小时 checkpoint 的基线数据，不含 A3+ `loss_weight` 字段。

## D. 当前剩余状态

已完成：

- A3+ 生成代码、loss_weight 配置、split manifest、Stage-1 JSONL 和测试已进 git。
- clean simulation 重跑后 sha256 全部一致。
- 服务器旧训练数据已归档并记录 sha256。

仍需注意：

- 当前工作区仍保留大量历史 dirty 改动，未被本次提交纳入。
- 本次没有启动 Stage-1 重训。
- 如果要在服务器执行 A3+ 重训，需要把 `5d3239c2d81502cf2184232cb80176afff1a6428` 以及对应数据文件同步到服务器训练目录，再启动路径 C。
