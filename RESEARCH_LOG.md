# PIWM Research Log

核心逻辑基点：**数据生成闭环优于单一架构优化**。

本文件是 PIWM 项目的动态索引与计划跟踪中心。活跃文档只保留能直接服务当前闭环的入口；历史材料统一放入 `docs/archive/`。

## Active Document Index

| Active Doc | Role |
|---|---|
| [docs/00_claim_to_artifact_audit.md](docs/00_claim_to_artifact_audit.md) | 最高优先级审计：论文 claim 与代码/数据工件差距 |
| [docs/01_data_generation_loop_status.md](docs/01_data_generation_loop_status.md) | 数据生成闭环现状、问题、目标 |
| [docs/02_data_loop_master_plan.md](docs/02_data_loop_master_plan.md) | 当前执行计划：阶段顺序与 DoD |
| [docs/03_world_model_supervision_contract.md](docs/03_world_model_supervision_contract.md) | World Model 监督契约：action-conditioned transition |
| [docs/04_visual_input_contract.md](docs/04_visual_input_contract.md) | 视觉输入契约：Kling、抽帧、frame manifest、QA |
| [docs/05_current_code_status.md](docs/05_current_code_status.md) | 当前代码状态：schema/rules/exporter/Kling wrapper |
| [docs/06_data_pipeline_usage.md](docs/06_data_pipeline_usage.md) | 现有数据管线使用说明 |
| [docs/07_kling_api_usage.md](docs/07_kling_api_usage.md) | Kling API wrapper 使用说明 |
| [docs/08_intro_related_work_v6.md](docs/08_intro_related_work_v6.md) | 最新 intro + related work 草稿，定义当前论文 claim |
| [docs/09_related_work_expert_distillation.md](docs/09_related_work_expert_distillation.md) | 高价值 related-work 审阅：专家知识蒸馏与销售/视觉 agent 差异 |
| [docs/10_readable_data_plan_background.md](docs/10_readable_data_plan_background.md) | 可读版背景说明，非执行入口 |
| [docs/11_docs_maintenance_rules.md](docs/11_docs_maintenance_rules.md) | docs 维护守则：新增、编号、归档、日志更新规范 |

## High-Density Updates

### [2026-04-29 02:19:27 CST] | Phase: Documentation Refactor / Claim-Data Alignment

**Key Progress**
- 将 `docs/` 活跃文档按处理顺序重命名为 `00` 到 `10`，archive 文档也统一编号。
- 新增 `00_claim_to_artifact_audit.md`，把 reward 三项分解、`sigma` vs `latent_state`、real-store split、六张运行时映射列为 P0 审计项。
- 拆出 `03_world_model_supervision_contract.md` 与 `04_visual_input_contract.md`，让 `01_data_generation_loop_status.md` 回到“现状诊断”职责。
- 更新 `02_data_loop_master_plan.md`：规则表口径修正为五张核心表 + fallback intent；数据契约加入 `aida_stage` output、`next_aida_stage`、`reward_components` 与 real-store 阻塞。
- 新增 `11_docs_maintenance_rules.md`，规定 docs 新增、编号、归档和 RESEARCH_LOG 更新规则。

**Data Loop Insight**
- 文档体系现在按闭环处理顺序组织：先审计 claim，再看现状，再执行主计划，再进入 World Model 和视觉输入细则。
- 当前最大 blocking 从“缺 BDI”升级为四类：专家规则来源、AIDA/BDI/latent_state 语义、reward decomposition、real-store split。

**Pending Criticals**
- DoD-0：`00_claim_to_artifact_audit.md` 中所有 P0 blocking 项有代码任务映射。
- DoD-Expert：六张运行时映射进入 `expert_corpus`，包含 fallback intent。
- DoD-Reward：transition reward 可由组件公式校验。
- DoD-Real：real-store split 有 schema、privacy metadata 与 QA 入口。

**Ref Reference**
- [docs/00_claim_to_artifact_audit.md](docs/00_claim_to_artifact_audit.md)
- [docs/01_data_generation_loop_status.md](docs/01_data_generation_loop_status.md)
- [docs/02_data_loop_master_plan.md](docs/02_data_loop_master_plan.md)
- [docs/03_world_model_supervision_contract.md](docs/03_world_model_supervision_contract.md)
- [docs/04_visual_input_contract.md](docs/04_visual_input_contract.md)
- [docs/11_docs_maintenance_rules.md](docs/11_docs_maintenance_rules.md)

### [2026-04-29 01:59:59 CST] | Phase: Data Loop Design / World Model Supervision

**Key Progress**
- 在 `docs/03_world_model_supervision_contract.md` 中固化“World Model 性质如何在训练中体现”。
- 明确 PIWM 的最小 World Model 判据：`same observation + same current state + different action -> different predicted future`。
- 将 `transition_modeling.jsonl` 定义为核心 world-modeling 证据，`state_inference` 仅负责 state estimation，`policy_preference` 只间接体现。
- 新增 action 对照组统计要求：`n_parent_states`、`n_transition_rows`、`avg_actions_per_state`、`n_states_with_action_contrast`。

**Data Loop Insight**
- 数据闭环必须从一条 current-state video 展开多条 action-conditioned transition rows；否则系统会退化为状态分类器加策略选择器，不能支撑 World Model claim。
- 后续实现应优先保证同一 `state_id` 下存在多个候选动作及差异化 future 标签。

**Pending Criticals**
- DoD-WM-1：每个有效 parent state 至少生成 2 条 action-conditioned transition rows。
- DoD-WM-2：统计 `n_states_with_action_contrast`，确保不同动作不总是导向同一 future。
- DoD-WM-3：`transition_modeling.jsonl` 保留 `parent_state_id`、`candidate_action`、`current_state_summary` 与完整 next-state outcome。

