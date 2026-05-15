# PIWM Project Directory Map

更新时间：2026-05-13 CST

本文记录本地仓库和远端数据盘的目录职责。后续新增数据、视频、checkpoint 或文档时，先按本表放置，避免把训练数据、评估结果和历史 smoke 混在一起。

## 1. 根目录分工

| 位置 | 角色 | 使用规则 |
|---|---|---|
| 本地 `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel` | 代码、文档、小型 JSON/Markdown 结果、少量 demo asset | 可以进 Git 的内容以代码和文档为主；不要把大视频、模型 cache、checkpoint 放进本地仓库主路径 |
| 远端 `/root/lanyun-fs/ProactiveIntentWorldModel` | 数据盘权威副本：视频、抽帧、official dataset、ms-swift 输入、训练结果、评估结果 | 大文件和所有 GPU/Kling 相关产物只放这里；不要写系统盘 |
| 远端 `/root/lanyun-fs/venvs/` | 远端 Python / ms-swift 环境 | 环境可以重建，不进 Git |

## 2. 本地目录职责

| 本地路径 | 内容 | 状态 |
|---|---|---|
| `piwm_data/` | 数据 schema、规则、archive loader、exporter、validation、数据测试 | 活跃代码 |
| `scripts/` | scenario/prompt/Kling/QA/dataset/ms-swift/eval 辅助脚本 | 活跃代码 |
| `piwm_train/` | SFT target、prompt、ms-swift adapter、训练数据适配 | 活跃代码 |
| `piwm_infer/` | parser、decision loop、baseline/eval 支撑 | 活跃代码 |
| `docs/current/` | 当前可读入口、数据总账、实验结果、demo、目录地图 | 活跃文档 |
| `docs/contracts/` | 方法契约：action space / realization、data schema v2.1、data generation chain、visual input、World Model、claim 对齐、文档维护规则 | 活跃契约 |
| `docs/contracts/data_generation_chain_v2_1_contract.md` | 动作、场景、label、专家知识库、official 重导的唯一维护链路 | 改生成逻辑前先看 |
| `docs/current/piwm_real_shooting_scripts_S01_S12.md` | 按 `拍摄脚本_S05` 格式整理的 S01-S12 单文件可执行拍摄脚本 | 活跃拍摄文档；拍摄团队只打开这一份 |
| `docs/current/paper_data_section_blueprint.md` | 论文数据部分写作蓝图：数据层级、QA、拍摄脚本、表格和维护顺序 | 写数据章节和重导数据前先看 |
| `docs/source_materials/` | 外部附件和来源副本，例如 2026-05 action-space 拍摄方案与 S05 脚本 | 只作追溯来源；不作为并行执行入口 |
| `docs/background/` | 历史背景和早期计划 | 只读参考，不作为执行入口 |
| `docs/archive/` | 被替代、重复、过期或 blocked 的文档 | 归档 |
| `data/official/` | official dataset alias 与小型 ms-swift JSONL 镜像 | 当前正式入口；远端为权威 |
| `data/official/piwm_realshoot_v1/` | `PIWM-RealShoot-v1` manifest 模板与 24 行 S01-S12 A/B 样例 | 不是已采集真实数据；assets 和 QA 补齐后才能进入 eval |
| `data/piwm_dataset_*` | 本地镜像的数据集导出和 official backing/source path | 保留复现价值；论文、汇报、示例展示和新脚本不要默认当 official |
| `data/piwm_results/` | 小型评估结果和 ms-swift JSONL 镜像 | 保留；大 checkpoint 以远端为准 |
| `local_artifacts/` | 本机生成视频、prompt、review sheets、cache | 不进 Git |
| `logs/` | 远端/本地运行日志镜像 | 小型日志可保留 |
| `paper/` | 论文源文件 | 活跃 |

## 3. 远端目录职责

| 远端路径 | 内容 | 使用规则 |
|---|---|---|
| `data/official/` | PIWM v1 official aliases 和 ms-swift training/eval JSONL | 对外口径优先引用这里 |
| `data/official/piwm_train_synth_v1` | `PIWM-Train-Synth-v1` symlink，543 parent synthetic train | 可以训练；保留真人导购逻辑；不可写成 QA-pass 或 target terminal 数据 |
| `data/official/piwm_eval_qa_v1` | `PIWM-Eval-QA-v1` symlink，36 QA-pass parent | 主评估入口 |
| `data/official/piwm_world_model_v1` | `PIWM-WorldModel-v1` symlink，24 parent / 44 continuation / 84 FV | World Model / Future Verification 入口 |
| `data/official/ms_swift/piwm_train_full_v2.jsonl` | 3339 examples，当前最完整 fresh SFT 输入 | 下一次从 base 重训优先使用 |
| `data/piwm_dataset_priority1000_unreviewed_compact_v2/` | `PIWM-Train-Synth-v1` backing/source path | official train symlink 指向这里；公开引用使用 `data/official/piwm_train_synth_v1/` |
| `data/piwm_dataset_priority40_qareviewed_sample_compact_v2_exact/` | 主 QA eval source | official eval symlink 指向这里 |
| `data/piwm_dataset_pilot30_with_continuations_compact_v2/` | World Model source | official world-model symlink 指向这里 |
| `data/piwm_results/` | ms-swift exports、eval JSON、checkpoint 输出 | 最新训练 checkpoint 在这里 |
| `Archive_generated_*` | Kling parent videos、frames、QA reports | 大文件，只留远端 |
| `Archive_prompts_*` | Kling prompt packages | 可重建，但保留以追溯生成输入 |

## 4. 当前 official 数据入口

| 名称 | 路径 | 规模 | 口径 |
|---|---|---:|---|
| `PIWM-Train-Synth-v1` | `data/official/ms_swift/piwm_train_synth_v1.jsonl` | 2554 SFT examples | Synthetic train，未全量人工视觉 QA，真人导购逻辑 |
| `PIWM-Train-Full-v2` | `data/official/ms_swift/piwm_train_full_v2.jsonl` | 3339 SFT examples | 推荐 fresh SFT 入口，包含 action-selection、continuation、Future Verification |
| `PIWM-Eval-QA-v1` | `data/official/ms_swift/piwm_eval_qa_all_v1.jsonl` | 162 eval rows | QA-reviewed 主评估 |
| `PIWM-WorldModel-v1` | `data/official/ms_swift/piwm_world_model_sft_v1.jsonl` | 218 SFT examples | World Model / Future Verification 小规模证据 |

## 5. 当前最新 checkpoint

最新有效训练 checkpoint：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/data/piwm_results/ms_swift_sft_qwen25vl7b_full_v2_len8192_8gpu/v0-20260502-193050/checkpoint-834
```

口径：

- 框架：ms-swift
- 基座：Qwen2.5-VL-7B-Instruct
- 训练数据：`PIWM-Train-Full-v2`
- 设备：8 GPU
- 产物：LoRA adapter

## 6. 放置规则

- 新视频、新抽帧、新 QA report、新 checkpoint 只放远端数据盘。
- 本地只保留小型 JSONL、Markdown、demo contact sheet 和必要样例。
- 新文档先放入既有 `docs/current/` 或 `docs/contracts/`；过期副本放 `docs/archive/`。
- 外部附件先复制到 `docs/source_materials/<date-topic>/` 并写 source digest，再由 `docs/contracts/` 或 `docs/current/` 消化为执行契约。
- 重复文件不删除，先归档并在最终汇报说明。
- `data/official/` 只保留 canonical manifest、README、official symlink / JSONL；旧 manifest 放 `data/official/archive/`。
