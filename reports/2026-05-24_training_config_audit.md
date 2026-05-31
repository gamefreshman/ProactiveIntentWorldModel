5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# Stage-1 / Stage-2 训练配置审计

本报告只读检查训练数据样本和 checkpoint 配置；没有跑训练、没有跑推理、没有修改数据或代码。

## 结论先行

PIWM 主模型的 Stage-2 不是“只拿 190 条动作样本单独训练”，而是用一个 joint 训练文件继续训练同一个 LoRA：`2544` 条 Stage-1 多字段任务 + `190` 条 Stage-2 action-only 任务，共 `2734` 条。Stage-2 的动作样本输出只监督 `<chosen>` 和干预话术，不监督 stage、intent、next_state、BDI 或 reward。

这意味着 representation collapse 的最可能机制不是“Stage-1 数据完全没 replay”，而是：目标域动作选择训练把模型优化到“给定已有 state 表征后直接输出动作”，但没有要求它在目标域继续显式输出并保持 stage/intent/next_state 表征；同时同一个 LoRA 从 Stage-1 继续训练，可能产生输出空间干扰和目标域 prompt 分布偏移。

## Q1：Stage-2 训练数据的 prompt/output 格式

**答案**：Stage-2 action-selection 样本的 assistant output 是 action-only 风格。它包含 `rationale / chosen / intervention_action / intervention_utterance`，但不包含 `stage / intent_label / next_state / BDI / reward` 等中间字段。注意：user prompt 里会给出 Stage-1 customer-state representation，因此动作选择任务是在“已给当前状态摘要”的条件下选动作。

原始证据：

