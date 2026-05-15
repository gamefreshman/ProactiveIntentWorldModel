# Review Log: batch_002_intent_tier

Status vocabulary: `pending`, `approved`, `revise`, `reject`.

Checklist for each principle:

- faithful to the source locator and paraphrase note;
- compact enough to be auditable;
- operationalizable as a rule or schema condition;
- no long copyrighted source text;
- not duplicative or conflicting with existing principles.

| ID | Source | Draft principle | Usable for | Schema | Decision | Notes |
|----|--------|-----------------|------------|--------|----------|-------|
| P_INTENT_TIER_001 | SRC_SALES_CONSUMER_DECISION_001 | Customer intent tier should distinguish browsing, exploration, evaluation, and purchase-readiness cues. | intent_tier, state_progression | ok | approved | Clear umbrella principle for tiered intent modeling; grounded in decision-process staging. |
| P_INTENT_TIER_002 | SRC_SALES_CONSUMER_FACTORS_001 | Persona traits should inform intent tier only when they are supported by observable shopping behavior. | intent_tier, persona_interpretation | ok | approved | Useful guardrail: persona is prior evidence, not a label override without visible cues. |
| P_INTENT_TIER_003 | SRC_SALES_BABIN_HEDONIC_UTILITARIAN_1994 | Recreational shopping cues can indicate lower immediate purchase intent than task-oriented evaluation cues. | intent_tier, shopping_motivation | ok | approved | Supports low-intent/recreational browsing distinction while preserving uncertainty with can indicate. |
| P_INTENT_TIER_004 | SRC_SALES_BELLENGER_RECREATIONAL_SHOPPER_1980 | Recreational browsing should be treated as low-intent unless accompanied by clear evaluation or commitment cues. | intent_tier, shopping_motivation | ok | approved | Operational rule for treating recreational browsing as low intent unless stronger cues appear. |

## Reviewer Notes

- Pending review. Do not promote this batch until decisions are changed
  to `approved` in `extracted_draft.jsonl` or copied into `finalized.jsonl`.
