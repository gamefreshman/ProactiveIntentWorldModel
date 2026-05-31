# Sample 10

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_10_frame_01.jpg)
[Frame 1: frames/sample_10_frame_01.jpg]

![Frame 2](frames/sample_10_frame_02.jpg)
[Frame 2: frames/sample_10_frame_02.jpg]

![Frame 3](frames/sample_10_frame_03.jpg)
[Frame 3: frames/sample_10_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: desire
- **意图**: compare_value_for_money
- **信念 (belief)**: 他已经判断自己想要的那款饮料就在面前的固定位置，且符合当前解渴和提神的需求。
- **愿望 (desire)**: 他想尽快确认选择并买下那款饮料，减少下班路上的停留时间。
- **意图行为 (intention)**: 他接下来倾向于直接伸手操作或确认购买，几乎不再继续比较其他选项。
- **可观察证据 (observable evidence)**: 他的目光持续锁定在画面下方偏中央的固定位置，双手保持在胸前到腰部范围内，手指轻微收拢又放松，只有短暂的小幅确认动作。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Inform_053014d173cc | Inform | 我先把价格和优惠信息放在屏幕上，方便您判断。 | {'action': 'show_price_or_discount', 'target': '{selected_item}', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Recommend_desire_stage_conditioned_target_piwm_712_7772394da4d5 | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
