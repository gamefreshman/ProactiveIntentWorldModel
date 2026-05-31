本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

# intent_label 标签空间审计

## 结论先行

- train+eval 中实际出现 `7` 个 intent_label，不是 14 个。
- 最需要 PI 审的类别是 `seek_reassurance`、`confirm_choice`、`request_demonstration`、`compare_value_for_money`、`negotiate_price`，因为它们常需要对话上下文或细粒度动机才能区分。
- F1=0 的类别包括 `compare_value_for_money`、`leave_without_purchase`、`negotiate_price`、`seek_reassurance`；其中 `seek_reassurance` 并非小样本，说明标签边界本身有问题。
- 本报告只做 taxonomy audit，不合并、不降权、不改数据，等待 PI 决策。

## 0. 范围澄清：intent_label 不是 5-act action

本报告审的是 `intent_label`，也就是“顾客现在想做什么”的状态标签；它不是 agent 的 5-act 动作空间。

- 当前锁定的 5-act action 是 `Greet / Elicit / Inform / Recommend / Hold`。
- `Reassure` action 已排除在当前 operational 5-act 训练/评测路径之外。
- `seek_reassurance` 仍然是一个合法的 customer intent_label，表示顾客可能在寻求安心、确认或降低不确定性。

因此，不能因为 `Reassure` action 被排除，就删除或等同排除 `seek_reassurance` intent。二者属于不同层：前者是系统动作，后者是顾客意图。

## 0.1 标签边界初判表

| intent_label | 可见证据通常是什么 | 可能需要的上下文 | 易混标签 | 初判 |
|---|---|---|---|---|
| `confirm_choice` | 接近柜台、寻找导购、停留在候选商品前、动作趋于结束 | 是否已经有明确偏好、是否正在准备成交 | `seek_reassurance`, `request_demonstration` | 裸视觉可部分识别，但和“需要安心/演示”边界薄 |
| `seek_reassurance` | 反复看商品、价签、导购或评价信息，犹豫但未离开 | 顾客担心的点是什么；是否只是要确认而非已决定 | `confirm_choice`, `request_demonstration`, `compare_value_for_money` | 视觉不可稳定区分，强依赖对话/历史 |
| `request_demonstration` | 触摸、试用、靠近商品功能区，看向商品反馈 | 顾客是否明确要“演示”，还是只是自主体验 | `explore_options`, `confirm_choice`, `seek_reassurance` | 有手部试用证据时较清楚，否则易混 |
| `explore_options` | 浏览多个商品、视线切换、尚未固定一个目标 | 是否在泛浏览，还是围绕性价比比较 | `request_demonstration`, `compare_value_for_money` | 需要比较对象/移动轨迹支持 |
| `compare_value_for_money` | 看价签、规格、评价、同类商品，停留比较 | 是否真的在比较“性价比”，还是普通犹豫/安心需求 | `negotiate_price`, `seek_reassurance`, `explore_options` | 单靠图像较难，最好有价格/规格上下文 |
| `negotiate_price` | 看价格、靠近导购或柜台，可能准备询价 | 是否有讨价还价语言或促销语境 | `compare_value_for_money`, `confirm_choice` | 基本需要对话上下文；裸视觉证据不足 |
| `leave_without_purchase` | 转身离开、远离货架、注意力脱离商品 | 是否是暂时换区还是真正离开购买流程 | `explore_options`, `attention` 类状态 | 需要更长时序判断，三帧容易误判 |

### 重点错误模式

- `seek_reassurance` 在 eval 中 9 条全错：6 条被预测成 `request_demonstration`，2 条被预测成 `confirm_choice`，1 条被预测成 `explore_options`。这说明它不是单纯小样本问题，而是边界和输入证据不足。
- `negotiate_price` 在 eval 中 5 条全错：4 条被预测成 `request_demonstration`，1 条被预测成 `confirm_choice`。这说明“议价”更像需要对话或价格互动证据的标签。
- `request_demonstration` 与 `confirm_choice` 互相错分明显：前者 5 条被预测成 `confirm_choice`，后者 8 条被预测成 `request_demonstration`。

## A. 类别样本抽样

### A(a) 所有类别 + train/eval 样本数

| intent_label | train_count | eval_count | eval_F1 | 重点关注 |
|---|---|---|---|---|
| `compare_value_for_money` | 15 | 1 | 0.000 | yes |
| `confirm_choice` | 163 | 14 | 0.414 |  |
| `explore_options` | 87 | 7 | 0.500 | yes |
| `leave_without_purchase` | 15 | 2 | 0.000 | yes |
| `negotiate_price` | 50 | 5 | 0.000 | yes |
| `request_demonstration` | 81 | 12 | 0.333 |  |
| `seek_reassurance` | 82 | 9 | 0.000 | yes |

### A(b) 每类 3 条 train 样本

### 类别 `compare_value_for_money`

- stage distribution: `interest`=8, `desire`=8
- top desires: `find better value for money`=16
- top intentions: `compare alternatives before deciding`=16

#### train sample 1: `piwm_a30772dee0`

- task_id: `piwm_a30772dee0`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_a30772dee0/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_a30772dee0/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_a30772dee0/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "compare_value_for_money",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是手机陈列区，可见判断应围绕配置差异、使用年限、售后和实际到手价是否足以支撑价格。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对配置差异、使用年限、售后和实际到手价，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和拍照、续航、存储容量、屏幕尺寸和以旧换新价格之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "find better value for money",
  "intention": "compare alternatives before deciding"
}
```

#### train sample 2: `piwm_d666c709a1`

- task_id: `piwm_d666c709a1`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_d666c709a1/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_d666c709a1/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_d666c709a1/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "compare_value_for_money",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是护肤品陈列区，可见判断应围绕成分、容量、使用周期和肤质匹配度是否足以支撑价格。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对成分、容量、使用周期和肤质匹配度，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和肤质适配、主打成分、质地、容量和单次使用成本之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "find better value for money",
  "intention": "compare alternatives before deciding"
}
```

