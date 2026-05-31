# Exhaustive Runtime Rewrite Round

Generated from the EC2 benchmark environment on 2026-05-31.

## Scope

This round tested semantics-preserving SQL rewrites across all 65 event bundle
queries. Each candidate had to return the same normalized columns and row values
as the current optimized SQL before it could be considered for EXPLAIN ANALYZE
comparison.

Candidate classes tested:

- CASE pruning via Group A dimension rollup.
- Predicate pushdown via filtered scalar subqueries.
- DISTINCT/session tuning with `tidb_opt_distinct_agg_push_down`.
- Group C `LEFT JOIN` to `JOIN` / device-first join order.
- Repeated numeric score cast projection.
- Null-binding app-layer skip, preserving SQL semantics for `col = NULL`.

Full A/B artifact:

- `code/results/exhaustive_rewrite_all65.md`
- `code/results/exhaustive_rewrite_all65.json`

## Accepted Single-SQL Candidates

The exhaustive per-bundle run found 8 single-SQL candidates that were faster in
isolation:

| Bundle | Rewrite | Current best | Candidate best | Gain |
| --- | --- | ---: | ---: | ---: |
| `group_a_bundle_006` | Group A dimension rollup | 491.6 ms | 121.4 ms | 75.3% |
| `group_a_bundle_012` | Group A dimension rollup | 120.6 ms | 30.8 ms | 74.4% |
| `group_a_bundle_002` | Group A dimension rollup | 323.9 ms | 99.0 ms | 69.4% |
| `group_c_bundle_002` | Device-first join | 351.6 ms | 188.6 ms | 46.4% |
| `group_c_bundle_017` | Device-first join | 286.8 ms | 213.1 ms | 25.7% |
| `group_c_bundle_016` | Device-first join | 321.3 ms | 242.7 ms | 24.5% |
| `group_c_bundle_014` | Inner join | 167.2 ms | 146.3 ms | 12.5% |
| `group_c_bundle_003` | Device-first join | 165.6 ms | 146.6 ms | 11.5% |

## Full Fan-Out Decision

The full 65-way event fan-out benchmark overrode the single-query result for
Group C. The Group C join rewrites improved selected isolated plans but hurt the
full-event 350 ms path under concurrent fan-out, so they are left as explicit
environment-variable experiments and are not enabled by default.

Final defaults keep only the new Group A dimension rollups:

- `group_a_bundle_002`
- `group_a_bundle_006`
- `group_a_bundle_012`

Existing defaults retained:

- `group_a_bundle_010`
- `group_a_bundle_014`
- targeted TiFlash MPP for `group_b_bundle_012` and `group_c_bundle_018`
- prod180 pre-aggregation for selected 180d bundles

## 12 eps Validation

All runs used the same reused event sample, no writes, 600 read connections, 600
bundle workers, 128 event workers, and prod180 hybrid mode.

| Run | JSON | 65/65 <=350 | 65/65 <=500 | Full 65/65 p95 | Score-ready 60/65 p95 | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Control old shape | `mixed_traffic_1780202931.json` | 320/361 (88.6%) | 332/361 (92.0%) | 338.6 ms | 237.0 ms | A010/A014 only |
| A-only rewrite | `mixed_traffic_1780202997.json` | 332/361 (92.0%) | 333/361 (92.2%) | 316.9 ms | 250.3 ms | Best full 65/65 result |
| C-only rewrite | `mixed_traffic_1780203060.json` | 316/361 (87.5%) | 332/361 (92.0%) | 349.3 ms | 221.7 ms | Rejected as default |
| All accepted rewrites | `mixed_traffic_1780202858.json` | 300/360 (83.3%) | 326/360 (90.6%) | 370.3 ms | 290.4 ms | Rejected as default |
| Final default | `mixed_traffic_1780203146.json` | 324/360 (90.0%) | 332/360 (92.2%) | 327.0 ms | 261.2 ms | Default code path after this round |
| Final + 60/65 score-ready | `mixed_traffic_1780203213.json` | 0/361 full 65/65 by design | 0/361 full 65/65 by design | N/A | 454.8 ms | Event p95 466.1 ms, p99 492.4 ms |

## Remaining Bottlenecks

The final full-wait run still has residual hot-key tail, mostly:

- `group_c_bundle_018` and `group_b_bundle_012` on hot `true_ip`.
- prod180 helper paths including `group_b_bundle_020`, `group_b_bundle_018`,
  `group_b_bundle_019`, `group_c_bundle_023`, and `group_c_bundle_025`.
- Group A card/merchant/routing bundles under concurrent score-ready mode.

The scalar-subquery rewrite was broadly rejected: it moves predicates into WHERE
clauses, but the repeated independent scans cost more than the CASE savings in
fan-out traffic.
