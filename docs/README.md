# PIWM Docs Entry Point

更新时间：2026-05-15

本文是 `docs/` 的唯一阅读入口。当前阶段的原则是：

```text
先服务 NeurIPS sprint 的实验闭环，再保留长期研究背景。
```

如果只想知道“现在做到哪、下一步做什么”，只读第 1 节。

## 1. 当前必读

| 顺序 | 文档 | 用途 |
|---:|---|---|
| 1 | [current/experiment_result_digest.md](current/experiment_result_digest.md) | 当前已落盘实验结果速览：能写什么、还缺什么 |
| 2 | [current/experiment_status_main_table_v2.md](current/experiment_status_main_table_v2.md) | 主表 v2、visual ablation、frame budget、Future Verification 结果 |
| 3 | [current/dataset_inventory.md](current/dataset_inventory.md) | 数据集总账：official v2 数据、真实拍摄 manifest、训练/评估/World Model 边界 |
| 4 | [current/paper_data_section_blueprint.md](current/paper_data_section_blueprint.md) | 论文数据部分写作蓝图：数据层级、拍摄、QA、表格和维护机制 |
| 5 | [current/piwm_real_shooting_scripts_S01_S12.md](current/piwm_real_shooting_scripts_S01_S12.md) | 12 个真实拍摄状态的 A/B 单文件脚本全集；拍摄团队只打开这一份 |
| 6 | [current/piwm_real_shooting_data_annotation_appendix_v2.md](current/piwm_real_shooting_data_annotation_appendix_v2.md) | 真实数据后期标注附录：给数据负责人看的 ShootingClipRecord、QA 字段、入库字段 |
| 7 | [current/company_openrouter_funding_brief.md](current/company_openrouter_funding_brief.md) | 精简预算说明（完整版见 `company_data_status_for_openrouter.md`） |
| 8 | [current/company_data_status_for_openrouter.md](current/company_data_status_for_openrouter.md) | 完整版：进度、数据、效果、OpenRouter 机型与额度、附录主表（口径与精简版一致） |
| 9 | [current/current_sprint_status_and_reporting_policy.md](current/current_sprint_status_and_reporting_policy.md) | 对外报告口径：QA-reviewed / synthetic train / diagnostic-only 边界 |
| 10 | [current/priority_generation_policy.md](current/priority_generation_policy.md) | 新增 Kling 额度如何扩到 500/1000 parent synthetic |
| 11 | [current/data_demo_effect_status.md](current/data_demo_effect_status.md) | 数据 / demo / 效果提升原因的一页状态表；展示口径，非数据契约 |
| 12 | [current/before_after_demo_examples.md](current/before_after_demo_examples.md) | 同一输入下，训练前 vs 训练后的输出对比 demo；展示口径，非数据契约 |
| 13 | [current/remote_sprint_runbook.md](current/remote_sprint_runbook.md) | 远端数据盘、ms-swift、Kling、状态检查命令 |
| 14 | [current/project_directory_map.md](current/project_directory_map.md) | 本地/远端目录职责地图：official 数据、视频、checkpoint、docs 和 local artifacts 放置规则 |
| 15 | [current/repo_cleanup_github_plan.md](current/repo_cleanup_github_plan.md) | 本地/服务器目录清理与 GitHub 管理计划 |
| 16 | [current/local_artifacts_layout.md](current/local_artifacts_layout.md) | 本机根目录生成产物整理后的存放位置 |
| 17 | [contracts/action_space_realization_contract.md](contracts/action_space_realization_contract.md) | 6-act 动作空间、真人导购逻辑 / target terminal 数据边界、旧 A/T 标签兼容映射 |
| 18 | [contracts/data_generation_chain_v2_1_contract.md](contracts/data_generation_chain_v2_1_contract.md) | v2.2 动作、场景、label、专家知识库、policy slice 和 official 重导的唯一维护链路 |
| 19 | [contracts/data_schema_v2_contract.md](contracts/data_schema_v2_contract.md) | 当前成熟数据格式：MainSchemaRecord、ShootingClipRecord、导出字段和维护规则 |
| 20 | [v2_validation/distillation_summary.md](v2_validation/distillation_summary.md) | v2.2 专家蒸馏基础设施、batch 状态、审阅入口 |
| 21 | [v2_validation/compatibility_report.md](v2_validation/compatibility_report.md) | official 543 在 v2.2 下的基础兼容分级 + 扩展重推导审计 |
| 22 | [v2_validation/action_distribution.md](v2_validation/action_distribution.md) | official v1 best 分布、official 543 v2 重推导分布、864 explicit policy slice 分布 |
| 23 | [v2_validation/v2_2_reexport_dry_run.md](v2_validation/v2_2_reexport_dry_run.md) | official v2.2 dry-run、diff 预演与独立 v2 导出记录 |
| 24 | [v2_validation/v2_2_reexport_diff_preview.md](v2_validation/v2_2_reexport_diff_preview.md) | `--output-diff` 写回预演：如果 commit 会改哪些 official 文件 |
| 25 | [v2_validation/v2_2_test_coverage.md](v2_validation/v2_2_test_coverage.md) | v2.2 新增测试清单、覆盖面和当前缺口 |
| 26 | [v2_validation/v2_2_release_notes.md](v2_validation/v2_2_release_notes.md) | v2.2 上线说明：产物、字段、计数、验证和边界 |
| 27 | [v2_validation/action_space_audit_train_synth_v1.json](v2_validation/action_space_audit_train_synth_v1.json) | official train action-space 机器审计输出 |
| 28 | [data/official/README.md](../data/official/README.md) | official 数据入口、v2 重导状态和 red lines |

