本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Stage-1 A3+ 样本数差异核查

日期：2026-05-21

## 结论

没有发现 A3+ 重建导致 train 样本消失。当前本地可验证证据显示：

```text
旧报告口径：493 user_intent train + 1816 next_state_prediction train = 2309 train
新 A3+ 后：493 user_intent train + 1816 next_state_prediction train = 2309 train
差异：0
```

`2310 train + 235 val = 2544` 这个说法本身算术不成立，因为 `2310 + 235 = 2545`。仓库内也没有任何报告或文件证明旧 train 是 2310；能找到的旧报告都指向 `2309 train + 235 val = 2544`。

因此，本轮没有可以 dump 的“消失样本”。当前判断是：这是旧口径记录或转述里的数字错误，不是 A3+ loader silent drop。

## A. 旧/新 task_id 差集

### 可用旧证据

旧 JSONL 原始文件内容已经不在当前工作区。当前只找到旧报告里的文件行数和 sha256：

| 旧文件 | 旧报告行数 | 旧报告 sha256 |
|---|---:|---|
| `piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | `9e98a875906efc909ddaea3a6342f8ea42ab63342189f52d76e2eccd363a699f` |
| `piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | `e6acf951a22593f05f15b1981407ec49a07e5da45a93e4315e081cefb0be30b1` |
| train total | 2309 | - |
| val total | 235 | - |
| all total | 2544 | `68f37965030cf7cb4fa79ee25da7259d42d11b47d1200b19392948aebd6093a7` |

我在当前 repo 下按这些旧 sha256 搜索过，没有找到旧文件副本。因此不能从“旧文件字节内容”直接算 `set(old task_id) - set(new task_id)`。

### 用旧报告计数与新文件计数对比

| Split file | 旧报告行数 | 新 A3+ 行数 | delta |
|---|---:|---:|---:|
| user_intent train | 493 | 493 | 0 |
| next_state_prediction train | 1816 | 1816 | 0 |
| user_intent val | 50 | 50 | 0 |
| next_state_prediction val | 185 | 185 | 0 |
| train total | 2309 | 2309 | 0 |
| val total | 235 | 235 | 0 |
| full Stage-1 | 2544 | 2544 | 0 |

在可验证证据下，差集应解释为：

```text
set(旧 task_id) - set(新 task_id) = 不可直接计算；旧文件内容缺失
基于旧报告计数：无行数差异

set(新 task_id) - set(旧 task_id) = 不可直接计算；旧文件内容缺失
基于旧报告计数：无行数差异
```

## B. “消失样本”完整 dump

没有可证明消失的样本，因此无样本可 dump。

如果后续能拿到旧文件，例如：

```text
旧 user train sha256 = 9e98a875906efc909ddaea3a6342f8ea42ab63342189f52d76e2eccd363a699f
旧 next train sha256 = e6acf951a22593f05f15b1981407ec49a07e5da45a93e4315e081cefb0be30b1
```

就可以按 `task + source_id` 作为 task_id 重新做精确集合差分。

## C. 消失原因判断

当前判断：没有样本消失；不是 A3+ 主动剔除，也不是 silent drop。

证据：

1. A3+ 只给 user_intent 样本增加/修改 `weight`、`loss_weight` 和 `meta.loss_weight_policy`，没有增加过滤条件。
2. 当前四个 split 文件行数与旧报告一致。
3. 当前四个 split 文件的 `source_id` 都没有重复：
   - user_intent train: 493 rows / 493 unique source_id
   - next_state_prediction train: 1816 rows / 1816 unique source_id
   - user_intent val: 50 rows / 50 unique source_id
   - next_state_prediction val: 185 rows / 185 unique source_id
4. `2544 = 2309 train + 235 val` 成立；`2544 = 2310 train + 235 val` 不成立。

## D. Silent drop 风险

当前没有发现 silent drop。

仍然存在一个工程治理风险：`data/official/ms_swift/` 和 `data/official/piwm_train_synth_v2/` 当前是 ignored 数据目录，旧 JSONL 不在 git 中保存，所以后续如果只保留报告 sha256、不保留 task_id manifest，就无法复盘精确样本差集。

建议后续补一个轻量清单，不需要把大 JSONL 入 git：

```text
data/official/piwm_train_synth_v2/stage1_split_task_ids_seed42.json
```

内容只保存：

- split 名
- task
- source_id
- task_id = task + "::" + source_id
- generated file sha256

这样以后重建 loader 时能直接比较样本集合，而不是只能比行数。

## E. A3+ low-weight rows = 146 拆分

这里要区分两个口径：

### Full Stage-1 口径

文件：

```text
data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
```

| intent_label | low-weight rows |
|---|---:|
| seek_reassurance | 91 |
| negotiate_price | 55 |
| total | 146 |

结论：

```text
91 + 55 = 146  PASS
```

### Train split 口径

文件：

```text
data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
```

| intent_label | low-weight rows |
|---|---:|
| seek_reassurance | 82 |
| negotiate_price | 50 |
| total | 132 |

Val split 中还有：

| intent_label | low-weight rows |
|---|---:|
| seek_reassurance | 9 |
| negotiate_price | 5 |
| total | 14 |

所以：

```text
train 132 + val 14 = full 146
```

如果说 “A3+ low-weight rows = 146”，它指的是 full Stage-1 all 文件，不是 train-only split。

## 当前文件 sha256

```text
6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6  data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702  data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456  data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl
36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68  data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
2b0e3b7aa4a3c542dcf6794db844f823b978934c0992fc44210906964e6d4e1e  data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
```
