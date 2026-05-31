# piwm score 字段重命名报告

日期：2026-05-21

## 结论

已在轻量 `piwm` 仓库创建分支 `codex/ordinal-score-rename`，把动作排序字段从容易混淆的 `score` 改为 `ordinal_score`。这次改动只处理 piwm 仓库内部的 1–5 档位分，不改变主项目 `ProactiveIntentWorldModel` 的 `preference_score` / `reward` 语义。

## 为什么改

piwm 的旧 `score` 是 1–5 整数，表示同一条样本内部哪个候选动作更好；主项目的 `preference_score` / `reward` 是连续浮点数，表示规则或偏好模型里的强弱程度。两个字段如果都叫 score，后续 import 时很容易被解析成同一类分数，造成静默污染。

## 实际数据状态

检查后发现：当前 piwm 共有 318 个 labeled 文件、1062 个 outcome。不是所有文件都有旧 `score`：

| 项目 | 数量 |
|---|---:|
| labeled 文件 | 318 |
| outcome 总数 | 1062 |
| 本次从 `score` 重命名为 `ordinal_score` 的 outcome | 590 |
| 涉及 labeled 文件 | 200 |
| 仍保留 `preference_score` 的 outcome | 747 |
| 迁移后残留 outcome.`score` | 0 |

说明：118 个文件原本没有旧 `score`，只有 `preference_score` 或其他扩展字段。本次没有把 `preference_score` 强行换算成 `ordinal_score`，避免制造新的语义混淆。

## 改动内容

1. 数据字段重命名
   - `data/labeled/piwm_700.json` 到 `data/labeled/piwm_899.json` 中已有 outcome.`score` 全部改为 outcome.`ordinal_score`。
   - 迁移后 `data/labeled/` 下没有 outcome.`score` 残留。

2. 生成脚本更新
   - `script/gen_scores.py`：后续补分只写 `ordinal_score`，LLM 输出格式改为 `ordinal_scores`。
   - `script/gen_deliberation.py`：新生成 labeled 数据只输出 `ordinal_score`。
   - `script/gen_sft.py`：Stage-2 训练样本输出 `ordinal_score`，不再输出 `score`。

3. adapter 新增
   - 新增 `script/score_adapter.py`。
   - 提供候选转换：`preference_score = (ordinal_score - 1) / 4.0`。
   - 该公式只保留 1–5 档位的排序信息，不代表 piwm 的 `ordinal_score` 等同主项目连续 `preference_score`。主项目实际 import 时仍需 PI 明确确认。

4. 文档同步
   - 更新 `README.md`、`docs/schema.md`、`docs/pipeline.md`、`docs/training.md`、`docs/action_prompt.md`、`docs/sample_action.json`、`docs/design.md`、`docs/index.md`、`docs/usage.md`。
   - 文档中明确写入：`ordinal_score` 不等同于主项目 `preference_score` / `reward`，不能直接对接。

## 验证结果

已完成以下检查：

```bash
python3 -m py_compile script/gen_scores.py script/gen_sft.py script/gen_deliberation.py script/score_adapter.py
python3 script/gen_sft.py --dry-run --stage 2 --id piwm_818
python3 script/gen_scores.py --dry-run
python3 -m json.tool docs/sample_action.json >/dev/null
rg -n '"score"\s*:' --glob '!reports/**' .
git diff --check
```

关键结果：

- `gen_sft.py --dry-run --stage 2 --id piwm_818` 输出的 assistant JSON 已使用 `ordinal_score`。
- `gen_scores.py --dry-run` 显示仍有 118 个文件缺少 `ordinal_score`，这些文件原本也没有旧 `score`，需要后续用 LLM 补分或由 PI 决定是否不补。
- `rg -n '"score"\s*:' --glob '!reports/**' .` 无结果，说明源码、文档和数据中没有 JSON 风格的 `"score":` 字段残留。
- `git diff --check` 通过。

## PR 状态

已提交并推送到 piwm 仓库分支：

```text
codex/ordinal-score-rename
```

本机没有可用的 GitHub CLI 登录态，无法在命令行里直接创建 PR。可用下面的 GitHub 创建页发起同事审核：

```text
https://github.com/guochenmeinian/piwm/pull/new/codex/ordinal-score-rename
```

PR 标题建议：

```text
Rename piwm ordinal score field
```

PR 合并前需要同事重点看两点：

1. 是否接受 `ordinal_score` 作为 piwm 1–5 档位字段的正式名称。
2. 是否接受 `script/score_adapter.py` 只作为候选 import adapter，而不是默认把 piwm 分数等同主项目 `preference_score`。
