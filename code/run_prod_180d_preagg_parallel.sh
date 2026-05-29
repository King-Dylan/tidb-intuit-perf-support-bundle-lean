#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

# Defaults match the benchmark event window. Override when using a different
# reference-date event set.
START_DAY="${START_DAY:-2025-11-19}"
END_DAY="${END_DAY:-2026-05-18}"
WORKERS="${PREAGG_DAILY_WORKERS:-4}"
LOG_DIR="logs/prod_180d_preagg_parallel_${START_DAY}_${END_DAY}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

echo "Building production-style 180d pre-agg tables in parallel"
echo "start_day=$START_DAY end_day=$END_DAY workers=$WORKERS log_dir=$LOG_DIR"

python3 -u prod_180d_preagg.py drop --execute 2>&1 | tee "$LOG_DIR/00_drop.log"
python3 -u prod_180d_preagg.py create --execute 2>&1 | tee "$LOG_DIR/01_create.log"

python3 - "$START_DAY" "$END_DAY" > "$LOG_DIR/days.txt" <<'PY'
from datetime import date, timedelta
import sys

start = date.fromisoformat(sys.argv[1])
end = date.fromisoformat(sys.argv[2])
day = start
while day <= end:
    print(day.isoformat())
    day += timedelta(days=1)
PY

while IFS= read -r day; do
  (
    echo "### Building day $day"
    python3 -u prod_180d_preagg.py build --day "$day" --execute
    echo "### Completed day $day"
  ) > "$LOG_DIR/day_${day}.log" 2>&1 &

  while (( "$(jobs -pr | wc -l | tr -d ' ')" >= WORKERS )); do
    sleep 5
  done
done < "$LOG_DIR/days.txt"

wait

python3 -u prod_180d_preagg.py analyze --execute 2>&1 | tee "$LOG_DIR/99_analyze.log"

echo "Done: $LOG_DIR"
