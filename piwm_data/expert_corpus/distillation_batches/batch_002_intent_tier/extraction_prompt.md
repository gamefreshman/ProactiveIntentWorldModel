# Intent Tier Distillation Prompt

You are distilling retail-pedagogy principles for PIWM. Use only the provided
source locators and paraphrase notes. Do not quote or reconstruct copyrighted
text.

Return compact principles suitable for `ExtractedPrinciple`:

- one principle per line;
- 45 words or fewer;
- source-backed and not speculative;
- usable for one or more of: `intent_tier`, `shopping_motivation`,
  `persona_interpretation`, `candidate_actions`.

Focus on whether observable behavior and persona framing indicate:

- `low_intent_browsing`: curiosity, recreational exploration, weak buying
  commitment, low tolerance for closing pressure;
- `exploring`: active information search or option comparison, medium
  readiness, useful response to elicitation and brief information;
- `ready_to_buy`: commitment cues, service approach, purchase confirmation,
  higher tolerance for specific recommendation.
