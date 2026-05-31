# 5-Frame Ablation Recheck

The earlier blocked diagnosis was too strong.

Original reason recorded here: target-domain training rows under `data/official/piwm_target_v1/frames/` expose only the three extracted frame images used by the main PIWM setup, and the corresponding source `video.mp4` files were not found on the A100 server.

Recheck result:
- Local repository source: `/Users/mutsumi/Desktop/WorkSpace/piwm/data/videos/synth` contains all 118/118 `PIWM-Target-Frontcam-v1` source videos.
- Local official 5-frame artifacts already exist for target-frontcam data: `data/official/ms_swift_5frame/piwm_train_stage2_target_5act_greet_aug_v2.jsonl` has 86 rows with 5 images each, and `data/official/domain_specialization_eval_v2_5frame/target_frontcam_5act_test_action_selection.jsonl` has 30 rows with 5 images each.
- A100 source coverage before recovery: `/root/lanyun-fs/piwm/data/videos/synth` contains only 8/118 target videos. For the current 2734-row balanced training JSONL, A100 video index covers 543/614 sessions and misses 71 sessions / 71 rows; all missing sessions are target numeric `piwm_*` videos.
- HuggingFace public check: the public `guochenmeinian` profile lists only `openreview_dataset` and `openreview_raw`; `guochenmeinian/piwm` is not accessible through the public HuggingFace API in this environment.

Updated status: superseded by `reports/ablation_5frame_20260526_0640/`.

The recovery path was executed after this recheck:
- synced local 118/118 target source videos to A100;
- rebuilt the 5-frame mirror with 2734/2734 train rows, no skipped rows, and `image_count=5`;
- launched 5-frame training with unchanged batch-2 ablation hyperparameters.

The training attempt failed at the first training step with CUDA OOM, so the current final status for this ablation is "data recovered; training failed: OOM", not "source videos missing".
