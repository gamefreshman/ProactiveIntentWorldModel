# Closed Model Best-Action Eval Blocker

Date: 2026-05-25

## Current Status

- Step 1 eval set has been constructed: `reports/closed_model_eval_set_60.jsonl`
- Size: 60 rows = target 30 + general 30
- Target gold: available
- General gold: recovered from the full source corpus, available
- Candidate actions and gold customer state text: present for all rows
- OpenRouter calls: not started
- Local model inference: not run on this workstation because `torch` and remote checkpoint paths are unavailable

Update after A100 recovery:

- The six missing local frame triplets were recovered from `/root/lanyun-fs/ProactiveIntentWorldModel/archives/Archive_generated_synth_core/<source_id>/frames/`.
- `reports/closed_model_eval_set_60.summary.json` now has `missing_images: []`.
- A100-side eval set was also regenerated with remote-readable image paths and `missing_images: []`.
- The target 30 source was switched to the historical PIWM 0.641 source file: `data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl`.

## Blocking Issue

Six general-domain samples have valid metadata and gold labels, but their local video-frame files are missing. This prevents a valid 60-sample multimodal evaluation.

Missing samples:

| eval_id | source_id | gold_best_action | missing frames |
|---|---|---:|---:|
| `general_045_piwm_dcf035b98f` | `piwm_dcf035b98f` | Elicit | 3 |
| `general_046_piwm_edacd4c7cd` | `piwm_edacd4c7cd` | Recommend | 3 |
| `general_047_piwm_f1198c1c8a` | `piwm_f1198c1c8a` | Elicit | 3 |
| `general_048_piwm_f29432adae` | `piwm_f29432adae` | Elicit | 3 |
| `general_049_piwm_f5d9f82742` | `piwm_f5d9f82742` | Recommend | 3 |
| `general_050_piwm_ffe9d89f49` | `piwm_ffe9d89f49` | Hold | 3 |

The expected paths are under:

```text
Archive_generated_priority256/<source_id>/frames/000.jpg
Archive_generated_priority256/<source_id>/frames/001.jpg
Archive_generated_priority256/<source_id>/frames/002.jpg
```

Local search found only metadata folders under:

```text
local_artifacts/generated_videos/Archive_generated_priority256/<source_id>/
local_artifacts/prompts/Archive_prompts_priority256/<source_id>/
```

Those folders do not contain `frames/` or `video.mp4`.

## Safety Guard Added

`scripts/closed_model_best_action_eval.py run-openrouter` now preflights all image files and aborts before any OpenRouter API call if any frame is missing. This avoids producing partial raw outputs or spending API cost on an invalid run.

Verification command:

```bash
python3 scripts/closed_model_best_action_eval.py run-openrouter --models gpt-4o
```

Result: aborted before API-key lookup/API calls with the 18 missing image paths listed.

## Recommended Decision

Preferred: restore the six missing source folders from the original server/media archive, at least:

```text
/root/lanyun-fs/ProactiveIntentWorldModel/Archive_generated_priority256/
  piwm_dcf035b98f/frames/000.jpg
  piwm_dcf035b98f/frames/001.jpg
  piwm_dcf035b98f/frames/002.jpg
  ...
```

If original media cannot be restored, PI should choose one of:

- replace these six general samples with other general-source samples that already have local frames and best-action gold;
- reduce the general subset to the 24 currently frame-complete samples and report as a 54-sample partial diagnostic, not the requested 60-sample apple-to-apple result.
