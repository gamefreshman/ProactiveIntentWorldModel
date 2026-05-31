5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# 4 维度评估 Sanity Check（只读）

## 结论先行
Dim 4 anchor 复现，且四个维度 parse rate 均高于 0.7；低分主要不是 parser 失败，而是模型输出的标签本身与 gold 不匹配。

## 证据 1：Dim 4 anchor 复现

| 项目 | 数值 | 判定 |
| --- | ---: | --- |
| 4 维度 pipeline 重算 Dim 4 parsed macro F1 | 0.640989 | 通过 |
| 与主结果 0.641 的差值 | -0.000011 | 允许范围 ±0.005 |
| strict macro F1 | 0.622857 | 参考 |
| parse rate | 28/30 = 0.933 | 参考 |

结论：Dim 4 在 4 维度 pipeline 内可复现 `0.641 ± 0.005`，所以 action-selection anchor 本身对齐。

## 证据 2：每个维度 parse rate

| 维度 | 单位 | parse 成功 | parse rate | 是否低于 0.7 |
| --- | --- | ---: | ---: | --- |
| Dim 1 AIDA stage | target scene | 30/30 | 1.000 | 否 |
| Dim 2 intent_label | target scene | 30/30 | 1.000 | 否 |
| Dim 3 next_state | candidate action | 80/80 | 1.000 | 否 |
| Dim 4 best_act | target scene | 28/30 | 0.933 | 否 |

说明：Dim 3 的评估单位是 candidate action，不是 scene；本轮使用 80 条有 gold 的 covered candidates。

## 证据 3：每维度 5 条 raw output 抽样

### Dim 1：AIDA stage

#### target_piwm_700
- gold: `interest`
- parser prediction: `action`
- match: `False`
- raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>
<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>
<belief>The product is nearly ready, but confirmation is still needed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### target_piwm_701
- gold: `interest`
- parser prediction: `interest`
- match: `True`
- raw output:
```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是智能售货机前，可见判断应围绕手机查询内容与功能覆盖、操作步骤和无接触体验的结合。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对功能覆盖、操作步骤或无接触体验，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和支付流程、优惠信息和功能差异之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>
<belief>External prices, reviews, or specifications may change the choice.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### target_piwm_702
- gold: `interest`
- parser prediction: `action`
- match: `False`
- raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是自助贩货机前，可见判断应围绕顾客是否需要围绕支付、权限和心理感知获得人工确认。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### target_piwm_703
- gold: `attention`
- parser prediction: `attention`
- match: `True`
- raw output:
```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是智能售货机前，可见判断应围绕是否形成对智能商品的稳定兴趣，而不是深度比较。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>
<belief>The category is only mildly interesting, and interruption may feel premature.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```

#### target_piwm_704
- gold: `attention`
- parser prediction: `action`
- match: `False`
- raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是智能售货机前，可见判断应围绕顾客是否需要围绕支付、权限和后悔中获得明确 reassurance。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### Dim 2：intent_label

#### target_piwm_700
- gold: `explore_options`
- parser prediction: `confirm_choice`
- match: `False`
- raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>
<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>
<belief>The product is nearly ready, but confirmation is still needed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### target_piwm_701
- gold: `explore_options`
- parser prediction: `confirm_choice`
- match: `False`
- raw output:
```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是智能售货机前，可见判断应围绕手机查询内容与功能覆盖、操作步骤和无接触体验的结合。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对功能覆盖、操作步骤或无接触体验，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和支付流程、优惠信息和功能差异之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>
<belief>External prices, reviews, or specifications may change the choice.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### target_piwm_702
- gold: `compare_value_for_money`
- parser prediction: `confirm_choice`
- match: `False`
- raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是自助贩货机前，可见判断应围绕顾客是否需要围绕支付、权限和心理感知获得人工确认。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### target_piwm_703
- gold: `no_clear_intent`
- parser prediction: `explore_options`
- match: `False`
- raw output:
```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是智能售货机前，可见判断应围绕是否形成对智能商品的稳定兴趣，而不是深度比较。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>
<belief>The category is only mildly interesting, and interruption may feel premature.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```

