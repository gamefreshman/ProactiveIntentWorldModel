本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Stage-1 Split Content Validation

## Scope

This check validates the four Stage-1 train/val split files without regenerating them.

Files checked:

```text
data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl
data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl
data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl
```

## Reassure Grep

Command shape:

```bash
grep -i "reassure" <file> | wc -l
```

| File | Rows | `reassure` line count |
|---|---:|---:|
| `piwm_train_stage1_user_intent_train_v1.jsonl` | 493 | 0 |
| `piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 1816 | 0 |
| `piwm_train_stage1_user_intent_val_v1.jsonl` | 50 | 0 |
| `piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 185 | 0 |

Result: pass.

## best_action Field Check

The four Stage-1 split files contain no `best_action` field and no `best_act` field.

| File | `best_action` field count | `best_action` distribution |
|---|---:|---|
| `piwm_train_stage1_user_intent_train_v1.jsonl` | 0 | `{}` |
| `piwm_train_stage1_next_state_prediction_train_v1.jsonl` | 0 | `{}` |
| `piwm_train_stage1_user_intent_val_v1.jsonl` | 0 | `{}` |
| `piwm_train_stage1_next_state_prediction_val_v1.jsonl` | 0 | `{}` |

This is expected for Stage-1:

- `user_intent` rows train current state recognition.
- `next_state_prediction` rows train action-conditioned next-state prediction.
- Neither task is an action-selection task, so neither should contain `best_action`.

Therefore the brief distribution:

```text
Elicit=46% / Recommend=23% / Inform=19% / Hold=11% / Greet=0%
```

does not apply to these four Stage-1 split files. That distribution is an action-selection / best-act distribution, not a Stage-1 state/world-model split distribution.

## Candidate-act Distribution in next_state_prediction Rows

For reference only, the `next_state_prediction` rows do carry `candidate_act` because they ask the model to predict the future under one candidate action.

| Candidate act | Train | Val | Total |
|---|---:|---:|---:|
| Elicit | 433 | 43 | 476 |
| Inform | 439 | 42 | 481 |
| Hold | 405 | 44 | 449 |
| Recommend | 539 | 56 | 595 |
| Greet | 0 | 0 | 0 |
| Reassure | 0 | 0 | 0 |

This is not `best_action`; it is the set of candidate actions used for transition/world-model training.

## Hashes and mtimes

| File | mtime | sha256 |
|---|---|---|
| `piwm_train_stage1_user_intent_train_v1.jsonl` | `2026-05-19 21:29:27 CST` | `9e98a875906efc909ddaea3a6342f8ea42ab63342189f52d76e2eccd363a699f` |
| `piwm_train_stage1_next_state_prediction_train_v1.jsonl` | `2026-05-19 21:29:28 CST` | `e6acf951a22593f05f15b1981407ec49a07e5da45a93e4315e081cefb0be30b1` |
| `piwm_train_stage1_user_intent_val_v1.jsonl` | `2026-05-19 21:29:27 CST` | `34bac504a3498e57bbfb5e6e9f1e1ccb7b2fee55c6d7dde52f291b0e6e4ea3d0` |
| `piwm_train_stage1_next_state_prediction_val_v1.jsonl` | `2026-05-19 21:29:28 CST` | `3a2fc367461e1df6327ca48b3af30b2ef47c581b70d6cde4ffd7318a9abbdd31` |

The combined Stage-1 JSONL remains:

```text
path: /Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_user_intent_v1.jsonl
rows: 2544
sha256: 68f37965030cf7cb4fa79ee25da7259d42d11b47d1200b19392948aebd6093a7
mtime: 2026-05-20 14:19:08 CST
```

## Decision

Stage-1 data is ready for Stage-1 training with the following interpretation:

- It contains no `Reassure`.
- It contains no `best_action`, so the action-selection best-act distribution check is not applicable.
- The combined Stage-1 hash stays `68f37965...`.

