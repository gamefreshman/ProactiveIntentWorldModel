# piwm Sync Clarification: Scores and Real Videos

Date: 2026-05-21

## Summary

Two points need to be separated:

1. `script/gen_scores.py` in the lightweight `piwm` repo generates an LLM-assigned ordinal `score` field in `[1, 5]`. It is related to action preference, but it is **not the same field** as the main project's `preference_score` / reward.
2. `data/videos/real/21.mp4` to `35.mp4` contains **10 raw real videos**. They are **not yet the same thing** as the main project's planned `Real-50` / sim-to-real evaluation set, because they do not yet have a main-project manifest, QA status, labels, or an evaluation split.

## A. `script/gen_scores.py`

### What It Does

Path inspected:

```text
/Users/mutsumi/Desktop/WorkSpace/piwm/script/gen_scores.py
```

`gen_scores.py` is a post-processing utility for lightweight `piwm` labeled JSON files.

It reads:

```text
data/labeled/piwm_NNN.json
```

For records whose action outcomes do not yet contain a `score` field, it sends the current state and existing action outcomes to an LLM and asks for:

```json
{"scores": {"action_1": 5, "action_2": 3, "action_3": 1}}
```

Important constraints in the script:

- `score` is an integer from `1` to `5`.
- Exactly one candidate action must have `score=5`.
- The action with `score=5` is expected to correspond to `best_action`.
- The script does **not** regenerate `next_aida_stage` or `next_bdi`; it only adds scores to already generated outcomes.
- Default model in the script is `gpt-4.1`.

Current dry-run result:

```text
python3 script/gen_scores.py --dry-run
```

reports 118 lightweight `piwm` labeled files still missing `score`.

### Relationship to `preference_score`

They are not the same concept.

| Field | Repo | Type | Meaning | Current use |
|---|---|---:|---|---|
| `score` | lightweight `piwm` | integer `1-5` | LLM ordinal action quality score; one best action must be `5` | Used by lightweight `script/gen_sft.py` as Stage-2 supervision output |
| `preference_score` | main project / older lightweight records | continuous numeric reward-like value | Formula-derived synthetic preference from `delta_stage`, `delta_mental`, and `action_cost` | Imported by main project as reward / outcome preference |

In the main project, `scripts/import_piwm_target_dataset.py` currently expects each lightweight outcome to contain:

```text
preference_score
delta_stage
delta_mental
action_cost
risk
benefit
```

and imports:

```python
reward = float(outcome["preference_score"])
```

So main-project import currently treats `preference_score` as the reward field, not `score`.

### Should Main Project Import This Logic?

Recommendation: **do not import `gen_scores.py` directly into the main data pipeline as reward logic.**

Reason:

- `score` is a discrete LLM ranking label.
- `preference_score` is a continuous synthetic reward / preference proxy.
- Directly replacing one with the other would mix two supervision semantics and make reward comparisons unstable.

Useful path forward:

1. Keep `gen_scores.py` as a lightweight `piwm` SFT-helper for records that need `score` in the `1-5` format.
2. If the main project wants to import score-only records such as some newer `piwm_818+` samples, add an explicit adapter:
   - preserve `score` as `ordinal_score`;
   - optionally map `score` to a derived reward only with a documented conversion;
   - mark the provenance as `llm_ordinal_score`, not as formula-based `preference_score`.
3. Do not mix `score` and `preference_score` under the same field name.

## B. `data/videos/real/21.mp4` to `35.mp4`

### Count and Files

Path inspected:

```text
/Users/mutsumi/Desktop/WorkSpace/piwm/data/videos/real/
```

Current files:

```text
21.mp4
22.mp4
23.mp4
24.mp4
25.mp4
31.mp4
32.mp4
33.mp4
34.mp4
35.mp4
```

Count:

```text
10 mp4 files
```

Total size:

```text
317M
```

### Are These the Same as the Main Project's "~50 Real Videos"?

Current answer: **No, not yet.**

The main project currently says:

```text
sim_to_real_on_real_50: planned validation track, not current result.
The repo currently has a real-shooting manifest/protocol, not 50 collected and QA-reviewed real videos.
```

That means the main project does not yet recognize a finished `Real-50` dataset.

The 10 videos in lightweight `piwm` are real raw assets, but they are missing the main-project requirements:

- no main-project `ShootingClipRecord`;
- no mapping to PIWM state IDs;
- no 5-act label package;
- no QA status;
- no train/eval split;
- no sim-to-real metric result.

Therefore they can be described as:

```text
10 raw real-video candidates toward future sim-to-real evaluation
```

but not as:

```text
the Real-50 evaluation set
```

### Planned Use

Recommended current use:

| Use | Status | Reason |
|---|---|---|
| Training | Not recommended now | No labels, no QA, no action/outcome annotations |
| Evaluation | Candidate use after annotation | Could become part of sim-to-real eval after manifest + QA + labels |
| Data augmentation | Not yet | Would blur raw real footage with labeled training data before quality control |
| QA / calibration | Yes, as raw material | Useful for checking whether synthetic / target-frontcam behavior looks realistic |

Practical next step:

1. Build a small real-video manifest for these 10 clips.
2. Assign each clip a stable ID, e.g. `real_021`, `real_022`, ...
3. Extract fixed frames.
4. Label state, candidate actions, best action, and go/no-go.
5. Run QA.
6. Only after that decide whether they enter:
   - sim-to-real evaluation;
   - realshoot calibration;
   - or a future small real-data training split.

## Evidence Checked

Commands / files inspected:

```text
/Users/mutsumi/Desktop/WorkSpace/piwm/script/gen_scores.py
/Users/mutsumi/Desktop/WorkSpace/piwm/script/gen_sft.py
/Users/mutsumi/Desktop/WorkSpace/piwm/data/labeled/piwm_700.json
/Users/mutsumi/Desktop/WorkSpace/piwm/data/labeled/piwm_818.json
/Users/mutsumi/Desktop/WorkSpace/piwm/data/labeled/piwm_1000.json
/Users/mutsumi/Desktop/WorkSpace/piwm/data/videos/real/
/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/import_piwm_target_dataset.py
/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/docs/current/domain_specialization_experiment_plan.md
```

Validation snippets:

```text
lightweight piwm labeled files: 318
outcomes total: 1062
outcomes missing score: 472
outcomes missing preference_score: 315
real mp4 files: 10
real mp4 total size: 317M
```

## Decision Recommendation

Do not merge the lightweight `score` semantics into the main `preference_score` field.

Do treat the 10 real videos as a useful incoming raw asset batch, but keep them outside training and outside formal `Real-50` claims until they have manifest, labels, QA, and evaluation routing.

