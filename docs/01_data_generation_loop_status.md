# PIWM 数据生成闭环：现状、问题与实现目标

更新时间：2026-04-29

## 1. 定位

本文是数据生成闭环的冷启动诊断文档。它回答三件事：

1. 当前项目已经有什么；
2. 当前数据闭环断在哪里；
3. 下一步实现目标是什么。

详细设计拆到独立文档：

- [00_claim_to_artifact_audit.md](00_claim_to_artifact_audit.md)：论文 claim 与代码/数据工件对齐审计；
- [03_world_model_supervision_contract.md](03_world_model_supervision_contract.md)：什么训练才体现 World Model；
- [04_visual_input_contract.md](04_visual_input_contract.md)：Kling 视频、抽帧、多图输入与 QA 契约。

核心判断保持不变：

> 数据生成闭环优于单一架构优化。  
> 在 `expert rules -> controlled video -> QA -> dataset JSONL` 没有闭合之前，不应优先实现训练/推理侧大型架构。

## 2. 目标闭环

目标闭环是：

```text
销售专家知识 / AIDA / SOP
  -> conditional_rules.jsonl
  -> rules.py runtime tables
  -> scenario_sampler.py
  -> prompt_builder.py
  -> Kling current-state video
  -> frame_manifest.json + frames/
  -> QA gate
  -> main_schema.jsonl
  -> state_inference / transition_modeling / policy_preference
  -> piwm_train / piwm_infer
```

这个闭环服务论文当前主张：

- pedagogy-derived action constraints；
- AIDA-BDI state representation；
- action-conditioned transition prediction；
- controllable video rendering；
- synthetic / real-store / OOD split evaluation。

## 3. 当前已有模块

| 模块 | 路径 | 当前状态 |
|---|---|---|
| 主 schema | `piwm_data/schemas.py` | 已实现基础版；有 `aida_stage`、`latent_state`、`intent`、`proactive_score`、候选动作和动作后果；缺显式 BDI |
| 规则层 | `piwm_data/rules.py` | 已实现但为硬编码；包含五张核心表 + 一张 fallback intent 表 |
| Loader | `piwm_data/archive_loader.py` | 读取新格式 `prompt.json + frames/` |
| Exporter | `piwm_data/exporters.py` | 已导出三套 JSONL；缺 `bdi`、`next_bdi`、`state_summary`、`candidate_block` |
| Validator | `piwm_data/validate.py` | 校验 schema 和图片路径 |
| Dataset CLI | `piwm_data/build_dataset.py` | 写 `main_schema.jsonl` 与三套训练 JSONL |
| Kling wrapper | `kling/generate_session.js` | 已验证存在；只做 API 调用，不构造受控 prompt |
| 测试 | `piwm_data/tests/` | 最近一次验证为 36 个测试通过；新增测试后需更新该快照 |

当前 `data/piwm_dataset/*.jsonl` 是空数据产物，不代表已有可训练数据。原因是仓库里的旧 `Archive/` 是旧格式，当前 loader 只接受：

```text
session/
├── prompt.json
└── frames/
```

旧 Archive 不再作为主线迁移；旧项目只复用 Kling API 调用经验。

## 4. 核心问题与修正目标

| 问题 | 当前状态 | 修正目标 | 验收 |
|---|---|---|---|
| ~~专家规则来源不足~~ | ~~`rules.py` 直接硬编码~~ | ~~新增 `piwm_data/expert_corpus`，从 JSONL 编译运行时表~~ | **✅ 完成 2026-04-29**：72 条 JSONL（10/14/9/9/9/21）+ 13 测试 + pytest 49 passed |
| BDI 缺失 | schema 只有 `intent`，无 `belief/desire/intention` | 增加 `BDISummary`；exporter 输出 `bdi` / `next_bdi` | 三字段非空；训练 target 可读取 |
| `sigma` 与 `latent_state` 混淆 | 论文 `sigma` 是 AIDA；代码 `latent_state` 是行为子状态 | 明确：`aida_stage = sigma`，`latent_state` 改定位为 `behavioral_state/state_subtype` | `state_inference.output.aida_stage` 进入监督目标 |
| reward 公式未落地 | 代码 reward 是标量 magic number | 记录 `reward_components`，用 `alpha*delta_stage + beta*delta_mental - gamma*action_cost` 校验 | `final_reward` 与组件公式一致 |
| Kling 只接 API | 缺 sampler / prompt builder / split | 场景采样与 prompt timeline 自动生成 | manifest 可复现，prompt 不泄露标签 |
| QA gate 缺失 | 合法 frames 即可入库 | QA 同时检查视频与 sampled frames | fail 样本写 reject log |
| OOD split 缺失 | 无 split manifest | sampler 生成 train/dev/test/ood_product/ood_persona | split 可复现 |
| real-store split 缺失 | 论文承诺 real-store test，但代码未定义 | 定义 `real_test` / `real_calibration` 数据契约 | 不经 Kling，但进入同一 schema |
| 两阶段训练契约不完整 | 三套 JSONL 已有雏形，但与 SFT/DPO 未显式绑定 | Phase 1 用 state+transition SFT，Phase 2 用 preference DPO | 见 `02_data_loop_master_plan.md` |

## 5. 规则表口径

当前 `rules.py` 中需要进入专家规则语料层的映射不是单纯“五张表”，而是：

| 映射 | 当前条数 | 处理方式 |
|---|---:|---|
| `CUE_TO_STATE_PRIOR` | 10 | 编译自 expert corpus |
| `PERSONA_STATE_TO_INTENT` | 14 | 编译自 expert corpus |
| `STATE_FALLBACK_INTENT` | 9 | 编译自 expert corpus，避免隐藏硬编码 |
| `STATE_TO_PROACTIVE_SCORE` | 9 | 编译自 expert corpus |
| `STATE_AIDA_TO_CANDIDATES` | 9 | 编译自 expert corpus |
| `TRANSITION_TABLE` | 21 | 编译自 expert corpus，并补 reward components |

后续文档中如果简称“五张核心表”，必须额外说明 fallback intent 是第六张运行时映射。

## 6. 当前不应优先做

- 不直接实现 `piwm_train.sft` / `piwm_train.dpo`；
- 不直接实现完整 `piwm_infer`；
- 不把完整视频输入作为第一版主训练模式；
- 不做多视频多轮训练；
- 不迁移旧 Archive 作为主线；
- 不把 seed rules 说成真实教材蒸馏结果；
- 不在没有 QA gate 的情况下批量生成训练数据。

## 7. 下一步

1. 完成 [00_claim_to_artifact_audit.md](00_claim_to_artifact_audit.md) 中 P0 blocking 项的文档修正；
2. 实现 `piwm_data/expert_corpus`，先让六张运行时映射可追溯；
3. 补 `reward_components`，让 reward 标量不再是 magic number；
4. 补 BDI、`aida_stage` 输出、`state_summary`、`candidate_block`；
5. 再进入 sampler / prompt builder / QA gate。
