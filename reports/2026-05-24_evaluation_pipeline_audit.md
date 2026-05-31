5-act 自检：Greet/Elicit/Inform/Recommend/Hold；Reassure 不进入操作输出。

# PIWM 评估流程完整审计

本报告只读展示现有评估流程、代码、数据样本、prompt、parser、gold 与 metric。没有跑模型、没有改 official 数据、没有修改模型 checkpoint。

说明：部分“实际执行命令”没有保存在仓库日志中；对应位置标注为“未找到原始命令记录”，并列出由 raw artifact 字段可还原出的命令形态。


## 1. Dim 1 AIDA stage 评估

### Step A: 评估入口

- 评估脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/eval_ms_swift_checkpoint.py`
- 汇总/输入准备脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/piwm_4dim_eval.py`
- 命令行入口：本地未找到 shell history 或 tmux log 中的完整原始命令；以下命令由 raw artifact 的 `input_jsonl/eval_args/checkpoint` 字段与脚本参数还原：

```bash
python3 scripts/eval_ms_swift_checkpoint.py --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500 --input-jsonl reports/4dim_eval_raw_20260524/target_user_next_scored.server.jsonl --out reports/4dim_eval_raw_20260524/piwm_main_user_next.json --max-new-tokens 384 --image-limit 3 --max-pixels 1003520
```

### Step B: 评估数据加载

- 输入数据文件路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/4dim_eval_raw_20260524/target_user_intent.jsonl`
- 一共加载：`30` 条
- 数据加载代码片段：

```python
def _read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows
```

- 1 条原始数据 sample（完整 JSON）：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在智能售货机前。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    },
    {
      "role": "assistant",
      "content": "<stage>interest</stage>\n<intent_label>explore_options</intent_label>\n<visual_summary>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</visual_summary>\n<engagement_pattern>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</engagement_pattern>\n<gaze_and_attention>表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。</gaze_and_attention>\n<body_and_hands>正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。</body_and_hands>\n<belief>售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。</belief>\n<desire>想进一步了解商品是否值得购买，并确认它是否符合自己的需求。</desire>\n<intention>继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。</intention>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "target_piwm_700",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "test",
    "qa_status": "qa_reviewed_pass",
    "human_review_status": "project_lead_reviewed_pass",
    "viewpoint": "target_frontcam",
    "stage": "interest",
    "intent_label": "explore_options",
    "loss_weight": 1.0,
    "loss_weight_policy": "a3plus_visual_intent_low_confidence"
  }
}
```

### Step C: Prompt 构造

- prompt template 源码：

```python
def build_user_intent_prompt(record: dict, *, scene_description: str | None = None) -> str:
    frames = record["input"].get("frames", [])
    scene = scene_description or _scene_description(record)
    return (
        "You are observing a short customer-behavior window.\n\n"
        f"Scene: {scene}\n\n"
        "Below are "
        f"{len(frames)} frames sampled from a streaming camera, in chronological order.\n\n"
        f"{image_placeholders(len(frames))}\n\n"
        "Infer the customer's current user state from the visible behavior only. "
        "Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\n"
        "Output the following fields, in this exact order, each on its own line:\n"
        f"{config.tag_instruction_lines(config.USER_INTENT_TAGS)}\n\n"
        "- stage must be one of: attention, interest, desire, action.\n"
        "- intent_label must be one existing PIWM intention category, such as confirm_choice, "
        "explore_options, request_demonstration, seek_reassurance, negotiate_price, "
        "leave_without_purchase, compare_value_for_money, or no_clear_intent.\n"
        "- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n"
        "- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    )
```

- 1 条实际喂给模型的完整 prompt（messages 中 system + user，含 image token 标记）：

```json
{
  "system": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.",
  "user": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在智能售货机前。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
}
```

### Step D: 模型 inference

- 模型加载与推理代码：

```python
def _normalize_messages(row: dict[str, Any], *, image_limit: int | None = None, max_pixels: int | None = None) -> list[dict[str, Any]]:
    messages = row["messages"]
    system = messages[0]
    user = messages[1]
    text = str(user["content"]).replace("<image>", "").strip()
    content: list[dict[str, str]] = []
    images = row.get("images", [])
    if image_limit is not None:
        images = images[:image_limit]
    for image in images:
        item: dict[str, Any] = {"type": "image", "image": image}
        if max_pixels is not None:
            item["max_pixels"] = max_pixels
        content.append(item)
    content.append({"type": "text", "text": text})
    return [{"role": "system", "content": system["content"]}, {"role": "user", "content": content}]

def _generate_one(model, processor, row: dict[str, Any], args: argparse.Namespace) -> str:
    messages = _normalize_messages(row, image_limit=args.image_limit, max_pixels=args.max_pixels)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    logits_processor = _logits_processor_for_row(processor, row, args)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            logits_processor=logits_processor,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
```

- generation config：

```json
{
  "limit": null,
  "max_new_tokens": 384,
  "image_limit": 3,
  "max_pixels": 1003520,
  "torch_dtype": "bfloat16",
  "device_map": "auto",
  "hold_prior_lambda": 0.0,
  "hold_prior_target": 0.2,
  "hold_prior_observed": 0.5333333333333333
}
```

- 1 条模型 raw output（完整文本）：

```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>
<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>
<belief>The product is nearly ready, but confirmation is still needed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### Step E: Parsing / 抽取 prediction

- parser 函数源码：

```python
def parse_user_intent_output(raw: str) -> dict:
    values = _extract_tags(raw, config.USER_INTENT_TAGS)
    stage = values["stage"]
    if stage not in rules.AIDA_STAGES:
        raise MalformedOutputError(f"invalid stage: {stage}")
    intent_label = values["intent_label"]
    if not intent_label:
        raise MalformedOutputError("intent_label is empty")
    return {
        "aida_stage": stage,
        "intent_label": intent_label,
        "visual_state": {
            "summary": values["visual_summary"],
            "engagement_pattern": values["engagement_pattern"],
            "gaze_and_attention": values["gaze_and_attention"],
            "body_and_hands": values["body_and_hands"],
        },
        "bdi": {
            "belief": values["belief"],
            "desire": values["desire"],
            "intention": values["intention"],
        },
    }
```

- parser 输入和输出对照：

```json
{
  "parser_input_raw_output": "<stage>action</stage>\n<intent_label>confirm_choice</intent_label>\n<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>\n<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>\n<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>\n<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>\n<belief>The product is nearly ready, but confirmation is still needed.</belief>\n<desire>confirm the preferred choice</desire>\n<intention>move toward confirming the choice</intention>",
  "parser_output": {
    "aida_stage": "action",
    "intent_label": "confirm_choice",
    "visual_state": {
      "summary": "顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。",
      "engagement_pattern": "顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。",
      "gaze_and_attention": "视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。",
      "body_and_hands": "身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。"
    },
    "bdi": {
      "belief": "The product is nearly ready, but confirmation is still needed.",
      "desire": "confirm the preferred choice",
      "intention": "move toward confirming the choice"
    }
  },
  "parse_ok": true,
  "error": null
}
```

- parse 失败 fallback：`scripts/eval_ms_swift_checkpoint.py:evaluate` 在 `MalformedOutputError / RuntimeError / ValueError` 时写入 `parse_ok=False` 和 `error`；该样本不进入 parsed metric，strict metric 中由 4dim summarizer 计为 `__parse_error__`。

### Step F: Gold label 取法

- gold label 字段名：`<stage>...</stage>`
- gold label 取自：该 row 的 `messages[2].content`，再由相同 parser 或 `tag_value(...)` 抽取。
- 1 条 gold label 完整原文：

```text
<stage>interest</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</visual_summary>
<engagement_pattern>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</engagement_pattern>
<gaze_and_attention>表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。</gaze_and_attention>
<body_and_hands>正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。</body_and_hands>
<belief>售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。</belief>
<desire>想进一步了解商品是否值得购买，并确认它是否符合自己的需求。</desire>
<intention>继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。</intention>
```

- gold label space：`attention / interest / desire / action`

### Step G: Metric 计算

- metric 函数源码：

```python
def _score_user_intent(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    stage_pairs = []
    intent_pairs = []
    strict_stage_pairs = []
    strict_intent_pairs = []
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold_stage = tag_value(row["messages"][2]["content"], "stage")
        gold_intent = tag_value(row["messages"][2]["content"], "intent_label")
        if out.get("parse_ok"):
            parsed = out.get("parsed") or {}
            stage_pairs.append((parsed.get("aida_stage"), gold_stage))
            intent_pairs.append((parsed.get("intent_label"), gold_intent))
            strict_stage_pairs.append((parsed.get("aida_stage"), gold_stage))
            strict_intent_pairs.append((parsed.get("intent_label"), gold_intent))
        else:
            strict_stage_pairs.append(("__parse_error__", gold_stage))
            strict_intent_pairs.append(("__parse_error__", gold_intent))
    core_pairs = [(p, g) for p, g in intent_pairs if g not in LOW_CONFIDENCE_INTENTS]
    strict_core_pairs = [(p, g) for p, g in strict_intent_pairs if g not in LOW_CONFIDENCE_INTENTS]
    full_labels = sorted({g for _, g in intent_pairs if g})
    core_labels = sorted({g for _, g in core_pairs if g})
    return {
        "parse_rate": result.get("parse_rate"),
        "stage": _classification_metrics(stage_pairs, list(AIDA_STAGES)),
        "stage_strict": _classification_metrics(strict_stage_pairs, list(AIDA_STAGES)),
        "intent": _classification_metrics(intent_pairs, full_labels),
        "intent_strict": _classification_metrics(strict_intent_pairs, full_labels),
        "intent_core": _classification_metrics(core_pairs, core_labels),
        "intent_core_strict": _classification_metrics(strict_core_pairs, core_labels),
        "outputs_by_scene": _scene_output_map(result, "user_intent"),
    }

def _classification_metrics(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> dict[str, Any]:
    clean = [(p, g) for p, g in pairs if g is not None]
    return {
        "macro_f1": _macro_f1(clean, labels),
        "accuracy": _accuracy(clean),
        "per_class": {
            label: _per_label(clean, label)
            for label in labels
        },
        "support": dict(sorted(Counter(g for _, g in clean).items())),
        "pred_count": dict(sorted(Counter(p for p, _ in clean if p is not None).items())),
        "n": len(clean),
    }

def _macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(_per_label(pairs, label)["f1"] for label in labels) / len(labels)

def _per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }
```

- parse 失败处理：parsed macro F1 只使用 parse 成功样本；strict macro F1 在 4dim summarizer 中把 parse failure 作为 `__parse_error__` 预测写入分母。
- macro / micro / weighted：报告使用 macro F1；没有使用 weighted F1。
- 1 条 `(pred, gold, match/mismatch)` 示例：

```json
{
  "pred": "action",
  "gold": "interest",
  "match": false
}
```



## 2. Dim 2 intent 评估

### Step A: 评估入口

- 评估脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/eval_ms_swift_checkpoint.py`
- 汇总/输入准备脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/piwm_4dim_eval.py`
- 命令行入口：本地未找到 shell history 或 tmux log 中的完整原始命令；以下命令由 raw artifact 的 `input_jsonl/eval_args/checkpoint` 字段与脚本参数还原：

```bash
python3 scripts/eval_ms_swift_checkpoint.py --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500 --input-jsonl reports/4dim_eval_raw_20260524/target_user_next_scored.server.jsonl --out reports/4dim_eval_raw_20260524/piwm_main_user_next.json --max-new-tokens 384 --image-limit 3 --max-pixels 1003520
```

### Step B: 评估数据加载

- 输入数据文件路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/4dim_eval_raw_20260524/target_user_intent.jsonl`
- 一共加载：`30` 条
- 数据加载代码片段：

```python
def _read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows
```

- 1 条原始数据 sample（完整 JSON）：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在智能售货机前。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    },
    {
      "role": "assistant",
      "content": "<stage>interest</stage>\n<intent_label>explore_options</intent_label>\n<visual_summary>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</visual_summary>\n<engagement_pattern>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</engagement_pattern>\n<gaze_and_attention>表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。</gaze_and_attention>\n<body_and_hands>正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。</body_and_hands>\n<belief>售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。</belief>\n<desire>想进一步了解商品是否值得购买，并确认它是否符合自己的需求。</desire>\n<intention>继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。</intention>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "task": "user_intent",
  "source_id": "target_piwm_700",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "test",
    "qa_status": "qa_reviewed_pass",
    "human_review_status": "project_lead_reviewed_pass",
    "viewpoint": "target_frontcam",
    "stage": "interest",
    "intent_label": "explore_options",
    "loss_weight": 1.0,
    "loss_weight_policy": "a3plus_visual_intent_low_confidence"
  }
}
```

### Step C: Prompt 构造

- prompt template 源码：

```python
def build_user_intent_prompt(record: dict, *, scene_description: str | None = None) -> str:
    frames = record["input"].get("frames", [])
    scene = scene_description or _scene_description(record)
    return (
        "You are observing a short customer-behavior window.\n\n"
        f"Scene: {scene}\n\n"
        "Below are "
        f"{len(frames)} frames sampled from a streaming camera, in chronological order.\n\n"
        f"{image_placeholders(len(frames))}\n\n"
        "Infer the customer's current user state from the visible behavior only. "
        "Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\n"
        "Output the following fields, in this exact order, each on its own line:\n"
        f"{config.tag_instruction_lines(config.USER_INTENT_TAGS)}\n\n"
        "- stage must be one of: attention, interest, desire, action.\n"
        "- intent_label must be one existing PIWM intention category, such as confirm_choice, "
        "explore_options, request_demonstration, seek_reassurance, negotiate_price, "
        "leave_without_purchase, compare_value_for_money, or no_clear_intent.\n"
        "- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n"
        "- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
    )
