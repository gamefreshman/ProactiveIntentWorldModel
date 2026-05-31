# Stanford-Style Paper Review: PIWM Recent Draft

Reviewed source: `tmp/overleaf_edit/acl_latex.tex` synced with the live Overleaf draft on 2026-05-26.  
Review rubric basis: Stanford CS326 paper review guidance and Stanford Graphics paper-critique guidance.

## One-Paragraph Summary

The paper proposes SII (see, infer, intervene) for proactive retail assistance and instantiates it as PIWM, a Qwen2.5-VL-7B LoRA model that represents customer state with AIDA plus BDI, predicts action-conditioned intent transitions, and selects one of five service actions: `Greet`, `Elicit`, `Inform`, `Recommend`, or `Hold`. It introduces GuidanceSalesBench, a synthetic-plus-target retail benchmark with manifests, short videos, candidate actions, counterfactual outcomes, scores, and best-action labels. The main result is that PIWM reaches 0.641 macro F1 on Target-Test (n=30) under oracle customer-state conditioning, 0.734 on Cross-Domain (n=60), 0.295 end-to-end from video, and 0.579 action F1 on Real-Store Pilot (n=20). The paper's strongest empirical story is not that inference-time planning works, but that world-model-style state/outcome supervision plus balanced action training produces a stronger proactive action policy.

## What I Learned

- A proactive retail agent needs a non-intervention action; treating `Hold` as a first-class action is important and empirically difficult.
- AIDA-conditioned candidate filtering is not a minor implementation detail; it moves macro F1 from 0.504 to 0.641.
- Balanced action supervision is central: raw/small action training gives 0.390, while balanced 190-sample supervision gives 0.641.
- The world-model component is useful diagnostically and as training supervision, but explicit inference-time counterfactual planning underperforms direct policy selection.

## Strengths

1. **Clear and timely problem framing.** The SII framing is natural for proactive multimodal systems: description alone is insufficient, and the agent must decide whether and how to intervene before an explicit request.

2. **Good action-space design.** The five-action space is compact, interpretable, and domain-grounded. Including `Hold` makes the task less like generic sales recommendation and more like low-intrusion assistance.

3. **Structured dataset contribution.** GuidanceSalesBench records not only scenes and labels but also manifests, candidate sets, action-conditioned outcomes, and relative scores. This makes it more useful than a flat video-classification dataset.

4. **Ablations are unusually honest.** The paper directly reports that end-to-end action selection drops to 0.295, intent prediction is weak at 0.114, and inference-time planning is worse than direct action selection. That honesty makes the contribution more credible.

5. **The real-store pilot helps.** Even though n=20 is small, the 0.579 real-store action F1 is valuable evidence that the action-selection signal is not purely synthetic.

## Weaknesses / Criticism

1. **The main claim still risks overclaiming "world model" ability.** The best number, 0.641, is under oracle customer-state conditioning. End-to-end performance is much lower at 0.295, AIDA F1 is only 0.350, and intent F1 is 0.114. The paper now frames PIWM as a world-model-augmented action policy, which is the right direction, but the abstract and intro should be careful not to imply robust video-to-action world modeling.

2. **Evaluation scale is small.** Target-Test has only 30 examples, 6 per action. Real-Store Pilot has 20 fully annotated videos and no `Hold` examples. The reported confidence interval for PIWM on Target-Test is wide, so reviewers may see the result as promising but preliminary.

3. **Oracle-state evaluation needs stronger justification.** The paper says the main action result isolates action selection from state grounding, but the abstract only reports 0.641. A reviewer may object that the headline number depends on gold state, not video-only inference.

4. **Synthetic-label validity is the biggest dataset risk.** The dataset includes LLM-generated manifests/outcomes and structured validation, but the paper needs sharper evidence that best-action labels and action-conditioned outcomes are not just artifacts of the same generation rules. Human QA is mentioned, but the current draft should make the scope, expertise, and agreement/validation protocol concrete.

5. **The GPT-5.5 diagnostic row is risky.** Putting GPT-5.5 in the main table may distract reviewers because it is not an API-level, role-separated, reproducible closed-model baseline. It is marked diagnostic, but it still invites a fairness challenge.

6. **Candidate filtering may encode much of the task.** AIDA-conditioned candidate filtering substantially improves results. This is a legitimate design choice, but the paper should more explicitly argue why candidate filtering is part of the deployed system rather than label leakage or post-hoc narrowing.

7. **Sim-to-real evidence is promising but incomplete.** Real-store evaluation has only 20 full annotations, 10 weak labels, 20 missing files, and no independently annotated real-video intent labels. The paper already states this, but reviewers may still downgrade the real-world transfer claim.

