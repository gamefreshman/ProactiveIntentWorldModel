# Review Log: batch_004_recommend_pressure

Status vocabulary: `pending`, `approved`, `revise`, `reject`.

Checklist for each principle:

- faithful to the source locator and paraphrase note;
- compact enough to be auditable;
- operationalizable as a rule or schema condition;
- no long copyrighted source text;
- not duplicative or conflicting with existing principles.

| ID | Source | Draft principle | Usable for | Schema | Decision | Notes |
|----|--------|-----------------|------------|--------|----------|-------|
| P_RECOMMEND_PRESSURE_001 | SRC_SALES_SPIN_001 | Soft recommendation should connect to an observed need while preserving the customer's choice. | recommend_pressure, candidate_actions | ok | approved | Defines soft recommendation as need-linked and choice-preserving. |
| P_RECOMMEND_PRESSURE_002 | SRC_SALES_PERSONAL_SELLING_001 | Firm recommendation is more appropriate when commitment cues or explicit purchase questions are present. | recommend_pressure, transition | ok | approved | Defines firm recommendation gating by commitment or explicit purchase request. |
| P_RECOMMEND_PRESSURE_003 | SRC_SALES_REACTANCE_BREHM_1966 | Firm recommendation during low intent should be modeled as a pressure-reactance risk. | recommend_pressure, failure_mode | ok | approved | Maps low-intent firm recommendation to pressure-reactance risk. |

## Reviewer Notes

- Pending review. Do not promote this batch until decisions are changed
  to `approved` in `extracted_draft.jsonl` or copied into `finalized.jsonl`.
