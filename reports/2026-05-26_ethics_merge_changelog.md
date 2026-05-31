# Ethics Merge Changelog

Date: 2026-05-26

Target: `acl_latex.tex` (Overleaf project `6a0ab89c3af80cd32d608e60`; local mirror `tmp/overleaf_edit/acl_latex.tex`)

## Summary

- Added an unnumbered `Ethics Statement` section after `Limitations` and before `Data and Code Availability`.
- Updated the first paragraph of Section 6.6 to clarify that the real-store pilot consists of staged retail recordings by paid employee participants, not actual customer recordings.
- Added a new `Limitations` item on staged recordings after the sim-to-real scale limitation.
- Did not modify main result numbers, Table 3, Abstract, Method, or Conclusion.

## Task Status

| Task | Status | Notes |
|---|---|---|
| A. Ethics Statement | Done | Inserted the full section with data source, consent, ethics review, release, risk, profiling, representativeness, and compute-footprint paragraphs. |
| B. Section 6.6 first paragraph | Done | Replaced the pilot description with staged-recording / paid-employee wording and reference to the Ethics Statement. |
| C. Limitations staged-recording item | Done | `Limitations` now has 6 active items; the new item is inserted after the sim-to-real scale limitation. |
| D. Validation | Done | Local static reference check: `labels=30 refs=19 missing=0`. Overleaf source outline shows `Ethics Statement` between `Limitations` and `Data and Code Availability`. |

## Compile Result

- Overleaf compile: passed.
- PDF pages: 20.
- Warnings shown in Overleaf: 3.
- Local checks:
  - `Section 6.6` contains `staged retail recordings` and `rather than recordings of actual store customers`.
  - `Limitations` active item count before `Ethics Statement`: 6.
  - No local matches for `PLACEHOLDER`, `Section 6.5 reports ablations on schema`, or `auxiliary supervision`.
  - Temporary local sync server on port `8765` was stopped after Overleaf sync.
