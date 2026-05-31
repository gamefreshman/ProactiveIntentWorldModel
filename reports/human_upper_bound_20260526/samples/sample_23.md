# Sample 23

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_23_frame_01.jpg)
[Frame 1: frames/sample_23_frame_01.jpg]

![Frame 2](frames/sample_23_frame_02.jpg)
[Frame 2: frames/sample_23_frame_02.jpg]

![Frame 3](frames/sample_23_frame_03.jpg)
[Frame 3: frames/sample_23_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: action
- **意图**: confirm_choice
- **信念 (belief)**: 她认为扫码支付已经成功，购买流程基本完成，只需稍等片刻即可拿到商品。
- **愿望 (desire)**: 她想顺利完成取货，在下班途中快速获得一份方便的饮品或小食。
- **意图行为 (intention)**: 她倾向于原地轻松等待出货，并在流程结束时以点头微笑表示感谢后离开。
- **可观察证据 (observable evidence)**: 她正面站在镜头前，手机自然握在右手中，视线稳定看向前方，偶尔低头确认手机后又抬眼等待，动作放松且没有明显犹豫。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Greet_889a5021015d | Greet | 感谢惠顾，祝您使用愉快。 | {'action': 'show_thank_you', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Recommend_action_stage_conditioned_target_piwm_789_3b3823bf8ff3 | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
