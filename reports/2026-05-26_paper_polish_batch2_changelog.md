# Batch 2 Changelog: Layout Fixes, GPT-5.5, Ablations

Date: 2026-05-26

## Status Summary

| Subtask | Status | Notes |
|---|---|---|
| A. Layout fixes | success | Updated local Overleaf tex snapshot; regenerated V1/V3/V4 PDFs. |
| B. GPT-5.5 + analysis | success | Added GPT-5.5 diagnostic row to Table 3, bootstrap CI prose, Table 11 per-action breakdown, and Appendix A failure cases. |
| C. BDI ablation | success | Training and evaluation completed on A100 GPUs 0-1; raw outputs pulled to `reports/ablation_no_bdi_20260526_0335/`. |
| D. Observable evidence ablation | success | Training and evaluation completed on A100 GPUs 2-3; raw outputs pulled to `reports/ablation_no_evidence_20260526_0335/`. |
| E.a 1-frame ablation | success | Training and evaluation completed on A100 GPUs 4-5 with 513-step original-training schedule. |
| E.b 5-frame ablation | success | Recovered missing A100 source videos, rebuilt a 2734-row 5-frame mirror, trained to checkpoint-684, then completed final E2E evaluation on juwei after A100 credit exhaustion. |
| F. Closed-source baseline | pending | Left unchanged as requested; OpenRouter access still pending. |

## Completed Paper Edits

- Fixed Figure 6 confusion-matrix layout by moving the parse-failure note into the LaTeX caption and regenerating `V1_confusion_matrix`.
- Fixed Figure 5 radar chart to use strict per-class F1, with PIWM emphasized and comparison models shown as lighter dashed lines.
- Removed the internal title from Figure 8 error-propagation funnel and regenerated `V3_error_propagation_funnel`.
- Added the task-interference footnote sentence to the Table 6 caption.
- Reflowed Equation (8) into two lines to avoid right-margin clipping.
- Shortened Table 8 row labels and set the first column to `p{3cm}` with `\small`.
- Rewrote the Table 3 footnote so closed-source API issues appear only in Limitations.
- Updated Section 6.4 prose to distinguish the per-class radar chart from the single-model confusion matrix.
- Strengthened the final Section 5.4 dataset-statistics paragraph as requested.
- Added GPT-5.5 diagnostic row and caption qualifier to Table 3.
- Added Section 6.3 prose for GPT-5.5 and bootstrap confidence analysis.
- Added Table 11 per-action F1 breakdown.
- Added Appendix A failure-case analysis on Target-Test.
- Added Tables 12-14 to `tmp/overleaf_edit/acl_latex.tex` for BDI, observable-evidence, and frame-count ablations. The 5-frame row is filled from the merged juwei evaluation summary.

## Ablation Training Artifacts

| Variant | Training data | Checkpoint root | Status |
|---|---|---|---|
| PIWM no BDI | `data/ablation_no_bdi/piwm_train_stage1_plus_stage2_target_v2_balanced.no_bdi.server_resolved.jsonl` | `checkpoints/ablation_no_bdi_20260526_0335/` | complete; evaluated checkpoint-513 |
| PIWM no observable evidence | `data/ablation_no_evidence/piwm_train_stage1_plus_stage2_target_v2_balanced.no_evidence.server_resolved.jsonl` | `checkpoints/ablation_no_evidence_20260526_0335/` | complete; evaluated checkpoint-513 |
| PIWM 1-frame | `data/ablation_1frame/piwm_train_stage1_plus_stage2_target_v2_balanced.1frame.server_resolved.jsonl` | `checkpoints/ablation_1frame_20260526_0335/` | complete; evaluated checkpoint-513 |
| PIWM 5-frame | `data/ablation_5frame/piwm_train_stage1_plus_stage2_target_v2_balanced.5frame.server_resolved.jsonl` | `checkpoints/ablation_5frame_20260526_1126_6gpu_ddp/` | complete; evaluated checkpoint-684 via juwei resume |

## Ablation Results

All four ablations completed with local `summary.json` files. The 5-frame run was trained on A100, then finished on juwei by merging the existing A100 oracle/pipeline raw outputs with a resumed 30-sample E2E evaluation.

| Variant | Target-Test F1 | Cross-Domain F1 | E2E F1 | AIDA F1 | Intent F1 | Next-State F1 |
|---|---:|---:|---:|---:|---:|---:|
| PIWM full | 0.641 | 0.734 | 0.295 | 0.350 | 0.114 | 0.565 |
| PIWM no BDI | 0.526 | 0.693 | 0.219 | 0.428 | 0.120 | 0.163 |
| PIWM no observable evidence | 0.778 | 0.796 | 0.229 | 0.370 | 0.116 | 0.205 |
| PIWM 1-frame | 0.589 | 0.723 | 0.189 | 0.370 | 0.074 | 0.165 |
| PIWM 5-frame | 0.627 | 0.770 | 0.234 | 0.412 | 0.115 | 0.222 |

## Warnings

- The earlier 5-frame blocked diagnosis was corrected: A100 had only 8/118 target source videos. After syncing the full local 118-video source set, the rebuilt 5-frame mirror wrote 2734/2734 train rows with `image_count=5` and no skipped rows.
- The first 5-frame training attempt failed with CUDA OOM under unchanged PIWM ablation hyperparameters.
- After PI clarified that the priority was to use idle GPUs, I first restarted 5-frame on GPUs 4-5 with `per_device_train_batch_size=2` and `gradient_accumulation_steps=4`.
- At PI's follow-up instruction to use all six GPUs, I stopped the 2-GPU retry before any checkpoint was written and launched `20260526_1126_6gpu_ddp` with explicit `torch.distributed.run --nproc_per_node 6`. A prior `20260526_1121_6gpu` launch was aborted because it reported `world_size=1`.
- The 6-GPU DDP run uses effective global batch 12 (`per_device_train_batch_size=2`, `gradient_accumulation_steps=1`). Exact global batch 16 is not representable with 6 GPUs and integer gradient accumulation, so this is marked as a resource-utilization restart rather than an unchanged-hyperparameter run.
- After A100 credit exhaustion, I copied the checkpoint adapter, base-model dependency, evaluation frames, and existing A100 raw outputs to juwei. The remaining 30-sample E2E evaluation was split into two shards (`GPU0` and `GPU1+GPU2`) and merged into `reports/ablation_5frame_20260526_1126_6gpu_ddp/summary.json`.
- 5-frame E2E parse rates: Step 1 = 1.000, Step 2 = 0.867.
- Observable evidence ablation exceeds the PIWM full baseline on Target-Test (0.778 vs 0.641) and Cross-Domain (0.796 vs 0.734). Per instruction, the number is reported as-is with no hyperparameter changes, rerun, or retry.
- Local `latexmk` validation passed in `tmp/overleaf_edit/local_compile/`, producing a 22-page `acl_latex.pdf`. Local warnings remain for project citation files and known overfull boxes, but the ablation/table edits compile and the new table references resolve.