```

- 1 条实际喂给模型的完整 prompt（messages 中 system + user，含 image token 标记）：

```json
{
  "system": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.",
  "user": "<image><image><image>You are observing a short customer-behavior window.\n\nScene: 顾客在智能售货机前。\n\nBelow are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nInfer the customer's current user state from the visible behavior only. Do not choose a sales action. Do not output candidate actions, rewards, or recommendations.\n\nOutput the following fields, in this exact order, each on its own line:\n<stage>...</stage>\n<intent_label>...</intent_label>\n<visual_summary>...</visual_summary>\n<engagement_pattern>...</engagement_pattern>\n<gaze_and_attention>...</gaze_and_attention>\n<body_and_hands>...</body_and_hands>\n<belief>...</belief>\n<desire>...</desire>\n<intention>...</intention>\n\n- stage must be one of: attention, interest, desire, action.\n- intent_label must be one existing PIWM intention category, such as confirm_choice, explore_options, request_demonstration, seek_reassurance, negotiate_price, leave_without_purchase, compare_value_for_money, or no_clear_intent.\n- visual_summary, engagement_pattern, gaze_and_attention, and body_and_hands must cite visible evidence.\n- belief, desire, and intention must be short customer-state clauses, not salesperson advice."
}
```

### Step D: 模型 inference

- 模型加载与推理代码：

```python
def _normalize_messages(row: dict[str, Any], *, image_limit: int | None = None, max_pixels: int | None = None) -> list[dict[str, Any]]:
    messages = row["messages"]
    system = messages[0]
    user = messages[1]
    text = str(user["content"]).replace("<image>", "").strip()
    content: list[dict[str, str]] = []
    images = row.get("images", [])
    if image_limit is not None:
        images = images[:image_limit]
    for image in images:
        item: dict[str, Any] = {"type": "image", "image": image}
        if max_pixels is not None:
            item["max_pixels"] = max_pixels
        content.append(item)
    content.append({"type": "text", "text": text})
    return [{"role": "system", "content": system["content"]}, {"role": "user", "content": content}]

def _generate_one(model, processor, row: dict[str, Any], args: argparse.Namespace) -> str:
    messages = _normalize_messages(row, image_limit=args.image_limit, max_pixels=args.max_pixels)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    logits_processor = _logits_processor_for_row(processor, row, args)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            logits_processor=logits_processor,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
```

- generation config：

```json
{
  "limit": null,
  "max_new_tokens": 384,
  "image_limit": 3,
  "max_pixels": 1003520,
  "torch_dtype": "bfloat16",
  "device_map": "auto",
  "hold_prior_lambda": 0.0,
  "hold_prior_target": 0.2,
  "hold_prior_observed": 0.5333333333333333
}
```

- 1 条模型 raw output（完整文本）：

```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>
<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>
<belief>The product is nearly ready, but confirmation is still needed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

### Step E: Parsing / 抽取 prediction

- parser 函数源码：

```python
def parse_user_intent_output(raw: str) -> dict:
    values = _extract_tags(raw, config.USER_INTENT_TAGS)
    stage = values["stage"]
    if stage not in rules.AIDA_STAGES:
        raise MalformedOutputError(f"invalid stage: {stage}")
    intent_label = values["intent_label"]
    if not intent_label:
        raise MalformedOutputError("intent_label is empty")
    return {
        "aida_stage": stage,
        "intent_label": intent_label,
        "visual_state": {
            "summary": values["visual_summary"],
            "engagement_pattern": values["engagement_pattern"],
            "gaze_and_attention": values["gaze_and_attention"],
            "body_and_hands": values["body_and_hands"],
        },
        "bdi": {
            "belief": values["belief"],
            "desire": values["desire"],
            "intention": values["intention"],
        },
    }
```

- parser 输入和输出对照：

```json
{
  "parser_input_raw_output": "<stage>action</stage>\n<intent_label>confirm_choice</intent_label>\n<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>\n<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>\n<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>\n<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>\n<belief>The product is nearly ready, but confirmation is still needed.</belief>\n<desire>confirm the preferred choice</desire>\n<intention>move toward confirming the choice</intention>",
  "parser_output": {
    "aida_stage": "action",
    "intent_label": "confirm_choice",
    "visual_state": {
      "summary": "顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。",
      "engagement_pattern": "顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。",
      "gaze_and_attention": "视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。",
      "body_and_hands": "身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。"
    },
    "bdi": {
      "belief": "The product is nearly ready, but confirmation is still needed.",
      "desire": "confirm the preferred choice",
      "intention": "move toward confirming the choice"
    }
  },
  "parse_ok": true,
  "error": null
}
```

- parse 失败 fallback：`scripts/eval_ms_swift_checkpoint.py:evaluate` 在 `MalformedOutputError / RuntimeError / ValueError` 时写入 `parse_ok=False` 和 `error`；该样本不进入 parsed metric，strict metric 中由 4dim summarizer 计为 `__parse_error__`。

### Step F: Gold label 取法

- gold label 字段名：`<intent_label>...</intent_label>`
- gold label 取自：该 row 的 `messages[2].content`，再由相同 parser 或 `tag_value(...)` 抽取。
- 1 条 gold label 完整原文：

```text
<stage>interest</stage>
<intent_label>explore_options</intent_label>
<visual_summary>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</visual_summary>
<engagement_pattern>顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。</engagement_pattern>
<gaze_and_attention>表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。</gaze_and_attention>
<body_and_hands>正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。</body_and_hands>
<belief>售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。</belief>
<desire>想进一步了解商品是否值得购买，并确认它是否符合自己的需求。</desire>
<intention>继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。</intention>
```

- gold label space：`compare_value_for_money, confirm_choice, explore_options, no_clear_intent`

### Step G: Metric 计算

- metric 函数源码：

```python
def _score_user_intent(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    stage_pairs = []
    intent_pairs = []
    strict_stage_pairs = []
    strict_intent_pairs = []
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold_stage = tag_value(row["messages"][2]["content"], "stage")
        gold_intent = tag_value(row["messages"][2]["content"], "intent_label")
        if out.get("parse_ok"):
            parsed = out.get("parsed") or {}
            stage_pairs.append((parsed.get("aida_stage"), gold_stage))
            intent_pairs.append((parsed.get("intent_label"), gold_intent))
            strict_stage_pairs.append((parsed.get("aida_stage"), gold_stage))
            strict_intent_pairs.append((parsed.get("intent_label"), gold_intent))
        else:
            strict_stage_pairs.append(("__parse_error__", gold_stage))
            strict_intent_pairs.append(("__parse_error__", gold_intent))
    core_pairs = [(p, g) for p, g in intent_pairs if g not in LOW_CONFIDENCE_INTENTS]
    strict_core_pairs = [(p, g) for p, g in strict_intent_pairs if g not in LOW_CONFIDENCE_INTENTS]
    full_labels = sorted({g for _, g in intent_pairs if g})
    core_labels = sorted({g for _, g in core_pairs if g})
    return {
        "parse_rate": result.get("parse_rate"),
        "stage": _classification_metrics(stage_pairs, list(AIDA_STAGES)),
        "stage_strict": _classification_metrics(strict_stage_pairs, list(AIDA_STAGES)),
        "intent": _classification_metrics(intent_pairs, full_labels),
        "intent_strict": _classification_metrics(strict_intent_pairs, full_labels),
        "intent_core": _classification_metrics(core_pairs, core_labels),
        "intent_core_strict": _classification_metrics(strict_core_pairs, core_labels),
        "outputs_by_scene": _scene_output_map(result, "user_intent"),
    }

def _classification_metrics(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> dict[str, Any]:
    clean = [(p, g) for p, g in pairs if g is not None]
    return {
        "macro_f1": _macro_f1(clean, labels),
        "accuracy": _accuracy(clean),
        "per_class": {
            label: _per_label(clean, label)
            for label in labels
        },
        "support": dict(sorted(Counter(g for _, g in clean).items())),
        "pred_count": dict(sorted(Counter(p for p, _ in clean if p is not None).items())),
        "n": len(clean),
    }

def _macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(_per_label(pairs, label)["f1"] for label in labels) / len(labels)

def _per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }
```

- parse 失败处理：parsed macro F1 只使用 parse 成功样本；strict macro F1 在 4dim summarizer 中把 parse failure 作为 `__parse_error__` 预测写入分母。
- macro / micro / weighted：报告使用 macro F1；没有使用 weighted F1。
- 1 条 `(pred, gold, match/mismatch)` 示例：

```json
{
  "pred": "confirm_choice",
  "gold": "explore_options",
  "match": false
}
```

- full intent 由 gold 中实际出现的 intent label 构成；core intent 在 4dim summarizer 中排除 `seek_reassurance` 和 `negotiate_price`。



## 3. Dim 3 next_state 评估

### Step A: 评估入口

- 评估脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/eval_ms_swift_checkpoint.py`
- 汇总/输入准备脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/piwm_4dim_eval.py`
- 命令行入口：本地未找到 shell history 或 tmux log 中的完整原始命令；以下命令由 raw artifact 的 `input_jsonl/eval_args/checkpoint` 字段与脚本参数还原：

```bash
python3 scripts/run_trick6_counterfactual_planning.py --mode dim3 --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500 --action-jsonl data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl --transition-jsonl data/official/piwm_target_v1/transition_modeling.jsonl --covered-jsonl reports/4dim_eval_raw_20260524/next_state_covered80.jsonl --out reports/dim3_raw_20260524/dim3_next_state_current_state_prompt.json
```

### Step B: 评估数据加载

- 输入数据文件路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/4dim_eval_raw_20260524/next_state_covered80.jsonl`
- 一共加载：`80` 条
- 数据加载代码片段：

```python
def _read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows
```

- 1 条原始数据 sample（完整 JSON）：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您今天想先看价格、功能，还是适合什么场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}\n- voice_style: curious\n- light: soft_invitation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。\n- utterance: 您今天想先看价格、功能，还是适合什么场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>interest</next_stage>\n<next_belief>机器关注并理解她在比较，主动帮助理清关注点，信息获取门槛降低。</next_belief>\n<next_desire>更方便地筛选出关键考虑因素，明确自己真正关心的内容（如功能/价格/场景）。</next_desire>\n<next_intention>有动力进一步定位需求，从泛泛兴趣过渡到具体需求探索，准备了解更相关信息。</next_intention>\n<risk>medium</risk>\n<benefit>high</benefit>\n<reward>0.21</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "target_piwm_700#Elicit_b1166d372e5e",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "target_piwm_700",
    "candidate_action": "Elicit_b1166d372e5e",
    "candidate_act": "Elicit",
    "candidate_params": {
      "openness": "open",
      "slot": "need_focus"
    },
    "qa_status": "qa_pending_project_lead_review",
    "human_review_status": "pending_project_lead_review",
    "viewpoint": "target_frontcam"
  }
}
```

