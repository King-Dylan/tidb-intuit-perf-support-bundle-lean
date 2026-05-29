# TiDB Slow Query Optimization Summary

Generated: 2026-05-28 23:30 PT

## Test Setup

- Source slow list: `results/slow_bundles_post_index_3eps_60s.csv`
- Source traffic JSON: `results/mixed_traffic_1780029697.json`
- Read engines: `tikv,tidb` only; TiFlash excluded by session
- CTE materialization: `tidb_opt_force_inline_cte=0`
- Main post-patch plan report: `results/final_post_patch_problem_bundle_plans.md`
- Residual unresolved SQL report: `results/unoptimized_residual_sql_report.md`

## Changes Kept

1. Kept the three payment covering join indexes:
   - `idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)`
   - `idx_pmt_card_c_join_cov(card_holder_number_sha512, event_date, parsed_interaction_id, transaction_type)`
   - `idx_pmt_routing_acct_c_join_cov(check_bank_routing_number, check_bank_account_number_sha512, event_date, parsed_interaction_id, transaction_type)`
2. Rewrote selected constant-key runtime bundles to remove redundant `GROUP BY key` and use `HAVING COUNT(*) > 0`.
3. Rewrote prod180 distinct-only queries to materialize one raw cutoff boundary and unpivot distinct values.
4. Rewrote prod180 mixed Group C rollup+distinct queries, especially `group_c_bundle_022`, to share one `raw_boundary` CTE instead of running repeated scalar raw subqueries.
5. Added optional session knobs to the test pool: `INTUIT_HASHAGG_FINAL_CONCURRENCY` and `INTUIT_HASHAGG_PARTIAL_CONCURRENCY`.

## Representative Results

| Bundle | Before signal | After EXPLAIN ANALYZE | Optimization | Status |
| --- | ---: | ---: | --- | --- |
| `group_a_bundle_010` | timed out at 500ms; baseline test 744.8ms | 455.9ms | covering index + no redundant GROUP BY | under 500ms, still >350ms |
| `group_a_bundle_006` | timed out in mixed run | 146.6ms | existing covering index; no extra index needed | fixed |
| `group_a_bundle_014` | 393.6ms hot routing | 309.0ms | no redundant GROUP BY | fixed |
| `group_a_bundle_008` | 439.1ms hot merchant | 101.9ms | no redundant GROUP BY | fixed |
| `group_b_bundle_008` | 380.9ms | 112.1ms | no redundant GROUP BY | fixed |
| `group_b_bundle_012` | 515.3ms hot true_ip | 527.0ms in final report; best repeat ~500ms | no redundant GROUP BY; hashagg variants tested | borderline |
| `group_c_bundle_007` | context deadline sample | 102.3ms | merchant join covering index + no redundant GROUP BY | fixed |
| `group_c_bundle_011` | 414.9ms representative | 198.2ms | no redundant GROUP BY | fixed |
| `group_c_bundle_014` | context canceled sample | 137.3ms | merchant join covering index + no redundant GROUP BY | fixed |
| `group_c_bundle_018` | context canceled; baseline repeat 1989.2ms | repeat verification 366-442ms; full report had one noisy 777.1ms | no redundant GROUP BY; distinct pushdown tested but not required consistently | under 500ms on repeat, watch |
| `group_c_bundle_021` | context deadline sample; baseline 318.3ms | 188.8ms | merchant join covering index + no redundant GROUP BY | fixed |
| `group_c_bundle_022` | scalar-subquery shape 840ms+ / context deadline | 181.9ms | mixed rollup+distinct `raw_boundary` CTE | fixed |
| `group_c_bundle_025` | memory/error under old TiFlash/scalar path | 180.3ms | distinct-only `raw_boundary` CTE, TiKV-only | fixed |
| `group_b_bundle_018` | context deadline; scans 767,762 helper rows | 709.5ms | CTE raw boundary, pivot/hashagg variants tested | unresolved |
| `group_b_bundle_020` | context deadline; scans 1,559,443 helper rows | 1224.8ms | CTE raw boundary, pivot/hashagg variants tested | unresolved |

## Residual Root Cause

`group_b_bundle_018` and `group_b_bundle_020` are already covering-index reads on `group_b_180d_daily_distinct`. The remaining cost is exact `COUNT(DISTINCT)` over very large helper ranges:

- `group_b_bundle_018`: 767,762 helper rows, root `HashAgg` around 35 MB
- `group_b_bundle_020`: 1,559,443 helper rows, root `HashAgg` around 57 MB

I did not create another helper-table index because the current primary key already matches `(bundle_id, template_id, key1, key2, event_day, distinct_value)` and the rows read are real matching rows, not table lookups. A second index on the 2.5B-row helper table would be expensive and would not reduce the exact-distinct input cardinality.

## Manual Follow-up Candidates

1. Product/metric change: approximate distinct, capped distinct, or precomputed rolling-window distincts for B 180d hot keys.
2. Storage shape change: separate helper tables per `(bundle_id, template_id)` or a summary table keyed by hot keys if exactness must remain.
3. Query scheduling change: run B 180d exact distinct outside the 500ms critical path or return it asynchronously.
