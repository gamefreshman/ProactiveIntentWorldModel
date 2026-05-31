5-act self-check: Greet/Elicit/Inform/Recommend/Hold; Reassure is excluded from operational training/eval.

# PIWM Counterfactual Reasoning Supervision Audit

## Executive Conclusion

当前 Stage-1 的 `next_state_prediction` 确实提供了 **action-conditioned counterfactual supervision**：同一个 parent scene 会被展开成多条样本，每条样本使用同一组三帧图像，但替换成不同 candidate action，并监督不同的 `next_stage / next_bdi / risk / benefit / reward`。这是一种通过数据结构实现的 counterfactual learning，不是显式 contrastive loss。

同时必须明确：当前 A3 full 的 Stage-2 action-selection 评估 **不是** 在推理时枚举候选动作、逐个预测 next_state、再按 reward argmax 选动作；它是 direct action-selection：输入三帧图像 + Stage-1 state 表示 + candidate list，直接输出 best action。仓库里存在 `PIWMDecisionLoop` 这种可枚举候选并做 deliberation 的推理循环，但本轮报告数字没有使用它。

## A. next_state_prediction 数据结构

| Item | Value |
| --- | --- |
| parent records | 543 |
| next_state_prediction rows | 2001 |
| unique parent scene ids with next_state rows | 543 |
| average next_state rows per parent | 3.685 |
| coverage mismatches vs parent candidate_actions | 0 |
| scenes with only one next_state row | 0 |


每个 parent scene 的 next_state 样本数不是固定 5 条，而是等于该 scene 的 candidate action 数。当前分布如下：

| next_state rows per scene | scene count |
| --- | --- |
| 2 | 87 |
| 3 | 59 |
| 4 | 335 |
| 5 | 62 |


核对结论：`transition_modeling.jsonl` 覆盖每个 parent record 的 **全部 candidate_actions**，不是只覆盖 best_action + 1-2 个 negatives。`sum(candidate_actions)` 也等于 2001，与 next_state rows 完全一致。

### Candidate act coverage in next_state rows

| Candidate act | Rows |
| --- | --- |
| Elicit | 476 |
| Hold | 449 |
| Inform | 481 |
| Recommend | 595 |


注意：general Stage-1 的 next_state 里当前没有 `Greet`，因为 general 543 parent 的 best/candidate 生成本身没有 Greet；Greet 主要靠 target/GreetAug 的 Stage-2 action-selection 学。

### Current parent AIDA distribution

| AIDA stage | Parent count |
| --- | --- |
| action | 77 |
| attention | 49 |
| desire | 128 |
| interest | 289 |


### next_stage outcomes by candidate act

| Candidate act | attention | interest | desire | action |
| --- | --- | --- | --- | --- |
| Elicit | 0 | 0 | 430 | 46 |
| Hold | 128 | 291 | 14 | 16 |
| Inform | 0 | 0 | 481 | 0 |
| Recommend | 447 | 0 | 68 | 80 |


## B. Concrete Scene Dump

Example parent scene: `piwm_09df40aae2`. Current parent label: stage=`interest`, intent=`request_demonstration`. Candidate actions in parent record: `Elicit_b1166d372e5e, Inform_5ff00ba15ca5, Hold_eda24b4bb712, Recommend_8d7f8993e333`.

| candidate_action | act | params | gold next_stage | risk | benefit | reward | next_belief | next_desire | next_intention |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Elicit_b1166d372e5e | Elicit | {"openness": "open", "slot": "need_focus"} | desire | low | high | 0.83 | The salesperson may help resolve the decision. | explore available options | continue browsing and comparing |
| Hold_eda24b4bb712 | Hold | {"mode": "silent"} | interest | low | low | 0.20 | Several options remain worth comparing. | see how the product works | ask for a demonstration |
| Inform_5ff00ba15ca5 | Inform | {"content_type": "demo", "depth": "brief"} | desire | low | high | 0.80 | The salesperson may help resolve the decision. | explore available options | continue browsing and comparing |
| Recommend_8d7f8993e333 | Recommend | {"target": "item", "pressure": "soft"} | attention | medium | low | -0.30 | The salesperson may be applying too much pressure. | avoid further engagement | leave without buying |


