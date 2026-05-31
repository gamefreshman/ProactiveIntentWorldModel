本报告 5-act = Greet/Elicit/Inform/Recommend/Hold

# Target Test Stage / Best-action Matrix

## Scope

This report checks the current 30-record balanced target test under the locked 5-act set.

Input:

```text
data/official/piwm_target_v1/main_schema.jsonl
```

Filter:

```text
split == "test"
```

## Matrix: AIDA stage x best_action

| AIDA stage | Greet | Elicit | Inform | Recommend | Hold | Row total |
|---|---:|---:|---:|---:|---:|---:|
| attention | 0 | 3 | 0 | 0 | 0 | 3 |
| interest | 0 | 3 | 3 | 0 | 4 | 10 |
| desire | 0 | 0 | 3 | 6 | 2 | 11 |
| action | 6 | 0 | 0 | 0 | 0 | 6 |
| column total | 6 | 6 | 6 | 6 | 6 | 30 |

## Why attention has only 3 rows while Greet has 6

The 30-record target test is balanced by `best_action`, not by AIDA stage.

All 6 `Greet` best-action rows are currently in the `action` stage:

```text
target_piwm_718
target_piwm_719
target_piwm_720
target_piwm_721
target_piwm_789
target_piwm_790
```

So the reason is not that `Greet` spans multiple stages in this test. It is also not a label inconsistency under the current stage-conditioned design. The design allows:

```text
action -> Greet / Recommend / Hold
```

In the current target data, `Greet` appears as a close/completion-style terminal response in action-stage situations, not only as an opening greeting in attention-stage situations.

The attention-stage test rows are all `Elicit`:

```text
target_piwm_703
target_piwm_704
target_piwm_705
```

This means the test is action-balanced but not stage-balanced.

## Stage-conditioned Candidate Check

Candidate rule:

| AIDA stage | Candidate acts |
|---|---|
| attention | `Greet / Elicit / Inform / Hold` |
| interest | `Elicit / Inform / Recommend / Hold` |
| desire | `Inform / Recommend / Hold` |
| action | `Greet / Recommend / Hold` |

Result:

```text
best_act outside candidate set = 0 / 30
```

No violations were found.

## Candidate-size Distribution

| Candidate set size | Rows |
|---:|---:|
| 4 | 13 |
| 3 | 17 |

Breakdown:

| AIDA stage | Rows | Candidate count |
|---|---:|---:|
| attention | 3 | 4 |
| interest | 10 | 4 |
| desire | 11 | 3 |
| action | 6 | 3 |

## Per-record Check

| state_id | stage | best_act | stage-conditioned candidates |
|---|---|---|---|
| target_piwm_700 | interest | Elicit | Elicit / Inform / Recommend / Hold |
| target_piwm_701 | interest | Elicit | Elicit / Inform / Recommend / Hold |
| target_piwm_702 | interest | Inform | Elicit / Inform / Recommend / Hold |
| target_piwm_703 | attention | Elicit | Greet / Elicit / Inform / Hold |
| target_piwm_704 | attention | Elicit | Greet / Elicit / Inform / Hold |
| target_piwm_705 | attention | Elicit | Greet / Elicit / Inform / Hold |
| target_piwm_706 | interest | Elicit | Elicit / Inform / Recommend / Hold |
| target_piwm_707 | interest | Inform | Elicit / Inform / Recommend / Hold |
| target_piwm_708 | interest | Inform | Elicit / Inform / Recommend / Hold |
| target_piwm_712 | desire | Inform | Inform / Recommend / Hold |
| target_piwm_713 | desire | Inform | Inform / Recommend / Hold |
| target_piwm_714 | desire | Inform | Inform / Recommend / Hold |
| target_piwm_718 | action | Greet | Greet / Recommend / Hold |
| target_piwm_719 | action | Greet | Greet / Recommend / Hold |
| target_piwm_720 | action | Greet | Greet / Recommend / Hold |
| target_piwm_721 | action | Greet | Greet / Recommend / Hold |
| target_piwm_760 | desire | Recommend | Inform / Recommend / Hold |
| target_piwm_762 | desire | Recommend | Inform / Recommend / Hold |
| target_piwm_763 | desire | Recommend | Inform / Recommend / Hold |
| target_piwm_764 | desire | Recommend | Inform / Recommend / Hold |
| target_piwm_765 | desire | Recommend | Inform / Recommend / Hold |
| target_piwm_766 | desire | Recommend | Inform / Recommend / Hold |
| target_piwm_789 | action | Greet | Greet / Recommend / Hold |
| target_piwm_790 | action | Greet | Greet / Recommend / Hold |
| target_piwm_810 | interest | Hold | Elicit / Inform / Recommend / Hold |
| target_piwm_811 | interest | Hold | Elicit / Inform / Recommend / Hold |
| target_piwm_812 | desire | Hold | Inform / Recommend / Hold |
| target_piwm_813 | interest | Hold | Elicit / Inform / Recommend / Hold |
| target_piwm_816 | interest | Hold | Elicit / Inform / Recommend / Hold |
| target_piwm_817 | desire | Hold | Inform / Recommend / Hold |