8. **Presentation has some engineering artifacts.** The draft contains manual table counter adjustments and a placeholder anonymous URL. These are not scientific flaws, but they look fragile and should be cleaned before submission.

## Validity and Significance

The goal is significant: proactive multimodal assistance is a real gap between passive perception and embodied/action agents. The paper's narrower validated claim is sound: under structured customer-state conditioning, balanced action supervision and AIDA-constrained candidates improve best-action selection on a small target-domain test set. The broader claim that PIWM is an end-to-end proactive world model is only partially supported; current results identify state grounding and intent inference as bottlenecks rather than solved components.

## Methodology Quality

Methodology is directionally good but evidence-limited. The ablations cover the right axes: data composition, candidate filtering, planning, pipeline diagnostics, and oracle vs. end-to-end. The main weaknesses are sample size, synthetic-label provenance, and mismatch between oracle-state main evaluation and video-only deployment motivation. The counterfactual-planning ablation is especially useful because it prevents an unsupported planning claim.

## Writing and Structure

The writing is clear and the story is much stronger after reframing PIWM as a world-model-augmented action policy. Section 6 is now dense but useful. The most important writing fix is to align the abstract/introduction with the evidence: "strong action selection under oracle state; end-to-end remains limited" should be visible early, not only in Limitations.

## Reviewer-Likely Questions

1. How many human annotators reviewed the best-action and outcome labels, and what was their agreement or adjudication process?
2. Why is the main headline result oracle-state conditioned when the motivation is video-based proactive assistance?
3. How much of the improvement comes from AIDA candidate filtering versus learned action reasoning?
4. Are the synthetic outcomes and best-action labels generated by the same rules used to train/evaluate the model, creating circularity?
5. Why is GPT-5.5 included in the main table if the planned mid-tier API closed-source baselines were not run?
6. What happens on real-store examples containing `Hold`, since the current Real-Store Pilot (n=20) reports no `Hold` class?

## Scores

| Dimension | Score | Rationale |
|---|---:|---|
| Significance | 4 / 5 | Proactive retail intervention and non-intervention modeling are meaningful and underexplored. |
| Novelty | 3 / 5 | SII + AIDA/BDI + action-conditioned outcomes is a useful synthesis; not a fundamentally new learning algorithm. |
| Methodological convincingness | 2.5 / 5 | Ablations are good, but sample size, oracle-state dependency, and synthetic-label validity remain weak points. |
| Writing | 3.5 / 5 | Clear overall, but still needs sharper claim calibration and less table/appendix fragility. |
| Overall | 3 / 5 | Borderline. Promising contribution, but likely vulnerable to reviewer concerns unless claim scope and validation are tightened. |

## Recommendation

**Current review stance: borderline / weak reject for a top NLP venue if submitted as a strong end-to-end world-model paper; borderline / weak accept if framed as a new proactive retail benchmark plus world-model-augmented action-policy study with honest limitations.**

The safest submission framing is: PIWM demonstrates that structured state/outcome supervision and balanced action labels improve proactive action selection under a controlled oracle-state protocol; end-to-end video grounding remains an open bottleneck. This framing is defensible and matches the results.

## Must-Fix Before Submission

1. Replace the anonymous repo placeholder URL before final PDF export.
2. Make the abstract mention that the main 0.641 number is best-action selection under structured state conditioning, or add a short phrase that avoids implying full end-to-end video-to-action success.
3. Strengthen dataset validation: state who reviewed labels, what was checked, how disagreements were handled, and whether any human-vs-LLM validation sample exists.
4. Move GPT-5.5 out of the main table or keep it visually separated as diagnostic-only; otherwise it will invite baseline fairness criticism.
5. Add one sentence explaining why AIDA-conditioned candidates are part of the deployment policy, not an evaluation shortcut.
6. Keep the counterfactual-planning failure prominent; it protects the paper from overclaiming.
7. Clean table numbering/counter hacks after the final Overleaf compile.

## Stanford Rubric Mapping

- Summary: provided above in the one-paragraph summary.
- What was learned: action-conditioned supervision helps policy selection, while end-to-end state grounding remains weak.
- Praise: problem framing, action-space design, structured dataset, honest ablations.
- Criticism: oracle-state dependency, small evaluation, synthetic-label validity, baseline fairness.
- Goal validity/significance: valid and significant, but strongest as benchmark/action-policy work rather than full deployment-ready world modeling.
- Methodology quality: useful but limited by scale and annotation provenance.
- Discussion questions: listed under reviewer-likely questions.

Sources for review format:
- Stanford CS326 paper review guidance: https://web.stanford.edu/class/cs326/review.html
- Stanford Graphics critique guidance: https://graphics.stanford.edu/courses/cs448b-00-winter/critique.html
