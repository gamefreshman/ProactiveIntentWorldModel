本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

# Stage-1 Task-Level Evaluation

## 结论先行

- 全量 235 条 eval 已完成推理，parse error rate = `0.00%`，没有超过 5% 停止阈值。
- 整体判定：**FAIL（标红：未达到进入 Stage-2 的自动证据标准）**。本报告只给证据，不自动决定是否进入 Stage-2。
- `user_intent` 是主要短板：AIDA stage macro F1 = `0.415`，intent_label macro F1 = `0.178`。
- `next_state_prediction` 表现较强：next-stage macro F1 = `0.914`，reward MAE = `0.0343`，Spearman = `0.9710`。
- BDI overall soft match = `0.830`；但 user_intent 的 desire/intention soft match 只有 32%，说明模型经常把顾客意图解释成相邻意图。

## A. 全量推理产物

- checkpoint: `/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1/v5-20260520-180808/checkpoint-432`
- full inference JSONL: `reports/stage1_eval_full_inference.jsonl`
- LLM judge JSONL: `reports/stage1_bdi_llm_judge.jsonl`
- full inference sha256: `15d62284fc88b05627579c754f376fe04c68b0a24bf2e15976eb2ab5a9205d07`
- judge sha256: `8313c7b4afe534a033c4dcae7c025a30128fd27ae2c9bd7e9f750ec9bb6947ec`

| task | parse_status | count |
|---|---|---:|
| `user_intent` | `parsed_ok` | 50 |
| `next_state_prediction` | `parsed_ok` | 185 |

Parse error ratio: `0.00%`.

## B. user_intent 任务评估（50 条）

### B(a) AIDA stage

- macro F1: `0.415`
- accuracy: `0.620`

| label | support | pred_count | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|
| `action` | 7 | 2 | 0.500 | 0.143 | 0.222 |
| `attention` | 4 | 5 | 0.600 | 0.750 | 0.667 |
| `desire` | 12 | 0 | 0.000 | 0.000 | 0.000 |
| `interest` | 27 | 43 | 0.628 | 1.000 | 0.771 |

### B(b) intent_label

- macro F1: `0.178`
- accuracy: `0.320`

| label | support | pred_count | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|
| `compare_value_for_money` | 1 | 0 | 0.000 | 0.000 | 0.000 |
| `confirm_choice` | 14 | 15 | 0.400 | 0.429 | 0.414 |
| `explore_options` | 7 | 5 | 0.600 | 0.429 | 0.500 |
| `leave_without_purchase` | 2 | 0 | 0.000 | 0.000 | 0.000 |
| `negotiate_price` | 5 | 0 | 0.000 | 0.000 | 0.000 |
| `request_demonstration` | 12 | 30 | 0.233 | 0.583 | 0.333 |
| `seek_reassurance` | 9 | 0 | 0.000 | 0.000 | 0.000 |

### B(c) BDI exact + LLM-as-judge soft match

LLM judge prompt: `ground truth 和 prediction 是否语义等价，只输出 yes/no`。Exact match 的字段直接计入 soft yes；非 exact 字段由 Qwen2.5-VL-7B-Instruct 作为文本 judge 输出 yes/no。

| task | field | exact match | LLM yes on non-exact | LLM no on non-exact | soft match |
|---|---|---:|---:|---:|---:|
| `user_intent` | `belief` | 40.00% | 8 | 22 | 56.00% |
| `user_intent` | `desire` | 32.00% | 0 | 34 | 32.00% |
| `user_intent` | `intention` | 32.00% | 0 | 34 | 32.00% |

### B(d) intent_label confusion matrix

| gold \ pred | `compare_value_for_money` | `confirm_choice` | `explore_options` | `leave_without_purchase` | `negotiate_price` | `request_demonstration` | `seek_reassurance` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `compare_value_for_money` | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `confirm_choice` | 0 | 6 | 0 | 0 | 0 | 8 | 0 |
| `explore_options` | 0 | 0 | 3 | 0 | 0 | 4 | 0 |
| `leave_without_purchase` | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| `negotiate_price` | 0 | 1 | 0 | 0 | 0 | 4 | 0 |
| `request_demonstration` | 0 | 5 | 0 | 0 | 0 | 7 | 0 |
| `seek_reassurance` | 0 | 2 | 1 | 0 | 0 | 6 | 0 |

