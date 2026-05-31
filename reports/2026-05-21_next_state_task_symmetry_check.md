本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# next_state task 对称性修复确认

日期：2026-05-21

## 结论

当前 frozen 的 A3+ Stage-1 JSONL 里，`next_state_prediction` 任务仍然包含当前顾客状态信息。

它不是只给三张图和候选动作，而是给了：

```text
current visual evidence
current AIDA stage
current BDI: belief / desire / intention
candidate intervention
```

因此，路径 C 如果目标是“修复 task symmetry”，当前 frozen A3+ 数据还没有完成这个目标。A3+ commit 只冻结了 taxonomy loss_weight 和数据可复现性，没有修改 next_state 任务输入契约。

## A. 当前 next_state_prediction 输入字段

检查文件：

```text
data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
```

行数：

```text
train: 1816
val: 185
total: 2001
```

sha256：

```text
train: 3cc6822177f5750dc556742cc3f3a6160a316fd5411217d34ea46ba659431702
val:   36d69862d2d07718f7204aec3fa6e9f49f33cce1f09a0543eb94881f2a06ad68
```

每条 `next_state_prediction` JSONL 顶层字段：

```text
messages
images
task
source_id
weight
loss_weight
meta
```

`meta` 字段包含：

```text
parent_state_id
candidate_action
candidate_act
candidate_params
no_intervention_branch
split
qa_status
human_review_status
viewpoint
```

模型实际看到的输入在 `messages[].content` 里。全量 2001 条 prompt 都包含以下字段：

| 字段 | 出现条数 |
|---|---:|
| `The customer's current state is:` | 2001 |
| `- stage:` | 2001 |
| `- visible evidence:` | 2001 |
| `- engagement pattern:` | 2001 |
| `- gaze and attention:` | 2001 |
| `- body and hands:` | 2001 |
| `- belief:` | 2001 |
| `- desire:` | 2001 |
| `- intention:` | 2001 |
| `Consider one candidate intervention:` | 2001 |
| `Dialogue-act layer for this candidate:` | 2001 |
| `Terminal realization for this candidate:` | 2001 |
| `Concrete execution plan for this candidate:` | 2001 |

所以答案是：

```text
是否包含 current_state: 是，prompt 明文包含 The customer's current state is
是否包含 current_aida_stage: 是，prompt 明文包含 - stage: attention/interest/desire/action
是否包含 current_bdi: 是，prompt 明文包含 belief/desire/intention
```

注意：JSON 顶层没有字段名直接叫 `current_aida_stage` 或 `current_bdi`，但模型输入文本里已经给出了等价信息。

## B. 代码来源

生成入口：

```text
scripts/build_two_stage_training_and_eval.py
```

相关逻辑：

```python
def _next_state_example(row):
    return SFTExample(
        task="next_state_prediction",
        source_id=row["state_id"],
        prompt=build_deliberation_prompt(row),
        target=build_deliberation_target(row),
        ...
    )
```

prompt 构造函数：

```text
piwm_train/prompts.py
```

当前 `build_deliberation_prompt()` 明确读取：

```python
state = record["input"]["current_state_summary"]
bdi = state["bdi"]
```

然后写入 prompt：

```text
The customer's current state is:
- stage: ...
- visible evidence: ...
- engagement pattern: ...
- gaze and attention: ...
- body and hands: ...
- belief: ...
- desire: ...
- intention: ...
```

源数据 `transition_modeling.jsonl` 的 input 也确实包含：

```text
input.current_state_summary.aida_stage
input.current_state_summary.visual_state
input.current_state_summary.intent
input.current_state_summary.intent_tier
input.current_state_summary.bdi
input.candidate_action
input.candidate_action_spec
input.candidate_terminal_realization
```

## C. 这是设计选择还是漏改？

分两层判断：

### 对 A3+ commit 来说

这是保留旧设计，不是 A3+ commit 内部漏改。

