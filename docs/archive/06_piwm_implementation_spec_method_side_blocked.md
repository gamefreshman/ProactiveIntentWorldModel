# PIWM Implementation Spec — Method-side Code

> **目标读者**：Codex / 实现者。
> **写作目的**：把论文 §3（Method v2）的形式化对象翻译成可直接实现的代码契约。
> **配套**：论文 Method v2 (`method_section_v2.tex`)、数据管线 spec (`data_pipeline_spec.md`)。
> **不在本文档范围**：训练数据生成（见 data pipeline spec）、模型选型决策（见 §0.3）、评测指标实现（独立文档）。

---

## 0. 全局约定

### 0.1 模块布局

```
piwm_train/
├── __init__.py
├── prompts.py              # 训练时用的三个 role prompt 模板
├── targets.py              # 三个 role 的 target string 构造
├── sft.py                  # Phase 1: joint perception + deliberation SFT
├── dpo.py                  # Phase 2: DPO on policy_preference.jsonl
├── data_collator.py        # 把 jsonl 转成 batch
├── config.py               # 超参数、tag 字符串、字段名常量
└── tests/
    ├── test_prompts.py
    ├── test_targets.py
    └── test_data_collator.py

piwm_infer/
├── __init__.py
├── prompts.py              # 推理时用的三个 role prompt 模板（与 train 共用 base）
├── decision_loop.py        # Algorithm 1 的实现
├── parsers.py              # 解析 model output 的结构化字段
├── config.py               # 推理超参数（τ_silence、采样参数等）
└── tests/
    ├── test_parsers.py
    ├── test_decision_loop.py
    └── fixtures/
        └── mock_vlm.py     # 用于不依赖真实模型的端到端测试
```

依赖：`transformers>=4.45`, `trl>=0.11`（DPO），`pydantic>=2`，`torch>=2.3`。**不要引入 PEFT 之外的额外微调库**。

### 0.2 与 data pipeline 的契约边界

`piwm_train` 只读这四个文件：

```
data/piwm_dataset/
├── state_inference.jsonl            # → Perception SFT
├── transition_modeling.jsonl        # → Deliberation SFT
├── policy_preference.jsonl          # → DPO
└── _stats.json                      # 仅用于日志，不参与训练
```

字段名严格对齐 data pipeline spec §5.2–5.4。**`piwm_train` 不允许再次定义这些字段名常量**——通过 `from piwm_data.schemas import ...` 导入。

### 0.3 模型选型（写死，避免 Codex 自由发挥）

- 主模型：`Qwen2.5-VL-7B-Instruct`
- 备选：`Qwen2.5-VL-3B-Instruct`（消融用，资源紧张时）
- 不要尝试 LLaVA、InternVL 等其它族。原因：Qwen2.5-VL 的 chat template 对 image+text 多轮交错支持稳定；trl 的 DPOTrainer 对它的 tokenizer 已有 known-good 配置
- LoRA：rank=16, alpha=32, target=`["q_proj", "k_proj", "v_proj", "o_proj"]`
- 不冻结 vision encoder（让多模态 grounding 能在 Phase 1 跟着调整）

---

## 1. 字段 Tag 全表（必须严格一致）

### 1.1 Perception output tag

```
<stage>...</stage>
<belief>...</belief>
<desire>...</desire>
<intention>...</intention>
<score>...</score>
<cands>A1_silent_observe, A2_offer_value_comparison, ...</cands>
```

字符串 literal 全部小写、tag 之间空格 `\n`、`<cands>` 内用 `, ` 分隔。

### 1.2 Deliberation output tag

```
<next_stage>...</next_stage>
<next_belief>...</next_belief>
<next_desire>...</next_desire>
<next_intention>...</next_intention>
<risk>low|medium|high</risk>
<benefit>low|medium|high</benefit>
<reward>0.73</reward>
```

`<reward>` 取浮点字面量、保留两位小数、范围 `[-1.00, 1.00]`。**不允许**输出 `0.730000` 这种格式。

