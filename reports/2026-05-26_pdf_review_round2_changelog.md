# PDF Review Round 2 Changelog

Date: 2026-05-26

## Scope

Updated the Overleaf main manuscript source (`acl_latex.tex`) and added the Real-Store Pilot gallery figure for the PDF Review Round 2 fixes. Main result numbers in Table 3 were not changed.

## Changes

### 1. Abbreviation Expansion

- Expanded first occurrence of `SII` in the abstract to `See--Infer--Intervene (SII)`.
- Expanded first occurrence of `AIDA` in the abstract to `AIDA (Attention, Interest, Desire, Action)`.
- Expanded first occurrence of `BDI` in the abstract to `BDI (belief, desire, intention)`.

### 2. Abstract Real-Store Framing

- Revised the real-store pilot sentence to explicitly state that it is staged and recorded with paid participants performing scripted customer behaviors.
- Kept the reported 0.579 action macro F1 and added the 10 additional index-labeled videos.

### 3. Section 6.1 Experimental Setup

- Added Target-Test stratification explanation: balanced best-action distribution (6 per action) while preserving representative AIDA stage distribution.
- Added hardware budget statement: each main training run uses approximately 9 A100-hours on A100 80GB hardware, with details in Appendix B.

### 4. Section 6.3 Baselines and Main Results

- Added explanation that higher Cross-Domain F1 reflects greater training coverage in general scenes than in the held-out target deployment scenario.
- Added a paragraph emphasizing that full PIWM gains come from the world-model training framework paired with balanced target-domain action supervision, while inference-time counterfactual planning is not used for the main result.
- Added paired-bootstrap interpretation: the paired macro-F1 difference CI does not contain zero even though marginal CIs partially overlap.

### 5. Limitations

- Added that the fully annotated Real-Store Pilot subset contains no `HOLD` samples, so real-world non-intervention behavior is not measured in that pilot.
- Added a `Single-backbone evaluation` limitation noting that PIWM is trained and evaluated only with Qwen2.5-VL-7B-Instruct.

### 6. Conclusion

- Added a concise numeric recap: 0.641 Target-Test oracle, 0.295 end-to-end video-only, 0.579 staged Real-Store Pilot, and 0.240 State-Outcome baseline.

### 7. Naming Consistency

- Checked and retained the naming convention:
  - Formal dataset name: `Real-Store Pilot`
  - Generic adjective form: `real-store`
  - No unhyphenated `real store` remains in the source.

### 8. Section 5.4 Dataset Statistics

- Added a sentence explaining that Target-Test intent distribution differs from General Synthetic because the deployment scenario emphasizes price/value comparison and option exploration.

### 9. Appendix Failure Cases

- Expanded the three representative failure cases with full gold state, visual evidence, gold action, PIWM prediction, rationale, and failure analysis:
  - `target_piwm_810`: `HOLD -> ELICIT`
  - `target_piwm_760`: `RECOMMEND -> INFORM`
  - `target_piwm_721`: `GREET boundary`
- Reduced the table body to `\scriptsize`; visual render check shows no text overlap.

### 10. Real-Store Frame Gallery

- Added Appendix section `Real-Store Pilot Frame Examples`.
- Generated and uploaded `real_store_gallery.pdf` to Overleaf.
- Local source copies:
  - `figures/real_store_gallery.pdf`
  - `figures/real_store_gallery.png`
  - `reports/figures_batch1/real_store_gallery.pdf`
- Gallery uses 8 fully annotated sessions, excluding the Figure 2 examples (`real_006`, `real_016`, `real_021`, `real_031`):
  - `real_007 / video_002`: Attention / GREET
  - `real_008 / video_003`: Attention / GREET
  - `real_017 / video_007`: Interest / ELICIT
  - `real_019 / video_009`: Interest / ELICIT
  - `real_022 / video_012`: Desire / INFORM
  - `real_024 / video_014`: Desire / INFORM
  - `real_032 / video_022`: Action / RECOMMEND
  - `real_035 / video_025`: Desire / RECOMMEND

## Validation

- Overleaf source copy-back matches local `tmp/overleaf_edit/acl_latex.tex` modulo trailing blank lines.
- Overleaf file tree contains `real_store_gallery.pdf`.
- Overleaf preview compiles and shows 22 pages; page 22 displays the Real-Store frame gallery.
- Overleaf log shows 0 errors and 3 warnings: `\showhyphens` changed, plus two pre-existing `tabularx` width warnings at lines 333 and 526. No unresolved-reference warning appears in the Overleaf warning panel.
- Local isolated compile succeeded with `latexmk`; output: `tmp/overleaf_edit/local_compile/acl_latex.pdf` (21 pages). The page-count difference is due to the local mirror using an incomplete local bibliography file while Overleaf has the active project bibliography.
- Local rendered visual checks:
  - `tmp/overleaf_edit/pdf_round2_render/round2_page_20.png`: expanded failure-case table, no overlap.
  - `tmp/overleaf_edit/pdf_round2_render/round2_page_21.png`: Real-Store gallery, correctly rendered.

## Grep Checks

```text
See--Infer--Intervene: 1
Attention, Interest, Desire, Action: 1
belief, desire, intention: 1
staged real-store pilot: 2
raw "real store": 0
Placeholder: 0
PLACEHOLDER: 0
auxiliary supervision: 0
Section 6.5 reports ablations on schema: 0
fig:data_pipeline: 0
world-model-as-auxiliary: 0
world-model-augmented: 3
```

## Notes

- The local isolated compile reports undefined citation warnings because `tmp/overleaf_edit/custom.bib` is not the full Overleaf bibliography. Overleaf compile uses the active project bibliography and builds with 0 errors.
- Table 3 result values were not modified.
- Figure 1 was not modified.
