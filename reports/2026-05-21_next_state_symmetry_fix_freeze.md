本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# next_state task 对称性修复 + 重新 freeze

日期：2026-05-21

## 结论

已完成 next_state task 对称性修复，并冻结到当前分支：

```text
branch: codex/a3plus-reproducibility
commit: ce5c05fbea6d241b0b8c3b6c4f5f0ace644a6c1f
```

本次修复只改 Stage-1 `next_state_prediction` 的输入 prompt，不改 5-act，不启动训练。

## A. 修改内容

新增 prompt：

```text
piwm_train.prompts.build_next_state_prediction_prompt()
```

Stage-1 生成入口改为：

```text
scripts/build_two_stage_training_and_eval.py
_next_state_example() -> build_next_state_prediction_prompt(row)
```

从 `next_state_prediction` 输入中移除：

```text
current_stage
current_belief
current_desire
current_intention
gold current visual_state text
```

保留：

```text
3 frames
candidate action label
candidate act / params
terminal realization
concrete execution plan
task output instruction
```

新的 prompt 明确写：

```text
Use the frames to infer the customer's current state internally.
The current stage, intent, and BDI state are not provided.
```

## B. 重新生成后的行数

| 文件 | rows | task 分布 |
|---|---:|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 | user_intent=543, next_state_prediction=2001 |
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | user_intent=493 |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | user_intent=50 |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | next_state_prediction=1816 |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | next_state_prediction=185 |

验收：

```text
Stage-1 total = 2544
user_intent total = 543
next_state_prediction total = 2001
```

全部满足。

## C. sha256 比对

### user_intent 子集

user_intent train/val 子集没有变化。

| 文件 | A3+ freeze sha256 | symmetry fix sha256 | 结果 |
|---|---|---|---|
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | `6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6` | `6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6` | same |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | `d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456` | `d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456` | same |

### next_state 子集

next_state train/val 子集已经变化。

| 文件 | A3+ freeze sha256 | symmetry fix sha256 | 结果 |
|---|---|---|---|
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | `3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702` | `f4c470a922d7dfd24e823216811cc7f3c63786151276ba8be0fdf6365b73f46e` | changed |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | `36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68` | `1981ad6fd5eb4a7d6684bf434bf916b84e6d83ba8a6fd46aaed8668869658515` | changed |

### combined Stage-1 文件

`data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` 包含 user_intent + next_state_prediction，所以它也随 next_state 变化：

```text
A3+ freeze:   2b0e3b7aa4a3c542dcf6794db844f823b978934c0992fc44210906964e6d4e1e
symmetry fix: cdd601d868bb039da5cffc13a11f37d81be43e52939ddb1940b6b8e49f2111ae
```

### split manifest

split 没变：

```text
data/official/piwm_train_synth_v2/general_split_seed42.json
sha256 = 246d3f5d31f929287e77a1134f3e3a14d5d102b01fe37d4b6af50795612da198
```

## D. 泄漏字段检查

对 2001 条 `next_state_prediction` prompt 做全量检查：

| 字段 | 出现条数 |
|---|---:|
| `The customer's current state is:` | 0 |
| `- stage:` | 0 |
| `- visible evidence:` | 0 |
| `- engagement pattern:` | 0 |
| `- gaze and attention:` | 0 |
| `- body and hands:` | 0 |
| `- belief:` | 0 |
| `- desire:` | 0 |
| `- intention:` | 0 |
| `current_stage` | 0 |
| `current_bdi` | 0 |

样例 prompt 现在形如：

```text
<image><image><image>You are observing a customer in a retail store...

Use the frames to infer the customer's current state internally.
The current stage, intent, and BDI state are not provided.

Consider one candidate intervention: Elicit_b1166d372e5e
...
```

## E. 复现验证

执行：

```text
git stash push -u -m "codex-next-state-symmetry-clean-simulation"
git checkout codex/a3plus-reproducibility
python3 -m scripts.build_stage1_general_split
python3 -m scripts.build_two_stage_training_and_eval
```

重跑后 sha256：

```text
cdd601d868bb039da5cffc13a11f37d81be43e52939ddb1940b6b8e49f2111ae  data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
6126ef5891a39050a22586c54c2e66bc18569c90c083ea2d0f013cb64e7a09f6  data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
d01a3cd802deedeba7fd6697b111c2bb63a4799d029e67c8e5bafa1760a0d456  data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl
f4c470a922d7dfd24e823216811cc7f3c63786151276ba8be0fdf6365b73f46e  data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
1981ad6fd5eb4a7d6684bf434bf916b84e6d83ba8a6fd46aaed8668869658515  data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
246d3f5d31f929287e77a1134f3e3a14d5d102b01fe37d4b6af50795612da198  data/official/piwm_train_synth_v2/general_split_seed42.json
```

复现验证通过。重跑后工作区无本次提交相关 diff。

## F. 测试

已运行：

```text
python3 -m py_compile piwm_train/prompts.py scripts/build_two_stage_training_and_eval.py scripts/build_stage1_general_split.py
python3 -m pytest piwm_train/tests/test_prompts.py -q
python3 -m pytest piwm_train/tests/test_prompts.py piwm_train/tests/test_data_collator.py piwm_train/tests/test_stage1_a3plus_metrics.py -q
```

结果：

```text
test_prompts.py: 7 passed
combined prompt/data-collator/A3+ metrics tests: 23 passed
```

## G. 当前状态

当前分支：

```text
codex/a3plus-reproducibility
```

最新两个提交：

```text
ce5c05f next_state task symmetry: remove current_state leak
5d3239c freeze A3+ data generation pipeline for reproducibility
```

结论：

```text
路径 C 现在可以用 ce5c05f 对应的数据启动重训。
```

仍需注意：

```text
工作区仍有大量历史 dirty 文件，但它们没有进入本次 commit。
```
