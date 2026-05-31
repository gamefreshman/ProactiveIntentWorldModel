# PIWM Two-Stage Domain Specialization Plan

更新时间：2026-05-19 CST

本文是当前 EMNLP 口径下的训练和评估入口。核心故事是：先在 general retail 数据上学习用户意图世界模型，再用少量 target-frontcam 智能售货机视频做 5-act 目标域动作适配。当前不使用 200 条 video-pending prompt-ready 样本，也不把 realshoot manifest 当作真实视频结果。

## Current Data Entrypoints

| Role | Official file | Rows | Tasks | Notes |
|---|---|---:|---|---|
| Stage-1 full export | `data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl` | 2544 | user_intent=543, next_state_prediction=2001 | full general export; use split files below for training/validation |
| Stage-1 train | `data/official/piwm_train_synth_v2/user_intent_train.jsonl` + `data/official/piwm_train_synth_v2/next_state_prediction_train.jsonl` | 2309 | user_intent=493, next_state_prediction=1816 | seed=42 AIDA-stratified parent split |
| Stage-1 val | `data/official/piwm_train_synth_v2/user_intent_val.jsonl` + `data/official/piwm_train_synth_v2/next_state_prediction_val.jsonl` | 235 | user_intent=50, next_state_prediction=185 | seed=42 AIDA-stratified parent split |
| Stage-2 target train | `data/official/ms_swift/piwm_train_stage2_target_5act_v1.jsonl` | 71 | action_selection_5act=71 | clean 5-act train split; excludes best=`Reassure` rows and filters `Reassure` candidates |
| Joint baseline | `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_v1.jsonl` | 2615 | Stage-1 general + Stage-2 target action-selection | simple pooled baseline for the revised two-stage setup |
| Target 5-act eval | `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl` | 90 | user_intent=30, next_state_prediction=30, action_selection_5act=30 | balanced 30-record 5-act test; project-lead QA-reviewed pass |
| General eval | `data/official/domain_specialization_eval_v2/general_qa_stage1_all.jsonl` | 162 | user_intent=36, next_state_prediction=126 | existing general QA subset in revised Stage-1 format |

Build command:

```bash
python3 -m scripts.build_two_stage_training_and_eval
```

Official target split validation:

```bash
python3 -m scripts.check_target_frontcam_split
```

The build summary is:

```text
data/official/domain_specialization_eval_v2/two_stage_eval_summary.md
```

## Stage-1: User Intent World Modeling

Stage-1 trains the model to read the customer state before deciding any action.

Input:

```text
3 chronological frames
plain scene description, e.g. "顾客在零售店内。" or "顾客在智能售货机前。"
```

Output:

```text
AIDA stage
intent_label
visible evidence on three axes
BDI: belief / desire / intention
```

The Stage-1 prompt explicitly says not to choose a sales action and not to output candidate actions, rewards, or recommendations.

Stage-1 also includes action-conditioned next-state prediction through `next_state_prediction` rows. This is not an unconditioned natural-future task. The model predicts next BDI / next stage after a specified candidate action. `Hold(mode=silent)` rows are the no-intervention branch.

Main metrics:

- AIDA stage accuracy and macro F1.
- intent_label accuracy and macro F1.
- next_stage accuracy and macro F1.
- BDI generation is reported qualitatively in examples or appendix.

## Stage-2: Sales Action World Modeling

Stage-2 trains 5-act target-frontcam action selection.

Main policy space:

```text
Greet, Elicit, Inform, Recommend, Hold
```

`Recommend` keeps `pressure=soft/firm` in action params. `Reassure` is not counted in the main macro F1 and must be absent from operational training, eval, inference, and runtime export. It remains available only as a historical/source label and compatibility boundary.

The new action-selection prompt is leakage-free. It contains:

- 3 frames;
- the Stage-1 customer-state representation;
- candidate act + params;
- terminal or salesperson realization, such as surface text, screen behavior, voice style, light, physical action, utterance.