### Step C: Prompt 构造

- prompt template 源码：

```python
def build_next_state_prediction_prompt(record: dict) -> str:
    """Build the path-C next-state prompt without gold current-state labels."""
    frames = record["input"].get("frames", [])
    action = record["input"]["candidate_action"]
    realization = record["input"].get("candidate_action_realization") or {}
    act_spec = record["input"].get("candidate_dialogue_act") or {}
    terminal = record["input"].get("candidate_terminal_realization") or {}
    return (
        "You are observing a customer in a retail store. Below are "
        f"{len(frames)} frames sampled from a streaming camera, in chronological order.\n\n"
        f"{image_placeholders(len(frames))}\n\n"
        "Use the frames to infer the customer's current state internally. "
        "The current stage, intent, and BDI state are not provided.\n\n"
        f"Consider one candidate intervention: {action}\n\n"
        + (
            "Dialogue-act layer for this candidate:\n"
            f"- act: {act_spec.get('act')}\n"
            f"- params: {act_spec.get('params')}\n\n"
            if act_spec else ""
        )
        + (
            "Terminal realization for this candidate:\n"
            f"- surface_text: {terminal.get('surface_text', '')}\n"
            f"- screen: {terminal.get('screen', {})}\n"
            f"- voice_style: {terminal.get('voice_style', '')}\n"
            f"- light: {terminal.get('light', '')}\n\n"
            if terminal else ""
        )
        + (
            "Concrete execution plan for this candidate:\n"
            f"- physical action: {_physical_action(realization)}\n"
            f"- utterance: {_utterance(realization)}\n\n"
            if realization else ""
        )
        +
        "Predict how this candidate intervention will change the customer's state in the next decision step. "
        "Output the following fields, in this exact order, each on its own line:\n"
        f"{config.tag_instruction_lines(config.DELIBERATION_TAGS)}\n\n"
        "- next_stage must be one of: attention, interest, desire, action.\n"
        "- risk and benefit must each be one of: low, medium, high.\n"
        "- reward must be a number in [-1.00, 1.00] with two decimal places.\n"
        "- all textual spans must be a single short clause in English."
    )

# Trick6/dim3 current-state prompt builder also exists:
def build_deliberation_prompt(record: dict) -> str:
    frames = record["input"].get("frames", [])
    state = record["input"]["current_state_summary"]
    bdi = state["bdi"]
    action = record["input"]["candidate_action"]
    visual = state.get("visual_state", {})
    realization = record["input"].get("candidate_action_realization") or {}
    act_spec = record["input"].get("candidate_dialogue_act") or {}
    terminal = record["input"].get("candidate_terminal_realization") or {}
    return (
        "You are observing a customer in a retail store. Below are "
        f"{len(frames)} frames sampled from a streaming camera, in chronological order.\n\n"
        f"{image_placeholders(len(frames))}\n\n"
        "The customer's current state is:\n"
        f"- stage: {state['aida_stage']}\n"
        f"- visible evidence: {visual.get('summary', 'not provided')}\n"
        f"- engagement pattern: {visual.get('engagement_pattern', 'not provided')}\n"
        f"- gaze and attention: {visual.get('gaze_and_attention', 'not provided')}\n"
        f"- body and hands: {visual.get('body_and_hands', 'not provided')}\n"
        f"- belief: {bdi['belief']}\n"
        f"- desire: {bdi['desire']}\n"
        f"- intention: {bdi['intention']}\n\n"
        f"Consider one candidate intervention: {action}\n\n"
        + (
            "Dialogue-act layer for this candidate:\n"
            f"- act: {act_spec.get('act')}\n"
            f"- params: {act_spec.get('params')}\n\n"
            if act_spec else ""
        )
        + (
            "Terminal realization for this candidate:\n"
            f"- surface_text: {terminal.get('surface_text', '')}\n"
            f"- screen: {terminal.get('screen', {})}\n"
            f"- voice_style: {terminal.get('voice_style', '')}\n"
            f"- light: {terminal.get('light', '')}\n\n"
            if terminal else ""
        )
        + (
            "Concrete execution plan for this candidate:\n"
            f"- physical action: {_physical_action(realization)}\n"
            f"- utterance: {_utterance(realization)}\n\n"
            if realization else ""
        )
        +
        "Predict how this candidate intervention will change the customer's state in the next decision step. "
        "Output the following fields, in this exact order, each on its own line:\n"
        f"{config.tag_instruction_lines(config.DELIBERATION_TAGS)}\n\n"
        "- next_stage must be one of: attention, interest, desire, action.\n"
        "- risk and benefit must each be one of: low, medium, high.\n"
        "- reward must be a number in [-1.00, 1.00] with two decimal places.\n"
        "- all textual spans must be a single short clause in English."
    )
```

- 1 条实际喂给模型的完整 prompt（messages 中 system + user，含 image token 标记）：

```json
{
  "system": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.",
  "user": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您今天想先看价格、功能，还是适合什么场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}\n- voice_style: curious\n- light: soft_invitation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。\n- utterance: 您今天想先看价格、功能，还是适合什么场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
}
```

### Step D: 模型 inference

- 模型加载与推理代码：

```python
def _normalize_messages(row: dict[str, Any], *, image_limit: int | None = None, max_pixels: int | None = None) -> list[dict[str, Any]]:
    messages = row["messages"]
    system = messages[0]
    user = messages[1]
    text = str(user["content"]).replace("<image>", "").strip()
    content: list[dict[str, str]] = []
    images = row.get("images", [])
    if image_limit is not None:
        images = images[:image_limit]
    for image in images:
        item: dict[str, Any] = {"type": "image", "image": image}
        if max_pixels is not None:
            item["max_pixels"] = max_pixels
        content.append(item)
    content.append({"type": "text", "text": text})
    return [{"role": "system", "content": system["content"]}, {"role": "user", "content": content}]

def _generate_one(model, processor, row: dict[str, Any], args: argparse.Namespace) -> str:
    messages = _normalize_messages(row, image_limit=args.image_limit, max_pixels=args.max_pixels)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    logits_processor = _logits_processor_for_row(processor, row, args)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            logits_processor=logits_processor,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
```

- generation config：

```json
{
  "limit": null,
  "max_new_tokens": 384,
  "image_limit": 3,
  "max_pixels": 1003520,
  "torch_dtype": "bfloat16",
  "device_map": "auto",
  "hold_prior_lambda": 0.0,
  "hold_prior_target": 0.2,
  "hold_prior_observed": 0.5333333333333333
}
```

- 1 条模型 raw output（完整文本）：

```text
<next_stage>interest</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options and compare them</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.80</reward>
```

### Step E: Parsing / 抽取 prediction

- parser 函数源码：

```python
def parse_deliberation_output(raw: str) -> dict:
    values = _extract_tags(raw, config.DELIBERATION_TAGS)
    next_stage = values["next_stage"]
    if next_stage not in rules.AIDA_STAGES:
        raise MalformedOutputError(f"invalid next_stage: {next_stage}")
    risk = values["risk"]
    benefit = values["benefit"]
    if risk not in config.VALID_RISKS:
        raise MalformedOutputError(f"invalid risk: {risk}")
    if benefit not in config.VALID_BENEFITS:
        raise MalformedOutputError(f"invalid benefit: {benefit}")
    reward = _parse_reward(values["reward"])
    return {
        "next_aida_stage": next_stage,
        "next_bdi": {
            "belief": values["next_belief"],
            "desire": values["next_desire"],
            "intention": values["next_intention"],
        },
        "risk": risk,
        "benefit": benefit,
        "reward": reward,
    }
```

- parser 输入和输出对照：

```json
{
  "parser_input_raw_output": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options and compare them</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>",
  "parser_output": {
    "next_aida_stage": "interest",
    "next_bdi": {
      "belief": "The salesperson may help resolve the decision.",
      "desire": "explore available options and compare them",
      "intention": "continue browsing and comparing"
    },
    "risk": "low",
    "benefit": "high",
    "reward": 0.8
  },
  "parse_ok": true,
  "error": null
}
```

- parse 失败 fallback：`scripts/eval_ms_swift_checkpoint.py:evaluate` 在 `MalformedOutputError / RuntimeError / ValueError` 时写入 `parse_ok=False` 和 `error`；该样本不进入 parsed metric，strict metric 中由 4dim summarizer 计为 `__parse_error__`。

### Step F: Gold label 取法

- gold label 字段名：`<next_stage>...</next_stage>` 与 `<reward>...</reward>`
- gold label 取自：该 row 的 `messages[2].content`，再由相同 parser 或 `tag_value(...)` 抽取。
- 1 条 gold label 完整原文：

```text

```

- gold label space：`next_stage: attention / interest / desire / action; risk/benefit: low / medium / high; reward: [-1.00, 1.00] two decimals`

### Step G: Metric 计算

- metric 函数源码：

```python
def _score_next_state(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    pairs = []
    strict_pairs = []
    reward_errors = []
    by_act: dict[str, list[tuple[str, str]]] = defaultdict(list)
    by_act_reward: dict[str, list[float]] = defaultdict(list)
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold_stage = tag_value(row["messages"][2]["content"], "next_stage")
        gold_reward = _float_or_none(tag_value(row["messages"][2]["content"], "reward"))
        act = row.get("meta", {}).get("candidate_act")
        if out.get("parse_ok"):
            parsed = out.get("parsed") or {}
            pred_stage = parsed.get("next_aida_stage")
            pairs.append((pred_stage, gold_stage))
            strict_pairs.append((pred_stage, gold_stage))
            if act:
                by_act[act].append((pred_stage, gold_stage))
            pred_reward = _float_or_none(parsed.get("reward"))
            if pred_reward is not None and gold_reward is not None:
                err = abs(pred_reward - gold_reward)
                reward_errors.append(err)
                if act:
                    by_act_reward[act].append(err)
        else:
            strict_pairs.append(("__parse_error__", gold_stage))
    return {
        "parse_rate": result.get("parse_rate"),
        "next_stage": _classification_metrics(pairs, list(AIDA_STAGES)),
        "next_stage_strict": _classification_metrics(strict_pairs, list(AIDA_STAGES)),
        "reward_mae": sum(reward_errors) / len(reward_errors) if reward_errors else None,
        "by_candidate_act": {
            act: {
                **_classification_metrics(items, list(AIDA_STAGES)),
                "reward_mae": (sum(by_act_reward[act]) / len(by_act_reward[act]) if by_act_reward.get(act) else None),
                "n": len(items),
            }
            for act, items in sorted(by_act.items())
        },
        "outputs_by_candidate": _candidate_output_map(result),
    }

def _classification_metrics(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> dict[str, Any]:
    clean = [(p, g) for p, g in pairs if g is not None]
    return {
        "macro_f1": _macro_f1(clean, labels),
        "accuracy": _accuracy(clean),
        "per_class": {
            label: _per_label(clean, label)
            for label in labels
        },
        "support": dict(sorted(Counter(g for _, g in clean).items())),
        "pred_count": dict(sorted(Counter(p for p, _ in clean if p is not None).items())),
        "n": len(clean),
    }

def _macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(_per_label(pairs, label)["f1"] for label in labels) / len(labels)

def _per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }

def action_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [(row.get("chosen_act"), row.get("gold_act")) for row in outputs]
    return {
        "macro_f1": macro_f1(pairs, list(FIVE_ACTS)),
        "accuracy": accuracy(pairs),
        "per_act": {act: per_label(pairs, act) for act in FIVE_ACTS},
        "pred_count": dict(sorted(Counter(pred for pred, _ in pairs if pred).items())),
        "support": dict(sorted(Counter(gold for _, gold in pairs if gold).items())),
    }

def next_state_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = []
    strict_pairs = []
    reward_errors = []
    by_act: dict[str, list[tuple[str | None, str | None]]] = defaultdict(list)
    by_stage: dict[str, list[tuple[str | None, str | None]]] = defaultdict(list)
    for row in outputs:
        gold_stage = row.get("gold", {}).get("next_aida_stage")
        pred_stage = row.get("parsed", {}).get("next_aida_stage") if row.get("parse_ok") else None
        if row.get("parse_ok"):
            pairs.append((pred_stage, gold_stage))
            strict_pairs.append((pred_stage, gold_stage))
            try:
                reward_errors.append(abs(float(row["parsed"].get("reward")) - float(row["gold"].get("reward"))))
            except (TypeError, ValueError):
                pass
        else:
            strict_pairs.append(("__parse_error__", gold_stage))
        by_act[row.get("candidate_act")].append((pred_stage, gold_stage))
        by_stage[gold_stage].append((pred_stage, gold_stage))
    return {
        "parse_rate": sum(1 for row in outputs if row.get("parse_ok")) / len(outputs) if outputs else None,
        "next_stage_macro_f1": macro_f1(pairs, list(AIDA_STAGES)),
        "next_stage_strict_macro_f1": macro_f1(strict_pairs, list(AIDA_STAGES)),
        "accuracy": accuracy(pairs),
        "reward_mae": sum(reward_errors) / len(reward_errors) if reward_errors else None,
        "per_candidate_act": {
            key: {"n": len(value), "macro_f1": macro_f1(value, list(AIDA_STAGES)), "accuracy": accuracy(value)}
            for key, value in sorted(by_act.items())
        },
        "per_gold_stage": {
            key: {"n": len(value), "macro_f1": macro_f1(value, list(AIDA_STAGES)), "accuracy": accuracy(value)}
            for key, value in sorted(by_stage.items())
        },
    }

def macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(per_label(pairs, label)["f1"] for label in labels) / len(labels)

def per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }
```

