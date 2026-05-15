# Failure Mode Distillation Prompt

You are distilling failure-mode principles for PIWM action outcomes. Use only
the provided source locators and paraphrase notes. Do not quote or reconstruct
copyrighted text.

Return compact principles suitable for `ExtractedPrinciple`:

- one principle per line;
- 45 words or fewer;
- source-backed and operationalizable;
- usable for one or more of: `failure_mode`, `transition`, `risk_tags`,
  `candidate_actions`.

Focus on conditions where the same act can become harmful:

- recommending before need or commitment is clear;
- long feature-heavy explanations during low intent;
- pressure that threatens perceived choice freedom;
- interrupting focused comparison or private discussion.
