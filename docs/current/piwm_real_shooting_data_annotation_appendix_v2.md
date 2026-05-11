# PIWM 真实数据拍摄标注附录（给数据负责人）

本文不是给现场拍摄人员看的执行清单，而是给数据负责人、标注负责人和后期入库人员使用的技术附录。
现场拍摄团队只需要阅读 [piwm_real_shooting_execution_checklist_v2.md](piwm_real_shooting_execution_checklist_v2.md)。

## 使用边界

- 拍摄团队负责：画面、表演、A/B 对照、素材交付、现场质检。
- 数据负责人负责：把素材整理为 PIWM 可训练 / 可评估数据。
- 本附录负责：统一 `ShootingClipRecord`、三轴视觉状态、终端响应 realization、未来反应、QA 字段和入库字段。

## compact_v2 标注目标

每条 clip 不能只给粗标签。它需要支持下面这条链路：

```text
当前画面证据 -> 当前顾客状态 -> 终端响应 -> 后续可见反应 -> 动作好坏判断
```

其中“当前画面证据”和“后续可见反应”必须能被人从视频或抽帧中看出来。

## 当前视觉状态 visual_state

`visual_state` 描述“顾客现在看起来怎样”。它先于状态标签，不能只写结论。

```json
{
  "visual_state": {
    "summary": "顾客在鞋类商品区停留较长时间，反复查看价格区域；身体朝向商品，未表现快速离场动作。",
    "engagement_pattern": "顾客与商品保持稳定关系，不是路过式扫视，也没有明显离开趋势。",
    "gaze_and_attention": "视线在商品和价格区域之间反复切换，呈现犹豫式查看。",
    "body_and_hands": "身体朝向商品，手部停留在商品附近或在两个选项之间来回移动。"
  }
}
```

三轴含义：

| 字段 | 看什么 | 用来判断什么 |
|---|---|---|
| `engagement_pattern` | 停留、靠近、离开、互动强度 | 顾客是否仍在关系中，还是已经退出 |
| `gaze_and_attention` | 视线方向、注意力切换、是否找人 | 犹豫、求助、兴趣、回避 |
| `body_and_hands` | 身体朝向、手部触碰、回缩、展示 | 主动评估、防御、试用、准备决策 |

## 终端响应 terminal_realization

真实拍摄入库时使用 `dialogue_act / act_params / co_acts` 描述策略语义，使用 `terminal_realization` 描述智能售货柜实际执行包。旧 `best_action / best_action_realization` 只作历史数据兼容填充。

```json
{
  "dialogue_act": "Inform",
  "act_params": {"content_type": "comparison", "depth": "brief"},
  "co_acts": [],
  "legacy_action": "A2_offer_value_comparison",
  "t_state": "T2_VALUE_COMPARE",
  "terminal_realization": {
    "surface_text": "我把这两款的价格、功能和适合场景列在屏幕上，您可以慢慢看。",
    "screen": {"action": "show_comparison_or_details", "target": "candidate_items", "cta": null},
    "voice_style": "neutral",
    "light": "soft_focus_on_comparison_cards",
    "cabinet_motion": null,
    "duration_ms": 4000
  }
}
```

要求：

1. `dialogue_act / act_params` 必须能通过 `piwm_data.rules.validate_dialogue_act()`。
2. `surface_text` 必须是顾客能听到或看到的自然语言，不写内部枚举。
3. `screen.action` 必须是终端 UI 可执行动作，例如比较卡、演示页、开放问题或待机。
4. `voice_style / light / cabinet_motion / duration_ms` 用来复现终端表现，不写真人导购站位。
5. `legacy_action / t_state` 保留用于旧数据、旧训练和旧评测兼容。

## 后续可见反应 visible_reaction

`visible_reaction` 描述动作之后顾客“看起来怎么变”。它与 `visual_state` 使用同一套三轴。

正向反应示例：

```json
{
  "visible_reaction": {
    "engagement_pattern_change": "顾客从犹豫停留转为继续参与对话，仍停留在商品区域。",
    "gaze_and_attention_change": "视线从商品/价签切换到导购，再回到商品。",
    "body_and_hands_change": "身体保持朝向商品，手部重新指向或触碰比较对象。"
  }
}
```

