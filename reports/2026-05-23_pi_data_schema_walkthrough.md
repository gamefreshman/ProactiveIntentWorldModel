5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入 operational training/eval/inference/runtime。

# PIWM Stage-1 / Stage-2 Data Schema Walkthrough

本文件只 dump 现有数据与当前代码路径；没有重训、没有改数据、没有改 5-act。

## Attachment Index

- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_user_intent_row1.raw.jsonl`: 原始 JSONL 单行，未截断。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_user_intent_row1.pretty.json`: 同一行 pretty JSON，未删字段。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_user_intent_row1.user_prompt.txt`: `messages[1].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_user_intent_row1.gold_target.txt`: `messages[2].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_next_state_row1.raw.jsonl`: 原始 JSONL 单行，未截断。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_next_state_row1.pretty.json`: 同一行 pretty JSON，未删字段。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_next_state_row1.user_prompt.txt`: `messages[1].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_next_state_row1.gold_target.txt`: `messages[2].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.raw.jsonl`: 原始 JSONL 单行，未截断。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.pretty.json`: 同一行 pretty JSON，未删字段。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.user_prompt.txt`: `messages[1].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.gold_target.txt`: `messages[2].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/greet_aug_sample.raw.jsonl`: 原始 JSONL 单行，未截断。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/greet_aug_sample.pretty.json`: 同一行 pretty JSON，未删字段。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/greet_aug_sample.user_prompt.txt`: `messages[1].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/greet_aug_sample.gold_target.txt`: `messages[2].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/target_test_action_row1.raw.jsonl`: 原始 JSONL 单行，未截断。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/target_test_action_row1.pretty.json`: 同一行 pretty JSON，未删字段。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/target_test_action_row1.user_prompt.txt`: `messages[1].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/target_test_action_row1.gold_target.txt`: `messages[2].content`。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage1_train.sh`: 当前 Stage-1 启动脚本副本。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/eval_ms_swift_checkpoint.py`: 当前 evaluator 完整副本。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/parsers.py`: 当前 parser 完整副本。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/parser_eval_current_diff_vs_head.patch`: parser/evaluator 当前 diff，未截断。
- `reports/attachments/2026-05-23_pi_data_schema_walkthrough/qwen25vl_chat_template.txt`: Qwen2.5-VL tokenizer chat template。

## A. Stage-1 user_intent 任务一条完整样本

### A(a) 原始 JSONL 一行完整内容

```json
{"messages": [{"role": "system", "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."}, {"role": "user", "content": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在零售店内。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."}, {"role": "assistant", "content": "<stage>interest</stage>\n<intent_label>request_demonstration</intent_label>\n<visual_summary>顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。</visual_summary>\n<engagement_pattern>顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。</engagement_pattern>\n<gaze_and_attention>视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。</gaze_and_attention>\n<body_and_hands>身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。</body_and_hands>\n<belief>A companion's approval may influence whether the choice feels safe.</belief>\n<desire>see how the product works</desire>\n<intention>ask for a demonstration</intention>"}], "images": ["/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"], "task": "user_intent", "source_id": "piwm_09df40aae2", "weight": 1.0, "loss_weight": 1.0, "meta": {"split": "train", "qa_status": null, "human_review_status": null, "viewpoint": "salesperson_observable", "stage": "interest", "intent_label": "request_demonstration", "loss_weight": 1.0, "loss_weight_policy": "a3plus_visual_intent_low_confidence"}}
```

### A(b) 字段解释

```json
{
  "top_level_keys": [
    "messages",
    "images",
    "task",
    "source_id",
    "weight",
    "loss_weight",
    "meta"
  ],
  "messages": "长度为 3 的对话数组：system / user / assistant。训练时 user 是输入，assistant 是 gold 输出。",
  "messages[0].role": "system",
  "messages[0].content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.",
  "messages[1].role": "user",
  "messages[1].content_meaning": "3 个 <image> 占位符 + 文字任务说明；要求模型从三帧判断 stage、intent_label、视觉状态和 BDI。",
  "messages[2].role": "assistant",
  "messages[2].content_meaning": "gold target，严格 tag 格式：stage / intent_label / visual_summary / engagement_pattern / gaze_and_attention / body_and_hands / belief / desire / intention。",
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"
  ],
  "has_video_or_videos_field": false,
  "task": "user_intent",
  "source_id": "piwm_09df40aae2",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable",
    "stage": "interest",
    "intent_label": "request_demonstration",
    "loss_weight": 1.0,
    "loss_weight_policy": "a3plus_visual_intent_low_confidence"
  }
}
```

### A(c) ms-swift 实际看到的输入 prompt

JSONL 中实际输入文本如下。ms-swift 读取 `messages` + `images` 后，会把三张图片和这段 user 文本送入 Qwen2.5-VL chat template。

```
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
- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.
- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.
- belief, desire, and intention must be short customer-state clauses, not salesperson advice.
```

Qwen2.5-VL template 展开后的结构是下面这种形式；其中每张图对应一个 `<|vision_start|><|image_pad|><|vision_end|>`。

```
<|im_start|>system
You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.<|im_end|>
<|im_start|>user
<|vision_start|><|image_pad|><|vision_end|><|vision_start|><|image_pad|><|vision_end|><|vision_start|><|image_pad|><|vision_end|>You are observing a short customer-behavior window.

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
- belief, desire, and intention must be short customer-state clauses, not salesperson advice.<|im_end|>
<|im_start|>assistant

```

### A(d) ms-swift 期望输出 gold target

```
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。</engagement_pattern>
<gaze_and_attention>视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。</gaze_and_attention>
<body_and_hands>身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。</body_and_hands>
<belief>A companion's approval may influence whether the choice feels safe.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

### A(e) loss 计算范围

- 当前 Stage-1 走 standard SFT（监督微调，简单说就是让模型模仿 assistant 的标准答案）。
- ms-swift 对 `messages` 构造 prompt，并只对 assistant 输出 token 计算 cross-entropy loss；system/user prompt token 用作条件输入，不作为目标答案。
- 这一行 `loss_weight=1.0` 存在于 JSONL，但当前 `stage1_train.sh` 没有传入自定义 row-level loss hook；因此 vanilla ms-swift 训练不会因为这个字段改变 loss。

## B. Stage-1 next_state_prediction 任务一条完整样本

### B(a) 原始 JSONL 一行完整内容

```json
{"messages": [{"role": "system", "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."}, {"role": "user", "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您想先看价格、功能，还是使用场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}\n- voice_style: warm\n- light: neutral_prompt_color\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 您想先看价格、功能，还是使用场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."}, {"role": "assistant", "content": "<next_stage>desire</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.83</reward>"}], "images": ["/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"], "task": "next_state_prediction", "source_id": "piwm_09df40aae2#Elicit_b1166d372e5e", "weight": 1.0, "loss_weight": 1.0, "meta": {"parent_state_id": "piwm_09df40aae2", "candidate_action": "Elicit_b1166d372e5e", "candidate_act": "Elicit", "candidate_params": {"openness": "open", "slot": "need_focus"}, "no_intervention_branch": false, "split": "train", "qa_status": null, "human_review_status": null, "viewpoint": "salesperson_observable"}}
```

### B(b) 字段解释

```json
{
  "top_level_keys": [
    "messages",
    "images",
    "task",
    "source_id",
    "weight",
    "loss_weight",
    "meta"
  ],
  "messages": "system / user / assistant。user 给三帧 + candidate action；assistant 预测该候选动作后的 next_stage、next_bdi、risk、benefit、reward。",
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"
  ],
  "has_video_or_videos_field": false,
  "task": "next_state_prediction",
  "source_id": "piwm_09df40aae2#Elicit_b1166d372e5e",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_09df40aae2",
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
  }
}
```

### B(c) ms-swift 实际看到的输入 prompt

```
<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





Use the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.

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

Qwen template 结构：

```
<|im_start|>system
You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.<|im_end|>
<|im_start|>user
<|vision_start|><|image_pad|><|vision_end|><|vision_start|><|image_pad|><|vision_end|><|vision_start|><|image_pad|><|vision_end|>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.





Use the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.

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
- all textual spans must be a single short clause in English.<|im_end|>
<|im_start|>assistant

```

### B(d) ms-swift 期望输出 gold target

```
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.83</reward>
```

### B(e) loss 计算范围

- 同 A：standard SFT，只对 assistant target token 计算 cross-entropy。
- 当前没有额外 regularization，也没有 row-level `loss_weight` 生效。

### B(f) next_state symmetry fix 确认

```json
{
  "contains_current_state": false,
  "contains_current_stage": false,
  "contains_current_belief": false,
  "contains_current_desire": false,
  "contains_current_intention": false,
  "literal_instruction_in_prompt": "Use the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided."
}
```

## C. Stage-2 action_selection 任务一条完整样本

### C(a) 原始 JSONL 完整内容

该行 raw size = 5720 bytes，超过 5KB，完整 raw 放在 attachment：`reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.raw.jsonl`。

pretty JSON：

`reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.pretty.json`

### C(b) 字段解释 + candidate_action_acts

```json
{
  "top_level_keys": [
    "messages",
    "images",
    "task",
    "source_id",
    "weight",
    "loss_weight",
    "meta"
  ],
  "messages": "system / user / assistant。user 给 Stage-1 customer-state representation + stage-conditioned candidates；assistant 选择一个 candidate label。",
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_709/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_709/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_709/002.jpg"
  ],
  "task": "action_selection_5act",
  "source_id": "target_piwm_709",
  "best_act_gold": "Elicit",
  "candidate_action_acts": {
    "Elicit_b1166d372e5e": "Elicit",
    "Inform_24926eed1e21": "Inform",
    "Recommend_interest_stage_conditioned_target_piwm_709_e23e42313b98": "Recommend",
    "Hold_eda24b4bb712": "Hold"
  },
  "candidate_count": 4,
  "stage_from_prompt": "interest",
  "five_act_only": true,
  "leakage_control": "no_reward_no_predicted_outcome_in_prompt"
}
```

### C(c) ms-swift 实际输入 prompt

完整 user prompt 放在 `reports/attachments/2026-05-23_pi_data_schema_walkthrough/stage2_action_row1.user_prompt.txt`。

### C(d) gold target / 期望输出格式

```
<rationale>开放式引导提升被理解感，促进关注点聚焦，有助于从泛兴趣向明确探索转变。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

