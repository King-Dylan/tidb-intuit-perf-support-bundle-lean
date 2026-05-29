#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results

LOG="logs/prod180_correctness_gates_$(date +%Y%m%d_%H%M%S).log"
{
  echo "== Python compile gate =="
  python3 -m py_compile \
    preagg_rollups.py \
    optimized_config.py \
    apply_optimized_indexes.py \
    prod_180d_preagg.py \
    mixed_traffic_test.py \
    validate_prod180_integrity.py \
    spotcheck_prod180_correctness.py

  echo
  echo "== Structural/data coverage gate =="
  python3 -u validate_prod180_integrity.py

  echo
  echo "== Raw vs prod180 exact-result spotcheck =="
  python3 -u spotcheck_prod180_correctness.py

  echo
  echo "ALL PROD180 CORRECTNESS GATES PASSED"
} 2>&1 | tee "$LOG"

echo "WROTE $LOG"