> source_file: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl
> row_index: 0
> task_type: action_selection_5act
> task_id: None
> images: ["/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_709/000.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_709/001.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_709/002.jpg"]
> meta: {
>   "split": "train",
>   "qa_status": "synthetic_unreviewed",
>   "human_review_status": null,
>   "viewpoint": "target_frontcam",
>   "best_act": "Elicit",
>   "candidate_action_acts": {
>     "Elicit_b1166d372e5e": "Elicit",
>     "Inform_24926eed1e21": "Inform",
>     "Recommend_interest_stage_conditioned_target_piwm_709_e23e42313b98": "Recommend",
>     "Hold_eda24b4bb712": "Hold"
>   },
>   "five_act_only": true,
>   "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
>   "augmentation_policy": null,
>   "augmented_from_state_id": null
> }
>
> SYSTEM:
> You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.
>
> USER:
> <image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.
>
>
>
>
>
> The Stage-1 customer-state representation is:
> - stage: interest
> - intent_label: explore_options
> - visible evidence: 他站在设备前缓慢扫视，目光在镜头下方某处停留片刻后又移开，右手握着手机不急于操作，左手偶尔轻轻抬起又放下。
> - engagement pattern: 他站在设备前缓慢扫视，目光在镜头下方某处停留片刻后又移开，右手握着手机不急于操作，左手偶尔轻轻抬起又放下。
> - gaze and attention: 表情平静但略带迟疑，眉头轻微收紧，嘴唇自然闭合，眼神专注中带着思考。
> - body and hands: 身体正面朝向镜头，肩膀放松，微微前倾，双手保持在胸腹部附近的画面内，姿态克制而缓慢。
> - belief: 他认为这台智能设备可能有适合自己临时补充能量的选择，但还不确定是否真的需要购买。
> - desire: 他想快速判断有没有值得买的东西，同时避免冲动消费。
> - intention: 他倾向于再观察几秒并比较心中的需求，如果仍觉得合适才会继续操作。
>
> Candidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.
>
> - Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您今天想先看价格、功能，还是适合什么场景？, screen={'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}, voice_style=curious, light=soft_invitation, physical_action=智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。, utterance=您今天想先看价格、功能，还是适合什么场景？
> - Inform_24926eed1e21: act=Inform, params={'content_type': 'attributes', 'depth': 'brief'}, surface_text=您好，需要时我可以帮您说明。, screen={'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None}, voice_style=warm, light=soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您好，需要时我可以帮您说明。
> - Recommend_interest_stage_conditioned_target_piwm_709_e23e42313b98: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=如果您想省心选择，可以优先看这款更稳妥的。, screen={'action': 'highlight_soft_recommendation', 'cta': None}, voice_style=calm, light=highlight_one_option_soft, physical_action=智能售货柜轻量高亮一个选项，并保留顾客选择空间。, utterance=如果您想省心选择，可以优先看这款更稳妥的。
> - Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）
>
> Choose the best intervention and explain your reasoning briefly.
>
> Output the following fields, in this exact order:
> <rationale>...</rationale>
> <chosen>...</chosen>
> <intervention_action>...</intervention_action>
> <intervention_utterance>...</intervention_utterance>
>
> - chosen must be one of the candidate labels listed above, exact string match.
> - rationale should use the customer state and action fit, not hidden reward values.
> - intervention_action must describe the concrete salesperson or terminal behavior.
> - intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.
> - In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence.
>
> ASSISTANT:
> <rationale>开放式引导提升被理解感，促进关注点聚焦，有助于从泛兴趣向明确探索转变。</rationale>
> <chosen>Elicit_b1166d372e5e</chosen>
> <intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
> <intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>

一句话总结：Stage-2 输出没有显式维护顾客状态或动作后果表征，只训练“看到状态摘要和候选动作后选哪个动作”。

## Q2：Stage-1 训练数据的 prompt/output 格式

**答案**：Stage-1 是多字段监督，包含两类任务。

- `user_intent`：输出当前 `stage`、`intent_label`、视觉摘要、engagement、gaze、body，以及 BDI 三字段 `belief/desire/intention`。
- `next_state_prediction`：输出候选动作后的 `next_stage`、`next_belief/next_desire/next_intention`、`risk/benefit/reward`。

`user_intent` 原始证据：

> source_file: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
> row_index: 0
> task_type: user_intent
> task_id: None
> images: ["/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"]
> meta: {
>   "split": "train",
>   "qa_status": null,
>   "human_review_status": null,
>   "viewpoint": "salesperson_observable",
>   "stage": "interest",
>   "intent_label": "request_demonstration",
>   "loss_weight": 1.0,
>   "loss_weight_policy": "a3plus_visual_intent_low_confidence"
> }
>
> SYSTEM:
> You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.
>
> USER:
> <image><image><image>You are observing a short customer-behavior window.
>
> Scene: 顾客在零售店内。
>
> Below are 3 frames sampled from a streaming camera, in chronological order.
>
>
>
>
>
> Infer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.
>
> Output the following fields, in this exact order, each on its own line:
> <stage>...</stage>
> <intent_label>...</intent_label>
> <visual_summary>...</visual_summary>
> <engagement_pattern>...</engagement_pattern>
> <gaze_and_attention>...</gaze_and_attention>
> <body_and_hands>...</body_and_hands>
> <belief>...</belief>
> <desire>...</desire>
> <intention>...</intention>
>
> - stage must be one of: attention, interest, desire, action.
> - intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.
> - visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.
> - belief, desire, and intention must be short customer-state clauses, not salesperson advice.
>
> ASSISTANT:
> <stage>interest</stage>
> <intent_label>request_demonstration</intent_label>
> <visual_summary>顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。</visual_summary>
> <engagement_pattern>顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。</engagement_pattern>
> <gaze_and_attention>视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。</gaze_and_attention>
> <body_and_hands>身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。</body_and_hands>
> <belief>A companion's approval may influence whether the choice feels safe.</belief>
> <desire>see how the product works</desire>
> <intention>ask for a demonstration</intention>

`next_state_prediction` 原始证据：

> source_file: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
> row_index: 0
> task_type: next_state_prediction
> task_id: None
> images: ["/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/000.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/001.jpg", "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/Archive_generated_priority24/piwm_09df40aae2/frames/002.jpg"]
> meta: {
>   "parent_state_id": "piwm_09df40aae2",
>   "candidate_action": "Elicit_b1166d372e5e",
>   "candidate_act": "Elicit",
>   "candidate_params": {
>     "openness": "open",
>     "slot": "need_focus"
>   },
>   "no_intervention_branch": false,
>   "split": "train",
>   "qa_status": null,
>   "human_review_status": null,
>   "viewpoint": "salesperson_observable"
> }
>
> SYSTEM:
> You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.
>
> USER:
> <image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.
>
>
>
>
>
> Use the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.
>
> Consider one candidate intervention: Elicit_b1166d372e5e
>
> Dialogue-act layer for this candidate:
> - act: Elicit
> - params: {'openness': 'open', 'slot': 'need_focus'}
>
> Terminal realization for this candidate:
> - surface_text: 您想先看价格、功能，还是使用场景？
> - screen: {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None}
> - voice_style: warm
> - light: neutral_prompt_color
>
> Concrete execution plan for this candidate:
> - physical action: 智能售货柜按屏幕、语音、灯效执行该候选响应。
> - utterance: 您想先看价格、功能，还是使用场景？
>
> Predict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:
> <next_stage>...</next_stage>
> <next_belief>...</next_belief>
> <next_desire>...</next_desire>
> <next_intention>...</next_intention>
> <risk>...</risk>
> <benefit>...</benefit>
> <reward>...</reward>
>
> - next_stage must be one of: attention, interest, desire, action.
> - risk and benefit must each be one of: low, medium, high.
> - reward must be a number in [-1.00, 1.00] with two decimal places.
> - all textual spans must be a single short clause in English.
>
> ASSISTANT:
> <next_stage>desire</next_stage>
> <next_belief>The salesperson may help resolve the decision.</next_belief>
> <next_desire>explore available options</next_desire>
> <next_intention>continue browsing and comparing</next_intention>
> <risk>low</risk>
> <benefit>high</benefit>
> <reward>0.83</reward>

一句话总结：Stage-1 明确训练“看图识别当前状态”和“给定候选动作预测后果”，字段远多于 Stage-2 的动作选择输出。

## Q3：Stage-2 训练数据组成

**答案**：Stage-2 190 条本身是 `100% action_selection_5act`，且 `100% action-only output`。但 PIWM 主模型实际训练时使用的是 joint 文件，里面混入了 Stage-1 原始任务：`543` 条 user_intent、`2001` 条 next_state_prediction、`190` 条 action_selection_5act。

原始证据：

> stage2_only_file: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage2_target_v2_balanced.jsonl
> stage2_rows: 190
> stage2_task_counts: {'action_selection_5act': 190}
> stage2_output_style_counts: {'action_only': 190}
>
> joint_training_file: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_plus_stage2_target_v2_balanced.jsonl
> joint_rows: 2734
> joint_task_counts: {'user_intent': 543, 'next_state_prediction': 2001, 'action_selection_5act': 190}
> joint_output_style_counts: {'stage1_style': 2544, 'action_only': 190}
>
> summary_file: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage2_target_v2_balanced_summary.json
> summary_excerpt:
> {
>   "stage2_rows": null,
>   "joint_rows": null,
>   "stage2_write_summary": null,
>   "joint_write_summary": null
> }

一句话总结：如果只看 Stage-2 文件，它是纯 action-only；如果看主模型实际训练文件，它确实 replay 了 Stage-1，但动作选择部分仍然不要求模型输出中间表征。

## Q4：Stage-2 LoRA 配置

**答案**：主模型训练使用 Qwen2.5-VL-7B-Instruct + LoRA，关键配置如下。

- LoRA rank：`16`
- LoRA alpha：`32`
- target modules：训练参数写 `all-linear`，adapter 实际展开到 q/k/v/o/up/down/gate projection
- learning rate：`2e-5`
- epoch：`3.0`
- per-device batch size：`4`
- gradient accumulation：`2`
- max length：`8192`
- max pixels：`1003520`

原始证据：

> remote checkpoint requested by PI:
> /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3full-20260522-220941-px1003520-ml8192/checkpoint-500
>
> resolved run args copied to:
> /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/training_config_audit_remote_20260524/run_args.json
>
> selected run_args.json fields:
> {
>   "remote_run_dir": "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953",
>   "checkpoint": "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500",
>   "dataset": [
>     "data/official/ms_swift_targetv2_balanced_20260524/piwm_train_stage1_plus_stage2_target_v2_balanced.server_resolved.jsonl"
>   ],
>   "val_dataset": [
>     "data/official/ms_swift_pathC_symmetry_20260521/piwm_train_stage1_user_intent_val_v1.jsonl",
>     "data/official/ms_swift_pathC_symmetry_20260521/piwm_train_stage1_next_state_prediction_val_v1.jsonl"
>   ],
>   "model": "/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct",
>   "ckpt_dir": "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432",
>   "resume_from_checkpoint": null,
>   "lora_rank": 16,
>   "lora_alpha": 32,
>   "target_modules": [
>     "all-linear"
>   ],
>   "learning_rate": 2e-05,
>   "num_train_epochs": 3.0,
>   "per_device_train_batch_size": 4,
>   "gradient_accumulation_steps": 2,
>   "max_length": 8192,
>   "max_pixels": 1003520
> }
>
> selected adapter_config.json fields (/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/training_config_audit_remote_20260524/adapter_config.json):
> {
>   "base_model_name_or_path": "/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct",
>   "peft_type": "LORA",
>   "r": 16,
>   "lora_alpha": 32,
>   "lora_dropout": 0.05,
>   "target_modules": "^(model(?=\\.).*\\.(k_proj|up_proj|v_proj|down_proj|gate_proj|o_proj|q_proj))$",
>   "inference_mode": true
> }
>
> selected trainer_state.json fields (/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/training_config_audit_remote_20260524/trainer_state.json):
> {
>   "best_model_checkpoint": "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500",
>   "global_step": 500,
>   "max_steps": 513,
>   "num_train_epochs": 3,
>   "last_log_history": {
>     "epoch": 2.9239766081871346,
>     "eval_loss": 0.011731015518307686,
>     "eval_runtime": 543.2649,
>     "eval_samples_per_second": 0.433,
>     "eval_steps_per_second": 0.055,
>     "eval_token_acc": 0.9951282662760195,
>     "step": 500
>   }
> }

一句话总结：Stage-2 配置不是小学习率冻结式适配，而是在 Stage-1 checkpoint 上继续用 LoRA r=16、lr=2e-5 训练 3 epoch。

## Q5：Stage-2 vs Stage-1 的 LoRA adapter 关系

**答案**：最符合选项 **(a) 在 Stage-1 LoRA 之上继续训练同一个 adapter**。证据是 `run_args.json` 里 `ckpt_dir` 指向 Stage-1 checkpoint-432，`resume_from_checkpoint` 为 `null`，输出目录是新的 a3 full run。adapter_config 里只有一个 LoRA adapter 配置，base model 仍是 Qwen2.5-VL-7B-Instruct，没有发现两个 adapter stack，也没有发现先 merge Stage-1 再新开 Stage-2 LoRA 的配置证据。

需要精确表述：物理文件上是保存到一个新的 run/checkpoint 目录；训练语义上是从 Stage-1 LoRA checkpoint 继续优化并产出新的单 LoRA adapter。

原始证据：

> {
>   "ckpt_dir": "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432",
>   "resume_from_checkpoint": null,
>   "output_dir": "/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953",
>   "adapter_base_model": "/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct",
>   "adapter_peft_type": "LORA",
>   "adapter_target_modules": "^(model(?=\\.).*\\.(k_proj|up_proj|v_proj|down_proj|gate_proj|o_proj|q_proj))$"
> }

一句话总结：不是 fresh LoRA，也不是 Stage-1 LoRA + Stage-2 LoRA 双 adapter；它是在 Stage-1 adapter 基础上继续训练出的新单 adapter。

## 机制定位

基于这 5 个答案，PIWM representation collapse 最可能来自 **目标域 action-only 监督与 Stage-1 多字段监督之间的输出空间干扰**，并叠加 **Stage-2 action prompt 中直接提供 Stage-1 state representation** 的设计。

具体机制判断：

1. Stage-1 教模型输出 stage/intent/BDI/next_state/reward；Stage-2 动作样本只要求输出 chosen/action/utterance，不要求保持或复述这些中间变量。
2. 主模型继续训练同一个 LoRA，目标域动作选择虽然只占 190/2734 行，但它是最终任务，且 prompt 明确给了当前 state 表征，模型可以绕过“从图像重新恢复状态”的能力，直接把给定 state + candidate list 映射到动作。
3. 训练时的验证集只看到 Stage-1 val 文件，没有 target action-selection val；`eval_loss` 很低不等于目标域 Dim 1/2/3 表征被保持。
4. 因此 Dim 4 best_act 可以高，而 Dim 1/2/3 在 target test 上退化并不矛盾：模型学到了动作选择捷径，但没有在目标域维持可单独评估的显式世界模型输出能力。

下一步如果要修机制，优先考虑：在 Stage-2 中加入 multi-field auxiliary targets，或把 action-selection output 改成先输出 stage/intent/next_state rationale 再输出 chosen；另一个方向是在 Stage-2 训练中显式保持 Stage-1 任务比例和 target-domain state/effect replay，而不是只让 target rows 做 action-only。
