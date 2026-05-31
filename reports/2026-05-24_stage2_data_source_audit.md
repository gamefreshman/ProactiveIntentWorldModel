本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Stage-2 action_selection 数据来源审计

生成时间：2026-05-24  
范围：只审计，不修改任何数据、不重生成 JSONL、不改训练代码。  
当前主线：3-frame v2.2 数据；Stage-2 使用 `GreetAug-v2`。

## 1. 结论

当前最新 Stage-2 action-selection 监督入口是：

`data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl`

它一共 **86 条**，来源非常清楚：

| 来源 | 数量 | 说明 |
|---|---:|---|
| target-frontcam train | 71 | 来自 `PIWM-Target-Frontcam-v1` 清洗后的 Stage-2 train |
| general GreetAug-v2 | 15 | 从 general attention-stage state 合成的 Greet 增强样本 |
| 其他来源 | 0 | 未发现第三来源 |

所以答案是：**当前 86 条 = 71 条 target Stage-2 train + 15 条 GreetAug-v2；没有其他来源。**

当前 86 条 best_act 分布：

| Act | Count |
|---|---:|
| Inform | 41 |
| Greet | 26 |
| Elicit | 14 |
| Recommend | 5 |
| Hold | 0 |

QA 状态：

| QA status | Count |
|---|---:|
| synthetic_unreviewed | 71 |
| synthetic_augmented_unreviewed | 15 |

这说明当前 Stage-2 train 不是人工 QA-pass 数据；人工 QA-pass 的是 30 条 held-out target test，不是 train。

## 2. 当前 86 条来自哪里

审计文件：

`data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl`

基础 Stage-2 target train：

| 项 | 值 |
|---|---:|
| 行数 | 71 |
| task | action_selection_5act |
| source prefix | target=71 |
| augmentation_policy | none=71 |
| qa_status | synthetic_unreviewed=71 |

best_act 分布：

| Act | Count |
|---|---:|
| Inform | 41 |
| Elicit | 14 |
| Greet | 11 |
| Recommend | 5 |
| Hold | 0 |

审计文件：

`data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl`

增强后 Stage-2 train：

| 项 | 值 |
|---|---:|
| 行数 | 86 |
| target rows | 71 |
| general_greet_aug rows | 15 |
| 其他来源 | 0 |

best_act 分布：

| Act | Count |
|---|---:|
| Inform | 41 |
| Greet | 26 |
| Elicit | 14 |
| Recommend | 5 |
| Hold | 0 |

这个文件只是在 71 条 target train 后追加了 15 条 general-domain Greet 样本，用于补 Greet 监督。它没有补 Hold，也没有补 Recommend。

## 3. general 543 parent records 的 best_act 情况

审计文件：

`data/official/piwm_train_synth_v2/main_schema.jsonl`

general parent records 一共 **543 条**。每条都有 `best_action_spec`，也就是都有可投影成 action-selection 的 best_act 标签。

分布如下：

| Act | Count |
|---|---:|
| Elicit | 252 |
| Recommend | 125 |
| Inform | 105 |
| Hold | 61 |
| Greet | 0 |
| Reassure | 0 |

QA 状态：

| 字段 | 分布 |
|---|---|
| qa_status | 543 条全是 null |
| human_review_status | 543 条全是 null |
| 数据性质 | synthetic train pending visual QA |

兼容性分级：

| Tier | Count |
|---|---:|
| green | 462 |
| red | 81 |

按兼容性拆 best_act：

| Tier | Elicit | Recommend | Inform | Hold | Total |
|---|---:|---:|---:|---:|---:|
| green | 200 | 125 | 78 | 59 | 462 |
| red | 52 | 0 | 27 | 2 | 81 |

因此，general 543 不是没有动作标签，而是已有合成动作偏好标签；问题是这些标签并未进入当前 Stage-2 action-selection 训练。

## 4. general 为什么没有投影到 action_selection

代码入口：

`scripts/build_two_stage_training_and_eval.py`

当前 pipeline 的逻辑是：

1. Stage-1 从 general 生成两类任务：
   - `user_intent`
   - `next_state_prediction`