#### train sample 3: `piwm_7568b7e84e`

- task_id: `piwm_7568b7e84e`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_7568b7e84e/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_7568b7e84e/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_7568b7e84e/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "compare_value_for_money",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是服装陈列区，可见判断应围绕面料、剪裁、适用场合和搭配频率是否足以支撑价格。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对面料、剪裁、适用场合和搭配频率，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和版型、面料、颜色、尺码、护理方式和价格差异之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "find better value for money",
  "intention": "compare alternatives before deciding"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_4d433ad0b0`

- task_id: `piwm_4d433ad0b0`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_4d433ad0b0/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_4d433ad0b0/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_4d433ad0b0/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "compare_value_for_money",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是珠宝柜台，可见判断应围绕材质、证书、佩戴场景和送礼适配度是否足以支撑价格。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对材质、证书、佩戴场景和送礼适配度，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和材质、大小、光泽、佩戴效果、证书和价格差异之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "find better value for money",
  "intention": "compare alternatives before deciding"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是珠宝柜台，可见判断应围绕材质、光泽、佩戴效果和送礼场景是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对材质、光泽、佩戴效果和送礼场景，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和材质、大小、光泽、佩戴效果和送礼场景之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### 类别 `confirm_choice`

- stage distribution: `interest`=81, `action`=55, `desire`=34, `attention`=7
- top desires: `confirm the preferred choice`=177
- top intentions: `move toward confirming the choice`=177

#### train sample 1: `piwm_47d0c9e2dc`

- task_id: `piwm_47d0c9e2dc`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_47d0c9e2dc/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_47d0c9e2dc/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_47d0c9e2dc/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "action",
  "intent_label": "confirm_choice",
  "visual_summary": "顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是腕表柜台，可见判断应围绕顾客是否需要围绕表盘大小、表带材质、上手比例和佩戴场合获得人工确认。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。",
  "gaze_and_attention": "视线从商品转向周围空间或导购可能出现的位置。",
  "body_and_hands": "身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。",
  "belief": "A suitable option may be close, but staff input is needed before deciding.",
  "desire": "confirm the preferred choice",
  "intention": "move toward confirming the choice"
}
```

#### train sample 2: `piwm_605c4af4fa`

- task_id: `piwm_605c4af4fa`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_605c4af4fa/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_605c4af4fa/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_605c4af4fa/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "confirm_choice",
  "visual_summary": "顾客在两个商品之间来回比较，说明已经进入备选项评估。 当前场景是珠宝柜台，可见判断应围绕两个候选项在材质、大小、光泽、佩戴效果、证书和价格差异上的差异。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客注意力在两个具体选项之间切换。 移动围绕两个商品点位展开，不是离开式移动。 比较行为集中在材质、大小、光泽、佩戴效果、证书和价格差异，说明选择尚未收敛。",
  "gaze_and_attention": "视线在两个商品或对应价签之间来回移动。 视线切换应被解释为对材质、大小、光泽、佩戴效果、证书和价格差异的对照。",
  "body_and_hands": "身体朝向两个备选商品之间的区域。 手部可能指向、拿起或靠近两个备选商品。 手部或身体在两个选项之间移动，说明还没有锁定单一商品。",
  "belief": "Two options remain close, and the decisive difference is not yet clear.",
  "desire": "confirm the preferred choice",
  "intention": "move toward confirming the choice"
}
```

#### train sample 3: `piwm_663b1853b2`

- task_id: `piwm_663b1853b2`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_663b1853b2/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_663b1853b2/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_663b1853b2/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "confirm_choice",
  "visual_summary": "顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是电脑陈列区，可见判断应围绕手机查询内容与配置、便携性、保修和未来几年使用成本之间的关系。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对配置、便携性、保修和未来几年使用成本，而不是已经准备成交。",
  "gaze_and_attention": "视线在手机和商品区域之间切换。 注意力可能在价格、评价和处理器/内存配置、屏幕尺寸、重量、续航和售后之间切换。",
  "body_and_hands": "身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。",
  "belief": "External prices, reviews, or specifications may change the choice.",
  "desire": "confirm the preferred choice",
  "intention": "move toward confirming the choice"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_1cc2c20d89`

- task_id: `piwm_1cc2c20d89`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_1cc2c20d89/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_1cc2c20d89/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_1cc2c20d89/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "action",
  "intent_label": "confirm_choice",
  "visual_summary": "顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。",
  "gaze_and_attention": "视线从商品转向周围空间或导购可能出现的位置。",
  "body_and_hands": "身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。",
  "belief": "A suitable option may be close, but staff input is needed before deciding.",
  "desire": "confirm the preferred choice",
  "intention": "move toward confirming the choice"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是护肤品陈列区，可见判断应围绕成分、容量、质地和适合肤质是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对成分、容量、质地和适合肤质，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和肤质适配之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 2: `piwm_5883d29028`

- task_id: `piwm_5883d29028`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_5883d29028/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_5883d29028/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_5883d29028/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "attention",
  "intent_label": "confirm_choice",
  "visual_summary": "顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、光泽、尺寸和送礼场景获得人工确认。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。",
  "gaze_and_attention": "视线朝向柜台、导购或服务点。",
  "body_and_hands": "身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。",
  "belief": "The shopper may be ready for service, but still needs final confirmation.",
  "desire": "confirm the preferred choice",
  "intention": "move toward confirming the choice"
}
```
Prediction:

```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、证书和售后中需要确认尺码、光泽、光泽、证书和售后。视角从斜角监控变为直接观察柜台区域。</visual_summary>
<engagement_pattern>顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。</engagement_pattern>
<gaze_and_attention>视线朝向柜台、导购或服务点。</gaze_and_attention>
<body_and_hands>身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。</body_and_hands>
<belief>The shopper may be ready for service, but still needs confirmation.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### eval sample 3: `piwm_8916c58066`

