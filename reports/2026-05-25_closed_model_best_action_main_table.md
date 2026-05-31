# Closed Model Best-Action Main Table

- eval set: `reports/closed_model_eval_set_60.jsonl`
- n: 60 (target 30 + general 30)
- closed-model inference: temperature=0, one call per sample, parse failures counted as wrong
- target 30 uses the historical PIWM 0.641 source file: `data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl`
- PIWM target 30 historical parsed-only macro F1 is reproduced: 0.641 over 28/30 parsed outputs. The table reports strict F1 with parse failures counted as wrong, hence 0.623.

| 模型 | target 30 F1 | general 30 F1 | combined 60 F1 | parse rate | modal prediction |
|---|---:|---:|---:|---:|---|
| PIWM 主模型 | 0.623 | 0.603 | 0.734 | 0.933 | Elicit / 23 / 60 |
| Stage-1 only | 0.227 | 0.299 | 0.259 | 0.917 | Hold / 34 / 60 |
| Zero-shot Qwen2.5-VL-7B | 0.154 | 0.116 | 0.142 | 0.433 | PARSE_FAIL / 34 / 60 |
| GPT-4o | 未跑 | 未跑 | 未跑 | - | 未跑：OpenRouter 余额不足 / HTTP 402 |
| Gemini 2.5 Flash | 未跑 | 未跑 | 未跑 | - | 未跑：OpenRouter 余额不足 / HTTP 402 |
| Claude Sonnet 4.6 | 未跑 | 未跑 | 未跑 | - | 未跑：OpenRouter 余额不足 / HTTP 402 |
| Grok-3 | 未跑 | 未跑 | 未跑 | - | 未跑：OpenRouter 型号不可用 / HTTP 404 |
| Random | 0.414 | 0.421 | 0.466 | 1.000 | Hold / 20 / 60 |

## Diagnostic Non-Baseline

This row is not part of the paper closed-model baseline. It is a local Codex CLI self-eval requested for diagnosis; `codex exec` is an agent surface rather than the OpenRouter/API role-separated inference path.

| 模型 | target 30 F1 | general 30 F1 | combined 60 F1 | parse rate | modal prediction |
|---|---:|---:|---:|---:|---|
| GPT-5.5 / Codex CLI self diagnostic | 0.622 | 0.573 | 0.648 | 1.000 | Hold / 17 / 60 |

## Per-Class Breakdown

### PIWM 主模型

| act | precision | recall | F1 | support |
|---|---:|---:|---:|---:|
| Greet | 1.000 | 0.667 | 0.800 | 6 |
| Elicit | 0.826 | 1.000 | 0.905 | 19 |
| Inform | 0.667 | 0.500 | 0.571 | 12 |
| Recommend | 0.636 | 0.700 | 0.667 | 10 |
| Hold | 0.889 | 0.615 | 0.727 | 13 |

### Stage-1 only

| act | precision | recall | F1 | support |
|---|---:|---:|---:|---:|
| Greet | 0.000 | 0.000 | 0.000 | 6 |
| Elicit | 0.444 | 0.211 | 0.286 | 19 |
| Inform | 0.222 | 0.167 | 0.190 | 12 |
| Recommend | 0.667 | 0.200 | 0.308 | 10 |
| Hold | 0.353 | 0.923 | 0.511 | 13 |

### Zero-shot Qwen2.5-VL-7B

| act | precision | recall | F1 | support |
|---|---:|---:|---:|---:|
| Greet | 0.000 | 0.000 | 0.000 | 6 |
| Elicit | 0.333 | 0.105 | 0.160 | 19 |
| Inform | 0.000 | 0.000 | 0.000 | 12 |
| Recommend | 1.000 | 0.100 | 0.182 | 10 |
| Hold | 0.357 | 0.385 | 0.370 | 13 |

### Random

| act | precision | recall | F1 | support |
|---|---:|---:|---:|---:|
| Greet | 1.000 | 0.333 | 0.500 | 6 |
| Elicit | 0.647 | 0.579 | 0.611 | 19 |
| Inform | 0.455 | 0.417 | 0.435 | 12 |
| Recommend | 0.300 | 0.300 | 0.300 | 10 |
| Hold | 0.400 | 0.615 | 0.485 | 13 |