2. Stage-2 action-selection 只从 target 的 `policy_preference.jsonl` 生成：
   - 先清洗 target 5-act；
   - 再选出 balanced 30 条 test；
   - 剩余 71 条作为 train。

3. general 只额外提供 15 条 GreetAug-v2：
   - 这些不是从 general 原始 best_action 投影来的；
   - 而是从 attention-stage general state 合成 opening Greet 行。

关键代码行为：

| 行为 | 代码含义 |
|---|---|
| `_build_stage1_examples(general_dir)` | 只读 `state_inference.jsonl` 和 `transition_modeling.jsonl` |
| `stage2_target = [_action_example(row) for row in train_policy_rows]` | Stage-2 只用 target policy rows |
| `_build_general_greet_aug_policy_rows(...)` | 只额外合成 Greet augmentation，不导入 general 全量 policy |

这看起来是一个设计选择，不是数据缺失：之前把 general 定位为 Stage-1 的状态理解和世界模型训练，把 target 定位为 Stage-2 的目标域动作选择训练。

但代价也很明显：Stage-2 的动作监督量非常小，尤其：

| Act | 当前 Stage-2 GreetAug-v2 |
|---|---:|
| Inform | 41 |
| Greet | 26 |
| Elicit | 14 |
| Recommend | 5 |
| Hold | 0 |

这会导致 Recommend 和 Hold 在 Stage-2 几乎没有直接监督。

## 5. 如果 general 也参与 action_selection，会怎样

如果把 general 543 全部投影进 Stage-2 action-selection，那么当前 86 条加上 general 543 条后，总量会变成 **629 条**。

预计分布：

| Act | 当前 86 | + general 543 后 |
|---|---:|---:|
| Elicit | 14 | 266 |
| Inform | 41 | 146 |
| Recommend | 5 | 130 |
| Hold | 0 | 61 |
| Greet | 26 | 26 |
| Total | 86 | 629 |

如果只用 general 的 green tier 462 条，则总量会变成 **548 条**。

预计分布：

| Act | 当前 86 | + general green 462 后 |
|---|---:|---:|
| Elicit | 14 | 214 |
| Recommend | 5 | 130 |
| Inform | 41 | 119 |
| Hold | 0 | 59 |
| Greet | 26 | 26 |
| Total | 86 | 548 |

收益很直接：

- Elicit 监督从 14 条升到 214-266 条。
- Recommend 监督从 5 条升到 130 条。
- Hold 监督从 0 条升到 59-61 条。

风险也直接：

- general 是 `salesperson_observable` 视角，不是 target-frontcam 视角。
- general 的 actor_profile 是 `human_salesperson_logic`，不是 target terminal logic。
- general 未人工 QA-reviewed。
- 如果把它当 Stage-2 target action-selection 主监督，论文里必须明确这是 cross-domain synthetic action supervision，而不是 target-domain gold supervision。

## 6. 三种方案评估

### 方案 A：不动 general，只 import 同事 Hold + Recommend

PI 前提：总监督约 **175 条**。当前仓库内还没看到这批同事 Hold + Recommend 的 official 文件，因此这里按“当前 86 + 外部新增约 89 条”评估。

优点：

- 最符合当前 domain-specialization 故事：Stage-2 仍然主要是 target/frontcam/同事补充数据。
- 不把 general 的 human-salesperson 逻辑直接混入 target action-selection。
- 工程量最低，数据边界最干净。
- 对当前痛点最直接：补 Hold 和 Recommend，而不是继续补 Inform。

风险：

- 总量仍然偏小，175 条对 5-act 来说只是 minimal viable scale。
- 如果同事数据也不是 QA-reviewed，论文中仍需标 synthetic / unreviewed。
- 如果只补 Hold + Recommend，Elicit 仍只有 14 条，可能成为下一轮短板。

适合用途：

- 作为近期主线，优先验证 Stage-2 是否能明显超过 random baseline。
- 适合今晚或短期训练，不需要大改 pipeline。

建议：

**优先执行。** 这是当前风险最低、最贴近已拍板方向的方案。

### 方案 B：import 同事 + 从 general 抽部分高质量样本进 Stage-2

建议抽样原则：

- 只从 compatibility_tier=green 的 462 条里抽。
- 优先抽当前 target 最缺的 act：
  - Hold
  - Recommend
  - Elicit
