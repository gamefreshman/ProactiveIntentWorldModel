# Sample 04

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_04_frame_01.jpg)
[Frame 1: frames/sample_04_frame_01.jpg]

![Frame 2](frames/sample_04_frame_02.jpg)
[Frame 2: frames/sample_04_frame_02.jpg]

![Frame 3](frames/sample_04_frame_03.jpg)
[Frame 3: frames/sample_04_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: attention
- **意图**: no_clear_intent
- **信念 (belief)**: 他觉得前方设备的外观有点新奇，但还没有形成明确的购买判断。
- **愿望 (desire)**: 他只是想快速确认这是什么设备，满足一下路过时的好奇心。
- **意图行为 (intention)**: 他倾向于边走边看一眼，然后继续前往原本的目的地。
- **可观察证据 (observable evidence)**: 他从画面前方缓步经过，视线短暂抬向镜头附近，快速上下打量，手机握在一只手里，另一只手自然抓着书包肩带，没有停下操作。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Greet_attention_stage_conditioned_target_piwm_703_b337b63da88c | Greet | 欢迎光临，需要时我可以帮您。 | {'action': 'show_welcome_message', 'cta': None} | 智能售货柜以简短欢迎语和柔和灯效提示可用性。 |
| Elicit_b1166d372e5e | Elicit | 您今天想先看价格、功能，还是适合什么场景？ | {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Inform_5ff00ba15ca5 | Inform | 我给您演示一下这款的关键细节。 | {'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
