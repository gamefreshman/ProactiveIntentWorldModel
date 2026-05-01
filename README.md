# PIWM — Proactive Intent World Model

PIWM 是一个面向**线下零售第三人称导购**场景的多模态主动 agent 研究项目。
它把同一个 VLM 当作 internal simulator：先识别顾客状态，再为每个候选话术
动作预测后果，最后决定**是否开口、何时开口、说什么**。

> 数据管线与 SFT/评测脚本已随 sprint 迭代；文档入口统一见 [`docs/README.md`](docs/README.md)。

## 三层结构

```
Perception   →  从视觉 cue 推断  AIDA 阶段 + BDI（belief / desire / intention）
Deliberation →  对每个候选动作预测  next AIDA + next BDI + risk + benefit + reward
Action       →  比较 rollouts，选最优动作（包括沉默）
```

视觉输入是**多视角店内观察**（multi-view in-store visual observations）。
主设置是导购可观察视角（`salesperson_observable`）；监控/第三方视角与第一
人称视角保留作 view-shift 评估。详见 [`docs/contracts/visual_input_contract.md`](docs/contracts/visual_input_contract.md)。

## 目录速览

```
piwm_data/       数据管线（schema、规则层、loader、exporter）
piwm_train/      ms-swift / LoRA SFT 适配与训练入口
piwm_infer/      推理侧解析与工具
scripts/         sampler / prompt_builder / qa_gate / eval 辅助脚本
kling/           Kling API 调用（Node.js）
docs/            阅读入口见 docs/README.md（current / contracts / background / archive）
paper/           论文草稿
data/            本地生成 manifest、数据集与实验结果（大文件见 .gitignore）
RESEARCH_LOG.md  动态索引与 sprint 进度
```

## 5 分钟 quickstart

```bash
# 1. 跑测试
python3 -m pytest

# 2. 生成场景 manifest（含 viewpoint）
python3 -m scripts.scenario_sampler \
  --out data/scenario_manifest.jsonl \
  --stats-out data/_scenario_stats.json

# 3. 生成 10 条 mixed-view 人工审阅用 Kling prompt（dry-run，不调用 Kling）
python3 -m scripts.scenario_sampler \
  --out data/scenario_manifest_review10.jsonl \
  --stats-out data/_scenario_stats_review10.json \
  --limit 10 --balanced-cues
python3 -m scripts.prompt_builder \
  --manifest data/scenario_manifest_review10.jsonl \
  --out-root Archive_prompts_viewpoint_review \
  --overwrite

# 4. （可选）用 fixture 走通端到端 dry-run
node kling/generate_session.js \
  --prompt piwm_data/tests/fixtures/tiny_session/session_test_001/prompt.json \
  --out-root Archive_generated \
  --dry-run
```

## 文档导航

**唯一结构化索引：** [`docs/README.md`](docs/README.md)（按 current / contracts / background 分层）。

速查：

| 入口 | 何时看 |
|---|---|
| [`docs/README.md`](docs/README.md) | 不知道从哪份文档读起 |
| [`RESEARCH_LOG.md`](RESEARCH_LOG.md) | 最新进度、索引与高密度更新 |
| [`docs/contracts/claim_to_artifact_audit.md`](docs/contracts/claim_to_artifact_audit.md) | 论文 claim 与代码 / 数据工件对应 |
| [`docs/contracts/world_model_supervision_contract.md`](docs/contracts/world_model_supervision_contract.md) | World Model 监督字段与边界 |
| [`docs/contracts/visual_input_contract.md`](docs/contracts/visual_input_contract.md) | 多视角、抽帧、QA gate |
| [`docs/contracts/docs_maintenance_rules.md`](docs/contracts/docs_maintenance_rules.md) | 新增或归档文档前必读 |
| [`docs/contracts/expert_provenance_upgrade_plan.md`](docs/contracts/expert_provenance_upgrade_plan.md) | 专家规则 provenance |

## 当前状态（高频更新）

实时数字看 `RESEARCH_LOG.md` 顶部条目；不要在本 README 里复述测试通过数。

## License

待补。本仓库当前为研究内部草稿。