负向反应示例：

```json
{
  "visible_reaction": {
    "engagement_pattern_change": "顾客从停留比较转为减少互动，并出现后撤或离开趋势。",
    "gaze_and_attention_change": "视线避开导购和商品，注意力转向出口或其他区域。",
    "body_and_hands_change": "身体转离商品区域，手部从商品附近收回。"
  }
}
```

## risk / benefit / reward 规则

现场只记录可见事实，数据负责人按统一规则换算 `risk / benefit / reward`。

### risk

| risk | 判定条件 |
|---|---|
| `low` | 顾客没有明显防御、后撤、回避或加速离开；导购动作压力低 |
| `medium` | 顾客有轻微停顿、回避、犹豫增加，但仍留在商品区域 |
| `high` | 顾客后撤、收手、转身、快步离开、明显回避导购 |

### benefit

| benefit | 判定条件 |
|---|---|
| `low` | 动作没有推进判断，或使顾客更远离互动 |
| `medium` | 动作降低压力或维持停留，但没有明显推进决策 |
| `high` | 动作让顾客继续比较、回应导购、上手试用、接近决策 |

### reward

| 可见结果 | reward 建议 |
|---|---:|
| 顾客进入互动、继续评估、信心提升 | `0.70` 到 `0.90` |
| 顾客保持停留但变化不大 | `0.30` 到 `0.50` |
| 顾客无明显变化，动作基本中性 | `0.00` 到 `0.20` |
| 顾客犹豫加重、热度下降 | `-0.20` 到 `-0.40` |
| 顾客防御、后撤、离开 | `-0.50` 到 `-0.70` |

同一 parent 状态下，原则上应满足：

```text
reward(A版) > reward(B版)
dialogue_act / act_params = A版终端响应
```

如果实际画面里 B 版明显更好，不能强行标注，应退回现场说明或记录为异常样本。

## QA 字段

每条 clip 的 QA 记录建议保存为：

```json
{
  "clip_id": "G001_S05_A",
  "overall_pass": true,
  "checks": {
    "video_exists": true,
    "frames_100_exist": true,
    "start_state_visible": true,
    "terminal_response_visible": true,
    "future_reaction_visible": true,
    "ab_start_state_consistent": true,
    "viewpoint_pass": true,
    "visual_state_supported": true,
    "no_camera_look": true,
    "no_unlicensed_face_or_sensitive_info": true,
    "label_complete": true
  },
  "notes": ""
}
```

只有 `overall_pass=true` 的 clip 才能进入正式 QA-reviewed 评估集。
未完全人工审阅的 clip 可以进入训练候选池，但不能写成 QA-pass。

## 入库字段

每条 final 成片至少要有：

- `clip_id`
- `session_id`
- `viewpoint`
- `product_category`
- `persona_type`
- `split`
- `shooting_state`
- `version`
- `response_type_zh`
- `visual_state.summary`
- `visual_state.engagement_pattern`
- `visual_state.gaze_and_attention`
- `visual_state.body_and_hands`
- `aida_stage`
- `bdi.belief/desire/intention`
- `dialogue_act`
- `act_params`
- `co_acts`
- `terminal_realization.surface_text`
- `terminal_realization.screen`
- `terminal_realization.voice_style`
- `terminal_realization.light`
- `terminal_realization.cabinet_motion`
- `terminal_realization.duration_ms`
- `next_aida_stage`
- `next_bdi`
- `risk / benefit / reward`
- `best_action`
- `candidate_actions`
- `legacy_action`
- `t_state`

旧 `best_action_realization.utterance / physical_action / timing / rationale` 可由 `terminal_realization` 迁移填充，但不再作为新真实拍摄数据的主口径。

Future Verification 额外字段：

- `parent_clip_id`
- `continuation_role`
- `visible_reaction.engagement_pattern_change`
- `visible_reaction.gaze_and_attention_change`
- `visible_reaction.body_and_hands_change`
- `match`
