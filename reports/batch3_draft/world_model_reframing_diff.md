# World-Model Reframing Diff

Source basis: latest local Overleaf mirror `tmp/overleaf_edit/acl_latex_after.tex` (read-only). Do not apply automatically; merge manually after Batch 2 is stable.

## 1. Section 4 End: Outcome Modeling and Selection

**Insert after current Section 4.2 paragraph ending at `tmp/overleaf_edit/acl_latex_after.tex:262`:**

Current ending:

```tex
The selector $\pi$ is deterministic: it returns the candidate with score 5. Low-intrusion behavior is encoded through the candidate inventory and scoring rubric rather than an additional hand-designed cost function. For example, \textsc{Hold} can receive the highest score when the predicted intervention would disturb smooth browsing, while \textsc{Elicit} or \textsc{Inform} can be preferred when the customer shows uncertainty or an information gap.
```

Add:

```tex
While Equations (4)--(6) describe PIWM as a planning pipeline that estimates state, simulates outcomes, and selects actions, our empirical analysis (Section~\ref{tab:ablation_planning}) shows that the most effective use of the world-model component $h_{\phi}$ in practice is as training-time auxiliary supervision rather than as an inference-time planner. The action policy implicitly internalizes the action-conditioned reasoning, producing stronger best-action selection than counterfactual planning over explicit predicted outcomes. We retain the structured formulation because it (1) supports the dataset construction protocol (Section~5), (2) enables intermediate-state diagnostics (Section~6.5.4), and (3) provides a foundation for future work where stronger next-state prediction could make inference-time planning competitive.
```

Merge note: replace `Section~\ref{tab:ablation_planning}` with the actual section label if Section 6.5.3 has one. `\ref{tab:ablation_planning}` points to the table, not the subsection.

## 2. Section 6.5.3: Counterfactual Planning Prose

**Append one sentence to the current paragraph ending at `tmp/overleaf_edit/acl_latex_after.tex:578`:**

Current ending:

```tex
This suggests the world model functions as effective training-time supervision rather than as a standalone inference-time planner in the current setup. Figure~\ref{fig:trick6_distribution} shows the latest stage-reward prediction distribution against the balanced gold distribution.
```

Recommended replacement ending:

```tex
This suggests the world model functions as effective training-time supervision rather than as a standalone inference-time planner in the current setup. Together, the findings in this and the previous subsection suggest that PIWM functions as a world-model-augmented action policy: the world-model objective is essential as a training signal (Section~6.5.1), but the learned policy is the preferred decision-time component, not the predicted-outcome planner. Figure~\ref{fig:trick6_distribution} shows the latest stage-reward prediction distribution against the balanced gold distribution.
```

## 3. Conclusion Reframing

**Replace the first PIWM sentence in Conclusion at `tmp/overleaf_edit/acl_latex_after.tex:675`:**

Current:

```tex
This paper studies multimodal retail marketing as an SII problem: a device must see customer behavior, infer latent intent, and act before the customer makes an explicit request. We instantiate this view with PIWM, an intent-level world model that estimates AIDA--BDI customer state, predicts action-conditioned intent transitions, and selects from an AIDA-conditioned response set. Experiments on held-out target videos show that balanced action supervision and candidate constraints substantially improve best-action macro F1.
```

New:

```tex
This paper studies multimodal retail marketing as an SII problem: a device must see customer behavior, infer latent intent, and act before the customer makes an explicit request. We instantiate this view with PIWM, an intent-level world model that learns AIDA--BDI customer state estimation and action-conditioned intent transition prediction as auxiliary supervision for a proactive action selection policy. Experiments on held-out target videos show that balanced action supervision and candidate constraints substantially improve best-action macro F1.
```

