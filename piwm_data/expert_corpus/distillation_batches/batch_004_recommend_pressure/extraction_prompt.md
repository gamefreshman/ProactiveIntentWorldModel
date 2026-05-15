# Recommend Pressure Distillation Prompt

You are distilling principles that distinguish soft and firm recommendation in
PIWM. Use only the provided source locators and paraphrase notes. Do not quote
or reconstruct copyrighted text.

Return compact principles suitable for `ExtractedPrinciple`:

- one principle per line;
- 45 words or fewer;
- source-backed and operationalizable;
- usable for one or more of: `recommend_pressure`, `transition`,
  `candidate_actions`, `failure_mode`.

Focus on:

- soft recommendation after a need or tradeoff is visible;
- firm recommendation only after strong commitment or explicit request;
- preserving choice language when intent is still exploratory;
- consequences of pressure mismatch.
