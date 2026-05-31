# Sample 25

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_25_frame_01.jpg)
[Frame 1: frames/sample_25_frame_01.jpg]

![Frame 2](frames/sample_25_frame_02.jpg)
[Frame 2: frames/sample_25_frame_02.jpg]

![Frame 3](frames/sample_25_frame_03.jpg)
[Frame 3: frames/sample_25_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: interest
- **意图**: explore_options
- **信念 (belief)**: 她认为设备里可能有合适商品，正在按自己的节奏了解。
- **愿望 (desire)**: 想先自主看看不同信息，再决定是否深入比较。
- **意图行为 (intention)**: 继续安静浏览，不希望当前节奏被打断。
- **可观察证据 (observable evidence)**: 她的视线在前方几个区域之间稳定切换，节奏从容，没有明显困惑或求助信号。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Elicit_b1166d372e5e | Elicit | 您想先看价格、功能，还是使用场景？ | {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Inform_5ff00ba15ca5 | Inform | 我给您演示一下这款的关键细节。 | {'action': 'play_product_demo', 'target': '{candidate_item}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Recommend_interest_stage_conditioned_target_piwm_810_5d8cdcc48ed2 | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
