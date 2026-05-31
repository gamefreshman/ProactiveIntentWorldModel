本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# A3+ intent_label 实施报告

日期：2026-05-21

## 结论

A3+ 已按 PI 拍板实现到训练数据准备层和 Stage-1 评估层；没有重训，没有改 5-act 主口径，没有启动 Stage-2。

A3+ 的核心处理是：

- `seek_reassurance` 和 `negotiate_price` 保留在标签空间里，但在训练时降权为 `loss_weight=0.1`。
- 其他 intent_label 保持 `loss_weight=1.0`。
- Stage-1 intent 主指标改为核心 5 类 macro F1，排除这两个视觉不可识别标签。
- 这两个低可信标签仍输出附属指标：各自 F1、sample_count、pred_count，并标注 `visually unidentifiable`。

## 代码改动

### 训练数据层

- `piwm_train/config.py`
  - 新增 `LOW_CONFIDENCE_INTENT_LABELS = ("seek_reassurance", "negotiate_price")`
  - 新增 `LOW_CONFIDENCE_INTENT_LOSS_WEIGHT = 0.1`
  - 新增 `DEFAULT_INTENT_LOSS_WEIGHT = 1.0`

- `piwm_train/data_collator.py`
  - 新增 `user_intent_loss_weight(intent_label)`。
  - `build_sft_examples(... include_user_intent=True)` 生成 user_intent 样本时写入：
    - `example.weight`
    - `meta.loss_weight`
    - `meta.loss_weight_policy = "a3plus_visual_intent_low_confidence"`

- `piwm_train/ms_swift_adapter.py`
  - ms-swift JSONL 行新增顶层 `loss_weight`，与现有 `weight` 同值。
  - 这样后续训练脚本可以显式读取 `loss_weight`，旧消费方仍可用 `weight`。

- `scripts/build_two_stage_training_and_eval.py`
  - `_user_intent_example()` 使用同一套 `user_intent_loss_weight()`。
  - 重建后的 Stage-1 all / joint 文件已经包含 A3+ 权重。

### 评估层

- `piwm_train/a3plus_metrics.py`
  - 新增纯 Python 指标模块，避免单测导入评估脚本时被 `torch` 依赖卡住。
  - 提供 `intent_a3plus_metrics(pairs)`。

- `scripts/eval_ms_swift_checkpoint.py`
  - intent_label 原 full macro F1 继续保留。
  - 新增 A3+ 主指标：
    - `intent_core_5class_n`
    - `intent_core_5class_macro_f1`
    - `intent_core_5class_accuracy`
  - 新增低可信标签附属指标：
    - `intent_low_confidence_seek_reassurance_sample_count`
    - `intent_low_confidence_seek_reassurance_f1`
    - `intent_low_confidence_negotiate_price_sample_count`
    - `intent_low_confidence_negotiate_price_f1`
    - 对应 note 均为 `visually unidentifiable under the current visual-only Stage-1 contract`

- `scripts/train/stage1_eval.py`
  - Stage-1 eval 汇总报告改为两层：
    - 第一层：A3+ core 5-class intent macro F1，作为主 intent 指标。
    - 第二层：full 7-class macro F1 与两个低可信标签的附属表。
  - Stage-2 是否启动仍只按已有规则看 Task A AIDA macro F1 和 Task C next-stage macro F1；A3+ intent 暂时只报告，不自动 gate。

## 数据准备结果

已重建以下 Stage-1 / two-stage 入口文件，没有启动训练：

| 文件 | 行数 | A3+ 低权重行 |
|---|---:|---:|
| `data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | 132 |
| `data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | 14 |
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 | 146 |
| `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl` | 2615 | 146 |
| `data/official/domain_specialization_eval_v2/general_qa_stage1_all.jsonl` | 162 | 7 |
| `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_user_intent.jsonl` | 30 | 0 |

全量 Stage-1 文件中，543 条 user_intent 里：

- `seek_reassurance`: 91 条，全部 `loss_weight=0.1`
- `negotiate_price`: 55 条，全部 `loss_weight=0.1`
- 其他 397 条 user_intent，全部 `loss_weight=1.0`
- 2001 条 next_state_prediction，全部 `loss_weight=1.0`

Target 30 条 QA-reviewed test 没有低可信 intent_label，所以 target eval 不受 A3+ 降权影响。

## 关键文件 sha256

```text
2b0e3b7aa4a3c542dcf6794db844f823b978934c0992fc44210906964e6d4e1e  data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
3f9e8bfcb665ce53227e39e19adc7c767141d6af809afe1fed6407052cae6299  data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl
dbe2fd9d7eb5d9ad37938a55c008e79a8e6ceddf19d385130fcb650ed03e1feb  data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl
583f3482fe11e6ce7c1561d38ca0038b27b4c9007cab011c136de64fd09802f4  data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl
291e0ceda30b66b12bb5c43f8074cb412a35a8c09f80eb5bd45ca1f53b7db683  data/official/domain_specialization_eval_v2/general_qa_stage1_all.jsonl
```

## 验证结果

已运行并通过：

```bash
python3 -m py_compile piwm_train/config.py piwm_train/a3plus_metrics.py piwm_train/data_collator.py piwm_train/ms_swift_adapter.py scripts/build_two_stage_training_and_eval.py scripts/eval_ms_swift_checkpoint.py scripts/train/stage1_eval.py
python3 -m scripts.build_stage1_general_split
python3 -m scripts.build_two_stage_training_and_eval
python3 -m scripts.check_target_frontcam_split
python3 -m scripts.run_action_selection_baselines
python3 -m pytest piwm_data/tests/test_5act_invariant.py piwm_train/tests/test_data_collator.py piwm_train/tests/test_stage1_a3plus_metrics.py -q
git diff --check
```

验证摘要：

- Target 仍是 `101 clean = 71 Stage-2 train + 30 balanced test`。
- 30 条 balanced target test 仍是 `Greet=6 / Elicit=6 / Inform=6 / Recommend=6 / Hold=6`。
- `piwm_data/tests/test_5act_invariant.py` 通过，operational 层仍排除 Reassure。
- 相关单测共 23 个通过。
- random-candidate baseline 保持 `macro F1 = 0.2810744810744811`。

## 影响范围和后续

本次只准备 A3+ 数据与评估器，不改变模型权重。当前 4 小时 checkpoint 继续保留；A3+ 重训后，可以把旧 checkpoint 和新 checkpoint 做 ablation 对比：

- 旧 checkpoint：未降权、intent_label full 7-class 口径。
- 新 checkpoint：低可信两类训练降权、intent 主指标使用 core 5-class macro F1。

人工边界：PI 需要确认 A3+ 主指标是否以后写进论文主表，还是只写进附录和诊断表。