### 1.3 Action output tag

```
<rationale>...</rationale>
<chosen>A2_offer_value_comparison</chosen>
```

`<chosen>` 必须是 candidate set 中字面相同的字符串。

### 1.4 Tag 字符串常量定义

`piwm_train/config.py`：

```python
# Perception
TAG_STAGE_OPEN = "<stage>"
TAG_STAGE_CLOSE = "</stage>"
TAG_BELIEF_OPEN = "<belief>"
TAG_BELIEF_CLOSE = "</belief>"
# ... 完整列表见 piwm_train/config.py 实现
TAG_REWARD_OPEN = "<reward>"
TAG_REWARD_CLOSE = "</reward>"
TAG_CHOSEN_OPEN = "<chosen>"
TAG_CHOSEN_CLOSE = "</chosen>"

# 浮点格式
REWARD_FORMAT = "{:.2f}"            # e.g. f"{0.7341:.2f}" → "0.73"
```

**严禁**在 prompts.py、targets.py、parsers.py 里写裸 tag 字符串。一律 `from .config import TAG_*`。

---

## 2. Prompt 模板（训练 & 推理共用）

### 2.1 Perception prompt

```python
PERCEPTION_USER_TEMPLATE = """\
You are observing a customer in a retail store. Below are {n_frames} frames \
sampled from a streaming camera, in chronological order.

{image_placeholders}

History summary (states inferred at earlier decision points; may be empty):
{history_summary}

Identify the customer's current state and decide whether the situation \
warrants intervention.

Output the following fields, in this exact order, each on its own line:
{tag_format_instructions}

- <stage> must be one of: attention, interest, desire, action.
- <score> must be an integer 1-5, where 1 means "do not disturb" and 5 means "intervene immediately".
- <cands> must be a comma-separated list of candidate strategy labels appropriate for the inferred stage.
- All textual spans (<belief>, <desire>, <intention>) must be a single short clause in English.
"""
```

`{image_placeholders}` 是 Qwen2.5-VL 的 `<|image_pad|>` token 占位，由 `Qwen2VLProcessor` 自动展开。`{n_frames}` 主实验为 3。

### 2.2 Deliberation prompt

```python
DELIBERATION_USER_TEMPLATE = """\
You are observing a customer in a retail store. Below are {n_frames} frames \
sampled from a streaming camera, in chronological order.

{image_placeholders}

The customer's current state is:
- stage: {sigma}
- belief: {belief}
- desire: {desire}
- intention: {intention}

Consider one candidate intervention: {action}

Predict how this candidate intervention will change the customer's state in \
the next decision step. Output the following fields, in this exact order, \
each on its own line:
{tag_format_instructions}

- <next_stage> must be one of: attention, interest, desire, action.
- <risk> and <benefit> must each be one of: low, medium, high.
- <reward> must be a number in [-1.00, 1.00] with two decimal places.
- All textual spans must be a single short clause in English.
"""
```

**关键**：Deliberation prompt 一次只评估**一个** action。candidate set 是在调用方循环里展开的，不放进 prompt。

### 2.3 Action prompt

```python
ACTION_USER_TEMPLATE = """\
You are observing a customer in a retail store. Below are {n_frames} frames \
sampled from a streaming camera, in chronological order.

{image_placeholders}

The customer's current state is:
- stage: {sigma}
- belief: {belief}
- desire: {desire}
- intention: {intention}

You have evaluated the following candidate interventions:

{candidate_block}

Choose the best intervention and explain your reasoning briefly.

Output the following fields, in this exact order:
{tag_format_instructions}

- <chosen> must be one of the candidate labels listed above, exact string match.
- <rationale> should reference the predicted next states when justifying the choice.
"""
```

`{candidate_block}` 是个表格化字符串，每个候选一行：

```
- A2_offer_value_comparison: predicted_next_stage=interest, risk=low, benefit=high, reward=0.73
- A1_silent_observe: predicted_next_stage=interest, risk=low, benefit=medium, reward=0.30
- A4_open_with_question: predicted_next_stage=interest, risk=low, benefit=high, reward=0.65
```

