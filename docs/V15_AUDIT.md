# v15 Full-Scale Readiness Audit

## Status

v15 is ready to configure against the Premium/BYOC database and start the full monthly + 180d pre-agg build.

Remote EC2 compile/shell validation passed on:

```text
/home/ec2-user/intuit-demo-v15
```

Validated files:

```text
mixed_traffic_test.py
prod_180d_preagg.py
setup_schema.py
load_data.py
run_final_mixed_preagg.sh
run_v15_prod180_benchmark.sh
run_v15_full_monthly_premium_build.sh
run_prod_180d_preagg_parallel.sh
```

## Critical Fixes Added For 1000 eps

- Unique-event mode is now supported and enabled by default in `run_v15_prod180_benchmark.sh`.
- Event sample size now scales from requested `READ_RATE * DURATION`.
- The benchmark now fails early if unique-event sampling is too small, instead of silently replaying the same events.
- Event execution uses a bounded shared event worker pool instead of one new thread per event.
- Bundle execution uses a bounded shared bundle worker pool instead of creating a new 65-thread pool for every event.
- `MAX_PENDING_EVENTS` applies backpressure so an overloaded run reports lower achieved EPS instead of OOMing the client.
- Runs at `>=100 eps` default to `SUMMARY_ONLY=1`, avoiding multi-GB result JSONs.
- Summary-only mode still prints Henry/Andrew coverage and bundle return-time histogram.
- Output records achieved read rate, worker sizing, summary-only mode, and reader backpressure stats.

## Design Guardrails

- Full build uses monthly partitioning, no clustering.
- Base tables and six 180d pre-agg tables default to `SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3`.
- Group C runtime and rollup paths keep date filters on both sides of the join.
- Runtime benchmark uses optimizer default engine choice.
- `READ_MAX_EXECUTION_TIME_MS=500` remains the customer timeout model.
- Full build runs `ANALYZE TABLE` after base load and after pre-agg table build.
- Full load defaults to segmented mode: multiple range-based loader processes
  per table, each with a small writer pool. This keeps row generation from
  becoming a single-core bottleneck while preserving deterministic join keys.

## Recommended Run Order

1. Configure Premium/BYOC database credentials in `/home/ec2-user/intuit-demo-v15/.db_config.json`.
2. Run `./run_v15_full_monthly_premium_build.sh`.
3. Delete/restore the cluster if we want a cleaner cluster/cache state before benchmark.
4. Run `./run_v15_prod180_benchmark.sh 3 300`.
5. Ramp: `10`, `25`, `50`, `100` eps.
6. Only try `200`, `500`, `1000` eps if achieved EPS and tail latency are healthy.

## Remaining Risk

- A single EC2 load generator might become the bottleneck before TiDB does, especially at 1000 eps / 65,000 bundle executions per second.
- Very high `POOL_SIZE` values can stress TiProxy/TiDB connection handling. If achieved EPS is low, check client CPU, connection errors, TiProxy/TiDB connection limits, and backpressure stats before blaming query performance.
- Summary-only high-rate runs are intentionally lighter on per-bundle detail. Use lower-rate detailed runs when we need exact slow-bundle CSV/Markdown output.