#### target_piwm_704
- gold: `no_clear_intent`
- parser prediction: `confirm_choice`
- match: `False`
- raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是智能售货机前，可见判断应围绕顾客是否需要围绕支付、权限和后悔中获得明确 reassurance。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### Dim 3：next_state

#### target_piwm_700#Elicit_b1166d372e5e
- gold next_stage: `interest`
- parser prediction next_stage: `desire`
- gold reward: `0.21`
- parser prediction reward: `0.83`
- match: `False`
- raw output:
```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.83</reward>
```

#### target_piwm_700#Inform_24926eed1e21
- gold next_stage: `interest`
- parser prediction next_stage: `desire`
- gold reward: `0.04`
- parser prediction reward: `0.4`
- match: `False`
- raw output:
```text
<next_stage>desire</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>low</risk>
<benefit>low</benefit>
<reward>0.40</reward>
```

#### target_piwm_700#Hold_eda24b4bb712
- gold next_stage: `interest`
- parser prediction next_stage: `attention`
- gold reward: `0.00`
- parser prediction reward: `-0.2`
- match: `False`
- raw output:
```text
<next_stage>attention</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>medium</risk>
<benefit>low</benefit>
<reward>-0.20</reward>
```

#### target_piwm_701#Elicit_b1166d372e5e
- gold next_stage: `interest`
- parser prediction next_stage: `desire`
- gold reward: `0.11`
- parser prediction reward: `0.83`
- match: `False`
- raw output:
```text
<next_stage>desire</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.83</reward>
```

#### target_piwm_701#Inform_053014d173cc
- gold next_stage: `interest`
- parser prediction next_stage: `desire`
- gold reward: `0.07`
- parser prediction reward: `0.3`
- match: `False`
- raw output:
```text
<next_stage>desire</next_stage>
<next_belief>The current interaction is not useful enough to continue.</next_belief>
<next_desire>avoid further engagement</next_desire>
<next_intention>leave without buying</next_intention>
<risk>low</risk>
<benefit>low</benefit>
<reward>0.30</reward>
```

### Dim 4：best_act

#### target_piwm_700
- gold: `Elicit`
- parser prediction: `Elicit`
- match: `True`
- raw output:
```text
<rationale>开放式引导能有效降低犹豫，直接回应顾客关注点，显著提升信任感和兴趣。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

#### target_piwm_701
- gold: `Elicit`
- parser prediction: `Elicit`
- match: `True`
- raw output:
```text
<rationale>开放式引导帮助她明确需求，降低决策成本，提升信任感。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

#### target_piwm_702
- gold: `Inform`
- parser prediction: `Inform`
- match: `True`
- raw output:
```text
<rationale>对比卡降低了选择成本，提升信任感，让顾客主动进入决策，从兴趣转向明确欲望。</rationale>
<chosen>Inform_5ac252a82695</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>我把这几款的差别列在屏幕上，您可以先比较价格、功能和适合场景。</intervention_utterance>
```

#### target_piwm_703
- gold: `Elicit`
- parser prediction: `Elicit`
- match: `True`
- raw output:
```text
<rationale>开放式引导帮助顾客主动进入兴趣区域，降低决策成本。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

#### target_piwm_704
- gold: `Elicit`
- parser prediction: `Elicit`
- match: `True`
- raw output:
```text
<rationale>开放式引导帮助她明确需求，降低犹豫，提升信任感。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

## 证据 4：Stage-1 vs PIWM 在 Dim 1 上并列对比

以下 5 条使用同一份 target test。Stage-1 指“只做顾客状态与动作后果训练”的 checkpoint；PIWM 指后续动作选择训练后的主模型。