It does not contain:

- reward;
- risk;
- benefit;
- predicted_next_stage;
- next_state;
- any gold outcome.

Revised balanced 5-act split check:

```text
target records: 118
minus best=Reassure records: 17
empty rows after Reassure candidate filtering: 0
clean 5-act records: 101
balanced target test records: 30
target Stage-2 5-act train records: 71
target test best-act counts: Greet=6, Elicit=6, Inform=6, Recommend=6, Hold=6, Reassure=0
```

The balanced 5-act test is video-backed. Its current QA status is:

```text
qa_reviewed_pass: 30
```

So paper text may describe it as a balanced, video-backed, project-lead QA-reviewed target eval. The full `PIWM-Target-Frontcam-v1` corpus remains 118 video-backed records and is not a full human-QA-reviewed corpus. In the revised main experiment, `Reassure` rows are kept in the raw corpus for source/compatibility analysis but are not used as 5-act action-selection training or evaluation examples.

Stage-2 action-selection rows now carry inverse-frequency label weights so the small target train split does not let `Inform` dominate the loss. Current Stage-2 train best-act counts are `Inform=41 / Elicit=14 / Greet=11 / Recommend=5`; the exported weights are `Inform=0.432927 / Elicit=1.267857 / Greet=1.613636 / Recommend=3.55`. The default can be changed through `act_balancing=none|inverse_freq|oversample_minority` in the data-collator/export path for ablations.

Path C health check found a concrete Stage-2 prelaunch risk: the quick target probe predicted no `Greet` at all, even though the balanced target test contains 6 `Greet` rows. To address that before the Stage-2 main run, the project now has an explicit Greet-augmentation entrypoint:

```text
data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v2.jsonl
```

This file keeps the canonical 71 target rows intact and appends 15 synthetic general-domain attention-stage `Greet(phase=open)` rows. Its best-act distribution is `Greet=26 / Inform=41 / Elicit=14 / Recommend=5 / Hold=0`. These 15 rows are `synthetic_augmented_unreviewed`; they are a training patch, not QA-reviewed target-frontcam evaluation data. The earlier 40-row `greet_aug_v1` file is retained only as an audit artifact. The canonical 71-row file remains the audit baseline.

The same rebuild also adds a prompt-level Hold guardrail to 5-act action-selection prompts: `Hold` is defined as a real no-intervention decision, not an uncertainty fallback. This is meant to reduce the quick-probe failure mode where the model over-predicted `Hold` for uncertain target cases.

Stage-2 action-selection candidates are now stage-conditioned while the locked 5-act set itself stays unchanged:

| AIDA stage | Candidate acts |
|---|---|
| `attention` | `Greet / Elicit / Inform / Hold` |
| `interest` | `Elicit / Inform / Recommend / Hold` |
| `desire` | `Inform / Recommend / Hold` |
| `action` | `Greet / Recommend / Hold` |

This follows the lightweight `piwm` design and prevents impossible or poorly timed candidates from dominating the small target split. It does not remove any act from the global 5-act definition.

For Stage-2 inference and evaluation, the evaluator exposes a Hold prior calibration because Path C quick probe over-predicted `Hold` (`16/30`) while the balanced target test prior is `6/30`. The default mitigation is:

```bash
--hold-prior-lambda 1.0 \
--hold-prior-target 0.2 \
--hold-prior-observed 0.5333333333
```

The intended sweep is `lambda = 0.5 / 1.0 / 1.5`. This is an inference-time mitigation, not a new label. It should be reported separately because Stage-2 train still has no natural `Hold` best rows.

A4 weighted adaptation should use the targetx8 entrypoint:

```text
data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v2_targetx8_v1.jsonl
```

This file has 3232 rows: 2544 Stage-1 rows plus the 86-row GreetAug-v2 target action set repeated 8 times. The repeated rows are training weight, not new unique examples.

## Evaluation Matrix

