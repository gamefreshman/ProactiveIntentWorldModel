本报告 5-act = Greet/Elicit/Inform/Recommend/Hold。

# Path C Claude Follow-up Actions

## Trigger

Claude reviewed the Path C health check and returned this working decision:

- Do not start the Stage-2 main experiment yet.
- Treat Path C as conditionally healthy, not fully healthy.
- Fix two pre-Stage-2 issues first:
  1. `Greet` was never predicted in the quick target probe.
  2. `Hold` was over-predicted as an uncertainty fallback.

## Action 1: Greet Augmentation

Implemented a separate Stage-2 prelaunch augmentation entrypoint:

```text
data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v1.jsonl
```

This does not overwrite the canonical 71-row Stage-2 file.

| File | Rows | Best-act distribution |
|---|---:|---|
| `piwm_train_stage2_target_5act_v1.jsonl` | 71 | `Inform=41 / Elicit=14 / Greet=11 / Recommend=5 / Hold=0` |
| `piwm_train_stage2_target_5act_greet_aug_v1.jsonl` | 111 | `Greet=51 / Inform=41 / Elicit=14 / Recommend=5 / Hold=0` |

The 40 added rows are synthetic general-domain attention-stage `Greet(phase=open)` rows. They are marked as:

```text
augmentation_policy=stage2_prelaunch_general_greet_augmentation_v1
qa_status=synthetic_augmented_unreviewed
```

These rows are a training patch only. They are not target-frontcam QA-reviewed evaluation data.

## Action 2: Hold Overprediction Guardrail

Added a prompt-level 5-act guardrail in `piwm_train/prompts.py`:

```text
In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback.
Choose Hold only when the visible customer state clearly supports waiting or silence.
```

This is a lightweight Stage-2 prelaunch correction. It does not alter the 5-act set, and it does not change evaluation labels.

## Files Touched

- `scripts/build_two_stage_training_and_eval.py`
  - Added `--greet-augmentation-count`.
  - Writes explicit `*_greet_aug_*` Stage-2 and joint files when requested.
  - Keeps canonical `piwm_train_stage2_target_5act_v1.jsonl` intact.
- `piwm_train/prompts.py`
  - Added the Hold guardrail to 5-act action-selection prompts.
- `configs/domain_specialization_v1.json`
  - Added the Greet augmentation Stage-2 and joint entries.
- `data/official/DATASET_MANIFEST.json`
  - Added `PIWM-Stage2-Target-5Act-GreetAug-v1`.
- `docs/current/dataset_inventory.md`
  - Documented the augmented entrypoint.
- `docs/current/domain_specialization_experiment_plan.md`
  - Documented the Path C health-check follow-up and the two fixes.
- Generated:
  - `data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v1.jsonl`
  - `data/official/ms_swift/piwm_train_stage2_target_5act_greet_aug_v1_summary.json`
  - `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v1.jsonl`
  - `data/official/ms_swift/piwm_train_stage1_plus_stage2_target_5act_greet_aug_v1_summary.json`

## Validation

Commands run:

```bash
python3 -m scripts.build_two_stage_training_and_eval --greet-augmentation-count 40
python3 -m scripts.check_target_frontcam_split
python3 -m scripts.run_action_selection_baselines
python3 -m pytest piwm_data/tests/test_5act_invariant.py piwm_train/tests/test_data_collator.py piwm_infer/tests/test_parsers.py
python3 -m json.tool data/official/DATASET_MANIFEST.json >/dev/null
python3 -m json.tool configs/domain_specialization_v1.json >/dev/null
git diff --check
```

Results:

- `check_target_frontcam_split`: pass.
- Canonical Stage-2 train remains 71 rows.
- Balanced target test remains 30 rows with `Greet/Elicit/Inform/Recommend/Hold = 6/6/6/6/6`.
- Canonical Stage-2 Reassure text count: 0.
- Greet-augmented Stage-2 Reassure text count: 0.
- Target action eval Reassure text count: 0.
- Focused pytest: 36 passed.
- JSON validation: pass.
- `git diff --check`: pass.

Baseline rerun is unchanged on the balanced eval:

| Baseline | Macro F1 |
|---|---:|
| always-Greet | 0.067 |
| always-Elicit | 0.067 |
| always-Inform | 0.067 |
| always-Recommend | 0.067 |
| always-Hold | 0.067 |
| random-candidate | 0.281 |

## Current Status

Path C should now be described as:

```text
conditionally healthy: Stage-1 training clearly improves over zero-shot and the target probe is above random, but Stage-2 should use the Greet augmentation entrypoint and the Hold guardrail before main A0-A4 runs.
```

## Open Boundary

No Stage-2 main experiment has been started yet.

Recommended next decision for Claude/PI:

1. Confirm whether to use `piwm_train_stage2_target_5act_greet_aug_v1.jsonl` as the Stage-2 A0-A4 input.
2. Confirm whether the Hold guardrail is sufficient, or whether an inference-time Hold prior penalty is also required before Stage-2.
3. If confirmed, start Stage-2 A0-A4 with the augmented Stage-2 entrypoint.