输出不是 JSON，也不是单独 act name；它是四个 XML-like tags：`<rationale>`、`<chosen>`、`<intervention_action>`、`<intervention_utterance>`。其中 `<chosen>` 必须 exact match 某个 candidate label，例如 `Elicit_b1166d372e5e`。

### C(e) loss 计算范围

- 同 A：训练时对完整 assistant target 的 token 计算 loss，包括 rationale、chosen、intervention_action、intervention_utterance。
- 不是只训练 `<chosen>`。

## D. 一个 GreetAug 合成样本

### D(a) 完整 JSONL 内容

该行 raw size = 5902 bytes，超过 5KB，完整 raw 放在 attachment：`reports/attachments/2026-05-23_pi_data_schema_walkthrough/greet_aug_sample.raw.jsonl`。

### D(b) image / video 字段

```json
{
  "source_id": "greet_aug_001_piwm_00539e313f",
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/002.jpg"
  ],
  "has_video_or_videos_field": false,
  "meta": {
    "split": "train",
    "qa_status": "synthetic_augmented_unreviewed",
    "human_review_status": "not_reviewed",
    "viewpoint": "salesperson_observable",
    "best_act": "Greet",
    "candidate_action_acts": {
      "Greet_open_general_aug_88198d5a7a63": "Greet",
      "Elicit_need_focus_general_aug_135cd62fc1e8": "Elicit",
      "Inform_attributes_general_aug_93d64465ba6a": "Inform",
      "Hold_silent_general_aug_e7ce85d59d12": "Hold"
    },
    "five_act_only": true,
    "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
    "augmentation_policy": "stage2_prelaunch_general_greet_augmentation_v2",
    "augmented_from_state_id": "piwm_00539e313f"
  }
}
```

