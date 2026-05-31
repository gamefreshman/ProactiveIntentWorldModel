# Codex CLI Self-Eval: Best-Action Diagnostic

- date: 2026-05-25
- eval set: `reports/closed_model_eval_set_60.jsonl`
- runner: `scripts/run_codex_self_eval.py`
- raw outputs: `reports/closed_model_eval_20260525/codex_self/raw_outputs.jsonl`
- summary: `reports/closed_model_eval_20260525/codex_self/summary.json`
- Codex CLI: `codex-cli 0.133.0-alpha.1`
- local Codex config at run time: `model = "gpt-5.5"`, `model_reasoning_effort = "xhigh"`
- status: diagnostic only; not an OpenRouter/API closed-model baseline and not included in the paper main table.

## Protocol Notes

- One Codex CLI invocation per sample.
- Each invocation received only the original best-action prompt text plus the 3 attached frame images.
- Gold labels were used only by the wrapper after the subprocess returned.
- The subprocess cwd is a repo-external temporary empty directory, removed after each sample.
- `codex exec` does not expose a strict no-tools/no-agent mode here, and the original system/user roles are represented inside a single CLI prompt. Treat this as a Codex-agent diagnostic, not apple-to-apple API evaluation.

## Results

| model | target 30 F1 | general 30 F1 | combined 60 F1 | parse rate | modal prediction |
|---|---:|---:|---:|---:|---|
| GPT-5.5 / Codex CLI self diagnostic | 0.622 | 0.573 | 0.648 | 1.000 | Hold / 17 / 60 |

Correct count: target 20/30, general 21/30, combined 41/60.

Prediction counts:

| act | pred_count |
|---|---:|
| Hold | 17 |
| Inform | 16 |
| Elicit | 11 |
| Recommend | 11 |
| Greet | 5 |

## Per-Class Breakdown

| act | precision | recall | F1 | support |
|---|---:|---:|---:|---:|
| Greet | 0.400 | 0.333 | 0.364 | 6 |
| Elicit | 0.727 | 0.421 | 0.533 | 19 |
| Inform | 0.625 | 0.833 | 0.714 | 12 |
| Recommend | 0.727 | 0.800 | 0.762 | 10 |
| Hold | 0.765 | 1.000 | 0.867 | 13 |

## Confusion Matrix

Rows are gold labels; columns are predictions.

| gold \\ pred | Greet | Elicit | Inform | Recommend | Hold |
|---|---:|---:|---:|---:|---:|
| Greet | 2 | 0 | 0 | 1 | 3 |
| Elicit | 3 | 8 | 6 | 1 | 1 |
| Inform | 0 | 1 | 10 | 1 | 0 |
| Recommend | 0 | 2 | 0 | 8 | 0 |
| Hold | 0 | 0 | 0 | 0 | 13 |

## Interpretation

Codex CLI parsed cleanly on all 60 samples and was strong on `Hold`, `Recommend`, and `Inform`. The main error mode is under-recalling `Elicit`: 11/19 Elicit gold samples were shifted into `Greet`, `Inform`, `Recommend`, or `Hold`.