## C. next_state_prediction 任务评估（185 条）

### C(a) next_aida_stage

- macro F1: `0.914`
- accuracy: `0.962`

| label | support | pred_count | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|
| `action` | 13 | 9 | 0.889 | 0.615 | 0.727 |
| `attention` | 54 | 56 | 0.946 | 0.981 | 0.964 |
| `desire` | 91 | 92 | 0.978 | 0.989 | 0.984 |
| `interest` | 27 | 28 | 0.964 | 1.000 | 0.982 |

### C(b) preference_score / reward

- reward rows: `185`
- MAE: `0.0343`
- Spearman corr: `0.9710`

### C(c) next_BDI exact + LLM-as-judge soft match

| task | field | exact match | LLM yes on non-exact | LLM no on non-exact | soft match |
|---|---|---:|---:|---:|---:|
| `next_state_prediction` | `belief` | 94.59% | 0 | 10 | 94.59% |
| `next_state_prediction` | `desire` | 94.59% | 0 | 10 | 94.59% |
| `next_state_prediction` | `intention` | 94.59% | 0 | 10 | 94.59% |

## D. Brief 第 7 节阈值判定

| check | threshold | value | result |
|---|---:|---:|---|
| aida_stage macro F1 | > 0.6 | 0.415 | **FAIL** |
| next_aida_stage macro F1 | > 0.6 | 0.914 | PASS |
| intent_label macro F1 | > 0.5 | 0.178 | **FAIL** |
| BDI LLM-judge overall soft match | > 0.7 | 0.830 | PASS |

结论：本次 task-level evaluation 至少有 `aida_stage macro F1` 和 `intent_label macro F1` 未达标，因此报告按要求标红为 FAIL；不自动进入 Stage-2。

## E. 错误样本归因

| bucket | count |
|---|---:|
| `next_state_prediction::preference 错` | 8 |
| `next_state_prediction::多个错` | 10 |
| `user_intent::bdi 错` | 5 |
| `user_intent::多个错` | 38 |

### user_intent::stage 错

无样本。

### user_intent::intent 错

无样本。

### user_intent::bdi 错

#### 1. `piwm_8916c58066`

**Input excerpt**

```text
<image><image><image>You are observing a short customer-behavior window.

Scene: 顾客在零售店内。

Below are 3 frames sampled from a streaming camera, in chronological order.





Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.

Output the following fields, in this exact order, each on its own line:
<stage>...</stage>
<intent_label>...</intent_label>
<visual_summary>...</visual_summary>
<engagement_pattern>...</engagement_pattern>
<gaze_and_attention>...</gaze_and_attention>
<body_and_hands>...</body_and_hands>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>

- stage must be one of: attention, interest, desire, action.
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, n
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、光泽、尺寸和送礼场景获得人工确认。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。</engagement_pattern>
<gaze_and_attention>视线朝向柜台、导购或服务点。</gaze_and_attention>
<body_and_hands>身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。</body_and_hands>
<belief>The shopper may be ready for service, but still needs final confirmation.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

**Model output**

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客向柜台或导购方向移动，说明接近明确咨询或决策。 当前场景是珠宝柜台，可见判断应围绕柜台互动和商品细节是否足以支撑停留意图。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客从浏览转向服务区域，说明当前互动开始影响判断。 移动方向明确，正在前往柜台或导购点。</engagement_pattern>
<gaze_and_attention>视线朝柜台、导购或服务区域移动。 视线变化更关键，重点是柜台方向的视线变化。</gaze_and_attention>
<body_and_hands>身体朝柜台方向前进。 手部可能携带商品、拿起商品或靠近柜台。</body_and_hands>
<belief>Situation may be promising, but confirmation is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### 2. `piwm_4b61cd89e5`

**Input excerpt**

```text
<image><image><image>You are observing a short customer-behavior window.

Scene: 顾客在零售店内。

Below are 3 frames sampled from a streaming camera, in chronological order.





Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.

Output the following fields, in this exact order, each on its own line:
<stage>...</stage>
<intent_label>...</intent_label>
<visual_summary>...</visual_summary>
<engagement_pattern>...</engagement_pattern>
<gaze_and_attention>...</gaze_and_attention>
<body_and_hands>...</body_and_hands>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>