- parse 失败处理：parsed macro F1 只使用 parse 成功样本；strict macro F1 在 4dim summarizer 中把 parse failure 作为 `__parse_error__` 预测写入分母。
- macro / micro / weighted：报告使用 macro F1；没有使用 weighted F1。
- 1 条 `(pred, gold, match/mismatch)` 示例：

```json
{
  "pred": "interest",
  "gold": "interest",
  "match": true
}
```

- 80/107 coverage：`next_state_covered80.jsonl` 有 `80` 条；`next_state_unscored27.jsonl` 有 `27` 条。
- 无 gold 样本示例：

```json
{
  "scene_id": "target_piwm_700",
  "candidate_action": "Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e",
  "candidate_act": "Recommend",
  "reason": "stage-conditioned placeholder candidate has no exact transition_modeling gold"
}
```



## 4. Dim 4 best_act 评估

### Step A: 评估入口

- 评估脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/eval_ms_swift_checkpoint.py`
- 汇总/输入准备脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/piwm_4dim_eval.py`
- 命令行入口：本地未找到 shell history 或 tmux log 中的完整原始命令；以下命令由 raw artifact 的 `input_jsonl/eval_args/checkpoint` 字段与脚本参数还原：

```bash
python3 scripts/eval_ms_swift_checkpoint.py --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500 --input-jsonl data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl --out reports/4dim_eval_raw_20260524/piwm_main_action_selection.json --max-new-tokens 192 --image-limit 3 --max-pixels 1003520
```

### Step B: 评估数据加载

- 输入数据文件路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/reports/4dim_eval_raw_20260524/target_action_selection.jsonl`
- 一共加载：`30` 条
- 数据加载代码片段：

```python
def _read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows
```

- 1 条原始数据 sample（完整 JSON）：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe Stage-1 customer-state representation is:\n- stage: interest\n- intent_label: explore_options\n- visible evidence: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。\n- engagement pattern: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。\n- gaze and attention: 表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。\n- body and hands: 正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。\n- belief: 售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。\n- desire: 想进一步了解商品是否值得购买，并确认它是否符合自己的需求。\n- intention: 继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。\n\nCandidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您今天想先看价格、功能，还是适合什么场景？, screen={'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}, voice_style=curious, light=soft_invitation, physical_action=智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。, utterance=您今天想先看价格、功能，还是适合什么场景？\n- Inform_24926eed1e21: act=Inform, params={'content_type': 'attributes', 'depth': 'brief'}, surface_text=您好，需要时我可以帮您说明。, screen={'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None}, voice_style=warm, light=soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您好，需要时我可以帮您说明。\n- Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=如果您想省心选择，可以优先看这款更稳妥的。, screen={'action': 'highlight_soft_recommendation', 'cta': None}, voice_style=calm, light=highlight_one_option_soft, physical_action=智能售货柜轻量高亮一个选项，并保留顾客选择空间。, utterance=如果您想省心选择，可以优先看这款更稳妥的。\n- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）\n\nChoose the best intervention and explain your reasoning briefly.\n\nOutput the following fields, in this exact order:\n<rationale>...</rationale>\n<chosen>...</chosen>\n<intervention_action>...</intervention_action>\n<intervention_utterance>...</intervention_utterance>\n\n- chosen must be one of the candidate labels listed above, exact string match.\n- rationale should use the customer state and action fit, not hidden reward values.\n- intervention_action must describe the concrete salesperson or terminal behavior.\n- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence."
    },
    {
      "role": "assistant",
      "content": "<rationale>主动询问以轻松提问方式降低探索难度，让顾客感受被理解并激发针对性兴趣，对比后易逐步明晰需求。</rationale>\n<chosen>Elicit_b1166d372e5e</chosen>\n<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>\n<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "task": "action_selection_5act",
  "source_id": "target_piwm_700",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "test",
    "qa_status": "qa_reviewed_pass",
    "human_review_status": "project_lead_reviewed_pass",
    "viewpoint": "target_frontcam",
    "best_act": "Elicit",
    "candidate_action_acts": {
      "Elicit_b1166d372e5e": "Elicit",
      "Inform_24926eed1e21": "Inform",
      "Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e": "Recommend",
      "Hold_eda24b4bb712": "Hold"
    },
    "five_act_only": true,
    "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
    "augmentation_policy": null,
    "augmented_from_state_id": null
  }
}
```

### Step C: Prompt 构造

- prompt template 源码：

```python
def build_action_prompt_no_leak(record: dict, *, five_act_only: bool = False) -> str:
    state = record["meta"]["state_summary"]
    bdi = state["bdi"]
    visual = state.get("visual_state", {})
    frames = record["meta"].get("frames", [])
    candidate_block = format_candidate_block_no_leak(record["meta"]["candidate_block"], five_act_only=five_act_only)
    five_act_guardrail = (
        "\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. "
        "Choose Hold only when the visible customer state clearly supports waiting or silence."
        if five_act_only
        else ""
    )
    return (
        "You are observing a customer in a retail store. Below are "
        f"{len(frames)} frames sampled from a streaming camera, in chronological order.\n\n"
        f"{image_placeholders(len(frames))}\n\n"
        "The Stage-1 customer-state representation is:\n"
        f"- stage: {state['aida_stage']}\n"
        f"- intent_label: {state.get('intent', 'not provided')}\n"
        f"- visible evidence: {visual.get('summary', 'not provided')}\n"
        f"- engagement pattern: {visual.get('engagement_pattern', 'not provided')}\n"
        f"- gaze and attention: {visual.get('gaze_and_attention', 'not provided')}\n"
        f"- body and hands: {visual.get('body_and_hands', 'not provided')}\n"
        f"- belief: {bdi['belief']}\n"
        f"- desire: {bdi['desire']}\n"
        f"- intention: {bdi['intention']}\n\n"
        "Candidate interventions are listed below. They include only the action identity, parameters, "
        "and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n"
        f"{candidate_block}\n\n"
        "Choose the best intervention and explain your reasoning briefly.\n\n"
        "Output the following fields, in this exact order:\n"
        f"{config.tag_instruction_lines(config.ACTION_TAGS)}\n\n"
        "- chosen must be one of the candidate labels listed above, exact string match.\n"
        "- rationale should use the customer state and action fit, not hidden reward values.\n"
        "- intervention_action must describe the concrete salesperson or terminal behavior.\n"
        "- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold."
        f"{five_act_guardrail}"
    )
```

- 1 条实际喂给模型的完整 prompt（messages 中 system + user，含 image token 标记）：

```json
{
  "system": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.",
  "user": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe Stage-1 customer-state representation is:\n- stage: interest\n- intent_label: explore_options\n- visible evidence: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。\n- engagement pattern: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。\n- gaze and attention: 表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。\n- body and hands: 正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。\n- belief: 售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。\n- desire: 想进一步了解商品是否值得购买，并确认它是否符合自己的需求。\n- intention: 继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。\n\nCandidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您今天想先看价格、功能，还是适合什么场景？, screen={'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}, voice_style=curious, light=soft_invitation, physical_action=智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。, utterance=您今天想先看价格、功能，还是适合什么场景？\n- Inform_24926eed1e21: act=Inform, params={'content_type': 'attributes', 'depth': 'brief'}, surface_text=您好，需要时我可以帮您说明。, screen={'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None}, voice_style=warm, light=soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您好，需要时我可以帮您说明。\n- Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=如果您想省心选择，可以优先看这款更稳妥的。, screen={'action': 'highlight_soft_recommendation', 'cta': None}, voice_style=calm, light=highlight_one_option_soft, physical_action=智能售货柜轻量高亮一个选项，并保留顾客选择空间。, utterance=如果您想省心选择，可以优先看这款更稳妥的。\n- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）\n\nChoose the best intervention and explain your reasoning briefly.\n\nOutput the following fields, in this exact order:\n<rationale>...</rationale>\n<chosen>...</chosen>\n<intervention_action>...</intervention_action>\n<intervention_utterance>...</intervention_utterance>\n\n- chosen must be one of the candidate labels listed above, exact string match.\n- rationale should use the customer state and action fit, not hidden reward values.\n- intervention_action must describe the concrete salesperson or terminal behavior.\n- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence."
}
```

### Step D: 模型 inference

- 模型加载与推理代码：

```python
def _normalize_messages(row: dict[str, Any], *, image_limit: int | None = None, max_pixels: int | None = None) -> list[dict[str, Any]]:
    messages = row["messages"]
    system = messages[0]
    user = messages[1]
    text = str(user["content"]).replace("<image>", "").strip()
    content: list[dict[str, str]] = []
    images = row.get("images", [])
    if image_limit is not None:
        images = images[:image_limit]
    for image in images:
        item: dict[str, Any] = {"type": "image", "image": image}
        if max_pixels is not None:
            item["max_pixels"] = max_pixels
        content.append(item)
    content.append({"type": "text", "text": text})
    return [{"role": "system", "content": system["content"]}, {"role": "user", "content": content}]

def _generate_one(model, processor, row: dict[str, Any], args: argparse.Namespace) -> str:
    messages = _normalize_messages(row, image_limit=args.image_limit, max_pixels=args.max_pixels)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    logits_processor = _logits_processor_for_row(processor, row, args)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            logits_processor=logits_processor,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
```

- generation config：

```json
{
  "limit": null,
  "max_new_tokens": 192,
  "image_limit": 3,
  "max_pixels": 1003520,
  "torch_dtype": "bfloat16",
  "device_map": "auto",
  "hold_prior_lambda": 0.0,
  "hold_prior_target": 0.2,
  "hold_prior_observed": 0.5333333333333333
}
```

- 1 条模型 raw output（完整文本）：

