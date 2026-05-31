# PIWM Real Eval Label-Source Breakdown

ALL contains 20 fully annotated videos plus 10 index-derived weak-label videos. Weak-label metrics are diagnostic only.

| Model | Group | Rows | Videos | Parse | Stage Acc | Stage F1 | Action Acc | Action F1 | Stage parsed N | Action parsed N |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base_qwen25vl7b_real_all_scored | ALL | 60 | 30 | 0.600 | 0.120 | 0.056 | 0.364 | 0.333 | 25 | 11 |
| base_qwen25vl7b_real_all_scored | human_json_annotation | 40 | 20 | 0.575 | 0.200 | 0.088 | 0.125 | 0.111 | 15 | 8 |
| base_qwen25vl7b_real_all_scored | index_group_weak_label | 20 | 10 | 0.650 | 0.000 | 0.000 | 1.000 | 1.000 | 10 | 3 |
| customer_state_effect_only_real_all_scored | ALL | 60 | 30 | 0.933 | 0.167 | 0.175 | 0.346 | 0.292 | 30 | 26 |
| customer_state_effect_only_real_all_scored | human_json_annotation | 40 | 20 | 0.925 | 0.250 | 0.200 | 0.235 | 0.217 | 20 | 17 |
| customer_state_effect_only_real_all_scored | index_group_weak_label | 20 | 10 | 0.950 | 0.000 | 0.000 | 0.556 | 0.444 | 10 | 9 |
| piwm_main_real_all_scored | ALL | 60 | 30 | 0.933 | 0.214 | 0.241 | 0.679 | 0.520 | 28 | 28 |
| piwm_main_real_all_scored | human_json_annotation | 40 | 20 | 1.000 | 0.300 | 0.262 | 0.600 | 0.579 | 20 | 20 |
| piwm_main_real_all_scored | index_group_weak_label | 20 | 10 | 0.800 | 0.000 | 0.000 | 0.875 | 0.600 | 8 | 8 |
