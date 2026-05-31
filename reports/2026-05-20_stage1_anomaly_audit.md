# Stage-1 Checkpoint 数字异常验证

本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

## 结论先行

- Stage-1 checkpoint `checkpoint-432` 训练是正常完成的；最终 `eval_loss=0.01000058`、`eval_token_acc=0.99403809`。
- 没有发现 eval JSONL 与 train JSONL 的整行内容重叠：sha256 交集为 `0`。
- 进一步按 parent scene id 检查，train/val 原始场景也没有交集：parent overlap 为 `0`。
- 但 `trainer_state.json` 只有最终一次 eval；没有训练初始或中途 eval，所以不能证明 base model 一开始就能做到 `<0.1`。
- 数字偏低的主要可疑原因不是 split 泄漏，而是 Stage-1 任务本身高度模板化、输出格式封闭，尤其 `next_state_prediction` 的字段和值非常规则。
- 端到端抽测 3 条 eval：2 条 next-state 输出与 ground truth 完全一致；1 条 user-intent 的结构和 stage 正确，但 `intent_label/desire/intention` 偏向了相邻标签。

## 任务 A：eval set 内容审计

### A(a) 训练时实际使用的 JSONL

Checkpoint: `checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1/v5-20260520-180808/checkpoint-432`
Run args: `checkpoints/stage1_qwen25vl_7b_a100_2gpu_v1/v5-20260520-180808/args.json`

Train JSONL:
- `data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_train_v1.jsonl`
- `data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_train_v1.jsonl`

Eval JSONL:
- `data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl`
- `data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl`

关键训练参数：

| key | value |
|---|---|
| `model` | `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct` |
| `max_length` | `8192` |
| `tuner_type` | `lora` |
| `logging_steps` | `5` |
| `eval_strategy` | `steps` |
| `save_strategy` | `steps` |
| `num_train_epochs` | `3.0` |

### A(b) train/eval 内容重叠检查

| check | result |
|---|---:|
| train rows by line hash | 2309 |
| eval rows by line hash | 235 |
| exact line sha256 overlap | 0 |
| train parent scene ids | 493 |
| eval parent scene ids | 50 |
| parent scene id overlap | 0 |

解释：整行 sha256 无重叠只能证明没有完全相同训练行；parent scene id 无重叠进一步说明 eval 不复用 train 的同一原始场景。

### A(c) eval 行数与任务类型分布

| file | rows | task distribution | stale `meta.split` values |
|---|---:|---|---|
| `data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | `{'user_intent': 50}` | `{'train': 33, 'ood_product': 2, 'ood_persona': 9, 'dev': 4, 'test': 2}` |
| `data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | `{'next_state_prediction': 185}` | `{'train': 123, 'ood_product': 8, 'ood_persona': 32, 'dev': 14, 'test': 8}` |

Eval total: `235` rows, task distribution: `{'user_intent': 50, 'next_state_prediction': 185}`.

注意：eval 文件里的 `meta.split` 是历史元数据，出现 `train/dev/test/ood_*` 混合值；训练实际 split 由文件路径决定，ms-swift 确实加载了 `val_dataset` 的 235 行。这是元数据陈旧问题，建议后续清理，但不构成本次 train/eval 内容重叠。

### A(d) 5 条 eval 样本完整 JSON