构造函数 `format_candidate_block(per_candidate_outputs: dict[str, dict]) -> str` 在 `piwm_infer/prompts.py` 中实现。**严禁**在调用点拼字符串。

### 2.4 三个 prompt 的 system prefix

所有三个 role 共用同一个 system prompt：

```python
PIWM_SYSTEM_PROMPT = (
    "You are a multimodal sales-guidance agent trained on retail pedagogy. "
    "You observe customers in physical retail stores via a streaming camera "
    "and decide whether and how to intervene. Always output your reasoning "
    "in the structured tag format requested by the user prompt. Do not output "
    "free-form prose outside the requested tags."
)
```

---

## 3. Target 构造

### 3.1 Perception target

```python
def build_perception_target(record: dict) -> str:
    """从 state_inference.jsonl 的一条记录构造 target string。

    record["output"] 字段:
      current_state: str       # = sigma
      intent: str              # 旧字段，弃用（pipeline 已替换为 bdi）
      bdi: { belief, desire, intention }
      proactive_score: int
      candidate_actions: list[str]
      best_action: str         # 不进入 perception target
      rationale: str | None    # 不进入 perception target

    返回的字符串末尾不加 EOS（由 tokenizer 处理）。
    """
    out = record["output"]
    bdi = out["bdi"]
    return (
        f"{TAG_STAGE_OPEN}{out['current_state']}{TAG_STAGE_CLOSE}\n"
        f"{TAG_BELIEF_OPEN}{bdi['belief']}{TAG_BELIEF_CLOSE}\n"
        f"{TAG_DESIRE_OPEN}{bdi['desire']}{TAG_DESIRE_CLOSE}\n"
        f"{TAG_INTENTION_OPEN}{bdi['intention']}{TAG_INTENTION_CLOSE}\n"
        f"{TAG_SCORE_OPEN}{out['proactive_score']}{TAG_SCORE_CLOSE}\n"
        f"{TAG_CANDS_OPEN}{', '.join(out['candidate_actions'])}{TAG_CANDS_CLOSE}"
    )
```

### 3.2 Deliberation target

```python
def build_deliberation_target(record: dict) -> str:
    """从 transition_modeling.jsonl 的一条记录构造 target string。

    record["output"] 字段:
      next_stage: str
      next_bdi: { belief, desire, intention }     # 注意是 next_bdi，不是 bdi
      risk: "low" | "medium" | "high"
      benefit: "low" | "medium" | "high"
      reward: float
      worth_doing: bool                            # 不进入 target
      rationale: str | None                        # 不进入 target
    """
    out = record["output"]
    nbdi = out["next_bdi"]
    return (
        f"{TAG_NEXT_STAGE_OPEN}{out['next_stage']}{TAG_NEXT_STAGE_CLOSE}\n"
        f"{TAG_NEXT_BELIEF_OPEN}{nbdi['belief']}{TAG_NEXT_BELIEF_CLOSE}\n"
        f"{TAG_NEXT_DESIRE_OPEN}{nbdi['desire']}{TAG_NEXT_DESIRE_CLOSE}\n"
        f"{TAG_NEXT_INTENTION_OPEN}{nbdi['intention']}{TAG_NEXT_INTENTION_CLOSE}\n"
        f"{TAG_RISK_OPEN}{out['risk']}{TAG_RISK_CLOSE}\n"
        f"{TAG_BENEFIT_OPEN}{out['benefit']}{TAG_BENEFIT_CLOSE}\n"
        f"{TAG_REWARD_OPEN}{REWARD_FORMAT.format(out['reward'])}{TAG_REWARD_CLOSE}"
    )
```

### 3.3 Action chosen / rejected target

DPO 用的是两条 string：

