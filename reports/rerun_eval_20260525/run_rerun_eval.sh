#!/usr/bin/env bash
set -Eeuo pipefail
cd /root/lanyun-fs/ProactiveIntentWorldModel
export PYTHONPATH=/root/lanyun-fs/ProactiveIntentWorldModel:${PYTHONPATH:-}
PY=/root/lanyun-fs/venvs/piwm-train-fast/bin/python
MODEL=/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct
OUT=reports/rerun_eval_20260525
USER60=$OUT/user_intent_target30_general30_seed42.archive_resolved.server.jsonl
ACTION30=reports/4dim_eval_raw_20260524/target_action_selection.server.jsonl
COVERED80=reports/4dim_eval_raw_20260524/next_state_covered80.server.jsonl
TRANS=data/official/piwm_target_v1/transition_modeling.jsonl
PIWM_CK=/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500
STAGE1_CK=/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432
mkdir -p "$OUT/logs"
log(){ echo "[$(date +%F %T)] $*" | tee -a "$OUT/logs/run_rerun_eval.master.log"; }
run_lora(){
  local label=$1 ckpt=$2 gpu=$3
  export CUDA_VISIBLE_DEVICES=$gpu
  log "START ${label} on GPU ${gpu}"
  $PY scripts/eval_ms_swift_checkpoint.py \
    --model "$MODEL" \
    --checkpoint "$ckpt" \
    --eval-label "${label}_user_intent_60" \
    --input-jsonl "$USER60" \
    --out "$OUT/${label}_user_intent_60.json" \
    --max-new-tokens 256 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_user_intent_60.log" 2>&1
  log "DONE ${label} user_intent"
  $PY scripts/run_trick6_counterfactual_planning.py \
    --mode dim3 \
    --model "$MODEL" \
    --checkpoint "$ckpt" \
    --covered-jsonl "$COVERED80" \
    --action-jsonl "$ACTION30" \
    --transition-jsonl "$TRANS" \
    --out "$OUT/${label}_dim3_current_state.json" \
    --max-new-tokens 384 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_dim3_current_state.log" 2>&1
  log "DONE ${label} dim3"
  $PY scripts/run_trick6_counterfactual_planning.py \
    --mode trick6 --reward-mode stage_advance \
    --model "$MODEL" \
    --checkpoint "$ckpt" \
    --action-jsonl "$ACTION30" \
    --transition-jsonl "$TRANS" \
    --out "$OUT/${label}_trick6_rewardA_stage_advance.json" \
    --max-new-tokens 384 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_trick6_rewardA_stage_advance.log" 2>&1
  log "DONE ${label} trick6 rewardA"
  $PY scripts/run_trick6_counterfactual_planning.py \
    --mode trick6 --reward-mode model_score \
    --model "$MODEL" \
    --checkpoint "$ckpt" \
    --action-jsonl "$ACTION30" \
    --transition-jsonl "$TRANS" \
    --out "$OUT/${label}_trick6_rewardB_model_score.json" \
    --max-new-tokens 384 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_trick6_rewardB_model_score.log" 2>&1
  log "DONE ${label} trick6 rewardB"
  log "FINISH ${label}"
}
run_base(){
  local label=base_qwen25vl7b gpu=$1
  export CUDA_VISIBLE_DEVICES=$gpu
  log "START ${label} on GPU ${gpu}"
  $PY scripts/eval_ms_swift_checkpoint.py \
    --model "$MODEL" \
    --eval-label "${label}_user_intent_60" \
    --input-jsonl "$USER60" \
    --out "$OUT/${label}_user_intent_60.json" \
    --max-new-tokens 256 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_user_intent_60.log" 2>&1
  log "DONE ${label} user_intent"
  $PY scripts/run_trick6_counterfactual_planning.py \
    --mode dim3 \
    --model "$MODEL" \
    --covered-jsonl "$COVERED80" \
    --action-jsonl "$ACTION30" \
    --transition-jsonl "$TRANS" \
    --out "$OUT/${label}_dim3_current_state.json" \
    --max-new-tokens 384 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_dim3_current_state.log" 2>&1
  log "DONE ${label} dim3"
  $PY scripts/run_trick6_counterfactual_planning.py \
    --mode trick6 --reward-mode stage_advance \
    --model "$MODEL" \
    --action-jsonl "$ACTION30" \
    --transition-jsonl "$TRANS" \
    --out "$OUT/${label}_trick6_rewardA_stage_advance.json" \
    --max-new-tokens 384 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_trick6_rewardA_stage_advance.log" 2>&1
  log "DONE ${label} trick6 rewardA"
  $PY scripts/run_trick6_counterfactual_planning.py \
    --mode trick6 --reward-mode model_score \
    --model "$MODEL" \
    --action-jsonl "$ACTION30" \
    --transition-jsonl "$TRANS" \
    --out "$OUT/${label}_trick6_rewardB_model_score.json" \
    --max-new-tokens 384 --image-limit 3 --max-pixels 1003520 --progress-every 5 \
    > "$OUT/logs/${label}_trick6_rewardB_model_score.log" 2>&1
  log "DONE ${label} trick6 rewardB"
  log "FINISH ${label}"
}
log "RERUN EVAL LAUNCH five-act=Greet/Elicit/Inform/Recommend/Hold"
run_lora piwm_main "$PIWM_CK" 0 &
PID0=$!
run_lora customer_state_effect_only "$STAGE1_CK" 1 &
PID1=$!
wait $PID0
wait $PID1
run_base 0
log "ALL DONE"
