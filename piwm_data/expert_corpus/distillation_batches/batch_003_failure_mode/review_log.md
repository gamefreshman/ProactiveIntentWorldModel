# Review Log: batch_003_failure_mode

Status vocabulary: `pending`, `approved`, `revise`, `reject`.

Checklist for each principle:

- faithful to the source locator and paraphrase note;
- compact enough to be auditable;
- operationalizable as a rule or schema condition;
- no long copyrighted source text;
- not duplicative or conflicting with existing principles.

| ID | Source | Draft principle | Usable for | Schema | Decision | Notes |
|----|--------|-----------------|------------|--------|----------|-------|
| P_FAILURE_MODE_001 | SRC_SALES_PERSONAL_SELLING_001 | Closing-oriented actions should fit the buyer's readiness rather than replace discovery or evaluation. | failure_mode, transition | ok | approved | Directly supports premature-closing failure conditions in transition rules. |
| P_FAILURE_MODE_002 | SRC_SALES_SPIN_001 | Recommendation before need discovery increases mismatch risk and can reduce customer trust. | failure_mode, risk_tags | ok | approved | Supports need-discovery-before-recommendation risk; compact and actionable. |
| P_FAILURE_MODE_003 | SRC_SALES_REACTANCE_BREHM_1966 | High-pressure recommendations can trigger reactance when customer autonomy appears threatened. | failure_mode, pressure_reactance | ok | approved | Core pressure-reactance principle for high-pressure Recommend failure modeling. |
| P_FAILURE_MODE_004 | SRC_SALES_BUSINESS_COMM_001 | Disengagement cues should reduce intrusive information delivery and favor holding or reassurance. | failure_mode, nonverbal_cues | ok | approved | Connects nonverbal disengagement cues to less intrusive actions. |

## Reviewer Notes

- Pending review. Do not promote this batch until decisions are changed
  to `approved` in `extracted_draft.jsonl` or copied into `finalized.jsonl`.