```python
def build_action_target(record: dict, side: Literal["chosen", "rejected"]) -> str:
    """policy_preference.jsonl 一条记录构造一对 target。

    side="chosen": 用 chosen_json
    side="rejected": 用 rejected_json
    """
    block = record[f"{side}_json"]
    return (
        f"{TAG_RATIONALE_OPEN}{block['rationale']}{TAG_RATIONALE_CLOSE}\n"
        f"{TAG_CHOSEN_OPEN}{block['action']}{TAG_CHOSEN_CLOSE}"
    )
```

---

## 4. 训练侧 (Phase 1: SFT)

### 4.1 数据 collator 行为

`PIWMSFTCollator` 接受混合两个 jsonl 的 batch：

- 50% 来自 `state_inference.jsonl` → 用 PerceptionPrompt + perception target
- 50% 来自 `transition_modeling.jsonl` → 用 DeliberationPrompt + deliberation target

实现：构造一个统一 IterableDataset，每个 epoch 按 50/50 比例 round-robin 抽样。

```python
class PIWMSFTCollator:
    def __init__(
        self,
        processor: Qwen2VLProcessor,
        max_length: int = 2048,
        perception_weight: float = 1.0,    # λ_p
        deliberation_weight: float = 1.0,  # λ_d
    ): ...

    def __call__(self, batch: list[dict]) -> dict[str, Tensor]:
        """返回 {input_ids, attention_mask, labels, pixel_values, image_grid_thw}.

        labels 在 user prompt 部分填 -100（不参与 loss），只在 assistant target
        部分保留 token id。这是标准 SFT mask 做法。

        样本的损失权重通过返回字典里的 "sample_weights" 字段携带，由 trainer
        在 loss 聚合时使用。perception 样本权重 = λ_p，deliberation = λ_d。
        """
```

### 4.2 字段级损失加权（论文 §3.2 提到）

论文里说 `<stage>` 和 `<intention>` 字段加权 2x。实现方式：

不在 collator 里做 token 级权重（会破坏 cross-entropy 数学性），改为**在 perception target 里把这两个字段重复一次**作为 SFT-time data augmentation。

具体：

```python
# 在 perception target 后追加：
target += f"\n[recap]\n{TAG_STAGE_OPEN}{sigma}{TAG_STAGE_CLOSE}\n{TAG_INTENTION_OPEN}{intention}{TAG_INTENTION_CLOSE}"
```

这是 spec 强制要求，**不要尝试**改成 sample weight or per-token weight 的 fancy 实现。Recap 形式简单、可测、可被 ablation 关掉。

### 4.3 训练超参数（写死）

```python
SFT_CONFIG = dict(
    model_name="Qwen/Qwen2.5-VL-7B-Instruct",
    learning_rate=1e-5,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    num_train_epochs=2,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,           # effective batch = 16
    gradient_checkpointing=True,
    bf16=True,
    max_grad_norm=1.0,
    save_steps=500,
    logging_steps=10,
    lora_r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    lora_target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)
```

### 4.4 训练入口

```bash
python -m piwm_train.sft \
  --data-dir data/piwm_dataset \
  --output-dir checkpoints/piwm_sft \
  --config-overrides "num_train_epochs=2,learning_rate=1e-5"
```

**必须**在每个 save step 验证：从 checkpoint 加载、跑一个 mock prompt、检查输出包含所有必需 tag。

---

## 5. 训练侧 (Phase 2: DPO)

### 5.1 输入

`policy_preference.jsonl`，字段定义见 data pipeline spec §5.4。Phase 2 的 reference model 是 Phase 1 的产出 checkpoint。

### 5.2 实现框架

直接用 `trl.DPOTrainer`：

```python
from trl import DPOTrainer, DPOConfig

dpo_config = DPOConfig(
    beta=0.1,                               # KL strength
    loss_type="sigmoid",                    # 标准 DPO
    learning_rate=5e-6,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    bf16=True,
    max_length=2048,
    max_prompt_length=1536,
)

# 关键：reference model 是 Phase 1 的 LoRA-merged 模型
ref_model = load_phase1_merged()
policy_model = load_phase1_for_continued_training()

trainer = DPOTrainer(
    model=policy_model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=preference_dataset,
    tokenizer=processor.tokenizer,
)
trainer.train()
```

