# Batch 3 Merge Changelog

Date: 2026-05-26

## Target Files

- Updated local Overleaf main tex mirror: `tmp/overleaf_edit/acl_latex.tex`
- Updated working mirror source: `tmp/overleaf_edit/acl_latex_after.tex`
- Added BibTeX addendum: `tmp/overleaf_edit/custom.bib`

Note: this local checkout did not contain a root `acl_latex.tex` or `custom.bib`; the merge was applied to the existing Overleaf mirror under `tmp/overleaf_edit/` and materialized as `tmp/overleaf_edit/acl_latex.tex` for sync.

## Subtask Status

| Subtask | Status | Notes |
|---|---|---|
| A. Standalone Limitations | Done | Removed old inline `\paragraph{Limitations.}` from Section 6.6. Added `\section*{Limitations}` after Conclusion and before `\bibliography{custom}`. Deleted the closed-source-baseline item as requested; retained items 1-5 and schema-ablation placeholder item. |
| B. Reproducibility appendix | Done | Added `\section{Reproducibility}` after Prompt Templates and before Dataset Sample. Reworded compute to "approximately 9 A100-hours (A100 80GB)" and removed the unresolved card-count/audit-note wording. |
| C. AIDA+BDI justification | Done | Inserted at the start of Section 4, immediately after `\section{Proactive Intent World Model}`. Final sentence now points broadly to Section 6.5 without relying on future 6.5.6/6.5.7 numbering. |
| D. Related Work additions | Done | Added paragraphs to Section 2.1, 2.2, and 2.4. Added five requested BibTeX entries to `tmp/overleaf_edit/custom.bib`; no duplicate keys inside the local addendum. |
| E. Figure 1 caption fix | Skipped | Active Figure 1 caption was already non-placeholder. Structural check found no active `\caption{...}` containing "Placeholder"; only commented/figure-body placeholder text remains. |
| F. World-model reframing | Revised | Updated to the PI-approved "world-model-augmented proactive action policy" framing in Section 4.2, Section 6.5.3, and Conclusion. Removed the old "world-model-as-auxiliary-supervision" style framing; no ablation table values were changed. |
| G. Appendix skeleton | Done | Moved appendix after References. Added Prompt Templates, Reproducibility, Dataset Sample, and preserved the existing Batch 2 Failure Case Analysis table instead of replacing it with a placeholder. |
| Compile sanitization | Done | Replaced non-ASCII text inside appendix verbatim blocks with ASCII English equivalents so Overleaf pdfLaTeX can compile without Unicode-character errors. |

## Validation

- Structural order verified:
  - `\section{Conclusion}` at line 683
  - `\section*{Limitations}` at line 689
  - `\bibliography{custom}` at line 718
  - `\appendix` at line 720
  - Appendix sections: Prompt Templates, Reproducibility, Dataset Sample, Failure Case Analysis
- Active label/ref scan:
  - Active labels: 30
  - Active refs: 20
  - Duplicate active labels: none
  - Missing active refs: none
- BibTeX addendum scan:
  - Keys: `brohan2023rt2`, `kim2024openvla`, `black2024pi0`, `yao2022webshop`, `jin2024shoppingmmlu`
  - Duplicate keys inside local addendum: none
- Figure caption scan:
  - No active caption contains "Placeholder".
- World-model reframing scan:
  - `world-model-as-auxiliary`: 0 matches
  - `world-model-augmented`: 3 active matches in the intended F.1/F.2/F.3 locations
- Encoding scan:
  - `tmp/overleaf_edit/acl_latex.tex`: 0 non-ASCII lines after appendix sanitization

## Compile Result

Overleaf compile after browser sync:

```text
Recompile in https://www.overleaf.com/project/6a0ab89c3af80cd32d608e60
```

Result: PDF generated successfully in the Overleaf editor after appendix Unicode sanitization.

```text
PDF pages: 17
Errors: none blocking after sanitization
Warnings: 2 shown by the Overleaf toolbar
```

Additional static checks against the synced source and BibTeX:

```text
labels: 30
refs: 19
missing refs: none
cites: 41
unique cites: 28
missing cites: none
duplicate BibTeX keys: none
```

Local compile attempted:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=tmp/overleaf_edit/build_batch3 tmp/overleaf_edit/acl_latex.tex
```

Result: blocked by local environment, not by the merged tex content.

```text
! LaTeX Error: File `acl.sty' not found.
```

PDF pages: N/A. Warning count: N/A because compilation stops before document processing. The previous Batch 2 changelog reported the same local blocker; final compile should be run in Overleaf where `acl.sty` and the full `custom.bib` are available.
