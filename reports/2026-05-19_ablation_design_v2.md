本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Ablation Design v2

## Impact Estimate Before Execution

This task updates the repository-side experiment plan and adds this report. It does not modify the PI-maintained brief.

Files touched:

- `piwm_data/experiment_plan.md`
- `reports/2026-05-19_ablation_design_v2.md`

## Replacement Decision

The old four-group experiment design is replaced by A0-A4:

| ID | Stage-1 | Stage-2 | Why it exists |
|---|---|---|---|
| A0 | none | target 71 only | Provides the small-data target-only baseline. |
| A1 | state-only | target 71 only | Tests whether current-state perception pretraining is necessary. |
| A2 | state + transition | target 71 only | Tests whether action-conditioned world-model supervision adds value beyond state recognition. |
| A3 | state + transition | general policy/action + target 71 | Tests general-to-target transfer. |
| A4 | state + transition | general policy/action + weighted target 71 | Main model; tests weighted target adaptation. |

## Rationale

- A0 gives direct evidence for whether Stage-1 is necessary. If A0 is close to A2/A4, the Stage-1 story is weak.
- A1/A2 separate state recognition from transition/world-model contribution.
- A3/A4 separate general transfer from target-weighted adaptation.
- A4 is the main EMNLP-style low-resource target-specialization setup.

## What This Does Not Change

- It does not change the 5-act set.
- It does not start training.
- It does not change the 30-record balanced target test.
- It does not modify the PI brief.

