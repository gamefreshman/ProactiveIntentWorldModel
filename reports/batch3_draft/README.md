# Batch 3 Draft README

These files are writing-only snippets for later merge. They do not modify `acl_latex.tex` or any main paper source.

| File | Content | Merge location | Batch 2 dependency |
|---|---|---|---|
| `limitations_section.tex` | Standalone ACL/EMNLP Limitations section with seven items. | After Conclusion, before References. Remove the old inline `\paragraph{Limitations.}` from Section 6.6 when merging. | Item 7 depends on Batch 2 schema/frame ablation results; remove or fill placeholder before submission. |
| `world_model_reframing_diff.md` | Three explicit edit locations for framing PIWM as world-model-as-auxiliary-supervision. | Section 4.2, Section 6.5.3, and Conclusion. | Uses Batch 1/2 Table 6 and Section 6.5.3 wording. |
| `reproducibility_section.tex` | Training, inference, hardware, compute, and frame-sampling details. | Section 6.1 Experimental Setup or Appendix. | Hardware sentence should be reconciled with final server logs if exact world size is needed. |
| `aida_bdi_justification.tex` | AIDA+BDI theory justification paragraph. | End of Section 3 or start of Section 4. | Final sentence references future Section 6.5.6--6.5.7 ablations; edit after Batch 2. |
| `related_work_additions.tex` | Three related-work paragraphs plus BibTeX entries in an ignored block. | Section 2.1, 2.2, and 2.4; copy BibTeX entries to `custom.bib` if missing. | None, except cite-key reconciliation with Overleaf `custom.bib`. |
| `figure1_caption_fix.tex` | Replacement caption text for Figure 1 if it still says Placeholder. | Replace the relevant `\caption{...}`. | None. Latest local mirror already has a non-placeholder PIWM overview caption; check Overleaf before applying. |
| `equation_fixes.md` | Non-applied source snippets and suggested fixes for equation/table layout issues. | Manual merge only where the issues still appear. | Batch 2 may already have fixed the original Equation (8) clipping. |
| `appendix_skeleton.tex` | Appendix scaffold with prompt templates, one dataset sample, and failure-case placeholder. | After main body and before `\bibliography{custom}`, or after bibliography depending venue style. | Failure-case placeholder should be filled from Batch 2. |

Prompt note: the current repository does not define `build_best_action_prompt`. The best-action prompt used in action-selection rows is `piwm_train/prompts.py::build_action_prompt_no_leak(..., five_act_only=True)`.