- stage must be one of: attention, interest, desire, action.
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, n
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客反复接触或摆弄商品，说明正在主动评估商品细节。 当前场景是服装陈列区，可见判断应围绕版型、面料、颜色、尺码和搭配场景中需要手部确认的细节。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品有持续直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。</engagement_pattern>
<gaze_and_attention>视线主要集中在商品细节和手部操作位置。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体保持靠近商品，姿态显示评估意愿。 手部反复拿起、放下、调整或触摸商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。</body_and_hands>
<belief>The product details are promising, but tactile or functional confirmation is still needed.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

**Model output**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是服装陈列区，可见判断应围绕手机查询内容与面料、剪裁、版型和搭配场景中需要确认的细节是否产生互动。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对面料、剪裁、版型和搭配，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和版型、面料、颜色、尺码和价格差异之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>
<belief>External prices, reviews, or specifications may change the choice.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### 3. `piwm_7467483f51`

**Input excerpt**

```text
<image><image><image>You are observing a short customer-behavior window.

Scene: 顾客在零售店内。

Below are 3 frames sampled from a streaming camera, in chronological order.





Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.

Output the following fields, in this exact order, each on its own line:
<stage>...</stage>
<intent_label>...</intent_label>
<visual_summary>...</visual_summary>
<engagement_pattern>...</engagement_pattern>
<gaze_and_attention>...</gaze_and_attention>
<body_and_hands>...</body_and_hands>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>

- stage must be one of: attention, interest, desire, action.
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, n
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客反复接触或摆弄商品，说明正在主动评估商品细节。 当前场景是电脑陈列区，可见判断应围绕屏幕尺寸、键盘手感、性能配置、重量和价格差异中需要手部确认的细节。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客与商品有持续直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是屏幕显示、键盘触感、机身重量或接口布局是否被确认。</engagement_pattern>
<gaze_and_attention>视线主要集中在商品细节和手部操作位置。 视线重点应落在屏幕显示、键盘触感、机身重量或接口布局产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体保持靠近商品，姿态显示评估意愿。 手部反复拿起、放下、调整或触摸商品。 手部动作应重点看是否在确认屏幕显示、键盘触感、机身重量或接口布局。</body_and_hands>
<belief>The product details are promising, but tactile or functional confirmation is still needed.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

**Model output**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是电脑陈列区，可见判断应围绕屏幕显示、键盘手感、机身重量和续航表现。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是屏幕显示、键盘手感、机身重量和续航表现是否被确认。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在屏幕显示、键盘手感、机身重量和续航表现产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认屏幕显示、键盘手感、机身重量和续航表现。</body_and_hands>
<belief>The product is promising, but fit or usage experience must be confirmed.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

### user_intent::多个错

#### 1. `piwm_0b0d31c38b`

**Input excerpt**

```text
<image><image><image>You are observing a short customer-behavior window.

Scene: 顾客在零售店内。

Below are 3 frames sampled from a streaming camera, in chronological order.





Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.

Output the following fields, in this exact order, each on its own line:
<stage>...</stage>
<intent_label>...</intent_label>
<visual_summary>...</visual_summary>
<engagement_pattern>...</engagement_pattern>
<gaze_and_attention>...</gaze_and_attention>
<body_and_hands>...</body_and_hands>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>

- stage must be one of: attention, interest, desire, action.
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, n
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。</body_and_hands>
<belief>The product is promising, but fit or usage experience must be confirmed.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

**Model output**

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是手机陈列区，可见判断应围绕拍照、屏幕手感、电池续航和存储空间中需要手部确认的细节。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是拍照、屏幕手感、电池续航和存储空间中需要手部确认的细节，缺少可见反馈时才会转向价格和使用周期。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在拍照、屏幕手感、电池续航和存储空间中需要手部确认的细节。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认拍照、屏幕手感、电池续航和存储空间中的体验细节。</body_and_hands>
<belief>The product is promising, but fit or usage experience needs confirmation.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### 2. `piwm_1cc2c20d89`

**Input excerpt**