```text
<rationale>开放式引导能有效降低犹豫，直接回应顾客关注点，显著提升信任感和兴趣。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

### Step E: Parsing / 抽取 prediction

- parser 函数源码：

```python
def parse_action_output(raw: str, valid_actions: Iterable[str] | None = None, *, five_act_only: bool = False) -> dict:
    values = _extract_tags(raw, config.ACTION_TAGS)
    chosen = values["chosen"]
    if valid_actions is not None:
        valid = set(valid_actions)
        is_valid = chosen in valid and (not five_act_only or _action_label_act(chosen) in FIVE_ACTS)
    else:
        is_valid = _is_valid_action_label(chosen, five_act_only=five_act_only)
    if not is_valid:
        raise MalformedOutputError(f"chosen action is not valid: {chosen}")
    return {
        "rationale": values["rationale"],
        "chosen": chosen,
        "intervention_action": values["intervention_action"],
        "intervention_utterance": values["intervention_utterance"],
    }

def _extract_tags(raw: str, tags: tuple[config.TagPair, ...]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for tag in tags:
        pattern = re.escape(tag.open) + r"(.*?)" + re.escape(tag.close)
        matches = re.findall(pattern, raw, flags=re.DOTALL)
        if len(matches) != 1:
            raise MalformedOutputError(f"expected exactly one {tag.name} tag, found {len(matches)}")
        value = matches[0].strip()
        if value == "":
            raise MalformedOutputError(f"{tag.name} tag is empty")
        parsed[tag.name] = value
    return parsed

def _is_valid_action_label(action: str, *, five_act_only: bool = False) -> bool:
    act = _action_label_act(action)
    if five_act_only and act not in FIVE_ACTS:
        return False
    if action in rules.ACTIONS:
        return True
    return re.fullmatch(r"(Greet|Elicit|Inform|Recommend|Reassure|Hold)_[0-9a-f]{12}", action) is not None
```

- parser 输入和输出对照：

```json
{
  "parser_input_raw_output": "<rationale>开放式引导能有效降低犹豫，直接回应顾客关注点，显著提升信任感和兴趣。</rationale>\n<chosen>Elicit_b1166d372e5e</chosen>\n<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>\n<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>",
  "parser_output": {
    "rationale": "开放式引导能有效降低犹豫，直接回应顾客关注点，显著提升信任感和兴趣。",
    "chosen": "Elicit_b1166d372e5e",
    "intervention_action": "智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。",
    "intervention_utterance": "您今天想先看价格、功能，还是适合什么场景？"
  },
  "parse_ok": true,
  "error": null
}
```

- parse 失败 fallback：`scripts/eval_ms_swift_checkpoint.py:evaluate` 在 `MalformedOutputError / RuntimeError / ValueError` 时写入 `parse_ok=False` 和 `error`；该样本不进入 parsed metric，strict metric 中由 4dim summarizer 计为 `__parse_error__`。

### Step F: Gold label 取法

- gold label 字段名：`<chosen>...</chosen>`，再通过 `meta.candidate_action_acts` 映射到 Greet/Elicit/Inform/Recommend/Hold
- gold label 取自：该 row 的 `messages[2].content`，再由相同 parser 或 `tag_value(...)` 抽取。
- 1 条 gold label 完整原文：

```text
<rationale>主动询问以轻松提问方式降低探索难度，让顾客感受被理解并激发针对性兴趣，对比后易逐步明晰需求。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

- gold label space：`Greet / Elicit / Inform / Recommend / Hold`

### Step G: Metric 计算

- metric 函数源码：

```python
def _score_action(result: dict[str, Any], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = {row["source_id"]: row for row in inputs}
    pairs = []
    strict_pairs = []
    for out in result.get("outputs", []):
        row = by_source[out["source_id"]]
        gold = _gold_act(row)
        if out.get("parse_ok"):
            mapping = row.get("meta", {}).get("candidate_action_acts", {})
            pred = _action_to_act((out.get("parsed") or {}).get("chosen"), mapping)
            pairs.append((pred, gold))
            strict_pairs.append((pred, gold))
        else:
            strict_pairs.append(("__parse_error__", gold))
    return {
        "parse_rate": result.get("parse_rate"),
        "action": _classification_metrics(pairs, list(FIVE_ACTS)),
        "action_strict": _classification_metrics(strict_pairs, list(FIVE_ACTS)),
        "outputs_by_scene": _scene_output_map(result, "action"),
    }

def _classification_metrics(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> dict[str, Any]:
    clean = [(p, g) for p, g in pairs if g is not None]
    return {
        "macro_f1": _macro_f1(clean, labels),
        "accuracy": _accuracy(clean),
        "per_class": {
            label: _per_label(clean, label)
            for label in labels
        },
        "support": dict(sorted(Counter(g for _, g in clean).items())),
        "pred_count": dict(sorted(Counter(p for p, _ in clean if p is not None).items())),
        "n": len(clean),
    }

def _macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(_per_label(pairs, label)["f1"] for label in labels) / len(labels)

def _per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }

# Direct evaluator metric implementation:
def _macro_metrics(metric_totals: dict[str, int], metric_denoms: dict[str, int]) -> dict[str, float | None]:
    metrics: dict[str, float | None] = {}
    names = [key.removeprefix("__labels__") for key in metric_denoms if key.startswith("__labels__")]
    for name in sorted(names):
        pairs: list[tuple[str, str]] = []
        prefix = f"__labels__{name}\t"
        for key, count in metric_totals.items():
            if not key.startswith(prefix):
                continue
            pred, gold = key[len(prefix):].split("\t", 1)
            pairs.extend([(pred, gold)] * count)
        metrics[f"{name}_accuracy"] = _accuracy(pairs)
        metrics[f"{name}_macro_f1"] = _macro_f1(pairs)
        if name == "intent":
            metrics.update(intent_a3plus_metrics(pairs))
        if name == "go_no_go":
            metrics["go_precision"] = _precision(pairs, positive="go")
            metrics["go_recall"] = _recall(pairs, positive="go")
            metrics["no_go_precision"] = _precision(pairs, positive="no_go")
            metrics["no_go_recall"] = _recall(pairs, positive="no_go")
    return metrics

def _macro_f1(pairs: list[tuple[str, str]]) -> float | None:
    labels = sorted({label for pair in pairs for label in pair})
    if not labels:
        return None
    f1s = []
    for label in labels:
        tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
        fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
        fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1s.append((2 * precision * recall / (precision + recall)) if precision + recall else 0.0)
    return sum(f1s) / len(f1s)
```

- parse 失败处理：parsed macro F1 只使用 parse 成功样本；strict macro F1 在 4dim summarizer 中把 parse failure 作为 `__parse_error__` 预测写入分母。
- macro / micro / weighted：报告使用 macro F1；没有使用 weighted F1。
- 1 条 `(pred, gold, match/mismatch)` 示例：

```json
{
  "pred": "Elicit_b1166d372e5e",
  "gold": "Elicit_b1166d372e5e",
  "match": true
}
```

- Dim 4 raw artifact：`reports/4dim_eval_raw_20260524/piwm_main_action_selection.json`。



## 5. Trick 6 反事实推理评估（counterfactual planning）

### Step A: 评估入口

- 评估脚本路径：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/run_trick6_counterfactual_planning.py`
- 命令行入口：本地未找到 shell history 或 tmux log 中的完整原始命令；以下命令由 raw artifact 的 `checkpoint/action_jsonl/reward_mode` 字段与脚本参数还原：

Reward A:
```bash
python3 scripts/run_trick6_counterfactual_planning.py --mode trick6 --reward-mode stage_advance --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500 --action-jsonl data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl --transition-jsonl data/official/piwm_target_v1/transition_modeling.jsonl --out reports/trick6_raw_20260524/trick6_reward_stage_advance.json
```

Reward B:
```bash
python3 scripts/run_trick6_counterfactual_planning.py --mode trick6 --reward-mode model_score --model /root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct --checkpoint /root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500 --action-jsonl data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl --transition-jsonl data/official/piwm_target_v1/transition_modeling.jsonl --out reports/trick6_raw_20260524/trick6_reward_model_score.json
```

### Step B: 评估数据加载

- 输入 action 数据文件路径：`data/official/domain_specialization_eval_v2/target_frontcam_5act_test_action_selection.jsonl`
- 输入 transition gold 文件路径：`data/official/piwm_target_v1/transition_modeling.jsonl`
- 一共加载 action scenes：`30` 条
- 候选调用总数：`91`
- 数据加载与 index 构造代码片段：

```python
def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def build_transition_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row.get("meta", {}).get("parent_state_id"), row.get("input", {}).get("candidate_action")): row
        for row in rows
        if row.get("meta", {}).get("parent_state_id") and row.get("input", {}).get("candidate_action")
    }

def build_state_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    state_index: dict[str, dict[str, Any]] = {}
    for row in rows:
        parent = row.get("meta", {}).get("parent_state_id")
        state = row.get("input", {}).get("current_state_summary")
        if parent and state and parent not in state_index:
            state_index[parent] = state
    return state_index
```

- 1 条原始 action data sample（完整 JSON）：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nThe Stage-1 customer-state representation is:\n- stage: interest\n- intent_label: explore_options\n- visible evidence: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。\n- engagement pattern: 顾客走近后在机器前停留，身体轻微前倾，视线先稳定看向前方，再短暂下移，并在前方不同位置之间自然切换数次，持续表现出浏览、比较和确认信息的状态。\n- gaze and attention: 表情自然克制，带有轻微思考、权衡和犹豫，没有夸张惊讶或明显情绪波动。\n- body and hands: 正面朝向机器，站姿稳定，停留在原地，身体轻微前倾，双手自然放置并始终保持在画面内。\n- belief: 售货机里可能有她感兴趣的商品，值得停下来仔细看一看。她认为当前还需要继续确认和比较信息，暂时没有足够把握立即购买。\n- desire: 想进一步了解商品是否值得购买，并确认它是否符合自己的需求。\n- intention: 继续停留观察，反复确认信息并进行比较，在做出购买决定前保持谨慎。\n\nCandidate interventions are listed below. They include only the action identity, parameters, and concrete realization. They do not include gold rewards, predicted next states, risks, or benefits.\n\n- Elicit_b1166d372e5e: act=Elicit, params={'openness': 'open', 'slot': 'need_focus'}, surface_text=您今天想先看价格、功能，还是适合什么场景？, screen={'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}, voice_style=curious, light=soft_invitation, physical_action=智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。, utterance=您今天想先看价格、功能，还是适合什么场景？\n- Inform_24926eed1e21: act=Inform, params={'content_type': 'attributes', 'depth': 'brief'}, surface_text=您好，需要时我可以帮您说明。, screen={'action': 'show_comparison_or_details', 'target': '{candidate_items}', 'cta': None}, voice_style=warm, light=soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=您好，需要时我可以帮您说明。\n- Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e: act=Recommend, params={'target': 'item', 'pressure': 'soft'}, surface_text=如果您想省心选择，可以优先看这款更稳妥的。, screen={'action': 'highlight_soft_recommendation', 'cta': None}, voice_style=calm, light=highlight_one_option_soft, physical_action=智能售货柜轻量高亮一个选项，并保留顾客选择空间。, utterance=如果您想省心选择，可以优先看这款更稳妥的。\n- Hold_eda24b4bb712: act=Hold, params={'mode': 'silent'}, surface_text=, screen={'action': 'idle_minimal', 'cta': None}, voice_style=silent, light=maintain_current_soft_breathing, physical_action=智能售货柜按屏幕、语音、灯效执行该候选响应。, utterance=（静默）\n\nChoose the best intervention and explain your reasoning briefly.\n\nOutput the following fields, in this exact order:\n<rationale>...</rationale>\n<chosen>...</chosen>\n<intervention_action>...</intervention_action>\n<intervention_utterance>...</intervention_utterance>\n\n- chosen must be one of the candidate labels listed above, exact string match.\n- rationale should use the customer state and action fit, not hidden reward values.\n- intervention_action must describe the concrete salesperson or terminal behavior.\n- intervention_utterance must be a short customer-facing sentence, or （静默） for silent Hold.\n- In the 5-act setting, Hold is a real no-intervention decision, not an uncertainty fallback. Choose Hold only when the visible customer state clearly supports waiting or silence."
    },
    {
      "role": "assistant",
      "content": "<rationale>主动询问以轻松提问方式降低探索难度，让顾客感受被理解并激发针对性兴趣，对比后易逐步明晰需求。</rationale>\n<chosen>Elicit_b1166d372e5e</chosen>\n<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>\n<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "task": "action_selection_5act",
  "source_id": "target_piwm_700",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "split": "test",
    "qa_status": "qa_reviewed_pass",
    "human_review_status": "project_lead_reviewed_pass",
    "viewpoint": "target_frontcam",
    "best_act": "Elicit",
    "candidate_action_acts": {
      "Elicit_b1166d372e5e": "Elicit",
      "Inform_24926eed1e21": "Inform",
      "Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e": "Recommend",
      "Hold_eda24b4bb712": "Hold"
    },
    "five_act_only": true,
    "leakage_control": "no_reward_no_predicted_outcome_in_prompt",
    "augmentation_policy": null,
    "augmented_from_state_id": null
  }
}
```

