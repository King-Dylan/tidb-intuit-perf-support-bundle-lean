# Final Slow SQL Optimization Report

- Generated: `2026-05-29T13:32:53`
- Source mixed JSON: `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/mixed_traffic_1780029697.json`
- Source slow CSV: `/Users/dylanliu/Downloads/tidb_intuit_perf_support_bundle_lean/code/results/slow_bundles_post_index_3eps_60s.csv`
- Scope: only the 15 bundles still appearing in the post-index slow/error list
- Baseline session: TiKV/TiDB only, `tidb_opt_distinct_agg_push_down=0`, `tidb_hashagg_final_concurrency=4`, `tidb_hashagg_partial_concurrency=4`
- Optimized candidates tested per SQL: default optimized SQL, hashagg 16/8, hashagg 32/8, distinct pushdown, distinct pushdown + hashagg 16/8

## Summary

| Bundle | Filter | Optimization | Before | Best After | Delta | Best Variant | Status |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `group_a_bundle_010` | `p.check_bank_routing_number = %s` | SQL rewrite: pre-aggregate low-cardinality payment dimensions, then pivot CASE metrics from the compact rollup; Session tuning: optimized_distinct_pushdown | 468.9 ms | 115.2 ms | 75.4% | `optimized_distinct_pushdown` | `optimized` |
| `group_a_bundle_006` | `p.check_bank_routing_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8 | 142.7 ms | 134.9 ms | 5.5% | `optimized_hashagg_16_8` | `optimized` |
| `group_c_bundle_025` | `p.merchant_account_number = %s` | SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Index: use payment-side covering join index to avoid p table row lookup | 6095.6 ms | 136.4 ms | 97.8% | `optimized_default` | `optimized` |
| `group_b_bundle_018` | `d.input_ip = %s` | SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown | 1495.0 ms | 669.3 ms | 55.2% | `optimized_distinct_pushdown` | `unresolved` |
| `group_c_bundle_018` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 2511.5 ms | 988.6 ms | 60.6% | `optimized_distinct_pushdown_hashagg_16_8` | `unresolved` |
| `group_c_bundle_021` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_32_8 | 459.4 ms | 238.2 ms | 48.2% | `optimized_hashagg_32_8` | `optimized` |
| `group_b_bundle_020` | `d.true_ip = %s` | SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 3034.6 ms | 1128.5 ms | 62.8% | `optimized_distinct_pushdown_hashagg_16_8` | `unresolved` |
| `group_b_bundle_012` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0 | 507.2 ms | 502.1 ms | 1.0% | `optimized_default` | `unresolved` |
| `group_a_bundle_008` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0 | 109.9 ms | 70.6 ms | 35.8% | `optimized_default` | `optimized` |
| `group_a_bundle_014` | `p.check_bank_routing_number = %s` | SQL rewrite: pre-aggregate low-cardinality payment dimensions, then pivot CASE metrics from the compact rollup; Session tuning: optimized_distinct_pushdown | 323.3 ms | 106.2 ms | 67.1% | `optimized_distinct_pushdown` | `optimized` |
| `group_b_bundle_008` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0 | 47.4 ms | 36.3 ms | 23.3% | `optimized_default` | `optimized` |
| `group_c_bundle_011` | `d.true_ip = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8 | 901.7 ms | 105.4 ms | 88.3% | `optimized_distinct_pushdown_hashagg_16_8` | `optimized` |
| `group_c_bundle_014` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_32_8 | 159.2 ms | 118.3 ms | 25.7% | `optimized_hashagg_32_8` | `optimized` |
| `group_c_bundle_022` | `d.exact_id = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown | 3605.8 ms | 116.9 ms | 96.8% | `optimized_distinct_pushdown` | `optimized` |
| `group_c_bundle_007` | `p.merchant_account_number = %s` | SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_16_8 | 115.5 ms | 106.7 ms | 7.6% | `optimized_hashagg_16_8` | `optimized` |

## Detailed Evidence

### 1. group_a_bundle_010

- Filter/window: `p.check_bank_routing_number = %s` / `30d`
- Chosen event: `INV0046519149` kind=`hot_check_bank_routing_number` error=`(3024, 'Query execution was interrupted, maximum statement execution time exceeded')`
- Optimization: SQL rewrite: pre-aggregate low-cardinality payment dimensions, then pivot CASE metrics from the compact rollup; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 468.9 ms | ok |
| `optimized_default` | `{}` | 117.9 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 119.1 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 118.6 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 115.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 116.4 ms | ok |

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
-- explain_analyze_elapsed_ms=468.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	25.26	1	root		time:359.4ms, open:426.7µs, close:44.8µs, loops:2, RU:371.39, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#183, Column#186, Column#183, Column#187, Column#187, Column#188, Column#187, Column#189, Column#187, Column#190, Column#187, Column#191, Column#191, Column#192, Column#191, Column#193, Column#191, Column#194, Column#191, Column#195, Column#195, Column#196, Column#195, Column#197, Column#195, Column#198, Column#195, Column#199, Column#199, Column#200, Column#199, Column#201, Column#199, Column#202, Column#199, Column#203, Column#203, Column#204, Column#203, Column#205, Column#203, Column#206, Column#203, Column#207, Column#207, Column#208, Column#207, Column#209, Column#207, Column#210, Column#207, Column#211, Column#212, Column#213	230.1 KB	N/A
└─HashAgg_9	25.26	1	root		time:359ms, open:325.7µs, close:43.2µs, loops:2	group by:Column#1528, funcs:count(?)->Column#47, funcs:sum(Column#1362)->Column#48, funcs:min(Column#1363)->Column#49, funcs:max(Column#1364)->Column#50, funcs:sum(Column#1365)->Column#51, funcs:sum(Column#1366)->Column#52, funcs:min(Column#1367)->Column#53, funcs:max(Column#1368)->Column#54, funcs:sum(Column#1369)->Column#55, funcs:sum(Column#1370)->Column#56, funcs:min(Column#1371)->Column#57, funcs:max(Column#1372)->Column#58, funcs:sum(Column#1373)->Column#59, funcs:sum(Column#1374)->Column#60, funcs:min(Column#1375)->Column#61, funcs:max(Column#1376)->Column#62, funcs:sum(Column#1377)->Column#63, funcs:sum(Column#1378)->Column#64, funcs:min(Column#1379)->Column#65, funcs:max(Column#1380)->Column#66, funcs:sum(Column#1381)->Column#67, funcs:sum(Column#1382)->Column#68, funcs:min(Column#1383)->Column#69, funcs:max(Column#1384)->Column#70, funcs:sum(Column#1385)->Column#71, funcs:sum(Column#1386)->Column#72, funcs:min(Column#1387)->Column#73, funcs:max(Column#1388)->Column#74, funcs:sum(Column#1389)->Column#75, funcs:sum(Column#1390)->Column#76, funcs:min(Column#1391)->Column#77, funcs:max(Column#1392)->Column#78, funcs:sum(Column#1393)->Column#79, funcs:sum(Column#1394)->Column#80, funcs:min(Column#1395)->Column#81, funcs:max(Column#1396)->Column#82, funcs:sum(Column#1397)->Column#83, funcs:sum(Column#1398)->Column#84, funcs:min(Column#1399)->Column#85, funcs:max(Column#1400)->Column#86, funcs:sum(Column#1401)->Column#87, funcs:sum(Column#1402)->Column#88, funcs:min(Column#1403)->Column#89, funcs:max(Column#1404)->Column#90, funcs:sum(Column#1405)->Column#91, funcs:sum(Column#1406)->Column#92, funcs:min(Column#1407)->Column#93, funcs:max(Column#1408)->Column#94, funcs:sum(Column#1409)->Column#95, funcs:sum(Column#1410)->Column#96, funcs:min(Column#1411)->Column#97, funcs:max(Column#1412)->Column#98, funcs:sum(Column#1413)->Column#99, funcs:sum(Column#1414)->Column#100, funcs:min(Column#1415)->Column#101, funcs:max(Column#1416)->Column#102, funcs:sum(Column#1417)->Column#103, funcs:sum(Column#1418)->Column#104, funcs:min(Column#1419)->Column#105, funcs:max(Column#1420)->Column#106, funcs:sum(Column#1421)->Column#107, funcs:sum(Column#1422)->Column#108, funcs:min(Column#1423)->Column#109, funcs:max(Column#1424)->Column#110, funcs:sum(Column#1425)->Column#111, funcs:sum(Column#1426)->Column#112, funcs:min(Column#1427)->Column#113, funcs:max(Column#1428)->Column#114, funcs:sum(Column#1429)->Column#115, funcs:sum(Column#1430)->Column#116, funcs:min(Column#1431)->Column#117, funcs:max(Column#1432)->Column#118, funcs:sum(Column#1433)->Column#119, funcs:sum(Column#1434)->Column#120, funcs:min(Column#1435)->Column#121, funcs:max(Column#1436)->Column#122, funcs:sum(Column#1437)->Column#123, funcs:sum(Column#1438)->Column#124, funcs:min(Column#1439)->Column#125, funcs:max(Column#1440)->Column#126, funcs:sum(Column#1441)->Column#127, funcs:sum(Column#1442)->Column#128, funcs:min(Column#1443)->Column#129, funcs:max(Column#1444)->Column#130, funcs:sum(Column#1445)->Column#131, funcs:sum(Column#1446)->Column#132, funcs:min(Column#1447)->Column#133, funcs:max(Column#1448)->Column#134, funcs:sum(Column#1449)->Column#135, funcs:sum(Column#1450)->Column#136, funcs:min(Column#1451)->Column#137, funcs:max(Column#1452)->Column#138, funcs:sum(Column#1453)->Column#139, funcs:sum(Column#1454)->Column#140, funcs:min(Column#1455)->Column#141, funcs:max(Column#1456)->Column#142, funcs:sum(Column#1457)->Column#143, funcs:sum(Column#1458)->Column#144, funcs:min(Column#1459)->Column#145, funcs:max(Column#1460)->Column#146, funcs:sum(Column#1461)->Column#147, funcs:sum(Column#1462)->Column#148, funcs:min(Column#1463)->Column#149, funcs:max(Column#1464)->Column#150, funcs:sum(Column#1465)->Column#151, funcs:sum(Column#1466)->Column#152, funcs:min(Column#1467)->Column#153, funcs:max(Column#1468)->Column#154, funcs:sum(Column#1469)->Column#155, funcs:sum(Column#1470)->Column#156, funcs:min(Column#1471)->Column#157, funcs:max(Column#1472)->Column#158, funcs:sum(Column#1473)->Column#159, funcs:sum(Column#1474)->Column#160, funcs:min(Column#1475)->Column#161, funcs:max(Column#1476)->Column#162, funcs:sum(Column#1477)->Column#163, funcs:sum(Column#1478)->Column#164, funcs:min(Column#1479)->Column#165, funcs:max(Column#1480)->Column#166, funcs:sum(Column#1481)->Column#167, funcs:sum(Column#1482)->Column#168, funcs:min(Column#1483)->Column#169, funcs:max(Column#1484)->Column#170, funcs:sum(Column#1485)->Column#171, funcs:sum(Column#1486)->Column#172, funcs:min(Column#1487)->Column#173, funcs:max(Column#1488)->Column#174, funcs:sum(Column#1489)->Column#175, funcs:sum(Column#1490)->Column#176, funcs:min(Column#1491)->Column#177, funcs:max(Column#1492)->Column#178, funcs:sum(Column#1493)->Column#179, funcs:sum(Column#1494)->Column#180, funcs:min(Column#1495)->Column#181, funcs:max(Column#1496)->Column#182, funcs:sum(Column#1497)->Column#183, funcs:sum(Column#1498)->Column#184, funcs:min(Column#1499)->Column#185, funcs:max(Column#1500)->Column#186, funcs:sum(Column#1501)->Column#187, funcs:sum(Column#1502)->Column#188, funcs:min(Column#1503)->Column#189, funcs:max(Column#1504)->Column#190, funcs:sum(Column#1505)->Column#191, funcs:sum(Column#1506)->Column#192, funcs:min(Column#1507)->Column#193, funcs:max(Column#1508)->Column#194, funcs:sum(Column#1509)->Column#195, funcs:sum(Column#1510)->Column#196, funcs:min(Column#1511)->Column#197, funcs:max(Column#1512)->Column#198, funcs:sum(Column#1513)->Column#199, funcs:sum(Column#1514)->Column#200, funcs:min(Column#1515)->Column#201, funcs:max(Column#1516)->Column#202, funcs:sum(Column#1517)->Column#203, funcs:sum(Column#1518)->Column#204, funcs:min(Column#1519)->Column#205, funcs:max(Column#1520)->Column#206, funcs:sum(Column#1521)->Column#207, funcs:sum(Column#1522)->Column#208, funcs:min(Column#1523)->Column#209, funcs:max(Column#1524)->Column#210, funcs:count(distinct Column#1525)->Column#211, funcs:count(distinct Column#1526)->Column#212, funcs:count(distinct Column#1527)->Column#213	6.59 MB	0 Bytes
  └─Projection_41	285842.12	119821	root		time:18.2ms, open:84.2µs, close:42.1µs, loops:120, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#1362, intuit_risk.pmt_txn_fact.amount->Column#1363, intuit_risk.pmt_txn_fact.amount->Column#1364, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1365, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1366, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1367, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1368, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1369, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1370, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1371, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1372, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1373, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1374, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1375, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1376, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1377, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1378, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1379, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1380, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1381, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1382, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1383, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1384, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1385, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1386, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1387, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1388, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1389, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1390, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1391, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1392, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1393, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1394, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1395, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1396, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1397, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1398, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1399, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1400, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1401, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1402, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1403, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1404, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1405, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1406, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1407, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1408, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1409, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1410, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1411, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1412, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1413, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1414, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1415, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1416, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1417, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1418, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1419, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1420, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1421, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1422, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1423, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1424, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1425, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1426, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1427, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1428, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1429, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1430, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1431, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1432, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1433, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1434, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1435, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1436, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1437, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1438, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1439, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1440, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1441, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1442, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1443, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1444, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1445, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1446, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1447, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1448, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1449, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1450, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1451, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1452, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1453, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1454, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1455, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1456, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1457, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1458, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1459, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1460, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1461, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1462, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1463, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1464, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1465, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1466, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1467, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1468, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1469, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1470, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1471, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1472, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1473, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1474, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1475, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1476, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1477, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1478, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1479, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1480, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1481, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1482, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1483, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1484, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1485, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1486, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1487, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1488, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1489, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1490, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1491, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1492, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1493, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1494, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1495, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1496, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1497, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1498, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1499, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1500, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1501, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1502, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1503, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1504, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1505, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1506, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1507, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1508, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1509, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1510, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1511, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1512, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1513, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1514, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1515, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1516, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1517, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1518, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1519, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1520, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1521, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1522, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1523, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1524, intuit_risk.pmt_txn_fact.card_type->Column#1525, intuit_risk.pmt_txn_fact.entry_method->Column#1526, intuit_risk.pmt_txn_fact.mt_gateway->Column#1527, intuit_risk.pmt_txn_fact.check_bank_routing_number->Column#1528	33.0 MB	N/A
    └─IndexReader_29	285842.12	119821	root	partition:p20260401,p20260501,p20260601,pmax	time:9.19ms, open:82.7µs, close:11.3µs, loops:120, cop_task: {num: 21, max: 34.1ms, min: 1.03ms, avg: 7.02ms, p95: 18ms, max_proc_keys: 33760, p95_proc_keys: 17376, tot_proc: 90.6ms, tot_wait: 4.38ms, copr_cache: disabled, build_task_duration: 29.6µs, max_distsql_concurrency: 4}, fetch_resp_duration: 6.83ms, rpc_info:{Cop:{num_rpc:21, total_time:147ms}}	index:IndexRangeScan_28	5.97 MB	N/A
      └─IndexRangeScan_28	285842.12	119821	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:20ms, min:0s, avg: 3.33ms, p80:10ms, p95:10ms, iters:193, tasks:21}, scan_detail: {total_process_keys: 119821, total_process_keys_size: 21706797, total_keys: 119842, get_snapshot_time: 3.93ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 90.6ms, total_suspend_time: 218.6µs, total_wait_time: 4.38ms, total_kv_read_wall_time: 70ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  SUM(b.row_count) AS `metric__a_0041`,
  SUM(b.amount_sum) AS `metric__a_0042`,
  MIN(b.amount_min) AS `metric__a_0043`,
  MAX(b.amount_max) AS `metric__a_0044`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `metric__a_1001`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1001`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_sum END) AS `metric__a_1002`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1002`,
  MIN(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_min END) AS `metric__a_1003`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1003`,
  MAX(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_max END) AS `metric__a_1004`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1004`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `metric__a_1013`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1013`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_sum END) AS `metric__a_1014`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1014`,
  MIN(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_min END) AS `metric__a_1015`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1015`,
  MAX(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_max END) AS `metric__a_1016`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1016`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `metric__a_1025`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1025`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_sum END) AS `metric__a_1026`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1026`,
  MIN(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_min END) AS `metric__a_1027`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1027`,
  MAX(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_max END) AS `metric__a_1028`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1028`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `metric__a_1037`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1037`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_sum END) AS `metric__a_1038`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1038`,
  MIN(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_min END) AS `metric__a_1039`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1039`,
  MAX(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_max END) AS `metric__a_1040`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1040`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `metric__a_1049`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1049`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_sum END) AS `metric__a_1050`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1050`,
  MIN(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_min END) AS `metric__a_1051`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1051`,
  MAX(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_max END) AS `metric__a_1052`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1052`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `metric__a_1061`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1061`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_sum END) AS `metric__a_1062`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1062`,
  MIN(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_min END) AS `metric__a_1063`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1063`,
  MAX(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_max END) AS `metric__a_1064`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1064`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `metric__a_1073`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1073`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_sum END) AS `metric__a_1074`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1074`,
  MIN(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_min END) AS `metric__a_1075`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1075`,
  MAX(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_max END) AS `metric__a_1076`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1076`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `metric__a_1089`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1089`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_sum END) AS `metric__a_1090`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1090`,
  MIN(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_min END) AS `metric__a_1091`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1091`,
  MAX(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_max END) AS `metric__a_1092`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1092`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `metric__a_1101`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1101`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.amount_sum END) AS `metric__a_1102`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1102`,
  MIN(CASE WHEN b.transaction_type = 'Void' THEN b.amount_min END) AS `metric__a_1103`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1103`,
  MAX(CASE WHEN b.transaction_type = 'Void' THEN b.amount_max END) AS `metric__a_1104`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1104`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `metric__a_1113`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1113`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_sum END) AS `metric__a_1114`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1114`,
  MIN(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_min END) AS `metric__a_1115`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1115`,
  MAX(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_max END) AS `metric__a_1116`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1116`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `metric__a_1125`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1125`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_sum END) AS `metric__a_1126`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1126`,
  MIN(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_min END) AS `metric__a_1127`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1127`,
  MAX(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_max END) AS `metric__a_1128`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1128`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `metric__a_1137`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1137`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_sum END) AS `metric__a_1138`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1138`,
  MIN(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_min END) AS `metric__a_1139`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1139`,
  MAX(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_max END) AS `metric__a_1140`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1140`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `metric__a_1149`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1149`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_sum END) AS `metric__a_1150`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1150`,
  MIN(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_min END) AS `metric__a_1151`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1151`,
  MAX(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_max END) AS `metric__a_1152`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1152`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `metric__a_1161`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1161`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_sum END) AS `metric__a_1162`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1162`,
  MIN(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_min END) AS `metric__a_1163`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1163`,
  MAX(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_max END) AS `metric__a_1164`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1164`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `metric__a_1173`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1173`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_sum END) AS `metric__a_1174`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1174`,
  MIN(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_min END) AS `metric__a_1175`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1175`,
  MAX(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_max END) AS `metric__a_1176`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1176`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `metric__a_1185`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1185`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_sum END) AS `metric__a_1186`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1186`,
  MIN(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_min END) AS `metric__a_1187`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1187`,
  MAX(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_max END) AS `metric__a_1188`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1188`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `metric__a_1197`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1197`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_sum END) AS `metric__a_1198`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1198`,
  MIN(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_min END) AS `metric__a_1199`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1199`,
  MAX(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_max END) AS `metric__a_1200`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1200`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `metric__a_1209`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1209`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_sum END) AS `metric__a_1210`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1210`,
  MIN(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_min END) AS `metric__a_1211`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1211`,
  MAX(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_max END) AS `metric__a_1212`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1212`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `metric__a_1221`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1221`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_sum END) AS `metric__a_1222`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1222`,
  MIN(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_min END) AS `metric__a_1223`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1223`,
  MAX(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_max END) AS `metric__a_1224`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1224`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `metric__a_1233`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1233`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_sum END) AS `metric__a_1234`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1234`,
  MIN(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_min END) AS `metric__a_1235`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1235`,
  MAX(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_max END) AS `metric__a_1236`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1236`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `metric__a_1245`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1245`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_sum END) AS `metric__a_1246`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1246`,
  MIN(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_min END) AS `metric__a_1247`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1247`,
  MAX(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_max END) AS `metric__a_1248`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1248`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `metric__a_1257`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1257`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_sum END) AS `metric__a_1258`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1258`,
  MIN(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_min END) AS `metric__a_1259`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1259`,
  MAX(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_max END) AS `metric__a_1260`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1260`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `metric__a_1269`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1269`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.amount_sum END) AS `metric__a_1270`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1270`,
  MIN(CASE WHEN b.transaction_type = 'Return' THEN b.amount_min END) AS `metric__a_1271`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1271`,
  MAX(CASE WHEN b.transaction_type = 'Return' THEN b.amount_max END) AS `metric__a_1272`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1272`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `metric__a_1281`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1281`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_sum END) AS `metric__a_1282`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1282`,
  MIN(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_min END) AS `metric__a_1283`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1283`,
  MAX(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_max END) AS `metric__a_1284`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1284`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `metric__a_1293`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1293`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_sum END) AS `metric__a_1294`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1294`,
  MIN(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_min END) AS `metric__a_1295`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1295`,
  MAX(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_max END) AS `metric__a_1296`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1296`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `metric__a_1305`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1305`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_sum END) AS `metric__a_1306`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1306`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_min END) AS `metric__a_1307`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1307`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_max END) AS `metric__a_1308`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1308`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `metric__a_1317`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1317`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_sum END) AS `metric__a_1318`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1318`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_min END) AS `metric__a_1319`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1319`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_max END) AS `metric__a_1320`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1320`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `metric__a_1329`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1329`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.amount_sum END) AS `metric__a_1330`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1330`,
  MIN(CASE WHEN b.card_type = 'VISA' THEN b.amount_min END) AS `metric__a_1331`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1331`,
  MAX(CASE WHEN b.card_type = 'VISA' THEN b.amount_max END) AS `metric__a_1332`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1332`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `metric__a_1341`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1341`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_sum END) AS `metric__a_1342`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1342`,
  MIN(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_min END) AS `metric__a_1343`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1343`,
  MAX(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_max END) AS `metric__a_1344`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1344`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `metric__a_1353`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1353`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.amount_sum END) AS `metric__a_1354`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1354`,
  MIN(CASE WHEN b.card_type = 'CHECK' THEN b.amount_min END) AS `metric__a_1355`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1355`,
  MAX(CASE WHEN b.card_type = 'CHECK' THEN b.amount_max END) AS `metric__a_1356`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1356`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `metric__a_1365`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1365`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.amount_sum END) AS `metric__a_1366`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1366`,
  MIN(CASE WHEN b.card_type = 'AMEX' THEN b.amount_min END) AS `metric__a_1367`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1367`,
  MAX(CASE WHEN b.card_type = 'AMEX' THEN b.amount_max END) AS `metric__a_1368`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1368`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `metric__a_1377`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1377`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_sum END) AS `metric__a_1378`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1378`,
  MIN(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_min END) AS `metric__a_1379`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1379`,
  MAX(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_max END) AS `metric__a_1380`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1380`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `metric__a_1389`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1389`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.amount_sum END) AS `metric__a_1390`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1390`,
  MIN(CASE WHEN b.card_type = 'DINERS' THEN b.amount_min END) AS `metric__a_1391`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1391`,
  MAX(CASE WHEN b.card_type = 'DINERS' THEN b.amount_max END) AS `metric__a_1392`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1392`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `metric__a_1401`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1401`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.amount_sum END) AS `metric__a_1402`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1402`,
  MIN(CASE WHEN b.card_type = 'JCB' THEN b.amount_min END) AS `metric__a_1403`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1403`,
  MAX(CASE WHEN b.card_type = 'JCB' THEN b.amount_max END) AS `metric__a_1404`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1404`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `metric__a_1413`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1413`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_sum END) AS `metric__a_1414`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1414`,
  MIN(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_min END) AS `metric__a_1415`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1415`,
  MAX(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_max END) AS `metric__a_1416`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1416`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `metric__a_1425`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1425`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_sum END) AS `metric__a_1426`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1426`,
  MIN(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_min END) AS `metric__a_1427`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1427`,
  MAX(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_max END) AS `metric__a_1428`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1428`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `metric__a_1437`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1437`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_sum END) AS `metric__a_1438`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1438`,
  MIN(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_min END) AS `metric__a_1439`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1439`,
  MAX(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_max END) AS `metric__a_1440`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1440`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `metric__a_1449`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1449`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_sum END) AS `metric__a_1450`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1450`,
  MIN(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_min END) AS `metric__a_1451`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1451`,
  MAX(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_max END) AS `metric__a_1452`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1452`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `metric__a_1461`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1461`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_sum END) AS `metric__a_1462`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1462`,
  MIN(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_min END) AS `metric__a_1463`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1463`,
  MAX(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_max END) AS `metric__a_1464`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1464`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `metric__a_1473`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1473`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.amount_sum END) AS `metric__a_1474`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1474`,
  MIN(CASE WHEN b.card_type = 'GIFT' THEN b.amount_min END) AS `metric__a_1475`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1475`,
  MAX(CASE WHEN b.card_type = 'GIFT' THEN b.amount_max END) AS `metric__a_1476`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1476`,
  COUNT(DISTINCT b.card_type) AS `metric__a_1891`,
  COUNT(DISTINCT b.entry_method) AS `metric__a_1892`,
  COUNT(DISTINCT b.mt_gateway) AS `metric__a_1893`
FROM (
  SELECT p.mt_gateway, p.transaction_type, p.card_type, p.entry_method, COUNT(*) AS row_count, SUM(p.amount) AS amount_sum, MIN(p.amount) AS amount_min, MAX(p.amount) AS amount_max
  FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1773275781546
  GROUP BY p.mt_gateway, p.transaction_type, p.card_type, p.entry_method
) b
HAVING SUM(b.row_count) > 0;
```

#### Optimized Params

```json
[
  "322271627"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=115.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_9	0.80	1	root		time:69.3ms, open:389.8µs, close:17µs, loops:2, RU:366.08, Concurrency:OFF	Column#51->Column#218, Column#52->Column#219, Column#53->Column#220, Column#54->Column#221, Column#55->Column#222, Column#55->Column#223, Column#56->Column#224, Column#55->Column#225, Column#57->Column#226, Column#55->Column#227, Column#58->Column#228, Column#55->Column#229, Column#59->Column#230, Column#59->Column#231, Column#60->Column#232, Column#59->Column#233, Column#61->Column#234, Column#59->Column#235, Column#62->Column#236, Column#59->Column#237, Column#63->Column#238, Column#63->Column#239, Column#64->Column#240, Column#63->Column#241, Column#65->Column#242, Column#63->Column#243, Column#66->Column#244, Column#63->Column#245, Column#67->Column#246, Column#67->Column#247, Column#68->Column#248, Column#67->Column#249, Column#69->Column#250, Column#67->Column#251, Column#70->Column#252, Column#67->Column#253, Column#71->Column#254, Column#71->Column#255, Column#72->Column#256, Column#71->Column#257, Column#73->Column#258, Column#71->Column#259, Column#74->Column#260, Column#71->Column#261, Column#75->Column#262, Column#75->Column#263, Column#76->Column#264, Column#75->Column#265, Column#77->Column#266, Column#75->Column#267, Column#78->Column#268, Column#75->Column#269, Column#79->Column#270, Column#79->Column#271, Column#80->Column#272, Column#79->Column#273, Column#81->Column#274, Column#79->Column#275, Column#82->Column#276, Column#79->Column#277, Column#83->Column#278, Column#83->Column#279, Column#84->Column#280, Column#83->Column#281, Column#85->Column#282, Column#83->Column#283, Column#86->Column#284, Column#83->Column#285, Column#87->Column#286, Column#87->Column#287, Column#88->Column#288, Column#87->Column#289, Column#89->Column#290, Column#87->Column#291, Column#90->Column#292, Column#87->Column#293, Column#91->Column#294, Column#91->Column#295, Column#92->Column#296, Column#91->Column#297, Column#93->Column#298, Column#91->Column#299, Column#94->Column#300, Column#91->Column#301, Column#95->Column#302, Column#95->Column#303, Column#96->Column#304, Column#95->Column#305, Column#97->Column#306, Column#95->Column#307, Column#98->Column#308, Column#95->Column#309, Column#99->Column#310, Column#99->Column#311, Column#100->Column#312, Column#99->Column#313, Column#101->Column#314, Column#99->Column#315, Column#102->Column#316, Column#99->Column#317, Column#103->Column#318, Column#103->Column#319, Column#104->Column#320, Column#103->Column#321, Column#105->Column#322, Column#103->Column#323, Column#106->Column#324, Column#103->Column#325, Column#107->Column#326, Column#107->Column#327, Column#108->Column#328, Column#107->Column#329, Column#109->Column#330, Column#107->Column#331, Column#110->Column#332, Column#107->Column#333, Column#111->Column#334, Column#111->Column#335, Column#112->Column#336, Column#111->Column#337, Column#113->Column#338, Column#111->Column#339, Column#114->Column#340, Column#111->Column#341, Column#115->Column#342, Column#115->Column#343, Column#116->Column#344, Column#115->Column#345, Column#117->Column#346, Column#115->Column#347, Column#118->Column#348, Column#115->Column#349, Column#119->Column#350, Column#119->Column#351, Column#120->Column#352, Column#119->Column#353, Column#121->Column#354, Column#119->Column#355, Column#122->Column#356, Column#119->Column#357, Column#123->Column#358, Column#123->Column#359, Column#124->Column#360, Column#123->Column#361, Column#125->Column#362, Column#123->Column#363, Column#126->Column#364, Column#123->Column#365, Column#127->Column#366, Column#127->Column#367, Column#128->Column#368, Column#127->Column#369, Column#129->Column#370, Column#127->Column#371, Column#130->Column#372, Column#127->Column#373, Column#131->Column#374, Column#131->Column#375, Column#132->Column#376, Column#131->Column#377, Column#133->Column#378, Column#131->Column#379, Column#134->Column#380, Column#131->Column#381, Column#135->Column#382, Column#135->Column#383, Column#136->Column#384, Column#135->Column#385, Column#137->Column#386, Column#135->Column#387, Column#138->Column#388, Column#135->Column#389, Column#139->Column#390, Column#139->Column#391, Column#140->Column#392, Column#139->Column#393, Column#141->Column#394, Column#139->Column#395, Column#142->Column#396, Column#139->Column#397, Column#143->Column#398, Column#143->Column#399, Column#144->Column#400, Column#143->Column#401, Column#145->Column#402, Column#143->Column#403, Column#146->Column#404, Column#143->Column#405, Column#147->Column#406, Column#147->Column#407, Column#148->Column#408, Column#147->Column#409, Column#149->Column#410, Column#147->Column#411, Column#150->Column#412, Column#147->Column#413, Column#151->Column#414, Column#151->Column#415, Column#152->Column#416, Column#151->Column#417, Column#153->Column#418, Column#151->Column#419, Column#154->Column#420, Column#151->Column#421, Column#155->Column#422, Column#155->Column#423, Column#156->Column#424, Column#155->Column#425, Column#157->Column#426, Column#155->Column#427, Column#158->Column#428, Column#155->Column#429, Column#159->Column#430, Column#159->Column#431, Column#160->Column#432, Column#159->Column#433, Column#161->Column#434, Column#159->Column#435, Column#162->Column#436, Column#159->Column#437, Column#163->Column#438, Column#163->Column#439, Column#164->Column#440, Column#163->Column#441, Column#165->Column#442, Column#163->Column#443, Column#166->Column#444, Column#163->Column#445, Column#167->Column#446, Column#167->Column#447, Column#168->Column#448, Column#167->Column#449, Column#169->Column#450, Column#167->Column#451, Column#170->Column#452, Column#167->Column#453, Column#171->Column#454, Column#171->Column#455, Column#172->Column#456, Column#171->Column#457, Column#173->Column#458, Column#171->Column#459, Column#174->Column#460, Column#171->Column#461, Column#175->Column#462, Column#175->Column#463, Column#176->Column#464, Column#175->Column#465, Column#177->Column#466, Column#175->Column#467, Column#178->Column#468, Column#175->Column#469, Column#179->Column#470, Column#179->Column#471, Column#180->Column#472, Column#179->Column#473, Column#181->Column#474, Column#179->Column#475, Column#182->Column#476, Column#179->Column#477, Column#183->Column#478, Column#183->Column#479, Column#184->Column#480, Column#183->Column#481, Column#185->Column#482, Column#183->Column#483, Column#186->Column#484, Column#183->Column#485, Column#187->Column#486, Column#187->Column#487, Column#188->Column#488, Column#187->Column#489, Column#189->Column#490, Column#187->Column#491, Column#190->Column#492, Column#187->Column#493, Column#191->Column#494, Column#191->Column#495, Column#192->Column#496, Column#191->Column#497, Column#193->Column#498, Column#191->Column#499, Column#194->Column#500, Column#191->Column#501, Column#195->Column#502, Column#195->Column#503, Column#196->Column#504, Column#195->Column#505, Column#197->Column#506, Column#195->Column#507, Column#198->Column#508, Column#195->Column#509, Column#199->Column#510, Column#199->Column#511, Column#200->Column#512, Column#199->Column#513, Column#201->Column#514, Column#199->Column#515, Column#202->Column#516, Column#199->Column#517, Column#203->Column#518, Column#203->Column#519, Column#204->Column#520, Column#203->Column#521, Column#205->Column#522, Column#203->Column#523, Column#206->Column#524, Column#203->Column#525, Column#207->Column#526, Column#207->Column#527, Column#208->Column#528, Column#207->Column#529, Column#209->Column#530, Column#207->Column#531, Column#210->Column#532, Column#207->Column#533, Column#211->Column#534, Column#211->Column#535, Column#212->Column#536, Column#211->Column#537, Column#213->Column#538, Column#211->Column#539, Column#214->Column#540, Column#211->Column#541, Column#215->Column#542, Column#216->Column#543, Column#217->Column#544	231.1 KB	N/A
└─Selection_11	0.80	1	root		time:69ms, open:314.4µs, close:15.3µs, loops:2	gt(Column#51, ?)	231.1 KB	N/A
  └─HashAgg_15	1.00	1	root		time:68.9ms, open:254µs, close:14.6µs, loops:3	funcs:sum(Column#553)->Column#51, funcs:sum(Column#554)->Column#52, funcs:min(Column#555)->Column#53, funcs:max(Column#556)->Column#54, funcs:sum(Column#557)->Column#55, funcs:sum(Column#558)->Column#56, funcs:min(Column#559)->Column#57, funcs:max(Column#560)->Column#58, funcs:sum(Column#561)->Column#59, funcs:sum(Column#562)->Column#60, funcs:min(Column#563)->Column#61, funcs:max(Column#564)->Column#62, funcs:sum(Column#565)->Column#63, funcs:sum(Column#566)->Column#64, funcs:min(Column#567)->Column#65, funcs:max(Column#568)->Column#66, funcs:sum(Column#569)->Column#67, funcs:sum(Column#570)->Column#68, funcs:min(Column#571)->Column#69, funcs:max(Column#572)->Column#70, funcs:sum(Column#573)->Column#71, funcs:sum(Column#574)->Column#72, funcs:min(Column#575)->Column#73, funcs:max(Column#576)->Column#74, funcs:sum(Column#577)->Column#75, funcs:sum(Column#578)->Column#76, funcs:min(Column#579)->Column#77, funcs:max(Column#580)->Column#78, funcs:sum(Column#581)->Column#79, funcs:sum(Column#582)->Column#80, funcs:min(Column#583)->Column#81, funcs:max(Column#584)->Column#82, funcs:sum(Column#585)->Column#83, funcs:sum(Column#586)->Column#84, funcs:min(Column#587)->Column#85, funcs:max(Column#588)->Column#86, funcs:sum(Column#589)->Column#87, funcs:sum(Column#590)->Column#88, funcs:min(Column#591)->Column#89, funcs:max(Column#592)->Column#90, funcs:sum(Column#593)->Column#91, funcs:sum(Column#594)->Column#92, funcs:min(Column#595)->Column#93, funcs:max(Column#596)->Column#94, funcs:sum(Column#597)->Column#95, funcs:sum(Column#598)->Column#96, funcs:min(Column#599)->Column#97, funcs:max(Column#600)->Column#98, funcs:sum(Column#601)->Column#99, funcs:sum(Column#602)->Column#100, funcs:min(Column#603)->Column#101, funcs:max(Column#604)->Column#102, funcs:sum(Column#605)->Column#103, funcs:sum(Column#606)->Column#104, funcs:min(Column#607)->Column#105, funcs:max(Column#608)->Column#106, funcs:sum(Column#609)->Column#107, funcs:sum(Column#610)->Column#108, funcs:min(Column#611)->Column#109, funcs:max(Column#612)->Column#110, funcs:sum(Column#613)->Column#111, funcs:sum(Column#614)->Column#112, funcs:min(Column#615)->Column#113, funcs:max(Column#616)->Column#114, funcs:sum(Column#617)->Column#115, funcs:sum(Column#618)->Column#116, funcs:min(Column#619)->Column#117, funcs:max(Column#620)->Column#118, funcs:sum(Column#621)->Column#119, funcs:sum(Column#622)->Column#120, funcs:min(Column#623)->Column#121, funcs:max(Column#624)->Column#122, funcs:sum(Column#625)->Column#123, funcs:sum(Column#626)->Column#124, funcs:min(Column#627)->Column#125, funcs:max(Column#628)->Column#126, funcs:sum(Column#629)->Column#127, funcs:sum(Column#630)->Column#128, funcs:min(Column#631)->Column#129, funcs:max(Column#632)->Column#130, funcs:sum(Column#633)->Column#131, funcs:sum(Column#634)->Column#132, funcs:min(Column#635)->Column#133, funcs:max(Column#636)->Column#134, funcs:sum(Column#637)->Column#135, funcs:sum(Column#638)->Column#136, funcs:min(Column#639)->Column#137, funcs:max(Column#640)->Column#138, funcs:sum(Column#641)->Column#139, funcs:sum(Column#642)->Column#140, funcs:min(Column#643)->Column#141, funcs:max(Column#644)->Column#142, funcs:sum(Column#645)->Column#143, funcs:sum(Column#646)->Column#144, funcs:min(Column#647)->Column#145, funcs:max(Column#648)->Column#146, funcs:sum(Column#649)->Column#147, funcs:sum(Column#650)->Column#148, funcs:min(Column#651)->Column#149, funcs:max(Column#652)->Column#150, funcs:sum(Column#653)->Column#151, funcs:sum(Column#654)->Column#152, funcs:min(Column#655)->Column#153, funcs:max(Column#656)->Column#154, funcs:sum(Column#657)->Column#155, funcs:sum(Column#658)->Column#156, funcs:min(Column#659)->Column#157, funcs:max(Column#660)->Column#158, funcs:sum(Column#661)->Column#159, funcs:sum(Column#662)->Column#160, funcs:min(Column#663)->Column#161, funcs:max(Column#664)->Column#162, funcs:sum(Column#665)->Column#163, funcs:sum(Column#666)->Column#164, funcs:min(Column#667)->Column#165, funcs:max(Column#668)->Column#166, funcs:sum(Column#669)->Column#167, funcs:sum(Column#670)->Column#168, funcs:min(Column#671)->Column#169, funcs:max(Column#672)->Column#170, funcs:sum(Column#673)->Column#171, funcs:sum(Column#674)->Column#172, funcs:min(Column#675)->Column#173, funcs:max(Column#676)->Column#174, funcs:sum(Column#677)->Column#175, funcs:sum(Column#678)->Column#176, funcs:min(Column#679)->Column#177, funcs:max(Column#680)->Column#178, funcs:sum(Column#681)->Column#179, funcs:sum(Column#682)->Column#180, funcs:min(Column#683)->Column#181, funcs:max(Column#684)->Column#182, funcs:sum(Column#685)->Column#183, funcs:sum(Column#686)->Column#184, funcs:min(Column#687)->Column#185, funcs:max(Column#688)->Column#186, funcs:sum(Column#689)->Column#187, funcs:sum(Column#690)->Column#188, funcs:min(Column#691)->Column#189, funcs:max(Column#692)->Column#190, funcs:sum(Column#693)->Column#191, funcs:sum(Column#694)->Column#192, funcs:min(Column#695)->Column#193, funcs:max(Column#696)->Column#194, funcs:sum(Column#697)->Column#195, funcs:sum(Column#698)->Column#196, funcs:min(Column#699)->Column#197, funcs:max(Column#700)->Column#198, funcs:sum(Column#701)->Column#199, funcs:sum(Column#702)->Column#200, funcs:min(Column#703)->Column#201, funcs:max(Column#704)->Column#202, funcs:sum(Column#705)->Column#203, funcs:sum(Column#706)->Column#204, funcs:min(Column#707)->Column#205, funcs:max(Column#708)->Column#206, funcs:sum(Column#709)->Column#207, funcs:sum(Column#710)->Column#208, funcs:min(Column#711)->Column#209, funcs:max(Column#712)->Column#210, funcs:sum(Column#713)->Column#211, funcs:sum(Column#714)->Column#212, funcs:min(Column#715)->Column#213, funcs:max(Column#716)->Column#214, funcs:count(distinct Column#717)->Column#215, funcs:count(distinct Column#718)->Column#216, funcs:count(distinct Column#719)->Column#217	320.5 KB	0 Bytes
    └─Projection_32	1.00	149	root		time:68.3ms, open:120.3µs, close:13.9µs, loops:5, Concurrency:OFF	cast(Column#47, decimal(20,0) BINARY)->Column#553, Column#48->Column#554, Column#49->Column#555, Column#50->Column#556, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#557, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#558, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#559, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#560, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#561, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#562, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#563, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#564, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#565, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#566, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#567, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#568, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#569, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#570, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#571, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#572, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#573, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#574, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#575, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#576, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#577, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#578, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#579, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#580, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#581, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#582, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#583, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#584, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#585, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#586, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#587, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#588, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#589, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#590, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#591, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#592, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#593, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#594, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#595, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#596, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#597, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#598, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#599, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#600, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#601, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#602, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#603, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#604, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#605, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#606, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#607, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#608, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#609, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#610, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#611, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#612, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#613, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#614, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#615, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#616, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#617, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#618, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#619, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#620, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#621, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#622, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#623, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#624, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#625, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#626, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#627, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#628, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#629, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#630, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#631, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#632, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#633, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#634, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#635, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#636, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#637, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#638, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#639, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#640, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#641, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#642, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#643, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#644, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#645, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#646, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#647, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#648, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#649, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#650, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#651, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#652, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#653, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#654, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#655, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#656, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#657, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#658, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#659, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#660, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#661, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#48)->Column#662, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#49)->Column#663, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), Column#50)->Column#664, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#665, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#666, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#667, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#668, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#669, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#670, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#671, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#672, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#673, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#674, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#675, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#676, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#677, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#678, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#679, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#680, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#681, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#682, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#683, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#684, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#685, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#686, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#687, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#688, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#689, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#690, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#691, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#692, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#693, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#694, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#695, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#696, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#697, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#698, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#699, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#700, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#701, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#702, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#703, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#704, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#705, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#706, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#707, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#708, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#709, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#710, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#711, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#712, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#47, ?), decimal(20,0) BINARY)->Column#713, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#48)->Column#714, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#49)->Column#715, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), Column#50)->Column#716, intuit_risk.pmt_txn_fact.card_type->Column#717, intuit_risk.pmt_txn_fact.entry_method->Column#718, intuit_risk.pmt_txn_fact.mt_gateway->Column#719	12.1 KB	N/A
      └─HashAgg_24	1.00	149	root		time:66.1ms, open:117.3µs, close:13.1µs, loops:5, partial_worker:{wall_time:65.953629ms, concurrency:4, task_num:1, tot_wait:65.735292ms, tot_exec:179.185µs, tot_time:263.721801ms, max:65.934693ms, p95:65.934693ms}, final_worker:{wall_time:66.047459ms, concurrency:4, task_num:4, tot_wait:173.038µs, tot_exec:157ns, tot_time:264.035665ms, max:66.032908ms, p95:66.032908ms}	group by:intuit_risk.pmt_txn_fact.card_type, intuit_risk.pmt_txn_fact.entry_method, intuit_risk.pmt_txn_fact.mt_gateway, intuit_risk.pmt_txn_fact.transaction_type, funcs:count(Column#545)->Column#47, funcs:sum(Column#546)->Column#48, funcs:min(Column#547)->Column#49, funcs:max(Column#548)->Column#50, funcs:firstrow(intuit_risk.pmt_txn_fact.transaction_type)->intuit_risk.pmt_txn_fact.transaction_type, funcs:firstrow(intuit_risk.pmt_txn_fact.mt_gateway)->intuit_risk.pmt_txn_fact.mt_gateway, funcs:firstrow(intuit_risk.pmt_txn_fact.entry_method)->intuit_risk.pmt_txn_fact.entry_method, funcs:firstrow(intuit_risk.pmt_txn_fact.card_type)->intuit_risk.pmt_txn_fact.card_type	207.1 KB	0 Bytes
        └─IndexReader_25	1.00	326	root	partition:p20260401,p20260501,p20260601,pmax	time:65.8ms, open:83.1µs, close:9.92µs, loops:2, cop_task: {num: 5, max: 56.7ms, min: 446.7µs, avg: 20.4ms, p95: 56.7ms, max_proc_keys: 68608, p95_proc_keys: 68608, tot_proc: 97.5ms, tot_wait: 223.7µs, copr_cache: disabled, build_task_duration: 29.7µs, max_distsql_concurrency: 4}, fetch_resp_duration: 65.6ms, rpc_info:{Cop:{num_rpc:5, total_time:101.9ms}}	index:HashAgg_17	43.4 KB	N/A
          └─HashAgg_17	1.00	326	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 18ms, p80:50ms, p95:50ms, iters:120, tasks:5}, scan_detail: {total_process_keys: 119821, total_process_keys_size: 21706797, total_keys: 119826, get_snapshot_time: 109.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 97.5ms, total_suspend_time: 211.1µs, total_wait_time: 223.7µs, total_kv_read_wall_time: 30ms}	group by:intuit_risk.pmt_txn_fact.card_type, intuit_risk.pmt_txn_fact.entry_method, intuit_risk.pmt_txn_fact.mt_gateway, intuit_risk.pmt_txn_fact.transaction_type, funcs:count(?)->Column#545, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#546, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#547, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#548	N/A	N/A
            └─IndexRangeScan_23	285842.12	119821	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:30ms, min:0s, avg: 6ms, p80:30ms, p95:30ms, iters:120, tasks:5}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 2. group_a_bundle_006

- Filter/window: `p.check_bank_routing_number = %s` / `7d`
- Chosen event: `INV0046519149` kind=`hot_check_bank_routing_number` error=`(3024, 'Query execution was interrupted, maximum statement execution time exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 142.7 ms | ok |
| `optimized_default` | `{}` | 137.2 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 134.9 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 140.8 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 310.8 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 312.1 ms | ok |

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
-- explain_analyze_elapsed_ms=142.7
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	12.20	1	root		time:92.1ms, open:240.5µs, close:55.4µs, loops:2, RU:87.67, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#183, Column#186, Column#183, Column#187, Column#187, Column#188, Column#187, Column#189, Column#187, Column#190, Column#187, Column#191, Column#191, Column#192, Column#191, Column#193, Column#191, Column#194, Column#191, Column#195, Column#195, Column#196, Column#195, Column#197, Column#195, Column#198, Column#195, Column#199, Column#199, Column#200, Column#199, Column#201, Column#199, Column#202, Column#199, Column#203, Column#203, Column#204, Column#203, Column#205, Column#203, Column#206, Column#203, Column#207, Column#207, Column#208, Column#207, Column#209, Column#207, Column#210, Column#207, Column#211, Column#212, Column#213	230.1 KB	N/A
└─HashAgg_9	12.20	1	root		time:91.7ms, open:128.6µs, close:53.8µs, loops:2	group by:Column#1528, funcs:count(?)->Column#47, funcs:sum(Column#1362)->Column#48, funcs:min(Column#1363)->Column#49, funcs:max(Column#1364)->Column#50, funcs:sum(Column#1365)->Column#51, funcs:sum(Column#1366)->Column#52, funcs:min(Column#1367)->Column#53, funcs:max(Column#1368)->Column#54, funcs:sum(Column#1369)->Column#55, funcs:sum(Column#1370)->Column#56, funcs:min(Column#1371)->Column#57, funcs:max(Column#1372)->Column#58, funcs:sum(Column#1373)->Column#59, funcs:sum(Column#1374)->Column#60, funcs:min(Column#1375)->Column#61, funcs:max(Column#1376)->Column#62, funcs:sum(Column#1377)->Column#63, funcs:sum(Column#1378)->Column#64, funcs:min(Column#1379)->Column#65, funcs:max(Column#1380)->Column#66, funcs:sum(Column#1381)->Column#67, funcs:sum(Column#1382)->Column#68, funcs:min(Column#1383)->Column#69, funcs:max(Column#1384)->Column#70, funcs:sum(Column#1385)->Column#71, funcs:sum(Column#1386)->Column#72, funcs:min(Column#1387)->Column#73, funcs:max(Column#1388)->Column#74, funcs:sum(Column#1389)->Column#75, funcs:sum(Column#1390)->Column#76, funcs:min(Column#1391)->Column#77, funcs:max(Column#1392)->Column#78, funcs:sum(Column#1393)->Column#79, funcs:sum(Column#1394)->Column#80, funcs:min(Column#1395)->Column#81, funcs:max(Column#1396)->Column#82, funcs:sum(Column#1397)->Column#83, funcs:sum(Column#1398)->Column#84, funcs:min(Column#1399)->Column#85, funcs:max(Column#1400)->Column#86, funcs:sum(Column#1401)->Column#87, funcs:sum(Column#1402)->Column#88, funcs:min(Column#1403)->Column#89, funcs:max(Column#1404)->Column#90, funcs:sum(Column#1405)->Column#91, funcs:sum(Column#1406)->Column#92, funcs:min(Column#1407)->Column#93, funcs:max(Column#1408)->Column#94, funcs:sum(Column#1409)->Column#95, funcs:sum(Column#1410)->Column#96, funcs:min(Column#1411)->Column#97, funcs:max(Column#1412)->Column#98, funcs:sum(Column#1413)->Column#99, funcs:sum(Column#1414)->Column#100, funcs:min(Column#1415)->Column#101, funcs:max(Column#1416)->Column#102, funcs:sum(Column#1417)->Column#103, funcs:sum(Column#1418)->Column#104, funcs:min(Column#1419)->Column#105, funcs:max(Column#1420)->Column#106, funcs:sum(Column#1421)->Column#107, funcs:sum(Column#1422)->Column#108, funcs:min(Column#1423)->Column#109, funcs:max(Column#1424)->Column#110, funcs:sum(Column#1425)->Column#111, funcs:sum(Column#1426)->Column#112, funcs:min(Column#1427)->Column#113, funcs:max(Column#1428)->Column#114, funcs:sum(Column#1429)->Column#115, funcs:sum(Column#1430)->Column#116, funcs:min(Column#1431)->Column#117, funcs:max(Column#1432)->Column#118, funcs:sum(Column#1433)->Column#119, funcs:sum(Column#1434)->Column#120, funcs:min(Column#1435)->Column#121, funcs:max(Column#1436)->Column#122, funcs:sum(Column#1437)->Column#123, funcs:sum(Column#1438)->Column#124, funcs:min(Column#1439)->Column#125, funcs:max(Column#1440)->Column#126, funcs:sum(Column#1441)->Column#127, funcs:sum(Column#1442)->Column#128, funcs:min(Column#1443)->Column#129, funcs:max(Column#1444)->Column#130, funcs:sum(Column#1445)->Column#131, funcs:sum(Column#1446)->Column#132, funcs:min(Column#1447)->Column#133, funcs:max(Column#1448)->Column#134, funcs:sum(Column#1449)->Column#135, funcs:sum(Column#1450)->Column#136, funcs:min(Column#1451)->Column#137, funcs:max(Column#1452)->Column#138, funcs:sum(Column#1453)->Column#139, funcs:sum(Column#1454)->Column#140, funcs:min(Column#1455)->Column#141, funcs:max(Column#1456)->Column#142, funcs:sum(Column#1457)->Column#143, funcs:sum(Column#1458)->Column#144, funcs:min(Column#1459)->Column#145, funcs:max(Column#1460)->Column#146, funcs:sum(Column#1461)->Column#147, funcs:sum(Column#1462)->Column#148, funcs:min(Column#1463)->Column#149, funcs:max(Column#1464)->Column#150, funcs:sum(Column#1465)->Column#151, funcs:sum(Column#1466)->Column#152, funcs:min(Column#1467)->Column#153, funcs:max(Column#1468)->Column#154, funcs:sum(Column#1469)->Column#155, funcs:sum(Column#1470)->Column#156, funcs:min(Column#1471)->Column#157, funcs:max(Column#1472)->Column#158, funcs:sum(Column#1473)->Column#159, funcs:sum(Column#1474)->Column#160, funcs:min(Column#1475)->Column#161, funcs:max(Column#1476)->Column#162, funcs:sum(Column#1477)->Column#163, funcs:sum(Column#1478)->Column#164, funcs:min(Column#1479)->Column#165, funcs:max(Column#1480)->Column#166, funcs:sum(Column#1481)->Column#167, funcs:sum(Column#1482)->Column#168, funcs:min(Column#1483)->Column#169, funcs:max(Column#1484)->Column#170, funcs:sum(Column#1485)->Column#171, funcs:sum(Column#1486)->Column#172, funcs:min(Column#1487)->Column#173, funcs:max(Column#1488)->Column#174, funcs:sum(Column#1489)->Column#175, funcs:sum(Column#1490)->Column#176, funcs:min(Column#1491)->Column#177, funcs:max(Column#1492)->Column#178, funcs:sum(Column#1493)->Column#179, funcs:sum(Column#1494)->Column#180, funcs:min(Column#1495)->Column#181, funcs:max(Column#1496)->Column#182, funcs:sum(Column#1497)->Column#183, funcs:sum(Column#1498)->Column#184, funcs:min(Column#1499)->Column#185, funcs:max(Column#1500)->Column#186, funcs:sum(Column#1501)->Column#187, funcs:sum(Column#1502)->Column#188, funcs:min(Column#1503)->Column#189, funcs:max(Column#1504)->Column#190, funcs:sum(Column#1505)->Column#191, funcs:sum(Column#1506)->Column#192, funcs:min(Column#1507)->Column#193, funcs:max(Column#1508)->Column#194, funcs:sum(Column#1509)->Column#195, funcs:sum(Column#1510)->Column#196, funcs:min(Column#1511)->Column#197, funcs:max(Column#1512)->Column#198, funcs:sum(Column#1513)->Column#199, funcs:sum(Column#1514)->Column#200, funcs:min(Column#1515)->Column#201, funcs:max(Column#1516)->Column#202, funcs:sum(Column#1517)->Column#203, funcs:sum(Column#1518)->Column#204, funcs:min(Column#1519)->Column#205, funcs:max(Column#1520)->Column#206, funcs:sum(Column#1521)->Column#207, funcs:sum(Column#1522)->Column#208, funcs:min(Column#1523)->Column#209, funcs:max(Column#1524)->Column#210, funcs:count(distinct Column#1525)->Column#211, funcs:count(distinct Column#1526)->Column#212, funcs:count(distinct Column#1527)->Column#213	6.49 MB	0 Bytes
  └─Projection_41	138073.00	27634	root		time:11.8ms, open:76.7µs, close:52.7µs, loops:29, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#1362, intuit_risk.pmt_txn_fact.amount->Column#1363, intuit_risk.pmt_txn_fact.amount->Column#1364, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1365, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1366, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1367, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1368, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1369, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1370, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1371, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1372, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1373, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1374, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1375, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1376, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1377, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1378, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1379, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1380, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1381, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1382, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1383, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1384, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1385, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1386, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1387, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1388, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#1389, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1390, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1391, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#1392, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1393, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1394, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1395, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1396, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1397, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1398, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1399, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1400, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1401, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1402, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1403, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1404, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1405, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1406, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1407, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1408, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1409, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1410, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1411, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1412, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1413, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1414, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1415, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1416, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1417, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1418, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1419, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1420, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1421, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1422, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1423, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1424, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1425, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1426, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1427, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1428, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1429, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1430, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1431, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1432, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1433, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1434, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1435, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1436, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1437, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1438, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1439, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1440, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1441, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1442, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1443, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1444, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1445, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1446, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1447, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1448, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1449, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1450, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1451, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1452, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1453, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1454, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1455, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1456, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1457, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1458, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1459, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1460, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1461, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1462, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1463, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1464, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1465, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1466, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1467, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1468, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1469, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1470, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1471, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1472, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1473, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1474, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1475, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1476, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1477, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1478, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1479, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1480, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1481, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1482, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1483, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1484, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1485, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1486, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1487, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1488, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1489, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1490, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1491, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1492, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1493, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1494, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1495, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1496, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1497, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1498, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1499, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1500, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1501, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1502, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1503, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1504, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1505, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1506, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1507, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1508, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1509, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1510, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1511, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1512, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1513, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1514, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1515, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1516, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1517, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1518, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1519, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1520, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1521, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1522, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1523, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1524, intuit_risk.pmt_txn_fact.card_type->Column#1525, intuit_risk.pmt_txn_fact.entry_method->Column#1526, intuit_risk.pmt_txn_fact.mt_gateway->Column#1527, intuit_risk.pmt_txn_fact.check_bank_routing_number->Column#1528	32.9 MB	N/A
    └─IndexReader_29	138073.00	27634	root	partition:p20260501,p20260601,pmax	time:10.1ms, open:75.6µs, close:10.8µs, loops:29, cop_task: {num: 10, max: 9.32ms, min: 398.7µs, avg: 3.27ms, p95: 9.32ms, max_proc_keys: 9184, p95_proc_keys: 9184, tot_proc: 19.6ms, tot_wait: 325µs, copr_cache: disabled, build_task_duration: 25.9µs, max_distsql_concurrency: 3}, fetch_resp_duration: 9.38ms, rpc_info:{Cop:{num_rpc:10, total_time:32.6ms}}	index:IndexRangeScan_28	1.76 MB	N/A
      └─IndexRangeScan_28	138073.00	27634	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:60, tasks:10}, scan_detail: {total_process_keys: 27634, total_process_keys_size: 5005030, total_keys: 27644, get_snapshot_time: 141.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 19.6ms, total_suspend_time: 45.5µs, total_wait_time: 325µs}	range:[? ?,? +inf], keep order:false	N/A	N/A
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
-- explain_analyze_elapsed_ms=134.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:89ms, open:346.8µs, close:54.7µs, loops:2, RU:87.88, Concurrency:OFF	Column#47->Column#214, Column#48->Column#215, Column#49->Column#216, Column#50->Column#217, Column#51->Column#218, Column#51->Column#219, Column#52->Column#220, Column#51->Column#221, Column#53->Column#222, Column#51->Column#223, Column#54->Column#224, Column#51->Column#225, Column#55->Column#226, Column#55->Column#227, Column#56->Column#228, Column#55->Column#229, Column#57->Column#230, Column#55->Column#231, Column#58->Column#232, Column#55->Column#233, Column#59->Column#234, Column#59->Column#235, Column#60->Column#236, Column#59->Column#237, Column#61->Column#238, Column#59->Column#239, Column#62->Column#240, Column#59->Column#241, Column#63->Column#242, Column#63->Column#243, Column#64->Column#244, Column#63->Column#245, Column#65->Column#246, Column#63->Column#247, Column#66->Column#248, Column#63->Column#249, Column#67->Column#250, Column#67->Column#251, Column#68->Column#252, Column#67->Column#253, Column#69->Column#254, Column#67->Column#255, Column#70->Column#256, Column#67->Column#257, Column#71->Column#258, Column#71->Column#259, Column#72->Column#260, Column#71->Column#261, Column#73->Column#262, Column#71->Column#263, Column#74->Column#264, Column#71->Column#265, Column#75->Column#266, Column#75->Column#267, Column#76->Column#268, Column#75->Column#269, Column#77->Column#270, Column#75->Column#271, Column#78->Column#272, Column#75->Column#273, Column#79->Column#274, Column#79->Column#275, Column#80->Column#276, Column#79->Column#277, Column#81->Column#278, Column#79->Column#279, Column#82->Column#280, Column#79->Column#281, Column#83->Column#282, Column#83->Column#283, Column#84->Column#284, Column#83->Column#285, Column#85->Column#286, Column#83->Column#287, Column#86->Column#288, Column#83->Column#289, Column#87->Column#290, Column#87->Column#291, Column#88->Column#292, Column#87->Column#293, Column#89->Column#294, Column#87->Column#295, Column#90->Column#296, Column#87->Column#297, Column#91->Column#298, Column#91->Column#299, Column#92->Column#300, Column#91->Column#301, Column#93->Column#302, Column#91->Column#303, Column#94->Column#304, Column#91->Column#305, Column#95->Column#306, Column#95->Column#307, Column#96->Column#308, Column#95->Column#309, Column#97->Column#310, Column#95->Column#311, Column#98->Column#312, Column#95->Column#313, Column#99->Column#314, Column#99->Column#315, Column#100->Column#316, Column#99->Column#317, Column#101->Column#318, Column#99->Column#319, Column#102->Column#320, Column#99->Column#321, Column#103->Column#322, Column#103->Column#323, Column#104->Column#324, Column#103->Column#325, Column#105->Column#326, Column#103->Column#327, Column#106->Column#328, Column#103->Column#329, Column#107->Column#330, Column#107->Column#331, Column#108->Column#332, Column#107->Column#333, Column#109->Column#334, Column#107->Column#335, Column#110->Column#336, Column#107->Column#337, Column#111->Column#338, Column#111->Column#339, Column#112->Column#340, Column#111->Column#341, Column#113->Column#342, Column#111->Column#343, Column#114->Column#344, Column#111->Column#345, Column#115->Column#346, Column#115->Column#347, Column#116->Column#348, Column#115->Column#349, Column#117->Column#350, Column#115->Column#351, Column#118->Column#352, Column#115->Column#353, Column#119->Column#354, Column#119->Column#355, Column#120->Column#356, Column#119->Column#357, Column#121->Column#358, Column#119->Column#359, Column#122->Column#360, Column#119->Column#361, Column#123->Column#362, Column#123->Column#363, Column#124->Column#364, Column#123->Column#365, Column#125->Column#366, Column#123->Column#367, Column#126->Column#368, Column#123->Column#369, Column#127->Column#370, Column#127->Column#371, Column#128->Column#372, Column#127->Column#373, Column#129->Column#374, Column#127->Column#375, Column#130->Column#376, Column#127->Column#377, Column#131->Column#378, Column#131->Column#379, Column#132->Column#380, Column#131->Column#381, Column#133->Column#382, Column#131->Column#383, Column#134->Column#384, Column#131->Column#385, Column#135->Column#386, Column#135->Column#387, Column#136->Column#388, Column#135->Column#389, Column#137->Column#390, Column#135->Column#391, Column#138->Column#392, Column#135->Column#393, Column#139->Column#394, Column#139->Column#395, Column#140->Column#396, Column#139->Column#397, Column#141->Column#398, Column#139->Column#399, Column#142->Column#400, Column#139->Column#401, Column#143->Column#402, Column#143->Column#403, Column#144->Column#404, Column#143->Column#405, Column#145->Column#406, Column#143->Column#407, Column#146->Column#408, Column#143->Column#409, Column#147->Column#410, Column#147->Column#411, Column#148->Column#412, Column#147->Column#413, Column#149->Column#414, Column#147->Column#415, Column#150->Column#416, Column#147->Column#417, Column#151->Column#418, Column#151->Column#419, Column#152->Column#420, Column#151->Column#421, Column#153->Column#422, Column#151->Column#423, Column#154->Column#424, Column#151->Column#425, Column#155->Column#426, Column#155->Column#427, Column#156->Column#428, Column#155->Column#429, Column#157->Column#430, Column#155->Column#431, Column#158->Column#432, Column#155->Column#433, Column#159->Column#434, Column#159->Column#435, Column#160->Column#436, Column#159->Column#437, Column#161->Column#438, Column#159->Column#439, Column#162->Column#440, Column#159->Column#441, Column#163->Column#442, Column#163->Column#443, Column#164->Column#444, Column#163->Column#445, Column#165->Column#446, Column#163->Column#447, Column#166->Column#448, Column#163->Column#449, Column#167->Column#450, Column#167->Column#451, Column#168->Column#452, Column#167->Column#453, Column#169->Column#454, Column#167->Column#455, Column#170->Column#456, Column#167->Column#457, Column#171->Column#458, Column#171->Column#459, Column#172->Column#460, Column#171->Column#461, Column#173->Column#462, Column#171->Column#463, Column#174->Column#464, Column#171->Column#465, Column#175->Column#466, Column#175->Column#467, Column#176->Column#468, Column#175->Column#469, Column#177->Column#470, Column#175->Column#471, Column#178->Column#472, Column#175->Column#473, Column#179->Column#474, Column#179->Column#475, Column#180->Column#476, Column#179->Column#477, Column#181->Column#478, Column#179->Column#479, Column#182->Column#480, Column#179->Column#481, Column#183->Column#482, Column#183->Column#483, Column#184->Column#484, Column#183->Column#485, Column#185->Column#486, Column#183->Column#487, Column#186->Column#488, Column#183->Column#489, Column#187->Column#490, Column#187->Column#491, Column#188->Column#492, Column#187->Column#493, Column#189->Column#494, Column#187->Column#495, Column#190->Column#496, Column#187->Column#497, Column#191->Column#498, Column#191->Column#499, Column#192->Column#500, Column#191->Column#501, Column#193->Column#502, Column#191->Column#503, Column#194->Column#504, Column#191->Column#505, Column#195->Column#506, Column#195->Column#507, Column#196->Column#508, Column#195->Column#509, Column#197->Column#510, Column#195->Column#511, Column#198->Column#512, Column#195->Column#513, Column#199->Column#514, Column#199->Column#515, Column#200->Column#516, Column#199->Column#517, Column#201->Column#518, Column#199->Column#519, Column#202->Column#520, Column#199->Column#521, Column#203->Column#522, Column#203->Column#523, Column#204->Column#524, Column#203->Column#525, Column#205->Column#526, Column#203->Column#527, Column#206->Column#528, Column#203->Column#529, Column#207->Column#530, Column#207->Column#531, Column#208->Column#532, Column#207->Column#533, Column#209->Column#534, Column#207->Column#535, Column#210->Column#536, Column#207->Column#537, Column#211->Column#538, Column#212->Column#539, Column#213->Column#540	230.1 KB	N/A
└─Selection_9	0.80	1	root		time:88.6ms, open:262.7µs, close:52.4µs, loops:2	gt(Column#47, ?)	230.1 KB	N/A
  └─HashAgg_13	1.00	1	root		time:88.5ms, open:185.4µs, close:51.4µs, loops:3	funcs:count(?)->Column#47, funcs:sum(Column#869)->Column#48, funcs:min(Column#870)->Column#49, funcs:max(Column#871)->Column#50, funcs:sum(Column#872)->Column#51, funcs:sum(Column#873)->Column#52, funcs:min(Column#874)->Column#53, funcs:max(Column#875)->Column#54, funcs:sum(Column#876)->Column#55, funcs:sum(Column#877)->Column#56, funcs:min(Column#878)->Column#57, funcs:max(Column#879)->Column#58, funcs:sum(Column#880)->Column#59, funcs:sum(Column#881)->Column#60, funcs:min(Column#882)->Column#61, funcs:max(Column#883)->Column#62, funcs:sum(Column#884)->Column#63, funcs:sum(Column#885)->Column#64, funcs:min(Column#886)->Column#65, funcs:max(Column#887)->Column#66, funcs:sum(Column#888)->Column#67, funcs:sum(Column#889)->Column#68, funcs:min(Column#890)->Column#69, funcs:max(Column#891)->Column#70, funcs:sum(Column#892)->Column#71, funcs:sum(Column#893)->Column#72, funcs:min(Column#894)->Column#73, funcs:max(Column#895)->Column#74, funcs:sum(Column#896)->Column#75, funcs:sum(Column#897)->Column#76, funcs:min(Column#898)->Column#77, funcs:max(Column#899)->Column#78, funcs:sum(Column#900)->Column#79, funcs:sum(Column#901)->Column#80, funcs:min(Column#902)->Column#81, funcs:max(Column#903)->Column#82, funcs:sum(Column#904)->Column#83, funcs:sum(Column#905)->Column#84, funcs:min(Column#906)->Column#85, funcs:max(Column#907)->Column#86, funcs:sum(Column#908)->Column#87, funcs:sum(Column#909)->Column#88, funcs:min(Column#910)->Column#89, funcs:max(Column#911)->Column#90, funcs:sum(Column#912)->Column#91, funcs:sum(Column#913)->Column#92, funcs:min(Column#914)->Column#93, funcs:max(Column#915)->Column#94, funcs:sum(Column#916)->Column#95, funcs:sum(Column#917)->Column#96, funcs:min(Column#918)->Column#97, funcs:max(Column#919)->Column#98, funcs:sum(Column#920)->Column#99, funcs:sum(Column#921)->Column#100, funcs:min(Column#922)->Column#101, funcs:max(Column#923)->Column#102, funcs:sum(Column#924)->Column#103, funcs:sum(Column#925)->Column#104, funcs:min(Column#926)->Column#105, funcs:max(Column#927)->Column#106, funcs:sum(Column#928)->Column#107, funcs:sum(Column#929)->Column#108, funcs:min(Column#930)->Column#109, funcs:max(Column#931)->Column#110, funcs:sum(Column#932)->Column#111, funcs:sum(Column#933)->Column#112, funcs:min(Column#934)->Column#113, funcs:max(Column#935)->Column#114, funcs:sum(Column#936)->Column#115, funcs:sum(Column#937)->Column#116, funcs:min(Column#938)->Column#117, funcs:max(Column#939)->Column#118, funcs:sum(Column#940)->Column#119, funcs:sum(Column#941)->Column#120, funcs:min(Column#942)->Column#121, funcs:max(Column#943)->Column#122, funcs:sum(Column#944)->Column#123, funcs:sum(Column#945)->Column#124, funcs:min(Column#946)->Column#125, funcs:max(Column#947)->Column#126, funcs:sum(Column#948)->Column#127, funcs:sum(Column#949)->Column#128, funcs:min(Column#950)->Column#129, funcs:max(Column#951)->Column#130, funcs:sum(Column#952)->Column#131, funcs:sum(Column#953)->Column#132, funcs:min(Column#954)->Column#133, funcs:max(Column#955)->Column#134, funcs:sum(Column#956)->Column#135, funcs:sum(Column#957)->Column#136, funcs:min(Column#958)->Column#137, funcs:max(Column#959)->Column#138, funcs:sum(Column#960)->Column#139, funcs:sum(Column#961)->Column#140, funcs:min(Column#962)->Column#141, funcs:max(Column#963)->Column#142, funcs:sum(Column#964)->Column#143, funcs:sum(Column#965)->Column#144, funcs:min(Column#966)->Column#145, funcs:max(Column#967)->Column#146, funcs:sum(Column#968)->Column#147, funcs:sum(Column#969)->Column#148, funcs:min(Column#970)->Column#149, funcs:max(Column#971)->Column#150, funcs:sum(Column#972)->Column#151, funcs:sum(Column#973)->Column#152, funcs:min(Column#974)->Column#153, funcs:max(Column#975)->Column#154, funcs:sum(Column#976)->Column#155, funcs:sum(Column#977)->Column#156, funcs:min(Column#978)->Column#157, funcs:max(Column#979)->Column#158, funcs:sum(Column#980)->Column#159, funcs:sum(Column#981)->Column#160, funcs:min(Column#982)->Column#161, funcs:max(Column#983)->Column#162, funcs:sum(Column#984)->Column#163, funcs:sum(Column#985)->Column#164, funcs:min(Column#986)->Column#165, funcs:max(Column#987)->Column#166, funcs:sum(Column#988)->Column#167, funcs:sum(Column#989)->Column#168, funcs:min(Column#990)->Column#169, funcs:max(Column#991)->Column#170, funcs:sum(Column#992)->Column#171, funcs:sum(Column#993)->Column#172, funcs:min(Column#994)->Column#173, funcs:max(Column#995)->Column#174, funcs:sum(Column#996)->Column#175, funcs:sum(Column#997)->Column#176, funcs:min(Column#998)->Column#177, funcs:max(Column#999)->Column#178, funcs:sum(Column#1000)->Column#179, funcs:sum(Column#1001)->Column#180, funcs:min(Column#1002)->Column#181, funcs:max(Column#1003)->Column#182, funcs:sum(Column#1004)->Column#183, funcs:sum(Column#1005)->Column#184, funcs:min(Column#1006)->Column#185, funcs:max(Column#1007)->Column#186, funcs:sum(Column#1008)->Column#187, funcs:sum(Column#1009)->Column#188, funcs:min(Column#1010)->Column#189, funcs:max(Column#1011)->Column#190, funcs:sum(Column#1012)->Column#191, funcs:sum(Column#1013)->Column#192, funcs:min(Column#1014)->Column#193, funcs:max(Column#1015)->Column#194, funcs:sum(Column#1016)->Column#195, funcs:sum(Column#1017)->Column#196, funcs:min(Column#1018)->Column#197, funcs:max(Column#1019)->Column#198, funcs:sum(Column#1020)->Column#199, funcs:sum(Column#1021)->Column#200, funcs:min(Column#1022)->Column#201, funcs:max(Column#1023)->Column#202, funcs:sum(Column#1024)->Column#203, funcs:sum(Column#1025)->Column#204, funcs:min(Column#1026)->Column#205, funcs:max(Column#1027)->Column#206, funcs:sum(Column#1028)->Column#207, funcs:sum(Column#1029)->Column#208, funcs:min(Column#1030)->Column#209, funcs:max(Column#1031)->Column#210, funcs:count(distinct Column#1032)->Column#211, funcs:count(distinct Column#1033)->Column#212, funcs:count(distinct Column#1034)->Column#213	6.47 MB	0 Bytes
    └─Projection_28	138073.00	27634	root		time:11.1ms, open:81.7µs, close:50.2µs, loops:29, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#869, intuit_risk.pmt_txn_fact.amount->Column#870, intuit_risk.pmt_txn_fact.amount->Column#871, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#872, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#873, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#874, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#875, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#876, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#877, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#878, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#879, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#880, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#881, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#882, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#883, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#884, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#885, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#886, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#887, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#888, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#889, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#890, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#891, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#892, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#893, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#894, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#895, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?), decimal(20,0) BINARY)->Column#896, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#897, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#898, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount)->Column#899, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#900, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#901, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#902, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#903, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#904, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#905, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#906, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#907, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#908, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#909, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#910, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#911, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#912, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#913, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#914, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#915, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#916, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#917, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#918, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#919, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#920, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#921, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#922, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#923, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#924, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#925, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#926, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#927, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#928, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#929, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#930, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#931, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#932, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#933, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#934, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#935, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#936, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#937, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#938, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#939, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#940, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#941, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#942, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#943, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#944, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#945, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#946, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#947, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#948, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#949, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#950, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#951, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#952, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#953, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#954, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#955, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#956, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#957, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#958, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#959, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#960, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#961, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#962, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#963, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#964, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#965, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#966, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#967, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#968, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#969, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#970, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#971, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#972, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#973, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#974, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#975, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#976, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#977, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#978, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#979, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#980, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#981, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#982, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#983, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#984, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#985, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#986, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#987, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#988, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#989, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#990, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#991, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#992, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#993, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#994, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#995, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#996, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#997, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#998, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#999, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1000, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1001, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1002, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1003, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1004, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1005, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1006, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1007, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1008, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1009, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1010, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1011, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1012, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1013, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1014, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1015, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1016, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1017, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1018, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1019, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1020, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1021, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1022, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1023, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1024, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1025, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1026, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1027, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#1028, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1029, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1030, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#1031, intuit_risk.pmt_txn_fact.card_type->Column#1032, intuit_risk.pmt_txn_fact.entry_method->Column#1033, intuit_risk.pmt_txn_fact.mt_gateway->Column#1034	32.8 MB	N/A
      └─IndexReader_21	138073.00	27634	root	partition:p20260501,p20260601,pmax	time:9.33ms, open:80.2µs, close:11.3µs, loops:29, cop_task: {num: 10, max: 8.45ms, min: 445.8µs, avg: 3.11ms, p95: 8.45ms, max_proc_keys: 9184, p95_proc_keys: 9184, tot_proc: 20.3ms, tot_wait: 300.9µs, copr_cache: disabled, build_task_duration: 26.3µs, max_distsql_concurrency: 3}, fetch_resp_duration: 8.64ms, rpc_info:{Cop:{num_rpc:10, total_time:30.9ms}}	index:IndexRangeScan_20	1.76 MB	N/A
        └─IndexRangeScan_20	138073.00	27634	cop[tikv]	table:p, index:idx_pmt_routing_runtime_cov(check_bank_routing_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 3ms, p80:10ms, p95:10ms, iters:60, tasks:10}, scan_detail: {total_process_keys: 27634, total_process_keys_size: 5005030, total_keys: 27644, get_snapshot_time: 126.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 20.3ms, total_suspend_time: 43.8µs, total_wait_time: 300.9µs, total_kv_read_wall_time: 30ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 3. group_c_bundle_025

- Filter/window: `p.merchant_account_number = %s` / `180d`
- Chosen event: `INV0007318468` kind=`normal` error=`(1105, "other error for mpp stream: Code: 0, e.displayText() = DB::Exception: Memory limit (total) exceeded caused by 'RSS(Resident Set Size) much larger than limit' : process memory size would be 4.76 GiB for (attempt to allocate chunk of 1602419 bytes), limit of memory for data computing : 3.76 Gi`
- Optimization: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Index: use payment-side covering join index to avoid p table row lookup

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 6095.6 ms | ok |
| `optimized_default` | `{}` | 136.4 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 352.8 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 176.1 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 148.5 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 146.2 ms | ok |

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
-- explain_analyze_elapsed_ms=6095.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_1024	1.00	1	root		time:11.5µs, open:3.79µs, close:1.29µs, loops:2, RU:4865.83, Concurrency:OFF	?->Column#1756, ?->Column#1914, ?->Column#2066, ?->Column#2220, ?->Column#2424, ?->Column#2648, ?->Column#2832	0 Bytes	N/A
└─TableDual_1026	1.00	1	root		time:1.91µs, open:321ns, close:175ns, loops:2	rows:1	N/A	N/A
ScalarSubQuery_240	N/A	0	root			Output: ScalarQueryCol#1755	N/A	N/A
└─MaxOneRow_138	1.00	1	root		time:1.49s, open:10.1µs, close:28µs, loops:1		N/A	N/A
  └─HashAgg_143	1.00	1	root		time:1.49s, open:9.33µs, close:27.5µs, loops:2	funcs:count(distinct Column#1711)->Column#1712	384.6 KB	0 Bytes
    └─Union_147	10626.55	3755	root		time:1.49s, open:883ns, close:26.9µs, loops:7		N/A	N/A
      ├─Projection_149	66.33	3749	root		time:29.5ms, open:84.3µs, close:9.05µs, loops:6, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1711	146.4 KB	N/A
      │ └─IndexReader_153	66.33	3749	root		time:29.3ms, open:81.8µs, close:6.08µs, loops:6, cop_task: {num: 5, max: 17.7ms, min: 913.3µs, avg: 5.94ms, p95: 17.7ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 16.7ms, tot_wait: 1.62ms, copr_cache: disabled, build_task_duration: 33.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 29ms, rpc_info:{Cop:{num_rpc:5, total_time:29.6ms}}	index:Selection_152	377.9 KB	N/A
      │   └─Selection_152	66.33	3749	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:20, tasks:5}, scan_detail: {total_process_keys: 3749, total_process_keys_size: 1075963, total_keys: 3754, get_snapshot_time: 1.52ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 16.7ms, total_suspend_time: 24.1µs, total_wait_time: 1.62ms, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_151	66.43	3749	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:20, tasks:5}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_154	10560.23	6	root		time:1.49s, open:124.6µs, close:16.8µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1711	45.2 KB	N/A
        └─IndexHashJoin_164	10560.23	6	root		time:1.49s, open:123.4µs, close:4.84µs, loops:2, inner:{total:2.89s, concurrency:5, task:2, construct:3.1ms, fetch:2.88s, build:671.3µs, join:4.93ms}	inner join, inner:IndexLookUp_180, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.07 MB	N/A
          ├─IndexReader_175(Build)	5970.05	5192	root	partition:all	time:11.7ms, open:120.7µs, close:2.87µs, loops:8, cop_task: {num: 21, max: 7.54ms, min: 505.1µs, avg: 2.18ms, p95: 5.6ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 17ms, tot_wait: 9.69ms, copr_cache: disabled, build_task_duration: 66.6µs, max_distsql_concurrency: 9}, fetch_resp_duration: 11.3ms, rpc_info:{Cop:{num_rpc:21, total_time:45.6ms}}	index:Selection_174	36.1 KB	N/A
          │ └─Selection_174	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 9.29ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 17ms, total_suspend_time: 21.2µs, total_wait_time: 9.69ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_173	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_180(Probe)	10560.23	3752	root	partition:all	total_time:2.88s, total_open:14.4ms, total_close:14.7µs, loops:7, index_task: {total_time: 2.63s, fetch_handle: 2.63s, build: 12.5µs, wait: 31.7µs}, table_task: {total_time: 748.7ms, num: 12, concurrency: 5}, next: {wait_index: 2.64s, wait_table_lookup_build: 637.5µs, wait_table_lookup_resp: 226.6ms}		3.84 MB	N/A
            ├─Selection_178(Build)	13952.57	5192	cop[tikv]		total_time:2.64s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 1.38s, min: 3.56ms, avg: 255.6ms, p95: 1.26s, max_proc_keys: 770, p95_proc_keys: 683, tot_proc: 3.98s, tot_wait: 9.33ms, copr_cache: disabled, build_task_duration: 3.68ms, max_distsql_concurrency: 3}, fetch_resp_duration: 2.64s, rpc_info:{Cop:{num_rpc:24, total_time:6.13s}}, tikv_task:{proc max:1.38s, min:0s, avg: 166.3ms, p80:130ms, p95:1.26s, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 522774, total_keys: 29830, get_snapshot_time: 9.53ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.98s, total_suspend_time: 3.65ms, total_wait_time: 9.33ms, total_kv_read_wall_time: 3.83s}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_176	20599.13	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:1.38s, min:0s, avg: 166.3ms, p80:130ms, p95:1.26s, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_179(Probe)	10560.23	3752	cop[tikv]		total_time:744.3ms, total_open:0s, total_close:61.9µs, loops:24, cop_task: {num: 904, max: 71.3ms, min: 0s, avg: 2.43ms, p95: 18ms, max_proc_keys: 32, p95_proc_keys: 17, tot_proc: 2.33s, tot_wait: 1.26s, copr_cache: disabled, build_task_duration: 2.23ms, max_distsql_concurrency: 2, max_extra_concurrency: 9, store_batch_num: 637, store_batch_fallback_num: 64}, fetch_resp_duration: 740.9ms, rpc_info:{Cop:{num_rpc:321, total_time:2.35s}, rpc_errors:{bucket_version_not_match:54}}, backoff{regionMiss: 336ms}, tikv_task:{proc max:40ms, min:0s, avg: 2.61ms, p80:10ms, p95:10ms, iters:905, tasks:904}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 897.7ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.33s, total_suspend_time: 60.6ms, total_wait_time: 1.26s, total_kv_read_wall_time: 2.36s}	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	N/A	N/A
              └─TableRowIDScan_177	13952.57	5192	cop[tikv]	table:d	tikv_task:{proc max:40ms, min:0s, avg: 2.61ms, p80:10ms, p95:10ms, iters:905, tasks:904}	keep order:false	N/A	N/A
ScalarSubQuery_360	N/A	0	root			Output: ScalarQueryCol#1913	N/A	N/A
└─MaxOneRow_258	1.00	1	root		time:1.17s, open:8.3µs, close:27µs, loops:1		N/A	N/A
  └─HashAgg_263	1.00	1	root		time:1.17s, open:7.53µs, close:26.6µs, loops:2	funcs:count(distinct Column#1871)->Column#1872	384.3 KB	0 Bytes
    └─Union_267	10626.69	3708	root		time:1.17s, open:978ns, close:25.8µs, loops:6		N/A	N/A
      ├─Projection_269	66.46	3702	root		time:19.4ms, open:81.1µs, close:9.18µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1871	146.4 KB	N/A
      │ └─IndexReader_273	66.46	3702	root		time:19.2ms, open:73.4µs, close:6.09µs, loops:5, cop_task: {num: 4, max: 7.56ms, min: 2.66ms, avg: 4.79ms, p95: 7.56ms, max_proc_keys: 2006, p95_proc_keys: 2006, tot_proc: 12.7ms, tot_wait: 946.6µs, copr_cache: disabled, build_task_duration: 25.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 19ms, rpc_info:{Cop:{num_rpc:4, total_time:19.1ms}}	index:Selection_272	376.3 KB	N/A
      │   └─Selection_272	66.46	3702	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3702, total_process_keys_size: 1062474, total_keys: 3706, get_snapshot_time: 879.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 12.7ms, total_suspend_time: 23.9µs, total_wait_time: 946.6µs, total_kv_read_wall_time: 20ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_271	66.57	3702	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_274	10560.23	6	root		time:1.17s, open:114.3µs, close:16µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1871	45.2 KB	N/A
        └─IndexHashJoin_284	10560.23	6	root		time:1.17s, open:113.1µs, close:5.18µs, loops:2, inner:{total:2.29s, concurrency:5, task:2, construct:3.12ms, fetch:2.28s, build:649.9µs, join:4.72ms}	inner join, inner:IndexLookUp_300, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.09 MB	N/A
          ├─IndexReader_295(Build)	5970.05	5192	root	partition:all	time:4.83ms, open:108.2µs, close:2.68µs, loops:8, cop_task: {num: 21, max: 1.73ms, min: 374.4µs, avg: 924.6µs, p95: 1.65ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 6.72ms, tot_wait: 556.9µs, copr_cache: disabled, build_task_duration: 55.9µs, max_distsql_concurrency: 9}, fetch_resp_duration: 4.49ms, rpc_info:{Cop:{num_rpc:21, total_time:19.2ms}}	index:Selection_294	41.3 KB	N/A
          │ └─Selection_294	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 245.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 6.72ms, total_wait_time: 556.9µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_293	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_300(Probe)	10560.23	3705	root	partition:all	total_time:2.28s, total_open:14.6ms, total_close:14.7µs, loops:7, index_task: {total_time: 2.2s, fetch_handle: 2.2s, build: 9.82µs, wait: 24.5µs}, table_task: {total_time: 134.8ms, num: 12, concurrency: 5}, next: {wait_index: 2.2s, wait_table_lookup_build: 1.61ms, wait_table_lookup_resp: 59.2ms}		3.85 MB	N/A
            ├─Selection_298(Build)	14274.48	5192	cop[tikv]		total_time:2.23s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 1.14s, min: 2.47ms, avg: 510.9ms, p95: 1.1s, max_proc_keys: 742, p95_proc_keys: 681, tot_proc: 946.2ms, tot_wait: 287.5µs, copr_cache: disabled, build_task_duration: 3.4ms, max_distsql_concurrency: 3}, fetch_resp_duration: 2.23s, rpc_info:{Cop:{num_rpc:24, total_time:12.3s}}, tikv_task:{proc max:100ms, min:0s, avg: 39.2ms, p80:80ms, p95:90ms, iters:66, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 299484, total_keys: 4885, get_snapshot_time: 256.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 946.2ms, total_suspend_time: 408.9µs, total_wait_time: 287.5µs, total_kv_read_wall_time: 170ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_296	21074.40	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:100ms, min:0s, avg: 39.2ms, p80:80ms, p95:90ms, iters:66, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_299(Probe)	10560.23	3705	cop[tikv]		total_time:130.2ms, total_open:0s, total_close:70.2µs, loops:24, cop_task: {num: 925, max: 3.22ms, min: 0s, avg: 327µs, p95: 1.58ms, max_proc_keys: 33, p95_proc_keys: 17, tot_proc: 298.7ms, tot_wait: 73.3ms, copr_cache: disabled, build_task_duration: 2.48ms, max_distsql_concurrency: 2, max_extra_concurrency: 10, store_batch_num: 677, store_batch_fallback_num: 38}, fetch_resp_duration: 126.9ms, rpc_info:{Cop:{num_rpc:259, total_time:306.8ms}, rpc_errors:{bucket_version_not_match:11}}, backoff{regionMiss: 62ms}, tikv_task:{proc max:10ms, min:0s, avg: 378.4µs, p80:0s, p95:0s, iters:927, tasks:925}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 8.26ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 298.7ms, total_suspend_time: 470.9µs, total_wait_time: 73.3ms, total_kv_read_wall_time: 350ms}	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	N/A	N/A
              └─TableRowIDScan_297	14274.48	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 378.4µs, p80:0s, p95:0s, iters:927, tasks:925}	keep order:false	N/A	N/A
ScalarSubQuery_480	N/A	0	root			Output: ScalarQueryCol#2065	N/A	N/A
└─MaxOneRow_378	1.00	1	root		time:957.9ms, open:9.51µs, close:46.4µs, loops:1		N/A	N/A
  └─HashAgg_383	1.00	1	root		time:957.9ms, open:8.76µs, close:45.7µs, loops:2	funcs:count(distinct Column#2029)->Column#2030	179.1 KB	0 Bytes
    └─Union_387	10622.47	3330	root		time:957.2ms, open:951ns, close:44.8µs, loops:6		N/A	N/A
      ├─Projection_389	62.24	3325	root		time:8.63ms, open:69.2µs, close:8.98µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2029	130.4 KB	N/A
      │ └─IndexReader_393	62.24	3325	root		time:8.51ms, open:66.7µs, close:5.94µs, loops:5, cop_task: {num: 4, max: 2.78ms, min: 1.19ms, avg: 2.11ms, p95: 2.78ms, max_proc_keys: 1629, p95_proc_keys: 1629, tot_proc: 3.95ms, tot_wait: 593.9µs, copr_cache: disabled, build_task_duration: 23.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 8.29ms, rpc_info:{Cop:{num_rpc:4, total_time:8.4ms}}	index:Selection_392	281.0 KB	N/A
      │   └─Selection_392	62.24	3325	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}, scan_detail: {total_process_keys: 3325, total_process_keys_size: 802058, total_keys: 3329, get_snapshot_time: 551.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.95ms, total_suspend_time: 3.37µs, total_wait_time: 593.9µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_391	62.34	3325	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_394	10560.23	5	root		time:957.8ms, open:110.8µs, close:34.6µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2029	27.2 KB	N/A
        └─IndexHashJoin_404	10560.23	5	root		time:957.7ms, open:109.2µs, close:9.5µs, loops:2, inner:{total:1.85s, concurrency:5, task:2, construct:3.11ms, fetch:1.84s, build:664µs, join:4.22ms}	inner join, inner:IndexLookUp_420, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.05 MB	N/A
          ├─IndexReader_415(Build)	5970.05	5192	root	partition:all	time:4.5ms, open:107µs, close:5.74µs, loops:8, cop_task: {num: 21, max: 1.66ms, min: 293.7µs, avg: 862.5µs, p95: 1.39ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 5.67ms, tot_wait: 476.4µs, copr_cache: disabled, build_task_duration: 61.6µs, max_distsql_concurrency: 9}, fetch_resp_duration: 4.13ms, rpc_info:{Cop:{num_rpc:21, total_time:18ms}}	index:Selection_414	39.9 KB	N/A
          │ └─Selection_414	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 201.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.67ms, total_wait_time: 476.4µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_413	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_420(Probe)	10560.23	3328	root	partition:all	total_time:1.84s, total_open:14.8ms, total_close:14µs, loops:6, index_task: {total_time: 1.78s, fetch_handle: 1.78s, build: 14.5µs, wait: 30.8µs}, table_task: {total_time: 77.2ms, num: 12, concurrency: 5}, next: {wait_index: 1.78s, wait_table_lookup_build: 2.62ms, wait_table_lookup_resp: 46.4ms}		3.84 MB	N/A
            ├─Selection_418(Build)	15181.60	5192	cop[tikv]		total_time:1.8s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 929.9ms, min: 1.94ms, avg: 406.7ms, p95: 922.9ms, max_proc_keys: 738, p95_proc_keys: 677, tot_proc: 995.6ms, tot_wait: 231.7µs, copr_cache: disabled, build_task_duration: 3.48ms, max_distsql_concurrency: 3}, fetch_resp_duration: 1.8s, rpc_info:{Cop:{num_rpc:24, total_time:9.76s}}, tikv_task:{proc max:110ms, min:0s, avg: 41.7ms, p80:80ms, p95:100ms, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 291330, total_keys: 2408, get_snapshot_time: 216.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 995.6ms, total_suspend_time: 152.8µs, total_wait_time: 231.7µs, total_kv_read_wall_time: 70ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_416	22413.64	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:110ms, min:0s, avg: 41.7ms, p80:80ms, p95:100ms, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_419(Probe)	10560.23	3328	cop[tikv]		total_time:72.5ms, total_open:0s, total_close:65.5µs, loops:24, cop_task: {num: 924, max: 2.36ms, min: 0s, avg: 263.7µs, p95: 1.33ms, max_proc_keys: 35, p95_proc_keys: 17, tot_proc: 222ms, tot_wait: 50ms, copr_cache: disabled, build_task_duration: 2.46ms, max_distsql_concurrency: 3, max_extra_concurrency: 9, store_batch_num: 690, store_batch_fallback_num: 25}, fetch_resp_duration: 69.3ms, rpc_info:{Cop:{num_rpc:234, total_time:241.4ms}}, tikv_task:{proc max:10ms, min:0s, avg: 248.9µs, p80:0s, p95:0s, iters:926, tasks:924}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 7.25ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 222ms, total_suspend_time: 329.8µs, total_wait_time: 50ms, total_kv_read_wall_time: 230ms}	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	N/A	N/A
              └─TableRowIDScan_417	15181.60	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 248.9µs, p80:0s, p95:0s, iters:926, tasks:924}	keep order:false	N/A	N/A
ScalarSubQuery_600	N/A	0	root			Output: ScalarQueryCol#2219	N/A	N/A
└─MaxOneRow_498	1.00	1	root		time:275.3ms, open:9.46µs, close:26.7µs, loops:1		N/A	N/A
  └─HashAgg_503	1.00	1	root		time:275.3ms, open:8.98µs, close:26.2µs, loops:2	funcs:count(distinct Column#2181)->Column#2182	296.1 KB	0 Bytes
    └─Union_507	10624.39	3594	root		time:274.4ms, open:1.01µs, close:25.7µs, loops:6		N/A	N/A
      ├─Projection_509	64.16	3587	root		time:20.1ms, open:74µs, close:8.92µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2181	130.4 KB	N/A
      │ └─IndexReader_513	64.16	3587	root		time:20ms, open:71.1µs, close:6.18µs, loops:5, cop_task: {num: 4, max: 10.6ms, min: 1.8ms, avg: 4.98ms, p95: 10.6ms, max_proc_keys: 1891, p95_proc_keys: 1891, tot_proc: 9.4ms, tot_wait: 1.34ms, copr_cache: disabled, build_task_duration: 26.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 19.8ms, rpc_info:{Cop:{num_rpc:4, total_time:19.9ms}}	index:Selection_512	309.0 KB	N/A
      │   └─Selection_512	64.16	3587	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3587, total_process_keys_size: 865272, total_keys: 3591, get_snapshot_time: 1.29ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 9.4ms, total_suspend_time: 13.3µs, total_wait_time: 1.34ms, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_511	64.26	3587	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_514	10560.23	7	root		time:275.2ms, open:129.8µs, close:15.9µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2181	27.2 KB	N/A
        └─IndexHashJoin_524	10560.23	7	root		time:275.1ms, open:126.2µs, close:5.51µs, loops:2, inner:{total:523.9ms, concurrency:5, task:2, construct:3.12ms, fetch:516.1ms, build:658.9µs, join:4.64ms}	inner join, inner:IndexLookUp_540, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.13 MB	N/A
          ├─IndexReader_535(Build)	5970.05	5192	root	partition:all	time:4.28ms, open:123.9µs, close:3.22µs, loops:8, cop_task: {num: 21, max: 1.62ms, min: 334µs, avg: 837.8µs, p95: 1.4ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 5.38ms, tot_wait: 512.1µs, copr_cache: disabled, build_task_duration: 59.2µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.91ms, rpc_info:{Cop:{num_rpc:21, total_time:17.4ms}}	index:Selection_534	40.3 KB	N/A
          │ └─Selection_534	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 952.4µs, p80:0s, p95:10ms, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 226.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.38ms, total_wait_time: 512.1µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_533	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_540(Probe)	10560.23	3591	root	partition:all	total_time:514.7ms, total_open:14.6ms, total_close:16.3µs, loops:7, index_task: {total_time: 474.5ms, fetch_handle: 474.5ms, build: 15.4µs, wait: 35.9µs}, table_task: {total_time: 69.3ms, num: 12, concurrency: 5}, next: {wait_index: 454.5ms, wait_table_lookup_build: 2.35ms, wait_table_lookup_resp: 42.8ms}		3.84 MB	N/A
            ├─Selection_538(Build)	14414.37	5192	cop[tikv]		total_time:477.3ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 247.1ms, min: 1.54ms, avg: 69.5ms, p95: 230.9ms, max_proc_keys: 738, p95_proc_keys: 677, tot_proc: 1.01s, tot_wait: 516.2µs, copr_cache: disabled, build_task_duration: 3.43ms, max_distsql_concurrency: 3}, fetch_resp_duration: 476.7ms, rpc_info:{Cop:{num_rpc:24, total_time:1.67s}}, tikv_task:{proc max:120ms, min:0s, avg: 44.2ms, p80:90ms, p95:120ms, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 513000, total_keys: 27278, get_snapshot_time: 206.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.01s, total_suspend_time: 2ms, total_wait_time: 516.2µs, total_kv_read_wall_time: 850ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_536	21280.91	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:120ms, min:0s, avg: 44.2ms, p80:90ms, p95:120ms, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_539(Probe)	10560.23	3591	cop[tikv]		total_time:64.5ms, total_open:0s, total_close:67.2µs, loops:24, cop_task: {num: 925, max: 1.56ms, min: 0s, avg: 203.2µs, p95: 996.3µs, max_proc_keys: 35, p95_proc_keys: 17, tot_proc: 102.7ms, tot_wait: 29.4ms, copr_cache: disabled, build_task_duration: 2.51ms, max_distsql_concurrency: 3, max_extra_concurrency: 9, store_batch_num: 692, store_batch_fallback_num: 24}, fetch_resp_duration: 61.4ms, rpc_info:{Cop:{num_rpc:233, total_time:185.8ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:927, tasks:925}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 6.19ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 102.7ms, total_wait_time: 29.4ms}	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	N/A	N/A
              └─TableRowIDScan_537	14414.37	5192	cop[tikv]	table:d	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:927, tasks:925}	keep order:false	N/A	N/A
ScalarSubQuery_738	N/A	0	root			Output: ScalarQueryCol#2423	N/A	N/A
└─MaxOneRow_618	1.00	1	root		time:1.13s, open:9.76µs, close:25.5µs, loops:1		N/A	N/A
  └─HashAgg_623	1.00	1	root		time:1.13s, open:9.03µs, close:25µs, loops:2	funcs:count(distinct Column#2335)->Column#2336	29.7 KB	0 Bytes
    └─Union_627	10582.13	406	root		time:1.13s, open:960ns, close:24.3µs, loops:2		N/A	N/A
      ├─Projection_629	21.90	406	root		time:11.9ms, open:76.1µs, close:7.63µs, loops:2, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2335	55.2 KB	N/A
      │ └─IndexReader_633	21.90	406	root		time:11.8ms, open:69.8µs, close:4.68µs, loops:2, cop_task: {num: 2, max: 10.6ms, min: 1.05ms, avg: 5.83ms, p95: 10.6ms, max_proc_keys: 224, p95_proc_keys: 224, tot_proc: 8.25ms, tot_wait: 52.2µs, copr_cache: disabled, build_task_duration: 23.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 11.7ms, rpc_info:{Cop:{num_rpc:2, total_time:11.6ms}}	index:Selection_632	44.3 KB	N/A
      │   └─Selection_632	21.90	406	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:6, tasks:2}, scan_detail: {total_process_keys: 406, total_process_keys_size: 97954, total_keys: 408, get_snapshot_time: 21.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 8.25ms, total_suspend_time: 7.87µs, total_wait_time: 52.2µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_631	21.94	406	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:6, tasks:2}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_634	10560.23	0	root		time:1.13s, open:111.9µs, close:15.8µs, loops:1, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2335	6.21 KB	N/A
        └─IndexHashJoin_644	10560.23	0	root		time:1.13s, open:111.1µs, close:5.21µs, loops:1, inner:{total:2.02s, concurrency:5, task:2, construct:3.42ms, fetch:2.02s, build:648.2µs, join:714.7µs}	inner join, inner:IndexLookUp_660, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	986.3 KB	N/A
          ├─IndexReader_655(Build)	5970.05	5192	root	partition:all	time:4.07ms, open:109.8µs, close:3.06µs, loops:8, cop_task: {num: 21, max: 1.41ms, min: 343.2µs, avg: 853.2µs, p95: 1.34ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 4.84ms, tot_wait: 518.9µs, copr_cache: disabled, build_task_duration: 54.4µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.74ms, rpc_info:{Cop:{num_rpc:21, total_time:17.8ms}}	index:Selection_654	39.9 KB	N/A
          │ └─Selection_654	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 203.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.84ms, total_wait_time: 518.9µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_653	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_660(Probe)	10560.23	406	root	partition:all	total_time:2.02s, total_open:15ms, total_close:14.9µs, loops:4, index_task: {total_time: 1.96s, fetch_handle: 1.96s, build: 18.4µs, wait: 25.2µs}, table_task: {total_time: 64.8ms, num: 12, concurrency: 5}, next: {wait_index: 1.98s, wait_table_lookup_build: 1.09ms, wait_table_lookup_resp: 24.3ms}		3.85 MB	N/A
            ├─Selection_658(Build)	130973.11	5192	cop[tikv]		total_time:1.98s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 869.7ms, min: 882.3µs, avg: 350ms, p95: 835.8ms, max_proc_keys: 739, p95_proc_keys: 678, tot_proc: 874ms, tot_wait: 233.2µs, copr_cache: disabled, build_task_duration: 3.44ms, max_distsql_concurrency: 3}, fetch_resp_duration: 1.98s, rpc_info:{Cop:{num_rpc:24, total_time:8.4s}}, tikv_task:{proc max:90ms, min:0s, avg: 36.7ms, p80:70ms, p95:90ms, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 291384, total_keys: 2415, get_snapshot_time: 193.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 874ms, total_suspend_time: 73.6µs, total_wait_time: 233.2µs, total_kv_read_wall_time: 30ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_656	193364.56	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 36.7ms, p80:70ms, p95:90ms, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_659(Probe)	10560.23	406	cop[tikv]		total_time:60.2ms, total_open:0s, total_close:57.8µs, loops:24, cop_task: {num: 923, max: 1.48ms, min: 0s, avg: 178.3µs, p95: 876.5µs, max_proc_keys: 35, p95_proc_keys: 17, tot_proc: 58.2ms, tot_wait: 20.7ms, copr_cache: disabled, build_task_duration: 2.44ms, max_distsql_concurrency: 2, max_extra_concurrency: 9, store_batch_num: 687, store_batch_fallback_num: 28}, fetch_resp_duration: 57.6ms, rpc_info:{Cop:{num_rpc:237, total_time:162.8ms}, rpc_errors:{bucket_version_not_match:1}}, backoff{regionMiss: 4ms}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:925, tasks:923}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 5.98ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 58.2ms, total_wait_time: 20.7ms}	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	N/A	N/A
              └─TableRowIDScan_657	130973.11	5192	cop[tikv]	table:d	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:925, tasks:923}	keep order:false	N/A	N/A
ScalarSubQuery_890	N/A	0	root			Output: ScalarQueryCol#2647	N/A	N/A
└─MaxOneRow_756	1.00	1	root		time:337.7ms, open:8.98µs, close:28µs, loops:1		N/A	N/A
  └─HashAgg_761	1.00	1	root		time:337.7ms, open:8.25µs, close:27.6µs, loops:2	funcs:count(distinct Column#2539)->Column#2540	27.3 KB	0 Bytes
    └─Union_765	10626.40	3552	root		time:337.3ms, open:1.05µs, close:27µs, loops:6		N/A	N/A
      ├─Projection_767	66.17	3546	root		time:11.1ms, open:68.6µs, close:8.99µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2539	130.4 KB	N/A
      │ └─IndexReader_771	66.17	3546	root		time:11ms, open:65.6µs, close:6.23µs, loops:5, cop_task: {num: 4, max: 4.33ms, min: 1.39ms, avg: 2.73ms, p95: 4.33ms, max_proc_keys: 1850, p95_proc_keys: 1850, tot_proc: 5.79ms, tot_wait: 413µs, copr_cache: disabled, build_task_duration: 24.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 10.8ms, rpc_info:{Cop:{num_rpc:4, total_time:10.9ms}}	index:Selection_770	310.8 KB	N/A
      │   └─Selection_770	66.17	3546	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3546, total_process_keys_size: 886533, total_keys: 3550, get_snapshot_time: 370.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.79ms, total_suspend_time: 9.64µs, total_wait_time: 413µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_769	66.27	3546	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_772	10560.23	6	root		time:337.6ms, open:104.6µs, close:17µs, loops:2, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2539	31.2 KB	N/A
        └─IndexHashJoin_782	10560.23	6	root		time:337.6ms, open:103.4µs, close:5.59µs, loops:2, inner:{total:634.2ms, concurrency:5, task:2, construct:3.16ms, fetch:626.3ms, build:695µs, join:4.77ms}	inner join, inner:IndexLookUp_798, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.06 MB	N/A
          ├─IndexReader_793(Build)	5970.05	5192	root	partition:all	time:4.1ms, open:101.3µs, close:2.93µs, loops:8, cop_task: {num: 21, max: 2.17ms, min: 417.2µs, avg: 929.4µs, p95: 1.74ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 4.91ms, tot_wait: 3.05ms, copr_cache: disabled, build_task_duration: 52.7µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.76ms, rpc_info:{Cop:{num_rpc:21, total_time:19.4ms}}	index:Selection_792	39.9 KB	N/A
          │ └─Selection_792	5970.05	5192	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 2.76ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.91ms, total_wait_time: 3.05ms, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_791	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 476.2µs, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_798(Probe)	10560.23	3742	root	partition:all	total_time:624.8ms, total_open:14.7ms, total_close:15.3µs, loops:7, index_task: {total_time: 582.4ms, fetch_handle: 582.3ms, build: 14.8µs, wait: 41.5µs}, table_task: {total_time: 63.1ms, num: 12, concurrency: 5}, next: {wait_index: 575.8ms, wait_table_lookup_build: 1.94ms, wait_table_lookup_resp: 31.9ms}		3.84 MB	N/A
            ├─Selection_796(Build)	14707.02	5192	cop[tikv]		total_time:589.3ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 311.4ms, min: 836.3µs, avg: 79.8ms, p95: 279.6ms, max_proc_keys: 738, p95_proc_keys: 677, tot_proc: 817.1ms, tot_wait: 417.9µs, copr_cache: disabled, build_task_duration: 3.49ms, max_distsql_concurrency: 3}, fetch_resp_duration: 588.6ms, rpc_info:{Cop:{num_rpc:24, total_time:1.91s}}, tikv_task:{proc max:90ms, min:0s, avg: 33.3ms, p80:70ms, p95:80ms, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 458406, total_keys: 21077, get_snapshot_time: 172.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 817.1ms, total_suspend_time: 1.11ms, total_wait_time: 417.9µs, total_kv_read_wall_time: 400ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_794	21712.98	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 33.3ms, p80:70ms, p95:80ms, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_797(Probe)	10560.23	3742	cop[tikv]		total_time:58.4ms, total_open:0s, total_close:61.3µs, loops:24, cop_task: {num: 925, max: 1.43ms, min: 0s, avg: 168.2µs, p95: 830µs, max_proc_keys: 35, p95_proc_keys: 17, tot_proc: 43.9ms, tot_wait: 15.3ms, copr_cache: disabled, build_task_duration: 2.44ms, max_distsql_concurrency: 3, max_extra_concurrency: 9, store_batch_num: 692, store_batch_fallback_num: 24}, fetch_resp_duration: 55.1ms, rpc_info:{Cop:{num_rpc:233, total_time:153.4ms}}, tikv_task:{proc max:10ms, min:0s, avg: 54.1µs, p80:0s, p95:0s, iters:927, tasks:925}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 5.15ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 43.9ms, total_wait_time: 15.3ms, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	N/A	N/A
              └─TableRowIDScan_795	14707.02	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 54.1µs, p80:0s, p95:0s, iters:927, tasks:925}	keep order:false	N/A	N/A
ScalarSubQuery_1022	N/A	0	root			Output: ScalarQueryCol#2831	N/A	N/A
└─MaxOneRow_908	1.00	1	root		time:624.8ms, open:11.6µs, close:25.8µs, loops:1		N/A	N/A
  └─HashAgg_913	1.00	1	root		time:624.8ms, open:10.8µs, close:25.2µs, loops:2	funcs:count(distinct Column#2763)->Column#2764	1.60 KB	0 Bytes
    └─Union_917	10562.58	6	root		time:624.8ms, open:1.09µs, close:24.5µs, loops:2		N/A	N/A
      ├─Projection_919	2.36	6	root		time:783.5µs, open:76.3µs, close:7.59µs, loops:2, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2763	3.85 KB	N/A
      │ └─IndexReader_923	2.36	6	root		time:763.1µs, open:71.9µs, close:4.98µs, loops:2, cop_task: {num: 1, max: 666.4µs, proc_keys: 6, tot_proc: 226.6µs, tot_wait: 18.9µs, copr_cache: disabled, build_task_duration: 22.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 675.9µs, rpc_info:{Cop:{num_rpc:1, total_time:653.5µs}}	index:Selection_922	1.01 KB	N/A
      │   └─Selection_922	2.36	6	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_process_keys: 6, total_process_keys_size: 1348, total_keys: 7, get_snapshot_time: 6.78µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 226.6µs, total_wait_time: 18.9µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_921	2.36	6	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{time:0s, loops:1}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_924	10560.23	0	root		time:624.7ms, open:114.3µs, close:16µs, loops:1, Concurrency:5	cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2763	6.21 KB	N/A
        └─IndexHashJoin_934	10560.23	0	root		time:624.6ms, open:113µs, close:5.27µs, loops:1, inner:{total:1.22s, concurrency:5, task:2, construct:3.08ms, fetch:1.22s, build:696µs, join:98.8µs}	inner join, inner:IndexLookUp_950, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	985.8 KB	N/A
          ├─IndexReader_945(Build)	5970.05	5192	root	partition:all	time:4.16ms, open:110.7µs, close:3.01µs, loops:8, cop_task: {num: 21, max: 1.44ms, min: 324µs, avg: 822.2µs, p95: 1.43ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 4.7ms, tot_wait: 472.6µs, copr_cache: disabled, build_task_duration: 54.9µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.81ms, rpc_info:{Cop:{num_rpc:21, total_time:17.1ms}}	index:Selection_944	44.4 KB	N/A
          │ └─Selection_944	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 176.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.7ms, total_wait_time: 472.6µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
          │   └─IndexRangeScan_943	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
          └─IndexLookUp_950(Probe)	10560.23	6	root	partition:all	total_time:1.21s, total_open:14.7ms, total_close:15µs, loops:4, index_task: {total_time: 1.17s, fetch_handle: 1.17s, build: 17.5µs, wait: 40.7µs}, table_task: {total_time: 63.4ms, num: 12, concurrency: 5}, next: {wait_index: 1.15s, wait_table_lookup_build: 3.71ms, wait_table_lookup_resp: 43.7ms}		3.86 MB	N/A
            ├─Selection_948(Build)	21058627.41	5192	cop[tikv]		total_time:1.18s, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 600.5ms, min: 806.1µs, avg: 161.2ms, p95: 584.7ms, max_proc_keys: 736, p95_proc_keys: 676, tot_proc: 762.9ms, tot_wait: 385.9µs, copr_cache: disabled, build_task_duration: 4.42ms, max_distsql_concurrency: 3}, fetch_resp_duration: 1.18s, rpc_info:{Cop:{num_rpc:24, total_time:3.87s}}, tikv_task:{proc max:90ms, min:0s, avg: 30.4ms, p80:60ms, p95:80ms, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 390582, total_keys: 16957, get_snapshot_time: 173.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 762.9ms, total_suspend_time: 848µs, total_wait_time: 385.9µs, total_kv_read_wall_time: 280ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │ └─IndexRangeScan_946	31090290.88	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:90ms, min:0s, avg: 30.4ms, p80:60ms, p95:80ms, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
            └─Selection_949(Probe)	10560.23	6	cop[tikv]		total_time:58.5ms, total_open:0s, total_close:95.8µs, loops:17, cop_task: {num: 926, max: 1.33ms, min: 0s, avg: 160.8µs, p95: 799.5µs, max_proc_keys: 35, p95_proc_keys: 17, tot_proc: 37.4ms, tot_wait: 16.9ms, copr_cache: disabled, build_task_duration: 2.48ms, max_distsql_concurrency: 3, max_extra_concurrency: 9, store_batch_num: 693, store_batch_fallback_num: 24}, fetch_resp_duration: 56.4ms, rpc_info:{Cop:{num_rpc:233, total_time:146.7ms}}, tikv_task:{proc max:10ms, min:0s, avg: 10.8µs, p80:0s, p95:0s, iters:928, tasks:926}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 5.35ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 37.4ms, total_wait_time: 16.9ms, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	N/A	N/A
              └─TableRowIDScan_947	21058627.41	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 10.8µs, p80:0s, p95:0s, iters:928, tasks:926}	keep order:false	N/A	N/A
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
-- best_variant=optimized_default
-- explain_analyze_elapsed_ms=136.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_131	1.00	1	root		time:96.9ms, open:11.7µs, close:134µs, loops:2, RU:441.61	funcs:count(distinct Column#314)->Column#254, funcs:count(distinct Column#315)->Column#255, funcs:count(distinct Column#316)->Column#256, funcs:count(distinct Column#317)->Column#257, funcs:count(distinct Column#318)->Column#258, funcs:count(distinct Column#319)->Column#259, funcs:count(distinct Column#320)->Column#260	1.26 MB	0 Bytes
└─Projection_265	59486.89	18351	root		time:90ms, open:2.35µs, close:132.9µs, loops:25, Concurrency:5	case(eq(Column#252, ?), Column#253)->Column#314, case(eq(Column#252, ?), Column#253)->Column#315, case(eq(Column#252, ?), Column#253)->Column#316, case(eq(Column#252, ?), Column#253)->Column#317, case(eq(Column#252, ?), Column#253)->Column#318, case(eq(Column#252, ?), Column#253)->Column#319, case(eq(Column#252, ?), Column#253)->Column#320	985.0 KB	N/A
  └─Union_135	59486.89	18351	root		time:96.7ms, open:939ns, close:125.8µs, loops:25		N/A	N/A
    ├─Projection_137	349.62	18321	root		time:9.65ms, open:129.3µs, close:11.3µs, loops:20, Concurrency:OFF	intuit_risk.group_c_180d_daily_distinct.template_id->Column#252, cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	184.7 KB	N/A
    │ └─IndexReader_141	349.62	18321	root		time:8.32ms, open:108µs, close:8.93µs, loops:20, cop_task: {num: 23, max: 4.22ms, min: 900.7µs, avg: 1.95ms, p95: 3.97ms, max_proc_keys: 2016, p95_proc_keys: 2006, tot_proc: 21.4ms, tot_wait: 549µs, copr_cache: disabled, build_task_duration: 40.9µs, max_distsql_concurrency: 6}, fetch_resp_duration: 7.38ms, rpc_info:{Cop:{num_rpc:23, total_time:44.6ms}}	index:Selection_140	455.7 KB	N/A
    │   └─Selection_140	349.62	18321	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.3ms, p80:0s, p95:10ms, iters:98, tasks:23}, scan_detail: {total_process_keys: 18321, total_process_keys_size: 4791602, total_keys: 18345, get_snapshot_time: 234.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 21.4ms, total_suspend_time: 30.6µs, total_wait_time: 549µs, total_kv_read_wall_time: 30ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
    │     └─IndexRangeScan_139	350.16	18321	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 1.3ms, p80:0s, p95:10ms, iters:98, tasks:23}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_142	8448.18	6	root		time:96.4ms, open:147.3µs, close:43.2µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	30.7 KB	N/A
    │ └─Selection_144	8448.18	6	root		time:96.3ms, open:146.1µs, close:34.5µs, loops:2	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	20.9 KB	N/A
    │   └─CTEFullScan_146	10560.23	7	root	CTE:raw_boundary	time:96.3ms, open:139.6µs, close:33.9µs, loops:3	data:CTE_0	8.70 KB	0 Bytes
    ├─Projection_150	8448.18	6	root		time:96.5ms, open:191.4µs, close:12.9µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_152	8448.18	6	root		time:96.5ms, open:190.6µs, close:1.07µs, loops:2	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	62.4 KB	N/A
    │   └─CTEFullScan_154	10560.23	7	root	CTE:raw_boundary	time:96.4ms, open:186.5µs, close:278ns, loops:3	data:CTE_0	N/A	N/A
    ├─Projection_158	8448.18	5	root		time:96.5ms, open:96.4ms, close:9.5µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_160	8448.18	5	root		time:96.4ms, open:96.4ms, close:676ns, loops:2	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	4.35 KB	N/A
    │   └─CTEFullScan_162	10560.23	7	root	CTE:raw_boundary	time:96.4ms, open:96.3ms, close:97ns, loops:3	data:CTE_0	N/A	N/A
    ├─Projection_166	8448.18	7	root		time:96.5ms, open:96.4ms, close:8.33µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_168	8448.18	7	root		time:96.4ms, open:96.4ms, close:578ns, loops:2	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	4.35 KB	N/A
    │   └─CTEFullScan_170	10560.23	7	root	CTE:raw_boundary	time:96.4ms, open:96.4ms, close:119ns, loops:3	data:CTE_0	N/A	N/A
    ├─Projection_174	8448.18	0	root		time:86ms, open:86ms, close:16.5µs, loops:1, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	30.7 KB	N/A
    │ └─Selection_176	8448.18	0	root		time:86ms, open:86ms, close:861ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	4.35 KB	N/A
    │   └─CTEFullScan_178	10560.23	7	root	CTE:raw_boundary	time:86ms, open:86ms, close:327ns, loops:2	data:CTE_0	N/A	N/A
    ├─Projection_182	8448.18	6	root		time:223.4µs, open:9.88µs, close:11.5µs, loops:2, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	38.7 KB	N/A
    │ └─Selection_184	8448.18	6	root		time:48µs, open:8.59µs, close:549ns, loops:2	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	4.35 KB	N/A
    │   └─CTEFullScan_186	10560.23	7	root	CTE:raw_boundary	time:7.94µs, open:645ns, close:125ns, loops:3	data:CTE_0	N/A	N/A
    └─Projection_190	8448.18	0	root		time:52.8µs, open:4.79µs, close:11.1µs, loops:1, Concurrency:5	?->Column#252, cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#253	27.9 KB	N/A
      └─Selection_192	8448.18	0	root		time:15.4µs, open:4.03µs, close:500ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	4.35 KB	N/A
        └─CTEFullScan_194	10560.23	7	root	CTE:raw_boundary	time:2.89µs, open:172ns, close:110ns, loops:2	data:CTE_0	N/A	N/A
CTE_0	10560.23	7	root		time:96.3ms, open:139.6µs, close:33.9µs, loops:3	Non-Recursive CTE	8.70 KB	0 Bytes
└─Projection_78(Seed Part)	10560.23	7	root		time:96.2ms, open:136.5µs, close:32.7µs, loops:2, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.agent_os	98.7 KB	N/A
  └─IndexHashJoin_88	10560.23	7	root		time:96.1ms, open:135.3µs, close:9.72µs, loops:2, inner:{total:172ms, concurrency:5, task:2, construct:3.46ms, fetch:160.9ms, build:799.3µs, join:7.69ms}	inner join, inner:IndexLookUp_104, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	1.38 MB	N/A
    ├─IndexReader_99(Build)	5970.05	5192	root	partition:all	time:4.31ms, open:131.7µs, close:6.78µs, loops:8, cop_task: {num: 21, max: 1.52ms, min: 406.4µs, avg: 877.1µs, p95: 1.41ms, max_proc_keys: 864, p95_proc_keys: 646, tot_proc: 5.4ms, tot_wait: 641.8µs, copr_cache: disabled, build_task_duration: 70.1µs, max_distsql_concurrency: 9}, fetch_resp_duration: 3.75ms, rpc_info:{Cop:{num_rpc:21, total_time:18.1ms}}	index:Selection_98	39.9 KB	N/A
    │ └─Selection_98	5970.05	5192	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}, scan_detail: {total_process_keys: 7921, total_process_keys_size: 1020368, total_keys: 7942, get_snapshot_time: 247.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.4ms, total_wait_time: 641.8µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
    │   └─IndexRangeScan_97	8089.80	7921	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:76, tasks:21}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexLookUp_104(Probe)	10560.23	5182	root	partition:all	total_time:159ms, total_open:19.3ms, total_close:17.6µs, loops:9, index_task: {total_time: 108.8ms, fetch_handle: 108.8ms, build: 15.3µs, wait: 32.7µs}, table_task: {total_time: 66.4ms, num: 12, concurrency: 5}, next: {wait_index: 106.1ms, wait_table_lookup_build: 1.64ms, wait_table_lookup_resp: 30.4ms}		3.84 MB	N/A
      ├─Selection_102(Build)	10574.33	5192	cop[tikv]		total_time:115.9ms, total_open:0s, total_close:0s, loops:42, cop_task: {num: 24, max: 63.5ms, min: 899.2µs, avg: 26ms, p95: 61.3ms, max_proc_keys: 738, p95_proc_keys: 677, tot_proc: 525.5ms, tot_wait: 574.2µs, copr_cache: disabled, build_task_duration: 5.56ms, max_distsql_concurrency: 3}, fetch_resp_duration: 114.9ms, rpc_info:{Cop:{num_rpc:24, total_time:623.3ms}}, tikv_task:{proc max:60ms, min:0s, avg: 24.2ms, p80:40ms, p95:60ms, iters:67, tasks:24}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 521478, total_keys: 29767, get_snapshot_time: 234.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 525.5ms, total_suspend_time: 1.13ms, total_wait_time: 574.2µs, total_kv_read_wall_time: 420ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
      │ └─IndexRangeScan_100	15611.61	5192	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:60ms, min:0s, avg: 24.2ms, p80:40ms, p95:60ms, iters:67, tasks:24}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) not(isnull(intuit_risk.deviceprofile_fact.jms_timestamp)) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
      └─Selection_103(Probe)	10560.23	5182	cop[tikv]		total_time:61.1ms, total_open:0s, total_close:69.7µs, loops:24, cop_task: {num: 925, max: 1.57ms, min: 0s, avg: 175.9µs, p95: 850.1µs, max_proc_keys: 35, p95_proc_keys: 17, tot_proc: 45ms, tot_wait: 13.6ms, copr_cache: disabled, build_task_duration: 2.74ms, max_distsql_concurrency: 3, max_extra_concurrency: 9, store_batch_num: 692, store_batch_fallback_num: 24}, fetch_resp_duration: 55.3ms, rpc_info:{Cop:{num_rpc:233, total_time:160.3ms}}, tikv_task:{proc max:10ms, min:0s, avg: 54.1µs, p80:0s, p95:0s, iters:927, tasks:925}, scan_detail: {total_process_keys: 5192, total_process_keys_size: 3134897, total_keys: 5192, get_snapshot_time: 4.61ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 45ms, total_wait_time: 13.6ms, total_kv_read_wall_time: 30ms}	or(or(not(isnull(intuit_risk.deviceprofile_fact.smart_id)), or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.input_ip)))), or(or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))), or(not(isnull(intuit_risk.deviceprofile_fact.agent_type)), not(isnull(intuit_risk.deviceprofile_fact.agent_os)))))	N/A	N/A
        └─TableRowIDScan_101	10574.33	5192	cop[tikv]	table:d	tikv_task:{proc max:10ms, min:0s, avg: 32.4µs, p80:0s, p95:0s, iters:927, tasks:925}	keep order:false	N/A	N/A
```

### 4. group_b_bundle_018

- Filter/window: `d.input_ip = %s` / `180d`
- Chosen event: `INV0053143614` kind=`normal` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 1495.0 ms | ok |
| `optimized_default` | `{}` | 708.6 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 671.7 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 694.6 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 669.3 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 679.2 ms | ok |

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
-- explain_analyze_elapsed_ms=1495.0
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_265	1.00	1	root		time:8.9µs, open:2.79µs, close:987ns, loops:2, RU:1660.05, Concurrency:OFF	?->Column#652, ?->Column#770, ?->Column#882, ?->Column#976	0 Bytes	N/A
└─TableDual_267	1.00	1	root		time:1.94µs, open:154ns, close:302ns, loops:2	rows:1	N/A	N/A
ScalarSubQuery_100	N/A	0	root			Output: ScalarQueryCol#651	N/A	N/A
└─MaxOneRow_59	1.00	1	root		time:509.6ms, open:10.9µs, close:36.8µs, loops:1		N/A	N/A
  └─HashAgg_64	1.00	1	root		time:509.6ms, open:10.3µs, close:36.2µs, loops:2	funcs:count(distinct Column#604)->Column#605	13.4 MB	0 Bytes
    └─Union_68	319321.01	261396	root		time:422.4ms, open:798ns, close:35.6µs, loops:257		N/A	N/A
      ├─Projection_70	319319.92	261396	root		time:422.3ms, open:146.9µs, close:29.1µs, loops:257, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#604	838.5 KB	N/A
      │ └─IndexReader_73	319319.92	261396	root		time:424.2ms, open:145.4µs, close:10.5µs, loops:257, cop_task: {num: 7, max: 385.9ms, min: 2.24ms, avg: 60.5ms, p95: 385.9ms, max_proc_keys: 249556, p95_proc_keys: 249556, tot_proc: 189.3ms, tot_wait: 866.8µs, copr_cache: disabled, build_task_duration: 40.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 423.2ms, rpc_info:{Cop:{num_rpc:7, total_time:423.4ms}}	index:IndexRangeScan_72	28.4 MB	N/A
      │   └─IndexRangeScan_72	319319.92	261396	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:160ms, min:0s, avg: 27.1ms, p80:20ms, p95:160ms, iters:282, tasks:7}, scan_detail: {total_process_keys: 261396, total_process_keys_size: 34837590, total_keys: 11846, get_snapshot_time: 775µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 189.3ms, total_suspend_time: 48.8µs, total_wait_time: 866.8µs, total_kv_read_wall_time: 30ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_74	1.09	0	root		time:470.7µs, open:67.5µs, close:5.39µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#604	42.1 KB	N/A
        └─IndexReader_81	1.09	0	root	partition:p20251101	time:465µs, open:65.2µs, close:3.63µs, loops:1, cop_task: {num: 1, max: 374.6µs, proc_keys: 0, tot_proc: 17.6µs, tot_wait: 25.8µs, copr_cache: disabled, build_task_duration: 22.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 386.8µs, rpc_info:{Cop:{num_rpc:1, total_time:360.6µs}}	index:Selection_80	253 Bytes	N/A
          └─Selection_80	1.09	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 8.81µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 17.6µs, total_wait_time: 25.8µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	N/A	N/A
            └─IndexRangeScan_79	1.37	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_154	N/A	0	root			Output: ScalarQueryCol#769	N/A	N/A
└─MaxOneRow_113	1.00	1	root		time:495.6ms, open:11.7µs, close:32.8µs, loops:1		N/A	N/A
  └─HashAgg_118	1.00	1	root		time:495.6ms, open:11.1µs, close:32.2µs, loops:2	funcs:count(distinct Column#720)->Column#721	13.0 MB	0 Bytes
    └─Union_122	321246.34	259560	root		time:409.7ms, open:833ns, close:31.4µs, loops:255		N/A	N/A
      ├─Projection_124	321245.22	259560	root		time:409.5ms, open:69.8µs, close:24.4µs, loops:255, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#720	838.5 KB	N/A
      │ └─IndexReader_127	321245.22	259560	root		time:411.6ms, open:68.3µs, close:8.25µs, loops:255, cop_task: {num: 7, max: 379.7ms, min: 2.65ms, avg: 58.7ms, p95: 379.7ms, max_proc_keys: 247720, p95_proc_keys: 247720, tot_proc: 162.8ms, tot_wait: 692.1µs, copr_cache: disabled, build_task_duration: 24.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 410.7ms, rpc_info:{Cop:{num_rpc:7, total_time:410.7ms}}	index:IndexRangeScan_126	28.2 MB	N/A
      │   └─IndexRangeScan_126	321245.22	259560	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:140ms, min:0s, avg: 24.3ms, p80:10ms, p95:140ms, iters:280, tasks:7}, scan_detail: {total_process_keys: 259560, total_process_keys_size: 34603500, total_keys: 11846, get_snapshot_time: 598.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 162.8ms, total_suspend_time: 44.8µs, total_wait_time: 692.1µs, total_kv_read_wall_time: 30ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_128	1.12	0	root		time:531.3µs, open:77.8µs, close:5.83µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#720	12.2 KB	N/A
        └─IndexReader_132	1.12	0	root	partition:p20251101	time:523.8µs, open:73.8µs, close:3.66µs, loops:1, cop_task: {num: 1, max: 403.2µs, proc_keys: 0, tot_proc: 18µs, tot_wait: 33.6µs, copr_cache: disabled, build_task_duration: 23.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 436µs, rpc_info:{Cop:{num_rpc:1, total_time:381.4µs}}	index:Selection_131	254 Bytes	N/A
          └─Selection_131	1.12	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 13.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 18µs, total_wait_time: 33.6µs}	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	N/A	N/A
            └─IndexRangeScan_130	1.40	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_208	N/A	0	root			Output: ScalarQueryCol#881	N/A	N/A
└─MaxOneRow_167	1.00	1	root		time:435.9ms, open:10.2µs, close:30.8µs, loops:1		N/A	N/A
  └─HashAgg_172	1.00	1	root		time:435.9ms, open:9.73µs, close:30.4µs, loops:2	funcs:count(distinct Column#838)->Column#839	8.94 MB	0 Bytes
    └─Union_176	311368.80	246339	root		time:349.6ms, open:903ns, close:29.7µs, loops:243		N/A	N/A
      ├─Projection_178	311367.71	246339	root		time:349.4ms, open:78.4µs, close:24.4µs, loops:243, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#838	633.3 KB	N/A
      │ └─IndexReader_181	311367.71	246339	root		time:351.5ms, open:76.9µs, close:10.1µs, loops:243, cop_task: {num: 7, max: 311.7ms, min: 2.83ms, avg: 50.1ms, p95: 311.7ms, max_proc_keys: 234499, p95_proc_keys: 234499, tot_proc: 158.8ms, tot_wait: 1.49ms, copr_cache: disabled, build_task_duration: 24.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 350.6ms, rpc_info:{Cop:{num_rpc:7, total_time:350.7ms}}	index:IndexRangeScan_180	22.5 MB	N/A
      │   └─IndexRangeScan_180	311367.71	246339	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:130ms, min:0s, avg: 24.3ms, p80:10ms, p95:130ms, iters:268, tasks:7}, scan_detail: {total_process_keys: 246339, total_process_keys_size: 27009025, total_keys: 11846, get_snapshot_time: 1.38ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 158.8ms, total_suspend_time: 51.7µs, total_wait_time: 1.49ms, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_182	1.08	0	root		time:1.23ms, open:75.8µs, close:4.74µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#838	9.48 KB	N/A
        └─IndexReader_186	1.08	0	root	partition:p20251101	time:1.22ms, open:71.6µs, close:3.21µs, loops:1, cop_task: {num: 1, max: 1.12ms, proc_keys: 0, tot_proc: 21.5µs, tot_wait: 766.7µs, copr_cache: disabled, build_task_duration: 24.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.13ms, rpc_info:{Cop:{num_rpc:1, total_time:1.11ms}}	index:Selection_185	255 Bytes	N/A
          └─Selection_185	1.08	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 747.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 21.5µs, total_wait_time: 766.7µs}	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	N/A	N/A
            └─IndexRangeScan_184	1.35	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_264	N/A	0	root			Output: ScalarQueryCol#975	N/A	N/A
└─MaxOneRow_221	1.00	1	root		time:14.1ms, open:10.3µs, close:20.3µs, loops:1		N/A	N/A
  └─HashAgg_226	1.00	1	root		time:14.1ms, open:9.42µs, close:20µs, loops:2	funcs:count(distinct Column#950)->Column#951	14.1 KB	0 Bytes
    └─Union_230	182742.95	467	root		time:14ms, open:878ns, close:19.3µs, loops:2		N/A	N/A
      ├─Projection_232	182741.89	467	root		time:14ms, open:73µs, close:14.4µs, loops:2, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#950	79.0 KB	N/A
      │ └─IndexReader_235	182741.89	467	root		time:13.9ms, open:72µs, close:5.45µs, loops:2, cop_task: {num: 2, max: 12.6ms, min: 1.15ms, avg: 6.85ms, p95: 12.6ms, max_proc_keys: 243, p95_proc_keys: 243, tot_proc: 10.9ms, tot_wait: 856.9µs, copr_cache: disabled, build_task_duration: 25.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 13.8ms, rpc_info:{Cop:{num_rpc:2, total_time:13.7ms}}	index:IndexRangeScan_234	46.2 KB	N/A
      │   └─IndexRangeScan_234	182741.89	467	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 5ms, p80:10ms, p95:10ms, iters:7, tasks:2}, scan_detail: {total_process_keys: 467, total_process_keys_size: 99551, total_keys: 469, get_snapshot_time: 813.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 10.9ms, total_suspend_time: 7.65µs, total_wait_time: 856.9µs, total_kv_read_wall_time: 10ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_236	1.06	0	root		time:607.5µs, open:81.3µs, close:4.37µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#950	9.48 KB	N/A
        └─IndexReader_244	1.06	0	root	partition:p20251101	time:601.1µs, open:77.4µs, close:3.09µs, loops:1, cop_task: {num: 1, max: 484.1µs, proc_keys: 0, tot_proc: 57.2µs, tot_wait: 50.7µs, copr_cache: disabled, build_task_duration: 25.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 508.7µs, rpc_info:{Cop:{num_rpc:1, total_time:466.3µs}}	index:Selection_243	255 Bytes	N/A
          └─Selection_243	1.06	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 23.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 57.2µs, total_wait_time: 50.7µs}	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	N/A	N/A
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
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=669.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_63	1.00	1	root		time:636ms, open:9.39µs, close:68.3µs, loops:2, RU:1650.76	funcs:count(distinct Column#161)->Column#128, funcs:count(distinct Column#162)->Column#129, funcs:count(distinct Column#163)->Column#130, funcs:count(distinct Column#164)->Column#131	35.3 MB	0 Bytes
└─Projection_106	1134679.46	767762	root		time:316.2ms, open:2.08µs, close:66.9µs, loops:752, Concurrency:5	case(eq(Column#126, ?), Column#127)->Column#161, case(eq(Column#126, ?), Column#127)->Column#162, case(eq(Column#126, ?), Column#127)->Column#163, case(eq(Column#126, ?), Column#127)->Column#164	904.7 KB	N/A
  └─Union_65	1134679.46	767762	root		time:323.6ms, open:917ns, close:44.8µs, loops:752		N/A	N/A
    ├─Projection_67	1134674.75	767762	root		time:323.2ms, open:115.8µs, close:21µs, loops:752, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#126, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	954.8 KB	N/A
    │ └─IndexReader_70	1134674.75	767762	root		time:324.6ms, open:114.1µs, close:10.5µs, loops:752, cop_task: {num: 23, max: 392.4ms, min: 1.07ms, avg: 50ms, p95: 386.6ms, max_proc_keys: 249556, p95_proc_keys: 247720, tot_proc: 498.4ms, tot_wait: 586.9µs, copr_cache: disabled, build_task_duration: 41.4µs, max_distsql_concurrency: 4}, fetch_resp_duration: 321.7ms, rpc_info:{Cop:{num_rpc:23, total_time:1.15s}}	index:IndexRangeScan_69	77.5 MB	N/A
    │   └─IndexRangeScan_69	1134674.75	767762	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:170ms, min:0s, avg: 20.4ms, p80:10ms, p95:160ms, iters:837, tasks:23}, scan_detail: {total_process_keys: 767762, total_process_keys_size: 96549666, total_keys: 36007, get_snapshot_time: 272.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 498.4ms, total_suspend_time: 119.7µs, total_wait_time: 586.9µs, total_kv_read_wall_time: 20ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_71	1.18	0	root		time:636.9µs, open:97.6µs, close:10.9µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	18.1 KB	N/A
    │ └─Selection_73	1.18	0	root		time:629µs, open:93.6µs, close:8.61µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	71.0 KB	N/A
    │   └─CTEFullScan_75	1.47	0	root	CTE:raw_boundary	time:621.8µs, open:89.7µs, close:7.14µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_79	1.18	0	root		time:630.3µs, open:623.7µs, close:3.52µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	24.1 KB	N/A
    │ └─Selection_81	1.18	0	root		time:625.3µs, open:622µs, close:1.42µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	48.6 KB	N/A
    │   └─CTEFullScan_83	1.47	0	root	CTE:raw_boundary	time:618µs, open:616.8µs, close:207ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_87	1.18	0	root		time:633µs, open:628.8µs, close:2.3µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	3.11 KB	N/A
    │ └─Selection_89	1.18	0	root		time:629µs, open:627.1µs, close:761ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	6.48 KB	N/A
    │   └─CTEFullScan_91	1.47	0	root	CTE:raw_boundary	time:625.9µs, open:625.1µs, close:161ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_95	1.18	0	root		time:641.9µs, open:634.5µs, close:5.77µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	42.5 KB	N/A
      └─Selection_97	1.18	0	root		time:637µs, open:632.1µs, close:3.88µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.11 KB	N/A
        └─CTEFullScan_99	1.47	0	root	CTE:raw_boundary	time:629.3µs, open:627.8µs, close:908ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.47	0	root		time:621.8µs, open:89.7µs, close:7.14µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_50(Seed Part)	1.47	0	root		time:602.7µs, open:85.6µs, close:5.06µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.agent_type	47.7 KB	N/A
  └─IndexReader_55	1.83	0	root	partition:p20251101	time:595.2µs, open:80.9µs, close:3.81µs, loops:1, cop_task: {num: 1, max: 482.8µs, proc_keys: 0, tot_proc: 26.3µs, tot_wait: 47.3µs, copr_cache: disabled, build_task_duration: 30.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 497.5µs, rpc_info:{Cop:{num_rpc:1, total_time:462.3µs}}	index:Selection_54	255 Bytes	N/A
    └─Selection_54	1.83	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.3µs, total_wait_time: 47.3µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type))))	N/A	N/A
      └─IndexRangeScan_53	1.84	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```

### 5. group_c_bundle_018

- Filter/window: `d.true_ip = %s` / `30d`
- Chosen event: `INV0039365135` kind=`hot_true_ip` error=`(1105, 'context canceled')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 2511.5 ms | ok |
| `optimized_default` | `{}` | 1601.4 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 2433.7 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 1918.7 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 1057.0 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 988.6 ms | ok |

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
-- explain_analyze_elapsed_ms=2511.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_13	127.11	1	root		time:2.43s, open:97.3µs, close:29.5µs, loops:2, RU:4811.81	group by:intuit_risk.deviceprofile_fact.true_ip, funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	561.3 KB	0 Bytes
└─Projection_21	366700.29	4488	root		time:2.43s, open:89.9µs, close:28.8µs, loops:8, Concurrency:5	intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.deviceprofile_fact.true_ip	637.8 KB	N/A
  └─IndexHashJoin_30	366700.29	4488	root		time:2.43s, open:89µs, close:10.7µs, loops:8, inner:{total:10.1s, concurrency:5, task:7, construct:92.7ms, fetch:9.97s, build:14ms, join:5.9ms}	inner join, inner:IndexReader_58, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	20.4 MB	N/A
    ├─IndexReader_55(Build)	234478.88	99450	root	partition:p20260401,p20260501,p20260601,pmax	time:175.3ms, open:87.5µs, close:7.79µs, loops:99, cop_task: {num: 11, max: 174.4ms, min: 851.4µs, avg: 20.9ms, p95: 174.4ms, max_proc_keys: 117427, p95_proc_keys: 117427, tot_proc: 165.8ms, tot_wait: 2.19ms, copr_cache: disabled, build_task_duration: 35.3µs, max_distsql_concurrency: 4}, fetch_resp_duration: 173.5ms, rpc_info:{Cop:{num_rpc:11, total_time:230.1ms}}	index:Selection_54	4.76 MB	N/A
    │ └─Selection_54	234478.88	99450	cop[tikv]		tikv_task:{proc max:130ms, min:0s, avg: 15.5ms, p80:10ms, p95:130ms, iters:206, tasks:11}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 40538991, total_keys: 55418, get_snapshot_time: 2.61ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 165.8ms, total_suspend_time: 126.4µs, total_wait_time: 2.19ms, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_53	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:120ms, min:0s, avg: 14.5ms, p80:10ms, p95:120ms, iters:206, tasks:11}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_58(Probe)	366700.29	4488	root	partition:p20260401,p20260501,p20260601,pmax	total_time:9.93s, total_open:190.4ms, total_close:73µs, loops:16, cop_task: {num: 86, max: 1.91s, min: 1.52ms, avg: 233ms, p95: 1.31s, max_proc_keys: 432, p95_proc_keys: 224, tot_proc: 12.2s, tot_wait: 9.36ms, copr_cache: disabled, build_task_duration: 37.3ms, max_distsql_concurrency: 14}, fetch_resp_duration: 9.73s, rpc_info:{Cop:{num_rpc:86, total_time:20s}}	index:Selection_57	12.6 KB	N/A
      └─Selection_57	366700.29	4488	cop[tikv]		tikv_task:{proc max:1.78s, min:0s, avg: 142.8ms, p80:160ms, p95:690ms, iters:146, tasks:86}, scan_detail: {total_process_keys: 4488, total_process_keys_size: 1179527, total_keys: 31858, get_snapshot_time: 8.09ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 12.2s, total_suspend_time: 5.56ms, total_wait_time: 9.36ms, total_kv_read_wall_time: 11.4s}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_56	496902.96	4488	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:1.78s, min:0s, avg: 142.8ms, p80:160ms, p95:690ms, iters:146, tasks:86}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
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
-- explain_analyze_elapsed_ms=988.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Selection_13	0.80	1	root		time:894.9ms, open:99.9µs, close:12.2µs, loops:2, RU:1240.59	gt(Column#106, ?)	24.1 KB	N/A
└─HashAgg_17	1.00	1	root		time:894.8ms, open:97.7µs, close:11.5µs, loops:3	funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	537.1 KB	0 Bytes
  └─IndexHashJoin_28	366700.29	4488	root		time:893.2ms, open:89.1µs, close:10.9µs, loops:8, inner:{total:1.53s, concurrency:5, task:7, construct:96.4ms, fetch:1.43s, build:14ms, join:4.63ms}	inner join, inner:IndexReader_56, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	18.8 MB	N/A
    ├─IndexReader_53(Build)	234478.88	99450	root	partition:p20260401,p20260501,p20260601,pmax	time:163.7ms, open:88µs, close:8.04µs, loops:99, cop_task: {num: 11, max: 162.7ms, min: 613.1µs, avg: 19.5ms, p95: 162.7ms, max_proc_keys: 117427, p95_proc_keys: 117427, tot_proc: 184.3ms, tot_wait: 360.1µs, copr_cache: disabled, build_task_duration: 34.1µs, max_distsql_concurrency: 4}, fetch_resp_duration: 162ms, rpc_info:{Cop:{num_rpc:11, total_time:214.4ms}}	index:Selection_52	4.76 MB	N/A
    │ └─Selection_52	234478.88	99450	cop[tikv]		tikv_task:{proc max:140ms, min:0s, avg: 16.4ms, p80:10ms, p95:140ms, iters:206, tasks:11}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 40538991, total_keys: 55418, get_snapshot_time: 190.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 184.3ms, total_suspend_time: 126.9µs, total_wait_time: 360.1µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_51	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:140ms, min:0s, avg: 16.4ms, p80:10ms, p95:140ms, iters:206, tasks:11}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_56(Probe)	366700.29	4488	root	partition:p20260401,p20260501,p20260601,pmax	total_time:1.39s, total_open:178.3ms, total_close:70.2µs, loops:16, cop_task: {num: 89, max: 563.1ms, min: 697.8µs, avg: 22.5ms, p95: 67.9ms, max_proc_keys: 224, p95_proc_keys: 224, tot_proc: 1.48s, tot_wait: 2.87ms, copr_cache: disabled, build_task_duration: 38.3ms, max_distsql_concurrency: 14}, fetch_resp_duration: 1.21s, rpc_info:{Cop:{num_rpc:89, total_time:2s}}	index:Selection_55	13.4 KB	N/A
      └─Selection_55	366700.29	4488	cop[tikv]		tikv_task:{proc max:550ms, min:0s, avg: 16.6ms, p80:10ms, p95:50ms, iters:149, tasks:89}, scan_detail: {total_process_keys: 4488, total_process_keys_size: 1365621, total_keys: 49649, get_snapshot_time: 1.27ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.48s, total_suspend_time: 1.58ms, total_wait_time: 2.87ms, total_kv_read_wall_time: 1.26s}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_54	496902.96	4488	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:550ms, min:0s, avg: 16.6ms, p80:10ms, p95:50ms, iters:149, tasks:89}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### 6. group_c_bundle_021

- Filter/window: `p.merchant_account_number = %s` / `30d`
- Chosen event: `INV0037793946` kind=`hot_merchant_account_number` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_32_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 459.4 ms | ok |
| `optimized_default` | `{}` | 316.3 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 343.9 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 238.2 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 347.9 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 249.7 ms | ok |

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
-- explain_analyze_elapsed_ms=459.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_8	108.67	1	root		time:331.8ms, open:104.9µs, close:53.9µs, loops:2, RU:503.62, Concurrency:OFF	Column#106, Column#107, Column#108, Column#109, Column#110, Column#111, Column#112, Column#113, Column#114, Column#115, Column#114, Column#116, Column#114, Column#117, Column#118, Column#119, Column#118, Column#120, Column#118, Column#121, Column#122, Column#123, Column#122, Column#124, Column#122, Column#125, Column#126, Column#127, Column#126, Column#128, Column#126, Column#129, Column#130, Column#131, Column#130, Column#132, Column#133, Column#134, Column#133, Column#135, Column#136, Column#137, Column#136, Column#138, Column#139, Column#140, Column#139, Column#141, Column#142, Column#143, Column#142, Column#144, Column#145, Column#146, Column#145, Column#147, Column#148, Column#149, Column#148, Column#150, Column#151, Column#152, Column#151, Column#153, Column#154, Column#155, Column#154, Column#156, Column#157, Column#158, Column#157, Column#159, Column#160, Column#161, Column#160, Column#162, Column#163, Column#164, Column#163	296.5 KB	N/A
└─HashAgg_12	108.67	1	root		time:331.7ms, open:98.2µs, close:52.2µs, loops:2	group by:Column#242, funcs:count(distinct Column#183)->Column#106, funcs:count(distinct Column#184)->Column#107, funcs:count(distinct Column#185)->Column#108, funcs:count(distinct Column#186)->Column#109, funcs:count(distinct Column#187)->Column#110, funcs:count(distinct Column#188)->Column#111, funcs:count(distinct Column#189)->Column#112, funcs:count(distinct Column#190)->Column#113, funcs:sum(Column#191)->Column#114, funcs:count(distinct Column#192)->Column#115, funcs:count(distinct Column#193)->Column#116, funcs:count(distinct Column#194)->Column#117, funcs:sum(Column#195)->Column#118, funcs:count(distinct Column#196)->Column#119, funcs:count(distinct Column#197)->Column#120, funcs:count(distinct Column#198)->Column#121, funcs:sum(Column#199)->Column#122, funcs:count(distinct Column#200)->Column#123, funcs:count(distinct Column#201)->Column#124, funcs:count(distinct Column#202)->Column#125, funcs:sum(Column#203)->Column#126, funcs:count(distinct Column#204)->Column#127, funcs:count(distinct Column#205)->Column#128, funcs:min(Column#206)->Column#129, funcs:sum(Column#207)->Column#130, funcs:max(Column#208)->Column#131, funcs:min(Column#209)->Column#132, funcs:sum(Column#210)->Column#133, funcs:max(Column#211)->Column#134, funcs:min(Column#212)->Column#135, funcs:sum(Column#213)->Column#136, funcs:max(Column#214)->Column#137, funcs:min(Column#215)->Column#138, funcs:sum(Column#216)->Column#139, funcs:max(Column#217)->Column#140, funcs:min(Column#218)->Column#141, funcs:sum(Column#219)->Column#142, funcs:max(Column#220)->Column#143, funcs:min(Column#221)->Column#144, funcs:sum(Column#222)->Column#145, funcs:max(Column#223)->Column#146, funcs:min(Column#224)->Column#147, funcs:sum(Column#225)->Column#148, funcs:max(Column#226)->Column#149, funcs:min(Column#227)->Column#150, funcs:sum(Column#228)->Column#151, funcs:max(Column#229)->Column#152, funcs:min(Column#230)->Column#153, funcs:sum(Column#231)->Column#154, funcs:max(Column#232)->Column#155, funcs:min(Column#233)->Column#156, funcs:sum(Column#234)->Column#157, funcs:max(Column#235)->Column#158, funcs:min(Column#236)->Column#159, funcs:sum(Column#237)->Column#160, funcs:max(Column#238)->Column#161, funcs:min(Column#239)->Column#162, funcs:sum(Column#240)->Column#163, funcs:max(Column#241)->Column#164	3.09 MB	0 Bytes
  └─Projection_81	50174.75	3334	root		time:323.1ms, open:81.3µs, close:51.3µs, loops:6, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#183, intuit_risk.deviceprofile_fact.exact_id->Column#184, intuit_risk.deviceprofile_fact.input_ip->Column#185, intuit_risk.deviceprofile_fact.true_ip->Column#186, intuit_risk.deviceprofile_fact.proxy_ip->Column#187, intuit_risk.deviceprofile_fact.agent_type->Column#188, intuit_risk.deviceprofile_fact.agent_os->Column#189, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#190, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#191, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#192, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#193, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#194, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#196, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#197, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#198, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#199, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#200, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#201, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#202, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#203, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#204, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#205, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#207, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#208, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#209, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#210, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#212, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#213, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#214, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#215, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#217, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#218, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#221, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#222, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#223, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#225, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#226, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#230, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#232, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#234, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#235, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#236, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#237, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#238, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#239, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#240, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#241, intuit_risk.pmt_txn_fact.merchant_account_number->Column#242	6.86 MB	N/A
    └─IndexHashJoin_30	50174.75	3334	root		time:322.9ms, open:80.2µs, close:17.2µs, loops:6, inner:{total:743.1ms, concurrency:5, task:3, construct:7.24ms, fetch:732.8ms, build:1.45ms, join:3.06ms}	inner join, inner:IndexLookUp_45, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	2.59 MB	N/A
      ├─IndexReader_41(Build)	28365.44	11721	root	partition:p20260401,p20260501,p20260601,pmax	time:18.2ms, open:78.7µs, close:13.5µs, loops:14, cop_task: {num: 13, max: 7.72ms, min: 417.7µs, avg: 2.53ms, p95: 7.72ms, max_proc_keys: 5098, p95_proc_keys: 5098, tot_proc: 20.2ms, tot_wait: 2.48ms, copr_cache: disabled, build_task_duration: 29.8µs, max_distsql_concurrency: 4}, fetch_resp_duration: 17.8ms, rpc_info:{Cop:{num_rpc:13, total_time:32.7ms}}	index:Selection_40	226.8 KB	N/A
      │ └─Selection_40	28365.44	11721	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 769.2µs, p80:0s, p95:10ms, iters:62, tasks:13}, scan_detail: {total_process_keys: 18068, total_process_keys_size: 2321747, total_keys: 18081, get_snapshot_time: 2.25ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 20.2ms, total_suspend_time: 27.1µs, total_wait_time: 2.48ms, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
      │   └─IndexRangeScan_39	38437.04	18068	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 769.2µs, p80:0s, p95:10ms, iters:62, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
      └─IndexLookUp_45(Probe)	50174.75	3334	root	partition:p20260401,p20260501,p20260601,pmax	total_time:729.3ms, total_open:15ms, total_close:29.1µs, loops:8, index_task: {total_time: 590.7ms, fetch_handle: 590.7ms, build: 8.01µs, wait: 25.6µs}, table_task: {total_time: 232.8ms, num: 7, concurrency: 5}, next: {wait_index: 517ms, wait_table_lookup_build: 2.26ms, wait_table_lookup_resp: 194.3ms}		1.71 MB	N/A
        ├─Selection_44(Build)	50174.75	3334	cop[tikv]		total_time:590.8ms, total_open:0s, total_close:0s, loops:25, cop_task: {num: 15, max: 247.1ms, min: 3.24ms, avg: 84.2ms, p95: 247.1ms, max_proc_keys: 1131, p95_proc_keys: 1131, tot_proc: 754.9ms, tot_wait: 2.09ms, copr_cache: disabled, build_task_duration: 3.44ms, max_distsql_concurrency: 2}, fetch_resp_duration: 590.3ms, rpc_info:{Cop:{num_rpc:15, total_time:1.26s}}, tikv_task:{proc max:190ms, min:0s, avg: 50ms, p80:100ms, p95:190ms, iters:38, tasks:15}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 344574, total_keys: 22446, get_snapshot_time: 1.87ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 754.9ms, total_suspend_time: 1.85ms, total_wait_time: 2.09ms, total_kv_read_wall_time: 650ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
        │ └─IndexRangeScan_42	74076.41	3334	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:190ms, min:0s, avg: 50ms, p80:100ms, p95:190ms, iters:38, tasks:15}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
        └─TableRowIDScan_43(Probe)	50174.75	3334	cop[tikv]	table:d	total_time:230ms, total_open:0s, total_close:35.7µs, loops:14, cop_task: {num: 478, max: 40.6ms, min: 0s, avg: 1.38ms, p95: 8.14ms, max_proc_keys: 45, p95_proc_keys: 25, tot_proc: 800.9ms, tot_wait: 202.2ms, copr_cache: disabled, build_task_duration: 1.33ms, max_distsql_concurrency: 6, max_extra_concurrency: 10, store_batch_num: 342, store_batch_fallback_num: 20}, fetch_resp_duration: 227.7ms, rpc_info:{Cop:{num_rpc:137, total_time:659.2ms}, rpc_errors:{bucket_version_not_match:1}}, backoff{regionMiss: 44ms}, tikv_task:{proc max:40ms, min:0s, avg: 2.05ms, p80:0s, p95:10ms, iters:492, tasks:478}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 2010814, total_keys: 3334, get_snapshot_time: 146.3ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 800.9ms, total_suspend_time: 1.14ms, total_wait_time: 202.2ms, total_kv_read_wall_time: 980ms}	keep order:false	N/A	N/A
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
-- best_variant=optimized_hashagg_32_8
-- explain_analyze_elapsed_ms=238.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_10	0.80	1	root		time:198.7ms, open:90µs, close:54.7µs, loops:2, RU:341.55, Concurrency:OFF	Column#106->Column#166, Column#107->Column#167, Column#108->Column#168, Column#109->Column#169, Column#110->Column#170, Column#111->Column#171, Column#112->Column#172, Column#113->Column#173, Column#114->Column#174, Column#115->Column#175, Column#114->Column#176, Column#116->Column#177, Column#114->Column#178, Column#117->Column#179, Column#118->Column#180, Column#119->Column#181, Column#118->Column#182, Column#120->Column#183, Column#118->Column#184, Column#121->Column#185, Column#122->Column#186, Column#123->Column#187, Column#122->Column#188, Column#124->Column#189, Column#122->Column#190, Column#125->Column#191, Column#126->Column#192, Column#127->Column#193, Column#126->Column#194, Column#128->Column#195, Column#126->Column#196, Column#129->Column#197, Column#130->Column#198, Column#131->Column#199, Column#130->Column#200, Column#132->Column#201, Column#133->Column#202, Column#134->Column#203, Column#133->Column#204, Column#135->Column#205, Column#136->Column#206, Column#137->Column#207, Column#136->Column#208, Column#138->Column#209, Column#139->Column#210, Column#140->Column#211, Column#139->Column#212, Column#141->Column#213, Column#142->Column#214, Column#143->Column#215, Column#142->Column#216, Column#144->Column#217, Column#145->Column#218, Column#146->Column#219, Column#145->Column#220, Column#147->Column#221, Column#148->Column#222, Column#149->Column#223, Column#148->Column#224, Column#150->Column#225, Column#151->Column#226, Column#152->Column#227, Column#151->Column#228, Column#153->Column#229, Column#154->Column#230, Column#155->Column#231, Column#154->Column#232, Column#156->Column#233, Column#157->Column#234, Column#158->Column#235, Column#157->Column#236, Column#159->Column#237, Column#160->Column#238, Column#161->Column#239, Column#160->Column#240, Column#162->Column#241, Column#163->Column#242, Column#164->Column#243, Column#163->Column#244	313.2 KB	N/A
└─Selection_12	0.80	1	root		time:198.6ms, open:85.7µs, close:52.9µs, loops:2	gt(Column#165, ?)	345.9 KB	N/A
  └─HashAgg_16	1.00	1	root		time:198.6ms, open:80.3µs, close:52.1µs, loops:3	funcs:count(distinct Column#263)->Column#106, funcs:count(distinct Column#264)->Column#107, funcs:count(distinct Column#265)->Column#108, funcs:count(distinct Column#266)->Column#109, funcs:count(distinct Column#267)->Column#110, funcs:count(distinct Column#268)->Column#111, funcs:count(distinct Column#269)->Column#112, funcs:count(distinct Column#270)->Column#113, funcs:sum(Column#271)->Column#114, funcs:count(distinct Column#272)->Column#115, funcs:count(distinct Column#273)->Column#116, funcs:count(distinct Column#274)->Column#117, funcs:sum(Column#275)->Column#118, funcs:count(distinct Column#276)->Column#119, funcs:count(distinct Column#277)->Column#120, funcs:count(distinct Column#278)->Column#121, funcs:sum(Column#279)->Column#122, funcs:count(distinct Column#280)->Column#123, funcs:count(distinct Column#281)->Column#124, funcs:count(distinct Column#282)->Column#125, funcs:sum(Column#283)->Column#126, funcs:count(distinct Column#284)->Column#127, funcs:count(distinct Column#285)->Column#128, funcs:min(Column#286)->Column#129, funcs:sum(Column#287)->Column#130, funcs:max(Column#288)->Column#131, funcs:min(Column#289)->Column#132, funcs:sum(Column#290)->Column#133, funcs:max(Column#291)->Column#134, funcs:min(Column#292)->Column#135, funcs:sum(Column#293)->Column#136, funcs:max(Column#294)->Column#137, funcs:min(Column#295)->Column#138, funcs:sum(Column#296)->Column#139, funcs:max(Column#297)->Column#140, funcs:min(Column#298)->Column#141, funcs:sum(Column#299)->Column#142, funcs:max(Column#300)->Column#143, funcs:min(Column#301)->Column#144, funcs:sum(Column#302)->Column#145, funcs:max(Column#303)->Column#146, funcs:min(Column#304)->Column#147, funcs:sum(Column#305)->Column#148, funcs:max(Column#306)->Column#149, funcs:min(Column#307)->Column#150, funcs:sum(Column#308)->Column#151, funcs:max(Column#309)->Column#152, funcs:min(Column#310)->Column#153, funcs:sum(Column#311)->Column#154, funcs:max(Column#312)->Column#155, funcs:min(Column#313)->Column#156, funcs:sum(Column#314)->Column#157, funcs:max(Column#315)->Column#158, funcs:min(Column#316)->Column#159, funcs:sum(Column#317)->Column#160, funcs:max(Column#318)->Column#161, funcs:min(Column#319)->Column#162, funcs:sum(Column#320)->Column#163, funcs:max(Column#321)->Column#164, funcs:count(?)->Column#165	3.07 MB	0 Bytes
    └─Projection_84	50174.75	3334	root		time:189.9ms, open:69.2µs, close:51.2µs, loops:6, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#263, intuit_risk.deviceprofile_fact.exact_id->Column#264, intuit_risk.deviceprofile_fact.input_ip->Column#265, intuit_risk.deviceprofile_fact.true_ip->Column#266, intuit_risk.deviceprofile_fact.proxy_ip->Column#267, intuit_risk.deviceprofile_fact.agent_type->Column#268, intuit_risk.deviceprofile_fact.agent_os->Column#269, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#270, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#271, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#272, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#273, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#274, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#275, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#276, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#277, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#278, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#279, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#280, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#281, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#282, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#283, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#284, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#285, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#286, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#287, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#288, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#289, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#290, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#291, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#292, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#293, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#294, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#295, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#296, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#297, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#298, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#299, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#300, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#301, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#302, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#303, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#304, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#305, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#306, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#307, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#308, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#309, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#310, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#311, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#312, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#313, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#314, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#315, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#316, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#317, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#318, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#319, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#320, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#321	6.52 MB	N/A
      └─IndexHashJoin_28	50174.75	3334	root		time:189.9ms, open:68µs, close:15.3µs, loops:6, inner:{total:397.3ms, concurrency:5, task:3, construct:7.25ms, fetch:387.1ms, build:1.47ms, join:2.93ms}	inner join, inner:IndexLookUp_43, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	2.53 MB	N/A
        ├─IndexReader_39(Build)	28365.44	11721	root	partition:p20260401,p20260501,p20260601,pmax	time:13.5ms, open:66.5µs, close:10.3µs, loops:14, cop_task: {num: 13, max: 4.4ms, min: 383.1µs, avg: 1.6ms, p95: 4.4ms, max_proc_keys: 5098, p95_proc_keys: 5098, tot_proc: 10.9ms, tot_wait: 353.9µs, copr_cache: disabled, build_task_duration: 24.3µs, max_distsql_concurrency: 4}, fetch_resp_duration: 13.1ms, rpc_info:{Cop:{num_rpc:13, total_time:20.6ms}}	index:Selection_38	315.0 KB	N/A
        │ └─Selection_38	28365.44	11721	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:62, tasks:13}, scan_detail: {total_process_keys: 18068, total_process_keys_size: 2321747, total_keys: 18081, get_snapshot_time: 154.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 10.9ms, total_suspend_time: 19.3µs, total_wait_time: 353.9µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        │   └─IndexRangeScan_37	38437.04	18068	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:62, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
        └─IndexLookUp_43(Probe)	50174.75	3334	root	partition:p20260401,p20260501,p20260601,pmax	total_time:383.8ms, total_open:15.2ms, total_close:24.5µs, loops:8, index_task: {total_time: 344.4ms, fetch_handle: 344.4ms, build: 13.6µs, wait: 25µs}, table_task: {total_time: 38.6ms, num: 7, concurrency: 5}, next: {wait_index: 348.6ms, wait_table_lookup_build: 1.63ms, wait_table_lookup_resp: 17.5ms}		1.71 MB	N/A
          ├─Selection_42(Build)	50174.75	3334	cop[tikv]		total_time:344.6ms, total_open:0s, total_close:0s, loops:25, cop_task: {num: 15, max: 155.1ms, min: 3.17ms, avg: 45.8ms, p95: 155.1ms, max_proc_keys: 1163, p95_proc_keys: 1163, tot_proc: 610.9ms, tot_wait: 415µs, copr_cache: disabled, build_task_duration: 3.39ms, max_distsql_concurrency: 2}, fetch_resp_duration: 344ms, rpc_info:{Cop:{num_rpc:15, total_time:687ms}}, tikv_task:{proc max:150ms, min:0s, avg: 40.7ms, p80:80ms, p95:150ms, iters:39, tasks:15}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 344520, total_keys: 22423, get_snapshot_time: 199.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 610.9ms, total_suspend_time: 1.25ms, total_wait_time: 415µs, total_kv_read_wall_time: 500ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │ └─IndexRangeScan_40	74076.41	3334	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:150ms, min:0s, avg: 40.7ms, p80:80ms, p95:150ms, iters:39, tasks:15}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
          └─TableRowIDScan_41(Probe)	50174.75	3334	cop[tikv]	table:d	total_time:35.9ms, total_open:0s, total_close:32.3µs, loops:14, cop_task: {num: 489, max: 1.59ms, min: 0s, avg: 215.5µs, p95: 966.8µs, max_proc_keys: 46, p95_proc_keys: 24, tot_proc: 56.5ms, tot_wait: 17.7ms, copr_cache: disabled, build_task_duration: 1.27ms, max_distsql_concurrency: 6, max_extra_concurrency: 10, store_batch_num: 358, store_batch_fallback_num: 16}, fetch_resp_duration: 33.6ms, rpc_info:{Cop:{num_rpc:131, total_time:104.2ms}}, tikv_task:{proc max:10ms, min:0s, avg: 224.9µs, p80:0s, p95:0s, iters:501, tasks:489}, scan_detail: {total_process_keys: 3334, total_process_keys_size: 2010814, total_keys: 3334, get_snapshot_time: 2.74ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 56.5ms, total_wait_time: 17.7ms, total_kv_read_wall_time: 110ms}	keep order:false	N/A	N/A
```

### 7. group_b_bundle_020

- Filter/window: `d.true_ip = %s` / `180d`
- Chosen event: `INV0039365135` kind=`hot_true_ip` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 3034.6 ms | ok |
| `optimized_default` | `{}` | 1196.5 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 1128.8 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 1129.1 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 1154.9 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 1128.5 ms | ok |

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
-- explain_analyze_elapsed_ms=3034.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_324	1.00	1	root		time:9.96µs, open:2.82µs, close:858ns, loops:2, RU:4009.72, Concurrency:OFF	?->Column#788, ?->Column#908, ?->Column#1020, ?->Column#1114, ?->Column#1210	0 Bytes	N/A
└─TableDual_326	1.00	1	root		time:1.97µs, open:221ns, close:217ns, loops:2	rows:1	N/A	N/A
ScalarSubQuery_111	N/A	0	root			Output: ScalarQueryCol#787	N/A	N/A
└─MaxOneRow_70	1.00	1	root		time:1.15s, open:9.6µs, close:34.4µs, loops:1		N/A	N/A
  └─HashAgg_75	1.00	1	root		time:1.15s, open:8.77µs, close:33.7µs, loops:2	funcs:count(distinct Column#738)->Column#739	24.2 MB	0 Bytes
    └─Union_79	693750.42	523720	root		time:957.7ms, open:822ns, close:32.7µs, loops:514		N/A	N/A
      ├─Projection_81	693749.40	523720	root		time:959.7ms, open:70.9µs, close:25.9µs, loops:514, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#738	871.9 KB	N/A
      │ └─IndexReader_84	693749.40	523720	root		time:976.3ms, open:69.7µs, close:9.23µs, loops:514, cop_task: {num: 21, max: 894.6ms, min: 1.14ms, avg: 57.5ms, p95: 59.2ms, max_proc_keys: 289760, p95_proc_keys: 50144, tot_proc: 410.4ms, tot_wait: 2.14ms, copr_cache: disabled, build_task_duration: 24µs, max_distsql_concurrency: 2}, fetch_resp_duration: 974.5ms, rpc_info:{Cop:{num_rpc:21, total_time:1.21s}}	index:IndexRangeScan_83	36.4 MB	N/A
      │   └─IndexRangeScan_83	693749.40	523720	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:170ms, min:0s, avg: 18.1ms, p80:20ms, p95:40ms, iters:593, tasks:21}, scan_detail: {total_process_keys: 523720, total_process_keys_size: 96225360, total_keys: 233980, get_snapshot_time: 1.84ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 410.4ms, total_suspend_time: 546µs, total_wait_time: 2.14ms, total_kv_read_wall_time: 210ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_85	1.02	0	root		time:995.4µs, open:73.1µs, close:5.64µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#738	10.4 KB	N/A
        └─IndexReader_92	1.02	0	root	partition:p20251101	time:986.6µs, open:68.7µs, close:3.58µs, loops:1, cop_task: {num: 1, max: 893.1µs, proc_keys: 0, tot_proc: 31.8µs, tot_wait: 549.2µs, copr_cache: disabled, build_task_duration: 21.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 904.8µs, rpc_info:{Cop:{num_rpc:1, total_time:880.6µs}}	index:Selection_91	255 Bytes	N/A
          └─Selection_91	1.02	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 528.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 31.8µs, total_wait_time: 549.2µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	N/A	N/A
            └─IndexRangeScan_90	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_165	N/A	0	root			Output: ScalarQueryCol#907	N/A	N/A
└─MaxOneRow_124	1.00	1	root		time:932.7ms, open:10.1µs, close:40µs, loops:1		N/A	N/A
  └─HashAgg_129	1.00	1	root		time:932.7ms, open:9.59µs, close:39.4µs, loops:2	funcs:count(distinct Column#856)->Column#857	23.2 MB	0 Bytes
    └─Union_133	695358.92	519249	root		time:733.1ms, open:868ns, close:38.5µs, loops:509		N/A	N/A
      ├─Projection_135	695357.87	519249	root		time:732.6ms, open:76.4µs, close:31.9µs, loops:509, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#856	820.0 KB	N/A
      │ └─IndexReader_138	695357.87	519249	root		time:736ms, open:74.7µs, close:10.1µs, loops:509, cop_task: {num: 8, max: 465.8ms, min: 4.77ms, avg: 103.6ms, p95: 465.8ms, max_proc_keys: 289760, p95_proc_keys: 289760, tot_proc: 346.2ms, tot_wait: 781.6µs, copr_cache: disabled, build_task_duration: 27.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 734.3ms, rpc_info:{Cop:{num_rpc:8, total_time:829ms}}	index:IndexRangeScan_137	56.2 MB	N/A
      │   └─IndexRangeScan_137	695357.87	519249	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:170ms, min:0s, avg: 42.5ms, p80:140ms, p95:170ms, iters:538, tasks:8}, scan_detail: {total_process_keys: 519249, total_process_keys_size: 67448303, total_keys: 11846, get_snapshot_time: 697.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 346.2ms, total_suspend_time: 65.2µs, total_wait_time: 781.6µs, total_kv_read_wall_time: 30ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_139	1.04	0	root		time:601.6µs, open:83.7µs, close:5.45µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#856	5.42 KB	N/A
        └─IndexReader_146	1.04	0	root	partition:p20251101	time:593.3µs, open:79.3µs, close:3.17µs, loops:1, cop_task: {num: 1, max: 477.8µs, proc_keys: 0, tot_proc: 28.5µs, tot_wait: 47.6µs, copr_cache: disabled, build_task_duration: 24.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 501.8µs, rpc_info:{Cop:{num_rpc:1, total_time:456.9µs}}	index:Selection_145	255 Bytes	N/A
          └─Selection_145	1.04	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.5µs, total_wait_time: 47.6µs}	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	N/A	N/A
            └─IndexRangeScan_144	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_219	N/A	0	root			Output: ScalarQueryCol#1019	N/A	N/A
└─MaxOneRow_178	1.00	1	root		time:811.8ms, open:10.5µs, close:36µs, loops:1		N/A	N/A
  └─HashAgg_183	1.00	1	root		time:811.8ms, open:9.88µs, close:35.5µs, loops:2	funcs:count(distinct Column#976)->Column#977	9.42 MB	0 Bytes
    └─Union_187	651787.72	460693	root		time:650.3ms, open:935ns, close:34.8µs, loops:452		N/A	N/A
      ├─Projection_189	651786.72	460693	root		time:650ms, open:96.4µs, close:28.6µs, loops:452, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#976	640.0 KB	N/A
      │ └─IndexReader_192	651786.72	460693	root		time:655.5ms, open:91.9µs, close:9.52µs, loops:452, cop_task: {num: 11, max: 474.3ms, min: 3.5ms, avg: 63.5ms, p95: 474.3ms, max_proc_keys: 345056, p95_proc_keys: 345056, tot_proc: 375.9ms, tot_wait: 1.03ms, copr_cache: disabled, build_task_duration: 29.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 653.9ms, rpc_info:{Cop:{num_rpc:11, total_time:698.5ms}}	index:IndexRangeScan_191	33.6 MB	N/A
      │   └─IndexRangeScan_191	651786.72	460693	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:190ms, min:0s, avg: 29.1ms, p80:20ms, p95:190ms, iters:493, tasks:11}, scan_detail: {total_process_keys: 460693, total_process_keys_size: 60002367, total_keys: 115647, get_snapshot_time: 854.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 375.9ms, total_suspend_time: 237µs, total_wait_time: 1.03ms, total_kv_read_wall_time: 130ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_193	1.00	0	root		time:718.5µs, open:132.4µs, close:5.3µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#976	12.2 KB	N/A
        └─IndexReader_200	1.00	0	root	partition:p20251101	time:712.7µs, open:129.8µs, close:3.77µs, loops:1, cop_task: {num: 1, max: 528.8µs, proc_keys: 0, tot_proc: 28.8µs, tot_wait: 51.2µs, copr_cache: disabled, build_task_duration: 19.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 563.6µs, rpc_info:{Cop:{num_rpc:1, total_time:505µs}}	index:Selection_199	255 Bytes	N/A
          └─Selection_199	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.8µs, total_wait_time: 51.2µs}	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	N/A	N/A
            └─IndexRangeScan_198	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_267	N/A	0	root			Output: ScalarQueryCol#1113	N/A	N/A
└─MaxOneRow_232	1.00	1	root		time:63.9ms, open:11.7µs, close:32.3µs, loops:1		N/A	N/A
  └─HashAgg_237	1.00	1	root		time:63.9ms, open:11µs, close:31.7µs, loops:2	funcs:count(distinct Column#1088)->Column#1089	319.6 KB	0 Bytes
    └─Union_241	231700.09	55302	root		time:55.5ms, open:956ns, close:31µs, loops:56		N/A	N/A
      ├─Projection_243	231699.09	55302	root		time:56ms, open:84.6µs, close:24.9µs, loops:56, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1088	628.3 KB	N/A
      │ └─IndexReader_246	231699.09	55302	root		time:58.8ms, open:83.4µs, close:8.43µs, loops:56, cop_task: {num: 9, max: 17.5ms, min: 1.37ms, avg: 6.78ms, p95: 17.5ms, max_proc_keys: 17376, p95_proc_keys: 17376, tot_proc: 44.5ms, tot_wait: 745.7µs, copr_cache: disabled, build_task_duration: 27.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 58.3ms, rpc_info:{Cop:{num_rpc:9, total_time:60.9ms}}	index:IndexRangeScan_245	3.18 MB	N/A
      │   └─IndexRangeScan_245	231699.09	55302	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 4.44ms, p80:10ms, p95:10ms, iters:89, tasks:9}, scan_detail: {total_process_keys: 55302, total_process_keys_size: 11514477, total_keys: 55311, get_snapshot_time: 590.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 44.5ms, total_suspend_time: 106.3µs, total_wait_time: 745.7µs, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_247	1.00	0	root		time:628.8µs, open:129.9µs, close:5.09µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1088	14.0 KB	N/A
        └─IndexReader_251	1.00	0	root	partition:p20251101	time:623.8µs, open:127.9µs, close:3.4µs, loops:1, cop_task: {num: 1, max: 453.9µs, proc_keys: 0, tot_proc: 25.6µs, tot_wait: 46.2µs, copr_cache: disabled, build_task_duration: 14.1µs, max_distsql_concurrency: 1}, fetch_resp_duration: 480.9µs, rpc_info:{Cop:{num_rpc:1, total_time:438.4µs}}	index:Selection_250	255 Bytes	N/A
          └─Selection_250	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 25.6µs, total_wait_time: 46.2µs}	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	N/A	N/A
            └─IndexRangeScan_249	1.14	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_323	N/A	0	root			Output: ScalarQueryCol#1209	N/A	N/A
└─MaxOneRow_280	1.00	1	root		time:4.49ms, open:10.9µs, close:21.1µs, loops:1		N/A	N/A
  └─HashAgg_285	1.00	1	root		time:4.48ms, open:10.2µs, close:20.7µs, loops:2	funcs:count(distinct Column#1182)->Column#1183	11.7 KB	0 Bytes
    └─Union_289	378709.69	479	root		time:4.41ms, open:892ns, close:20µs, loops:2		N/A	N/A
      ├─Projection_291	378708.69	479	root		time:4.38ms, open:78µs, close:15.7µs, loops:2, Concurrency:5	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1182	76.6 KB	N/A
      │ └─IndexReader_294	378708.69	479	root		time:4.31ms, open:76.2µs, close:6.66µs, loops:2, cop_task: {num: 2, max: 3.01ms, min: 1.11ms, avg: 2.06ms, p95: 3.01ms, max_proc_keys: 255, p95_proc_keys: 255, tot_proc: 1.49ms, tot_wait: 1.02ms, copr_cache: disabled, build_task_duration: 24.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 4.18ms, rpc_info:{Cop:{num_rpc:2, total_time:4.09ms}}	index:IndexRangeScan_293	46.8 KB	N/A
      │   └─IndexRangeScan_293	378708.69	479	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:7, tasks:2}, scan_detail: {total_process_keys: 479, total_process_keys_size: 101568, total_keys: 481, get_snapshot_time: 977.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.49ms, total_suspend_time: 3.79µs, total_wait_time: 1.02ms}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_295	1.00	0	root		time:536.3µs, open:116.1µs, close:3.78µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1182	16.2 KB	N/A
        └─IndexReader_303	1.00	0	root	partition:p20251101	time:532µs, open:114.4µs, close:2.64µs, loops:1, cop_task: {num: 1, max: 385.9µs, proc_keys: 0, tot_proc: 24.7µs, tot_wait: 43.6µs, copr_cache: disabled, build_task_duration: 14.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 406.9µs, rpc_info:{Cop:{num_rpc:1, total_time:372.8µs}}	index:Selection_302	255 Bytes	N/A
          └─Selection_302	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 23.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 24.7µs, total_wait_time: 43.6µs}	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	N/A	N/A
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
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=1128.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_71	1.00	1	root		time:1.09s, open:10.8µs, close:73.7µs, loops:2, RU:3959.51	funcs:count(distinct Column#188)->Column#150, funcs:count(distinct Column#189)->Column#151, funcs:count(distinct Column#190)->Column#152, funcs:count(distinct Column#191)->Column#153, funcs:count(distinct Column#192)->Column#154	57.1 MB	0 Bytes
└─Projection_122	2651307.27	1559443	root		time:392.4ms, open:1.97µs, close:72.5µs, loops:1529, Concurrency:5	case(eq(Column#148, ?), Column#149)->Column#188, case(eq(Column#148, ?), Column#149)->Column#189, case(eq(Column#148, ?), Column#149)->Column#190, case(eq(Column#148, ?), Column#149)->Column#191, case(eq(Column#148, ?), Column#149)->Column#192	1.04 MB	N/A
  └─Union_73	2651307.27	1559443	root		time:417.5ms, open:833ns, close:52.1µs, loops:1529		N/A	N/A
    ├─Projection_75	2651301.78	1559443	root		time:419.4ms, open:125.5µs, close:28µs, loops:1529, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#148, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	957.6 KB	N/A
    │ └─IndexReader_78	2651301.78	1559443	root		time:435.4ms, open:123.6µs, close:10.9µs, loops:1529, cop_task: {num: 51, max: 450ms, min: 969.1µs, avg: 41.6ms, p95: 415ms, max_proc_keys: 345056, p95_proc_keys: 289760, tot_proc: 1.03s, tot_wait: 2.59ms, copr_cache: disabled, build_task_duration: 57.2µs, max_distsql_concurrency: 6}, fetch_resp_duration: 429.6ms, rpc_info:{Cop:{num_rpc:51, total_time:2.12s}}	index:IndexRangeScan_77	98.1 MB	N/A
    │   └─IndexRangeScan_77	2651301.78	1559443	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:190ms, min:0s, avg: 18.8ms, p80:10ms, p95:140ms, iters:1720, tasks:51}, scan_detail: {total_process_keys: 1559443, total_process_keys_size: 235292075, total_keys: 417265, get_snapshot_time: 1.84ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.03s, total_suspend_time: 763.4µs, total_wait_time: 2.59ms, total_kv_read_wall_time: 340ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_79	1.10	0	root		time:650.1µs, open:88µs, close:11.4µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_81	1.10	0	root		time:643.9µs, open:85.6µs, close:8.98µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	11.4 KB	N/A
    │   └─CTEFullScan_83	1.37	0	root	CTE:raw_boundary	time:635.9µs, open:81.7µs, close:7.01µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_87	1.10	0	root		time:658.2µs, open:653.5µs, close:2.98µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	55.9 KB	N/A
    │ └─Selection_89	1.10	0	root		time:653.9µs, open:651.8µs, close:1.05µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	32.6 KB	N/A
    │   └─CTEFullScan_91	1.37	0	root	CTE:raw_boundary	time:649.1µs, open:648.5µs, close:81ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_95	1.10	0	root		time:662.4µs, open:657.9µs, close:2.58µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	6.73 KB	N/A
    │ └─Selection_97	1.10	0	root		time:657.8µs, open:655.9µs, close:829ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	8.61 KB	N/A
    │   └─CTEFullScan_99	1.37	0	root	CTE:raw_boundary	time:653.5µs, open:652.9µs, close:127ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_103	1.10	0	root		time:666.5µs, open:661.9µs, close:2.98µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	83.2 KB	N/A
    │ └─Selection_105	1.10	0	root		time:662.2µs, open:659.9µs, close:1.27µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	44.7 KB	N/A
    │   └─CTEFullScan_107	1.37	0	root	CTE:raw_boundary	time:658.4µs, open:657.9µs, close:72ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_111	1.10	0	root		time:12.6µs, open:7.45µs, close:2.36µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	70.5 KB	N/A
      └─Selection_113	1.10	0	root		time:8.34µs, open:5.49µs, close:1.19µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	19.3 KB	N/A
        └─CTEFullScan_115	1.37	0	root	CTE:raw_boundary	time:1.39µs, open:509ns, close:85ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.37	0	root		time:635.9µs, open:81.7µs, close:7.01µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_58(Seed Part)	1.37	0	root		time:617.1µs, open:78.1µs, close:5.37µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type	36.3 KB	N/A
  └─IndexReader_63	1.71	0	root	partition:p20251101	time:609.8µs, open:73.8µs, close:4.03µs, loops:1, cop_task: {num: 1, max: 503.3µs, proc_keys: 0, tot_proc: 30.5µs, tot_wait: 49.3µs, copr_cache: disabled, build_task_duration: 26.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 519.8µs, rpc_info:{Cop:{num_rpc:1, total_time:483.6µs}}	index:Selection_62	255 Bytes	N/A
    └─Selection_62	1.71	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 30.5µs, total_wait_time: 49.3µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type)))))	N/A	N/A
      └─IndexRangeScan_61	1.72	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### 8. group_b_bundle_012

- Filter/window: `d.true_ip = %s` / `30d`
- Chosen event: `INV0039365135` kind=`hot_true_ip` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 507.2 ms | ok |
| `optimized_default` | `{}` | 502.1 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 504.2 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 505.0 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 2490.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 2410.0 ms | ok |

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
-- explain_analyze_elapsed_ms=507.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	187.67	1	root		time:472.4ms, open:113.8µs, close:43.9µs, loops:2, RU:722.46, Concurrency:OFF	Column#60, Column#61, Column#61, Column#62, Column#62, Column#63, Column#63, Column#64, Column#64, Column#65, Column#65, Column#66, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, Column#73, Column#75, Column#73, Column#76, Column#77, Column#78, Column#77, Column#79, Column#77, Column#80, Column#81, Column#82, Column#81, Column#83, Column#81, Column#84, Column#85, Column#86, Column#85, Column#87, Column#85, Column#88, Column#89, Column#90, Column#89, Column#91, Column#89	99.7 KB	N/A
└─HashAgg_9	187.67	1	root		time:472.3ms, open:110.5µs, close:42µs, loops:2	group by:Column#223, funcs:count(?)->Column#60, funcs:sum(Column#192)->Column#61, funcs:sum(Column#193)->Column#62, funcs:sum(Column#194)->Column#63, funcs:sum(Column#195)->Column#64, funcs:sum(Column#196)->Column#65, funcs:sum(Column#197)->Column#66, funcs:count(distinct Column#198)->Column#67, funcs:count(distinct Column#199)->Column#68, funcs:count(distinct Column#200)->Column#69, funcs:count(distinct Column#201)->Column#70, funcs:count(distinct Column#202)->Column#71, funcs:min(Column#203)->Column#72, funcs:sum(Column#204)->Column#73, funcs:max(Column#205)->Column#74, funcs:avg(Column#206)->Column#75, funcs:min(Column#207)->Column#76, funcs:sum(Column#208)->Column#77, funcs:max(Column#209)->Column#78, funcs:avg(Column#210)->Column#79, funcs:min(Column#211)->Column#80, funcs:sum(Column#212)->Column#81, funcs:max(Column#213)->Column#82, funcs:avg(Column#214)->Column#83, funcs:min(Column#215)->Column#84, funcs:sum(Column#216)->Column#85, funcs:max(Column#217)->Column#86, funcs:avg(Column#218)->Column#87, funcs:min(Column#219)->Column#88, funcs:sum(Column#220)->Column#89, funcs:max(Column#221)->Column#90, funcs:avg(Column#222)->Column#91	23.3 MB	0 Bytes
  └─Projection_29	346177.19	172835	root		time:166.8ms, open:96µs, close:41µs, loops:172, Concurrency:5	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#192, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#193, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#194, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#196, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#197, intuit_risk.deviceprofile_fact.exact_id->Column#198, intuit_risk.deviceprofile_fact.smart_id->Column#199, intuit_risk.deviceprofile_fact.input_ip->Column#200, intuit_risk.deviceprofile_fact.proxy_ip->Column#201, intuit_risk.deviceprofile_fact.agent_type->Column#202, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#203, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#204, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#205, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#207, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#208, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#209, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#210, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#212, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#213, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#214, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#215, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#217, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#222, intuit_risk.deviceprofile_fact.true_ip->Column#223	6.73 MB	N/A
    └─IndexReader_21	346177.19	172835	root	partition:p20260401,p20260501,p20260601,pmax	time:184.6ms, open:95.1µs, close:12.6µs, loops:172, cop_task: {num: 18, max: 248.7ms, min: 962.2µs, avg: 19.5ms, p95: 248.7ms, max_proc_keys: 105587, p95_proc_keys: 105587, tot_proc: 189.8ms, tot_wait: 4.4ms, copr_cache: disabled, build_task_duration: 36.1µs, max_distsql_concurrency: 4}, fetch_resp_duration: 182.3ms, rpc_info:{Cop:{num_rpc:18, total_time:351.3ms}}	index:IndexRangeScan_20	21.0 MB	N/A
      └─IndexRangeScan_20	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:120ms, min:0s, avg: 8.89ms, p80:10ms, p95:120ms, iters:233, tasks:18}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 42640965, total_keys: 67265, get_snapshot_time: 4.1ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 189.8ms, total_suspend_time: 171.8µs, total_wait_time: 4.4ms, total_kv_read_wall_time: 40ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
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
-- explain_analyze_elapsed_ms=502.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:466.2ms, open:131.4µs, close:42.5µs, loops:2, RU:721.60, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	743.2 KB	N/A
└─Selection_9	0.80	1	root		time:466.1ms, open:128.7µs, close:40.7µs, loops:2	gt(Column#60, ?)	488.4 KB	N/A
  └─HashAgg_13	1.00	1	root		time:466ms, open:126µs, close:40.3µs, loops:3	funcs:count(?)->Column#60, funcs:sum(Column#208)->Column#61, funcs:sum(Column#209)->Column#62, funcs:sum(Column#210)->Column#63, funcs:sum(Column#211)->Column#64, funcs:sum(Column#212)->Column#65, funcs:sum(Column#213)->Column#66, funcs:count(distinct Column#214)->Column#67, funcs:count(distinct Column#215)->Column#68, funcs:count(distinct Column#216)->Column#69, funcs:count(distinct Column#217)->Column#70, funcs:count(distinct Column#218)->Column#71, funcs:min(Column#219)->Column#72, funcs:sum(Column#220)->Column#73, funcs:max(Column#221)->Column#74, funcs:avg(Column#222)->Column#75, funcs:min(Column#223)->Column#76, funcs:sum(Column#224)->Column#77, funcs:max(Column#225)->Column#78, funcs:avg(Column#226)->Column#79, funcs:min(Column#227)->Column#80, funcs:sum(Column#228)->Column#81, funcs:max(Column#229)->Column#82, funcs:avg(Column#230)->Column#83, funcs:min(Column#231)->Column#84, funcs:sum(Column#232)->Column#85, funcs:max(Column#233)->Column#86, funcs:avg(Column#234)->Column#87, funcs:min(Column#235)->Column#88, funcs:sum(Column#236)->Column#89, funcs:max(Column#237)->Column#90, funcs:avg(Column#238)->Column#91	23.3 MB	0 Bytes
    └─Projection_28	346177.19	172835	root		time:171.8ms, open:113.8µs, close:39.5µs, loops:172, Concurrency:5	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#208, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#209, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#210, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#211, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#212, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#213, intuit_risk.deviceprofile_fact.exact_id->Column#214, intuit_risk.deviceprofile_fact.smart_id->Column#215, intuit_risk.deviceprofile_fact.input_ip->Column#216, intuit_risk.deviceprofile_fact.proxy_ip->Column#217, intuit_risk.deviceprofile_fact.agent_type->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#222, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#223, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#224, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#225, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#226, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#230, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#231, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#232, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#233, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#234, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#235, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#236, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#237, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#238	6.60 MB	N/A
      └─IndexReader_21	346177.19	172835	root	partition:p20260401,p20260501,p20260601,pmax	time:188.1ms, open:112.6µs, close:12.9µs, loops:172, cop_task: {num: 18, max: 250.9ms, min: 627.4µs, avg: 19.3ms, p95: 250.9ms, max_proc_keys: 105587, p95_proc_keys: 105587, tot_proc: 187.2ms, tot_wait: 573.7µs, copr_cache: disabled, build_task_duration: 34.8µs, max_distsql_concurrency: 4}, fetch_resp_duration: 185.8ms, rpc_info:{Cop:{num_rpc:18, total_time:346.2ms}}	index:IndexRangeScan_20	21.0 MB	N/A
        └─IndexRangeScan_20	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:120ms, min:0s, avg: 8.89ms, p80:10ms, p95:120ms, iters:233, tasks:18}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 42640965, total_keys: 67265, get_snapshot_time: 270.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 187.2ms, total_suspend_time: 172.8µs, total_wait_time: 573.7µs, total_kv_read_wall_time: 40ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 9. group_a_bundle_008

- Filter/window: `p.merchant_account_number = %s` / `7d`
- Chosen event: `INV0030289106` kind=`hot_merchant_account_number` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 109.9 ms | ok |
| `optimized_default` | `{}` | 70.6 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 71.1 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 76.0 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 90.6 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 91.1 ms | ok |

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
-- explain_analyze_elapsed_ms=109.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	70.37	1	root		time:33.2ms, open:261.5µs, close:51.7µs, loops:2, RU:20.33, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75, Column#79, Column#79, Column#80, Column#79, Column#81, Column#79, Column#82, Column#79, Column#83, Column#83, Column#84, Column#83, Column#85, Column#83, Column#86, Column#83, Column#87, Column#87, Column#88, Column#87, Column#89, Column#87, Column#90, Column#87, Column#91, Column#91, Column#92, Column#91, Column#93, Column#91, Column#94, Column#91, Column#95, Column#95, Column#96, Column#95, Column#97, Column#95, Column#98, Column#95, Column#99, Column#99, Column#100, Column#99, Column#101, Column#99, Column#102, Column#99, Column#103, Column#103, Column#104, Column#103, Column#105, Column#103, Column#106, Column#103, Column#107, Column#107, Column#108, Column#107, Column#109, Column#107, Column#110, Column#107, Column#111, Column#111, Column#112, Column#111, Column#113, Column#111, Column#114, Column#111, Column#115, Column#115, Column#116, Column#115, Column#117, Column#115, Column#118, Column#115, Column#119, Column#119, Column#120, Column#119, Column#121, Column#119, Column#122, Column#119, Column#123, Column#123, Column#124, Column#123, Column#125, Column#123, Column#126, Column#123, Column#127, Column#127, Column#128, Column#127, Column#129, Column#127, Column#130, Column#127, Column#131, Column#131, Column#132, Column#131, Column#133, Column#131, Column#134, Column#131, Column#135, Column#135, Column#136, Column#135, Column#137, Column#135, Column#138, Column#135, Column#139, Column#139, Column#140, Column#139, Column#141, Column#139, Column#142, Column#139, Column#143, Column#143, Column#144, Column#143, Column#145, Column#143, Column#146, Column#143, Column#147, Column#147, Column#148, Column#147, Column#149, Column#147, Column#150, Column#147, Column#151, Column#151, Column#152, Column#151, Column#153, Column#151, Column#154, Column#151, Column#155, Column#155, Column#156, Column#155, Column#157, Column#155, Column#158, Column#155, Column#159, Column#159, Column#160, Column#159, Column#161, Column#159, Column#162, Column#159, Column#163, Column#163, Column#164, Column#163, Column#165, Column#163, Column#166, Column#163, Column#167, Column#167, Column#168, Column#167, Column#169, Column#167, Column#170, Column#167, Column#171, Column#171, Column#172, Column#171, Column#173, Column#171, Column#174, Column#171, Column#175, Column#175, Column#176, Column#175, Column#177, Column#175, Column#178, Column#175, Column#179, Column#179, Column#180, Column#179, Column#181, Column#179, Column#182, Column#179, Column#183, Column#183, Column#184, Column#183, Column#185, Column#185, Column#186, Column#185, Column#187, Column#187, Column#188, Column#187, Column#189, Column#189, Column#190, Column#189, Column#191, Column#191, Column#192, Column#191, Column#193, Column#193, Column#194, Column#193, Column#195, Column#195, Column#196, Column#195, Column#197, Column#197, Column#198, Column#197, Column#199, Column#199, Column#200, Column#199, Column#201, Column#201, Column#202, Column#201, Column#203, Column#203, Column#204, Column#203, Column#205, Column#206, Column#207	261.4 KB	N/A
└─HashAgg_9	70.37	1	root		time:32.9ms, open:198.7µs, close:49.9µs, loops:2	group by:Column#1000, funcs:count(?)->Column#47, funcs:sum(Column#840)->Column#48, funcs:min(Column#841)->Column#49, funcs:max(Column#842)->Column#50, funcs:sum(Column#843)->Column#51, funcs:sum(Column#844)->Column#52, funcs:min(Column#845)->Column#53, funcs:max(Column#846)->Column#54, funcs:sum(Column#847)->Column#55, funcs:sum(Column#848)->Column#56, funcs:min(Column#849)->Column#57, funcs:max(Column#850)->Column#58, funcs:sum(Column#851)->Column#59, funcs:sum(Column#852)->Column#60, funcs:min(Column#853)->Column#61, funcs:max(Column#854)->Column#62, funcs:sum(Column#855)->Column#63, funcs:sum(Column#856)->Column#64, funcs:min(Column#857)->Column#65, funcs:max(Column#858)->Column#66, funcs:sum(Column#859)->Column#67, funcs:sum(Column#860)->Column#68, funcs:min(Column#861)->Column#69, funcs:max(Column#862)->Column#70, funcs:sum(Column#863)->Column#71, funcs:sum(Column#864)->Column#72, funcs:min(Column#865)->Column#73, funcs:max(Column#866)->Column#74, funcs:sum(Column#867)->Column#75, funcs:sum(Column#868)->Column#76, funcs:min(Column#869)->Column#77, funcs:max(Column#870)->Column#78, funcs:sum(Column#871)->Column#79, funcs:sum(Column#872)->Column#80, funcs:min(Column#873)->Column#81, funcs:max(Column#874)->Column#82, funcs:sum(Column#875)->Column#83, funcs:sum(Column#876)->Column#84, funcs:min(Column#877)->Column#85, funcs:max(Column#878)->Column#86, funcs:sum(Column#879)->Column#87, funcs:sum(Column#880)->Column#88, funcs:min(Column#881)->Column#89, funcs:max(Column#882)->Column#90, funcs:sum(Column#883)->Column#91, funcs:sum(Column#884)->Column#92, funcs:min(Column#885)->Column#93, funcs:max(Column#886)->Column#94, funcs:sum(Column#887)->Column#95, funcs:sum(Column#888)->Column#96, funcs:min(Column#889)->Column#97, funcs:max(Column#890)->Column#98, funcs:sum(Column#891)->Column#99, funcs:sum(Column#892)->Column#100, funcs:min(Column#893)->Column#101, funcs:max(Column#894)->Column#102, funcs:sum(Column#895)->Column#103, funcs:sum(Column#896)->Column#104, funcs:min(Column#897)->Column#105, funcs:max(Column#898)->Column#106, funcs:sum(Column#899)->Column#107, funcs:sum(Column#900)->Column#108, funcs:min(Column#901)->Column#109, funcs:max(Column#902)->Column#110, funcs:sum(Column#903)->Column#111, funcs:sum(Column#904)->Column#112, funcs:min(Column#905)->Column#113, funcs:max(Column#906)->Column#114, funcs:sum(Column#907)->Column#115, funcs:sum(Column#908)->Column#116, funcs:min(Column#909)->Column#117, funcs:max(Column#910)->Column#118, funcs:sum(Column#911)->Column#119, funcs:sum(Column#912)->Column#120, funcs:min(Column#913)->Column#121, funcs:max(Column#914)->Column#122, funcs:sum(Column#915)->Column#123, funcs:sum(Column#916)->Column#124, funcs:min(Column#917)->Column#125, funcs:max(Column#918)->Column#126, funcs:sum(Column#919)->Column#127, funcs:sum(Column#920)->Column#128, funcs:min(Column#921)->Column#129, funcs:max(Column#922)->Column#130, funcs:sum(Column#923)->Column#131, funcs:sum(Column#924)->Column#132, funcs:min(Column#925)->Column#133, funcs:max(Column#926)->Column#134, funcs:sum(Column#927)->Column#135, funcs:sum(Column#928)->Column#136, funcs:min(Column#929)->Column#137, funcs:max(Column#930)->Column#138, funcs:sum(Column#931)->Column#139, funcs:sum(Column#932)->Column#140, funcs:min(Column#933)->Column#141, funcs:max(Column#934)->Column#142, funcs:sum(Column#935)->Column#143, funcs:sum(Column#936)->Column#144, funcs:min(Column#937)->Column#145, funcs:max(Column#938)->Column#146, funcs:sum(Column#939)->Column#147, funcs:sum(Column#940)->Column#148, funcs:min(Column#941)->Column#149, funcs:max(Column#942)->Column#150, funcs:sum(Column#943)->Column#151, funcs:sum(Column#944)->Column#152, funcs:min(Column#945)->Column#153, funcs:max(Column#946)->Column#154, funcs:sum(Column#947)->Column#155, funcs:sum(Column#948)->Column#156, funcs:min(Column#949)->Column#157, funcs:max(Column#950)->Column#158, funcs:sum(Column#951)->Column#159, funcs:sum(Column#952)->Column#160, funcs:min(Column#953)->Column#161, funcs:max(Column#954)->Column#162, funcs:sum(Column#955)->Column#163, funcs:sum(Column#956)->Column#164, funcs:min(Column#957)->Column#165, funcs:max(Column#958)->Column#166, funcs:sum(Column#959)->Column#167, funcs:sum(Column#960)->Column#168, funcs:min(Column#961)->Column#169, funcs:max(Column#962)->Column#170, funcs:sum(Column#963)->Column#171, funcs:sum(Column#964)->Column#172, funcs:min(Column#965)->Column#173, funcs:max(Column#966)->Column#174, funcs:sum(Column#967)->Column#175, funcs:sum(Column#968)->Column#176, funcs:min(Column#969)->Column#177, funcs:max(Column#970)->Column#178, funcs:sum(Column#971)->Column#179, funcs:sum(Column#972)->Column#180, funcs:min(Column#973)->Column#181, funcs:max(Column#974)->Column#182, funcs:sum(Column#975)->Column#183, funcs:sum(Column#976)->Column#184, funcs:sum(Column#977)->Column#185, funcs:sum(Column#978)->Column#186, funcs:sum(Column#979)->Column#187, funcs:sum(Column#980)->Column#188, funcs:sum(Column#981)->Column#189, funcs:sum(Column#982)->Column#190, funcs:sum(Column#983)->Column#191, funcs:sum(Column#984)->Column#192, funcs:sum(Column#985)->Column#193, funcs:sum(Column#986)->Column#194, funcs:sum(Column#987)->Column#195, funcs:sum(Column#988)->Column#196, funcs:sum(Column#989)->Column#197, funcs:sum(Column#990)->Column#198, funcs:sum(Column#991)->Column#199, funcs:sum(Column#992)->Column#200, funcs:sum(Column#993)->Column#201, funcs:sum(Column#994)->Column#202, funcs:sum(Column#995)->Column#203, funcs:sum(Column#996)->Column#204, funcs:count(distinct Column#997)->Column#205, funcs:count(distinct Column#998)->Column#206, funcs:count(distinct Column#999)->Column#207	6.24 MB	0 Bytes
  └─Projection_32	18368.93	4152	root		time:20.1ms, open:74.7µs, close:48.8µs, loops:6, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#840, intuit_risk.pmt_txn_fact.amount->Column#841, intuit_risk.pmt_txn_fact.amount->Column#842, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#843, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#844, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#845, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#846, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#847, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#848, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#849, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#850, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#851, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#852, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#853, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#854, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#855, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#856, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#857, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#858, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#859, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#860, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#861, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#862, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#863, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#864, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#865, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#866, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#867, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#868, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#869, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#870, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#871, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#872, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#873, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#874, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#875, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#876, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#877, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#878, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#879, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#880, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#881, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#882, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#883, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#884, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#885, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#886, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#887, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#888, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#889, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#890, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#891, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#892, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#893, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#894, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#895, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#896, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#897, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#898, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#899, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#900, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#901, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#902, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#903, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#904, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#905, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#906, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#907, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#908, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#909, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#910, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#911, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#912, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#913, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#914, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#915, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#916, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#917, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#918, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#919, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#920, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#921, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#922, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#923, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#924, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#925, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#926, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#927, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#928, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#929, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#930, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#931, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#932, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#933, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#934, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#935, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#936, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#937, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#938, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#939, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#940, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#941, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#942, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#943, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#944, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#945, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#946, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#947, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#948, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#949, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#950, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#951, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#952, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#953, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#954, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#955, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#956, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#957, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#958, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#959, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#960, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#961, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#962, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#963, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#964, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#965, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#966, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#967, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#968, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#969, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#970, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#971, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#972, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#973, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#974, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#975, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#976, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#977, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#978, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#979, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#980, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#981, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#982, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#983, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#984, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#985, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#986, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#987, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#988, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#989, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#990, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#991, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#992, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#993, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#994, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#995, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#996, intuit_risk.pmt_txn_fact.card_type->Column#997, intuit_risk.pmt_txn_fact.entry_method->Column#998, intuit_risk.pmt_txn_fact.mt_gateway->Column#999, intuit_risk.pmt_txn_fact.merchant_account_number->Column#1000	25.4 MB	N/A
    └─IndexReader_23	18368.93	4152	root	partition:p20260501,p20260601,pmax	time:23.7ms, open:72.9µs, close:14.3µs, loops:6, cop_task: {num: 7, max: 8.46ms, min: 1.42ms, avg: 4.29ms, p95: 8.46ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 18.7ms, tot_wait: 3.78ms, copr_cache: disabled, build_task_duration: 26.2µs, max_distsql_concurrency: 3}, fetch_resp_duration: 23.4ms, rpc_info:{Cop:{num_rpc:7, total_time:30ms}}	index:IndexRangeScan_22	316.7 KB	N/A
      └─IndexRangeScan_22	18368.93	4152	cop[tikv]	table:p, index:idx_pmt_merchant_runtime_cov(merchant_account_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 2.86ms, p80:10ms, p95:10ms, iters:24, tasks:7}, scan_detail: {total_process_keys: 4152, total_process_keys_size: 705989, total_keys: 4159, get_snapshot_time: 3.63ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.7ms, total_suspend_time: 15.2µs, total_wait_time: 3.78ms, total_kv_read_wall_time: 20ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
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
-- best_variant=optimized_default
-- explain_analyze_elapsed_ms=70.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:24.2ms, open:335.5µs, close:51.2µs, loops:2, RU:15.48, Concurrency:OFF	Column#47->Column#208, Column#48->Column#209, Column#49->Column#210, Column#50->Column#211, Column#51->Column#212, Column#51->Column#213, Column#52->Column#214, Column#51->Column#215, Column#53->Column#216, Column#51->Column#217, Column#54->Column#218, Column#51->Column#219, Column#55->Column#220, Column#55->Column#221, Column#56->Column#222, Column#55->Column#223, Column#57->Column#224, Column#55->Column#225, Column#58->Column#226, Column#55->Column#227, Column#59->Column#228, Column#59->Column#229, Column#60->Column#230, Column#59->Column#231, Column#61->Column#232, Column#59->Column#233, Column#62->Column#234, Column#59->Column#235, Column#63->Column#236, Column#63->Column#237, Column#64->Column#238, Column#63->Column#239, Column#65->Column#240, Column#63->Column#241, Column#66->Column#242, Column#63->Column#243, Column#67->Column#244, Column#67->Column#245, Column#68->Column#246, Column#67->Column#247, Column#69->Column#248, Column#67->Column#249, Column#70->Column#250, Column#67->Column#251, Column#71->Column#252, Column#71->Column#253, Column#72->Column#254, Column#71->Column#255, Column#73->Column#256, Column#71->Column#257, Column#74->Column#258, Column#71->Column#259, Column#75->Column#260, Column#75->Column#261, Column#76->Column#262, Column#75->Column#263, Column#77->Column#264, Column#75->Column#265, Column#78->Column#266, Column#75->Column#267, Column#79->Column#268, Column#79->Column#269, Column#80->Column#270, Column#79->Column#271, Column#81->Column#272, Column#79->Column#273, Column#82->Column#274, Column#79->Column#275, Column#83->Column#276, Column#83->Column#277, Column#84->Column#278, Column#83->Column#279, Column#85->Column#280, Column#83->Column#281, Column#86->Column#282, Column#83->Column#283, Column#87->Column#284, Column#87->Column#285, Column#88->Column#286, Column#87->Column#287, Column#89->Column#288, Column#87->Column#289, Column#90->Column#290, Column#87->Column#291, Column#91->Column#292, Column#91->Column#293, Column#92->Column#294, Column#91->Column#295, Column#93->Column#296, Column#91->Column#297, Column#94->Column#298, Column#91->Column#299, Column#95->Column#300, Column#95->Column#301, Column#96->Column#302, Column#95->Column#303, Column#97->Column#304, Column#95->Column#305, Column#98->Column#306, Column#95->Column#307, Column#99->Column#308, Column#99->Column#309, Column#100->Column#310, Column#99->Column#311, Column#101->Column#312, Column#99->Column#313, Column#102->Column#314, Column#99->Column#315, Column#103->Column#316, Column#103->Column#317, Column#104->Column#318, Column#103->Column#319, Column#105->Column#320, Column#103->Column#321, Column#106->Column#322, Column#103->Column#323, Column#107->Column#324, Column#107->Column#325, Column#108->Column#326, Column#107->Column#327, Column#109->Column#328, Column#107->Column#329, Column#110->Column#330, Column#107->Column#331, Column#111->Column#332, Column#111->Column#333, Column#112->Column#334, Column#111->Column#335, Column#113->Column#336, Column#111->Column#337, Column#114->Column#338, Column#111->Column#339, Column#115->Column#340, Column#115->Column#341, Column#116->Column#342, Column#115->Column#343, Column#117->Column#344, Column#115->Column#345, Column#118->Column#346, Column#115->Column#347, Column#119->Column#348, Column#119->Column#349, Column#120->Column#350, Column#119->Column#351, Column#121->Column#352, Column#119->Column#353, Column#122->Column#354, Column#119->Column#355, Column#123->Column#356, Column#123->Column#357, Column#124->Column#358, Column#123->Column#359, Column#125->Column#360, Column#123->Column#361, Column#126->Column#362, Column#123->Column#363, Column#127->Column#364, Column#127->Column#365, Column#128->Column#366, Column#127->Column#367, Column#129->Column#368, Column#127->Column#369, Column#130->Column#370, Column#127->Column#371, Column#131->Column#372, Column#131->Column#373, Column#132->Column#374, Column#131->Column#375, Column#133->Column#376, Column#131->Column#377, Column#134->Column#378, Column#131->Column#379, Column#135->Column#380, Column#135->Column#381, Column#136->Column#382, Column#135->Column#383, Column#137->Column#384, Column#135->Column#385, Column#138->Column#386, Column#135->Column#387, Column#139->Column#388, Column#139->Column#389, Column#140->Column#390, Column#139->Column#391, Column#141->Column#392, Column#139->Column#393, Column#142->Column#394, Column#139->Column#395, Column#143->Column#396, Column#143->Column#397, Column#144->Column#398, Column#143->Column#399, Column#145->Column#400, Column#143->Column#401, Column#146->Column#402, Column#143->Column#403, Column#147->Column#404, Column#147->Column#405, Column#148->Column#406, Column#147->Column#407, Column#149->Column#408, Column#147->Column#409, Column#150->Column#410, Column#147->Column#411, Column#151->Column#412, Column#151->Column#413, Column#152->Column#414, Column#151->Column#415, Column#153->Column#416, Column#151->Column#417, Column#154->Column#418, Column#151->Column#419, Column#155->Column#420, Column#155->Column#421, Column#156->Column#422, Column#155->Column#423, Column#157->Column#424, Column#155->Column#425, Column#158->Column#426, Column#155->Column#427, Column#159->Column#428, Column#159->Column#429, Column#160->Column#430, Column#159->Column#431, Column#161->Column#432, Column#159->Column#433, Column#162->Column#434, Column#159->Column#435, Column#163->Column#436, Column#163->Column#437, Column#164->Column#438, Column#163->Column#439, Column#165->Column#440, Column#163->Column#441, Column#166->Column#442, Column#163->Column#443, Column#167->Column#444, Column#167->Column#445, Column#168->Column#446, Column#167->Column#447, Column#169->Column#448, Column#167->Column#449, Column#170->Column#450, Column#167->Column#451, Column#171->Column#452, Column#171->Column#453, Column#172->Column#454, Column#171->Column#455, Column#173->Column#456, Column#171->Column#457, Column#174->Column#458, Column#171->Column#459, Column#175->Column#460, Column#175->Column#461, Column#176->Column#462, Column#175->Column#463, Column#177->Column#464, Column#175->Column#465, Column#178->Column#466, Column#175->Column#467, Column#179->Column#468, Column#179->Column#469, Column#180->Column#470, Column#179->Column#471, Column#181->Column#472, Column#179->Column#473, Column#182->Column#474, Column#179->Column#475, Column#183->Column#476, Column#183->Column#477, Column#184->Column#478, Column#183->Column#479, Column#185->Column#480, Column#185->Column#481, Column#186->Column#482, Column#185->Column#483, Column#187->Column#484, Column#187->Column#485, Column#188->Column#486, Column#187->Column#487, Column#189->Column#488, Column#189->Column#489, Column#190->Column#490, Column#189->Column#491, Column#191->Column#492, Column#191->Column#493, Column#192->Column#494, Column#191->Column#495, Column#193->Column#496, Column#193->Column#497, Column#194->Column#498, Column#193->Column#499, Column#195->Column#500, Column#195->Column#501, Column#196->Column#502, Column#195->Column#503, Column#197->Column#504, Column#197->Column#505, Column#198->Column#506, Column#197->Column#507, Column#199->Column#508, Column#199->Column#509, Column#200->Column#510, Column#199->Column#511, Column#201->Column#512, Column#201->Column#513, Column#202->Column#514, Column#201->Column#515, Column#203->Column#516, Column#203->Column#517, Column#204->Column#518, Column#203->Column#519, Column#205->Column#520, Column#206->Column#521, Column#207->Column#522	253.0 KB	N/A
└─Selection_9	0.80	1	root		time:23.9ms, open:279µs, close:49.2µs, loops:2	gt(Column#47, ?)	261.4 KB	N/A
  └─HashAgg_13	1.00	1	root		time:23.8ms, open:174.1µs, close:48.2µs, loops:3	funcs:count(?)->Column#47, funcs:sum(Column#839)->Column#48, funcs:min(Column#840)->Column#49, funcs:max(Column#841)->Column#50, funcs:sum(Column#842)->Column#51, funcs:sum(Column#843)->Column#52, funcs:min(Column#844)->Column#53, funcs:max(Column#845)->Column#54, funcs:sum(Column#846)->Column#55, funcs:sum(Column#847)->Column#56, funcs:min(Column#848)->Column#57, funcs:max(Column#849)->Column#58, funcs:sum(Column#850)->Column#59, funcs:sum(Column#851)->Column#60, funcs:min(Column#852)->Column#61, funcs:max(Column#853)->Column#62, funcs:sum(Column#854)->Column#63, funcs:sum(Column#855)->Column#64, funcs:min(Column#856)->Column#65, funcs:max(Column#857)->Column#66, funcs:sum(Column#858)->Column#67, funcs:sum(Column#859)->Column#68, funcs:min(Column#860)->Column#69, funcs:max(Column#861)->Column#70, funcs:sum(Column#862)->Column#71, funcs:sum(Column#863)->Column#72, funcs:min(Column#864)->Column#73, funcs:max(Column#865)->Column#74, funcs:sum(Column#866)->Column#75, funcs:sum(Column#867)->Column#76, funcs:min(Column#868)->Column#77, funcs:max(Column#869)->Column#78, funcs:sum(Column#870)->Column#79, funcs:sum(Column#871)->Column#80, funcs:min(Column#872)->Column#81, funcs:max(Column#873)->Column#82, funcs:sum(Column#874)->Column#83, funcs:sum(Column#875)->Column#84, funcs:min(Column#876)->Column#85, funcs:max(Column#877)->Column#86, funcs:sum(Column#878)->Column#87, funcs:sum(Column#879)->Column#88, funcs:min(Column#880)->Column#89, funcs:max(Column#881)->Column#90, funcs:sum(Column#882)->Column#91, funcs:sum(Column#883)->Column#92, funcs:min(Column#884)->Column#93, funcs:max(Column#885)->Column#94, funcs:sum(Column#886)->Column#95, funcs:sum(Column#887)->Column#96, funcs:min(Column#888)->Column#97, funcs:max(Column#889)->Column#98, funcs:sum(Column#890)->Column#99, funcs:sum(Column#891)->Column#100, funcs:min(Column#892)->Column#101, funcs:max(Column#893)->Column#102, funcs:sum(Column#894)->Column#103, funcs:sum(Column#895)->Column#104, funcs:min(Column#896)->Column#105, funcs:max(Column#897)->Column#106, funcs:sum(Column#898)->Column#107, funcs:sum(Column#899)->Column#108, funcs:min(Column#900)->Column#109, funcs:max(Column#901)->Column#110, funcs:sum(Column#902)->Column#111, funcs:sum(Column#903)->Column#112, funcs:min(Column#904)->Column#113, funcs:max(Column#905)->Column#114, funcs:sum(Column#906)->Column#115, funcs:sum(Column#907)->Column#116, funcs:min(Column#908)->Column#117, funcs:max(Column#909)->Column#118, funcs:sum(Column#910)->Column#119, funcs:sum(Column#911)->Column#120, funcs:min(Column#912)->Column#121, funcs:max(Column#913)->Column#122, funcs:sum(Column#914)->Column#123, funcs:sum(Column#915)->Column#124, funcs:min(Column#916)->Column#125, funcs:max(Column#917)->Column#126, funcs:sum(Column#918)->Column#127, funcs:sum(Column#919)->Column#128, funcs:min(Column#920)->Column#129, funcs:max(Column#921)->Column#130, funcs:sum(Column#922)->Column#131, funcs:sum(Column#923)->Column#132, funcs:min(Column#924)->Column#133, funcs:max(Column#925)->Column#134, funcs:sum(Column#926)->Column#135, funcs:sum(Column#927)->Column#136, funcs:min(Column#928)->Column#137, funcs:max(Column#929)->Column#138, funcs:sum(Column#930)->Column#139, funcs:sum(Column#931)->Column#140, funcs:min(Column#932)->Column#141, funcs:max(Column#933)->Column#142, funcs:sum(Column#934)->Column#143, funcs:sum(Column#935)->Column#144, funcs:min(Column#936)->Column#145, funcs:max(Column#937)->Column#146, funcs:sum(Column#938)->Column#147, funcs:sum(Column#939)->Column#148, funcs:min(Column#940)->Column#149, funcs:max(Column#941)->Column#150, funcs:sum(Column#942)->Column#151, funcs:sum(Column#943)->Column#152, funcs:min(Column#944)->Column#153, funcs:max(Column#945)->Column#154, funcs:sum(Column#946)->Column#155, funcs:sum(Column#947)->Column#156, funcs:min(Column#948)->Column#157, funcs:max(Column#949)->Column#158, funcs:sum(Column#950)->Column#159, funcs:sum(Column#951)->Column#160, funcs:min(Column#952)->Column#161, funcs:max(Column#953)->Column#162, funcs:sum(Column#954)->Column#163, funcs:sum(Column#955)->Column#164, funcs:min(Column#956)->Column#165, funcs:max(Column#957)->Column#166, funcs:sum(Column#958)->Column#167, funcs:sum(Column#959)->Column#168, funcs:min(Column#960)->Column#169, funcs:max(Column#961)->Column#170, funcs:sum(Column#962)->Column#171, funcs:sum(Column#963)->Column#172, funcs:min(Column#964)->Column#173, funcs:max(Column#965)->Column#174, funcs:sum(Column#966)->Column#175, funcs:sum(Column#967)->Column#176, funcs:min(Column#968)->Column#177, funcs:max(Column#969)->Column#178, funcs:sum(Column#970)->Column#179, funcs:sum(Column#971)->Column#180, funcs:min(Column#972)->Column#181, funcs:max(Column#973)->Column#182, funcs:sum(Column#974)->Column#183, funcs:sum(Column#975)->Column#184, funcs:sum(Column#976)->Column#185, funcs:sum(Column#977)->Column#186, funcs:sum(Column#978)->Column#187, funcs:sum(Column#979)->Column#188, funcs:sum(Column#980)->Column#189, funcs:sum(Column#981)->Column#190, funcs:sum(Column#982)->Column#191, funcs:sum(Column#983)->Column#192, funcs:sum(Column#984)->Column#193, funcs:sum(Column#985)->Column#194, funcs:sum(Column#986)->Column#195, funcs:sum(Column#987)->Column#196, funcs:sum(Column#988)->Column#197, funcs:sum(Column#989)->Column#198, funcs:sum(Column#990)->Column#199, funcs:sum(Column#991)->Column#200, funcs:sum(Column#992)->Column#201, funcs:sum(Column#993)->Column#202, funcs:sum(Column#994)->Column#203, funcs:sum(Column#995)->Column#204, funcs:count(distinct Column#996)->Column#205, funcs:count(distinct Column#997)->Column#206, funcs:count(distinct Column#998)->Column#207	6.23 MB	0 Bytes
    └─Projection_28	18368.93	4152	root		time:11.6ms, open:73.8µs, close:47.3µs, loops:6, Concurrency:5	intuit_risk.pmt_txn_fact.amount->Column#839, intuit_risk.pmt_txn_fact.amount->Column#840, intuit_risk.pmt_txn_fact.amount->Column#841, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#842, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#843, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#844, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#845, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#846, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#847, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#848, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#849, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#850, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#851, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#852, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#853, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#854, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#855, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#856, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#857, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#858, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#859, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#860, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#861, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#862, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#863, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#864, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#865, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#866, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#867, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#868, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#869, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#870, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#871, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#872, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#873, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#874, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#875, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#876, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#877, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#878, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#879, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#880, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#881, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#882, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#883, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#884, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#885, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#886, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#887, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#888, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#889, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#890, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#891, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#892, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#893, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#894, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#895, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#896, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#897, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#898, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#899, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#900, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#901, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#902, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#903, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#904, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#905, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#906, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#907, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#908, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#909, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#910, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#911, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#912, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#913, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#914, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#915, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#916, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#917, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#918, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#919, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#920, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#921, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#922, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#923, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#924, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#925, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#926, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#927, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#928, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#929, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#930, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#931, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#932, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#933, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#934, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#935, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#936, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#937, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#938, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#939, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#940, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#941, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#942, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#943, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#944, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#945, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#946, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#947, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#948, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#949, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#950, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#951, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#952, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#953, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#954, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#955, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#956, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#957, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#958, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#959, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#960, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#961, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#962, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#963, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#964, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#965, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#966, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#967, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#968, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#969, cast(case(eq(intuit_risk.pmt_txn_fact.card_type, ?), ?, ?), decimal(20,0) BINARY)->Column#970, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#971, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#972, case(eq(intuit_risk.pmt_txn_fact.card_type, ?), intuit_risk.pmt_txn_fact.amount)->Column#973, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#974, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#975, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#976, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#977, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#978, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#979, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#980, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#981, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#982, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#983, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#984, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#985, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#986, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#987, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#988, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#989, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#990, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#991, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#992, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#993, cast(case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), ?, ?), decimal(20,0) BINARY)->Column#994, case(and(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), eq(intuit_risk.pmt_txn_fact.entry_method, ?)), intuit_risk.pmt_txn_fact.amount)->Column#995, intuit_risk.pmt_txn_fact.card_type->Column#996, intuit_risk.pmt_txn_fact.entry_method->Column#997, intuit_risk.pmt_txn_fact.mt_gateway->Column#998	25.4 MB	N/A
      └─IndexReader_21	18368.93	4152	root	partition:p20260501,p20260601,pmax	time:8.84ms, open:72.6µs, close:11.6µs, loops:6, cop_task: {num: 7, max: 3.68ms, min: 420µs, avg: 1.58ms, p95: 3.68ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 4.15ms, tot_wait: 273µs, copr_cache: disabled, build_task_duration: 23.5µs, max_distsql_concurrency: 3}, fetch_resp_duration: 8.52ms, rpc_info:{Cop:{num_rpc:7, total_time:11ms}}	index:IndexRangeScan_20	316.7 KB	N/A
        └─IndexRangeScan_20	18368.93	4152	cop[tikv]	table:p, index:idx_pmt_merchant_runtime_cov(merchant_account_number, event_date, amount, mt_gateway, card_type, entry_method, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:24, tasks:7}, scan_detail: {total_process_keys: 4152, total_process_keys_size: 705989, total_keys: 4159, get_snapshot_time: 137.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.15ms, total_suspend_time: 5.39µs, total_wait_time: 273µs}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 10. group_a_bundle_014

- Filter/window: `p.check_bank_routing_number = %s` / `90d`
- Chosen event: `INV0019958147` kind=`hot_check_bank_routing_number` error=`None`
- Optimization: SQL rewrite: pre-aggregate low-cardinality payment dimensions, then pivot CASE metrics from the compact rollup; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 323.3 ms | ok |
| `optimized_default` | `{}` | 107.3 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 107.3 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 110.5 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 106.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 106.6 ms | ok |

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
-- explain_analyze_elapsed_ms=323.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	42.42	1	root		time:287.9ms, open:171.8µs, close:13µs, loops:2, RU:1043.26, Concurrency:OFF	Column#47, Column#48, Column#49, Column#50, Column#51, Column#51, Column#52, Column#51, Column#53, Column#51, Column#54, Column#51, Column#55, Column#55, Column#56, Column#55, Column#57, Column#55, Column#58, Column#55, Column#59, Column#59, Column#60, Column#59, Column#61, Column#59, Column#62, Column#59, Column#63, Column#63, Column#64, Column#63, Column#65, Column#63, Column#66, Column#63, Column#67, Column#67, Column#68, Column#67, Column#69, Column#67, Column#70, Column#67, Column#71, Column#71, Column#72, Column#71, Column#73, Column#71, Column#74, Column#71, Column#75, Column#75, Column#76, Column#75, Column#77, Column#75, Column#78, Column#75	47.7 KB	N/A
└─HashAgg_27	42.42	1	root		time:287.8ms, open:168.8µs, close:11.7µs, loops:2, partial_worker:{wall_time:287.597972ms, concurrency:4, task_num:1, tot_wait:287.538734ms, tot_exec:20.267µs, tot_time:1.150281406s, max:287.5749ms, p95:287.5749ms}, final_worker:{wall_time:287.611384ms, concurrency:4, task_num:4, tot_wait:4.466µs, tot_exec:152ns, tot_time:1.150369958s, max:287.59513ms, p95:287.59513ms}	group by:intuit_risk.pmt_txn_fact.check_bank_routing_number, funcs:count(Column#82)->Column#47, funcs:sum(Column#83)->Column#48, funcs:min(Column#84)->Column#49, funcs:max(Column#85)->Column#50, funcs:sum(Column#86)->Column#51, funcs:sum(Column#87)->Column#52, funcs:min(Column#88)->Column#53, funcs:max(Column#89)->Column#54, funcs:sum(Column#90)->Column#55, funcs:sum(Column#91)->Column#56, funcs:min(Column#92)->Column#57, funcs:max(Column#93)->Column#58, funcs:sum(Column#94)->Column#59, funcs:sum(Column#95)->Column#60, funcs:min(Column#96)->Column#61, funcs:max(Column#97)->Column#62, funcs:sum(Column#98)->Column#63, funcs:sum(Column#99)->Column#64, funcs:min(Column#100)->Column#65, funcs:max(Column#101)->Column#66, funcs:sum(Column#102)->Column#67, funcs:sum(Column#103)->Column#68, funcs:min(Column#104)->Column#69, funcs:max(Column#105)->Column#70, funcs:sum(Column#106)->Column#71, funcs:sum(Column#107)->Column#72, funcs:min(Column#108)->Column#73, funcs:max(Column#109)->Column#74, funcs:sum(Column#110)->Column#75, funcs:sum(Column#111)->Column#76, funcs:min(Column#112)->Column#77, funcs:max(Column#113)->Column#78	411.9 KB	0 Bytes
  └─IndexReader_28	42.42	4	root	partition:p20260201,p20260301,p20260401,p20260501,p20260601,pmax	time:287.7ms, open:110.5µs, close:8.38µs, loops:2, cop_task: {num: 6, max: 287.5ms, min: 812.7µs, avg: 134.2ms, p95: 287.5ms, max_proc_keys: 122612, p95_proc_keys: 122612, tot_proc: 793.6ms, tot_wait: 4.16ms, copr_cache: disabled, build_task_duration: 38.9µs, max_distsql_concurrency: 6}, fetch_resp_duration: 287.4ms, rpc_info:{Cop:{num_rpc:6, total_time:805ms}}	index:HashAgg_7	3.38 KB	N/A
    └─HashAgg_7	42.42	4	cop[tikv]		tikv_task:{proc max:280ms, min:0s, avg: 130ms, p80:240ms, p95:280ms, iters:336, tasks:6}, scan_detail: {total_process_keys: 340239, total_process_keys_size: 50848432, total_keys: 340245, get_snapshot_time: 4.02ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 793.6ms, total_suspend_time: 665.3µs, total_wait_time: 4.16ms, total_kv_read_wall_time: 150ms}	group by:intuit_risk.pmt_txn_fact.check_bank_routing_number, funcs:count(?)->Column#82, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#83, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#84, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#85, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#86, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#87, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#88, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#89, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#90, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#91, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#92, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#93, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#94, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#95, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#96, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#97, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#98, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#99, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#100, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#101, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#102, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#103, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#104, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#105, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#106, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#107, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#108, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#109, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), ?, ?))->Column#110, funcs:sum(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#111, funcs:min(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#112, funcs:max(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), intuit_risk.pmt_txn_fact.amount))->Column#113	N/A	N/A
      └─IndexRangeScan_25	479923.47	340239	cop[tikv]	table:p, index:idx_test(check_bank_routing_number, event_date, mt_gateway, amount)	tikv_task:{proc max:50ms, min:0s, avg: 25ms, p80:50ms, p95:50ms, iters:336, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

#### Optimized SQL

```sql
SELECT
  SUM(b.row_count) AS `metric__a_0045`,
  SUM(b.amount_sum) AS `metric__a_0046`,
  MIN(b.amount_min) AS `metric__a_0047`,
  MAX(b.amount_max) AS `metric__a_0048`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `metric__a_1005`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1005`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_sum END) AS `metric__a_1006`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1006`,
  MIN(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_min END) AS `metric__a_1007`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1007`,
  MAX(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_max END) AS `metric__a_1008`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1008`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `metric__a_1017`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1017`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_sum END) AS `metric__a_1018`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1018`,
  MIN(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_min END) AS `metric__a_1019`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1019`,
  MAX(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_max END) AS `metric__a_1020`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1020`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `metric__a_1029`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1029`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_sum END) AS `metric__a_1030`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1030`,
  MIN(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_min END) AS `metric__a_1031`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1031`,
  MAX(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_max END) AS `metric__a_1032`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1032`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `metric__a_1041`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1041`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_sum END) AS `metric__a_1042`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1042`,
  MIN(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_min END) AS `metric__a_1043`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1043`,
  MAX(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_max END) AS `metric__a_1044`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1044`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `metric__a_1053`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1053`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_sum END) AS `metric__a_1054`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1054`,
  MIN(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_min END) AS `metric__a_1055`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1055`,
  MAX(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_max END) AS `metric__a_1056`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1056`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `metric__a_1065`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1065`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_sum END) AS `metric__a_1066`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1066`,
  MIN(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_min END) AS `metric__a_1067`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1067`,
  MAX(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_max END) AS `metric__a_1068`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1068`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `metric__a_1077`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1077`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_sum END) AS `metric__a_1078`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1078`,
  MIN(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_min END) AS `metric__a_1079`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1079`,
  MAX(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_max END) AS `metric__a_1080`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1080`
FROM (
  SELECT p.mt_gateway, COUNT(*) AS row_count, SUM(p.amount) AS amount_sum, MIN(p.amount) AS amount_min, MAX(p.amount) AS amount_max
  FROM pmt_txn_fact p
WHERE p.check_bank_routing_number = %s AND p.event_date >= 1768101078317
  GROUP BY p.mt_gateway
) b
HAVING SUM(b.row_count) > 0;
```

#### Optimized Params

```json
[
  "322271627"
]
```

#### Optimized EXPLAIN ANALYZE

```text
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=106.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_9	0.80	1	root		time:72.5ms, open:135.6µs, close:13.8µs, loops:2, RU:845.83, Concurrency:OFF	Column#51->Column#83, Column#52->Column#84, Column#53->Column#85, Column#54->Column#86, Column#55->Column#87, Column#55->Column#88, Column#56->Column#89, Column#55->Column#90, Column#57->Column#91, Column#55->Column#92, Column#58->Column#93, Column#55->Column#94, Column#59->Column#95, Column#59->Column#96, Column#60->Column#97, Column#59->Column#98, Column#61->Column#99, Column#59->Column#100, Column#62->Column#101, Column#59->Column#102, Column#63->Column#103, Column#63->Column#104, Column#64->Column#105, Column#63->Column#106, Column#65->Column#107, Column#63->Column#108, Column#66->Column#109, Column#63->Column#110, Column#67->Column#111, Column#67->Column#112, Column#68->Column#113, Column#67->Column#114, Column#69->Column#115, Column#67->Column#116, Column#70->Column#117, Column#67->Column#118, Column#71->Column#119, Column#71->Column#120, Column#72->Column#121, Column#71->Column#122, Column#73->Column#123, Column#71->Column#124, Column#74->Column#125, Column#71->Column#126, Column#75->Column#127, Column#75->Column#128, Column#76->Column#129, Column#75->Column#130, Column#77->Column#131, Column#75->Column#132, Column#78->Column#133, Column#75->Column#134, Column#79->Column#135, Column#79->Column#136, Column#80->Column#137, Column#79->Column#138, Column#81->Column#139, Column#79->Column#140, Column#82->Column#141, Column#79->Column#142	69.7 KB	N/A
└─Selection_11	0.80	1	root		time:72.4ms, open:133.8µs, close:12.4µs, loops:2	gt(Column#51, ?)	102.2 KB	N/A
  └─StreamAgg_18	1.00	1	root		time:72.4ms, open:130.7µs, close:11.9µs, loops:3	funcs:sum(Column#154)->Column#51, funcs:sum(Column#155)->Column#52, funcs:min(Column#156)->Column#53, funcs:max(Column#157)->Column#54, funcs:sum(Column#158)->Column#55, funcs:sum(Column#159)->Column#56, funcs:min(Column#160)->Column#57, funcs:max(Column#161)->Column#58, funcs:sum(Column#162)->Column#59, funcs:sum(Column#163)->Column#60, funcs:min(Column#164)->Column#61, funcs:max(Column#165)->Column#62, funcs:sum(Column#166)->Column#63, funcs:sum(Column#167)->Column#64, funcs:min(Column#168)->Column#65, funcs:max(Column#169)->Column#66, funcs:sum(Column#170)->Column#67, funcs:sum(Column#171)->Column#68, funcs:min(Column#172)->Column#69, funcs:max(Column#173)->Column#70, funcs:sum(Column#174)->Column#71, funcs:sum(Column#175)->Column#72, funcs:min(Column#176)->Column#73, funcs:max(Column#177)->Column#74, funcs:sum(Column#178)->Column#75, funcs:sum(Column#179)->Column#76, funcs:min(Column#180)->Column#77, funcs:max(Column#181)->Column#78, funcs:sum(Column#182)->Column#79, funcs:sum(Column#183)->Column#80, funcs:min(Column#184)->Column#81, funcs:max(Column#185)->Column#82	90.6 KB	N/A
    └─Projection_37	1.00	10	root		time:72.4ms, open:125.6µs, close:11.4µs, loops:4, Concurrency:OFF	cast(Column#47, decimal(20,0) BINARY)->Column#154, Column#48->Column#155, Column#49->Column#156, Column#50->Column#157, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#158, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#159, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#160, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#161, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#162, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#163, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#164, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#165, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#166, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#167, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#168, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#169, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#170, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#171, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#172, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#173, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#174, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#175, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#176, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#177, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#178, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#179, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#180, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#181, cast(case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#47, ?), decimal(20,0) BINARY)->Column#182, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#48)->Column#183, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#49)->Column#184, case(eq(intuit_risk.pmt_txn_fact.mt_gateway, ?), Column#50)->Column#185	19.2 KB	N/A
      └─HashAgg_27	1.00	10	root		time:72.2ms, open:123.6µs, close:10.6µs, loops:4, partial_worker:{wall_time:72.025889ms, concurrency:4, task_num:1, tot_wait:71.970188ms, tot_exec:25.868µs, tot_time:288.018958ms, max:72.005556ms, p95:72.005556ms}, final_worker:{wall_time:72.03724ms, concurrency:4, task_num:4, tot_wait:32.482µs, tot_exec:148ns, tot_time:288.101448ms, max:72.028387ms, p95:72.028387ms}	group by:intuit_risk.pmt_txn_fact.mt_gateway, funcs:count(Column#146)->Column#47, funcs:sum(Column#147)->Column#48, funcs:min(Column#148)->Column#49, funcs:max(Column#149)->Column#50, funcs:firstrow(intuit_risk.pmt_txn_fact.mt_gateway)->intuit_risk.pmt_txn_fact.mt_gateway	108.3 KB	0 Bytes
        └─IndexReader_28	1.00	40	root	partition:p20260201,p20260301,p20260401,p20260501,p20260601,pmax	time:72.1ms, open:96.3µs, close:7.92µs, loops:2, cop_task: {num: 6, max: 71.9ms, min: 432.5µs, avg: 34.3ms, p95: 71.9ms, max_proc_keys: 122612, p95_proc_keys: 122612, tot_proc: 201.3ms, tot_wait: 252.7µs, copr_cache: disabled, build_task_duration: 39.1µs, max_distsql_concurrency: 6}, fetch_resp_duration: 71.9ms, rpc_info:{Cop:{num_rpc:6, total_time:205.8ms}}	index:HashAgg_19	3.35 KB	N/A
          └─HashAgg_19	1.00	40	cop[tikv]		tikv_task:{proc max:80ms, min:0s, avg: 38.3ms, p80:70ms, p95:80ms, iters:336, tasks:6}, scan_detail: {total_process_keys: 340239, total_process_keys_size: 50848432, total_keys: 340245, get_snapshot_time: 119.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 201.3ms, total_suspend_time: 410.3µs, total_wait_time: 252.7µs, total_kv_read_wall_time: 150ms}	group by:intuit_risk.pmt_txn_fact.mt_gateway, funcs:count(?)->Column#146, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#147, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#148, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#149	N/A	N/A
            └─IndexRangeScan_25	479923.47	340239	cop[tikv]	table:p, index:idx_test(check_bank_routing_number, event_date, mt_gateway, amount)	tikv_task:{proc max:50ms, min:0s, avg: 25ms, p80:50ms, p95:50ms, iters:336, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### 11. group_b_bundle_008

- Filter/window: `d.true_ip = %s` / `7d`
- Chosen event: `INV0042672604` kind=`normal` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 47.4 ms | ok |
| `optimized_default` | `{}` | 36.3 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 36.6 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 39.4 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 41.6 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 39.6 ms | ok |

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
-- explain_analyze_elapsed_ms=47.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	1.00	1	root		time:12.5ms, open:101.2µs, close:13.8µs, loops:2, RU:6.18, Concurrency:OFF	Column#60, Column#61, Column#61, Column#62, Column#62, Column#63, Column#63, Column#64, Column#64, Column#65, Column#65, Column#66, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, Column#73, Column#75, Column#73, Column#76, Column#77, Column#78, Column#77, Column#79, Column#77, Column#80, Column#81, Column#82, Column#81, Column#83, Column#81, Column#84, Column#85, Column#86, Column#85, Column#87, Column#85, Column#88, Column#89, Column#90, Column#89, Column#91, Column#89	132.7 KB	N/A
└─HashAgg_9	1.00	1	root		time:12.5ms, open:98µs, close:12.1µs, loops:2	group by:Column#223, funcs:count(?)->Column#60, funcs:sum(Column#192)->Column#61, funcs:sum(Column#193)->Column#62, funcs:sum(Column#194)->Column#63, funcs:sum(Column#195)->Column#64, funcs:sum(Column#196)->Column#65, funcs:sum(Column#197)->Column#66, funcs:count(distinct Column#198)->Column#67, funcs:count(distinct Column#199)->Column#68, funcs:count(distinct Column#200)->Column#69, funcs:count(distinct Column#201)->Column#70, funcs:count(distinct Column#202)->Column#71, funcs:min(Column#203)->Column#72, funcs:sum(Column#204)->Column#73, funcs:max(Column#205)->Column#74, funcs:avg(Column#206)->Column#75, funcs:min(Column#207)->Column#76, funcs:sum(Column#208)->Column#77, funcs:max(Column#209)->Column#78, funcs:avg(Column#210)->Column#79, funcs:min(Column#211)->Column#80, funcs:sum(Column#212)->Column#81, funcs:max(Column#213)->Column#82, funcs:avg(Column#214)->Column#83, funcs:min(Column#215)->Column#84, funcs:sum(Column#216)->Column#85, funcs:max(Column#217)->Column#86, funcs:avg(Column#218)->Column#87, funcs:min(Column#219)->Column#88, funcs:sum(Column#220)->Column#89, funcs:max(Column#221)->Column#90, funcs:avg(Column#222)->Column#91	193.6 KB	0 Bytes
  └─Projection_29	367.45	135	root		time:12.2ms, open:89.3µs, close:11.5µs, loops:2, Concurrency:OFF	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#192, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#193, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#194, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#196, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#197, intuit_risk.deviceprofile_fact.exact_id->Column#198, intuit_risk.deviceprofile_fact.smart_id->Column#199, intuit_risk.deviceprofile_fact.input_ip->Column#200, intuit_risk.deviceprofile_fact.proxy_ip->Column#201, intuit_risk.deviceprofile_fact.agent_type->Column#202, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#203, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#204, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#205, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#207, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#208, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#209, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#210, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#212, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#213, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#214, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#215, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#217, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#222, intuit_risk.deviceprofile_fact.true_ip->Column#223	73.5 KB	N/A
    └─IndexReader_21	367.45	135	root	partition:p20260401,p20260501,p20260601,pmax	time:11.6ms, open:82.7µs, close:10.5µs, loops:2, cop_task: {num: 4, max: 11.5ms, min: 961.3µs, avg: 4.54ms, p95: 11.5ms, max_proc_keys: 116, p95_proc_keys: 116, tot_proc: 10.6ms, tot_wait: 4.32ms, copr_cache: disabled, build_task_duration: 28µs, max_distsql_concurrency: 4}, fetch_resp_duration: 11.5ms, rpc_info:{Cop:{num_rpc:4, total_time:18.1ms}}	index:IndexRangeScan_20	25.4 KB	N/A
      └─IndexRangeScan_20	367.45	135	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:6, tasks:4}, scan_detail: {total_process_keys: 135, total_process_keys_size: 49941, total_keys: 139, get_snapshot_time: 4.23ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 10.6ms, total_suspend_time: 12.4µs, total_wait_time: 4.32ms, total_kv_read_wall_time: 10ms}	range:(? ?,? +inf], keep order:false	N/A	N/A
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
-- best_variant=optimized_default
-- explain_analyze_elapsed_ms=36.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:2.3ms, open:108.2µs, close:11.7µs, loops:2, RU:2.84, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	175.3 KB	N/A
└─Selection_9	0.80	1	root		time:2.27ms, open:105.4µs, close:10.1µs, loops:2	gt(Column#60, ?)	159.3 KB	N/A
  └─HashAgg_13	1.00	1	root		time:2.26ms, open:102.1µs, close:9.53µs, loops:3	funcs:count(?)->Column#60, funcs:sum(Column#208)->Column#61, funcs:sum(Column#209)->Column#62, funcs:sum(Column#210)->Column#63, funcs:sum(Column#211)->Column#64, funcs:sum(Column#212)->Column#65, funcs:sum(Column#213)->Column#66, funcs:count(distinct Column#214)->Column#67, funcs:count(distinct Column#215)->Column#68, funcs:count(distinct Column#216)->Column#69, funcs:count(distinct Column#217)->Column#70, funcs:count(distinct Column#218)->Column#71, funcs:min(Column#219)->Column#72, funcs:sum(Column#220)->Column#73, funcs:max(Column#221)->Column#74, funcs:avg(Column#222)->Column#75, funcs:min(Column#223)->Column#76, funcs:sum(Column#224)->Column#77, funcs:max(Column#225)->Column#78, funcs:avg(Column#226)->Column#79, funcs:min(Column#227)->Column#80, funcs:sum(Column#228)->Column#81, funcs:max(Column#229)->Column#82, funcs:avg(Column#230)->Column#83, funcs:min(Column#231)->Column#84, funcs:sum(Column#232)->Column#85, funcs:max(Column#233)->Column#86, funcs:avg(Column#234)->Column#87, funcs:min(Column#235)->Column#88, funcs:sum(Column#236)->Column#89, funcs:max(Column#237)->Column#90, funcs:avg(Column#238)->Column#91	191.4 KB	0 Bytes
    └─Projection_28	367.45	135	root		time:1.98ms, open:90.9µs, close:8.87µs, loops:2, Concurrency:OFF	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#208, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#209, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#210, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#211, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#212, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#213, intuit_risk.deviceprofile_fact.exact_id->Column#214, intuit_risk.deviceprofile_fact.smart_id->Column#215, intuit_risk.deviceprofile_fact.input_ip->Column#216, intuit_risk.deviceprofile_fact.proxy_ip->Column#217, intuit_risk.deviceprofile_fact.agent_type->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#222, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#223, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#224, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#225, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#226, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#230, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#231, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#232, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#233, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#234, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#235, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#236, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#237, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#238	78.1 KB	N/A
      └─IndexReader_21	367.45	135	root	partition:p20260401,p20260501,p20260601,pmax	time:1.49ms, open:86.2µs, close:7.99µs, loops:2, cop_task: {num: 4, max: 1.36ms, min: 551.6µs, avg: 956.9µs, p95: 1.36ms, max_proc_keys: 116, p95_proc_keys: 116, tot_proc: 548.5µs, tot_wait: 193.1µs, copr_cache: disabled, build_task_duration: 30.6µs, max_distsql_concurrency: 4}, fetch_resp_duration: 1.35ms, rpc_info:{Cop:{num_rpc:4, total_time:3.77ms}}	index:IndexRangeScan_20	25.3 KB	N/A
        └─IndexRangeScan_20	367.45	135	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:6, tasks:4}, scan_detail: {total_process_keys: 135, total_process_keys_size: 49941, total_keys: 139, get_snapshot_time: 94.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 548.5µs, total_wait_time: 193.1µs}	range:(? ?,? +inf], keep order:false	N/A	N/A
```

### 12. group_c_bundle_011

- Filter/window: `d.true_ip = %s` / `7d`
- Chosen event: `INV0009827520` kind=`normal` error=`None`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 901.7 ms | ok |
| `optimized_default` | `{}` | 337.3 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 202.2 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 144.7 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 119.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 105.4 ms | ok |

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
-- explain_analyze_elapsed_ms=901.7
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_13	40.17	1	root		time:868.9ms, open:93.4µs, close:29.1µs, loops:2, RU:692.25	group by:intuit_risk.deviceprofile_fact.true_ip, funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	50.9 KB	0 Bytes
└─Projection_21	115880.01	324	root		time:868.7ms, open:86.1µs, close:28.3µs, loops:5, Concurrency:5	intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.deviceprofile_fact.true_ip	89.6 KB	N/A
  └─IndexHashJoin_30	115880.01	324	root		time:868.7ms, open:85µs, close:10.1µs, loops:5, inner:{total:3.2s, concurrency:5, task:4, construct:11.8ms, fetch:3.19s, build:2.33ms, join:518.6µs}	inner join, inner:IndexReader_48, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	3.97 MB	N/A
    ├─IndexReader_45(Build)	74097.06	17870	root	partition:p20260401,p20260501,p20260601,pmax	time:48.7ms, open:83.7µs, close:6.37µs, loops:20, cop_task: {num: 13, max: 19.2ms, min: 570.5µs, avg: 4.5ms, p95: 19.2ms, max_proc_keys: 12951, p95_proc_keys: 12951, tot_proc: 46.8ms, tot_wait: 1.77ms, copr_cache: disabled, build_task_duration: 30.8µs, max_distsql_concurrency: 4}, fetch_resp_duration: 48.1ms, rpc_info:{Cop:{num_rpc:13, total_time:58.4ms}}	index:Selection_44	677.0 KB	N/A
    │ └─Selection_44	74097.06	17870	cop[tikv]		tikv_task:{proc max:20ms, min:0s, avg: 3.08ms, p80:10ms, p95:20ms, iters:75, tasks:13}, scan_detail: {total_process_keys: 31026, total_process_keys_size: 10980601, total_keys: 31039, get_snapshot_time: 1.47ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 46.8ms, total_suspend_time: 130.9µs, total_wait_time: 1.77ms, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_43	109394.56	31026	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:20ms, min:0s, avg: 3.08ms, p80:10ms, p95:20ms, iters:75, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_48(Probe)	115880.01	324	root	partition:p20260401,p20260501,p20260601,pmax	total_time:3.18s, total_open:26.8ms, total_close:40.9µs, loops:8, cop_task: {num: 44, max: 798.6ms, min: 2.43ms, avg: 103.8ms, p95: 795.3ms, max_proc_keys: 145, p95_proc_keys: 51, tot_proc: 1.44s, tot_wait: 5.97ms, copr_cache: disabled, build_task_duration: 5.02ms, max_distsql_concurrency: 11}, fetch_resp_duration: 3.15s, rpc_info:{Cop:{num_rpc:44, total_time:4.57s}}	index:Selection_47	9.43 KB	N/A
      └─Selection_47	115880.01	324	cop[tikv]		tikv_task:{proc max:350ms, min:0s, avg: 33.4ms, p80:40ms, p95:140ms, iters:49, tasks:44}, scan_detail: {total_process_keys: 324, total_process_keys_size: 55034, total_keys: 4766, get_snapshot_time: 6.29ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.44s, total_suspend_time: 80.8µs, total_wait_time: 5.97ms, total_kv_read_wall_time: 1.29s}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_46	157025.02	324	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:350ms, min:0s, avg: 33.4ms, p80:40ms, p95:140ms, iters:49, tasks:44}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
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
-- best_variant=optimized_distinct_pushdown_hashagg_16_8
-- explain_analyze_elapsed_ms=105.4
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Selection_13	0.80	1	root		time:72.2ms, open:105.9µs, close:7.22µs, loops:2, RU:226.62	gt(Column#106, ?)	27.4 KB	N/A
└─HashAgg_17	1.00	1	root		time:72.2ms, open:103.4µs, close:6.61µs, loops:3	funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	46.5 KB	0 Bytes
  └─IndexHashJoin_28	115880.01	324	root		time:72ms, open:95.6µs, close:5.85µs, loops:5, inner:{total:98.1ms, concurrency:5, task:4, construct:12.2ms, fetch:85.5ms, build:2.36ms, join:444.3µs}	inner join, inner:IndexReader_46, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	3.55 MB	N/A
    ├─IndexReader_43(Build)	74097.06	17870	root	partition:p20260401,p20260501,p20260601,pmax	time:27.3ms, open:94.4µs, close:3.67µs, loops:20, cop_task: {num: 13, max: 11.4ms, min: 606.6µs, avg: 2.55ms, p95: 11.4ms, max_proc_keys: 12951, p95_proc_keys: 12951, tot_proc: 25.6ms, tot_wait: 436.5µs, copr_cache: disabled, build_task_duration: 36.4µs, max_distsql_concurrency: 4}, fetch_resp_duration: 26.7ms, rpc_info:{Cop:{num_rpc:13, total_time:33ms}}	index:Selection_42	677.0 KB	N/A
    │ └─Selection_42	74097.06	17870	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.54ms, p80:0s, p95:10ms, iters:75, tasks:13}, scan_detail: {total_process_keys: 31026, total_process_keys_size: 10980601, total_keys: 31039, get_snapshot_time: 179.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 25.6ms, total_suspend_time: 66.7µs, total_wait_time: 436.5µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_41	109394.56	31026	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.54ms, p80:0s, p95:10ms, iters:75, tasks:13}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_46(Probe)	115880.01	324	root	partition:p20260401,p20260501,p20260601,pmax	total_time:79.4ms, total_open:30.6ms, total_close:35.2µs, loops:8, cop_task: {num: 44, max: 21.3ms, min: 700µs, avg: 3.58ms, p95: 10.3ms, max_proc_keys: 145, p95_proc_keys: 51, tot_proc: 65.6ms, tot_wait: 1.33ms, copr_cache: disabled, build_task_duration: 7.1ms, max_distsql_concurrency: 11}, fetch_resp_duration: 47.6ms, rpc_info:{Cop:{num_rpc:44, total_time:156.3ms}}	index:Selection_45	12.9 KB	N/A
      └─Selection_45	115880.01	324	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.82ms, p80:0s, p95:10ms, iters:49, tasks:44}, scan_detail: {total_process_keys: 324, total_process_keys_size: 104833, total_keys: 9828, get_snapshot_time: 522.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 65.6ms, total_suspend_time: 111.9µs, total_wait_time: 1.33ms, total_kv_read_wall_time: 80ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_44	157025.02	324	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1.82ms, p80:0s, p95:10ms, iters:49, tasks:44}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### 13. group_c_bundle_014

- Filter/window: `p.merchant_account_number = %s` / `7d`
- Chosen event: `INV0037793946` kind=`hot_merchant_account_number` error=`(1105, 'context canceled')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_32_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 159.2 ms | ok |
| `optimized_default` | `{}` | 123.9 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 118.4 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 118.3 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 118.5 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 122.6 ms | ok |

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
-- explain_analyze_elapsed_ms=159.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_8	66.18	1	root		time:87.6ms, open:184.7µs, close:36.4µs, loops:2, RU:113.58, Concurrency:OFF	Column#106, Column#107, Column#108, Column#109, Column#110, Column#111, Column#112, Column#113, Column#114, Column#115, Column#114, Column#116, Column#114, Column#117, Column#118, Column#119, Column#118, Column#120, Column#118, Column#121, Column#122, Column#123, Column#122, Column#124, Column#122, Column#125, Column#126, Column#127, Column#126, Column#128, Column#126, Column#129, Column#130, Column#131, Column#130, Column#132, Column#133, Column#134, Column#133, Column#135, Column#136, Column#137, Column#136, Column#138, Column#139, Column#140, Column#139, Column#141, Column#142, Column#143, Column#142, Column#144, Column#145, Column#146, Column#145, Column#147, Column#148, Column#149, Column#148, Column#150, Column#151, Column#152, Column#151, Column#153, Column#154, Column#155, Column#154, Column#156, Column#157, Column#158, Column#157, Column#159, Column#160, Column#161, Column#160, Column#162, Column#163, Column#164, Column#163	313.2 KB	N/A
└─HashAgg_12	66.18	1	root		time:87.5ms, open:117.5µs, close:34.7µs, loops:2	group by:Column#242, funcs:count(distinct Column#183)->Column#106, funcs:count(distinct Column#184)->Column#107, funcs:count(distinct Column#185)->Column#108, funcs:count(distinct Column#186)->Column#109, funcs:count(distinct Column#187)->Column#110, funcs:count(distinct Column#188)->Column#111, funcs:count(distinct Column#189)->Column#112, funcs:count(distinct Column#190)->Column#113, funcs:sum(Column#191)->Column#114, funcs:count(distinct Column#192)->Column#115, funcs:count(distinct Column#193)->Column#116, funcs:count(distinct Column#194)->Column#117, funcs:sum(Column#195)->Column#118, funcs:count(distinct Column#196)->Column#119, funcs:count(distinct Column#197)->Column#120, funcs:count(distinct Column#198)->Column#121, funcs:sum(Column#199)->Column#122, funcs:count(distinct Column#200)->Column#123, funcs:count(distinct Column#201)->Column#124, funcs:count(distinct Column#202)->Column#125, funcs:sum(Column#203)->Column#126, funcs:count(distinct Column#204)->Column#127, funcs:count(distinct Column#205)->Column#128, funcs:min(Column#206)->Column#129, funcs:sum(Column#207)->Column#130, funcs:max(Column#208)->Column#131, funcs:min(Column#209)->Column#132, funcs:sum(Column#210)->Column#133, funcs:max(Column#211)->Column#134, funcs:min(Column#212)->Column#135, funcs:sum(Column#213)->Column#136, funcs:max(Column#214)->Column#137, funcs:min(Column#215)->Column#138, funcs:sum(Column#216)->Column#139, funcs:max(Column#217)->Column#140, funcs:min(Column#218)->Column#141, funcs:sum(Column#219)->Column#142, funcs:max(Column#220)->Column#143, funcs:min(Column#221)->Column#144, funcs:sum(Column#222)->Column#145, funcs:max(Column#223)->Column#146, funcs:min(Column#224)->Column#147, funcs:sum(Column#225)->Column#148, funcs:max(Column#226)->Column#149, funcs:min(Column#227)->Column#150, funcs:sum(Column#228)->Column#151, funcs:max(Column#229)->Column#152, funcs:min(Column#230)->Column#153, funcs:sum(Column#231)->Column#154, funcs:max(Column#232)->Column#155, funcs:min(Column#233)->Column#156, funcs:sum(Column#234)->Column#157, funcs:max(Column#235)->Column#158, funcs:min(Column#236)->Column#159, funcs:sum(Column#237)->Column#160, funcs:max(Column#238)->Column#161, funcs:min(Column#239)->Column#162, funcs:sum(Column#240)->Column#163, funcs:max(Column#241)->Column#164	586.4 KB	0 Bytes
  └─Projection_81	30558.10	421	root		time:86.4ms, open:98.9µs, close:34µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#183, intuit_risk.deviceprofile_fact.exact_id->Column#184, intuit_risk.deviceprofile_fact.input_ip->Column#185, intuit_risk.deviceprofile_fact.true_ip->Column#186, intuit_risk.deviceprofile_fact.proxy_ip->Column#187, intuit_risk.deviceprofile_fact.agent_type->Column#188, intuit_risk.deviceprofile_fact.agent_os->Column#189, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#190, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#191, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#192, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#193, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#194, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#196, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#197, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#198, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#199, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#200, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#201, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#202, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#203, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#204, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#205, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#207, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#208, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#209, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#210, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#212, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#213, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#214, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#215, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#217, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#218, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#221, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#222, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#223, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#225, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#226, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#230, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#232, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#234, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#235, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#236, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#237, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#238, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#239, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#240, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#241, intuit_risk.pmt_txn_fact.merchant_account_number->Column#242	1.57 MB	N/A
    └─IndexHashJoin_30	30558.10	421	root		time:85.6ms, open:97.8µs, close:12µs, loops:3, inner:{total:156ms, concurrency:5, task:2, construct:2.6ms, fetch:153ms, build:553.1µs, join:460.3µs}	inner join, inner:IndexLookUp_45, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	972.3 KB	N/A
      ├─IndexReader_41(Build)	17275.51	4362	root	partition:p20260401,p20260501,p20260601,pmax	time:6.7ms, open:96.3µs, close:8.28µs, loops:7, cop_task: {num: 10, max: 2.15ms, min: 435.5µs, avg: 1.34ms, p95: 2.15ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 4.11ms, tot_wait: 2.53ms, copr_cache: disabled, build_task_duration: 36.4µs, max_distsql_concurrency: 4}, fetch_resp_duration: 6.37ms, rpc_info:{Cop:{num_rpc:10, total_time:13.3ms}}	index:Selection_40	121.3 KB	N/A
      │ └─Selection_40	17275.51	4362	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:38, tasks:10}, scan_detail: {total_process_keys: 6630, total_process_keys_size: 854810, total_keys: 6640, get_snapshot_time: 2.35ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.11ms, total_wait_time: 2.53ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
      │   └─IndexRangeScan_39	23409.44	6630	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:38, tasks:10}	range:[? ?,? +inf], keep order:false	N/A	N/A
      └─IndexLookUp_45(Probe)	30558.10	421	root	partition:p20260401,p20260501,p20260601,pmax	total_time:151.8ms, total_open:5.7ms, total_close:15.6µs, loops:4, index_task: {total_time: 123.4ms, fetch_handle: 123.4ms, build: 7.73µs, wait: 12µs}, table_task: {total_time: 35.4ms, num: 4, concurrency: 5}, next: {wait_index: 110.5ms, wait_table_lookup_build: 818.4µs, wait_table_lookup_resp: 34.6ms}		1.71 MB	N/A
        ├─Selection_44(Build)	30558.10	421	cop[tikv]		total_time:123.6ms, total_open:0s, total_close:0s, loops:16, cop_task: {num: 10, max: 63.2ms, min: 3.2ms, avg: 26.4ms, p95: 63.2ms, max_proc_keys: 132, p95_proc_keys: 132, tot_proc: 206ms, tot_wait: 2.79ms, copr_cache: disabled, build_task_duration: 1.38ms, max_distsql_concurrency: 2}, fetch_resp_duration: 123.3ms, rpc_info:{Cop:{num_rpc:10, total_time:263.6ms}}, tikv_task:{proc max:50ms, min:0s, avg: 20ms, p80:50ms, p95:50ms, iters:18, tasks:10}, scan_detail: {total_process_keys: 421, total_process_keys_size: 32130, total_keys: 5645, get_snapshot_time: 3.6ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 206ms, total_suspend_time: 243.9µs, total_wait_time: 2.79ms, total_kv_read_wall_time: 110ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
        │ └─IndexRangeScan_42	45115.02	421	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:50ms, min:0s, avg: 20ms, p80:50ms, p95:50ms, iters:18, tasks:10}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
        └─TableRowIDScan_43(Probe)	30558.10	421	cop[tikv]	table:d	total_time:34.5ms, total_open:0s, total_close:15.9µs, loops:8, cop_task: {num: 139, max: 2.49ms, min: 0s, avg: 408.3µs, p95: 2.14ms, max_proc_keys: 19, p95_proc_keys: 12, tot_proc: 17.4ms, tot_wait: 90.8ms, copr_cache: disabled, build_task_duration: 512.3µs, max_distsql_concurrency: 1, max_extra_concurrency: 3, store_batch_num: 101, store_batch_fallback_num: 6}, fetch_resp_duration: 33.9ms, rpc_info:{Cop:{num_rpc:38, total_time:56.4ms}}, tikv_task:{proc max:10ms, min:0s, avg: 143.9µs, p80:0s, p95:0s, iters:139, tasks:139}, scan_detail: {total_process_keys: 421, total_process_keys_size: 251544, total_keys: 421, get_snapshot_time: 89.5ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 17.4ms, total_wait_time: 90.8ms, total_kv_read_wall_time: 20ms}	keep order:false	N/A	N/A
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
-- best_variant=optimized_hashagg_32_8
-- explain_analyze_elapsed_ms=118.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_10	0.80	1	root		time:77.2ms, open:110.5µs, close:32.4µs, loops:2, RU:84.29, Concurrency:OFF	Column#106->Column#166, Column#107->Column#167, Column#108->Column#168, Column#109->Column#169, Column#110->Column#170, Column#111->Column#171, Column#112->Column#172, Column#113->Column#173, Column#114->Column#174, Column#115->Column#175, Column#114->Column#176, Column#116->Column#177, Column#114->Column#178, Column#117->Column#179, Column#118->Column#180, Column#119->Column#181, Column#118->Column#182, Column#120->Column#183, Column#118->Column#184, Column#121->Column#185, Column#122->Column#186, Column#123->Column#187, Column#122->Column#188, Column#124->Column#189, Column#122->Column#190, Column#125->Column#191, Column#126->Column#192, Column#127->Column#193, Column#126->Column#194, Column#128->Column#195, Column#126->Column#196, Column#129->Column#197, Column#130->Column#198, Column#131->Column#199, Column#130->Column#200, Column#132->Column#201, Column#133->Column#202, Column#134->Column#203, Column#133->Column#204, Column#135->Column#205, Column#136->Column#206, Column#137->Column#207, Column#136->Column#208, Column#138->Column#209, Column#139->Column#210, Column#140->Column#211, Column#139->Column#212, Column#141->Column#213, Column#142->Column#214, Column#143->Column#215, Column#142->Column#216, Column#144->Column#217, Column#145->Column#218, Column#146->Column#219, Column#145->Column#220, Column#147->Column#221, Column#148->Column#222, Column#149->Column#223, Column#148->Column#224, Column#150->Column#225, Column#151->Column#226, Column#152->Column#227, Column#151->Column#228, Column#153->Column#229, Column#154->Column#230, Column#155->Column#231, Column#154->Column#232, Column#156->Column#233, Column#157->Column#234, Column#158->Column#235, Column#157->Column#236, Column#159->Column#237, Column#160->Column#238, Column#161->Column#239, Column#160->Column#240, Column#162->Column#241, Column#163->Column#242, Column#164->Column#243, Column#163->Column#244	283.5 KB	N/A
└─Selection_12	0.80	1	root		time:77.2ms, open:105.8µs, close:30.8µs, loops:2	gt(Column#165, ?)	400.6 KB	N/A
  └─HashAgg_16	1.00	1	root		time:77.1ms, open:100.1µs, close:30.3µs, loops:3	funcs:count(distinct Column#263)->Column#106, funcs:count(distinct Column#264)->Column#107, funcs:count(distinct Column#265)->Column#108, funcs:count(distinct Column#266)->Column#109, funcs:count(distinct Column#267)->Column#110, funcs:count(distinct Column#268)->Column#111, funcs:count(distinct Column#269)->Column#112, funcs:count(distinct Column#270)->Column#113, funcs:sum(Column#271)->Column#114, funcs:count(distinct Column#272)->Column#115, funcs:count(distinct Column#273)->Column#116, funcs:count(distinct Column#274)->Column#117, funcs:sum(Column#275)->Column#118, funcs:count(distinct Column#276)->Column#119, funcs:count(distinct Column#277)->Column#120, funcs:count(distinct Column#278)->Column#121, funcs:sum(Column#279)->Column#122, funcs:count(distinct Column#280)->Column#123, funcs:count(distinct Column#281)->Column#124, funcs:count(distinct Column#282)->Column#125, funcs:sum(Column#283)->Column#126, funcs:count(distinct Column#284)->Column#127, funcs:count(distinct Column#285)->Column#128, funcs:min(Column#286)->Column#129, funcs:sum(Column#287)->Column#130, funcs:max(Column#288)->Column#131, funcs:min(Column#289)->Column#132, funcs:sum(Column#290)->Column#133, funcs:max(Column#291)->Column#134, funcs:min(Column#292)->Column#135, funcs:sum(Column#293)->Column#136, funcs:max(Column#294)->Column#137, funcs:min(Column#295)->Column#138, funcs:sum(Column#296)->Column#139, funcs:max(Column#297)->Column#140, funcs:min(Column#298)->Column#141, funcs:sum(Column#299)->Column#142, funcs:max(Column#300)->Column#143, funcs:min(Column#301)->Column#144, funcs:sum(Column#302)->Column#145, funcs:max(Column#303)->Column#146, funcs:min(Column#304)->Column#147, funcs:sum(Column#305)->Column#148, funcs:max(Column#306)->Column#149, funcs:min(Column#307)->Column#150, funcs:sum(Column#308)->Column#151, funcs:max(Column#309)->Column#152, funcs:min(Column#310)->Column#153, funcs:sum(Column#311)->Column#154, funcs:max(Column#312)->Column#155, funcs:min(Column#313)->Column#156, funcs:sum(Column#314)->Column#157, funcs:max(Column#315)->Column#158, funcs:min(Column#316)->Column#159, funcs:sum(Column#317)->Column#160, funcs:max(Column#318)->Column#161, funcs:min(Column#319)->Column#162, funcs:sum(Column#320)->Column#163, funcs:max(Column#321)->Column#164, funcs:count(?)->Column#165	589.5 KB	0 Bytes
    └─Projection_84	30558.10	421	root		time:76.1ms, open:87.9µs, close:29.7µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#263, intuit_risk.deviceprofile_fact.exact_id->Column#264, intuit_risk.deviceprofile_fact.input_ip->Column#265, intuit_risk.deviceprofile_fact.true_ip->Column#266, intuit_risk.deviceprofile_fact.proxy_ip->Column#267, intuit_risk.deviceprofile_fact.agent_type->Column#268, intuit_risk.deviceprofile_fact.agent_os->Column#269, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#270, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#271, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#272, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#273, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#274, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#275, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#276, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#277, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#278, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#279, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#280, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#281, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#282, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#283, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#284, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#285, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#286, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#287, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#288, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#289, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#290, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#291, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#292, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#293, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#294, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#295, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#296, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#297, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#298, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#299, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#300, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#301, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#302, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#303, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#304, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#305, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#306, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#307, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#308, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#309, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#310, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#311, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#312, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#313, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#314, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#315, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#316, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#317, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#318, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#319, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#320, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#321	1.16 MB	N/A
      └─IndexHashJoin_28	30558.10	421	root		time:75ms, open:87µs, close:9.94µs, loops:3, inner:{total:140.3ms, concurrency:5, task:2, construct:2.63ms, fetch:137.2ms, build:546.8µs, join:426.3µs}	inner join, inner:IndexLookUp_43, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	1008.8 KB	N/A
        ├─IndexReader_39(Build)	17275.51	4362	root	partition:p20260401,p20260501,p20260601,pmax	time:5.26ms, open:85µs, close:7.06µs, loops:7, cop_task: {num: 10, max: 1.7ms, min: 355.6µs, avg: 1.04ms, p95: 1.7ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 3.97ms, tot_wait: 312.3µs, copr_cache: disabled, build_task_duration: 29.8µs, max_distsql_concurrency: 4}, fetch_resp_duration: 4.99ms, rpc_info:{Cop:{num_rpc:10, total_time:10.3ms}}	index:Selection_38	121.3 KB	N/A
        │ └─Selection_38	17275.51	4362	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:38, tasks:10}, scan_detail: {total_process_keys: 6630, total_process_keys_size: 854810, total_keys: 6640, get_snapshot_time: 121.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.97ms, total_suspend_time: 4.42µs, total_wait_time: 312.3µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        │   └─IndexRangeScan_37	23409.44	6630	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:38, tasks:10}	range:[? ?,? +inf], keep order:false	N/A	N/A
        └─IndexLookUp_43(Probe)	30558.10	421	root	partition:p20260401,p20260501,p20260601,pmax	total_time:136ms, total_open:5.76ms, total_close:14.4µs, loops:4, index_task: {total_time: 113.3ms, fetch_handle: 113.3ms, build: 5.48µs, wait: 29.9µs}, table_task: {total_time: 21.6ms, num: 4, concurrency: 5}, next: {wait_index: 108.6ms, wait_table_lookup_build: 706.4µs, wait_table_lookup_resp: 20.8ms}		1.71 MB	N/A
          ├─Selection_42(Build)	30558.10	421	cop[tikv]		total_time:113.4ms, total_open:0s, total_close:0s, loops:16, cop_task: {num: 10, max: 58.7ms, min: 3.23ms, avg: 16.4ms, p95: 58.7ms, max_proc_keys: 132, p95_proc_keys: 132, tot_proc: 121.6ms, tot_wait: 249µs, copr_cache: disabled, build_task_duration: 1.33ms, max_distsql_concurrency: 2}, fetch_resp_duration: 113.2ms, rpc_info:{Cop:{num_rpc:10, total_time:164.2ms}}, tikv_task:{proc max:50ms, min:0s, avg: 14ms, p80:40ms, p95:50ms, iters:18, tasks:10}, scan_detail: {total_process_keys: 421, total_process_keys_size: 32130, total_keys: 5645, get_snapshot_time: 113.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 121.6ms, total_suspend_time: 118.6µs, total_wait_time: 249µs, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │ └─IndexRangeScan_40	45115.02	421	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:50ms, min:0s, avg: 14ms, p80:40ms, p95:50ms, iters:18, tasks:10}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
          └─TableRowIDScan_41(Probe)	30558.10	421	cop[tikv]	table:d	total_time:20.7ms, total_open:0s, total_close:17.6µs, loops:8, cop_task: {num: 139, max: 915µs, min: 0s, avg: 165.5µs, p95: 772.9µs, max_proc_keys: 19, p95_proc_keys: 12, tot_proc: 4.54ms, tot_wait: 2.63ms, copr_cache: disabled, build_task_duration: 443.8µs, max_distsql_concurrency: 1, max_extra_concurrency: 3, store_batch_num: 101, store_batch_fallback_num: 6}, fetch_resp_duration: 20.2ms, rpc_info:{Cop:{num_rpc:38, total_time:22.7ms}}, tikv_task:{proc max:10ms, min:0s, avg: 143.9µs, p80:0s, p95:0s, iters:139, tasks:139}, scan_detail: {total_process_keys: 421, total_process_keys_size: 251544, total_keys: 421, get_snapshot_time: 1.15ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.54ms, total_wait_time: 2.63ms, total_kv_read_wall_time: 20ms}	keep order:false	N/A	N/A
```

### 14. group_c_bundle_022

- Filter/window: `d.exact_id = %s` / `180d`
- Chosen event: `INV0004166099` kind=`normal` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 3605.8 ms | ok |
| `optimized_default` | `{}` | 121.2 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 119.2 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 327.4 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 116.9 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 117.8 ms | ok |

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
-- explain_analyze_elapsed_ms=3605.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_828	1.00	1	root		time:270.1ms, open:34.1µs, close:54.4µs, loops:2, RU:7381.22, Concurrency:OFF	Column#1496, Column#1497, Column#1498, Column#1499, ?->Column#1658, ?->Column#1817, ?->Column#1974, ?->Column#2131, ?->Column#2288, ?->Column#2449	11.1 KB	N/A
└─HashAgg_832	1.00	1	root		time:270.1ms, open:32µs, close:52.6µs, loops:2, partial_worker:{wall_time:269.949126ms, concurrency:4, task_num:6, tot_wait:426.118688ms, tot_exec:574.705µs, tot_time:1.079720068s, max:269.933926ms, p95:269.933926ms}, final_worker:{wall_time:269.989361ms, concurrency:4, task_num:7, tot_wait:5.389µs, tot_exec:2.815µs, tot_time:1.079795485s, max:269.958502ms, p95:269.958502ms}	funcs:sum(Column#124)->Column#1496, funcs:sum(Column#125)->Column#1497, funcs:min(Column#126)->Column#1498, funcs:max(Column#127)->Column#1499	901.3 KB	0 Bytes
  └─Union_836	4969.72	4793	root		time:270ms, open:1.08µs, close:50.2µs, loops:7		N/A	N/A
    ├─Projection_838	4938.02	4792	root		time:52ms, open:14.5µs, close:26.6µs, loops:6, Concurrency:5	intuit_risk.group_c_180d_daily_rollup.metric__c_0031->Column#124, cast(intuit_risk.group_c_180d_daily_rollup.metric__c_0032, decimal(41,6) BINARY)->Column#125, intuit_risk.group_c_180d_daily_rollup.metric__c_0033->Column#126, intuit_risk.group_c_180d_daily_rollup.metric__c_0034->Column#127	1.31 MB	N/A
    │ └─IndexLookUp_843	4938.02	4792	root		time:52.1ms, open:12.8µs, close:8.47µs, loops:6, index_task: {total_time: 7.59ms, fetch_handle: 7.59ms, build: 3.67µs, wait: 2.18µs}, table_task: {total_time: 43.5ms, num: 1, concurrency: 5}, next: {wait_index: 7.74ms, wait_table_lookup_build: 2.98ms, wait_table_lookup_resp: 40.4ms}		2.12 MB	N/A
    │   ├─Selection_842(Build)	4938.02	4792	cop[tikv]		time:7.25ms, open:0s, close:0s, loops:7, cop_task: {num: 1, max: 7.22ms, proc_keys: 4792, tot_proc: 3.9ms, tot_wait: 1.62ms, copr_cache: disabled, build_task_duration: 21.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 7.23ms, rpc_info:{Cop:{num_rpc:1, total_time:7.2ms}}, tikv_task:{time:10ms, loops:9}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 1059032, total_keys: 4793, get_snapshot_time: 1.61ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 3.9ms, total_suspend_time: 9.19µs, total_wait_time: 1.62ms, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_rollup.d_event_day, ?)	N/A	N/A
    │   │ └─IndexRangeScan_840	4945.65	4792	cop[tikv]	table:r, index:PRIMARY(bundle_id, key1, key2, p_event_day, d_event_day)	tikv_task:{time:10ms, loops:9}	range:(? ? ? ?,? ? ? +inf], keep order:false	N/A	N/A
    │   └─TableRowIDScan_841(Probe)	4938.02	4792	cop[tikv]	table:r	time:40.3ms, open:0s, close:3.63µs, loops:6, cop_task: {num: 95, max: 20ms, min: 0s, avg: 4.5ms, p95: 12.4ms, max_proc_keys: 241, p95_proc_keys: 184, tot_proc: 375.3ms, tot_wait: 75ms, copr_cache: disabled, build_task_duration: 937.1µs, max_distsql_concurrency: 15, max_extra_concurrency: 1, store_batch_num: 28}, fetch_resp_duration: 38.2ms, rpc_info:{Cop:{num_rpc:74, total_time:438.5ms}, rpc_errors:{bucket_version_not_match:7}}, backoff{regionMiss: 14ms}, tikv_task:{proc max:10ms, min:0s, avg: 4.95ms, p80:10ms, p95:10ms, iters:165, tasks:95}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 987152, total_keys: 4792, get_snapshot_time: 71.6ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 375.3ms, total_suspend_time: 1.91ms, total_wait_time: 75ms, total_kv_read_wall_time: 470ms}	keep order:false	N/A	N/A
    └─Projection_844	31.70	1	root		time:269.9ms, open:184.2µs, close:22.6µs, loops:2, Concurrency:OFF	cast(Column#120, decimal(38,6) BINARY)->Column#124, cast(Column#121, decimal(41,6) BINARY)->Column#125, cast(Column#122, decimal(38,6) BINARY)->Column#126, cast(Column#123, decimal(38,6) BINARY)->Column#127	8.71 KB	N/A
      └─HashAgg_848	31.70	1	root		time:269.9ms, open:181.7µs, close:21.3µs, loops:2, partial_worker:{wall_time:269.660011ms, concurrency:4, task_num:4, tot_wait:423.256733ms, tot_exec:39.768µs, tot_time:1.078260222s, max:269.567495ms, p95:269.567495ms}, final_worker:{wall_time:269.676361ms, concurrency:4, task_num:7, tot_wait:47.76µs, tot_exec:4.883µs, tot_time:1.078402379s, max:269.629045ms, p95:269.629045ms}	group by:intuit_risk.deviceprofile_fact.exact_id, funcs:count(?)->Column#120, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#121, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#122, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#123	24.6 KB	0 Bytes
        └─Projection_856	33729.75	6	root		time:269.7ms, open:151µs, close:19µs, loops:5, Concurrency:5	intuit_risk.pmt_txn_fact.amount, intuit_risk.deviceprofile_fact.exact_id	20.2 KB	N/A
          └─IndexHashJoin_865	33729.75	6	root		time:269.7ms, open:149.6µs, close:7.83µs, loops:5, inner:{total:388.6ms, concurrency:5, task:4, construct:20.5ms, fetch:359.6ms, build:4.19ms, join:8.44ms}	inner join, inner:IndexReader_879, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.35 MB	N/A
            ├─IndexReader_876(Build)	21567.79	21121	root	partition:all	time:15.8ms, open:147.7µs, close:4.82µs, loops:23, cop_task: {num: 34, max: 5.24ms, min: 453.5µs, avg: 1.74ms, p95: 4.42ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 33.1ms, tot_wait: 2.01ms, copr_cache: disabled, build_task_duration: 76.7µs, max_distsql_concurrency: 9}, fetch_resp_duration: 13.8ms, rpc_info:{Cop:{num_rpc:34, total_time:58.8ms}}	index:Selection_875	337.1 KB	N/A
            │ └─Selection_875	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 588.2µs, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 1.52ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 33.1ms, total_suspend_time: 54.1µs, total_wait_time: 2.01ms, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
            │   └─IndexRangeScan_874	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 588.2µs, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
            └─IndexReader_879(Probe)	33729.75	5285	root	partition:all	total_time:348ms, total_open:86.9ms, total_close:44.7µs, loops:11, cop_task: {num: 160, max: 213.9ms, min: 474.7µs, avg: 4.4ms, p95: 9.33ms, max_proc_keys: 151, p95_proc_keys: 120, tot_proc: 188.3ms, tot_wait: 12.2ms, copr_cache: disabled, build_task_duration: 14.9ms, max_distsql_concurrency: 15}, fetch_resp_duration: 257.6ms, rpc_info:{Cop:{num_rpc:160, total_time:700.4ms}}	index:Selection_878	10.4 KB	N/A
              └─Selection_878	33729.75	5285	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.31ms, p80:0s, p95:10ms, iters:229, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.32ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 188.3ms, total_suspend_time: 378.1µs, total_wait_time: 12.2ms, total_kv_read_wall_time: 210ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
                └─IndexRangeScan_877	45706.03	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1.31ms, p80:0s, p95:10ms, iters:229, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_237	N/A	0	root			Output: ScalarQueryCol#1657	N/A	N/A
└─MaxOneRow_135	1.00	1	root		time:812.9ms, open:8.79µs, close:38.5µs, loops:1		N/A	N/A
  └─HashAgg_140	1.00	1	root		time:812.9ms, open:8.09µs, close:37.9µs, loops:2	funcs:count(distinct Column#1614)->Column#1615	337.0 KB	0 Bytes
    └─Union_144	33791.70	5291	root		time:811.8ms, open:792ns, close:37.1µs, loops:10		N/A	N/A
      ├─Projection_146	61.95	5285	root		time:12.3ms, open:83.1µs, close:8.93µs, loops:7, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1614	148.0 KB	N/A
      │ └─IndexReader_150	61.95	5285	root		time:12.2ms, open:80.8µs, close:5.7µs, loops:7, cop_task: {num: 5, max: 3.48ms, min: 1.4ms, avg: 2.51ms, p95: 3.48ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 6.1ms, tot_wait: 1.4ms, copr_cache: disabled, build_task_duration: 27.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 11.9ms, rpc_info:{Cop:{num_rpc:5, total_time:12.5ms}}	index:Selection_149	450.3 KB	N/A
      │   └─Selection_149	61.95	5285	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:24, tasks:5}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1516795, total_keys: 5290, get_snapshot_time: 1.32ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 6.1ms, total_suspend_time: 8.25µs, total_wait_time: 1.4ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_148	62.05	5285	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:24, tasks:5}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_151	33729.75	6	root		time:812.9ms, open:131.7µs, close:27µs, loops:4, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.merchant_account_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1614	30.6 KB	N/A
        └─IndexHashJoin_162	33729.75	6	root		time:812.8ms, open:130.3µs, close:9.9µs, loops:4, inner:{total:2.05s, concurrency:5, task:4, construct:14.4ms, fetch:2.02s, build:2.83ms, join:8.41ms}	inner join, inner:IndexReader_176, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.42 MB	N/A
          ├─IndexReader_173(Build)	21567.79	21121	root	partition:all	time:35.1ms, open:127.7µs, close:6.38µs, loops:23, cop_task: {num: 34, max: 13.1ms, min: 536.9µs, avg: 3.27ms, p95: 8.2ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 61.2ms, tot_wait: 7.69ms, copr_cache: disabled, build_task_duration: 64.8µs, max_distsql_concurrency: 9}, fetch_resp_duration: 34.1ms, rpc_info:{Cop:{num_rpc:34, total_time:110.9ms}}	index:Selection_172	278.6 KB	N/A
          │ └─Selection_172	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 7.17ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 61.2ms, total_suspend_time: 132.6µs, total_wait_time: 7.69ms, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_171	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_176(Probe)	33729.75	5285	root	partition:all	total_time:2.02s, total_open:77.8ms, total_close:53.9µs, loops:11, cop_task: {num: 160, max: 686.2ms, min: 1.8ms, avg: 70.2ms, p95: 300.5ms, max_proc_keys: 147, p95_proc_keys: 122, tot_proc: 9.98s, tot_wait: 210.9ms, copr_cache: disabled, build_task_duration: 15.7ms, max_distsql_concurrency: 15}, fetch_resp_duration: 1.94s, rpc_info:{Cop:{num_rpc:162, total_time:11.2s}, rpc_errors:{bucket_version_not_match:2}}, backoff{regionMiss: 4ms}	index:Selection_175	7.48 KB	N/A
            └─Selection_175	33729.75	5285	cop[tikv]		tikv_task:{proc max:680ms, min:0s, avg: 65.7ms, p80:120ms, p95:300ms, iters:229, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43614, get_snapshot_time: 24ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 9.98s, total_suspend_time: 557.4ms, total_wait_time: 210.9ms, total_kv_read_wall_time: 10.5s}	not(isnull(intuit_risk.pmt_txn_fact.merchant_account_number)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_174	45743.67	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:680ms, min:0s, avg: 65.7ms, p80:120ms, p95:300ms, iters:229, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_358	N/A	0	root			Output: ScalarQueryCol#1816	N/A	N/A
└─MaxOneRow_256	1.00	1	root		time:1.91s, open:8.4µs, close:26.5µs, loops:1		N/A	N/A
  └─HashAgg_261	1.00	1	root		time:1.91s, open:7.92µs, close:26.1µs, loops:2	funcs:count(distinct Column#1773)->Column#1774	514.3 KB	0 Bytes
    └─Union_265	33780.10	3426	root		time:1.91s, open:926ns, close:25.4µs, loops:8		N/A	N/A
      ├─Projection_267	50.35	3423	root		time:11.4ms, open:76.4µs, close:10.1µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1773	215.2 KB	N/A
      │ └─IndexReader_271	50.35	3423	root		time:11.3ms, open:73.8µs, close:7.27µs, loops:5, cop_task: {num: 4, max: 4.26ms, min: 1.49ms, avg: 2.81ms, p95: 4.26ms, max_proc_keys: 1727, p95_proc_keys: 1727, tot_proc: 5.92ms, tot_wait: 735µs, copr_cache: disabled, build_task_duration: 27.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 11ms, rpc_info:{Cop:{num_rpc:4, total_time:11.2ms}}	index:Selection_270	468.9 KB	N/A
      │   └─Selection_270	50.35	3423	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}, scan_detail: {total_process_keys: 3423, total_process_keys_size: 1331547, total_keys: 3427, get_snapshot_time: 667.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.92ms, total_suspend_time: 11.3µs, total_wait_time: 735µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_269	50.43	3423	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_272	33729.75	3	root		time:1.91s, open:126.7µs, close:14.7µs, loops:4, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.card_holder_number_sha512, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1773	77.8 KB	N/A
        └─IndexHashJoin_283	33729.75	3	root		time:1.91s, open:125.7µs, close:6.19µs, loops:4, inner:{total:5.73s, concurrency:5, task:4, construct:14.4ms, fetch:5.71s, build:2.8ms, join:6ms}	inner join, inner:IndexReader_297, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.19 MB	N/A
          ├─IndexReader_294(Build)	21567.79	21121	root	partition:all	time:20.9ms, open:123.6µs, close:3.42µs, loops:23, cop_task: {num: 34, max: 7.13ms, min: 417.3µs, avg: 2.15ms, p95: 6.05ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 46.3ms, tot_wait: 1.13ms, copr_cache: disabled, build_task_duration: 64.2µs, max_distsql_concurrency: 9}, fetch_resp_duration: 19.8ms, rpc_info:{Cop:{num_rpc:34, total_time:72.9ms}}	index:Selection_293	337.1 KB	N/A
          │ └─Selection_293	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 882.4µs, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 526.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 46.3ms, total_suspend_time: 108.8µs, total_wait_time: 1.13ms, total_kv_read_wall_time: 30ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_292	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 882.4µs, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_297(Probe)	33729.75	3423	root	partition:all	total_time:5.7s, total_open:89.9ms, total_close:36.2µs, loops:10, cop_task: {num: 160, max: 1.87s, min: 1.03ms, avg: 77.2ms, p95: 575.7ms, max_proc_keys: 151, p95_proc_keys: 120, tot_proc: 1.68s, tot_wait: 7.76ms, copr_cache: disabled, build_task_duration: 17.4ms, max_distsql_concurrency: 15}, fetch_resp_duration: 5.6s, rpc_info:{Cop:{num_rpc:160, total_time:12.4s}}	index:Selection_296	10.5 KB	N/A
            └─Selection_296	33729.75	3423	cop[tikv]		tikv_task:{proc max:90ms, min:0s, avg: 11.4ms, p80:20ms, p95:40ms, iters:229, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1585121, total_keys: 34051, get_snapshot_time: 1.96ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.68s, total_suspend_time: 24.6ms, total_wait_time: 7.76ms, total_kv_read_wall_time: 1.42s}	not(isnull(intuit_risk.pmt_txn_fact.card_holder_number_sha512)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_295	65559.91	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:90ms, min:0s, avg: 11.4ms, p80:20ms, p95:40ms, iters:229, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_473	N/A	0	root			Output: ScalarQueryCol#1973	N/A	N/A
└─MaxOneRow_377	1.00	1	root		time:136.8ms, open:10.3µs, close:63.3µs, loops:1		N/A	N/A
  └─HashAgg_382	1.00	1	root		time:136.8ms, open:9.65µs, close:62.9µs, loops:2	funcs:count(distinct Column#1932)->Column#1933	17.2 KB	0 Bytes
    └─Union_386	33783.04	3604	root		time:136.5ms, open:1.03µs, close:62.2µs, loops:9		N/A	N/A
      ├─Projection_388	53.28	3599	root		time:10.3ms, open:73.2µs, close:12.8µs, loops:5, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1932	132.0 KB	N/A
      │ └─IndexReader_392	53.28	3599	root		time:10.2ms, open:70.9µs, close:10µs, loops:5, cop_task: {num: 4, max: 4.02ms, min: 1.17ms, avg: 2.52ms, p95: 4.02ms, max_proc_keys: 1903, p95_proc_keys: 1903, tot_proc: 4.39ms, tot_wait: 1.59ms, copr_cache: disabled, build_task_duration: 25.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 9.86ms, rpc_info:{Cop:{num_rpc:4, total_time:10ms}}	index:Selection_391	321.0 KB	N/A
      │   └─Selection_391	53.28	3599	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}, scan_detail: {total_process_keys: 3599, total_process_keys_size: 914146, total_keys: 3603, get_snapshot_time: 1.54ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 4.39ms, total_suspend_time: 3.19µs, total_wait_time: 1.59ms, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_390	53.37	3599	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2.5ms, p80:10ms, p95:10ms, iters:18, tasks:4}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_393	33729.75	5	root		time:136.7ms, open:162.8µs, close:48.8µs, loops:5, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.card_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1932	21.8 KB	N/A
        └─IndexHashJoin_404	33729.75	5	root		time:136.6ms, open:161.7µs, close:5.91µs, loops:5, inner:{total:328.8ms, concurrency:5, task:4, construct:15.9ms, fetch:306.4ms, build:3.34ms, join:6.43ms}	inner join, inner:IndexReader_418, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.31 MB	N/A
          ├─IndexReader_415(Build)	21567.79	21121	root	partition:all	time:19.6ms, open:159.7µs, close:3.4µs, loops:23, cop_task: {num: 34, max: 6.8ms, min: 496.6µs, avg: 2.03ms, p95: 5.61ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 41ms, tot_wait: 1.1ms, copr_cache: disabled, build_task_duration: 73.3µs, max_distsql_concurrency: 9}, fetch_resp_duration: 17.7ms, rpc_info:{Cop:{num_rpc:34, total_time:68.7ms}}	index:Selection_414	337.1 KB	N/A
          │ └─Selection_414	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 495.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 41ms, total_suspend_time: 96.3µs, total_wait_time: 1.1ms, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_413	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_418(Probe)	33729.75	3871	root	partition:all	total_time:297.8ms, total_open:100.7ms, total_close:43.5µs, loops:10, cop_task: {num: 160, max: 60.5ms, min: 899.8µs, avg: 9.36ms, p95: 28.4ms, max_proc_keys: 151, p95_proc_keys: 120, tot_proc: 1.13s, tot_wait: 11.8ms, copr_cache: disabled, build_task_duration: 19.3ms, max_distsql_concurrency: 15}, fetch_resp_duration: 192.7ms, rpc_info:{Cop:{num_rpc:160, total_time:1.49s}}	index:Selection_417	9.79 KB	N/A
            └─Selection_417	33729.75	3871	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 7.25ms, p80:10ms, p95:30ms, iters:229, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1666865, total_keys: 41023, get_snapshot_time: 1.86ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.13s, total_suspend_time: 3.61ms, total_wait_time: 11.8ms, total_kv_read_wall_time: 1.06s}	not(isnull(intuit_risk.pmt_txn_fact.card_type)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_416	62068.67	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:50ms, min:0s, avg: 7.25ms, p80:10ms, p95:30ms, iters:229, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_588	N/A	0	root			Output: ScalarQueryCol#2130	N/A	N/A
└─MaxOneRow_492	1.00	1	root		time:123ms, open:10.9µs, close:38.5µs, loops:1		N/A	N/A
  └─HashAgg_497	1.00	1	root		time:123ms, open:10.1µs, close:37.7µs, loops:2	funcs:count(distinct Column#2089)->Column#2090	12.6 KB	0 Bytes
    └─Union_501	33752.89	728	root		time:122.9ms, open:962ns, close:36.8µs, loops:2		N/A	N/A
      ├─Projection_503	23.14	728	root		time:4.08ms, open:80.4µs, close:7.27µs, loops:2, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2089	95.4 KB	N/A
      │ └─IndexReader_507	23.14	728	root		time:4.04ms, open:75.9µs, close:4.49µs, loops:2, cop_task: {num: 3, max: 2.3ms, min: 492.7µs, avg: 1.29ms, p95: 2.3ms, max_proc_keys: 480, p95_proc_keys: 480, tot_proc: 1.18ms, tot_wait: 645.5µs, copr_cache: disabled, build_task_duration: 28µs, max_distsql_concurrency: 1}, fetch_resp_duration: 3.82ms, rpc_info:{Cop:{num_rpc:3, total_time:3.83ms}}	index:Selection_506	79.8 KB	N/A
      │   └─Selection_506	23.14	728	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:8, tasks:3}, scan_detail: {total_process_keys: 728, total_process_keys_size: 185640, total_keys: 731, get_snapshot_time: 599µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.18ms, total_wait_time: 645.5µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_505	23.17	728	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:8, tasks:3}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_508	33729.75	0	root		time:122.9ms, open:136.9µs, close:28.5µs, loops:1, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.entry_method, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2089	6.21 KB	N/A
        └─IndexHashJoin_519	33729.75	0	root		time:122.8ms, open:134.5µs, close:7.91µs, loops:1, inner:{total:276.4ms, concurrency:5, task:4, construct:15.9ms, fetch:258.9ms, build:3.36ms, join:1.58ms}	inner join, inner:IndexReader_533, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.30 MB	N/A
          ├─IndexReader_530(Build)	21567.79	21121	root	partition:all	time:16.8ms, open:132.3µs, close:4.52µs, loops:23, cop_task: {num: 34, max: 5.51ms, min: 383.8µs, avg: 1.77ms, p95: 4.77ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 34.6ms, tot_wait: 925.9µs, copr_cache: disabled, build_task_duration: 73.4µs, max_distsql_concurrency: 9}, fetch_resp_duration: 14.9ms, rpc_info:{Cop:{num_rpc:34, total_time:59.8ms}}	index:Selection_529	337.1 KB	N/A
          │ └─Selection_529	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 882.4µs, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 396.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 34.6ms, total_suspend_time: 59.6µs, total_wait_time: 925.9µs, total_kv_read_wall_time: 30ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_528	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 882.4µs, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_533(Probe)	33729.75	731	root	partition:all	total_time:250.6ms, total_open:101ms, total_close:39.2µs, loops:8, cop_task: {num: 160, max: 56.8ms, min: 514µs, avg: 4.81ms, p95: 13.7ms, max_proc_keys: 156, p95_proc_keys: 120, tot_proc: 446.6ms, tot_wait: 5.65ms, copr_cache: disabled, build_task_duration: 20ms, max_distsql_concurrency: 15}, fetch_resp_duration: 145.3ms, rpc_info:{Cop:{num_rpc:160, total_time:766.8ms}}	index:Selection_532	8.65 KB	N/A
            └─Selection_532	33729.75	731	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 2.38ms, p80:0s, p95:10ms, iters:228, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.56ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 446.6ms, total_suspend_time: 1.05ms, total_wait_time: 5.65ms, total_kv_read_wall_time: 380ms}	not(isnull(intuit_risk.pmt_txn_fact.entry_method)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_531	317192.19	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:50ms, min:0s, avg: 2.38ms, p80:0s, p95:10ms, iters:228, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_703	N/A	0	root			Output: ScalarQueryCol#2287	N/A	N/A
└─MaxOneRow_607	1.00	1	root		time:105.2ms, open:11.3µs, close:27.2µs, loops:1		N/A	N/A
  └─HashAgg_612	1.00	1	root		time:105.1ms, open:10.8µs, close:26.8µs, loops:2	funcs:count(distinct Column#2246)->Column#2247	27.6 KB	0 Bytes
    └─Union_616	33791.76	5106	root		time:104.5ms, open:946ns, close:26.1µs, loops:11		N/A	N/A
      ├─Projection_618	62.01	5100	root		time:10.8ms, open:78µs, close:10.7µs, loops:7, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2246	149.9 KB	N/A
      │ └─IndexReader_622	62.01	5100	root		time:10.6ms, open:73.8µs, close:7.39µs, loops:7, cop_task: {num: 5, max: 3ms, min: 1.23ms, avg: 2.16ms, p95: 3ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 5.53ms, tot_wait: 638.2µs, copr_cache: disabled, build_task_duration: 25.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 10.2ms, rpc_info:{Cop:{num_rpc:5, total_time:10.8ms}}	index:Selection_621	420.5 KB	N/A
      │   └─Selection_621	62.01	5100	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:24, tasks:5}, scan_detail: {total_process_keys: 5100, total_process_keys_size: 1414856, total_keys: 5105, get_snapshot_time: 569.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 5.53ms, total_suspend_time: 6.84µs, total_wait_time: 638.2µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_620	62.11	5100	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 2ms, p80:10ms, p95:10ms, iters:24, tasks:5}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_623	33729.75	6	root		time:105.1ms, open:120.8µs, close:14.8µs, loops:5, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.mt_gateway, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2246	31.8 KB	N/A
        └─IndexHashJoin_634	33729.75	6	root		time:105ms, open:119.9µs, close:5.83µs, loops:5, inner:{total:242ms, concurrency:5, task:4, construct:16ms, fetch:217.7ms, build:3.33ms, join:8.2ms}	inner join, inner:IndexReader_648, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.30 MB	N/A
          ├─IndexReader_645(Build)	21567.79	21121	root	partition:all	time:16.1ms, open:118.4µs, close:3.35µs, loops:23, cop_task: {num: 34, max: 5.56ms, min: 390.8µs, avg: 1.7ms, p95: 4.11ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 33.4ms, tot_wait: 902.9µs, copr_cache: disabled, build_task_duration: 69.1µs, max_distsql_concurrency: 9}, fetch_resp_duration: 14.2ms, rpc_info:{Cop:{num_rpc:34, total_time:57.4ms}}	index:Selection_644	337.1 KB	N/A
          │ └─Selection_644	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 294.1µs, p80:0s, p95:0s, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 360µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 33.4ms, total_suspend_time: 54.3µs, total_wait_time: 902.9µs, total_kv_read_wall_time: 10ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_643	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 294.1µs, p80:0s, p95:0s, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_648(Probe)	33729.75	5285	root	partition:all	total_time:208.5ms, total_open:101.3ms, total_close:43µs, loops:11, cop_task: {num: 160, max: 38.6ms, min: 495.3µs, avg: 3.63ms, p95: 11.3ms, max_proc_keys: 151, p95_proc_keys: 120, tot_proc: 262.8ms, tot_wait: 4.02ms, copr_cache: disabled, build_task_duration: 18.4ms, max_distsql_concurrency: 15}, fetch_resp_duration: 102.6ms, rpc_info:{Cop:{num_rpc:160, total_time:576.8ms}}	index:Selection_647	9.90 KB	N/A
            └─Selection_647	33729.75	5285	cop[tikv]		tikv_task:{proc max:30ms, min:0s, avg: 1.63ms, p80:0s, p95:10ms, iters:229, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.45ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 262.8ms, total_suspend_time: 605.1µs, total_wait_time: 4.02ms, total_kv_read_wall_time: 260ms}	not(isnull(intuit_risk.pmt_txn_fact.mt_gateway)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_646	45743.81	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:30ms, min:0s, avg: 1.63ms, p80:0s, p95:10ms, iters:229, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
ScalarSubQuery_824	N/A	0	root			Output: ScalarQueryCol#2448	N/A	N/A
└─MaxOneRow_722	1.00	1	root		time:84.5ms, open:11.4µs, close:28.5µs, loops:1		N/A	N/A
  └─HashAgg_727	1.00	1	root		time:84.5ms, open:10.6µs, close:28.1µs, loops:2	funcs:count(distinct Column#2403)->Column#2404	74.5 KB	0 Bytes
    └─Union_731	33761.35	1415	root		time:84.2ms, open:1.11µs, close:27.2µs, loops:4		N/A	N/A
      ├─Projection_733	31.60	1414	root		time:5.43ms, open:81.9µs, close:8.87µs, loops:3, Concurrency:OFF	cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2403	137.2 KB	N/A
      │ └─IndexReader_737	31.60	1414	root		time:5.35ms, open:77.5µs, close:5.51µs, loops:3, cop_task: {num: 3, max: 2.71ms, min: 1.06ms, avg: 1.7ms, p95: 2.71ms, max_proc_keys: 710, p95_proc_keys: 710, tot_proc: 2.12ms, tot_wait: 665.3µs, copr_cache: disabled, build_task_duration: 28.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 5.09ms, rpc_info:{Cop:{num_rpc:3, total_time:5.06ms}}	index:Selection_736	141.9 KB	N/A
      │   └─Selection_736	31.60	1414	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:12, tasks:3}, scan_detail: {total_process_keys: 1414, total_process_keys_size: 383194, total_keys: 1417, get_snapshot_time: 622µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.12ms, total_wait_time: 665.3µs}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
      │     └─IndexRangeScan_735	31.65	1414	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:12, tasks:3}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_738	33729.75	1	root		time:84.5ms, open:131.8µs, close:17.7µs, loops:2, Concurrency:5	cast(cast(intuit_risk.pmt_txn_fact.check_bank_routing_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#2403	12.2 KB	N/A
        └─IndexHashJoin_749	33729.75	1	root		time:84.4ms, open:130.5µs, close:5.52µs, loops:2, inner:{total:191.3ms, concurrency:5, task:4, construct:16.2ms, fetch:172.3ms, build:3.26ms, join:2.73ms}	inner join, inner:IndexReader_763, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.34 MB	N/A
          ├─IndexReader_760(Build)	21567.79	21121	root	partition:all	time:15.8ms, open:128.4µs, close:2.68µs, loops:23, cop_task: {num: 34, max: 4.84ms, min: 334.7µs, avg: 1.67ms, p95: 4.44ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 32.8ms, tot_wait: 872µs, copr_cache: disabled, build_task_duration: 68.4µs, max_distsql_concurrency: 9}, fetch_resp_duration: 13.8ms, rpc_info:{Cop:{num_rpc:34, total_time:56.4ms}}	index:Selection_759	337.1 KB	N/A
          │ └─Selection_759	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 348.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 32.8ms, total_suspend_time: 54.1µs, total_wait_time: 872µs, total_kv_read_wall_time: 50ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │   └─IndexRangeScan_758	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 1.47ms, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
          └─IndexReader_763(Probe)	33729.75	1414	root	partition:all	total_time:163.1ms, total_open:99.9ms, total_close:39µs, loops:8, cop_task: {num: 160, max: 17.2ms, min: 556.7µs, avg: 3.1ms, p95: 10ms, max_proc_keys: 159, p95_proc_keys: 120, tot_proc: 189.4ms, tot_wait: 3.82ms, copr_cache: disabled, build_task_duration: 20.1ms, max_distsql_concurrency: 15}, fetch_resp_duration: 58.9ms, rpc_info:{Cop:{num_rpc:160, total_time:492.3ms}}	index:Selection_762	8.54 KB	N/A
            └─Selection_762	33729.75	1414	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 1ms, p80:0s, p95:10ms, iters:230, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43614, get_snapshot_time: 1.34ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 189.4ms, total_suspend_time: 435µs, total_wait_time: 3.82ms, total_kv_read_wall_time: 160ms}	not(isnull(intuit_risk.pmt_txn_fact.check_bank_routing_number)), not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
              └─IndexRangeScan_761	130475.89	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 1ms, p80:0s, p95:10ms, iters:230, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
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
-- best_variant=optimized_distinct_pushdown
-- explain_analyze_elapsed_ms=116.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashJoin_202	1.00	1	root		time:80.2ms, open:32µs, close:196.4µs, loops:2, RU:592.51, build_hash_table:{total:79.8ms, fetch:79.8ms, build:4.84µs}, probe:{concurrency:5, total:399.1ms, max:79.8ms, probe:4.2µs, fetch and wait:399.1ms}	CARTESIAN inner join	67.2 KB	0 Bytes
├─HashAgg_283(Build)	1.00	1	root		time:79.9ms, open:6.32µs, close:129.2µs, loops:2	funcs:count(distinct Column#505)->Column#433, funcs:count(distinct Column#506)->Column#434, funcs:count(distinct Column#507)->Column#435, funcs:count(distinct Column#508)->Column#436, funcs:count(distinct Column#509)->Column#437, funcs:count(distinct Column#510)->Column#438	973.2 KB	0 Bytes
│ └─Projection_343	162185.14	19570	root		time:74.7ms, open:786ns, close:128.1µs, loops:26, Concurrency:5	case(eq(Column#431, ?), Column#432)->Column#505, case(eq(Column#431, ?), Column#432)->Column#506, case(eq(Column#431, ?), Column#432)->Column#507, case(eq(Column#431, ?), Column#432)->Column#508, case(eq(Column#431, ?), Column#432)->Column#509, case(eq(Column#431, ?), Column#432)->Column#510	949.7 KB	N/A
│   └─Union_285	162185.14	19570	root		time:79.8ms, open:177ns, close:110.3µs, loops:26		N/A	N/A
│     ├─Projection_287	282.34	19549	root		time:8.31ms, open:114.1µs, close:8.27µs, loops:21, Concurrency:OFF	intuit_risk.group_c_180d_daily_distinct.template_id->Column#431, cast(intuit_risk.group_c_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	227.8 KB	N/A
│     │ └─IndexReader_291	282.34	19549	root		time:7.52ms, open:108.1µs, close:5.93µs, loops:21, cop_task: {num: 24, max: 2.92ms, min: 494.4µs, avg: 1.44ms, p95: 2.82ms, max_proc_keys: 2016, p95_proc_keys: 2016, tot_proc: 17.6ms, tot_wait: 512.5µs, copr_cache: disabled, build_task_duration: 42.7µs, max_distsql_concurrency: 6}, fetch_resp_duration: 6.81ms, rpc_info:{Cop:{num_rpc:24, total_time:34.2ms}}	index:Selection_290	546.5 KB	N/A
│     │   └─Selection_290	282.34	19549	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 833.3µs, p80:0s, p95:10ms, iters:104, tasks:24}, scan_detail: {total_process_keys: 19549, total_process_keys_size: 5746178, total_keys: 19573, get_snapshot_time: 209.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 17.6ms, total_suspend_time: 20.4µs, total_wait_time: 512.5µs, total_kv_read_wall_time: 20ms}	gt(intuit_risk.group_c_180d_daily_distinct.d_event_day, ?)	N/A	N/A
│     │     └─IndexRangeScan_289	282.77	19549	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, p_event_day, d_event_day, distinct_value)	tikv_task:{proc max:10ms, min:0s, avg: 833.3µs, p80:0s, p95:10ms, iters:104, tasks:24}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
│     ├─Projection_292	26983.80	6	root		time:79.4ms, open:129.9µs, close:17.6µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.merchant_account_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│     │ └─Selection_294	26983.80	6	root		time:79.4ms, open:128.3µs, close:1.06µs, loops:2	not(isnull(intuit_risk.pmt_txn_fact.merchant_account_number))	114.3 KB	N/A
│     │   └─CTEFullScan_296	33729.75	6	root	CTE:raw_boundary	time:79.3ms, open:125.1µs, close:210ns, loops:6	data:CTE_0	39.0 KB	0 Bytes
│     ├─Projection_300	26983.80	3	root		time:79.5ms, open:123.9µs, close:16.7µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.card_holder_number_sha512, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│     │ └─Selection_302	26983.80	3	root		time:79.5ms, open:122.6µs, close:1.05µs, loops:2	not(isnull(intuit_risk.pmt_txn_fact.card_holder_number_sha512))	69.0 KB	N/A
│     │   └─CTEFullScan_304	33729.75	6	root	CTE:raw_boundary	time:79.5ms, open:113µs, close:297ns, loops:6	data:CTE_0	N/A	N/A
│     ├─Projection_308	26983.80	5	root		time:79.7ms, open:79.4ms, close:16.9µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.card_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│     │ └─Selection_310	26983.80	5	root		time:79.6ms, open:79.4ms, close:1.65µs, loops:2	not(isnull(intuit_risk.pmt_txn_fact.card_type))	10.1 KB	N/A
│     │   └─CTEFullScan_312	33729.75	6	root	CTE:raw_boundary	time:79.5ms, open:79.4ms, close:726ns, loops:6	data:CTE_0	N/A	N/A
│     ├─Projection_316	26983.80	0	root		time:79.7ms, open:79.5ms, close:13.9µs, loops:1, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.entry_method, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	30.6 KB	N/A
│     │ └─Selection_318	26983.80	0	root		time:79.7ms, open:79.5ms, close:505ns, loops:1	not(isnull(intuit_risk.pmt_txn_fact.entry_method))	15.4 KB	N/A
│     │   └─CTEFullScan_320	33729.75	6	root	CTE:raw_boundary	time:79.6ms, open:79.5ms, close:141ns, loops:5	data:CTE_0	N/A	N/A
│     ├─Projection_324	26983.80	6	root		time:70.8ms, open:70.7ms, close:15.4µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.mt_gateway, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	47.9 KB	N/A
│     │ └─Selection_326	26983.80	6	root		time:70.7ms, open:70.7ms, close:742ns, loops:2	not(isnull(intuit_risk.pmt_txn_fact.mt_gateway))	15.5 KB	N/A
│     │   └─CTEFullScan_328	33729.75	6	root	CTE:raw_boundary	time:70.7ms, open:70.7ms, close:133ns, loops:6	data:CTE_0	N/A	N/A
│     └─Projection_332	26983.80	1	root		time:88.7µs, open:5.95µs, close:20µs, loops:2, Concurrency:5	?->Column#431, cast(cast(intuit_risk.pmt_txn_fact.check_bank_routing_number, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#432	40.8 KB	N/A
│       └─Selection_334	26983.80	1	root		time:37.3µs, open:4.81µs, close:713ns, loops:2	not(isnull(intuit_risk.pmt_txn_fact.check_bank_routing_number))	6.26 KB	N/A
│         └─CTEFullScan_336	33729.75	6	root	CTE:raw_boundary	time:9.05µs, open:331ns, close:156ns, loops:6	data:CTE_0	N/A	N/A
└─HashAgg_209(Probe)	1.00	1	root		time:79.7ms, open:24.4µs, close:60.1µs, loops:2, partial_worker:{wall_time:79.600421ms, concurrency:4, task_num:6, tot_wait:123.564332ms, tot_exec:554.672µs, tot_time:318.242645ms, max:79.561161ms, p95:79.561161ms}, final_worker:{wall_time:79.623773ms, concurrency:4, task_num:7, tot_wait:4.596µs, tot_exec:4.236µs, tot_time:318.434624ms, max:79.613299ms, p95:79.613299ms}	funcs:sum(Column#353)->Column#357, funcs:sum(Column#354)->Column#358, funcs:min(Column#355)->Column#359, funcs:max(Column#356)->Column#360	1.06 MB	0 Bytes
  └─Union_213	4938.82	4793	root		time:79.6ms, open:875ns, close:57.6µs, loops:7		N/A	N/A
    ├─Projection_215	4938.02	4792	root		time:14.7ms, open:12.2µs, close:21µs, loops:6, Concurrency:5	intuit_risk.group_c_180d_daily_rollup.metric__c_0031->Column#353, cast(intuit_risk.group_c_180d_daily_rollup.metric__c_0032, decimal(41,6) BINARY)->Column#354, intuit_risk.group_c_180d_daily_rollup.metric__c_0033->Column#355, intuit_risk.group_c_180d_daily_rollup.metric__c_0034->Column#356	1.31 MB	N/A
    │ └─IndexLookUp_220	4938.02	4792	root		time:14.8ms, open:11µs, close:7.14µs, loops:6, index_task: {total_time: 4.04ms, fetch_handle: 4.03ms, build: 1.64µs, wait: 6.8µs}, table_task: {total_time: 9.55ms, num: 1, concurrency: 5}, next: {wait_index: 4.11ms, wait_table_lookup_build: 1.97ms, wait_table_lookup_resp: 7.58ms}		2.16 MB	N/A
    │   ├─Selection_219(Build)	4938.02	4792	cop[tikv]		time:3.88ms, open:0s, close:0s, loops:7, cop_task: {num: 1, max: 3.85ms, proc_keys: 4792, tot_proc: 2.93ms, tot_wait: 43.6µs, copr_cache: disabled, build_task_duration: 17.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 3.87ms, rpc_info:{Cop:{num_rpc:1, total_time:3.84ms}}, tikv_task:{time:10ms, loops:9}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 1059032, total_keys: 4793, get_snapshot_time: 21.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.93ms, total_suspend_time: 7.08µs, total_wait_time: 43.6µs, total_kv_read_wall_time: 10ms}	gt(intuit_risk.group_c_180d_daily_rollup.d_event_day, ?)	N/A	N/A
    │   │ └─IndexRangeScan_217	4945.65	4792	cop[tikv]	table:r, index:PRIMARY(bundle_id, key1, key2, p_event_day, d_event_day)	tikv_task:{time:10ms, loops:9}	range:(? ? ? ?,? ? ? +inf], keep order:false	N/A	N/A
    │   └─TableRowIDScan_218(Probe)	4938.02	4792	cop[tikv]	table:r	time:7.5ms, open:0s, close:3.36µs, loops:6, cop_task: {num: 100, max: 3.25ms, min: 0s, avg: 877.2µs, p95: 2.48ms, max_proc_keys: 241, p95_proc_keys: 184, tot_proc: 42.6ms, tot_wait: 3.13ms, copr_cache: disabled, build_task_duration: 665.5µs, max_distsql_concurrency: 15, max_extra_concurrency: 1, store_batch_num: 34}, fetch_resp_duration: 6.25ms, rpc_info:{Cop:{num_rpc:66, total_time:87.1ms}}, tikv_task:{proc max:10ms, min:0s, avg: 400µs, p80:0s, p95:0s, iters:169, tasks:100}, scan_detail: {total_process_keys: 4792, total_process_keys_size: 987152, total_keys: 4792, get_snapshot_time: 801µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 42.6ms, total_suspend_time: 40.8µs, total_wait_time: 3.13ms, total_kv_read_wall_time: 40ms}	keep order:false	N/A	N/A
    └─Projection_221	0.80	1	root		time:79.5ms, open:79.4ms, close:35.7µs, loops:2, Concurrency:OFF	cast(Column#345, decimal(38,6) BINARY)->Column#353, cast(Column#346, decimal(41,6) BINARY)->Column#354, cast(Column#347, decimal(38,6) BINARY)->Column#355, cast(Column#348, decimal(38,6) BINARY)->Column#356	11.4 KB	N/A
      └─Selection_223	0.80	1	root		time:79.5ms, open:79.4ms, close:34.5µs, loops:2	gt(Column#345, ?)	16.7 KB	N/A
        └─HashAgg_227	1.00	1	root		time:79.5ms, open:79.4ms, close:33.9µs, loops:3, partial_worker:{wall_time:51.057µs, concurrency:4, task_num:4, tot_wait:1.948µs, tot_exec:23.957µs, tot_time:87.43µs, max:27.035µs, p95:27.035µs}, final_worker:{wall_time:89.599µs, concurrency:4, task_num:7, tot_wait:3.684µs, tot_exec:2.014µs, tot_time:212.679µs, max:70.039µs, p95:70.039µs}	funcs:count(?)->Column#345, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#346, funcs:min(intuit_risk.pmt_txn_fact.amount)->Column#347, funcs:max(intuit_risk.pmt_txn_fact.amount)->Column#348	58.0 KB	0 Bytes
          └─CTEFullScan_231	33729.75	6	root	CTE:raw_boundary	time:79.4ms, open:79.3ms, close:31.7µs, loops:5	data:CTE_0	N/A	N/A
CTE_0	33729.75	6	root		time:79.3ms, open:125.1µs, close:210ns, loops:6	Non-Recursive CTE	39.0 KB	0 Bytes
└─Projection_146(Seed Part)	33729.75	6	root		time:79.3ms, open:121.7µs, close:31µs, loops:5, Concurrency:5	intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.pmt_txn_fact.card_type, intuit_risk.pmt_txn_fact.entry_method, intuit_risk.pmt_txn_fact.mt_gateway, intuit_risk.pmt_txn_fact.check_bank_routing_number	162.5 KB	N/A
  └─IndexHashJoin_157	33729.75	6	root		time:79.2ms, open:120.6µs, close:9.73µs, loops:5, inner:{total:178.5ms, concurrency:5, task:4, construct:14.5ms, fetch:155ms, build:2.93ms, join:8.98ms}	inner join, inner:IndexReader_171, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id), other cond:or(lt(intuit_risk.pmt_txn_fact.event_date, ?), lt(intuit_risk.deviceprofile_fact.jms_timestamp, ?))	5.35 MB	N/A
    ├─IndexReader_168(Build)	21567.79	21121	root	partition:all	time:17.5ms, open:119.3µs, close:6.76µs, loops:23, cop_task: {num: 34, max: 5.89ms, min: 454.6µs, avg: 1.77ms, p95: 4.54ms, max_proc_keys: 4064, p95_proc_keys: 4064, tot_proc: 33.9ms, tot_wait: 924.5µs, copr_cache: disabled, build_task_duration: 72.4µs, max_distsql_concurrency: 9}, fetch_resp_duration: 16.5ms, rpc_info:{Cop:{num_rpc:34, total_time:59.6ms}}	index:Selection_167	337.1 KB	N/A
    │ └─Selection_167	21567.79	21121	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 588.2µs, p80:0s, p95:10ms, iters:154, tasks:34}, scan_detail: {total_process_keys: 36773, total_process_keys_size: 14573536, total_keys: 36807, get_snapshot_time: 402.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 33.9ms, total_suspend_time: 53µs, total_wait_time: 924.5µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_166	31842.00	36773	cop[tikv]	table:d, index:idx_dev_exact_runtime_cov(exact_id, jms_timestamp, interaction_id, agent_type, agent_os, browser_language, device_fingerprint_score, device_score, device_worst_score, input_ip, input_ip_score, proxy_ip, smart_id, true_ip, true_ip_score)	tikv_task:{proc max:10ms, min:0s, avg: 588.2µs, p80:0s, p95:10ms, iters:154, tasks:34}	range:(? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_171(Probe)	33729.75	5285	root	partition:all	total_time:147.9ms, total_open:85.5ms, total_close:44.1µs, loops:11, cop_task: {num: 160, max: 16ms, min: 457.3µs, avg: 3ms, p95: 9.67ms, max_proc_keys: 151, p95_proc_keys: 120, tot_proc: 185.9ms, tot_wait: 4.05ms, copr_cache: disabled, build_task_duration: 20ms, max_distsql_concurrency: 15}, fetch_resp_duration: 58.6ms, rpc_info:{Cop:{num_rpc:160, total_time:477ms}}	index:Selection_170	18.8 KB	N/A
      └─Selection_170	33729.75	5285	cop[tikv]		tikv_task:{proc max:10ms, min:0s, avg: 812.5µs, p80:0s, p95:10ms, iters:229, tasks:160}, scan_detail: {total_process_keys: 5285, total_process_keys_size: 1722837, total_keys: 43613, get_snapshot_time: 1.53ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 185.9ms, total_suspend_time: 406.1µs, total_wait_time: 4.05ms, total_kv_read_wall_time: 130ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_169	45706.03	5285	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:10ms, min:0s, avg: 812.5µs, p80:0s, p95:10ms, iters:229, tasks:160}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### 15. group_c_bundle_007

- Filter/window: `p.merchant_account_number = %s` / `1d`
- Chosen event: `INV0037793946` kind=`hot_merchant_account_number` error=`(1105, 'context deadline exceeded')`
- Optimization: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Index: use payment-side covering join index to avoid p table row lookup; Session tuning: optimized_hashagg_16_8

#### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 115.5 ms | ok |
| `optimized_default` | `{}` | 107.4 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 106.7 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 107.1 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 106.8 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 107.7 ms | ok |

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
-- explain_analyze_elapsed_ms=115.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_8	48.46	1	root		time:75.9ms, open:117.5µs, close:36.7µs, loops:2, RU:39.18, Concurrency:OFF	Column#106, Column#107, Column#108, Column#109, Column#110, Column#111, Column#112, Column#113, Column#114, Column#115, Column#114, Column#116, Column#114, Column#117, Column#118, Column#119, Column#118, Column#120, Column#118, Column#121, Column#122, Column#123, Column#122, Column#124, Column#122, Column#125, Column#126, Column#127, Column#126, Column#128, Column#126, Column#129, Column#130, Column#131, Column#130, Column#132, Column#133, Column#134, Column#133, Column#135, Column#136, Column#137, Column#136, Column#138, Column#139, Column#140, Column#139, Column#141, Column#142, Column#143, Column#142, Column#144, Column#145, Column#146, Column#145, Column#147, Column#148, Column#149, Column#148, Column#150, Column#151, Column#152, Column#151, Column#153, Column#154, Column#155, Column#154, Column#156, Column#157, Column#158, Column#157, Column#159, Column#160, Column#161, Column#160, Column#162, Column#163, Column#164, Column#163	339.1 KB	N/A
└─HashAgg_12	48.46	1	root		time:75.8ms, open:112.5µs, close:35.2µs, loops:2	group by:Column#242, funcs:count(distinct Column#183)->Column#106, funcs:count(distinct Column#184)->Column#107, funcs:count(distinct Column#185)->Column#108, funcs:count(distinct Column#186)->Column#109, funcs:count(distinct Column#187)->Column#110, funcs:count(distinct Column#188)->Column#111, funcs:count(distinct Column#189)->Column#112, funcs:count(distinct Column#190)->Column#113, funcs:sum(Column#191)->Column#114, funcs:count(distinct Column#192)->Column#115, funcs:count(distinct Column#193)->Column#116, funcs:count(distinct Column#194)->Column#117, funcs:sum(Column#195)->Column#118, funcs:count(distinct Column#196)->Column#119, funcs:count(distinct Column#197)->Column#120, funcs:count(distinct Column#198)->Column#121, funcs:sum(Column#199)->Column#122, funcs:count(distinct Column#200)->Column#123, funcs:count(distinct Column#201)->Column#124, funcs:count(distinct Column#202)->Column#125, funcs:sum(Column#203)->Column#126, funcs:count(distinct Column#204)->Column#127, funcs:count(distinct Column#205)->Column#128, funcs:min(Column#206)->Column#129, funcs:sum(Column#207)->Column#130, funcs:max(Column#208)->Column#131, funcs:min(Column#209)->Column#132, funcs:sum(Column#210)->Column#133, funcs:max(Column#211)->Column#134, funcs:min(Column#212)->Column#135, funcs:sum(Column#213)->Column#136, funcs:max(Column#214)->Column#137, funcs:min(Column#215)->Column#138, funcs:sum(Column#216)->Column#139, funcs:max(Column#217)->Column#140, funcs:min(Column#218)->Column#141, funcs:sum(Column#219)->Column#142, funcs:max(Column#220)->Column#143, funcs:min(Column#221)->Column#144, funcs:sum(Column#222)->Column#145, funcs:max(Column#223)->Column#146, funcs:min(Column#224)->Column#147, funcs:sum(Column#225)->Column#148, funcs:max(Column#226)->Column#149, funcs:min(Column#227)->Column#150, funcs:sum(Column#228)->Column#151, funcs:max(Column#229)->Column#152, funcs:min(Column#230)->Column#153, funcs:sum(Column#231)->Column#154, funcs:max(Column#232)->Column#155, funcs:min(Column#233)->Column#156, funcs:sum(Column#234)->Column#157, funcs:max(Column#235)->Column#158, funcs:min(Column#236)->Column#159, funcs:sum(Column#237)->Column#160, funcs:max(Column#238)->Column#161, funcs:min(Column#239)->Column#162, funcs:sum(Column#240)->Column#163, funcs:max(Column#241)->Column#164	502.9 KB	0 Bytes
  └─Projection_81	22376.97	139	root		time:75.4ms, open:77.5µs, close:34.3µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#183, intuit_risk.deviceprofile_fact.exact_id->Column#184, intuit_risk.deviceprofile_fact.input_ip->Column#185, intuit_risk.deviceprofile_fact.true_ip->Column#186, intuit_risk.deviceprofile_fact.proxy_ip->Column#187, intuit_risk.deviceprofile_fact.agent_type->Column#188, intuit_risk.deviceprofile_fact.agent_os->Column#189, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#190, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#191, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#192, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#193, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#194, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#196, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#197, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#198, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#199, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#200, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#201, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#202, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#203, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#204, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#205, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#207, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#208, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#209, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#210, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#212, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#213, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#214, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#215, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#217, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#218, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#221, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#222, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#223, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#225, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#226, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#227, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#228, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#229, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#230, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#232, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#234, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#235, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#236, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#237, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#238, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#239, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#240, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#241, intuit_risk.pmt_txn_fact.merchant_account_number->Column#242	988.4 KB	N/A
    └─IndexHashJoin_30	22376.97	139	root		time:74.4ms, open:76.6µs, close:9.68µs, loops:3, inner:{total:78.2ms, concurrency:5, task:2, construct:1.43ms, fetch:76.6ms, build:302.2µs, join:156µs}	inner join, inner:IndexLookUp_45, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	539.8 KB	N/A
      ├─IndexReader_41(Build)	12650.44	2352	root	partition:p20260501,p20260601,pmax	time:3.81ms, open:74.2µs, close:6.85µs, loops:5, cop_task: {num: 6, max: 1.7ms, min: 384.9µs, avg: 879.5µs, p95: 1.7ms, max_proc_keys: 1907, p95_proc_keys: 1907, tot_proc: 2.28ms, tot_wait: 172.5µs, copr_cache: disabled, build_task_duration: 22.3µs, max_distsql_concurrency: 3}, fetch_resp_duration: 3.64ms, rpc_info:{Cop:{num_rpc:6, total_time:5.2ms}}	index:Selection_40	100.3 KB	N/A
      │ └─Selection_40	12650.44	2352	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}, scan_detail: {total_process_keys: 3603, total_process_keys_size: 463666, total_keys: 3609, get_snapshot_time: 74.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.28ms, total_suspend_time: 4.16µs, total_wait_time: 172.5µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
      │   └─IndexRangeScan_39	17142.18	3603	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
      └─IndexLookUp_45(Probe)	22376.97	139	root	partition:p20260501,p20260601,pmax	total_time:75.9ms, total_open:2.32ms, total_close:12.6µs, loops:4, index_task: {total_time: 65.8ms, fetch_handle: 65.8ms, build: 2.88µs, wait: 2.9µs}, table_task: {total_time: 6.86ms, num: 2, concurrency: 5}, next: {wait_index: 66.7ms, wait_table_lookup_build: 238.6µs, wait_table_lookup_resp: 6.56ms}		189.0 KB	N/A
        ├─Selection_44(Build)	22376.97	139	cop[tikv]		total_time:66.9ms, total_open:0s, total_close:0s, loops:10, cop_task: {num: 8, max: 61ms, min: 1.02ms, avg: 10ms, p95: 61ms, max_proc_keys: 91, p95_proc_keys: 91, tot_proc: 49.6ms, tot_wait: 284.5µs, copr_cache: disabled, build_task_duration: 546.2µs, max_distsql_concurrency: 2}, fetch_resp_duration: 66.8ms, rpc_info:{Cop:{num_rpc:8, total_time:80.1ms}}, tikv_task:{proc max:40ms, min:0s, avg: 5ms, p80:0s, p95:40ms, iters:10, tasks:8}, scan_detail: {total_process_keys: 139, total_process_keys_size: 10098, total_keys: 876, get_snapshot_time: 128.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 49.6ms, total_suspend_time: 24.9µs, total_wait_time: 284.5µs}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
        │ └─IndexRangeScan_42	33036.65	139	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:40ms, min:0s, avg: 5ms, p80:0s, p95:40ms, iters:10, tasks:8}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
        └─TableRowIDScan_43(Probe)	22376.97	139	cop[tikv]	table:d	total_time:6.52ms, total_open:0s, total_close:7.16µs, loops:4, cop_task: {num: 46, max: 917.7µs, min: 0s, avg: 221.9µs, p95: 753.1µs, max_proc_keys: 13, p95_proc_keys: 12, tot_proc: 1.73ms, tot_wait: 936.6µs, copr_cache: disabled, build_task_duration: 152.9µs, max_distsql_concurrency: 1, max_extra_concurrency: 4, store_batch_num: 30, store_batch_fallback_num: 2}, fetch_resp_duration: 6.32ms, rpc_info:{Cop:{num_rpc:16, total_time:10.1ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:46, tasks:46}, scan_detail: {total_process_keys: 139, total_process_keys_size: 82492, total_keys: 139, get_snapshot_time: 428.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.73ms, total_wait_time: 936.6µs}	keep order:false	N/A	N/A
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
-- best_variant=optimized_hashagg_16_8
-- explain_analyze_elapsed_ms=106.7
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_10	0.80	1	root		time:68.4ms, open:114.2µs, close:36.6µs, loops:2, RU:38.14, Concurrency:OFF	Column#106->Column#166, Column#107->Column#167, Column#108->Column#168, Column#109->Column#169, Column#110->Column#170, Column#111->Column#171, Column#112->Column#172, Column#113->Column#173, Column#114->Column#174, Column#115->Column#175, Column#114->Column#176, Column#116->Column#177, Column#114->Column#178, Column#117->Column#179, Column#118->Column#180, Column#119->Column#181, Column#118->Column#182, Column#120->Column#183, Column#118->Column#184, Column#121->Column#185, Column#122->Column#186, Column#123->Column#187, Column#122->Column#188, Column#124->Column#189, Column#122->Column#190, Column#125->Column#191, Column#126->Column#192, Column#127->Column#193, Column#126->Column#194, Column#128->Column#195, Column#126->Column#196, Column#129->Column#197, Column#130->Column#198, Column#131->Column#199, Column#130->Column#200, Column#132->Column#201, Column#133->Column#202, Column#134->Column#203, Column#133->Column#204, Column#135->Column#205, Column#136->Column#206, Column#137->Column#207, Column#136->Column#208, Column#138->Column#209, Column#139->Column#210, Column#140->Column#211, Column#139->Column#212, Column#141->Column#213, Column#142->Column#214, Column#143->Column#215, Column#142->Column#216, Column#144->Column#217, Column#145->Column#218, Column#146->Column#219, Column#145->Column#220, Column#147->Column#221, Column#148->Column#222, Column#149->Column#223, Column#148->Column#224, Column#150->Column#225, Column#151->Column#226, Column#152->Column#227, Column#151->Column#228, Column#153->Column#229, Column#154->Column#230, Column#155->Column#231, Column#154->Column#232, Column#156->Column#233, Column#157->Column#234, Column#158->Column#235, Column#157->Column#236, Column#159->Column#237, Column#160->Column#238, Column#161->Column#239, Column#160->Column#240, Column#162->Column#241, Column#163->Column#242, Column#164->Column#243, Column#163->Column#244	337.5 KB	N/A
└─Selection_12	0.80	1	root		time:68.3ms, open:108.9µs, close:34.8µs, loops:2	gt(Column#165, ?)	376.8 KB	N/A
  └─HashAgg_16	1.00	1	root		time:68.3ms, open:101.7µs, close:34.1µs, loops:3	funcs:count(distinct Column#263)->Column#106, funcs:count(distinct Column#264)->Column#107, funcs:count(distinct Column#265)->Column#108, funcs:count(distinct Column#266)->Column#109, funcs:count(distinct Column#267)->Column#110, funcs:count(distinct Column#268)->Column#111, funcs:count(distinct Column#269)->Column#112, funcs:count(distinct Column#270)->Column#113, funcs:sum(Column#271)->Column#114, funcs:count(distinct Column#272)->Column#115, funcs:count(distinct Column#273)->Column#116, funcs:count(distinct Column#274)->Column#117, funcs:sum(Column#275)->Column#118, funcs:count(distinct Column#276)->Column#119, funcs:count(distinct Column#277)->Column#120, funcs:count(distinct Column#278)->Column#121, funcs:sum(Column#279)->Column#122, funcs:count(distinct Column#280)->Column#123, funcs:count(distinct Column#281)->Column#124, funcs:count(distinct Column#282)->Column#125, funcs:sum(Column#283)->Column#126, funcs:count(distinct Column#284)->Column#127, funcs:count(distinct Column#285)->Column#128, funcs:min(Column#286)->Column#129, funcs:sum(Column#287)->Column#130, funcs:max(Column#288)->Column#131, funcs:min(Column#289)->Column#132, funcs:sum(Column#290)->Column#133, funcs:max(Column#291)->Column#134, funcs:min(Column#292)->Column#135, funcs:sum(Column#293)->Column#136, funcs:max(Column#294)->Column#137, funcs:min(Column#295)->Column#138, funcs:sum(Column#296)->Column#139, funcs:max(Column#297)->Column#140, funcs:min(Column#298)->Column#141, funcs:sum(Column#299)->Column#142, funcs:max(Column#300)->Column#143, funcs:min(Column#301)->Column#144, funcs:sum(Column#302)->Column#145, funcs:max(Column#303)->Column#146, funcs:min(Column#304)->Column#147, funcs:sum(Column#305)->Column#148, funcs:max(Column#306)->Column#149, funcs:min(Column#307)->Column#150, funcs:sum(Column#308)->Column#151, funcs:max(Column#309)->Column#152, funcs:min(Column#310)->Column#153, funcs:sum(Column#311)->Column#154, funcs:max(Column#312)->Column#155, funcs:min(Column#313)->Column#156, funcs:sum(Column#314)->Column#157, funcs:max(Column#315)->Column#158, funcs:min(Column#316)->Column#159, funcs:sum(Column#317)->Column#160, funcs:max(Column#318)->Column#161, funcs:min(Column#319)->Column#162, funcs:sum(Column#320)->Column#163, funcs:max(Column#321)->Column#164, funcs:count(?)->Column#165	304.6 KB	0 Bytes
    └─Projection_84	22376.97	139	root		time:67.9ms, open:84.3µs, close:33.3µs, loops:3, Concurrency:5	intuit_risk.deviceprofile_fact.smart_id->Column#263, intuit_risk.deviceprofile_fact.exact_id->Column#264, intuit_risk.deviceprofile_fact.input_ip->Column#265, intuit_risk.deviceprofile_fact.true_ip->Column#266, intuit_risk.deviceprofile_fact.proxy_ip->Column#267, intuit_risk.deviceprofile_fact.agent_type->Column#268, intuit_risk.deviceprofile_fact.agent_os->Column#269, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#270, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#271, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#272, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#273, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#274, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#275, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#276, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#277, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#278, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#279, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#280, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#281, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.smart_id)->Column#282, cast(case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), ?, ?), decimal(20,0) BINARY)->Column#283, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.exact_id)->Column#284, case(eq(intuit_risk.pmt_txn_fact.transaction_type, ?), intuit_risk.deviceprofile_fact.input_ip)->Column#285, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#286, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#287, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#288, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#289, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#290, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#291, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#292, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#293, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#294, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#295, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#296, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#297, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#298, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#299, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#300, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#301, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#302, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#303, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#304, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#305, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#306, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#307, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#308, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#309, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#310, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#311, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#312, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#313, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#314, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#315, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#316, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#317, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_score))), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#318, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#319, cast(case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#320, case(and(and(eq(intuit_risk.deviceprofile_fact.agent_type, ?), not(isnull(intuit_risk.deviceprofile_fact.device_worst_score))), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#321	567.5 KB	N/A
      └─IndexHashJoin_28	22376.97	139	root		time:66.8ms, open:83.4µs, close:9.06µs, loops:3, inner:{total:68.1ms, concurrency:5, task:2, construct:1.4ms, fetch:66.5ms, build:316.8µs, join:191.8µs}	inner join, inner:IndexLookUp_43, outer key:intuit_risk.pmt_txn_fact.parsed_interaction_id, inner key:intuit_risk.deviceprofile_fact.interaction_id, equal cond:eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id)	538 KB	N/A
        ├─IndexReader_39(Build)	12650.44	2352	root	partition:p20260501,p20260601,pmax	time:3.72ms, open:82µs, close:5.86µs, loops:5, cop_task: {num: 6, max: 1.4ms, min: 478.7µs, avg: 888.8µs, p95: 1.4ms, max_proc_keys: 1907, p95_proc_keys: 1907, tot_proc: 2.2ms, tot_wait: 193.3µs, copr_cache: disabled, build_task_duration: 26.7µs, max_distsql_concurrency: 3}, fetch_resp_duration: 3.49ms, rpc_info:{Cop:{num_rpc:6, total_time:5.24ms}}	index:Selection_38	100.3 KB	N/A
        │ └─Selection_38	12650.44	2352	cop[tikv]		tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}, scan_detail: {total_process_keys: 3603, total_process_keys_size: 463666, total_keys: 3609, get_snapshot_time: 87.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 2.2ms, total_wait_time: 193.3µs}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        │   └─IndexRangeScan_37	17142.18	3603	cop[tikv]	table:p, index:idx_pmt_merchant_c_join_cov(merchant_account_number, event_date, parsed_interaction_id, transaction_type)	tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:20, tasks:6}	range:[? ?,? +inf], keep order:false	N/A	N/A
        └─IndexLookUp_43(Probe)	22376.97	139	root	partition:p20260501,p20260601,pmax	total_time:65.8ms, total_open:2.33ms, total_close:14µs, loops:4, index_task: {total_time: 55.7ms, fetch_handle: 55.7ms, build: 5.05µs, wait: 3.43µs}, table_task: {total_time: 6.85ms, num: 2, concurrency: 5}, next: {wait_index: 56.6ms, wait_table_lookup_build: 218.7µs, wait_table_lookup_resp: 6.56ms}		189.0 KB	N/A
          ├─Selection_42(Build)	22376.97	139	cop[tikv]		total_time:56.9ms, total_open:0s, total_close:0s, loops:10, cop_task: {num: 8, max: 53.5ms, min: 1.13ms, avg: 8.72ms, p95: 53.5ms, max_proc_keys: 91, p95_proc_keys: 91, tot_proc: 46.5ms, tot_wait: 227.9µs, copr_cache: disabled, build_task_duration: 563.5µs, max_distsql_concurrency: 2}, fetch_resp_duration: 56.8ms, rpc_info:{Cop:{num_rpc:8, total_time:69.6ms}}, tikv_task:{proc max:40ms, min:0s, avg: 7.5ms, p80:10ms, p95:40ms, iters:10, tasks:8}, scan_detail: {total_process_keys: 139, total_process_keys_size: 10098, total_keys: 876, get_snapshot_time: 99.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 46.5ms, total_suspend_time: 18.9µs, total_wait_time: 227.9µs, total_kv_read_wall_time: 20ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
          │ └─IndexRangeScan_40	33036.65	139	cop[tikv]	table:d, index:idx_interaction_id_jms_timestamp(interaction_id, jms_timestamp)	tikv_task:{proc max:40ms, min:0s, avg: 7.5ms, p80:10ms, p95:40ms, iters:10, tasks:8}	range: decided by [eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id) ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)], keep order:false	N/A	N/A
          └─TableRowIDScan_41(Probe)	22376.97	139	cop[tikv]	table:d	total_time:6.53ms, total_open:0s, total_close:7.92µs, loops:4, cop_task: {num: 46, max: 956µs, min: 0s, avg: 225.8µs, p95: 771.8µs, max_proc_keys: 13, p95_proc_keys: 12, tot_proc: 1.7ms, tot_wait: 1.01ms, copr_cache: disabled, build_task_duration: 151.5µs, max_distsql_concurrency: 1, max_extra_concurrency: 4, store_batch_num: 30, store_batch_fallback_num: 2}, fetch_resp_duration: 6.31ms, rpc_info:{Cop:{num_rpc:16, total_time:10.2ms}}, tikv_task:{proc max:0s, min:0s, avg: 0s, p80:0s, p95:0s, iters:46, tasks:46}, scan_detail: {total_process_keys: 139, total_process_keys_size: 82492, total_keys: 139, get_snapshot_time: 417.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.7ms, total_wait_time: 1.01ms}	keep order:false	N/A	N/A
```