## 2. 当前执行线

| 任务 | 主文档 | 备注 |
|---|---|---|
| 扩训练数据 | [current/priority_generation_policy.md](current/priority_generation_policy.md) | 先跑 `priority500_new_after280`，再视额度追加 `priority1000_new_after280` |
| 数据集整理 | [current/dataset_inventory.md](current/dataset_inventory.md) | 训练集、评估集、World Model 数据和历史 smoke 的唯一总账 |
| Demo 和提升解释 | [current/data_demo_effect_status.md](current/data_demo_effect_status.md) | 展示材料；里面的旧 A/T action 写法只作为历史兼容，不作为新数据契约 |
| Before / After 输出对比 | [current/before_after_demo_examples.md](current/before_after_demo_examples.md) | 展示材料；里面的旧 action label 只作为 legacy alias |
| 主实验结果冻结 | [current/experiment_status_main_table_v2.md](current/experiment_status_main_table_v2.md) | 表格数字必须来自落盘 JSON/Markdown |
| 结果摘要与写作入口 | [current/experiment_result_digest.md](current/experiment_result_digest.md) | 适合给写作对话或导师快速阅读 |
| 公司预算沟通 | [current/company_openrouter_funding_brief.md](current/company_openrouter_funding_brief.md) | 一页摘要；细节与表格见完整版 |
| 组内技术汇报 | [current/company_data_status_for_openrouter.md](current/company_data_status_for_openrouter.md) | 完整叙述 + 预算档位 + 附录数字 |
| 真实数据拍摄 | [current/piwm_real_shooting_scripts_S01_S12.md](current/piwm_real_shooting_scripts_S01_S12.md) | 唯一现场脚本；不要再给拍摄团队分发旧 checklist 或分散脚本 |
| 真实数据标注 | [current/piwm_real_shooting_data_annotation_appendix_v2.md](current/piwm_real_shooting_data_annotation_appendix_v2.md) | 给数据负责人使用；承接拍摄素材到 ShootingClipRecord 入库字段 |
| 远端运行 | [current/remote_sprint_runbook.md](current/remote_sprint_runbook.md) | 所有大数据和视频放 `/root/lanyun-fs`，不要放系统盘 |
| 本地/远端目录管理 | [current/project_directory_map.md](current/project_directory_map.md) | official 数据、视频、checkpoint、docs、local artifacts 的职责边界 |
| Repo 清理与 GitHub 管理 | [current/repo_cleanup_github_plan.md](current/repo_cleanup_github_plan.md) | 本地和服务器如何只用 Git 管代码/文档，数据留数据盘 |
| 本机产物整理 | [current/local_artifacts_layout.md](current/local_artifacts_layout.md) | 根目录下的 `Archive*` / prompt / review sheet 已集中到 `local_artifacts/` |
| 文档维护 | [contracts/docs_maintenance_rules.md](contracts/docs_maintenance_rules.md) | 新增或归档文档前先看 |
| 动作空间更新 | [contracts/action_space_realization_contract.md](contracts/action_space_realization_contract.md) | 以 2026-05 附件为准；旧 A1-A8/T-state 只作兼容 alias |
| 数据生成链路更新 | [contracts/data_generation_chain_v2_1_contract.md](contracts/data_generation_chain_v2_1_contract.md) | 改动作、场景、label、专家规则、policy slice 或 official 重导前先看 |
| 数据格式维护 | [contracts/data_schema_v2_contract.md](contracts/data_schema_v2_contract.md) | 修改 schema、真实拍摄入库字段、official JSONL 前先看 |
| 专家规则 v2.2 蒸馏 | [v2_validation/distillation_summary.md](v2_validation/distillation_summary.md) | 改 intent tier、failure mode、Recommend pressure 前先审阅 batch |
| 真实拍摄脚本 | [current/piwm_real_shooting_scripts_S01_S12.md](current/piwm_real_shooting_scripts_S01_S12.md) | S01-S12 A/B 单文件脚本；现场拍摄只打开这一份 |
| 论文数据部分 | [current/paper_data_section_blueprint.md](current/paper_data_section_blueprint.md) | 写 dataset section、数据表、QA 口径和 real-shooting plan 时先看 |

