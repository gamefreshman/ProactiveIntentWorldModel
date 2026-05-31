# 2026-05-25 Figure Data Samples

Scope: read-only extraction from the current PIWM training data. This report dumps raw records only; it does not edit data, run training, draw figures, or write LaTeX.

## Source Files

- Joint training mix: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl`
- Task counts in joint mix: `user_intent=543`, `next_state_prediction=2001`, `action_selection_5act=190`.
- Source scene records: `data/official/piwm_train_synth_v2/main_schema.jsonl`

## Filter Audit

- Strict-pass scene/action candidates after hard filters: `62`.
- Strict-pass best_act distribution: `{'Elicit': 26, 'Recommend': 36}`.
- No strict-pass `Hold` sample exists in the current training mix: every `best_act=Hold` action-selection row has candidate count `2`.
- Hold action-selection candidate-size audit: `[2]`; count `41`.
- Therefore Sample 3 is included as an explicit best-effort HOLD exception so PI can still inspect the available raw HOLD data. It satisfies scene coverage and next-state completeness but not hard filter #2.

### Sample 1 (scene_id: piwm_1cc2c20d89, best_action: Recommend, 类型: 典型)

Selection note: Strict-pass. Recommend winner has a wider top-2 reward gap among strict candidates (0.85 vs 0.60).

Quick candidate reward view derived from the matching `next_state_prediction` rows:

```json
[
  {
    "candidate_id": "Elicit_b1166d372e5e",
    "act": "Elicit",
    "next_stage": "desire",
    "reward": "0.20"
  },
  {
    "candidate_id": "Hold_eda24b4bb712",
    "act": "Hold",
    "next_stage": "attention",
    "reward": "-0.20"
  },
  {
    "candidate_id": "Recommend_8d7f8993e333",
    "act": "Recommend",
    "next_stage": "action",
    "reward": "0.85"
  },
  {
    "candidate_id": "Recommend_9ff23b139b07",
    "act": "Recommend",
    "next_stage": "action",
    "reward": "0.60"
  }
]
```

#### Section A: Scene Seed / Source Scene Record

Source: `data/official/piwm_train_synth_v2/main_schema.jsonl` line `50`

```json
{
  "act_params": {
    "pressure": "soft",
    "target": "item"
  },
  "actor_profile": "human_salesperson_logic",
  "aida_stage": "action",
  "bdi": {
    "belief": "A suitable option may be close, but staff input is needed before deciding.",
    "desire": "confirm the preferred choice",
    "intention": "move toward confirming the choice"
  },
  "best_action": "Recommend_8d7f8993e333",
  "best_action_realization": {
    "physical_action": "智能售货柜按屏幕、语音、灯效执行该候选响应。",
    "rationale": "operational 5-act terminal realization for Recommend_8d7f8993e333",
    "timing": "设备前置摄像头检测到当前顾客状态后触发。",
    "utterance": "这款可以作为一个参考选项。"
  },
  "best_action_spec": {
    "act": "Recommend",
    "params": {
      "pressure": "soft",
      "target": "item"
    }
  },
  "candidate_action_specs": [
    {
      "act": "Elicit",
      "params": {
        "openness": "open",
        "slot": "need_focus"
      }
    },
    {
      "act": "Hold",
      "params": {
        "mode": "silent"
      }
    },
    {
      "act": "Recommend",
      "params": {
        "pressure": "soft",
        "target": "item"
      }
    },
    {
      "act": "Recommend",
      "params": {
        "pressure": "firm",
        "target": "item"
      }
    }
  ],
  "candidate_actions": [
    "Elicit_b1166d372e5e",
    "Hold_eda24b4bb712",
    "Recommend_8d7f8993e333",
    "Recommend_9ff23b139b07"
  ],
  "compatibility_tier": "green",
  "continuations": {},
  "dialogue_act": "Recommend",
  "images": [
    {
      "index": 0,
      "relative_path": "Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
      "timestamp_sec": null
    },
    {
      "index": 1,
      "relative_path": "Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
      "timestamp_sec": null
    },
    {
      "index": 2,
      "relative_path": "Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg",
      "timestamp_sec": null
    }
  ],
  "intent": "confirm_choice",
  "is_anchor": false,
  "latent_state": "ready_to_decide",
  "legacy_mismatch_flags": [],
  "next_state_by_action": {
    "Elicit_b1166d372e5e": {
      "act_params": {
        "openness": "open",
        "slot": "need_focus"
      },
      "benefit": "high",
      "dialogue_act": "Elicit",
      "failure_mode": "若顾客已经明确要下单，继续追问可能变成不必要摩擦。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "desire",
      "next_bdi": {
        "belief": "The decision remains uncertain after the last observation.",
        "desire": "gain reassurance before deciding",
        "intention": "look for reassurance or clarification"
      },
      "next_state": "continued_hesitation",
      "outcome_type": "failure",
      "rationale": "Rule-derived expectation: A4_open_with_question from ready_to_decide leads to continued_hesitation with low risk, high benefit, and reward 0.20.",
      "reward": 0.2,
      "reward_components": {
        "action_cost": 0.1,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 0.6866666666666668,
        "delta_stage": -0.3333333333333333,
        "final_reward": 0.2,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": [
        "failure_mode_triggered"
      ]
    },
    "Hold_eda24b4bb712": {
      "act_params": {
        "mode": "silent"
      },
      "benefit": "low",
      "dialogue_act": "Hold",
      "failure_mode": "若顾客已进入购买确认，保持静默会错过服务与成交窗口。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The current interaction is not useful enough to continue.",
        "desire": "avoid further engagement",
        "intention": "leave without buying"
      },
      "next_state": "disengaged",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A1_silent_observe from ready_to_decide leads to disengaged with medium risk, low benefit, and reward -0.20.",
      "reward": -0.2,
      "reward_components": {
        "action_cost": 0.0,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 0.4,
        "delta_stage": -1.0,
        "final_reward": -0.2,
        "gamma": 0.1
      },
      "risk": "medium",
      "risk_tags": []
    },
    "Recommend_8d7f8993e333": {
      "act_params": {
        "pressure": "soft",
        "target": "item"
      },
      "benefit": "high",
      "dialogue_act": "Recommend",
      "failure_mode": "若顾客虽接近决策但仍高敏感，强推荐仍可能压迫选择自由。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "action",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from ready_to_decide leads to engaged_dialogue with low risk, high benefit, and reward 0.85.",
      "reward": 0.85,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.76,
        "delta_stage": 0.0,
        "final_reward": 0.85,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Recommend_9ff23b139b07": {
      "act_params": {
        "pressure": "firm",
        "target": "item"
      },
      "benefit": "high",
      "dialogue_act": "Recommend",
      "failure_mode": "若顾客虽接近决策但仍高敏感，强推荐仍可能压迫选择自由。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "action",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from ready_to_decide leads to engaged_dialogue with medium risk, high benefit, and reward 0.60.",
      "reward": 0.6,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.26,
        "delta_stage": 0.0,
        "final_reward": 0.6,
        "gamma": 0.1
      },
      "risk": "medium",
      "risk_tags": []
    }
  },
  "next_state_by_action_v2": {
    "Elicit_b1166d372e5e": {
      "act_params": {
        "openness": "open",
        "slot": "need_focus"
      },
      "benefit": "high",
      "dialogue_act": "Elicit",
      "failure_mode": "若顾客已经明确要下单，继续追问可能变成不必要摩擦。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "desire",
      "next_bdi": {
        "belief": "The decision remains uncertain after the last observation.",
        "desire": "gain reassurance before deciding",
        "intention": "look for reassurance or clarification"
      },
      "next_state": "continued_hesitation",
      "outcome_type": "failure",
      "rationale": "Rule-derived expectation: A4_open_with_question from ready_to_decide leads to continued_hesitation with low risk, high benefit, and reward 0.20.",
      "reward": 0.2,
      "reward_components": {
        "action_cost": 0.1,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 0.6866666666666668,
        "delta_stage": -0.3333333333333333,
        "final_reward": 0.2,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": [
        "failure_mode_triggered"
      ]
    },
    "Hold_eda24b4bb712": {
      "act_params": {
        "mode": "silent"
      },
      "benefit": "low",
      "dialogue_act": "Hold",
      "failure_mode": "若顾客已进入购买确认，保持静默会错过服务与成交窗口。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The current interaction is not useful enough to continue.",
        "desire": "avoid further engagement",
        "intention": "leave without buying"
      },
      "next_state": "disengaged",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A1_silent_observe from ready_to_decide leads to disengaged with medium risk, low benefit, and reward -0.20.",
      "reward": -0.2,
      "reward_components": {
        "action_cost": 0.0,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 0.4,
        "delta_stage": -1.0,
        "final_reward": -0.2,
        "gamma": 0.1
      },
      "risk": "medium",
      "risk_tags": []
    },
    "Recommend_8d7f8993e333": {
      "act_params": {
        "pressure": "soft",
        "target": "item"
      },
      "benefit": "high",
      "dialogue_act": "Recommend",
      "failure_mode": "若顾客虽接近决策但仍高敏感，强推荐仍可能压迫选择自由。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "action",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from ready_to_decide leads to engaged_dialogue with low risk, high benefit, and reward 0.85.",
      "reward": 0.85,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.76,
        "delta_stage": 0.0,
        "final_reward": 0.85,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Recommend_9ff23b139b07": {
      "act_params": {
        "pressure": "firm",
        "target": "item"
      },
      "benefit": "high",
      "dialogue_act": "Recommend",
      "failure_mode": "若顾客虽接近决策但仍高敏感，强推荐仍可能压迫选择自由。",
      "intent_tier": "ready_to_buy",
      "next_aida_stage": "action",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from ready_to_decide leads to engaged_dialogue with medium risk, high benefit, and reward 0.60.",
      "reward": 0.6,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.26,
        "delta_stage": 0.0,
        "final_reward": 0.6,
        "gamma": 0.1
      },
      "risk": "medium",
      "risk_tags": []
    }
  },
  "observable_cues": [
    "looking_around_for_help"
  ],
  "persona": {
    "description": "An experienced shopper who already trusts familiar brands and compares details quickly.",
    "intent_tier": "ready_to_buy",
    "type": "experienced_brand_loyal"
  },
  "proactive_score": 5,
  "product_category": "cosmetics_skincare",
  "provenance": [
    {
      "field_name": "product_category",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "split",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "viewpoint",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "latent_state",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "visual_state",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "intent",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "bdi",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "proactive_score",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "candidate_actions",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "next_state_by_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "reward_by_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "best_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "best_action_realization",
      "rule_version": "v1.0",
      "source": "rule_derived"
    }
  ],
  "rationale": "Rule-derived expectation: A3_strong_recommend from ready_to_decide leads to engaged_dialogue with low risk, high benefit, and reward 0.85.",
  "realization": {
    "act_params": {
      "pressure": "soft",
      "target": "item"
    },
    "cabinet_motion": null,
    "dialogue_act": "Recommend",
    "duration_ms": 4000,
    "legacy_action": null,
    "light": "soft_focus_on_recommendation",
    "screen": {
      "action": "highlight_item",
      "cta": null,
      "target": "{candidate_item}"
    },
    "surface_text": "这款可以作为一个参考选项。",
    "voice_style": "neutral"
  },
  "reward_by_action": {
    "Elicit_b1166d372e5e": 0.2,
    "Hold_eda24b4bb712": -0.2,
    "Recommend_8d7f8993e333": 0.85,
    "Recommend_9ff23b139b07": 0.6
  },
  "schema_version": "dialogue_act_human_salesperson_v2.2",
  "split": "train",
  "state_id": "piwm_1cc2c20d89",
  "viewpoint": "salesperson_observable",
  "visual_state": {
    "body_and_hands": "身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。",
    "engagement_pattern": "顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。",
    "gaze_and_attention": "视线从商品转向周围空间或导购可能出现的位置。",
    "summary": "顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。"
  }
}
```

#### Section B: user_intent Training Row

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `50`

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
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "piwm_1cc2c20d89",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable",
    "stage": "action",
    "intent_label": "confirm_choice",
    "loss_weight": 1.0,
    "loss_weight_policy": "a3plus_visual_intent_low_confidence"
  }
}
```