- task_id: `piwm_8916c58066`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_8916c58066/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_8916c58066/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_8916c58066/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "confirm_choice",
  "visual_summary": "顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是珠宝柜台，可见判断应围绕顾客是否需要围绕佩戴效果、材质、光泽、尺寸和送礼场景获得人工确认。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。",
  "gaze_and_attention": "视线朝向柜台、导购或服务点。",
  "body_and_hands": "身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。",
  "belief": "The shopper may be ready for service, but still needs final confirmation.",
  "desire": "confirm the preferred choice",
  "intention": "move toward confirming the choice"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客向柜台或导购方向移动，说明接近明确咨询或决策。 当前场景是珠宝柜台，可见判断应围绕柜台互动和商品细节是否足以支撑停留意图。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客从浏览转向服务区域，说明当前互动开始影响判断。 移动方向明确，正在前往柜台或导购点。</engagement_pattern>
<gaze_and_attention>视线朝柜台、导购或服务区域移动。 视线变化更关键，重点是柜台方向的视线变化。</gaze_and_attention>
<body_and_hands>身体朝柜台方向前进。 手部可能携带商品、拿起商品或靠近柜台。</body_and_hands>
<belief>Situation may be promising, but confirmation is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### 类别 `explore_options`

- stage distribution: `attention`=42, `interest`=40, `desire`=12
- top desires: `explore available options`=94
- top intentions: `continue browsing and comparing`=94

#### train sample 1: `piwm_89f8a709a7`

- task_id: `piwm_89f8a709a7`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_89f8a709a7/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_89f8a709a7/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_89f8a709a7/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "explore_options",
  "visual_summary": "顾客反复接触或摆弄商品，说明正在主动评估商品细节。 当前场景是家电展示区，可见判断应围绕尺寸、核心功能、能耗、噪音和售后安装中需要手部确认的细节。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品有持续直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是关键功能、操作步骤、噪音或空间占用是否被确认。",
  "gaze_and_attention": "视线主要集中在商品细节和手部操作位置。 视线重点应落在关键功能、操作步骤、噪音或空间占用产生的可见反馈。",
  "body_and_hands": "身体保持靠近商品，姿态显示评估意愿。 手部反复拿起、放下、调整或触摸商品。 手部动作应重点看是否在确认关键功能、操作步骤、噪音或空间占用。",
  "belief": "The product details are promising, but tactile or functional confirmation is still needed.",
  "desire": "explore available options",
  "intention": "continue browsing and comparing"
}
```

#### train sample 2: `piwm_8f1c6eb583`

- task_id: `piwm_8f1c6eb583`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_8f1c6eb583/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_8f1c6eb583/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_8f1c6eb583/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "explore_options",
  "visual_summary": "顾客反复接触或摆弄商品，说明正在主动评估商品细节。 当前场景是电脑陈列区，可见判断应围绕屏幕尺寸、键盘手感、性能配置、重量和价格差异中需要手部确认的细节。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品有持续直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是屏幕显示、键盘触感、机身重量或接口布局是否被确认。",
  "gaze_and_attention": "视线主要集中在商品细节和手部操作位置。 视线重点应落在屏幕显示、键盘触感、机身重量或接口布局产生的可见反馈。",
  "body_and_hands": "身体保持靠近商品，姿态显示评估意愿。 手部反复拿起、放下、调整或触摸商品。 手部动作应重点看是否在确认屏幕显示、键盘触感、机身重量或接口布局。",
  "belief": "The product details are promising, but tactile or functional confirmation is still needed.",
  "desire": "explore available options",
  "intention": "continue browsing and comparing"
}
```

#### train sample 3: `piwm_9f15fb9aca`

- task_id: `piwm_9f15fb9aca`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_9f15fb9aca/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_9f15fb9aca/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_9f15fb9aca/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "attention",
  "intent_label": "explore_options",
  "visual_summary": "顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是家电展示区，可见判断应围绕是否形成对家电的稳定兴趣，而不是深度比较。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。",
  "gaze_and_attention": "视线短暂扫过商品区域，很快离开。",
  "body_and_hands": "身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。",
  "belief": "The category is only mildly interesting, and interruption may feel premature.",
  "desire": "explore available options",
  "intention": "continue browsing and comparing"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_5d80d9bd7d`

- task_id: `piwm_5d80d9bd7d`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_5d80d9bd7d/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_5d80d9bd7d/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_5d80d9bd7d/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "explore_options",
  "visual_summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是电脑陈列区，可见判断应围绕同伴反馈如何影响屏幕尺寸、键盘手感、性能配置、重量和价格差异。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
  "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
  "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。",
  "belief": "A companion's approval may influence whether the choice feels safe.",
  "desire": "explore available options",
  "intention": "continue browsing and comparing"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是电脑陈列区，可见判断应围绕同伴反馈如何影响屏幕尺寸、键盘手感、性能配置、重量和价格差异。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。</engagement_pattern>
<gaze_and_attention>视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。</gaze_and_attention>
<body_and_hands>身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。</body_and_hands>
<belief>A companion's approval may influence whether the choice feels safe.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 2: `piwm_fcff61e1e2`

- task_id: `piwm_fcff61e1e2`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_fcff61e1e2/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_fcff61e1e2/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_fcff61e1e2/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "explore_options",
  "visual_summary": "顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是家电展示区，可见判断应围绕手机查询内容与功能覆盖、能耗、安装条件和长期使用成本之间的关系。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。",
  "gaze_and_attention": "视线在手机和商品区域之间切换。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。",
  "body_and_hands": "身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。",
  "belief": "External prices, reviews, or specifications may change the choice.",
  "desire": "explore available options",
  "intention": "continue browsing and comparing"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是家电展示区，可见判断应围绕手机查询内容与功能覆盖、能耗、安装条件和长期使用成本之间的关系。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>
<belief>External prices, reviews, or specifications may change the choice.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 3: `piwm_3caa2e1ac2`

- task_id: `piwm_3caa2e1ac2`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_3caa2e1ac2/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_3caa2e1ac2/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_3caa2e1ac2/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "attention",
  "intent_label": "explore_options",
  "visual_summary": "顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是家电展示区，可见判断应围绕是否形成对家电的稳定兴趣，而不是深度比较。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。",
  "gaze_and_attention": "视线短暂扫过商品区域，很快离开。",
  "body_and_hands": "身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。",
  "belief": "The category is only mildly interesting, and interruption may feel premature.",
  "desire": "explore available options",
  "intention": "continue browsing and comparing"
}
```
Prediction:

