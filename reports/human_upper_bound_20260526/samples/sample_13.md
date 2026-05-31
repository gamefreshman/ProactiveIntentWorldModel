# Sample 13

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_13_frame_01.jpg)
[Frame 1: frames/sample_13_frame_01.jpg]

![Frame 2](frames/sample_13_frame_02.jpg)
[Frame 2: frames/sample_13_frame_02.jpg]

![Frame 3](frames/sample_13_frame_03.jpg)
[Frame 3: frames/sample_13_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: action
- **意图**: confirm_choice
- **信念 (belief)**: 他认为自己已经选好了合适的饮料，购买步骤很简单且不需要再比较。
- **愿望 (desire)**: 他想快速完成购买，在下一节课前拿到饮料。
- **意图行为 (intention)**: 他准备立即伸手操作并确认购买。
- **可观察证据 (observable evidence)**: 他始终正面看向前方，视线稳定，动作直接，右手从胸前自然抬起并向画面下方前伸，左手轻扶背包肩带，全程没有停顿、回看或反复比较的动作。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Greet_889a5021015d | Greet | 感谢惠顾，祝您使用愉快。 | {'action': 'show_thank_you', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Recommend_action_stage_conditioned_target_piwm_718_db61c6f3be0c | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
