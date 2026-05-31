本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

# intent_label Taxonomy Refinement Options

## 0. 决策背景

本轮只设计方案，不实施、不重训、不改数据、不改 5-act 主口径。

依据 `reports/2026-05-20_intent_label_taxonomy_audit.md`：

- 当前 `user_intent` train/eval 中实际出现 7 个 `intent_label`。
- `seek_reassurance` 在 eval 中 F1=0，且 train 有 82 条、eval 有 9 条，不是单纯小样本问题。
- `negotiate_price` 在 eval 中 F1=0，train 有 50 条、eval 有 5 条，裸视觉三帧基本不足以判断“议价”。
- 这两个标签更依赖对话上下文、价格互动或更长时序，不适合作为当前 Stage-1 裸视觉 user_intent 的强监督标签。

当前原始分布：

| intent_label | train | eval |
|---|---:|---:|
| `compare_value_for_money` | 15 | 1 |
| `confirm_choice` | 163 | 14 |
| `explore_options` | 87 | 7 |
| `leave_without_purchase` | 15 | 2 |
| `negotiate_price` | 50 | 5 |
| `request_demonstration` | 81 | 12 |
| `seek_reassurance` | 82 | 9 |
| **Total** | **493** | **50** |

## 1. 方案 A1：删除 `seek_reassurance` + `negotiate_price`

### A1.1 原数据处理方式

推荐处理方式：从当前 `user_intent` 强监督训练和主 eval 中删除这两类样本。

可选处理：

| 处理方式 | 含义 | 影响 | 建议 |
|---|---|---|---|
| 删除 | `seek_reassurance` 和 `negotiate_price` 样本不进入 Stage-1 user_intent 训练/eval | 训练标签更干净，但样本减少 | **推荐作为 A1 主定义** |
| 重打标签 | 人工把每条样本改成 `confirm_choice` / `explore_options` / `compare_value_for_money` 等 | 信息保留最多，但需要人工审 132 条 train + 14 条 eval | 可作为后续 A1.1 |
| 标为 `unknown` | 保留样本，但主分类不要求模型预测具体意图 | 保留数据，但引入新类，论文解释复杂 | 不推荐作为主方案 |

### A1.2 删除后规模

被删除样本：

- train：`seek_reassurance=82` + `negotiate_price=50` = `132`
- eval：`seek_reassurance=9` + `negotiate_price=5` = `14`

删除后：

- train：`493 - 132 = 361`
- eval：`50 - 14 = 36`

### A1.3 删除后预期类别分布

| intent_label | train | train % | eval | eval % |
|---|---:|---:|---:|---:|
| `compare_value_for_money` | 15 | 4.16% | 1 | 2.78% |
| `confirm_choice` | 163 | 45.15% | 14 | 38.89% |
| `explore_options` | 87 | 24.10% | 7 | 19.44% |
| `leave_without_purchase` | 15 | 4.16% | 2 | 5.56% |
| `request_demonstration` | 81 | 22.44% | 12 | 33.33% |
| **Total** | **361** | **100%** | **36** | **100%** |

### A1.4 判断

优点：

- 标签空间最干净，删除了当前视觉模态最不可靠的两个标签。
- 评估口径更诚实：模型只评估三帧图像较可能支持的意图。
- 论文中容易解释为“we exclude visually underdetermined intent labels from the primary visual-intent task”。

缺点：

- 样本减少明显，train 少 26.77%，eval 少 28%。
- 删除 `negotiate_price` 会弱化价格互动能力，删除 `seek_reassurance` 会弱化“顾客不确定性”建模。
- eval 只剩 36 条，统计波动会更大。

适合场景：

- 如果 PI 希望 Stage-1 user_intent 成为一个干净、可辩护的视觉识别任务，A1 最稳。

## 2. 方案 A2：合并到 `explore_options`

### A2.1 合并规则

将：

- `seek_reassurance` -> `explore_options`
- `negotiate_price` -> `explore_options`

理由：

- 二者都可视作“顾客仍在探索/比较，还未形成稳定成交动作”。
- 当前视觉模态很难区分“寻求安心”和“议价”，但可以较合理地判断为“仍在探索/比较”。

### A2.2 语义损失

语义损失：中到高。

具体损失：

- `seek_reassurance` 原本表达“顾客需要降低不确定性或获得确认”，合并后只剩“继续探索”。
- `negotiate_price` 原本表达“顾客对价格让步或优惠有意图”，合并后丢失价格互动细节。
- `explore_options` 会变成一个很宽的桶，包含泛浏览、安心确认、议价探索，类别内部异质性变高。

但它的好处是：不删除样本，并把不可识别的细标签降到更粗粒度的视觉可识别标签。

### A2.3 合并后分布

合并后总量不变：

- train：`493`
- eval：`50`

| intent_label | train | train % | eval | eval % |
|---|---:|---:|---:|---:|
| `compare_value_for_money` | 15 | 3.04% | 1 | 2.00% |
| `confirm_choice` | 163 | 33.06% | 14 | 28.00% |
| `explore_options` | 219 | 44.42% | 21 | 42.00% |
| `leave_without_purchase` | 15 | 3.04% | 2 | 4.00% |
| `request_demonstration` | 81 | 16.43% | 12 | 24.00% |
| **Total** | **493** | **100%** | **50** | **100%** |