A3+ commit 的实际范围是：

```text
1. seek_reassurance / negotiate_price loss_weight = 0.1
2. A3+ intent_label 评估指标分层
3. seed=42 Stage-1 split 和 JSONL 可复现性冻结
```

commit message 没有声明 next_state task symmetry 修改，代码也没有做这件事。

### 对路径 C 来说

如果路径 C 的目标明确是“修复任务对称性”，那么当前状态就是漏掉了关键修改。

当前 next_state task 是：

```text
给定当前状态文本 + 候选动作 → 预测下一状态
```

更对称的路径 C 应该更接近：

```text
给定三张图 + 候选动作 → 预测下一状态
```

或者至少：

```text
给定三张图 + 低泄漏的视觉描述 + 候选动作 → 预测下一状态
```

当前版本会让 next_state_prediction 任务明显更容易，因为模型不需要先从图像中推断当前 stage / BDI，它已经在输入里拿到了这些信息。

## D. 补救方案

### 选项 1：修复 next_state 输入，对称化任务，然后重新 freeze

做法：

1. 修改 `piwm_train/prompts.py`，新增或替换 next_state prompt。
2. 修改 `scripts/build_two_stage_training_and_eval.py`，让 `_next_state_example()` 使用新的低泄漏 prompt。
3. 重新生成 Stage-1 JSONL。
4. 重新跑 sha256 对比和可复现性验证。
5. 新建一个 follow-up commit，例如：

```text
fix Stage-1 next_state task symmetry
```

建议的新输入保留：

```text
images
candidate intervention
candidate act / params
terminal realization
```

建议的新输入移除：

```text
gold current AIDA stage
gold current BDI
gold current intent_label
```

可选保留：

```text
visible evidence / engagement / gaze / body
```

但如果路径 C 真正要测试视觉推理，最好也不要直接给完整 gold visual_state，而是让模型从图像里推断。

影响：

- Stage-1 next_state_prediction 会变难。
- 旧 checkpoint 与新路径 C checkpoint 不可直接公平比较为“只差 A3+”，因为任务定义也变了。
- 论文可以说路径 C 同时修复了 taxonomy weighting 和 transition task leakage/symmetry。

适用场景：

```text
路径 C 的目标是认真验证 Stage-1 world-modeling 能力，而不是只测 taxonomy 权重。
```

### 选项 2：接受现状，只把路径 C 定义为 A3+ taxonomy ablation

做法：

1. 不改 next_state JSONL。
2. 直接用当前 frozen A3+ 数据重训。
3. 报告中明确写：

```text
Path C tests A3+ low-confidence intent-label weighting only.
It does not alter the action-conditioned next-state prediction task contract.
The next-state task remains current-state-conditioned.
```

影响：

- 可以直接重训，工程风险低。
- 不能把路径 C 宣称为“任务对称性修复”。
- 如果 next_state eval 数字很高，仍需要解释：模型输入已经给了当前 stage / BDI。

适用场景：

```text
今晚只想快速测 A3+ taxonomy 是否改善 intent_label，并保留原 Stage-1 world-model task 作为 teacher-forced transition prediction。
```

## 建议

如果路径 C 名义上要解决“为什么 next_state loss / eval 过低、是否任务太简单”的问题，我建议选项 1。

理由：当前 next_state prompt 把当前 stage 和 BDI 直接交给模型，确实会削弱这个任务作为视觉 world model 的证据力。继续用当前数据重训，只能回答 A3+ 对 intent_label 的影响，不能回答 task symmetry 是否修复。

如果今晚时间很紧，也可以先选项 2，但报告和论文 framing 必须同步降级：路径 C 不再叫 task-symmetry fix，只叫 A3+ taxonomy-weighted rerun。

## 本轮未做事项

- 没有修改任何代码。
- 没有重新生成数据。
- 没有启动训练。
- 没有修改 5-act 集合。