#### Section C: next_state_prediction Training Rows for Action Candidates

##### Candidate: Elicit_b1166d372e5e (Elicit)

Action prompt block from `action_selection_5act`:

```text
- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您想先看价格、功能，还是使用场景？, screen={'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}, voice_style=warm, light=neutral_prompt_color, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您想先看价格、功能，还是使用场景？
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `712`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您想先看价格、功能，还是使用场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}\n- voice_style: warm\n- light: neutral_prompt_color\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 您想先看价格、功能，还是使用场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>desire</next_stage>\n<next_belief>The decision remains uncertain after the last observation.</next_belief>\n<next_desire>gain reassurance before deciding</next_desire>\n<next_intention>look for reassurance or clarification</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.20</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_1cc2c20d89#Elicit_b1166d372e5e",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_1cc2c20d89",
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

##### Candidate: Hold_eda24b4bb712 (Hold)

Action prompt block from `action_selection_5act`:

```text
- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `713`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Hold_eda24b4bb712\n\nDialogue-act layer for this candidate:\n- act: Hold\n- params: {'mode': 'silent'}\n\nTerminal realization for this candidate:\n- surface_text: \n- screen: {'action': 'idle_minimal', 'cta': None}\n- voice_style: silent\n- light: maintain_current_soft_breathing\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: （静默）\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>attention</next_stage>\n<next_belief>The current interaction is not useful enough to continue.</next_belief>\n<next_desire>avoid further engagement</next_desire>\n<next_intention>leave without buying</next_intention>\n<risk>medium</risk>\n<benefit>low</benefit>\n<reward>-0.20</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_1cc2c20d89#Hold_eda24b4bb712",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_1cc2c20d89",
    "candidate_action": "Hold_eda24b4bb712",
    "candidate_act": "Hold",
    "candidate_params": {
      "mode": "silent"
    },
    "no_intervention_branch": true,
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  }
}
```

##### Candidate: Recommend_8d7f8993e333 (Recommend)

Action prompt block from `action_selection_5act`:

```text
- Recommend_8d7f8993e333: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=这款可以作为一个参考选项。, screen={'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=soft_focus_on_recommendation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款可以作为一个参考选项。
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `714`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Recommend_8d7f8993e333\n\nDialogue-act layer for this candidate:\n- act: Recommend\n- params: {'target': 'item', 'pressure': 'soft'}\n\nTerminal realization for this candidate:\n- surface_text: 这款可以作为一个参考选项。\n- screen: {'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}\n- voice_style: neutral\n- light: soft_focus_on_recommendation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 这款可以作为一个参考选项。\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>action</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.85</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_1cc2c20d89#Recommend_8d7f8993e333",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_1cc2c20d89",
    "candidate_action": "Recommend_8d7f8993e333",
    "candidate_act": "Recommend",
    "candidate_params": {
      "target": "item",
      "pressure": "soft"
    },
    "no_intervention_branch": false,
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  }
}
```

##### Candidate: Recommend_9ff23b139b07 (Recommend)

Action prompt block from `action_selection_5act`:

```text
- Recommend_9ff23b139b07: act=Recommend, params={'target': 'item', 'pressure': 'firm'}, surface_text=这款最适合您，建议直接选这款。, screen={'action': 'show_fullscreen_recommendation', 'target': '{candidate_item}', 'cta': '立即购买'}, voice_style=firm, light=warm_red_or_yellow_guidance, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款最适合您，建议直接选这款。
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `715`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Recommend_9ff23b139b07\n\nDialogue-act layer for this candidate:\n- act: Recommend\n- params: {'target': 'item', 'pressure': 'firm'}\n\nTerminal realization for this candidate:\n- surface_text: 这款最适合您，建议直接选这款。\n- screen: {'action': 'show_fullscreen_recommendation', 'target': '{candidate_item}', 'cta': '立即购买'}\n- voice_style: firm\n- light: warm_red_or_yellow_guidance\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 这款最适合您，建议直接选这款。\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>action</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>medium</risk>\n<benefit>high</benefit>\n<reward>0.60</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_1cc2c20d89#Recommend_9ff23b139b07",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_1cc2c20d89",
    "candidate_action": "Recommend_9ff23b139b07",
    "candidate_act": "Recommend",
    "candidate_params": {
      "target": "item",
      "pressure": "firm"
    },
    "no_intervention_branch": false,
    "split": "train",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  }
}
```

#### Section D: action_selection_5act Training Row

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `2662`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe Stage-1 customer-state representation is:\n- stage: action\n- intent_label: confirm_choice\n- visible evidence: 顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。\n- engagement pattern: 顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。\n- gaze and attention: 视线从商品转向周围空间或导购可能出现的位置。\n- body and hands: 身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。\n- belief: A suitable option may be close, but staff input is needed before deciding.\n- desire: confirm the preferred choice\n- intention: move toward confirming the choice\n\nCandidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您想先看价格、功能，还是使用场景？, screen={'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}, voice_style=warm, light=neutral_prompt_color, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您想先看价格、功能，还是使用场景？\n- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）\n- Recommend_8d7f8993e333: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=这款可以作为一个参考选项。, screen={'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=soft_focus_on_recommendation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款可以作为一个参考选项。\n- Recommend_9ff23b139b07: act=Recommend, params={'target': 'item', 'pressure': 'firm'}, surface_text=这款最适合您，建议直接选这款。, screen={'action': 'show_fullscreen_recommendation', 'target': '{candidate_item}', 'cta': '立即购买'}, voice_style=firm, light=warm_red_or_yellow_guidance, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款最适合您，建议直接选这款。\n\nChoose the best intervention and explain your reasoning briefly.\n\nOutput the following fields, in this exact order:\n<rationale>...</rationale>\n<chosen>...</chosen>\n<intervention_action>...</intervention_action>\n<intervention_utterance>...</intervention_utterance>\n\n- chosen must be one of the candidate labels listed above, exact string match.\n- rationale should use the customer state and action fit, not hidden reward values.\n- intervention_action must describe the concrete salesperson or terminal behavior.\n- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence."
    },
    {
      "role": "assistant",
      "content": "<rationale>Rule-derived expectation: A3_strong_recommend from ready_to_decide leads to engaged_dialogue with low risk, high benefit, and reward 0.85.</rationale>\n<chosen>Recommend_8d7f8993e333</chosen>\n<intervention_action>智能售货柜按屏幕、语音、灯效执行该候选响应。</intervention_action>\n<intervention_utterance>这款可以作为一个参考选项。</intervention_utterance>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority256/piwm_1cc2c20d89/frames/002.jpg"
  ],
  "task": "action_selection_5act",
  "source_id": "general_recommend_piwm_1cc2c20d89",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": "synthetic_unreviewed",
    "human_review_status": "not_reviewed",
    "viewpoint": "salesperson_observable",
    "best_act": "Recommend",
    "candidate_action_acts": {
      "Elicit_b1166d372e5e": "Elicit",
      "Hold_eda24b4bb712": "Hold",
      "Recommend_8d7f8993e333": "Recommend",
      "Recommend_9ff23b139b07": "Recommend"
    },
    "five_act_only": true,
    "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
    "augmentation_policy": "target_v2_general_recommend_balance_to_41_v2",
    "augmented_from_state_id": null
  }
}
```

