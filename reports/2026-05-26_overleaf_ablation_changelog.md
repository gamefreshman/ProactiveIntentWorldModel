# 2026-05-26 Overleaf Ablation/Main Table Changelog

## Scope

- Edited Overleaf main file: `acl_latex.tex` in project `6a0ab89c3af80cd32d608e60`.
- Local working snapshots:
  - Before: `tmp/overleaf_edit/acl_latex_before.tex`
  - After: `tmp/overleaf_edit/acl_latex_after.tex`
- Modification boundary: Section 6 Experiments only, plus one limitations paragraph inserted immediately before `\section{Conclusion}`.

## Modified

- Replaced Table 3 `tab:main_results` with the Scenario Transfer main table covering Target 30 Oracle, Combined 60 Oracle, Target 30 E2E, and Real Video 20.
- Added main-table narrative after Table 3 and before `\subsection{Action-level Analysis}`.
- Replaced old `\subsection{Ablation Studies}` content with five ablation subsubsections:
  - `Training Data Composition`
  - `Candidate Filtering Strategy`
  - `Inference-time Counterfactual Planning`
  - `Pipeline Diagnostics`
  - `Oracle State vs. End-to-End`
- Replaced old `\subsection{Pipeline Diagnostics}` with `\subsection{Sim-to-Real Pilot Evaluation}`.
- Added a limitations paragraph before `\section{Conclusion}` without editing the Conclusion text itself.

## Added / Updated Labels

- Kept `tab:main_results`.
- Kept and expanded `tab:ablation`.
- Added `tab:ablation_training`.
- Added `tab:ablation_candidates`.
- Added `tab:ablation_planning`.
- Added `tab:ablation_pipeline`.
- Added `tab:ablation_e2e`.
- Added `tab:sim_to_real`.

## Notes

- The counterfactual-planning paragraph uses the supported 0.171 / 0.265 numbers and avoids the older unsupported `24 of 30 Hold` wording.
- Table 5 was wrapped with `\resizebox{\columnwidth}{!}{...}` after Overleaf reported `Package tabularx Warning: X Columns too narrow`.
- No Abstract, Introduction, Method, Related Work, Dataset section, or Conclusion text was changed.

## Verification

- Local structural check: pre-Experiments text unchanged; Conclusion body unchanged.
- Local environment counts: `table`, `table*`, `subtable`, `tabularx`, `tabular`, `figure*`, and `subfigure` begin/end counts match.
- Overleaf compile: passed.
- Overleaf log status after final compile: Errors 0, Warnings 1.
- Remaining warning: `Command \showhyphens has changed.` from ACL/template context.
- Removed warning: `Package tabularx Warning: X Columns too narrow (table too wide)` for Table 5.
- PDF: generated in Overleaf as a 10-page PDF. Direct local `curl` download failed with HTTP 403 because the Overleaf build URL requires browser authentication.
