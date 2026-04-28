# PIWM Claim-to-Artifact Audit

更新时间：2026-04-29（Phase 1 expert_corpus 已落地后再次更新）

## 1. 目的

本文把论文 `paper/main.tex` 中的核心 claim 映射到当前代码和数据工件，标出缺口与修正优先级。

状态定义：

- `covered`：当前已有代码/数据工件基本支撑；
- `partial`：已有骨架，但语义或字段不完整；
- `blocking`：论文 claim 当前缺少必要工件，继续实现前必须补；
- `future`：论文或实验后续增强，当前不阻塞小规模 pilot。

## 2. P0 审计表

| Claim | 论文位置 / 内容 | 当前工件 | 状态 | 缺口 | 必须修正 |
|---|---|---|---|---|---|
| Pedagogy-derived action space | action set compiled from retail training manuals | `piwm_data/rules.py` + `piwm_data/expert_corpus/distilled/conditional_rules.jsonl` (72 entries, all `seed_rule`) | covered（first batch 是 honest seed，后续可接受真实蒸馏条目） | 第一批是 seed_rule，不是真实教材引用；后续条目按需补 `manual_distillation`/`pedagogy_text` 来源 | 视论文叙事强度，决定是否第二批补真实教材蒸馏 |
| AIDA-BDI state | `s_t=(sigma_t,b_t,d_t,i_t)` | `aida_stage` + `latent_state` + `intent` | blocking | 无显式 BDI；`latent_state` 与 `sigma` 语义混用 | `aida_stage=sigma`；新增 `bdi`；`latent_state` 定位为 `state_subtype` |
| Perception target | `<sigma,b,d,i,rho,C>` | `state_inference.output` | partial | `aida_stage` 在 meta，不在 output；缺 BDI | `output.aida_stage`、`output.bdi` 进入监督目标 |
| Deliberation target | `<sigma_next,b_next,d_next,i_next,risk,benefit,reward>` | `transition_modeling.output` | partial | 已有 `next_state/risk/benefit/reward`；缺 `next_bdi`；`next_state` 不是 AIDA sigma | 增加 `next_aida_stage` 或明确映射；增加 `next_bdi` |
| Reward decomposition | `r=alpha*Delta_sigma+beta*Delta_m-gamma*c(a)` | `TRANSITION_TABLE.reward` | blocking | 当前是直接标量，无组件来源 | 增加 `reward_components` 并校验 final reward |
| World Model supervision | same state + different action -> different future | `transition_modeling.jsonl` | partial | exporter 已按 action 展开；缺对照组统计，空数据未验证 | 增加 contrast stats；pilot 数据必须非空 |
| Two-phase training | Phase 1 SFT, Phase 2 DPO | 三套 JSONL | partial | 文档未明确三套数据如何分配到训练阶段 | Phase 1: state + transition；Phase 2: preference |
| Real-store split | reserved real-store scenes for calibration/test | 无 | blocking | 无 real data schema、split、privacy metadata | 定义 `real_test` / `real_calibration` 契约 |
| OOD split | held-out products/personas | 无 sampler | blocking | 无 split manifest | sampler 写入 `ood_product` / `ood_persona` |
| Visual rendering | Kling renders visual side, not labels | `kling/generate_session.js` | partial | API wrapper 已有；无 prompt builder / QA | 实现 sampler + prompt builder + QA gate |
| Internal simulator | same VLM queried three times | method-side spec in archive | future | 数据契约未稳定，训练代码暂缓 | 数据 pilot 后解锁 `piwm_train` / `piwm_infer` |

## 3. 关键语义决策

### 3.1 `sigma` 与 `latent_state`

论文中的 `sigma_t` 是 AIDA 四阶段：

```text
attention / interest / desire / action
```

代码中的 `latent_state` 是行为/心理子状态：

```text
high_hesitation / active_evaluation / ready_to_decide / ...
```

修正原则：

- `aida_stage` 对应论文 `sigma_t`；
- `bdi` 对应论文 `(b_t,d_t,i_t)`；
- `latent_state` 不再冒充 `stage`，应定位为 `state_subtype` 或 `behavioral_state`；
- 训练 tag `<stage>` 只能输出 AIDA，不输出 `latent_state`。

### 3.2 Reward 标量与公式

当前 `reward=0.8` 等数值可以暂时保留，但必须能解释为：

```text
final_reward = alpha * delta_stage + beta * delta_mental - gamma * action_cost
```

建议规则 JSONL 增加：

```json
{
  "reward_components": {
    "delta_stage": 0.4,
    "delta_mental": 0.6,
    "action_cost": 0.1,
    "alpha": 0.4,
    "beta": 0.5,
    "gamma": 0.1,
    "final_reward": 0.75
  }
}
```

编译时：

- 校验 `final_reward` 在 `[-1, 1]`；
- 校验 `alpha + beta + gamma = 1`；
- 校验公式结果与 `final_reward` 在容差内一致；
- `TRANSITION_TABLE.reward` 使用 `final_reward`。

### 3.3 Real-store 数据契约

real-store 数据不经过 Kling，但必须进入同一主 schema。

建议字段：

```json
{
  "is_synthetic": false,
  "split": "real_test",
  "capture_source": "real_store",
  "privacy_review": {
    "consent_status": "approved",
    "face_blur": true,
    "brand_blur": true,
    "raw_video_restricted": true
  }
}
```

real-store 样本仍需：

- `prompt.json` 或等价 metadata；
- `frames/`；
- `qa_report.json`；
- 人工或专家确认的 cue/state/action labels。

## 4. DoD 映射

| DoD | 对应文档 | 验收条件 |
|---|---|---|
| DoD-0 | 本文 | P0 claims 均标注 `covered/partial/blocking`，不得把缺失 claim 写成已完成 |
| DoD-Expert | [01_data_generation_loop_status.md](01_data_generation_loop_status.md) | 六张运行时映射可从 expert corpus 编译 |
| DoD-Reward | 本文 | reward components 可解释并校验 final reward |
| DoD-Visual | [04_visual_input_contract.md](04_visual_input_contract.md) | sampled frames 支持 target cue |
| DoD-WM | [03_world_model_supervision_contract.md](03_world_model_supervision_contract.md) | 同一 parent state 有多条 action-conditioned future |
| DoD-Real | 本文 | real-store split 有 schema、privacy metadata 与 QA |

## 5. 当前最急修正

> 进度：第 1 项已完成（`expert_corpus` + 72 条 JSONL + 13 个测试），具体见 RESEARCH_LOG 2026-04-29 22:30。

1. ~~将"规则表五张"修为"六张运行时映射"~~（**已完成 2026-04-29**：72 条 = 10/14/9/9/9/21，pytest 49 passed）
2. 明确 `aida_stage=sigma`，`latent_state=state_subtype`；
3. `state_inference.output` 增加 `aida_stage` 与 `bdi`；
4. `transition_modeling.output` 增加 `next_bdi`，并明确 next stage 字段；
5. `TRANSITION_TABLE` 增加 reward component 来源；
6. 新增 real-store split 契约。
