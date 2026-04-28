# PIWM Docs Maintenance Rules

更新时间：2026-04-29

## 1. 核心原则

`docs/` 的维护原则是：

> 数据生成闭环优于单一架构优化。  
> 文档必须帮助项目从 expert rules 到可训练 JSONL 闭合，而不是无约束增加想法。

新增文档前必须先回答：

1. 它服务哪个闭环阶段？
2. 它替代、补充，还是归档已有文档？
3. 它的 DoD 是否能被验证？
4. 它是否需要加入 `RESEARCH_LOG.md` 的 Active Document Index？

## 2. 编号规则

活跃文档使用两位数字前缀：

```text
00_*.md
01_*.md
02_*.md
...
```

编号含义：

| 编号段 | 用途 |
|---|---|
| `00` | 最高优先级审计、claim 对齐、阻塞项 |
| `01-02` | 当前状态与执行主计划 |
| `03-04` | 核心技术契约 |
| `05-07` | 当前代码和工具使用说明 |
| `08-09` | 论文与 related work 支撑材料 |
| `10-19` | 背景说明、维护规则、辅助决策 |
| `90-99` | 临时草稿，仅短期存在 |

当前活跃顺序以 `RESEARCH_LOG.md` 的 Active Document Index 为准。

## 3. 新增文档规则

新增文档必须满足至少一个条件：

- 填补当前数据闭环的具体缺口；
- 记录一个会影响实现顺序的设计决策；
- 固化一组可验证 DoD；
- 保存最新论文 claim 或重要审稿反馈；
- 为新协作者提供必要冷启动上下文。

不允许新增：

- 与现有文档重复的泛泛计划；
- 没有 DoD 的构想堆叠；
- 只复述聊天内容但不沉淀决策的记录；
- 与当前主线无关的训练架构草图，除非明确标记为 blocked 或 archive。

## 4. 文档职责边界

| 文档类型 | 应放内容 | 不应放内容 |
|---|---|---|
| Claim audit | 论文 claim、当前工件、gap、priority | 长篇实现计划 |
| Status | 现状、缺口、下一步目标 | 详细设计推导 |
| Master plan | 阶段顺序、DoD、进入条件 | 原始讨论记录 |
| Contract | 字段、输入输出、验收标准 | 论文修辞 |
| Usage | 命令、输入结构、错误处理 | 研究叙事 |
| Background | 可读解释、历史讨论 | 当前执行入口 |
| Archive | 历史计划、被替代文档、blocked spec | 活跃 DoD |

## 5. 归档规则

以下情况必须移入 `docs/archive/`：

- 被更新版本取代；
- 与当前执行顺序冲突；
- 只保留历史价值；
- 依赖未满足，不能作为执行入口；
- 空文件或低信息密度草稿。

归档文件也保留编号：

```text
docs/archive/00_README.md
docs/archive/01_...
```

归档后必须：

- 更新 `RESEARCH_LOG.md`；
- 修正活跃文档中的链接；
- 在最终回复中说明归档原因。

## 6. RESEARCH_LOG 更新规则

每次新增、重命名、归档活跃文档，必须更新 `RESEARCH_LOG.md`。

日志格式保持：

```text
### [Timestamp] | Phase: ...

**Key Progress**
- ...

**Data Loop Insight**
- ...

**Pending Criticals**
- ...

**Ref Reference**
- ...
```

`RESEARCH_LOG.md` 只索引活跃文档，不索引所有 archive 文档。archive 只在相关日志条目中引用。

## 7. 命名规则

文件名使用英文 snake_case，必要时保留中文标题在正文中：

```text
03_world_model_supervision_contract.md
04_visual_input_contract.md
```

避免新增中文文件名。历史中文文件可保留在 archive。

## 8. 修改前检查清单

修改 `docs/` 前先检查：

```bash
find docs -maxdepth 2 -type f | sort
rg -n "docs/|\\.md\\)" RESEARCH_LOG.md docs --glob "*.md"
```

修改后至少检查：

```bash
find docs -maxdepth 2 -type f | sort
rg -n "old_filename|missing_filename" RESEARCH_LOG.md docs --glob "*.md"
```

如果只是文档修改，不必跑 pytest；如果改了代码、schema、exporter 或测试配置，必须跑：

```bash
python3 -m pytest
```

## 9. 当前新增文档优先级

当前只允许优先新增以下类别：

1. claim-to-artifact 修正；
2. expert corpus 设计与验收；
3. reward decomposition 契约；
4. real-store split 契约；
5. sampler / prompt builder / QA gate 契约；
6. dataset pilot 状态报告。

其它文档默认先进入草稿或 archive，不作为执行入口。
