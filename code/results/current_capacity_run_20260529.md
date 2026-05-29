# Current Capacity Run

Generated on 2026-05-29 from EC2 clean no-write runs.

## Configuration

- Shape: 65 independent bundle SQLs per event.
- Storage: TiKV/TiDB only, `TIDB_ISOLATION_READ_ENGINES=tikv,tidb`.
- Query layout: `prod180` hybrid, with pre-agg only for 180d Group A/B/C bundles.
- Read protection: `max_execution_time=500ms`.
- Event mix: 5% hot-key events.
- Event bindings: reused from `results/mixed_traffic_1780092771.json`.
- Writes: disabled with `NO_WRITES=1` because the lean support bundle does not include a usable write thread.
- Report mode: `SUMMARY_ONLY=1` to avoid per-bundle result serialization overhead in the capacity run.

The reused event JSON is a benchmark harness choice, not a production SQL optimization. It skips the pre-test `top_value()` full-table `GROUP BY` used only to find hot keys, and keeps event bindings stable across runs.

## Result Summary

| Run | Achieved eps | Events | >=60/65 by 350ms | >=60/65 by 500ms | 60/65 p95 | 60/65 p99 | Full 65/65 by 500ms | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `mixed_traffic_1780094362.json` | 12.03 | 361 | 357/361 (98.9%) | 358/361 (99.2%) | 184.3 ms | 333.1 ms | 339/361 (93.9%) | stable demo point |
| `mixed_traffic_1780094427.json` | 13.03 | 391 | 29/391 (7.4%) | 40/391 (10.2%) | 2372.5 ms | 3100.2 ms | 24/391 (6.1%) | overloaded |

## 12 eps Detail

- Event latency: p50 170.3 ms, p95 547.9 ms, p99 682.0 ms.
- Score-ready 60/65 completion: p50 121.4 ms, p95 184.3 ms, p99 333.1 ms, max 387.8 ms.
- 60/65 coverage by 500ms: 358/361 events.
- 65/65 completion: p50 164.6 ms, p95 339.3 ms, p99 415.5 ms, max 454.3 ms for events that completed all bundles.
- No connection replacements.

Interpretation: this run satisfies the fallback framing, with 99.2% of events reaching at least 60/65 bundles by 500ms. It is still not perfect full-event latency because hot-key events can have event-level tails above 500ms, but scoring can proceed from 60 bundle results.

## 13 eps Detail

- Event latency: p50 1689.0 ms, p95 3155.5 ms, p99 5461.4 ms.
- Score-ready 60/65 completion: p50 1229.3 ms, p95 2372.5 ms, p99 3100.2 ms.
- 60/65 coverage by 500ms: 40/391 events.
- Queueing became visible: bundle task queue max p95 749.6 ms, p99 1227.7 ms.
- Read pool connection replacements: 10.

Interpretation: 13 eps crosses the current knee. The system can submit and complete 13 eps, but the completion time distribution collapses and no longer meets the 500ms fallback target.

## Current Answer

Current defensible capacity in this environment is approximately **12 events/sec**, or about **780 bundle SQL/sec**.

13 events/sec, about 845 bundle SQL/sec, is not stable under the same configuration.