| Label | Checkpoint | Eval file | Purpose |
|---|---|---|---|
| `general_on_general` | `checkpoint_general` | `data/official/domain_specialization_eval_v2/general_qa_stage1_all.jsonl` | Stage-1 general health check |
| `general_on_target` | `checkpoint_general` | `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl` | zero-shot target transfer |
| `target_specialized_on_target` | `checkpoint_target` | `data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl` | target specialization gain |
| `target_specialized_on_general` | `checkpoint_target` | `data/official/domain_specialization_eval_v2/general_qa_stage1_all.jsonl` | catastrophic forgetting check |

Evaluation script:

```bash
python3 -m scripts.eval_ms_swift_checkpoint \
  --model <MODEL> \
  --checkpoint <CHECKPOINT> \
  --eval-label general_on_target \
  --input-jsonl data/official/domain_specialization_eval_v2/target_frontcam_5act_test_all.jsonl \
  --out data/piwm_results/domain_specialization_eval/general_on_target.json \
  --image-limit 3
```

The evaluator now reports task exact-match metrics plus macro-F1 style classification metrics:

- `stage_macro_f1`
- `intent_macro_f1`
- `next_stage_macro_f1`
- `action_macro_f1`
- `go_precision`, `go_recall`, `no_go_precision`, `no_go_recall`

## Baselines

For the target 5-act action-selection rows, report at least:

- always-Inform;
- always-Hold;
- random among the candidate set.

These baselines should be reported against 5-act macro F1 and go/no-go precision/recall. Overall accuracy alone is not sufficient, even with a balanced test, because go/no-go collapses four intervention acts into one side and `Hold` into the other.

Baseline command and current output:

```bash
python3 -m scripts.run_action_selection_baselines
```

```text
data/piwm_results/domain_specialization_eval/target_5act_action_baselines.md
```

Current baseline numbers on the balanced 30-row target action-selection eval:

| Baseline | Action accuracy | Action macro F1 |
|---|---:|---:|
| always-Greet | 0.200 | 0.067 |
| always-Elicit | 0.200 | 0.067 |
| always-Inform | 0.200 | 0.067 |
| always-Recommend | 0.200 | 0.067 |
| always-Hold | 0.200 | 0.067 |
| random-candidate, seed 42 | 0.267 | 0.281 |

## Stage-1 Training Skeleton

The Stage-1 launch skeleton is intentionally dry-run first:

```bash
bash scripts/train/stage1_train.sh --dry-run
```

It prints the ms-swift command that will use:

- train inputs: `user_intent_train.jsonl` + `next_state_prediction_train.jsonl`;
- val inputs: `user_intent_val.jsonl` + `next_state_prediction_val.jsonl`;
- 3 frames per example;
- epochs=3 and learning rate=2e-5;
- output checkpoint path `checkpoints/stage1_v1/`;
- log path `logs/stage1_v1/`.

Before real training, the project lead must fill `MODEL_ID` and `BATCH_SIZE`. The local checkout is missing many general synthetic frames; run the real job only in an environment that has the full general frame directories.

## External Validation Status

The following are planned validation tracks, not current results:

- `sim_to_real_on_real_50`: the repo currently has a real-shooting manifest/protocol, not 50 collected and QA-reviewed real videos.
- salesperson experience labels: three salesperson majority-vote labels should be collected on 30 target records, then reported with model-vs-majority agreement and Cohen's kappa. These labels must not be used for training.

## Red Lines

- Do not include `Reassure` in the main 5-act macro F1, operational training/eval files, inference candidates, or runtime export.
- Preserve `Recommend(pressure=soft/firm)` in action params wherever Recommend appears.
- Do not use old action-selection prompts that expose reward or predicted outcomes for the main Stage-2 experiment.
- The new 5-act target test is balanced, video-backed, and `qa_reviewed_pass=30`; do not extend that QA claim to the 71 target train records.
- Do not count 200 prompt-ready/video-pending rows as multimodal training data.
- Do not report real-50 or salesperson-majority-vote numbers until the assets and labels exist.