```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是家电展示区，可见判断应围绕是否形成对家电的稳定兴趣，而不是深度比较。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>
<belief>The category is only mildly interesting, and interruption may feel premature.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```

### 类别 `leave_without_purchase`

- stage distribution: `action`=8, `desire`=7, `interest`=2
- top desires: `avoid further engagement`=17
- top intentions: `leave without buying`=17

#### train sample 1: `piwm_846584adac`

- task_id: `piwm_846584adac`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_846584adac/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_846584adac/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_846584adac/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "desire",
  "intent_label": "leave_without_purchase",
  "visual_summary": "顾客避免眼神接触或身体回避，说明当前不适合主动推进。 当前场景是家电展示区，可见判断应围绕回避互动和离开倾向，不能只按商品兴趣解释。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品或导购的互动关系较弱。 可能有离开或减少互动的趋势。 当前更明显的是回避互动，应优先降低打扰感，而不是推进商品介绍。",
  "gaze_and_attention": "视线回避导购或交流区域。",
  "body_and_hands": "身体可能偏离商品或导购方向。 手部不主动展示需求，可能收回或保持封闭。 身体和手部的封闭信号比商品兴趣更重要。",
  "belief": "Further engagement may feel intrusive at this moment.",
  "desire": "avoid further engagement",
  "intention": "leave without buying"
}
```

#### train sample 2: `piwm_a89307e016`

- task_id: `piwm_a89307e016`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_a89307e016/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_a89307e016/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_a89307e016/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "desire",
  "intent_label": "leave_without_purchase",
  "visual_summary": "顾客避免眼神接触或身体回避，说明当前不适合主动推进。 当前场景是珠宝柜台，可见判断应围绕回避互动和离开倾向，不能只按商品兴趣解释。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品或导购的互动关系较弱。 可能有离开或减少互动的趋势。 当前更明显的是回避互动，应优先降低打扰感，而不是推进商品介绍。",
  "gaze_and_attention": "视线回避导购或交流区域。",
  "body_and_hands": "身体可能偏离商品或导购方向。 手部不主动展示需求，可能收回或保持封闭。 身体和手部的封闭信号比商品兴趣更重要。",
  "belief": "Further engagement may feel intrusive at this moment.",
  "desire": "avoid further engagement",
  "intention": "leave without buying"
}
```

#### train sample 3: `piwm_0102032a3a`

- task_id: `piwm_0102032a3a`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0102032a3a/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0102032a3a/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0102032a3a/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "desire",
  "intent_label": "leave_without_purchase",
  "visual_summary": "顾客避免眼神接触或身体回避，说明当前不适合主动推进。 当前场景是护肤品陈列区，可见判断应围绕回避互动和离开倾向，不能只按商品兴趣解释。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客与商品或导购的互动关系较弱。 可能有离开或减少互动的趋势。 当前更明显的是回避互动，应优先降低打扰感，而不是推进商品介绍。",
  "gaze_and_attention": "视线回避导购或交流区域。",
  "body_and_hands": "身体可能偏离商品或导购方向。 手部不主动展示需求，可能收回或保持封闭。 身体和手部的封闭信号比商品兴趣更重要。",
  "belief": "Further engagement may feel intrusive at this moment.",
  "desire": "avoid further engagement",
  "intention": "leave without buying"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_7ff44d2096`

- task_id: `piwm_7ff44d2096`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_7ff44d2096/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_7ff44d2096/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_7ff44d2096/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "desire",
  "intent_label": "leave_without_purchase",
  "visual_summary": "顾客避免眼神接触或身体回避，说明当前不适合主动推进。 当前场景是电脑陈列区，可见判断应围绕回避互动和离开倾向，不能只按商品兴趣解释。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客与商品或导购的互动关系较弱。 可能有离开或减少互动的趋势。 当前更明显的是回避互动，应优先降低打扰感，而不是推进商品介绍。",
  "gaze_and_attention": "视线回避导购或交流区域。",
  "body_and_hands": "身体可能偏离商品或导购方向。 手部不主动展示需求，可能收回或保持封闭。 身体和手部的封闭信号比商品兴趣更重要。",
  "belief": "Further engagement may feel intrusive at this moment.",
  "desire": "avoid further engagement",
  "intention": "leave without buying"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是电脑陈列区，可见判断应围绕配置差异、使用年限、售后和实际价差是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对配置差异、使用年限、售后和实际价差，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和处理器/内存配置之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 2: `piwm_a0a987dafb`

- task_id: `piwm_a0a987dafb`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_a0a987dafb/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_a0a987dafb/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_a0a987dafb/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "desire",
  "intent_label": "leave_without_purchase",
  "visual_summary": "顾客避免眼神接触或身体回避，说明当前不适合主动推进。 当前场景是家电展示区，可见判断应围绕回避互动和离开倾向，不能只按商品兴趣解释。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客与商品或导购的互动关系较弱。 可能有离开或减少互动的趋势。 当前更明显的是回避互动，应优先降低打扰感，而不是推进商品介绍。",
  "gaze_and_attention": "视线回避导购或交流区域。",
  "body_and_hands": "身体可能偏离商品或导购方向。 手部不主动展示需求，可能收回或保持封闭。 身体和手部的封闭信号比商品兴趣更重要。",
  "belief": "Further engagement may feel intrusive at this moment.",
  "desire": "avoid further engagement",
  "intention": "leave without buying"
}
```
Prediction:

