# PIWM Visual Input Contract

更新时间：2026-04-29

## 1. 推荐主线

第一版主线定义为：

```text
单视频 -> 多图抽帧 -> 单轮样本 -> 推理时多次调用
```

正式字段：

```text
training_input_mode = multi_image_single_turn
```

含义：

- Kling 生成一条 current-state video；
- 从视频中抽 K 张关键帧，主实验 K=3；
- 三套训练数据共享同一组 sampled frames；
- 训练样本是单轮监督；
- 推理时同一 VLM 多次调用，完成 perception / deliberation / action。

## 2. 为什么不直接主用单图或视频

| 模式 | 当前定位 | 原因 |
|---|---|---|
| 单图单轮 | ablation | 丢失 dwell、handling、comparison 等时间性 cue |
| 多图单轮 | 主线 | 能表达短时行为变化，兼容现有 frame-based pipeline |
| 单视频单轮 | 后续 ablation | 依赖 video-native VLM 支持，token 和训练成本高 |
| 多图多轮 | 后续增强 | 需要 history schema 稳定 |
| 多视频多轮 | 暂不做 | 数据与 QA 成本过高 |

## 3. Kling Prompt 必须服务抽帧

Prompt 不应只写：

```text
The customer hesitates.
```

而应写 behavior timeline：

```text
0-2s: customer approaches the display and notices the product.
2-5s: customer looks down at the price tag, pauses, then looks back at the product.
5-8s: customer lightly touches the product but does not pick it up.
8-10s: customer looks at the price area again and remains undecided.
```

这样抽帧策略才能稳定选择：

```text
cue_onset: 2s
cue_peak: 5s
cue_resolution: 8s
```

## 4. Prompt 层级

`prompt_builder.py` 输出至少包含四层：

| 层 | 内容 |
|---|---|
| Camera | 视角、时长、单人、无字幕、无品牌 |
| Scene | 店铺、商品、空间布局 |
| Behavior timeline | 目标 cue 在时间轴上的可见行为 |
| Negative | 禁止标签泄露、额外人物、购买完成、夸张表演 |

禁止在 prompt 文本中泄露：

- `latent_state` / `state_subtype`；
- action label；
- reward；
- BDI 标签名；
- “this is high hesitation” 这类标注性文字。

## 5. Frame Manifest

每个生成 session 需要保存：

```text
frame_manifest.json
```

建议格式：

```json
{
  "source_video": "video.mp4",
  "training_input_mode": "multi_image_single_turn",
  "frame_sampling_strategy": "cue_timeline_3point",
  "sampled_frames": [
    {"index": 0, "path": "frames/000.jpg", "timestamp_sec": 2.0, "role": "cue_onset"},
    {"index": 1, "path": "frames/001.jpg", "timestamp_sec": 5.0, "role": "cue_peak"},
    {"index": 2, "path": "frames/002.jpg", "timestamp_sec": 8.0, "role": "cue_resolution"}
  ]
}
```

## 6. QA Gate

QA 必须检查两层：

1. 整段视频是否合理；
2. sampled frames 是否足以支持标签。

`qa_report.json` 至少包含：

```json
{
  "video_level_pass": true,
  "sampled_frames_pass": true,
  "target_cue": "long_dwell_with_price_check",
  "cue_visible_in_video": true,
  "cue_visible_in_sampled_frames": true,
  "label_leakage": false,
  "extra_subjects": false,
  "rejection_reason": null
}
```

如果视频整体有 cue，但 sampled frames 没有 cue，这条样本不能进入训练集。

## 7. 三套 JSONL 共享视觉输入

| JSONL | 视觉输入 |
|---|---|
| `state_inference.jsonl` | sampled frames |
| `transition_modeling.jsonl` | 同一组 sampled frames + 单个 action |
| `policy_preference.jsonl` | 同一组 sampled frames + candidate outcomes |

这对应论文 §3.5 的设计理由：一个 VLM 共享视觉 grounding，而不是三套互不相干的数据。

## 8. Definition of Done

| DoD | 验收 |
|---|---|
| Visual-1 | `prompt_builder.py` 输出 behavior timeline |
| Visual-2 | `extract_frames.py` 生成 `frame_manifest.json` |
| Visual-3 | QA 同时检查 video-level 与 sampled-frame-level |
| Visual-4 | loader / build_dataset 只读取 QA pass 样本 |
| Visual-5 | K=1 single-frame ablation 可由同一 video/frame manifest 派生 |