#### Eval sample 1: `user_intent` / `piwm_0b0d31c38b`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在零售店内。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    },
    {
      "role": "assistant",
      "content": "<stage>interest</stage>\n<intent_label>request_demonstration</intent_label>\n<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。</visual_summary>\n<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。</engagement_pattern>\n<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。</gaze_and_attention>\n<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。</body_and_hands>\n<belief>The product is promising, but fit or usage experience must be confirmed.</belief>\n<desire>see how the product works</desire>\n<intention>ask for a demonstration</intention>"
    }
  ],
  "images": [
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/000.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/001.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "piwm_0b0d31c38b",
  "weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable",
    "stage": "interest",
    "intent_label": "request_demonstration"
  },
  "_source_file": "data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl",
  "_line_no": 1
}
```

#### Eval sample 2: `user_intent` / `piwm_1cc2c20d89`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在零售店内。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    },
    {
      "role": "assistant",
      "content": "<stage>action</stage>\n<intent_label>confirm_choice</intent_label>\n<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。</visual_summary>\n<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>\n<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>\n<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>\n<belief>A suitable option may be close, but staff input is needed before deciding.</belief>\n<desire>confirm the preferred choice</desire>\n<intention>move toward confirming the choice</intention>"
    }
  ],
  "images": [
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_1cc2c20d89/frames/000.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_1cc2c20d89/frames/001.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "piwm_1cc2c20d89",
  "weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable",
    "stage": "action",
    "intent_label": "confirm_choice"
  },
  "_source_file": "data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl",
  "_line_no": 2
}
```