### D(c) 15 条 GreetAug-v2 怎么生成

生成逻辑来自 `scripts/build_two_stage_training_and_eval.py` 的 `_build_general_greet_aug_policy_rows()` / `_general_greet_aug_policy_row()`。代码依据如下：

```python
def _build_general_greet_aug_policy_rows(general_dir: Path, *, count: int) -> list[dict[str, Any]]:
    """Create deterministic Stage-2 Greet augmentation rows from general attention states.

    The target-frontcam corpus is the only filmed target source with Greet labels,
    but the Stage-1 general corpus has no Greet best labels. This augmentation
    uses existing general-domain frames and creates low-leak action-selection
    examples where an opening Greet is the correct response to attention-stage
    approach/entry behavior. The rows are marked synthetic_augmented_unreviewed
    and are written only to the explicit *_greet_aug_* Stage-2 entrypoint.
    """
    if count <= 0:
        return []
    states = [
        row
        for row in _read_jsonl(general_dir / "state_inference.jsonl")
        if row.get("output", {}).get("aida_stage") == "attention"
    ]
    states = sorted(states, key=lambda row: row["state_id"])
    if len(states) < count:
        raise ValueError(f"not enough general attention rows for Greet augmentation: need {count}, found {len(states)}")
    return [_general_greet_aug_policy_row(row, index=index) for index, row in enumerate(states[:count], start=1)]


def _general_greet_aug_policy_row(state_row: dict[str, Any], *, index: int) -> dict[str, Any]:
    out = state_row["output"]
    visual = out.get("visual_state") or {}
    state_summary = {
        "aida_stage": "attention",
        "product_category": state_row.get("meta", {}).get("product_category", "general_retail"),
        "state_subtype": out.get("state_subtype") or out.get("current_state") or "approach_or_entry",
        "state": out.get("current_state") or out.get("state_subtype") or "approach_or_entry",
        "visual_state": {
            "summary": _greet_visible_summary(visual.get("summary", "")),
            "engagement_pattern": visual.get("engagement_pattern", visual.get("summary", "")),
            "gaze_and_attention": visual.get("gaze_and_attention", visual.get("gaze", "")),
            "body_and_hands": visual.get("body_and_hands", ""),
        },
        "intent": "no_clear_intent",
        "intent_tier": "exploring",
        "bdi": {
            "belief": "The shopper has just entered the selling zone and may need orientation.",
            "desire": "feel welcomed without being pressured",
            "intention": "decide whether to continue browsing or ask for help",
        },
        "proactive_score": 3,
        "candidate_action_specs": [
            {"act": "Greet", "params": {"phase": "open"}},
            {"act": "Elicit", "params": {"openness": "open", "slot": "need_focus"}},
            {"act": "Inform", "params": {"content_type": "attributes", "depth": "brief"}},
            {"act": "Hold", "params": {"mode": "silent"}},
        ],
        "best_action_spec": {"act": "Greet", "params": {"phase": "open"}},
        "persona_type": state_row.get("input", {}).get("persona_summary", "general_retail_shopper"),
        "observable_cues": ["approach_or_entry", "initial_attention"],
        "dialogue_act": "Greet",
        "act_params": {"phase": "open"},
    }
    blocks = [
        _action_block(
            "Greet_open_general_aug",
            "Greet",
            {"phase": "open"},
            "欢迎光临，您可以先随意看看，需要时我在。",
            "show_welcome_message",
            "warm",
            "soft_welcome",
            "智能导购终端以轻柔灯效和简短欢迎语完成开场，不施加购买压力。",
            "开场问候能在顾客刚进入服务区时建立可用性，同时保持低压力。",
        ),
        _action_block(
            "Elicit_need_focus_general_aug",
            "Elicit",
            {"openness": "open", "slot": "need_focus"},
            "您今天想先看价格、功能，还是适合什么场景？",
            "show_choice_bubbles",
            "curious",
            "soft_invitation",
            "智能导购终端给出轻量选择问题，引导顾客表达关注点。",
```

