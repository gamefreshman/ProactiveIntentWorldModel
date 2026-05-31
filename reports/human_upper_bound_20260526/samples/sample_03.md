# Sample 03

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_03_frame_01.jpg)
[Frame 1: frames/sample_03_frame_01.jpg]

![Frame 2](frames/sample_03_frame_02.jpg)
[Frame 2: frames/sample_03_frame_02.jpg]

![Frame 3](frames/sample_03_frame_03.jpg)
[Frame 3: frames/sample_03_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: interest
- **意图**: compare_value_for_money
- **信念 (belief)**: 他认为这里可能有适合下午提神的饮品，但还不确定哪一种更合适。
- **愿望 (desire)**: 他想快速选到一款不太甜、能让自己恢复精神的饮品。
- **意图行为 (intention)**: 他倾向于继续观察并在两个备选之间做比较后再决定是否购买。
- **可观察证据 (observable evidence)**: 他站在设备前停留，视线在不同位置之间来回移动，右手握着手机但不操作，左手偶尔抬起又放下，表现出比较和犹豫。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Elicit_b1166d372e5e | Elicit | 您想先看价格、功能，还是使用场景？ | {'action': 'show_choice_bubbles', 'choices': ['功能', '价格', '场景'], 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Inform_5ac252a82695 | Inform | 我把这几款的差别列在屏幕上，您可以先比较价格、功能和适合场景。 | {'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Recommend_interest_stage_conditioned_target_piwm_702_7b41761a1f49 | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
