#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results

# v15 is the full-scale Premium/BYOC build of the winning v12 design.
export INTUIT_PARTITION_GRAIN="${INTUIT_PARTITION_GRAIN:-monthly}"
export INTUIT_DEMO_SCALE="${INTUIT_DEMO_SCALE:-full}"
export INTUIT_RANDOM_SEED="${INTUIT_RANDOM_SEED:-20260512}"
export INTUIT_SETUP_TIFLASH="${INTUIT_SETUP_TIFLASH:-0}"
export INTUIT_LOAD_WRITER_THREADS="${INTUIT_LOAD_WRITER_THREADS:-96}"
export INTUIT_LOAD_BATCH_SIZE="${INTUIT_LOAD_BATCH_SIZE:-10000}"
export INTUIT_LOAD_MAX_PENDING_BATCHES="${INTUIT_LOAD_MAX_PENDING_BATCHES:-512}"
export INTUIT_SEGMENTED_LOAD="${INTUIT_SEGMENTED_LOAD:-1}"
export INTUIT_SEGMENT_WRITER_THREADS="${INTUIT_SEGMENT_WRITER_THREADS:-4}"
export INTUIT_SEGMENT_BATCH_SIZE="${INTUIT_SEGMENT_BATCH_SIZE:-10000}"
export INTUIT_SEGMENT_MAX_PENDING_BATCHES="${INTUIT_SEGMENT_MAX_PENDING_BATCHES:-32}"
export PMT_SEGMENTS="${PMT_SEGMENTS:-16}"
export DEVICE_SEGMENTS="${DEVICE_SEGMENTS:-32}"
export PREAGG_DAILY_WORKERS="${PREAGG_DAILY_WORKERS:-8}"
export START_DAY="${START_DAY:-2025-11-19}"
export END_DAY="${END_DAY:-2026-05-18}"

LOG="logs/v15_full_monthly_premium_build_$(date +%Y%m%d_%H%M%S).log"

{
  echo "Starting v15 full-scale Premium/BYOC build"
  echo "layout=$INTUIT_PARTITION_GRAIN scale=$INTUIT_DEMO_SCALE seed=$INTUIT_RANDOM_SEED"
  echo "loader_threads=$INTUIT_LOAD_WRITER_THREADS batch_size=$INTUIT_LOAD_BATCH_SIZE max_pending=$INTUIT_LOAD_MAX_PENDING_BATCHES"
  echo "segmented_load=$INTUIT_SEGMENTED_LOAD segment_writer_threads=$INTUIT_SEGMENT_WRITER_THREADS pmt_segments=$PMT_SEGMENTS device_segments=$DEVICE_SEGMENTS"
  echo "preagg_workers=$PREAGG_DAILY_WORKERS preagg_window=$START_DAY..$END_DAY"
  echo
  echo "WARNING: setup_schema.py drops/recreates pmt_txn_fact and deviceprofile_fact in the configured database."

  python3 setup_schema.py
  if [[ "$INTUIT_SEGMENTED_LOAD" == "1" ]]; then
    ./run_segmented_full_load.sh
  else
    ./run_fast_full_load.sh
  fi
  python3 enable_tiflash.py
  python3 analyze_tables.py
  python3 verify_partitioning.py
  python3 profile_validation.py --output "results/v15_data_shape_validation_monthly_full.md"
  ./run_prod_180d_preagg_parallel.sh

  echo
  echo "v15 full monthly build complete."
  echo "Next: delete/restore if you want a cleaner cluster/cache state, then run:"
  echo "  ./run_v15_prod180_benchmark.sh 3 300"
} 2>&1 | tee "$LOG"
