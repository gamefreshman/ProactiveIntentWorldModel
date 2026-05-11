# 智能导购 Agent 行为空间分层定义（v0 草案）

> 用途：状态机 / Action 空间设计的会议讨论起点
> 状态：v0，故意做窄，欢迎挑战
> 范围：实体智能导购终端的对客行为决策与执行

---

## 1. 背景与动机

当前 action 列表（A0–A6）把"agent 的决策空间"和"终端的行为能力库"混在同一层，引发三个具体问题：

1. **粒度不齐**：A3（compare_options）是 A2（offer_information）的特例；A5（suggest_next_step）和 A6（push_recommendation）只是力度差异，不是不同动作
2. **扩展冲突**：每新增一个终端能力（屏幕新模式、新语音风格、新肢体动作），都要争论"这是新动作还是变种"，没有客观判据
3. **状态机膨胀**：动作数随能力线性增长，policy 学习成本和评估难度同步上升

本文提议把行为空间拆成三层：上层（agent 决策）、中层（动作 → 表现的映射）、下层（终端硬件能力）。这套分层在对话系统与会话推荐文献里有明确支撑（见 §9）。

---

## 2. 总体架构

```
┌──────────────────────────────────────────────────────┐
│ 上层：Dialogue Act（policy 的决策空间）               │
│   6 个抽象动作 · 多维度可共现 · 状态机在此运转         │
└──────────────────────────────────────────────────────┘
                       ↓ (act, params)
┌──────────────────────────────────────────────────────┐
│ 中层：Realization（动作 → 模板的查表翻译）            │
│   规则驱动 · 根据 dialogue state 选具体表现模板        │
└──────────────────────────────────────────────────────┘
                       ↓ (text, screen, voice, motion)
┌──────────────────────────────────────────────────────┐
│ 下层：终端能力（屏幕 / 语音 / 灯光 / 实体动作）        │
│   硬件可枚举 · policy 不可见                          │
└──────────────────────────────────────────────────────┘
```

**核心原则**：每层只负责一件事，跨层不可见。

- 上层不知道硬件长什么样——它只输出"我要推荐这个商品，用温和的力度"
- 下层不知道上层在想什么——它只接收"播放温和语音 + 屏幕高亮 SKU + 4 秒"
- 中层是唯一的翻译者，决定"温和力度的推荐"在当前上下文里具体长什么样

---

## 3. 上层：6 个 Dialogue Acts

| # | 动作 | 维度 | 定义 | 主要参数（v0） |
|---|---|---|---|---|
| 1 | **Greet** | Social Obligations | 开场或收尾的社交礼节 | `phase ∈ {open, close}` |
| 2 | **Elicit** | Task | 主动获取顾客信息 | `openness ∈ {open, closed}`, `slot` |
| 3 | **Inform** | Task | 提供信息（描述/比较/参数/价格） | `content_type`, `depth ∈ {brief, detailed}` |
| 4 | **Recommend** | Task | 提议具体商品或下一步动作 | `target ∈ {item, action}`, `pressure ∈ {soft, firm}` |
| 5 | **Reassure** | Allo-Feedback | 情感安抚 / 降低决策压力 | `focus ∈ {time, decision, alternatives}` |
| 6 | **Hold** | Turn Management | 让出话轮 / 低干扰观察 | `mode ∈ {silent, ambient}` |

**与原 A0–A6 的对应**：

| 原动作 | 新动作 | 说明 |
|---|---|---|
| A0 stay_silent | `Hold(mode=silent)` | 维度从 Task 移到 Turn Management |
| A1 ask_open_question | `Elicit(openness=open)` | 闭式提问也用同一动作，参数区分 |
| A2 offer_information | `Inform(content_type=*)` | 含产品描述、参数、价格等 |
| A3 compare_options | `Inform(content_type=comparison)` | 不再是独立动作，而是 Inform 的特例 |
| A4 provide_reassurance | `Reassure` | 维度移到 Allo-Feedback |
| A5 suggest_next_step | `Recommend(pressure=soft)` | 与 A6 合并，pressure 区分 |
| A6 push_recommendation | `Recommend(pressure=firm)` | 与 A5 合并，pressure 区分 |

**共现规则**：

- Task 维度（Elicit / Inform / Recommend）每轮**最多选一个**
- Greet / Reassure / Hold 不在 Task 维度，**可与 Task 动作共现**
- 例："您慢慢看，需要时叫我" = `Hold(silent)` + `Reassure(focus=time)`

---

## 4. 中层：Realization 接口（详解）

### 4.1 这一层是干什么的

中层是**确定性的翻译层**，不做决策。它接收上层输出的抽象动作，根据当前对话状态查表选模板，输出一个"具体怎么演"的指令包给下层。

类比：