### Step C: Prompt 构造

- Trick 6 每个 candidate 会调用 `next_state_ms_row(...)` 构造 next_state prompt；若有 transition gold，用 `build_deliberation_prompt`，若无 transition gold，用 action row 中的 state 和 candidate payload 拼 placeholder prompt。

```python
def next_state_ms_row(
    action_row: dict[str, Any],
    candidate: str,
    transition_index: dict[tuple[str, str], dict[str, Any]],
    state_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scene_id = action_row["source_id"]
    transition = transition_index.get((scene_id, candidate))
    if transition is not None:
        record = {
            "input": {
                **transition["input"],
                "frames": list(transition["input"].get("frames", [])),
            }
        }
        prompt = build_deliberation_prompt(record)
        images = [str((REPO_ROOT / frame).resolve()) if not str(frame).startswith("/") else str(frame) for frame in record["input"]["frames"]]
        candidate_spec = transition["input"].get("candidate_action_spec", {})
        candidate_act = candidate_spec.get("act") or action_row.get("meta", {}).get("candidate_action_acts", {}).get(candidate)
        candidate_params = candidate_spec.get("params", {})
        gold = transition.get("output", {}).get("next_state", {})
        target = _transition_target_text(transition)
    else:
        state = state_index.get(scene_id) or parse_current_state_from_action_prompt(action_row)
        candidate_payload = parse_candidate_payload(action_row, candidate)
        record = {
            "input": {
                "frames": list(action_row.get("images", [])),
                "current_state_summary": state,
                "candidate_action": candidate,
                "candidate_action_key": candidate,
                "candidate_action_spec": candidate_payload["candidate_action_spec"],
                "candidate_dialogue_act": candidate_payload["candidate_dialogue_act"],
                "candidate_action_realization": candidate_payload["candidate_action_realization"],
                "candidate_terminal_realization": candidate_payload["candidate_terminal_realization"],
            }
        }
        prompt = build_deliberation_prompt(record)
        images = list(action_row.get("images", []))
        candidate_act = candidate_payload["candidate_action_spec"].get("act")
        candidate_params = candidate_payload["candidate_action_spec"].get("params", {})
        target = ""
    return {
        "messages": [
            {"role": "system", "content": PIWM_SYSTEM_PROMPT},
            {"role": "user", "content": f"{'<image>' * len(images)}{prompt.replace(train_config.IMAGE_PLACEHOLDER, '').strip()}"},
            {"role": "assistant", "content": target},
        ],
        "images": images,
        "task": "next_state_prediction",
        "source_id": f"{scene_id}#{candidate}",
        "meta": {
            "parent_state_id": scene_id,
            "candidate_action": candidate,
            "candidate_act": candidate_act,
            "candidate_params": candidate_params,
            "has_transition_gold": transition is not None,
        },
    }
```

- 1 条实际喂给模型的完整 prompt（以 Dim3 covered candidate 同源 prompt 展示，messages 中 system + user，含 image token 标记）：

```json
{
  "system": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags.",
  "user": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您今天想先看价格、功能，还是适合什么场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}\n- voice_style: curious\n- light: soft_invitation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。\n- utterance: 您今天想先看价格、功能，还是适合什么场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
}
```

### Step D: 模型 inference

- 模型加载、message normalize、generation 调用代码：

```python
def load_model(args: argparse.Namespace):
    import torch
    from peft import PeftModel
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
    base = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if args.torch_dtype == "bfloat16" else torch.float16,
        device_map=args.device_map,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, args.checkpoint) if args.checkpoint else base
    model.eval()
    return model, processor

def normalize_messages(row: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    user = row["messages"][1]
    text = str(user["content"]).replace("<image>", "").strip()
    content: list[dict[str, Any]] = []
    for image in row.get("images", [])[: args.image_limit]:
        item: dict[str, Any] = {"type": "image", "image": resolve_runtime_image_path(image)}
        if args.max_pixels is not None:
            item["max_pixels"] = args.max_pixels
        content.append(item)
    content.append({"type": "text", "text": text})
    return [{"role": "system", "content": row["messages"][0]["content"]}, {"role": "user", "content": content}]

def generate_one(model, processor, row: dict[str, Any], args: argparse.Namespace) -> str:
    import torch
    from qwen_vl_utils import process_vision_info

    messages = normalize_messages(row, args)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, prompt_len:]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
```

- generation config：

```json
{
  "max_new_tokens": 384,
  "image_limit": 3,
  "max_pixels": 1003520,
  "do_sample": false,
  "torch_dtype": "bfloat16",
  "device_map": "auto"
}
```

- 1 条模型 raw output（Reward A trace 的第一个 candidate）：

```text
<next_stage>interest</next_stage>
<next_belief>The decision remains uncertain after the last observation.</next_belief>
<next_desire>gain reassurance before deciding</next_desire>
<next_intention>continue comparing and checking</next_intention>
<risk>low</risk>
<benefit>medium</benefit>
<reward>0.30</reward>
```

### Step E: Parsing / 抽取 prediction

- parser 函数源码：

```python
def parse_deliberation_output(raw: str) -> dict:
    values = _extract_tags(raw, config.DELIBERATION_TAGS)
    next_stage = values["next_stage"]
    if next_stage not in rules.AIDA_STAGES:
        raise MalformedOutputError(f"invalid next_stage: {next_stage}")
    risk = values["risk"]
    benefit = values["benefit"]
    if risk not in config.VALID_RISKS:
        raise MalformedOutputError(f"invalid risk: {risk}")
    if benefit not in config.VALID_BENEFITS:
        raise MalformedOutputError(f"invalid benefit: {benefit}")
    reward = _parse_reward(values["reward"])
    return {
        "next_aida_stage": next_stage,
        "next_bdi": {
            "belief": values["next_belief"],
            "desire": values["next_desire"],
            "intention": values["next_intention"],
        },
        "risk": risk,
        "benefit": benefit,
        "reward": reward,
    }
```

- parser 输入和输出对照：

```json
{
  "parser_input_raw_output": "<next_stage>interest</next_stage>\n<next_belief>The decision remains uncertain after the last observation.</next_belief>\n<next_desire>gain reassurance before deciding</next_desire>\n<next_intention>continue comparing and checking</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.30</reward>",
  "parser_output": {
    "next_aida_stage": "interest",
    "next_bdi": {
      "belief": "The decision remains uncertain after the last observation.",
      "desire": "gain reassurance before deciding",
      "intention": "continue comparing and checking"
    },
    "risk": "low",
    "benefit": "medium",
    "reward": 0.3
  },
  "parse_ok": true
}
```

- parse 失败 fallback：单个 candidate parse 失败时 `planning_reward=-inf`；若全部 candidate 失败，调用 direct action inference fallback。

### Step F: Gold label 取法

- gold action 字段：action row assistant target 的 `<chosen>...</chosen>`。
- gold act 映射：`meta.candidate_action_acts[chosen]`。
- Trick 6 的 per-candidate next_state inference 不用 gold 决策，只在最终 action metric 中用 gold action。
- 1 条 gold label 完整原文：

```text
<rationale>主动询问以轻松提问方式降低探索难度，让顾客感受被理解并激发针对性兴趣，对比后易逐步明晰需求。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

- gold label space：Greet / Elicit / Inform / Recommend / Hold。

### Step G: Metric 计算

- reward A/B、argmax、metric 源码：

```python
def reward_stage_advance(current_stage: str | None, parsed: dict[str, Any]) -> float:
    next_stage = parsed.get("next_aida_stage")
    if current_stage not in STAGE_ORDER or next_stage not in STAGE_ORDER:
        return -math.inf
    current_index = STAGE_ORDER[current_stage]
    next_index = STAGE_ORDER[next_stage]
    if next_index > current_index:
        return 1.0
    if next_index == current_index:
        return 0.0
    return -1.0

def reward_model_score(current_stage: str | None, parsed: dict[str, Any]) -> float:
    value = parsed.get("reward")
    try:
        return float(value)
    except (TypeError, ValueError):
        return reward_stage_advance(current_stage, parsed)

def choose_candidate(candidates: list[str], per_candidate: dict[str, Any]) -> str | None:
    parsed = [candidate for candidate in candidates if per_candidate.get(candidate, {}).get("parse_ok")]
    if not parsed:
        return None
    return max(parsed, key=lambda candidate: (per_candidate[candidate]["planning_reward"], -candidates.index(candidate)))

def action_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [(row.get("chosen_act"), row.get("gold_act")) for row in outputs]
    return {
        "macro_f1": macro_f1(pairs, list(FIVE_ACTS)),
        "accuracy": accuracy(pairs),
        "per_act": {act: per_label(pairs, act) for act in FIVE_ACTS},
        "pred_count": dict(sorted(Counter(pred for pred, _ in pairs if pred).items())),
        "support": dict(sorted(Counter(gold for _, gold in pairs if gold).items())),
    }

def next_state_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = []
    strict_pairs = []
    reward_errors = []
    by_act: dict[str, list[tuple[str | None, str | None]]] = defaultdict(list)
    by_stage: dict[str, list[tuple[str | None, str | None]]] = defaultdict(list)
    for row in outputs:
        gold_stage = row.get("gold", {}).get("next_aida_stage")
        pred_stage = row.get("parsed", {}).get("next_aida_stage") if row.get("parse_ok") else None
        if row.get("parse_ok"):
            pairs.append((pred_stage, gold_stage))
            strict_pairs.append((pred_stage, gold_stage))
            try:
                reward_errors.append(abs(float(row["parsed"].get("reward")) - float(row["gold"].get("reward"))))
            except (TypeError, ValueError):
                pass
        else:
            strict_pairs.append(("__parse_error__", gold_stage))
        by_act[row.get("candidate_act")].append((pred_stage, gold_stage))
        by_stage[gold_stage].append((pred_stage, gold_stage))
    return {
        "parse_rate": sum(1 for row in outputs if row.get("parse_ok")) / len(outputs) if outputs else None,
        "next_stage_macro_f1": macro_f1(pairs, list(AIDA_STAGES)),
        "next_stage_strict_macro_f1": macro_f1(strict_pairs, list(AIDA_STAGES)),
        "accuracy": accuracy(pairs),
        "reward_mae": sum(reward_errors) / len(reward_errors) if reward_errors else None,
        "per_candidate_act": {
            key: {"n": len(value), "macro_f1": macro_f1(value, list(AIDA_STAGES)), "accuracy": accuracy(value)}
            for key, value in sorted(by_act.items())
        },
        "per_gold_stage": {
            key: {"n": len(value), "macro_f1": macro_f1(value, list(AIDA_STAGES)), "accuracy": accuracy(value)}
            for key, value in sorted(by_stage.items())
        },
    }

def macro_f1(pairs: list[tuple[str | None, str | None]], labels: list[str]) -> float | None:
    if not labels:
        return None
    return sum(per_label(pairs, label)["f1"] for label in labels) / len(labels)