#### Eval sample 3: `user_intent` / `piwm_23563ed080`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在零售店内。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    },
    {
      "role": "assistant",
      "content": "<stage>interest</stage>\n<intent_label>seek_reassurance</intent_label>\n<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是家电展示区，可见判断应围绕功能覆盖、能耗、安装条件和长期使用成本是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>\n<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。</engagement_pattern>\n<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。</gaze_and_attention>\n<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>\n<belief>The product is interesting, but its value-for-money is not yet justified.</belief>\n<desire>gain reassurance before deciding</desire>\n<intention>look for reassurance or clarification</intention>"
    }
  ],
  "images": [
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_23563ed080/frames/000.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_23563ed080/frames/001.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_23563ed080/frames/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "piwm_23563ed080",
  "weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable",
    "stage": "interest",
    "intent_label": "seek_reassurance"
  },
  "_source_file": "data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl",
  "_line_no": 3
}
```

#### Eval sample 4: `next_state_prediction` / `piwm_0b0d31c38b#Elicit_b1166d372e5e`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe customer's current state is:\n- stage: interest\n- visible evidence: 顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。\n- engagement pattern: 顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。\n- gaze and attention: 视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。\n- body and hands: 身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。\n- belief: The product is promising, but fit or usage experience must be confirmed.\n- desire: see how the product works\n- intention: ask for a demonstration\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您想先看价格、功能，还是使用场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}\n- voice_style: warm\n- light: neutral_prompt_color\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 您想先看价格、功能，还是使用场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>desire</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.83</reward>"
    }
  ],
  "images": [
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/000.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/001.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_0b0d31c38b#Elicit_b1166d372e5e",
  "weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_0b0d31c38b",
    "candidate_action": "Elicit_b1166d372e5e",
    "candidate_act": "Elicit",
    "candidate_params": {
      "openness": "open",
      "slot": "need_focus"
    },
    "no_intervention_branch": false,
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  },
  "_source_file": "data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl",
  "_line_no": 1
}
```

#### Eval sample 5: `next_state_prediction` / `piwm_0b0d31c38b#Inform_5ff00ba15ca5`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe customer's current state is:\n- stage: interest\n- visible evidence: 顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。\n- engagement pattern: 顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。\n- gaze and attention: 视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。\n- body and hands: 身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。\n- belief: The product is promising, but fit or usage experience must be confirmed.\n- desire: see how the product works\n- intention: ask for a demonstration\n\nConsider one candidate intervention: Inform_5ff00ba15ca5\n\nDialogue-act layer for this candidate:\n- act: Inform\n- params: {'content_type': 'demo', 'depth': 'brief'}\n\nTerminal realization for this candidate:\n- surface_text: 我给您演示一下这款的关键细节。\n- screen: {'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None}\n- voice_style: neutral\n- light: follow_demo_animation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 我给您演示一下这款的关键细节。\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>desire</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>"
    }
  ],
  "images": [
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/000.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/001.jpg",
    "/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_0b0d31c38b#Inform_5ff00ba15ca5",
  "weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_0b0d31c38b",
    "candidate_action": "Inform_5ff00ba15ca5",
    "candidate_act": "Inform",
    "candidate_params": {
      "content_type": "demo",
      "depth": "brief"
    },
    "no_intervention_branch": false,
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  },
  "_source_file": "data/official/ms_swift_server_resolved/piwm_train_stage1_next_state_prediction_val_v1.jsonl",
  "_line_no": 2
}
```

## 任务 B：trainer_state.json 解读

### B(a) loss 曲线

说明：`trainer_state.json` 没有保存每一个 optimizer step 的 loss，只保存了 `logging_steps=5` 的日志点，以及 step 1 和最终 eval。因此下表是 trainer_state 中的完整 recorded curve。

| step | epoch | train_loss | token_acc | learning_rate | eval_loss | eval_token_acc |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.0069204152 | 1.7715094 | 0.66651746 | 1.9999736e-05 |  |  |
| 5 | 0.034602076 | 1.4698017 | 0.70369881 | 1.999339e-05 |  |  |
| 10 | 0.069204152 | 1.2762444 | 0.7318537 | 1.9973569e-05 |  |  |
| 15 | 0.10380623 | 1.4459026 | 0.6812399 | 1.9940563e-05 |  |  |
| 20 | 0.1384083 | 1.387837 | 0.71192395 | 1.9894416e-05 |  |  |
| 25 | 0.17301038 | 1.1820868 | 0.74194226 | 1.9835189e-05 |  |  |
| 30 | 0.20761246 | 1.0254972 | 0.77208361 | 1.976296e-05 |  |  |
| 35 | 0.24221453 | 1.1590534 | 0.73769223 | 1.9677825e-05 |  |  |
| 40 | 0.27681661 | 0.85479279 | 0.78764437 | 1.9579895e-05 |  |  |
| 45 | 0.31141869 | 1.1536745 | 0.74859627 | 1.9469301e-05 |  |  |
| 50 | 0.34602076 | 0.65169611 | 0.84275534 | 1.9346189e-05 |  |  |
| 55 | 0.38062284 | 0.84815388 | 0.79487946 | 1.9210722e-05 |  |  |
| 60 | 0.41522491 | 0.80519953 | 0.81211335 | 1.9063078e-05 |  |  |
| 65 | 0.44982699 | 0.55903816 | 0.85472371 | 1.8903453e-05 |  |  |
| 70 | 0.48442907 | 0.68616972 | 0.82963907 | 1.8732058e-05 |  |  |
| 75 | 0.51903114 | 0.4497365 | 0.88233268 | 1.8549119e-05 |  |  |
| 80 | 0.55363322 | 0.52424121 | 0.86485633 | 1.8354878e-05 |  |  |
| 85 | 0.58823529 | 0.42138472 | 0.88544283 | 1.8149593e-05 |  |  |
| 90 | 0.62283737 | 0.45543032 | 0.88308562 | 1.7933533e-05 |  |  |
| 95 | 0.65743945 | 0.37883472 | 0.89143217 | 1.7706986e-05 |  |  |
| 100 | 0.69204152 | 0.29662576 | 0.92033253 | 1.7470251e-05 |  |  |
| 105 | 0.7266436 | 0.45736918 | 0.87486975 | 1.722364e-05 |  |  |
| 110 | 0.76124567 | 0.33370743 | 0.90689552 | 1.6967479e-05 |  |  |
| 115 | 0.79584775 | 0.23861828 | 0.93274759 | 1.6702108e-05 |  |  |
| 120 | 0.83044983 | 0.29329467 | 0.92209026 | 1.6427876e-05 |  |  |
| 125 | 0.8650519 | 0.21160381 | 0.93996793 | 1.6145147e-05 |  |  |
| 130 | 0.89965398 | 0.16464257 | 0.95535059 | 1.5854294e-05 |  |  |
| 135 | 0.93425606 | 0.16247457 | 0.95325663 | 1.5555702e-05 |  |  |
| 140 | 0.96885813 | 0.14530282 | 0.96133132 | 1.5249766e-05 |  |  |
| 145 | 1 | 0.14228444 | 0.96637122 | 1.4936889e-05 |  |  |
| 150 | 1.0346021 | 0.099009383 | 0.97406431 | 1.4617486e-05 |  |  |
| 155 | 1.0692042 | 0.07590946 | 0.97755319 | 1.4291979e-05 |  |  |
| 160 | 1.1038062 | 0.11002495 | 0.9709224 | 1.3960798e-05 |  |  |
| 165 | 1.1384083 | 0.066673672 | 0.98256071 | 1.362438e-05 |  |  |
| 170 | 1.1730104 | 0.091564643 | 0.97622478 | 1.3283172e-05 |  |  |
| 175 | 1.2076125 | 0.058490694 | 0.98391654 | 1.2937623e-05 |  |  |
| 180 | 1.2422145 | 0.070493579 | 0.97869797 | 1.258819e-05 |  |  |
| 185 | 1.2768166 | 0.075385749 | 0.98062016 | 1.2235337e-05 |  |  |
| 190 | 1.3114187 | 0.055519938 | 0.98343121 | 1.1879528e-05 |  |  |
| 195 | 1.3460208 | 0.069716567 | 0.98082784 | 1.1521234e-05 |  |  |
| 200 | 1.3806228 | 0.048306489 | 0.98572586 | 1.1160929e-05 |  |  |
| 205 | 1.4152249 | 0.045763081 | 0.9860496 | 1.079909e-05 |  |  |
| 210 | 1.449827 | 0.048261911 | 0.98540529 | 1.0436194e-05 |  |  |
| 215 | 1.4844291 | 0.043388858 | 0.98652151 | 1.0072721e-05 |  |  |
| 220 | 1.5190311 | 0.037893605 | 0.98887588 | 9.7091528e-06 |  |  |
| 225 | 1.5536332 | 0.040064609 | 0.98906069 | 9.3459687e-06 |  |  |
| 230 | 1.5882353 | 0.03031233 | 0.99003287 | 8.9836492e-06 |  |  |
| 235 | 1.6228374 | 0.039892551 | 0.98805195 | 8.6226733e-06 |  |  |
| 240 | 1.6574394 | 0.03857429 | 0.98760734 | 8.2635182e-06 |  |  |
| 245 | 1.6920415 | 0.033728653 | 0.98979044 | 7.9066587e-06 |  |  |
| 250 | 1.7266436 | 0.037913799 | 0.98773476 | 7.5525666e-06 |  |  |
| 255 | 1.7612457 | 0.02468385 | 0.99199278 | 7.2017099e-06 |  |  |
| 260 | 1.7958478 | 0.031286168 | 0.99031069 | 6.8545524e-06 |  |  |
| 265 | 1.8304498 | 0.039658788 | 0.9882393 | 6.5115532e-06 |  |  |
| 270 | 1.8650519 | 0.023022386 | 0.99301784 | 6.1731657e-06 |  |  |
| 275 | 1.899654 | 0.035001612 | 0.98904758 | 5.8398371e-06 |  |  |
| 280 | 1.9342561 | 0.021773167 | 0.99263843 | 5.5120082e-06 |  |  |
| 285 | 1.9688581 | 0.018126225 | 0.99325301 | 5.1901123e-06 |  |  |
| 290 | 2 | 0.026766589 | 0.99014835 | 4.874575e-06 |  |  |
| 295 | 2.0346021 | 0.024787104 | 0.99090909 | 4.5658134e-06 |  |  |
| 300 | 2.0692042 | 0.015265749 | 0.99543226 | 4.2642356e-06 |  |  |
| 305 | 2.1038062 | 0.015830758 | 0.99433144 | 3.9702405e-06 |  |  |
| 310 | 2.1384083 | 0.018231316 | 0.99485212 | 3.6842165e-06 |  |  |
| 315 | 2.1730104 | 0.019954771 | 0.99354497 | 3.4065418e-06 |  |  |
| 320 | 2.2076125 | 0.018737791 | 0.99426126 | 3.1375836e-06 |  |  |
| 325 | 2.2422145 | 0.018802397 | 0.99343936 | 2.8776974e-06 |  |  |
| 330 | 2.2768166 | 0.020571333 | 0.99362072 | 2.6272266e-06 |  |  |
| 335 | 2.3114187 | 0.016514331 | 0.99376947 | 2.3865026e-06 |  |  |
| 340 | 2.3460208 | 0.01659936 | 0.99296394 | 2.1558434e-06 |  |  |
| 345 | 2.3806228 | 0.020011038 | 0.99256542 | 1.935554e-06 |  |  |
| 350 | 2.4152249 | 0.016614848 | 0.9936119 | 1.7259256e-06 |  |  |
| 355 | 2.449827 | 0.014134043 | 0.99527595 | 1.5272354e-06 |  |  |
| 360 | 2.4844291 | 0.018128431 | 0.9936449 | 1.339746e-06 |  |  |
| 365 | 2.5190311 | 0.016111392 | 0.99408226 | 1.1637052e-06 |  |  |
| 370 | 2.5536332 | 0.015105602 | 0.99555418 | 9.9934588e-07 |  |  |
| 375 | 2.5882353 | 0.016522138 | 0.99498081 | 8.4688521e-07 |  |  |
| 380 | 2.6228374 | 0.015870987 | 0.99390181 | 7.0652476e-07 |  |  |
| 385 | 2.6574394 | 0.010973365 | 0.99700951 | 5.7845008e-07 |  |  |
| 390 | 2.6920415 | 0.012540594 | 0.99593452 | 4.6283049e-07 |  |  |
| 395 | 2.7266436 | 0.016038415 | 0.99519937 | 3.5981884e-07 |  |  |
| 400 | 2.7612457 | 0.012771672 | 0.99610056 | 2.6955129e-07 |  |  |
| 405 | 2.7958478 | 0.014276469 | 0.99539122 | 1.921472e-07 |  |  |
| 410 | 2.8304498 | 0.012939738 | 0.99500278 | 1.2770887e-07 |  |  |
| 415 | 2.8650519 | 0.016443175 | 0.99368507 | 7.6321499e-08 |  |  |
| 420 | 2.899654 | 0.012979701 | 0.99622682 | 3.8053019e-08 |  |  |
| 425 | 2.9342561 | 0.0075146288 | 0.99816222 | 1.295402e-08 |  |  |
| 430 | 2.9688581 | 0.015092906 | 0.99469604 | 1.0576807e-09 |  |  |
| 432 | 2.982699 |  |  |  | 0.010000576 | 0.99403809 |

### B(b) eval_loss 是一开始就低，还是逐步降下来的？

`trainer_state.json` 中 eval 记录数量为 `1`。唯一 eval 记录在 step `432`，即训练结束后。

因此不能用这次日志判断 base model 是否一开始就 `<0.1`。要回答这个问题，需要单独跑一次 `checkpoint-0/base` 或未训练 LoRA 的 eval。

### B(c) train_loss 与 eval_loss gap 何时反向？

最终可比较点：step `430` 的 logged train_loss=`0.01509291`，最终 eval_loss=`0.01000058`。eval_loss 低于最终 logged train_loss。
但由于没有中途 eval_loss 曲线，无法判断 gap 是何时反向的。当前只能说：最终 eval_loss 低于末尾 logged train_loss。

## 任务 C：3 条 eval 样本端到端推理

推理方式：加载 `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct` + LoRA adapter `checkpoint-432`，对 3 条 eval JSONL 用同一组图片和 user prompt 做 greedy generation。完整原始输出已保存到：`/root/lanyun-fs/ProactiveIntentWorldModel/reports/stage1_eval_infer3_outputs.json`。

### Inference sample 1: `user_intent` / `piwm_0b0d31c38b`

**Input**

```text
You are observing a short customer-behavior window.

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
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.
- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.
- belief, desire, and intention must be short customer-state clauses, not salesperson advice.
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
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、版型覆盖、垂坠感和搭配效果。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、版型覆盖、垂坠感和搭配效果是否被确认。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、版型覆盖、垂坠感和搭配效果产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、版型覆盖、垂坠感和搭配效果。</body_and_hands>
<belief>The product is promising, but fit or usage experience must be confirmed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### Inference sample 2: `next_state_prediction` / `piwm_0b0d31c38b#Elicit_b1166d372e5e`

