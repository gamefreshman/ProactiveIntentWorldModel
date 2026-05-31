本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

# Stage-1 评估补充诊断

## 结论先行

- `user_intent` 分数低不是 parse 问题；核心是类别混淆和任务输入信息不足。
- 训练集 intent_label 分布很不均：最大类 `confirm_choice` 有 163 条，最小类只有 15 条。
- intent_label 的训练样本数与 eval F1 呈中等到较强正相关：Pearson `0.719`，Spearman `0.775`；少样本确实会压低 F1，但不能完全解释问题，因为 `seek_reassurance` 等训练样本不少的类别仍然 F1 为 0。
- stage 混淆最大的是 `desire -> interest`，共 10 条；模型预测明显偏向 `interest`。
- `next_state_prediction` 输入显式包含 current_state/current_aida_stage/current_bdi，这是设计选择，不是数据生成 bug；它让模型学习 transition，而不是从裸图重新识别当前状态。

## A. intent_label 类别分布

### A(a) train/eval 分布与 per-class F1

| intent_label | train_count | eval_count | eval_F1 |
|---|---|---|---|
| `compare_value_for_money` | 15 | 1 | 0.000 |
| `confirm_choice` | 163 | 14 | 0.414 |
| `explore_options` | 87 | 7 | 0.500 |
| `leave_without_purchase` | 15 | 2 | 0.000 |
| `negotiate_price` | 50 | 5 | 0.000 |
| `request_demonstration` | 81 | 12 | 0.333 |
| `seek_reassurance` | 82 | 9 | 0.000 |

### A(b) 样本数 < 10 的稀有类别

- Train rare: 无
- Eval rare: `compare_value_for_money`=1, `explore_options`=7, `leave_without_purchase`=2, `negotiate_price`=5, `seek_reassurance`=9

### A(c) 样本数与 F1 相关性

| count source | Pearson corr(count,F1) | Spearman corr(count,F1) |
|---|---|---|
| train_count | 0.719 | 0.775 |
| eval_count/support | 0.659 | 0.611 |

解释：相关性为正，说明样本数确实影响 F1；但它不是唯一原因。比如 `seek_reassurance` 在 train 中有 82 条、eval 中有 9 条，F1 仍为 0，说明标签语义边界和视觉证据不足也是主因。

## B. AIDA stage 混淆模式

### B(a) 4x4 confusion matrix

| gold \ pred | `attention` | `interest` | `desire` | `action` |
|---|---|---|---|---|
| `attention` | 3 | 0 | 0 | 1 |
| `interest` | 0 | 27 | 0 | 0 |
| `desire` | 2 | 10 | 0 | 0 |
| `action` | 0 | 6 | 0 | 1 |

### B(b) 最大混淆对

- `desire` -> `interest`: 10 条
- `action` -> `interest`: 6 条
- `desire` -> `attention`: 2 条
- `attention` -> `action`: 1 条

### B(c) gold vs prediction 分布

| stage | gold_count | pred_count | gold_pct | pred_pct |
|---|---|---|---|---|
| `attention` | 4 | 5 | 8.00% | 10.00% |
| `interest` | 27 | 43 | 54.00% | 86.00% |
| `desire` | 12 | 0 | 24.00% | 0.00% |
| `action` | 7 | 2 | 14.00% | 4.00% |

判断：模型明显偏向 `interest`；50 条里预测 `interest` 的比例远高于 gold。

## C. next_state vs user_intent 输入差异核查

### C(a) user_intent 输入字段列表

- 3 张图像。
- Scene 简述。
- 指令：只从 visible behavior 推断当前用户状态，不选择销售动作。
- 要求输出：stage、intent_label、visual_summary、engagement_pattern、gaze_and_attention、body_and_hands、belief、desire、intention。
- 不包含 current_state/current_bdi/candidate action/reward。

### C(b) next_state_prediction 输入字段列表

- 3 张图像。
- The customer current state：stage、visible evidence、engagement pattern、gaze and attention、body and hands、belief、desire、intention。
- 一个候选 intervention：action key、act、params。
- terminal realization：surface_text、screen、voice_style、light。
- concrete execution plan：physical_action、utterance。
- 要求输出：next_stage、next_belief、next_desire、next_intention、risk、benefit、reward。

### C(c) next_state 是否包含 current_state/current_aida_stage/current_bdi

| field | present in next_state input? | evidence |
|---|---|---|
| current_state / visible evidence | yes | `The customer's current state is:` 后含 visible evidence 等字段 |
| current_aida_stage | yes | `- stage: interest` 等 |
| current_bdi | yes | `- belief:` / `- desire:` / `- intention:` |

### C(d) 设计判断

这是 task design choice，不是 data generation bug。`next_state_prediction` 本来是在给定当前状态和候选动作后学习 transition；它不是裸图状态识别任务。因此它比 `user_intent` 更容易，也解释了为什么 next_state 指标显著高于 user_intent。

## D. user_intent BDI desire/intention 32% 归因

### D(a-c) 三字段 soft match rate

| field | exact_match | LLM yes on non-exact | LLM no on non-exact | soft_match |
|---|---|---|---|---|
| `belief` | 40.00% | 8 | 22 | 56.00% |
| `desire` | 32.00% | 0 | 34 | 32.00% |
| `intention` | 32.00% | 0 | 34 | 32.00% |

### D(d) 语义距离例子

#### `belief`

1. `piwm_0b0d31c38b` judge=`yes`
   - ground truth: The product is promising, but fit or usage experience must be confirmed.
   - prediction: The product is promising, but fit or usage experience needs confirmation.
2. `piwm_1cc2c20d89` judge=`no`
   - ground truth: A suitable option may be close, but staff input is needed before deciding.
   - prediction: The product is interesting, but its value-for-money is not yet justified.
3. `piwm_3549e65d37` judge=`no`
   - ground truth: The shopper may be ready for service, but still needs final confirmation.
   - prediction: The product is promising, but fit or usage experience must be confirmed.

#### `desire`

1. `piwm_0b0d31c38b` judge=`no`
   - ground truth: see how the product works
   - prediction: confirm the preferred choice
2. `piwm_1cc2c20d89` judge=`no`
   - ground truth: confirm the preferred choice
   - prediction: see how the product works
3. `piwm_23563ed080` judge=`no`
   - ground truth: gain reassurance before deciding
   - prediction: see how the product works

#### `intention`

1. `piwm_0b0d31c38b` judge=`no`
   - ground truth: ask for a demonstration
   - prediction: move toward confirming the choice
2. `piwm_1cc2c20d89` judge=`no`
   - ground truth: move toward confirming the choice
   - prediction: ask for a demonstration
3. `piwm_23563ed080` judge=`no`
   - ground truth: look for reassurance or clarification
   - prediction: ask for a demonstration

## 文件与校验

- `reports/stage1_eval_full_inference.jsonl` sha256 `15d62284fc88b05627579c754f376fe04c68b0a24bf2e15976eb2ab5a9205d07`
- `reports/stage1_task_level_eval_intermediate.json` sha256 `c3e922e037df894e1ede56f0c2ebbda64148e168855c35ea2610cf5576fc749f`
- `reports/stage1_bdi_llm_judge.jsonl` sha256 `8313c7b4afe534a033c4dcae7c025a30128fd27ae2c9bd7e9f750ec9bb6947ec`
