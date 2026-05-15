# PIWM Expert Distillation Batches

This directory records auditable distillation work before anything is promoted
into `distilled/`.

The current rule corpus is a seed baseline mirrored from `piwm_data/rules.py`.
New v2.2 knowledge must enter through a batch, be reviewed, and only then be
promoted into the main corpus. Batch files store compact paraphrases and
source locators only. Do not store long copyrighted excerpts here.

## Batch Contract

Each batch should contain:

- `source_additions.jsonl`: candidate `SourceRegistryEntry` rows.
- `extraction_prompt.md`: prompt/instructions used for extraction.
- `source_excerpts.jsonl`: short paraphrase notes and source locators.
- `extracted_draft.jsonl`: draft compact principles.
- `review_log.md`: human review checklist and decisions.
- `finalized.jsonl`: approved principles ready for promotion.
- `run_log.json`: model/tool settings and hashes for the extraction run.

## Current Batches

- `batch_001_seed`: documents the existing 72 seed rules.
- `batch_002_intent_tier`: intent-tier principles from consumer behavior and
  shopping motivation sources.
- `batch_003_failure_mode`: failure-mode principles from pressure/reactance
  and selling-process sources.
- `batch_004_recommend_pressure`: soft vs firm recommendation principles.
- `batch_005_source_hardening`: gift-shopping and hedonic-browsing source
  hardening before Phase 2 runtime integration.