```text
<stage>attention</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客短暂扫视商品但持续移动，当前兴趣较弱。 当前场景是家电展示区，可见判断应围绕是否形成对家电的稳定兴趣，而不是深度比较。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品只有短暂视觉接触，没有形成稳定停留。 持续走过，缺少停留。 当前互动强度不足，不应把短暂停留误读成明确购买意图。</engagement_pattern>
<gaze_and_attention>视线短暂扫过商品区域，很快离开。</gaze_and_attention>
<body_and_hands>身体主要沿行走方向前进，没有明显转向商品。 手部没有接触商品。 没有接触动作时，不应提前进入推荐或演示。</body_and_hands>
<belief>The category is only mildly interesting, and interruption may feel premature.</belief>
<desire>explore available options</desire>
<intention>continue browsing and comparing</intention>
```

### 类别 `negotiate_price`

- stage distribution: `interest`=40, `desire`=15
- top desires: `obtain a better price`=55
- top intentions: `ask about price flexibility`=55

#### train sample 1: `piwm_3ff954786d`

- task_id: `piwm_3ff954786d`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_3ff954786d/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_3ff954786d/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_3ff954786d/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "negotiate_price",
  "visual_summary": "顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是珠宝柜台，可见判断应围绕上身比例、光泽变化、扣合方式或证书信息。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是上身比例、光泽变化、扣合方式或证书信息是否被确认。",
  "gaze_and_attention": "视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在上身比例、光泽变化、扣合方式或证书信息产生的可见反馈。",
  "body_and_hands": "身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认上身比例、光泽变化、扣合方式或证书信息。",
  "belief": "The product is promising, but fit or usage experience must be confirmed.",
  "desire": "obtain a better price",
  "intention": "ask about price flexibility"
}
```

#### train sample 2: `piwm_6ea36fb640`

- task_id: `piwm_6ea36fb640`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_6ea36fb640/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_6ea36fb640/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_6ea36fb640/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "negotiate_price",
  "visual_summary": "顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是家电展示区，可见判断应围绕手机查询内容与功能覆盖、能耗、安装条件和长期使用成本之间的关系。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。",
  "gaze_and_attention": "视线在手机和商品区域之间切换。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。",
  "body_and_hands": "身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。",
  "belief": "External prices, reviews, or specifications may change the choice.",
  "desire": "obtain a better price",
  "intention": "ask about price flexibility"
}
```

#### train sample 3: `piwm_0c6a9c6e9c`

- task_id: `piwm_0c6a9c6e9c`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0c6a9c6e9c/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0c6a9c6e9c/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0c6a9c6e9c/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "negotiate_price",
  "visual_summary": "顾客反复接触或摆弄商品，说明正在主动评估商品细节。 当前场景是鞋类商品区，可见判断应围绕尺码、脚感、支撑、鞋型和价格差异中需要手部确认的细节。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客与商品有持续直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是鞋底弯折、脚跟包裹、鞋面软硬或尺码贴合是否被确认。",
  "gaze_and_attention": "视线主要集中在商品细节和手部操作位置。 视线重点应落在鞋底弯折、脚跟包裹、鞋面软硬或尺码贴合产生的可见反馈。",
  "body_and_hands": "身体保持靠近商品，姿态显示评估意愿。 手部反复拿起、放下、调整或触摸商品。 手部动作应重点看是否在确认鞋底弯折、脚跟包裹、鞋面软硬或尺码贴合。",
  "belief": "The product details are promising, but tactile or functional confirmation is still needed.",
  "desire": "obtain a better price",
  "intention": "ask about price flexibility"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_11b1c9b3b2`

- task_id: `piwm_11b1c9b3b2`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_11b1c9b3b2/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_11b1c9b3b2/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_11b1c9b3b2/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "negotiate_price",
  "visual_summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是手机陈列区，可见判断应围绕同伴反馈如何影响屏幕手感、拍照、电池、存储和价格差异。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
  "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
  "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。",
  "belief": "A companion's approval may influence whether the choice feels safe.",
  "desire": "obtain a better price",
  "intention": "ask about price flexibility"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是手机陈列区，可见判断应围绕同伴反馈如何影响屏幕手感、拍照样张、续航和价格差异。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。</engagement_pattern>
<gaze_and_attention>视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。</gaze_and_attention>
<body_and_hands>身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。</body_and_hands>
<belief>A companion's approval may influence whether the choice feels safe.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 2: `piwm_1e48f04174`

- task_id: `piwm_1e48f04174`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_1e48f04174/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_1e48f04174/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_1e48f04174/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "negotiate_price",
  "visual_summary": "顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是服装陈列区，可见判断应围绕手机查询内容与面料、剪裁、适用场合和搭配频率之间的关系。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客没有离开商品区域，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对面料、剪裁、适用场合和搭配频率，而不是已经准备成交。",
  "gaze_and_attention": "视线在手机和商品区域之间切换。 注意力可能在价格、评价和版型、面料、颜色、尺码、护理方式和价格差异之间切换。",
  "body_and_hands": "身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。",
  "belief": "External prices, reviews, or specifications may change the choice.",
  "desire": "obtain a better price",
  "intention": "ask about price flexibility"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域查看手机，可能正在做价格、评价或规格研究。 当前场景是服装陈列区，可见判断应围绕手机查询内容与面料、剪裁、版型、颜色和搭配场景中需要确认面料、尺码和护理方式。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客没有离开，手机行为与商品决策同时发生。 移动较少，处在查询和比较状态。 停留本身更像在核对面料、剪裁、版型、颜色和搭配，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线在手机和商品区域之间切换。 注意力可能在价格、评价和版型、面料、尺幅、护理和价格差异之间切换。</gaze_and_attention>
<body_and_hands>身体仍靠近商品，说明手机查询服务于当前商品判断。 至少一只手持手机或操作手机。</body_and_hands>
<belief>External prices, reviews, or specifications may change the choice.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### eval sample 3: `piwm_ae109f5eb9`

- task_id: `piwm_ae109f5eb9`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_ae109f5eb9/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_ae109f5eb9/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_extended/piwm_ae109f5eb9/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "negotiate_price",
  "visual_summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是电脑陈列区，可见判断应围绕同伴反馈如何影响屏幕尺寸、键盘手感、性能配置、重量和价格差异。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
  "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
  "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。",
  "belief": "A companion's approval may influence whether the choice feels safe.",
  "desire": "obtain a better price",
  "intention": "ask about price flexibility"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是电脑陈列区，可见判断应围绕同伴反馈如何影响屏幕尺寸、键盘手感、重量、续航和价格差异。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。</engagement_pattern>
<gaze_and_attention>视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。</gaze_and_attention>
<body_and_hands>身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。</body_and_hands>
<belief>A companion's approval may influence whether the choice feels safe.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

### 类别 `request_demonstration`

- stage distribution: `interest`=80, `desire`=13
- top desires: `see how the product works`=93
- top intentions: `ask for a demonstration`=93

#### train sample 1: `piwm_09df40aae2`

- task_id: `piwm_09df40aae2`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_09df40aae2/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_09df40aae2/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_09df40aae2/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "request_demonstration",
  "visual_summary": "顾客向同伴寻求意见，说明决策受到社交反馈影响。 当前场景是珠宝柜台，可见判断应围绕同伴反馈如何影响佩戴效果、材质、光泽、尺寸和送礼场景。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客仍围绕商品做判断。 移动不大，重点是沟通和确认。 互动对象从商品扩展到同伴，决策节奏会受第三方反馈影响。",
  "gaze_and_attention": "视线在商品和同伴之间切换。 视线不只看商品，也在等待同伴反应。",
  "body_and_hands": "身体在商品与同伴之间形成互动姿态。 手部可能指向商品或把商品展示给同伴。",
  "belief": "A companion's approval may influence whether the choice feels safe.",
  "desire": "see how the product works",
  "intention": "ask for a demonstration"
}
```