### Sample 2 (scene_id: piwm_b251a2cd8f, best_action: Elicit, 类型: 难例)

Selection note: Strict-pass. Elicit and Inform are close (0.83 vs 0.80), useful as near-tie decision example.

Quick candidate reward view derived from the matching `next_state_prediction` rows:

```json
[
  {
    "candidate_id": "Elicit_b1166d372e5e",
    "act": "Elicit",
    "next_stage": "desire",
    "reward": "0.83"
  },
  {
    "candidate_id": "Inform_5ff00ba15ca5",
    "act": "Inform",
    "next_stage": "desire",
    "reward": "0.80"
  },
  {
    "candidate_id": "Hold_eda24b4bb712",
    "act": "Hold",
    "next_stage": "interest",
    "reward": "0.20"
  },
  {
    "candidate_id": "Recommend_8d7f8993e333",
    "act": "Recommend",
    "next_stage": "attention",
    "reward": "-0.30"
  }
]
```

#### Section A: Scene Seed / Source Scene Record

Source: `data/official/piwm_train_synth_v2/main_schema.jsonl` line `377`

```json
{
  "act_params": {
    "openness": "open",
    "slot": "need_focus"
  },
  "actor_profile": "human_salesperson_logic",
  "aida_stage": "interest",
  "bdi": {
    "belief": "External prices, reviews, or specifications may change the choice.",
    "desire": "see how the product works",
    "intention": "ask for a demonstration"
  },
  "best_action": "Elicit_b1166d372e5e",
  "best_action_realization": {
    "physical_action": "智能售货柜按屏幕、语音、灯效执行该候选响应。",
    "rationale": "operational 5-act terminal realization for Elicit_b1166d372e5e",
    "timing": "设备前置摄像头检测到当前顾客状态后触发。",
    "utterance": "您想先看价格、功能，还是使用场景？"
  },
  "best_action_spec": {
    "act": "Elicit",
    "params": {
      "openness": "open",
      "slot": "need_focus"
    }
  },
  "candidate_action_specs": [
    {
      "act": "Elicit",
      "params": {
        "openness": "open",
        "slot": "need_focus"
      }
    },
    {
      "act": "Inform",
      "params": {
        "content_type": "demo",
        "depth": "brief"
      }
    },
    {
      "act": "Hold",
      "params": {
        "mode": "silent"
      }
    },
    {
      "act": "Recommend",
      "params": {
        "pressure": "soft",
        "target": "item"
      }
    }
  ],
  "candidate_actions": [
    "Elicit_b1166d372e5e",
    "Inform_5ff00ba15ca5",
    "Hold_eda24b4bb712",
    "Recommend_8d7f8993e333"
  ],
  "compatibility_tier": "green",
  "continuations": {},
  "dialogue_act": "Elicit",
  "images": [
    {
      "index": 0,
      "relative_path": "Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
      "timestamp_sec": null
    },
    {
      "index": 1,
      "relative_path": "Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
      "timestamp_sec": null
    },
    {
      "index": 2,
      "relative_path": "Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg",
      "timestamp_sec": null
    }
  ],
  "intent": "request_demonstration",
  "is_anchor": false,
  "latent_state": "active_evaluation",
  "legacy_mismatch_flags": [],
  "next_state_by_action": {
    "Elicit_b1166d372e5e": {
      "act_params": {
        "openness": "open",
        "slot": "need_focus"
      },
      "benefit": "high",
      "dialogue_act": "Elicit",
      "failure_mode": "若顾客正专注比较且未释放互动信号，连续提问可能造成时机侵入。",
      "intent_tier": "exploring",
      "next_aida_stage": "desire",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A4_open_with_question from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.83.",
      "reward": 0.83,
      "reward_components": {
        "action_cost": 0.1,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.4133333333333333,
        "delta_stage": 0.3333333333333333,
        "final_reward": 0.83,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Hold_eda24b4bb712": {
      "act_params": {
        "mode": "silent"
      },
      "benefit": "low",
      "dialogue_act": "Hold",
      "failure_mode": "若顾客正在主动比较却没有得到回应，静默可能延长犹豫。",
      "intent_tier": "exploring",
      "next_aida_stage": "interest",
      "next_bdi": {
        "belief": "Several options remain worth comparing.",
        "desire": "see how the product works",
        "intention": "ask for a demonstration"
      },
      "next_state": "active_evaluation",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A1_silent_observe from active_evaluation leads to active_evaluation with low risk, low benefit, and reward 0.20.",
      "reward": 0.2,
      "reward_components": {
        "action_cost": 0.0,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 0.4,
        "delta_stage": 0.0,
        "final_reward": 0.2,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Inform_5ff00ba15ca5": {
      "act_params": {
        "content_type": "demo",
        "depth": "brief"
      },
      "benefit": "high",
      "dialogue_act": "Inform",
      "failure_mode": "若顾客仍是低意图浏览，演示可能过早升级为信息负担。",
      "intent_tier": "exploring",
      "next_aida_stage": "desire",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A5_provide_demonstration from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.80.",
      "reward": 0.8,
      "reward_components": {
        "action_cost": 0.2,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.3733333333333335,
        "delta_stage": 0.3333333333333333,
        "final_reward": 0.8,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Recommend_8d7f8993e333": {
      "act_params": {
        "pressure": "soft",
        "target": "item"
      },
      "benefit": "low",
      "dialogue_act": "Recommend",
      "failure_mode": "若仍处在评估阶段，强推荐可能替代需求发现并造成防御。",
      "intent_tier": "exploring",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The salesperson may be applying too much pressure.",
        "desire": "avoid further engagement",
        "intention": "leave without buying"
      },
      "next_state": "defensive_withdrawal",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from active_evaluation leads to defensive_withdrawal with medium risk, low benefit, and reward -0.30.",
      "reward": -0.3,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": -0.2733333333333333,
        "delta_stage": -0.3333333333333333,
        "final_reward": -0.3,
        "gamma": 0.1
      },
      "risk": "medium",
      "risk_tags": []
    }
  },
  "next_state_by_action_v2": {
    "Elicit_b1166d372e5e": {
      "act_params": {
        "openness": "open",
        "slot": "need_focus"
      },
      "benefit": "high",
      "dialogue_act": "Elicit",
      "failure_mode": "若顾客正专注比较且未释放互动信号，连续提问可能造成时机侵入。",
      "intent_tier": "exploring",
      "next_aida_stage": "desire",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A4_open_with_question from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.83.",
      "reward": 0.83,
      "reward_components": {
        "action_cost": 0.1,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.4133333333333333,
        "delta_stage": 0.3333333333333333,
        "final_reward": 0.83,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Hold_eda24b4bb712": {
      "act_params": {
        "mode": "silent"
      },
      "benefit": "low",
      "dialogue_act": "Hold",
      "failure_mode": "若顾客正在主动比较却没有得到回应，静默可能延长犹豫。",
      "intent_tier": "exploring",
      "next_aida_stage": "interest",
      "next_bdi": {
        "belief": "Several options remain worth comparing.",
        "desire": "see how the product works",
        "intention": "ask for a demonstration"
      },
      "next_state": "active_evaluation",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A1_silent_observe from active_evaluation leads to active_evaluation with low risk, low benefit, and reward 0.20.",
      "reward": 0.2,
      "reward_components": {
        "action_cost": 0.0,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 0.4,
        "delta_stage": 0.0,
        "final_reward": 0.2,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Inform_5ff00ba15ca5": {
      "act_params": {
        "content_type": "demo",
        "depth": "brief"
      },
      "benefit": "high",
      "dialogue_act": "Inform",
      "failure_mode": "若顾客仍是低意图浏览，演示可能过早升级为信息负担。",
      "intent_tier": "exploring",
      "next_aida_stage": "desire",
      "next_bdi": {
        "belief": "The salesperson may help resolve the decision.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "engaged_dialogue",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A5_provide_demonstration from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.80.",
      "reward": 0.8,
      "reward_components": {
        "action_cost": 0.2,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.3733333333333335,
        "delta_stage": 0.3333333333333333,
        "final_reward": 0.8,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Recommend_8d7f8993e333": {
      "act_params": {
        "pressure": "soft",
        "target": "item"
      },
      "benefit": "low",
      "dialogue_act": "Recommend",
      "failure_mode": "若仍处在评估阶段，强推荐可能替代需求发现并造成防御。",
      "intent_tier": "exploring",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The salesperson may be applying too much pressure.",
        "desire": "avoid further engagement",
        "intention": "leave without buying"
      },
      "next_state": "defensive_withdrawal",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from active_evaluation leads to defensive_withdrawal with medium risk, low benefit, and reward -0.30.",
      "reward": -0.3,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": -0.2733333333333333,
        "delta_stage": -0.3333333333333333,
        "final_reward": -0.3,
        "gamma": 0.1
      },
      "risk": "medium",
      "risk_tags": []
    }
  },
  "observable_cues": [
    "checking_phone_likely_research"
  ],
  "persona": {
    "description": "A shopper buying for someone else and unsure which option fits best.",
    "intent_tier": "exploring",
    "type": "gift_buyer_uncertain"
  },
  "proactive_score": 3,
  "product_category": "electronics_laptop",
  "provenance": [
    {
      "field_name": "product_category",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "split",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "viewpoint",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "latent_state",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "visual_state",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "intent",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "bdi",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "proactive_score",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "candidate_actions",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "next_state_by_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "reward_by_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "best_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "best_action_realization",
      "rule_version": "v1.0",
      "source": "rule_derived"
    }
  ],
  "rationale": "Rule-derived expectation: A4_open_with_question from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.83.",
  "realization": {
    "act_params": {
      "openness": "open",
      "slot": "need_focus"
    },
    "cabinet_motion": null,
    "dialogue_act": "Elicit",
    "duration_ms": 4000,
    "legacy_action": null,
    "light": "neutral_prompt_color",
    "screen": {
      "action": "show_choice_bubbles",
      "choices": [
        "功能",
        "价格",
        "场景"
      ],
      "cta": null
    },
    "surface_text": "您想先看价格、功能，还是使用场景？",
    "voice_style": "warm"
  },
  "reward_by_action": {
    "Elicit_b1166d372e5e": 0.83,
    "Hold_eda24b4bb712": 0.2,
    "Inform_5ff00ba15ca5": 0.8,
    "Recommend_8d7f8993e333": -0.3
  },
  "schema_version": "dialogue_act_human_salesperson_v2.2",
  "split": "ood_persona",
  "state_id": "piwm_b251a2cd8f",
  "viewpoint": "surveillance_oblique",
  "visual_state": {
    "body_and_hands": "身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。",
    "engagement_pattern": "顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对配置、便携性、保修和未来几年使用成本，而不是已经准备成交。",
    "gaze_and_attention": "视线在手机和商品区域之间切换。 注意力可能在价格、评价和处理器/内存配置、屏幕尺寸、重量、续航和售后之间切换。",
    "summary": "顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是电脑陈列区，可见判断应围绕手机查询内容与配置、便携性、保修和未来几年使用成本之间的关系。视角为斜角监控/第三方视角。"
  }
}
```

