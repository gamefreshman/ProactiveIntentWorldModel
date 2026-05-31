# Sample 22

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_22_frame_01.jpg)
[Frame 1: frames/sample_22_frame_01.jpg]

![Frame 2](frames/sample_22_frame_02.jpg)
[Frame 2: frames/sample_22_frame_02.jpg]

![Frame 3](frames/sample_22_frame_03.jpg)
[Frame 3: frames/sample_22_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: desire
- **意图**: explore_options
- **信念 (belief)**: 他认为目标商品价格可以接受，信息基本符合自己的需求，只差一个推荐结果来最终确认。
- **愿望 (desire)**: 他想快速买到一款适合下班后解渴提神的饮品，避免继续浪费时间比较。
- **意图行为 (intention)**: 他倾向于接受一个明确的推荐确认，并尽快做出购买决定。
- **可观察证据 (observable evidence)**: 他正面站在镜头前，视线稳定地在镜头下方区域短暂扫动，像是在核对价格和关键信息，随后轻轻点头，双手始终在胸腹前可见，手机握在一只手里但没有大幅操作。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Inform_053014d173cc | Inform | 您好，需要时我可以帮您说明。 | {'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Recommend_8d7f8993e333 | Recommend | 如果您想省时间，可以先从这款开始看，它比较符合您现在关注的点。 | {'action': 'highlight_recommended_item', 'target': '{recommended_item}', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
