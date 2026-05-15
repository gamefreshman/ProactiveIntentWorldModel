# Extraction Prompt

Extract only compact, source-faithful principles that can support PIWM
intent-tier rules. Do not quote source text. Do not infer a machine rule unless
the principle is explicitly marked as an engineering formalization in the rule
layer.

Required output fields:

- `principle_id`
- `source_id`
- `principle`
- `usable_for`
- `extraction_method`
- `copyright_note`
- `confidence`
