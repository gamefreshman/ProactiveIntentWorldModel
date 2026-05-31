# PIWM Action Space and Realization Contract

更新时间：2026-05-19 CST

本文是 PIWM v2.2 动作空间的当前契约。它替代旧文档中把 policy 动作、T-state、屏幕 UI、真人导购动作混在一起的写法。旧 `A1-A8` 和 `T1-T7/T_TRANSACT` 仍作为兼容标签保留，但不再是新体系的语义中心。

当前明确分成两条数据线：

- `PIWM-Train-Synth-v1` 保留真人导购逻辑，训练模型理解顾客状态、真人导购介入策略、话术和动作。这里的执行主体是 human salesperson logic。
- 后续单独建设 target terminal dataset，执行主体才是智能导购终端 / 数字人售货柜，使用 `screen / voice / light / cabinet_motion` 作为主监督。

当前 operational policy space 收敛为 5 个动作：`Greet / Elicit / Inform / Recommend / Hold`。`Reassure` 保留为历史/source 标签和兼容分析边界，但不进入当前 5-act action-selection 训练、推理和 macro-F1 口径。

## 1. Three Layers

```text
Policy layer:      DialogueAct + params
Human realization: salesperson utterance / physical_action / timing
Terminal target:   screen / voice / light / cabinet motion
```

- Policy layer 只决定“做什么”，例如 `Inform(content_type=comparison)`。
- `PIWM-Train-Synth-v1` 的 realization 仍以真人导购的 `best_action_realization` 为主。
- target terminal dataset 另行用 deterministic template/rule layer 输出终端响应包。
- Terminal layer 只执行响应包，不理解 AIDA/BDI/reward。

## 2. Operational Dialogue Acts

| Act | Dimension | Params | Meaning |
|---|---|---|---|
| `Elicit` | Task | `openness=open|closed`, `slot` | 主动获取顾客信息 |
| `Inform` | Task | `content_type=comparison|demo|attributes|price`, `depth=brief|detailed` | 提供描述、比较、演示或参数信息 |
| `Recommend` | Task | `target=item|action`, `pressure=soft|firm` | 建议具体商品或下一步 |
| `Greet` | Social Obligations | `phase=open|close` | 开场或收尾礼节 |
| `Hold` | Turn Management | `mode=silent|ambient` | 让出话轮或低干扰观察 |

排除/兼容动作：

| Act | Status | Params | Meaning |
|---|---|---|---|
| `Reassure` | historical/source compatibility; excluded from current 5-act train/eval/inference | `focus=time|decision|alternatives` | 安抚、降压、降低决策压力 |

共现规则：

- `Greet / Elicit / Inform / Recommend` 每轮最多一个。
- `Hold` 可与 Task act 共现。
- `Reassure` 不进入当前 5-act action-selection 主路径；历史数据中出现时只能作为 source/compatibility 分析对象。
- 新增终端能力优先挂到已有 act 的 params 或 realization 模板，不直接新增 policy act。
- v2.2 不再把共现动作作为顶层 `co_acts`；辅助动作写入 `act_params.supporting_acts`。旧 `co_acts` 只作为 legacy alias 读入和回写。

示例：

```json
{
  "dialogue_act": "Reassure",
  "act_params": {
    "focus": "time",
    "supporting_acts": [
      {"type": "Hold", "params": {"mode": "ambient"}}
    ]
  },
  "legacy_action": "A6_acknowledge_and_wait"
}
```

## 3. Human and Terminal Realization

`PIWM-Train-Synth-v1` 的主监督是真人导购执行：

```json
{
  "best_action_realization": {
    "utterance": "您可以慢慢看，我就在旁边...",
    "physical_action": "轻微点头或短句确认后后退半步，身体侧开。",
    "timing": "顾客需要空间但不应完全消失时使用。",
    "rationale": "降低打扰感，适合犹豫但未准备交流的顾客。"
  }
}
```

target terminal dataset 的 realization 输出以下结构：

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
  "legacy_co_acts": [],
  "legacy_action": "A2_offer_value_comparison"
}
```

旧 `best_action_realization.utterance / physical_action / timing / rationale` 在 `PIWM-Train-Synth-v1` 中不是废字段，而是该数据集的主体监督。`realization` 只作为从同一 policy act 派生出的终端 target 草案，后续需要在独立 target terminal dataset 中重新采集/校准。

## 4. Legacy Mapping

| Legacy action | DialogueAct |
|---|---|
| `A1_silent_observe` | `Hold(mode=silent)` |
| `A2_offer_value_comparison` | `Inform(content_type=comparison, depth=brief)` |
| `A3_strong_recommend` | `Recommend(target=item, pressure=firm)` |
| `A4_open_with_question` | `Elicit(openness=open, slot=need_focus)` |
| `A5_provide_demonstration` | `Inform(content_type=demo, depth=brief)` |
| `A6_acknowledge_and_wait` | `Reassure(focus=time, supporting_acts=[Hold(mode=ambient)])` |
| `A7_disengage` | `Hold(mode=ambient)` |
| `A8_offer_companion_invite` | `Elicit(openness=open, slot=companion_opinion)` |

| T-state | DialogueAct |
|---|---|
| `T1_SILENT_OBSERVE` | `Hold(mode=silent)` |
| `T2_VALUE_COMPARE` | `Inform(content_type=comparison, depth=brief)` |
| `T3_STRONG_RECOMMEND` | `Recommend(target=item, pressure=firm)` |
| `T4_OPEN_QUESTION` | `Elicit(openness=open, slot=need_focus)` |
| `T5_DEMO` | `Inform(content_type=demo, depth=brief)` |
| `T6_ACK_WAIT` | `Reassure(focus=time, supporting_acts=[Hold(mode=ambient)])`，历史/source 兼容，不计入当前主 5-act |
| `T7_DISENGAGE` | `Hold(mode=ambient)` |
| `T_TRANSACT` | `Greet(phase=close)`，当前 5-act 兼容映射 |

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
| 安抚降压 | `Reassure(focus=time, supporting_acts=[Hold(mode=ambient)])`，历史/source 兼容，不进入当前 5-act |
| 暂不打扰 - 完全静默 | `Hold(mode=silent)` |
| 暂不打扰 - 背景退出 | `Hold(mode=ambient)` |

S05 验收样例：

- `G001_S05_A`: `T2_VALUE_COMPARE` -> `Inform(content_type=comparison, depth=brief)`，顾客继续评估、信心略升。
- `G001_S05_B`: `T3_STRONG_RECOMMEND` -> `Recommend(target=item, pressure=firm)`，顾客防御后撤、压力上升。

## 6. Code Anchors

- `piwm_data/rules.py`: act enum、参数 schema、legacy/T-state/shooting response mapping、supporting_acts 兼容层、terminal realization 默认模板。
- `piwm_data/schemas.py`: `MainSchemaRecord.dialogue_act / act_params / realization`，旧 `co_acts` 只作 legacy alias。
- `piwm_data/exporters.py`: 导出时同时保留旧 action 和新 dialogue-act/terminal-realization 字段。
- `docs/source_materials/2026-05-action-space/`: 本契约的来源材料副本。