## 3. 研究契约

这些文件定义 PIWM 的方法边界和数据契约。它们不是每天第一入口，但改代码/写方法章节时需要查。

| 文档 | 用途 |
|---|---|
| [contracts/claim_to_artifact_audit.md](contracts/claim_to_artifact_audit.md) | 论文 claim 与代码/数据工件对应关系 |
| [contracts/action_space_realization_contract.md](contracts/action_space_realization_contract.md) | 6 个 Dialogue Acts、真人导购逻辑 / target terminal 数据边界、旧动作标签迁移规则 |
| [contracts/data_generation_chain_v2_1_contract.md](contracts/data_generation_chain_v2_1_contract.md) | 动作、场景、label、专家知识库、official 重导的唯一维护链路 |
| [contracts/data_schema_v2_contract.md](contracts/data_schema_v2_contract.md) | 成熟数据格式、真实拍摄 clip manifest、导出策略和版本维护 |
| [contracts/world_model_supervision_contract.md](contracts/world_model_supervision_contract.md) | World Model 监督契约，含 continuation / Future Verification 逻辑 |
| [contracts/visual_input_contract.md](contracts/visual_input_contract.md) | 多视角、K=3 抽帧、QA gate、frame manifest |
| [contracts/expert_provenance_upgrade_plan.md](contracts/expert_provenance_upgrade_plan.md) | 专家规则 provenance 补强计划 |
| [contracts/kling_api_usage.md](contracts/kling_api_usage.md) | Kling wrapper 使用说明 |

来源材料：

| 文档 | 用途 |
|---|---|
| [source_materials/2026-05-action-space/source_digest.md](source_materials/2026-05-action-space/source_digest.md) | 本次动作空间整合的附件副本、来源优先级和 S05 验收样例 |

## 4. 背景与历史参考

这些文件保留历史价值，但不再作为当前决策入口。

