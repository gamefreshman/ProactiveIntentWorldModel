# Sample 19

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_19_frame_01.jpg)
[Frame 1: frames/sample_19_frame_01.jpg]

![Frame 2](frames/sample_19_frame_02.jpg)
[Frame 2: frames/sample_19_frame_02.jpg]

![Frame 3](frames/sample_19_frame_03.jpg)
[Frame 3: frames/sample_19_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: desire
- **意图**: explore_options
- **信念 (belief)**: 她已经充分了解并认可这款商品，认为它符合自己下班后补充能量的需求。
- **愿望 (desire)**: 她希望得到一个明确而坚定的推荐，让自己无需再比较就可以放心购买。
- **意图行为 (intention)**: 如果接收到强推荐信号，她会立刻完成最后的确认动作。
- **可观察证据 (observable evidence)**: 她的视线稳定停留在正前方同一位置，几乎不再左右比较，右手拇指轻轻摩擦手机边缘，随后手指逐渐收紧，表现出即将确认的状态。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Inform_desire_stage_conditioned_target_piwm_763_98475049c32b | Inform | 这几款主要区别在口味、容量和价格，我可以帮您快速对比。 | {'action': 'show_comparison_or_details', 'cta': None} | 智能售货柜展示简短对比信息，避免长篇推销。 |
| Recommend_9ff23b139b07 | Recommend | 这款最适合您，建议直接选这款。 | {'action': 'highlight_single_item_with_cta', 'target': '{recommended_item}', 'cta': 'buy_now'} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