```text
<image><image><image>You are observing a short customer-behavior window.

Scene: 顾客在零售店内。

Below are 3 frames sampled from a streaming camera, in chronological order.





Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.

Output the following fields, in this exact order, each on its own line:
<stage>...</stage>
<intent_label>...</intent_label>
<visual_summary>...</visual_summary>
<engagement_pattern>...</engagement_pattern>
<gaze_and_attention>...</gaze_and_attention>
<body_and_hands>...</body_and_hands>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>

- stage must be one of: attention, interest, desire, action.
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, n
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

**Model output**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是护肤品陈列区，可见判断应围绕成分、容量、质地和适合肤质是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对成分、容量、质地和适合肤质，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和肤质适配之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### 3. `piwm_23563ed080`

**Input excerpt**

```text
<image><image><image>You are observing a short customer-behavior window.

Scene: 顾客在零售店内。

Below are 3 frames sampled from a streaming camera, in chronological order.





Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.

Output the following fields, in this exact order, each on its own line:
<stage>...</stage>
<intent_label>...</intent_label>
<visual_summary>...</visual_summary>
<engagement_pattern>...</engagement_pattern>
<gaze_and_attention>...</gaze_and_attention>
<body_and_hands>...</body_and_hands>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>

- stage must be one of: attention, interest, desire, action.
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, n
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<stage>interest</stage>
<intent_label>seek_reassurance</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是家电展示区，可见判断应围绕功能覆盖、能耗、安装条件和长期使用成本是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>gain reassurance before deciding</desire>
<intention>look for reassurance or clarification</intention>
```

**Model output**

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是家电展示区，可见判断应围绕功能覆盖、能耗、安装条件和长期使用成本是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

### next_state_prediction::stage 错

无样本。

### next_state_prediction::bdi 错

无样本。

### next_state_prediction::preference 错

#### 1. `piwm_3549e65d37#Hold_eda24b4bb712`

**Input excerpt**

```text
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: action
- visible evidence: 顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。
- engagement pattern: 顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。
- gaze and attention: 视线朝向柜台、导购或服务点。
- body and hands: 身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。
- belief: The shopper may be ready for service, but still needs final confirmation.
- desire: gain reassurance before deciding
- intention: look for reassurance or clarification

Consider one candidate intervention: Hold_eda24b4bb712

Dialogue-act layer for this candidate:
- act: Hold
- params: {'mode': 'silent'}

Terminal realization for this candidate:
- surface_text: 
- screen: {'action': 'idle_minimal', 'cta': None}
- voice_style: silent
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<next_stage>attention</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>low</benefit>
<reward>-0.20</reward>
```

**Model output**

```text
<next_stage>attention</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>low</benefit>
<reward>-0.25</reward>
```

#### 2. `piwm_5883d29028#Hold_eda24b4bb712`

**Input excerpt**

```text
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: attention
- visible evidence: 顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、光泽、尺寸和送礼场景获得人工确认。视角为斜角监控/第三方视角。
- engagement pattern: 顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。
- gaze and attention: 视线朝向柜台、导购或服务点。
- body and hands: 身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。
- belief: The shopper may be ready for service, but still needs final confirmation.
- desire: confirm the preferred choice
- intention: move toward confirming the choice

Consider one candidate intervention: Hold_eda24b4bb712

Dialogue-act layer for this candidate:
- act: Hold
- params: {'mode': 'silent'}

Terminal realization for this candidate:
- surface_text: 
- screen: {'action': 'idle_minimal', 'cta': None}
- voice_style: silent
- ligh
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<next_stage>attention</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>low</benefit>
<reward>-0.20</reward>
```

**Model output**

```text
<next_stage>attention</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>low</benefit>
<reward>-0.25</reward>
```

#### 3. `piwm_5883d29028#Recommend_8d7f8993e333`

**Input excerpt**

```text
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: attention
- visible evidence: 顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、光泽、尺寸和送礼场景获得人工确认。视角为斜角监控/第三方视角。
- engagement pattern: 顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。
- gaze and attention: 视线朝向柜台、导购或服务点。
- body and hands: 身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。
- belief: The shopper may be ready for service, but still needs final confirmation.
- desire: confirm the preferred choice
- intention: move toward confirming the choice

Consider one candidate intervention: Recommend_8d7f8993e333

Dialogue-act layer for this candidate:
- act: Recommend
- params: {'target': 'item', 'pressure': 'soft'}

Terminal realization for this candidate:
- surface_text: 这款可以作为一个参考选项。
- screen: {'action': 'highlight_ite
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>medium</risk>
<benefit>high</benefit>
<reward>0.60</reward>
```

