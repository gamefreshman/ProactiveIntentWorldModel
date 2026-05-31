# Sample 28

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_28_frame_01.jpg)
[Frame 1: frames/sample_28_frame_01.jpg]

![Frame 2](frames/sample_28_frame_02.jpg)
[Frame 2: frames/sample_28_frame_02.jpg]

![Frame 3](frames/sample_28_frame_03.jpg)
[Frame 3: frames/sample_28_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: interest
- **意图**: explore_options
- **信念 (belief)**: 她觉得自己可以继续慢慢看，暂时不需要额外说明。
- **愿望 (desire)**: 想在低打扰环境里继续自由浏览。
- **意图行为 (intention)**: 如果系统不继续追问，她会愿意多停留一会儿。
- **可观察证据 (observable evidence)**: 她持续看向前方，浏览节奏已经放慢，偶尔短暂停顿，但并不显得困惑。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Elicit_b1166d372e5e | Elicit | 您想先看价格、功能，还是使用场景？ | {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Inform_24926eed1e21 | Inform | 您好，需要时我可以帮您说明。 | {'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Recommend_interest_stage_conditioned_target_piwm_813_95885d8f66ad | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
