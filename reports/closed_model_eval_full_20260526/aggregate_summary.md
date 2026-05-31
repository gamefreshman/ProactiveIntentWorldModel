# Closed-Source Four-Scenario Evaluation

| Model | Target-Test (n=30) Oracle | Cross-Domain (n=60) Oracle | Target-Test E2E (n=30) | Real-Store Pilot (n=20) |
|---|---:|---:|---:|---:|
| Gemini 2.5 Flash | 0.659 (parse 0.967) | 0.638 (parse 0.933) | 0.216 (parse 0.833) | 0.655 (parse 0.800) |
| GPT-4o | 0.445 (parse 1.000) | 0.503 (parse 1.000) | 0.354 (parse 1.000) | 0.535 (parse 1.000) |
| Claude Sonnet 4.6 | 0.579 (parse 1.000) | 0.569 (parse 1.000) | 0.294 (parse 0.967) | 0.833 (parse 1.000) |

## Notes

- API provider: 302ai `/v1/chat/completions`.
- Target-Test oracle is derived from the target subset of the Cross-Domain oracle calls because the prompt and inputs are identical.
