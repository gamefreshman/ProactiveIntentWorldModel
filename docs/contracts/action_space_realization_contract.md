# PIWM Action Space and Realization Contract

更新时间：2026-05-11 CST

本文是 PIWM v2 动作空间的当前契约。它替代旧文档中把 policy 动作、T-state、屏幕 UI、真人导购动作混在一起的写法。旧 `A1-A8` 和 `T1-T7/T_TRANSACT` 仍作为兼容标签保留，但不再是新体系的语义中心。

## 1. Three Layers

```text
Policy layer:      DialogueAct + params
Realization layer: deterministic template/rule translation
Terminal layer:    screen / voice / light / cabinet motion
```

- Policy layer 只决定“做什么”，例如 `Inform(content_type=comparison)`。
- Realization layer 决定“怎么演”，输出终端响应包。
- Terminal layer 只执行响应包，不理解 AIDA/BDI/reward。

## 2. Dialogue Acts

| Act | Dimension | Params | Meaning |
|---|---|---|---|
| `Greet` | Social Obligations | `phase=open|close` | 开场或收尾礼节 |
| `Elicit` | Task | `openness=open|closed`, `slot` | 主动获取顾客信息 |
| `Inform` | Task | `content_type=comparison|demo|attributes|price`, `depth=brief|detailed` | 提供描述、比较、演示或参数信息 |
| `Recommend` | Task | `target=item|action`, `pressure=soft|firm` | 建议具体商品或下一步 |
| `Reassure` | Allo-Feedback | `focus=time|decision|alternatives` | 安抚、降压、降低决策压力 |
| `Hold` | Turn Management | `mode=silent|ambient` | 让出话轮或低干扰观察 |

共现规则：

- `Elicit / Inform / Recommend` 每轮最多一个。
- `Greet / Reassure / Hold` 可与 Task act 共现。
- 新增终端能力优先挂到已有 act 的 params 或 realization 模板，不直接新增 policy act。

## 3. Terminal Realization Output

Realization layer 输出以下结构：

```json
{
  "surface_text": "我把这两款的差别列清楚...",
  "screen": {"action": "show_comparison_or_details", "target": "{candidate_items}", "cta": null},
  "voice_style": "neutral",
  "light": "soft_focus_on_comparison_cards",
  "cabinet_motion": null,
  "duration_ms": 4000,
  "dialogue_act": "Inform",
  "act_params": {"content_type": "comparison", "depth": "brief"},
  "co_acts": [],
  "legacy_action": "A2_offer_value_comparison"
}
```

旧 `best_action_realization.utterance / physical_action / timing / rationale` 继续保留，服务已有训练和评估；新终端演出以 `realization` 为准。

## 4. Legacy Mapping

| Legacy action | DialogueAct |
|---|---|
| `A1_silent_observe` | `Hold(mode=silent)` |
| `A2_offer_value_comparison` | `Inform(content_type=comparison, depth=brief)` |
| `A3_strong_recommend` | `Recommend(target=item, pressure=firm)` |
| `A4_open_with_question` | `Elicit(openness=open, slot=need_focus)` |
| `A5_provide_demonstration` | `Inform(content_type=demo, depth=brief)` |
| `A6_acknowledge_and_wait` | `Reassure(focus=time)` + `Hold(mode=ambient)` |
| `A7_disengage` | `Hold(mode=ambient)` |
| `A8_offer_companion_invite` | `Elicit(openness=open, slot=companion_opinion)` |

| T-state | DialogueAct |
|---|---|
| `T1_SILENT_OBSERVE` | `Hold(mode=silent)` |
| `T2_VALUE_COMPARE` | `Inform(content_type=comparison, depth=brief)` |
| `T3_STRONG_RECOMMEND` | `Recommend(target=item, pressure=firm)` |
| `T4_OPEN_QUESTION` | `Elicit(openness=open, slot=need_focus)` |
| `T5_DEMO` | `Inform(content_type=demo, depth=brief)` |
| `T6_ACK_WAIT` | `Reassure(focus=time)` + `Hold(mode=ambient)` |
| `T7_DISENGAGE` | `Hold(mode=ambient)` |
| `T_TRANSACT` | `Greet(phase=close)` |

## 5. Shooting Response Mapping

| 拍摄响应 | DialogueAct |
|---|---|
| 招呼问候 | `Greet(phase=close)` |
| 提问探询 | `Elicit(openness=open, slot=need_focus)` |
| 提供信息 - 比较两件 | `Inform(content_type=comparison, depth=brief)` |
| 提供信息 - 演示一件 | `Inform(content_type=demo, depth=brief)` |
| 提供信息 - 罗列参数 / 价格 | `Inform(content_type=attributes, depth=brief)` |
| 建议推荐 - 力度温和 | `Recommend(target=item, pressure=soft)` |
| 建议推荐 - 力度强势 | `Recommend(target=item, pressure=firm)` |
| 安抚降压 | `Reassure(focus=time)` + `Hold(mode=ambient)` |
| 暂不打扰 - 完全静默 | `Hold(mode=silent)` |
| 暂不打扰 - 背景退出 | `Hold(mode=ambient)` |

S05 验收样例：

- `G001_S05_A`: `T2_VALUE_COMPARE` -> `Inform(content_type=comparison, depth=brief)`，顾客继续评估、信心略升。
- `G001_S05_B`: `T3_STRONG_RECOMMEND` -> `Recommend(target=item, pressure=firm)`，顾客防御后撤、压力上升。

## 6. Code Anchors

- `piwm_data/rules.py`: act enum、参数 schema、legacy/T-state/shooting response mapping、terminal realization 默认模板。
- `piwm_data/schemas.py`: `MainSchemaRecord.dialogue_act / act_params / co_acts / realization`。
- `piwm_data/exporters.py`: 导出时同时保留旧 action 和新 dialogue-act/terminal-realization 字段。
- `docs/source_materials/2026-05-action-space/`: 本契约的来源材料副本。
