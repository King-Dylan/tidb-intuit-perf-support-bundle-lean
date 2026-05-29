#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

: "${INTUIT_DEMO_SCALE:=full}"
: "${INTUIT_JOIN_MODEL:=one_to_one}"
: "${INTUIT_RANDOM_SEED:=20260512}"
: "${INTUIT_SEGMENT_WRITER_THREADS:=4}"
: "${INTUIT_SEGMENT_BATCH_SIZE:=10000}"
: "${INTUIT_SEGMENT_MAX_PENDING_BATCHES:=32}"
: "${PMT_SEGMENTS:=16}"
: "${DEVICE_SEGMENTS:=32}"
: "${INTUIT_SEGMENT_TABLES:=pmt,device}"

PMT_ROWS=83461494
DEVICE_ROWS=365744830
RUN_ID="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="logs/segmented_full_load_${RUN_ID}"
mkdir -p "$LOG_DIR"

echo "Starting segmented full load"
echo "scale=$INTUIT_DEMO_SCALE join_model=$INTUIT_JOIN_MODEL seed=$INTUIT_RANDOM_SEED"
echo "segment_writer_threads=$INTUIT_SEGMENT_WRITER_THREADS batch_size=$INTUIT_SEGMENT_BATCH_SIZE max_pending=$INTUIT_SEGMENT_MAX_PENDING_BATCHES"
echo "pmt_segments=$PMT_SEGMENTS device_segments=$DEVICE_SEGMENTS tables=$INTUIT_SEGMENT_TABLES log_dir=$LOG_DIR"

run_table_segments() {
  local table="$1"
  local total_rows="$2"
  local segments="$3"
  local base=$(( total_rows / segments ))
  local rem=$(( total_rows % segments ))

  echo
  echo "Loading $table rows=$total_rows segments=$segments"
  local pids=()
  local logs=()
  for ((seg=0; seg<segments; seg++)); do
    local count="$base"
    if (( seg < rem )); then
      count=$(( count + 1 ))
    fi
    local start=$(( seg * base + (seg < rem ? seg : rem) ))
    local log="$LOG_DIR/${table}_seg$(printf '%03d' "$seg")_${start}_${count}.log"
    (
      echo "### $table segment=$seg start=$start count=$count"
      INTUIT_DEMO_SCALE="$INTUIT_DEMO_SCALE" \
      INTUIT_JOIN_MODEL="$INTUIT_JOIN_MODEL" \
      INTUIT_RANDOM_SEED="$INTUIT_RANDOM_SEED" \
      INTUIT_LOAD_WRITER_THREADS="$INTUIT_SEGMENT_WRITER_THREADS" \
      INTUIT_LOAD_BATCH_SIZE="$INTUIT_SEGMENT_BATCH_SIZE" \
      INTUIT_LOAD_MAX_PENDING_BATCHES="$INTUIT_SEGMENT_MAX_PENDING_BATCHES" \
      python3 -u load_data.py --table "$table" --start-index "$start" --row-count "$count" --skip-verify-counts
      echo "### completed $table segment=$seg"
    ) > "$log" 2>&1 &
    pids+=("$!")
    logs+=("$log")
  done

  local failures=0
  for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
      echo "ERROR: $table segment failed. log=${logs[$i]}"
      tail -n 40 "${logs[$i]}" || true
      failures=$((failures + 1))
    fi
  done
  if (( failures > 0 )); then
    echo "ERROR: $failures $table segment(s) failed; aborting segmented load."
    return 1
  fi
  echo "Completed $table segmented load"
}

if [[ ",$INTUIT_SEGMENT_TABLES," == *",pmt,"* ]]; then
  run_table_segments pmt "$PMT_ROWS" "$PMT_SEGMENTS"
fi
if [[ ",$INTUIT_SEGMENT_TABLES," == *",device,"* ]]; then
  run_table_segments device "$DEVICE_ROWS" "$DEVICE_SEGMENTS"
fi

echo
echo "Segmented full load complete: $LOG_DIR"
