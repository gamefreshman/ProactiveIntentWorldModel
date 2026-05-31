# Sample 18

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_18_frame_01.jpg)
[Frame 1: frames/sample_18_frame_01.jpg]

![Frame 2](frames/sample_18_frame_02.jpg)
[Frame 2: frames/sample_18_frame_02.jpg]

![Frame 3](frames/sample_18_frame_03.jpg)
[Frame 3: frames/sample_18_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: desire
- **意图**: explore_options
- **信念 (belief)**: 她觉得眼前的选择里应该有适合午休后饮用的商品，但不确定哪一个更符合自己的口味和身体需求。
- **愿望 (desire)**: 她想买一份清爽又稳妥的饮品，同时希望得到一个温和的推荐来增强选择信心。
- **意图行为 (intention)**: 她倾向于在得到明确但不强硬的推荐后，选择其中一个并继续购买。
- **可观察证据 (observable evidence)**: 她站在原地反复看向前方偏下的位置，视线在不同选项间缓慢移动，手指轻轻摩挲包带，偶尔微微抬手又放下，表现出中等程度的犹豫。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Inform_053014d173cc | Inform | 您好，需要时我可以帮您说明。 | {'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Recommend_8d7f8993e333 | Recommend | 如果您想省时间，可以先从这款开始看，它比较符合您现在关注的点。 | {'action': 'highlight_recommended_item', 'target': '{recommended_item}', 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
