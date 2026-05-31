# Stanford Review Fixes Changelog

Date: 2026-05-26

## Scope

Target source: `tmp/overleaf_edit/acl_latex.tex`, then synced to the live Overleaf `acl_latex.tex`.

## Fixes Applied

| Item | Status | Change |
|---|---|---|
| Real data visibility | Done | Added an explicit Section 5 real-store data paragraph: 30 accessible paid-participant videos, 3 released frames per video, 20 full session-level annotations, 10 group-level index labels, 20 planned files inaccessible and excluded. |
| Real video slices in正文 | Done | Generated and uploaded `V6_real_store_video_slices.pdf`, then inserted a `figure*` in Section 5 immediately after the real-store data paragraph with four fully annotated real-store sessions and three sparse frames per session. |
| Dataset source table | Done | Replaced the ambiguous `Real-store videos / 50` row with explicit rows for 30 accessible pilot videos, 20 fully annotated, 10 index-labeled, and a separate row for 20 planned benchmark candidates with missing video files. |
| Experimental setup | Done | Replaced the old `50-video real-store benchmark` sentence with a precise real-store pilot description: 20 full annotations as the primary metric, 10 index-labeled videos as auxiliary real data, no training use. |
| Abstract oracle-state clarity | Done | Rewrote the abstract result sentence to state that 0.641 is under ground-truth customer-state conditioning and that end-to-end video-only selection is 0.295. Added the real-store pilot result: 0.579 action macro F1 on 20 fully annotated videos, with 10 additional index-labeled videos released. |
| Introduction oracle-state clarity | Done | Rewrote the Target-Test result sentence to say 0.641 uses the ground-truth customer-state representation and that Target-Test E2E reaches 0.295 without oracle state. Added the 30/20/10 real-store pilot split in the introduction. |
| Main result real-data note | Done | Expanded the Table 3 note to state that the 10 index-labeled videos and 20 missing planned videos are excluded from the primary Real-Store Pilot metric. |
| Real-data claim strength | Done | Changed the Real-Store Pilot interpretation from a broad synthetic-to-real claim to preliminary evidence, and added that the fully annotated real-store subset has no `Hold` cases, so it does not evaluate real-world non-intervention decisions. |
| Data/code availability | Done | Rewrote the release sentence to distinguish per-video frames for 30 accessible real-store videos, full session-level annotations for 20, group-level index labels for 10, and a manifest documenting 20 planned missing files. |
| Sim-to-real section wording | Done | Rewrote the Section 6.6 opening so Real-Store Pilot (n=20) clearly refers only to the full-annotation subset, while the 10 index-labeled videos are auxiliary release data. |
| Candidate filtering concern | Done | Added a deployment-policy explanation for AIDA-conditioned candidate filtering in Section 6.5.2. |
| Anonymous URL | Done | Created and pushed the private GitHub source repo, generated the anonymous.4open.science mirror, and replaced the paper's old anonymous URL placeholder with `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`. |

## Validation

- Static TeX reference check before Overleaf sync: 29 labels, 17 refs, 0 missing refs.
- Old anonymous URL marker count after update in `acl_latex.tex`: 0.
- Overleaf source sync: completed by replacing the live `acl_latex.tex` with `tmp/overleaf_edit/acl_latex.tex`.
- Overleaf compile: completed; PDF preview shows 18 pages and 3 log warnings.
- Copied-back Overleaf source check: exact byte-for-byte match with `tmp/overleaf_edit/acl_latex.tex`.
- Copied-back source contains the new oracle-state abstract wording, real-store pilot abstract sentence, precise real-data availability wording, and no draft placeholder markers.
- Real-slice figure source: `reports/figures_batch1/V6_real_store_video_slices.py`.
- Real-slice figure outputs: `reports/figures_batch1/V6_real_store_video_slices.pdf` and `.png`.
- Overleaf V6 sync: `V6_real_store_video_slices.pdf` is present in the Overleaf file tree, `acl_latex.tex` references `V6_real_store_video_slices.pdf` and `fig:real_store_slices`, compile completed with 19 pages and 3 log warnings.
- Copied-back Overleaf source after V6 insertion: exact byte-for-byte match with `tmp/overleaf_edit/acl_latex.tex`.
- Anonymous repo check: `/tmp/piwm_anon_repo` exists, is pushed to a private GitHub repo at commit `3a3c623`, size is 42M, contains 90 real-store frame images and 30 annotation rows. The generated anonymous URL is `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`.
- Overleaf anonymous URL sync: live `acl_latex.tex` now shows the generated anonymous URL in Data and Code Availability; compile completed with 19 pages and 3 log warnings.

## Notes

- The real-store frame release uses the archived real-eval manifest timestamps (0s, 5s, 10s), while the generic frame-extraction appendix still documents the default synthetic sampling plan (2s, 5s, 8s).
