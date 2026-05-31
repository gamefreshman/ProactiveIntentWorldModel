#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="${PIWM_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$REPO_ROOT"
export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"

PY="${PY:-python3}"
MODEL="${MODEL:-/root/lanyun-fs/models/Qwen2.5-VL-7B-Instruct}"
INPUT_JSONL="${INPUT_JSONL:-reports/real_eval_20260525/real_all_scored.jsonl}"
OUT_DIR="${OUT_DIR:-reports/real_eval_20260525/model_runs}"
MAX_PIXELS="${MAX_PIXELS:-1003520}"
IMAGE_LIMIT="${IMAGE_LIMIT:-3}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-256}"
PROGRESS_EVERY="${PROGRESS_EVERY:-5}"

PIWM_CK="${PIWM_CK:-/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/a3_full_targetv2_balanced_3epoch_v1/a3full-20260522-220941-px1003520-ml8192/v0-20260522-220953/checkpoint-500}"
STAGE1_CK="${STAGE1_CK:-/root/lanyun-fs/ProactiveIntentWorldModel/checkpoints/stage1_qwen25vl_7b_a100_2gpu_pathC_symmetry_v1/pathC-20260521-185907-px1003520/v0-20260521-190055/checkpoint-432}"

mkdir -p "$OUT_DIR/logs"

run_eval() {
  local label="$1"
  local checkpoint="${2:-}"
  local gpu="${3:-0}"
  local out="$OUT_DIR/${label}_real_all_scored.json"
  local log="$OUT_DIR/logs/${label}_real_all_scored.log"
  local checkpoint_args=()

  if [[ -n "$checkpoint" ]]; then
    checkpoint_args=(--checkpoint "$checkpoint")
  fi

  echo "[$(date +%F\ %T)] START $label gpu=$gpu"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" scripts/eval_ms_swift_checkpoint.py \
    --model "$MODEL" \
    "${checkpoint_args[@]}" \
    --eval-label "${label}_real_all_scored" \
    --input-jsonl "$INPUT_JSONL" \
    --out "$out" \
    --max-new-tokens "$MAX_NEW_TOKENS" \
    --image-limit "$IMAGE_LIMIT" \
    --max-pixels "$MAX_PIXELS" \
    --progress-every "$PROGRESS_EVERY" \
    > "$log" 2>&1
  echo "[$(date +%F\ %T)] DONE  $label -> $out"
}

run_eval "piwm_main" "$PIWM_CK" "${PIWM_GPU:-0}"
run_eval "customer_state_effect_only" "$STAGE1_CK" "${STAGE1_GPU:-0}"
run_eval "base_qwen25vl7b" "" "${BASE_GPU:-0}"

"$PY" scripts/summarize_real_eval_results.py "$OUT_DIR" --out-md "$OUT_DIR/summary.md" --out-json "$OUT_DIR/summary.json"