- 文本：不是运行时 GPT 生成；是脚本中的确定性模板填充。
- 视频帧：从 general corpus 里 `aida_stage == attention` 的已有样本借用前三帧。这个样本来自 `Archive_generated_priority500_new_after280/piwm_00539e313f/frames/`。
- `qa_status=synthetic_augmented_unreviewed`：表示这是为了补 Greet 覆盖而合成的训练补丁，未经过项目负责人 QA；它进入 Stage-2 train，不进入 30 条 target test。

### D(d) 它和真实 target Greet 的 schema 差异

```json
{
  "same_top_level_schema": true,
  "same_task": true,
  "same_message_shape": true,
  "real_target_stage2_counts": {
    "real_rows": 71,
    "real_greet_rows": 11
  },
  "greet_aug_counts": {
    "aug_rows": 15,
    "aug_greet_rows": 15
  },
  "schema_differences": {
    "viewpoint": {
      "real_target_example": "target_frontcam",
      "greet_aug": "salesperson_observable"
    },
    "qa_status": {
      "real_target_example": "synthetic_unreviewed",
      "greet_aug": "synthetic_augmented_unreviewed"
    },
    "human_review_status": {
      "real_target_example": null,
      "greet_aug": "not_reviewed"
    },
    "augmentation_policy": {
      "real_target_example": null,
      "greet_aug": "stage2_prelaunch_general_greet_augmentation_v2"
    },
    "augmented_from_state_id": {
      "real_target_example": null,
      "greet_aug": "piwm_00539e313f"
    }
  }
}
```

## E. 30 条 target test 一条完整样本

### E(a) 完整 JSONL 内容

该行 raw size = 5940 bytes，超过 5KB，完整 raw 放在 attachment：`reports/attachments/2026-05-23_pi_data_schema_walkthrough/target_test_action_row1.raw.jsonl`。

### E(b) source / AIDA / best_act / images / candidates

```json
{
  "source_id": "target_piwm_700",
  "aida_stage_gold_from_prompt": "interest",
  "best_act_gold": "Elicit",
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "candidate_action_acts": {
    "Elicit_b1166d372e5e": "Elicit",
    "Inform_24926eed1e21": "Inform",
    "Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e": "Recommend",
    "Hold_eda24b4bb712": "Hold"
  },
  "candidate_count": 4,
  "qa_status": "qa_reviewed_pass",
  "human_review_status": "project_lead_reviewed_pass"
}
```

### E(c) 评估时 evaluator 如何判定正确

- `parse_success`：模型输出能被 parser 成功解析，没有抛出 `MalformedOutputError` / `RuntimeError` / `ValueError`。
- action 任务 parser 要求输出含且仅含这些 tag：`rationale / chosen / intervention_action / intervention_utterance`。
- `<chosen>` 必须是候选表里的 exact candidate label，并且在 5-act 内。
- 正确性是 exact match：`parsed.chosen == gold.chosen`。不是 fuzzy match。
- per-act F1 会把 candidate label 通过 `meta.candidate_action_acts` 映射到 act，例如 `Elicit_b1166d372e5e -> Elicit`。

## F. ms-swift 实际训练 pipeline

### F(a) stage1_train.sh 完整内容