#### Section B: user_intent Training Row

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `377`

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
      "content": "<stage>interest</stage>\n<intent_label>request_demonstration</intent_label>\n<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是电脑陈列区，可见判断应围绕手机查询内容与配置、便携性、保修和未来几年使用成本之间的关系。视角为斜角监控/第三方视角。</visual_summary>\n<engagement_pattern>顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对配置、便携性、保修和未来几年使用成本，而不是已经准备成交。</engagement_pattern>\n<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和处理器/内存配置、屏幕尺寸、重量、续航和售后之间切换。</gaze_and_attention>\n<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>\n<belief>External prices, reviews, or specifications may change the choice.</belief>\n<desire>see how the product works</desire>\n<intention>ask for a demonstration</intention>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "piwm_b251a2cd8f",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "ood_persona",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "surveillance_oblique",
    "stage": "interest",
    "intent_label": "request_demonstration",
    "loss_weight": 1.0,
    "loss_weight_policy": "a3plus_visual_intent_low_confidence"
  }
}
```

#### Section C: next_state_prediction Training Rows for Action Candidates

##### Candidate: Elicit_b1166d372e5e (Elicit)

Action prompt block from `action_selection_5act`:

```text
- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您想先看价格、功能，还是使用场景？, screen={'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}, voice_style=warm, light=neutral_prompt_color, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您想先看价格、功能，还是使用场景？
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `1864`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您想先看价格、功能，还是使用场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}\n- voice_style: warm\n- light: neutral_prompt_color\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 您想先看价格、功能，还是使用场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>desire</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.83</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_b251a2cd8f#Elicit_b1166d372e5e",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_b251a2cd8f",
    "candidate_action": "Elicit_b1166d372e5e",
    "candidate_act": "Elicit",
    "candidate_params": {
      "openness": "open",
      "slot": "need_focus"
    },
    "no_intervention_branch": false,
    "split": "ood_persona",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "surveillance_oblique"
  }
}
```

##### Candidate: Inform_5ff00ba15ca5 (Inform)

Action prompt block from `action_selection_5act`:

```text
- Inform_5ff00ba15ca5: act=Inform, params={'content_type': 'demo', 'depth': 'brief'}, surface_text=我给您演示一下这款的关键细节。, screen={'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=follow_demo_animation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=我给您演示一下这款的关键细节。
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `1865`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Inform_5ff00ba15ca5\n\nDialogue-act layer for this candidate:\n- act: Inform\n- params: {'content_type': 'demo', 'depth': 'brief'}\n\nTerminal realization for this candidate:\n- surface_text: 我给您演示一下这款的关键细节。\n- screen: {'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None}\n- voice_style: neutral\n- light: follow_demo_animation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 我给您演示一下这款的关键细节。\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>desire</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_b251a2cd8f#Inform_5ff00ba15ca5",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_b251a2cd8f",
    "candidate_action": "Inform_5ff00ba15ca5",
    "candidate_act": "Inform",
    "candidate_params": {
      "content_type": "demo",
      "depth": "brief"
    },
    "no_intervention_branch": false,
    "split": "ood_persona",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "surveillance_oblique"
  }
}
```

##### Candidate: Hold_eda24b4bb712 (Hold)

Action prompt block from `action_selection_5act`:

```text
- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `1866`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Hold_eda24b4bb712\n\nDialogue-act layer for this candidate:\n- act: Hold\n- params: {'mode': 'silent'}\n\nTerminal realization for this candidate:\n- surface_text: \n- screen: {'action': 'idle_minimal', 'cta': None}\n- voice_style: silent\n- light: maintain_current_soft_breathing\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: （静默）\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>interest</next_stage>\n<next_belief>Several options remain worth comparing.</next_belief>\n<next_desire>see how the product works</next_desire>\n<next_intention>ask for a demonstration</next_intention>\n<risk>low</risk>\n<benefit>low</benefit>\n<reward>0.20</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_b251a2cd8f#Hold_eda24b4bb712",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_b251a2cd8f",
    "candidate_action": "Hold_eda24b4bb712",
    "candidate_act": "Hold",
    "candidate_params": {
      "mode": "silent"
    },
    "no_intervention_branch": true,
    "split": "ood_persona",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "surveillance_oblique"
  }
}
```

##### Candidate: Recommend_8d7f8993e333 (Recommend)

Action prompt block from `action_selection_5act`:

```text
- Recommend_8d7f8993e333: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=这款可以作为一个参考选项。, screen={'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=soft_focus_on_recommendation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款可以作为一个参考选项。
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `1867`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Recommend_8d7f8993e333\n\nDialogue-act layer for this candidate:\n- act: Recommend\n- params: {'target': 'item', 'pressure': 'soft'}\n\nTerminal realization for this candidate:\n- surface_text: 这款可以作为一个参考选项。\n- screen: {'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}\n- voice_style: neutral\n- light: soft_focus_on_recommendation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 这款可以作为一个参考选项。\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>attention</next_stage>\n<next_belief>The salesperson may be applying too much pressure.</next_belief>\n<next_desire>avoid further engagement</next_desire>\n<next_intention>leave without buying</next_intention>\n<risk>medium</risk>\n<benefit>low</benefit>\n<reward>-0.30</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_b251a2cd8f#Recommend_8d7f8993e333",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_b251a2cd8f",
    "candidate_action": "Recommend_8d7f8993e333",
    "candidate_act": "Recommend",
    "candidate_params": {
      "target": "item",
      "pressure": "soft"
    },
    "no_intervention_branch": false,
    "split": "ood_persona",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "surveillance_oblique"
  }
}
```

#### Section D: action_selection_5act Training Row

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `2649`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe Stage-1 customer-state representation is:\n- stage: interest\n- intent_label: request_demonstration\n- visible evidence: 顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是电脑陈列区，可见判断应围绕手机查询内容与配置、便携性、保修和未来几年使用成本之间的关系。视角为斜角监控/第三方视角。\n- engagement pattern: 顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对配置、便携性、保修和未来几年使用成本，而不是已经准备成交。\n- gaze and attention: 视线在手机和商品区域之间切换。 注意力可能在价格、评价和处理器/内存配置、屏幕尺寸、重量、续航和售后之间切换。\n- body and hands: 身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。\n- belief: External prices, reviews, or specifications may change the choice.\n- desire: see how the product works\n- intention: ask for a demonstration\n\nCandidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您想先看价格、功能，还是使用场景？, screen={'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}, voice_style=warm, light=neutral_prompt_color, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您想先看价格、功能，还是使用场景？\n- Inform_5ff00ba15ca5: act=Inform, params={'content_type': 'demo', 'depth': 'brief'}, surface_text=我给您演示一下这款的关键细节。, screen={'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=follow_demo_animation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=我给您演示一下这款的关键细节。\n- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）\n- Recommend_8d7f8993e333: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=这款可以作为一个参考选项。, screen={'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=soft_focus_on_recommendation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款可以作为一个参考选项。\n\nChoose the best intervention and explain your reasoning briefly.\n\nOutput the following fields, in this exact order:\n<rationale>...</rationale>\n<chosen>...</chosen>\n<intervention_action>...</intervention_action>\n<intervention_utterance>...</intervention_utterance>\n\n- chosen must be one of the candidate labels listed above, exact string match.\n- rationale should use the customer state and action fit, not hidden reward values.\n- intervention_action must describe the concrete salesperson or terminal behavior.\n- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence."
    },
    {
      "role": "assistant",
      "content": "<rationale>Rule-derived expectation: A4_open_with_question from active_evaluation leads to engaged_dialogue with low risk, high benefit, and reward 0.83.</rationale>\n<chosen>Elicit_b1166d372e5e</chosen>\n<intervention_action>智能售货柜按屏幕、语音、灯效执行该候选响应。</intervention_action>\n<intervention_utterance>您想先看价格、功能，还是使用场景？</intervention_utterance>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_b251a2cd8f/frames/002.jpg"
  ],
  "task": "action_selection_5act",
  "source_id": "general_elicit_piwm_b251a2cd8f",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": "synthetic_unreviewed",
    "human_review_status": "not_reviewed",
    "viewpoint": "surveillance_oblique",
    "best_act": "Elicit",
    "candidate_action_acts": {
      "Elicit_b1166d372e5e": "Elicit",
      "Inform_5ff00ba15ca5": "Inform",
      "Hold_eda24b4bb712": "Hold",
      "Recommend_8d7f8993e333": "Recommend"
    },
    "five_act_only": true,
    "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
    "augmentation_policy": "target_v2_general_elicit_balance_to_41_v2",
    "augmented_from_state_id": null
  }
}
```