**Input**

```text
You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: interest
- visible evidence: 顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。
- engagement pattern: 顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。
- gaze and attention: 视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。
- body and hands: 身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。
- belief: The product is promising, but fit or usage experience must be confirmed.
- desire: see how the product works
- intention: ask for a demonstration

Consider one candidate intervention: Elicit_b1166d372e5e

Dialogue-act layer for this candidate:
- act: Elicit
- params: {'openness': 'open', 'slot': 'need_focus'}

Terminal realization for this candidate:
- surface_text: 您想先看价格、功能，还是使用场景？
- screen: {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}
- voice_style: warm
- light: neutral_prompt_color

Concrete execution plan for this candidate:
- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。
- utterance: 您想先看价格、功能，还是使用场景？

Predict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:
<next_stage>...</next_stage>
<next_belief>...</next_belief>
<next_desire>...</next_desire>
<next_intention>...</next_intention>
<risk>...</risk>
<benefit>...</benefit>
<reward>...</reward>

- next_stage must be one of: attention, interest, desire, action.
- risk and benefit must each be one of: low, medium, high.
- reward must be a number in [-1.00, 1.00] with two decimal places.
- all textual spans must be a single short clause in English.
```

**Ground truth**

```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.83</reward>
```

**Model output**

```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.83</reward>
```