```bash
#!/usr/bin/env bash
set -euo pipefail

# Stage-1 User Intent World Modeling SFT launcher.
#
# Target hardware: 8 x RTX 4090 24GB.
# Expected runtime: about 4-6 hours for the current 2309-example train split,
# depending on storage throughput, image decoding, and ms-swift version.
# This script is configuration only by default; pass --run to launch training.

RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)
      RUN=0
      ;;
    --run)
      RUN=1
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

MODEL_ID="${MODEL_ID:-Qwen/Qwen2.5-VL-7B-Instruct}"
SWIFT_BIN="${SWIFT_BIN:-swift}"
NPROC_PER_NODE="${NPROC_PER_NODE:-8}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"

TRAIN_USER="${TRAIN_USER:-data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl}"
TRAIN_NEXT="${TRAIN_NEXT:-data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl}"
VAL_USER="${VAL_USER:-data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl}"
VAL_NEXT="${VAL_NEXT:-data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl}"

OUTPUT_DIR="${OUTPUT_DIR:-checkpoints/stage1_qwen25vl_7b_v1}"
LOG_DIR="${LOG_DIR:-logs/stage1_qwen25vl_7b_v1}"
EPOCHS="${EPOCHS:-3}"
LR="${LR:-2e-5}"
PER_DEVICE_BATCH_SIZE="${PER_DEVICE_BATCH_SIZE:-4}"
GRAD_ACCUM_STEPS="${GRAD_ACCUM_STEPS:-2}"
MAX_FRAMES="${MAX_FRAMES:-3}"
MAX_LENGTH="${MAX_LENGTH:-4096}"
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-32}"
# ms-swift 4.1.3 uses all-linear as the broad LoRA target-module setting.
# Override TARGET_MODULES=auto only in environments where that alias is supported.
TARGET_MODULES="${TARGET_MODULES:-all-linear}"
ACT_BALANCING="${ACT_BALANCING:-none}"

for required in "$TRAIN_USER" "$TRAIN_NEXT" "$VAL_USER" "$VAL_NEXT"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing required Stage-1 data file: $required" >&2
    echo "Run: python3 -m scripts.build_stage1_general_split" >&2
    exit 1
  fi
done

DATASET=("$TRAIN_USER" "$TRAIN_NEXT")
VAL_DATASET=("$VAL_USER" "$VAL_NEXT")

CMD=(
  "$SWIFT_BIN" sft
  --model "$MODEL_ID"
  --dataset "${DATASET[@]}"
  --val_dataset "${VAL_DATASET[@]}"
  --output_dir "$OUTPUT_DIR"
  --tuner_type lora
  --lora_rank "$LORA_RANK"
  --lora_alpha "$LORA_ALPHA"
  --target_modules "$TARGET_MODULES"
  --learning_rate "$LR"
  --num_train_epochs "$EPOCHS"
  --per_device_train_batch_size "$PER_DEVICE_BATCH_SIZE"
  --per_device_eval_batch_size "$PER_DEVICE_BATCH_SIZE"
  --gradient_accumulation_steps "$GRAD_ACCUM_STEPS"
  --max_length "$MAX_LENGTH"
  --torch_dtype bfloat16
  --gradient_checkpointing true
  --logging_dir "$LOG_DIR"
)

echo "Stage-1 ms-swift launch configuration:"
echo "  MODEL_ID=$MODEL_ID"
echo "  SWIFT_BIN=$SWIFT_BIN"
echo "  CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "  NPROC_PER_NODE=$NPROC_PER_NODE"
echo "  ACT_BALANCING=$ACT_BALANCING (Stage-1 has no action-selection balancing)"
echo "  MAX_FRAMES=$MAX_FRAMES (enforced by dataset rows; not passed as a ms-swift CLI arg)"
echo "  Train: ${DATASET[*]}"
echo "  Val:   ${VAL_DATASET[*]}"
echo "  Output checkpoint dir: $OUTPUT_DIR"
echo "  Log dir: $LOG_DIR"
echo
echo "Full command:"
printf ' %q' CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" NPROC_PER_NODE="$NPROC_PER_NODE" "${CMD[@]}"
printf '\n'

if [[ "$RUN" != "1" ]]; then
  echo
  echo "Dry-run only. Re-run with --run to start training."
  exit 0
fi

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"
export CUDA_VISIBLE_DEVICES
export NPROC_PER_NODE
"${CMD[@]}" 2>&1 | tee "$LOG_DIR/train.log"

```

### F(b) ms-swift 拿到 JSONL 后读取/忽略哪些字段

```json
{
  "read_by_ms_swift_standard_sft": [
    "messages",
    "images"
  ],
  "used_for_training_prompt": "messages 形成 system/user/assistant 对话；images 绑定到视觉输入。",
  "project_metadata_fields_present_but_not_used_by_vanilla_ms_swift_loss": [
    "task",
    "source_id",
    "weight",
    "loss_weight",
    "meta"
  ],
  "loss_weight_status": "JSONL 中有 loss_weight；但当前 stage1_train.sh 没有自定义 trainer 或 row-level loss hook，ms-swift 4.1.3 standard SFT 不会自动按该字段加权。",
  "max_pixels": "当前 Path C / A3 remote launch 显式用了 --max_pixels 1003520；本地 stage1_train.sh 默认没有写 max_pixels。",
  "image_count": "由 JSONL 的 images 数量决定；当前 Stage-1 frozen 数据是每行 3 张图。"
}
```