### Sample 3 (scene_id: piwm_00539e313f, best_action: Hold, 类型: HOLD)

Selection note: Best-effort HOLD example. It has all three task types and complete next-state labels, but violates hard filter #2 because all Hold action-selection rows have exactly 2 candidates in the current training mix.

Quick candidate reward view derived from the matching `next_state_prediction` rows:

```json
[
  {
    "candidate_id": "Hold_eda24b4bb712",
    "act": "Hold",
    "next_stage": "attention",
    "reward": "0.50"
  },
  {
    "candidate_id": "Recommend_8d7f8993e333",
    "act": "Recommend",
    "next_stage": "attention",
    "reward": "-0.60"
  }
]
```

#### Section A: Scene Seed / Source Scene Record

Source: `data/official/piwm_train_synth_v2/main_schema.jsonl` line `260`

```json
{
  "act_params": {
    "mode": "silent"
  },
  "actor_profile": "human_salesperson_logic",
  "aida_stage": "attention",
  "bdi": {
    "belief": "The category is only mildly interesting, and interruption may feel premature.",
    "desire": "explore available options",
    "intention": "continue browsing and comparing"
  },
  "best_action": "Hold_eda24b4bb712",
  "best_action_realization": {
    "physical_action": "智能售货柜按屏幕、语音、灯效执行该候选响应。",
    "rationale": "operational 5-act terminal realization for Hold_eda24b4bb712",
    "timing": "设备前置摄像头检测到当前顾客状态后触发。",
    "utterance": "（静默）"
  },
  "best_action_spec": {
    "act": "Hold",
    "params": {
      "mode": "silent"
    }
  },
  "candidate_action_specs": [
    {
      "act": "Hold",
      "params": {
        "mode": "silent"
      }
    },
    {
      "act": "Recommend",
      "params": {
        "pressure": "soft",
        "target": "item"
      }
    }
  ],
  "candidate_actions": [
    "Hold_eda24b4bb712",
    "Recommend_8d7f8993e333"
  ],
  "compatibility_tier": "green",
  "continuations": {},
  "dialogue_act": "Hold",
  "images": [
    {
      "index": 0,
      "relative_path": "Archive_generated_priority500_new_after280/piwm_00539e313f/frames/000.jpg",
      "timestamp_sec": null
    },
    {
      "index": 1,
      "relative_path": "Archive_generated_priority500_new_after280/piwm_00539e313f/frames/001.jpg",
      "timestamp_sec": null
    },
    {
      "index": 2,
      "relative_path": "Archive_generated_priority500_new_after280/piwm_00539e313f/frames/002.jpg",
      "timestamp_sec": null
    }
  ],
  "intent": "explore_options",
  "is_anchor": false,
  "latent_state": "early_browsing",
  "legacy_mismatch_flags": [],
  "next_state_by_action": {
    "Hold_eda24b4bb712": {
      "act_params": {
        "mode": "silent"
      },
      "benefit": "medium",
      "dialogue_act": "Hold",
      "failure_mode": null,
      "intent_tier": "exploring",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The category is worth a brief look, but commitment is low.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "early_browsing",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A1_silent_observe from early_browsing leads to early_browsing with low risk, medium benefit, and reward 0.50.",
      "reward": 0.5,
      "reward_components": {
        "action_cost": 0.0,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.0,
        "delta_stage": 0.0,
        "final_reward": 0.5,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Recommend_8d7f8993e333": {
      "act_params": {
        "pressure": "soft",
        "target": "item"
      },
      "benefit": "low",
      "dialogue_act": "Recommend",
      "failure_mode": "若顾客还在早期浏览，强推荐是过早 closing，容易直接劝退。",
      "intent_tier": "exploring",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The current interaction is not useful enough to continue.",
        "desire": "avoid further engagement",
        "intention": "leave without buying"
      },
      "next_state": "disengaged",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from early_browsing leads to disengaged with high risk, low benefit, and reward -0.60.",
      "reward": -0.6,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": -1.14,
        "delta_stage": 0.0,
        "final_reward": -0.6,
        "gamma": 0.1
      },
      "risk": "high",
      "risk_tags": []
    }
  },
  "next_state_by_action_v2": {
    "Hold_eda24b4bb712": {
      "act_params": {
        "mode": "silent"
      },
      "benefit": "medium",
      "dialogue_act": "Hold",
      "failure_mode": null,
      "intent_tier": "exploring",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The category is worth a brief look, but commitment is low.",
        "desire": "explore available options",
        "intention": "continue browsing and comparing"
      },
      "next_state": "early_browsing",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A1_silent_observe from early_browsing leads to early_browsing with low risk, medium benefit, and reward 0.50.",
      "reward": 0.5,
      "reward_components": {
        "action_cost": 0.0,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": 1.0,
        "delta_stage": 0.0,
        "final_reward": 0.5,
        "gamma": 0.1
      },
      "risk": "low",
      "risk_tags": []
    },
    "Recommend_8d7f8993e333": {
      "act_params": {
        "pressure": "soft",
        "target": "item"
      },
      "benefit": "low",
      "dialogue_act": "Recommend",
      "failure_mode": "若顾客还在早期浏览，强推荐是过早 closing，容易直接劝退。",
      "intent_tier": "exploring",
      "next_aida_stage": "attention",
      "next_bdi": {
        "belief": "The current interaction is not useful enough to continue.",
        "desire": "avoid further engagement",
        "intention": "leave without buying"
      },
      "next_state": "disengaged",
      "outcome_type": "success",
      "rationale": "Rule-derived expectation: A3_strong_recommend from early_browsing leads to disengaged with high risk, low benefit, and reward -0.60.",
      "reward": -0.6,
      "reward_components": {
        "action_cost": 0.3,
        "alpha": 0.4,
        "beta": 0.5,
        "delta_mental": -1.14,
        "delta_stage": 0.0,
        "final_reward": -0.6,
        "gamma": 0.1
      },
      "risk": "high",
      "risk_tags": []
    }
  },
  "observable_cues": [
    "brief_glance_walking_past"
  ],
  "persona": {
    "description": "A careful shopper who repeatedly weighs price and value before engaging.",
    "intent_tier": "exploring",
    "type": "price_sensitive_cautious"
  },
  "proactive_score": 2,
  "product_category": "footwear",
  "provenance": [
    {
      "field_name": "product_category",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "split",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "viewpoint",
      "rule_version": "v1.0",
      "source": "prompt_json"
    },
    {
      "field_name": "latent_state",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "visual_state",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "intent",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "bdi",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "proactive_score",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "candidate_actions",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "next_state_by_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "reward_by_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "best_action",
      "rule_version": "v1.0",
      "source": "rule_derived"
    },
    {
      "field_name": "best_action_realization",
      "rule_version": "v1.0",
      "source": "rule_derived"
    }
  ],
  "rationale": "Rule-derived expectation: A1_silent_observe from early_browsing leads to early_browsing with low risk, medium benefit, and reward 0.50.",
  "realization": {
    "act_params": {
      "mode": "silent"
    },
    "cabinet_motion": null,
    "dialogue_act": "Hold",
    "duration_ms": 0,
    "legacy_action": null,
    "light": "maintain_current_soft_breathing",
    "screen": {
      "action": "idle_minimal",
      "cta": null
    },
    "surface_text": "",
    "voice_style": "silent"
  },
  "reward_by_action": {
    "Hold_eda24b4bb712": 0.5,
    "Recommend_8d7f8993e333": -0.6
  },
  "schema_version": "dialogue_act_human_salesperson_v2.2",
  "split": "ood_product",
  "state_id": "piwm_00539e313f",
  "viewpoint": "salesperson_observable",
  "visual_state": {
    "body_and_hands": "身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。",
    "engagement_pattern": "顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。",
    "gaze_and_attention": "视线短暂扫过商品区域，很快离开。",
    "summary": "顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是鞋类商品区，可见判断应围绕是否形成对鞋类商品的稳定兴趣，而不是深度比较。视角为导购可观察中近距离视角。"
  }
}
```