#### train sample 2: `piwm_57cc115146`

- task_id: `piwm_57cc115146`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_57cc115146/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_57cc115146/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_57cc115146/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "request_demonstration",
  "visual_summary": "顾客在两个商品之间来回比较，说明已经进入备选项评估。 当前场景是护肤品陈列区，可见判断应围绕两个候选项在肤质适配、主打成分、质地、容量和单次使用成本上的差异。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客注意力在两个具体选项之间切换。 移动围绕两个商品点位展开，不是离开式移动。 比较行为集中在肤质适配、主打成分、质地、容量和单次使用成本，说明选择尚未收敛。",
  "gaze_and_attention": "视线在两个商品或对应价签之间来回移动。 视线切换应被解释为对肤质适配、主打成分、质地、容量和单次使用成本的对照。",
  "body_and_hands": "身体朝向两个备选商品之间的区域。 手部可能指向、拿起或靠近两个备选商品。 手部或身体在两个选项之间移动，说明还没有锁定单一商品。",
  "belief": "Two options remain close, and the decisive difference is not yet clear.",
  "desire": "see how the product works",
  "intention": "ask for a demonstration"
}
```

#### train sample 3: `piwm_0df1b1cf71`

- task_id: `piwm_0df1b1cf71`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0df1b1cf71/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0df1b1cf71/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0df1b1cf71/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "request_demonstration",
  "visual_summary": "顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是珠宝柜台，可见判断应围绕上身比例、光泽变化、扣合方式或证书信息。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是上身比例、光泽变化、扣合方式或证书信息是否被确认。",
  "gaze_and_attention": "视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在上身比例、光泽变化、扣合方式或证书信息产生的可见反馈。",
  "body_and_hands": "身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认上身比例、光泽变化、扣合方式或证书信息。",
  "belief": "The product is promising, but fit or usage experience must be confirmed.",
  "desire": "see how the product works",
  "intention": "ask for a demonstration"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_0b0d31c38b`

- task_id: `piwm_0b0d31c38b`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_0b0d31c38b/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "request_demonstration",
  "visual_summary": "顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是服装陈列区，可见判断应围绕面料手感、垂坠感、版型线条或搭配效果。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是面料手感、垂坠感、版型线条或搭配效果是否被确认。",
  "gaze_and_attention": "视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在面料手感、垂坠感、版型线条或搭配效果产生的可见反馈。",
  "body_and_hands": "身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认面料手感、垂坠感、版型线条或搭配效果。",
  "belief": "The product is promising, but fit or usage experience must be confirmed.",
  "desire": "see how the product works",
  "intention": "ask for a demonstration"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是手机陈列区，可见判断应围绕拍照、屏幕手感、电池续航和存储空间中需要手部确认的细节。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是拍照、屏幕手感、电池续航和存储空间中需要手部确认的细节，缺少可见反馈时才会转向价格和使用周期。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在拍照、屏幕手感、电池续航和存储空间中需要手部确认的细节。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认拍照、屏幕手感、电池续航和存储空间中的体验细节。</body_and_hands>
<belief>The product is promising, but fit or usage experience needs confirmation.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### eval sample 2: `piwm_8f67abde4f`

- task_id: `piwm_8f67abde4f`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_8f67abde4f/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_8f67abde4f/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_8f67abde4f/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "request_demonstration",
  "visual_summary": "顾客在两个商品之间来回比较，说明已经进入备选项评估。 当前场景是鞋类商品区，可见判断应围绕两个候选项在尺码脚感、鞋底支撑、材质、适用场景和价格差异上的差异。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客注意力在两个具体选项之间切换。 移动围绕两个商品点位展开，不是离开式移动。 比较行为集中在尺码脚感、鞋底支撑、材质、适用场景和价格差异，说明选择尚未收敛。",
  "gaze_and_attention": "视线在两个商品或对应价签之间来回移动。 视线切换应被解释为对尺码脚感、鞋底支撑、材质、适用场景和价格差异的对照。",
  "body_and_hands": "身体朝向两个备选商品之间的区域。 手部可能指向、拿起或靠近两个备选商品。 手部或身体在两个选项之间移动，说明还没有锁定单一商品。",
  "belief": "Two options remain close, and the decisive difference is not yet clear.",
  "desire": "see how the product works",
  "intention": "ask for a demonstration"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在两个商品之间来回比较，说明已经进入备选项评估。 当前场景是鞋类商品区，可见判断应围绕两个候选项在尺码、脚感、支撑、材质、清洁方式和价格差异上的差异。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客注意力在两个具体选项之间切换。 移动围绕两个商品点位展开，不是离开式移动。 比较行为集中在尺码、脚感、支撑、材质、清洁方式和价格差异，说明选择尚未收敛。</engagement_pattern>