Qwen2.5-VL chat template：

```jinja
{% set image_count = namespace(value=0) %}{% set video_count = namespace(value=0) %}{% for message in messages %}{% if loop.first and message['role'] != 'system' %}<|im_start|>system
You are a helpful assistant.<|im_end|>
{% endif %}<|im_start|>{{ message['role'] }}
{% if message['content'] is string %}{{ message['content'] }}<|im_end|>
{% else %}{% for content in message['content'] %}{% if content['type'] == 'image' or 'image' in content or 'image_url' in content %}{% set image_count.value = image_count.value + 1 %}{% if add_vision_id %}Picture {{ image_count.value }}: {% endif %}<|vision_start|><|image_pad|><|vision_end|>{% elif content['type'] == 'video' or 'video' in content %}{% set video_count.value = video_count.value + 1 %}{% if add_vision_id %}Video {{ video_count.value }}: {% endif %}<|vision_start|><|video_pad|><|vision_end|>{% elif 'text' in content %}{{ content['text'] }}{% endif %}{% endfor %}<|im_end|>
{% endif %}{% endfor %}{% if add_generation_prompt %}<|im_start|>assistant
{% endif %}

```

### F(c) 训练 loss 计算

- standard SFT cross-entropy on assistant tokens。
- 没有 DPO、CADPO、reward regularization 或额外 planning loss。
- LoRA 只让一小部分 adapter 参数可训练，base model 权重不全量更新。

### F(d) checkpoint 保存内容

以 Path C `checkpoint-432` 为例，目录中有：

```
README.md 5244 bytes
adapter_config.json 1093 bytes
adapter_model.safetensors 161533192 bytes
additional_config.json 67 bytes
args.json 19083 bytes
optimizer.pt 323290986 bytes
rng_state_0.pth 14512 bytes
rng_state_1.pth 14512 bytes
scheduler.pt 1064 bytes
trainer_state.json 20736 bytes
training_args.bin 6840 bytes
```

- `adapter_model.safetensors` + `adapter_config.json`：LoRA adapter。
- `optimizer.pt` / `scheduler.pt` / `rng_state_*.pth` / `trainer_state.json`：恢复训练用状态。
- 不是 full model checkpoint；base model 仍来自 `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct`。

## G. 评估 pipeline

### G(a) scripts/eval_ms_swift_checkpoint.py 核心逻辑

加载模型/LoRA：

```python
processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
base = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    args.model,
    torch_dtype=torch.bfloat16 if args.torch_dtype == "bfloat16" else torch.float16,
    device_map=args.device_map,
    trust_remote_code=True,
)
if args.checkpoint is not None:
    model = PeftModel.from_pretrained(base, args.checkpoint)
else:
    model = base
```

inference prompt 构造：

```python
messages = _normalize_messages(row, image_limit=args.image_limit, max_pixels=args.max_pixels)
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt")
```

- evaluator 会把 JSONL 中 user content 的 `<image>` 删除，再把 `images` 路径转换成 Qwen content-list 里的 image items。
- 训练和评估使用的是同一批 JSONL prompt 文本；评估端显式调用 Qwen `apply_chat_template`。
- generation 默认：`max_new_tokens=256`，`do_sample=False`，没有 temperature 采样。

parser：

```python
def _extract_tags(raw, tags):
    pattern = re.escape(tag.open) + r"(.*?)" + re.escape(tag.close)
    matches = re.findall(pattern, raw, flags=re.DOTALL)
    if len(matches) != 1:
        raise MalformedOutputError(...)

# action_selection_5act:
parse_action_output(raw, valid_actions=meta.candidate_action_acts.keys(), five_act_only=True)
```

### G(b) parser fix 之前和之后的具体 diff

完整 diff 同时保存到 attachment：
`reports/attachments/2026-05-23_pi_data_schema_walkthrough/parser_eval_current_diff_vs_head.patch`