### target_piwm_700
- gold stage: `interest`
- Stage-1 parsed stage: `action`, match=`False`
- PIWM parsed stage: `action`, match=`False`
- Stage-1 raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是智能售货机前，可见判断应围绕顾客是否需要围绕支付、权限或核对信息获得人工确认。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```
- PIWM raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>
<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>
<belief>The product is nearly ready, but confirmation is still needed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### target_piwm_701
- gold stage: `interest`
- Stage-1 parsed stage: `interest`, match=`True`
- PIWM parsed stage: `interest`, match=`True`
- Stage-1 raw output:
```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是智能售货机前，可见判断应围绕手机查询内容与附近商品的结合度，围绕容量、材质、颜色和到手价产生主动获取、比较或确认需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客没有离开，而是把注意力放在手机和商品之间。 移动较少，处在查询状态。 停留本身更像在核对容量、材质、颜色和到手价，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和尺寸、重量、容量、材质、颜色和到手价之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明还没有形成离开意图。 至少一只手持手机或在查询动作中。</body_and_hands>
<belief>The product is promising, but price or alternative options must be confirmed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```
- PIWM raw output:
```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是智能售货机前，可见判断应围绕手机查询内容与功能覆盖、操作步骤和无接触体验的结合。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对功能覆盖、操作步骤或无接触体验，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和支付流程、优惠信息和功能差异之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>
<belief>External prices, reviews, or specifications may change the choice.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### target_piwm_702
- gold stage: `interest`
- Stage-1 parsed stage: `action`, match=`False`
- PIWM parsed stage: `action`, match=`False`
- Stage-1 raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是智能售货机前，可见判断应围绕顾客是否需要围绕支付、权限或核对尺寸/容量获得人工确认。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```
- PIWM raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是自助贩货机前，可见判断应围绕顾客是否需要围绕支付、权限和心理感知获得人工确认。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### target_piwm_703
- gold stage: `attention`
- Stage-1 parsed stage: `attention`, match=`True`
- PIWM parsed stage: `attention`, match=`True`
- Stage-1 raw output:
```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是智能售货机前，可见判断应围绕是否形成围绕核心功能、评价维度或价格差异的稳定兴趣，而不仅是停留本身。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。</body_and_hands>
<belief>The product may be interesting, but confirmation is not yet strong enough.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```
- PIWM raw output:
```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是智能售货机前，可见判断应围绕是否形成对智能商品的稳定兴趣，而不是深度比较。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>
<belief>The category is only mildly interesting, and interruption may feel premature.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```

### target_piwm_704
- gold stage: `attention`
- Stage-1 parsed stage: `attention`, match=`True`
- PIWM parsed stage: `action`, match=`False`
- Stage-1 raw output:
```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是智能售货机前，可见兴趣应围绕功能和使用场景，可能在价格、评价或第三方使用体验上形成犹豫。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>
<belief>The category is only mildly interesting, and interruption may feel premature.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```
- PIWM raw output:
```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是智能售货机前，可见判断应围绕顾客是否需要围绕支付、权限和后悔中获得明确 reassurance。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

## 诊断判断

- Dim 4 anchor 复现，说明 4 维度 pipeline 的 action-selection 评分口径没有明显脱离主结果。
- Dim 1/2/3 parse rate 分别为 1.000 / 1.000 / 1.000，低分不是 parser 抓不到字段导致。
- Dim 4 parse rate 为 0.933，也高于 0.7。
- Dim 1/2 的 raw output 显示 PIWM 主模型经常输出合法但错误的 `action / confirm_choice` 组合；这更像训练后的表征偏移或目标域动作选择训练带来的模式偏置，而不是正则解析失败。
- Stage-1 和 PIWM 在抽样中都存在把早期浏览样本判成 `action / confirm_choice` 的情况；PIWM 没有明显格式崩坏，但没有保住 Stage-1 在 AIDA 上的更高分。

结论：Confirmed: PIWM 在 Dim 1/2/3 上真实退化，framing 需要降级