### A2.4 判断

优点：

- 不丢样本。
- 标签空间从 7 类降到 5 类，任务更容易。
- 可解释为“coarse visual-intent taxonomy”，更符合三帧裸视觉输入能力。

缺点：

- `explore_options` 占比会膨胀到 train 44.42%、eval 42%，类别严重偏大。
- 合并后 `explore_options` 语义过宽，模型即使预测对，也不一定说明理解了顾客真实心理。
- 论文中需要诚实说明：价格谈判和寻求安心被降为粗粒度探索状态。

适合场景：

- 如果 PI 想保留 493/50 的完整规模，并接受 Stage-1 只做粗粒度 intent，A2 是最省工程量的方案。

## 3. 方案 A3：保留标签，但训练 loss 降权到 0.1

### A3.1 训练权重方案

不改标签，不删样本，只在 `user_intent` 训练时给以下标签较低 loss 权重：

- `seek_reassurance`: `sample_weight = 0.1`
- `negotiate_price`: `sample_weight = 0.1`
- 其他 intent_label: `sample_weight = 1.0`

实现位置建议：

- 在 Stage-1 `user_intent` 数据导出或 collator 层加入 `intent_label_weight`。
- 训练 loss 乘以样本权重。
- eval 仍保留原标签，但报告中分成：
  - full 7-class eval
  - core 5-class eval without low-confidence intent labels

### A3.2 有效训练权重分布

原始 train 仍是 `493` 条，但按 loss 权重折算：

- `seek_reassurance`: 82 条 x 0.1 = 8.2
- `negotiate_price`: 50 条 x 0.1 = 5.0
- 有效总权重：`493 - 132 + 13.2 = 374.2`

| intent_label | raw train | loss weight | effective train weight | effective % |
|---|---:|---:|---:|---:|
| `compare_value_for_money` | 15 | 1.0 | 15.0 | 4.01% |
| `confirm_choice` | 163 | 1.0 | 163.0 | 43.56% |
| `explore_options` | 87 | 1.0 | 87.0 | 23.25% |
| `leave_without_purchase` | 15 | 1.0 | 15.0 | 4.01% |
| `negotiate_price` | 50 | 0.1 | 5.0 | 1.34% |
| `request_demonstration` | 81 | 1.0 | 81.0 | 21.65% |
| `seek_reassurance` | 82 | 0.1 | 8.2 | 2.19% |
| **Total** | **493** | - | **374.2** | **100%** |

Eval 分布不变：

| intent_label | eval |
|---|---:|
| `compare_value_for_money` | 1 |
| `confirm_choice` | 14 |
| `explore_options` | 7 |
| `leave_without_purchase` | 2 |
| `negotiate_price` | 5 |
| `request_demonstration` | 12 |
| `seek_reassurance` | 9 |
| **Total** | **50** |

### A3.3 优缺点

优点：

- 保留原标签结构，论文容易写：这些类别不是删除，而是标记为 visually underdetermined / weak labels。
- 不破坏数据规模。
- 避免两个低可信标签强行污染主要可视觉识别类别。
- 后续如果加入对话上下文或更长 trajectory，可以把权重恢复。

缺点：

- 模型可能仍然学不会这两类。
- full 7-class macro F1 仍可能被这两类拖低。
- 训练实现需要支持 sample-level loss weight，工程上比 A1/A2 多一点。
- 如果论文评估只报 full 7-class，结果可能仍不好看；必须同时报 core 5-class 或 low-confidence label analysis。

适合场景：

- 如果 PI 希望最大限度保留 taxonomy，同时承认这两个标签在当前视觉模态下是弱监督，A3 最平衡。

## 4. 三方案对比

| 方案 | 样本规模 | 标签数 | 主要优点 | 主要风险 | 我的建议 |
|---|---:|---:|---|---|---|
| A1 删除 | train 361 / eval 36 | 5 | 最干净，视觉任务最可辩护 | 样本减少，丢掉不确定性和议价语义 | 适合追求干净评估 |
| A2 合并到 `explore_options` | train 493 / eval 50 | 5 | 不丢样本，任务更容易 | `explore_options` 过宽且占比膨胀 | 可作为快速工程方案 |
| A3 降权到 0.1 | train 493 / eval 50 | 7 | 保留 taxonomy，降低污染 | 仍可能学不会，需加权训练支持 | **推荐先选** |

## 5. 推荐决策

我建议 PI 优先选择 A3。

原因：

1. A3 不破坏现有数据，也不掩盖 taxonomy 中真实存在的困难标签。
2. A3 最符合论文叙事：当前视觉-only user-intent task 对部分心理意图存在模态边界，因此用低权重保留、单独分析。
3. A3 后续可退回 A1 或 A2：如果实验后仍污染训练，再删除或合并；但如果一开始删除，恢复语义成本更高。

如果 PI 更看重主表数字和清洁评估，则选 A1。

如果 PI 更看重不丢样本和快速推进，则选 A2。

## 6. 本轮不做

- 不重训。
- 不实施 taxonomy refinement。
- 不改任何 JSONL 数据。
- 不改 5-act 主口径。
- 不把 `seek_reassurance` 和 action-level `Reassure` 混为一谈。
