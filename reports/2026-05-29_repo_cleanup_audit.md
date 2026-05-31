# Repository Cleanup Audit

Date: 2026-05-29

Scope: local cleanup for `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel`.
This pass avoided deleting data, checkpoints, evaluation raw outputs, or existing source changes.

## Actions completed

- Updated `.gitignore` to ignore LaTeX build outputs, local paper PDF renders, and local `tmp/` scratch/Overleaf mirror files.
- Moved 37 obvious local artifacts into `local_artifacts/cleanup_quarantine_20260529/` instead of deleting them.
- Left all staged ablation outputs, paper reports, model/eval raw outputs, checkpoints, and source-code changes untouched.

## Quarantined artifact classes

| Class | Count | Destination |
|---|---:|---|
| LaTeX build outputs and local paper renders under `paper/` | 17 | `local_artifacts/cleanup_quarantine_20260529/paper/` |
| macOS/Finder duplicate files with ` 2` suffix under `docs/current/` | 17 | `local_artifacts/cleanup_quarantine_20260529/docs/current/` |
| Duplicate script copy `scripts/build_ms_swift_5frame_data 2.py` | 1 | `local_artifacts/cleanup_quarantine_20260529/scripts/` |
| Duplicate human-upper-bound zip | 1 | `local_artifacts/cleanup_quarantine_20260529/reports/` |
| Accidental shell-format filename `{thr:.1f}` | 1 | `local_artifacts/cleanup_quarantine_20260529/` |

The full moved-file manifest is at:

```text
local_artifacts/cleanup_quarantine_20260529/moved_files.txt
```

## Current repository state after cleanup

The working tree is still intentionally dirty. The remaining visible changes are project-relevant and should not be bulk-cleaned without a commit/release decision:

- Modified source and docs from prior PIWM work.
- Staged/new ablation reports and figure assets.
- Untracked evaluation outputs under `reports/`, including closed-model, real-store, rerun, end-to-end, and ablation artifacts.
- Untracked scripts/tests for the current evaluation and data-building workflow.
- One untracked manuscript source, `paper/piwm_arr_temporary_submission.tex`, retained because it is not a build artifact.

## Recommended next pass

1. Decide which result bundles in `reports/` should be tracked as paper evidence versus moved to `local_artifacts/`.
2. Move durable evaluation scripts from ad-hoc locations into `scripts/` and keep run-only helpers in ignored `tmp/`.
3. Split commits by purpose:
   - core code/data-contract changes;
   - evaluation scripts;
   - paper/report artifacts;
   - generated figures and ablation summaries.
4. Do not commit checkpoints, full video bundles, local paper PDFs, or transient LaTeX compile products.

## Red lines

Do not bulk-delete these without a dedicated manifest check:

- `data/official/` and `data/GuidanceSalesBench/`: canonical dataset entrypoints and manifests.
- `reports/ablation_*_20260526_*`: ablation raw outputs and summaries supporting paper tables.
- `reports/closed_model_eval_*`, `reports/real_eval_20260525/`, `reports/end_to_end_eval_20260525/`, `reports/rerun_eval_20260525/`: evaluation evidence and raw model outputs.
- `reports/human_upper_bound_20260526/` and its zip: human upper-bound annotation package.
- `reports/2026-05-24_paper_writing_materials.md` and dated `2026-05-26_*changelog.md`: paper integration history.
- `tmp/overleaf_edit/acl_latex.tex`: staged Overleaf mirror from the live manuscript workflow.
- `references/piwm_lightweight/`: imported lightweight reference repository; do not flatten into the main tree.
- Any `data/official/ms_swift_5frame/**/frames/*/* 2.jpg` file: these look like Finder duplicates, but they are inside an official generated dataset and require hash/manifest validation before cleanup.

## Remaining cleanup candidates

These are candidates, not automatically removed:

- `reports/**/*.partial`: likely interrupted output. Keep unless the matching complete output and summary are verified.
- `tmp/openreview_update/compile/`, `tmp/overleaf_edit/local_compile/`, and `tmp/overleaf_edit/build*`: local compile sandboxes now ignored by `.gitignore`.
- `logs/`: ignored training/sync logs. Archive by date if needed.
- `paper/piwm_arr_temporary_submission.tex`: manuscript source-shaped file, so it was retained even though adjacent build outputs were quarantined.
