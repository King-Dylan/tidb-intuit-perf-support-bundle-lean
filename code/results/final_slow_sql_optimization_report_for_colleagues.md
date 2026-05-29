# Final Slow SQL Optimization Report for Colleagues

- Generated: `2026-05-29T00:23:56`
- Source full before/after evidence: `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/final_before_after_optimization_report.md`
- Source residual attempt matrix: `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/residual_group_b_optimization_attempts.json`, `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/residual_group_b_followup_attempts.json`

This report keeps the complete before/after SQL and `EXPLAIN ANALYZE` evidence, then appends the extra residual experiments for the two SQLs that still need manual data-model optimization.

## Permanent Changes Applied

### Covering Indexes

```sql
CREATE INDEX idx_pmt_merchant_c_join_cov
  ON pmt_txn_fact (merchant_account_number, event_date, parsed_interaction_id, transaction_type);

CREATE INDEX idx_pmt_card_c_join_cov
  ON pmt_txn_fact (card_holder_number_sha512, event_date, parsed_interaction_id, transaction_type);

CREATE INDEX idx_pmt_routing_acct_c_join_cov
  ON pmt_txn_fact (check_bank_routing_number, check_bank_account_number_sha512, event_date, parsed_interaction_id, transaction_type);
```

These indexes were verified in `information_schema.statistics` before this report was generated.

### SQL Rewrites And Session Settings Tested

- Removed redundant `GROUP BY` on constant equality keys and preserved empty-result behavior with `HAVING COUNT(*) > 0`.
- Rewrote 180-day distinct-only and mixed rollup+distinct SQL to share a single `raw_boundary` CTE instead of repeating raw table scans.
- Tested session variants with TiKV/TiDB only, `tidb_opt_distinct_agg_push_down`, `tidb_opt_agg_push_down`, hashagg concurrency, scan concurrency, executor concurrency, and paging on/off.


- Generated: `2026-05-29T00:06:58`
- Source mixed JSON: `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/mixed_traffic_1780029697.json`
- Source slow CSV: `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/slow_bundles_post_index_3eps_60s.csv`
- Scope: only the 15 bundles still appearing in the post-index slow/error list
- Baseline session: TiKV/TiDB only, `tidb_opt_distinct_agg_push_down=0`, `tidb_hashagg_final_concurrency=4`, `tidb_hashagg_partial_concurrency=4`
- Optimized candidates tested per SQL: default optimized SQL, hashagg 16/8, hashagg 32/8, distinct pushdown, distinct pushdown + hashagg 16/8

## Summary

| Bundle | Filter | Optimization | Before | Best After | Delta | Best Variant | Status |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `group_a_bundle_010` | `p.check_bank_routing_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0 | 455.4 ms | 418.1 ms | 8.2% | `optimized_default` | `optimized` |
| `group_a_bundle_006` | `p.check_bank_routing_number = %s` | No material improvement found; retained current covering-index/CTE shape | 140.2 ms | 143.3 ms | -2.2% | `optimized_default` | `optimized` |
| `group_c_bundle_025` | `p.merchant_account_number = %s` | SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 2325.0 ms | 161.1 ms | 93.1% | `optimized_distinct_pushdown_hashagg_16_8` | `optimized` |
| `group_b_bundle_018` | `d.input_ip = %s` | SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 1496.6 ms | 695.3 ms | 53.5% | `optimized_distinct_pushdown_hashagg_16_8` | `unresolved` |
| `group_c_bundle_018` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 1601.9 ms | 362.1 ms | 77.4% | `optimized_distinct_pushdown_hashagg_16_8` | `optimized` |
| `group_c_bundle_021` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_16_8 | 968.5 ms | 301.5 ms | 68.9% | `optimized_hashagg_16_8` | `optimized` |
| `group_b_bundle_020` | `d.true_ip = %s` | SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown | 2884.2 ms | 1128.4 ms | 60.9% | `optimized_distinct_pushdown` | `unresolved` |
| `group_b_bundle_012` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0 | 501.2 ms | 485.6 ms | 3.1% | `optimized_default` | `optimized` |
| `group_a_bundle_008` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8 | 108.3 ms | 67.8 ms | 37.4% | `optimized_hashagg_16_8` | `optimized` |
| `group_a_bundle_014` | `p.check_bank_routing_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8 | 365.9 ms | 315.5 ms | 13.8% | `optimized_hashagg_16_8` | `optimized` |
| `group_b_bundle_008` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8 | 43.8 ms | 34.2 ms | 22.0% | `optimized_hashagg_16_8` | `optimized` |
| `group_c_bundle_011` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown | 592.1 ms | 101.5 ms | 82.9% | `optimized_distinct_pushdown` | `optimized` |
| `group_c_bundle_014` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 152.9 ms | 112.6 ms | 26.4% | `optimized_distinct_pushdown_hashagg_16_8` | `optimized` |
| `group_c_bundle_022` | `d.exact_id = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 2712.4 ms | 104.1 ms | 96.2% | `optimized_distinct_pushdown_hashagg_16_8` | `optimized` |
| `group_c_bundle_007` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_distinct_pushdown | 102.2 ms | 104.6 ms | -2.4% | `optimized_distinct_pushdown` | `optimized` |

## Detailed Evidence

### 1. group_a_bundle_010

- Filter/window: `p.check_bank_routing_number = %s` / `30d`
- Chosen event: `INV0046519149` kind=`hot_check_bank_routing_number` error=`(3024, 'Query execution was interrupted, maximum statement execution time exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 455.4 ms | ok |
| `optimized_default` | `{}` | 418.1 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 432.4 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 424.0 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 829.3 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 859.5 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0041`,
  SUM(p.amount) AS `metric__a_0042`,
  MIN(p.amount) AS `metric__a_0043`,
  MAX(p.amount) AS `metric__a_0044`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `metric__a_1001`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1001`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1002`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1002`,
  MIN(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1003`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1003`,
  MAX(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1004`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1004`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `metric__a_1013`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1013`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1014`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1014`,
  MIN(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1015`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1015`,
  MAX(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1016`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1016`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `metric__a_1025`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1025`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1026`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1026`,
  MIN(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1027`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1027`,
  MAX(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1028`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1028`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `metric__a_1037`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1037`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1038`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1038`,
  MIN(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1039`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1039`,
  MAX(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1040`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1040`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `metric__a_1049`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1049`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1050`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1050`,
  MIN(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1051`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1051`,
  MAX(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1052`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1052`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `metric__a_1061`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1061`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1062`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1062`,
  MIN(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1063`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1063`,
  MAX(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1064`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1064`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `metric__a_1073`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1073`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1074`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1074`,
  MIN(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1075`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1075`,
  MAX(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1076`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1076`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__a_1089`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1089`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1090`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1090`,
  MIN(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1091`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1091`,
  MAX(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1092`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1092`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `metric__a_1101`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1101`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1102`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1102`,
  MIN(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1103`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1103`,
  MAX(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1104`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1104`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__a_1113`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1113`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1114`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1114`,
  MIN(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1115`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1115`,
  MAX(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1116`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1116`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `metric__a_1125`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1125`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1126`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1126`,
  MIN(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1127`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1127`,
  MAX(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1128`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1128`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `metric__a_1137`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1137`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1138`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1138`,
  MIN(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1139`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1139`,
  MAX(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1140`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1140`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `metric__a_1149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1150`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1150`,
  MIN(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1151`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1151`,
  MAX(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1152`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1152`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `metric__a_1161`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1161`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1162`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1162`,
  MIN(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1163`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1163`,
  MAX(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1164`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1164`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `metric__a_1173`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1173`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1174`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1174`,
  MIN(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1175`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1175`,
  MAX(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1176`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1176`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `metric__a_1185`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1185`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1186`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1186`,
  MIN(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1187`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1187`,
  MAX(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1188`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1188`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `metric__a_1197`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1197`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1198`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1198`,
  MIN(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1199`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1199`,
  MAX(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1200`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1200`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `metric__a_1209`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1209`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1210`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1210`,
  MIN(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1211`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1211`,
  MAX(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1212`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1212`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `metric__a_1221`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1221`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1222`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1222`,
  MIN(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1223`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1223`,
  MAX(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1224`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1224`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `metric__a_1233`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1233`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1234`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1234`,
  MIN(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1235`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1235`,
  MAX(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1236`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1236`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `metric__a_1245`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1245`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1246`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1246`,
  MIN(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1247`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1247`,
  MAX(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1248`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1248`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `metric__a_1257`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1257`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1258`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1258`,
  MIN(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1259`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1259`,
  MAX(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1260`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1260`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `metric__a_1269`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1269`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1270`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1270`,
  MIN(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1271`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1271`,
  MAX(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1272`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1272`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__a_1281`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1281`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1282`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1282`,
  MIN(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1283`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1283`,
  MAX(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1284`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1284`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `metric__a_1293`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1293`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1294`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1294`,
  MIN(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1295`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1295`,
  MAX(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1296`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1296`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `metric__a_1305`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1305`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1306`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1306`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1307`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1307`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1308`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1308`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `metric__a_1317`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1317`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1318`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1318`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1319`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1319`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1320`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1320`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `metric__a_1329`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1329`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1330`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1330`,
  MIN(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1331`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1331`,
  MAX(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1332`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1332`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `metric__a_1341`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1341`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1342`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1342`,
  MIN(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1343`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1343`,
  MAX(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1344`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1344`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `metric__a_1353`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1353`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1354`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1354`,
  MIN(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1355`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1355`,
  MAX(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1356`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1356`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `metric__a_1365`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1365`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1366`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1366`,
  MIN(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1367`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1367`,
  MAX(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1368`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1368`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `metric__a_1377`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1377`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1378`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1378`,
  MIN(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1379`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1379`,
  MAX(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1380`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1380`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `metric__a_1389`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1389`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1390`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1390`,
  MIN(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1391`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1391`,
  MAX(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1392`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1392`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `metric__a_1401`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1401`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1402`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1402`,
  MIN(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1403`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1403`,
  MAX(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1404`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1404`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `metric__a_1413`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1413`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1414`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1414`,
  MIN(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1415`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1415`,
  MAX(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1416`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1416`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `metric__a_1425`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1425`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1426`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1426`,
  MIN(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1427`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1427`,
  MAX(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1428`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1428`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `metric__a_1437`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1437`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1438`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1438`,
  MIN(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1439`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1439`,
  MAX(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1440`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1440`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `metric__a_1449`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1449`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1450`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1450`,
  MIN(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1451`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1451`,
  MAX(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1452`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1452`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `metric__a_1461`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1461`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1462`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1462`,
  MIN(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1463`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1463`,
  MAX(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1464`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1464`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `metric__a_1473`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1473`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1474`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1474`,
  MIN(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1475`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1475`,
  MAX(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1476`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1476`,
  COUNT(DISTINCT(p.card_type)) AS `metric__a_1891`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__a_1892`,
  COUNT(DISTINCT(p.mt_gateway)) AS `metric__a_1893`
FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1773275781546
GROUP BY p.check_bank_routing_number;
```

#### Original Params

```json
[
  "322271627"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=455.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	25.26	1	root		time:353.3ms, open:1.11ms, close:47.6µs, loops:2, RU:391.03, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#183, Column#186, Column#183, Column#187, Column#187, Column#188, Column#187, Column#189, Column#187, Column#190, Column#187, Column#191, Column#191, Column#192, Column#191, Column#193, Column#191, Column#194, Column#191, Column#195, Column#195, Column#196, Column#195, Column#197, Column#195, Column#198, Column#195, Column#199, Column#199, Column#200, Column#199, Column#201, Column#199, Column#202, Column#199, Column#203, Column#203, Column#204, Column#203, Column#205, Column#203, Column#206, Column#203, Column#207, Column#207, Column#208, Column#207, Column#209, Column#207, Column#210, Column#207, Column#211, Column#212, Column#213	230.1 KB	N/A
└─HashAgg_9	25.26	1	root		time:353ms, open:1.04ms, close:45.4µs, loops:2	group by:Column#1528, funcs:count(?)->Column#47, funcs:sum(Column#1362)->Column#48, funcs:min(Column#1363)->Column#49, funcs:max(Column#1364)->Column#50, funcs:sum(Column#1365)->Column#51, funcs:sum(Column#1366)->Column#52, funcs:min(Column#1367)->Column#53, funcs:max(Column#1368)->Column#54, funcs:sum(Column#1369)->Column#55, funcs:sum(Column#1370)->Column#56, funcs:min(Column#1371)->Column#57, funcs:max(Column#1372)->Column#58, funcs:sum(Column#1373)->Column#59, funcs:sum(Column#1374)->Column#60, funcs:min(Column#1375)->Column#61, funcs:max(Column#1376)->Column#62, funcs:sum(Column#1377)->Column#63, funcs:sum(Column#1378)->Column#64, funcs:min(Column#1379)->Column#65, funcs:max(Column#1380)->Column#66, funcs:sum(Column#1381)->Column#67, funcs:sum(Column#1382)->Column#68, funcs:min(Column#1383)->Column#69, funcs:max(Column#1384)->Column#70, funcs:sum(Column#1385)->Column#71, funcs:sum(Column#1386)->Column#72, funcs:min(Column#1387)->Column#73, funcs:max(Column#1388)->Column#74, funcs:sum(Column#1389)->Column#75, funcs:sum(Column#1390)->Column#76, funcs:min(Column#1391)->Column#77, funcs:max(Column#1392)->Column#78, funcs:sum(Column#1393)->Column#79, funcs:sum(Column#1394)->Column#80, funcs:min(Column#1395)->Column#81, funcs:max(Column#1396)->Column#82, funcs:sum(Column#1397)->Column#83, funcs:sum(Column#1398)->Column#84, funcs:min(Column#1399)->Column#85, funcs:max(Column#1400)->Column#86, funcs:sum(Column#1401)->Column#87, funcs:sum(Column#1402)->Column#88, funcs:min(Column#1403)->Column#89, funcs:max(Column#1404)->Column#90, funcs:sum(Column#1405)->Column#91, funcs:sum(Column#1406)->Column#92, funcs:min(Column#1407)->Column#93, funcs:max(Column#1408)->Column#94, funcs:sum(Column#1409)->Column#95, funcs:sum(Column#1410)->Column#96, funcs:min(Column#1411)->Column#97, funcs:max(Column#1412)->Column#98, funcs:sum(Column#1413)->Column#99, funcs:sum(Column#1414)->Column#100, funcs:min(Column#1415)->Column#101, funcs:max(Column#1416)->Column#102, funcs:sum(Column#1417)->Column#103, funcs:sum(Column#1418)->Column#104, funcs:min(Column#1419)->Column#105, funcs:max(Column#1420)->Column#106, funcs:sum(Column#1421)->Column#107, funcs:sum(Column#1422)->Column#108, funcs:min(Column#1423)->Column#109, funcs:max(Column#1424)->Column#110, funcs:sum(Column#1425)->Column#111, funcs:sum(Column#1426)->Column#112, funcs:min(Column#1427)->Column#113, funcs:max(Column#1428)->Column#114, funcs:sum(Column#1429)->Column#115, funcs:sum(Column#1430)->Column#116, funcs:min(Column#1431)->Column#117, funcs:max(Column#1432)->Column#118, funcs:sum(Column#1433)->Column#119, funcs:sum(Column#1434)->Column#120, funcs:min(Column#1435)->Column#121, funcs:max(Column#1436)->Column#122, funcs:sum(Column#1437)->Column#123, funcs:sum(Column#1438)->Column#124, funcs:min(Column#1439)->Column#125, funcs:max(Column#1440)->Column#126, funcs:sum(Column#1441)->Column#127, funcs:sum(Column#1442)->Column#128, funcs:min(Column#1443)->Column#129, funcs:max(Column#1444)->Column#130, funcs:sum(Column#1445)->Column#131, funcs:sum(Column#1446)->Column#132, funcs:min(Column#1447)->Column#133, funcs:max(Column#1448)->Column#134, funcs:sum(Column#1449)->Column#135, funcs:sum(Column#1450)->Column#136, funcs:min(Column#1451)->Column#137, funcs:max(Column#1452)->Column#138, funcs:sum(Column#1453)->Column#139, funcs:sum(Column#1454)->Column#140, funcs:min(Column#1455)->Column#141, funcs:max(Column#1456)->Column#142, funcs:sum(Column#1457)->Column#143, funcs:sum(Column#1458)->Column#144, funcs:min(Column#1459)->Column#145, funcs:max(Column#1460)->Column#146, funcs:sum(Column#1461)->Column#147, funcs:sum(Column#1462)->Column#148, funcs:min(Column#1463)->Column#149, funcs:max(Column#1464)->Column#150, funcs:sum(Column#1465)->Column#151, funcs:sum(Column#1466)->Column#152, funcs:min(Column#1467)->Column#153, funcs:max(Column#1468)->Column#154, funcs:sum(Column#1469)->Column#155, funcs:sum(Column#1470)->Column#156, funcs:min(Column#1471)->Column#157, funcs:max(Column#1472)->Column#158, funcs:sum(Column#1473)->Column#159, funcs:sum(Column#1474)->Column#160, funcs:min(Column#1475)->Column#161, funcs:max(Column#1476)->Column#162, funcs:sum(Column#1477)->Column#163, funcs:sum(Column#1478)->Column#164, funcs:min(Column#1479)->Column#165, funcs:max(Column#1480)->Column#166, funcs:sum(Column#1481)->Column#167, funcs:sum(Column#1482)->Column#168, funcs:min(Column#1483)->Column#169, funcs:max(Column#1484)->Column#170, funcs:sum(Column#1485)->Column#171, funcs:sum(Column#1486)->Column#172, funcs:min(Column#1487)->Column#173, funcs:max(Column#1488)->Column#174, funcs:sum(Column#1489)->Column#175, funcs:sum(Column#1490)->Column#176, funcs:min(Column#1491)->Column#177, funcs:max(Column#1492)->Column#178, funcs:sum(Column#1493)->Column#179, funcs:sum(Column#1494)->Column#180, funcs:min(Column#1495)->Column#181, funcs:max(Column#1496)->Column#182, funcs:sum(Column#1497)->Column#183, funcs:sum(Column#1498)->Column#184, funcs:min(Column#1499)->Column#185, funcs:max(Column#1500)->Column#186, funcs:sum(Column#1501)->Column#187, funcs:sum(Column#1502)->Column#188, funcs:min(Column#1503)->Column#189, funcs:max(Column#1504)->Column#190, funcs:sum(Column#1505)->Column#191, funcs:sum(Column#1506)->Column#192, funcs:min(Column#1507)->Column#193, funcs:max(Column#1508)->Column#194, funcs:sum(Column#1509)->Column#195, funcs:sum(Column#1510)->Column#196, funcs:min(Column#1511)->Column#197, funcs:max(Column#1512)->Column#198, funcs:sum(Column#1513)->Column#199, funcs:sum(Column#1514)->Column#200, funcs:min(Column#1515)->Column#201, funcs:max(Column#1516)->Column#202, funcs:sum(Column#1517)->Column#203, funcs:sum(Column#1518)->Column#204, funcs:min(Column#1519)->Column#205, funcs:max(Column#1520)->Column#206, funcs:sum(Column#1521)->Column#207, funcs:sum(Column#1522)->Column#208, funcs:min(Column#1523)->Column#209, funcs:max(Column#1524)->Column#210, funcs:count(distinct Column#1525)->Column#211, funcs:count(distinct Column#1526)->Column#212, funcs:count(distinct Column#1527)->Column#213	6.59 MB	0 Bytes
  └─Projection_41	285842.12	119821	root		time:15.2ms, open:836.7µs, close:44.4µs, loops:120, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#1362, intuit_risk.pmt_txn_fact.amount->Column#1363, intuit_risk.pmt_txn_fact.amount->Column#1364, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1365, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1366, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1367, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1368, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1369, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1370, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1371, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1372, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1373, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1374, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1375, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1376, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1377, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1378, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1379, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1380, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1381, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1382, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1383, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1384, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1385, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1386, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1387, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1388, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1389, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1390, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1391, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1392, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1393, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1394, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1395, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1396, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1397, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1398, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1399, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1400, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1401, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1402, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1403, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1404, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1405, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1406, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1407, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1408, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1409, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1410, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1411, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1412, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1413, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1414, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1415, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1416, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1417, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1418, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1419, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1420, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1421, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1422, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1423, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1424, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1425, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1426, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1427, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1428, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1429, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1430, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1431, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1432, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1433, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1434, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1435, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1436, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1437, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1438, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1439, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1440, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1441, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1442, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1443, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1444, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1445, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1446, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1447, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1448, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1449, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1450, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1451, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1452, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1453, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1454, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1455, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1456, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1457, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1458, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1459, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1460, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1461, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1462, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1463, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1464, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1465, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1466, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1467, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1468, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1469, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1470, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1471, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1472, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1473, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1474, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1475, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1476, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1477, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1478, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1479, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1480, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1481, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1482, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1483, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1484, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1485, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1486, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1487, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1488, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1489, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1490, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1491, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1492, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1493, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1494, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1495, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1496, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1497, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1498, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1499, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1500, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1501, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1502, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1503, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1504, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1505, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1506, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1507, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1508, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1509, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1510, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1511, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1512, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1513, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1514, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1515, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1516, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1517, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1518, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1519, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1520, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1521, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1522, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1523, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1524, intuit_risk.pmt_txn_fact.card_type->Column#1525, intuit_risk.pmt_txn_fact.entry_method->Column#1526, intuit_risk.pmt_txn_fact.mt_gateway->Column#1527, intuit_risk.pmt_txn_fact.check_bank_routing_number->Column#1528	33.0 MB	N/A
    └─IndexReader_29	285842.12	119821	root	partition:p20260401,p20260501,p20260601,pmax	time:14.2ms, open:833.2µs, close:13.3µs, loops:120, cop_task: {num: 21, max: 50.3ms, min: 1.04ms, avg: 9.93ms, p95: 27.3ms, max_proc_keys: 33760, p95_proc_keys: 17376, tot_proc: 149.5ms, tot_wait: 4.93ms, copr_cache: disabled, build_task_duration: 783.8µs, max_distsql_concurrency: 4}, fetch_resp_duration: 11.7ms, rpc_info:{Cop:{num_rpc:21, total_time:208.2ms}}	index:IndexRangeScan_28	5.68 MB	N/A
      └─IndexRangeScan_28	285842.12	119821	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:30ms, min:0s, avg: 5.71ms, p80:10ms, p95:20ms, iters:193, tasks:21}, scan_detail: {total_process_keys: 119821, total_process_keys_size: 21706797, total_keys: 119842, get_snapshot_time: 4.46ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 149.5ms, total_suspend_time: 375.6µs, total_wait_time: 4.93ms, total_kv_read_wall_time: 120ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0041`,
  SUM(p.amount) AS `metric__a_0042`,
  MIN(p.amount) AS `metric__a_0043`,
  MAX(p.amount) AS `metric__a_0044`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `metric__a_1001`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1001`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1002`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1002`,
  MIN(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1003`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1003`,
  MAX(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1004`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1004`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `metric__a_1013`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1013`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1014`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1014`,
  MIN(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1015`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1015`,
  MAX(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1016`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1016`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `metric__a_1025`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1025`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1026`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1026`,
  MIN(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1027`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1027`,
  MAX(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1028`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1028`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `metric__a_1037`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1037`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1038`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1038`,
  MIN(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1039`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1039`,
  MAX(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1040`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1040`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `metric__a_1049`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1049`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1050`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1050`,
  MIN(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1051`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1051`,
  MAX(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1052`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1052`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `metric__a_1061`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1061`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1062`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1062`,
  MIN(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1063`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1063`,
  MAX(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1064`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1064`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `metric__a_1073`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1073`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1074`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1074`,
  MIN(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1075`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1075`,
  MAX(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1076`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1076`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__a_1089`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1089`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1090`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1090`,
  MIN(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1091`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1091`,
  MAX(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1092`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1092`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `metric__a_1101`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1101`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1102`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1102`,
  MIN(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1103`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1103`,
  MAX(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1104`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1104`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__a_1113`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1113`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1114`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1114`,
  MIN(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1115`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1115`,
  MAX(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1116`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1116`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `metric__a_1125`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1125`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1126`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1126`,
  MIN(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1127`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1127`,
  MAX(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1128`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1128`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `metric__a_1137`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1137`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1138`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1138`,
  MIN(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1139`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1139`,
  MAX(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1140`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1140`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `metric__a_1149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1150`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1150`,
  MIN(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1151`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1151`,
  MAX(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1152`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1152`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `metric__a_1161`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1161`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1162`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1162`,
  MIN(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1163`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1163`,
  MAX(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1164`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1164`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `metric__a_1173`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1173`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1174`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1174`,
  MIN(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1175`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1175`,
  MAX(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1176`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1176`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `metric__a_1185`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1185`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1186`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1186`,
  MIN(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1187`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1187`,
  MAX(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1188`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1188`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `metric__a_1197`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1197`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1198`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1198`,
  MIN(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1199`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1199`,
  MAX(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1200`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1200`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `metric__a_1209`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1209`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1210`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1210`,
  MIN(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1211`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1211`,
  MAX(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1212`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1212`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `metric__a_1221`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1221`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1222`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1222`,
  MIN(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1223`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1223`,
  MAX(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1224`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1224`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `metric__a_1233`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1233`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1234`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1234`,
  MIN(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1235`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1235`,
  MAX(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1236`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1236`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `metric__a_1245`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1245`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1246`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1246`,
  MIN(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1247`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1247`,
  MAX(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1248`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1248`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `metric__a_1257`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1257`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1258`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1258`,
  MIN(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1259`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1259`,
  MAX(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1260`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1260`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `metric__a_1269`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1269`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1270`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1270`,
  MIN(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1271`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1271`,
  MAX(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1272`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1272`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__a_1281`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1281`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1282`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1282`,
  MIN(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1283`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1283`,
  MAX(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1284`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1284`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `metric__a_1293`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1293`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1294`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1294`,
  MIN(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1295`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1295`,
  MAX(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1296`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1296`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `metric__a_1305`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1305`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1306`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1306`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1307`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1307`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1308`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1308`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `metric__a_1317`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1317`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1318`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1318`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1319`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1319`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1320`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1320`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `metric__a_1329`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1329`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1330`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1330`,
  MIN(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1331`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1331`,
  MAX(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1332`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1332`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `metric__a_1341`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1341`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1342`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1342`,
  MIN(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1343`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1343`,
  MAX(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1344`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1344`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `metric__a_1353`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1353`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1354`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1354`,
  MIN(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1355`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1355`,
  MAX(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1356`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1356`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `metric__a_1365`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1365`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1366`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1366`,
  MIN(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1367`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1367`,
  MAX(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1368`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1368`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `metric__a_1377`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1377`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1378`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1378`,
  MIN(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1379`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1379`,
  MAX(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1380`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1380`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `metric__a_1389`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1389`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1390`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1390`,
  MIN(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1391`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1391`,
  MAX(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1392`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1392`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `metric__a_1401`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1401`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1402`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1402`,
  MIN(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1403`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1403`,
  MAX(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1404`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1404`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `metric__a_1413`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1413`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1414`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1414`,
  MIN(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1415`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1415`,
  MAX(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1416`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1416`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `metric__a_1425`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1425`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1426`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1426`,
  MIN(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1427`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1427`,
  MAX(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1428`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1428`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `metric__a_1437`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1437`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1438`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1438`,
  MIN(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1439`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1439`,
  MAX(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1440`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1440`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `metric__a_1449`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1449`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1450`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1450`,
  MIN(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1451`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1451`,
  MAX(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1452`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1452`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `metric__a_1461`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1461`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1462`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1462`,
  MIN(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1463`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1463`,
  MAX(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1464`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1464`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `metric__a_1473`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1473`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1474`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1474`,
  MIN(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1475`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1475`,
  MAX(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1476`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1476`,
  COUNT(DISTINCT(p.card_type)) AS `metric__a_1891`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__a_1892`,
  COUNT(DISTINCT(p.mt_gateway)) AS `metric__a_1893`
FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1773275781546
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  "322271627"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_default
-- explain_analyze_elapsed_ms=418.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:344.2ms, open:311.9µs, close:42µs, loops:2, RU:377.94, Concurrency:OFF	Column#47->Column#214, Column#48->Column#215, Column#49->Column#216, Column#50->Column#217, Column#51->Column#218, Column#51->Column#219, Column#52->Column#220, Column#51->Column#221, Column#53->Column#222, Column#51->Column#223, Column#54->Column#224, Column#51->Column#225, Column#55->Column#226, Column#55->Column#227, Column#56->Column#228, Column#55->Column#229, Column#57->Column#230, Column#55->Column#231, Column#58->Column#232, Column#55->Column#233, Column#59->Column#234, Column#59->Column#235, Column#60->Column#236, Column#59->Column#237, Column#61->Column#238, Column#59->Column#239, Column#62->Column#240, Column#59->Column#241, Column#63->Column#242, Column#63->Column#243, Column#64->Column#244, Column#63->Column#245, Column#65->Column#246, Column#63->Column#247, Column#66->Column#248, Column#63->Column#249, Column#67->Column#250, Column#67->Column#251, Column#68->Column#252, Column#67->Column#253, Column#69->Column#254, Column#67->Column#255, Column#70->Column#256, Column#67->Column#257, Column#71->Column#258, Column#71->Column#259, Column#72->Column#260, Column#71->Column#261, Column#73->Column#262, Column#71->Column#263, Column#74->Column#264, Column#71->Column#265, Column#75->Column#266, Column#75->Column#267, Column#76->Column#268, Column#75->Column#269, Column#77->Column#270, Column#75->Column#271, Column#78->Column#272, Column#75->Column#273, Column#79->Column#274, Column#79->Column#275, Column#80->Column#276, Column#79->Column#277, Column#81->Column#278, Column#79->Column#279, Column#82->Column#280, Column#79->Column#281, Column#83->Column#282, Column#83->Column#283, Column#84->Column#284, Column#83->Column#285, Column#85->Column#286, Column#83->Column#287, Column#86->Column#288, Column#83->Column#289, Column#87->Column#290, Column#87->Column#291, Column#88->Column#292, Column#87->Column#293, Column#89->Column#294, Column#87->Column#295, Column#90->Column#296, Column#87->Column#297, Column#91->Column#298, Column#91->Column#299, Column#92->Column#300, Column#91->Column#301, Column#93->Column#302, Column#91->Column#303, Column#94->Column#304, Column#91->Column#305, Column#95->Column#306, Column#95->Column#307, Column#96->Column#308, Column#95->Column#309, Column#97->Column#310, Column#95->Column#311, Column#98->Column#312, Column#95->Column#313, Column#99->Column#314, Column#99->Column#315, Column#100->Column#316, Column#99->Column#317, Column#101->Column#318, Column#99->Column#319, Column#102->Column#320, Column#99->Column#321, Column#103->Column#322, Column#103->Column#323, Column#104->Column#324, Column#103->Column#325, Column#105->Column#326, Column#103->Column#327, Column#106->Column#328, Column#103->Column#329, Column#107->Column#330, Column#107->Column#331, Column#108->Column#332, Column#107->Column#333, Column#109->Column#334, Column#107->Column#335, Column#110->Column#336, Column#107->Column#337, Column#111->Column#338, Column#111->Column#339, Column#112->Column#340, Column#111->Column#341, Column#113->Column#342, Column#111->Column#343, Column#114->Column#344, Column#111->Column#345, Column#115->Column#346, Column#115->Column#347, Column#116->Column#348, Column#115->Column#349, Column#117->Column#350, Column#115->Column#351, Column#118->Column#352, Column#115->Column#353, Column#119->Column#354, Column#119->Column#355, Column#120->Column#356, Column#119->Column#357, Column#121->Column#358, Column#119->Column#359, Column#122->Column#360, Column#119->Column#361, Column#123->Column#362, Column#123->Column#363, Column#124->Column#364, Column#123->Column#365, Column#125->Column#366, Column#123->Column#367, Column#126->Column#368, Column#123->Column#369, Column#127->Column#370, Column#127->Column#371, Column#128->Column#372, Column#127->Column#373, Column#129->Column#374, Column#127->Column#375, Column#130->Column#376, Column#127->Column#377, Column#131->Column#378, Column#131->Column#379, Column#132->Column#380, Column#131->Column#381, Column#133->Column#382, Column#131->Column#383, Column#134->Column#384, Column#131->Column#385, Column#135->Column#386, Column#135->Column#387, Column#136->Column#388, Column#135->Column#389, Column#137->Column#390, Column#135->Column#391, Column#138->Column#392, Column#135->Column#393, Column#139->Column#394, Column#139->Column#395, Column#140->Column#396, Column#139->Column#397, Column#141->Column#398, Column#139->Column#399, Column#142->Column#400, Column#139->Column#401, Column#143->Column#402, Column#143->Column#403, Column#144->Column#404, Column#143->Column#405, Column#145->Column#406, Column#143->Column#407, Column#146->Column#408, Column#143->Column#409, Column#147->Column#410, Column#147->Column#411, Column#148->Column#412, Column#147->Column#413, Column#149->Column#414, Column#147->Column#415, Column#150->Column#416, Column#147->Column#417, Column#151->Column#418, Column#151->Column#419, Column#152->Column#420, Column#151->Column#421, Column#153->Column#422, Column#151->Column#423, Column#154->Column#424, Column#151->Column#425, Column#155->Column#426, Column#155->Column#427, Column#156->Column#428, Column#155->Column#429, Column#157->Column#430, Column#155->Column#431, Column#158->Column#432, Column#155->Column#433, Column#159->Column#434, Column#159->Column#435, Column#160->Column#436, Column#159->Column#437, Column#161->Column#438, Column#159->Column#439, Column#162->Column#440, Column#159->Column#441, Column#163->Column#442, Column#163->Column#443, Column#164->Column#444, Column#163->Column#445, Column#165->Column#446, Column#163->Column#447, Column#166->Column#448, Column#163->Column#449, Column#167->Column#450, Column#167->Column#451, Column#168->Column#452, Column#167->Column#453, Column#169->Column#454, Column#167->Column#455, Column#170->Column#456, Column#167->Column#457, Column#171->Column#458, Column#171->Column#459, Column#172->Column#460, Column#171->Column#461, Column#173->Column#462, Column#171->Column#463, Column#174->Column#464, Column#171->Column#465, Column#175->Column#466, Column#175->Column#467, Column#176->Column#468, Column#175->Column#469, Column#177->Column#470, Column#175->Column#471, Column#178->Column#472, Column#175->Column#473, Column#179->Column#474, Column#179->Column#475, Column#180->Column#476, Column#179->Column#477, Column#181->Column#478, Column#179->Column#479, Column#182->Column#480, Column#179->Column#481, Column#183->Column#482, Column#183->Column#483, Column#184->Column#484, Column#183->Column#485, Column#185->Column#486, Column#183->Column#487, Column#186->Column#488, Column#183->Column#489, Column#187->Column#490, Column#187->Column#491, Column#188->Column#492, Column#187->Column#493, Column#189->Column#494, Column#187->Column#495, Column#190->Column#496, Column#187->Column#497, Column#191->Column#498, Column#191->Column#499, Column#192->Column#500, Column#191->Column#501, Column#193->Column#502, Column#191->Column#503, Column#194->Column#504, Column#191->Column#505, Column#195->Column#506, Column#195->Column#507, Column#196->Column#508, Column#195->Column#509, Column#197->Column#510, Column#195->Column#511, Column#198->Column#512, Column#195->Column#513, Column#199->Column#514, Column#199->Column#515, Column#200->Column#516, Column#199->Column#517, Column#201->Column#518, Column#199->Column#519, Column#202->Column#520, Column#199->Column#521, Column#203->Column#522, Column#203->Column#523, Column#204->Column#524, Column#203->Column#525, Column#205->Column#526, Column#203->Column#527, Column#206->Column#528, Column#203->Column#529, Column#207->Column#530, Column#207->Column#531, Column#208->Column#532, Column#207->Column#533, Column#209->Column#534, Column#207->Column#535, Column#210->Column#536, Column#207->Column#537, Column#211->Column#538, Column#212->Column#539, Column#213->Column#540	230.1 KB	N/A
└─Selection_9	0.80	1	root		time:343.8ms, open:236.5µs, close:39.7µs, loops:2	gt(Column#47, ?)	230.1 KB	N/A
  └─HashAgg_13	1.00	1	root		time:343.7ms, open:177.7µs, close:38.9µs, loops:3	funcs:count(?)->Column#47, funcs:sum(Column#869)->Column#48, funcs:min(Column#870)->Column#49, funcs:max(Column#871)->Column#50, funcs:sum(Column#872)->Column#51, funcs:sum(Column#873)->Column#52, funcs:min(Column#874)->Column#53, funcs:max(Column#875)->Column#54, funcs:sum(Column#876)->Column#55, funcs:sum(Column#877)->Column#56, funcs:min(Column#878)->Column#57, funcs:max(Column#879)->Column#58, funcs:sum(Column#880)->Column#59, funcs:sum(Column#881)->Column#60, funcs:min(Column#882)->Column#61, funcs:max(Column#883)->Column#62, funcs:sum(Column#884)->Column#63, funcs:sum(Column#885)->Column#64, funcs:min(Column#886)->Column#65, funcs:max(Column#887)->Column#66, funcs:sum(Column#888)->Column#67, funcs:sum(Column#889)->Column#68, funcs:min(Column#890)->Column#69, funcs:max(Column#891)->Column#70, funcs:sum(Column#892)->Column#71, funcs:sum(Column#893)->Column#72, funcs:min(Column#894)->Column#73, funcs:max(Column#895)->Column#74, funcs:sum(Column#896)->Column#75, funcs:sum(Column#897)->Column#76, funcs:min(Column#898)->Column#77, funcs:max(Column#899)->Column#78, funcs:sum(Column#900)->Column#79, funcs:sum(Column#901)->Column#80, funcs:min(Column#902)->Column#81, funcs:max(Column#903)->Column#82, funcs:sum(Column#904)->Column#83, funcs:sum(Column#905)->Column#84, funcs:min(Column#906)->Column#85, funcs:max(Column#907)->Column#86, funcs:sum(Column#908)->Column#87, funcs:sum(Column#909)->Column#88, funcs:min(Column#910)->Column#89, funcs:max(Column#911)->Column#90, funcs:sum(Column#912)->Column#91, funcs:sum(Column#913)->Column#92, funcs:min(Column#914)->Column#93, funcs:max(Column#915)->Column#94, funcs:sum(Column#916)->Column#95, funcs:sum(Column#917)->Column#96, funcs:min(Column#918)->Column#97, funcs:max(Column#919)->Column#98, funcs:sum(Column#920)->Column#99, funcs:sum(Column#921)->Column#100, funcs:min(Column#922)->Column#101, funcs:max(Column#923)->Column#102, funcs:sum(Column#924)->Column#103, funcs:sum(Column#925)->Column#104, funcs:min(Column#926)->Column#105, funcs:max(Column#927)->Column#106, funcs:sum(Column#928)->Column#107, funcs:sum(Column#929)->Column#108, funcs:min(Column#930)->Column#109, funcs:max(Column#931)->Column#110, funcs:sum(Column#932)->Column#111, funcs:sum(Column#933)->Column#112, funcs:min(Column#934)->Column#113, funcs:max(Column#935)->Column#114, funcs:sum(Column#936)->Column#115, funcs:sum(Column#937)->Column#116, funcs:min(Column#938)->Column#117, funcs:max(Column#939)->Column#118, funcs:sum(Column#940)->Column#119, funcs:sum(Column#941)->Column#120, funcs:min(Column#942)->Column#121, funcs:max(Column#943)->Column#122, funcs:sum(Column#944)->Column#123, funcs:sum(Column#945)->Column#124, funcs:min(Column#946)->Column#125, funcs:max(Column#947)->Column#126, funcs:sum(Column#948)->Column#127, funcs:sum(Column#949)->Column#128, funcs:min(Column#950)->Column#129, funcs:max(Column#951)->Column#130, funcs:sum(Column#952)->Column#131, funcs:sum(Column#953)->Column#132, funcs:min(Column#954)->Column#133, funcs:max(Column#955)->Column#134, funcs:sum(Column#956)->Column#135, funcs:sum(Column#957)->Column#136, funcs:min(Column#958)->Column#137, funcs:max(Column#959)->Column#138, funcs:sum(Column#960)->Column#139, funcs:sum(Column#961)->Column#140, funcs:min(Column#962)->Column#141, funcs:max(Column#963)->Column#142, funcs:sum(Column#964)->Column#143, funcs:sum(Column#965)->Column#144, funcs:min(Column#966)->Column#145, funcs:max(Column#967)->Column#146, funcs:sum(Column#968)->Column#147, funcs:sum(Column#969)->Column#148, funcs:min(Column#970)->Column#149, funcs:max(Column#971)->Column#150, funcs:sum(Column#972)->Column#151, funcs:sum(Column#973)->Column#152, funcs:min(Column#974)->Column#153, funcs:max(Column#975)->Column#154, funcs:sum(Column#976)->Column#155, funcs:sum(Column#977)->Column#156, funcs:min(Column#978)->Column#157, funcs:max(Column#979)->Column#158, funcs:sum(Column#980)->Column#159, funcs:sum(Column#981)->Column#160, funcs:min(Column#982)->Column#161, funcs:max(Column#983)->Column#162, funcs:sum(Column#984)->Column#163, funcs:sum(Column#985)->Column#164, funcs:min(Column#986)->Column#165, funcs:max(Column#987)->Column#166, funcs:sum(Column#988)->Column#167, funcs:sum(Column#989)->Column#168, funcs:min(Column#990)->Column#169, funcs:max(Column#991)->Column#170, funcs:sum(Column#992)->Column#171, funcs:sum(Column#993)->Column#172, funcs:min(Column#994)->Column#173, funcs:max(Column#995)->Column#174, funcs:sum(Column#996)->Column#175, funcs:sum(Column#997)->Column#176, funcs:min(Column#998)->Column#177, funcs:max(Column#999)->Column#178, funcs:sum(Column#1000)->Column#179, funcs:sum(Column#1001)->Column#180, funcs:min(Column#1002)->Column#181, funcs:max(Column#1003)->Column#182, funcs:sum(Column#1004)->Column#183, funcs:sum(Column#1005)->Column#184, funcs:min(Column#1006)->Column#185, funcs:max(Column#1007)->Column#186, funcs:sum(Column#1008)->Column#187, funcs:sum(Column#1009)->Column#188, funcs:min(Column#1010)->Column#189, funcs:max(Column#1011)->Column#190, funcs:sum(Column#1012)->Column#191, funcs:sum(Column#1013)->Column#192, funcs:min(Column#1014)->Column#193, funcs:max(Column#1015)->Column#194, funcs:sum(Column#1016)->Column#195, funcs:sum(Column#1017)->Column#196, funcs:min(Column#1018)->Column#197, funcs:max(Column#1019)->Column#198, funcs:sum(Column#1020)->Column#199, funcs:sum(Column#1021)->Column#200, funcs:min(Column#1022)->Column#201, funcs:max(Column#1023)->Column#202, funcs:sum(Column#1024)->Column#203, funcs:sum(Column#1025)->Column#204, funcs:min(Column#1026)->Column#205, funcs:max(Column#1027)->Column#206, funcs:sum(Column#1028)->Column#207, funcs:sum(Column#1029)->Column#208, funcs:min(Column#1030)->Column#209, funcs:max(Column#1031)->Column#210, funcs:count(distinct Column#1032)->Column#211, funcs:count(distinct Column#1033)->Column#212, funcs:count(distinct Column#1034)->Column#213	6.57 MB	0 Bytes
    └─Projection_28	285842.12	119821	root		time:15.7ms, open:59.7µs, close:38.2µs, loops:120, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#869, intuit_risk.pmt_txn_fact.amount->Column#870, intuit_risk.pmt_txn_fact.amount->Column#871, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#872, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#873, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#874, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#875, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#876, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#877, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#878, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#879, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#880, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#881, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#882, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#883, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#884, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#885, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#886, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#887, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#888, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#889, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#890, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#891, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#892, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#893, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#894, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#895, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#896, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#897, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#898, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#899, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#900, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#901, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#902, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#903, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#904, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#905, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#906, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#907, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#908, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#909, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#910, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#911, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#912, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#913, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#914, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#915, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#916, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#917, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#918, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#919, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#920, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#921, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#922, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#923, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#924, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#925, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#926, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#927, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#928, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#929, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#930, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#931, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#932, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#933, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#934, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#935, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#936, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#937, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#938, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#939, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#940, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#941, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#942, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#943, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#944, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#945, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#946, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#947, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#948, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#949, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#950, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#951, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#952, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#953, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#954, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#955, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#956, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#957, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#958, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#959, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#960, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#961, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#962, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#963, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#964, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#965, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#966, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#967, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#968, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#969, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#970, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#971, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#972, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#973, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#974, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#975, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#976, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#977, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#978, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#979, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#980, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#981, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#982, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#983, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#984, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#985, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#986, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#987, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#988, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#989, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#990, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#991, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#992, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#993, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#994, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#995, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#996, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#997, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#998, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#999, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1000, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1001, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1002, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1003, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1004, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1005, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1006, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1007, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1008, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1009, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1010, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1011, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1012, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1013, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1014, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1015, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1016, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1017, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1018, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1019, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1020, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1021, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1022, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1023, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1024, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1025, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1026, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1027, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1028, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1029, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1030, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1031, intuit_risk.pmt_txn_fact.card_type->Column#1032, intuit_risk.pmt_txn_fact.entry_method->Column#1033, intuit_risk.pmt_txn_fact.mt_gateway->Column#1034	32.9 MB	N/A
      └─IndexReader_21	285842.12	119821	root	partition:p20260401,p20260501,p20260601,pmax	time:7.4ms, open:58.7µs, close:11.6µs, loops:120, cop_task: {num: 21, max: 39.5ms, min: 923µs, avg: 7.36ms, p95: 21.4ms, max_proc_keys: 33760, p95_proc_keys: 17376, tot_proc: 110.2ms, tot_wait: 860.9µs, copr_cache: disabled, build_task_duration: 14.3µs, max_distsql_concurrency: 4}, fetch_resp_duration: 5.55ms, rpc_info:{Cop:{num_rpc:21, total_time:154.2ms}}	index:IndexRangeScan_20	5.97 MB	N/A
        └─IndexRangeScan_20	285842.12	119821	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:30ms, min:0s, avg: 4.76ms, p80:10ms, p95:10ms, iters:193, tasks:21}, scan_detail: {total_process_keys: 119821, total_process_keys_size: 21706797, total_keys: 119842, get_snapshot_time: 387.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 110.2ms, total_suspend_time: 301.9µs, total_wait_time: 860.9µs, total_kv_read_wall_time: 100ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 2. group_a_bundle_006

- Filter/window: `p.check_bank_routing_number = %s` / `7d`
- Chosen event: `INV0046519149` kind=`hot_check_bank_routing_number` error=`(3024, 'Query execution was interrupted, maximum statement execution time exceeded')`
- Optimization: No material improvement found; retained current covering-index/CTE shape

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 140.2 ms | ok |
| `optimized_default` | `{}` | 143.3 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 149.4 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 174.5 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 376.0 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 380.5 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0037`,
  SUM(p.amount) AS `metric__a_0038`,
  MIN(p.amount) AS `metric__a_0039`,
  MAX(p.amount) AS `metric__a_0040`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `metric__a_0997`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_0997`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_0998`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_0998`,
  MIN(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_0999`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_0999`,
  MAX(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1000`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1000`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `metric__a_1009`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1009`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1010`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1010`,
  MIN(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1011`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1011`,
  MAX(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1012`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1012`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `metric__a_1021`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1021`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1022`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1022`,
  MIN(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1023`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1023`,
  MAX(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1024`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1024`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `metric__a_1033`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1033`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1034`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1034`,
  MIN(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1035`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1035`,
  MAX(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1036`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1036`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `metric__a_1045`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1045`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1046`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1046`,
  MIN(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1047`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1047`,
  MAX(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1048`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1048`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `metric__a_1057`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1057`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1058`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1058`,
  MIN(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1059`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1059`,
  MAX(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1060`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1060`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `metric__a_1069`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1069`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1070`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1070`,
  MIN(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1071`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1071`,
  MAX(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1072`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1072`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__a_1085`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1085`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1086`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1086`,
  MIN(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1087`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1087`,
  MAX(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1088`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1088`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `metric__a_1097`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1097`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1098`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1098`,
  MIN(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1099`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1099`,
  MAX(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1100`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1100`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__a_1109`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1109`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1110`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1110`,
  MIN(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1111`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1111`,
  MAX(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1112`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1112`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `metric__a_1121`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1121`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1122`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1122`,
  MIN(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1123`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1123`,
  MAX(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1124`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1124`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `metric__a_1133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1134`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1134`,
  MIN(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1135`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1135`,
  MAX(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1136`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1136`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `metric__a_1145`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1145`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1146`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1146`,
  MIN(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1147`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1147`,
  MAX(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1148`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1148`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `metric__a_1157`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1157`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1158`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1158`,
  MIN(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1159`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1159`,
  MAX(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1160`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1160`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `metric__a_1169`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1169`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1170`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1170`,
  MIN(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1171`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1171`,
  MAX(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1172`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1172`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `metric__a_1181`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1181`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1182`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1182`,
  MIN(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1183`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1183`,
  MAX(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1184`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1184`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `metric__a_1193`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1193`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1194`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1194`,
  MIN(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1195`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1195`,
  MAX(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1196`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1196`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `metric__a_1205`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1205`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1206`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1206`,
  MIN(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1207`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1207`,
  MAX(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1208`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1208`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `metric__a_1217`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1217`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1218`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1218`,
  MIN(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1219`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1219`,
  MAX(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1220`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1220`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `metric__a_1229`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1229`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1230`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1230`,
  MIN(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1231`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1231`,
  MAX(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1232`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1232`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `metric__a_1241`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1241`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1242`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1242`,
  MIN(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1243`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1243`,
  MAX(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1244`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1244`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `metric__a_1253`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1253`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1254`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1254`,
  MIN(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1255`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1255`,
  MAX(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1256`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1256`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `metric__a_1265`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1265`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1266`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1266`,
  MIN(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1267`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1267`,
  MAX(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1268`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1268`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__a_1277`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1277`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1278`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1278`,
  MIN(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1279`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1279`,
  MAX(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1280`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1280`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `metric__a_1289`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1289`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1290`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1290`,
  MIN(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1291`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1291`,
  MAX(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1292`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1292`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `metric__a_1301`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1301`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1302`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1302`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1303`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1303`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1304`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1304`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `metric__a_1313`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1313`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1314`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1314`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1315`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1315`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1316`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1316`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `metric__a_1325`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1325`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1326`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1326`,
  MIN(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1327`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1327`,
  MAX(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1328`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1328`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `metric__a_1337`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1337`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1338`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1338`,
  MIN(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1339`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1339`,
  MAX(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1340`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1340`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `metric__a_1349`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1349`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1350`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1350`,
  MIN(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1351`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1351`,
  MAX(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1352`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1352`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `metric__a_1361`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1361`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1362`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1362`,
  MIN(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1363`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1363`,
  MAX(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1364`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1364`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `metric__a_1373`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1373`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1374`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1374`,
  MIN(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1375`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1375`,
  MAX(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1376`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1376`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `metric__a_1385`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1385`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1386`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1386`,
  MIN(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1387`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1387`,
  MAX(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1388`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1388`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `metric__a_1397`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1397`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1398`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1398`,
  MIN(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1399`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1399`,
  MAX(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1400`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1400`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `metric__a_1409`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1409`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1410`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1410`,
  MIN(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1411`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1411`,
  MAX(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1412`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1412`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `metric__a_1421`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1421`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1422`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1422`,
  MIN(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1423`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1423`,
  MAX(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1424`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1424`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `metric__a_1433`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1433`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1434`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1434`,
  MIN(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1435`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1435`,
  MAX(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1436`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1436`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `metric__a_1445`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1445`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1446`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1446`,
  MIN(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1447`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1447`,
  MAX(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1448`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1448`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `metric__a_1457`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1457`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1458`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1458`,
  MIN(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1459`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1459`,
  MAX(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1460`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1460`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `metric__a_1469`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1469`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1470`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1470`,
  MIN(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1471`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1471`,
  MAX(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1472`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1472`,
  COUNT(DISTINCT(p.card_type)) AS `metric__a_1888`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__a_1889`,
  COUNT(DISTINCT(p.mt_gateway)) AS `metric__a_1890`
FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1775262981546
GROUP BY p.check_bank_routing_number;
```

#### Original Params

```json
[
  "322271627"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=140.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	12.20	1	root		time:92.4ms, open:245.9µs, close:43.6µs, loops:2, RU:87.43, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#183, Column#186, Column#183, Column#187, Column#187, Column#188, Column#187, Column#189, Column#187, Column#190, Column#187, Column#191, Column#191, Column#192, Column#191, Column#193, Column#191, Column#194, Column#191, Column#195, Column#195, Column#196, Column#195, Column#197, Column#195, Column#198, Column#195, Column#199, Column#199, Column#200, Column#199, Column#201, Column#199, Column#202, Column#199, Column#203, Column#203, Column#204, Column#203, Column#205, Column#203, Column#206, Column#203, Column#207, Column#207, Column#208, Column#207, Column#209, Column#207, Column#210, Column#207, Column#211, Column#212, Column#213	230.1 KB	N/A
└─HashAgg_9	12.20	1	root		time:92ms, open:137.8µs, close:41.6µs, loops:2	group by:Column#1528, funcs:count(?)->Column#47, funcs:sum(Column#1362)->Column#48, funcs:min(Column#1363)->Column#49, funcs:max(Column#1364)->Column#50, funcs:sum(Column#1365)->Column#51, funcs:sum(Column#1366)->Column#52, funcs:min(Column#1367)->Column#53, funcs:max(Column#1368)->Column#54, funcs:sum(Column#1369)->Column#55, funcs:sum(Column#1370)->Column#56, funcs:min(Column#1371)->Column#57, funcs:max(Column#1372)->Column#58, funcs:sum(Column#1373)->Column#59, funcs:sum(Column#1374)->Column#60, funcs:min(Column#1375)->Column#61, funcs:max(Column#1376)->Column#62, funcs:sum(Column#1377)->Column#63, funcs:sum(Column#1378)->Column#64, funcs:min(Column#1379)->Column#65, funcs:max(Column#1380)->Column#66, funcs:sum(Column#1381)->Column#67, funcs:sum(Column#1382)->Column#68, funcs:min(Column#1383)->Column#69, funcs:max(Column#1384)->Column#70, funcs:sum(Column#1385)->Column#71, funcs:sum(Column#1386)->Column#72, funcs:min(Column#1387)->Column#73, funcs:max(Column#1388)->Column#74, funcs:sum(Column#1389)->Column#75, funcs:sum(Column#1390)->Column#76, funcs:min(Column#1391)->Column#77, funcs:max(Column#1392)->Column#78, funcs:sum(Column#1393)->Column#79, funcs:sum(Column#1394)->Column#80, funcs:min(Column#1395)->Column#81, funcs:max(Column#1396)->Column#82, funcs:sum(Column#1397)->Column#83, funcs:sum(Column#1398)->Column#84, funcs:min(Column#1399)->Column#85, funcs:max(Column#1400)->Column#86, funcs:sum(Column#1401)->Column#87, funcs:sum(Column#1402)->Column#88, funcs:min(Column#1403)->Column#89, funcs:max(Column#1404)->Column#90, funcs:sum(Column#1405)->Column#91, funcs:sum(Column#1406)->Column#92, funcs:min(Column#1407)->Column#93, funcs:max(Column#1408)->Column#94, funcs:sum(Column#1409)->Column#95, funcs:sum(Column#1410)->Column#96, funcs:min(Column#1411)->Column#97, funcs:max(Column#1412)->Column#98, funcs:sum(Column#1413)->Column#99, funcs:sum(Column#1414)->Column#100, funcs:min(Column#1415)->Column#101, funcs:max(Column#1416)->Column#102, funcs:sum(Column#1417)->Column#103, funcs:sum(Column#1418)->Column#104, funcs:min(Column#1419)->Column#105, funcs:max(Column#1420)->Column#106, funcs:sum(Column#1421)->Column#107, funcs:sum(Column#1422)->Column#108, funcs:min(Column#1423)->Column#109, funcs:max(Column#1424)->Column#110, funcs:sum(Column#1425)->Column#111, funcs:sum(Column#1426)->Column#112, funcs:min(Column#1427)->Column#113, funcs:max(Column#1428)->Column#114, funcs:sum(Column#1429)->Column#115, funcs:sum(Column#1430)->Column#116, funcs:min(Column#1431)->Column#117, funcs:max(Column#1432)->Column#118, funcs:sum(Column#1433)->Column#119, funcs:sum(Column#1434)->Column#120, funcs:min(Column#1435)->Column#121, funcs:max(Column#1436)->Column#122, funcs:sum(Column#1437)->Column#123, funcs:sum(Column#1438)->Column#124, funcs:min(Column#1439)->Column#125, funcs:max(Column#1440)->Column#126, funcs:sum(Column#1441)->Column#127, funcs:sum(Column#1442)->Column#128, funcs:min(Column#1443)->Column#129, funcs:max(Column#1444)->Column#130, funcs:sum(Column#1445)->Column#131, funcs:sum(Column#1446)->Column#132, funcs:min(Column#1447)->Column#133, funcs:max(Column#1448)->Column#134, funcs:sum(Column#1449)->Column#135, funcs:sum(Column#1450)->Column#136, funcs:min(Column#1451)->Column#137, funcs:max(Column#1452)->Column#138, funcs:sum(Column#1453)->Column#139, funcs:sum(Column#1454)->Column#140, funcs:min(Column#1455)->Column#141, funcs:max(Column#1456)->Column#142, funcs:sum(Column#1457)->Column#143, funcs:sum(Column#1458)->Column#144, funcs:min(Column#1459)->Column#145, funcs:max(Column#1460)->Column#146, funcs:sum(Column#1461)->Column#147, funcs:sum(Column#1462)->Column#148, funcs:min(Column#1463)->Column#149, funcs:max(Column#1464)->Column#150, funcs:sum(Column#1465)->Column#151, funcs:sum(Column#1466)->Column#152, funcs:min(Column#1467)->Column#153, funcs:max(Column#1468)->Column#154, funcs:sum(Column#1469)->Column#155, funcs:sum(Column#1470)->Column#156, funcs:min(Column#1471)->Column#157, funcs:max(Column#1472)->Column#158, funcs:sum(Column#1473)->Column#159, funcs:sum(Column#1474)->Column#160, funcs:min(Column#1475)->Column#161, funcs:max(Column#1476)->Column#162, funcs:sum(Column#1477)->Column#163, funcs:sum(Column#1478)->Column#164, funcs:min(Column#1479)->Column#165, funcs:max(Column#1480)->Column#166, funcs:sum(Column#1481)->Column#167, funcs:sum(Column#1482)->Column#168, funcs:min(Column#1483)->Column#169, funcs:max(Column#1484)->Column#170, funcs:sum(Column#1485)->Column#171, funcs:sum(Column#1486)->Column#172, funcs:min(Column#1487)->Column#173, funcs:max(Column#1488)->Column#174, funcs:sum(Column#1489)->Column#175, funcs:sum(Column#1490)->Column#176, funcs:min(Column#1491)->Column#177, funcs:max(Column#1492)->Column#178, funcs:sum(Column#1493)->Column#179, funcs:sum(Column#1494)->Column#180, funcs:min(Column#1495)->Column#181, funcs:max(Column#1496)->Column#182, funcs:sum(Column#1497)->Column#183, funcs:sum(Column#1498)->Column#184, funcs:min(Column#1499)->Column#185, funcs:max(Column#1500)->Column#186, funcs:sum(Column#1501)->Column#187, funcs:sum(Column#1502)->Column#188, funcs:min(Column#1503)->Column#189, funcs:max(Column#1504)->Column#190, funcs:sum(Column#1505)->Column#191, funcs:sum(Column#1506)->Column#192, funcs:min(Column#1507)->Column#193, funcs:max(Column#1508)->Column#194, funcs:sum(Column#1509)->Column#195, funcs:sum(Column#1510)->Column#196, funcs:min(Column#1511)->Column#197, funcs:max(Column#1512)->Column#198, funcs:sum(Column#1513)->Column#199, funcs:sum(Column#1514)->Column#200, funcs:min(Column#1515)->Column#201, funcs:max(Column#1516)->Column#202, funcs:sum(Column#1517)->Column#203, funcs:sum(Column#1518)->Column#204, funcs:min(Column#1519)->Column#205, funcs:max(Column#1520)->Column#206, funcs:sum(Column#1521)->Column#207, funcs:sum(Column#1522)->Column#208, funcs:min(Column#1523)->Column#209, funcs:max(Column#1524)->Column#210, funcs:count(distinct Column#1525)->Column#211, funcs:count(distinct Column#1526)->Column#212, funcs:count(distinct Column#1527)->Column#213	6.49 MB	0 Bytes
  └─Projection_41	138073.00	27634	root		time:14.8ms, open:74µs, close:40.4µs, loops:29, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#1362, intuit_risk.pmt_txn_fact.amount->Column#1363, intuit_risk.pmt_txn_fact.amount->Column#1364, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1365, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1366, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1367, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1368, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1369, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1370, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1371, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1372, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1373, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1374, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1375, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1376, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1377, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1378, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1379, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1380, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1381, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1382, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1383, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1384, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1385, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1386, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1387, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1388, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1389, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1390, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1391, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1392, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1393, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1394, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1395, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1396, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1397, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1398, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1399, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1400, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1401, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1402, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1403, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1404, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1405, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1406, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1407, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1408, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1409, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1410, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1411, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1412, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1413, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1414, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1415, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1416, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1417, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1418, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1419, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1420, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1421, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1422, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1423, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1424, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1425, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1426, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1427, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1428, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1429, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1430, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1431, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1432, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1433, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1434, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1435, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1436, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1437, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1438, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1439, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1440, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1441, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1442, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1443, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1444, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1445, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1446, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1447, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1448, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1449, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1450, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1451, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1452, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1453, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1454, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1455, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1456, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1457, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1458, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1459, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1460, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1461, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1462, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1463, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1464, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1465, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1466, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1467, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1468, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1469, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1470, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1471, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1472, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1473, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1474, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1475, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1476, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1477, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1478, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1479, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1480, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1481, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1482, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1483, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1484, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1485, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1486, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1487, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1488, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1489, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1490, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1491, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1492, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1493, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1494, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1495, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1496, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1497, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1498, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1499, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1500, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1501, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1502, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1503, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1504, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1505, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1506, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1507, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1508, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1509, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1510, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1511, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1512, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1513, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1514, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1515, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1516, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1517, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1518, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1519, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1520, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1521, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1522, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1523, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1524, intuit_risk.pmt_txn_fact.card_type->Column#1525, intuit_risk.pmt_txn_fact.entry_method->Column#1526, intuit_risk.pmt_txn_fact.mt_gateway->Column#1527, intuit_risk.pmt_txn_fact.check_bank_routing_number->Column#1528	32.9 MB	N/A
    └─IndexReader_29	138073.00	27634	root	partition:p20260501,p20260601,pmax	time:8.04ms, open:72.6µs, close:11.6µs, loops:29, cop_task: {num: 10, max: 8.18ms, min: 762.2µs, avg: 2.8ms, p95: 8.18ms, max_proc_keys: 9184, p95_proc_keys: 9184, tot_proc: 18.9ms, tot_wait: 359.7µs, copr_cache: disabled, build_task_duration: 19.7µs, max_distsql_concurrency: 3}, fetch_resp_duration: 7.19ms, rpc_info:{Cop:{num_rpc:10, total_time:27.8ms}}	index:IndexRangeScan_28	1.76 MB	N/A
      └─IndexRangeScan_28	138073.00	27634	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:60, tasks:10}, scan_detail: {total_process_keys: 27634, total_process_keys_size: 5005030, total_keys: 27644, get_snapshot_time: 165.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.9ms, total_suspend_time: 48.4µs, total_wait_time: 359.7µs, total_kv_read_wall_time: 20ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0037`,
  SUM(p.amount) AS `metric__a_0038`,
  MIN(p.amount) AS `metric__a_0039`,
  MAX(p.amount) AS `metric__a_0040`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `metric__a_0997`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_0997`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_0998`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_0998`,
  MIN(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_0999`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_0999`,
  MAX(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1000`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1000`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `metric__a_1009`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1009`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1010`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1010`,
  MIN(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1011`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1011`,
  MAX(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1012`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1012`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `metric__a_1021`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1021`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1022`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1022`,
  MIN(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1023`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1023`,
  MAX(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1024`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1024`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `metric__a_1033`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1033`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1034`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1034`,
  MIN(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1035`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1035`,
  MAX(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1036`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1036`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `metric__a_1045`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1045`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1046`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1046`,
  MIN(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1047`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1047`,
  MAX(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1048`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1048`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `metric__a_1057`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1057`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1058`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1058`,
  MIN(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1059`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1059`,
  MAX(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1060`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1060`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `metric__a_1069`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1069`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1070`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1070`,
  MIN(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1071`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1071`,
  MAX(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1072`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1072`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__a_1085`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1085`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1086`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1086`,
  MIN(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1087`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1087`,
  MAX(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_1088`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_1088`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `metric__a_1097`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1097`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1098`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1098`,
  MIN(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1099`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1099`,
  MAX(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_1100`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_1100`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__a_1109`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1109`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1110`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1110`,
  MIN(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1111`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1111`,
  MAX(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_1112`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_1112`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `metric__a_1121`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1121`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1122`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1122`,
  MIN(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1123`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1123`,
  MAX(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_1124`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_1124`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `metric__a_1133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1134`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1134`,
  MIN(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1135`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1135`,
  MAX(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_1136`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_1136`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `metric__a_1145`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1145`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1146`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1146`,
  MIN(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1147`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1147`,
  MAX(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_1148`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_1148`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `metric__a_1157`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1157`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1158`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1158`,
  MIN(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1159`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1159`,
  MAX(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_1160`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_1160`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `metric__a_1169`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1169`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1170`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1170`,
  MIN(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1171`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1171`,
  MAX(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_1172`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_1172`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `metric__a_1181`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1181`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1182`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1182`,
  MIN(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1183`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1183`,
  MAX(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_1184`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_1184`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `metric__a_1193`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1193`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1194`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1194`,
  MIN(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1195`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1195`,
  MAX(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_1196`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_1196`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `metric__a_1205`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1205`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1206`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1206`,
  MIN(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1207`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1207`,
  MAX(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_1208`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_1208`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `metric__a_1217`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1217`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1218`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1218`,
  MIN(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1219`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1219`,
  MAX(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_1220`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_1220`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `metric__a_1229`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1229`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1230`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1230`,
  MIN(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1231`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1231`,
  MAX(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_1232`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_1232`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `metric__a_1241`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1241`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1242`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1242`,
  MIN(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1243`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1243`,
  MAX(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_1244`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_1244`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `metric__a_1253`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1253`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1254`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1254`,
  MIN(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1255`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1255`,
  MAX(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_1256`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_1256`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `metric__a_1265`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1265`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1266`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1266`,
  MIN(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1267`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1267`,
  MAX(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_1268`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_1268`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__a_1277`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1277`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1278`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1278`,
  MIN(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1279`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1279`,
  MAX(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_1280`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_1280`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `metric__a_1289`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1289`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1290`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1290`,
  MIN(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1291`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1291`,
  MAX(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_1292`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_1292`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `metric__a_1301`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1301`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1302`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1302`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1303`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1303`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_1304`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_1304`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `metric__a_1313`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1313`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1314`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1314`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1315`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1315`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_1316`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_1316`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `metric__a_1325`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1325`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1326`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1326`,
  MIN(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1327`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1327`,
  MAX(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_1328`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_1328`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `metric__a_1337`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1337`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1338`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1338`,
  MIN(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1339`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1339`,
  MAX(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_1340`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_1340`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `metric__a_1349`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1349`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1350`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1350`,
  MIN(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1351`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1351`,
  MAX(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_1352`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_1352`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `metric__a_1361`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1361`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1362`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1362`,
  MIN(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1363`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1363`,
  MAX(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_1364`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_1364`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `metric__a_1373`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1373`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1374`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1374`,
  MIN(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1375`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1375`,
  MAX(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_1376`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_1376`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `metric__a_1385`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1385`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1386`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1386`,
  MIN(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1387`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1387`,
  MAX(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_1388`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_1388`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `metric__a_1397`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1397`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1398`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1398`,
  MIN(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1399`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1399`,
  MAX(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_1400`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_1400`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `metric__a_1409`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1409`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1410`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1410`,
  MIN(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1411`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1411`,
  MAX(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_1412`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_1412`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `metric__a_1421`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1421`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1422`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1422`,
  MIN(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1423`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1423`,
  MAX(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_1424`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_1424`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `metric__a_1433`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1433`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1434`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1434`,
  MIN(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1435`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1435`,
  MAX(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_1436`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_1436`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `metric__a_1445`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1445`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1446`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1446`,
  MIN(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1447`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1447`,
  MAX(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_1448`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_1448`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `metric__a_1457`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1457`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1458`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1458`,
  MIN(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1459`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1459`,
  MAX(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_1460`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_1460`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `metric__a_1469`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1469`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1470`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1470`,
  MIN(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1471`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1471`,
  MAX(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_1472`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_1472`,
  COUNT(DISTINCT(p.card_type)) AS `metric__a_1888`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__a_1889`,
  COUNT(DISTINCT(p.mt_gateway)) AS `metric__a_1890`
FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1775262981546
GROUP BY p.check_bank_routing_number;
```

#### Optimized Params

```json
[
  "322271627"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_default
-- explain_analyze_elapsed_ms=143.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	12.20	1	root		time:94.3ms, open:241µs, close:42.3µs, loops:2, RU:87.34, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#183, Column#186, Column#183, Column#187, Column#187, Column#188, Column#187, Column#189, Column#187, Column#190, Column#187, Column#191, Column#191, Column#192, Column#191, Column#193, Column#191, Column#194, Column#191, Column#195, Column#195, Column#196, Column#195, Column#197, Column#195, Column#198, Column#195, Column#199, Column#199, Column#200, Column#199, Column#201, Column#199, Column#202, Column#199, Column#203, Column#203, Column#204, Column#203, Column#205, Column#203, Column#206, Column#203, Column#207, Column#207, Column#208, Column#207, Column#209, Column#207, Column#210, Column#207, Column#211, Column#212, Column#213	231.3 KB	N/A
└─HashAgg_9	12.20	1	root		time:93.8ms, open:127.4µs, close:40.5µs, loops:2	group by:Column#1528, funcs:count(?)->Column#47, funcs:sum(Column#1362)->Column#48, funcs:min(Column#1363)->Column#49, funcs:max(Column#1364)->Column#50, funcs:sum(Column#1365)->Column#51, funcs:sum(Column#1366)->Column#52, funcs:min(Column#1367)->Column#53, funcs:max(Column#1368)->Column#54, funcs:sum(Column#1369)->Column#55, funcs:sum(Column#1370)->Column#56, funcs:min(Column#1371)->Column#57, funcs:max(Column#1372)->Column#58, funcs:sum(Column#1373)->Column#59, funcs:sum(Column#1374)->Column#60, funcs:min(Column#1375)->Column#61, funcs:max(Column#1376)->Column#62, funcs:sum(Column#1377)->Column#63, funcs:sum(Column#1378)->Column#64, funcs:min(Column#1379)->Column#65, funcs:max(Column#1380)->Column#66, funcs:sum(Column#1381)->Column#67, funcs:sum(Column#1382)->Column#68, funcs:min(Column#1383)->Column#69, funcs:max(Column#1384)->Column#70, funcs:sum(Column#1385)->Column#71, funcs:sum(Column#1386)->Column#72, funcs:min(Column#1387)->Column#73, funcs:max(Column#1388)->Column#74, funcs:sum(Column#1389)->Column#75, funcs:sum(Column#1390)->Column#76, funcs:min(Column#1391)->Column#77, funcs:max(Column#1392)->Column#78, funcs:sum(Column#1393)->Column#79, funcs:sum(Column#1394)->Column#80, funcs:min(Column#1395)->Column#81, funcs:max(Column#1396)->Column#82, funcs:sum(Column#1397)->Column#83, funcs:sum(Column#1398)->Column#84, funcs:min(Column#1399)->Column#85, funcs:max(Column#1400)->Column#86, funcs:sum(Column#1401)->Column#87, funcs:sum(Column#1402)->Column#88, funcs:min(Column#1403)->Column#89, funcs:max(Column#1404)->Column#90, funcs:sum(Column#1405)->Column#91, funcs:sum(Column#1406)->Column#92, funcs:min(Column#1407)->Column#93, funcs:max(Column#1408)->Column#94, funcs:sum(Column#1409)->Column#95, funcs:sum(Column#1410)->Column#96, funcs:min(Column#1411)->Column#97, funcs:max(Column#1412)->Column#98, funcs:sum(Column#1413)->Column#99, funcs:sum(Column#1414)->Column#100, funcs:min(Column#1415)->Column#101, funcs:max(Column#1416)->Column#102, funcs:sum(Column#1417)->Column#103, funcs:sum(Column#1418)->Column#104, funcs:min(Column#1419)->Column#105, funcs:max(Column#1420)->Column#106, funcs:sum(Column#1421)->Column#107, funcs:sum(Column#1422)->Column#108, funcs:min(Column#1423)->Column#109, funcs:max(Column#1424)->Column#110, funcs:sum(Column#1425)->Column#111, funcs:sum(Column#1426)->Column#112, funcs:min(Column#1427)->Column#113, funcs:max(Column#1428)->Column#114, funcs:sum(Column#1429)->Column#115, funcs:sum(Column#1430)->Column#116, funcs:min(Column#1431)->Column#117, funcs:max(Column#1432)->Column#118, funcs:sum(Column#1433)->Column#119, funcs:sum(Column#1434)->Column#120, funcs:min(Column#1435)->Column#121, funcs:max(Column#1436)->Column#122, funcs:sum(Column#1437)->Column#123, funcs:sum(Column#1438)->Column#124, funcs:min(Column#1439)->Column#125, funcs:max(Column#1440)->Column#126, funcs:sum(Column#1441)->Column#127, funcs:sum(Column#1442)->Column#128, funcs:min(Column#1443)->Column#129, funcs:max(Column#1444)->Column#130, funcs:sum(Column#1445)->Column#131, funcs:sum(Column#1446)->Column#132, funcs:min(Column#1447)->Column#133, funcs:max(Column#1448)->Column#134, funcs:sum(Column#1449)->Column#135, funcs:sum(Column#1450)->Column#136, funcs:min(Column#1451)->Column#137, funcs:max(Column#1452)->Column#138, funcs:sum(Column#1453)->Column#139, funcs:sum(Column#1454)->Column#140, funcs:min(Column#1455)->Column#141, funcs:max(Column#1456)->Column#142, funcs:sum(Column#1457)->Column#143, funcs:sum(Column#1458)->Column#144, funcs:min(Column#1459)->Column#145, funcs:max(Column#1460)->Column#146, funcs:sum(Column#1461)->Column#147, funcs:sum(Column#1462)->Column#148, funcs:min(Column#1463)->Column#149, funcs:max(Column#1464)->Column#150, funcs:sum(Column#1465)->Column#151, funcs:sum(Column#1466)->Column#152, funcs:min(Column#1467)->Column#153, funcs:max(Column#1468)->Column#154, funcs:sum(Column#1469)->Column#155, funcs:sum(Column#1470)->Column#156, funcs:min(Column#1471)->Column#157, funcs:max(Column#1472)->Column#158, funcs:sum(Column#1473)->Column#159, funcs:sum(Column#1474)->Column#160, funcs:min(Column#1475)->Column#161, funcs:max(Column#1476)->Column#162, funcs:sum(Column#1477)->Column#163, funcs:sum(Column#1478)->Column#164, funcs:min(Column#1479)->Column#165, funcs:max(Column#1480)->Column#166, funcs:sum(Column#1481)->Column#167, funcs:sum(Column#1482)->Column#168, funcs:min(Column#1483)->Column#169, funcs:max(Column#1484)->Column#170, funcs:sum(Column#1485)->Column#171, funcs:sum(Column#1486)->Column#172, funcs:min(Column#1487)->Column#173, funcs:max(Column#1488)->Column#174, funcs:sum(Column#1489)->Column#175, funcs:sum(Column#1490)->Column#176, funcs:min(Column#1491)->Column#177, funcs:max(Column#1492)->Column#178, funcs:sum(Column#1493)->Column#179, funcs:sum(Column#1494)->Column#180, funcs:min(Column#1495)->Column#181, funcs:max(Column#1496)->Column#182, funcs:sum(Column#1497)->Column#183, funcs:sum(Column#1498)->Column#184, funcs:min(Column#1499)->Column#185, funcs:max(Column#1500)->Column#186, funcs:sum(Column#1501)->Column#187, funcs:sum(Column#1502)->Column#188, funcs:min(Column#1503)->Column#189, funcs:max(Column#1504)->Column#190, funcs:sum(Column#1505)->Column#191, funcs:sum(Column#1506)->Column#192, funcs:min(Column#1507)->Column#193, funcs:max(Column#1508)->Column#194, funcs:sum(Column#1509)->Column#195, funcs:sum(Column#1510)->Column#196, funcs:min(Column#1511)->Column#197, funcs:max(Column#1512)->Column#198, funcs:sum(Column#1513)->Column#199, funcs:sum(Column#1514)->Column#200, funcs:min(Column#1515)->Column#201, funcs:max(Column#1516)->Column#202, funcs:sum(Column#1517)->Column#203, funcs:sum(Column#1518)->Column#204, funcs:min(Column#1519)->Column#205, funcs:max(Column#1520)->Column#206, funcs:sum(Column#1521)->Column#207, funcs:sum(Column#1522)->Column#208, funcs:min(Column#1523)->Column#209, funcs:max(Column#1524)->Column#210, funcs:count(distinct Column#1525)->Column#211, funcs:count(distinct Column#1526)->Column#212, funcs:count(distinct Column#1527)->Column#213	6.49 MB	0 Bytes
  └─Projection_41	138073.00	27634	root		time:15.5ms, open:65.3µs, close:39.7µs, loops:29, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#1362, intuit_risk.pmt_txn_fact.amount->Column#1363, intuit_risk.pmt_txn_fact.amount->Column#1364, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1365, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1366, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1367, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1368, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1369, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1370, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1371, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1372, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1373, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1374, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1375, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1376, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1377, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1378, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1379, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1380, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1381, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1382, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1383, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1384, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1385, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1386, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1387, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1388, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1389, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1390, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1391, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1392, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1393, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1394, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1395, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1396, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1397, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1398, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1399, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1400, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1401, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1402, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1403, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1404, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1405, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1406, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1407, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1408, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1409, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1410, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1411, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1412, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1413, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1414, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1415, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1416, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1417, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1418, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1419, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1420, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1421, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1422, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1423, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1424, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1425, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1426, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1427, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1428, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1429, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1430, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1431, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1432, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1433, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1434, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1435, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1436, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1437, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1438, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1439, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1440, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1441, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1442, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1443, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1444, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1445, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1446, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1447, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1448, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1449, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1450, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1451, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1452, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1453, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1454, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1455, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1456, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1457, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1458, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1459, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1460, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1461, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1462, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1463, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1464, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1465, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1466, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1467, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1468, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1469, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1470, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1471, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1472, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1473, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1474, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1475, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1476, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1477, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1478, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1479, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1480, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1481, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1482, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1483, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1484, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1485, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1486, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1487, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1488, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1489, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1490, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1491, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1492, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1493, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1494, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1495, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1496, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1497, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1498, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1499, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1500, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1501, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1502, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1503, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1504, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1505, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1506, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1507, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1508, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1509, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1510, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1511, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1512, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1513, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1514, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1515, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1516, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1517, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1518, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1519, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1520, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1521, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1522, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1523, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1524, intuit_risk.pmt_txn_fact.card_type->Column#1525, intuit_risk.pmt_txn_fact.entry_method->Column#1526, intuit_risk.pmt_txn_fact.mt_gateway->Column#1527, intuit_risk.pmt_txn_fact.check_bank_routing_number->Column#1528	32.9 MB	N/A
    └─IndexReader_29	138073.00	27634	root	partition:p20260501,p20260601,pmax	time:8.03ms, open:64µs, close:11.3µs, loops:29, cop_task: {num: 10, max: 7.57ms, min: 659.6µs, avg: 2.74ms, p95: 7.57ms, max_proc_keys: 9184, p95_proc_keys: 9184, tot_proc: 18.7ms, tot_wait: 352.2µs, copr_cache: disabled, build_task_duration: 15.6µs, max_distsql_concurrency: 3}, fetch_resp_duration: 7.18ms, rpc_info:{Cop:{num_rpc:10, total_time:27.3ms}}	index:IndexRangeScan_28	1.76 MB	N/A
      └─IndexRangeScan_28	138073.00	27634	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:60, tasks:10}, scan_detail: {total_process_keys: 27634, total_process_keys_size: 5005030, total_keys: 27644, get_snapshot_time: 154.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.7ms, total_suspend_time: 48µs, total_wait_time: 352.2µs, total_kv_read_wall_time: 20ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 3. group_c_bundle_025

- Filter/window: `p.merchant_account_number = %s` / `180d`
- Chosen event: `INV0007318468` kind=`normal` error=`(1105, "other error for mpp stream: Code: 0, e.displayText() = DB::Exception: Memory limit (total) exceeded caused by 'RSS(Resident Set Size) much larger than limit' : process memory size would be 4.76 GiB for (attempt to allocate chunk of 1602419 bytes), limit of memory for data computing : 3.76 Gi`
- Optimization: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 2325.0 ms | ok |
| `optimized_default` | `{}` | 163.2 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 227.9 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 235.9 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 209.6 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 161.1 ms | ok |

#### Original SQL

```sql
SELECT
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0211' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.smart_id AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.smart_id IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0211`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0212' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.exact_id IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0212`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0213' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.input_ip AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.input_ip IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0213`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0214' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.true_ip AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.true_ip IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0214`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0215' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.proxy_ip AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.proxy_ip IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0215`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0216' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.agent_type AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.agent_type IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0216`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_025' AND x.template_id = 'c_0217' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12' UNION ALL SELECT CAST(d.agent_os AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE p.merchant_account_number = %s AND d.agent_os IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')) u) AS `metric__c_0217`;
```

#### Original Params

```json
[
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111",
  "5247719970153111"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=2325.0
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_1024	1.00	1	root		time:10.6µs, open:3.64µs, close:1.01µs, loops:2, RU:4425.86, Concurrency:OFF	?->Column#1756, ?->Column#1914, ?->Column#2066, ?->Column#2220, ?->Column#2424, ?->Column#2648, ?->Column#2832	0 Bytes	N/A
└─TableDual_1026	1.00	1	root		time:1.94µs, open:252ns, close:185ns, loops:2	rows:1	N/A	N/A
ScalarSubQuery_240	N/A	0	root			Output: ScalarQueryCol#1755	N/A	N/A
└─MaxOneRow_138	1.00	1	root		time:688.8ms, open:9.83µs, close:39.6µs, loops:1		N/A	N/A
  └─HashAgg_143	1.00	1	root		time:688.8ms, open:8.99µs, close:39.1µs, loops:2	funcs:count(distinct Column#1711)->Column#1712	384.6 KB	0 Bytes
    └─Union_147	10626.55	3755	root		time:687.7ms, open:902ns, close:38.2µs, loops:7		N/A	N/A
      ├─Projection_149	66.33	3749	root		time:23.7ms, open:528.7µs, close:10µs, loops:6, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1711	145.7 KB	N/A
      │ └─IndexReader_153	66.33	3749	root		time:23.4ms, open:523.2µs, close:6.7µs, loops:6, cop_task: {num: 5, max: 11.6ms, min: 1.08ms, avg: 4.7ms, p95: 11.6ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 13.6ms, tot_wait: 1.91ms, copr_cache: disabled, build_task_duration: 470.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 22.7ms, rpc_info:{Cop:{num_rpc:5, total_time:23.4ms}}	index:Selection_152	377.9 KB	N/A
      │   └─Selection_152	66.33	3749	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 4ms, p80:10ms, p95:10ms, iters:20, tasks:5}, scan_detail: {total_process_keys: 3749, total_process_keys_size: 1075963, total_keys: 3754, get_snapshot_time: 1.81ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 13.6ms, total_suspend_time: 14.4µs, total_wait_time: 1.91ms, total_kv_read_wall_time: 20ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_151	66.43	3749	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 4ms, p80:10ms, p95:10ms, iters:20, tasks:5}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_154	10560.23	6	root		time:688.7ms, open:974.3µs, close:27.3µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1711	45.2 KB	N/A
        └─IndexHashJoin_164	10560.23	6	root		time:688.6ms, open:972.9µs, close:8.32µs, loops:2, inner:{total:1.32s, concurrency:5, task:2, construct:3.4ms, fetch:1.31s, build:719.2µs, join:4.93ms}	inner join, inner:IndexLookUp_180, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.14 MB	N/A
          ├─IndexReader_175(Build)	5970.05	5192	root	partition:all	time:11.9ms, open:970.8µs, close:5.65µs, loops:8, cop_task: {num: 21, max: 7.22ms, min: 718.5µs, avg: 2.31ms, p95: 4.65ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 20.1ms, tot_wait: 8.43ms, copr_cache: disabled, build_task_duration: 905.8µs, max_distsql_concurrency: 9}, fetch_resp_duration: 10.5ms, rpc_info:{Cop:{num_rpc:21, total_time:48.3ms}}	index:Selection_174	40.3 KB	N/A
          │ └─Selection_174	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 8.02ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 20.1ms, total_suspend_time: 31.5µs, total_wait_time: 8.43ms, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_173	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_180(Probe)	10560.23	3752	root	partition:all	total_time:1.31s, total_open:15.2ms, total_close:14.8µs, loops:7, index_task: {total_time: 1.05s, fetch_handle: 1.05s, build: 11.7µs, wait: 20.8µs}, table_task: {total_time: 882.3ms, num: 12, concurrency: 5}, next: {wait_index: 758.4ms, wait_table_lookup_build: 5.11ms, wait_table_lookup_resp: 532ms}		3.85 MB	N/A
            ├─Selection_178(Build)	13952.57	5192	cop[tikv]		total_time:1.05s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 496ms, min: 3.34ms, avg: 87ms, p95: 441.1ms, max_proc_keys: 763, p95_proc_keys: 504, tot_proc: 2.64s, tot_wait: 7.62ms, copr_cache: disabled, build_task_duration: 67ms, max_distsql_concurrency: 4}, fetch_resp_duration: 1.05s, rpc_info:{Cop:{num_rpc:39, total_time:2.98s}, rpc_errors:{bucket_version_not_match:5}}, backoff{regionMiss: 14ms}, tikv_task:{proc max:490ms, min:0s, avg: 77.4ms, p80:110ms, p95:430ms, iters:87, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 445068, total_keys: 21337, get_snapshot_time: 7.29ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.64s, total_suspend_time: 2.9ms, total_wait_time: 7.62ms, total_kv_read_wall_time: 2.26s}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_176	20599.13	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:490ms, min:0s, avg: 77.4ms, p80:110ms, p95:430ms, iters:87, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_179(Probe)	10560.23	3752	cop[tikv]		total_time:868.1ms, total_open:0s, total_close:76.2µs, loops:24, cop_task: {num: 794, max: 63.7ms, min: 0s, avg: 2.29ms, p95: 8.16ms, max_proc_keys: 33, p95_proc_keys: 18, tot_proc: 1.71s, tot_wait: 328.3ms, copr_cache: disabled, build_task_duration: 11.8ms, max_distsql_concurrency: 7, max_extra_concurrency: 12, store_batch_num: 472, store_batch_fallback_num: 139}, fetch_resp_duration: 864.3ms, rpc_info:{Cop:{num_rpc:477, total_time:2.02s}, rpc_errors:{bucket_version_not_match:155}}, backoff{regionMiss: 1.59s}, tikv_task:{proc max:50ms, min:0s, avg: 1.81ms, p80:0s, p95:10ms, iters:796, tasks:794}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 281.4ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.71s, total_suspend_time: 8.07ms, total_wait_time: 328.3ms, total_kv_read_wall_time: 1.43s}	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	N/A	N/A
              └─TableRowIDScan_177	13952.57	5192	cop[tikv]	table:d	tikv_task:{proc max:50ms, min:0s, avg: 1.8ms, p80:0s, p95:10ms, iters:796, tasks:794}	keep order:false	N/A	N/A
ScalarSubQuery_360	N/A	0	root			Output: ScalarQueryCol#1913	N/A	N/A
└─MaxOneRow_258	1.00	1	root		time:610ms, open:9.89µs, close:29.8µs, loops:1		N/A	N/A
  └─HashAgg_263	1.00	1	root		time:610ms, open:9.38µs, close:29.3µs, loops:2	funcs:count(distinct Column#1871)->Column#1872	384.3 KB	0 Bytes
    └─Union_267	10626.69	3708	root		time:608.9ms, open:862ns, close:28.7µs, loops:6		N/A	N/A
      ├─Projection_269	66.46	3702	root		time:21ms, open:758.9µs, close:8.4µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1871	146.4 KB	N/A
      │ └─IndexReader_273	66.46	3702	root		time:20.7ms, open:730.2µs, close:5.49µs, loops:5, cop_task: {num: 4, max: 9.56ms, min: 1.6ms, avg: 4.98ms, p95: 9.56ms, max_proc_keys: 2006, p95_proc_keys: 2006, tot_proc: 12.3ms, tot_wait: 1.7ms, copr_cache: disabled, build_task_duration: 688.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 19.7ms, rpc_info:{Cop:{num_rpc:4, total_time:19.9ms}}	index:Selection_272	376.3 KB	N/A
      │   └─Selection_272	66.46	3702	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3702, total_process_keys_size: 1062474, total_keys: 3706, get_snapshot_time: 1.64ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 12.3ms, total_suspend_time: 19.3µs, total_wait_time: 1.7ms, total_kv_read_wall_time: 20ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_271	66.57	3702	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_274	10560.23	6	root		time:609.9ms, open:88.2µs, close:19.2µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1871	45.2 KB	N/A
        └─IndexHashJoin_284	10560.23	6	root		time:609.9ms, open:87.2µs, close:4.85µs, loops:2, inner:{total:1.18s, concurrency:5, task:2, construct:3.43ms, fetch:1.17s, build:758.9µs, join:4.7ms}	inner join, inner:IndexLookUp_300, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.09 MB	N/A
          ├─IndexReader_295(Build)	5970.05	5192	root	partition:all	time:3.99ms, open:85.7µs, close:2.74µs, loops:8, cop_task: {num: 21, max: 1.49ms, min: 606.2µs, avg: 943.4µs, p95: 1.34ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 7.1ms, tot_wait: 649.5µs, copr_cache: disabled, build_task_duration: 38.8µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.53ms, rpc_info:{Cop:{num_rpc:21, total_time:19.6ms}}	index:Selection_294	39.9 KB	N/A
          │ └─Selection_294	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 273.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 7.1ms, total_wait_time: 649.5µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_293	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_300(Probe)	10560.23	3705	root	partition:all	total_time:1.17s, total_open:17.7ms, total_close:14.5µs, loops:7, index_task: {total_time: 1.1s, fetch_handle: 1.1s, build: 14.1µs, wait: 38.3µs}, table_task: {total_time: 123.8ms, num: 12, concurrency: 5}, next: {wait_index: 1.09s, wait_table_lookup_build: 1.36ms, wait_table_lookup_resp: 66.1ms}		3.85 MB	N/A
            ├─Selection_298(Build)	14274.48	5192	cop[tikv]		total_time:1.11s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 568ms, min: 1.84ms, avg: 69.4ms, p95: 546.2ms, max_proc_keys: 746, p95_proc_keys: 521, tot_proc: 1.05s, tot_wait: 580.8µs, copr_cache: disabled, build_task_duration: 5.49ms, max_distsql_concurrency: 4}, fetch_resp_duration: 1.11s, rpc_info:{Cop:{num_rpc:34, total_time:2.36s}}, tikv_task:{proc max:90ms, min:0s, avg: 31.2ms, p80:50ms, p95:90ms, iters:87, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 329616, total_keys: 6481, get_snapshot_time: 396.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.05s, total_suspend_time: 656.9µs, total_wait_time: 580.8µs, total_kv_read_wall_time: 320ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_296	21074.40	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 31.2ms, p80:50ms, p95:90ms, iters:87, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_299(Probe)	10560.23	3705	cop[tikv]		total_time:119.1ms, total_open:0s, total_close:62.8µs, loops:24, cop_task: {num: 807, max: 3.09ms, min: 0s, avg: 351.7µs, p95: 1.74ms, max_proc_keys: 32, p95_proc_keys: 19, tot_proc: 286.5ms, tot_wait: 151.6ms, copr_cache: disabled, build_task_duration: 2.32ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 589, store_batch_fallback_num: 32}, fetch_resp_duration: 115.9ms, rpc_info:{Cop:{num_rpc:218, total_time:281.8ms}}, tikv_task:{proc max:10ms, min:0s, avg: 74.3µs, p80:0s, p95:0s, iters:808, tasks:807}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 7.42ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 286.5ms, total_suspend_time: 395.4µs, total_wait_time: 151.6ms, total_kv_read_wall_time: 60ms}	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	N/A	N/A
              └─TableRowIDScan_297	14274.48	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 74.3µs, p80:0s, p95:0s, iters:808, tasks:807}	keep order:false	N/A	N/A
ScalarSubQuery_480	N/A	0	root			Output: ScalarQueryCol#2065	N/A	N/A
└─MaxOneRow_378	1.00	1	root		time:197.3ms, open:12.7µs, close:49.6µs, loops:1		N/A	N/A
  └─HashAgg_383	1.00	1	root		time:197.3ms, open:12µs, close:49µs, loops:2	funcs:count(distinct Column#2029)->Column#2030	179.1 KB	0 Bytes
    └─Union_387	10622.47	3330	root		time:196.5ms, open:995ns, close:48.1µs, loops:6		N/A	N/A
      ├─Projection_389	62.24	3325	root		time:12ms, open:450.3µs, close:7.99µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2029	130.4 KB	N/A
      │ └─IndexReader_393	62.24	3325	root		time:11.8ms, open:443.3µs, close:5.37µs, loops:5, cop_task: {num: 4, max: 4.33ms, min: 1.1ms, avg: 2.83ms, p95: 4.33ms, max_proc_keys: 1629, p95_proc_keys: 1629, tot_proc: 8.29ms, tot_wait: 610.6µs, copr_cache: disabled, build_task_duration: 402.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 11.1ms, rpc_info:{Cop:{num_rpc:4, total_time:11.3ms}}	index:Selection_392	281.0 KB	N/A
      │   └─Selection_392	62.24	3325	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}, scan_detail: {total_process_keys: 3325, total_process_keys_size: 802058, total_keys: 3329, get_snapshot_time: 552.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 8.29ms, total_suspend_time: 17.1µs, total_wait_time: 610.6µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_391	62.34	3325	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_394	10560.23	5	root		time:197.2ms, open:95.2µs, close:38.8µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2029	27.2 KB	N/A
        └─IndexHashJoin_404	10560.23	5	root		time:197.1ms, open:93.8µs, close:10.1µs, loops:2, inner:{total:294.8ms, concurrency:5, task:2, construct:3.46ms, fetch:287ms, build:797.3µs, join:4.3ms}	inner join, inner:IndexLookUp_420, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.05 MB	N/A
          ├─IndexReader_415(Build)	5970.05	5192	root	partition:all	time:3.72ms, open:92.1µs, close:6.89µs, loops:8, cop_task: {num: 21, max: 1.44ms, min: 458.9µs, avg: 911.2µs, p95: 1.35ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 6.69ms, tot_wait: 610µs, copr_cache: disabled, build_task_duration: 39µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.23ms, rpc_info:{Cop:{num_rpc:21, total_time:18.9ms}}	index:Selection_414	39.9 KB	N/A
          │ └─Selection_414	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 266.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 6.69ms, total_wait_time: 610µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_413	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_420(Probe)	10560.23	3328	root	partition:all	total_time:285.4ms, total_open:18.1ms, total_close:15.6µs, loops:6, index_task: {total_time: 215.6ms, fetch_handle: 215.6ms, build: 19.5µs, wait: 39.1µs}, table_task: {total_time: 99.4ms, num: 12, concurrency: 5}, next: {wait_index: 216.8ms, wait_table_lookup_build: 1.35ms, wait_table_lookup_resp: 48.7ms}		3.84 MB	N/A
            ├─Selection_418(Build)	15181.60	5192	cop[tikv]		total_time:224ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 155.8ms, min: 1.5ms, avg: 40.5ms, p95: 153.2ms, max_proc_keys: 751, p95_proc_keys: 516, tot_proc: 898.9ms, tot_wait: 561.3µs, copr_cache: disabled, build_task_duration: 5.14ms, max_distsql_concurrency: 4}, fetch_resp_duration: 223.1ms, rpc_info:{Cop:{num_rpc:34, total_time:1.38s}}, tikv_task:{proc max:90ms, min:0s, avg: 27.1ms, p80:50ms, p95:90ms, iters:88, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 329130, total_keys: 6471, get_snapshot_time: 365.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 898.9ms, total_suspend_time: 466.9µs, total_wait_time: 561.3µs, total_kv_read_wall_time: 190ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_416	22413.64	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 27.1ms, p80:50ms, p95:90ms, iters:88, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_419(Probe)	10560.23	3328	cop[tikv]		total_time:94.9ms, total_open:0s, total_close:57µs, loops:24, cop_task: {num: 813, max: 2.46ms, min: 0s, avg: 239µs, p95: 1.25ms, max_proc_keys: 32, p95_proc_keys: 19, tot_proc: 138.9ms, tot_wait: 69.1ms, copr_cache: disabled, build_task_duration: 2.28ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 602, store_batch_fallback_num: 25}, fetch_resp_duration: 91.9ms, rpc_info:{Cop:{num_rpc:211, total_time:192.4ms}}, tikv_task:{proc max:10ms, min:0s, avg: 123µs, p80:0s, p95:0s, iters:814, tasks:813}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 6.2ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 138.9ms, total_suspend_time: 24.7µs, total_wait_time: 69.1ms, total_kv_read_wall_time: 100ms}	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	N/A	N/A
              └─TableRowIDScan_417	15181.60	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 123µs, p80:0s, p95:0s, iters:814, tasks:813}	keep order:false	N/A	N/A
ScalarSubQuery_600	N/A	0	root			Output: ScalarQueryCol#2219	N/A	N/A
└─MaxOneRow_498	1.00	1	root		time:181.3ms, open:9.45µs, close:42.4µs, loops:1		N/A	N/A
  └─HashAgg_503	1.00	1	root		time:181.3ms, open:8.9µs, close:41.7µs, loops:2	funcs:count(distinct Column#2181)->Column#2182	296.1 KB	0 Bytes
    └─Union_507	10624.39	3594	root		time:180.3ms, open:843ns, close:40.7µs, loops:6		N/A	N/A
      ├─Projection_509	64.16	3587	root		time:17.4ms, open:886.2µs, close:8.45µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2181	130.4 KB	N/A
      │ └─IndexReader_513	64.16	3587	root		time:17.2ms, open:876.6µs, close:5.39µs, loops:5, cop_task: {num: 4, max: 7.76ms, min: 2.06ms, avg: 4.09ms, p95: 7.76ms, max_proc_keys: 1891, p95_proc_keys: 1891, tot_proc: 9.51ms, tot_wait: 1.27ms, copr_cache: disabled, build_task_duration: 836.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 16.1ms, rpc_info:{Cop:{num_rpc:4, total_time:16.3ms}}	index:Selection_512	309.0 KB	N/A
      │   └─Selection_512	64.16	3587	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3587, total_process_keys_size: 865272, total_keys: 3591, get_snapshot_time: 1.22ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 9.51ms, total_suspend_time: 16.4µs, total_wait_time: 1.27ms, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_511	64.26	3587	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_514	10560.23	7	root		time:181.2ms, open:93.7µs, close:31.2µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2181	27.2 KB	N/A
        └─IndexHashJoin_524	10560.23	7	root		time:181.2ms, open:92.6µs, close:9.73µs, loops:2, inner:{total:292.2ms, concurrency:5, task:2, construct:3.39ms, fetch:284.3ms, build:687.7µs, join:4.55ms}	inner join, inner:IndexLookUp_540, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.06 MB	N/A
          ├─IndexReader_535(Build)	5970.05	5192	root	partition:all	time:3.57ms, open:90.8µs, close:6.57µs, loops:8, cop_task: {num: 21, max: 1.46ms, min: 413.1µs, avg: 838.7µs, p95: 1.22ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 5.35ms, tot_wait: 505.6µs, copr_cache: disabled, build_task_duration: 34.5µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.12ms, rpc_info:{Cop:{num_rpc:21, total_time:17.4ms}}	index:Selection_534	40.1 KB	N/A
          │ └─Selection_534	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 199µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.35ms, total_wait_time: 505.6µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_533	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_540(Probe)	10560.23	3591	root	partition:all	total_time:282.5ms, total_open:18.2ms, total_close:15.5µs, loops:7, index_task: {total_time: 222.2ms, fetch_handle: 222.1ms, build: 11.2µs, wait: 33µs}, table_task: {total_time: 87.5ms, num: 12, concurrency: 5}, next: {wait_index: 207.1ms, wait_table_lookup_build: 1.82ms, wait_table_lookup_resp: 54.8ms}		3.84 MB	N/A
            ├─Selection_538(Build)	14414.37	5192	cop[tikv]		total_time:229.5ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 146.4ms, min: 618µs, avg: 35ms, p95: 119.6ms, max_proc_keys: 751, p95_proc_keys: 516, tot_proc: 850.5ms, tot_wait: 574.6µs, copr_cache: disabled, build_task_duration: 5.11ms, max_distsql_concurrency: 4}, fetch_resp_duration: 228.6ms, rpc_info:{Cop:{num_rpc:34, total_time:1.19s}}, tikv_task:{proc max:120ms, min:0s, avg: 25.9ms, p80:50ms, p95:90ms, iters:88, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 367956, total_keys: 12380, get_snapshot_time: 277µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 850.5ms, total_suspend_time: 739µs, total_wait_time: 574.6µs, total_kv_read_wall_time: 300ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_536	21280.91	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:120ms, min:0s, avg: 25.9ms, p80:50ms, p95:90ms, iters:88, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_539(Probe)	10560.23	3591	cop[tikv]		total_time:82.9ms, total_open:0s, total_close:62.3µs, loops:24, cop_task: {num: 813, max: 1.72ms, min: 0s, avg: 193.9µs, p95: 997.7µs, max_proc_keys: 32, p95_proc_keys: 19, tot_proc: 82.6ms, tot_wait: 21.1ms, copr_cache: disabled, build_task_duration: 2.31ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 602, store_batch_fallback_num: 25}, fetch_resp_duration: 79.5ms, rpc_info:{Cop:{num_rpc:211, total_time:155.6ms}}, tikv_task:{proc max:10ms, min:0s, avg: 49.2µs, p80:0s, p95:0s, iters:814, tasks:813}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 5.81ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 82.6ms, total_wait_time: 21.1ms, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	N/A	N/A
              └─TableRowIDScan_537	14414.37	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 49.2µs, p80:0s, p95:0s, iters:814, tasks:813}	keep order:false	N/A	N/A
ScalarSubQuery_738	N/A	0	root			Output: ScalarQueryCol#2423	N/A	N/A
└─MaxOneRow_618	1.00	1	root		time:177.3ms, open:15.3µs, close:26.4µs, loops:1		N/A	N/A
  └─HashAgg_623	1.00	1	root		time:177.3ms, open:14.7µs, close:25.9µs, loops:2	funcs:count(distinct Column#2335)->Column#2336	29.7 KB	0 Bytes
    └─Union_627	10582.13	406	root		time:177.2ms, open:812ns, close:25µs, loops:2		N/A	N/A
      ├─Projection_629	21.90	406	root		time:4.56ms, open:63.7µs, close:7.91µs, loops:2, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2335	55.2 KB	N/A
      │ └─IndexReader_633	21.90	406	root		time:4.51ms, open:59.4µs, close:4.59µs, loops:2, cop_task: {num: 2, max: 3.22ms, min: 1.1ms, avg: 2.16ms, p95: 3.22ms, max_proc_keys: 224, p95_proc_keys: 224, tot_proc: 2.29ms, tot_wait: 42.7µs, copr_cache: disabled, build_task_duration: 17.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 4.36ms, rpc_info:{Cop:{num_rpc:2, total_time:4.31ms}}	index:Selection_632	44.3 KB	N/A
      │   └─Selection_632	21.90	406	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:6, tasks:2}, scan_detail: {total_process_keys: 406, total_process_keys_size: 97954, total_keys: 408, get_snapshot_time: 17.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.29ms, total_suspend_time: 4.4µs, total_wait_time: 42.7µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_631	21.94	406	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:6, tasks:2}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_634	10560.23	0	root		time:177.3ms, open:86.2µs, close:16.1µs, loops:1, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2335	6.21 KB	N/A
        └─IndexHashJoin_644	10560.23	0	root		time:177.2ms, open:85.4µs, close:4.81µs, loops:1, inner:{total:276.9ms, concurrency:5, task:2, construct:3.44ms, fetch:272.7ms, build:741.9µs, join:724.6µs}	inner join, inner:IndexLookUp_660, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	995.7 KB	N/A
          ├─IndexReader_655(Build)	5970.05	5192	root	partition:all	time:3.52ms, open:83.9µs, close:2.88µs, loops:8, cop_task: {num: 21, max: 1.28ms, min: 417.7µs, avg: 813.1µs, p95: 1.13ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 4.88ms, tot_wait: 482.6µs, copr_cache: disabled, build_task_duration: 36.9µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.07ms, rpc_info:{Cop:{num_rpc:21, total_time:16.8ms}}	index:Selection_654	44.1 KB	N/A
          │ └─Selection_654	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 182.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.88ms, total_wait_time: 482.6µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_653	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_660(Probe)	10560.23	406	root	partition:all	total_time:270.9ms, total_open:18ms, total_close:14.9µs, loops:4, index_task: {total_time: 210.9ms, fetch_handle: 210.9ms, build: 27.6µs, wait: 28µs}, table_task: {total_time: 84.9ms, num: 12, concurrency: 5}, next: {wait_index: 202.3ms, wait_table_lookup_build: 1.4ms, wait_table_lookup_resp: 49ms}		3.85 MB	N/A
            ├─Selection_658(Build)	130973.11	5192	cop[tikv]		total_time:218.7ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 139.8ms, min: 607.9µs, avg: 33.4ms, p95: 119.4ms, max_proc_keys: 746, p95_proc_keys: 521, tot_proc: 846.7ms, tot_wait: 570.8µs, copr_cache: disabled, build_task_duration: 5.09ms, max_distsql_concurrency: 4}, fetch_resp_duration: 217.7ms, rpc_info:{Cop:{num_rpc:34, total_time:1.14s}}, tikv_task:{proc max:110ms, min:0s, avg: 24.4ms, p80:50ms, p95:90ms, iters:87, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 406566, total_keys: 15443, get_snapshot_time: 267.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 846.7ms, total_suspend_time: 853.4µs, total_wait_time: 570.8µs, total_kv_read_wall_time: 310ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_656	193364.56	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:110ms, min:0s, avg: 24.4ms, p80:50ms, p95:90ms, iters:87, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_659(Probe)	10560.23	406	cop[tikv]		total_time:80.3ms, total_open:0s, total_close:57.8µs, loops:24, cop_task: {num: 815, max: 1.25ms, min: 0s, avg: 171.8µs, p95: 903.6µs, max_proc_keys: 32, p95_proc_keys: 19, tot_proc: 47ms, tot_wait: 18.1ms, copr_cache: disabled, build_task_duration: 2.33ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 603, store_batch_fallback_num: 26}, fetch_resp_duration: 77.8ms, rpc_info:{Cop:{num_rpc:212, total_time:138ms}}, tikv_task:{proc max:10ms, min:0s, avg: 49.1µs, p80:0s, p95:0s, iters:816, tasks:815}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 5.29ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 47ms, total_wait_time: 18.1ms, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	N/A	N/A
              └─TableRowIDScan_657	130973.11	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 49.1µs, p80:0s, p95:0s, iters:816, tasks:815}	keep order:false	N/A	N/A
ScalarSubQuery_890	N/A	0	root			Output: ScalarQueryCol#2647	N/A	N/A
└─MaxOneRow_756	1.00	1	root		time:194.9ms, open:12.8µs, close:25.6µs, loops:1		N/A	N/A
  └─HashAgg_761	1.00	1	root		time:194.9ms, open:12.2µs, close:25µs, loops:2	funcs:count(distinct Column#2539)->Column#2540	27.3 KB	0 Bytes
    └─Union_765	10626.40	3552	root		time:194.5ms, open:1.84µs, close:24.3µs, loops:6		N/A	N/A
      ├─Projection_767	66.17	3546	root		time:11ms, open:770.9µs, close:8.73µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2539	130.4 KB	N/A
      │ └─IndexReader_771	66.17	3546	root		time:10.9ms, open:764.6µs, close:5.64µs, loops:5, cop_task: {num: 4, max: 3.53ms, min: 1.26ms, avg: 2.52ms, p95: 3.53ms, max_proc_keys: 1850, p95_proc_keys: 1850, tot_proc: 4.14ms, tot_wait: 988.5µs, copr_cache: disabled, build_task_duration: 725.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 9.87ms, rpc_info:{Cop:{num_rpc:4, total_time:10.1ms}}	index:Selection_770	310.8 KB	N/A
      │   └─Selection_770	66.17	3546	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}, scan_detail: {total_process_keys: 3546, total_process_keys_size: 886533, total_keys: 3550, get_snapshot_time: 919.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.14ms, total_suspend_time: 3.55µs, total_wait_time: 988.5µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_769	66.27	3546	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_772	10560.23	6	root		time:194.9ms, open:90.1µs, close:14.6µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2539	31.2 KB	N/A
        └─IndexHashJoin_782	10560.23	6	root		time:194.8ms, open:88.8µs, close:4.42µs, loops:2, inner:{total:291.4ms, concurrency:5, task:2, construct:3.4ms, fetch:283.1ms, build:728.9µs, join:4.84ms}	inner join, inner:IndexLookUp_798, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.04 MB	N/A
          ├─IndexReader_793(Build)	5970.05	5192	root	partition:all	time:3.56ms, open:86µs, close:2.69µs, loops:8, cop_task: {num: 21, max: 1.36ms, min: 424.7µs, avg: 801.3µs, p95: 1.1ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 5.08ms, tot_wait: 498.7µs, copr_cache: disabled, build_task_duration: 38.5µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.12ms, rpc_info:{Cop:{num_rpc:21, total_time:16.7ms}}	index:Selection_792	39.9 KB	N/A
          │ └─Selection_792	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 189.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.08ms, total_wait_time: 498.7µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_791	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_798(Probe)	10560.23	3742	root	partition:all	total_time:281.3ms, total_open:18.1ms, total_close:15.4µs, loops:7, index_task: {total_time: 214.8ms, fetch_handle: 214.7ms, build: 10.9µs, wait: 33.8µs}, table_task: {total_time: 86ms, num: 12, concurrency: 5}, next: {wait_index: 217.1ms, wait_table_lookup_build: 1.38ms, wait_table_lookup_resp: 44.3ms}		3.84 MB	N/A
            ├─Selection_796(Build)	14707.02	5192	cop[tikv]		total_time:222.2ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 154.3ms, min: 510.7µs, avg: 36.3ms, p95: 153.1ms, max_proc_keys: 751, p95_proc_keys: 516, tot_proc: 739ms, tot_wait: 448.3µs, copr_cache: disabled, build_task_duration: 4.99ms, max_distsql_concurrency: 4}, fetch_resp_duration: 221.3ms, rpc_info:{Cop:{num_rpc:34, total_time:1.23s}}, tikv_task:{proc max:90ms, min:0s, avg: 21.5ms, p80:40ms, p95:90ms, iters:88, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 329130, total_keys: 6471, get_snapshot_time: 256.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 739ms, total_suspend_time: 114.1µs, total_wait_time: 448.3µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_794	21712.98	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 21.2ms, p80:40ms, p95:90ms, iters:88, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_797(Probe)	10560.23	3742	cop[tikv]		total_time:81.4ms, total_open:0s, total_close:61.8µs, loops:24, cop_task: {num: 813, max: 1.18ms, min: 0s, avg: 169.4µs, p95: 882.5µs, max_proc_keys: 32, p95_proc_keys: 19, tot_proc: 40.3ms, tot_wait: 16.6ms, copr_cache: disabled, build_task_duration: 2.34ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 602, store_batch_fallback_num: 25}, fetch_resp_duration: 78.2ms, rpc_info:{Cop:{num_rpc:211, total_time:135.8ms}}, tikv_task:{proc max:10ms, min:0s, avg: 12.3µs, p80:0s, p95:0s, iters:814, tasks:813}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 4.9ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 40.3ms, total_wait_time: 16.6ms, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	N/A	N/A
              └─TableRowIDScan_795	14707.02	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 12.3µs, p80:0s, p95:0s, iters:814, tasks:813}	keep order:false	N/A	N/A
ScalarSubQuery_1022	N/A	0	root			Output: ScalarQueryCol#2831	N/A	N/A
└─MaxOneRow_908	1.00	1	root		time:167.5ms, open:9.24µs, close:37.8µs, loops:1		N/A	N/A
  └─HashAgg_913	1.00	1	root		time:167.5ms, open:8.66µs, close:37.2µs, loops:2	funcs:count(distinct Column#2763)->Column#2764	1.60 KB	0 Bytes
    └─Union_917	10562.58	6	root		time:167.4ms, open:849ns, close:36.4µs, loops:2		N/A	N/A
      ├─Projection_919	2.36	6	root		time:916.8µs, open:71µs, close:7.15µs, loops:2, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2763	3.85 KB	N/A
      │ └─IndexReader_923	2.36	6	root		time:899µs, open:64.8µs, close:4.5µs, loops:2, cop_task: {num: 1, max: 807.2µs, proc_keys: 6, tot_proc: 230.9µs, tot_wait: 18.8µs, copr_cache: disabled, build_task_duration: 17.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 818.7µs, rpc_info:{Cop:{num_rpc:1, total_time:796.6µs}}	index:Selection_922	1.01 KB	N/A
      │   └─Selection_922	2.36	6	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_process_keys: 6, total_process_keys_size: 1348, total_keys: 7, get_snapshot_time: 8.19µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 230.9µs, total_wait_time: 18.8µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_921	2.36	6	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{time:0s, loops:1}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_924	10560.23	0	root		time:167.4ms, open:155.1µs, close:28.2µs, loops:1, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2763	6.21 KB	N/A
        └─IndexHashJoin_934	10560.23	0	root		time:167.3ms, open:153.7µs, close:8.76µs, loops:1, inner:{total:254.9ms, concurrency:5, task:2, construct:3.48ms, fetch:251.3ms, build:761µs, join:99.7µs}	inner join, inner:IndexLookUp_950, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	986.3 KB	N/A
          ├─IndexReader_945(Build)	5970.05	5192	root	partition:all	time:3.68ms, open:151.8µs, close:5.78µs, loops:8, cop_task: {num: 21, max: 2.21ms, min: 411.3µs, avg: 904.7µs, p95: 1.43ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 4.94ms, tot_wait: 2.49ms, copr_cache: disabled, build_task_duration: 35.3µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.16ms, rpc_info:{Cop:{num_rpc:21, total_time:18.8ms}}	index:Selection_944	39.9 KB	N/A
          │ └─Selection_944	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 2.19ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.94ms, total_wait_time: 2.49ms, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_943	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_950(Probe)	10560.23	6	root	partition:all	total_time:249.5ms, total_open:17.7ms, total_close:14.7µs, loops:4, index_task: {total_time: 197.5ms, fetch_handle: 197.4ms, build: 28.1µs, wait: 37.8µs}, table_task: {total_time: 81.6ms, num: 12, concurrency: 5}, next: {wait_index: 170.5ms, wait_table_lookup_build: 1.81ms, wait_table_lookup_resp: 59.4ms}		3.84 MB	N/A
            ├─Selection_948(Build)	21058627.41	5192	cop[tikv]		total_time:205ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 136.3ms, min: 469.5µs, avg: 30ms, p95: 86.3ms, max_proc_keys: 751, p95_proc_keys: 516, tot_proc: 740.5ms, tot_wait: 549.6µs, copr_cache: disabled, build_task_duration: 5.07ms, max_distsql_concurrency: 4}, fetch_resp_duration: 204.1ms, rpc_info:{Cop:{num_rpc:34, total_time:1.02s}}, tikv_task:{proc max:90ms, min:0s, avg: 21.8ms, p80:50ms, p95:90ms, iters:88, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 376434, total_keys: 14883, get_snapshot_time: 256.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 740.5ms, total_suspend_time: 667.8µs, total_wait_time: 549.6µs, total_kv_read_wall_time: 230ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_946	31090290.88	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 21.8ms, p80:50ms, p95:90ms, iters:88, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_949(Probe)	10560.23	6	cop[tikv]		total_time:77.1ms, total_open:0s, total_close:58µs, loops:18, cop_task: {num: 813, max: 1.14ms, min: 0s, avg: 160µs, p95: 839.1µs, max_proc_keys: 32, p95_proc_keys: 19, tot_proc: 35.7ms, tot_wait: 14.6ms, copr_cache: disabled, build_task_duration: 2.25ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 602, store_batch_fallback_num: 25}, fetch_resp_duration: 75.1ms, rpc_info:{Cop:{num_rpc:211, total_time:128.2ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:814, tasks:813}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 4.63ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 35.7ms, total_wait_time: 14.6ms}	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	N/A	N/A
              └─TableRowIDScan_947	21058627.41	5192	cop[tikv]	table:d	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:814, tasks:813}	keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.smart_id AS `raw_distinct_0`,
    d.exact_id AS `raw_distinct_1`,
    d.input_ip AS `raw_distinct_2`,
    d.true_ip AS `raw_distinct_3`,
    d.proxy_ip AS `raw_distinct_4`,
    d.agent_type AS `raw_distinct_5`,
    d.agent_os AS `raw_distinct_6`
  FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id
  WHERE p.merchant_account_number = %s AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760286177318 AND d.jms_timestamp >= '2025-10-12 09:22:57.318000' AND (p.event_date < 1760338800000 OR d.jms_timestamp < '2025-10-13 00:00:00.000000')
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_c_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_c_bundle_025'
    AND x.template_id IN ('c_0211', 'c_0212', 'c_0213', 'c_0214', 'c_0215', 'c_0216', 'c_0217')
    AND x.key1 = %s AND x.key2 = ''
    AND x.p_event_day > '2025-10-12' AND x.d_event_day > '2025-10-12'
  UNION ALL
  SELECT 'c_0211' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'c_0212' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'c_0213' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'c_0214' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION ALL
  SELECT 'c_0215' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
  UNION ALL
  SELECT 'c_0216' AS template_id, CAST(`raw_distinct_5` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_5` IS NOT NULL
  UNION ALL
  SELECT 'c_0217' AS template_id, CAST(`raw_distinct_6` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_6` IS NOT NULL
)
SELECT
  COUNT(DISTINCT CASE WHEN template_id = 'c_0211' THEN distinct_value END) AS `metric__c_0211`,
  COUNT(DISTINCT CASE WHEN template_id = 'c_0212' THEN distinct_value END) AS `metric__c_0212`,
  COUNT(DISTINCT CASE WHEN template_id = 'c_0213' THEN distinct_value END) AS `metric__c_0213`,
  COUNT(DISTINCT CASE WHEN template_id = 'c_0214' THEN distinct_value END) AS `metric__c_0214`,
  COUNT(DISTINCT CASE WHEN template_id = 'c_0215' THEN distinct_value END) AS `metric__c_0215`,
  COUNT(DISTINCT CASE WHEN template_id = 'c_0216' THEN distinct_value END) AS `metric__c_0216`,
  COUNT(DISTINCT CASE WHEN template_id = 'c_0217' THEN distinct_value END) AS `metric__c_0217`
FROM distinct_values;
```

#### Optimized Params

```json
[
  "5247719970153111",
  "5247719970153111"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=161.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_131	1.00	1	root		time:119.5ms, open:8.39µs, close:169.2µs, loops:2, RU:438.15	funcs:count(distinct Column#314)->Column#254, funcs:count(distinct Column#315)->Column#255, funcs:count(distinct Column#316)->Column#256, funcs:count(distinct Column#317)->Column#257, funcs:count(distinct Column#318)->Column#258, funcs:count(distinct Column#319)->Column#259, funcs:count(distinct Column#320)->Column#260	1.26 MB	0 Bytes
└─Projection_199	59486.89	18351	root		time:113ms, open:1.91µs, close:168.5µs, loops:26, Concurrency:5	case(eq(Column#252, ?), Column#253)->Column#314, case(eq(Column#252, ?), Column#253)->Column#315, case(eq(Column#252, ?), Column#253)->Column#316, case(eq(Column#252, ?), Column#253)->Column#317, case(eq(Column#252, ?), Column#253)->Column#318, case(eq(Column#252, ?), Column#253)->Column#319, case(eq(Column#252, ?), Column#253)->Column#320	990.4 KB	N/A
  └─Union_133	59486.89	18351	root		time:118ms, open:771ns, close:160.6µs, loops:26		N/A	N/A
    ├─Projection_135	349.62	18321	root		time:7.91ms, open:106.1µs, close:9.04µs, loops:21, Concurrency:OFF	intuit_risk.group_c_180d_daily_distinct.template_id->Column#252, cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	173.5 KB	N/A
    │ └─IndexReader_139	349.62	18321	root		time:7.26ms, open:101.5µs, close:6.64µs, loops:21, cop_task: {num: 23, max: 2.81ms, min: 591.1µs, avg: 1.59ms, p95: 2.79ms, max_proc_keys: 2016, p95_proc_keys: 2006, tot_proc: 16.3ms, tot_wait: 587.3µs, copr_cache: disabled, build_task_duration: 34.6µs, max_distsql_concurrency: 6}, fetch_resp_duration: 6.6ms, rpc_info:{Cop:{num_rpc:23, total_time:36.3ms}}	index:Selection_138	504.4 KB	N/A
    │   └─Selection_138	349.62	18321	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 869.6µs, p80:0s, p95:10ms, iters:98, tasks:23}, scan_detail: {total_process_keys: 18321, total_process_keys_size: 4791602, total_keys: 18345, get_snapshot_time: 231.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 16.3ms, total_suspend_time: 21.7µs, total_wait_time: 587.3µs, total_kv_read_wall_time: 20ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
    │     └─IndexRangeScan_137	350.16	18321	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 869.6µs, p80:0s, p95:10ms, iters:98, tasks:23}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_140	8448.18	6	root		time:119.1ms, open:109.7µs, close:54.2µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_142	8448.18	6	root		time:119ms, open:109µs, close:38.6µs, loops:2	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	66.8 KB	N/A
    │   └─CTEFullScan_144	10560.23	7	root	CTE:raw_boundary	time:118.9ms, open:102.8µs, close:37.5µs, loops:3	data:CTE_0	8.70 KB	0 Bytes
    ├─Projection_148	8448.18	6	root		time:119ms, open:137.5µs, close:19.1µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_150	8448.18	6	root		time:118.9ms, open:136.7µs, close:986ns, loops:2	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	4.97 KB	N/A
    │   └─CTEFullScan_152	10560.23	7	root	CTE:raw_boundary	time:118.9ms, open:134.4µs, close:276ns, loops:3	data:CTE_0	N/A	N/A
    ├─Projection_156	8448.18	5	root		time:119ms, open:161.9µs, close:16.9µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_158	8448.18	5	root		time:119ms, open:159.4µs, close:909ns, loops:2	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	55.9 KB	N/A
    │   └─CTEFullScan_160	10560.23	7	root	CTE:raw_boundary	time:118.9ms, open:155µs, close:269ns, loops:3	data:CTE_0	N/A	N/A
    ├─Projection_164	8448.18	7	root		time:119.1ms, open:119ms, close:17.2µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	30.7 KB	N/A
    │ └─Selection_166	8448.18	7	root		time:119.1ms, open:119ms, close:1.09µs, loops:2	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	4.35 KB	N/A
    │   └─CTEFullScan_168	10560.23	7	root	CTE:raw_boundary	time:119ms, open:119ms, close:283ns, loops:3	data:CTE_0	N/A	N/A
    ├─Projection_172	8448.18	0	root		time:110.5ms, open:110.4ms, close:14.5µs, loops:1, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	30.7 KB	N/A
    │ └─Selection_174	8448.18	0	root		time:110.4ms, open:110.4ms, close:713ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	4.35 KB	N/A
    │   └─CTEFullScan_176	10560.23	7	root	CTE:raw_boundary	time:110.4ms, open:110.4ms, close:135ns, loops:2	data:CTE_0	N/A	N/A
    ├─Projection_180	8448.18	6	root		time:121.3µs, open:12.7µs, close:15.3µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_182	8448.18	6	root		time:38.8µs, open:11.1µs, close:665ns, loops:2	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	4.35 KB	N/A
    │   └─CTEFullScan_184	10560.23	7	root	CTE:raw_boundary	time:6.2µs, open:690ns, close:141ns, loops:3	data:CTE_0	N/A	N/A
    └─Projection_188	8448.18	0	root		time:68µs, open:5.4µs, close:12.8µs, loops:1, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	27.9 KB	N/A
      └─Selection_190	8448.18	0	root		time:29.4µs, open:4.46µs, close:516ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	4.35 KB	N/A
        └─CTEFullScan_192	10560.23	7	root	CTE:raw_boundary	time:6.63µs, open:231ns, close:93ns, loops:2	data:CTE_0	N/A	N/A
CTE_0	10560.23	7	root		time:118.9ms, open:102.8µs, close:37.5µs, loops:3	Non-Recursive CTE	8.70 KB	0 Bytes
└─Projection_78(Seed Part)	10560.23	7	root		time:118.9ms, open:100µs, close:36.4µs, loops:2, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.agent_os	84.9 KB	N/A
  └─IndexHashJoin_88	10560.23	7	root		time:118.8ms, open:98.9µs, close:9.76µs, loops:2, inner:{total:186.3ms, concurrency:5, task:2, construct:3.21ms, fetch:175.7ms, build:678.5µs, join:7.35ms}	inner join, inner:IndexLookUp_104, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.51 MB	N/A
    ├─IndexReader_99(Build)	5970.05	5192	root	partition:all	time:3.62ms, open:97µs, close:6.08µs, loops:8, cop_task: {num: 21, max: 1.41ms, min: 451µs, avg: 830.2µs, p95: 1.12ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 5.29ms, tot_wait: 551.7µs, copr_cache: disabled, build_task_duration: 38.3µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.24ms, rpc_info:{Cop:{num_rpc:21, total_time:17.3ms}}	index:Selection_98	43.5 KB	N/A
    │ └─Selection_98	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 208.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.29ms, total_wait_time: 551.7µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
    │   └─IndexRangeScan_97	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexLookUp_104(Probe)	10560.23	5182	root	partition:all	total_time:174.2ms, total_open:15.8ms, total_close:16.5µs, loops:9, index_task: {total_time: 121.6ms, fetch_handle: 121.5ms, build: 12.7µs, wait: 32.3µs}, table_task: {total_time: 76ms, num: 12, concurrency: 5}, next: {wait_index: 123.2ms, wait_table_lookup_build: 992.7µs, wait_table_lookup_resp: 33.3ms}		3.85 MB	N/A
      ├─Selection_102(Build)	10574.33	5192	cop[tikv]		total_time:128.7ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 34, max: 78.3ms, min: 598.4µs, avg: 22.1ms, p95: 75.7ms, max_proc_keys: 757, p95_proc_keys: 510, tot_proc: 536.5ms, tot_wait: 654.4µs, copr_cache: disabled, build_task_duration: 3.56ms, max_distsql_concurrency: 4}, fetch_resp_duration: 128ms, rpc_info:{Cop:{num_rpc:34, total_time:749.5ms}}, tikv_task:{proc max:50ms, min:0s, avg: 16.5ms, p80:40ms, p95:50ms, iters:87, tasks:34}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 444960, total_keys: 21346, get_snapshot_time: 324µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 536.5ms, total_suspend_time: 523.9µs, total_wait_time: 654.4µs, total_kv_read_wall_time: 210ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
      │ └─IndexRangeScan_100	15611.61	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:50ms, min:0s, avg: 16.5ms, p80:40ms, p95:50ms, iters:87, tasks:34}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
      └─Selection_103(Probe)	10560.23	5182	cop[tikv]		total_time:71.8ms, total_open:0s, total_close:60.9µs, loops:24, cop_task: {num: 820, max: 1.23ms, min: 0s, avg: 176.9µs, p95: 894.6µs, max_proc_keys: 35, p95_proc_keys: 18, tot_proc: 45ms, tot_wait: 14.4ms, copr_cache: disabled, build_task_duration: 2.07ms, max_distsql_concurrency: 6, max_extra_concurrency: 12, store_batch_num: 607, store_batch_fallback_num: 25}, fetch_resp_duration: 68.2ms, rpc_info:{Cop:{num_rpc:213, total_time:143.3ms}}, tikv_task:{proc max:10ms, min:0s, avg: 48.8µs, p80:0s, p95:0s, iters:822, tasks:820}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 4.24ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 45ms, total_wait_time: 14.4ms, total_kv_read_wall_time: 10ms}	or(or(not(isnull(intuit_risk.deviceprofile_fact.smart_id)), or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.input_ip)))), or(or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))), or(not(isnull(intuit_risk.deviceprofile_fact.agent_type)), not(isnull(intuit_risk.deviceprofile_fact.agent_os)))))	N/A	N/A
        └─TableRowIDScan_101	10574.33	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 12.2µs, p80:0s, p95:0s, iters:822, tasks:820}	keep order:false	N/A	N/A
```

### 4. group_b_bundle_018

- Filter/window: `d.input_ip = %s` / `180d`
- Chosen event: `INV0053143614` kind=`normal` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 1496.6 ms | ok |
| `optimized_default` | `{}` | 711.1 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 700.9 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 699.1 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 709.3 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 695.3 ms | ok |

#### Original SQL

```sql
SELECT
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0146' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.exact_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0146`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0150' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.smart_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.smart_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0150`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0154' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.true_ip AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.true_ip IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0154`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0158' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.agent_type AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.agent_type IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0158`;
```

#### Original Params

```json
[
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=1496.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_265	1.00	1	root		time:9.19µs, open:3.37µs, close:902ns, loops:2, RU:1660.14, Concurrency:OFF	?->Column#652, ?->Column#770, ?->Column#882, ?->Column#976	0 Bytes	N/A
└─TableDual_267	1.00	1	root		time:1.95µs, open:221ns, close:202ns, loops:2	rows:1	N/A	N/A
ScalarSubQuery_100	N/A	0	root			Output: ScalarQueryCol#651	N/A	N/A
└─MaxOneRow_59	1.00	1	root		time:509.5ms, open:8.91µs, close:36µs, loops:1		N/A	N/A
  └─HashAgg_64	1.00	1	root		time:509.5ms, open:8.26µs, close:35.5µs, loops:2	funcs:count(distinct Column#604)->Column#605	13.4 MB	0 Bytes
    └─Union_68	319321.01	261396	root		time:435.7ms, open:645ns, close:34.6µs, loops:257		N/A	N/A
      ├─Projection_70	319319.92	261396	root		time:435.5ms, open:579.3µs, close:28.7µs, loops:257, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#604	838.5 KB	N/A
      │ └─IndexReader_73	319319.92	261396	root		time:437.4ms, open:577.2µs, close:10.4µs, loops:257, cop_task: {num: 7, max: 407.4ms, min: 2.33ms, avg: 62.3ms, p95: 407.4ms, max_proc_keys: 249556, p95_proc_keys: 249556, tot_proc: 169.8ms, tot_wait: 858.6µs, copr_cache: disabled, build_task_duration: 531.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 435.9ms, rpc_info:{Cop:{num_rpc:7, total_time:436.1ms}}	index:IndexRangeScan_72	28.4 MB	N/A
      │   └─IndexRangeScan_72	319319.92	261396	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:150ms, min:0s, avg: 24.3ms, p80:10ms, p95:150ms, iters:282, tasks:7}, scan_detail: {total_process_keys: 261396, total_process_keys_size: 34837590, total_keys: 11846, get_snapshot_time: 774.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 169.8ms, total_suspend_time: 53.2µs, total_wait_time: 858.6µs, total_kv_read_wall_time: 20ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_74	1.09	0	root		time:779.6µs, open:74.5µs, close:4.89µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#604	30.1 KB	N/A
        └─IndexReader_81	1.09	0	root	partition:p20251101	time:774.1µs, open:72.3µs, close:3.13µs, loops:1, cop_task: {num: 1, max: 676.1µs, proc_keys: 0, tot_proc: 26.4µs, tot_wait: 44.9µs, copr_cache: disabled, build_task_duration: 32.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 687.3µs, rpc_info:{Cop:{num_rpc:1, total_time:661.4µs}}	index:Selection_80	255 Bytes	N/A
          └─Selection_80	1.09	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 22.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.4µs, total_wait_time: 44.9µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	N/A	N/A
            └─IndexRangeScan_79	1.37	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_154	N/A	0	root			Output: ScalarQueryCol#769	N/A	N/A
└─MaxOneRow_113	1.00	1	root		time:502.3ms, open:8.32µs, close:36.7µs, loops:1		N/A	N/A
  └─HashAgg_118	1.00	1	root		time:502.3ms, open:7.85µs, close:36µs, loops:2	funcs:count(distinct Column#720)->Column#721	13.0 MB	0 Bytes
    └─Union_122	321246.34	259560	root		time:425.6ms, open:803ns, close:35.1µs, loops:255		N/A	N/A
      ├─Projection_124	321245.22	259560	root		time:425.4ms, open:911.7µs, close:28.5µs, loops:255, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#720	838.5 KB	N/A
      │ └─IndexReader_127	321245.22	259560	root		time:427.3ms, open:910.1µs, close:10.3µs, loops:255, cop_task: {num: 7, max: 394.9ms, min: 2.67ms, avg: 60.8ms, p95: 394.9ms, max_proc_keys: 247720, p95_proc_keys: 247720, tot_proc: 181.8ms, tot_wait: 1.38ms, copr_cache: disabled, build_task_duration: 864.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 425.6ms, rpc_info:{Cop:{num_rpc:7, total_time:425.6ms}}	index:IndexRangeScan_126	28.2 MB	N/A
      │   └─IndexRangeScan_126	321245.22	259560	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:160ms, min:0s, avg: 27.1ms, p80:10ms, p95:160ms, iters:280, tasks:7}, scan_detail: {total_process_keys: 259560, total_process_keys_size: 34603500, total_keys: 11846, get_snapshot_time: 1.29ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 181.8ms, total_suspend_time: 46.7µs, total_wait_time: 1.38ms, total_kv_read_wall_time: 30ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_128	1.12	0	root		time:889.5µs, open:148.9µs, close:5.51µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#720	30.3 KB	N/A
        └─IndexReader_132	1.12	0	root	partition:p20251101	time:881.7µs, open:144.9µs, close:3.36µs, loops:1, cop_task: {num: 1, max: 702.1µs, proc_keys: 0, tot_proc: 24.9µs, tot_wait: 39µs, copr_cache: disabled, build_task_duration: 32.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 718.3µs, rpc_info:{Cop:{num_rpc:1, total_time:679.9µs}}	index:Selection_131	255 Bytes	N/A
          └─Selection_131	1.12	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 17.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 24.9µs, total_wait_time: 39µs}	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	N/A	N/A
            └─IndexRangeScan_130	1.40	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_208	N/A	0	root			Output: ScalarQueryCol#881	N/A	N/A
└─MaxOneRow_167	1.00	1	root		time:440.3ms, open:9.09µs, close:31.6µs, loops:1		N/A	N/A
  └─HashAgg_172	1.00	1	root		time:440.3ms, open:8.61µs, close:31.2µs, loops:2	funcs:count(distinct Column#838)->Column#839	8.94 MB	0 Bytes
    └─Union_176	311368.80	246339	root		time:364.4ms, open:884ns, close:30.6µs, loops:243		N/A	N/A
      ├─Projection_178	311367.71	246339	root		time:364.3ms, open:758.4µs, close:24.3µs, loops:243, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#838	649.5 KB	N/A
      │ └─IndexReader_181	311367.71	246339	root		time:366.2ms, open:756.9µs, close:10.3µs, loops:243, cop_task: {num: 7, max: 329ms, min: 2.77ms, avg: 52.1ms, p95: 329ms, max_proc_keys: 234499, p95_proc_keys: 234499, tot_proc: 165.8ms, tot_wait: 960.5µs, copr_cache: disabled, build_task_duration: 706µs, max_distsql_concurrency: 1}, fetch_resp_duration: 364.7ms, rpc_info:{Cop:{num_rpc:7, total_time:364.8ms}}	index:IndexRangeScan_180	22.5 MB	N/A
      │   └─IndexRangeScan_180	311367.71	246339	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:140ms, min:0s, avg: 22.9ms, p80:10ms, p95:140ms, iters:268, tasks:7}, scan_detail: {total_process_keys: 246339, total_process_keys_size: 27009025, total_keys: 11846, get_snapshot_time: 854.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 165.8ms, total_suspend_time: 58µs, total_wait_time: 960.5µs, total_kv_read_wall_time: 20ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_182	1.08	0	root		time:911µs, open:137.8µs, close:5.68µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#838	26.1 KB	N/A
        └─IndexReader_186	1.08	0	root	partition:p20251101	time:902.5µs, open:132.3µs, close:3.66µs, loops:1, cop_task: {num: 1, max: 739.8µs, proc_keys: 0, tot_proc: 26.1µs, tot_wait: 45.7µs, copr_cache: disabled, build_task_duration: 21.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 754.1µs, rpc_info:{Cop:{num_rpc:1, total_time:719.1µs}}	index:Selection_185	255 Bytes	N/A
          └─Selection_185	1.08	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 21.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.1µs, total_wait_time: 45.7µs}	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	N/A	N/A
            └─IndexRangeScan_184	1.35	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_264	N/A	0	root			Output: ScalarQueryCol#975	N/A	N/A
└─MaxOneRow_221	1.00	1	root		time:8.46ms, open:9.23µs, close:30.9µs, loops:1		N/A	N/A
  └─HashAgg_226	1.00	1	root		time:8.46ms, open:8.39µs, close:30.3µs, loops:2	funcs:count(distinct Column#950)->Column#951	14.9 KB	0 Bytes
    └─Union_230	182742.95	467	root		time:8.37ms, open:881ns, close:29.4µs, loops:2		N/A	N/A
      ├─Projection_232	182741.89	467	root		time:8.34ms, open:573.2µs, close:24.7µs, loops:2, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#950	80.1 KB	N/A
      │ └─IndexReader_235	182741.89	467	root		time:8.27ms, open:571.7µs, close:8.13µs, loops:2, cop_task: {num: 2, max: 6.39ms, min: 1.22ms, avg: 3.8ms, p95: 6.39ms, max_proc_keys: 243, p95_proc_keys: 243, tot_proc: 4.8ms, tot_wait: 1.04ms, copr_cache: disabled, build_task_duration: 524.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 7.61ms, rpc_info:{Cop:{num_rpc:2, total_time:7.58ms}}	index:IndexRangeScan_234	46.2 KB	N/A
      │   └─IndexRangeScan_234	182741.89	467	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:7, tasks:2}, scan_detail: {total_process_keys: 467, total_process_keys_size: 99551, total_keys: 469, get_snapshot_time: 999.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.8ms, total_suspend_time: 6.5µs, total_wait_time: 1.04ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_236	1.06	0	root		time:811.9µs, open:76µs, close:4.03µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#950	23.0 KB	N/A
        └─IndexReader_244	1.06	0	root	partition:p20251101	time:805µs, open:71.9µs, close:2.62µs, loops:1, cop_task: {num: 1, max: 704.4µs, proc_keys: 0, tot_proc: 25µs, tot_wait: 39.2µs, copr_cache: disabled, build_task_duration: 21.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 719.8µs, rpc_info:{Cop:{num_rpc:1, total_time:683.9µs}}	index:Selection_243	255 Bytes	N/A
          └─Selection_243	1.06	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 25µs, total_wait_time: 39.2µs}	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	N/A	N/A
            └─IndexRangeScan_242	1.33	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.true_ip AS `raw_distinct_2`,
    d.agent_type AS `raw_distinct_3`
  FROM deviceprofile_fact d
  WHERE d.input_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000'
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
  UNION ALL
  SELECT 'b_0146' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'b_0150' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'b_0154' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'b_0158' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
)
SELECT
  COUNT(DISTINCT CASE WHEN template_id = 'b_0146' THEN distinct_value END) AS `metric__b_0146`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0150' THEN distinct_value END) AS `metric__b_0150`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0154' THEN distinct_value END) AS `metric__b_0154`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0158' THEN distinct_value END) AS `metric__b_0158`
FROM distinct_values;
```

#### Optimized Params

```json
[
  "135.232.20.92",
  "135.232.20.92"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=695.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_63	1.00	1	root		time:662.7ms, open:9.05µs, close:80.1µs, loops:2, RU:1643.83	funcs:count(distinct Column#161)->Column#128, funcs:count(distinct Column#162)->Column#129, funcs:count(distinct Column#163)->Column#130, funcs:count(distinct Column#164)->Column#131	35.3 MB	0 Bytes
└─Projection_106	1134679.46	767762	root		time:380.6ms, open:2.12µs, close:79.1µs, loops:752, Concurrency:5	case(eq(Column#126, ?), Column#127)->Column#161, case(eq(Column#126, ?), Column#127)->Column#162, case(eq(Column#126, ?), Column#127)->Column#163, case(eq(Column#126, ?), Column#127)->Column#164	882.4 KB	N/A
  └─Union_65	1134679.46	767762	root		time:389.1ms, open:860ns, close:50.1µs, loops:752		N/A	N/A
    ├─Projection_67	1134674.75	767762	root		time:389ms, open:108.2µs, close:27.1µs, loops:752, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#126, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	923.9 KB	N/A
    │ └─IndexReader_70	1134674.75	767762	root		time:392.6ms, open:106.7µs, close:12.2µs, loops:752, cop_task: {num: 23, max: 475.5ms, min: 1.22ms, avg: 59.4ms, p95: 455.2ms, max_proc_keys: 249556, p95_proc_keys: 247720, tot_proc: 477.6ms, tot_wait: 577µs, copr_cache: disabled, build_task_duration: 36.9µs, max_distsql_concurrency: 4}, fetch_resp_duration: 389.7ms, rpc_info:{Cop:{num_rpc:23, total_time:1.37s}}	index:IndexRangeScan_69	55.5 MB	N/A
    │   └─IndexRangeScan_69	1134674.75	767762	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:160ms, min:0s, avg: 20.4ms, p80:10ms, p95:160ms, iters:837, tasks:23}, scan_detail: {total_process_keys: 767762, total_process_keys_size: 96549666, total_keys: 36007, get_snapshot_time: 265µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 477.6ms, total_suspend_time: 114.7µs, total_wait_time: 577µs, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_71	1.18	0	root		time:1.41ms, open:91.9µs, close:11.9µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_73	1.18	0	root		time:1.4ms, open:87.7µs, close:9.29µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	7.29 KB	N/A
    │   └─CTEFullScan_75	1.47	0	root	CTE:raw_boundary	time:1.4ms, open:84µs, close:7.65µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_79	1.18	0	root		time:1.41ms, open:1.4ms, close:3.32µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	18.2 KB	N/A
    │ └─Selection_81	1.18	0	root		time:1.4ms, open:1.4ms, close:1.43µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	74.4 KB	N/A
    │   └─CTEFullScan_83	1.47	0	root	CTE:raw_boundary	time:1.4ms, open:1.39ms, close:139ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_87	1.18	0	root		time:1.41ms, open:1.41ms, close:2.47µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	72.8 KB	N/A
    │ └─Selection_89	1.18	0	root		time:1.41ms, open:1.4ms, close:979ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	41.7 KB	N/A
    │   └─CTEFullScan_91	1.47	0	root	CTE:raw_boundary	time:1.4ms, open:1.4ms, close:162ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_95	1.18	0	root		time:1.42ms, open:1.41ms, close:3.74µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	55.5 KB	N/A
      └─Selection_97	1.18	0	root		time:1.41ms, open:1.41ms, close:1.63µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	53.3 KB	N/A
        └─CTEFullScan_99	1.47	0	root	CTE:raw_boundary	time:1.41ms, open:1.4ms, close:143ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.47	0	root		time:1.4ms, open:84µs, close:7.65µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_50(Seed Part)	1.47	0	root		time:1.38ms, open:80.6µs, close:5.98µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.agent_type	63.6 KB	N/A
  └─IndexReader_55	1.83	0	root	partition:p20251101	time:1.37ms, open:76µs, close:4.6µs, loops:1, cop_task: {num: 1, max: 1.26ms, proc_keys: 0, tot_proc: 27.1µs, tot_wait: 537.4µs, copr_cache: disabled, build_task_duration: 23.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.28ms, rpc_info:{Cop:{num_rpc:1, total_time:1.25ms}}	index:Selection_54	255 Bytes	N/A
    └─Selection_54	1.83	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 507.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 27.1µs, total_wait_time: 537.4µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type))))	N/A	N/A
      └─IndexRangeScan_53	1.84	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```

### 5. group_c_bundle_018

- Filter/window: `d.true_ip = %s` / `30d`
- Chosen event: `INV0039365135` kind=`hot_true_ip` error=`(1105, 'context canceled')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 1601.9 ms | ok |
| `optimized_default` | `{}` | 416.7 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 412.0 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 402.7 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 372.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 362.1 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0102`,
  SUM(p.amount) AS `metric__c_0103`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0104`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0105`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1773281789762
  AND d.jms_timestamp >= '2026-03-11 19:16:29.762000'
GROUP BY d.true_ip;
```

#### Original Params

```json
[
  "74.179.68.52"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=1601.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_13	127.11	1	root		time:1.57s, open:976.1µs, close:28.9µs, loops:2, RU:6141.28	group by:intuit_risk.deviceprofile_fact.true_ip, funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	561.3 KB	0 Bytes
└─Projection_21	366700.29	4488	root		time:1.57s, open:967.4µs, close:28µs, loops:8, Concurrency:5	intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.deviceprofile_fact.true_ip	648.5 KB	N/A
  └─IndexHashJoin_30	366700.29	4488	root		time:1.57s, open:965.9µs, close:8.64µs, loops:8, inner:{total:6.53s, concurrency:5, task:7, construct:79ms, fetch:6.44s, build:13.3ms, join:5.26ms}	inner join, inner:IndexReader_58, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	20.5 MB	N/A
    ├─IndexReader_55(Build)	234478.88	99450	root	partition:p20260401,p20260501,p20260601,pmax	time:169.5ms, open:961.1µs, close:5.93µs, loops:99, cop_task: {num: 11, max: 167.7ms, min: 1.11ms, avg: 25ms, p95: 167.7ms, max_proc_keys: 117427, p95_proc_keys: 117427, tot_proc: 217.3ms, tot_wait: 3.39ms, copr_cache: disabled, build_task_duration: 912.5µs, max_distsql_concurrency: 4}, fetch_resp_duration: 166.9ms, rpc_info:{Cop:{num_rpc:11, total_time:275ms}}	index:Selection_54	4.76 MB	N/A
    │ └─Selection_54	234478.88	99450	cop[tikv]		tikv_task:{proc max:130ms, min:0s, avg: 17.3ms, p80:10ms, p95:130ms, iters:206, tasks:11}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 40538991, total_keys: 55418, get_snapshot_time: 3.92ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 217.3ms, total_suspend_time: 238.6µs, total_wait_time: 3.39ms, total_kv_read_wall_time: 60ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_53	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:130ms, min:0s, avg: 17.3ms, p80:10ms, p95:130ms, iters:206, tasks:11}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_58(Probe)	366700.29	4488	root	partition:p20260401,p20260501,p20260601,pmax	total_time:6.41s, total_open:175.4ms, total_close:63.3µs, loops:16, cop_task: {num: 82, max: 1.41s, min: 1.58ms, avg: 249.7ms, p95: 1.14s, max_proc_keys: 224, p95_proc_keys: 193, tot_proc: 16.2s, tot_wait: 114.8ms, copr_cache: disabled, build_task_duration: 45.3ms, max_distsql_concurrency: 13}, fetch_resp_duration: 6.23s, rpc_info:{Cop:{num_rpc:85, total_time:20.5s}, rpc_errors:{bucket_version_not_match:3}}, backoff{regionMiss: 6ms}	index:Selection_57	7.21 KB	N/A
      └─Selection_57	366700.29	4488	cop[tikv]		tikv_task:{proc max:1.17s, min:0s, avg: 198.4ms, p80:340ms, p95:910ms, iters:138, tasks:82}, scan_detail: {total_process_keys: 4488, total_process_keys_size: 1208296, total_keys: 35907, get_snapshot_time: 7.62ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 16.2s, total_suspend_time: 81.9ms, total_wait_time: 114.8ms, total_kv_read_wall_time: 15.5s}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_56	496902.96	4488	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:1.17s, min:0s, avg: 198.4ms, p80:340ms, p95:910ms, iters:138, tasks:82}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0102`,
  SUM(p.amount) AS `metric__c_0103`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0104`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0105`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1773281789762
  AND d.jms_timestamp >= '2026-03-11 19:16:29.762000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  "74.179.68.52"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=362.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Selection_13	0.80	1	root		time:328.6ms, open:89.5µs, close:9.12µs, loops:2, RU:1072.42	gt(Column#106, ?)	18.1 KB	N/A
└─HashAgg_17	1.00	1	root		time:328.6ms, open:87.1µs, close:8.51µs, loops:3	funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	543.7 KB	0 Bytes
  └─IndexHashJoin_28	366700.29	4488	root		time:327ms, open:79.5µs, close:8.01µs, loops:8, inner:{total:614.5ms, concurrency:5, task:7, construct:78.9ms, fetch:531.2ms, build:13.5ms, join:4.35ms}	inner join, inner:IndexReader_56, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	18.8 MB	N/A
    ├─IndexReader_53(Build)	234478.88	99450	root	partition:p20260401,p20260501,p20260601,pmax	time:159.5ms, open:78µs, close:5.56µs, loops:99, cop_task: {num: 11, max: 158.6ms, min: 553.3µs, avg: 19.4ms, p95: 158.6ms, max_proc_keys: 117427, p95_proc_keys: 117427, tot_proc: 163.8ms, tot_wait: 330µs, copr_cache: disabled, build_task_duration: 27.1µs, max_distsql_concurrency: 4}, fetch_resp_duration: 158ms, rpc_info:{Cop:{num_rpc:11, total_time:212.8ms}}	index:Selection_52	4.76 MB	N/A
    │ └─Selection_52	234478.88	99450	cop[tikv]		tikv_task:{proc max:130ms, min:0s, avg: 15.5ms, p80:10ms, p95:130ms, iters:206, tasks:11}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 40538991, total_keys: 55418, get_snapshot_time: 174.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 163.8ms, total_suspend_time: 124.9µs, total_wait_time: 330µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_51	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:120ms, min:0s, avg: 14.5ms, p80:10ms, p95:120ms, iters:206, tasks:11}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_56(Probe)	366700.29	4488	root	partition:p20260401,p20260501,p20260601,pmax	total_time:498.5ms, total_open:155.9ms, total_close:67.1µs, loops:16, cop_task: {num: 85, max: 94.5ms, min: 1.07ms, avg: 19.5ms, p95: 69.8ms, max_proc_keys: 224, p95_proc_keys: 193, tot_proc: 1.01s, tot_wait: 2.57ms, copr_cache: disabled, build_task_duration: 27.9ms, max_distsql_concurrency: 13}, fetch_resp_duration: 338.4ms, rpc_info:{Cop:{num_rpc:85, total_time:1.65s}}	index:Selection_55	8.28 KB	N/A
      └─Selection_55	366700.29	4488	cop[tikv]		tikv_task:{proc max:70ms, min:0s, avg: 11.4ms, p80:10ms, p95:60ms, iters:141, tasks:85}, scan_detail: {total_process_keys: 4488, total_process_keys_size: 1213878, total_keys: 36249, get_snapshot_time: 1.19ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.01s, total_suspend_time: 724.3µs, total_wait_time: 2.57ms, total_kv_read_wall_time: 300ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_54	496902.96	4488	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:70ms, min:0s, avg: 11.4ms, p80:10ms, p95:60ms, iters:141, tasks:85}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### 6. group_c_bundle_021

- Filter/window: `p.merchant_account_number = %s` / `30d`
- Chosen event: `INV0037793946` kind=`hot_merchant_account_number` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 968.5 ms | ok |
| `optimized_default` | `{}` | 316.7 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 301.5 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 307.8 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 337.6 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 360.8 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(DISTINCT(d.smart_id)) AS `metric__c_0204`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__c_0205`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__c_0206`,
  COUNT(DISTINCT(d.true_ip)) AS `metric__c_0207`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__c_0208`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__c_0209`,
  COUNT(DISTINCT(d.agent_os)) AS `metric__c_0210`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.smart_id END) AS `metric__c_0263`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0263`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.exact_id END) AS `metric__c_0264`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0264`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.input_ip END) AS `metric__c_0265`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0265`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.smart_id END) AS `metric__c_0272`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0272`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.exact_id END) AS `metric__c_0273`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0273`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.input_ip END) AS `metric__c_0274`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0274`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.smart_id END) AS `metric__c_0281`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0281`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.exact_id END) AS `metric__c_0282`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0282`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.input_ip END) AS `metric__c_0283`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0283`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.smart_id END) AS `metric__c_0290`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0290`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.exact_id END) AS `metric__c_0291`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0291`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.input_ip END) AS `metric__c_0292`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0292`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0337`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0337`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0338`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0338`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0339`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0339`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0340`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0340`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0349`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0349`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0350`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0350`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0351`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0351`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0352`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0352`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0361`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0361`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0362`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0362`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0363`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0363`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0364`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0364`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0373`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0373`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0374`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0374`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0375`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0375`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0376`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0376`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0385`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0385`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0386`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0386`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0387`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0387`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0388`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0388`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0397`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0397`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0398`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0398`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0399`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0399`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0400`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0400`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1772739440017
  AND d.jms_timestamp >= '2026-03-05 11:37:20.017000'
GROUP BY p.merchant_account_number;
```

#### Original Params

```json
[
  5247719989330882
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=968.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_8	108.67	1	root		time:903.5ms, open:104µs, close:48.4µs, loops:2, RU:937.23, Concurrency:OFF	Column#106, Column#107, Column#108, Column#109, Column#110, Column#111, Column#112, Column#113, Column#114, Column#115, Column#114, Column#116, Column#114, Column#117, Column#118, Column#119, Column#118, Column#120, Column#118, Column#121, Column#122, Column#123, Column#122, Column#124, Column#122, Column#125, Column#126, Column#127, Column#126, Column#128, Column#126, Column#129, Column#130, Column#131, Column#130, Column#132, Column#133, Column#134, Column#133, Column#135, Column#136, Column#137, Column#136, Column#138, Column#139, Column#140, Column#139, Column#141, Column#142, Column#143, Column#142, Column#144, Column#145, Column#146, Column#145, Column#147, Column#148, Column#149, Column#148, Column#150, Column#151, Column#152, Column#151, Column#153, Column#154, Column#155, Column#154, Column#156, Column#157, Column#158, Column#157, Column#159, Column#160, Column#161, Column#160, Column#162, Column#163, Column#164, Column#163	297.8 KB	N/A
└─HashAgg_12	108.67	1	root		time:903.4ms, open:98.7µs, close:46.7µs, loops:2	group by:Column#242, funcs:count(distinct Column#183)->Column#106, funcs:count(distinct Column#184)->Column#107, funcs:count(distinct Column#185)->Column#108, funcs:count(distinct Column#186)->Column#109, funcs:count(distinct Column#187)->Column#110, funcs:count(distinct Column#188)->Column#111, funcs:count(distinct Column#189)->Column#112, funcs:count(distinct Column#190)->Column#113, funcs:sum(Column#191)->Column#114, funcs:count(distinct Column#192)->Column#115, funcs:count(distinct Column#193)->Column#116, funcs:count(distinct Column#194)->Column#117, funcs:sum(Column#195)->Column#118, funcs:count(distinct Column#196)->Column#119, funcs:count(distinct Column#197)->Column#120, funcs:count(distinct Column#198)->Column#121, funcs:sum(Column#199)->Column#122, funcs:count(distinct Column#200)->Column#123, funcs:count(distinct Column#201)->Column#124, funcs:count(distinct Column#202)->Column#125, funcs:sum(Column#203)->Column#126, funcs:count(distinct Column#204)->Column#127, funcs:count(distinct Column#205)->Column#128, funcs:min(Column#206)->Column#129, funcs:sum(Column#207)->Column#130, funcs:max(Column#208)->Column#131, funcs:min(Column#209)->Column#132, funcs:sum(Column#210)->Column#133, funcs:max(Column#211)->Column#134, funcs:min(Column#212)->Column#135, funcs:sum(Column#213)->Column#136, funcs:max(Column#214)->Column#137, funcs:min(Column#215)->Column#138, funcs:sum(Column#216)->Column#139, funcs:max(Column#217)->Column#140, funcs:min(Column#218)->Column#141, funcs:sum(Column#219)->Column#142, funcs:max(Column#220)->Column#143, funcs:min(Column#221)->Column#144, funcs:sum(Column#222)->Column#145, funcs:max(Column#223)->Column#146, funcs:min(Column#224)->Column#147, funcs:sum(Column#225)->Column#148, funcs:max(Column#226)->Column#149, funcs:min(Column#227)->Column#150, funcs:sum(Column#228)->Column#151, funcs:max(Column#229)->Column#152, funcs:min(Column#230)->Column#153, funcs:sum(Column#231)->Column#154, funcs:max(Column#232)->Column#155, funcs:min(Column#233)->Column#156, funcs:sum(Column#234)->Column#157, funcs:max(Column#235)->Column#158, funcs:min(Column#236)->Column#159, funcs:sum(Column#237)->Column#160, funcs:max(Column#238)->Column#161, funcs:min(Column#239)->Column#162, funcs:sum(Column#240)->Column#163, funcs:max(Column#241)->Column#164	3.08 MB	0 Bytes
  └─Projection_81	50174.75	3334	root		time:895.1ms, open:83.9µs, close:45.8µs, loops:6, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#183, intuit_risk.deviceprofile_fact.exact_id->Column#184, intuit_risk.deviceprofile_fact.input_ip->Column#185, intuit_risk.deviceprofile_fact.true_ip->Column#186, intuit_risk.deviceprofile_fact.proxy_ip->Column#187, intuit_risk.deviceprofile_fact.agent_type->Column#188, intuit_risk.deviceprofile_fact.agent_os->Column#189, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#190, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#191, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#192, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#193, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#194, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#196, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#197, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#198, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#199, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#200, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#201, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#202, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#203, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#204, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#205, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#207, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#208, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#209, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#210, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#212, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#213, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#214, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#215, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#217, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#218, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#221, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#222, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#223, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#225, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#226, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#230, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#232, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#234, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#235, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#236, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#237, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#238, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#239, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#240, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#241, intuit_risk.pmt_txn_fact.merchant_account_number->Column#242	7.03 MB	N/A
    └─IndexHashJoin_30	50174.75	3334	root		time:895ms, open:82.8µs, close:13µs, loops:6, inner:{total:2.07s, concurrency:5, task:3, construct:7.22ms, fetch:2.06s, build:1.48ms, join:2.88ms}	inner join, inner:IndexLookUp_45, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	2.59 MB	N/A
      ├─IndexReader_41(Build)	28365.44	11721	root	partition:p20260401,p20260501,p20260601,pmax	time:17.8ms, open:81.5µs, close:9.24µs, loops:14, cop_task: {num: 13, max: 6ms, min: 637.1µs, avg: 2.42ms, p95: 6ms, max_proc_keys: 5098, p95_proc_keys: 5098, tot_proc: 18.1ms, tot_wait: 1.8ms, copr_cache: disabled, build_task_duration: 28.7µs, max_distsql_concurrency: 4}, fetch_resp_duration: 17.4ms, rpc_info:{Cop:{num_rpc:13, total_time:31.3ms}}	index:Selection_40	315.1 KB	N/A
      │ └─Selection_40	28365.44	11721	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.54ms, p80:0s, p95:10ms, iters:62, tasks:13}, scan_detail: {total_process_keys: 18068, total_process_keys_size: 2321747, total_keys: 18081, get_snapshot_time: 1.58ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.1ms, total_suspend_time: 26.1µs, total_wait_time: 1.8ms, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
      │   └─IndexRangeScan_39	38437.04	18068	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1.54ms, p80:0s, p95:10ms, iters:62, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
      └─IndexLookUp_45(Probe)	50174.75	3334	root	partition:p20260401,p20260501,p20260601,pmax	total_time:2.05s, total_open:14.9ms, total_close:25.4µs, loops:8, index_task: {total_time: 1.95s, fetch_handle: 1.95s, build: 9.6µs, wait: 27.5µs}, table_task: {total_time: 137.9ms, num: 7, concurrency: 5}, next: {wait_index: 1.95s, wait_table_lookup_build: 1.4ms, wait_table_lookup_resp: 81.3ms}		1.71 MB	N/A
        ├─Selection_44(Build)	50174.75	3334	cop[tikv]		total_time:1.95s, total_open:0s, total_close:0s, loops:25, cop_task: {num: 15, max: 826.7ms, min: 3.11ms, avg: 155.3ms, p95: 826.7ms, max_proc_keys: 1163, p95_proc_keys: 1163, tot_proc: 2.25s, tot_wait: 1.9ms, copr_cache: disabled, build_task_duration: 3.31ms, max_distsql_concurrency: 2}, fetch_resp_duration: 1.95s, rpc_info:{Cop:{num_rpc:15, total_time:2.33s}}, tikv_task:{proc max:820ms, min:0s, avg: 148.7ms, p80:420ms, p95:820ms, iters:39, tasks:15}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 344520, total_keys: 22423, get_snapshot_time: 1.67ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.25s, total_suspend_time: 2.59ms, total_wait_time: 1.9ms, total_kv_read_wall_time: 2.11s}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
        │ └─IndexRangeScan_42	74076.41	3334	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:820ms, min:0s, avg: 148ms, p80:420ms, p95:820ms, iters:39, tasks:15}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
        └─TableRowIDScan_43(Probe)	50174.75	3334	cop[tikv]	table:d	total_time:135.3ms, total_open:0s, total_close:33.9µs, loops:14, cop_task: {num: 417, max: 16.1ms, min: 0s, avg: 973µs, p95: 4.27ms, max_proc_keys: 43, p95_proc_keys: 27, tot_proc: 521.8ms, tot_wait: 226.3ms, copr_cache: disabled, build_task_duration: 1.13ms, max_distsql_concurrency: 12, max_extra_concurrency: 7, store_batch_num: 297, store_batch_fallback_num: 21}, fetch_resp_duration: 133.2ms, rpc_info:{Cop:{num_rpc:120, total_time:404.5ms}}, tikv_task:{proc max:20ms, min:0s, avg: 1.63ms, p80:0s, p95:10ms, iters:427, tasks:417}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 2010814, total_keys: 3334, get_snapshot_time: 132ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 521.8ms, total_suspend_time: 7.55ms, total_wait_time: 226.3ms, total_kv_read_wall_time: 680ms}	keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(DISTINCT(d.smart_id)) AS `metric__c_0204`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__c_0205`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__c_0206`,
  COUNT(DISTINCT(d.true_ip)) AS `metric__c_0207`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__c_0208`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__c_0209`,
  COUNT(DISTINCT(d.agent_os)) AS `metric__c_0210`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.smart_id END) AS `metric__c_0263`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0263`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.exact_id END) AS `metric__c_0264`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0264`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.input_ip END) AS `metric__c_0265`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0265`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.smart_id END) AS `metric__c_0272`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0272`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.exact_id END) AS `metric__c_0273`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0273`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.input_ip END) AS `metric__c_0274`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0274`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.smart_id END) AS `metric__c_0281`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0281`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.exact_id END) AS `metric__c_0282`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0282`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.input_ip END) AS `metric__c_0283`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0283`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.smart_id END) AS `metric__c_0290`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0290`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.exact_id END) AS `metric__c_0291`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0291`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.input_ip END) AS `metric__c_0292`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0292`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0337`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0337`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0338`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0338`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0339`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0339`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0340`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0340`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0349`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0349`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0350`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0350`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0351`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0351`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0352`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0352`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0361`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0361`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0362`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0362`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0363`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0363`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0364`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0364`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0373`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0373`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0374`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0374`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0375`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0375`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0376`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0376`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0385`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0385`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0386`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0386`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0387`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0387`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0388`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0388`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0397`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0397`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0398`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0398`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0399`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0399`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0400`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0400`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1772739440017
  AND d.jms_timestamp >= '2026-03-05 11:37:20.017000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  5247719989330882
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_hashagg_16_8
-- explain_analyze_elapsed_ms=301.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_10	0.80	1	root		time:240.8ms, open:111µs, close:46.9µs, loops:2, RU:339.81, Concurrency:OFF	Column#106->Column#166, Column#107->Column#167, Column#108->Column#168, Column#109->Column#169, Column#110->Column#170, Column#111->Column#171, Column#112->Column#172, Column#113->Column#173, Column#114->Column#174, Column#115->Column#175, Column#114->Column#176, Column#116->Column#177, Column#114->Column#178, Column#117->Column#179, Column#118->Column#180, Column#119->Column#181, Column#118->Column#182, Column#120->Column#183, Column#118->Column#184, Column#121->Column#185, Column#122->Column#186, Column#123->Column#187, Column#122->Column#188, Column#124->Column#189, Column#122->Column#190, Column#125->Column#191, Column#126->Column#192, Column#127->Column#193, Column#126->Column#194, Column#128->Column#195, Column#126->Column#196, Column#129->Column#197, Column#130->Column#198, Column#131->Column#199, Column#130->Column#200, Column#132->Column#201, Column#133->Column#202, Column#134->Column#203, Column#133->Column#204, Column#135->Column#205, Column#136->Column#206, Column#137->Column#207, Column#136->Column#208, Column#138->Column#209, Column#139->Column#210, Column#140->Column#211, Column#139->Column#212, Column#141->Column#213, Column#142->Column#214, Column#143->Column#215, Column#142->Column#216, Column#144->Column#217, Column#145->Column#218, Column#146->Column#219, Column#145->Column#220, Column#147->Column#221, Column#148->Column#222, Column#149->Column#223, Column#148->Column#224, Column#150->Column#225, Column#151->Column#226, Column#152->Column#227, Column#151->Column#228, Column#153->Column#229, Column#154->Column#230, Column#155->Column#231, Column#154->Column#232, Column#156->Column#233, Column#157->Column#234, Column#158->Column#235, Column#157->Column#236, Column#159->Column#237, Column#160->Column#238, Column#161->Column#239, Column#160->Column#240, Column#162->Column#241, Column#163->Column#242, Column#164->Column#243, Column#163->Column#244	337.3 KB	N/A
└─Selection_12	0.80	1	root		time:240.7ms, open:106.4µs, close:45.2µs, loops:2	gt(Column#165, ?)	340.4 KB	N/A
  └─HashAgg_16	1.00	1	root		time:240.7ms, open:101µs, close:44.4µs, loops:3	funcs:count(distinct Column#263)->Column#106, funcs:count(distinct Column#264)->Column#107, funcs:count(distinct Column#265)->Column#108, funcs:count(distinct Column#266)->Column#109, funcs:count(distinct Column#267)->Column#110, funcs:count(distinct Column#268)->Column#111, funcs:count(distinct Column#269)->Column#112, funcs:count(distinct Column#270)->Column#113, funcs:sum(Column#271)->Column#114, funcs:count(distinct Column#272)->Column#115, funcs:count(distinct Column#273)->Column#116, funcs:count(distinct Column#274)->Column#117, funcs:sum(Column#275)->Column#118, funcs:count(distinct Column#276)->Column#119, funcs:count(distinct Column#277)->Column#120, funcs:count(distinct Column#278)->Column#121, funcs:sum(Column#279)->Column#122, funcs:count(distinct Column#280)->Column#123, funcs:count(distinct Column#281)->Column#124, funcs:count(distinct Column#282)->Column#125, funcs:sum(Column#283)->Column#126, funcs:count(distinct Column#284)->Column#127, funcs:count(distinct Column#285)->Column#128, funcs:min(Column#286)->Column#129, funcs:sum(Column#287)->Column#130, funcs:max(Column#288)->Column#131, funcs:min(Column#289)->Column#132, funcs:sum(Column#290)->Column#133, funcs:max(Column#291)->Column#134, funcs:min(Column#292)->Column#135, funcs:sum(Column#293)->Column#136, funcs:max(Column#294)->Column#137, funcs:min(Column#295)->Column#138, funcs:sum(Column#296)->Column#139, funcs:max(Column#297)->Column#140, funcs:min(Column#298)->Column#141, funcs:sum(Column#299)->Column#142, funcs:max(Column#300)->Column#143, funcs:min(Column#301)->Column#144, funcs:sum(Column#302)->Column#145, funcs:max(Column#303)->Column#146, funcs:min(Column#304)->Column#147, funcs:sum(Column#305)->Column#148, funcs:max(Column#306)->Column#149, funcs:min(Column#307)->Column#150, funcs:sum(Column#308)->Column#151, funcs:max(Column#309)->Column#152, funcs:min(Column#310)->Column#153, funcs:sum(Column#311)->Column#154, funcs:max(Column#312)->Column#155, funcs:min(Column#313)->Column#156, funcs:sum(Column#314)->Column#157, funcs:max(Column#315)->Column#158, funcs:min(Column#316)->Column#159, funcs:sum(Column#317)->Column#160, funcs:max(Column#318)->Column#161, funcs:min(Column#319)->Column#162, funcs:sum(Column#320)->Column#163, funcs:max(Column#321)->Column#164, funcs:count(?)->Column#165	3.07 MB	0 Bytes
    └─Projection_84	50174.75	3334	root		time:232.1ms, open:84.1µs, close:43.6µs, loops:6, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#263, intuit_risk.deviceprofile_fact.exact_id->Column#264, intuit_risk.deviceprofile_fact.input_ip->Column#265, intuit_risk.deviceprofile_fact.true_ip->Column#266, intuit_risk.deviceprofile_fact.proxy_ip->Column#267, intuit_risk.deviceprofile_fact.agent_type->Column#268, intuit_risk.deviceprofile_fact.agent_os->Column#269, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#270, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#271, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#272, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#273, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#274, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#275, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#276, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#277, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#278, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#279, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#280, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#281, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#282, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#283, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#284, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#285, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#286, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#287, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#288, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#289, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#290, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#291, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#292, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#293, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#294, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#295, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#296, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#297, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#298, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#299, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#300, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#301, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#302, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#303, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#304, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#305, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#306, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#307, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#308, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#309, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#310, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#311, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#312, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#313, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#314, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#315, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#316, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#317, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#318, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#319, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#320, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#321	6.52 MB	N/A
      └─IndexHashJoin_28	50174.75	3334	root		time:232.3ms, open:82.7µs, close:12.9µs, loops:6, inner:{total:455.5ms, concurrency:5, task:3, construct:7.27ms, fetch:445.4ms, build:1.44ms, join:2.8ms}	inner join, inner:IndexLookUp_43, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	2.65 MB	N/A
        ├─IndexReader_39(Build)	28365.44	11721	root	partition:p20260401,p20260501,p20260601,pmax	time:15.2ms, open:81.3µs, close:9.44µs, loops:14, cop_task: {num: 13, max: 4.81ms, min: 676µs, avg: 1.79ms, p95: 4.81ms, max_proc_keys: 5098, p95_proc_keys: 5098, tot_proc: 11.2ms, tot_wait: 397.9µs, copr_cache: disabled, build_task_duration: 25µs, max_distsql_concurrency: 4}, fetch_resp_duration: 14.8ms, rpc_info:{Cop:{num_rpc:13, total_time:23.2ms}}	index:Selection_38	315.1 KB	N/A
        │ └─Selection_38	28365.44	11721	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 769.2µs, p80:0s, p95:10ms, iters:62, tasks:13}, scan_detail: {total_process_keys: 18068, total_process_keys_size: 2321747, total_keys: 18081, get_snapshot_time: 162.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 11.2ms, total_suspend_time: 21.1µs, total_wait_time: 397.9µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        │   └─IndexRangeScan_37	38437.04	18068	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 769.2µs, p80:0s, p95:10ms, iters:62, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
        └─IndexLookUp_43(Probe)	50174.75	3334	root	partition:p20260401,p20260501,p20260601,pmax	total_time:442ms, total_open:15.2ms, total_close:23.7µs, loops:8, index_task: {total_time: 380ms, fetch_handle: 380ms, build: 11.8µs, wait: 29.6µs}, table_task: {total_time: 60.9ms, num: 7, concurrency: 5}, next: {wait_index: 384ms, wait_table_lookup_build: 1.34ms, wait_table_lookup_resp: 40.7ms}		1.71 MB	N/A
          ├─Selection_42(Build)	50174.75	3334	cop[tikv]		total_time:380.1ms, total_open:0s, total_close:0s, loops:25, cop_task: {num: 15, max: 182.4ms, min: 3.61ms, avg: 50.9ms, p95: 182.4ms, max_proc_keys: 1163, p95_proc_keys: 1163, tot_proc: 617.7ms, tot_wait: 252.9µs, copr_cache: disabled, build_task_duration: 3.28ms, max_distsql_concurrency: 2}, fetch_resp_duration: 379.6ms, rpc_info:{Cop:{num_rpc:15, total_time:762.3ms}}, tikv_task:{proc max:150ms, min:0s, avg: 40.7ms, p80:100ms, p95:150ms, iters:39, tasks:15}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 181764, total_keys: 519, get_snapshot_time: 227.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 617.7ms, total_suspend_time: 35µs, total_wait_time: 252.9µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │ └─IndexRangeScan_40	74076.41	3334	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:150ms, min:0s, avg: 40.7ms, p80:100ms, p95:150ms, iters:39, tasks:15}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
          └─TableRowIDScan_41(Probe)	50174.75	3334	cop[tikv]	table:d	total_time:58.4ms, total_open:0s, total_close:32.9µs, loops:14, cop_task: {num: 418, max: 2.55ms, min: 0s, avg: 283µs, p95: 1.45ms, max_proc_keys: 43, p95_proc_keys: 27, tot_proc: 101.5ms, tot_wait: 26.8ms, copr_cache: disabled, build_task_duration: 1.1ms, max_distsql_concurrency: 12, max_extra_concurrency: 7, store_batch_num: 301, store_batch_fallback_num: 18}, fetch_resp_duration: 56.5ms, rpc_info:{Cop:{num_rpc:117, total_time:117.2ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:428, tasks:418}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 2010814, total_keys: 3334, get_snapshot_time: 3.05ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 101.5ms, total_suspend_time: 44.5µs, total_wait_time: 26.8ms}	keep order:false	N/A	N/A
```

### 7. group_b_bundle_020

- Filter/window: `d.true_ip = %s` / `180d`
- Chosen event: `INV0039365135` kind=`hot_true_ip` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 2884.2 ms | ok |
| `optimized_default` | `{}` | 1151.3 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 1178.1 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 1163.4 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 1128.4 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 1148.3 ms | ok |

#### Original SQL

```sql
SELECT
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0162' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.exact_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0162`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0166' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.smart_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.smart_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0166`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0170' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.input_ip AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.input_ip IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0170`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0174' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.proxy_ip AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.proxy_ip IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0174`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0178' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.agent_type AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.agent_type IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0178`;
```

#### Original Params

```json
[
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=2884.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_324	1.00	1	root		time:8.94µs, open:2.82µs, close:961ns, loops:2, RU:3563.41, Concurrency:OFF	?->Column#788, ?->Column#908, ?->Column#1020, ?->Column#1114, ?->Column#1210	0 Bytes	N/A
└─TableDual_326	1.00	1	root		time:1.99µs, open:182ns, close:190ns, loops:2	rows:1	N/A	N/A
ScalarSubQuery_111	N/A	0	root			Output: ScalarQueryCol#787	N/A	N/A
└─MaxOneRow_70	1.00	1	root		time:912ms, open:9.39µs, close:42.4µs, loops:1		N/A	N/A
  └─HashAgg_75	1.00	1	root		time:912ms, open:8.71µs, close:41.8µs, loops:2	funcs:count(distinct Column#738)->Column#739	24.2 MB	0 Bytes
    └─Union_79	693750.42	523720	root		time:743.1ms, open:926ns, close:41.1µs, loops:513		N/A	N/A
      ├─Projection_81	693749.40	523720	root		time:743ms, open:874.1µs, close:34.1µs, loops:513, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#738	831.7 KB	N/A
      │ └─IndexReader_84	693749.40	523720	root		time:749.5ms, open:871.3µs, close:13.8µs, loops:513, cop_task: {num: 8, max: 472.9ms, min: 3.37ms, avg: 104.8ms, p95: 472.9ms, max_proc_keys: 289760, p95_proc_keys: 289760, tot_proc: 348.4ms, tot_wait: 982.9µs, copr_cache: disabled, build_task_duration: 821.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 747.2ms, rpc_info:{Cop:{num_rpc:8, total_time:838.4ms}}	index:IndexRangeScan_83	56.7 MB	N/A
      │   └─IndexRangeScan_83	693749.40	523720	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:180ms, min:0s, avg: 43.8ms, p80:140ms, p95:180ms, iters:542, tasks:8}, scan_detail: {total_process_keys: 523720, total_process_keys_size: 68016120, total_keys: 11846, get_snapshot_time: 917.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 348.4ms, total_suspend_time: 65.8µs, total_wait_time: 982.9µs, total_kv_read_wall_time: 30ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_85	1.02	0	root		time:1.9ms, open:61.2µs, close:5.77µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#738	10.4 KB	N/A
        └─IndexReader_92	1.02	0	root	partition:p20251101	time:1.89ms, open:57.9µs, close:3.46µs, loops:1, cop_task: {num: 1, max: 1.81ms, proc_keys: 0, tot_proc: 21.4µs, tot_wait: 1.22ms, copr_cache: disabled, build_task_duration: 19.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.82ms, rpc_info:{Cop:{num_rpc:1, total_time:1.8ms}}	index:Selection_91	259 Bytes	N/A
          └─Selection_91	1.02	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 1.19ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 21.4µs, total_wait_time: 1.22ms}	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	N/A	N/A
            └─IndexRangeScan_90	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_165	N/A	0	root			Output: ScalarQueryCol#907	N/A	N/A
└─MaxOneRow_124	1.00	1	root		time:978.4ms, open:9.44µs, close:35.8µs, loops:1		N/A	N/A
  └─HashAgg_129	1.00	1	root		time:978.4ms, open:8.68µs, close:35.4µs, loops:2	funcs:count(distinct Column#856)->Column#857	23.2 MB	0 Bytes
    └─Union_133	695358.92	519249	root		time:809.5ms, open:899ns, close:34.8µs, loops:509		N/A	N/A
      ├─Projection_135	695357.87	519249	root		time:808.8ms, open:772.6µs, close:29.2µs, loops:509, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#856	820.0 KB	N/A
      │ └─IndexReader_138	695357.87	519249	root		time:812.1ms, open:770.8µs, close:11.7µs, loops:509, cop_task: {num: 8, max: 497ms, min: 4.77ms, avg: 110.9ms, p95: 497ms, max_proc_keys: 289760, p95_proc_keys: 289760, tot_proc: 316.1ms, tot_wait: 1.26ms, copr_cache: disabled, build_task_duration: 719.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 809.8ms, rpc_info:{Cop:{num_rpc:8, total_time:887.2ms}}	index:IndexRangeScan_137	56.2 MB	N/A
      │   └─IndexRangeScan_137	695357.87	519249	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:150ms, min:0s, avg: 40ms, p80:130ms, p95:150ms, iters:538, tasks:8}, scan_detail: {total_process_keys: 519249, total_process_keys_size: 67448303, total_keys: 11846, get_snapshot_time: 1.18ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 316.1ms, total_suspend_time: 68.3µs, total_wait_time: 1.26ms, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_139	1.04	0	root		time:811.1µs, open:84.9µs, close:4.46µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#856	10.7 KB	N/A
        └─IndexReader_146	1.04	0	root	partition:p20251101	time:803.7µs, open:80.1µs, close:2.89µs, loops:1, cop_task: {num: 1, max: 694.5µs, proc_keys: 0, tot_proc: 22.2µs, tot_wait: 37.3µs, copr_cache: disabled, build_task_duration: 27.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 710.3µs, rpc_info:{Cop:{num_rpc:1, total_time:672.8µs}}	index:Selection_145	255 Bytes	N/A
          └─Selection_145	1.04	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 22.2µs, total_wait_time: 37.3µs}	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	N/A	N/A
            └─IndexRangeScan_144	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_219	N/A	0	root			Output: ScalarQueryCol#1019	N/A	N/A
└─MaxOneRow_178	1.00	1	root		time:847ms, open:9.57µs, close:35.9µs, loops:1		N/A	N/A
  └─HashAgg_183	1.00	1	root		time:847ms, open:9.08µs, close:35.5µs, loops:2	funcs:count(distinct Column#976)->Column#977	9.42 MB	0 Bytes
    └─Union_187	651787.72	460693	root		time:711.1ms, open:974ns, close:34.8µs, loops:452		N/A	N/A
      ├─Projection_189	651786.72	460693	root		time:710.7ms, open:517µs, close:28.1µs, loops:452, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#976	640.0 KB	N/A
      │ └─IndexReader_192	651786.72	460693	root		time:715.9ms, open:514.9µs, close:10µs, loops:452, cop_task: {num: 11, max: 493.1ms, min: 4.43ms, avg: 69.7ms, p95: 493.1ms, max_proc_keys: 345056, p95_proc_keys: 345056, tot_proc: 421.9ms, tot_wait: 945.3µs, copr_cache: disabled, build_task_duration: 463.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 714ms, rpc_info:{Cop:{num_rpc:11, total_time:766.6ms}}	index:IndexRangeScan_191	33.6 MB	N/A
      │   └─IndexRangeScan_191	651786.72	460693	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:190ms, min:10ms, avg: 36.4ms, p80:30ms, p95:190ms, iters:493, tasks:11}, scan_detail: {total_process_keys: 460693, total_process_keys_size: 60002367, total_keys: 115647, get_snapshot_time: 781.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 421.9ms, total_suspend_time: 285µs, total_wait_time: 945.3µs, total_kv_read_wall_time: 210ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_193	1.00	0	root		time:883.4µs, open:92.4µs, close:5.52µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#976	12.2 KB	N/A
        └─IndexReader_200	1.00	0	root	partition:p20251101	time:874.2µs, open:86.3µs, close:3.46µs, loops:1, cop_task: {num: 1, max: 756µs, proc_keys: 0, tot_proc: 23.8µs, tot_wait: 43.5µs, copr_cache: disabled, build_task_duration: 36.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 771.3µs, rpc_info:{Cop:{num_rpc:1, total_time:735.8µs}}	index:Selection_199	255 Bytes	N/A
          └─Selection_199	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 23.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 23.8µs, total_wait_time: 43.5µs}	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	N/A	N/A
            └─IndexRangeScan_198	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_267	N/A	0	root			Output: ScalarQueryCol#1113	N/A	N/A
└─MaxOneRow_232	1.00	1	root		time:76.8ms, open:8.71µs, close:35µs, loops:1		N/A	N/A
  └─HashAgg_237	1.00	1	root		time:76.8ms, open:8.08µs, close:34.6µs, loops:2	funcs:count(distinct Column#1088)->Column#1089	319.6 KB	0 Bytes
    └─Union_241	231700.09	55302	root		time:68.2ms, open:999ns, close:34µs, loops:56		N/A	N/A
      ├─Projection_243	231699.09	55302	root		time:68.7ms, open:923µs, close:27.2µs, loops:56, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1088	642.6 KB	N/A
      │ └─IndexReader_246	231699.09	55302	root		time:71.6ms, open:921.6µs, close:9.11µs, loops:56, cop_task: {num: 9, max: 23.9ms, min: 1.05ms, avg: 8.1ms, p95: 23.9ms, max_proc_keys: 17376, p95_proc_keys: 17376, tot_proc: 61.4ms, tot_wait: 695.8µs, copr_cache: disabled, build_task_duration: 880.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 70.2ms, rpc_info:{Cop:{num_rpc:9, total_time:72.8ms}}	index:IndexRangeScan_245	3.18 MB	N/A
      │   └─IndexRangeScan_245	231699.09	55302	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 4.44ms, p80:10ms, p95:10ms, iters:89, tasks:9}, scan_detail: {total_process_keys: 55302, total_process_keys_size: 11514477, total_keys: 55311, get_snapshot_time: 508.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 61.4ms, total_suspend_time: 138.5µs, total_wait_time: 695.8µs, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_247	1.00	0	root		time:809µs, open:70.7µs, close:5.93µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1088	14.0 KB	N/A
        └─IndexReader_251	1.00	0	root	partition:p20251101	time:802.2µs, open:66.8µs, close:4µs, loops:1, cop_task: {num: 1, max: 710.5µs, proc_keys: 0, tot_proc: 26.6µs, tot_wait: 50.3µs, copr_cache: disabled, build_task_duration: 23.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 723.2µs, rpc_info:{Cop:{num_rpc:1, total_time:694.2µs}}	index:Selection_250	255 Bytes	N/A
          └─Selection_250	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 26.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.6µs, total_wait_time: 50.3µs}	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	N/A	N/A
            └─IndexRangeScan_249	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_323	N/A	0	root			Output: ScalarQueryCol#1209	N/A	N/A
└─MaxOneRow_280	1.00	1	root		time:5.83ms, open:10.3µs, close:19.8µs, loops:1		N/A	N/A
  └─HashAgg_285	1.00	1	root		time:5.82ms, open:9.56µs, close:19.4µs, loops:2	funcs:count(distinct Column#1182)->Column#1183	11.7 KB	0 Bytes
    └─Union_289	378709.69	479	root		time:5.75ms, open:860ns, close:18.9µs, loops:2		N/A	N/A
      ├─Projection_291	378708.69	479	root		time:5.72ms, open:853.7µs, close:15.1µs, loops:2, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1182	76.6 KB	N/A
      │ └─IndexReader_294	378708.69	479	root		time:5.62ms, open:851.8µs, close:6.44µs, loops:2, cop_task: {num: 2, max: 3.58ms, min: 1.16ms, avg: 2.37ms, p95: 3.58ms, max_proc_keys: 255, p95_proc_keys: 255, tot_proc: 1.52ms, tot_wait: 1.53ms, copr_cache: disabled, build_task_duration: 802µs, max_distsql_concurrency: 1}, fetch_resp_duration: 4.71ms, rpc_info:{Cop:{num_rpc:2, total_time:4.72ms}}	index:IndexRangeScan_293	46.8 KB	N/A
      │   └─IndexRangeScan_293	378708.69	479	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:7, tasks:2}, scan_detail: {total_process_keys: 479, total_process_keys_size: 101568, total_keys: 481, get_snapshot_time: 1.49ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.52ms, total_suspend_time: 3.91µs, total_wait_time: 1.53ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_295	1.00	0	root		time:867.2µs, open:71.3µs, close:3.16µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1182	16.2 KB	N/A
        └─IndexReader_303	1.00	0	root	partition:p20251101	time:861.9µs, open:68µs, close:2.13µs, loops:1, cop_task: {num: 1, max: 772µs, proc_keys: 0, tot_proc: 20.7µs, tot_wait: 41.7µs, copr_cache: disabled, build_task_duration: 24.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 783.2µs, rpc_info:{Cop:{num_rpc:1, total_time:759.2µs}}	index:Selection_302	255 Bytes	N/A
          └─Selection_302	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 20.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 20.7µs, total_wait_time: 41.7µs}	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	N/A	N/A
            └─IndexRangeScan_301	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.input_ip AS `raw_distinct_2`,
    d.proxy_ip AS `raw_distinct_3`,
    d.agent_type AS `raw_distinct_4`
  FROM deviceprofile_fact d
  WHERE d.true_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
  UNION ALL
  SELECT 'b_0162' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'b_0166' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'b_0170' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'b_0174' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION ALL
  SELECT 'b_0178' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
)
SELECT
  COUNT(DISTINCT CASE WHEN template_id = 'b_0162' THEN distinct_value END) AS `metric__b_0162`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0166' THEN distinct_value END) AS `metric__b_0166`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0170' THEN distinct_value END) AS `metric__b_0170`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0174' THEN distinct_value END) AS `metric__b_0174`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0178' THEN distinct_value END) AS `metric__b_0178`
FROM distinct_values;
```

#### Optimized Params

```json
[
  "74.179.68.52",
  "74.179.68.52"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=1128.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_71	1.00	1	root		time:1.09s, open:9.35µs, close:81.9µs, loops:2, RU:3992.43	funcs:count(distinct Column#188)->Column#150, funcs:count(distinct Column#189)->Column#151, funcs:count(distinct Column#190)->Column#152, funcs:count(distinct Column#191)->Column#153, funcs:count(distinct Column#192)->Column#154	57.2 MB	0 Bytes
└─Projection_122	2651307.27	1559443	root		time:435.9ms, open:1.98µs, close:81µs, loops:1530, Concurrency:5	case(eq(Column#148, ?), Column#149)->Column#188, case(eq(Column#148, ?), Column#149)->Column#189, case(eq(Column#148, ?), Column#149)->Column#190, case(eq(Column#148, ?), Column#149)->Column#191, case(eq(Column#148, ?), Column#149)->Column#192	1.02 MB	N/A
  └─Union_73	2651307.27	1559443	root		time:454.4ms, open:787ns, close:59.8µs, loops:1530		N/A	N/A
    ├─Projection_75	2651301.78	1559443	root		time:457.9ms, open:114.7µs, close:33.3µs, loops:1530, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#148, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	945.1 KB	N/A
    │ └─IndexReader_78	2651301.78	1559443	root		time:476ms, open:112.1µs, close:12.5µs, loops:1530, cop_task: {num: 51, max: 525.1ms, min: 833.4µs, avg: 46.6ms, p95: 463.8ms, max_proc_keys: 345056, p95_proc_keys: 289760, tot_proc: 1.13s, tot_wait: 1.43ms, copr_cache: disabled, build_task_duration: 39µs, max_distsql_concurrency: 6}, fetch_resp_duration: 470.5ms, rpc_info:{Cop:{num_rpc:51, total_time:2.37s}}	index:IndexRangeScan_77	67.8 MB	N/A
    │   └─IndexRangeScan_77	2651301.78	1559443	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:220ms, min:0s, avg: 22.2ms, p80:20ms, p95:170ms, iters:1720, tasks:51}, scan_detail: {total_process_keys: 1559443, total_process_keys_size: 235292075, total_keys: 417265, get_snapshot_time: 663µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.13s, total_suspend_time: 891.6µs, total_wait_time: 1.43ms, total_kv_read_wall_time: 430ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_79	1.10	0	root		time:1.08ms, open:88.5µs, close:13.1µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	70.5 KB	N/A
    │ └─Selection_81	1.10	0	root		time:1.07ms, open:84.4µs, close:10.6µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	32.6 KB	N/A
    │   └─CTEFullScan_83	1.37	0	root	CTE:raw_boundary	time:1.07ms, open:80.6µs, close:8.87µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_87	1.10	0	root		time:1.09ms, open:1.08ms, close:2.93µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	24.7 KB	N/A
    │ └─Selection_89	1.10	0	root		time:1.08ms, open:1.08ms, close:1.39µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	11.4 KB	N/A
    │   └─CTEFullScan_91	1.37	0	root	CTE:raw_boundary	time:1.08ms, open:1.08ms, close:169ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_95	1.10	0	root		time:1.09ms, open:1.09ms, close:2.74µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	14.6 KB	N/A
    │ └─Selection_97	1.10	0	root		time:1.09ms, open:1.09ms, close:1.25µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	33.1 KB	N/A
    │   └─CTEFullScan_99	1.37	0	root	CTE:raw_boundary	time:1.08ms, open:1.08ms, close:74ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_103	1.10	0	root		time:1.1ms, open:1.09ms, close:3.28µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	90.8 KB	N/A
    │ └─Selection_105	1.10	0	root		time:1.09ms, open:1.09ms, close:1.53µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	47.6 KB	N/A
    │   └─CTEFullScan_107	1.37	0	root	CTE:raw_boundary	time:1.09ms, open:1.09ms, close:163ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_111	1.10	0	root		time:13.6µs, open:7.95µs, close:2.65µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
      └─Selection_113	1.10	0	root		time:8.37µs, open:5.37µs, close:1.2µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.11 KB	N/A
        └─CTEFullScan_115	1.37	0	root	CTE:raw_boundary	time:1.55µs, open:416ns, close:158ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.37	0	root		time:1.07ms, open:80.6µs, close:8.87µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_58(Seed Part)	1.37	0	root		time:1.05ms, open:77µs, close:6.88µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type	67.5 KB	N/A
  └─IndexReader_63	1.71	0	root	partition:p20251101	time:1.04ms, open:72.3µs, close:4.83µs, loops:1, cop_task: {num: 1, max: 935.7µs, proc_keys: 0, tot_proc: 29.1µs, tot_wait: 49.6µs, copr_cache: disabled, build_task_duration: 22.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 953.4µs, rpc_info:{Cop:{num_rpc:1, total_time:916.6µs}}	index:Selection_62	255 Bytes	N/A
    └─Selection_62	1.71	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 29.1µs, total_wait_time: 49.6µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type)))))	N/A	N/A
      └─IndexRangeScan_61	1.72	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### 8. group_b_bundle_012

- Filter/window: `d.true_ip = %s` / `30d`
- Chosen event: `INV0039365135` kind=`hot_true_ip` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 501.2 ms | ok |
| `optimized_default` | `{}` | 485.6 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 490.2 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 497.3 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 2500.6 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 2425.8 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__b_0011`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `metric__b_0057`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `present__b_0057`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `metric__b_0060`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `present__b_0060`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `metric__b_0063`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `present__b_0063`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `metric__b_0066`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `present__b_0066`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `metric__b_0069`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `present__b_0069`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `metric__b_0072`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `present__b_0072`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__b_0161`,
  COUNT(DISTINCT(d.smart_id)) AS `metric__b_0165`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__b_0169`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__b_0173`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__b_0177`,
  MIN(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0275`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0275`,
  MAX(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0276`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0276`,
  AVG(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0277`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0277`,
  MIN(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0284`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0284`,
  MAX(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0285`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0285`,
  AVG(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0286`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0286`,
  MIN(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0293`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0293`,
  MAX(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0294`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0294`,
  AVG(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0295`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0295`,
  MIN(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0302`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0302`,
  MAX(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0303`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0303`,
  AVG(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0304`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0304`,
  MIN(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0311`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0311`,
  MAX(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0312`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0312`,
  AVG(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0313`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0313`
FROM deviceprofile_fact d
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-11 19:16:29.762000'
GROUP BY d.true_ip;
```

#### Original Params

```json
[
  "74.179.68.52"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=501.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	187.67	1	root		time:466.5ms, open:99.5µs, close:48.5µs, loops:2, RU:722.00, Concurrency:OFF	Column#60, Column#61, Column#61, Column#62, Column#62, Column#63, Column#63, Column#64, Column#64, Column#65, Column#65, Column#66, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, Column#73, Column#75, Column#73, Column#76, Column#77, Column#78, Column#77, Column#79, Column#77, Column#80, Column#81, Column#82, Column#81, Column#83, Column#81, Column#84, Column#85, Column#86, Column#85, Column#87, Column#85, Column#88, Column#89, Column#90, Column#89, Column#91, Column#89	151.5 KB	N/A
└─HashAgg_9	187.67	1	root		time:466.5ms, open:95.4µs, close:46.6µs, loops:2	group by:Column#223, funcs:count(?)->Column#60, funcs:sum(Column#192)->Column#61, funcs:sum(Column#193)->Column#62, funcs:sum(Column#194)->Column#63, funcs:sum(Column#195)->Column#64, funcs:sum(Column#196)->Column#65, funcs:sum(Column#197)->Column#66, funcs:count(distinct Column#198)->Column#67, funcs:count(distinct Column#199)->Column#68, funcs:count(distinct Column#200)->Column#69, funcs:count(distinct Column#201)->Column#70, funcs:count(distinct Column#202)->Column#71, funcs:min(Column#203)->Column#72, funcs:sum(Column#204)->Column#73, funcs:max(Column#205)->Column#74, funcs:avg(Column#206)->Column#75, funcs:min(Column#207)->Column#76, funcs:sum(Column#208)->Column#77, funcs:max(Column#209)->Column#78, funcs:avg(Column#210)->Column#79, funcs:min(Column#211)->Column#80, funcs:sum(Column#212)->Column#81, funcs:max(Column#213)->Column#82, funcs:avg(Column#214)->Column#83, funcs:min(Column#215)->Column#84, funcs:sum(Column#216)->Column#85, funcs:max(Column#217)->Column#86, funcs:avg(Column#218)->Column#87, funcs:min(Column#219)->Column#88, funcs:sum(Column#220)->Column#89, funcs:max(Column#221)->Column#90, funcs:avg(Column#222)->Column#91	23.3 MB	0 Bytes
  └─Projection_29	346177.19	172835	root		time:182.1ms, open:82.2µs, close:45.6µs, loops:172, Concurrency:5	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#192, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#193, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#194, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#196, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#197, intuit_risk.deviceprofile_fact.exact_id->Column#198, intuit_risk.deviceprofile_fact.smart_id->Column#199, intuit_risk.deviceprofile_fact.input_ip->Column#200, intuit_risk.deviceprofile_fact.proxy_ip->Column#201, intuit_risk.deviceprofile_fact.agent_type->Column#202, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#203, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#204, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#205, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#207, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#208, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#209, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#210, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#212, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#213, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#214, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#215, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#217, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#222, intuit_risk.deviceprofile_fact.true_ip->Column#223	6.71 MB	N/A
    └─IndexReader_21	346177.19	172835	root	partition:p20260401,p20260501,p20260601,pmax	time:209ms, open:81.1µs, close:14µs, loops:172, cop_task: {num: 18, max: 255ms, min: 1.38ms, avg: 20.8ms, p95: 255ms, max_proc_keys: 105587, p95_proc_keys: 105587, tot_proc: 188.4ms, tot_wait: 4.04ms, copr_cache: disabled, build_task_duration: 28.6µs, max_distsql_concurrency: 4}, fetch_resp_duration: 207ms, rpc_info:{Cop:{num_rpc:18, total_time:373.5ms}}	index:IndexRangeScan_20	21.0 MB	N/A
      └─IndexRangeScan_20	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:110ms, min:0s, avg: 8.89ms, p80:10ms, p95:110ms, iters:233, tasks:18}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 42640965, total_keys: 67265, get_snapshot_time: 3.72ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 188.4ms, total_suspend_time: 206.9µs, total_wait_time: 4.04ms, total_kv_read_wall_time: 50ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__b_0011`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `metric__b_0057`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `present__b_0057`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `metric__b_0060`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `present__b_0060`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `metric__b_0063`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `present__b_0063`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `metric__b_0066`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `present__b_0066`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `metric__b_0069`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `present__b_0069`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `metric__b_0072`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `present__b_0072`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__b_0161`,
  COUNT(DISTINCT(d.smart_id)) AS `metric__b_0165`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__b_0169`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__b_0173`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__b_0177`,
  MIN(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0275`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0275`,
  MAX(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0276`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0276`,
  AVG(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0277`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0277`,
  MIN(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0284`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0284`,
  MAX(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0285`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0285`,
  AVG(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0286`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0286`,
  MIN(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0293`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0293`,
  MAX(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0294`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0294`,
  AVG(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0295`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0295`,
  MIN(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0302`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0302`,
  MAX(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0303`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0303`,
  AVG(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0304`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0304`,
  MIN(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0311`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0311`,
  MAX(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0312`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0312`,
  AVG(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0313`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0313`
FROM deviceprofile_fact d
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-11 19:16:29.762000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  "74.179.68.52"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_default
-- explain_analyze_elapsed_ms=485.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:451.4ms, open:96.1µs, close:47.4µs, loops:2, RU:719.47, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	743.2 KB	N/A
└─Selection_9	0.80	1	root		time:451.3ms, open:93.2µs, close:45.7µs, loops:2	gt(Column#60, ?)	521.3 KB	N/A
  └─HashAgg_13	1.00	1	root		time:451.3ms, open:90.2µs, close:45.1µs, loops:3	funcs:count(?)->Column#60, funcs:sum(Column#208)->Column#61, funcs:sum(Column#209)->Column#62, funcs:sum(Column#210)->Column#63, funcs:sum(Column#211)->Column#64, funcs:sum(Column#212)->Column#65, funcs:sum(Column#213)->Column#66, funcs:count(distinct Column#214)->Column#67, funcs:count(distinct Column#215)->Column#68, funcs:count(distinct Column#216)->Column#69, funcs:count(distinct Column#217)->Column#70, funcs:count(distinct Column#218)->Column#71, funcs:min(Column#219)->Column#72, funcs:sum(Column#220)->Column#73, funcs:max(Column#221)->Column#74, funcs:avg(Column#222)->Column#75, funcs:min(Column#223)->Column#76, funcs:sum(Column#224)->Column#77, funcs:max(Column#225)->Column#78, funcs:avg(Column#226)->Column#79, funcs:min(Column#227)->Column#80, funcs:sum(Column#228)->Column#81, funcs:max(Column#229)->Column#82, funcs:avg(Column#230)->Column#83, funcs:min(Column#231)->Column#84, funcs:sum(Column#232)->Column#85, funcs:max(Column#233)->Column#86, funcs:avg(Column#234)->Column#87, funcs:min(Column#235)->Column#88, funcs:sum(Column#236)->Column#89, funcs:max(Column#237)->Column#90, funcs:avg(Column#238)->Column#91	23.3 MB	0 Bytes
    └─Projection_28	346177.19	172835	root		time:170ms, open:80.6µs, close:44.2µs, loops:172, Concurrency:5	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#208, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#209, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#210, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#211, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#212, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#213, intuit_risk.deviceprofile_fact.exact_id->Column#214, intuit_risk.deviceprofile_fact.smart_id->Column#215, intuit_risk.deviceprofile_fact.input_ip->Column#216, intuit_risk.deviceprofile_fact.proxy_ip->Column#217, intuit_risk.deviceprofile_fact.agent_type->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#222, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#223, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#224, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#225, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#226, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#230, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#231, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#232, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#233, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#234, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#235, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#236, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#237, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#238	6.61 MB	N/A
      └─IndexReader_21	346177.19	172835	root	partition:p20260401,p20260501,p20260601,pmax	time:193.5ms, open:79.6µs, close:12µs, loops:172, cop_task: {num: 18, max: 248.8ms, min: 569.2µs, avg: 19.7ms, p95: 248.8ms, max_proc_keys: 105587, p95_proc_keys: 105587, tot_proc: 180.8ms, tot_wait: 590.6µs, copr_cache: disabled, build_task_duration: 26.5µs, max_distsql_concurrency: 4}, fetch_resp_duration: 191.4ms, rpc_info:{Cop:{num_rpc:18, total_time:354ms}}	index:IndexRangeScan_20	21.0 MB	N/A
        └─IndexRangeScan_20	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:110ms, min:0s, avg: 8.33ms, p80:10ms, p95:110ms, iters:233, tasks:18}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 42640965, total_keys: 67265, get_snapshot_time: 292.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 180.8ms, total_suspend_time: 187.4µs, total_wait_time: 590.6µs, total_kv_read_wall_time: 40ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 9. group_a_bundle_008

- Filter/window: `p.merchant_account_number = %s` / `7d`
- Chosen event: `INV0030289106` kind=`hot_merchant_account_number` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 108.3 ms | ok |
| `optimized_default` | `{}` | 70.1 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 67.8 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 72.0 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 94.3 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 99.2 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0005`,
  SUM(p.amount) AS `metric__a_0006`,
  MIN(p.amount) AS `metric__a_0007`,
  MAX(p.amount) AS `metric__a_0008`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__a_0069`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0069`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_0070`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0070`,
  MIN(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_0071`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0071`,
  MAX(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_0072`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0072`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `metric__a_0085`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0085`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_0086`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0086`,
  MIN(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_0087`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0087`,
  MAX(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_0088`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0088`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__a_0101`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0101`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_0102`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0102`,
  MIN(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_0103`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0103`,
  MAX(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_0104`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0104`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `metric__a_0117`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0117`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_0118`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0118`,
  MIN(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_0119`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0119`,
  MAX(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_0120`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0120`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `metric__a_0133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_0134`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0134`,
  MIN(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_0135`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0135`,
  MAX(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_0136`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0136`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `metric__a_0149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_0150`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0150`,
  MIN(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_0151`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0151`,
  MAX(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_0152`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0152`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `metric__a_0165`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0165`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_0166`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0166`,
  MIN(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_0167`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0167`,
  MAX(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_0168`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0168`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `metric__a_0181`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0181`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_0182`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0182`,
  MIN(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_0183`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0183`,
  MAX(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_0184`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0184`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `metric__a_0197`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0197`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_0198`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0198`,
  MIN(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_0199`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0199`,
  MAX(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_0200`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0200`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `metric__a_0213`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0213`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_0214`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0214`,
  MIN(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_0215`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0215`,
  MAX(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_0216`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0216`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `metric__a_0229`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0229`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_0230`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0230`,
  MIN(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_0231`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0231`,
  MAX(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_0232`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0232`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `metric__a_0245`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0245`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_0246`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0246`,
  MIN(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_0247`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0247`,
  MAX(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_0248`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0248`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `metric__a_0261`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0261`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_0262`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0262`,
  MIN(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_0263`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0263`,
  MAX(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_0264`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0264`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `metric__a_0277`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0277`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_0278`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0278`,
  MIN(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_0279`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0279`,
  MAX(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_0280`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0280`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `metric__a_0293`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0293`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_0294`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0294`,
  MIN(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_0295`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0295`,
  MAX(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_0296`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0296`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `metric__a_0309`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0309`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_0310`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0310`,
  MIN(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_0311`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0311`,
  MAX(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_0312`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0312`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__a_0325`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0325`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_0326`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0326`,
  MIN(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_0327`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0327`,
  MAX(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_0328`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0328`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `metric__a_0341`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0341`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_0342`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0342`,
  MIN(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_0343`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0343`,
  MAX(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_0344`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0344`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `metric__a_0357`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0357`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_0358`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0358`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_0359`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0359`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_0360`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0360`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `metric__a_0373`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0373`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_0374`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0374`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_0375`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0375`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_0376`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0376`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `metric__a_0389`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0389`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_0390`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0390`,
  MIN(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_0391`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0391`,
  MAX(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_0392`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0392`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `metric__a_0401`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0401`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_0402`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0402`,
  MIN(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_0403`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0403`,
  MAX(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_0404`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0404`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `metric__a_0413`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0413`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_0414`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0414`,
  MIN(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_0415`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0415`,
  MAX(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_0416`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0416`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `metric__a_0425`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0425`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_0426`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0426`,
  MIN(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_0427`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0427`,
  MAX(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_0428`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0428`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `metric__a_0437`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0437`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_0438`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0438`,
  MIN(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_0439`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0439`,
  MAX(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_0440`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0440`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `metric__a_0449`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0449`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_0450`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0450`,
  MIN(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_0451`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0451`,
  MAX(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_0452`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0452`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `metric__a_0461`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0461`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_0462`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0462`,
  MIN(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_0463`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0463`,
  MAX(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_0464`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0464`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `metric__a_0473`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0473`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_0474`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0474`,
  MIN(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_0475`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0475`,
  MAX(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_0476`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0476`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `metric__a_0485`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0485`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_0486`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0486`,
  MIN(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_0487`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0487`,
  MAX(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_0488`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0488`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `metric__a_0497`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0497`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_0498`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0498`,
  MIN(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_0499`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0499`,
  MAX(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_0500`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0500`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `metric__a_0509`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0509`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_0510`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0510`,
  MIN(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_0511`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0511`,
  MAX(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_0512`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0512`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `metric__a_0521`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0521`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_0522`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0522`,
  MIN(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_0523`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0523`,
  MAX(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_0524`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0524`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `metric__a_0533`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0533`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_0534`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0534`,
  MIN(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_0535`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0535`,
  MAX(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_0536`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0536`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1731`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1731`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1732`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1732`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1743`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1743`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1744`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1744`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN 1 ELSE 0 END) AS `metric__a_1755`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN 1 ELSE 0 END) AS `present__a_1755`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN p.amount END) AS `metric__a_1756`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN 1 ELSE 0 END) AS `present__a_1756`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN 1 ELSE 0 END) AS `metric__a_1767`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN 1 ELSE 0 END) AS `present__a_1767`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN p.amount END) AS `metric__a_1768`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN 1 ELSE 0 END) AS `present__a_1768`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN 1 ELSE 0 END) AS `metric__a_1779`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN 1 ELSE 0 END) AS `present__a_1779`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN p.amount END) AS `metric__a_1780`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN 1 ELSE 0 END) AS `present__a_1780`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1791`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1791`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1792`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1792`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1803`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1803`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1804`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1804`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1815`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1815`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1816`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1816`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1827`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1827`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1828`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1828`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1839`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1839`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1840`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1840`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1851`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1851`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1852`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1852`,
  COUNT(DISTINCT(p.card_type)) AS `metric__a_1864`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__a_1865`,
  COUNT(DISTINCT(p.mt_gateway)) AS `metric__a_1866`
FROM pmt_txn_fact p
WHERE p.merchant_account_number = %s AND p.event_date >= 1775168526667
GROUP BY p.merchant_account_number;
```

#### Original Params

```json
[
  5247719989330882
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=108.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	70.37	1	root		time:29.4ms, open:757.7µs, close:46.1µs, loops:2, RU:17.25, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#185, Column#186, Column#185, Column#187, Column#187, Column#188, Column#187, Column#189, Column#189, Column#190, Column#189, Column#191, Column#191, Column#192, Column#191, Column#193, Column#193, Column#194, Column#193, Column#195, Column#195, Column#196, Column#195, Column#197, Column#197, Column#198, Column#197, Column#199, Column#199, Column#200, Column#199, Column#201, Column#201, Column#202, Column#201, Column#203, Column#203, Column#204, Column#203, Column#205, Column#206, Column#207	257.3 KB	N/A
└─HashAgg_9	70.37	1	root		time:29.1ms, open:688.4µs, close:44.4µs, loops:2	group by:Column#1000, funcs:count(?)->Column#47, funcs:sum(Column#840)->Column#48, funcs:min(Column#841)->Column#49, funcs:max(Column#842)->Column#50, funcs:sum(Column#843)->Column#51, funcs:sum(Column#844)->Column#52, funcs:min(Column#845)->Column#53, funcs:max(Column#846)->Column#54, funcs:sum(Column#847)->Column#55, funcs:sum(Column#848)->Column#56, funcs:min(Column#849)->Column#57, funcs:max(Column#850)->Column#58, funcs:sum(Column#851)->Column#59, funcs:sum(Column#852)->Column#60, funcs:min(Column#853)->Column#61, funcs:max(Column#854)->Column#62, funcs:sum(Column#855)->Column#63, funcs:sum(Column#856)->Column#64, funcs:min(Column#857)->Column#65, funcs:max(Column#858)->Column#66, funcs:sum(Column#859)->Column#67, funcs:sum(Column#860)->Column#68, funcs:min(Column#861)->Column#69, funcs:max(Column#862)->Column#70, funcs:sum(Column#863)->Column#71, funcs:sum(Column#864)->Column#72, funcs:min(Column#865)->Column#73, funcs:max(Column#866)->Column#74, funcs:sum(Column#867)->Column#75, funcs:sum(Column#868)->Column#76, funcs:min(Column#869)->Column#77, funcs:max(Column#870)->Column#78, funcs:sum(Column#871)->Column#79, funcs:sum(Column#872)->Column#80, funcs:min(Column#873)->Column#81, funcs:max(Column#874)->Column#82, funcs:sum(Column#875)->Column#83, funcs:sum(Column#876)->Column#84, funcs:min(Column#877)->Column#85, funcs:max(Column#878)->Column#86, funcs:sum(Column#879)->Column#87, funcs:sum(Column#880)->Column#88, funcs:min(Column#881)->Column#89, funcs:max(Column#882)->Column#90, funcs:sum(Column#883)->Column#91, funcs:sum(Column#884)->Column#92, funcs:min(Column#885)->Column#93, funcs:max(Column#886)->Column#94, funcs:sum(Column#887)->Column#95, funcs:sum(Column#888)->Column#96, funcs:min(Column#889)->Column#97, funcs:max(Column#890)->Column#98, funcs:sum(Column#891)->Column#99, funcs:sum(Column#892)->Column#100, funcs:min(Column#893)->Column#101, funcs:max(Column#894)->Column#102, funcs:sum(Column#895)->Column#103, funcs:sum(Column#896)->Column#104, funcs:min(Column#897)->Column#105, funcs:max(Column#898)->Column#106, funcs:sum(Column#899)->Column#107, funcs:sum(Column#900)->Column#108, funcs:min(Column#901)->Column#109, funcs:max(Column#902)->Column#110, funcs:sum(Column#903)->Column#111, funcs:sum(Column#904)->Column#112, funcs:min(Column#905)->Column#113, funcs:max(Column#906)->Column#114, funcs:sum(Column#907)->Column#115, funcs:sum(Column#908)->Column#116, funcs:min(Column#909)->Column#117, funcs:max(Column#910)->Column#118, funcs:sum(Column#911)->Column#119, funcs:sum(Column#912)->Column#120, funcs:min(Column#913)->Column#121, funcs:max(Column#914)->Column#122, funcs:sum(Column#915)->Column#123, funcs:sum(Column#916)->Column#124, funcs:min(Column#917)->Column#125, funcs:max(Column#918)->Column#126, funcs:sum(Column#919)->Column#127, funcs:sum(Column#920)->Column#128, funcs:min(Column#921)->Column#129, funcs:max(Column#922)->Column#130, funcs:sum(Column#923)->Column#131, funcs:sum(Column#924)->Column#132, funcs:min(Column#925)->Column#133, funcs:max(Column#926)->Column#134, funcs:sum(Column#927)->Column#135, funcs:sum(Column#928)->Column#136, funcs:min(Column#929)->Column#137, funcs:max(Column#930)->Column#138, funcs:sum(Column#931)->Column#139, funcs:sum(Column#932)->Column#140, funcs:min(Column#933)->Column#141, funcs:max(Column#934)->Column#142, funcs:sum(Column#935)->Column#143, funcs:sum(Column#936)->Column#144, funcs:min(Column#937)->Column#145, funcs:max(Column#938)->Column#146, funcs:sum(Column#939)->Column#147, funcs:sum(Column#940)->Column#148, funcs:min(Column#941)->Column#149, funcs:max(Column#942)->Column#150, funcs:sum(Column#943)->Column#151, funcs:sum(Column#944)->Column#152, funcs:min(Column#945)->Column#153, funcs:max(Column#946)->Column#154, funcs:sum(Column#947)->Column#155, funcs:sum(Column#948)->Column#156, funcs:min(Column#949)->Column#157, funcs:max(Column#950)->Column#158, funcs:sum(Column#951)->Column#159, funcs:sum(Column#952)->Column#160, funcs:min(Column#953)->Column#161, funcs:max(Column#954)->Column#162, funcs:sum(Column#955)->Column#163, funcs:sum(Column#956)->Column#164, funcs:min(Column#957)->Column#165, funcs:max(Column#958)->Column#166, funcs:sum(Column#959)->Column#167, funcs:sum(Column#960)->Column#168, funcs:min(Column#961)->Column#169, funcs:max(Column#962)->Column#170, funcs:sum(Column#963)->Column#171, funcs:sum(Column#964)->Column#172, funcs:min(Column#965)->Column#173, funcs:max(Column#966)->Column#174, funcs:sum(Column#967)->Column#175, funcs:sum(Column#968)->Column#176, funcs:min(Column#969)->Column#177, funcs:max(Column#970)->Column#178, funcs:sum(Column#971)->Column#179, funcs:sum(Column#972)->Column#180, funcs:min(Column#973)->Column#181, funcs:max(Column#974)->Column#182, funcs:sum(Column#975)->Column#183, funcs:sum(Column#976)->Column#184, funcs:sum(Column#977)->Column#185, funcs:sum(Column#978)->Column#186, funcs:sum(Column#979)->Column#187, funcs:sum(Column#980)->Column#188, funcs:sum(Column#981)->Column#189, funcs:sum(Column#982)->Column#190, funcs:sum(Column#983)->Column#191, funcs:sum(Column#984)->Column#192, funcs:sum(Column#985)->Column#193, funcs:sum(Column#986)->Column#194, funcs:sum(Column#987)->Column#195, funcs:sum(Column#988)->Column#196, funcs:sum(Column#989)->Column#197, funcs:sum(Column#990)->Column#198, funcs:sum(Column#991)->Column#199, funcs:sum(Column#992)->Column#200, funcs:sum(Column#993)->Column#201, funcs:sum(Column#994)->Column#202, funcs:sum(Column#995)->Column#203, funcs:sum(Column#996)->Column#204, funcs:count(distinct Column#997)->Column#205, funcs:count(distinct Column#998)->Column#206, funcs:count(distinct Column#999)->Column#207	6.24 MB	0 Bytes
  └─Projection_32	18368.93	4152	root		time:17.2ms, open:564.9µs, close:43.6µs, loops:6, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#840, intuit_risk.pmt_txn_fact.amount->Column#841, intuit_risk.pmt_txn_fact.amount->Column#842, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#843, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#844, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#845, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#846, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#847, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#848, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#849, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#850, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#851, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#852, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#853, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#854, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#855, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#856, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#857, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#858, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#859, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#860, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#861, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#862, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#863, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#864, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#865, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#866, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#867, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#868, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#869, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#870, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#871, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#872, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#873, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#874, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#875, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#876, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#877, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#878, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#879, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#880, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#881, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#882, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#883, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#884, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#885, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#886, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#887, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#888, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#889, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#890, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#891, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#892, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#893, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#894, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#895, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#896, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#897, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#898, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#899, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#900, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#901, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#902, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#903, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#904, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#905, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#906, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#907, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#908, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#909, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#910, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#911, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#912, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#913, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#914, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#915, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#916, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#917, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#918, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#919, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#920, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#921, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#922, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#923, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#924, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#925, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#926, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#927, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#928, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#929, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#930, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#931, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#932, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#933, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#934, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#935, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#936, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#937, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#938, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#939, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#940, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#941, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#942, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#943, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#944, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#945, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#946, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#947, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#948, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#949, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#950, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#951, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#952, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#953, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#954, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#955, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#956, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#957, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#958, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#959, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#960, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#961, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#962, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#963, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#964, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#965, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#966, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#967, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#968, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#969, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#970, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#971, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#972, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#973, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#974, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#975, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#976, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#977, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#978, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#979, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#980, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#981, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#982, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#983, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#984, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#985, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#986, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#987, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#988, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#989, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#990, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#991, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#992, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#993, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#994, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#995, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#996, intuit_risk.pmt_txn_fact.card_type->Column#997, intuit_risk.pmt_txn_fact.entry_method->Column#998, intuit_risk.pmt_txn_fact.mt_gateway->Column#999, intuit_risk.pmt_txn_fact.merchant_account_number->Column#1000	25.4 MB	N/A
    └─IndexReader_23	18368.93	4152	root	partition:p20260501,p20260601,pmax	time:15.7ms, open:562.5µs, close:12.5µs, loops:6, cop_task: {num: 7, max: 4.41ms, min: 1.26ms, avg: 2.99ms, p95: 4.41ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 9.44ms, tot_wait: 3.59ms, copr_cache: disabled, build_task_duration: 522.1µs, max_distsql_concurrency: 3}, fetch_resp_duration: 14.8ms, rpc_info:{Cop:{num_rpc:7, total_time:20.9ms}}	index:IndexRangeScan_22	316.7 KB	N/A
      └─IndexRangeScan_22	18368.93	4152	cop[tikv]	table:p, index:idx_pmt_merchant_runtime_cov(merchant_account_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:24, tasks:7}, scan_detail: {total_process_keys: 4152, total_process_keys_size: 705989, total_keys: 4159, get_snapshot_time: 3.44ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 9.44ms, total_suspend_time: 10.1µs, total_wait_time: 3.59ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0005`,
  SUM(p.amount) AS `metric__a_0006`,
  MIN(p.amount) AS `metric__a_0007`,
  MAX(p.amount) AS `metric__a_0008`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__a_0069`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0069`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_0070`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0070`,
  MIN(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_0071`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0071`,
  MAX(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__a_0072`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__a_0072`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `metric__a_0085`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0085`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_0086`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0086`,
  MIN(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_0087`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0087`,
  MAX(CASE WHEN p.transaction_type = 'Void' THEN p.amount END) AS `metric__a_0088`,
  SUM(CASE WHEN p.transaction_type = 'Void' THEN 1 ELSE 0 END) AS `present__a_0088`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__a_0101`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0101`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_0102`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0102`,
  MIN(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_0103`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0103`,
  MAX(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__a_0104`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__a_0104`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `metric__a_0117`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0117`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_0118`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0118`,
  MIN(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_0119`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0119`,
  MAX(CASE WHEN p.transaction_type = 'Auth' THEN p.amount END) AS `metric__a_0120`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__a_0120`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `metric__a_0133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0133`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_0134`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0134`,
  MIN(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_0135`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0135`,
  MAX(CASE WHEN p.transaction_type = 'Capture' THEN p.amount END) AS `metric__a_0136`,
  SUM(CASE WHEN p.transaction_type = 'Capture' THEN 1 ELSE 0 END) AS `present__a_0136`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `metric__a_0149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0149`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_0150`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0150`,
  MIN(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_0151`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0151`,
  MAX(CASE WHEN p.transaction_type = 'Reversal' THEN p.amount END) AS `metric__a_0152`,
  SUM(CASE WHEN p.transaction_type = 'Reversal' THEN 1 ELSE 0 END) AS `present__a_0152`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `metric__a_0165`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0165`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_0166`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0166`,
  MIN(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_0167`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0167`,
  MAX(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN p.amount END) AS `metric__a_0168`,
  SUM(CASE WHEN p.transaction_type = 'CAPTURE_ORDER' THEN 1 ELSE 0 END) AS `present__a_0168`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `metric__a_0181`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0181`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_0182`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0182`,
  MIN(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_0183`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0183`,
  MAX(CASE WHEN p.transaction_type = 'EMV_Advice' THEN p.amount END) AS `metric__a_0184`,
  SUM(CASE WHEN p.transaction_type = 'EMV_Advice' THEN 1 ELSE 0 END) AS `present__a_0184`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `metric__a_0197`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0197`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_0198`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0198`,
  MIN(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_0199`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0199`,
  MAX(CASE WHEN p.transaction_type = 'Adjustment' THEN p.amount END) AS `metric__a_0200`,
  SUM(CASE WHEN p.transaction_type = 'Adjustment' THEN 1 ELSE 0 END) AS `present__a_0200`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `metric__a_0213`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0213`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_0214`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0214`,
  MIN(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_0215`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0215`,
  MAX(CASE WHEN p.transaction_type = 'Credit' THEN p.amount END) AS `metric__a_0216`,
  SUM(CASE WHEN p.transaction_type = 'Credit' THEN 1 ELSE 0 END) AS `present__a_0216`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `metric__a_0229`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0229`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_0230`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0230`,
  MIN(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_0231`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0231`,
  MAX(CASE WHEN p.transaction_type = 'Debit' THEN p.amount END) AS `metric__a_0232`,
  SUM(CASE WHEN p.transaction_type = 'Debit' THEN 1 ELSE 0 END) AS `present__a_0232`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `metric__a_0245`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0245`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_0246`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0246`,
  MIN(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_0247`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0247`,
  MAX(CASE WHEN p.transaction_type = 'AuthOnly' THEN p.amount END) AS `metric__a_0248`,
  SUM(CASE WHEN p.transaction_type = 'AuthOnly' THEN 1 ELSE 0 END) AS `present__a_0248`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `metric__a_0261`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0261`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_0262`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0262`,
  MIN(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_0263`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0263`,
  MAX(CASE WHEN p.transaction_type = 'CaptureOnly' THEN p.amount END) AS `metric__a_0264`,
  SUM(CASE WHEN p.transaction_type = 'CaptureOnly' THEN 1 ELSE 0 END) AS `present__a_0264`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `metric__a_0277`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0277`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_0278`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0278`,
  MIN(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_0279`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0279`,
  MAX(CASE WHEN p.transaction_type = 'PostAuth' THEN p.amount END) AS `metric__a_0280`,
  SUM(CASE WHEN p.transaction_type = 'PostAuth' THEN 1 ELSE 0 END) AS `present__a_0280`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `metric__a_0293`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0293`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_0294`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0294`,
  MIN(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_0295`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0295`,
  MAX(CASE WHEN p.transaction_type = 'PreAuth' THEN p.amount END) AS `metric__a_0296`,
  SUM(CASE WHEN p.transaction_type = 'PreAuth' THEN 1 ELSE 0 END) AS `present__a_0296`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `metric__a_0309`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0309`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_0310`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0310`,
  MIN(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_0311`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0311`,
  MAX(CASE WHEN p.transaction_type = 'Return' THEN p.amount END) AS `metric__a_0312`,
  SUM(CASE WHEN p.transaction_type = 'Return' THEN 1 ELSE 0 END) AS `present__a_0312`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__a_0325`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0325`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_0326`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0326`,
  MIN(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_0327`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0327`,
  MAX(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__a_0328`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__a_0328`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `metric__a_0341`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0341`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_0342`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0342`,
  MIN(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_0343`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0343`,
  MAX(CASE WHEN p.transaction_type = 'Dispute' THEN p.amount END) AS `metric__a_0344`,
  SUM(CASE WHEN p.transaction_type = 'Dispute' THEN 1 ELSE 0 END) AS `present__a_0344`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `metric__a_0357`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0357`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_0358`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0358`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_0359`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0359`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN p.amount END) AS `metric__a_0360`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_NSF' THEN 1 ELSE 0 END) AS `present__a_0360`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `metric__a_0373`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0373`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_0374`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0374`,
  MIN(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_0375`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0375`,
  MAX(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN p.amount END) AS `metric__a_0376`,
  SUM(CASE WHEN p.transaction_type = 'Reversal_Timeout' THEN 1 ELSE 0 END) AS `present__a_0376`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `metric__a_0389`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0389`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_0390`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0390`,
  MIN(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_0391`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0391`,
  MAX(CASE WHEN p.card_type = 'VISA' THEN p.amount END) AS `metric__a_0392`,
  SUM(CASE WHEN p.card_type = 'VISA' THEN 1 ELSE 0 END) AS `present__a_0392`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `metric__a_0401`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0401`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_0402`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0402`,
  MIN(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_0403`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0403`,
  MAX(CASE WHEN p.card_type = 'MASTERCARD' THEN p.amount END) AS `metric__a_0404`,
  SUM(CASE WHEN p.card_type = 'MASTERCARD' THEN 1 ELSE 0 END) AS `present__a_0404`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `metric__a_0413`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0413`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_0414`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0414`,
  MIN(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_0415`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0415`,
  MAX(CASE WHEN p.card_type = 'CHECK' THEN p.amount END) AS `metric__a_0416`,
  SUM(CASE WHEN p.card_type = 'CHECK' THEN 1 ELSE 0 END) AS `present__a_0416`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `metric__a_0425`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0425`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_0426`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0426`,
  MIN(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_0427`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0427`,
  MAX(CASE WHEN p.card_type = 'AMEX' THEN p.amount END) AS `metric__a_0428`,
  SUM(CASE WHEN p.card_type = 'AMEX' THEN 1 ELSE 0 END) AS `present__a_0428`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `metric__a_0437`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0437`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_0438`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0438`,
  MIN(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_0439`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0439`,
  MAX(CASE WHEN p.card_type = 'DISCOVER' THEN p.amount END) AS `metric__a_0440`,
  SUM(CASE WHEN p.card_type = 'DISCOVER' THEN 1 ELSE 0 END) AS `present__a_0440`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `metric__a_0449`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0449`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_0450`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0450`,
  MIN(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_0451`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0451`,
  MAX(CASE WHEN p.card_type = 'DINERS' THEN p.amount END) AS `metric__a_0452`,
  SUM(CASE WHEN p.card_type = 'DINERS' THEN 1 ELSE 0 END) AS `present__a_0452`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `metric__a_0461`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0461`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_0462`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0462`,
  MIN(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_0463`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0463`,
  MAX(CASE WHEN p.card_type = 'JCB' THEN p.amount END) AS `metric__a_0464`,
  SUM(CASE WHEN p.card_type = 'JCB' THEN 1 ELSE 0 END) AS `present__a_0464`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `metric__a_0473`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0473`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_0474`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0474`,
  MIN(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_0475`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0475`,
  MAX(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN p.amount END) AS `metric__a_0476`,
  SUM(CASE WHEN p.card_type = 'CARTE_BLANCHE' THEN 1 ELSE 0 END) AS `present__a_0476`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `metric__a_0485`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0485`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_0486`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0486`,
  MIN(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_0487`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0487`,
  MAX(CASE WHEN p.card_type = 'UNKNOWN' THEN p.amount END) AS `metric__a_0488`,
  SUM(CASE WHEN p.card_type = 'UNKNOWN' THEN 1 ELSE 0 END) AS `present__a_0488`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `metric__a_0497`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0497`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_0498`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0498`,
  MIN(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_0499`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0499`,
  MAX(CASE WHEN p.card_type = 'DEBIT' THEN p.amount END) AS `metric__a_0500`,
  SUM(CASE WHEN p.card_type = 'DEBIT' THEN 1 ELSE 0 END) AS `present__a_0500`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `metric__a_0509`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0509`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_0510`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0510`,
  MIN(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_0511`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0511`,
  MAX(CASE WHEN p.card_type = 'CREDIT' THEN p.amount END) AS `metric__a_0512`,
  SUM(CASE WHEN p.card_type = 'CREDIT' THEN 1 ELSE 0 END) AS `present__a_0512`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `metric__a_0521`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0521`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_0522`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0522`,
  MIN(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_0523`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0523`,
  MAX(CASE WHEN p.card_type = 'PREPAID' THEN p.amount END) AS `metric__a_0524`,
  SUM(CASE WHEN p.card_type = 'PREPAID' THEN 1 ELSE 0 END) AS `present__a_0524`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `metric__a_0533`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0533`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_0534`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0534`,
  MIN(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_0535`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0535`,
  MAX(CASE WHEN p.card_type = 'GIFT' THEN p.amount END) AS `metric__a_0536`,
  SUM(CASE WHEN p.card_type = 'GIFT' THEN 1 ELSE 0 END) AS `present__a_0536`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1731`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1731`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1732`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1732`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1743`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1743`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1744`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1744`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN 1 ELSE 0 END) AS `metric__a_1755`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN 1 ELSE 0 END) AS `present__a_1755`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN p.amount END) AS `metric__a_1756`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CHIP' THEN 1 ELSE 0 END) AS `present__a_1756`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN 1 ELSE 0 END) AS `metric__a_1767`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN 1 ELSE 0 END) AS `present__a_1767`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN p.amount END) AS `metric__a_1768`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'CONTACTLESS' THEN 1 ELSE 0 END) AS `present__a_1768`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN 1 ELSE 0 END) AS `metric__a_1779`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN 1 ELSE 0 END) AS `present__a_1779`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN p.amount END) AS `metric__a_1780`,
  SUM(CASE WHEN p.transaction_type = 'Sale' AND p.entry_method = 'SWIPED' THEN 1 ELSE 0 END) AS `present__a_1780`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1791`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1791`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1792`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1792`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1803`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1803`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1804`,
  SUM(CASE WHEN p.transaction_type = 'Refund' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1804`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1815`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1815`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1816`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1816`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1827`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1827`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1828`,
  SUM(CASE WHEN p.transaction_type = 'Auth' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1828`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `metric__a_1839`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1839`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN p.amount END) AS `metric__a_1840`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'KEYED' THEN 1 ELSE 0 END) AS `present__a_1840`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `metric__a_1851`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1851`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN p.amount END) AS `metric__a_1852`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' AND p.entry_method = 'ECOM' THEN 1 ELSE 0 END) AS `present__a_1852`,
  COUNT(DISTINCT(p.card_type)) AS `metric__a_1864`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__a_1865`,
  COUNT(DISTINCT(p.mt_gateway)) AS `metric__a_1866`
FROM pmt_txn_fact p
WHERE p.merchant_account_number = %s AND p.event_date >= 1775168526667
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  5247719989330882
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_hashagg_16_8
-- explain_analyze_elapsed_ms=67.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:24.4ms, open:329.2µs, close:42.9µs, loops:2, RU:15.19, Concurrency:OFF	Column#47->Column#208, Column#48->Column#209, Column#49->Column#210, Column#50->Column#211, Column#51->Column#212, Column#51->Column#213, Column#52->Column#214, Column#51->Column#215, Column#53->Column#216, Column#51->Column#217, Column#54->Column#218, Column#51->Column#219, Column#55->Column#220, Column#55->Column#221, Column#56->Column#222, Column#55->Column#223, Column#57->Column#224, Column#55->Column#225, Column#58->Column#226, Column#55->Column#227, Column#59->Column#228, Column#59->Column#229, Column#60->Column#230, Column#59->Column#231, Column#61->Column#232, Column#59->Column#233, Column#62->Column#234, Column#59->Column#235, Column#63->Column#236, Column#63->Column#237, Column#64->Column#238, Column#63->Column#239, Column#65->Column#240, Column#63->Column#241, Column#66->Column#242, Column#63->Column#243, Column#67->Column#244, Column#67->Column#245, Column#68->Column#246, Column#67->Column#247, Column#69->Column#248, Column#67->Column#249, Column#70->Column#250, Column#67->Column#251, Column#71->Column#252, Column#71->Column#253, Column#72->Column#254, Column#71->Column#255, Column#73->Column#256, Column#71->Column#257, Column#74->Column#258, Column#71->Column#259, Column#75->Column#260, Column#75->Column#261, Column#76->Column#262, Column#75->Column#263, Column#77->Column#264, Column#75->Column#265, Column#78->Column#266, Column#75->Column#267, Column#79->Column#268, Column#79->Column#269, Column#80->Column#270, Column#79->Column#271, Column#81->Column#272, Column#79->Column#273, Column#82->Column#274, Column#79->Column#275, Column#83->Column#276, Column#83->Column#277, Column#84->Column#278, Column#83->Column#279, Column#85->Column#280, Column#83->Column#281, Column#86->Column#282, Column#83->Column#283, Column#87->Column#284, Column#87->Column#285, Column#88->Column#286, Column#87->Column#287, Column#89->Column#288, Column#87->Column#289, Column#90->Column#290, Column#87->Column#291, Column#91->Column#292, Column#91->Column#293, Column#92->Column#294, Column#91->Column#295, Column#93->Column#296, Column#91->Column#297, Column#94->Column#298, Column#91->Column#299, Column#95->Column#300, Column#95->Column#301, Column#96->Column#302, Column#95->Column#303, Column#97->Column#304, Column#95->Column#305, Column#98->Column#306, Column#95->Column#307, Column#99->Column#308, Column#99->Column#309, Column#100->Column#310, Column#99->Column#311, Column#101->Column#312, Column#99->Column#313, Column#102->Column#314, Column#99->Column#315, Column#103->Column#316, Column#103->Column#317, Column#104->Column#318, Column#103->Column#319, Column#105->Column#320, Column#103->Column#321, Column#106->Column#322, Column#103->Column#323, Column#107->Column#324, Column#107->Column#325, Column#108->Column#326, Column#107->Column#327, Column#109->Column#328, Column#107->Column#329, Column#110->Column#330, Column#107->Column#331, Column#111->Column#332, Column#111->Column#333, Column#112->Column#334, Column#111->Column#335, Column#113->Column#336, Column#111->Column#337, Column#114->Column#338, Column#111->Column#339, Column#115->Column#340, Column#115->Column#341, Column#116->Column#342, Column#115->Column#343, Column#117->Column#344, Column#115->Column#345, Column#118->Column#346, Column#115->Column#347, Column#119->Column#348, Column#119->Column#349, Column#120->Column#350, Column#119->Column#351, Column#121->Column#352, Column#119->Column#353, Column#122->Column#354, Column#119->Column#355, Column#123->Column#356, Column#123->Column#357, Column#124->Column#358, Column#123->Column#359, Column#125->Column#360, Column#123->Column#361, Column#126->Column#362, Column#123->Column#363, Column#127->Column#364, Column#127->Column#365, Column#128->Column#366, Column#127->Column#367, Column#129->Column#368, Column#127->Column#369, Column#130->Column#370, Column#127->Column#371, Column#131->Column#372, Column#131->Column#373, Column#132->Column#374, Column#131->Column#375, Column#133->Column#376, Column#131->Column#377, Column#134->Column#378, Column#131->Column#379, Column#135->Column#380, Column#135->Column#381, Column#136->Column#382, Column#135->Column#383, Column#137->Column#384, Column#135->Column#385, Column#138->Column#386, Column#135->Column#387, Column#139->Column#388, Column#139->Column#389, Column#140->Column#390, Column#139->Column#391, Column#141->Column#392, Column#139->Column#393, Column#142->Column#394, Column#139->Column#395, Column#143->Column#396, Column#143->Column#397, Column#144->Column#398, Column#143->Column#399, Column#145->Column#400, Column#143->Column#401, Column#146->Column#402, Column#143->Column#403, Column#147->Column#404, Column#147->Column#405, Column#148->Column#406, Column#147->Column#407, Column#149->Column#408, Column#147->Column#409, Column#150->Column#410, Column#147->Column#411, Column#151->Column#412, Column#151->Column#413, Column#152->Column#414, Column#151->Column#415, Column#153->Column#416, Column#151->Column#417, Column#154->Column#418, Column#151->Column#419, Column#155->Column#420, Column#155->Column#421, Column#156->Column#422, Column#155->Column#423, Column#157->Column#424, Column#155->Column#425, Column#158->Column#426, Column#155->Column#427, Column#159->Column#428, Column#159->Column#429, Column#160->Column#430, Column#159->Column#431, Column#161->Column#432, Column#159->Column#433, Column#162->Column#434, Column#159->Column#435, Column#163->Column#436, Column#163->Column#437, Column#164->Column#438, Column#163->Column#439, Column#165->Column#440, Column#163->Column#441, Column#166->Column#442, Column#163->Column#443, Column#167->Column#444, Column#167->Column#445, Column#168->Column#446, Column#167->Column#447, Column#169->Column#448, Column#167->Column#449, Column#170->Column#450, Column#167->Column#451, Column#171->Column#452, Column#171->Column#453, Column#172->Column#454, Column#171->Column#455, Column#173->Column#456, Column#171->Column#457, Column#174->Column#458, Column#171->Column#459, Column#175->Column#460, Column#175->Column#461, Column#176->Column#462, Column#175->Column#463, Column#177->Column#464, Column#175->Column#465, Column#178->Column#466, Column#175->Column#467, Column#179->Column#468, Column#179->Column#469, Column#180->Column#470, Column#179->Column#471, Column#181->Column#472, Column#179->Column#473, Column#182->Column#474, Column#179->Column#475, Column#183->Column#476, Column#183->Column#477, Column#184->Column#478, Column#183->Column#479, Column#185->Column#480, Column#185->Column#481, Column#186->Column#482, Column#185->Column#483, Column#187->Column#484, Column#187->Column#485, Column#188->Column#486, Column#187->Column#487, Column#189->Column#488, Column#189->Column#489, Column#190->Column#490, Column#189->Column#491, Column#191->Column#492, Column#191->Column#493, Column#192->Column#494, Column#191->Column#495, Column#193->Column#496, Column#193->Column#497, Column#194->Column#498, Column#193->Column#499, Column#195->Column#500, Column#195->Column#501, Column#196->Column#502, Column#195->Column#503, Column#197->Column#504, Column#197->Column#505, Column#198->Column#506, Column#197->Column#507, Column#199->Column#508, Column#199->Column#509, Column#200->Column#510, Column#199->Column#511, Column#201->Column#512, Column#201->Column#513, Column#202->Column#514, Column#201->Column#515, Column#203->Column#516, Column#203->Column#517, Column#204->Column#518, Column#203->Column#519, Column#205->Column#520, Column#206->Column#521, Column#207->Column#522	257.3 KB	N/A
└─Selection_9	0.80	1	root		time:24.1ms, open:259.5µs, close:41.1µs, loops:2	gt(Column#47, ?)	259.7 KB	N/A
  └─HashAgg_13	1.00	1	root		time:24ms, open:202.8µs, close:40.4µs, loops:3	funcs:count(?)->Column#47, funcs:sum(Column#839)->Column#48, funcs:min(Column#840)->Column#49, funcs:max(Column#841)->Column#50, funcs:sum(Column#842)->Column#51, funcs:sum(Column#843)->Column#52, funcs:min(Column#844)->Column#53, funcs:max(Column#845)->Column#54, funcs:sum(Column#846)->Column#55, funcs:sum(Column#847)->Column#56, funcs:min(Column#848)->Column#57, funcs:max(Column#849)->Column#58, funcs:sum(Column#850)->Column#59, funcs:sum(Column#851)->Column#60, funcs:min(Column#852)->Column#61, funcs:max(Column#853)->Column#62, funcs:sum(Column#854)->Column#63, funcs:sum(Column#855)->Column#64, funcs:min(Column#856)->Column#65, funcs:max(Column#857)->Column#66, funcs:sum(Column#858)->Column#67, funcs:sum(Column#859)->Column#68, funcs:min(Column#860)->Column#69, funcs:max(Column#861)->Column#70, funcs:sum(Column#862)->Column#71, funcs:sum(Column#863)->Column#72, funcs:min(Column#864)->Column#73, funcs:max(Column#865)->Column#74, funcs:sum(Column#866)->Column#75, funcs:sum(Column#867)->Column#76, funcs:min(Column#868)->Column#77, funcs:max(Column#869)->Column#78, funcs:sum(Column#870)->Column#79, funcs:sum(Column#871)->Column#80, funcs:min(Column#872)->Column#81, funcs:max(Column#873)->Column#82, funcs:sum(Column#874)->Column#83, funcs:sum(Column#875)->Column#84, funcs:min(Column#876)->Column#85, funcs:max(Column#877)->Column#86, funcs:sum(Column#878)->Column#87, funcs:sum(Column#879)->Column#88, funcs:min(Column#880)->Column#89, funcs:max(Column#881)->Column#90, funcs:sum(Column#882)->Column#91, funcs:sum(Column#883)->Column#92, funcs:min(Column#884)->Column#93, funcs:max(Column#885)->Column#94, funcs:sum(Column#886)->Column#95, funcs:sum(Column#887)->Column#96, funcs:min(Column#888)->Column#97, funcs:max(Column#889)->Column#98, funcs:sum(Column#890)->Column#99, funcs:sum(Column#891)->Column#100, funcs:min(Column#892)->Column#101, funcs:max(Column#893)->Column#102, funcs:sum(Column#894)->Column#103, funcs:sum(Column#895)->Column#104, funcs:min(Column#896)->Column#105, funcs:max(Column#897)->Column#106, funcs:sum(Column#898)->Column#107, funcs:sum(Column#899)->Column#108, funcs:min(Column#900)->Column#109, funcs:max(Column#901)->Column#110, funcs:sum(Column#902)->Column#111, funcs:sum(Column#903)->Column#112, funcs:min(Column#904)->Column#113, funcs:max(Column#905)->Column#114, funcs:sum(Column#906)->Column#115, funcs:sum(Column#907)->Column#116, funcs:min(Column#908)->Column#117, funcs:max(Column#909)->Column#118, funcs:sum(Column#910)->Column#119, funcs:sum(Column#911)->Column#120, funcs:min(Column#912)->Column#121, funcs:max(Column#913)->Column#122, funcs:sum(Column#914)->Column#123, funcs:sum(Column#915)->Column#124, funcs:min(Column#916)->Column#125, funcs:max(Column#917)->Column#126, funcs:sum(Column#918)->Column#127, funcs:sum(Column#919)->Column#128, funcs:min(Column#920)->Column#129, funcs:max(Column#921)->Column#130, funcs:sum(Column#922)->Column#131, funcs:sum(Column#923)->Column#132, funcs:min(Column#924)->Column#133, funcs:max(Column#925)->Column#134, funcs:sum(Column#926)->Column#135, funcs:sum(Column#927)->Column#136, funcs:min(Column#928)->Column#137, funcs:max(Column#929)->Column#138, funcs:sum(Column#930)->Column#139, funcs:sum(Column#931)->Column#140, funcs:min(Column#932)->Column#141, funcs:max(Column#933)->Column#142, funcs:sum(Column#934)->Column#143, funcs:sum(Column#935)->Column#144, funcs:min(Column#936)->Column#145, funcs:max(Column#937)->Column#146, funcs:sum(Column#938)->Column#147, funcs:sum(Column#939)->Column#148, funcs:min(Column#940)->Column#149, funcs:max(Column#941)->Column#150, funcs:sum(Column#942)->Column#151, funcs:sum(Column#943)->Column#152, funcs:min(Column#944)->Column#153, funcs:max(Column#945)->Column#154, funcs:sum(Column#946)->Column#155, funcs:sum(Column#947)->Column#156, funcs:min(Column#948)->Column#157, funcs:max(Column#949)->Column#158, funcs:sum(Column#950)->Column#159, funcs:sum(Column#951)->Column#160, funcs:min(Column#952)->Column#161, funcs:max(Column#953)->Column#162, funcs:sum(Column#954)->Column#163, funcs:sum(Column#955)->Column#164, funcs:min(Column#956)->Column#165, funcs:max(Column#957)->Column#166, funcs:sum(Column#958)->Column#167, funcs:sum(Column#959)->Column#168, funcs:min(Column#960)->Column#169, funcs:max(Column#961)->Column#170, funcs:sum(Column#962)->Column#171, funcs:sum(Column#963)->Column#172, funcs:min(Column#964)->Column#173, funcs:max(Column#965)->Column#174, funcs:sum(Column#966)->Column#175, funcs:sum(Column#967)->Column#176, funcs:min(Column#968)->Column#177, funcs:max(Column#969)->Column#178, funcs:sum(Column#970)->Column#179, funcs:sum(Column#971)->Column#180, funcs:min(Column#972)->Column#181, funcs:max(Column#973)->Column#182, funcs:sum(Column#974)->Column#183, funcs:sum(Column#975)->Column#184, funcs:sum(Column#976)->Column#185, funcs:sum(Column#977)->Column#186, funcs:sum(Column#978)->Column#187, funcs:sum(Column#979)->Column#188, funcs:sum(Column#980)->Column#189, funcs:sum(Column#981)->Column#190, funcs:sum(Column#982)->Column#191, funcs:sum(Column#983)->Column#192, funcs:sum(Column#984)->Column#193, funcs:sum(Column#985)->Column#194, funcs:sum(Column#986)->Column#195, funcs:sum(Column#987)->Column#196, funcs:sum(Column#988)->Column#197, funcs:sum(Column#989)->Column#198, funcs:sum(Column#990)->Column#199, funcs:sum(Column#991)->Column#200, funcs:sum(Column#992)->Column#201, funcs:sum(Column#993)->Column#202, funcs:sum(Column#994)->Column#203, funcs:sum(Column#995)->Column#204, funcs:count(distinct Column#996)->Column#205, funcs:count(distinct Column#997)->Column#206, funcs:count(distinct Column#998)->Column#207	6.23 MB	0 Bytes
    └─Projection_28	18368.93	4152	root		time:11.7ms, open:77.5µs, close:39.7µs, loops:6, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#839, intuit_risk.pmt_txn_fact.amount->Column#840, intuit_risk.pmt_txn_fact.amount->Column#841, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#842, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#843, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#844, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#845, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#846, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#847, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#848, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#849, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#850, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#851, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#852, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#853, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#854, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#855, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#856, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#857, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#858, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#859, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#860, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#861, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#862, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#863, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#864, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#865, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#866, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#867, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#868, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#869, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#870, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#871, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#872, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#873, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#874, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#875, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#876, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#877, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#878, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#879, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#880, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#881, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#882, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#883, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#884, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#885, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#886, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#887, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#888, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#889, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#890, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#891, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#892, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#893, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#894, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#895, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#896, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#897, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#898, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#899, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#900, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#901, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#902, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#903, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#904, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#905, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#906, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#907, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#908, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#909, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#910, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#911, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#912, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#913, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#914, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#915, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#916, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#917, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#918, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#919, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#920, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#921, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#922, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#923, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#924, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#925, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#926, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#927, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#928, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#929, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#930, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#931, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#932, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#933, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#934, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#935, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#936, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#937, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#938, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#939, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#940, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#941, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#942, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#943, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#944, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#945, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#946, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#947, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#948, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#949, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#950, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#951, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#952, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#953, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#954, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#955, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#956, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#957, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#958, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#959, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#960, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#961, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#962, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#963, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#964, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#965, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#966, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#967, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#968, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#969, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#970, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#971, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#972, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#973, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#974, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#975, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#976, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#977, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#978, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#979, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#980, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#981, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#982, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#983, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#984, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#985, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#986, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#987, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#988, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#989, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#990, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#991, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#992, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#993, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#994, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#995, intuit_risk.pmt_txn_fact.card_type->Column#996, intuit_risk.pmt_txn_fact.entry_method->Column#997, intuit_risk.pmt_txn_fact.mt_gateway->Column#998	25.4 MB	N/A
      └─IndexReader_21	18368.93	4152	root	partition:p20260501,p20260601,pmax	time:8.23ms, open:76.5µs, close:11.8µs, loops:6, cop_task: {num: 7, max: 3.21ms, min: 693.1µs, avg: 1.48ms, p95: 3.21ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 3.29ms, tot_wait: 259.6µs, copr_cache: disabled, build_task_duration: 22.1µs, max_distsql_concurrency: 3}, fetch_resp_duration: 7.9ms, rpc_info:{Cop:{num_rpc:7, total_time:10.3ms}}	index:IndexRangeScan_20	316.8 KB	N/A
        └─IndexRangeScan_20	18368.93	4152	cop[tikv]	table:p, index:idx_pmt_merchant_runtime_cov(merchant_account_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1.43ms, p80:0s, p95:10ms, iters:24, tasks:7}, scan_detail: {total_process_keys: 4152, total_process_keys_size: 705989, total_keys: 4159, get_snapshot_time: 119µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.29ms, total_suspend_time: 4.73µs, total_wait_time: 259.6µs, total_kv_read_wall_time: 10ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 10. group_a_bundle_014

- Filter/window: `p.check_bank_routing_number = %s` / `90d`
- Chosen event: `INV0019958147` kind=`hot_check_bank_routing_number` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 365.9 ms | ok |
| `optimized_default` | `{}` | 327.5 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 315.5 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 316.5 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 324.5 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 364.4 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0045`,
  SUM(p.amount) AS `metric__a_0046`,
  MIN(p.amount) AS `metric__a_0047`,
  MAX(p.amount) AS `metric__a_0048`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `metric__a_1005`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1005`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1006`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1006`,
  MIN(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1007`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1007`,
  MAX(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1008`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1008`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `metric__a_1017`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1017`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1018`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1018`,
  MIN(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1019`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1019`,
  MAX(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1020`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1020`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `metric__a_1029`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1029`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1030`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1030`,
  MIN(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1031`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1031`,
  MAX(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1032`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1032`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `metric__a_1041`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1041`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1042`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1042`,
  MIN(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1043`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1043`,
  MAX(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1044`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1044`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `metric__a_1053`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1053`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1054`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1054`,
  MIN(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1055`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1055`,
  MAX(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1056`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1056`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `metric__a_1065`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1065`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1066`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1066`,
  MIN(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1067`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1067`,
  MAX(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1068`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1068`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `metric__a_1077`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1077`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1078`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1078`,
  MIN(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1079`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1079`,
  MAX(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1080`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1080`
FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1768101078317
GROUP BY p.check_bank_routing_number;
```

#### Original Params

```json
[
  "322271627"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=365.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	42.42	1	root		time:331ms, open:1.2ms, close:13.4µs, loops:2, RU:1072.15, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75	94.5 KB	N/A
└─HashAgg_27	42.42	1	root		time:331ms, open:1.2ms, close:11.8µs, loops:2, partial_worker:{wall_time:329.74668ms, concurrency:4, task_num:1, tot_wait:329.686578ms, tot_exec:24.937µs, tot_time:1.318885294s, max:329.7243ms, p95:329.7243ms}, final_worker:{wall_time:329.785203ms, concurrency:4, task_num:4, tot_wait:15.177µs, tot_exec:142ns, tot_time:1.318937029s, max:329.739391ms, p95:329.739391ms}	group by:intuit_risk.pmt_txn_fact.check_bank_routing_number, funcs:count(Column#82)->Column#47, funcs:sum(Column#83)->Column#48, funcs:min(Column#84)->Column#49, funcs:max(Column#85)->Column#50, funcs:sum(Column#86)->Column#51, funcs:sum(Column#87)->Column#52, funcs:min(Column#88)->Column#53, funcs:max(Column#89)->Column#54, funcs:sum(Column#90)->Column#55, funcs:sum(Column#91)->Column#56, funcs:min(Column#92)->Column#57, funcs:max(Column#93)->Column#58, funcs:sum(Column#94)->Column#59, funcs:sum(Column#95)->Column#60, funcs:min(Column#96)->Column#61, funcs:max(Column#97)->Column#62, funcs:sum(Column#98)->Column#63, funcs:sum(Column#99)->Column#64, funcs:min(Column#100)->Column#65, funcs:max(Column#101)->Column#66, funcs:sum(Column#102)->Column#67, funcs:sum(Column#103)->Column#68, funcs:min(Column#104)->Column#69, funcs:max(Column#105)->Column#70, funcs:sum(Column#106)->Column#71, funcs:sum(Column#107)->Column#72, funcs:min(Column#108)->Column#73, funcs:max(Column#109)->Column#74, funcs:sum(Column#110)->Column#75, funcs:sum(Column#111)->Column#76, funcs:min(Column#112)->Column#77, funcs:max(Column#113)->Column#78	475.5 KB	0 Bytes
  └─IndexReader_28	42.42	4	root	partition:p20260201,p20260301,p20260401,p20260501,p20260601,pmax	time:330.8ms, open:1.12ms, close:9.14µs, loops:2, cop_task: {num: 6, max: 329.6ms, min: 781.8µs, avg: 148.7ms, p95: 329.6ms, max_proc_keys: 122612, p95_proc_keys: 122612, tot_proc: 880.2ms, tot_wait: 3.98ms, copr_cache: disabled, build_task_duration: 1.06ms, max_distsql_concurrency: 6}, fetch_resp_duration: 329.6ms, rpc_info:{Cop:{num_rpc:6, total_time:891.9ms}}	index:HashAgg_7	3.38 KB	N/A
    └─HashAgg_7	42.42	4	cop[tikv]		tikv_task:{proc max:330ms, min:0s, avg: 146.7ms, p80:260ms, p95:330ms, iters:336, tasks:6}, scan_detail: {total_process_keys: 340239, total_process_keys_size: 50848432, total_keys: 340245, get_snapshot_time: 3.85ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 880.2ms, total_suspend_time: 906.4µs, total_wait_time: 3.98ms, total_kv_read_wall_time: 260ms}	group by:intuit_risk.pmt_txn_fact.check_bank_routing_number, funcs:count(?)->Column#82, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#83, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#84, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#85, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#86, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#87, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#88, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#89, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#90, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#91, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#92, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#93, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#94, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#95, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#96, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#97, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#98, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#99, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#100, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#101, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#102, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#103, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#104, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#105, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#106, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#107, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#108, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#109, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#110, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#111, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#112, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#113	N/A	N/A
      └─IndexRangeScan_25	479923.47	340239	cop[tikv]	table:p, index:idx_test(check_bank_routing_number, event_date, mt_gateway, amount)	tikv_task:{proc max:100ms, min:0s, avg: 43.3ms, p80:90ms, p95:100ms, iters:336, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__a_0045`,
  SUM(p.amount) AS `metric__a_0046`,
  MIN(p.amount) AS `metric__a_0047`,
  MAX(p.amount) AS `metric__a_0048`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `metric__a_1005`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1005`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1006`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1006`,
  MIN(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1007`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1007`,
  MAX(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN p.amount END) AS `metric__a_1008`,
  SUM(CASE WHEN p.mt_gateway = 'MM-MerchantLink' THEN 1 ELSE 0 END) AS `present__a_1008`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `metric__a_1017`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1017`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1018`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1018`,
  MIN(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1019`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1019`,
  MAX(CASE WHEN p.mt_gateway = 'QBMS' THEN p.amount END) AS `metric__a_1020`,
  SUM(CASE WHEN p.mt_gateway = 'QBMS' THEN 1 ELSE 0 END) AS `present__a_1020`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `metric__a_1029`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1029`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1030`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1030`,
  MIN(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1031`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1031`,
  MAX(CASE WHEN p.mt_gateway = 'Direct' THEN p.amount END) AS `metric__a_1032`,
  SUM(CASE WHEN p.mt_gateway = 'Direct' THEN 1 ELSE 0 END) AS `present__a_1032`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `metric__a_1041`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1041`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1042`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1042`,
  MIN(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1043`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1043`,
  MAX(CASE WHEN p.mt_gateway = 'PayPal' THEN p.amount END) AS `metric__a_1044`,
  SUM(CASE WHEN p.mt_gateway = 'PayPal' THEN 1 ELSE 0 END) AS `present__a_1044`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `metric__a_1053`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1053`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1054`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1054`,
  MIN(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1055`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1055`,
  MAX(CASE WHEN p.mt_gateway = 'Stripe' THEN p.amount END) AS `metric__a_1056`,
  SUM(CASE WHEN p.mt_gateway = 'Stripe' THEN 1 ELSE 0 END) AS `present__a_1056`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `metric__a_1065`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1065`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1066`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1066`,
  MIN(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1067`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1067`,
  MAX(CASE WHEN p.mt_gateway = 'Square' THEN p.amount END) AS `metric__a_1068`,
  SUM(CASE WHEN p.mt_gateway = 'Square' THEN 1 ELSE 0 END) AS `present__a_1068`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `metric__a_1077`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1077`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1078`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1078`,
  MIN(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1079`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1079`,
  MAX(CASE WHEN p.mt_gateway = 'Braintree' THEN p.amount END) AS `metric__a_1080`,
  SUM(CASE WHEN p.mt_gateway = 'Braintree' THEN 1 ELSE 0 END) AS `present__a_1080`
FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1768101078317
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  "322271627"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_hashagg_16_8
-- explain_analyze_elapsed_ms=315.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:285.4ms, open:225.7µs, close:18.4µs, loops:2, RU:1042.09, Concurrency:OFF	Column#47->Column#79, Column#48->Column#80, Column#49->Column#81, Column#50->Column#82, Column#51->Column#83, Column#51->Column#84, Column#52->Column#85, Column#51->Column#86, Column#53->Column#87, Column#51->Column#88, Column#54->Column#89, Column#51->Column#90, Column#55->Column#91, Column#55->Column#92, Column#56->Column#93, Column#55->Column#94, Column#57->Column#95, Column#55->Column#96, Column#58->Column#97, Column#55->Column#98, Column#59->Column#99, Column#59->Column#100, Column#60->Column#101, Column#59->Column#102, Column#61->Column#103, Column#59->Column#104, Column#62->Column#105, Column#59->Column#106, Column#63->Column#107, Column#63->Column#108, Column#64->Column#109, Column#63->Column#110, Column#65->Column#111, Column#63->Column#112, Column#66->Column#113, Column#63->Column#114, Column#67->Column#115, Column#67->Column#116, Column#68->Column#117, Column#67->Column#118, Column#69->Column#119, Column#67->Column#120, Column#70->Column#121, Column#67->Column#122, Column#71->Column#123, Column#71->Column#124, Column#72->Column#125, Column#71->Column#126, Column#73->Column#127, Column#71->Column#128, Column#74->Column#129, Column#71->Column#130, Column#75->Column#131, Column#75->Column#132, Column#76->Column#133, Column#75->Column#134, Column#77->Column#135, Column#75->Column#136, Column#78->Column#137, Column#75->Column#138	53.1 KB	N/A
└─Selection_9	0.80	1	root		time:285.3ms, open:209.7µs, close:16.3µs, loops:2	gt(Column#47, ?)	51.7 KB	N/A
  └─HashAgg_19	1.00	1	root		time:285.2ms, open:193.5µs, close:15.8µs, loops:3, partial_worker:{wall_time:285.001697ms, concurrency:8, task_num:1, tot_wait:284.92163ms, tot_exec:16.59µs, tot_time:2.279626322s, max:284.960787ms, p95:284.960787ms}, final_worker:{wall_time:285.021788ms, concurrency:16, task_num:16, tot_wait:180.908µs, tot_exec:653ns, tot_time:4.559836314s, max:285.00776ms, p95:285.00776ms}	funcs:count(Column#142)->Column#47, funcs:sum(Column#143)->Column#48, funcs:min(Column#144)->Column#49, funcs:max(Column#145)->Column#50, funcs:sum(Column#146)->Column#51, funcs:sum(Column#147)->Column#52, funcs:min(Column#148)->Column#53, funcs:max(Column#149)->Column#54, funcs:sum(Column#150)->Column#55, funcs:sum(Column#151)->Column#56, funcs:min(Column#152)->Column#57, funcs:max(Column#153)->Column#58, funcs:sum(Column#154)->Column#59, funcs:sum(Column#155)->Column#60, funcs:min(Column#156)->Column#61, funcs:max(Column#157)->Column#62, funcs:sum(Column#158)->Column#63, funcs:sum(Column#159)->Column#64, funcs:min(Column#160)->Column#65, funcs:max(Column#161)->Column#66, funcs:sum(Column#162)->Column#67, funcs:sum(Column#163)->Column#68, funcs:min(Column#164)->Column#69, funcs:max(Column#165)->Column#70, funcs:sum(Column#166)->Column#71, funcs:sum(Column#167)->Column#72, funcs:min(Column#168)->Column#73, funcs:max(Column#169)->Column#74, funcs:sum(Column#170)->Column#75, funcs:sum(Column#171)->Column#76, funcs:min(Column#172)->Column#77, funcs:max(Column#173)->Column#78	801.6 KB	0 Bytes
    └─IndexReader_20	1.00	4	root	partition:p20260201,p20260301,p20260401,p20260501,p20260601,pmax	time:285ms, open:83µs, close:11.7µs, loops:2, cop_task: {num: 6, max: 285ms, min: 998.3µs, avg: 132.7ms, p95: 285ms, max_proc_keys: 122612, p95_proc_keys: 122612, tot_proc: 790.1ms, tot_wait: 262.3µs, copr_cache: disabled, build_task_duration: 23.7µs, max_distsql_concurrency: 6}, fetch_resp_duration: 284.8ms, rpc_info:{Cop:{num_rpc:6, total_time:795.9ms}}	index:HashAgg_11	3.31 KB	N/A
      └─HashAgg_11	1.00	4	cop[tikv]		tikv_task:{proc max:290ms, min:0s, avg: 135ms, p80:250ms, p95:290ms, iters:336, tasks:6}, scan_detail: {total_process_keys: 340239, total_process_keys_size: 50848432, total_keys: 340245, get_snapshot_time: 127.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 790.1ms, total_suspend_time: 740.3µs, total_wait_time: 262.3µs, total_kv_read_wall_time: 160ms}	funcs:count(?)->Column#142, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#143, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#144, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#145, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#146, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#147, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#148, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#149, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#150, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#151, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#152, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#153, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#154, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#155, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#156, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#157, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#158, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#159, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#160, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#161, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#162, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#163, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#164, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#165, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#166, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#167, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#168, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#169, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#170, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#171, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#172, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#173	N/A	N/A
        └─IndexRangeScan_17	479923.47	340239	cop[tikv]	table:p, index:idx_test(check_bank_routing_number, event_date, mt_gateway, amount)	tikv_task:{proc max:60ms, min:0s, avg: 26.7ms, p80:50ms, p95:60ms, iters:336, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 11. group_b_bundle_008

- Filter/window: `d.true_ip = %s` / `7d`
- Chosen event: `INV0042672604` kind=`normal` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 43.8 ms | ok |
| `optimized_default` | `{}` | 35.9 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 34.2 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 37.2 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 38.5 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 37.3 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__b_0010`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `metric__b_0056`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `present__b_0056`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `metric__b_0059`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `present__b_0059`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `metric__b_0062`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `present__b_0062`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `metric__b_0065`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `present__b_0065`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `metric__b_0068`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `present__b_0068`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `metric__b_0071`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `present__b_0071`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__b_0160`,
  COUNT(DISTINCT(d.smart_id)) AS `metric__b_0164`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__b_0168`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__b_0172`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__b_0176`,
  MIN(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0272`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0272`,
  MAX(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0273`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0273`,
  AVG(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0274`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0274`,
  MIN(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0281`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0281`,
  MAX(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0282`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0282`,
  AVG(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0283`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0283`,
  MIN(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0290`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0290`,
  MAX(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0291`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0291`,
  AVG(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0292`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0292`,
  MIN(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0299`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0299`,
  MAX(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0300`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0300`,
  AVG(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0301`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0301`,
  MIN(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0308`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0308`,
  MAX(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0309`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0309`,
  AVG(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0310`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0310`
FROM deviceprofile_fact d
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-30 18:23:33.347000'
GROUP BY d.true_ip;
```

#### Original Params

```json
[
  "109.99.144.24"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=43.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	1.00	1	root		time:12.1ms, open:869.4µs, close:10.7µs, loops:2, RU:6.31, Concurrency:OFF	Column#60, Column#61, Column#61, Column#62, Column#62, Column#63, Column#63, Column#64, Column#64, Column#65, Column#65, Column#66, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, Column#73, Column#75, Column#73, Column#76, Column#77, Column#78, Column#77, Column#79, Column#77, Column#80, Column#81, Column#82, Column#81, Column#83, Column#81, Column#84, Column#85, Column#86, Column#85, Column#87, Column#85, Column#88, Column#89, Column#90, Column#89, Column#91, Column#89	130.0 KB	N/A
└─HashAgg_9	1.00	1	root		time:12ms, open:866µs, close:9µs, loops:2	group by:Column#223, funcs:count(?)->Column#60, funcs:sum(Column#192)->Column#61, funcs:sum(Column#193)->Column#62, funcs:sum(Column#194)->Column#63, funcs:sum(Column#195)->Column#64, funcs:sum(Column#196)->Column#65, funcs:sum(Column#197)->Column#66, funcs:count(distinct Column#198)->Column#67, funcs:count(distinct Column#199)->Column#68, funcs:count(distinct Column#200)->Column#69, funcs:count(distinct Column#201)->Column#70, funcs:count(distinct Column#202)->Column#71, funcs:min(Column#203)->Column#72, funcs:sum(Column#204)->Column#73, funcs:max(Column#205)->Column#74, funcs:avg(Column#206)->Column#75, funcs:min(Column#207)->Column#76, funcs:sum(Column#208)->Column#77, funcs:max(Column#209)->Column#78, funcs:avg(Column#210)->Column#79, funcs:min(Column#211)->Column#80, funcs:sum(Column#212)->Column#81, funcs:max(Column#213)->Column#82, funcs:avg(Column#214)->Column#83, funcs:min(Column#215)->Column#84, funcs:sum(Column#216)->Column#85, funcs:max(Column#217)->Column#86, funcs:avg(Column#218)->Column#87, funcs:min(Column#219)->Column#88, funcs:sum(Column#220)->Column#89, funcs:max(Column#221)->Column#90, funcs:avg(Column#222)->Column#91	199.4 KB	0 Bytes
  └─Projection_29	367.45	135	root		time:11.8ms, open:854.8µs, close:8.5µs, loops:2, Concurrency:OFF	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#192, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#193, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#194, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#196, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#197, intuit_risk.deviceprofile_fact.exact_id->Column#198, intuit_risk.deviceprofile_fact.smart_id->Column#199, intuit_risk.deviceprofile_fact.input_ip->Column#200, intuit_risk.deviceprofile_fact.proxy_ip->Column#201, intuit_risk.deviceprofile_fact.agent_type->Column#202, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#203, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#204, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#205, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#207, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#208, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#209, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#210, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#212, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#213, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#214, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#215, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#217, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#222, intuit_risk.deviceprofile_fact.true_ip->Column#223	75.0 KB	N/A
    └─IndexReader_21	367.45	135	root	partition:p20260401,p20260501,p20260601,pmax	time:11.3ms, open:848.1µs, close:7.65µs, loops:2, cop_task: {num: 4, max: 10.3ms, min: 1.39ms, avg: 4.64ms, p95: 10.3ms, max_proc_keys: 116, p95_proc_keys: 116, tot_proc: 11ms, tot_wait: 4.39ms, copr_cache: disabled, build_task_duration: 803.4µs, max_distsql_concurrency: 4}, fetch_resp_duration: 10.4ms, rpc_info:{Cop:{num_rpc:4, total_time:18.5ms}}	index:IndexRangeScan_20	25.4 KB	N/A
      └─IndexRangeScan_20	367.45	135	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:6, tasks:4}, scan_detail: {total_process_keys: 135, total_process_keys_size: 49941, total_keys: 139, get_snapshot_time: 4.3ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 11ms, total_suspend_time: 12.4µs, total_wait_time: 4.39ms, total_kv_read_wall_time: 20ms}	range:(? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__b_0010`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `metric__b_0056`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' THEN 1 ELSE 0 END) AS `present__b_0056`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `metric__b_0059`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' THEN 1 ELSE 0 END) AS `present__b_0059`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `metric__b_0062`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' THEN 1 ELSE 0 END) AS `present__b_0062`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `metric__b_0065`,
  SUM(CASE WHEN d.agent_type = 'tablet' THEN 1 ELSE 0 END) AS `present__b_0065`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `metric__b_0068`,
  SUM(CASE WHEN d.agent_type = 'desktop' THEN 1 ELSE 0 END) AS `present__b_0068`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `metric__b_0071`,
  SUM(CASE WHEN d.agent_type = 'unknown' THEN 1 ELSE 0 END) AS `present__b_0071`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__b_0160`,
  COUNT(DISTINCT(d.smart_id)) AS `metric__b_0164`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__b_0168`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__b_0172`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__b_0176`,
  MIN(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0272`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0272`,
  MAX(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0273`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0273`,
  AVG(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__b_0274`,
  SUM(CASE WHEN d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__b_0274`,
  MIN(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0281`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0281`,
  MAX(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0282`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0282`,
  AVG(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN CAST(d.device_fingerprint_score AS DECIMAL(10,2)) END) AS `metric__b_0283`,
  SUM(CASE WHEN d.device_fingerprint_score IS NOT NULL AND d.device_fingerprint_score != '' THEN 1 ELSE 0 END) AS `present__b_0283`,
  MIN(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0290`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0290`,
  MAX(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0291`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0291`,
  AVG(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__b_0292`,
  SUM(CASE WHEN d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__b_0292`,
  MIN(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0299`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0299`,
  MAX(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0300`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0300`,
  AVG(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN CAST(d.true_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0301`,
  SUM(CASE WHEN d.true_ip_score IS NOT NULL AND d.true_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0301`,
  MIN(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0308`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0308`,
  MAX(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0309`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0309`,
  AVG(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN CAST(d.input_ip_score AS DECIMAL(10,2)) END) AS `metric__b_0310`,
  SUM(CASE WHEN d.input_ip_score IS NOT NULL AND d.input_ip_score != '' THEN 1 ELSE 0 END) AS `present__b_0310`
FROM deviceprofile_fact d
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-30 18:23:33.347000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  "109.99.144.24"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_hashagg_16_8
-- explain_analyze_elapsed_ms=34.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:2.35ms, open:98.7µs, close:10.5µs, loops:2, RU:2.83, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	156.5 KB	N/A
└─Selection_9	0.80	1	root		time:2.32ms, open:96µs, close:8.97µs, loops:2	gt(Column#60, ?)	114.6 KB	N/A
  └─HashAgg_13	1.00	1	root		time:2.3ms, open:92.8µs, close:8.54µs, loops:3	funcs:count(?)->Column#60, funcs:sum(Column#208)->Column#61, funcs:sum(Column#209)->Column#62, funcs:sum(Column#210)->Column#63, funcs:sum(Column#211)->Column#64, funcs:sum(Column#212)->Column#65, funcs:sum(Column#213)->Column#66, funcs:count(distinct Column#214)->Column#67, funcs:count(distinct Column#215)->Column#68, funcs:count(distinct Column#216)->Column#69, funcs:count(distinct Column#217)->Column#70, funcs:count(distinct Column#218)->Column#71, funcs:min(Column#219)->Column#72, funcs:sum(Column#220)->Column#73, funcs:max(Column#221)->Column#74, funcs:avg(Column#222)->Column#75, funcs:min(Column#223)->Column#76, funcs:sum(Column#224)->Column#77, funcs:max(Column#225)->Column#78, funcs:avg(Column#226)->Column#79, funcs:min(Column#227)->Column#80, funcs:sum(Column#228)->Column#81, funcs:max(Column#229)->Column#82, funcs:avg(Column#230)->Column#83, funcs:min(Column#231)->Column#84, funcs:sum(Column#232)->Column#85, funcs:max(Column#233)->Column#86, funcs:avg(Column#234)->Column#87, funcs:min(Column#235)->Column#88, funcs:sum(Column#236)->Column#89, funcs:max(Column#237)->Column#90, funcs:avg(Column#238)->Column#91	199.7 KB	0 Bytes
    └─Projection_28	367.45	135	root		time:2.08ms, open:84.1µs, close:7.87µs, loops:2, Concurrency:OFF	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#208, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#209, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#210, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#211, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#212, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#213, intuit_risk.deviceprofile_fact.exact_id->Column#214, intuit_risk.deviceprofile_fact.smart_id->Column#215, intuit_risk.deviceprofile_fact.input_ip->Column#216, intuit_risk.deviceprofile_fact.proxy_ip->Column#217, intuit_risk.deviceprofile_fact.agent_type->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#222, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#223, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#224, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#225, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#226, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#230, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#231, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#232, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#233, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#234, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#235, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#236, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#237, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#238	73.4 KB	N/A
      └─IndexReader_21	367.45	135	root	partition:p20260401,p20260501,p20260601,pmax	time:1.58ms, open:79.9µs, close:7.05µs, loops:2, cop_task: {num: 4, max: 1.41ms, min: 515µs, avg: 933.8µs, p95: 1.41ms, max_proc_keys: 116, p95_proc_keys: 116, tot_proc: 499.3µs, tot_wait: 154.2µs, copr_cache: disabled, build_task_duration: 27.7µs, max_distsql_concurrency: 4}, fetch_resp_duration: 1.44ms, rpc_info:{Cop:{num_rpc:4, total_time:3.66ms}}	index:IndexRangeScan_20	25.3 KB	N/A
        └─IndexRangeScan_20	367.45	135	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:6, tasks:4}, scan_detail: {total_process_keys: 135, total_process_keys_size: 49941, total_keys: 139, get_snapshot_time: 71µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 499.3µs, total_wait_time: 154.2µs}	range:(? ?,? +inf], keep order:false	N/A	N/A
```

### 12. group_c_bundle_011

- Filter/window: `d.true_ip = %s` / `7d`
- Chosen event: `INV0009827520` kind=`normal` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 592.1 ms | ok |
| `optimized_default` | `{}` | 123.6 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 109.9 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 142.1 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 101.5 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 104.3 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0098`,
  SUM(p.amount) AS `metric__c_0099`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0100`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0101`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1774951222853
  AND d.jms_timestamp >= '2026-03-31 03:00:22.853000'
GROUP BY d.true_ip;
```

#### Original Params

```json
[
  "9.169.124.5"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=592.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_13	40.17	1	root		time:417.7ms, open:555.2µs, close:30.8µs, loops:2, RU:1215.87	group by:intuit_risk.deviceprofile_fact.true_ip, funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	50.9 KB	0 Bytes
└─Projection_21	115880.01	324	root		time:417.5ms, open:547.2µs, close:29.8µs, loops:5, Concurrency:5	intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.deviceprofile_fact.true_ip	90.7 KB	N/A
  └─IndexHashJoin_30	115880.01	324	root		time:417.6ms, open:545.8µs, close:8.15µs, loops:5, inner:{total:846.9ms, concurrency:5, task:4, construct:11.5ms, fetch:834.8ms, build:2.35ms, join:505.5µs}	inner join, inner:IndexReader_48, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	3.99 MB	N/A
    ├─IndexReader_45(Build)	74097.06	17870	root	partition:p20260401,p20260501,p20260601,pmax	time:51.3ms, open:543.3µs, close:5.35µs, loops:20, cop_task: {num: 13, max: 20.2ms, min: 742.8µs, avg: 4.8ms, p95: 20.2ms, max_proc_keys: 12951, p95_proc_keys: 12951, tot_proc: 46.8ms, tot_wait: 1.81ms, copr_cache: disabled, build_task_duration: 503.7µs, max_distsql_concurrency: 4}, fetch_resp_duration: 50.3ms, rpc_info:{Cop:{num_rpc:13, total_time:62.2ms}}	index:Selection_44	677.0 KB	N/A
    │ └─Selection_44	74097.06	17870	cop[tikv]		tikv_task:{proc max:20ms, min:0s, avg: 4.62ms, p80:10ms, p95:20ms, iters:75, tasks:13}, scan_detail: {total_process_keys: 31026, total_process_keys_size: 10980601, total_keys: 31039, get_snapshot_time: 1.54ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 46.8ms, total_suspend_time: 129.6µs, total_wait_time: 1.81ms, total_kv_read_wall_time: 60ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_43	109394.56	31026	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:20ms, min:0s, avg: 4.62ms, p80:10ms, p95:20ms, iters:75, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_48(Probe)	115880.01	324	root	partition:p20260401,p20260501,p20260601,pmax	total_time:830ms, total_open:26.4ms, total_close:38.7µs, loops:8, cop_task: {num: 44, max: 345.3ms, min: 3.4ms, avg: 73.6ms, p95: 206.3ms, max_proc_keys: 65, p95_proc_keys: 33, tot_proc: 3.01s, tot_wait: 116.3ms, copr_cache: disabled, build_task_duration: 4.98ms, max_distsql_concurrency: 11}, fetch_resp_duration: 802.5ms, rpc_info:{Cop:{num_rpc:44, total_time:3.24s}}	index:Selection_47	8.31 KB	N/A
      └─Selection_47	115880.01	324	cop[tikv]		tikv_task:{proc max:340ms, min:0s, avg: 67.5ms, p80:130ms, p95:190ms, iters:47, tasks:44}, scan_detail: {total_process_keys: 324, total_process_keys_size: 104833, total_keys: 9828, get_snapshot_time: 7.66ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.01s, total_suspend_time: 7.06ms, total_wait_time: 116.3ms, total_kv_read_wall_time: 2.97s}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_46	157025.02	324	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:340ms, min:0s, avg: 67.5ms, p80:130ms, p95:190ms, iters:47, tasks:44}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0098`,
  SUM(p.amount) AS `metric__c_0099`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0100`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0101`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1774951222853
  AND d.jms_timestamp >= '2026-03-31 03:00:22.853000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  "9.169.124.5"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=101.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Selection_13	0.80	1	root		time:65.6ms, open:74.2µs, close:7.36µs, loops:2, RU:228.37	gt(Column#106, ?)	36.3 KB	N/A
└─HashAgg_17	1.00	1	root		time:65.5ms, open:72.2µs, close:6.78µs, loops:3	funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	46.5 KB	0 Bytes
  └─IndexHashJoin_28	115880.01	324	root		time:65.4ms, open:66.3µs, close:6.1µs, loops:5, inner:{total:73.2ms, concurrency:5, task:4, construct:11.6ms, fetch:61.2ms, build:2.38ms, join:375.1µs}	inner join, inner:IndexReader_46, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	2.63 MB	N/A
    ├─IndexReader_43(Build)	74097.06	17870	root	partition:p20260401,p20260501,p20260601,pmax	time:31.1ms, open:65.2µs, close:4.3µs, loops:20, cop_task: {num: 13, max: 12.6ms, min: 860.8µs, avg: 2.94ms, p95: 12.6ms, max_proc_keys: 12951, p95_proc_keys: 12951, tot_proc: 26.5ms, tot_wait: 399.4µs, copr_cache: disabled, build_task_duration: 22.5µs, max_distsql_concurrency: 4}, fetch_resp_duration: 30.6ms, rpc_info:{Cop:{num_rpc:13, total_time:38.1ms}}	index:Selection_42	677.0 KB	N/A
    │ └─Selection_42	74097.06	17870	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 3.08ms, p80:10ms, p95:10ms, iters:75, tasks:13}, scan_detail: {total_process_keys: 31026, total_process_keys_size: 10980601, total_keys: 31039, get_snapshot_time: 170.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.5ms, total_suspend_time: 70.9µs, total_wait_time: 399.4µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_41	109394.56	31026	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 3.08ms, p80:10ms, p95:10ms, iters:75, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_46(Probe)	115880.01	324	root	partition:p20260401,p20260501,p20260601,pmax	total_time:56.3ms, total_open:30.2ms, total_close:41.4µs, loops:8, cop_task: {num: 44, max: 11.5ms, min: 856.6µs, avg: 3.77ms, p95: 8.14ms, max_proc_keys: 65, p95_proc_keys: 31, tot_proc: 70ms, tot_wait: 1.43ms, copr_cache: disabled, build_task_duration: 6.93ms, max_distsql_concurrency: 11}, fetch_resp_duration: 25.1ms, rpc_info:{Cop:{num_rpc:44, total_time:164.6ms}}	index:Selection_45	8.30 KB	N/A
      └─Selection_45	115880.01	324	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.14ms, p80:0s, p95:10ms, iters:46, tasks:44}, scan_detail: {total_process_keys: 324, total_process_keys_size: 104833, total_keys: 9828, get_snapshot_time: 574.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 70ms, total_suspend_time: 93.1µs, total_wait_time: 1.43ms, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_44	157025.02	324	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1.14ms, p80:0s, p95:10ms, iters:46, tasks:44}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### 13. group_c_bundle_014

- Filter/window: `p.merchant_account_number = %s` / `7d`
- Chosen event: `INV0037793946` kind=`hot_merchant_account_number` error=`(1105, 'context canceled')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 152.9 ms | ok |
| `optimized_default` | `{}` | 112.8 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 114.9 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 112.8 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 116.7 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 112.6 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(DISTINCT(d.smart_id)) AS `metric__c_0197`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__c_0198`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__c_0199`,
  COUNT(DISTINCT(d.true_ip)) AS `metric__c_0200`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__c_0201`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__c_0202`,
  COUNT(DISTINCT(d.agent_os)) AS `metric__c_0203`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.smart_id END) AS `metric__c_0260`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0260`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.exact_id END) AS `metric__c_0261`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0261`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.input_ip END) AS `metric__c_0262`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0262`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.smart_id END) AS `metric__c_0269`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0269`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.exact_id END) AS `metric__c_0270`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0270`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.input_ip END) AS `metric__c_0271`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0271`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.smart_id END) AS `metric__c_0278`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0278`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.exact_id END) AS `metric__c_0279`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0279`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.input_ip END) AS `metric__c_0280`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0280`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.smart_id END) AS `metric__c_0287`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0287`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.exact_id END) AS `metric__c_0288`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0288`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.input_ip END) AS `metric__c_0289`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0289`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0333`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0333`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0334`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0334`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0335`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0335`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0336`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0336`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0345`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0345`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0346`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0346`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0347`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0347`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0348`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0348`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0357`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0357`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0358`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0358`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0359`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0359`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0360`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0360`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0369`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0369`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0370`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0370`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0371`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0371`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0372`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0372`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0381`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0381`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0382`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0382`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0383`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0383`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0384`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0384`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0393`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0393`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0394`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0394`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0395`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0395`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0396`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0396`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1774726640017
  AND d.jms_timestamp >= '2026-03-28 12:37:20.017000'
GROUP BY p.merchant_account_number;
```

#### Original Params

```json
[
  5247719989330882
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=152.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_8	66.18	1	root		time:82.2ms, open:103.3µs, close:34.5µs, loops:2, RU:115.79, Concurrency:OFF	Column#106, Column#107, Column#108, Column#109, Column#110, Column#111, Column#112, Column#113, Column#114, Column#115, Column#114, Column#116, Column#114, Column#117, Column#118, Column#119, Column#118, Column#120, Column#118, Column#121, Column#122, Column#123, Column#122, Column#124, Column#122, Column#125, Column#126, Column#127, Column#126, Column#128, Column#126, Column#129, Column#130, Column#131, Column#130, Column#132, Column#133, Column#134, Column#133, Column#135, Column#136, Column#137, Column#136, Column#138, Column#139, Column#140, Column#139, Column#141, Column#142, Column#143, Column#142, Column#144, Column#145, Column#146, Column#145, Column#147, Column#148, Column#149, Column#148, Column#150, Column#151, Column#152, Column#151, Column#153, Column#154, Column#155, Column#154, Column#156, Column#157, Column#158, Column#157, Column#159, Column#160, Column#161, Column#160, Column#162, Column#163, Column#164, Column#163	311.7 KB	N/A
└─HashAgg_12	66.18	1	root		time:82.1ms, open:97.3µs, close:33µs, loops:2	group by:Column#242, funcs:count(distinct Column#183)->Column#106, funcs:count(distinct Column#184)->Column#107, funcs:count(distinct Column#185)->Column#108, funcs:count(distinct Column#186)->Column#109, funcs:count(distinct Column#187)->Column#110, funcs:count(distinct Column#188)->Column#111, funcs:count(distinct Column#189)->Column#112, funcs:count(distinct Column#190)->Column#113, funcs:sum(Column#191)->Column#114, funcs:count(distinct Column#192)->Column#115, funcs:count(distinct Column#193)->Column#116, funcs:count(distinct Column#194)->Column#117, funcs:sum(Column#195)->Column#118, funcs:count(distinct Column#196)->Column#119, funcs:count(distinct Column#197)->Column#120, funcs:count(distinct Column#198)->Column#121, funcs:sum(Column#199)->Column#122, funcs:count(distinct Column#200)->Column#123, funcs:count(distinct Column#201)->Column#124, funcs:count(distinct Column#202)->Column#125, funcs:sum(Column#203)->Column#126, funcs:count(distinct Column#204)->Column#127, funcs:count(distinct Column#205)->Column#128, funcs:min(Column#206)->Column#129, funcs:sum(Column#207)->Column#130, funcs:max(Column#208)->Column#131, funcs:min(Column#209)->Column#132, funcs:sum(Column#210)->Column#133, funcs:max(Column#211)->Column#134, funcs:min(Column#212)->Column#135, funcs:sum(Column#213)->Column#136, funcs:max(Column#214)->Column#137, funcs:min(Column#215)->Column#138, funcs:sum(Column#216)->Column#139, funcs:max(Column#217)->Column#140, funcs:min(Column#218)->Column#141, funcs:sum(Column#219)->Column#142, funcs:max(Column#220)->Column#143, funcs:min(Column#221)->Column#144, funcs:sum(Column#222)->Column#145, funcs:max(Column#223)->Column#146, funcs:min(Column#224)->Column#147, funcs:sum(Column#225)->Column#148, funcs:max(Column#226)->Column#149, funcs:min(Column#227)->Column#150, funcs:sum(Column#228)->Column#151, funcs:max(Column#229)->Column#152, funcs:min(Column#230)->Column#153, funcs:sum(Column#231)->Column#154, funcs:max(Column#232)->Column#155, funcs:min(Column#233)->Column#156, funcs:sum(Column#234)->Column#157, funcs:max(Column#235)->Column#158, funcs:min(Column#236)->Column#159, funcs:sum(Column#237)->Column#160, funcs:max(Column#238)->Column#161, funcs:min(Column#239)->Column#162, funcs:sum(Column#240)->Column#163, funcs:max(Column#241)->Column#164	602.2 KB	0 Bytes
  └─Projection_81	30558.10	421	root		time:81.1ms, open:79.9µs, close:32.1µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#183, intuit_risk.deviceprofile_fact.exact_id->Column#184, intuit_risk.deviceprofile_fact.input_ip->Column#185, intuit_risk.deviceprofile_fact.true_ip->Column#186, intuit_risk.deviceprofile_fact.proxy_ip->Column#187, intuit_risk.deviceprofile_fact.agent_type->Column#188, intuit_risk.deviceprofile_fact.agent_os->Column#189, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#190, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#191, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#192, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#193, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#194, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#196, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#197, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#198, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#199, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#200, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#201, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#202, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#203, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#204, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#205, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#207, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#208, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#209, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#210, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#212, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#213, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#214, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#215, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#217, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#218, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#221, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#222, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#223, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#225, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#226, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#230, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#232, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#234, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#235, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#236, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#237, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#238, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#239, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#240, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#241, intuit_risk.pmt_txn_fact.merchant_account_number->Column#242	1.58 MB	N/A
    └─IndexHashJoin_30	30558.10	421	root		time:80.1ms, open:78.4µs, close:8.66µs, loops:3, inner:{total:140.3ms, concurrency:5, task:2, construct:2.59ms, fetch:137.3ms, build:573.4µs, join:421.4µs}	inner join, inner:IndexLookUp_45, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	972.9 KB	N/A
      ├─IndexReader_41(Build)	17275.51	4362	root	partition:p20260401,p20260501,p20260601,pmax	time:7.43ms, open:77.2µs, close:6.04µs, loops:7, cop_task: {num: 10, max: 1.96ms, min: 658.5µs, avg: 1.34ms, p95: 1.96ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 4.13ms, tot_wait: 1.85ms, copr_cache: disabled, build_task_duration: 24.6µs, max_distsql_concurrency: 4}, fetch_resp_duration: 7.18ms, rpc_info:{Cop:{num_rpc:10, total_time:13.3ms}}	index:Selection_40	121.3 KB	N/A
      │ └─Selection_40	17275.51	4362	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1ms, p80:0s, p95:10ms, iters:38, tasks:10}, scan_detail: {total_process_keys: 6630, total_process_keys_size: 854810, total_keys: 6640, get_snapshot_time: 1.66ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.13ms, total_suspend_time: 3.97µs, total_wait_time: 1.85ms, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
      │   └─IndexRangeScan_39	23409.44	6630	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1ms, p80:0s, p95:10ms, iters:38, tasks:10}	range:[? ?,? +inf], keep order:false	N/A	N/A
      └─IndexLookUp_45(Probe)	30558.10	421	root	partition:p20260401,p20260501,p20260601,pmax	total_time:136.1ms, total_open:5.53ms, total_close:15µs, loops:4, index_task: {total_time: 121.9ms, fetch_handle: 121.9ms, build: 4.96µs, wait: 11.6µs}, table_task: {total_time: 22.3ms, num: 4, concurrency: 5}, next: {wait_index: 109.1ms, wait_table_lookup_build: 494.4µs, wait_table_lookup_resp: 20.7ms}		1.71 MB	N/A
        ├─Selection_44(Build)	30558.10	421	cop[tikv]		total_time:122ms, total_open:0s, total_close:0s, loops:16, cop_task: {num: 10, max: 64.7ms, min: 3.47ms, avg: 27ms, p95: 64.7ms, max_proc_keys: 132, p95_proc_keys: 132, tot_proc: 201.7ms, tot_wait: 2.18ms, copr_cache: disabled, build_task_duration: 1.29ms, max_distsql_concurrency: 2}, fetch_resp_duration: 121.7ms, rpc_info:{Cop:{num_rpc:10, total_time:269.5ms}}, tikv_task:{proc max:50ms, min:0s, avg: 20ms, p80:50ms, p95:50ms, iters:18, tasks:10}, scan_detail: {total_process_keys: 421, total_process_keys_size: 32130, total_keys: 5645, get_snapshot_time: 2.03ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 201.7ms, total_suspend_time: 233.5µs, total_wait_time: 2.18ms, total_kv_read_wall_time: 120ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
        │ └─IndexRangeScan_42	45115.02	421	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:50ms, min:0s, avg: 20ms, p80:50ms, p95:50ms, iters:18, tasks:10}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
        └─TableRowIDScan_43(Probe)	30558.10	421	cop[tikv]	table:d	total_time:21.4ms, total_open:0s, total_close:14µs, loops:8, cop_task: {num: 193, max: 2.36ms, min: 0s, avg: 315.1µs, p95: 2.08ms, max_proc_keys: 7, p95_proc_keys: 5, tot_proc: 18.1ms, tot_wait: 108.2ms, copr_cache: disabled, build_task_duration: 424.7µs, max_distsql_concurrency: 1, max_extra_concurrency: 6, store_batch_num: 147, store_batch_fallback_num: 3}, fetch_resp_duration: 20.7ms, rpc_info:{Cop:{num_rpc:46, total_time:60.4ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:193, tasks:193}, scan_detail: {total_process_keys: 421, total_process_keys_size: 251544, total_keys: 421, get_snapshot_time: 106.2ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.1ms, total_wait_time: 108.2ms}	keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(DISTINCT(d.smart_id)) AS `metric__c_0197`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__c_0198`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__c_0199`,
  COUNT(DISTINCT(d.true_ip)) AS `metric__c_0200`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__c_0201`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__c_0202`,
  COUNT(DISTINCT(d.agent_os)) AS `metric__c_0203`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.smart_id END) AS `metric__c_0260`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0260`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.exact_id END) AS `metric__c_0261`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0261`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.input_ip END) AS `metric__c_0262`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0262`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.smart_id END) AS `metric__c_0269`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0269`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.exact_id END) AS `metric__c_0270`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0270`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.input_ip END) AS `metric__c_0271`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0271`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.smart_id END) AS `metric__c_0278`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0278`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.exact_id END) AS `metric__c_0279`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0279`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.input_ip END) AS `metric__c_0280`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0280`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.smart_id END) AS `metric__c_0287`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0287`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.exact_id END) AS `metric__c_0288`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0288`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.input_ip END) AS `metric__c_0289`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0289`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0333`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0333`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0334`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0334`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0335`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0335`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0336`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0336`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0345`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0345`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0346`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0346`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0347`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0347`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0348`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0348`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0357`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0357`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0358`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0358`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0359`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0359`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0360`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0360`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0369`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0369`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0370`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0370`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0371`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0371`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0372`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0372`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0381`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0381`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0382`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0382`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0383`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0383`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0384`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0384`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0393`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0393`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0394`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0394`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0395`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0395`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0396`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0396`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1774726640017
  AND d.jms_timestamp >= '2026-03-28 12:37:20.017000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  5247719989330882
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=112.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_10	0.80	1	root		time:74.7ms, open:93.4µs, close:34.2µs, loops:2, RU:84.64, Concurrency:OFF	Column#106->Column#166, Column#107->Column#167, Column#108->Column#168, Column#109->Column#169, Column#110->Column#170, Column#111->Column#171, Column#112->Column#172, Column#113->Column#173, Column#114->Column#174, Column#115->Column#175, Column#114->Column#176, Column#116->Column#177, Column#114->Column#178, Column#117->Column#179, Column#118->Column#180, Column#119->Column#181, Column#118->Column#182, Column#120->Column#183, Column#118->Column#184, Column#121->Column#185, Column#122->Column#186, Column#123->Column#187, Column#122->Column#188, Column#124->Column#189, Column#122->Column#190, Column#125->Column#191, Column#126->Column#192, Column#127->Column#193, Column#126->Column#194, Column#128->Column#195, Column#126->Column#196, Column#129->Column#197, Column#130->Column#198, Column#131->Column#199, Column#130->Column#200, Column#132->Column#201, Column#133->Column#202, Column#134->Column#203, Column#133->Column#204, Column#135->Column#205, Column#136->Column#206, Column#137->Column#207, Column#136->Column#208, Column#138->Column#209, Column#139->Column#210, Column#140->Column#211, Column#139->Column#212, Column#141->Column#213, Column#142->Column#214, Column#143->Column#215, Column#142->Column#216, Column#144->Column#217, Column#145->Column#218, Column#146->Column#219, Column#145->Column#220, Column#147->Column#221, Column#148->Column#222, Column#149->Column#223, Column#148->Column#224, Column#150->Column#225, Column#151->Column#226, Column#152->Column#227, Column#151->Column#228, Column#153->Column#229, Column#154->Column#230, Column#155->Column#231, Column#154->Column#232, Column#156->Column#233, Column#157->Column#234, Column#158->Column#235, Column#157->Column#236, Column#159->Column#237, Column#160->Column#238, Column#161->Column#239, Column#160->Column#240, Column#162->Column#241, Column#163->Column#242, Column#164->Column#243, Column#163->Column#244	327.4 KB	N/A
└─Selection_12	0.80	1	root		time:74.7ms, open:89.5µs, close:32.4µs, loops:2	gt(Column#165, ?)	414.7 KB	N/A
  └─HashAgg_16	1.00	1	root		time:74.6ms, open:83µs, close:31.5µs, loops:3	funcs:count(distinct Column#263)->Column#106, funcs:count(distinct Column#264)->Column#107, funcs:count(distinct Column#265)->Column#108, funcs:count(distinct Column#266)->Column#109, funcs:count(distinct Column#267)->Column#110, funcs:count(distinct Column#268)->Column#111, funcs:count(distinct Column#269)->Column#112, funcs:count(distinct Column#270)->Column#113, funcs:sum(Column#271)->Column#114, funcs:count(distinct Column#272)->Column#115, funcs:count(distinct Column#273)->Column#116, funcs:count(distinct Column#274)->Column#117, funcs:sum(Column#275)->Column#118, funcs:count(distinct Column#276)->Column#119, funcs:count(distinct Column#277)->Column#120, funcs:count(distinct Column#278)->Column#121, funcs:sum(Column#279)->Column#122, funcs:count(distinct Column#280)->Column#123, funcs:count(distinct Column#281)->Column#124, funcs:count(distinct Column#282)->Column#125, funcs:sum(Column#283)->Column#126, funcs:count(distinct Column#284)->Column#127, funcs:count(distinct Column#285)->Column#128, funcs:min(Column#286)->Column#129, funcs:sum(Column#287)->Column#130, funcs:max(Column#288)->Column#131, funcs:min(Column#289)->Column#132, funcs:sum(Column#290)->Column#133, funcs:max(Column#291)->Column#134, funcs:min(Column#292)->Column#135, funcs:sum(Column#293)->Column#136, funcs:max(Column#294)->Column#137, funcs:min(Column#295)->Column#138, funcs:sum(Column#296)->Column#139, funcs:max(Column#297)->Column#140, funcs:min(Column#298)->Column#141, funcs:sum(Column#299)->Column#142, funcs:max(Column#300)->Column#143, funcs:min(Column#301)->Column#144, funcs:sum(Column#302)->Column#145, funcs:max(Column#303)->Column#146, funcs:min(Column#304)->Column#147, funcs:sum(Column#305)->Column#148, funcs:max(Column#306)->Column#149, funcs:min(Column#307)->Column#150, funcs:sum(Column#308)->Column#151, funcs:max(Column#309)->Column#152, funcs:min(Column#310)->Column#153, funcs:sum(Column#311)->Column#154, funcs:max(Column#312)->Column#155, funcs:min(Column#313)->Column#156, funcs:sum(Column#314)->Column#157, funcs:max(Column#315)->Column#158, funcs:min(Column#316)->Column#159, funcs:sum(Column#317)->Column#160, funcs:max(Column#318)->Column#161, funcs:min(Column#319)->Column#162, funcs:sum(Column#320)->Column#163, funcs:max(Column#321)->Column#164, funcs:count(?)->Column#165	589.5 KB	0 Bytes
    └─Projection_65	30558.10	421	root		time:73.5ms, open:68.6µs, close:30.6µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#263, intuit_risk.deviceprofile_fact.exact_id->Column#264, intuit_risk.deviceprofile_fact.input_ip->Column#265, intuit_risk.deviceprofile_fact.true_ip->Column#266, intuit_risk.deviceprofile_fact.proxy_ip->Column#267, intuit_risk.deviceprofile_fact.agent_type->Column#268, intuit_risk.deviceprofile_fact.agent_os->Column#269, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#270, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#271, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#272, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#273, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#274, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#275, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#276, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#277, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#278, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#279, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#280, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#281, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#282, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#283, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#284, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#285, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#286, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#287, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#288, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#289, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#290, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#291, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#292, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#293, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#294, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#295, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#296, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#297, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#298, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#299, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#300, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#301, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#302, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#303, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#304, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#305, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#306, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#307, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#308, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#309, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#310, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#311, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#312, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#313, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#314, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#315, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#316, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#317, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#318, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#319, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#320, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#321	1.19 MB	N/A
      └─IndexHashJoin_26	30558.10	421	root		time:72.4ms, open:67.5µs, close:8.4µs, loops:3, inner:{total:126ms, concurrency:5, task:2, construct:3.07ms, fetch:122.5ms, build:636.8µs, join:446.2µs}	inner join, inner:IndexLookUp_41, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	999.2 KB	N/A
        ├─IndexReader_37(Build)	17275.51	4362	root	partition:p20260401,p20260501,p20260601,pmax	time:6.63ms, open:66µs, close:5.67µs, loops:7, cop_task: {num: 10, max: 2.01ms, min: 602.5µs, avg: 1.17ms, p95: 2.01ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 3.98ms, tot_wait: 332.8µs, copr_cache: disabled, build_task_duration: 23.2µs, max_distsql_concurrency: 4}, fetch_resp_duration: 6.25ms, rpc_info:{Cop:{num_rpc:10, total_time:11.6ms}}	index:Selection_36	121.3 KB	N/A
        │ └─Selection_36	17275.51	4362	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:38, tasks:10}, scan_detail: {total_process_keys: 6630, total_process_keys_size: 854810, total_keys: 6640, get_snapshot_time: 137.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.98ms, total_suspend_time: 4.34µs, total_wait_time: 332.8µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        │   └─IndexRangeScan_35	23409.44	6630	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:38, tasks:10}	range:[? ?,? +inf], keep order:false	N/A	N/A
        └─IndexLookUp_41(Probe)	30558.10	421	root	partition:p20260401,p20260501,p20260601,pmax	total_time:121ms, total_open:6.9ms, total_close:14.4µs, loops:4, index_task: {total_time: 107.6ms, fetch_handle: 107.6ms, build: 6.87µs, wait: 13.8µs}, table_task: {total_time: 10.7ms, num: 4, concurrency: 5}, next: {wait_index: 103.2ms, wait_table_lookup_build: 784.4µs, wait_table_lookup_resp: 9.87ms}		1.71 MB	N/A
          ├─Selection_40(Build)	30558.10	421	cop[tikv]		total_time:107.7ms, total_open:0s, total_close:0s, loops:16, cop_task: {num: 10, max: 56.9ms, min: 3.55ms, avg: 15.4ms, p95: 56.9ms, max_proc_keys: 132, p95_proc_keys: 132, tot_proc: 112.8ms, tot_wait: 299.9µs, copr_cache: disabled, build_task_duration: 1.98ms, max_distsql_concurrency: 2}, fetch_resp_duration: 107.4ms, rpc_info:{Cop:{num_rpc:10, total_time:153.7ms}}, tikv_task:{proc max:50ms, min:0s, avg: 11ms, p80:40ms, p95:50ms, iters:18, tasks:10}, scan_detail: {total_process_keys: 421, total_process_keys_size: 32130, total_keys: 5645, get_snapshot_time: 145.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 112.8ms, total_suspend_time: 84.2µs, total_wait_time: 299.9µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │ └─IndexRangeScan_38	45115.02	421	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:50ms, min:0s, avg: 11ms, p80:40ms, p95:50ms, iters:18, tasks:10}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
          └─TableRowIDScan_39(Probe)	30558.10	421	cop[tikv]	table:d	total_time:9.8ms, total_open:0s, total_close:20.1µs, loops:8, cop_task: {num: 193, max: 921.6µs, min: 0s, avg: 120.7µs, p95: 745.2µs, max_proc_keys: 7, p95_proc_keys: 5, tot_proc: 5.25ms, tot_wait: 3.13ms, copr_cache: disabled, build_task_duration: 458.9µs, max_distsql_concurrency: 1, max_extra_concurrency: 6, store_batch_num: 148, store_batch_fallback_num: 2}, fetch_resp_duration: 9.07ms, rpc_info:{Cop:{num_rpc:45, total_time:22.8ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:193, tasks:193}, scan_detail: {total_process_keys: 421, total_process_keys_size: 251544, total_keys: 421, get_snapshot_time: 1.34ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.25ms, total_wait_time: 3.13ms}	keep order:false	N/A	N/A
```

### 14. group_c_bundle_022

- Filter/window: `d.exact_id = %s` / `180d`
- Chosen event: `INV0004166099` kind=`normal` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 2712.4 ms | ok |
| `optimized_default` | `{}` | 111.0 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 110.4 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 109.8 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 112.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 104.1 ms | ok |

#### Original SQL

```sql
SELECT
  SUM(`metric__c_0031`) AS `metric__c_0031`,
  SUM(`metric__c_0032`) AS `metric__c_0032`,
  MIN(`metric__c_0033`) AS `metric__c_0033`,
  MAX(`metric__c_0034`) AS `metric__c_0034`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_022' AND x.template_id = 'c_0035' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09' UNION ALL SELECT CAST(p.merchant_account_number AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE d.exact_id = %s AND p.merchant_account_number IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')) u) AS `metric__c_0035`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_022' AND x.template_id = 'c_0036' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09' UNION ALL SELECT CAST(p.card_holder_number_sha512 AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE d.exact_id = %s AND p.card_holder_number_sha512 IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')) u) AS `metric__c_0036`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_022' AND x.template_id = 'c_0037' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09' UNION ALL SELECT CAST(p.card_type AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE d.exact_id = %s AND p.card_type IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')) u) AS `metric__c_0037`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_022' AND x.template_id = 'c_0038' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09' UNION ALL SELECT CAST(p.entry_method AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE d.exact_id = %s AND p.entry_method IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')) u) AS `metric__c_0038`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_022' AND x.template_id = 'c_0039' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09' UNION ALL SELECT CAST(p.mt_gateway AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE d.exact_id = %s AND p.mt_gateway IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')) u) AS `metric__c_0039`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_c_180d_daily_distinct` x WHERE x.bundle_id = 'group_c_bundle_022' AND x.template_id = 'c_0040' AND x.key1 = %s AND x.key2 = '' AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09' UNION ALL SELECT CAST(p.check_bank_routing_number AS CHAR(256)) AS distinct_value FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id WHERE d.exact_id = %s AND p.check_bank_routing_number IS NOT NULL AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')) u) AS `metric__c_0040`
FROM (
  SELECT `metric__c_0031`, `metric__c_0032`, `metric__c_0033`, `metric__c_0034`
  FROM `group_c_180d_daily_rollup` r
  WHERE r.bundle_id = 'group_c_bundle_022'
    AND r.key1 = %s AND r.key2 = ''
    AND r.p_event_day > '2025-10-09' AND r.d_event_day > '2025-10-09'
  UNION ALL
  SELECT COUNT(*) AS `metric__c_0031`, SUM(p.amount) AS `metric__c_0032`, MIN(p.amount) AS `metric__c_0033`, MAX(p.amount) AS `metric__c_0034`
  FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id
  WHERE d.exact_id = %s AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')
  GROUP BY d.exact_id
) r;
```

#### Original Params

```json
[
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12"
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=2712.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_828	1.00	1	root		time:66ms, open:31.8µs, close:57.3µs, loops:2, RU:7204.76, Concurrency:OFF	Column#1496, Column#1497, Column#1498, Column#1499, ?->Column#1658, ?->Column#1817, ?->Column#1974, ?->Column#2131, ?->Column#2288, ?->Column#2449	11.1 KB	N/A
└─HashAgg_832	1.00	1	root		time:66ms, open:30µs, close:55.6µs, loops:2, partial_worker:{wall_time:65.925448ms, concurrency:4, task_num:6, tot_wait:259.077413ms, tot_exec:536.779µs, tot_time:263.587023ms, max:65.900179ms, p95:65.900179ms}, final_worker:{wall_time:65.951473ms, concurrency:4, task_num:7, tot_wait:68.578µs, tot_exec:3.154µs, tot_time:263.705576ms, max:65.934846ms, p95:65.934846ms}	funcs:sum(Column#124)->Column#1496, funcs:sum(Column#125)->Column#1497, funcs:min(Column#126)->Column#1498, funcs:max(Column#127)->Column#1499	901.3 KB	0 Bytes
  └─Union_836	4969.72	4793	root		time:65.9ms, open:938ns, close:54µs, loops:7		N/A	N/A
    ├─Projection_838	4938.02	4792	root		time:64.4ms, open:18.3µs, close:20.4µs, loops:6, Concurrency:5	intuit_risk.group_c_180d_daily_rollup.metric__c_0031->Column#124, cast(intuit_risk.group_c_180d_daily_rollup.metric__c_0032, decimal(41,6) BINARY)->Column#125, intuit_risk.group_c_180d_daily_rollup.metric__c_0033->Column#126, intuit_risk.group_c_180d_daily_rollup.metric__c_0034->Column#127	1.31 MB	N/A
    │ └─IndexLookUp_843	4938.02	4792	root		time:64.5ms, open:16.3µs, close:6.17µs, loops:6, index_task: {total_time: 7.01ms, fetch_handle: 7.01ms, build: 1.77µs, wait: 1.86µs}, table_task: {total_time: 55.4ms, num: 1, concurrency: 5}, next: {wait_index: 8.14ms, wait_table_lookup_build: 11.7ms, wait_table_lookup_resp: 43.7ms}		2.06 MB	N/A
    │   ├─Selection_842(Build)	4938.02	4792	cop[tikv]		time:6.87ms, open:0s, close:0s, loops:7, cop_task: {num: 1, max: 6.84ms, proc_keys: 4792, tot_proc: 4.35ms, tot_wait: 640.4µs, copr_cache: disabled, build_task_duration: 1.06ms, max_distsql_concurrency: 1}, fetch_resp_duration: 6.86ms, rpc_info:{Cop:{num_rpc:1, total_time:6.83ms}}, tikv_task:{time:0s, loops:9}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 1059032, total_keys: 4793, get_snapshot_time: 629.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.35ms, total_suspend_time: 10.2µs, total_wait_time: 640.4µs}	gt(intuit_risk.group_c_180d_daily_rollup.d_event_day, ?)	N/A	N/A
    │   │ └─IndexRangeScan_840	4945.65	4792	cop[tikv]	table:r, index:PRIMARY(bundle_id, key1, key2, p_event_day, d_event_day)	tikv_task:{time:0s, loops:9}	range:(? ? ? ?,? ? ? +inf], keep order:false	N/A	N/A
    │   └─TableRowIDScan_841(Probe)	4938.02	4792	cop[tikv]	table:r	time:43.6ms, open:0s, close:2.65µs, loops:6, cop_task: {num: 84, max: 25.9ms, min: 0s, avg: 5.19ms, p95: 12.6ms, max_proc_keys: 270, p95_proc_keys: 165, tot_proc: 368.9ms, tot_wait: 45.4ms, copr_cache: disabled, build_task_duration: 10.4ms, max_distsql_concurrency: 15, max_extra_concurrency: 1, store_batch_num: 15}, fetch_resp_duration: 42ms, rpc_info:{Cop:{num_rpc:83, total_time:459.5ms}, rpc_errors:{bucket_version_not_match:14}}, backoff{regionMiss: 28ms}, tikv_task:{proc max:30ms, min:0s, avg: 3.33ms, p80:10ms, p95:10ms, iters:160, tasks:84}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 987152, total_keys: 4792, get_snapshot_time: 41.2ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 368.9ms, total_suspend_time: 2.6ms, total_wait_time: 45.4ms, total_kv_read_wall_time: 280ms}	keep order:false	N/A	N/A
    └─Projection_844	31.70	1	root		time:65.9ms, open:178.5µs, close:32.9µs, loops:2, Concurrency:OFF	cast(Column#120, decimal(38,6) BINARY)->Column#124, cast(Column#121, decimal(41,6) BINARY)->Column#125, cast(Column#122, decimal(38,6) BINARY)->Column#126, cast(Column#123, decimal(38,6) BINARY)->Column#127	8.71 KB	N/A
      └─HashAgg_848	31.70	1	root		time:65.9ms, open:176µs, close:31.6µs, loops:2, partial_worker:{wall_time:65.63248ms, concurrency:4, task_num:4, tot_wait:179.036823ms, tot_exec:32.199µs, tot_time:262.259264ms, max:65.565597ms, p95:65.565597ms}, final_worker:{wall_time:65.676726ms, concurrency:4, task_num:7, tot_wait:6.654µs, tot_exec:2.495µs, tot_time:262.391844ms, max:65.611814ms, p95:65.611814ms}	group by:intuit_risk.deviceprofile_fact.exact_id, funcs:count(?)->Column#120, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#121, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#122, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#123	24.5 KB	0 Bytes
        └─Projection_856	33729.75	6	root		time:65.7ms, open:149.2µs, close:28.9µs, loops:5, Concurrency:5	intuit_risk.pmt_txn_fact.amount, intuit_risk.deviceprofile_fact.exact_id	20.2 KB	N/A
          └─IndexHashJoin_865	33729.75	6	root		time:65.7ms, open:147.9µs, close:8.5µs, loops:5, inner:{total:149.9ms, concurrency:5, task:4, construct:13.9ms, fetch:128ms, build:2.82ms, join:8.03ms}	inner join, inner:IndexReader_879, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.35 MB	N/A
            ├─IndexReader_876(Build)	21567.79	21121	root	partition:all	time:13.7ms, open:145.7µs, close:6.11µs, loops:23, cop_task: {num: 34, max: 4.61ms, min: 305.8µs, avg: 1.61ms, p95: 4ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 33.6ms, tot_wait: 845.4µs, copr_cache: disabled, build_task_duration: 70.6µs, max_distsql_concurrency: 9}, fetch_resp_duration: 12.7ms, rpc_info:{Cop:{num_rpc:34, total_time:54.5ms}}	index:Selection_875	337.1 KB	N/A
            │ └─Selection_875	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 329.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 33.6ms, total_suspend_time: 53.9µs, total_wait_time: 845.4µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │   └─IndexRangeScan_874	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
            └─IndexReader_879(Probe)	33729.75	5285	root	partition:all	total_time:121.6ms, total_open:72.1ms, total_close:37.9µs, loops:11, cop_task: {num: 172, max: 11.9ms, min: 695.9µs, avg: 2.91ms, p95: 8.93ms, max_proc_keys: 151, p95_proc_keys: 115, tot_proc: 188.5ms, tot_wait: 7.29ms, copr_cache: disabled, build_task_duration: 13.4ms, max_distsql_concurrency: 15}, fetch_resp_duration: 46.2ms, rpc_info:{Cop:{num_rpc:172, total_time:497.1ms}}	index:Selection_878	10.3 KB	N/A
              └─Selection_878	33729.75	5285	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 930.2µs, p80:0s, p95:10ms, iters:242, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.41ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 188.5ms, total_suspend_time: 361.2µs, total_wait_time: 7.29ms, total_kv_read_wall_time: 160ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
                └─IndexRangeScan_877	45706.03	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 930.2µs, p80:0s, p95:10ms, iters:242, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_237	N/A	0	root			Output: ScalarQueryCol#1657	N/A	N/A
└─MaxOneRow_135	1.00	1	root		time:530.8ms, open:10.8µs, close:25.3µs, loops:1		N/A	N/A
  └─HashAgg_140	1.00	1	root		time:530.8ms, open:10.1µs, close:24.9µs, loops:2	funcs:count(distinct Column#1614)->Column#1615	337.0 KB	0 Bytes
    └─Union_144	33791.70	5291	root		time:529.6ms, open:787ns, close:24.3µs, loops:11		N/A	N/A
      ├─Projection_146	61.95	5285	root		time:15.5ms, open:976.9µs, close:9.19µs, loops:7, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1614	148.0 KB	N/A
      │ └─IndexReader_150	61.95	5285	root		time:15.2ms, open:969.6µs, close:6.47µs, loops:7, cop_task: {num: 5, max: 4.25ms, min: 1.42ms, avg: 2.95ms, p95: 4.25ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 6.53ms, tot_wait: 1.19ms, copr_cache: disabled, build_task_duration: 922.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 14ms, rpc_info:{Cop:{num_rpc:5, total_time:14.7ms}}	index:Selection_149	450.3 KB	N/A
      │   └─Selection_149	61.95	5285	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:24, tasks:5}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1516795, total_keys: 5290, get_snapshot_time: 1.12ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 6.53ms, total_suspend_time: 12.6µs, total_wait_time: 1.19ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_148	62.05	5285	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:24, tasks:5}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_151	33729.75	6	root		time:530.7ms, open:949.9µs, close:14.5µs, loops:5, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.merchant_account_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1614	30.6 KB	N/A
        └─IndexHashJoin_162	33729.75	6	root		time:530.6ms, open:948.3µs, close:5.22µs, loops:5, inner:{total:1.45s, concurrency:5, task:4, construct:15.8ms, fetch:1.42s, build:3.33ms, join:8.43ms}	inner join, inner:IndexReader_176, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.31 MB	N/A
          ├─IndexReader_173(Build)	21567.79	21121	root	partition:all	time:33.8ms, open:945.3µs, close:2.99µs, loops:23, cop_task: {num: 34, max: 13ms, min: 330.2µs, avg: 3.24ms, p95: 7.77ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 67.2ms, tot_wait: 7.17ms, copr_cache: disabled, build_task_duration: 840.2µs, max_distsql_concurrency: 9}, fetch_resp_duration: 31.2ms, rpc_info:{Cop:{num_rpc:34, total_time:109.8ms}}	index:Selection_172	278.6 KB	N/A
          │ └─Selection_172	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.76ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 6.57ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 67.2ms, total_suspend_time: 155.3µs, total_wait_time: 7.17ms, total_kv_read_wall_time: 60ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_171	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.76ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_176(Probe)	33729.75	5285	root	partition:all	total_time:1.42s, total_open:130.7ms, total_close:46.7µs, loops:11, cop_task: {num: 168, max: 407.3ms, min: 2.12ms, avg: 66.7ms, p95: 217.5ms, max_proc_keys: 155, p95_proc_keys: 117, tot_proc: 9.63s, tot_wait: 446.1ms, copr_cache: disabled, build_task_duration: 53.6ms, max_distsql_concurrency: 15}, fetch_resp_duration: 1.28s, rpc_info:{Cop:{num_rpc:188, total_time:11.2s}, rpc_errors:{bucket_version_not_match:20}}, backoff{regionMiss: 40ms}	index:Selection_175	7.52 KB	N/A
            └─Selection_175	33729.75	5285	cop[tikv]		tikv_task:{proc max:400ms, min:0s, avg: 61.8ms, p80:110ms, p95:210ms, iters:242, tasks:168}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43614, get_snapshot_time: 17.3ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 9.63s, total_suspend_time: 682.3ms, total_wait_time: 446.1ms, total_kv_read_wall_time: 10.4s}	not(isnull(intuit_risk.pmt_txn_fact.merchant_account_number)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_174	45743.67	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:400ms, min:0s, avg: 61.8ms, p80:110ms, p95:210ms, iters:242, tasks:168}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_358	N/A	0	root			Output: ScalarQueryCol#1816	N/A	N/A
└─MaxOneRow_256	1.00	1	root		time:1.42s, open:7.39µs, close:24µs, loops:1		N/A	N/A
  └─HashAgg_261	1.00	1	root		time:1.42s, open:6.84µs, close:23.6µs, loops:2	funcs:count(distinct Column#1773)->Column#1774	514.3 KB	0 Bytes
    └─Union_265	33780.10	3426	root		time:1.42s, open:920ns, close:23.1µs, loops:8		N/A	N/A
      ├─Projection_267	50.35	3423	root		time:9.99ms, open:979.1µs, close:8.4µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1773	212.5 KB	N/A
      │ └─IndexReader_271	50.35	3423	root		time:9.71ms, open:974.5µs, close:5.19µs, loops:5, cop_task: {num: 4, max: 2.95ms, min: 1.17ms, avg: 2.19ms, p95: 2.95ms, max_proc_keys: 1727, p95_proc_keys: 1727, tot_proc: 5.25ms, tot_wait: 625.9µs, copr_cache: disabled, build_task_duration: 932.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 8.44ms, rpc_info:{Cop:{num_rpc:4, total_time:8.71ms}}	index:Selection_270	468.9 KB	N/A
      │   └─Selection_270	50.35	3423	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3423, total_process_keys_size: 1331547, total_keys: 3427, get_snapshot_time: 560.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.25ms, total_suspend_time: 7.71µs, total_wait_time: 625.9µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_269	50.43	3423	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_272	33729.75	3	root		time:1.42s, open:114.5µs, close:14.1µs, loops:4, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.card_holder_number_sha512, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1773	77.8 KB	N/A
        └─IndexHashJoin_283	33729.75	3	root		time:1.42s, open:113.3µs, close:5.25µs, loops:4, inner:{total:4.24s, concurrency:5, task:4, construct:16.2ms, fetch:4.22s, build:3.4ms, join:5.78ms}	inner join, inner:IndexReader_297, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.21 MB	N/A
          ├─IndexReader_294(Build)	21567.79	21121	root	partition:all	time:17.9ms, open:111.7µs, close:2.96µs, loops:23, cop_task: {num: 34, max: 6.37ms, min: 304.2µs, avg: 2.02ms, p95: 5.6ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 46.1ms, tot_wait: 1.1ms, copr_cache: disabled, build_task_duration: 53.4µs, max_distsql_concurrency: 9}, fetch_resp_duration: 16ms, rpc_info:{Cop:{num_rpc:34, total_time:68.3ms}}	index:Selection_293	251.7 KB	N/A
          │ └─Selection_293	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 481.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 46.1ms, total_suspend_time: 115µs, total_wait_time: 1.1ms, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_292	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_297(Probe)	33729.75	3423	root	partition:all	total_time:4.21s, total_open:96.6ms, total_close:43.9µs, loops:10, cop_task: {num: 172, max: 1.36s, min: 1.05ms, avg: 34ms, p95: 32.9ms, max_proc_keys: 157, p95_proc_keys: 116, tot_proc: 1.51s, tot_wait: 5.1ms, copr_cache: disabled, build_task_duration: 16.4ms, max_distsql_concurrency: 15}, fetch_resp_duration: 4.11s, rpc_info:{Cop:{num_rpc:172, total_time:5.84s}}	index:Selection_296	9.70 KB	N/A
            └─Selection_296	33729.75	3423	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 8.78ms, p80:10ms, p95:30ms, iters:241, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1644144, total_keys: 39881, get_snapshot_time: 2.2ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.51s, total_suspend_time: 3.16ms, total_wait_time: 5.1ms, total_kv_read_wall_time: 1.35s}	not(isnull(intuit_risk.pmt_txn_fact.card_holder_number_sha512)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_295	65559.91	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:50ms, min:0s, avg: 8.72ms, p80:10ms, p95:30ms, iters:241, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_473	N/A	0	root			Output: ScalarQueryCol#1973	N/A	N/A
└─MaxOneRow_377	1.00	1	root		time:140ms, open:10.8µs, close:26µs, loops:1		N/A	N/A
  └─HashAgg_382	1.00	1	root		time:140ms, open:10.2µs, close:25.4µs, loops:2	funcs:count(distinct Column#1932)->Column#1933	17.2 KB	0 Bytes
    └─Union_386	33783.04	3604	root		time:139.6ms, open:883ns, close:24.7µs, loops:9		N/A	N/A
      ├─Projection_388	53.28	3599	root		time:10.4ms, open:657.7µs, close:9.77µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1932	133.4 KB	N/A
      │ └─IndexReader_392	53.28	3599	root		time:10.3ms, open:652.5µs, close:6.48µs, loops:5, cop_task: {num: 4, max: 3.5ms, min: 1.27ms, avg: 2.4ms, p95: 3.5ms, max_proc_keys: 1903, p95_proc_keys: 1903, tot_proc: 4.09ms, tot_wait: 506.4µs, copr_cache: disabled, build_task_duration: 605.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 9.4ms, rpc_info:{Cop:{num_rpc:4, total_time:9.58ms}}	index:Selection_391	321.0 KB	N/A
      │   └─Selection_391	53.28	3599	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3599, total_process_keys_size: 914146, total_keys: 3603, get_snapshot_time: 446.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.09ms, total_suspend_time: 3.22µs, total_wait_time: 506.4µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_390	53.37	3599	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_393	33729.75	5	root		time:139.9ms, open:141.3µs, close:14.2µs, loops:5, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.card_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1932	21.8 KB	N/A
        └─IndexHashJoin_404	33729.75	5	root		time:139.9ms, open:140.1µs, close:5.58µs, loops:5, inner:{total:337.3ms, concurrency:5, task:4, construct:15.9ms, fetch:315.2ms, build:3.39ms, join:6.27ms}	inner join, inner:IndexReader_418, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.31 MB	N/A
          ├─IndexReader_415(Build)	21567.79	21121	root	partition:all	time:16.5ms, open:138.3µs, close:3.09µs, loops:23, cop_task: {num: 34, max: 5.83ms, min: 309.6µs, avg: 1.89ms, p95: 5.08ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 40.7ms, tot_wait: 1.19ms, copr_cache: disabled, build_task_duration: 59.8µs, max_distsql_concurrency: 9}, fetch_resp_duration: 14.7ms, rpc_info:{Cop:{num_rpc:34, total_time:64ms}}	index:Selection_414	251.7 KB	N/A
          │ └─Selection_414	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 561.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 40.7ms, total_suspend_time: 110.2µs, total_wait_time: 1.19ms, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_413	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_418(Probe)	33729.75	3871	root	partition:all	total_time:307.1ms, total_open:100.4ms, total_close:42.4µs, loops:10, cop_task: {num: 172, max: 63.3ms, min: 929.2µs, avg: 8.13ms, p95: 22ms, max_proc_keys: 158, p95_proc_keys: 117, tot_proc: 1.04s, tot_wait: 4.96ms, copr_cache: disabled, build_task_duration: 18.8ms, max_distsql_concurrency: 15}, fetch_resp_duration: 202.1ms, rpc_info:{Cop:{num_rpc:172, total_time:1.39s}}	index:Selection_417	8.86 KB	N/A
            └─Selection_417	33729.75	3871	cop[tikv]		tikv_task:{proc max:40ms, min:0s, avg: 5.64ms, p80:10ms, p95:20ms, iters:241, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1667242, total_keys: 41025, get_snapshot_time: 2.1ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.04s, total_suspend_time: 2.34ms, total_wait_time: 4.96ms, total_kv_read_wall_time: 860ms}	not(isnull(intuit_risk.pmt_txn_fact.card_type)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_416	62068.67	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:40ms, min:0s, avg: 5.64ms, p80:10ms, p95:20ms, iters:241, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_588	N/A	0	root			Output: ScalarQueryCol#2130	N/A	N/A
└─MaxOneRow_492	1.00	1	root		time:117.6ms, open:10.7µs, close:32.6µs, loops:1		N/A	N/A
  └─HashAgg_497	1.00	1	root		time:117.5ms, open:10µs, close:32.1µs, loops:2	funcs:count(distinct Column#2089)->Column#2090	12.6 KB	0 Bytes
    └─Union_501	33752.89	728	root		time:117.4ms, open:916ns, close:31.5µs, loops:2		N/A	N/A
      ├─Projection_503	23.14	728	root		time:7.45ms, open:953.2µs, close:7.44µs, loops:2, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2089	95.0 KB	N/A
      │ └─IndexReader_507	23.14	728	root		time:7.4ms, open:944.5µs, close:4.87µs, loops:2, cop_task: {num: 3, max: 4.08ms, min: 870.9µs, avg: 2.11ms, p95: 4.08ms, max_proc_keys: 480, p95_proc_keys: 480, tot_proc: 2.73ms, tot_wait: 449.9µs, copr_cache: disabled, build_task_duration: 898.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 6.31ms, rpc_info:{Cop:{num_rpc:3, total_time:6.3ms}}	index:Selection_506	79.8 KB	N/A
      │   └─Selection_506	23.14	728	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:8, tasks:3}, scan_detail: {total_process_keys: 728, total_process_keys_size: 185640, total_keys: 731, get_snapshot_time: 398.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.73ms, total_suspend_time: 3.56µs, total_wait_time: 449.9µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_505	23.17	728	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:8, tasks:3}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_508	33729.75	0	root		time:117.5ms, open:133.9µs, close:23µs, loops:1, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.entry_method, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2089	6.21 KB	N/A
        └─IndexHashJoin_519	33729.75	0	root		time:117.4ms, open:132.5µs, close:5.53µs, loops:1, inner:{total:275.5ms, concurrency:5, task:4, construct:16.1ms, fetch:257.9ms, build:3.27ms, join:1.57ms}	inner join, inner:IndexReader_533, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.30 MB	N/A
          ├─IndexReader_530(Build)	21567.79	21121	root	partition:all	time:14.8ms, open:130.9µs, close:3.18µs, loops:23, cop_task: {num: 34, max: 5.48ms, min: 316.1µs, avg: 1.7ms, p95: 4.78ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 34.5ms, tot_wait: 976.5µs, copr_cache: disabled, build_task_duration: 57.5µs, max_distsql_concurrency: 9}, fetch_resp_duration: 12.9ms, rpc_info:{Cop:{num_rpc:34, total_time:57.3ms}}	index:Selection_529	251.7 KB	N/A
          │ └─Selection_529	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 406.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 34.5ms, total_suspend_time: 62.6µs, total_wait_time: 976.5µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_528	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_533(Probe)	33729.75	731	root	partition:all	total_time:249.3ms, total_open:100.2ms, total_close:41.8µs, loops:8, cop_task: {num: 172, max: 54.7ms, min: 685.5µs, avg: 4.11ms, p95: 10.7ms, max_proc_keys: 160, p95_proc_keys: 115, tot_proc: 363.1ms, tot_wait: 4.43ms, copr_cache: disabled, build_task_duration: 18.6ms, max_distsql_concurrency: 15}, fetch_resp_duration: 144.8ms, rpc_info:{Cop:{num_rpc:172, total_time:703.9ms}}	index:Selection_532	8.32 KB	N/A
            └─Selection_532	33729.75	731	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 1.92ms, p80:0s, p95:10ms, iters:244, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.69ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 363.1ms, total_suspend_time: 790.2µs, total_wait_time: 4.43ms, total_kv_read_wall_time: 330ms}	not(isnull(intuit_risk.pmt_txn_fact.entry_method)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_531	317192.19	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:50ms, min:0s, avg: 1.92ms, p80:0s, p95:10ms, iters:244, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_703	N/A	0	root			Output: ScalarQueryCol#2287	N/A	N/A
└─MaxOneRow_607	1.00	1	root		time:77ms, open:10.2µs, close:24µs, loops:1		N/A	N/A
  └─HashAgg_612	1.00	1	root		time:77ms, open:9.64µs, close:23.6µs, loops:2	funcs:count(distinct Column#2246)->Column#2247	27.6 KB	0 Bytes
    └─Union_616	33791.76	5106	root		time:76.4ms, open:931ns, close:23µs, loops:11		N/A	N/A
      ├─Projection_618	62.01	5100	root		time:11.2ms, open:956.3µs, close:8.82µs, loops:7, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2246	148.4 KB	N/A
      │ └─IndexReader_622	62.01	5100	root		time:11ms, open:947µs, close:6.21µs, loops:7, cop_task: {num: 5, max: 3.13ms, min: 1.01ms, avg: 2.07ms, p95: 3.13ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 6.3ms, tot_wait: 530.6µs, copr_cache: disabled, build_task_duration: 901.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 9.74ms, rpc_info:{Cop:{num_rpc:5, total_time:10.3ms}}	index:Selection_621	420.5 KB	N/A
      │   └─Selection_621	62.01	5100	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:24, tasks:5}, scan_detail: {total_process_keys: 5100, total_process_keys_size: 1414856, total_keys: 5105, get_snapshot_time: 444.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 6.3ms, total_suspend_time: 12.1µs, total_wait_time: 530.6µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_620	62.11	5100	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:24, tasks:5}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_623	33729.75	6	root		time:76.9ms, open:122.9µs, close:13.8µs, loops:5, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.mt_gateway, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2246	31.8 KB	N/A
        └─IndexHashJoin_634	33729.75	6	root		time:76.8ms, open:121.5µs, close:5.13µs, loops:5, inner:{total:185.5ms, concurrency:5, task:4, construct:15.9ms, fetch:161.1ms, build:3.41ms, join:8.44ms}	inner join, inner:IndexReader_648, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.32 MB	N/A
          ├─IndexReader_645(Build)	21567.79	21121	root	partition:all	time:14.4ms, open:119.7µs, close:3.06µs, loops:23, cop_task: {num: 34, max: 4.97ms, min: 277.1µs, avg: 1.62ms, p95: 3.93ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 32.9ms, tot_wait: 880.8µs, copr_cache: disabled, build_task_duration: 54.2µs, max_distsql_concurrency: 9}, fetch_resp_duration: 12.2ms, rpc_info:{Cop:{num_rpc:34, total_time:54.8ms}}	index:Selection_644	251.7 KB	N/A
          │ └─Selection_644	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 380.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 32.9ms, total_suspend_time: 61.3µs, total_wait_time: 880.8µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_643	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_648(Probe)	33729.75	5285	root	partition:all	total_time:152.7ms, total_open:100.2ms, total_close:40.2µs, loops:11, cop_task: {num: 172, max: 11.8ms, min: 723.2µs, avg: 3.17ms, p95: 8.48ms, max_proc_keys: 156, p95_proc_keys: 117, tot_proc: 226.8ms, tot_wait: 4.4ms, copr_cache: disabled, build_task_duration: 18.1ms, max_distsql_concurrency: 15}, fetch_resp_duration: 48.6ms, rpc_info:{Cop:{num_rpc:172, total_time:541.1ms}}	index:Selection_647	9.67 KB	N/A
            └─Selection_647	33729.75	5285	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 930.2µs, p80:0s, p95:10ms, iters:242, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.64ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 226.8ms, total_suspend_time: 518.7µs, total_wait_time: 4.4ms, total_kv_read_wall_time: 160ms}	not(isnull(intuit_risk.pmt_txn_fact.mt_gateway)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_646	45743.81	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 930.2µs, p80:0s, p95:10ms, iters:242, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_824	N/A	0	root			Output: ScalarQueryCol#2448	N/A	N/A
└─MaxOneRow_722	1.00	1	root		time:71.8ms, open:12.8µs, close:25.4µs, loops:1		N/A	N/A
  └─HashAgg_727	1.00	1	root		time:71.8ms, open:12µs, close:24.8µs, loops:2	funcs:count(distinct Column#2403)->Column#2404	74.5 KB	0 Bytes
    └─Union_731	33761.35	1415	root		time:71.5ms, open:872ns, close:24.3µs, loops:4		N/A	N/A
      ├─Projection_733	31.60	1414	root		time:8.08ms, open:733µs, close:8.46µs, loops:3, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2403	139.9 KB	N/A
      │ └─IndexReader_737	31.60	1414	root		time:8.02ms, open:726.7µs, close:5.75µs, loops:3, cop_task: {num: 3, max: 4.48ms, min: 1.09ms, avg: 2.39ms, p95: 4.48ms, max_proc_keys: 710, p95_proc_keys: 710, tot_proc: 3.62ms, tot_wait: 816µs, copr_cache: disabled, build_task_duration: 682.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 7.19ms, rpc_info:{Cop:{num_rpc:3, total_time:7.14ms}}	index:Selection_736	141.9 KB	N/A
      │   └─Selection_736	31.60	1414	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 3.33ms, p80:10ms, p95:10ms, iters:12, tasks:3}, scan_detail: {total_process_keys: 1414, total_process_keys_size: 383194, total_keys: 1417, get_snapshot_time: 776µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.62ms, total_suspend_time: 2.89µs, total_wait_time: 816µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_735	31.65	1414	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 3.33ms, p80:10ms, p95:10ms, iters:12, tasks:3}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_738	33729.75	1	root		time:71.8ms, open:116.6µs, close:15.2µs, loops:2, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.check_bank_routing_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2403	12.2 KB	N/A
        └─IndexHashJoin_749	33729.75	1	root		time:71.7ms, open:115.6µs, close:5.09µs, loops:2, inner:{total:162.1ms, concurrency:5, task:4, construct:14ms, fetch:145.4ms, build:2.91ms, join:2.63ms}	inner join, inner:IndexReader_763, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.32 MB	N/A
          ├─IndexReader_760(Build)	21567.79	21121	root	partition:all	time:13.9ms, open:113.9µs, close:3.01µs, loops:23, cop_task: {num: 34, max: 4.65ms, min: 329.1µs, avg: 1.62ms, p95: 3.93ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 32.7ms, tot_wait: 876.1µs, copr_cache: disabled, build_task_duration: 57.1µs, max_distsql_concurrency: 9}, fetch_resp_duration: 12.9ms, rpc_info:{Cop:{num_rpc:34, total_time:54.8ms}}	index:Selection_759	337.1 KB	N/A
          │ └─Selection_759	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.18ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 356.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 32.7ms, total_suspend_time: 56.3µs, total_wait_time: 876.1µs, total_kv_read_wall_time: 30ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_758	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 882.4µs, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_763(Probe)	33729.75	1414	root	partition:all	total_time:139.2ms, total_open:74.6ms, total_close:40.2µs, loops:8, cop_task: {num: 172, max: 20ms, min: 648.5µs, avg: 2.98ms, p95: 8.4ms, max_proc_keys: 154, p95_proc_keys: 115, tot_proc: 204.9ms, tot_wait: 4.32ms, copr_cache: disabled, build_task_duration: 13.8ms, max_distsql_concurrency: 15}, fetch_resp_duration: 61.5ms, rpc_info:{Cop:{num_rpc:172, total_time:508.8ms}}	index:Selection_762	8.33 KB	N/A
            └─Selection_762	33729.75	1414	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.22ms, p80:0s, p95:10ms, iters:242, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.5ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 204.9ms, total_suspend_time: 411µs, total_wait_time: 4.32ms, total_kv_read_wall_time: 210ms}	not(isnull(intuit_risk.pmt_txn_fact.check_bank_routing_number)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_761	130475.89	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1.22ms, p80:0s, p95:10ms, iters:242, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
WITH raw_boundary AS (
  SELECT
    p.amount AS raw_p_amount,
    p.merchant_account_number AS `raw_distinct_0`,
    p.card_holder_number_sha512 AS `raw_distinct_1`,
    p.card_type AS `raw_distinct_2`,
    p.entry_method AS `raw_distinct_3`,
    p.mt_gateway AS `raw_distinct_4`,
    p.check_bank_routing_number AS `raw_distinct_5`
  FROM pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id
  WHERE d.exact_id = %s AND p.event_date IS NOT NULL AND d.jms_timestamp IS NOT NULL AND p.event_date >= 1760045003248 AND d.jms_timestamp >= '2025-10-09 14:23:23.248000' AND (p.event_date < 1760079600000 OR d.jms_timestamp < '2025-10-10 00:00:00.000000')
), rollup_rows AS (
  SELECT `metric__c_0031`, `metric__c_0032`, `metric__c_0033`, `metric__c_0034`
  FROM `group_c_180d_daily_rollup` r
  WHERE r.bundle_id = 'group_c_bundle_022'
    AND r.key1 = %s AND r.key2 = ''
    AND r.p_event_day > '2025-10-09' AND r.d_event_day > '2025-10-09'
  UNION ALL
  SELECT COUNT(*) AS `metric__c_0031`, SUM(raw_p_amount) AS `metric__c_0032`, MIN(raw_p_amount) AS `metric__c_0033`, MAX(raw_p_amount) AS `metric__c_0034`
  FROM raw_boundary
  HAVING COUNT(*) > 0
), rollup_final AS (
  SELECT
    SUM(`metric__c_0031`) AS `metric__c_0031`,
    SUM(`metric__c_0032`) AS `metric__c_0032`,
    MIN(`metric__c_0033`) AS `metric__c_0033`,
    MAX(`metric__c_0034`) AS `metric__c_0034`
  FROM rollup_rows
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_c_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_c_bundle_022'
    AND x.template_id IN ('c_0035', 'c_0036', 'c_0037', 'c_0038', 'c_0039', 'c_0040')
    AND x.key1 = %s AND x.key2 = ''
    AND x.p_event_day > '2025-10-09' AND x.d_event_day > '2025-10-09'
  UNION ALL
  SELECT 'c_0035' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'c_0036' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'c_0037' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'c_0038' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION ALL
  SELECT 'c_0039' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
  UNION ALL
  SELECT 'c_0040' AS template_id, CAST(`raw_distinct_5` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_5` IS NOT NULL
), distinct_counts AS (
  SELECT
    COUNT(DISTINCT CASE WHEN template_id = 'c_0035' THEN distinct_value END) AS `metric__c_0035`,
    COUNT(DISTINCT CASE WHEN template_id = 'c_0036' THEN distinct_value END) AS `metric__c_0036`,
    COUNT(DISTINCT CASE WHEN template_id = 'c_0037' THEN distinct_value END) AS `metric__c_0037`,
    COUNT(DISTINCT CASE WHEN template_id = 'c_0038' THEN distinct_value END) AS `metric__c_0038`,
    COUNT(DISTINCT CASE WHEN template_id = 'c_0039' THEN distinct_value END) AS `metric__c_0039`,
    COUNT(DISTINCT CASE WHEN template_id = 'c_0040' THEN distinct_value END) AS `metric__c_0040`
  FROM distinct_values
)
SELECT
  rollup_final.`metric__c_0031`,
  rollup_final.`metric__c_0032`,
  rollup_final.`metric__c_0033`,
  rollup_final.`metric__c_0034`,
  distinct_counts.`metric__c_0035`,
  distinct_counts.`metric__c_0036`,
  distinct_counts.`metric__c_0037`,
  distinct_counts.`metric__c_0038`,
  distinct_counts.`metric__c_0039`,
  distinct_counts.`metric__c_0040`
FROM rollup_final
CROSS JOIN distinct_counts;
```

#### Optimized Params

```json
[
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12",
  "3196d683b95a420394a36143f1613f12"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=104.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashJoin_202	1.00	1	root		time:68.3ms, open:70.2µs, close:176.7µs, loops:2, RU:598.40, build_hash_table:{total:67.9ms, fetch:67.9ms, build:4.74µs}, probe:{concurrency:5, total:339.8ms, max:68ms, probe:6.92µs, fetch and wait:339.8ms}	CARTESIAN inner join	50.7 KB	0 Bytes
├─HashAgg_283(Build)	1.00	1	root		time:68ms, open:22.5µs, close:94µs, loops:2	funcs:count(distinct Column#505)->Column#433, funcs:count(distinct Column#506)->Column#434, funcs:count(distinct Column#507)->Column#435, funcs:count(distinct Column#508)->Column#436, funcs:count(distinct Column#509)->Column#437, funcs:count(distinct Column#510)->Column#438	983.2 KB	0 Bytes
│ └─Projection_343	162185.14	19570	root		time:62.6ms, open:16.5µs, close:92.9µs, loops:26, Concurrency:5	case(eq(Column#431, ?), Column#432)->Column#505, case(eq(Column#431, ?), Column#432)->Column#506, case(eq(Column#431, ?), Column#432)->Column#507, case(eq(Column#431, ?), Column#432)->Column#508, case(eq(Column#431, ?), Column#432)->Column#509, case(eq(Column#431, ?), Column#432)->Column#510	856.4 KB	N/A
│   └─Union_285	162185.14	19570	root		time:67.8ms, open:184ns, close:83.6µs, loops:26		N/A	N/A
│     ├─Projection_287	282.34	19549	root		time:8.52ms, open:123.8µs, close:5.55µs, loops:21, Concurrency:OFF	intuit_risk.group_c_180d_daily_distinct.template_id->Column#431, cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	227.8 KB	N/A
│     │ └─IndexReader_291	282.34	19549	root		time:7.83ms, open:115.2µs, close:3.88µs, loops:21, cop_task: {num: 24, max: 2.54ms, min: 423.5µs, avg: 1.34ms, p95: 2.43ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 16.9ms, tot_wait: 510.7µs, copr_cache: disabled, build_task_duration: 38.9µs, max_distsql_concurrency: 6}, fetch_resp_duration: 7.12ms, rpc_info:{Cop:{num_rpc:24, total_time:32ms}}	index:Selection_290	546.5 KB	N/A
│     │   └─Selection_290	282.34	19549	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 833.3µs, p80:0s, p95:10ms, iters:104, tasks:24}, scan_detail: {total_process_keys: 19549, total_process_keys_size: 5746178, total_keys: 19573, get_snapshot_time: 197µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 16.9ms, total_suspend_time: 17.7µs, total_wait_time: 510.7µs, total_kv_read_wall_time: 20ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
│     │     └─IndexRangeScan_289	282.77	19549	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 833.3µs, p80:0s, p95:10ms, iters:104, tasks:24}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
│     ├─Projection_292	26983.80	6	root		time:67.5ms, open:150.7µs, close:11.2µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.merchant_account_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│     │ └─Selection_294	26983.80	6	root		time:67.4ms, open:148.3µs, close:731ns, loops:2	not(isnull(intuit_risk.pmt_txn_fact.merchant_account_number))	19.5 KB	N/A
│     │   └─CTEFullScan_296	33729.75	6	root	CTE:raw_boundary	time:67.4ms, open:141.5µs, close:171ns, loops:6	data:CTE_0	39.0 KB	0 Bytes
│     ├─Projection_300	26983.80	3	root		time:67.5ms, open:190.9µs, close:10.2µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.card_holder_number_sha512, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│     │ └─Selection_302	26983.80	3	root		time:67.4ms, open:189.7µs, close:901ns, loops:2	not(isnull(intuit_risk.pmt_txn_fact.card_holder_number_sha512))	19.5 KB	N/A
│     │   └─CTEFullScan_304	33729.75	6	root	CTE:raw_boundary	time:67.4ms, open:178.4µs, close:96ns, loops:6	data:CTE_0	N/A	N/A
│     ├─Projection_308	26983.80	5	root		time:67.7ms, open:67.6ms, close:19.8µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.card_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│     │ └─Selection_310	26983.80	5	root		time:67.6ms, open:67.6ms, close:1.41µs, loops:2	not(isnull(intuit_risk.pmt_txn_fact.card_type))	18.2 KB	N/A
│     │   └─CTEFullScan_312	33729.75	6	root	CTE:raw_boundary	time:67.6ms, open:67.6ms, close:573ns, loops:6	data:CTE_0	N/A	N/A
│     ├─Projection_316	26983.80	0	root		time:67.6ms, open:67.5ms, close:12.7µs, loops:1, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.entry_method, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	30.6 KB	N/A
│     │ └─Selection_318	26983.80	0	root		time:67.5ms, open:67.5ms, close:651ns, loops:1	not(isnull(intuit_risk.pmt_txn_fact.entry_method))	16.9 KB	N/A
│     │   └─CTEFullScan_320	33729.75	6	root	CTE:raw_boundary	time:67.5ms, open:67.5ms, close:102ns, loops:5	data:CTE_0	N/A	N/A
│     ├─Projection_324	26983.80	6	root		time:58.7ms, open:58.6ms, close:9.93µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.mt_gateway, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	47.9 KB	N/A
│     │ └─Selection_326	26983.80	6	root		time:58.7ms, open:58.6ms, close:761ns, loops:2	not(isnull(intuit_risk.pmt_txn_fact.mt_gateway))	19.5 KB	N/A
│     │   └─CTEFullScan_328	33729.75	6	root	CTE:raw_boundary	time:58.7ms, open:58.6ms, close:125ns, loops:6	data:CTE_0	N/A	N/A
│     └─Projection_332	26983.80	1	root		time:76µs, open:7.5µs, close:12.5µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.check_bank_routing_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│       └─Selection_334	26983.80	1	root		time:29.3µs, open:6.25µs, close:713ns, loops:2	not(isnull(intuit_risk.pmt_txn_fact.check_bank_routing_number))	16.9 KB	N/A
│         └─CTEFullScan_336	33729.75	6	root	CTE:raw_boundary	time:9.55µs, open:403ns, close:73ns, loops:6	data:CTE_0	N/A	N/A
└─HashAgg_209(Probe)	1.00	1	root		time:68.1ms, open:46.1µs, close:73.7µs, loops:2, partial_worker:{wall_time:67.940171ms, concurrency:8, task_num:6, tot_wait:135.071059ms, tot_exec:549.644µs, tot_time:543.034442ms, max:67.890936ms, p95:67.890936ms}, final_worker:{wall_time:67.951481ms, concurrency:16, task_num:21, tot_wait:414.254µs, tot_exec:6.075µs, tot_time:1.086799245s, max:67.933329ms, p95:67.933329ms}	funcs:sum(Column#353)->Column#357, funcs:sum(Column#354)->Column#358, funcs:min(Column#355)->Column#359, funcs:max(Column#356)->Column#360	1.58 MB	0 Bytes
  └─Union_213	4938.82	4793	root		time:67.9ms, open:734ns, close:70.1µs, loops:7		N/A	N/A
    ├─Projection_215	4938.02	4792	root		time:13.6ms, open:12.7µs, close:29.4µs, loops:6, Concurrency:5	intuit_risk.group_c_180d_daily_rollup.metric__c_0031->Column#353, cast(intuit_risk.group_c_180d_daily_rollup.metric__c_0032, decimal(41,6) BINARY)->Column#354, intuit_risk.group_c_180d_daily_rollup.metric__c_0033->Column#355, intuit_risk.group_c_180d_daily_rollup.metric__c_0034->Column#356	1.31 MB	N/A
    │ └─IndexLookUp_220	4938.02	4792	root		time:13.6ms, open:11.2µs, close:7.19µs, loops:6, index_task: {total_time: 4.02ms, fetch_handle: 4.02ms, build: 1.41µs, wait: 1.55µs}, table_task: {total_time: 8.6ms, num: 1, concurrency: 5}, next: {wait_index: 4.07ms, wait_table_lookup_build: 1.79ms, wait_table_lookup_resp: 6.81ms}		2.12 MB	N/A
    │   ├─Selection_219(Build)	4938.02	4792	cop[tikv]		time:3.87ms, open:0s, close:0s, loops:7, cop_task: {num: 1, max: 3.84ms, proc_keys: 4792, tot_proc: 2.83ms, tot_wait: 32.4µs, copr_cache: disabled, build_task_duration: 15.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 3.86ms, rpc_info:{Cop:{num_rpc:1, total_time:3.83ms}}, tikv_task:{time:10ms, loops:9}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 1059032, total_keys: 4793, get_snapshot_time: 17.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.83ms, total_suspend_time: 6.31µs, total_wait_time: 32.4µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_rollup.d_event_day, ?)	N/A	N/A
    │   │ └─IndexRangeScan_217	4945.65	4792	cop[tikv]	table:r, index:PRIMARY(bundle_id, key1, key2, p_event_day, d_event_day)	tikv_task:{time:10ms, loops:9}	range:(? ? ? ?,? ? ? +inf], keep order:false	N/A	N/A
    │   └─TableRowIDScan_218(Probe)	4938.02	4792	cop[tikv]	table:r	time:6.73ms, open:0s, close:3.74µs, loops:6, cop_task: {num: 93, max: 3.5ms, min: 0s, avg: 896.7µs, p95: 1.96ms, max_proc_keys: 270, p95_proc_keys: 165, tot_proc: 33.4ms, tot_wait: 2.99ms, copr_cache: disabled, build_task_duration: 457.7µs, max_distsql_concurrency: 15, max_extra_concurrency: 1, store_batch_num: 24}, fetch_resp_duration: 5.49ms, rpc_info:{Cop:{num_rpc:69, total_time:82.7ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:167, tasks:93}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 987152, total_keys: 4792, get_snapshot_time: 689.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 33.4ms, total_suspend_time: 26.2µs, total_wait_time: 2.99ms}	keep order:false	N/A	N/A
    └─Projection_221	0.80	1	root		time:67.9ms, open:67.6ms, close:39.5µs, loops:2, Concurrency:OFF	cast(Column#345, decimal(38,6) BINARY)->Column#353, cast(Column#346, decimal(41,6) BINARY)->Column#354, cast(Column#347, decimal(38,6) BINARY)->Column#355, cast(Column#348, decimal(38,6) BINARY)->Column#356	22.9 KB	N/A
      └─Selection_223	0.80	1	root		time:67.8ms, open:67.6ms, close:38.3µs, loops:2	gt(Column#345, ?)	22.9 KB	N/A
        └─HashAgg_227	1.00	1	root		time:67.8ms, open:67.6ms, close:37.7µs, loops:3, partial_worker:{wall_time:168.232µs, concurrency:8, task_num:4, tot_wait:237.381µs, tot_exec:18.9µs, tot_time:774.862µs, max:100.975µs, p95:100.975µs}, final_worker:{wall_time:195.535µs, concurrency:16, task_num:19, tot_wait:495.952µs, tot_exec:2.488µs, tot_time:2.377513ms, max:160.178µs, p95:160.178µs}	funcs:count(?)->Column#345, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#346, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#347, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#348	144.5 KB	0 Bytes
          └─CTEFullScan_231	33729.75	6	root	CTE:raw_boundary	time:67.6ms, open:67.5ms, close:33.4µs, loops:5	data:CTE_0	N/A	N/A
CTE_0	33729.75	6	root		time:67.4ms, open:141.5µs, close:171ns, loops:6	Non-Recursive CTE	39.0 KB	0 Bytes
└─Projection_146(Seed Part)	33729.75	6	root		time:67.3ms, open:138.9µs, close:32.7µs, loops:5, Concurrency:5	intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.pmt_txn_fact.card_type, intuit_risk.pmt_txn_fact.entry_method, intuit_risk.pmt_txn_fact.mt_gateway, intuit_risk.pmt_txn_fact.check_bank_routing_number	105.1 KB	N/A
  └─IndexHashJoin_157	33729.75	6	root		time:67.3ms, open:138µs, close:10.9µs, loops:5, inner:{total:152.6ms, concurrency:5, task:4, construct:14ms, fetch:129.7ms, build:2.79ms, join:8.88ms}	inner join, inner:IndexReader_171, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.35 MB	N/A
    ├─IndexReader_168(Build)	21567.79	21121	root	partition:all	time:14ms, open:136.2µs, close:7.85µs, loops:23, cop_task: {num: 34, max: 5ms, min: 259.2µs, avg: 1.6ms, p95: 3.95ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 33.4ms, tot_wait: 833.5µs, copr_cache: disabled, build_task_duration: 67.4µs, max_distsql_concurrency: 9}, fetch_resp_duration: 13ms, rpc_info:{Cop:{num_rpc:34, total_time:53.9ms}}	index:Selection_167	337.1 KB	N/A
    │ └─Selection_167	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 294.1µs, p80:0s, p95:0s, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 331.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 33.4ms, total_suspend_time: 54.5µs, total_wait_time: 833.5µs}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_166	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_171(Probe)	33729.75	5285	root	partition:all	total_time:123.6ms, total_open:73.9ms, total_close:42µs, loops:11, cop_task: {num: 172, max: 13.7ms, min: 631.4µs, avg: 2.84ms, p95: 8.37ms, max_proc_keys: 151, p95_proc_keys: 115, tot_proc: 186.4ms, tot_wait: 4.02ms, copr_cache: disabled, build_task_duration: 13.6ms, max_distsql_concurrency: 15}, fetch_resp_duration: 45.8ms, rpc_info:{Cop:{num_rpc:172, total_time:484.3ms}}	index:Selection_170	15.8 KB	N/A
      └─Selection_170	33729.75	5285	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 930.2µs, p80:0s, p95:10ms, iters:241, tasks:172}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.44ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 186.4ms, total_suspend_time: 373.5µs, total_wait_time: 4.02ms, total_kv_read_wall_time: 150ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_169	45706.03	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 872.1µs, p80:0s, p95:10ms, iters:241, tasks:172}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### 15. group_c_bundle_007

- Filter/window: `p.merchant_account_number = %s` / `1d`
- Chosen event: `INV0037793946` kind=`hot_merchant_account_number` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 102.2 ms | ok |
| `optimized_default` | `{}` | 192.1 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 112.7 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 114.6 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 104.6 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 106.9 ms | ok |

#### Original SQL

```sql
SELECT
  COUNT(DISTINCT(d.smart_id)) AS `metric__c_0190`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__c_0191`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__c_0192`,
  COUNT(DISTINCT(d.true_ip)) AS `metric__c_0193`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__c_0194`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__c_0195`,
  COUNT(DISTINCT(d.agent_os)) AS `metric__c_0196`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.smart_id END) AS `metric__c_0257`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0257`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.exact_id END) AS `metric__c_0258`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0258`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.input_ip END) AS `metric__c_0259`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0259`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.smart_id END) AS `metric__c_0266`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0266`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.exact_id END) AS `metric__c_0267`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0267`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.input_ip END) AS `metric__c_0268`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0268`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.smart_id END) AS `metric__c_0275`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0275`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.exact_id END) AS `metric__c_0276`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0276`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.input_ip END) AS `metric__c_0277`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0277`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.smart_id END) AS `metric__c_0284`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0284`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.exact_id END) AS `metric__c_0285`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0285`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.input_ip END) AS `metric__c_0286`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0286`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0329`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0329`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0330`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0330`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0331`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0331`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0332`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0332`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0341`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0341`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0342`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0342`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0343`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0343`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0344`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0344`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0353`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0353`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0354`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0354`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0355`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0355`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0356`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0356`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0365`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0365`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0366`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0366`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0367`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0367`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0368`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0368`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0377`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0377`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0378`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0378`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0379`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0379`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0380`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0380`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0389`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0389`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0390`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0390`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0391`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0391`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0392`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0392`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1775245040017
  AND d.jms_timestamp >= '2026-04-03 12:37:20.017000'
GROUP BY p.merchant_account_number;
```

#### Original Params

```json
[
  5247719989330882
]
```

#### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=102.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_8	48.46	1	root		time:66.6ms, open:98.2µs, close:33.7µs, loops:2, RU:43.50, Concurrency:OFF	Column#106, Column#107, Column#108, Column#109, Column#110, Column#111, Column#112, Column#113, Column#114, Column#115, Column#114, Column#116, Column#114, Column#117, Column#118, Column#119, Column#118, Column#120, Column#118, Column#121, Column#122, Column#123, Column#122, Column#124, Column#122, Column#125, Column#126, Column#127, Column#126, Column#128, Column#126, Column#129, Column#130, Column#131, Column#130, Column#132, Column#133, Column#134, Column#133, Column#135, Column#136, Column#137, Column#136, Column#138, Column#139, Column#140, Column#139, Column#141, Column#142, Column#143, Column#142, Column#144, Column#145, Column#146, Column#145, Column#147, Column#148, Column#149, Column#148, Column#150, Column#151, Column#152, Column#151, Column#153, Column#154, Column#155, Column#154, Column#156, Column#157, Column#158, Column#157, Column#159, Column#160, Column#161, Column#160, Column#162, Column#163, Column#164, Column#163	350.2 KB	N/A
└─HashAgg_12	48.46	1	root		time:66.6ms, open:92.3µs, close:32.2µs, loops:2	group by:Column#242, funcs:count(distinct Column#183)->Column#106, funcs:count(distinct Column#184)->Column#107, funcs:count(distinct Column#185)->Column#108, funcs:count(distinct Column#186)->Column#109, funcs:count(distinct Column#187)->Column#110, funcs:count(distinct Column#188)->Column#111, funcs:count(distinct Column#189)->Column#112, funcs:count(distinct Column#190)->Column#113, funcs:sum(Column#191)->Column#114, funcs:count(distinct Column#192)->Column#115, funcs:count(distinct Column#193)->Column#116, funcs:count(distinct Column#194)->Column#117, funcs:sum(Column#195)->Column#118, funcs:count(distinct Column#196)->Column#119, funcs:count(distinct Column#197)->Column#120, funcs:count(distinct Column#198)->Column#121, funcs:sum(Column#199)->Column#122, funcs:count(distinct Column#200)->Column#123, funcs:count(distinct Column#201)->Column#124, funcs:count(distinct Column#202)->Column#125, funcs:sum(Column#203)->Column#126, funcs:count(distinct Column#204)->Column#127, funcs:count(distinct Column#205)->Column#128, funcs:min(Column#206)->Column#129, funcs:sum(Column#207)->Column#130, funcs:max(Column#208)->Column#131, funcs:min(Column#209)->Column#132, funcs:sum(Column#210)->Column#133, funcs:max(Column#211)->Column#134, funcs:min(Column#212)->Column#135, funcs:sum(Column#213)->Column#136, funcs:max(Column#214)->Column#137, funcs:min(Column#215)->Column#138, funcs:sum(Column#216)->Column#139, funcs:max(Column#217)->Column#140, funcs:min(Column#218)->Column#141, funcs:sum(Column#219)->Column#142, funcs:max(Column#220)->Column#143, funcs:min(Column#221)->Column#144, funcs:sum(Column#222)->Column#145, funcs:max(Column#223)->Column#146, funcs:min(Column#224)->Column#147, funcs:sum(Column#225)->Column#148, funcs:max(Column#226)->Column#149, funcs:min(Column#227)->Column#150, funcs:sum(Column#228)->Column#151, funcs:max(Column#229)->Column#152, funcs:min(Column#230)->Column#153, funcs:sum(Column#231)->Column#154, funcs:max(Column#232)->Column#155, funcs:min(Column#233)->Column#156, funcs:sum(Column#234)->Column#157, funcs:max(Column#235)->Column#158, funcs:min(Column#236)->Column#159, funcs:sum(Column#237)->Column#160, funcs:max(Column#238)->Column#161, funcs:min(Column#239)->Column#162, funcs:sum(Column#240)->Column#163, funcs:max(Column#241)->Column#164	507.4 KB	0 Bytes
  └─Projection_81	22376.97	139	root		time:66.2ms, open:73.4µs, close:31.4µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#183, intuit_risk.deviceprofile_fact.exact_id->Column#184, intuit_risk.deviceprofile_fact.input_ip->Column#185, intuit_risk.deviceprofile_fact.true_ip->Column#186, intuit_risk.deviceprofile_fact.proxy_ip->Column#187, intuit_risk.deviceprofile_fact.agent_type->Column#188, intuit_risk.deviceprofile_fact.agent_os->Column#189, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#190, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#191, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#192, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#193, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#194, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#196, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#197, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#198, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#199, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#200, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#201, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#202, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#203, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#204, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#205, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#207, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#208, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#209, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#210, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#212, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#213, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#214, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#215, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#217, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#218, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#221, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#222, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#223, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#225, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#226, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#230, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#232, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#234, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#235, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#236, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#237, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#238, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#239, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#240, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#241, intuit_risk.pmt_txn_fact.merchant_account_number->Column#242	993.0 KB	N/A
    └─IndexHashJoin_30	22376.97	139	root		time:65.1ms, open:72.5µs, close:9.3µs, loops:3, inner:{total:68.5ms, concurrency:5, task:2, construct:1.37ms, fetch:67ms, build:311µs, join:166.7µs}	inner join, inner:IndexLookUp_45, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	617.1 KB	N/A
      ├─IndexReader_41(Build)	12650.44	2352	root	partition:p20260501,p20260601,pmax	time:4.92ms, open:71.1µs, close:6.38µs, loops:5, cop_task: {num: 6, max: 1.88ms, min: 653µs, avg: 1.07ms, p95: 1.88ms, max_proc_keys: 1907, p95_proc_keys: 1907, tot_proc: 2.21ms, tot_wait: 180.6µs, copr_cache: disabled, build_task_duration: 21.8µs, max_distsql_concurrency: 3}, fetch_resp_duration: 4.72ms, rpc_info:{Cop:{num_rpc:6, total_time:6.32ms}}	index:Selection_40	100.3 KB	N/A
      │ └─Selection_40	12650.44	2352	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}, scan_detail: {total_process_keys: 3603, total_process_keys_size: 463666, total_keys: 3609, get_snapshot_time: 76.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.21ms, total_wait_time: 180.6µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
      │   └─IndexRangeScan_39	17142.18	3603	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
      └─IndexLookUp_45(Probe)	22376.97	139	root	partition:p20260501,p20260601,pmax	total_time:66.1ms, total_open:2.38ms, total_close:14.8µs, loops:4, index_task: {total_time: 59.4ms, fetch_handle: 59.4ms, build: 2.51µs, wait: 3.06µs}, table_task: {total_time: 3.33ms, num: 2, concurrency: 5}, next: {wait_index: 60.4ms, wait_table_lookup_build: 221.4µs, wait_table_lookup_resp: 3.05ms}		189.0 KB	N/A
        ├─Selection_44(Build)	22376.97	139	cop[tikv]		total_time:60.6ms, total_open:0s, total_close:0s, loops:10, cop_task: {num: 8, max: 53.9ms, min: 1.03ms, avg: 9.36ms, p95: 53.9ms, max_proc_keys: 91, p95_proc_keys: 91, tot_proc: 59.7ms, tot_wait: 230.6µs, copr_cache: disabled, build_task_duration: 527.1µs, max_distsql_concurrency: 2}, fetch_resp_duration: 60.4ms, rpc_info:{Cop:{num_rpc:8, total_time:74.7ms}}, tikv_task:{proc max:50ms, min:0s, avg: 6.25ms, p80:0s, p95:50ms, iters:10, tasks:8}, scan_detail: {total_process_keys: 139, total_process_keys_size: 10098, total_keys: 876, get_snapshot_time: 105.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 59.7ms, total_suspend_time: 26.8µs, total_wait_time: 230.6µs}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
        │ └─IndexRangeScan_42	33036.65	139	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:50ms, min:0s, avg: 6.25ms, p80:0s, p95:50ms, iters:10, tasks:8}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
        └─TableRowIDScan_43(Probe)	22376.97	139	cop[tikv]	table:d	total_time:3.01ms, total_open:0s, total_close:7.91µs, loops:4, cop_task: {num: 73, max: 1.05ms, min: 0s, avg: 127.4µs, p95: 775.8µs, max_proc_keys: 5, p95_proc_keys: 4, tot_proc: 2.1ms, tot_wait: 1.54ms, copr_cache: disabled, build_task_duration: 142.9µs, max_distsql_concurrency: 1, max_extra_concurrency: 6, store_batch_num: 55}, fetch_resp_duration: 2.74ms, rpc_info:{Cop:{num_rpc:18, total_time:9.12ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:73, tasks:73}, scan_detail: {total_process_keys: 139, total_process_keys_size: 82492, total_keys: 139, get_snapshot_time: 574.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.1ms, total_wait_time: 1.54ms}	keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  COUNT(DISTINCT(d.smart_id)) AS `metric__c_0190`,
  COUNT(DISTINCT(d.exact_id)) AS `metric__c_0191`,
  COUNT(DISTINCT(d.input_ip)) AS `metric__c_0192`,
  COUNT(DISTINCT(d.true_ip)) AS `metric__c_0193`,
  COUNT(DISTINCT(d.proxy_ip)) AS `metric__c_0194`,
  COUNT(DISTINCT(d.agent_type)) AS `metric__c_0195`,
  COUNT(DISTINCT(d.agent_os)) AS `metric__c_0196`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.smart_id END) AS `metric__c_0257`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0257`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.exact_id END) AS `metric__c_0258`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0258`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Sale' THEN d.input_ip END) AS `metric__c_0259`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0259`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.smart_id END) AS `metric__c_0266`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0266`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.exact_id END) AS `metric__c_0267`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0267`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Refund' THEN d.input_ip END) AS `metric__c_0268`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0268`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.smart_id END) AS `metric__c_0275`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0275`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.exact_id END) AS `metric__c_0276`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0276`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Chargeback' THEN d.input_ip END) AS `metric__c_0277`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0277`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.smart_id END) AS `metric__c_0284`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0284`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.exact_id END) AS `metric__c_0285`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0285`,
  COUNT(DISTINCT CASE WHEN p.transaction_type = 'Auth' THEN d.input_ip END) AS `metric__c_0286`,
  SUM(CASE WHEN p.transaction_type = 'Auth' THEN 1 ELSE 0 END) AS `present__c_0286`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0329`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0329`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0330`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0330`,
  MIN(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0331`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0331`,
  MAX(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0332`,
  SUM(CASE WHEN d.agent_type = 'browser_computer' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0332`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0341`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0341`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0342`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0342`,
  MIN(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0343`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0343`,
  MAX(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0344`,
  SUM(CASE WHEN d.agent_type = 'browser_mobile' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0344`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0353`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0353`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0354`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0354`,
  MIN(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0355`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0355`,
  MAX(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0356`,
  SUM(CASE WHEN d.agent_type = 'mobile_app' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0356`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0365`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0365`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0366`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0366`,
  MIN(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0367`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0367`,
  MAX(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0368`,
  SUM(CASE WHEN d.agent_type = 'tablet' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0368`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0377`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0377`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0378`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0378`,
  MIN(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0379`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0379`,
  MAX(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0380`,
  SUM(CASE WHEN d.agent_type = 'desktop' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0380`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0389`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0389`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN CAST(d.device_score AS DECIMAL(10,2)) END) AS `metric__c_0390`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_score IS NOT NULL AND d.device_score != '' THEN 1 ELSE 0 END) AS `present__c_0390`,
  MIN(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0391`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0391`,
  MAX(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN CAST(d.device_worst_score AS DECIMAL(10,2)) END) AS `metric__c_0392`,
  SUM(CASE WHEN d.agent_type = 'unknown' AND d.device_worst_score IS NOT NULL AND d.device_worst_score != '' THEN 1 ELSE 0 END) AS `present__c_0392`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1775245040017
  AND d.jms_timestamp >= '2026-04-03 12:37:20.017000'
HAVING COUNT(*) > 0;
```

#### Optimized Params

```json
[
  5247719989330882
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=104.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_10	0.80	1	root		time:64.4ms, open:85.6µs, close:33.8µs, loops:2, RU:39.07, Concurrency:OFF	Column#106->Column#166, Column#107->Column#167, Column#108->Column#168, Column#109->Column#169, Column#110->Column#170, Column#111->Column#171, Column#112->Column#172, Column#113->Column#173, Column#114->Column#174, Column#115->Column#175, Column#114->Column#176, Column#116->Column#177, Column#114->Column#178, Column#117->Column#179, Column#118->Column#180, Column#119->Column#181, Column#118->Column#182, Column#120->Column#183, Column#118->Column#184, Column#121->Column#185, Column#122->Column#186, Column#123->Column#187, Column#122->Column#188, Column#124->Column#189, Column#122->Column#190, Column#125->Column#191, Column#126->Column#192, Column#127->Column#193, Column#126->Column#194, Column#128->Column#195, Column#126->Column#196, Column#129->Column#197, Column#130->Column#198, Column#131->Column#199, Column#130->Column#200, Column#132->Column#201, Column#133->Column#202, Column#134->Column#203, Column#133->Column#204, Column#135->Column#205, Column#136->Column#206, Column#137->Column#207, Column#136->Column#208, Column#138->Column#209, Column#139->Column#210, Column#140->Column#211, Column#139->Column#212, Column#141->Column#213, Column#142->Column#214, Column#143->Column#215, Column#142->Column#216, Column#144->Column#217, Column#145->Column#218, Column#146->Column#219, Column#145->Column#220, Column#147->Column#221, Column#148->Column#222, Column#149->Column#223, Column#148->Column#224, Column#150->Column#225, Column#151->Column#226, Column#152->Column#227, Column#151->Column#228, Column#153->Column#229, Column#154->Column#230, Column#155->Column#231, Column#154->Column#232, Column#156->Column#233, Column#157->Column#234, Column#158->Column#235, Column#157->Column#236, Column#159->Column#237, Column#160->Column#238, Column#161->Column#239, Column#160->Column#240, Column#162->Column#241, Column#163->Column#242, Column#164->Column#243, Column#163->Column#244	345.8 KB	N/A
└─Selection_12	0.80	1	root		time:64.4ms, open:80.5µs, close:32.1µs, loops:2	gt(Column#165, ?)	383.1 KB	N/A
  └─HashAgg_16	1.00	1	root		time:64.3ms, open:75.4µs, close:31.3µs, loops:3	funcs:count(distinct Column#263)->Column#106, funcs:count(distinct Column#264)->Column#107, funcs:count(distinct Column#265)->Column#108, funcs:count(distinct Column#266)->Column#109, funcs:count(distinct Column#267)->Column#110, funcs:count(distinct Column#268)->Column#111, funcs:count(distinct Column#269)->Column#112, funcs:count(distinct Column#270)->Column#113, funcs:sum(Column#271)->Column#114, funcs:count(distinct Column#272)->Column#115, funcs:count(distinct Column#273)->Column#116, funcs:count(distinct Column#274)->Column#117, funcs:sum(Column#275)->Column#118, funcs:count(distinct Column#276)->Column#119, funcs:count(distinct Column#277)->Column#120, funcs:count(distinct Column#278)->Column#121, funcs:sum(Column#279)->Column#122, funcs:count(distinct Column#280)->Column#123, funcs:count(distinct Column#281)->Column#124, funcs:count(distinct Column#282)->Column#125, funcs:sum(Column#283)->Column#126, funcs:count(distinct Column#284)->Column#127, funcs:count(distinct Column#285)->Column#128, funcs:min(Column#286)->Column#129, funcs:sum(Column#287)->Column#130, funcs:max(Column#288)->Column#131, funcs:min(Column#289)->Column#132, funcs:sum(Column#290)->Column#133, funcs:max(Column#291)->Column#134, funcs:min(Column#292)->Column#135, funcs:sum(Column#293)->Column#136, funcs:max(Column#294)->Column#137, funcs:min(Column#295)->Column#138, funcs:sum(Column#296)->Column#139, funcs:max(Column#297)->Column#140, funcs:min(Column#298)->Column#141, funcs:sum(Column#299)->Column#142, funcs:max(Column#300)->Column#143, funcs:min(Column#301)->Column#144, funcs:sum(Column#302)->Column#145, funcs:max(Column#303)->Column#146, funcs:min(Column#304)->Column#147, funcs:sum(Column#305)->Column#148, funcs:max(Column#306)->Column#149, funcs:min(Column#307)->Column#150, funcs:sum(Column#308)->Column#151, funcs:max(Column#309)->Column#152, funcs:min(Column#310)->Column#153, funcs:sum(Column#311)->Column#154, funcs:max(Column#312)->Column#155, funcs:min(Column#313)->Column#156, funcs:sum(Column#314)->Column#157, funcs:max(Column#315)->Column#158, funcs:min(Column#316)->Column#159, funcs:sum(Column#317)->Column#160, funcs:max(Column#318)->Column#161, funcs:min(Column#319)->Column#162, funcs:sum(Column#320)->Column#163, funcs:max(Column#321)->Column#164, funcs:count(?)->Column#165	304.6 KB	0 Bytes
    └─Projection_65	22376.97	139	root		time:63.9ms, open:63.8µs, close:30.4µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#263, intuit_risk.deviceprofile_fact.exact_id->Column#264, intuit_risk.deviceprofile_fact.input_ip->Column#265, intuit_risk.deviceprofile_fact.true_ip->Column#266, intuit_risk.deviceprofile_fact.proxy_ip->Column#267, intuit_risk.deviceprofile_fact.agent_type->Column#268, intuit_risk.deviceprofile_fact.agent_os->Column#269, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#270, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#271, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#272, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#273, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#274, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#275, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#276, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#277, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#278, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#279, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#280, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#281, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#282, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#283, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#284, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#285, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#286, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#287, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#288, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#289, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#290, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#291, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#292, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#293, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#294, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#295, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#296, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#297, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#298, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#299, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#300, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#301, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#302, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#303, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#304, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#305, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#306, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#307, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#308, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#309, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#310, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#311, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#312, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#313, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#314, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#315, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#316, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#317, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#318, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#319, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#320, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#321	567.5 KB	N/A
      └─IndexHashJoin_26	22376.97	139	root		time:62.9ms, open:62.6µs, close:8.83µs, loops:3, inner:{total:62.8ms, concurrency:5, task:2, construct:1.36ms, fetch:61.3ms, build:309.4µs, join:150.6µs}	inner join, inner:IndexLookUp_41, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	635.4 KB	N/A
        ├─IndexReader_37(Build)	12650.44	2352	root	partition:p20260501,p20260601,pmax	time:5.09ms, open:61.3µs, close:5.91µs, loops:5, cop_task: {num: 6, max: 1.79ms, min: 700.8µs, avg: 1.11ms, p95: 1.79ms, max_proc_keys: 1907, p95_proc_keys: 1907, tot_proc: 2.28ms, tot_wait: 231.2µs, copr_cache: disabled, build_task_duration: 19.8µs, max_distsql_concurrency: 3}, fetch_resp_duration: 4.93ms, rpc_info:{Cop:{num_rpc:6, total_time:6.56ms}}	index:Selection_36	100.3 KB	N/A
        │ └─Selection_36	12650.44	2352	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}, scan_detail: {total_process_keys: 3603, total_process_keys_size: 463666, total_keys: 3609, get_snapshot_time: 98.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.28ms, total_wait_time: 231.2µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        │   └─IndexRangeScan_35	17142.18	3603	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
        └─IndexLookUp_41(Probe)	22376.97	139	root	partition:p20260501,p20260601,pmax	total_time:60.7ms, total_open:2.3ms, total_close:11.4µs, loops:4, index_task: {total_time: 54.3ms, fetch_handle: 54.3ms, build: 3.07µs, wait: 2.78µs}, table_task: {total_time: 3.19ms, num: 2, concurrency: 5}, next: {wait_index: 55.2ms, wait_table_lookup_build: 232µs, wait_table_lookup_resp: 2.9ms}		189.0 KB	N/A
          ├─Selection_40(Build)	22376.97	139	cop[tikv]		total_time:55.4ms, total_open:0s, total_close:0s, loops:10, cop_task: {num: 8, max: 51.9ms, min: 1.04ms, avg: 8.64ms, p95: 51.9ms, max_proc_keys: 91, p95_proc_keys: 91, tot_proc: 46.3ms, tot_wait: 215.3µs, copr_cache: disabled, build_task_duration: 528.1µs, max_distsql_concurrency: 2}, fetch_resp_duration: 55.3ms, rpc_info:{Cop:{num_rpc:8, total_time:69ms}}, tikv_task:{proc max:40ms, min:0s, avg: 6.25ms, p80:10ms, p95:40ms, iters:10, tasks:8}, scan_detail: {total_process_keys: 139, total_process_keys_size: 10098, total_keys: 876, get_snapshot_time: 85.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 46.3ms, total_suspend_time: 19.5µs, total_wait_time: 215.3µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │ └─IndexRangeScan_38	33036.65	139	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:40ms, min:0s, avg: 6.25ms, p80:10ms, p95:40ms, iters:10, tasks:8}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
          └─TableRowIDScan_39(Probe)	22376.97	139	cop[tikv]	table:d	total_time:2.87ms, total_open:0s, total_close:7.11µs, loops:4, cop_task: {num: 73, max: 1.03ms, min: 0s, avg: 123.8µs, p95: 655.2µs, max_proc_keys: 5, p95_proc_keys: 4, tot_proc: 2.1ms, tot_wait: 1.29ms, copr_cache: disabled, build_task_duration: 153.6µs, max_distsql_concurrency: 1, max_extra_concurrency: 6, store_batch_num: 55}, fetch_resp_duration: 2.59ms, rpc_info:{Cop:{num_rpc:18, total_time:8.87ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:73, tasks:73}, scan_detail: {total_process_keys: 139, total_process_keys_size: 82492, total_keys: 139, get_snapshot_time: 504µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.1ms, total_wait_time: 1.29ms}	keep order:false	N/A	N/A
```

## Residual Manual Optimization Required

These two SQLs are still exact-count hot-key distinct workloads. The current SQL is already covered by the helper table primary key, but it still has to read hundreds of thousands to 1.5M helper rows and perform exact distinct aggregation at the TiDB root.

### Residual Summary

| Bundle | Current exact best | Extra exact best tried | Extra approximate best | Helper rows scanned | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `group_b_bundle_018` | 695.3 ms | 754.2 ms (`split_union_distinct_countstar`/`agg_pd_hash16`) | 783.9 ms | 767,762 | Manual data-model/pre-aggregation optimization needed |
| `group_b_bundle_020` | 1128.4 ms | 1143.0 ms (`split_union_distinct_countstar`/`distinct_pd_hash16`) | 1133.3 ms | 1,559,443 | Manual data-model/pre-aggregation optimization needed |

The table size check for `group_b_180d_daily_distinct` returned about `2,543,647,958` rows, `208 GB` data, and `229 GB` existing index size. I did not create another experimental full-table index on this helper table because it would be a large online DDL with unproven benefit.

### group_b_bundle_018

- Original baseline: `1496.6 ms`
- Current optimized exact best: `695.3 ms`, variant `optimized_distinct_pushdown_hashagg_16_8`
- Key/filter: `input_ip = 135.232.20.92`
- Raw boundary rows for the tested sample: `0`; helper-only guard was tested but did not beat the current exact plan.

#### Helper Row Counts

| Template | Rows | Day range |
| --- | ---: | --- |
| `b_0146` | 261,396 | `2025-11-01` to `2026-04-10` |
| `b_0150` | 259,560 | `2025-11-01` to `2026-04-10` |
| `b_0154` | 246,339 | `2025-11-01` to `2026-04-10` |
| `b_0158` | 467 | `2025-11-01` to `2026-04-10` |

#### Current Optimized Exact SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.`exact_id` AS `raw_distinct_0`,
    d.`smart_id` AS `raw_distinct_1`,
    d.`true_ip` AS `raw_distinct_2`,
    d.`agent_type` AS `raw_distinct_3`
  FROM deviceprofile_fact d
  WHERE d.`input_ip` = %s
    AND d.jms_timestamp IS NOT NULL
    AND d.jms_timestamp >= '2025-10-11 09:39:36.398000'
    AND d.jms_timestamp < '2025-10-12 00:00:00.000000'
),
distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
  UNION ALL
  SELECT 'b_0146' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'b_0150' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'b_0154' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'b_0158' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
)
SELECT
  COUNT(DISTINCT CASE WHEN template_id = 'b_0146' THEN distinct_value END) AS `metric__b_0146`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0150' THEN distinct_value END) AS `metric__b_0150`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0154' THEN distinct_value END) AS `metric__b_0154`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0158' THEN distinct_value END) AS `metric__b_0158`
FROM distinct_values;
```

Params:

```json
[
  "135.232.20.92",
  "135.232.20.92"
]
```

The full original and current optimized `EXPLAIN ANALYZE` plans for this SQL are included earlier in this same report under the detailed evidence section.

#### Additional Attempts

| Attempt shape | Best setting | Best time | Result |
| --- | --- | ---: | --- |
| `split_union_distinct_countstar` | `agg_pd_hash16` | 754.2 ms | best extra exact attempt, still slower/equal |
| `helper_only_approx_not_exact_raw_empty_guard` | `base` | 783.9 ms | rejected: approximate distinct semantics |
| `current_approx_not_exact` | `agg_pd_hash16` | 812.2 ms | rejected: approximate distinct semantics |
| `split_scalar_union_all` | `base` | 845.6 ms | rejected: not faster than current exact best |
| `helper_only_group_by_template_raw_empty_guard` | `distinct_pd_hash16` | 900.5 ms | rejected: needs runtime raw-empty branch and was not faster |
| `helper_only_case_distinct_raw_empty_guard` | `distinct_pd_hash16` | 928.7 ms | rejected: needs runtime raw-empty branch and was not faster |
| `current_case_distinct_stream_hint` | `distinct_pd_hash16` | 962.2 ms | rejected: not faster than current exact best |
| `helper_dedup_first` | `agg_pd_distinct_pd_hash16` | 1020.3 ms | rejected: not faster than current exact best |
| `group_by_template` | `base` | 1041.1 ms | rejected: not faster than current exact best |
| `current_case_distinct` | `distinct_pd_hash16` | 1045.9 ms | rejected: not faster than current exact best |
| `two_stage_dedup` | `distinct_pd_hash16` | 1057.1 ms | rejected: not faster than current exact best |

#### Best Extra Exact Attempt SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.`exact_id` AS `raw_distinct_0`,
    d.`smart_id` AS `raw_distinct_1`,
    d.`true_ip` AS `raw_distinct_2`,
    d.`agent_type` AS `raw_distinct_3`
  FROM deviceprofile_fact d
  WHERE d.`input_ip` = %s
    AND d.jms_timestamp IS NOT NULL
    AND d.jms_timestamp >= '2025-10-11 09:39:36.398000'
    AND d.jms_timestamp < '2025-10-12 00:00:00.000000'
),
counts AS (
  SELECT 'b_0146' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0146'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION
    SELECT CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0150' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0150'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION
    SELECT CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0154' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0154'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION
    SELECT CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0158' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0158'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION
    SELECT CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  ) u
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0146' THEN distinct_count END), 0) AS `metric__b_0146`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0150' THEN distinct_count END), 0) AS `metric__b_0150`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0154' THEN distinct_count END), 0) AS `metric__b_0154`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0158' THEN distinct_count END), 0) AS `metric__b_0158`
FROM counts;
```

Params:

```json
[
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92"
]
```

Best extra exact `EXPLAIN ANALYZE`:

```text
-- shape=split_union_distinct_countstar
-- setting=agg_pd_hash16
-- explain_analyze_elapsed_ms=754.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_140	1.00	1	root		time:410.4ms, open:51.7µs, close:107.3µs, loops:2, RU:1567.45, Concurrency:OFF	coalesce(Column#186, ?)->Column#190, coalesce(Column#187, ?)->Column#191, coalesce(Column#188, ?)->Column#192, coalesce(Column#189, ?)->Column#193	28.8 KB	N/A
└─HashAgg_144	1.00	1	root		time:410.4ms, open:50.2µs, close:105.5µs, loops:2, partial_worker:{wall_time:410.208965ms, concurrency:8, task_num:4, tot_wait:1.110515681s, tot_exec:14.019µs, tot_time:3.281186132s, max:410.15035ms, p95:410.15035ms}, final_worker:{wall_time:410.294048ms, concurrency:16, task_num:19, tot_wait:43.607µs, tot_exec:2.439µs, tot_time:6.562951223s, max:410.19945ms, p95:410.19945ms}	funcs:max(Column#218)->Column#186, funcs:max(Column#219)->Column#187, funcs:max(Column#220)->Column#188, funcs:max(Column#221)->Column#189	232.9 KB	0 Bytes
  └─Union_145	4.00	4	root		time:410.2ms, open:789ns, close:100.9µs, loops:5		N/A	N/A
    ├─StreamAgg_152	1.00	1	root		time:410.1ms, open:94.1µs, close:40.8µs, loops:2	funcs:max(Column#251)->Column#218, funcs:max(Column#252)->Column#219, funcs:max(Column#253)->Column#220, funcs:max(Column#254)->Column#221	38.1 KB	N/A
    │ └─Projection_361	1.00	1	root		time:410.1ms, open:91.3µs, close:39.8µs, loops:2, Concurrency:OFF	Column#137->Column#251, case(?, Column#137)->Column#252, case(?, Column#137)->Column#253, case(?, Column#137)->Column#254	380 Bytes	N/A
    │   └─HashAgg_155	1.00	1	root		time:410.1ms, open:88.9µs, close:38.5µs, loops:2, partial_worker:{wall_time:409.934097ms, concurrency:8, task_num:208, tot_wait:3.2698235s, tot_exec:8.046119ms, tot_time:3.279028833s, max:409.883516ms, p95:409.883516ms}, final_worker:{wall_time:409.946097ms, concurrency:16, task_num:23, tot_wait:153.009µs, tot_exec:2.771µs, tot_time:6.558699357s, max:409.931318ms, p95:409.931318ms}	funcs:count(?)->Column#137	375.4 KB	0 Bytes
    │     └─HashAgg_161	161.46	203836	root		time:409.7ms, open:37.1µs, close:35.8µs, loops:209, partial_worker:{wall_time:406.04099ms, concurrency:8, task_num:208, tot_wait:3.188994868s, tot_exec:56.378763ms, tot_time:3.247438389s, max:405.937242ms, p95:405.937242ms}, final_worker:{wall_time:409.840073ms, concurrency:16, task_num:123, tot_wait:40.478µs, tot_exec:24.979679ms, tot_time:6.543006711s, max:409.817569ms, p95:409.817569ms}	group by:Column#136, funcs:firstrow(?)->Column#226	47.5 MB	0 Bytes
    │       └─Union_165	161.46	203836	root		time:402ms, open:227ns, close:33.1µs, loops:209		N/A	N/A
    │         ├─HashAgg_173	160.46	203836	root		time:394.7ms, open:273.2µs, close:19.1µs, loops:209, partial_worker:{wall_time:393.578538ms, concurrency:8, task_num:1, tot_wait:304.713216ms, tot_exec:88.760177ms, tot_time:3.147923582s, max:393.497153ms, p95:393.497153ms}, final_worker:{wall_time:405.247339ms, concurrency:16, task_num:16, tot_wait:5.229571ms, tot_exec:589ns, tot_time:6.470157524s, max:405.205847ms, p95:405.205847ms}	group by:Column#242, funcs:firstrow(Column#242)->Column#136	56.6 MB	0 Bytes
    │         │ └─IndexReader_174	160.46	203836	root		time:304.8ms, open:78.3µs, close:14.8µs, loops:2, cop_task: {num: 1, max: 304.8ms, proc_keys: 261396, tot_proc: 190ms, copr_cache: disabled, build_task_duration: 21.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 304.7ms, rpc_info:{Cop:{num_rpc:1, total_time:304.7ms}}	index:HashAgg_167	7.78 MB	N/A
    │         │   └─HashAgg_167	160.46	203836	cop[tikv]		tikv_task:{time:250ms, loops:256}, scan_detail: {total_process_keys: 261396, total_process_keys_size: 33327990, get_snapshot_time: 21.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 190ms}	group by:cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin), 	N/A	N/A
    │         │     └─IndexRangeScan_172	319319.92	261396	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:190ms, loops:256}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │         └─HashAgg_179	1.00	0	root		time:1.46ms, open:144.1µs, close:13.1µs, loops:1, partial_worker:{wall_time:1.274814ms, concurrency:8, task_num:0, tot_wait:0s, tot_exec:0s, tot_time:9.910595ms, max:1.247371ms, p95:1.247371ms}, final_worker:{wall_time:1.296047ms, concurrency:16, task_num:16, tot_wait:142.476µs, tot_exec:593ns, tot_time:19.979127ms, max:1.25779ms, p95:1.25779ms}	group by:Column#250, funcs:firstrow(Column#250)->Column#136	136.7 KB	0 Bytes
    │           └─Projection_360	1.18	0	root		time:1.29ms, open:81µs, close:10.3µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#250	71.0 KB	N/A
    │             └─Selection_182	1.18	0	root		time:1.28ms, open:78.9µs, close:8.69µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	73.7 KB	N/A
    │               └─CTEFullScan_184	1.47	0	root	CTE:raw_boundary	time:1.27ms, open:75.9µs, close:7.39µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─StreamAgg_205	1.00	1	root		time:402ms, open:175.6µs, close:21.2µs, loops:2	funcs:max(Column#256)->Column#218, funcs:max(Column#257)->Column#219, funcs:max(Column#258)->Column#220, funcs:max(Column#259)->Column#221	1.58 KB	N/A
    │ └─Projection_363	1.00	1	root		time:402ms, open:173µs, close:19.5µs, loops:2, Concurrency:OFF	case(?, Column#152)->Column#256, Column#152->Column#257, case(?, Column#152)->Column#258, case(?, Column#152)->Column#259	380 Bytes	N/A
    │   └─HashAgg_208	1.00	1	root		time:402ms, open:170.5µs, close:18.1µs, loops:2, partial_worker:{wall_time:401.704579ms, concurrency:8, task_num:192, tot_wait:3.204004588s, tot_exec:7.343043ms, tot_time:3.21336439s, max:401.677001ms, p95:401.677001ms}, final_worker:{wall_time:401.837464ms, concurrency:16, task_num:23, tot_wait:23.265µs, tot_exec:2.27µs, tot_time:6.42837388s, max:401.803654ms, p95:401.803654ms}	funcs:count(?)->Column#152	375.4 KB	0 Bytes
    │     └─HashAgg_214	162.43	190667	root		time:401.3ms, open:120.8µs, close:15µs, loops:193, partial_worker:{wall_time:397.498702ms, concurrency:8, task_num:192, tot_wait:3.127174794s, tot_exec:51.048834ms, tot_time:3.179764434s, max:397.4758ms, p95:397.4758ms}, final_worker:{wall_time:401.64182ms, concurrency:16, task_num:123, tot_wait:40.903µs, tot_exec:22.890089ms, tot_time:6.409616499s, max:401.586221ms, p95:401.586221ms}	group by:Column#151, funcs:firstrow(?)->Column#227	45.1 MB	0 Bytes
    │       └─Union_218	162.43	190667	root		time:393.5ms, open:380ns, close:12.4µs, loops:193		N/A	N/A
    │         ├─HashAgg_226	161.43	190667	root		time:389.7ms, open:138.8µs, close:6.45µs, loops:193, partial_worker:{wall_time:388.846207ms, concurrency:8, task_num:1, tot_wait:305.687157ms, tot_exec:83.104644ms, tot_time:3.110550956s, max:388.824788ms, p95:388.824788ms}, final_worker:{wall_time:397.093153ms, concurrency:16, task_num:16, tot_wait:16.736µs, tot_exec:642ns, tot_time:6.339133641s, max:397.079471ms, p95:397.079471ms}	group by:Column#244, funcs:firstrow(Column#244)->Column#151	54.3 MB	0 Bytes
    │         │ └─IndexReader_227	161.43	190667	root		time:305.7ms, open:60.3µs, close:2.73µs, loops:2, cop_task: {num: 1, max: 305.7ms, proc_keys: 259560, tot_proc: 160ms, copr_cache: disabled, build_task_duration: 16.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 305.6ms, rpc_info:{Cop:{num_rpc:1, total_time:305.6ms}}	index:HashAgg_220	7.27 MB	N/A
    │         │   └─HashAgg_220	161.43	190667	cop[tikv]		tikv_task:{time:250ms, loops:254}, scan_detail: {total_process_keys: 259560, total_process_keys_size: 33093900, get_snapshot_time: 6.24µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 160ms}	group by:cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin), 	N/A	N/A
    │         │     └─IndexRangeScan_225	321245.22	259560	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:160ms, loops:254}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │         └─HashAgg_232	1.00	0	root		time:1.41ms, open:327.6µs, close:5.12µs, loops:1, partial_worker:{wall_time:1.066911ms, concurrency:8, task_num:0, tot_wait:0s, tot_exec:0s, tot_time:8.207839ms, max:1.029949ms, p95:1.029949ms}, final_worker:{wall_time:1.072454ms, concurrency:16, task_num:16, tot_wait:90.803µs, tot_exec:593ns, tot_time:16.62486ms, max:1.042366ms, p95:1.042366ms}	group by:Column#255, funcs:firstrow(Column#255)->Column#151	16.6 KB	0 Bytes
    │           └─Projection_362	1.18	0	root		time:1.3ms, open:273.4µs, close:2.36µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#255	11.4 KB	N/A
    │             └─Selection_235	1.18	0	root		time:1.29ms, open:271.1µs, close:745ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	2.48 KB	N/A
    │               └─CTEFullScan_237	1.47	0	root	CTE:raw_boundary	time:1.02ms, open:488ns, close:148ns, loops:1	data:CTE_0	N/A	N/A
    ├─StreamAgg_258	1.00	1	root		time:296.5ms, open:122.4µs, close:19.7µs, loops:2	funcs:max(Column#261)->Column#218, funcs:max(Column#262)->Column#219, funcs:max(Column#263)->Column#220, funcs:max(Column#264)->Column#221	1.58 KB	N/A
    │ └─Projection_365	1.00	1	root		time:296.5ms, open:116.2µs, close:18.4µs, loops:2, Concurrency:OFF	case(?, Column#167)->Column#261, case(?, Column#167)->Column#262, Column#167->Column#263, case(?, Column#167)->Column#264	380 Bytes	N/A
    │   └─HashAgg_261	1.00	1	root		time:296.4ms, open:113.7µs, close:17.3µs, loops:2, partial_worker:{wall_time:296.286502ms, concurrency:8, task_num:144, tot_wait:2.36234773s, tot_exec:6.012898ms, tot_time:2.369850091s, max:296.236666ms, p95:296.236666ms}, final_worker:{wall_time:296.334783ms, concurrency:16, task_num:23, tot_wait:81.727µs, tot_exec:2.963µs, tot_time:4.740396729s, max:296.304675ms, p95:296.304675ms}	funcs:count(?)->Column#167	375.4 KB	0 Bytes
    │     └─HashAgg_267	157.47	141739	root		time:296.1ms, open:62.8µs, close:14µs, loops:145, partial_worker:{wall_time:294.308432ms, concurrency:8, task_num:144, tot_wait:2.308340246s, tot_exec:36.343674ms, tot_time:2.345846811s, max:293.237858ms, p95:293.237858ms}, final_worker:{wall_time:296.190834ms, concurrency:16, task_num:121, tot_wait:411.672µs, tot_exec:17.506447ms, tot_time:4.726388636s, max:296.128114ms, p95:296.128114ms}	group by:Column#166, funcs:firstrow(?)->Column#228	35.6 MB	0 Bytes
    │       └─Union_271	157.47	141739	root		time:289.1ms, open:736ns, close:11.8µs, loops:145		N/A	N/A
    │         ├─HashAgg_279	156.47	141739	root		time:288.6ms, open:150.9µs, close:4.97µs, loops:145, partial_worker:{wall_time:288.040666ms, concurrency:8, task_num:1, tot_wait:228.597143ms, tot_exec:59.333969ms, tot_time:2.303665175s, max:287.963091ms, p95:287.963091ms}, final_worker:{wall_time:292.449353ms, concurrency:16, task_num:16, tot_wait:1.311408ms, tot_exec:684ns, tot_time:4.673100628s, max:292.430519ms, p95:292.430519ms}	group by:Column#246, funcs:firstrow(Column#246)->Column#166	33.8 MB	0 Bytes
    │         │ └─IndexReader_280	156.47	141739	root		time:228.6ms, open:50.3µs, close:1.9µs, loops:2, cop_task: {num: 1, max: 228.6ms, proc_keys: 246339, tot_proc: 120ms, copr_cache: disabled, build_task_duration: 18.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 228.6ms, rpc_info:{Cop:{num_rpc:1, total_time:228.5ms}}	index:HashAgg_273	2.87 MB	N/A
    │         │   └─HashAgg_273	156.47	141739	cop[tikv]		tikv_task:{time:210ms, loops:241}, scan_detail: {total_process_keys: 246339, total_process_keys_size: 25770245, get_snapshot_time: 17.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 120ms}	group by:cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin), 	N/A	N/A
    │         │     └─IndexRangeScan_278	311367.71	246339	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:120ms, loops:241}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │         └─HashAgg_285	1.00	0	root		time:1.46ms, open:279.3µs, close:6.08µs, loops:1, partial_worker:{wall_time:1.15896ms, concurrency:8, task_num:0, tot_wait:0s, tot_exec:0s, tot_time:8.636042ms, max:1.083317ms, p95:1.083317ms}, final_worker:{wall_time:1.153385ms, concurrency:16, task_num:16, tot_wait:250.349µs, tot_exec:602ns, tot_time:17.94463ms, max:1.131337ms, p95:1.131337ms}	group by:Column#260, funcs:firstrow(Column#260)->Column#166	73.2 KB	0 Bytes
    │           └─Projection_364	1.18	0	root		time:1.18ms, open:107.6µs, close:2.48µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#260	85.2 KB	N/A
    │             └─Selection_288	1.18	0	root		time:1.18ms, open:104.8µs, close:993ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	85.3 KB	N/A
    │               └─CTEFullScan_290	1.47	0	root	CTE:raw_boundary	time:1.16ms, open:93.9µs, close:78ns, loops:1	data:CTE_0	N/A	N/A
    └─StreamAgg_311	1.00	1	root		time:1.8ms, open:223.8µs, close:17.6µs, loops:2	funcs:max(Column#266)->Column#218, funcs:max(Column#267)->Column#219, funcs:max(Column#268)->Column#220, funcs:max(Column#269)->Column#221	1.58 KB	N/A
      └─Projection_367	1.00	1	root		time:1.79ms, open:218.5µs, close:16.4µs, loops:2, Concurrency:OFF	case(?, Column#182)->Column#266, case(?, Column#182)->Column#267, case(?, Column#182)->Column#268, Column#182->Column#269	380 Bytes	N/A
        └─HashAgg_314	1.00	1	root		time:1.73ms, open:213.4µs, close:15.5µs, loops:2, partial_worker:{wall_time:1.49178ms, concurrency:8, task_num:3, tot_wait:4.104335ms, tot_exec:5.586µs, tot_time:11.071793ms, max:1.384315ms, p95:1.384315ms}, final_worker:{wall_time:1.489141ms, concurrency:16, task_num:18, tot_wait:256.496µs, tot_exec:1.565µs, tot_time:22.852897ms, max:1.436773ms, p95:1.436773ms}	funcs:count(?)->Column#182	14.0 KB	0 Bytes
          └─HashAgg_320	92.83	3	root		time:1.46ms, open:66.6µs, close:12.7µs, loops:4, partial_worker:{wall_time:1.373977ms, concurrency:8, task_num:3, tot_wait:3.864109ms, tot_exec:18.816µs, tot_time:10.617045ms, max:1.335754ms, p95:1.335754ms}, final_worker:{wall_time:1.373895ms, concurrency:16, task_num:19, tot_wait:281.71µs, tot_exec:915ns, tot_time:21.656782ms, max:1.361462ms, p95:1.361462ms}	group by:Column#181, funcs:firstrow(?)->Column#229	145.1 KB	0 Bytes
            └─Union_324	92.83	3	root		time:1.32ms, open:917ns, close:10.2µs, loops:4		N/A	N/A
              ├─HashAgg_332	91.83	3	root		time:1.26ms, open:124.3µs, close:5.14µs, loops:4, partial_worker:{wall_time:1.111962ms, concurrency:8, task_num:1, tot_wait:997.187µs, tot_exec:12.195µs, tot_time:8.167694ms, max:1.02472ms, p95:1.02472ms}, final_worker:{wall_time:1.132247ms, concurrency:16, task_num:16, tot_wait:329.41µs, tot_exec:592ns, tot_time:16.990977ms, max:1.074612ms, p95:1.074612ms}	group by:Column#248, funcs:firstrow(Column#248)->Column#181	71.3 KB	0 Bytes
              │ └─IndexReader_333	91.83	3	root		time:1.06ms, open:57.3µs, close:1.89µs, loops:2, cop_task: {num: 1, max: 1ms, proc_keys: 467, tot_proc: 425.9µs, tot_wait: 37.5µs, copr_cache: disabled, build_task_duration: 17.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 984.7µs, rpc_info:{Cop:{num_rpc:1, total_time:989.5µs}}	index:HashAgg_326	403 Bytes	N/A
              │   └─HashAgg_326	91.83	3	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_process_keys: 467, total_process_keys_size: 99551, total_keys: 468, get_snapshot_time: 19.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 425.9µs, total_wait_time: 37.5µs}	group by:cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin), 	N/A	N/A
              │     └─IndexRangeScan_331	182741.89	467	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
              └─HashAgg_338	1.00	0	root		time:1.25ms, open:1.17ms, close:4.3µs, loops:1, partial_worker:{wall_time:58.08µs, concurrency:8, task_num:0, tot_wait:0s, tot_exec:0s, tot_time:124.387µs, max:24.1µs, p95:24.1µs}, final_worker:{wall_time:58.659µs, concurrency:16, task_num:16, tot_wait:134.851µs, tot_exec:597ns, tot_time:467.951µs, max:39.565µs, p95:39.565µs}	group by:Column#265, funcs:firstrow(Column#265)->Column#181	14.0 KB	0 Bytes
                └─Projection_366	1.18	0	root		time:1.12ms, open:1.11ms, close:1.3µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#265	2.48 KB	N/A
                  └─Selection_341	1.18	0	root		time:1.11ms, open:1.1ms, close:452ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	2.48 KB	N/A
                    └─CTEFullScan_343	1.47	0	root	CTE:raw_boundary	time:1.1ms, open:1.1ms, close:104ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.47	0	root		time:1.27ms, open:75.9µs, close:7.39µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_131(Seed Part)	1.47	0	root		time:1.23ms, open:71.3µs, close:5.11µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.agent_type	99.6 KB	N/A
  └─IndexReader_136	1.83	0	root	partition:p20251101	time:1.22ms, open:68.3µs, close:3.62µs, loops:1, cop_task: {num: 1, max: 1.12ms, proc_keys: 0, tot_proc: 27.2µs, tot_wait: 48.3µs, copr_cache: disabled, build_task_duration: 27.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.14ms, rpc_info:{Cop:{num_rpc:1, total_time:1.08ms}}	index:Selection_135	255 Bytes	N/A
    └─Selection_135	1.83	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 27.2µs, total_wait_time: 48.3µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type))))	N/A	N/A
      └─IndexRangeScan_134	1.84	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```

#### Raw-Empty Guard Attempt

The best helper-only exact attempt was `helper_only_group_by_template_raw_empty_guard` with `distinct_pd_hash16` at `900.5 ms`; it did not beat the current exact plan, so I did not keep this rewrite.

#### Approximate Distinct Attempt

The best approximate attempt was `helper_only_approx_not_exact_raw_empty_guard` with `base` at `783.9 ms`. I rejected it because `APPROX_COUNT_DISTINCT` changes metric semantics.

### group_b_bundle_020

- Original baseline: `2884.2 ms`
- Current optimized exact best: `1128.4 ms`, variant `optimized_distinct_pushdown`
- Key/filter: `true_ip = 74.179.68.52`
- Raw boundary rows for the tested sample: `0`; helper-only guard was tested but did not beat the current exact plan.

#### Helper Row Counts

| Template | Rows | Day range |
| --- | ---: | --- |
| `b_0162` | 523,720 | `2025-11-01` to `2026-04-10` |
| `b_0166` | 519,249 | `2025-11-01` to `2026-04-10` |
| `b_0170` | 460,693 | `2025-11-01` to `2026-04-10` |
| `b_0174` | 55,302 | `2025-11-01` to `2026-04-10` |
| `b_0178` | 479 | `2025-11-01` to `2026-04-10` |

#### Current Optimized Exact SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.`exact_id` AS `raw_distinct_0`,
    d.`smart_id` AS `raw_distinct_1`,
    d.`input_ip` AS `raw_distinct_2`,
    d.`proxy_ip` AS `raw_distinct_3`,
    d.`agent_type` AS `raw_distinct_4`
  FROM deviceprofile_fact d
  WHERE d.`true_ip` = %s
    AND d.jms_timestamp IS NOT NULL
    AND d.jms_timestamp >= '2025-10-12 19:16:29.762000'
    AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
),
distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
  UNION ALL
  SELECT 'b_0162' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'b_0166' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'b_0170' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'b_0174' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION ALL
  SELECT 'b_0178' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
)
SELECT
  COUNT(DISTINCT CASE WHEN template_id = 'b_0162' THEN distinct_value END) AS `metric__b_0162`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0166' THEN distinct_value END) AS `metric__b_0166`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0170' THEN distinct_value END) AS `metric__b_0170`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0174' THEN distinct_value END) AS `metric__b_0174`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0178' THEN distinct_value END) AS `metric__b_0178`
FROM distinct_values;
```

Params:

```json
[
  "74.179.68.52",
  "74.179.68.52"
]
```

The full original and current optimized `EXPLAIN ANALYZE` plans for this SQL are included earlier in this same report under the detailed evidence section.

#### Additional Attempts

| Attempt shape | Best setting | Best time | Result |
| --- | --- | ---: | --- |
| `helper_only_approx_not_exact_raw_empty_guard` | `base` | 1133.3 ms | rejected: approximate distinct semantics |
| `split_union_distinct_countstar` | `distinct_pd_hash16` | 1143.0 ms | best extra exact attempt, still slower/equal |
| `current_approx_not_exact` | `base` | 1146.4 ms | rejected: approximate distinct semantics |
| `helper_only_group_by_template_raw_empty_guard` | `distinct_pd_hash16` | 1191.5 ms | rejected: needs runtime raw-empty branch and was not faster |
| `split_scalar_union_all` | `agg_pd_distinct_pd_hash16` | 1209.6 ms | rejected: not faster than current exact best |
| `two_stage_dedup` | `distinct_pd_hash16` | 1241.0 ms | rejected: not faster than current exact best |
| `helper_dedup_first` | `distinct_pd_hash16` | 1254.5 ms | rejected: not faster than current exact best |
| `current_case_distinct_stream_hint` | `base` | 1294.8 ms | rejected: not faster than current exact best |
| `group_by_template` | `distinct_pd_hash16` | 1326.3 ms | rejected: not faster than current exact best |
| `current_case_distinct` | `base` | 1331.9 ms | rejected: not faster than current exact best |
| `helper_only_case_distinct_raw_empty_guard` | `base` | 1344.4 ms | rejected: needs runtime raw-empty branch and was not faster |

#### Best Extra Exact Attempt SQL

```sql
WITH raw_boundary AS (
  SELECT
    d.`exact_id` AS `raw_distinct_0`,
    d.`smart_id` AS `raw_distinct_1`,
    d.`input_ip` AS `raw_distinct_2`,
    d.`proxy_ip` AS `raw_distinct_3`,
    d.`agent_type` AS `raw_distinct_4`
  FROM deviceprofile_fact d
  WHERE d.`true_ip` = %s
    AND d.jms_timestamp IS NOT NULL
    AND d.jms_timestamp >= '2025-10-12 19:16:29.762000'
    AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
),
counts AS (
  SELECT 'b_0162' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0162'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION
    SELECT CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0166' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0166'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION
    SELECT CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0170' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0170'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION
    SELECT CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0174' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0174'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION
    SELECT CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0178' AS template_id, COUNT(*) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0178'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION
    SELECT CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
  ) u
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0162' THEN distinct_count END), 0) AS `metric__b_0162`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0166' THEN distinct_count END), 0) AS `metric__b_0166`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0170' THEN distinct_count END), 0) AS `metric__b_0170`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0174' THEN distinct_count END), 0) AS `metric__b_0174`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0178' THEN distinct_count END), 0) AS `metric__b_0178`
FROM counts;
```

Params:

```json
[
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52",
  "74.179.68.52"
]
```

Best extra exact `EXPLAIN ANALYZE`:

```text
-- shape=split_union_distinct_countstar
-- setting=distinct_pd_hash16
-- explain_analyze_elapsed_ms=1143.0
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_149	1.00	1	root		time:806.8ms, open:9.79µs, close:224.8µs, loops:2, RU:3988.24, Concurrency:OFF	coalesce(Column#226, ?)->Column#231, coalesce(Column#227, ?)->Column#232, coalesce(Column#228, ?)->Column#233, coalesce(Column#229, ?)->Column#234, coalesce(Column#230, ?)->Column#235	47.5 KB	N/A
└─StreamAgg_156	1.00	1	root		time:806.7ms, open:7.09µs, close:222.9µs, loops:2	funcs:max(Column#283)->Column#226, funcs:max(Column#284)->Column#227, funcs:max(Column#285)->Column#228, funcs:max(Column#286)->Column#229, funcs:max(Column#287)->Column#230	47.6 KB	N/A
  └─Projection_410	5.00	5	root		time:806.7ms, open:4.2µs, close:222.3µs, loops:6, Concurrency:OFF	case(eq(Column#224, ?), Column#225)->Column#283, case(eq(Column#224, ?), Column#225)->Column#284, case(eq(Column#224, ?), Column#225)->Column#285, case(eq(Column#224, ?), Column#225)->Column#286, case(eq(Column#224, ?), Column#225)->Column#287	28.5 KB	N/A
    └─Union_361	5.00	5	root		time:806.6ms, open:947ns, close:221.3µs, loops:6		N/A	N/A
      ├─Projection_363	1.00	1	root		time:561.4ms, open:145.9µs, close:64.7µs, loops:2, Concurrency:OFF	?->Column#224, Column#158->Column#225	9.49 KB	N/A
      │ └─HashAgg_367	1.00	1	root		time:561.4ms, open:141.5µs, close:62.7µs, loops:2, partial_worker:{wall_time:561.17965ms, concurrency:8, task_num:326, tot_wait:4.471281751s, tot_exec:13.427591ms, tot_time:4.48890802s, max:561.119017ms, p95:561.119017ms}, final_worker:{wall_time:561.233502ms, concurrency:16, task_num:23, tot_wait:27.8µs, tot_exec:2.729µs, tot_time:8.978445892s, max:561.175066ms, p95:561.175066ms}	funcs:count(?)->Column#158	375.4 KB	0 Bytes
      │   └─HashAgg_169	349.62	325548	root		time:560.6ms, open:78.7µs, close:58.4µs, loops:327, partial_worker:{wall_time:544.59421ms, concurrency:8, task_num:513, tot_wait:4.134090617s, tot_exec:218.74244ms, tot_time:4.356354702s, max:544.556945ms, p95:544.556945ms}, final_worker:{wall_time:561.071815ms, concurrency:16, task_num:128, tot_wait:58.781µs, tot_exec:104.155589ms, tot_time:8.876057611s, max:561.041476ms, p95:561.041476ms}	group by:Column#157, funcs:firstrow(?)->Column#266	116.3 MB	0 Bytes
      │     └─Union_173	693750.50	523720	root		time:524.8ms, open:817ns, close:54.5µs, loops:514		N/A	N/A
      │       ├─Projection_175	693749.40	523720	root		time:523.2ms, open:53.2µs, close:40.6µs, loops:514, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#157	855.9 KB	N/A
      │       │ └─IndexReader_178	693749.40	523720	root		time:524.5ms, open:51.7µs, close:10.8µs, loops:514, cop_task: {num: 21, max: 423.4ms, min: 1.22ms, avg: 32ms, p95: 48.6ms, max_proc_keys: 289760, p95_proc_keys: 50144, tot_proc: 359.3ms, tot_wait: 612.6µs, copr_cache: disabled, build_task_duration: 17.2µs, max_distsql_concurrency: 2}, fetch_resp_duration: 522.6ms, rpc_info:{Cop:{num_rpc:21, total_time:670.8ms}}	index:IndexRangeScan_177	36.4 MB	N/A
      │       │   └─IndexRangeScan_177	693749.40	523720	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:180ms, min:0s, avg: 15.7ms, p80:20ms, p95:30ms, iters:593, tasks:21}, scan_detail: {total_process_keys: 523720, total_process_keys_size: 96225360, total_keys: 233980, get_snapshot_time: 247.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 359.3ms, total_suspend_time: 431.6µs, total_wait_time: 612.6µs, total_kv_read_wall_time: 150ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      │       └─Projection_179	1.10	0	root		time:1.75ms, open:1.74ms, close:12.6µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#157	88.9 KB	N/A
      │         └─Selection_181	1.10	0	root		time:1.75ms, open:1.74ms, close:10.3µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	90.9 KB	N/A
      │           └─CTEFullScan_183	1.37	0	root	CTE:raw_boundary	time:1.74ms, open:1.73ms, close:8.96µs, loops:1	data:CTE_0	N/A	N/A
      ├─Projection_372	1.00	1	root		time:806.5ms, open:133.1µs, close:42.2µs, loops:2, Concurrency:OFF	?->Column#224, Column#174->Column#225	380 Bytes	N/A
      │ └─HashAgg_376	1.00	1	root		time:806.5ms, open:130.6µs, close:41.1µs, loops:2, partial_worker:{wall_time:806.262702ms, concurrency:8, task_num:288, tot_wait:6.435716449s, tot_exec:11.613412ms, tot_time:6.449666722s, max:806.216826ms, p95:806.216826ms}, final_worker:{wall_time:806.299066ms, concurrency:16, task_num:23, tot_wait:158.387µs, tot_exec:2.879µs, tot_time:12.900215594s, max:806.279011ms, p95:806.279011ms}	funcs:count(?)->Column#174	375.4 KB	0 Bytes
      │   └─HashAgg_209	350.42	290833	root		time:806ms, open:81.7µs, close:37.1µs, loops:289, partial_worker:{wall_time:791.868637ms, concurrency:8, task_num:508, tot_wait:6.129609673s, tot_exec:201.895375ms, tot_time:6.334652885s, max:791.845549ms, p95:791.845549ms}, final_worker:{wall_time:806.161683ms, concurrency:16, task_num:128, tot_wait:59.23µs, tot_exec:98.829849ms, tot_time:12.812709732s, max:806.137726ms, p95:806.137726ms}	group by:Column#173, funcs:firstrow(?)->Column#267	115.6 MB	0 Bytes
      │     └─Union_213	695358.97	519249	root		time:768.7ms, open:283ns, close:34.1µs, loops:509		N/A	N/A
      │       ├─Projection_215	695357.87	519249	root		time:767.8ms, open:62.9µs, close:28.8µs, loops:509, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#173	801.0 KB	N/A
      │       │ └─IndexReader_218	695357.87	519249	root		time:767.6ms, open:61.9µs, close:7.42µs, loops:509, cop_task: {num: 8, max: 424.9ms, min: 4.94ms, avg: 97.2ms, p95: 424.9ms, max_proc_keys: 289760, p95_proc_keys: 289760, tot_proc: 339.7ms, tot_wait: 235.3µs, copr_cache: disabled, build_task_duration: 20.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 766.2ms, rpc_info:{Cop:{num_rpc:8, total_time:777.4ms}}	index:IndexRangeScan_217	56.2 MB	N/A
      │       │   └─IndexRangeScan_217	695357.87	519249	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:170ms, min:0s, avg: 40ms, p80:140ms, p95:170ms, iters:538, tasks:8}, scan_detail: {total_process_keys: 519249, total_process_keys_size: 67448303, total_keys: 11846, get_snapshot_time: 632.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 339.7ms, total_suspend_time: 64.6µs, total_wait_time: 235.3µs, total_kv_read_wall_time: 10ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      │       └─Projection_219	1.10	0	root		time:1.79ms, open:93.3µs, close:4.06µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#173	109.9 KB	N/A
      │         └─Selection_221	1.10	0	root		time:1.78ms, open:90.1µs, close:1.88µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	84.9 KB	N/A
      │           └─CTEFullScan_223	1.37	0	root	CTE:raw_boundary	time:1.77ms, open:84.2µs, close:848ns, loops:1	data:CTE_0	0 Bytes	0 Bytes
      ├─Projection_381	1.00	1	root		time:665.8ms, open:168.1µs, close:41.8µs, loops:2, Concurrency:OFF	?->Column#224, Column#190->Column#225	9.49 KB	N/A
      │ └─HashAgg_385	1.00	1	root		time:665.8ms, open:166µs, close:40.1µs, loops:2, partial_worker:{wall_time:665.585363ms, concurrency:8, task_num:183, tot_wait:5.315727908s, tot_exec:7.056921ms, tot_time:5.324403238s, max:665.561481ms, p95:665.561481ms}, final_worker:{wall_time:665.618905ms, concurrency:16, task_num:23, tot_wait:97.027µs, tot_exec:2.802µs, tot_time:10.649344338s, max:665.605096ms, p95:665.605096ms}	funcs:count(?)->Column#190	375.4 KB	0 Bytes
      │   └─HashAgg_249	328.53	180152	root		time:665.4ms, open:101.7µs, close:35.8µs, loops:184, partial_worker:{wall_time:657.718373ms, concurrency:8, task_num:451, tot_wait:5.122572848s, tot_exec:131.560892ms, tot_time:5.261441611s, max:657.683802ms, p95:657.683802ms}, final_worker:{wall_time:665.497505ms, concurrency:16, task_num:128, tot_wait:53.316µs, tot_exec:57.354504ms, tot_time:10.603040201s, max:665.472452ms, p95:665.472452ms}	group by:Column#189, funcs:firstrow(?)->Column#268	59.7 MB	0 Bytes
      │     └─Union_253	651787.82	460693	root		time:645.3ms, open:172ns, close:32.1µs, loops:452		N/A	N/A
      │       ├─Projection_255	651786.72	460693	root		time:641.9ms, open:47µs, close:28µs, loops:452, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#189	622.0 KB	N/A
      │       │ └─IndexReader_258	651786.72	460693	root		time:642.1ms, open:46.1µs, close:5.88µs, loops:452, cop_task: {num: 11, max: 462.8ms, min: 3.11ms, avg: 59.7ms, p95: 462.8ms, max_proc_keys: 345056, p95_proc_keys: 345056, tot_proc: 384.9ms, tot_wait: 1.25ms, copr_cache: disabled, build_task_duration: 15.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 640.6ms, rpc_info:{Cop:{num_rpc:11, total_time:656.6ms}}	index:IndexRangeScan_257	33.6 MB	N/A
      │       │   └─IndexRangeScan_257	651786.72	460693	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:220ms, min:0s, avg: 32.7ms, p80:20ms, p95:220ms, iters:493, tasks:11}, scan_detail: {total_process_keys: 460693, total_process_keys_size: 60002367, total_keys: 115647, get_snapshot_time: 1.08ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 384.9ms, total_suspend_time: 208.4µs, total_wait_time: 1.25ms, total_kv_read_wall_time: 140ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      │       └─Projection_259	1.10	0	root		time:1.77ms, open:1.76ms, close:3.21µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#189	86.9 KB	N/A
      │         └─Selection_261	1.10	0	root		time:1.76ms, open:1.76ms, close:1.49µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	59.3 KB	N/A
      │           └─CTEFullScan_263	1.37	0	root	CTE:raw_boundary	time:1.76ms, open:1.76ms, close:552ns, loops:1	data:CTE_0	N/A	N/A
      ├─Projection_390	1.00	1	root		time:52ms, open:213.3µs, close:33.7µs, loops:2, Concurrency:OFF	?->Column#224, Column#206->Column#225	9.49 KB	N/A
      │ └─HashAgg_394	1.00	1	root		time:52ms, open:208.8µs, close:31.8µs, loops:2, partial_worker:{wall_time:51.733838ms, concurrency:8, task_num:16, tot_wait:412.32587ms, tot_exec:285.839µs, tot_time:413.318789ms, max:51.670121ms, p95:51.670121ms}, final_worker:{wall_time:51.746365ms, concurrency:16, task_num:23, tot_wait:268.075µs, tot_exec:2.269µs, tot_time:827.372483ms, max:51.716761ms, p95:51.716761ms}	funcs:count(?)->Column#206	154.3 KB	0 Bytes
      │   └─HashAgg_289	117.43	5009	root		time:51.7ms, open:56µs, close:28.1µs, loops:17, partial_worker:{wall_time:51.337924ms, concurrency:8, task_num:55, tot_wait:396.668763ms, tot_exec:13.024912ms, tot_time:410.387412ms, max:51.313508ms, p95:51.313508ms}, final_worker:{wall_time:51.638156ms, concurrency:16, task_num:128, tot_wait:50.148µs, tot_exec:2.12378ms, tot_time:824.254626ms, max:51.617824ms, p95:51.617824ms}	group by:Column#205, funcs:firstrow(?)->Column#269	5.76 MB	0 Bytes
      │     └─Union_293	231700.19	55302	root		time:50.9ms, open:576ns, close:25.1µs, loops:56		N/A	N/A
      │       ├─Projection_295	231699.09	55302	root		time:49.7ms, open:54.5µs, close:21.3µs, loops:56, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#205	638.8 KB	N/A
      │       │ └─IndexReader_298	231699.09	55302	root		time:49.9ms, open:53.6µs, close:2.75µs, loops:56, cop_task: {num: 9, max: 13.7ms, min: 1.21ms, avg: 5.6ms, p95: 13.7ms, max_proc_keys: 17376, p95_proc_keys: 17376, tot_proc: 35.3ms, tot_wait: 282.9µs, copr_cache: disabled, build_task_duration: 15.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 49.4ms, rpc_info:{Cop:{num_rpc:9, total_time:50.3ms}}	index:IndexRangeScan_297	3.18 MB	N/A
      │       │   └─IndexRangeScan_297	231699.09	55302	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:20ms, min:0s, avg: 4.44ms, p80:10ms, p95:20ms, iters:89, tasks:9}, scan_detail: {total_process_keys: 55302, total_process_keys_size: 11514477, total_keys: 55311, get_snapshot_time: 100.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 35.3ms, total_suspend_time: 85.5µs, total_wait_time: 282.9µs, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      │       └─Projection_299	1.10	0	root		time:1.72ms, open:18.9µs, close:2.86µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#205	54.2 KB	N/A
      │         └─Selection_301	1.10	0	root		time:1.71ms, open:16µs, close:1.01µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	109.9 KB	N/A
      │           └─CTEFullScan_303	1.37	0	root	CTE:raw_boundary	time:1.7ms, open:710ns, close:192ns, loops:1	data:CTE_0	N/A	N/A
      └─Projection_399	1.00	1	root		time:2.41ms, open:230.1µs, close:37.1µs, loops:2, Concurrency:OFF	?->Column#224, Column#222->Column#225	9.49 KB	N/A
        └─HashAgg_403	1.00	1	root		time:2.4ms, open:227µs, close:35.1µs, loops:2, partial_worker:{wall_time:2.117104ms, concurrency:8, task_num:3, tot_wait:6.167205ms, tot_exec:7.772µs, tot_time:16.600475ms, max:2.085725ms, p95:2.085725ms}, final_worker:{wall_time:2.156132ms, concurrency:16, task_num:18, tot_wait:22.361µs, tot_exec:1.45µs, tot_time:34.00428ms, max:2.137477ms, p95:2.137477ms}	funcs:count(?)->Column#222	52.5 KB	0 Bytes
          └─HashAgg_329	191.30	3	root		time:2.25ms, open:155.4µs, close:30.6µs, loops:4, partial_worker:{wall_time:2.043677ms, concurrency:8, task_num:1, tot_wait:1.94039ms, tot_exec:56.561µs, tot_time:16.065518ms, max:2.013651ms, p95:2.013651ms}, final_worker:{wall_time:2.060552ms, concurrency:16, task_num:16, tot_wait:165.881µs, tot_exec:594ns, tot_time:32.529107ms, max:2.03783ms, p95:2.03783ms}	group by:Column#221, funcs:firstrow(?)->Column#270	197.2 KB	0 Bytes
            └─Union_333	378709.79	479	root		time:2ms, open:503ns, close:26.9µs, loops:2		N/A	N/A
              ├─Projection_335	378708.69	479	root		time:1.95ms, open:47.1µs, close:23µs, loops:2, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#221	76.6 KB	N/A
              │ └─IndexReader_338	378708.69	479	root		time:1.88ms, open:46.1µs, close:3µs, loops:2, cop_task: {num: 2, max: 930.7µs, min: 819.3µs, avg: 875µs, p95: 930.7µs, max_proc_keys: 255, p95_proc_keys: 255, tot_proc: 524.7µs, tot_wait: 64.1µs, copr_cache: disabled, build_task_duration: 14.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.76ms, rpc_info:{Cop:{num_rpc:2, total_time:1.71ms}}	index:IndexRangeScan_337	46.8 KB	N/A
              │   └─IndexRangeScan_337	378708.69	479	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:7, tasks:2}, scan_detail: {total_process_keys: 479, total_process_keys_size: 101568, total_keys: 481, get_snapshot_time: 33µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 524.7µs, total_wait_time: 64.1µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
              └─Projection_339	1.10	0	root		time:1.7ms, open:1.7ms, close:3.14µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#221	3.11 KB	N/A
                └─Selection_341	1.10	0	root		time:1.7ms, open:1.7ms, close:1.24µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	39.8 KB	N/A
                  └─CTEFullScan_343	1.37	0	root	CTE:raw_boundary	time:1.69ms, open:1.69ms, close:217ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.37	0	root		time:1.74ms, open:1.73ms, close:8.96µs, loops:1	Non-Recursive CTE	N/A	N/A
└─Projection_140(Seed Part)	1.37	0	root		time:1.75ms, open:80.7µs, close:7.3µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type	54.3 KB	N/A
  └─IndexReader_145	1.71	0	root	partition:p20251101	time:1.74ms, open:75.4µs, close:4.01µs, loops:1, cop_task: {num: 1, max: 1.66ms, proc_keys: 0, tot_proc: 26.2µs, tot_wait: 643.7µs, copr_cache: disabled, build_task_duration: 20.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.65ms, rpc_info:{Cop:{num_rpc:1, total_time:1.64ms}}	index:Selection_144	255 Bytes	N/A
    └─Selection_144	1.71	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 617.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.2µs, total_wait_time: 643.7µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type)))))	N/A	N/A
      └─IndexRangeScan_143	1.72	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

#### Raw-Empty Guard Attempt

The best helper-only exact attempt was `helper_only_group_by_template_raw_empty_guard` with `distinct_pd_hash16` at `1191.5 ms`; it did not beat the current exact plan, so I did not keep this rewrite.

#### Approximate Distinct Attempt

The best approximate attempt was `helper_only_approx_not_exact_raw_empty_guard` with `base` at `1133.3 ms`. I rejected it because `APPROX_COUNT_DISTINCT` changes metric semantics.

### Manual Follow-Up Options

- Build a real rolling distinct pre-aggregation, for example a per-window/count snapshot keyed by `(bundle_id, template_id, key1, key2)` so the read path does not scan one row per distinct value per day.
- If exact distinct by value must remain query-time, evaluate a shadow/off-peak index such as `(bundle_id, template_id, key1, key2, distinct_value, event_day)`. This may enable lower-memory ordered distinct plans, but it would be a very large index on a 2.54B-row helper table and was not created in this run.
- Consider approximate distinct only if the business metric can accept approximation; in this sample it was not a clear win and is a semantic change.