# Maotai Gold Sales Questionnaire Source Package

This package records the structured intake of three anonymized Maotai retail-sales expert questionnaires. It is an internal expert-practice source, not a public textbook or paper source.

## Contents

- `structured_records.json`: normalized questionnaire JSON for `salesperson_A`, `salesperson_B`, and `salesperson_C`.
- `source_manifest.json`: source ids, checksums, use policy, and reviewer boundary.

## Intake Summary

- `salesperson_A` from `茅台金牌导购深度知识-01.pdf`: experience `3-5年（独当一面）`, non-null field count `631`.
- `salesperson_B` from `茅台金牌导购深度知识-02.docx`: experience `1年以下（新手上路）`, non-null field count `661`.
- `salesperson_C` from `茅台金牌导购深度知识-03.docx`: experience `1年以下（新手上路）`, non-null field count `473`.

Global counts:
- field values: `3088`
- null values: `1323`
- unreadable markers: `5`

## Use Boundary

Use this package to derive compact, reviewed expert principles. Do not use the questionnaire wording as direct model-training text until it has been anonymized and reviewed.