- 不抽 red。
- 不抽 Greet，因为 general 本身没有 Greet best labels；Greet 继续由 target + GreetAug 支撑。

可行规模：

- 当前 86
- 同事新增后约 175
- 再从 general green 抽 100-150 条
- 总量约 275-325 条

优点：

- 明显提高 Stage-2 action-selection 监督量。
- 可以把 Recommend 从 5 条提升到几十条以上。
- 可以补 Hold=0 的硬缺口。
- 比全量 general 风险小，论文中可以说是 curated synthetic action supervision。

风险：

- 需要新增筛选脚本、抽样策略、manifest 记录和 ablation。
- general 仍然不是 target-frontcam，仍有 domain gap。
- 如果筛选标准写不清，reviewer 会质疑 cherry-picking。

适合用途：

- 作为 A 之后的增强版主实验或 ablation。
- 适合写成 “curated general-to-target action supervision”。

建议：

**作为中期方案。** A 跑完如果仍低于 baseline 或 Hold/Recommend 仍弱，就上 B。

### 方案 C：全 general 进 Stage-2

规模：

- 当前 86 + general 543 = 629 条。

分布：

| Act | Count |
|---|---:|
| Elicit | 266 |
| Inform | 146 |
| Recommend | 130 |
| Hold | 61 |
| Greet | 26 |

优点：

- 数据量最大。
- Recommend / Elicit / Hold 监督立刻充足。
- 工程上不难，只需要把 general policy rows 转成 action_selection_5act。

风险：

- general 未 QA-reviewed。
- general 是 human-salesperson logic，可能和 target terminal logic 冲突。
- general 没有 Greet，Greet 仍然只靠 26 条。
- 会把 Stage-2 从“target adaptation”变成“mixed-domain action SFT”，论文故事要重写。
- 如果效果变好，难解释是 target adaptation 变好，还是 general action labels 变多导致的。
- 如果效果变差，难定位是 domain gap、标签质量、还是动作分布污染。

适合用途：

- 作为 ablation 或 upper-bound，不建议作为主线。

建议：

**暂不作为主实验。** 除非 A/B 都失败，再用 C 做诊断性实验。

## 7. 推荐决策

当前我建议：

1. **先执行方案 A。**
   - import 同事 Hold + Recommend。
   - 目标是把当前 86 条提升到约 175 条。
   - 这是最符合当前研究叙事的动作。

2. **同时准备方案 B 的 dry-run。**
   - 从 general green 里抽取高质量 action-selection 候选。
   - 暂不并入主训练。
   - 等 A 的 quick probe 结果出来后决定是否启用。

3. **不要直接做方案 C。**
   - 全 general 进 Stage-2 会把问题变大。
   - 它适合做 ablation，不适合作为当前主线。

一句话：**A 是当前主线，B 是后备增强，C 是诊断性上界，不应直接成为主实验。**

## 8. 审计证据摘要

关键文件：

| 文件 | 行数 | sha256 |
|---|---:|---|
| `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | 71 | `ebbc6ae2f012bd90f9bce4204517d6ae9544e3dd8947aa89fe87939f598b5529` |
| `data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl` | 86 | `ee9fac6411a60234aaac36bae01ec9e8926ab42001bf34e1418804161af421fa` |
| `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl` | 3232 | `e2c2879fe04371a4cdfefda241e1dc9b8f3af769286ae9d2c12c51bc50418824` |
| `data/official/piwm_train_synth_v2/main_schema.jsonl` | 543 | `391d05fa5d3e85eb6f16a0bc612fc8027286646792439f5e6317fb14f1542267` |
| `data/official/piwm_train_synth_v2/policy_preference.jsonl` | 543 | `d9fd33d3c51ff121dd7c16892d7857cf3a2700884de96663817380d1cd790c02` |

当前明确边界：

- 5-act 不变：Greet / Elicit / Inform / Recommend / Hold。
- Reassure 不进入 operational training / eval / inference。
- 当前 Stage-2 train 86 条不是 QA-reviewed。
- 30 条 target test 已是 held-out QA-reviewed pass，不应混入 train。
- general 543 都有 best_act，但它们是合成标签，未做视觉 QA。