### 5.3 数据格式 adapter

`trl.DPOTrainer` 要 `{prompt, chosen, rejected}` 三字段。从 jsonl 转换：

```python
def to_dpo_record(record: dict, processor) -> dict:
    """policy_preference.jsonl 一条 → DPO 训练记录。"""
    prompt = build_action_prompt_for_training(
        frames=record["meta"]["frames"],
        state=record["meta"].get("state_summary"),    # data pipeline 需要补这个字段
        candidates_with_predictions=record["meta"]["candidate_block"],
    )
    chosen = build_action_target(record, side="chosen")
    rejected = build_action_target(record, side="rejected")
    return {"prompt": prompt, "chosen": chosen, "rejected": rejected}
```

> ⚠️ **数据契约依赖**：当前 `policy_preference.jsonl` 的 `meta` 字段需要补两项：`state_summary`（来自父 main schema 的 `latent_state` + `bdi`）和 `candidate_block`（每个 candidate 的 (next_state, reward) 摘要）。这是 data pipeline 必须先补齐的字段，否则 Phase 2 跑不起来。**先开 issue 给 data pipeline，再开始实现 Phase 2**。

---

## 6. 推理侧（Algorithm 1 实现）

### 6.1 主入口

```python
class PIWMAgent:
    def __init__(
        self,
        model_path: str,
        tau_silence: int = 1,
        rollout_depth: int = 1,
        device: str = "cuda",
    ): ...

    @torch.no_grad()
    def decide(
        self,
        frames: list[Image.Image],
        history_summary: str = "",
    ) -> AgentDecision:
        """对单个时刻做一次决策。

        返回:
            AgentDecision(
                chosen_action: str,
                inferred_state: CustomerState,
                proactive_score: int,
                per_candidate_predictions: dict[str, ActionPrediction] | None,
                rationale: str | None,
                latency_breakdown: dict[str, float],
            )
        """
```

### 6.2 完整决策循环

严格按论文 §3.3 / Algorithm 1：

```python
def decide(self, frames, history_summary=""):
    t0 = time.time()

    # Step 1: Perception
    perc_prompt = build_perception_prompt(frames, history_summary)
    perc_raw = self._generate(perc_prompt, max_new_tokens=256)
    state, score, candidates = parse_perception_output(perc_raw)
    t1 = time.time()

    # Early abort
    if score <= self.tau_silence:
        return AgentDecision(
            chosen_action="A1_silent_observe",
            inferred_state=state,
            proactive_score=score,
            per_candidate_predictions=None,
            rationale="proactive score below threshold; abstain",
            latency_breakdown={"perception_s": t1-t0, "deliberation_s": 0, "action_s": 0},
        )

    # Step 2: Deliberation, one call per candidate
    per_cand_preds = {}
    for a in candidates:
        delib_prompt = build_deliberation_prompt(frames, state, a)
        delib_raw = self._generate(delib_prompt, max_new_tokens=192)
        per_cand_preds[a] = parse_deliberation_output(delib_raw)
    t2 = time.time()

    # Step 3: Action
    act_prompt = build_action_prompt(frames, state, per_cand_preds)
    act_raw = self._generate(act_prompt, max_new_tokens=128)
    chosen, rationale = parse_action_output(act_raw, valid_actions=set(candidates))
    t3 = time.time()

    return AgentDecision(
        chosen_action=chosen,
        inferred_state=state,
        proactive_score=score,
        per_candidate_predictions=per_cand_preds,
        rationale=rationale,
        latency_breakdown={
            "perception_s": t1 - t0,
            "deliberation_s": t2 - t1,
            "action_s": t3 - t2,
        },
    )
```

### 6.3 Parsers 的健壮性要求

`parse_perception_output(raw: str) -> tuple[CustomerState, int, list[str]]`：

