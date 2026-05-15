# PIWM v2.2 Failure Mode Coverage

更新时间：2026-05-15

本页说明 v2.2 `failure_mode` taxonomy 的覆盖范围和已知边界。它不是新的规则入口；可执行规则仍以 `piwm_data/expert_corpus/distilled/conditional_rules.jsonl` 为准。

## 覆盖范围

v2.2 的 failure-mode taxonomy 覆盖的是主动干预失败，主要来源于当前 expert corpus 中已经纳入的销售过程、SPIN Selling、非语言互动和 Reactance Theory：

- premature closing：在顾客仍处于 attention / interest / exploration 时过早进入 closing。
- pressure reactance：强推荐或选择自由受威胁时触发防御性反弹。
- feature dump / information overload：顾客低意图或回避时，信息展示变成负担。
- timing intrusion：顾客只是路过或无眼神接触时，主动信息干预打断其节奏。

这些失败模式主要解释 `Recommend`、`Inform`、`Elicit`、`Reassure` 等主动动作在错误时机下的反效果。

## 已知边界

v2.2 暂不建模被动干预失败：

- under-engagement：顾客其实需要帮助，但系统/导购过度静默。
- premature withdrawal：顾客仍可挽回，但系统/导购过早退出。
- misclassified disengagement：状态推断错误，把犹豫顾客误判为 disengaged。

这些失败更接近 service failure / service recovery 文献，而不是当前 batch_003 使用的 SPIN Selling、personal selling process 和 Reactance Theory。为了保持 provenance 诚实，v2.2 不凭空补被动失败模板。

## 4 条 null transition

当前 21 条 transition 中有 17 条显式 `failure_mode`，4 条为 `null`：

| rule_id | state | action | rationale |
|---|---|---|---|
| `TRANS_015` | `early_browsing` | `A1_silent_observe` | 静默观察是低干预动作；当前 source-backed taxonomy 没有独立失败分支 |
| `TRANS_018` | `disengaged` | `A7_disengage` | 已 disengaged 时退出是去压迫动作；失败更可能来自 state 误判 |
| `TRANS_019` | `disengaged` | `A1_silent_observe` | 静默不升级压力；失败更可能来自 state 误判 |
| `TRANS_020` | `defensive_withdrawal` | `A7_disengage` | 防御性回避下退出是 de-escalation；更细的 service recovery 失败留给后续版本 |

统一 rationale 字段：

```text
Low-intervention or disengagement actions in this state are not associated with distinct failure branches in the current source-backed taxonomy.
```

## 后续扩展

如果 v2.3 要建模被动干预失败，应先新增 service failure / service recovery source batch，再扩充 taxonomy。候选文献方向包括 Bitner et al. (1990) 及后续服务失败与服务补救研究。

在新 source batch 完成前，不应把 under-engagement 或 premature withdrawal 作为 source-backed failure mode 写入 transition rules。
