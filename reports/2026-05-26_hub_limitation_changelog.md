# HUB Limitation Changelog

Date: 2026-05-26

Target: `acl_latex.tex` (Overleaf project `6a0ab89c3af80cd32d608e60`; local mirror `tmp/overleaf_edit/acl_latex.tex`)

## Summary

- Added one new `Limitations` item after `Intent classification from 3-frame video remains weak`.
- `Limitations` active item count changed from 6 to 7.
- Did not modify Table 3, main result numbers, Section 6 prose, Ethics Statement, Data and Code Availability, or Appendix content.

## New Item

```latex
\item \textbf{Human upper bound on the action-selection task is not 
yet reported.} The macro F1 of professional retail staff on the same 
Target-Test ($n=30$) would establish a task-difficulty ceiling and 
contextualize PIWM's 0.641 result. Human annotation of the benchmark 
set is currently being conducted by professional retail staff through 
a third-party annotation service and was not completed in time for the 
present submission. We plan to include the human upper bound figure in 
the camera-ready version or in an extended release of this benchmark.
```

## Validation

- Local `Limitations` active item count: 7.
- Local static reference check: `labels=30 refs=19 missing=0`.
- Overleaf source sync: completed; browser title updated to `SYNCED_75411`.
- Overleaf compile: passed.
- PDF pages after compile: 20.
- Warnings shown in Overleaf: 3.
- Temporary local sync server on port `8765` was stopped after sync.
