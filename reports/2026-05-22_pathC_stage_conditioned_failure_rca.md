本报告 5-act = Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入 operational 输出。

# Path C stage-conditioned probe failure RCA

## Why this report exists

The corrected stage-conditioned quick probe shows Path C is below random baseline:

| Metric | Value |
|---|---:|
| strict macro F1 | 0.227 |
| parsed-only macro F1 | 0.240 |
| random-candidate macro F1 | 0.414 |
| strict delta vs random | -0.187 |

This report explains the immediate causes and proposes the smallest repair plan before launching Stage-2 A0-A4.

## Root causes

### 1. Evaluation parser originally over-rejected valid stage-conditioned keys

The first probe showed 7 parse errors. Three of them were not real model-format failures:

| source_id | predicted chosen | local candidate table status |
|---|---|---|
| target_piwm_721 | `Recommend_action_stage_conditioned_target_piwm_721_38623010cdef` | valid |
| target_piwm_760 | `Inform_desire_stage_conditioned_target_piwm_760_e7247f5d4264` | valid |
| target_piwm_812 | `Inform_desire_stage_conditioned_target_piwm_812_24f402b2bf2e` | valid |

Cause: `scripts/eval_ms_swift_checkpoint.py` used the default parser for `action_selection_5act`, which only accepts `Act_12hex`-style labels unless `valid_actions` is provided. Stage-conditioned placeholder keys are longer, so valid model outputs were rejected.

Fix already applied locally: pass each row's `meta.candidate_action_acts.keys()` into `parse_action_output(...)`.

### 2. Real structured-output failures remain

After the parser fix, 4 rows still fail:

| source_id | stage | gold | failure |
|---|---|---|---|
| target_piwm_708 | interest | Inform | unclosed `intervention_utterance` |
| target_piwm_712 | desire | Inform | unclosed `intervention_utterance` |
| target_piwm_713 | desire | Inform | unclosed `intervention_utterance` |
| target_piwm_718 | action | Greet | misspelled `</rationale>` as `</rationationale>` |

Likely causes:

- `max_new_tokens=256` is too tight for some verbose rationales and action text.
- The model is not yet robust at copying the full XML-like output schema under action-selection prompts.

Minimal test before training changes: rerun the same probe with `--max-new-tokens 384` or `512`.

### 3. Hold overprediction remains severe

Strict prediction counts after parser fix:

| Prediction | Count |
|---|---:|
| Hold | 18 |
| Inform | 5 |
| Recommend | 2 |
| Elicit | 1 |
| Greet | 0 |
| parse_error | 4 |

Gold is balanced at 6 per act, so Hold should be around 6, not 18.

Interpretation:

- Path C is still a Stage-1 checkpoint, not action-selection-specialized.
- The model seems to use a conservative "do not disturb" heuristic when uncertain.
- `Hold_eda24b4bb712` is a short, stable key with a simple utterance `（静默）`, making it easier to copy than long stage-conditioned keys.

### 4. Greet is never selected

All 6 gold Greet rows are `stage=action`, not opening greetings. In this dataset, `Greet` is effectively a closing/acknowledgement act after the customer reaches an action-ready state.

The model likely interprets `Greet` as ordinary opening greeting, while the visual state says the customer is already near confirmation. It therefore prefers Hold or Recommend rather than the gold `Greet` closing action.

This is an act-semantics mismatch:

- dataset meaning: `Greet(close)` = closing acknowledgement / warm transaction support
- common language prior: `Greet` = opening hello

## Minimum repair plan before Stage-2

### Repair 1: Prompt-format repair

Goal: reduce parse errors and invalid key generation.

Recommended changes:

1. Increase probe generation limit from 256 to 384 or 512.
2. Add a strict instruction in action-selection prompt:
   - "Copy exactly one candidate label from the list."
   - "Do not invent or modify candidate labels."
   - "Output all four tags and close every tag."
3. Consider moving candidate labels into a compact numbered table:
   - `A: <full_key> act=...`
   - `B: <full_key> act=...`
   But keep the required output as the original full key unless the downstream parser is changed.

### Repair 2: Greet semantic disambiguation

Goal: make target `Greet` learnable.

Recommended prompt wording:

```text
In this 5-act target setting, Greet means a short terminal greeting or closing acknowledgement.
For action-stage shoppers, Greet can mean welcoming/confirming/thanks-style support near transaction completion, not only an opening hello.
```

This should be included in action-selection prompts and Stage-2 training examples.

### Repair 3: Hold anti-collapse

Goal: prevent the model from treating uncertainty as automatic Hold.

Recommended options:

1. Training-side: oversample non-Hold target examples or downweight Hold rows.
2. Inference-side: use the existing Hold prior penalty sweep (`lambda=0.5/1.0/1.5`) only after action-selection fine-tuning starts.
3. Prompt-side: add "Hold is only correct when the customer likely prefers no intervention; uncertainty alone is not enough."

## Recommended next order

Do not launch full A0-A4 yet.

Run these in order:

1. Rerun this exact stage-conditioned probe with `max_new_tokens=512` to separate true decision failure from output truncation.
2. Apply prompt-format repair and Greet semantic disambiguation to action-selection prompts.
3. Rebuild only the target action-selection training/eval JSONL; do not change 5-act or gold labels.
4. Run a small A0 smoke train, not full A0-A4:
   - short Stage-2 adaptation on target-only or GreetAug-v2 target
   - evaluate on the same 30 stage-conditioned test
5. Proceed to full A0-A4 only if smoke strict macro F1 rises above random baseline or if PI explicitly decides the baseline risk is acceptable.

## Current no-go statement

Based on the corrected probe, Path C alone is **not healthy enough** to justify full Stage-2 A0-A4 launch. The next move should be a small prompt/schema repair plus smoke probe, not a full experimental run.

