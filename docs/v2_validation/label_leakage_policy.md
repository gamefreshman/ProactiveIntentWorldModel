# PIWM v2.2 Label Leakage Policy

更新时间：2026-05-15

本页定义 Kling prompt / video-generation prompt 中禁止出现的内部标签。目标是防止 synthetic video 直接暴露 gold labels，导致后续多模态训练学到文字标签而不是视觉行为。

## 禁止出现在 `kling_prompt`

### State / BDI / outcome labels

```text
latent_state
state_subtype
intent_tier
low_intent_browsing
ready_to_buy
BDI
belief
desire
intention
reward
risk_tags
risk_level
failure_mode
outcome_type
success
failure
best_action
```

### DialogueAct names

```text
Greet
Elicit
Inform
Recommend
Reassure
Hold
```

### Legacy action names

```text
A1_silent_observe
A2_offer_value_comparison
A3_strong_recommend
A4_open_with_question
A5_provide_demonstration
A6_acknowledge_and_wait
A7_disengage
A8_offer_companion_invite
```

### Intent labels

```text
compare_value_for_money
seek_reassurance
explore_options
confirm_choice
leave_without_purchase
request_demonstration
negotiate_price
no_clear_intent
```

## 允许的自然语言描述

允许描述可见行为，但不能写内部标签名。例如：

```text
The shopper briefly turns their head toward the display and keeps walking.
```

允许描述摄像机、场景、商品、时间线和负约束：

```text
no subtitles, no voiceover, no UI overlays
```

## Runtime Enforcement

当前检查入口：

```text
scripts.prompt_builder.forbidden_label_hits(prompt)
scripts.qa_gate.check_label_leakage(prompt_json)
```

`run_qa_for_session()` 会调用 `check_label_leakage()`，并把结果写入：

```text
label_leakage
label_leakage_hits
```

若 `label_leakage=true`，QA gate 不允许 `overall_pass=true`。

## 扩展规则

新增任何 internal label 字段前，必须同步扩展：

1. `forbidden_label_hits()` blacklist
2. `check_label_leakage()` 单测
3. 本文档
