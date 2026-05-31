# Sample 01

## 视频画面 (3 帧)

时间顺序：t=0 / t=midpoint / t=end。

![Frame 1](frames/sample_01_frame_01.jpg)
[Frame 1: frames/sample_01_frame_01.jpg]

![Frame 2](frames/sample_01_frame_02.jpg)
[Frame 2: frames/sample_01_frame_02.jpg]

![Frame 3](frames/sample_01_frame_03.jpg)
[Frame 3: frames/sample_01_frame_03.jpg]

## 顾客状态

- **AIDA 阶段**: interest
- **意图**: explore_options
- **信念 (belief)**: 售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。
- **愿望 (desire)**: 想进一步了解商品是否值得购买，并确认它是否符合自己的需求。
- **意图行为 (intention)**: 继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。
- **可观察证据 (observable evidence)**: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。

## 候选介入动作

| ID | 动作类型 | 说话内容 | 屏幕显示 | 物理动作 |
|---|---|---|---|---|
| Elicit_b1166d372e5e | Elicit | 您今天想先看价格、功能，还是适合什么场景？ | {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None} | 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。 |
| Inform_24926eed1e21 | Inform | 您好，需要时我可以帮您说明。 | {'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |
| Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e | Recommend | 如果您想省心选择，可以优先看这款更稳妥的。 | {'action': 'highlight_soft_recommendation', 'cta': None} | 智能售货柜轻量高亮一个选项，并保留顾客选择空间。 |
| Hold_eda24b4bb712 | Hold | （静默） | {'action': 'idle_minimal', 'cta': None} | 智能售货柜按屏幕、语音、灯效执行该候选响应。 |

## 你的选择

请从候选中选一个动作类型，并写到 `annotation_template.csv` 对应行的 `chosen_action` 列。
可选值只能是：`Greet` / `Elicit` / `Inform` / `Recommend` / `Hold`。