| 层 | 角色 | 工作 |
|---|---|---|
| 上层 | **导演** | 决定这一幕"要做什么"（推荐？提问？安抚？） |
| 中层 | **编剧 / 分镜** | 根据现场情况把"做什么"翻成"怎么演" |
| 下层 | **演员 / 舞美** | 按照分镜把动作真的执行出来 |

**中层为什么必须存在**：因为同一个抽象动作（比如"温和地推荐一款商品"）在不同场景下应该长得不一样——客户刚摸过某件商品 vs 客户刚拒绝过一次推荐 vs 客户犹豫但还没动手——三种情况下"温和推荐"的台词、屏幕、语调都该不同。如果不要中层，要么 policy 自己学这些细节（动作空间爆炸），要么模板写死（无法适配上下文）。中层就是吸收这种适配复杂度的地方。

**关键性质**：中层的"智能"是**查表 + 规则**，不是 ML。它对每个 `(act, params)` 组合维护一个模板候选集，选哪个模板由 dialogue state 触发的规则决定。便于调试、审查、热更新。

### 4.2 输入与输出

**输入**：

```
1) (act, params)            ← 上层 policy 的输出
2) dialogue_state           ← 当前对话状态，至少包含：
     - candidates           候选商品列表（count, attributes）
     - signals              客户行为信号（停留时长、触摸/试用、注视点）
     - history              对话历史（上一轮 act、本对话已出现过的 act 序列）
     - profile (optional)   客户画像（偏好、复购、会员等级等）
```

**输出**：

```
Output := {
  surface_text:  string,           # 实际要说的话
  screen:        ScreenAction,     # 屏幕显示什么
  voice_style:   string,           # 语音风格（neutral/warm/energetic/calm）
  motion:        MotionCue | None, # 实体动作（终端支持时）
  duration_ms:   int               # 这个动作占多长时间
}
```

### 4.3 选择逻辑

每个 `(act, params)` 组合下注册多个**模板（template）**。每个模板带一个**适用条件（precondition）**，描述"在什么 state 下这个模板可用"。

```
步骤 1: 列出所有匹配 (act, params) 的模板
步骤 2: 过滤出 precondition 在当前 state 下成立的模板
步骤 3: 多个模板时，按优先级排序（v0 用静态优先级），取第一个
步骤 4: 用 state 中的变量填充模板，生成 Output
```

### 4.4 一个完整的例子

**假设 policy 输出**：

```
act = Recommend
params = { target: item, pressure: soft }
```

**当前 dialogue state**：

```
candidates    = [SKU_A, SKU_B]
dwell_time    = 45s
last_touched  = SKU_A
prev_acts     = [Elicit, Inform]
```

**中层查 `Recommend(target=item, pressure=soft)` 下注册的模板**：

| 模板 ID | precondition | 优先级 | 表现描述 |
|---|---|---|---|
| `gentle_suggest_touched` | `last_touched != None` | 10 | 围绕客户摸过的那件做温和推荐 |
| `gentle_suggest_dwelled` | `dwell_time > 30s` | 5 | 围绕停留区域做推荐 |
| `gentle_suggest_default` | `(默认兜底)` | 0 | 推荐第一个候选 |

`gentle_suggest_touched` 和 `gentle_suggest_dwelled` 的 precondition 都成立；按优先级取前者。

**中层产出**：

```json
{
  "surface_text": "您刚才看的这款挺适合您，要不要再仔细看看？",
  "screen":       { "action": "highlight", "target": "SKU_A" },
  "voice_style":  "warm",
  "motion":       null,
  "duration_ms":  4000
}
```

下层硬件按这个指令包执行。

### 4.5 模板登记规范

每个模板是一个 YAML 条目：

```yaml
template_id: gentle_suggest_touched
act: Recommend
params:
  target: item
  pressure: soft
precondition: "state.last_touched != None"
priority: 10
output:
  surface_text: "您刚才看的这款挺适合您，要不要再仔细看看？"
  screen:
    action: highlight
    target: "{state.last_touched}"
  voice_style: warm
  duration_ms: 4000
```

**关键约束**：

- 每个 `(act, params)` 组合**至少要有一个默认兜底模板**（precondition 恒真），保证不会出现"无模板可选"
- 模板**不能改变 act 的语义**（不能在 Recommend 模板里写实际劝退的台词）
- 模板的增删改**不影响 policy**；policy 训练数据里只有 `(act, params)` 序列，跟具体台词无关
- 模板版本化管理，支持 A/B 测试和灰度

---

## 5. 下层：终端能力（占位）

由硬件 / 终端团队定义。本层负责把中层的 Output 指令包真正执行出来：TTS 合成、屏幕渲染、灯光控制、实体动作驱动。

接口约定（v0）：接收中层 Output 的 JSON，返回执行成功/失败 + 实际耗时。具体能力清单留给终端团队补充。

