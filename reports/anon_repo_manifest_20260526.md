# Anonymous Repo Manifest
Date: 2026-05-26
Root: `/tmp/piwm_anon_repo/`
Anonymous URL: `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`

## Summary
- Total files (excluding `.git`): 114
- Total size (excluding `.git`): 21.1 MB
- Total repo size after `git init` (`du -sh`): 42M
- Real-store frame count: 90 images (30 videos x 3 frames)
- Real-store annotations: 30 JSONL rows
- Annotation sources: {'full_human_annotation': 20, 'index_weak_label': 10}
- Frame status: {'available': 30}
- Synthetic samples: 3 JSON files
- Largest frame: `data/real_store_frames/frames/video_002/002.jpg` (271.1 KB); no frame exceeds 500 KB
- Full videos and checkpoints are not included.
- Private GitHub source repo has been pushed at commit `3a3c623`; anonymous mirror is available at `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`.
- Anonymous mirror public access check: README and ZIP endpoints returned HTTP 200; downloaded ZIP contains 90 frame images and no hits for local/server paths or checked identity terms.
- Face blurring was not applied because release consent was confirmed by the project lead; only sampled frames are included.
- Note: the archived real-eval manifest records frame timestamps `[0.0, 5.0, 10.0]`; the repo README follows this source-of-truth value.

## Code Cleaning Summary
- Copied core prompt/eval scripts and removed local/remote absolute paths.
- Replaced hardcoded model/checkpoint defaults with relative placeholder paths or required CLI arguments.
- Added minimal public `piwm_data/rules.py` constants instead of copying the full internal data-generation rule module.
- Replaced internal Chinese report placeholders in the Trick 6 helper with neutral `N/A` wording.
- Did not copy `reports/`, `tmp/`, checkpoint files, raw videos, or private notes.
- `python3 -m compileall` passes for released Python modules and scripts.