- 用正则提取每个 tag 之间的内容
- 缺 tag → 返回 `ParseError`，调用方决定 fallback
- `<stage>` 内容不在 `{attention, interest, desire, action}` → `ParseError`
- `<score>` 不能 int 化或不在 1..5 → `ParseError`
- `<cands>` 解析后为空 → `ParseError`
- BDI 三字段有任一为空字符串 → `ParseError`

**Codex 注意**：不要做 fuzzy match。出错就 raise。Algorithm 1 上层捕获 `ParseError` 后 fallback 到 `A6_acknowledge_and_wait`（最低风险动作）。

### 6.4 多步 rollout (`rollout_depth > 1`)

```python
# 在 Step 2 内部，对每个 a 链式调用 H 次：
def deliberate_rollout(self, frames, state, action, depth):
    """链式调用 deliberation H 次，第二次起的输入 state 是上一次的 next state。"""
    cumulative_reward = 0.0
    discount = 1.0
    cur_state = state
    for h in range(depth):
        prompt = build_deliberation_prompt(frames, cur_state, action)
        pred = parse_deliberation_output(self._generate(prompt, ...))
        cumulative_reward += discount * pred.reward
        discount *= 0.9                # γ=0.9, 写死
        cur_state = pred.next_state
        # 第二步起，action 由 candidates of cur_state 中最高 reward 候选填补
        # 这是 closed-loop self-rollout，主实验不开
    return RolloutResult(final_state=cur_state, cumulative_reward=cumulative_reward)
```

**主实验 H=1，本函数仅在 ablation 跑**。

### 6.5 推理超参数

```python
INFERENCE_CONFIG = dict(
    do_sample=False,            # 主实验贪心解码
    temperature=0.0,
    max_new_tokens_perception=256,
    max_new_tokens_deliberation=192,
    max_new_tokens_action=128,
    tau_silence=1,
    rollout_depth=1,
    discount_gamma=0.9,         # 仅 H>1 用
    fallback_action_on_parse_error="A6_acknowledge_and_wait",
)
```

---

## 7. 测试要求

### 7.1 必须通过的单元测试

`test_targets.py`：
- `build_perception_target(record)` 输出包含全部 6 个 perception tag
- 每个 tag 出现且仅出现一次
- recap 段以 `[recap]` 开头并包含 stage 与 intention
- `build_deliberation_target(record)` 的 reward 字段满足 `[-1.00, 1.00]` 两位小数
- `build_action_target(chosen)` 的 `<chosen>` 与 `policy_preference.chosen` 一致

`test_prompts.py`：
- 三个 user template 包含且仅包含 `f-string` 占位符 `{n_frames}, {image_placeholders}, ...`
- 没有任何裸 tag 字面量（用 `re` 检查所有 `<` 都来自 `TAG_*` 常量）

`test_parsers.py`：
- 合法 perception output 解析成功
- 缺一个 tag → `ParseError`
- stage 是非法值（如 `commitment`）→ `ParseError`
- score 是 `0` 或 `7` → `ParseError`
- 包含多余文本（在 tag 之外）→ 仍能解析（只看 tag 内内容）

`test_decision_loop.py`（依赖 mock VLM）：
- `tau_silence=2`、Perception 输出 score=2 时，跳过 Deliberation 直接返回 silence
- `tau_silence=1`、Perception 输出 score=2 时，进入完整三步循环
- Deliberation parse 失败时降级到 fallback action
- Action 输出的 chosen 不在 candidate set → `ParseError` → fallback

### 7.2 端到端集成测试

`test_e2e.py`：

```python
def test_e2e_decide_with_mock_vlm():
    """用 MockVLM (查表式 VLM 替身) 跑一个完整决策。"""
    mock = MockVLM(scripted_responses={
        "perception": canned_perception_output,
        "deliberation_A1_silent_observe": canned_a1_output,
        "deliberation_A2_offer_value_comparison": canned_a2_output,
        "deliberation_A4_open_with_question": canned_a4_output,
        "action": canned_action_output_choosing_A2,
    })
    agent = PIWMAgent.from_mock(mock, tau_silence=1, rollout_depth=1)
    decision = agent.decide(frames=[fake_image, fake_image, fake_image])
    assert decision.chosen_action == "A2_offer_value_comparison"
    assert decision.proactive_score == 4
    assert "A2" in decision.rationale or "value" in decision.rationale
```