def per_label(pairs: list[tuple[str | None, str | None]], label: str) -> dict[str, float | int]:
    tp = sum(1 for pred, gold in pairs if pred == label and gold == label)
    fp = sum(1 for pred, gold in pairs if pred == label and gold != label)
    fn = sum(1 for pred, gold in pairs if pred != label and gold == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": sum(1 for _, gold in pairs if gold == label),
        "pred_count": sum(1 for pred, _ in pairs if pred == label),
    }
```

- parse 失败处理：candidate parse failure 记为 `planning_reward=-inf`；action macro F1 对最终 chosen act 与 gold act 计算。
- macro / micro / weighted：报告使用 macro F1。
- 1 条 `(pred, gold, match/mismatch)` 示例：

```json
{
  "Reward A pred": "Hold",
  "Reward B pred": "Inform",
  "gold": "Elicit",
  "Reward A match": false,
  "Reward B match": false
}
```

### Trick 6 端到端 trace

说明：当前 stage-conditioned candidate policy 每条是 3-4 个候选，不是 5 个候选；下面这条 `target_piwm_700` 有 4 个候选。

Reward A 完整 trace：

```json
{
  "scene_id": "target_piwm_700",
  "current_stage": "interest",
  "gold_candidate": "Elicit_b1166d372e5e",
  "gold_act": "Elicit",
  "chosen_candidate": "Hold_eda24b4bb712",
  "chosen_act": "Hold",
  "fallback_used": false,
  "candidate_order": [
    "Hold_eda24b4bb712",
    "Elicit_b1166d372e5e",
    "Inform_24926eed1e21",
    "Inform_053014d173cc"
  ],
  "per_candidate": {
    "Hold_eda24b4bb712": {
      "act": "Hold",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The decision remains uncertain after the last observation.</next_belief>\n<next_desire>gain reassurance before deciding</next_desire>\n<next_intention>continue comparing and checking</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.30</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The decision remains uncertain after the last observation.",
          "desire": "gain reassurance before deciding",
          "intention": "continue comparing and checking"
        },
        "risk": "low",
        "benefit": "medium",
        "reward": 0.3
      },
      "planning_reward": 0.0,
      "has_transition_gold": true
    },
    "Elicit_b1166d372e5e": {
      "act": "Elicit",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options and compare them</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The salesperson may help resolve the decision.",
          "desire": "explore available options and compare them",
          "intention": "continue browsing and comparing"
        },
        "risk": "low",
        "benefit": "high",
        "reward": 0.8
      },
      "planning_reward": 0.0,
      "has_transition_gold": true
    },
    "Inform_24926eed1e21": {
      "act": "Inform",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.85</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The salesperson may help resolve the decision.",
          "desire": "explore available options",
          "intention": "continue browsing and comparing"
        },
        "risk": "low",
        "benefit": "high",
        "reward": 0.85
      },
      "planning_reward": 0.0,
      "has_transition_gold": true
    },
    "Inform_053014d173cc": {
      "act": "Inform",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The salesperson may help resolve the decision.",
          "desire": "explore available options",
          "intention": "continue browsing and comparing"
        },
        "risk": "low",
        "benefit": "high",
        "reward": 0.8
      },
      "planning_reward": 0.0,
      "has_transition_gold": true
    }
  }
}
```

Reward B 完整 trace：

```json
{
  "scene_id": "target_piwm_700",
  "current_stage": "interest",
  "gold_candidate": "Elicit_b1166d372e5e",
  "gold_act": "Elicit",
  "chosen_candidate": "Inform_24926eed1e21",
  "chosen_act": "Inform",
  "fallback_used": false,
  "candidate_order": [
    "Hold_eda24b4bb712",
    "Elicit_b1166d372e5e",
    "Inform_24926eed1e21",
    "Inform_053014d173cc"
  ],
  "per_candidate": {
    "Hold_eda24b4bb712": {
      "act": "Hold",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The decision remains uncertain after the last observation.</next_belief>\n<next_desire>gain reassurance before deciding</next_desire>\n<next_intention>continue comparing and checking</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.30</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The decision remains uncertain after the last observation.",
          "desire": "gain reassurance before deciding",
          "intention": "continue comparing and checking"
        },
        "risk": "low",
        "benefit": "medium",
        "reward": 0.3
      },
      "planning_reward": 0.3,
      "has_transition_gold": true
    },
    "Elicit_b1166d372e5e": {
      "act": "Elicit",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options and compare them</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The salesperson may help resolve the decision.",
          "desire": "explore available options and compare them",
          "intention": "continue browsing and comparing"
        },
        "risk": "low",
        "benefit": "high",
        "reward": 0.8
      },
      "planning_reward": 0.8,
      "has_transition_gold": true
    },
    "Inform_24926eed1e21": {
      "act": "Inform",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.85</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The salesperson may help resolve the decision.",
          "desire": "explore available options",
          "intention": "continue browsing and comparing"
        },
        "risk": "low",
        "benefit": "high",
        "reward": 0.85
      },
      "planning_reward": 0.85,
      "has_transition_gold": true
    },
    "Inform_053014d173cc": {
      "act": "Inform",
      "parse_ok": true,
      "prediction": "<next_stage>interest</next_stage>\n<next_belief>The salesperson may help resolve the decision.</next_belief>\n<next_desire>explore available options</next_desire>\n<next_intention>continue browsing and comparing</next_intention>\n<risk>low</risk>\n<benefit>high</benefit>\n<reward>0.80</reward>",
      "parsed": {
        "next_aida_stage": "interest",
        "next_bdi": {
          "belief": "The salesperson may help resolve the decision.",
          "desire": "explore available options",
          "intention": "continue browsing and comparing"
        },
        "risk": "low",
        "benefit": "high",
        "reward": 0.8
      },
      "planning_reward": 0.8,
      "has_transition_gold": true
    }
  }
}
```


## Q1：Dim 4 在两条 pipeline 上的口径是否一致

### best_act 主 pipeline

- 推理脚本：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/eval_ms_swift_checkpoint.py`
- parser：`parse_action_output(raw, valid_actions=meta.candidate_action_acts.keys(), five_act_only=True)`
- metric：`scripts/eval_ms_swift_checkpoint.py` 中 `_classification_items -> _macro_metrics -> _macro_f1`
- raw artifact：`reports/4dim_eval_raw_20260524/piwm_main_action_selection.json`

### 4 维度评估 pipeline 中的 Dim 4

- 汇总脚本：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/scripts/piwm_4dim_eval.py`
- parser：不重新 parse raw text；读取 `piwm_main_action_selection.json` 中已经 parse 好的 `parsed.chosen`
- metric：`scripts/piwm_4dim_eval.py` 中 `_score_action -> _classification_metrics -> _macro_f1`

### 逐字段对比

| 项 | best_act 主 pipeline | 4 维度 Dim4 pipeline |
| --- | --- | --- |
| 输入 JSONL | raw artifact 中记录为 `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl` | `reports/4dim_eval_raw_20260524/target_action_selection.jsonl` 用于 summarizer 对齐 gold |
| Prompt | action row 原始 `messages` | 不重新构造，读取 action row/gold 与 raw output |
| Parser | `parse_action_output` | 使用已解析 `parsed.chosen`，再 `_action_to_act` |
| Valid action | row-level candidate keys | row-level `meta.candidate_action_acts` |
| Macro F1 labels | eval script 从 pairs 中出现的 labels 汇总 | 固定 FIVE_ACTS = Greet/Elicit/Inform/Recommend/Hold |
| Parse failure | 不加入 classification item；记录 `parse_ok=False` | strict 版本可计 `__parse_error__`，parsed 版本只看 parse 成功 |

## Q2：Dim 1/2/3 是否和 Dim 4 在同一次推理调用里产生

- Dim 1 与 Dim 2 来自同一个 `user_intent` prompt，一次输出同时包含 stage、intent、visual fields、BDI。
- Dim 3 来自独立 `next_state_prediction` prompt，每个 candidate action 一次 prompt。
- Dim 4 来自独立 `action_selection_5act` prompt，每个 scene 一次 prompt。
- 未找到一个同时要求输出 `stage+intent+next_state+best_act` 的 multi-field prompt。

Dim1/Dim2 raw output 示例：

```text
<stage>action</stage>
<intent_label>confirm_choice</intent_label>
<visual_summary>顾客在智能售货机前直接操作，说明已经进入备付或确认阶段。 当前场景是自助式售货机，可见判断应围绕顾客是否接近完成购买、兴趣点是什么，以及是否有明确的决策需求。视角为斜角监控/第三方视角。</visual_summary>
<engagement_pattern>顾客与商品发生直接互动。 移动较少，动作集中在商品操作上。 互动已经进入体验层面，重点是确认尺寸、重量、功能或价格差异。</engagement_pattern>
<gaze_and_attention>视线集中在操作位置，伴随直接互动。 视线重点应落在确认点（如尺寸、重量、功能或价格差异），而不是停留于商品本身。</gaze_and_attention>
<body_and_hands>身体靠近商品并配合手部动作。 手部主要围绕核对尺寸、重量、功能或价格差异。</body_and_hands>
<belief>The product is nearly ready, but confirmation is still needed.</belief>
<desire>confirm the preferred choice</desire>
<intention>move toward confirming the choice</intention>
```

Dim3 raw output 示例：

```text
<next_stage>interest</next_stage>
<next_belief>The salesperson may help resolve the decision.</next_belief>
<next_desire>explore available options and compare them</next_desire>
<next_intention>continue browsing and comparing</next_intention>
<risk>low</risk>
<benefit>high</benefit>
<reward>0.80</reward>
```

Dim4 raw output 示例：

```text
<rationale>开放式引导能有效降低犹豫，直接回应顾客关注点，显著提升信任感和兴趣。</rationale>
<chosen>Elicit_b1166d372e5e</chosen>
<intervention_action>智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。</intervention_action>
<intervention_utterance>您今天想先看价格、功能，还是适合什么场景？</intervention_utterance>
```

## Q3：Dim 2 intent label space 和训练数据 label space 是否对齐

训练数据来源：`/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl` + `/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl`

训练 intent label space：

```json
{
  "compare_value_for_money": 16,
  "confirm_choice": 177,
  "explore_options": 94,
  "leave_without_purchase": 17,
  "negotiate_price": 55,
  "request_demonstration": 93,
  "seek_reassurance": 91
}
```

评估 target test intent label space：

```json
{
  "compare_value_for_money": 6,
  "confirm_choice": 6,
  "explore_options": 15,
  "no_clear_intent": 3
}
```

逐项对比：

```json
{
  "train_only": [
    "leave_without_purchase",
    "negotiate_price",
    "request_demonstration",
    "seek_reassurance"
  ],
  "eval_only": [
    "no_clear_intent"
  ],
  "common": [
    "compare_value_for_money",
    "confirm_choice",
    "explore_options"
  ]
}
```

## Q4：Dim 1 AIDA label space 一致性

训练 stage label space：

```json
{
  "action": 77,
  "attention": 49,
  "desire": 128,
  "interest": 289
}
```

评估 target test stage label space：

```json
{
  "action": 6,
  "attention": 3,
  "desire": 11,
  "interest": 10
}
```

逐项对比：

```json
{
  "train_only": [],
  "eval_only": [],
  "common": [
    "action",
    "attention",
    "desire",
    "interest"
  ]
}
```

## Q5：Dim 3 next_state 的输入条件

### prompt 给了哪些条件信息

- `next_state_covered80.jsonl` 当前 prompt 使用 `build_next_state_prediction_prompt` 风格：给 3 帧图像 + candidate action + dialogue-act params + terminal realization + concrete execution plan；文本中写明 current stage / intent / BDI 不提供。
- `run_trick6_counterfactual_planning.py` 中 `next_state_ms_row(...)` 对有 transition gold 的 candidate 使用 `build_deliberation_prompt`，该模板会包含 current state summary；对无 transition gold 的 placeholder candidate 从 action prompt 解析 current state 再构造 prompt。

有 gold 样本：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a multimodal sales-guidance agent trained on retail pedagogy. You observe customers in physical retail stores via a streaming camera and decide whether and how to intervene. Always output your reasoning in the structured tag format requested by the user prompt. Do not output free-form prose outside the requested tags."
    },
    {
      "role": "user",
      "content": "<image><image><image>You are observing a customer in a retail store. Below are 3 frames sampled from a streaming camera, in chronological order.\n\n\n\n\n\nUse the frames to infer the customer's current state internally. The current stage, intent, and BDI state are not provided.\n\nConsider one candidate intervention: Elicit_b1166d372e5e\n\nDialogue-act layer for this candidate:\n- act: Elicit\n- params: {'openness': 'open', 'slot': 'need_focus'}\n\nTerminal realization for this candidate:\n- surface_text: 您今天想先看价格、功能，还是适合什么场景？\n- screen: {'action': 'show_choice_bubbles', 'choices': ['价格', '功能', '场景'], 'cta': None}\n- voice_style: curious\n- light: soft_invitation\n\nConcrete execution plan for this candidate:\n- physical action: 智能售货柜通过屏幕、语音、灯效和必要的柜体反馈执行响应。\n- utterance: 您今天想先看价格、功能，还是适合什么场景？\n\nPredict how this candidate intervention will change the customer's state in the next decision step. Output the following fields, in this exact order, each on its own line:\n<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\n- next_stage must be one of: attention, interest, desire, action.\n- risk and benefit must each be one of: low, medium, high.\n- reward must be a number in [-1.00, 1.00] with two decimal places.\n- all textual spans must be a single short clause in English."
    },
    {
      "role": "assistant",
      "content": "<next_stage>interest</next_stage>\n<next_belief>机器关注并理解她在比较，主动帮助理清关注点，信息获取门槛降低。</next_belief>\n<next_desire>更方便地筛选出关键考虑因素，明确自己真正关心的内容（如功能/价格/场景）。</next_desire>\n<next_intention>有动力进一步定位需求，从泛泛兴趣过渡到具体需求探索，准备了解更相关信息。</next_intention>\n<risk>medium</risk>\n<benefit>high</benefit>\n<reward>0.21</reward>"
    }
  ],
  "images": [
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/000.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/001.jpg",
    "/Users/mutsumi/Desktop/WorkSpace/ProactiveIntentWorldModel/data/official/piwm_target_v1/frames/piwm_700/002.jpg"
  ],
  "task": "next_state_prediction",
  "source_id": "target_piwm_700#Elicit_b1166d372e5e",
  "weight": 1.0,
  "loss_weight": 1.0,
  "meta": {
    "parent_state_id": "target_piwm_700",
    "candidate_action": "Elicit_b1166d372e5e",
    "candidate_act": "Elicit",
    "candidate_params": {
      "openness": "open",
      "slot": "need_focus"
    },
    "qa_status": "qa_pending_project_lead_review",
    "human_review_status": "pending_project_lead_review",
    "viewpoint": "target_frontcam"
  }
}
```

