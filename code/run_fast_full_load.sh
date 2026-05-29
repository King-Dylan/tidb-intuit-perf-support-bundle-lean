#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

: "${INTUIT_DEMO_SCALE:=tenpct}"
: "${INTUIT_JOIN_MODEL:=one_to_one}"
: "${INTUIT_LOAD_WRITER_THREADS:=64}"
: "${INTUIT_LOAD_BATCH_SIZE:=10000}"
: "${INTUIT_LOAD_MAX_PENDING_BATCHES:=256}"
: "${INTUIT_RANDOM_SEED:=20260512}"

export INTUIT_DEMO_SCALE
export INTUIT_JOIN_MODEL
export INTUIT_LOAD_WRITER_THREADS
export INTUIT_LOAD_BATCH_SIZE
export INTUIT_LOAD_MAX_PENDING_BATCHES
export INTUIT_RANDOM_SEED

LOG="logs/load_data_fast_${INTUIT_DEMO_SCALE}_$(date +%Y%m%d_%H%M%S).log"

echo "Starting fast v12 load"
echo "scale=$INTUIT_DEMO_SCALE join_model=$INTUIT_JOIN_MODEL random_seed=$INTUIT_RANDOM_SEED writer_threads=$INTUIT_LOAD_WRITER_THREADS batch_size=$INTUIT_LOAD_BATCH_SIZE max_pending_batches=$INTUIT_LOAD_MAX_PENDING_BATCHES log=$LOG"

python3 -u load_data.py "$@" 2>&1 | tee "$LOG"