---

## 6. 设计规则（用于会上裁决新增需求）

1. **Policy 只看上层** —— 状态机的转移、reward、训练样本，全部基于 6 个 act 与其参数，不感知 realization
2. **Realization 不能发明新 act** —— 任何新增终端能力，要么进入已有 act 的参数空间，要么作为新模板挂到已有 `(act, params)` 下；都不是新动作
3. **参数优于增项** —— 力度差异、详略差异、开放程度差异一律用参数，不开新 act。判断标准：如果两个候选动作只在程度上不同、目的相同，它们是同一个 act 加参数
4. **多维度共现走加法** —— 一轮可以输出 ≤1 个 Task act + 任意非 Task act 的组合
5. **MVP 维度收敛** —— 从 ISO 24617-2 的 9 维度里只取 Task / Social Obligations / Allo-Feedback / Turn Management 四维；其余五维（Time Management / Discourse Structuring / Auto-Feedback / Own Communication Management / Partner Communication Management）v0 不引入，需要时再加

---

## 7. 端到端示例

把上中下三层一次跑通。

**场景**：客户在童装区驻足 30 秒，触摸了一件外套，之前 agent 已经打过招呼。

**上层 policy** 看到 state（`dwell_time=30s, last_touched=外套A, prev_acts=[Greet]`），决定：

```
act = Inform
params = { content_type: product_attributes, depth: brief }
```

**中层** 查表，匹配模板 `inform_brief_touched`（precondition: `last_touched != None`）：

```yaml
output:
  surface_text: "这件{state.last_touched.name}是{state.last_touched.material}的，{state.last_touched.season}款。"
  screen:
    action: show_detail
    target: "{state.last_touched.id}"
  voice_style: neutral
  duration_ms: 3500
```

填充变量后产出：

```json
{
  "surface_text": "这件简约外套是纯棉的，春秋款。",
  "screen":       { "action": "show_detail", "target": "SKU_外套A" },
  "voice_style":  "neutral",
  "motion":       null,
  "duration_ms":  3500
}
```

**下层** 接收指令：屏幕切到 SKU_外套A 的详情页，TTS 用 neutral 风格播放文本，3.5 秒后回到等待状态。

**整个过程中**：policy 不知道屏幕长什么样、TTS 用了什么模型；硬件不知道为什么是这句话；只有中层知道这个上下文该怎么演。任一层独立迭代，不影响其他层。

---

## 8. 待确认（拿到会上讨论）

| # | 问题 | v0 暂定 |
|---|---|---|
| Q1 | `Recommend` 的 `pressure` 是二元（soft/firm）还是三档（soft/medium/firm）？ | 二元 |
| Q2 | 是否允许同一轮出现两个 Task act？（"这款 ¥999，看预算合不合适？" = Inform+Elicit） | 禁止，强制拆成两轮 |
| Q3 | `Greet` 的 close 是否单独拆成 `Farewell`？ | 合并以保持 6 个动作 |
| Q4 | 是否在 act 层加 `Acknowledge`（"嗯/好的/明白了"）？ | 暂不加，由 NLG 层自动处理 |

---

## 9. 参考依据

- **ISO 24617-2:2020** *Language resource management — Semantic annotation framework — Part 2: Dialogue acts (DiAML)*
   9 维度对话动作国际标准；本设计采用其多维度框架并选取 4 维子集
- **Henderson et al. (2013)** Dialogue State Tracking Challenge
   任务型对话 agent 紧凑动作集（inform/request/confirm/affirm/negate）参考
- **Azzopardi et al. (2024)** *A Conceptual Framework for Conversational Search and Recommendation*
   会话推荐高层动作（inquire / reveal / traverse / suggest / explain）参考
- **Kim et al. (2024)** *Towards Personalized Conversational Sales Agents (CSALES)*, Yonsei
   LLM 时代会话销售 agent 的 preference elicitation + recommendation + persuasion 三段式
- **Fang et al. (2024)** *Multi-Agent Conversational Recommender System (MACRS)*, arXiv:2402.01135
   显式两层架构：act planning 与 response generation 解耦的工程参考
- **McFarland, Challagalla & Shervani (2006)** *Influence Tactics for Effective Adaptive Selling*, *Journal of Marketing*, 70(4)
   销售影响策略 6 分类（SITs），用于 Recommend 与 Reassure 的参数化依据
- **Bush, Bush, Ortinau & Hair (1990)** *Developing a Behavior-Based Scale to Assess Retail Salesperson Performance*, *Journal of Retailing*, 66(1)
   零售导购行为量表，用于本地化场景适配

---

*v0 修订记录：初版。下次修订建议补充：状态机转移图（什么 state 下哪些 act 合法）；模板优先级冲突的解决策略；客户画像未知时的降级路径。*