**Ref Reference**
- [docs/03_world_model_supervision_contract.md](docs/03_world_model_supervision_contract.md)
- [docs/02_data_loop_master_plan.md](docs/02_data_loop_master_plan.md)

### [2026-04-29 00:46:39 CST] | Phase: Data Loop Design / Visual Input Contract

**Key Progress**
- 在 `docs/04_visual_input_contract.md` 中固化“视觉样本形态与训练模式决策”。
- 将第一版主线固定为 `单视频 -> 多图抽帧 -> 单轮样本 -> 推理时多次调用`。
- 明确 `state_inference`、`transition_modeling`、`policy_preference` 均共享同一组 sampled frames，差异只在文本任务。
- 新增 `frame_manifest.json`、`training_input_mode`、`cue_visible_in_sampled_frames` 等字段要求，防止视频整体有 cue 但训练帧无 cue。

**Data Loop Insight**
- 数据闭环的视觉一致性不能只验证 `video.mp4`，必须验证“模型实际读到的帧”与标签一致。
- 当前主训练模式定义为 `multi_image_single_turn`；single-frame、video-native、多视频多轮均降级为 ablation 或后续增强。

**Pending Criticals**
- DoD-Visual-1：`prompt_builder.py` 输出 behavior timeline，能支持 cue onset / peak / resolution 三点抽帧。
- DoD-Visual-2：`extract_frames.py` 生成 `frame_manifest.json`，记录时间戳、帧角色、采样策略和 `training_input_mode`。
- DoD-Visual-3：QA gate 同时检查整段视频与 sampled frames，sampled frames 不支持标签时拒绝样本。

**Ref Reference**
- [docs/04_visual_input_contract.md](docs/04_visual_input_contract.md)
- [docs/02_data_loop_master_plan.md](docs/02_data_loop_master_plan.md)

### [2026-04-29 00:40:31 CST] | Phase: Data Loop Documentation / Cold Start

**Key Progress**
- 新增 `docs/01_data_generation_loop_status.md`，把当前数据生成闭环拆成已实现模块、缺口、实现目标、非优先事项。
- 明确当前 `data/piwm_dataset/*.jsonl` 是空数据产物，不代表已有可训练数据。
- 将训练/推理侧阻塞具体化为 `bdi`、`next_bdi`、`state_summary`、`candidate_block` 四个缺失字段。
- 固化下一步最小任务：先做 `claim_to_artifact_audit.md`，再做 `expert_corpus` 规则来源迁移。

**Data Loop Insight**
- 当前闭环断点不在 exporter 能不能写 JSONL，而在专家规则来源、Kling prompt 受控构造、QA gate、BDI 训练契约四个环节。
- 文档将“可运行的 schema 骨架”和“可训练的数据闭环”明确区分，降低后续实现者误判项目进度的风险。

**Pending Criticals**
- DoD-0：`docs/00_claim_to_artifact_audit.md` 完成，P0 claim 不得误标为 covered。
- DoD-1：`expert_corpus` 编译出的五张核心规则表 + fallback intent 表保持现有行为不漂移。
- DoD-2：BDI 与 preference meta 字段进入 data pipeline，而不是只存在于训练 spec。
- DoD-3：Kling 生成样本必须经过 target cue 可见性 QA。

**Ref Reference**
- [docs/01_data_generation_loop_status.md](docs/01_data_generation_loop_status.md)
- [docs/02_data_loop_master_plan.md](docs/02_data_loop_master_plan.md)
- [docs/05_current_code_status.md](docs/05_current_code_status.md)

### [2026-04-29 00:31:27 CST] | Phase: Research Documentation / Data Loop Governance

**Key Progress**
- 将项目文档控制原则固化为“数据生成闭环优于单一架构优化”。
- 新增 `docs/02_data_loop_master_plan.md`，把专家规则、Kling、QA gate、schema/exporter、训练解锁条件串成单一闭环。
- 保存最新 v6 论文草稿到 `docs/08_intro_related_work_v6.md`，作为当前 claim 源。
- 将 Claude method-side implementation spec 保存到 `docs/archive/06_piwm_implementation_spec_method_side_blocked.md`，标记为被 BDI 与 preference meta 数据契约阻塞。
- 清理过时/低活跃文档到 `docs/archive/`，活跃索引只保留当前闭环相关入口。

**Data Loop Insight**
- 当前不能直接进入 `piwm_train` / `piwm_infer`；训练侧 spec 依赖尚未产出的 `bdi`、`next_bdi`、`state_summary`、`candidate_block`。
- 下一步应先完成 `expert_corpus -> runtime rules -> sampler/prompt_builder -> Kling video -> QA -> dataset JSONL`，否则 architecture code 会绑定不存在的数据格式。

**Pending Criticals**
- DoD-0：完成 `docs/00_claim_to_artifact_audit.md`，确认 v6 每个 P0 claim 对应代码/数据工件。
- DoD-1：`conditional_rules.jsonl` 覆盖当前五张核心规则表 + fallback intent 表，编译后既有 pytest 不回退。
- DoD-2：data pipeline 输出显式 `bdi` / `next_bdi` / `meta.state_summary` / `meta.candidate_block`。
- DoD-3：Kling prompt 由 sampler + prompt builder 生成，且 QA gate 能拒绝 cue 不可见样本。

**Ref Reference**
- [docs/02_data_loop_master_plan.md](docs/02_data_loop_master_plan.md)
- [docs/08_intro_related_work_v6.md](docs/08_intro_related_work_v6.md)
- [docs/10_readable_data_plan_background.md](docs/10_readable_data_plan_background.md)
- [docs/archive/06_piwm_implementation_spec_method_side_blocked.md](docs/archive/06_piwm_implementation_spec_method_side_blocked.md)
