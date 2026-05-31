# Sample 05

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_05_frame_01.jpg)
[Frame 1: frames/sample_05_frame_01.jpg]

![Frame 2](frames/sample_05_frame_02.jpg)
[Frame 2: frames/sample_05_frame_02.jpg]

![Frame 3](frames/sample_05_frame_03.jpg)
[Frame 3: frames/sample_05_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: attention
- **意图**: no_clear_intent
- **信念 (belief)**: 她刚注意到前方设备似乎有值得查看的内容，但还不确定是否与自己当前需求相关。
- **愿望 (desire)**: 她想快速判断这里是否有适合下班路上购买的饮品或小食。
- **意图行为 (intention)**: 她倾向先停下来观察几秒，再决定是否进一步靠近或操作。
- **可观察证据 (observable evidence)**: 她从经过状态放慢并停住，视线被前方吸引，头部微微转向设备方向，手机握在胸前但没有操作，另一只手轻轻扶着包带。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Greet_attention_stage_conditioned_target_piwm_704_51a30acf5b8b | Greet | 欢迎光临，需要时我可以帮您。 | {'action': 'show_welcome_message', 'cta': None} | 智能售货柜以简短欢迎语和柔和灯效提示可用性。 |
| Elicit_b1166d372e5e | Elicit | 您今天想先看价格、功能，还是适合什么场景？ | {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Inform_5ff00ba15ca5 | Inform | 我给您演示一下这款的关键细节。 | {'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
