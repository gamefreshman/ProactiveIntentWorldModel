5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# Zero-shot Qwen LoRA 加载 bug 审计与修复

## 一句话结论

确认存在 bug：2026-05-25 主表上一版的 Zero-shot Qwen 在 Dim 3 / Trick 6 路径中实际加载了 PIWM LoRA adapter。已做最小修复：在 `scripts/run_trick6_counterfactual_planning.py` 增加 `--no-lora`，并只重跑 zero-shot 的 Dim 3 与 Trick 6 A/B。

## Step 1：raw artifact 审计

| artifact | 文件 | checkpoint 字段 | 结论 |
|---|---|---|---|
| Dim 1/2 zero-shot | `reports/rerun_eval_20260525/base_qwen25vl7b_user_intent_60.json` | `null` | 正确，未加载 LoRA |
| Dim 3 zero-shot（旧） | `reports/rerun_eval_20260525/base_qwen25vl7b_dim3_current_state.json` | PIWM `checkpoint-500` | 错误，加载了 PIWM LoRA |
| Trick 6 Reward A zero-shot（旧） | `reports/rerun_eval_20260525/base_qwen25vl7b_trick6_rewardA_stage_advance.json` | PIWM `checkpoint-500` | 错误，加载了 PIWM LoRA |
| Trick 6 Reward B zero-shot（旧） | `reports/rerun_eval_20260525/base_qwen25vl7b_trick6_rewardB_model_score.json` | PIWM `checkpoint-500` | 错误，加载了 PIWM LoRA |

PIWM checkpoint 路径：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500
```

## Step 1.2：脚本加载逻辑对比

`scripts/eval_ms_swift_checkpoint.py` 的 zero-shot 逻辑是正确的：

```text
lines 231-238:
if args.checkpoint is not None:
    model = PeftModel.from_pretrained(base, args.checkpoint)
    checkpoint = str(args.checkpoint)
else:
    model = base
    checkpoint = None
```

并且 CLI 默认：

```text
line 439:
parser.add_argument("--checkpoint", type=Path, default=None)
```

所以不传 `--checkpoint` 时，Dim 1/2 会使用 base Qwen。

`scripts/run_trick6_counterfactual_planning.py` 的模型加载函数本身支持无 LoRA：

```text
line 105:
model = PeftModel.from_pretrained(base, args.checkpoint) if args.checkpoint else base
```

但 CLI 默认 checkpoint 是 PIWM checkpoint：

```text
old behavior:
parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/a3_full_targetv2_balanced_3epoch_v1/.../checkpoint-500"))
```

因此不传 `--checkpoint` 并不会进入 base 分支，而是加载默认 PIWM LoRA。这就是 Dim 3 / Trick 6 zero-shot 被污染的根因。

## Step 2：最小修复

修改文件：

```text
scripts/run_trick6_counterfactual_planning.py
```

修复范围：

```text
line 791:
parser.add_argument("--no-lora", action="store_true", help="Load the base model only; ignore --checkpoint for zero-shot evaluation.")

lines 807-810:
if args.no_lora:
    args.checkpoint = None
elif not args.checkpoint.is_absolute():
    args.checkpoint = REPO_ROOT / args.checkpoint

lines 460, 528:
"checkpoint": str(args.checkpoint) if args.checkpoint else None
```

说明：这是最小修复，没有改 prompt、metric、候选枚举、reward 函数或 PIWM 主模型路径。

## Step 2 dry run 验证

在 A100 上用 `--no-lora` 跑 1 条 Dim 3：

```text
/root/lanyun-fs/ProactiveIntentWorldModel/reports/rerun_eval_20260525/zero_shot_no_lora_dryrun_dim3_1.json
```

验证结果：

| 检查项 | 结果 |
|---|---|
| artifact checkpoint | `null` |
| dry-run 输出是否与 PIWM 第一条完全相同 | 否 |
| dry-run parse | 失败，base model 未按 next_state tag 输出 |

对照证据：

```text
dryrun checkpoint None
dryrun raw MalformedOutputError: expected exactly one next_stage tag, found 0
piwm raw <next_stage>interest</next_stage>...
same? False
```

因此可以确认 adapter 已关闭。

## Step 3：重跑 zero-shot Dim 3 / Trick 6

输出文件：

```text
reports/rerun_eval_20260525/zero_shot_qwen_dim3_fixed.json
reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_a_fixed.json
reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_b_fixed.json
```

远端日志：

```text
reports/rerun_eval_20260525/logs/zero_shot_fixed.master.log
reports/rerun_eval_20260525/logs/zero_shot_qwen_dim3_fixed.log
reports/rerun_eval_20260525/logs/zero_shot_qwen_trick6_reward_a_fixed.log
reports/rerun_eval_20260525/logs/zero_shot_qwen_trick6_reward_b_fixed.log
```

完成时间：

```text
[2026-05-24_19:42:21] START zero-shot fixed no-lora
[2026-05-24_19:49:13] DONE dim3
[2026-05-24_19:56:36] DONE trick6 A
[2026-05-24_20:04:02] DONE trick6 B
[2026-05-24_20:04:03] ALL DONE zero-shot fixed
```

## 修复前后数字对比

| 指标 | 修复前 | 修复后 | 备注 |
|---|---:|---:|---|
| Dim 3 next-stage strict macro F1 | 0.565 | 0.108 | 修复后 parse rate 只有 0.250 |
| Dim 3 parsed-only macro F1 | 0.599 | 0.269 | parsed-only，不作为主表 strict 数字 |
| Trick 6 Reward A macro F1 | 0.171 | 0.247 | candidate parse rate 0.262 |
| Trick 6 Reward B macro F1 | 0.265 | 0.372 | candidate parse rate 0.262 |

## 更新的文件

- `scripts/run_trick6_counterfactual_planning.py`
- `reports/2026-05-25_rerun_evaluation_main_table.md`
- `reports/2026-05-24_paper_writing_materials.md`
- `reports/rerun_eval_20260525/zero_shot_qwen_dim3_fixed.json`
- `reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_a_fixed.json`
- `reports/rerun_eval_20260525/zero_shot_qwen_trick6_reward_b_fixed.json`

## 状态

A100 运行结束后 GPU 状态：

```text
GPU0: 0 MiB, 0%
GPU1: 0 MiB, 0%
```

没有继续占用 GPU 的 tmux session。
