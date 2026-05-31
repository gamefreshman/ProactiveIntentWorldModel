# Sample 02

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_02_frame_01.jpg)
[Frame 1: frames/sample_02_frame_01.jpg]

![Frame 2](frames/sample_02_frame_02.jpg)
[Frame 2: frames/sample_02_frame_02.jpg]

![Frame 3](frames/sample_02_frame_03.jpg)
[Frame 3: frames/sample_02_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: interest
- **意图**: explore_options
- **信念 (belief)**: 她认为眼前的饮品选择可能适合下班后解渴或提神，但还需要简单比较一下。
- **愿望 (desire)**: 她想快速找到一款口味合适、喝起来轻松的饮品。
- **意图行为 (intention)**: 她倾向继续平稳扫视并做一个简单判断，若看到合适选项就准备购买。
- **可观察证据 (observable evidence)**: 她站在设备前方，目光平稳地从左到右扫视，偶尔短暂停留，手指轻轻握着手机，动作自然放松，没有明显反复犹豫。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Elicit_b1166d372e5e | Elicit | 您今天想先看价格、功能，还是适合什么场景？ | {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Inform_053014d173cc | Inform | 您好，需要时我可以帮您说明。 | {'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Recommend_interest_stage_conditioned_target_piwm_701_72bc6d16c156 | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