这个例子显示，同一场景下：Elicit 和 Inform 都推进到 `desire`，Hold 保持在 `interest`，Recommend 触发回退到 `attention` 并给负 reward。这就是当前数据里最直接的 counterfactual supervision。

## C. Counterfactual Supervision Coverage

| Question | Answer |
| --- | --- |
| 543 parent records 是否都有 next_state supervision? | 是，543/543。 |
| 每个 parent 是否都有 multiple counterfactual options? | 是，最少 2 条，最多 5 条；没有单候选 parent。 |
| 是否覆盖所有 candidate actions? | 是，coverage mismatch=0。 |
| 平均每个 scene 几条 next_state samples? | 3.685。 |
| 训练/验证 split | train=1816 next_state rows, val=185 next_state rows。 |


## D. Training 是否有效利用 counterfactual supervision

ms-swift 的 SFT 训练本质上仍是 token cross-entropy：模型读入 user prompt，生成 assistant target。counterfactual 信号来自样本组织方式：同一个 `parent_state_id` 的三帧图片重复出现多次，但 `candidate_action` 不同，target 里的 `next_stage / next_bdi / reward` 也不同。

Path C 修复后，next_state prompt 不再提供 gold current stage / intent / BDI，而是明确写着 “Use the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.” 代码位置：`piwm_train/prompts.py:122-164`。Stage-1 构造入口在 `scripts/build_two_stage_training_and_eval.py:239-242`，next_state 样本 meta 记录 candidate action 和 parent_state_id 的位置在 `scripts/build_two_stage_training_and_eval.py:268-285`。

因此，当前实现是 **implicit counterfactual learning through repeated action-conditioned examples**，不是 explicit pairwise loss、contrastive loss 或 reward-ranking loss。

## E. 当前 inference 是否使用 counterfactual planning

结论：**A3 full 报告里的 Stage-2 action-selection 评估没有使用 counterfactual planning。**

- A3 full 使用 `scripts/eval_ms_swift_checkpoint.py` 直接对 `action_selection_5act` rows 生成 `<chosen>...</chosen>`；parser 只校验候选 label 是否属于该 row 的 candidate list。证据：`scripts/eval_ms_swift_checkpoint.py:64-85` 和 `:112-134`。

- Stage-2 action prompt 使用 `build_action_prompt_no_leak()`，输入包含 Stage-1 state 表示、candidate action identity/params/realization，但明确不包含 gold rewards、predicted next states、risks 或 benefits。证据：`piwm_train/prompts.py:320-356`。

- 仓库中的 `PIWMDecisionLoop` 确实有枚举 candidates、逐个跑 deliberation/continuation、再 action selection/fallback to highest predicted reward 的逻辑。证据：`piwm_infer/decision_loop.py:99-191`。但这个 loop 不是当前 A3 full target test 指标的执行路径。

论文写法建议：可以说 Stage-1 训练了 action-conditioned world model / counterfactual next-state predictor；不能把当前 A3 full 指标写成 “decision-time world-model planning result”，除非后续真的用 `PIWMDecisionLoop` 或等价 rollout evaluator 跑一组结果。

## F. Source Files Audited

| File | Role | Rows / note |
| --- | --- | --- |
| `data/official/piwm_train_synth_v2/main_schema.jsonl` | parent scene schema | 543 |
| `data/official/piwm_train_synth_v2/transition_modeling.jsonl` | next_state counterfactual source | 2001 |
| `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | Stage-1 combined ms-swift entrypoint | 543 user_intent + 2001 next_state |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl` | next_state train split | 1816 |
| `data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl` | next_state val split | 185 |
| `scripts/eval_ms_swift_checkpoint.py` | current checkpoint eval path | direct generation, not rollout planning |
| `piwm_infer/decision_loop.py` | available rollout-style loop | not used for A3 full metric |