```diff
diff --git a/piwm_infer/parsers.py b/piwm_infer/parsers.py
index 09b3c3e..ccdbe37 100644
--- a/piwm_infer/parsers.py
+++ b/piwm_infer/parsers.py
@@ -44,6 +44,31 @@ def parse_perception_output(raw: str) -> dict:
     }
 
 
+def parse_user_intent_output(raw: str) -> dict:
+    values = _extract_tags(raw, config.USER_INTENT_TAGS)
+    stage = values["stage"]
+    if stage not in rules.AIDA_STAGES:
+        raise MalformedOutputError(f"invalid stage: {stage}")
+    intent_label = values["intent_label"]
+    if not intent_label:
+        raise MalformedOutputError("intent_label is empty")
+    return {
+        "aida_stage": stage,
+        "intent_label": intent_label,
+        "visual_state": {
+            "summary": values["visual_summary"],
+            "engagement_pattern": values["engagement_pattern"],
+            "gaze_and_attention": values["gaze_and_attention"],
+            "body_and_hands": values["body_and_hands"],
+        },
+        "bdi": {
+            "belief": values["belief"],
+            "desire": values["desire"],
+            "intention": values["intention"],
+        },
+    }
+
+
 def parse_deliberation_output(raw: str) -> dict:
     values = _extract_tags(raw, config.DELIBERATION_TAGS)
     next_stage = values["next_stage"]
@@ -97,14 +122,17 @@ def parse_future_verification_output(raw: str) -> dict:
     }
 
 
-def parse_action_output(raw: str, valid_actions: Iterable[str] | None = None) -> dict:
+FIVE_ACTS = {"Greet", "Elicit", "Inform", "Recommend", "Hold"}
+
+
+def parse_action_output(raw: str, valid_actions: Iterable[str] | None = None, *, five_act_only: bool = False) -> dict:
     values = _extract_tags(raw, config.ACTION_TAGS)
     chosen = values["chosen"]
     if valid_actions is not None:
         valid = set(valid_actions)
-        is_valid = chosen in valid
+        is_valid = chosen in valid and (not five_act_only or _action_label_act(chosen) in FIVE_ACTS)
     else:
-        is_valid = _is_valid_action_label(chosen)
+        is_valid = _is_valid_action_label(chosen, five_act_only=five_act_only)
     if not is_valid:
         raise MalformedOutputError(f"chosen action is not valid: {chosen}")
     return {
@@ -156,7 +184,18 @@ def _parse_candidates(value: str) -> list[str]:
     return candidates
 
 
-def _is_valid_action_label(action: str) -> bool:
+def _is_valid_action_label(action: str, *, five_act_only: bool = False) -> bool:
+    act = _action_label_act(action)
+    if five_act_only and act not in FIVE_ACTS:
+        return False
     if action in rules.ACTIONS:
         return True
     return re.fullmatch(r"(Greet|Elicit|Inform|Recommend|Reassure|Hold)_[0-9a-f]{12}", action) is not None
+
+
+def _action_label_act(action: str) -> str | None:
+    if "_" in action:
+        prefix = action.split("_", 1)[0]
+        if prefix in {"Greet", "Elicit", "Inform", "Recommend", "Reassure", "Hold"}:
+            return prefix
+    return None
diff --git a/scripts/eval_ms_swift_checkpoint.py b/scripts/eval_ms_swift_checkpoint.py
index 48b5149..df5ad85 100644
--- a/scripts/eval_ms_swift_checkpoint.py
+++ b/scripts/eval_ms_swift_checkpoint.py
@@ -9,6 +9,7 @@ from __future__ import annotations
 
 import argparse
 import json
+import math
 import sys
 import time
 from pathlib import Path
@@ -17,7 +18,7 @@ from typing import Any
 import torch
 from peft import PeftModel
 from qwen_vl_utils import process_vision_info
-from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
+from transformers import AutoProcessor, LogitsProcessor, LogitsProcessorList, Qwen2_5_VLForConditionalGeneration
 
 REPO_ROOT = Path(__file__).resolve().parents[1]
 if str(REPO_ROOT) not in sys.path:
@@ -35,6 +36,19 @@ from piwm_infer.parsers import (
 )
 
 
+class TokenBiasLogitsProcessor(LogitsProcessor):
+    """Apply a constant generation-time bias to selected token ids."""
+
+    def __init__(self, token_ids: set[int], bias: float) -> None:
+        self.token_ids = sorted(token_ids)
+        self.bias = bias
+
+    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
+        if self.token_ids and self.bias:
+            scores[:, self.token_ids] += self.bias
+        return scores
+
+
 def _read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
     rows: list[dict[str, Any]] = []
     with path.open(encoding="utf-8") as handle:
@@ -47,7 +61,7 @@ def _read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
     return rows
 
 
-def _task_parser(task: str):
+def _task_parser(task: str, row: dict[str, Any] | None = None):
     if task == "user_intent":
         return parse_user_intent_output
     if task == "perception":
@@ -59,7 +73,16 @@ def _task_parser(task: str):
     if task == "future_verification":
         return parse_future_verification_output
     if task in {"action_selection", "action_selection_5act"}:
-        return (lambda raw: parse_action_output(raw, five_act_only=True)) if task == "action_selection_5act" else parse_action_output
+        valid_actions = None
+        if row is not None:
+            mapping = row.get("meta", {}).get("candidate_action_acts", {})
+            if mapping:
+                valid_actions = mapping.keys()
+        return (
+            lambda raw: parse_action_output(raw, valid_actions=valid_actions, five_act_only=True)
+            if task == "action_selection_5act"
+            else parse_action_output(raw, valid_actions=valid_actions)
+        )
     raise ValueError(f"unsupported task: {task}")
 
 
@@ -98,13 +121,46 @@ def _generate_one(model, processor, row: dict[str, Any], args: argparse.Namespac
         return_tensors="pt",
     )
     inputs = inputs.to(model.device)
+    logits_processor = _logits_processor_for_row(processor, row, args)
     with torch.inference_mode():
-        generated_ids = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
+        generated_ids = model.generate(
+            **inputs,
+            max_new_tokens=args.max_new_tokens,
+            do_sample=False,
+            logits_processor=logits_processor,
+        )
     prompt_len = inputs["input_ids"].shape[-1]
     generated_ids = generated_ids[:, prompt_len:]
     return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
 
 
+def _logits_processor_for_row(processor, row: dict[str, Any], args: argparse.Namespace) -> LogitsProcessorList | None:
+    if row.get("task") != "action_selection_5act":
+        return None
+    if args.hold_prior_lambda <= 0:
+        return None
+    hold_token_ids = _hold_candidate_token_ids(processor, row)
+    if not hold_token_ids:
+        return None
+    prior = max(float(args.hold_prior_observed), 1e-6)
+    target = max(float(args.hold_prior_target), 1e-6)
+    penalty = float(args.hold_prior_lambda) * math.log(prior / target)
+    if penalty <= 0:
+        return None
+    return LogitsProcessorList([TokenBiasLogitsProcessor(hold_token_ids, -penalty)])
+
+
+def _hold_candidate_token_ids(processor, row: dict[str, Any]) -> set[int]:
+    mapping = row.get("meta", {}).get("candidate_action_acts", {})
+    hold_labels = [label for label, act in mapping.items() if act == "Hold"]
+    token_ids: set[int] = set()
+    tokenizer = processor.tokenizer
+    for label in hold_labels:
+        encoded = tokenizer(label, add_special_tokens=False)
+        token_ids.update(int(token_id) for token_id in encoded.get("input_ids", []))
+    return token_ids
+
+
 def _score(parsed: dict[str, Any], gold: dict[str, Any], task: str) -> dict[str, bool]:
     if task == "user_intent":
         return {
@@ -194,7 +250,7 @@ def evaluate(args: argparse.Namespace) -> dict[str, Any]:
     for index, row in enumerate(rows, start=1):
         task = row.get("task", "unknown")
         task_counts[task] = task_counts.get(task, 0) + 1
-        parser = _task_parser(task)
+        parser = _task_parser(task, row)
         gold_raw = _primary_structured_block(row["messages"][2]["content"])
         gold = parser(gold_raw)
         record: dict[str, Any] = {
@@ -272,6 +328,9 @@ def evaluate(args: argparse.Namespace) -> dict[str, Any]:
             "max_pixels": args.max_pixels,
             "torch_dtype": args.torch_dtype,
             "device_map": args.device_map,
+            "hold_prior_lambda": args.hold_prior_lambda,
+            "hold_prior_target": args.hold_prior_target,
+            "hold_prior_observed": args.hold_prior_observed,
         },
         "n_records": len(rows),
         "task_counts": task_counts,
@@ -387,6 +446,24 @@ def parse_args() -> argparse.Namespace:
     parser.add_argument("--max-pixels", type=int, default=None)
     parser.add_argument("--torch-dtype", choices=["bfloat16", "float16"], default="bfloat16")
     parser.add_argument("--device-map", default="auto")
+    parser.add_argument(
+        "--hold-prior-lambda",
+        type=float,
+        default=0.0,
+        help="For action_selection_5act generation, subtract lambda*log(observed/target) from Hold candidate label token logits.",
+    )
+    parser.add_argument(
+        "--hold-prior-target",
+        type=float,
+        default=0.2,
+        help="Target Hold prior used by --hold-prior-lambda. Balanced 5-act target test uses 0.2.",
+    )
+    parser.add_argument(
+        "--hold-prior-observed",
+        type=float,
+        default=16 / 30,
+        help="Observed Hold prediction prior from the Path C quick probe.",
+    )
     parser.add_argument("--progress-every", type=int, default=10)
     parser.add_argument("--partial-out-every", type=int, default=25)
     return parser.parse_args()

```

### G(c) Hold prior calibration 怎么实施

```json
{
  "intervention_point": "model.generate(..., logits_processor=logits_processor)",
  "only_applies_when": "row.task == action_selection_5act and --hold-prior-lambda > 0",
  "formula": "penalty = lambda * log(hold_prior_observed / hold_prior_target)",
  "defaults": {
    "hold_prior_observed": "16/30",
    "hold_prior_target": 0.2,
    "lambda": 1.0
  },
  "lambda_1_penalty": 0.980829,
  "operation": "对 Hold candidate label 分词得到的 token ids 加负 bias，即 scores[:, token_id] += -penalty。",
  "affected_tokens": "动态由 tokenizer(Hold candidate label, add_special_tokens=False) 得到；例如该行候选中 act==Hold 的 label 是 Hold_eda24b4bb712。"
}
```

对应代码：

```python
hold_labels = [label for label, act in mapping.items() if act == "Hold"]
encoded = tokenizer(label, add_special_tokens=False)
token_ids.update(encoded["input_ids"])
penalty = lambda * math.log(observed / target)
scores[:, token_ids] += -penalty
```