无 gold 样本：

```json
{
  "scene_id": "target_piwm_700",
  "candidate_action": "Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e",
  "candidate_act": "Recommend",
  "reason": "stage-conditioned placeholder candidate has no exact transition_modeling gold"
}
```

### 80/107 coverage 来源

- `scripts/piwm_4dim_eval.py:prepare_inputs` 用 `(parent_state_id, candidate_action)` 去 `data/official/piwm_target_v1/transition_modeling.jsonl` 精确匹配。
- 找到匹配的写入 `next_state_covered80.jsonl`。
- 找不到匹配的写入 `next_state_unscored27.jsonl`，reason 是 `stage-conditioned placeholder candidate has no exact transition_modeling gold`。

无 gold candidates 按 act 分布：

```json
{
  "Elicit": 1,
  "Greet": 3,
  "Inform": 4,
  "Recommend": 19
}
```

## Q6：Trick 6 反事实推理流程

### 候选 action 如何枚举

`run_trick6` 从 action row 的 `meta.candidate_action_acts` 取 key 顺序：

```python
    for index, action_row in enumerate(action_rows, start=1):
        mapping = action_row.get("meta", {}).get("candidate_action_acts", {})
        candidates = list(mapping)
        scene_stage = current_stage(action_row, state_index)
        per_candidate: dict[str, Any] = {}
        for candidate in candidates:
            candidate_total += 1
            next_row = next_state_ms_row(action_row, candidate, transition_index, state_index)
            try:
```

### 每个候选 action 的 inference prompt

每个候选用 `next_state_ms_row(action_row, candidate, transition_index, state_index)` 生成 next-state row，然后调用 `generate_one`：

```python
            next_row = next_state_ms_row(action_row, candidate, transition_index, state_index)
            try:
                raw = generate_one(model, processor, next_row, args)
                parsed = parse_deliberation_output(raw.split("\n[recap]", 1)[0].strip())
                reward = reward_fn(scene_stage, parsed)
                candidate_parsed += 1
                per_candidate[candidate] = {
                    "act": mapping.get(candidate),
                    "parse_ok": True,
                    "prediction": raw,
                    "parsed": parsed,
                    "planning_reward": reward,
                    "has_transition_gold": next_row["meta"]["has_transition_gold"],
                }
```

### next_state / reward 如何 parse

```python
            try:
                raw = generate_one(model, processor, next_row, args)
                parsed = parse_deliberation_output(raw.split("\n[recap]", 1)[0].strip())
                reward = reward_fn(scene_stage, parsed)
                candidate_parsed += 1
```

### argmax 公式

```python
def reward_stage_advance(current_stage: str | None, parsed: dict[str, Any]) -> float:
    next_stage = parsed.get("next_aida_stage")
    if current_stage not in STAGE_ORDER or next_stage not in STAGE_ORDER:
        return -math.inf
    current_index = STAGE_ORDER[current_stage]
    next_index = STAGE_ORDER[next_stage]
    if next_index > current_index:
        return 1.0
    if next_index == current_index:
        return 0.0
    return -1.0

def reward_model_score(current_stage: str | None, parsed: dict[str, Any]) -> float:
    value = parsed.get("reward")
    try:
        return float(value)
    except (TypeError, ValueError):
        return reward_stage_advance(current_stage, parsed)

def choose_candidate(candidates: list[str], per_candidate: dict[str, Any]) -> str | None:
    parsed = [candidate for candidate in candidates if per_candidate.get(candidate, {}).get("parse_ok")]
    if not parsed:
        return None
    return max(parsed, key=lambda candidate: (per_candidate[candidate]["planning_reward"], -candidates.index(candidate)))
```

### 0.263 与 0.360 的计算差异

- Reward A raw：`reports/trick6_raw_20260524/trick6_reward_stage_advance.json`
- Reward B raw：`reports/trick6_raw_20260524/trick6_reward_model_score.json`
- Reward A metric：

```json
{
  "macro_f1": 0.2626984126984127,
  "accuracy": 0.3,
  "per_act": {
    "Greet": {
      "precision": 1.0,
      "recall": 0.16666666666666666,
      "f1": 0.2857142857142857,
      "support": 6,
      "pred_count": 1
    },
    "Elicit": {
      "precision": 0.6666666666666666,
      "recall": 0.3333333333333333,
      "f1": 0.4444444444444444,
      "support": 6,
      "pred_count": 3
    },
    "Inform": {
      "precision": 0.5,
      "recall": 0.16666666666666666,
      "f1": 0.25,
      "support": 6,
      "pred_count": 2
    },
    "Recommend": {
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "support": 6,
      "pred_count": 0
    },
    "Hold": {
      "precision": 0.20833333333333334,
      "recall": 0.8333333333333334,
      "f1": 0.33333333333333337,
      "support": 6,
      "pred_count": 24
    }
  },
  "pred_count": {
    "Elicit": 3,
    "Greet": 1,
    "Hold": 24,
    "Inform": 2
  },
  "support": {
    "Elicit": 6,
    "Greet": 6,
    "Hold": 6,
    "Inform": 6,
    "Recommend": 6
  }
}
```

- Reward B metric：

```json
{
  "macro_f1": 0.35988455988455986,
  "accuracy": 0.3333333333333333,
  "per_act": {
    "Greet": {
      "precision": 1.0,
      "recall": 0.16666666666666666,
      "f1": 0.2857142857142857,
      "support": 6,
      "pred_count": 1
    },
    "Elicit": {
      "precision": 0.3333333333333333,
      "recall": 0.3333333333333333,
      "f1": 0.3333333333333333,
      "support": 6,
      "pred_count": 6
    },
    "Inform": {
      "precision": 0.6,
      "recall": 0.5,
      "f1": 0.5454545454545454,
      "support": 6,
      "pred_count": 5
    },
    "Recommend": {
      "precision": 0.6666666666666666,
      "recall": 0.3333333333333333,
      "f1": 0.4444444444444444,
      "support": 6,
      "pred_count": 3
    },
    "Hold": {
      "precision": 0.13333333333333333,
      "recall": 0.3333333333333333,
      "f1": 0.19047619047619044,
      "support": 6,
      "pred_count": 15
    }
  },
  "pred_count": {
    "Elicit": 6,
    "Greet": 1,
    "Hold": 15,
    "Inform": 5,
    "Recommend": 3
  },
  "support": {
    "Elicit": 6,
    "Greet": 6,
    "Hold": 6,
    "Inform": 6,
    "Recommend": 6
  }
}
```

Reward A 用 `next_stage` 相对 current stage 的推进/持平/退步给 `+1/0/-1`；Reward B 优先用模型输出的 `<reward>` 浮点数，缺失时 fallback 到 Reward A。

## PI 关注点候选清单

- `target_user_intent` 的 gold intent label space 只有 4 类：`['compare_value_for_money', 'confirm_choice', 'explore_options', 'no_clear_intent']`；训练 intent label space 有 `['compare_value_for_money', 'confirm_choice', 'explore_options', 'leave_without_purchase', 'negotiate_price', 'request_demonstration', 'seek_reassurance']`。
- 4dim Dim1/Dim2 是同一个 user_intent prompt 与同一条 raw output，不是分别独立问 stage 和 intent。
- Dim3 在 4dim input 文件中使用 “current state not provided” 的 prompt；Trick6 脚本对 covered transition candidate 的 `next_state_ms_row` 分支使用 `build_deliberation_prompt`，模板包含 current state summary。
- Dim3 只有 80/107 个 stage-conditioned candidates 有 transition gold；27 条 unscored 主要是 Recommend placeholder：`{'Elicit': 1, 'Greet': 3, 'Inform': 4, 'Recommend': 19}`。
- 当前 4dim manifest 记录 `stage_conditioned_candidate_total=107`，但现有 Trick 6 raw 记录 `candidate_total=91`。
- 当前 action sample 第一条候选包含 `Recommend_interest_stage_conditioned_target_piwm_700_605fd47cf01e`，但 Trick6 raw 第一条 trace 的第四个候选是 `Inform_053014d173cc`。
- Dim4 主 raw artifact 的 `input_jsonl` 指向 `/root/lanyun-fs/ProactiveIntentWorldModel/data/official/domain_specialization_eval_v2_a3_minimal_20260523/target_frontcam_5act_test_action_selection.server_resolved.jsonl`，4dim prepare input 位于 `reports/4dim_eval_raw_20260524/target_action_selection.jsonl`。
- Trick6 trace 中 stage-conditioned candidate 数是 3-4 个，不是每条都 5 个；示例 `target_piwm_700` 是 4 个候选。
- `parse_action_output` 在 `five_act_only=True` 时允许 Greet/Elicit/Inform/Recommend/Hold，拒绝 Reassure；`eval_ms_swift_checkpoint.py::_action_to_act` 的 prefix 集合仍包含 Reassure，但 action parser valid set 来自 row-level candidates。
- parsed macro F1 与 strict macro F1 的 parse failure 处理不同：parsed 版本通常只纳入 parse 成功样本；strict 版本把 parse failure 作为错误预测写入分母。
