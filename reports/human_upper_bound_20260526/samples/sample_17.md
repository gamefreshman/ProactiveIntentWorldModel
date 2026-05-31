# Sample 17

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_17_frame_01.jpg)
[Frame 1: frames/sample_17_frame_01.jpg]

![Frame 2](frames/sample_17_frame_02.jpg)
[Frame 2: frames/sample_17_frame_02.jpg]

![Frame 3](frames/sample_17_frame_03.jpg)
[Frame 3: frames/sample_17_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: desire
- **意图**: explore_options
- **信念 (belief)**: 她认为眼前这款商品很符合自己下班后的即时需求，品质和口味都可能让她满意。
- **愿望 (desire)**: 她想买下这款自己明显喜欢的商品，作为下班路上的轻松奖励。
- **意图行为 (intention)**: 她倾向于购买，但还需要一个温和的推荐或确认来打消“要不要现在买”的最后犹豫。
- **可观察证据 (observable evidence)**: 她的视线长时间停留在前方同一位置，偶尔短暂移开又回到原处，手指轻轻摩挲手机边缘，表现出想买但仍在确认的状态。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Inform_desire_stage_conditioned_target_piwm_760_e7247f5d4264 | Inform | 这几款主要区别在口味、容量和价格，我可以帮您快速对比。 | {'action': 'show_comparison_or_details', 'cta': None} | 智能售货柜展示简短对比信息，避免长篇推销。 |
| Recommend_8d7f8993e333 | Recommend | 如果您想省时间，可以先从这款开始看，它比较符合您现在关注的点。 | {'action': 'highlight_recommended_item', 'target': '{recommended_item}', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
