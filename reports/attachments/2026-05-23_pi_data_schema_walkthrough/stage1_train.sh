#!/usr/bin/env bash
set -euo pipefail

# Stage-1 User Intent World Modeling SFT launcher.
#
# Target hardware: 8 x RTX 4090 24GB.
# Expected runtime: about 4-6 hours for the current 2309-example train split,
# depending on storage throughput, image decoding, and ms-swift version.
# This script is configuration only by default; pass --run to launch training.

RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)
      RUN=0
      ;;
    --run)
      RUN=1
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

MODEL_ID="${MODEL_ID:-Qwen/Qwen2.5-VL-7B-Instruct}"
SWIFT_BIN="${SWIFT_BIN:-swift}"
NPROC_PER_NODE="${NPROC_PER_NODE:-8}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"

TRAIN_USER="${TRAIN_USER:-data/official/ms_swift/piwm_train_stage1_user_intent_train_v1.jsonl}"
TRAIN_NEXT="${TRAIN_NEXT:-data/official/ms_swift/piwm_train_stage1_next_state_prediction_train_v1.jsonl}"
VAL_USER="${VAL_USER:-data/official/ms_swift/piwm_train_stage1_user_intent_val_v1.jsonl}"
VAL_NEXT="${VAL_NEXT:-data/official/ms_swift/piwm_train_stage1_next_state_prediction_val_v1.jsonl}"

OUTPUT_DIR="${OUTPUT_DIR:-checkpoints/stage1_qwen25vl_7b_v1}"
LOG_DIR="${LOG_DIR:-logs/stage1_qwen25vl_7b_v1}"
EPOCHS="${EPOCHS:-3}"
LR="${LR:-2e-5}"
PER_DEVICE_BATCH_SIZE="${PER_DEVICE_BATCH_SIZE:-4}"
GRAD_ACCUM_STEPS="${GRAD_ACCUM_STEPS:-2}"
MAX_FRAMES="${MAX_FRAMES:-3}"
MAX_LENGTH="${MAX_LENGTH:-4096}"
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-32}"
# ms-swift 4.1.3 uses all-linear as the broad LoRA target-module setting.
# Override TARGET_MODULES=auto only in environments where that alias is supported.
TARGET_MODULES="${TARGET_MODULES:-all-linear}"
ACT_BALANCING="${ACT_BALANCING:-none}"

for required in "$TRAIN_USER" "$TRAIN_NEXT" "$VAL_USER" "$VAL_NEXT"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing required Stage-1 data file: $required" >&2
    echo "Run: python3 -m scripts.build_stage1_general_split" >&2
    exit 1
  fi
done

DATASET=("$TRAIN_USER" "$TRAIN_NEXT")
VAL_DATASET=("$VAL_USER" "$VAL_NEXT")

CMD=(
  "$SWIFT_BIN" sft
  --model "$MODEL_ID"
  --dataset "${DATASET[@]}"
  --val_dataset "${VAL_DATASET[@]}"
  --output_dir "$OUTPUT_DIR"
  --tuner_type lora
  --lora_rank "$LORA_RANK"
  --lora_alpha "$LORA_ALPHA"
  --target_modules "$TARGET_MODULES"
  --learning_rate "$LR"
  --num_train_epochs "$EPOCHS"
  --per_device_train_batch_size "$PER_DEVICE_BATCH_SIZE"
  --per_device_eval_batch_size "$PER_DEVICE_BATCH_SIZE"
  --gradient_accumulation_steps "$GRAD_ACCUM_STEPS"
  --max_length "$MAX_LENGTH"
  --torch_dtype bfloat16
  --gradient_checkpointing true
  --logging_dir "$LOG_DIR"
)

echo "Stage-1 ms-swift launch configuration:"
echo "  MODEL_ID=$MODEL_ID"
echo "  SWIFT_BIN=$SWIFT_BIN"
echo "  CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "  NPROC_PER_NODE=$NPROC_PER_NODE"
echo "  ACT_BALANCING=$ACT_BALANCING (Stage-1 has no action-selection balancing)"
echo "  MAX_FRAMES=$MAX_FRAMES (enforced by dataset rows; not passed as a ms-swift CLI arg)"
echo "  Train: ${DATASET[*]}"
echo "  Val:   ${VAL_DATASET[*]}"
echo "  Output checkpoint dir: $OUTPUT_DIR"
echo "  Log dir: $LOG_DIR"
echo
echo "Full command:"
printf ' %q' CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" NPROC_PER_NODE="$NPROC_PER_NODE" "${CMD[@]}"
printf '\n'

if [[ "$RUN" != "1" ]]; then
  echo
  echo "Dry-run only. Re-run with --run to start training."
  exit 0
fi

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"
export CUDA_VISIBLE_DEVICES
export NPROC_PER_NODE
"${CMD[@]}" 2>&1 | tee "$LOG_DIR/train.log"
