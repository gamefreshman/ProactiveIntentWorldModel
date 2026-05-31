# Closed Model Eval Changelog

Date: 2026-05-26

## Scope

- Provider: 302ai only; OpenRouter was not attempted per PI instruction.
- Models: Gemini 2.5 Flash (`gemini-2.5-flash`), GPT-4o (`gpt-4o`), Claude Sonnet 4.6 (`claude-sonnet-4-6`).
- Prompts: reused serialized PIWM system/user prompt text and XML parsers; `<image>` placeholders were replaced with API-native `image_url` inputs.
- Target-Test oracle metrics are derived from Cross-Domain target-subset outputs to avoid duplicate identical API calls.

## API Preflight

- Model-list result: `{"count": 725, "selected": {"gemini_2.5_flash": "gemini-2.5-flash", "gpt_4o": "gpt-4o", "claude_sonnet_4.6": "claude-sonnet-4-6"}, "missing": {}}`
- Balance endpoint result: `{"ok": false, "status": 403, "body": "{\"error\":{\"err_code\":403,\"message\":\"\",\"message_cn\":\"\",\"message_jp\":\"\",\"type\":\"api_error\"}}"}`

## Results

| Model | Target Oracle | Cross-Domain Oracle | E2E | Real-Store |
|---|---:|---:|---:|---:|
| Gemini 2.5 Flash | 0.659 (parse 0.967) | 0.638 (parse 0.933) | 0.216 (parse 0.833) | 0.655 (parse 0.800) |
| GPT-4o | 0.445 (parse 1.000) | 0.503 (parse 1.000) | 0.354 (parse 1.000) | 0.535 (parse 1.000) |
| Claude Sonnet 4.6 | 0.579 (parse 1.000) | 0.569 (parse 1.000) | 0.294 (parse 0.967) | 0.833 (parse 1.000) |

## Usage / Cost Tracking

- 302ai balance endpoint returned 403 for this API key, so balance-delta cost could not be queried from the API in this run.
- Raw `usage` objects returned by the chat-completions API are stored per request in each scenario JSONL and summed in each model `summary.json`.
- If 302ai dashboard access is enabled later, cost can be reconciled against the request ids stored in raw outputs.

## Real-Store Pilot Frame Transmission Log

Real-Store Pilot uses 20 fully human-annotated sessions. For each completed model run, 20 sessions x 3 frames = 60 real-store images were transmitted to 302ai via HTTPS POST. PI confirmed participant release-form coverage for public release/API transmission. Request timestamps, image paths, and response ids are logged in each model's `real_store_20.jsonl`.

## Parse Warnings

- No scenario fell below the 0.70 parse-rate check threshold. Lowest parse rates were Gemini Real-Store (0.800) and Gemini Target-Test E2E step-2 parse (0.833).

## Manuscript Update

- Updated Overleaf project `6a0ab89c3af80cd32d608e60` directly in the web editor (`acl_latex.tex`).
- Table 3 now includes Gemini 2.5 Flash, GPT-4o, and Claude Sonnet 4.6 rows with strict macro F1 values.
- Section 6.3 now describes the mixed closed-source comparison: Gemini strongest on oracle Target/Cross among closed-source baselines, GPT-4o strongest on E2E, Claude strongest on Real-Store.
- Limitations now include a scale/model-family gap item reflecting mixed closed-source results.
- The Overleaf compile button returned to `Recompile` after compilation; no fatal compile blocker was visible in the editor.