MockVLM 的实现见 `piwm_infer/tests/fixtures/mock_vlm.py`。**严禁**为了让测试通过而修改实际模型行为；MockVLM 是约束的载体，不是橡皮泥。

---

## 8. 实现顺序（给 Codex）

按依赖关系：

1. `piwm_train/config.py` （所有 tag 字符串与 prompt 占位常量）
2. `piwm_train/targets.py` + `test_targets.py` 通过
3. `piwm_train/prompts.py` + `test_prompts.py` 通过
4. `piwm_infer/parsers.py` + `test_parsers.py` 通过
5. `piwm_infer/prompts.py`（与 train 共用 base）
6. `piwm_infer/decision_loop.py` + MockVLM + `test_decision_loop.py` 通过
7. `piwm_infer/decision_loop.py` 端到端 `test_e2e.py` 通过
8. `piwm_train/data_collator.py` + `piwm_train/sft.py` （需要真实 GPU；可先跑 1 epoch dry run）
9. `piwm_train/dpo.py` （**等 data pipeline 补齐 `meta.state_summary` 与 `meta.candidate_block` 字段后**）

每完成一步跑全部 pytest，绿了再下一步。

---

## 9. 已知风险与拦路问题

### 9.1 必须先解决的依赖

- **`policy_preference.jsonl` 的 `meta.state_summary` 与 `meta.candidate_block` 字段当前不存在**。这是 data pipeline 的输出契约，需要先在 `piwm_data/exporters.py` 补齐，否则 Phase 2 卡住。**这是 P0 阻塞**。
- **`state_inference.jsonl` 与 `transition_modeling.jsonl` 当前用的是 `intent` 字段，论文方案改成 `bdi` 三字段**。这是 schema 变更，需要 data pipeline 改 `MainSchemaRecord` 与 `exporters` 同步。**这是 P0 阻塞**。

这两件事不解决，本 spec 的 §3、§4、§5 都跑不了。建议先开 data pipeline 的 issue。

### 9.2 不阻塞但要早处理

- Qwen2.5-VL 多帧输入的 `image_grid_thw` 计算容易出错。建议先在最简 fixture 上 dry-run 一次 forward，确认 image embedding 维度与 attention mask 对齐。
- DPO Phase 2 需要把 LoRA merge 进 base model 后再 load，否则 `ref_model` 与 `policy_model` 的 base weights 不一致。merge 步骤要写进 Phase 2 入口脚本。

### 9.3 不在本期范围

- 多步 rollout 的 closed-loop self-action 选择
- 候选集 $\mathcal{C}_t$ 的 union widening（论文 §3.6 提到的 stage-transition 处理）
- 真实视频 streaming（本期假设输入是已经采样好的 K=3 帧）
- Reward shaping 的实时 RL fine-tune

---

## 10. 给 Codex 的指令模板

直接发给 Codex：

> 请按附件 `piwm_implementation_spec.md` 实现 PIWM 训练与推理代码。先实现 §8 中的步骤 1-7（不需要 GPU），每步跑完对应 pytest 验证通过后再做下一步。**不要**实现 §8 步骤 8-9，那两步需要先解决 §9.1 的 data pipeline 依赖。
>
> 你必须严格遵守：
>
> - §1 的所有 tag 字符串字面值
> - §2 的 prompt 模板（一字不改）
> - §3 的 target 构造逻辑
> - §6.3 的 parser 健壮性要求（出错即 raise，不做 fuzzy match）
> - §0.3 的模型选型（不要换其它 VLM）
>
> 任何 spec 没明说的细节，先按文档实现，再在 PR description 提出。
