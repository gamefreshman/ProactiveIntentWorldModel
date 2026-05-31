# Anonymous Repo and Data/Code Availability Changelog

Date: 2026-05-26

## Outputs

- Anonymous repo root: `/tmp/piwm_anon_repo/`
- Anonymous public URL: `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`
- Repo manifest: `reports/anon_repo_manifest_20260526.md`
- PI upload steps: `reports/2026-05-26_anonymous_repo_pi_steps.md`
- Paper source mirror updated: `tmp/overleaf_edit/acl_latex.tex`

## Completed Tasks

| Task | Status | Notes |
|---|---|---|
| A.1 Repo structure | Done | Created README, Apache-2.0 LICENSE, requirements, prompt/eval code, config, synthetic samples, real-store frames, and docs. Added minimal `piwm_infer/` and `piwm_data/` support modules so copied scripts compile. |
| A.2 Real-store frames | Done | Copied 30 runnable real-store samples x 3 frames = 90 JPGs from `reports/real_eval_20260525/frames/`. No full videos copied. |
| A.2 annotations | Done | Generated `data/real_store_frames/annotations.jsonl` with gold state, candidate action mapping, gold best action, PIWM prediction, and annotation source. |
| A.3 Synthetic samples | Done | Exported 3 representative `GuidanceSalesBench/general/main_schema.jsonl` samples covering attention, interest, and desire stages. |
| A.4 Code cleaning | Done | Removed absolute local/server paths, used relative placeholders, replaced internal report placeholders with neutral wording, and avoided copying private reports/tmp/checkpoints. |
| A.5-A.9 Docs/config | Done | Added README, official Apache-2.0 license text, requirements, LoRA YAML config, and Markdown prompt templates. |
| B Data/Code Availability | Done | Inserted unnumbered section after Limitations and before References in `tmp/overleaf_edit/acl_latex.tex`; synced the same source into the live Overleaf editor and recompiled. |
| C PI steps | Done | Created the private GitHub source repo, pushed commit `3a3c623`, generated the anonymous.4open.science mirror, and retained PI instructions for future URL maintenance. |

## Notes

- The user task mentioned sampled timestamps `t=2/5/8s`; the actual archived `reports/real_eval_20260525/manifest.json` records `[0.0, 5.0, 10.0]`, so the anonymous repo documentation uses the manifest-backed values.
- No frame exceeds 500 KB; JPEG recompression was not needed.
- Face blurring was not applied because release consent was confirmed by the project lead and only frames, not full videos, are included.

## Validation Status

- `python3 -m compileall` on released Python code: pass
- Real frames: 90 JPGs
- Annotation rows: 30
- Synthetic samples: 3
- Repo size before `.git`: 21.1 MB
- Repo size after `git init`: 42M
- Git commit: `3a3c623` on branch `main` with author `Anonymous <anonymous@anonymous.4open.science>`
- GitHub source repo: private repository pushed at commit `3a3c623`
- Anonymous mirror: `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`
- Leak grep after git commit: no hits for `/Users/`, `/root/lanyun-fs`, `mutsumi`, `qhdlink`, `lanyun`, `rtkvj`, SSH/server credential strings, or checked collaborator names
- Overleaf source sync: copied live `acl_latex.tex` back to `tmp/overleaf_edit/live_acl_latex_anonymous_repo.tex`; byte-for-byte matches `tmp/overleaf_edit/acl_latex.tex`
- Overleaf compile after initial Data/Code Availability sync: completed; PDF preview remained at 17 pages and the log indicator showed 2 warnings
- Anonymous URL publication: private GitHub repo was pushed, anonymous.4open.science mirror was generated, and the live Overleaf `acl_latex.tex` Data and Code Availability URL was updated to `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`
- Anonymous mirror public access check: README URL returned HTTP 200 and the ZIP endpoint downloaded successfully (21M); downloaded ZIP contains 90 frame images and no hits for local/server paths or checked identity terms.
- Overleaf compile after anonymous URL update: completed; PDF preview shows 19 pages and the log indicator shows 3 warnings
- Static reference check on mirrored TeX: 29 labels, 18 refs, 0 missing labels
