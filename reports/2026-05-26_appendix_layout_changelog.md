# Appendix Layout Fix Changelog

Date: 2026-05-26

## Scope

Adjusted appendix layout in the Overleaf main file `acl_latex.tex` to remove overlapping prompt / JSON blocks while keeping the manuscript in ACL / EMNLP two-column format.

## Changes

- Replaced appendix `verbatim` blocks with `listings`-based environments:
  - `PromptBlock` for prompt templates, using `\scriptsize` monospace text with automatic line breaking.
  - `JsonBlock` for the dataset sample, using compact monospace text with automatic line breaking.
- Added line-breaking support for long code/data paths using `\path{...}`.
- Added `\clearpage` before `\bibliography{custom}` and before `\appendix` so floats and appendix material no longer collide.
- Kept the failure-case table as a two-column-wide `table*`, which is appropriate for wide appendix tables.

## EMNLP 2026 / ARR Format Check

- The paper still uses the official ACL review style: `\usepackage[review]{acl}`.
- The appendix remains in two-column ACL format; no `\onecolumn`, custom page geometry, or template override was introduced.
- The appendix is placed after references, consistent with ARR guidance for submitted PDFs.
- Limitations, Ethics, references, and appendix material are outside the main content page limit under EMNLP / ARR guidance.
- The appendix contains reproducibility details, prompt templates, a dataset sample, and failure cases, all supporting replication rather than replacing core paper content.

## Verification

- Overleaf compile passed after sync.
- Latest Overleaf PDF page count: 21 pages.
- Rendered and inspected the appendix pages from the Overleaf-generated PDF:
  - `tmp/pdfs/piwm_appendix_review/overleaf_after_layout/page_18.png`
  - `tmp/pdfs/piwm_appendix_review/overleaf_after_layout/page_19.png`
  - `tmp/pdfs/piwm_appendix_review/overleaf_after_layout/page_20.png`
  - `tmp/pdfs/piwm_appendix_review/overleaf_after_layout/page_21.png`
- Visual result: no prompt / JSON overlap, no text crossing column boundaries, and no clipped appendix table.
- Text sanity checks on the downloaded Overleaf PDF:
  - `??`: 0
  - `Placeholder`: 0
  - `PLACEHOLDER`: 0
  - `world-model-as-auxiliary`: 0
