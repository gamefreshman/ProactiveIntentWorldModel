第一行自检：5-act = Greet/Elicit/Inform/Recommend/Hold；本评估只看 Stage-1 next_state_prediction，不改 5-act。

# Base Qwen2.5-VL next_state quick zero-shot eval

## 结论

未 SFT 的 Qwen2.5-VL-7B-Instruct 在 30 条 Path-C next_state 快评估上表现很弱。严格解析下 next-stage macro F1 只有 `0.071`；用宽松解析尽量排除格式问题后也只有 `0.071`。这说明 Stage-1 SFT 至少不是多余的，base model 不能直接完成这个反事实 transition 任务。

## 评估设置

| Item | Value |
|---|---|
| model | `/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct` |
| checkpoint | none, base model zero-shot |
| input | `reports/2026-05-24_zero_shot_next_state_quick30_server_input.jsonl` |
| n | 30 next_state_prediction rows |
| image frames | 3 frames, max_pixels=501760 |
| GPU use | single A100, about 80 seconds generation; GPUs free after run |
| input sha256 | `012204206061f4a43a9b47daf4899db5d46bb1a4ec425359f4cbbd63db5a87d7` |
| raw output sha256 | `228855b5ef17f70d3a3593f569ee1d622676617d4df50b4f56d5d2eec067ec7a` |

## 格式问题和内容评分分开看

| Metric | Strict parser | Tolerant/content-first parser |
|---|---:|---:|
| parse / recoverable rows | 21/30 = 0.700 | 27/30 = 0.900 |
| next_stage accuracy | 0.048 | 0.074 |
| next_stage macro F1 | 0.071 | 0.071 |
| risk macro F1 | - | 0.267 |
| benefit macro F1 | - | 0.154 |
| reward MAE | - | 0.376 (27 parsed rewards) |

说明：tolerant parser 会接受正确 tag，也会从自由文本里找 stage/risk/benefit/reward，目的是尽量不把“格式没跟上”误算成“完全不会”。

## next_stage 分布

| Stage | Gold count | Pred count tolerant | F1 tolerant |
|---|---:|---:|---:|
| `attention` | 7 | 7 | 0.286 |
| `interest` | 4 | 20 | 0.000 |
| `desire` | 10 | 0 | 0.000 |
| `action` | 6 | 0 | 0.000 |

## 代表错误

- `piwm_0b0d31c38b#Elicit_b1166d372e5e` parse_ok=True, gold=`desire`, pred=`interest`  
  output: `<next_stage>interest</next_stage>\n<next_belief>customer is interested in phone features</next_belief>\n<next_desire>customer wants more information about phone features</next_desire>\n<next_intention>customer will ask about phone features</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.50</reward>`
- `piwm_0b0d31c38b#Inform_5ff00ba15ca5` parse_ok=True, gold=`desire`, pred=`interest`  
  output: `<next_stage>interest</next_stage>\n<next_belief>customer is interested in the product details</next_belief>\n<next_desire>customer wants more information about the product</next_desire>\n<next_intention>customer will ask for more details about the product</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.75</reward>`
- `piwm_0b0d31c38b#Hold_eda24b4bb712` parse_ok=False, gold=`interest`, pred=`attention`  
  output: `<next_stage>...</next_stage>\n<next_belief>...</next_belief>\n<next_desire>...</next_desire>\n<next_intention>...</next_intention>\n<risk>...</risk>\n<benefit>...</benefit>\n<reward>...</reward>\n\nattention\nThe customer is looking at the phone, indicating they are interested in it.\nlow\nmedium\n0.50`
- `piwm_0b0d31c38b#Recommend_8d7f8993e333` parse_ok=True, gold=`attention`, pred=`interest`  
  output: `<next_stage>interest</next_stage>\n<next_belief>customer is interested in the phone</next_belief>\n<next_desire>customer wants more information about the phone</next_desire>\n<next_intention>customer will ask for more details about the phone</next_intention>\n<risk>low</risk>\n<benefit>medium</benefit>\n<reward>0.50</reward>`

## 判断

- 这次只跑了 30 条，目的是低成本 sanity check，不占主训练资源；它不是正式论文表格。
- 即便用宽松解析，base model 仍明显低于可用水平，主要偏向输出 `interest`，也经常把 reward/risk/benefit 模板化。
- 因此，Stage-1 SFT 的必要性是有证据的：没有 SFT 的模型不能可靠执行 action-conditioned next-state prediction。
- 后续如果要正式入论文，建议等主训练空窗时对完整 185 条 next_state eval 跑同样 zero-shot，并和 Path C checkpoint 同表比较。
