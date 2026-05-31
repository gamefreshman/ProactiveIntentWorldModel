# PIWM Real Eval Summary

| Model | N | Parse | Stage Acc | Stage Macro F1 | Intent Acc | Action Acc | Action Macro F1 | Chosen Exact |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base_qwen25vl7b_real_all_scored | 60 | 0.600 | 0.120 | 0.056 | 0.000 | 0.364 | 0.333 | 0.364 |
| customer_state_effect_only_real_all_scored | 60 | 0.933 | 0.167 | 0.175 | 0.333 | 0.346 | 0.292 | 0.346 |
| piwm_main_real_all_scored | 60 | 0.933 | 0.214 | 0.241 | 0.286 | 0.679 | 0.520 | 0.679 |

Primary metrics are Stage Acc and Action Macro F1. Intent labels in the generated real set are heuristic, so Intent Acc is secondary.
