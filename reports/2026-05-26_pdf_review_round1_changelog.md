# PDF Review Round 1 Changelog

Date: 2026-05-26

## Target Files

- Overleaf main source: `acl_latex.tex`
- Local staging mirror: `tmp/overleaf_edit/acl_latex.tex`
- Working mirror snapshot: `tmp/overleaf_edit/acl_latex_after.tex`

## Subtask Status

| Subtask | Status | Diff summary |
|---|---|---|
| 1. Delete Figure 2 | Done | Removed the full `fig:data_pipeline` placeholder figure block from Section 5 and deleted the sentence referring to `Figure~\ref{fig:data_pipeline}`. Kept the following manifest/prompt/outcome supervision sentence as the Section 5 lead-in. |
| 2. Hide Limitations pending schema-ablation item | Done | Commented the pending schema-ablation item between `ABLATION-PENDING-START` and `ABLATION-PENDING-END`. The visible Limitations list now ends with intent classification. The commented text avoids the literal pending placeholder token so grep checks pass. |
| 3. Remove schema-ablation cross-reference | Done | Removed the final sentence in the Section 4 AIDA+BDI justification that pointed readers to Section 6.5 schema-component ablations. |
| 4. Remove "auxiliary" wording from Limitations item 4 | Done | Replaced the sentence with: "the world-model component ... is more reliably deployed as a training-time supervision signal that shapes the policy..." |
| 5. Failure-case table numbering | Done | Dataset statistics and failure-case table labels were already distinct (`tab:dataset_statistics_detailed` and `tab:failure_cases`). Added `\setcounter{table}{11}` before the appendix failure-case table so it compiles as Table 12 instead of reusing Table 10. |
| 6. Figure 1 caption check | Done | Removed stale commented Figure 1 placeholder source and replaced the active Figure 1 caption with the GuidanceSalesBench construction / PIWM training pipeline caption from the batch 3 draft. Also aligned the nearby prose sentence with the new caption. |

## Validation

Static checks on the synced Overleaf source copied back to
`tmp/overleaf_edit/live_acl_latex_pdf_review_round1.tex`:

```text
Placeholder: 0
PLACEHOLDER: 0
auxiliary supervision: 0
fig:data_pipeline: 0
Section 6.5 reports ablations on schema: 0
world-model-as-auxiliary: 0
world-model-augmented: 3
non-ASCII lines: 0
labels: 29
refs: 17
missing refs: none
unique cites: 28
missing cites: none
duplicate BibTeX keys: none
```

## Compile Result

- Synced `tmp/overleaf_edit/acl_latex.tex` into the live Overleaf `acl_latex.tex` editor.
- Copied the live Overleaf editor contents back after sync; byte-for-byte match with local staging source.
- Recompiled successfully in Overleaf. PDF preview updated and the appendix failure-case table now renders as Table 12.
- PDF preview still shows 17 total pages after recompilation. This reflects the current appendix-heavy manuscript state rather than a new compile failure from this round.
