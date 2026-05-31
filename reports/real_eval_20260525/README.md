# PIWM Real Eval Inputs

Generated ms-swift rows for the real-video PIWM eval set.

- source: `references/piwm_lightweight/data/eval/real`
- human_annotation_records: 40
- index_derived_weak_label_records: 10
- runnable_records_with_video: 30
- label_source_counts_runnable: `{'human_json_annotation': 20, 'index_group_weak_label': 10}`
- skipped_missing_video_count: 20
- frame_timestamps_sec: `[0.0, 5.0, 10.0]`
- all_scored_jsonl: `reports/real_eval_20260525/real_all_scored.jsonl`

Primary metrics: Stage-1 `stage_accuracy` and Stage-2 `action_accuracy` / `action_macro_f1`.
Rows marked `index_group_weak_label` use group-level labels from `index.json` because per-session annotation JSON is missing.
The `intent_label` field is a deterministic heuristic derived from `best_action`, so treat intent metrics as secondary.