#### Section B: user_intent Training Row

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `260`

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
      "content": "<stage>attention</stage>\n<intent_label>explore_options</intent_label>\n<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是鞋类商品区，可见判断应围绕是否形成对鞋类商品的稳定兴趣，而不是深度比较。视角为导购可观察中近距离视角。</visual_summary>\n<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>\n<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>\n<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>\n<belief>The category is only mildly interesting, and interruption may feel premature.</belief>\n<desire>explore available options</desire>\n<intention>continue browsing and comparing</intention>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "piwm_00539e313f",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "ood_product",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable",
    "stage": "attention",
    "intent_label": "explore_options",
    "loss_weight": 1.0,
    "loss_weight_policy": "a3plus_visual_intent_low_confidence"
  }
}
```

#### Section C: next_state_prediction Training Rows for Action Candidates

##### Candidate: Hold_eda24b4bb712 (Hold)

Action prompt block from `action_selection_5act`:

```text
- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `1458`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Hold_eda24b4bb712\n\nDialogue-act layer for this candidate:\n- act: Hold\n- params: {'mode': 'silent'}\n\nTerminal realization for this candidate:\n- surface_text: \n- screen: {'action': 'idle_minimal', 'cta': None}\n- voice_style: silent\n- light: maintain_current_soft_breathing\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: （静默）\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>attention</next_stage>\n<next_belief>The category is worth a brief look, but commitment is low.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.50</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_00539e313f#Hold_eda24b4bb712",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_00539e313f",
    "candidate_action": "Hold_eda24b4bb712",
    "candidate_act": "Hold",
    "candidate_params": {
      "mode": "silent"
    },
    "no_intervention_branch": true,
    "split": "ood_product",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  }
}
```

##### Candidate: Recommend_8d7f8993e333 (Recommend)

Action prompt block from `action_selection_5act`:

```text
- Recommend_8d7f8993e333: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=这款可以作为一个参考选项。, screen={'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=soft_focus_on_recommendation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款可以作为一个参考选项。
```

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `1459`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Recommend_8d7f8993e333\n\nDialogue-act layer for this candidate:\n- act: Recommend\n- params: {'target': 'item', 'pressure': 'soft'}\n\nTerminal realization for this candidate:\n- surface_text: 这款可以作为一个参考选项。\n- screen: {'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}\n- voice_style: neutral\n- light: soft_focus_on_recommendation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。\n- utterance: 这款可以作为一个参考选项。\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>attention</next_stage>\n<next_belief>The current interaction is not useful enough to continue.</next_belief>\n<next_desire>avoid further engagement</next_desire>\n<next_intention>leave without buying</next_intention>\n<risk>high</risk>\n<benefit>low</benefit>\n<reward>-0.60</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "piwm_00539e313f#Recommend_8d7f8993e333",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "piwm_00539e313f",
    "candidate_action": "Recommend_8d7f8993e333",
    "candidate_act": "Recommend",
    "candidate_params": {
      "target": "item",
      "pressure": "soft"
    },
    "no_intervention_branch": false,
    "split": "ood_product",
    "qa_status": null,
    "human_review_status": null,
    "viewpoint": "salesperson_observable"
  }
}
```

#### Section D: action_selection_5act Training Row

Source: `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl` line `2694`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe Stage-1 customer-state representation is:\n- stage: attention\n- intent_label: explore_options\n- visible evidence: 顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是鞋类商品区，可见判断应围绕是否形成对鞋类商品的稳定兴趣，而不是深度比较。视角为导购可观察中近距离视角。\n- engagement pattern: 顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。\n- gaze and attention: 视线短暂扫过商品区域，很快离开。\n- body and hands: 身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。\n- belief: The category is only mildly interesting, and interruption may feel premature.\n- desire: explore available options\n- intention: continue browsing and comparing\n\nCandidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）\n- Recommend_8d7f8993e333: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=这款可以作为一个参考选项。, screen={'action': 'highlight_item', 'target': '{candidate_item}', 'cta': None}, voice_style=neutral, light=soft_focus_on_recommendation, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=这款可以作为一个参考选项。\n\nChoose the best intervention and explain your reasoning briefly.\n\nOutput the following fields, in this exact order:\n<rationale>...</rationale>\n<chosen>...</chosen>\n<intervention_action>...</intervention_action>\n<intervention_utterance>...</intervention_utterance>\n\n- chosen must be one of the candidate labels listed above, exact string match.\n- rationale should use the customer state and action fit, not hidden reward values.\n- intervention_action must describe the concrete salesperson or terminal behavior.\n- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence."
    },
    {
      "role": "assistant",
      "content": "<rationale>Rule-derived expectation: A1_silent_observe from early_browsing leads to early_browsing with low risk, medium benefit, and reward 0.50.</rationale>\n<chosen>Hold_eda24b4bb712</chosen>\n<intervention_action>智能售货柜按屏幕、语音、灯效执行该候选响应。</intervention_action>\n<intervention_utterance>（静默）</intervention_utterance>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority500_new_after280/piwm_00539e313f/frames/002.jpg"
  ],
  "task": "action_selection_5act",
  "source_id": "general_hold_piwm_00539e313f",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "train",
    "qa_status": "synthetic_unreviewed",
    "human_review_status": "not_reviewed",
    "viewpoint": "salesperson_observable",
    "best_act": "Hold",
    "candidate_action_acts": {
      "Hold_eda24b4bb712": "Hold",
      "Recommend_8d7f8993e333": "Recommend"
    },
    "five_act_only": true,
    "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
    "augmentation_policy": "target_v2_general_hold_balance_to_41_v2",
    "augmented_from_state_id": null
  }
}
```
