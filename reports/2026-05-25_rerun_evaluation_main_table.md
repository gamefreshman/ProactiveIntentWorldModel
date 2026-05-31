5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# 2026-05-25 4 维度重跑评估主表

本轮只读评估；不重训、不改 official 数据、不改 5-act。Dim 4 direct best_act 不在本次重跑范围内；这里重跑的是 Dim 1/2、Dim 3（带 current state 的 deliberation prompt）和 Trick 6 反事实规划。

## 运行产物

- raw output 目录：`reports/rerun_eval_20260525/`
- General 域 seed=42 抽样列表：`reports/general_domain_eval_seed42.jsonl`
- Dim 3 prompt 证据：`reports/rerun_eval_20260525/dim3_deliberation_prompt_evidence.json`
- 注意：`Stage-2 only` checkpoint 未找到，因此本表不使用其他模型冒充。

## 主表

单元格格式：`strict macro F1 (modal prediction count / total)`；parse 失败样本按错误计入分母。带 `parse<0.7` 的结果表示解析率低于阈值，数字需谨慎使用。Random 列给 seed=42 单次均匀随机 macro F1；下方另列 1000 次平均。

| 维度 | PIWM 主模型 | 仅顾客状态与动作后果训练 | Stage-2 only | Zero-shot Qwen2.5-VL-7B | Random(seed=42) |
|---|---:|---:|---:|---:|---:|
| Dim 1 target AIDA | 0.245 (interest 12/30) | 0.279 (action 13/30) ⚠ parse<0.7 | 未跑：缺 checkpoint | 0.206 (interest 16/30) | 0.106 (attention 11/30) |
| Dim 1 general AIDA | 0.442 (action 8/30) ⚠ parse<0.7 | 0.403 (interest 7/30) ⚠ parse<0.7 | 未跑：缺 checkpoint | 0.153 (interest 23/30) | 0.223 (attention 11/30) |
| Dim 1 combined AIDA | 0.350 (action 19/60) ⚠ parse<0.7 | 0.349 (action 19/60) ⚠ parse<0.7 | 未跑：缺 checkpoint | 0.190 (interest 39/60) | 0.119 (attention 20/60) |
| Dim 2 target intent core | 0.046 (confirm_choice 23/30) | 0.048 (confirm_choice 15/30) ⚠ parse<0.7 | 未跑：缺 checkpoint | 0.078 (explore_options 15/30) | 0.048 (request_demonstration 8/30) |
| Dim 2 general intent core | 0.231 (confirm_choice 12/30) ⚠ parse<0.7 | 0.220 (confirm_choice 13/30) ⚠ parse<0.7 | 未跑：缺 checkpoint | 0.017 (explore_options 22/30) | 0.110 (compare_value_for_money 7/22) |
| Dim 2 combined intent core | 0.114 (confirm_choice 35/60) ⚠ parse<0.7 | 0.111 (confirm_choice 28/60) ⚠ parse<0.7 | 未跑：缺 checkpoint | 0.053 (explore_options 37/60) | 0.111 (compare_value_for_money 12/52) |
| Dim 3 next-stage F1 (80 covered) | 0.565 (desire 25/80) | 0.587 (interest 32/80) | 未跑：缺 checkpoint | 0.108 (UNPARSED 60/80) ⚠ parse<0.7 | 0.271 (attention 23/80) |
| Dim 3 parse rate | 0.887 | 1.000 | 未跑：缺 checkpoint | 0.250 | - |
| Trick 6 Reward A: stage_advance macro F1 | 0.171 (Elicit 11/30) | 0.165 (Elicit 11/30) | 未跑：缺 checkpoint | 0.247 (Inform 10/30) ⚠ parse<0.7 | 0.414 (random-candidate baseline) |
| Trick 6 Reward B: model_score macro F1 | 0.265 (Elicit 8/30) | 0.418 (Inform 9/30) | 未跑：缺 checkpoint | 0.372 (Elicit 11/30) ⚠ parse<0.7 | 0.414 (random-candidate baseline) |

## Random baseline 1000 次平均

| 维度 | 1000 次均匀随机期望 macro F1 | seed=42 macro F1 |
|---|---:|---:|
| Dim 1 target AIDA | 0.226 | 0.106 |
| Dim 1 general AIDA | 0.237 | 0.223 |
| Dim 1 combined AIDA | 0.235 | 0.119 |
| Dim 2 target intent core | 0.117 | 0.048 |
| Dim 2 general intent core | 0.117 | 0.110 |
| Dim 2 combined intent core | 0.138 | 0.111 |
| Dim 3 next-stage | 0.233 | 0.271 |

## 关键读数

- Dim 3 已按 PI 要求使用带 current state 的 deliberation prompt 重跑；PIWM 主模型 next-stage strict macro F1 = **0.565**，parsed-only macro F1 = **0.599**，parse rate = **0.887**。
- Trick 6 没有超过 direct best_act 主结果 0.641：PIWM Reward A = **0.171**，Reward B = **0.265**。
- Dim 1/2 的 PIWM 主模型解析率低于 0.7：combined parse rate = **0.667**；仅顾客状态与动作后果训练模型 = **0.567**。
- Stage-2 only checkpoint 不存在，本报告保留列位但不填数字，避免用错误 checkpoint 代替。

## Changelog 2026-05-25 (zero-shot bug fix)

上一版 zero-shot 列在 Dim 3 / Trick 6 上错误加载了 PIWM LoRA adapter，因为 `scripts/run_trick6_counterfactual_planning.py` 的 `--checkpoint` 有默认 PIWM checkpoint，不传 checkpoint 也会加载 adapter。已在该脚本加入 `--no-lora`，并让 `run_dim3` / `run_trick6` 在 no-lora 模式下写出 `checkpoint: null`。修复后只重跑 zero-shot 的 Dim 3 与 Trick 6，不改其他模型数字。

修复前后数字对比：

- Dim 3: 旧 0.565 → 新 0.108；parse rate 0.887 → 0.250。
- Trick 6 Reward A: 旧 0.171 → 新 0.247；candidate parse rate 0.907 → 0.262。
- Trick 6 Reward B: 旧 0.265 → 新 0.372；candidate parse rate 0.907 → 0.262。

修复后的 raw output：

- `reports/rerun_eval_20260525/zero_shot_qwen_dim3_fixed.json`
- `reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_a_fixed.json`
- `reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_b_fixed.json`