| 文档 | 当前状态 |
|---|---|
| [background/data_generation_loop_status.md](background/data_generation_loop_status.md) | 早期数据闭环诊断，已被 `current/` 的 sprint 状态覆盖 |
| [background/data_loop_master_plan.md](background/data_loop_master_plan.md) | 早期主计划，当前执行以 `current/` 为准 |
| [background/current_code_status.md](background/current_code_status.md) | 代码状态冷启动说明，查老 pipeline 时有用 |
| [background/intro_related_work_v6.md](background/intro_related_work_v6.md) | 早期 intro + related work 草稿，不等于当前 paper 最新结果 |
| [background/related_work_expert_distillation.md](background/related_work_expert_distillation.md) | 专家蒸馏 related-work 背景 |
| [background/readable_data_plan_background.md](background/readable_data_plan_background.md) | 给非实现者看的可读版背景 |
| [background/pilot30_continuation_review_report.md](background/pilot30_continuation_review_report.md) | pilot30 continuation 历史审阅报告 |
| [background/neurips_sprint_master_plan.md](background/neurips_sprint_master_plan.md) | sprint 初始总计划，已被当前结果文档覆盖 |
| [background/neurips_sprint_codex_plan.md](background/neurips_sprint_codex_plan.md) | sprint 初始执行计划，已被当前结果文档覆盖 |
| [background/neurips_sprint_result_snapshot_20260430.md](background/neurips_sprint_result_snapshot_20260430.md) | 2026-04-30 快照，已被当前结果文档覆盖 |

## 5. 不要混用的口径

| 概念 | 正确用法 |
|---|---|
| `PIWM-Train-Synth-v1` | 正式主训练集；`priority1000_unreviewed*` 只作 backing/source path，不作为公开数据名；training-only synthetic，不写成 QA-pass |
| `PIWM-Train-Synth-v2` | v2.2 schema 独立导出；同一批 543 parent，不代表新增视频；训练入口为 `data/official/ms_swift/piwm_train_synth_v2.jsonl` |
| `PIWM-PolicySlice-v2` | 864 条 explicit candidate-rule policy manifest；不是视频数据，不是 QA-reviewed dataset |
| `PIWM-Eval-QA-v1` | 正式主评估集，旧名 `priority40_qareviewed_sample`；当前最干净的 QA-reviewed parent eval subset |
| `PIWM-WorldModel-v1` | 正式 World Model 数据，旧名 `pilot30_with_continuations`；Future Verification 小规模视觉监督，不是主训练规模来源 |
| `PIWM-RealShoot-v1` | 真实拍摄 manifest 模板与 S01-S12 A/B 协议；视频和 QA 未完成前不能写成已采集真实数据 |
| `A1-A8 / T-state` | 只作为 legacy alias 和迁移键；`PIWM-Train-Synth-v1` 保留真人导购逻辑，新动作语义使用 `candidate_action_specs / best_action_spec / DialogueAct + params` |
| v2.2 official 重导 | 不覆盖 v1；重导前先跑 `python3 scripts/refresh_official_v2_exports.py --dry-run --output-diff docs/v2_validation/v2_2_reexport_diff_preview.md`，然后写入独立 v2 路径 |
| `Future Verification full84` | action-conditioned future verification 证据，不是完整 benchmark |
| DPO | 当前 sprint 暂停，不作为主实验阻塞项 |

## 6. 文档维护规则

- 新增文档前先判断是否能放入现有 `current/` 或 `contracts/`。
- 如果只是实验结果摘要，优先更新 [current/experiment_result_digest.md](current/experiment_result_digest.md)。
- 如果是主表数字或消融，优先更新 [current/experiment_status_main_table_v2.md](current/experiment_status_main_table_v2.md)。
- 如果是数据生成规模、Kling 队列、QA 口径，优先更新 [current/priority_generation_policy.md](current/priority_generation_policy.md) 或 [current/current_sprint_status_and_reporting_policy.md](current/current_sprint_status_and_reporting_policy.md)。
- `background/` 只作为历史参考，不再扩写。