<gaze_and_attention>视线在两个商品或对应价签之间来回移动。 视线切换应被解释为对尺码、脚感、支撑、材质、清洁方式和价格差异的对照。</gaze_and_attention>
<body_and_hands>身体朝向两个备选商品之间的区域。 手部可能指向、拿起或靠近两个备选商品。 手部或身体在两个选项之间移动，说明还没有锁定单一商品。</body_and_hands>
<belief>Two options remain close, and the decisive difference is not yet clear.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

#### eval sample 3: `piwm_900c2eedb5`

- task_id: `piwm_900c2eedb5`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_900c2eedb5/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_900c2eedb5/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_900c2eedb5/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "request_demonstration",
  "visual_summary": "顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是手机陈列区，可见判断应围绕拍照样张、屏幕滑动流畅度或手持重量。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是拍照样张、屏幕滑动流畅度或手持重量是否被确认。",
  "gaze_and_attention": "视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在拍照样张、屏幕滑动流畅度或手持重量产生的可见反馈。",
  "body_and_hands": "身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认拍照样张、屏幕滑动流畅度或手持重量。",
  "belief": "The product is promising, but fit or usage experience must be confirmed.",
  "desire": "see how the product works",
  "intention": "ask for a demonstration"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是手机陈列区，可见判断应围绕拍照、屏幕手感、存储容量和电池续航。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是拍照、屏幕手感、存储容量和电池续航是否被确认。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在拍照样张、屏幕显示效果、存储容量和电池续航产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认拍照、屏幕手感、存储容量和电池续航。</body_and_hands>
<belief>The product is promising, but fit or usage experience must be confirmed.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

### 类别 `seek_reassurance`

- stage distribution: `desire`=39, `interest`=38, `action`=14
- top desires: `gain reassurance before deciding`=91
- top intentions: `look for reassurance or clarification`=91

#### train sample 1: `piwm_66f3f910c0`

- task_id: `piwm_66f3f910c0`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_66f3f910c0/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_66f3f910c0/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_66f3f910c0/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "seek_reassurance",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是电脑陈列区，可见判断应围绕配置、便携性、保修和未来几年使用成本是否足以支撑价格。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对配置、便携性、保修和未来几年使用成本，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和处理器/内存配置、屏幕尺寸、重量、续航和售后之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "gain reassurance before deciding",
  "intention": "look for reassurance or clarification"
}
```

#### train sample 2: `piwm_7527cafeef`

- task_id: `piwm_7527cafeef`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_7527cafeef/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_7527cafeef/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_7527cafeef/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "seek_reassurance",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是珠宝柜台，可见判断应围绕材质、证书、佩戴场景和送礼适配度是否足以支撑价格。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对材质、证书、佩戴场景和送礼适配度，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和材质、大小、光泽、佩戴效果、证书和价格差异之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "gain reassurance before deciding",
  "intention": "look for reassurance or clarification"
}
```

#### train sample 3: `piwm_7bc8354764`

- task_id: `piwm_7bc8354764`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_7bc8354764/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_7bc8354764/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_evalqa_seed/piwm_7bc8354764/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "seek_reassurance",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是鞋类商品区，可见判断应围绕脚感、材质、耐穿度和使用场景是否足以支撑价格。视角为斜角监控/第三方视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对脚感、材质、耐穿度和使用场景，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和尺码脚感、鞋底支撑、材质、适用场景和价格差异之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "gain reassurance before deciding",
  "intention": "look for reassurance or clarification"
}
```

Eval examples with prediction:

#### eval sample 1: `piwm_23563ed080`

- task_id: `piwm_23563ed080`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_23563ed080/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_23563ed080/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_23563ed080/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "interest",
  "intent_label": "seek_reassurance",
  "visual_summary": "顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是家电展示区，可见判断应围绕功能覆盖、能耗、安装条件和长期使用成本是否足以支撑价格。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。",
  "gaze_and_attention": "视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。",
  "body_and_hands": "身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。",
  "belief": "The product is interesting, but its value-for-money is not yet justified.",
  "desire": "gain reassurance before deciding",
  "intention": "look for reassurance or clarification"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客持续停留在商品区域，并反复关注价格或价值信息，表现为有兴趣但仍在犹豫。 当前场景是家电展示区，可见判断应围绕功能覆盖、能耗、安装条件和长期使用成本是否足以支撑价格。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品保持稳定关系，不是快速经过；注意力围绕商品和价格区域。 移动速度较慢或基本停留，缺少快速离场动作。 停留本身更像在核对功能覆盖、能耗、安装条件和长期使用成本，而不是已经准备成交。</engagement_pattern>
<gaze_and_attention>视线持续落在商品、价签或附近陈列区域，呈现反复查看而非一次性扫视。 注意力可能在价格、评价和尺寸、功率/能耗、核心功能、安装条件和售后之间切换。</gaze_and_attention>
<body_and_hands>身体朝向商品区域，姿态相对停留，没有明显转身离开。 手部没有快速离开商品区域，可能停在商品附近或保持比较姿态。</body_and_hands>
<belief>The product is interesting, but its value-for-money is not yet justified.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 2: `piwm_3549e65d37`

- task_id: `piwm_3549e65d37`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_3549e65d37/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_3549e65d37/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_3549e65d37/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "action",
  "intent_label": "seek_reassurance",
  "visual_summary": "顾客主动走向柜台或服务区域，说明接近明确咨询或决策时刻。 当前场景是护肤品陈列区，可见判断应围绕顾客是否需要围绕肤质适配、成分功效、质地和价格容量获得人工确认。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客从浏览转向服务/结算区域。 移动方向明确，正在接近服务点。",
  "gaze_and_attention": "视线朝向柜台、导购或服务点。",
  "body_and_hands": "身体朝柜台方向前进。 手部可能携带商品、指向柜台或准备询问。",
  "belief": "The shopper may be ready for service, but still needs final confirmation.",
  "desire": "gain reassurance before deciding",
  "intention": "look for reassurance or clarification"
}
```
Prediction:

```text
<stage>interest</stage>
<intent_label>request_demonstration</intent_label>
<visual_summary>顾客正在试用或测试商品，说明已经进入体验式评估。 当前场景是护肤品陈列区，可见判断应围绕质地、吸收速度、气味和试用肤感。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客和商品发生直接体验关系。 动作与试用过程相关，停留意愿较强。 互动已经进入体验层面，重点是质地、吸收速度、气味和试用肤感是否被确认。</engagement_pattern>
<gaze_and_attention>视线集中在试用效果、镜面反馈或商品反应上。 视线重点应落在质地、吸收速度、气味和试用肤感产生的可见反馈。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合测试动作。 手部正在操作、试穿或测试商品。 手部动作应重点看是否在确认质地、吸收速度、气味和试用肤感。</body_and_hands>
<belief>The product is promising, but fit or usage experience must be confirmed.</belief>
<desire>see how the product works</desire>
<intention>ask for a demonstration</intention>
```

#### eval sample 3: `piwm_6393f77756`

- task_id: `piwm_6393f77756`
- image paths:
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_6393f77756/frames/000.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_6393f77756/frames/001.jpg`
  - `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/piwm_6393f77756/frames/002.jpg`

Ground truth user_intent JSON:

```json
{
  "stage": "action",
  "intent_label": "seek_reassurance",
  "visual_summary": "顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是家电展示区，可见判断应围绕顾客是否需要围绕尺寸、核心功能、能耗、噪音和售后安装获得人工确认。视角为导购可观察中近距离视角。",
  "engagement_pattern": "顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。",
  "gaze_and_attention": "视线从商品转向周围空间或导购可能出现的位置。",
  "body_and_hands": "身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。",
  "belief": "A suitable option may be close, but staff input is needed before deciding.",
  "desire": "gain reassurance before deciding",
  "intention": "look for reassurance or clarification"
}
```
Prediction:

```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在商品区域停留并向周围寻找帮助，可能已经接近需要导购介入。 当前场景是家电展示区，可见判断应围绕顾客是否需要围绕尺寸、核心功能、能耗、噪音和售后安装获得人工确认。视角为导购可观察中近距离视角。</visual_summary>
<engagement_pattern>顾客仍处在商品或柜台附近。 移动不明显，更多是原地寻找帮助。</engagement_pattern>
<gaze_and_attention>视线从商品转向周围空间或导购可能出现的位置。</gaze_and_attention>
<body_and_hands>身体仍面向商品或柜台，但头部/视线外转。 手部动作相对暂停，像是在等待回应。</body_and_hands>
<belief>A suitable option may be close, but staff input is needed before deciding.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

## B. 类别相似度初判

范围：只比较 train+eval 样本数 >= 30 的类别。判断是 Codex 的初判，用于帮助 PI 决定是否合并/降权/接受，不作为最终 taxonomy 决策。

| pair | 视觉上是否可区分 | 语义是否重叠 | 理由 |
|---|---|---|---|
| `confirm_choice` vs `explore_options` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |
| `confirm_choice` vs `negotiate_price` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |
| `confirm_choice` vs `request_demonstration` | uncertain | partial | 试用后可能走向确认选择，也可能只是要求演示；视觉证据边界接近。 |
| `confirm_choice` vs `seek_reassurance` | uncertain | yes | 都处在接近决策但仍需确认的区域；视觉上常表现为停留、看价签/商品/导购，缺少对话很难区分“确认选择”还是“寻求安心”。 |
| `explore_options` vs `negotiate_price` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |
| `explore_options` vs `request_demonstration` | uncertain | yes | 都可能表现为靠近商品和试用/浏览；区别在于是否明确需要演示，单靠三帧图像常不稳定。 |
| `explore_options` vs `seek_reassurance` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |
| `negotiate_price` vs `request_demonstration` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |
| `negotiate_price` vs `seek_reassurance` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |
| `request_demonstration` vs `seek_reassurance` | uncertain | uncertain | 二者共享 AIDA stage，三帧视觉证据可能不足以稳定区分；需要 PI 看样本确认。 |

## C. PI 审阅建议

1. 优先审 `confirm_choice` vs `seek_reassurance`：二者都可能是“接近决策但仍需确认”，视觉边界很薄。
2. 优先审 `compare_value_for_money` vs `negotiate_price`：前者是价值判断，后者通常需要讨价还价语境；仅凭图像很难判定。
3. 审 `request_demonstration` vs `explore_options`：如果没有明确手部试用/请求演示动作，二者容易混。
4. 对 F1=0 但训练样本不少的 `seek_reassurance`，建议考虑改写定义、合并到 confirm_choice 的子标签，或在 Stage-1 中降权为弱标签。

## 文件与校验

- `data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_train_v1.jsonl` rows `493` sha256 `33871d33f802e6ade7c84354fd5934c052b91c0696533dd3b775faceac1ad685`
- `data/official/ms_swift_server_resolved/piwm_train_stage1_user_intent_val_v1.jsonl` rows `50` sha256 `18257faf817c097f40dc8a198e34e1d443a62c92fb216cf2c4e46dc74dc5ed31`
- `reports/stage1_eval_full_inference.jsonl` rows `235` sha256 `15d62284fc88b05627579c754f376fe04c68b0a24bf2e15976eb2ab5a9205d07`
- `reports/stage1_task_level_eval_intermediate.json` rows `json` sha256 `c3e922e037df894e1ede56f0c2ebbda64148e168855c35ea2610cf5576fc749f`