### Inference sample 3: `next_state_prediction` / `piwm_0b0d31c38b#Inform_5ff00ba15ca5`

**Input**

```text
You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





The customer's current state is:
- stage: interest
- visible evidence: 顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。
- engagement pattern: 顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。
- gaze and attention: 视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。
- body and hands: 身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。
- belief: The product is promising, but fit or usage experience must be confirmed.
- desire: see how the product works
- intention: ask for a demonstration

Consider one candidate intervention: Inform_5ff00ba15ca5

Dialogue-act layer for this candidate:
- act: Inform
- params: {'content_type': 'demo', 'depth': 'brief'}

Terminal realization for this candidate:
- surface_text: 我给您演示一下这款的关键细节。
- screen: {'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None}
- voice_style: neutral
- light: follow_demo_animation

Concrete execution plan for this candidate:
- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。
- utterance: 我给您演示一下这款的关键细节。

Predict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:
<next_stage>...</next_stage>
<next_belief>...</next_belief>
<next_desire>...</next_desire>
<next_intention>...</next_intention>
<risk>...</risk>
<benefit>...</benefit>
<reward>...</reward>

- next_stage must be one of: attention, interest, desire, action.
- risk and benefit must each be one of: low, medium, high.
- reward must be a number in [-1.00, 1.00] with two decimal places.
- all textual spans must be a single short clause in English.
```

**Ground truth**

```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.80</reward>
```

**Model output**

```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.80</reward>
```

## 审计判断

1. 当前异常数字不是由明显的 train/eval 行级泄漏造成；整行 hash 和 parent scene id 都无重叠。
2. `eval_loss=0.0100` 不能被解释为 base model 原本就会，因为本次没有初始 eval。
3. 端到端结果显示 next-state 任务非常容易被模板化学习，至少抽样中两条完全一致；这能解释低 eval_loss 的一部分。
4. user-intent 任务并非完全无误，抽样第一条 stage 正确但 intent_label 与 BDI 偏移，说明低 token-level loss 不等于所有结构字段都正确。
5. 建议下一步在 PI 决策后再做：base model zero-shot eval、字段级 exact-match/F1、按任务类型分别计算 eval loss/field accuracy。