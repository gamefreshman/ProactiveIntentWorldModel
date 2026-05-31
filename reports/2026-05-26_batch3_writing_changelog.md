# Batch 3 Writing Changelog

Date: 2026-05-26

## Scope

Writing-only task completed under `reports/batch3_draft/`. No main tex file was modified.

## Files Added

| File | Purpose |
|---|---|
| `reports/batch3_draft/limitations_section.tex` | Standalone Limitations section for ACL/EMNLP compliance. |
| `reports/batch3_draft/world_model_reframing_diff.md` | Manual diff plan for reframing PIWM as world-model-as-auxiliary-supervision. |
| `reports/batch3_draft/reproducibility_section.tex` | Reproducibility block with audited LoRA, optimizer, inference, and frame-sampling details. |
| `reports/batch3_draft/aida_bdi_justification.tex` | AIDA+BDI theoretical justification paragraph. |
| `reports/batch3_draft/related_work_additions.tex` | Related-work additions for VLA, proactive multimodal assistants, and shopping/retail agents, with BibTeX entries. |
| `reports/batch3_draft/figure1_caption_fix.tex` | Figure caption replacement snippet. |
| `reports/batch3_draft/equation_fixes.md` | Non-applied equation/table layout fix suggestions. |
| `reports/batch3_draft/appendix_skeleton.tex` | Appendix skeleton with prompt templates and one dataset sample. |
| `reports/batch3_draft/README.md` | Merge guide and dependency notes. |

## Evidence Checked

- Latest local Overleaf mirror: `tmp/overleaf_edit/acl_latex_after.tex`.
- Prompt builders: `piwm_train/prompts.py`.
- Evaluation scripts: `scripts/eval_ms_swift_checkpoint.py`, `scripts/eval_e2e_decision_loop_checkpoint.py`.
- Frame extraction: `scripts/extract_frames.py`.
- Training config: `reports/training_config_audit_remote_20260524/run_args.json`, `adapter_config.json`, `trainer_state.json`.
- Dataset sample source: `data/GuidanceSalesBench/general/main_schema.jsonl`.

## Notes

- The repository has no function named `build_best_action_prompt`; the current best-action prompt is `build_action_prompt_no_leak(..., five_act_only=True)`.
- The local repo does not contain `custom.bib`; related-work BibTeX entries are included inside an ignored block in `related_work_additions.tex` for manual copy into Overleaf if needed.
- The latest local mirror already has a non-placeholder caption for `fig:piwm_overview`; `figure1_caption_fix.tex` is still provided because the user requested a standalone caption fix snippet.
- Hardware accounting in `reproducibility_section.tex` includes the PI-requested 6x A100 estimate and an audit note that the archived main run args record `global_world_size=2`.