**Model output**

```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.85</reward>
```

### next_state_prediction::多个错

#### 1. `piwm_1cc2c20d89#Recommend_9ff23b139b07`

**Input excerpt**

```text
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: action
- visible evidence: 顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。
- engagement pattern: 顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。
- gaze and attention: 视线从商品转向周围空间或导购可能出现的位置。
- body and hands: 身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。
- belief: A suitable option may be close, but staff input is needed before deciding.
- desire: confirm the preferred choice
- intention: move toward confirming the choice

Consider one candidate intervention: Recommend_9ff23b139b07

Dialogue-act layer for this candidate:
- act: Recommend
- params: {'target': 'item', 'pressure': 'firm'}

Terminal realization for this candidate:
- surface_text: 这款最适合您，建议直接选这款。
- screen: {'act
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<next_stage>action</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>medium</risk>
<benefit>high</benefit>
<reward>0.60</reward>
```

**Model output**

```text
<next_stage>attention</next_stage>
<next_belief>The salesperson may be applying too much pressure.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>high</benefit>
<reward>-0.20</reward>
```

#### 2. `piwm_8916c58066#Hold_eda24b4bb712`

**Input excerpt**

```text
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: interest
- visible evidence: 顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、光泽、尺寸和送礼场景获得人工确认。视角为斜角监控/第三方视角。
- engagement pattern: 顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。
- gaze and attention: 视线朝向柜台、导购或服务点。
- body and hands: 身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。
- belief: The shopper may be ready for service, but still needs final confirmation.
- desire: confirm the preferred choice
- intention: move toward confirming the choice

Consider one candidate intervention: Hold_eda24b4bb712

Dialogue-act layer for this candidate:
- act: Hold
- params: {'mode': 'silent'}

Terminal realization for this candidate:
- surface_text: 
- screen: {'action': 'idle_minimal', 'cta': None}
- voice_style: silent
- light
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<next_stage>attention</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>low</benefit>
<reward>-0.20</reward>
```

**Model output**

```text
<next_stage>interest</next_stage>
<next_belief>The decision remains uncertain after the last observation.</next_belief>
<next_desire>gain reassurance before deciding</next_desire>
<next_intention>look for reassurance or clarification</next_intention>
<risk>low</risk>
<benefit>medium</benefit>
<reward>0.30</reward>
```

#### 3. `piwm_cf882269c4#Elicit_b1166d372e5e`

**Input excerpt**

```text
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: action
- visible evidence: 顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是鞋类商品区，可见判断应围绕顾客是否需要围绕尺码、脚感、支撑、鞋型和价格差异获得人工确认。视角为斜角监控/第三方视角。
- engagement pattern: 顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。
- gaze and attention: 视线从商品转向周围空间或导购可能出现的位置。
- body and hands: 身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。
- belief: A suitable option may be close, but staff input is needed before deciding.
- desire: confirm the preferred choice
- intention: move toward confirming the choice

Consider one candidate intervention: Elicit_b1166d372e5e

Dialogue-act layer for this candidate:
- act: Elicit
- params: {'openness': 'open', 'slot': 'need_focus'}

Terminal realization for this candidate:
- surface_text: 您想先看价格、功能，还是使用场景？
- screen: {'action
...[truncated in report; full row is in stage1_eval_full_inference.jsonl]
```

**Ground truth**

```text
<next_stage>desire</next_stage>
<next_belief>The decision remains uncertain after the last observation.</next_belief>
<next_desire>gain reassurance before deciding</next_desire>
<next_intention>look for reassurance or clarification</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.20</reward>
```

**Model output**

```text
<next_stage>action</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.80</reward>
```


## 解释与建议

- 这次不是格式失败：235 条全部 parsed_ok。
- `next_state_prediction` 任务强，尤其 next-stage 和 reward 排序；但它高度模板化，不能单独证明模型已经可靠理解顾客意图。
- `user_intent` 的主要问题是把相邻意图混淆，例如 request_demonstration / confirm_choice / seek_reassurance 之间互相漂移。
- 下一步如果 PI 允许，建议补做 base-model zero-shot task-level eval，以及字段级训练前后对比；但本报告不启动 Stage-2。