## File List
| Path | Size |
|---|---:|
| `.gitignore` | 79 B |
| `LICENSE` | 11.1 KB |
| `README.md` | 2.1 KB |
| `configs/piwm_main_lora.yaml` | 776 B |
| `data/real_store_frames/README.md` | 569 B |
| `data/real_store_frames/annotations.jsonl` | 48.2 KB |
| `data/real_store_frames/frames/video_001/000.jpg` | 217.6 KB |
| `data/real_store_frames/frames/video_001/001.jpg` | 232.2 KB |
| `data/real_store_frames/frames/video_001/002.jpg` | 231.1 KB |
| `data/real_store_frames/frames/video_002/000.jpg` | 239.3 KB |
| `data/real_store_frames/frames/video_002/001.jpg` | 226.4 KB |
| `data/real_store_frames/frames/video_002/002.jpg` | 271.1 KB |
| `data/real_store_frames/frames/video_003/000.jpg` | 214.1 KB |
| `data/real_store_frames/frames/video_003/001.jpg` | 228.8 KB |
| `data/real_store_frames/frames/video_003/002.jpg` | 238.9 KB |
| `data/real_store_frames/frames/video_004/000.jpg` | 215.3 KB |
| `data/real_store_frames/frames/video_004/001.jpg` | 228.1 KB |
| `data/real_store_frames/frames/video_004/002.jpg` | 237.9 KB |
| `data/real_store_frames/frames/video_005/000.jpg` | 214.9 KB |
| `data/real_store_frames/frames/video_005/001.jpg` | 229.2 KB |
| `data/real_store_frames/frames/video_005/002.jpg` | 256.8 KB |
| `data/real_store_frames/frames/video_006/000.jpg` | 240.4 KB |
| `data/real_store_frames/frames/video_006/001.jpg` | 235.8 KB |
| `data/real_store_frames/frames/video_006/002.jpg` | 237.4 KB |
| `data/real_store_frames/frames/video_007/000.jpg` | 243.9 KB |
| `data/real_store_frames/frames/video_007/001.jpg` | 236.7 KB |
| `data/real_store_frames/frames/video_007/002.jpg` | 243.2 KB |
| `data/real_store_frames/frames/video_008/000.jpg` | 242.2 KB |
| `data/real_store_frames/frames/video_008/001.jpg` | 238.8 KB |
| `data/real_store_frames/frames/video_008/002.jpg` | 239.9 KB |
| `data/real_store_frames/frames/video_009/000.jpg` | 237.2 KB |
| `data/real_store_frames/frames/video_009/001.jpg` | 234.8 KB |
| `data/real_store_frames/frames/video_009/002.jpg` | 238.6 KB |
| `data/real_store_frames/frames/video_010/000.jpg` | 235.5 KB |
| `data/real_store_frames/frames/video_010/001.jpg` | 236.5 KB |
| `data/real_store_frames/frames/video_010/002.jpg` | 269.9 KB |
| `data/real_store_frames/frames/video_011/000.jpg` | 210.1 KB |
| `data/real_store_frames/frames/video_011/001.jpg` | 223.4 KB |
| `data/real_store_frames/frames/video_011/002.jpg` | 225.1 KB |
| `data/real_store_frames/frames/video_012/000.jpg` | 243.3 KB |
| `data/real_store_frames/frames/video_012/001.jpg` | 232.8 KB |
| `data/real_store_frames/frames/video_012/002.jpg` | 240.4 KB |
| `data/real_store_frames/frames/video_013/000.jpg` | 243.4 KB |
| `data/real_store_frames/frames/video_013/001.jpg` | 239.3 KB |
| `data/real_store_frames/frames/video_013/002.jpg` | 233.5 KB |
| `data/real_store_frames/frames/video_014/000.jpg` | 238.4 KB |
| `data/real_store_frames/frames/video_014/001.jpg` | 236.7 KB |
| `data/real_store_frames/frames/video_014/002.jpg` | 243.3 KB |
| `data/real_store_frames/frames/video_015/000.jpg` | 237.0 KB |
| `data/real_store_frames/frames/video_015/001.jpg` | 232.8 KB |
| `data/real_store_frames/frames/video_015/002.jpg` | 233.2 KB |
| `data/real_store_frames/frames/video_016/000.jpg` | 239.0 KB |
| `data/real_store_frames/frames/video_016/001.jpg` | 240.7 KB |
| `data/real_store_frames/frames/video_016/002.jpg` | 233.9 KB |
| `data/real_store_frames/frames/video_017/000.jpg` | 236.7 KB |
| `data/real_store_frames/frames/video_017/001.jpg` | 241.1 KB |
| `data/real_store_frames/frames/video_017/002.jpg` | 235.0 KB |
| `data/real_store_frames/frames/video_018/000.jpg` | 238.0 KB |
| `data/real_store_frames/frames/video_018/001.jpg` | 234.2 KB |
| `data/real_store_frames/frames/video_018/002.jpg` | 241.1 KB |
| `data/real_store_frames/frames/video_019/000.jpg` | 228.5 KB |
| `data/real_store_frames/frames/video_019/001.jpg` | 238.9 KB |
| `data/real_store_frames/frames/video_019/002.jpg` | 242.9 KB |
| `data/real_store_frames/frames/video_020/000.jpg` | 231.6 KB |
| `data/real_store_frames/frames/video_020/001.jpg` | 235.8 KB |
| `data/real_store_frames/frames/video_020/002.jpg` | 239.3 KB |
| `data/real_store_frames/frames/video_021/000.jpg` | 232.2 KB |
| `data/real_store_frames/frames/video_021/001.jpg` | 237.4 KB |
| `data/real_store_frames/frames/video_021/002.jpg` | 232.4 KB |
| `data/real_store_frames/frames/video_022/000.jpg` | 239.6 KB |
| `data/real_store_frames/frames/video_022/001.jpg` | 236.9 KB |
| `data/real_store_frames/frames/video_022/002.jpg` | 234.7 KB |
| `data/real_store_frames/frames/video_023/000.jpg` | 240.1 KB |
| `data/real_store_frames/frames/video_023/001.jpg` | 242.3 KB |
| `data/real_store_frames/frames/video_023/002.jpg` | 265.2 KB |
| `data/real_store_frames/frames/video_024/000.jpg` | 244.4 KB |
| `data/real_store_frames/frames/video_024/001.jpg` | 242.1 KB |
| `data/real_store_frames/frames/video_024/002.jpg` | 242.1 KB |
| `data/real_store_frames/frames/video_025/000.jpg` | 243.5 KB |
| `data/real_store_frames/frames/video_025/001.jpg` | 243.6 KB |
| `data/real_store_frames/frames/video_025/002.jpg` | 240.5 KB |
| `data/real_store_frames/frames/video_026/000.jpg` | 230.5 KB |
| `data/real_store_frames/frames/video_026/001.jpg` | 238.8 KB |
| `data/real_store_frames/frames/video_026/002.jpg` | 233.3 KB |
| `data/real_store_frames/frames/video_027/000.jpg` | 235.2 KB |
| `data/real_store_frames/frames/video_027/001.jpg` | 236.4 KB |
| `data/real_store_frames/frames/video_027/002.jpg` | 268.1 KB |
| `data/real_store_frames/frames/video_028/000.jpg` | 239.1 KB |
| `data/real_store_frames/frames/video_028/001.jpg` | 230.8 KB |
| `data/real_store_frames/frames/video_028/002.jpg` | 253.9 KB |
| `data/real_store_frames/frames/video_029/000.jpg` | 236.2 KB |
| `data/real_store_frames/frames/video_029/001.jpg` | 235.0 KB |
| `data/real_store_frames/frames/video_029/002.jpg` | 258.8 KB |
| `data/real_store_frames/frames/video_030/000.jpg` | 231.2 KB |
| `data/real_store_frames/frames/video_030/001.jpg` | 228.7 KB |
| `data/real_store_frames/frames/video_030/002.jpg` | 240.0 KB |
| `data/synthetic_samples/sample_001.json` | 8.8 KB |
| `data/synthetic_samples/sample_002.json` | 14.1 KB |
| `data/synthetic_samples/sample_003.json` | 8.6 KB |
| `docs/prompt_templates.md` | 4.7 KB |
| `piwm_data/__init__.py` | 61 B |
| `piwm_data/rules.py` | 396 B |
| `piwm_infer/__init__.py` | 55 B |
| `piwm_infer/config.py` | 260 B |
| `piwm_infer/parsers.py` | 7.2 KB |
| `piwm_train/__init__.py` | 54 B |
| `piwm_train/a3plus_metrics.py` | 2.6 KB |
| `piwm_train/config.py` | 6.8 KB |
| `piwm_train/prompts.py` | 19.4 KB |
| `requirements.txt` | 119 B |
| `scripts/eval_e2e_decision_loop_checkpoint.py` | 18.5 KB |
| `scripts/eval_ms_swift_checkpoint.py` | 19.7 KB |
| `scripts/extract_frames.py` | 6.0 KB |
| `scripts/run_trick6_counterfactual_planning.py` | 34.5 KB |
