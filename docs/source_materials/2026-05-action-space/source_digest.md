# 2026-05 Action Space Source Digest

更新时间：2026-05-11 CST

本目录保存本次 PIWM 项目体系整合的外部来源副本。后续更新动作空间、拍摄标签、realization 模板或真实数据入库字段时，以这里的材料为第一追溯入口。

## Source Priority

```text
附件版本 > guochenmeinian/piwm 轻量 pipeline > 当前仓库旧 A1-A8 文档
```

## Files

| 文件 | 来源 | 用途 |
|---|---|---|
| `agent_action_space_design_v0.md` | 用户提供附件 | 定义 6 个 Dialogue Acts、三层架构、共现规则、Realization 接口 |
| `shooting_plan_v4.md` | 用户提供附件 | 定义 12 个顾客状态、6 种终端响应、A/B 匹配、clip manifest 建议字段 |
| `shooting_script_S05.pdf` | 用户提供附件 | S05 犹豫比较的代表拍摄脚本；A 版 `T2_VALUE_COMPARE`，B 版 `T3_STRONG_RECOMMEND` |
| `/Users/mutsumi/Desktop/WorkSpace/piwm` | `guochenmeinian/piwm` 本地 clone | 轻量 `seed -> manifest -> labeled -> kling` 参考，不作为主仓库 |

## Decisions Captured

- 主项目入口固定为 `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel`。
- 上层 policy 只看 6 个 Dialogue Acts，不直接学习屏幕、灯效、柜内动作等硬件实现。
- 中层 Realization 是 deterministic template/rule layer，负责把 `(act, params)` 翻译成终端输出包。
- 旧 `A1-A8` 与 `T1-T7/T_TRANSACT` 不再作为新 policy 语义层，但保留为兼容 alias。
- S05 作为第一条验收样例：A 版是 `Inform(content_type=comparison)`，B 版是 `Recommend(pressure=firm)`。
