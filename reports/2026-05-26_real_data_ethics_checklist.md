# Real-Data Ethics Checklist

Date: 2026-05-26

## Current Evidence in Repo

- `docs/current/piwm_real_shooting_execution_checklist_v2.md` defines the real-data collection as PIWM research-data filming, not product publicity. It specifies 10-second clips, A/B scripted interventions, post-hoc data owner labeling, and QA gates.
- `docs/current/piwm_real_shooting_scripts_S01_S12.md` is the concrete shooting script used by filming teams. It specifies scripted customer states, A/B responses, terminal-centric realization, and a no-sensitive-information QA check.
- `docs/source_materials/2026-05-action-space/shooting_plan_v4.md` frames the earlier plan as actor interaction with a smart sales cabinet in an internal showroom and includes a public-usability check: no unlicensed faces, QR codes, payment codes, or third-party brands.
- `reports/real_eval_20260525/manifest.json` records the evaluated real-video split: 50 candidate videos, 30 accessible/runnable videos, 20 missing video files, 20 runnable videos with full human JSON annotation, and 10 runnable videos with index-level weak labels.
- `reports/anon_repo_manifest_20260526.md` records the anonymous-release artifact: 30 videos represented by 90 frames, 30 annotation rows, 20 full human annotations, 10 weak labels, and no full videos/checkpoints in the anonymous repo.

## Ethics Items We Should Cover

1. **Scripted participant filming, not covert customer surveillance.**
   State that the real-store pilot consists of scripted filming with paid adult participants/actors in a controlled retail/showroom setting. Avoid wording that implies hidden surveillance of ordinary shoppers.

2. **Consent and release.**
   State only if confirmed by project records: participants gave informed consent for research use and release of recorded footage or sampled frames. Because faces are visible in the released frames, the consent/release form should explicitly cover public research release, anonymous-review release, and future full-video release.

3. **No minors and no vulnerable population.**
   Confirm participants were adults. If true, state that no minors or vulnerable populations were recruited.

4. **Compensation and voluntariness.**
   State that participants were paid recruits and that participation was voluntary. Keep signed compensation/consent records outside the anonymous repo.

5. **Privacy and incidental bystanders.**
   The shooting QA already requires no unlicensed faces, phone numbers, QR/payment codes, or private information. Ethics text should say frames were screened for these items and that clips with unauthorized bystanders or sensitive background information are excluded or reshot.

6. **Data minimization for release.**
   During review, release only 3 sparse frames per accessible video plus JSON annotations, not full videos. Full videos should be released only after licensing/consent terms are finalized.

7. **Real data is held-out transfer evaluation, not training data.**
   State that real-store footage is used for sim-to-real transfer evaluation and frame-release demonstration, not for PIWM training.

8. **Latent-state labels are annotator inferences.**
   Because AIDA/BDI labels infer customer state, avoid treating them as factual mental states. Use wording such as "annotator-inferred customer-state labels" or "structured state annotations" and note that the model should not be used for high-stakes psychological inference.

9. **Potential misuse and deployment boundary.**
   Acknowledge that proactive retail agents can be misused for intrusive persuasion or surveillance. State that the action space includes `Hold` as a non-intervention option, that candidate actions are low-pressure service interventions, and that deployment requires signage, opt-out, and local privacy compliance.

10. **IRB / ethics-review determination.**
    Do not claim IRB approval unless a formal approval or exemption letter exists. If there is no IRB record, PI should obtain either an institutional IRB/exemption determination or a written internal ethics determination before submission. For manuscript wording, use a placeholder until confirmed.

## Missing Items to Confirm Before Final Paper

- Written consent/release form exists and covers: research use, publication of sampled frames, anonymous-review repository, future full-video release, visible face/body appearance, withdrawal window, compensation, data retention, and contact information.
- Participant population: adults only, no minors, no vulnerable groups.
- Collection location: controlled internal showroom / staged retail setting, not covert public surveillance.
- Bystander policy: no unconsented bystanders; clips with bystanders are excluded, blurred, or reshot.
- Institutional status: IRB approved, IRB exempt, not-human-subjects determination, or internal company ethics review.
- Licensing decision for real frames and future full videos.

## Draft Ethics Statement Snippet

```latex
\section*{Ethics Statement}

The real-store pilot was collected through scripted filming with paid adult participants in a controlled retail/showroom setting. These videos are staged service-interaction scenarios rather than covert recordings of ordinary shoppers. Participants were informed about the research purpose and consented to research use and release of the recorded footage or sampled frames. Signed consent and release records are retained internally and are not included in the anonymous repository.

To reduce privacy risk during review, the anonymous release includes only three sparsely sampled frames per accessible video together with JSON annotations; full videos are withheld until final licensing and release terms are confirmed. We screen released frames and clips for unauthorized bystanders, phone numbers, QR or payment codes, and other private background information. Clips failing these checks are excluded, corrected, or reshot.

The real-store footage is used only for held-out sim-to-real transfer evaluation and release demonstration, not for model training. Customer-state labels such as AIDA stage and BDI fields are annotator-inferred structured labels rather than verified psychological facts. PIWM is intended as a low-pressure service-assistance research prototype; deployment in real stores would require visible notice, opt-out mechanisms, local privacy compliance, and safeguards against intrusive persuasion.

[IRB/ethics-review status to be inserted after PI confirms the institutional determination.]
```

