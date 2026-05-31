# Exhaustive Bundle Rewrite Optimizer

- Generated: `2026-05-31T04:35:24`
- Mixed JSON: `/home/ec2-user/tidb_intuit_perf_support_bundle_lean/code/results/mixed_traffic_1780186589.json`
- Bundle count: `65`
- Rule: candidates must return the same columns and normalized row values as the current optimized SQL.

## Summary

| Bundle | Group | Current Best | Best Candidate | Candidate Best | Gain | Accepted | Reason |
| --- | --- | ---: | --- | ---: | ---: | --- | --- |
| `group_a_bundle_001` | A | 19.2 | `group_a_dimension_rollup/default` | 18.2 | 5.1% | no | below_threshold |
| `group_a_bundle_002` | A | 323.9 | `group_a_dimension_rollup/default` | 99.0 | 69.4% | yes | >=10pct_faster |
| `group_a_bundle_003` | A | 12.2 | `group_a_dimension_rollup/distinct_pushdown_hashagg_16_8` | 11.2 | 7.9% | no | below_threshold |
| `group_a_bundle_004` | A | 17.9 | `group_a_dimension_rollup/default` | 17.4 | 3.0% | no | below_threshold |
| `group_a_bundle_005` | A | 19.4 | `group_a_dimension_rollup/default` | 18.8 | 3.3% | no | below_threshold |
| `group_a_bundle_006` | A | 491.6 | `group_a_dimension_rollup/distinct_pushdown` | 121.4 | 75.3% | yes | >=10pct_faster |
| `group_a_bundle_007` | A | 12.3 | `group_a_dimension_rollup/default` | 11.6 | 5.7% | no | below_threshold |
| `group_a_bundle_008` | A | 19.3 | `group_a_dimension_rollup/distinct_pushdown` | 18.4 | 4.6% | no | below_threshold |
| `group_a_bundle_009` | A | 21.3 | `group_a_dimension_rollup/distinct_pushdown` | 20.7 | 2.9% | no | below_threshold |
| `group_a_bundle_010` | A | 84.8 | `group_a_dimension_rollup/distinct_pushdown` | 84.1 | 0.8% | no | below_threshold |
| `group_a_bundle_011` | A | 8.0 | `group_a_dimension_rollup/distinct_pushdown` | 7.8 | 1.7% | no | below_threshold |
| `group_a_bundle_012` | A | 120.6 | `group_a_dimension_rollup/default` | 30.8 | 74.4% | yes | >=10pct_faster |
| `group_a_bundle_013` | A | 3.0 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_a_bundle_014` | A | 5.5 | `group_a_dimension_rollup/default` | 5.6 | -0.0% | no | below_threshold |
| `group_a_bundle_015` | A | 3.1 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_a_bundle_016` | A | 10.1 | `group_a_dimension_rollup/default` | 9.5 | 5.2% | no | below_threshold |
| `group_a_bundle_017` | A | 5.0 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_a_bundle_018` | A | 6.6 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_a_bundle_019` | A | 5.0 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_a_bundle_020` | A | 5.3 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_b_bundle_001` | B | 80.6 | `filtered_scalar_subqueries/distinct_pushdown_hashagg_16_8` | 572.0 | -609.3% | no | below_threshold |
| `group_b_bundle_002` | B | 167.9 | `filtered_scalar_subqueries/hashagg_16_8` | 1858.2 | -1006.7% | no | below_threshold |
| `group_b_bundle_003` | B | 388.4 | `filtered_scalar_subqueries/distinct_pushdown` | 2168.4 | -458.3% | no | not_enough_gain |
| `group_b_bundle_004` | B | 209.4 | `group_b_numeric_projection/agg_pushdown_hashagg_16_8` | 211.8 | -1.2% | no | below_threshold |
| `group_b_bundle_005` | B | 7.6 | `filtered_scalar_subqueries/distinct_pushdown` | 143.1 | -1778.6% | no | below_threshold |
| `group_b_bundle_006` | B | 222.9 | `filtered_scalar_subqueries/hashagg_16_8` | 2635.7 | -1082.3% | no | below_threshold |
| `group_b_bundle_007` | B | 205.2 | `filtered_scalar_subqueries/distinct_pushdown` | 2348.2 | -1044.3% | no | below_threshold |
| `group_b_bundle_008` | B | 258.6 | `group_b_numeric_projection/hashagg_16_8` | 258.8 | -0.1% | no | below_threshold |
| `group_b_bundle_009` | B | 89.5 | `filtered_scalar_subqueries/distinct_pushdown` | 577.2 | -545.0% | no | below_threshold |
| `group_b_bundle_010` | B | 717.5 | `filtered_scalar_subqueries/distinct_pushdown` | 8908.8 | -1141.7% | no | not_enough_gain |
| `group_b_bundle_011` | B | 444.5 | `filtered_scalar_subqueries/distinct_pushdown_hashagg_16_8` | 6132.7 | -1279.6% | no | not_enough_gain |
| `group_b_bundle_012` | B | 705.3 | `group_b_numeric_projection/default` | 711.3 | -0.8% | no | not_enough_gain |
| `group_b_bundle_013` | B | 3.1 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_b_bundle_014` | B | 81.7 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_b_bundle_015` | B | 3.1 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_b_bundle_016` | B | 3.2 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_b_bundle_017` | B | 8.1 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_b_bundle_018` | B | 610.8 | `-` | 0.0 | 0.0% | no | no_valid_candidate |
| `group_b_bundle_019` | B | 659.7 | `-` | 0.0 | 0.0% | no | no_valid_candidate |
| `group_b_bundle_020` | B | 1023.8 | `-` | 0.0 | 0.0% | no | no_valid_candidate |
| `group_c_bundle_001` | C | 7.5 | `group_c_device_first_join/hashagg_16_8` | 7.3 | 3.4% | no | below_threshold |
| `group_c_bundle_002` | C | 351.6 | `group_c_device_first_join/distinct_pushdown` | 188.6 | 46.4% | yes | >=10pct_faster |
| `group_c_bundle_003` | C | 165.6 | `group_c_device_first_join/agg_pushdown_hashagg_16_8` | 146.6 | 11.5% | yes | >=10pct_faster |
| `group_c_bundle_004` | C | 205.7 | `group_c_device_first_join/distinct_pushdown` | 192.7 | 6.3% | no | below_threshold |
| `group_c_bundle_005` | C | 8.1 | `group_c_inner_join/default` | 8.1 | -0.0% | no | below_threshold |
| `group_c_bundle_006` | C | 5.8 | `group_c_inner_join/default` | 5.6 | 3.5% | no | below_threshold |
| `group_c_bundle_007` | C | 212.6 | `group_c_inner_join/hashagg_16_8` | 209.4 | 1.5% | no | below_threshold |
| `group_c_bundle_008` | C | 7.1 | `group_c_device_first_join/default` | 7.0 | 1.8% | no | below_threshold |
| `group_c_bundle_009` | C | 231.9 | `group_c_device_first_join/default` | 212.2 | 8.5% | no | below_threshold |
| `group_c_bundle_010` | C | 165.2 | `group_c_device_first_join/distinct_pushdown_hashagg_16_8` | 162.6 | 1.5% | no | below_threshold |
| `group_c_bundle_011` | C | 296.1 | `group_c_inner_join/default` | 293.7 | 0.8% | no | below_threshold |
| `group_c_bundle_012` | C | 7.1 | `group_c_inner_join/distinct_pushdown_hashagg_16_8` | 6.8 | 3.6% | no | below_threshold |
| `group_c_bundle_013` | C | 5.5 | `group_c_inner_join/default` | 5.3 | 2.9% | no | below_threshold |
| `group_c_bundle_014` | C | 167.2 | `group_c_inner_join/default` | 146.3 | 12.5% | yes | >=10pct_faster |
| `group_c_bundle_015` | C | 7.9 | `group_c_device_first_join/distinct_pushdown` | 7.5 | 4.8% | no | below_threshold |
| `group_c_bundle_016` | C | 321.3 | `group_c_device_first_join/agg_pushdown_hashagg_16_8` | 242.7 | 24.5% | yes | >=10pct_faster |
| `group_c_bundle_017` | C | 286.8 | `group_c_device_first_join/hashagg_16_8` | 213.1 | 25.7% | yes | >=10pct_faster |
| `group_c_bundle_018` | C | 452.4 | `group_c_device_first_join/distinct_pushdown` | 443.5 | 2.0% | no | not_enough_gain |
| `group_c_bundle_019` | C | 10.5 | `group_c_inner_join/distinct_pushdown_hashagg_16_8` | 10.2 | 2.9% | no | below_threshold |
| `group_c_bundle_020` | C | 5.8 | `group_c_inner_join/agg_pushdown_hashagg_16_8` | 5.8 | -0.6% | no | below_threshold |
| `group_c_bundle_021` | C | 161.4 | `group_c_inner_join/distinct_pushdown_hashagg_16_8` | 150.1 | 7.0% | no | below_threshold |
| `group_c_bundle_022` | C | 13.3 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_c_bundle_023` | C | 1267.5 | `-` | 0.0 | 0.0% | no | no_valid_candidate |
| `group_c_bundle_024` | C | 12.3 | `-` | 0.0 | 0.0% | no | below_threshold |
| `group_c_bundle_025` | C | 769.2 | `-` | 0.0 | 0.0% | no | no_valid_candidate |

- Accepted rewrites: `8`
- Unresolved >= threshold: `10`

## Accepted Rewrites

| Bundle | Method | Current | New | Gain |
| --- | --- | ---: | ---: | ---: |
| `group_a_bundle_002` | CASE pruning: pre-aggregate low-cardinality dimensions, then pivot CASE metrics from compact rows | 323.9 | 99.0 | 69.4% |
| `group_a_bundle_006` | CASE pruning: pre-aggregate low-cardinality dimensions, then pivot CASE metrics from compact rows | 491.6 | 121.4 | 75.3% |
| `group_a_bundle_012` | CASE pruning: pre-aggregate low-cardinality dimensions, then pivot CASE metrics from compact rows | 120.6 | 30.8 | 74.4% |
| `group_c_bundle_002` | Join order rewrite: start from filtered device rows, then join payment rows | 351.6 | 188.6 | 46.4% |
| `group_c_bundle_003` | Join order rewrite: start from filtered device rows, then join payment rows | 165.6 | 146.6 | 11.5% |
| `group_c_bundle_014` | Join rewrite: LEFT JOIN is semantically INNER because WHERE predicates require d-side rows | 167.2 | 146.3 | 12.5% |
| `group_c_bundle_016` | Join order rewrite: start from filtered device rows, then join payment rows | 321.3 | 242.7 | 24.5% |
| `group_c_bundle_017` | Join order rewrite: start from filtered device rows, then join payment rows | 286.8 | 213.1 | 25.7% |

## Per-Bundle Details

### group_a_bundle_001

- Group/filter/window: `A` / `p.card_holder_number_sha512 = %s` / `1d`
- Current best: `19.2ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`10`
- Best candidate: `group_a_dimension_rollup/default` `18.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 18.2 | 10 | False | not_enough_gain |

### group_a_bundle_002

- Group/filter/window: `A` / `p.check_bank_routing_number = %s` / `1d`
- Current best: `323.9ms` setting=`default` scan_sum=`140279`
- Best candidate: `group_a_dimension_rollup/default` `99.0ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 99.0 | 140279 | True | >=10pct_faster |

#### Accepted SQL

```sql
SELECT
  SUM(b.row_count) AS `metric__a_0033`,
  SUM(b.amount_sum) AS `metric__a_0034`,
  MIN(b.amount_min) AS `metric__a_0035`,
  MAX(b.amount_max) AS `metric__a_0036`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `metric__a_1081`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1081`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_sum END) AS `metric__a_1082`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1082`,
  MIN(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_min END) AS `metric__a_1083`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1083`,
  MAX(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_max END) AS `metric__a_1084`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1084`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `metric__a_1093`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1093`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.amount_sum END) AS `metric__a_1094`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1094`,
  MIN(CASE WHEN b.transaction_type = 'Void' THEN b.amount_min END) AS `metric__a_1095`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1095`,
  MAX(CASE WHEN b.transaction_type = 'Void' THEN b.amount_max END) AS `metric__a_1096`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1096`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `metric__a_1105`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1105`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_sum END) AS `metric__a_1106`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1106`,
  MIN(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_min END) AS `metric__a_1107`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1107`,
  MAX(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_max END) AS `metric__a_1108`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1108`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `metric__a_1117`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1117`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_sum END) AS `metric__a_1118`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1118`,
  MIN(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_min END) AS `metric__a_1119`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1119`,
  MAX(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_max END) AS `metric__a_1120`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1120`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `metric__a_1129`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1129`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_sum END) AS `metric__a_1130`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1130`,
  MIN(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_min END) AS `metric__a_1131`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1131`,
  MAX(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_max END) AS `metric__a_1132`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1132`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `metric__a_1141`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1141`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_sum END) AS `metric__a_1142`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1142`,
  MIN(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_min END) AS `metric__a_1143`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1143`,
  MAX(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_max END) AS `metric__a_1144`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1144`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `metric__a_1153`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1153`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_sum END) AS `metric__a_1154`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1154`,
  MIN(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_min END) AS `metric__a_1155`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1155`,
  MAX(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_max END) AS `metric__a_1156`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1156`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `metric__a_1165`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1165`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_sum END) AS `metric__a_1166`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1166`,
  MIN(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_min END) AS `metric__a_1167`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1167`,
  MAX(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_max END) AS `metric__a_1168`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1168`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `metric__a_1177`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1177`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_sum END) AS `metric__a_1178`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1178`,
  MIN(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_min END) AS `metric__a_1179`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1179`,
  MAX(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_max END) AS `metric__a_1180`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1180`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `metric__a_1189`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1189`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_sum END) AS `metric__a_1190`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1190`,
  MIN(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_min END) AS `metric__a_1191`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1191`,
  MAX(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_max END) AS `metric__a_1192`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1192`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `metric__a_1201`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1201`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_sum END) AS `metric__a_1202`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1202`,
  MIN(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_min END) AS `metric__a_1203`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1203`,
  MAX(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_max END) AS `metric__a_1204`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1204`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `metric__a_1213`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1213`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_sum END) AS `metric__a_1214`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1214`,
  MIN(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_min END) AS `metric__a_1215`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1215`,
  MAX(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_max END) AS `metric__a_1216`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1216`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `metric__a_1225`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1225`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_sum END) AS `metric__a_1226`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1226`,
  MIN(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_min END) AS `metric__a_1227`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1227`,
  MAX(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_max END) AS `metric__a_1228`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1228`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `metric__a_1237`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1237`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_sum END) AS `metric__a_1238`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1238`,
  MIN(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_min END) AS `metric__a_1239`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1239`,
  MAX(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_max END) AS `metric__a_1240`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1240`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `metric__a_1249`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1249`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_sum END) AS `metric__a_1250`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1250`,
  MIN(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_min END) AS `metric__a_1251`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1251`,
  MAX(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_max END) AS `metric__a_1252`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1252`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `metric__a_1261`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1261`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.amount_sum END) AS `metric__a_1262`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1262`,
  MIN(CASE WHEN b.transaction_type = 'Return' THEN b.amount_min END) AS `metric__a_1263`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1263`,
  MAX(CASE WHEN b.transaction_type = 'Return' THEN b.amount_max END) AS `metric__a_1264`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1264`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `metric__a_1273`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1273`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_sum END) AS `metric__a_1274`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1274`,
  MIN(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_min END) AS `metric__a_1275`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1275`,
  MAX(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_max END) AS `metric__a_1276`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1276`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `metric__a_1285`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1285`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_sum END) AS `metric__a_1286`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1286`,
  MIN(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_min END) AS `metric__a_1287`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1287`,
  MAX(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_max END) AS `metric__a_1288`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1288`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `metric__a_1297`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1297`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_sum END) AS `metric__a_1298`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1298`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_min END) AS `metric__a_1299`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1299`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_max END) AS `metric__a_1300`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1300`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `metric__a_1309`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1309`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_sum END) AS `metric__a_1310`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1310`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_min END) AS `metric__a_1311`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1311`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_max END) AS `metric__a_1312`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1312`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `metric__a_1321`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1321`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.amount_sum END) AS `metric__a_1322`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1322`,
  MIN(CASE WHEN b.card_type = 'VISA' THEN b.amount_min END) AS `metric__a_1323`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1323`,
  MAX(CASE WHEN b.card_type = 'VISA' THEN b.amount_max END) AS `metric__a_1324`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1324`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `metric__a_1333`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1333`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_sum END) AS `metric__a_1334`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1334`,
  MIN(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_min END) AS `metric__a_1335`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1335`,
  MAX(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_max END) AS `metric__a_1336`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1336`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `metric__a_1345`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1345`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.amount_sum END) AS `metric__a_1346`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1346`,
  MIN(CASE WHEN b.card_type = 'CHECK' THEN b.amount_min END) AS `metric__a_1347`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1347`,
  MAX(CASE WHEN b.card_type = 'CHECK' THEN b.amount_max END) AS `metric__a_1348`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1348`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `metric__a_1357`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1357`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.amount_sum END) AS `metric__a_1358`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1358`,
  MIN(CASE WHEN b.card_type = 'AMEX' THEN b.amount_min END) AS `metric__a_1359`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1359`,
  MAX(CASE WHEN b.card_type = 'AMEX' THEN b.amount_max END) AS `metric__a_1360`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1360`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `metric__a_1369`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1369`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_sum END) AS `metric__a_1370`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1370`,
  MIN(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_min END) AS `metric__a_1371`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1371`,
  MAX(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_max END) AS `metric__a_1372`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1372`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `metric__a_1381`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1381`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.amount_sum END) AS `metric__a_1382`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1382`,
  MIN(CASE WHEN b.card_type = 'DINERS' THEN b.amount_min END) AS `metric__a_1383`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1383`,
  MAX(CASE WHEN b.card_type = 'DINERS' THEN b.amount_max END) AS `metric__a_1384`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1384`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `metric__a_1393`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1393`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.amount_sum END) AS `metric__a_1394`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1394`,
  MIN(CASE WHEN b.card_type = 'JCB' THEN b.amount_min END) AS `metric__a_1395`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1395`,
  MAX(CASE WHEN b.card_type = 'JCB' THEN b.amount_max END) AS `metric__a_1396`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1396`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `metric__a_1405`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1405`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_sum END) AS `metric__a_1406`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1406`,
  MIN(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_min END) AS `metric__a_1407`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1407`,
  MAX(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_max END) AS `metric__a_1408`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1408`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `metric__a_1417`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1417`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_sum END) AS `metric__a_1418`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1418`,
  MIN(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_min END) AS `metric__a_1419`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1419`,
  MAX(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_max END) AS `metric__a_1420`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1420`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `metric__a_1429`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1429`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_sum END) AS `metric__a_1430`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1430`,
  MIN(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_min END) AS `metric__a_1431`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1431`,
  MAX(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_max END) AS `metric__a_1432`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1432`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `metric__a_1441`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1441`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_sum END) AS `metric__a_1442`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1442`,
  MIN(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_min END) AS `metric__a_1443`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1443`,
  MAX(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_max END) AS `metric__a_1444`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1444`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `metric__a_1453`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1453`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_sum END) AS `metric__a_1454`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1454`,
  MIN(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_min END) AS `metric__a_1455`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1455`,
  MAX(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_max END) AS `metric__a_1456`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1456`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `metric__a_1465`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1465`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.amount_sum END) AS `metric__a_1466`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1466`,
  MIN(CASE WHEN b.card_type = 'GIFT' THEN b.amount_min END) AS `metric__a_1467`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1467`,
  MAX(CASE WHEN b.card_type = 'GIFT' THEN b.amount_max END) AS `metric__a_1468`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1468`,
  COUNT(DISTINCT b.card_type) AS `metric__a_1885`,
  COUNT(DISTINCT b.entry_method) AS `metric__a_1886`,
  COUNT(DISTINCT b.mt_gateway) AS `metric__a_1887`
FROM (
  SELECT p.mt_gateway, p.transaction_type, p.card_type, p.entry_method, COUNT(*) AS row_count, SUM(p.amount) AS amount_sum, MIN(p.amount) AS amount_min, MAX(p.amount) AS amount_max
  FROM pmt_txn_fact p
  WHERE p.check_bank_routing_number = %s AND p.event_date >= 1772810055354
  GROUP BY p.mt_gateway, p.transaction_type, p.card_type, p.entry_method
) b
HAVING SUM(b.row_count) > 0;
```

### group_a_bundle_003

- Group/filter/window: `A` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `1d`
- Current best: `12.2ms` setting=`default` scan_sum=`1`
- Best candidate: `group_a_dimension_rollup/distinct_pushdown_hashagg_16_8` `11.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `distinct_pushdown_hashagg_16_8` | 11.2 | 1 | False | not_enough_gain |

### group_a_bundle_004

- Group/filter/window: `A` / `p.merchant_account_number = %s` / `1d`
- Current best: `17.9ms` setting=`hashagg_16_8` scan_sum=`56`
- Best candidate: `group_a_dimension_rollup/default` `17.4ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 17.4 | 56 | False | not_enough_gain |

### group_a_bundle_005

- Group/filter/window: `A` / `p.card_holder_number_sha512 = %s` / `7d`
- Current best: `19.4ms` setting=`default` scan_sum=`8`
- Best candidate: `group_a_dimension_rollup/default` `18.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 18.8 | 8 | False | not_enough_gain |

### group_a_bundle_006

- Group/filter/window: `A` / `p.check_bank_routing_number = %s` / `7d`
- Current best: `491.6ms` setting=`default` scan_sum=`164669`
- Best candidate: `group_a_dimension_rollup/distinct_pushdown` `121.4ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `distinct_pushdown` | 121.4 | 164669 | True | >=10pct_faster |

#### Accepted SQL

```sql
SELECT
  SUM(b.row_count) AS `metric__a_0037`,
  SUM(b.amount_sum) AS `metric__a_0038`,
  MIN(b.amount_min) AS `metric__a_0039`,
  MAX(b.amount_max) AS `metric__a_0040`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `metric__a_0997`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_0997`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_sum END) AS `metric__a_0998`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_0998`,
  MIN(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_min END) AS `metric__a_0999`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_0999`,
  MAX(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.amount_max END) AS `metric__a_1000`,
  SUM(CASE WHEN b.mt_gateway = 'MM-MerchantLink' THEN b.row_count ELSE 0 END) AS `present__a_1000`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `metric__a_1009`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1009`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_sum END) AS `metric__a_1010`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1010`,
  MIN(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_min END) AS `metric__a_1011`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1011`,
  MAX(CASE WHEN b.mt_gateway = 'QBMS' THEN b.amount_max END) AS `metric__a_1012`,
  SUM(CASE WHEN b.mt_gateway = 'QBMS' THEN b.row_count ELSE 0 END) AS `present__a_1012`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `metric__a_1021`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1021`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_sum END) AS `metric__a_1022`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1022`,
  MIN(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_min END) AS `metric__a_1023`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1023`,
  MAX(CASE WHEN b.mt_gateway = 'Direct' THEN b.amount_max END) AS `metric__a_1024`,
  SUM(CASE WHEN b.mt_gateway = 'Direct' THEN b.row_count ELSE 0 END) AS `present__a_1024`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `metric__a_1033`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1033`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_sum END) AS `metric__a_1034`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1034`,
  MIN(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_min END) AS `metric__a_1035`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1035`,
  MAX(CASE WHEN b.mt_gateway = 'PayPal' THEN b.amount_max END) AS `metric__a_1036`,
  SUM(CASE WHEN b.mt_gateway = 'PayPal' THEN b.row_count ELSE 0 END) AS `present__a_1036`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `metric__a_1045`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1045`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_sum END) AS `metric__a_1046`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1046`,
  MIN(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_min END) AS `metric__a_1047`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1047`,
  MAX(CASE WHEN b.mt_gateway = 'Stripe' THEN b.amount_max END) AS `metric__a_1048`,
  SUM(CASE WHEN b.mt_gateway = 'Stripe' THEN b.row_count ELSE 0 END) AS `present__a_1048`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `metric__a_1057`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1057`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_sum END) AS `metric__a_1058`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1058`,
  MIN(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_min END) AS `metric__a_1059`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1059`,
  MAX(CASE WHEN b.mt_gateway = 'Square' THEN b.amount_max END) AS `metric__a_1060`,
  SUM(CASE WHEN b.mt_gateway = 'Square' THEN b.row_count ELSE 0 END) AS `present__a_1060`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `metric__a_1069`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1069`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_sum END) AS `metric__a_1070`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1070`,
  MIN(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_min END) AS `metric__a_1071`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1071`,
  MAX(CASE WHEN b.mt_gateway = 'Braintree' THEN b.amount_max END) AS `metric__a_1072`,
  SUM(CASE WHEN b.mt_gateway = 'Braintree' THEN b.row_count ELSE 0 END) AS `present__a_1072`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `metric__a_1085`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1085`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_sum END) AS `metric__a_1086`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1086`,
  MIN(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_min END) AS `metric__a_1087`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1087`,
  MAX(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_max END) AS `metric__a_1088`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_1088`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `metric__a_1097`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1097`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.amount_sum END) AS `metric__a_1098`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1098`,
  MIN(CASE WHEN b.transaction_type = 'Void' THEN b.amount_min END) AS `metric__a_1099`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1099`,
  MAX(CASE WHEN b.transaction_type = 'Void' THEN b.amount_max END) AS `metric__a_1100`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_1100`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `metric__a_1109`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1109`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_sum END) AS `metric__a_1110`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1110`,
  MIN(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_min END) AS `metric__a_1111`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1111`,
  MAX(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_max END) AS `metric__a_1112`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_1112`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `metric__a_1121`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1121`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_sum END) AS `metric__a_1122`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1122`,
  MIN(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_min END) AS `metric__a_1123`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1123`,
  MAX(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_max END) AS `metric__a_1124`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_1124`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `metric__a_1133`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1133`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_sum END) AS `metric__a_1134`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1134`,
  MIN(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_min END) AS `metric__a_1135`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1135`,
  MAX(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_max END) AS `metric__a_1136`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_1136`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `metric__a_1145`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1145`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_sum END) AS `metric__a_1146`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1146`,
  MIN(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_min END) AS `metric__a_1147`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1147`,
  MAX(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_max END) AS `metric__a_1148`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_1148`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `metric__a_1157`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1157`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_sum END) AS `metric__a_1158`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1158`,
  MIN(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_min END) AS `metric__a_1159`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1159`,
  MAX(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_max END) AS `metric__a_1160`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_1160`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `metric__a_1169`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1169`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_sum END) AS `metric__a_1170`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1170`,
  MIN(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_min END) AS `metric__a_1171`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1171`,
  MAX(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_max END) AS `metric__a_1172`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_1172`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `metric__a_1181`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1181`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_sum END) AS `metric__a_1182`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1182`,
  MIN(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_min END) AS `metric__a_1183`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1183`,
  MAX(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_max END) AS `metric__a_1184`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_1184`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `metric__a_1193`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1193`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_sum END) AS `metric__a_1194`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1194`,
  MIN(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_min END) AS `metric__a_1195`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1195`,
  MAX(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_max END) AS `metric__a_1196`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_1196`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `metric__a_1205`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1205`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_sum END) AS `metric__a_1206`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1206`,
  MIN(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_min END) AS `metric__a_1207`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1207`,
  MAX(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_max END) AS `metric__a_1208`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_1208`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `metric__a_1217`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1217`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_sum END) AS `metric__a_1218`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1218`,
  MIN(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_min END) AS `metric__a_1219`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1219`,
  MAX(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_max END) AS `metric__a_1220`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_1220`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `metric__a_1229`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1229`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_sum END) AS `metric__a_1230`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1230`,
  MIN(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_min END) AS `metric__a_1231`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1231`,
  MAX(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_max END) AS `metric__a_1232`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_1232`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `metric__a_1241`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1241`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_sum END) AS `metric__a_1242`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1242`,
  MIN(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_min END) AS `metric__a_1243`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1243`,
  MAX(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_max END) AS `metric__a_1244`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_1244`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `metric__a_1253`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1253`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_sum END) AS `metric__a_1254`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1254`,
  MIN(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_min END) AS `metric__a_1255`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1255`,
  MAX(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_max END) AS `metric__a_1256`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_1256`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `metric__a_1265`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1265`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.amount_sum END) AS `metric__a_1266`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1266`,
  MIN(CASE WHEN b.transaction_type = 'Return' THEN b.amount_min END) AS `metric__a_1267`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1267`,
  MAX(CASE WHEN b.transaction_type = 'Return' THEN b.amount_max END) AS `metric__a_1268`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_1268`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `metric__a_1277`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1277`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_sum END) AS `metric__a_1278`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1278`,
  MIN(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_min END) AS `metric__a_1279`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1279`,
  MAX(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_max END) AS `metric__a_1280`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_1280`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `metric__a_1289`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1289`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_sum END) AS `metric__a_1290`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1290`,
  MIN(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_min END) AS `metric__a_1291`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1291`,
  MAX(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_max END) AS `metric__a_1292`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_1292`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `metric__a_1301`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1301`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_sum END) AS `metric__a_1302`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1302`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_min END) AS `metric__a_1303`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1303`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_max END) AS `metric__a_1304`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_1304`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `metric__a_1313`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1313`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_sum END) AS `metric__a_1314`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1314`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_min END) AS `metric__a_1315`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1315`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_max END) AS `metric__a_1316`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_1316`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `metric__a_1325`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1325`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.amount_sum END) AS `metric__a_1326`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1326`,
  MIN(CASE WHEN b.card_type = 'VISA' THEN b.amount_min END) AS `metric__a_1327`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1327`,
  MAX(CASE WHEN b.card_type = 'VISA' THEN b.amount_max END) AS `metric__a_1328`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_1328`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `metric__a_1337`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1337`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_sum END) AS `metric__a_1338`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1338`,
  MIN(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_min END) AS `metric__a_1339`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1339`,
  MAX(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_max END) AS `metric__a_1340`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_1340`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `metric__a_1349`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1349`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.amount_sum END) AS `metric__a_1350`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1350`,
  MIN(CASE WHEN b.card_type = 'CHECK' THEN b.amount_min END) AS `metric__a_1351`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1351`,
  MAX(CASE WHEN b.card_type = 'CHECK' THEN b.amount_max END) AS `metric__a_1352`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_1352`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `metric__a_1361`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1361`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.amount_sum END) AS `metric__a_1362`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1362`,
  MIN(CASE WHEN b.card_type = 'AMEX' THEN b.amount_min END) AS `metric__a_1363`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1363`,
  MAX(CASE WHEN b.card_type = 'AMEX' THEN b.amount_max END) AS `metric__a_1364`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_1364`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `metric__a_1373`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1373`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_sum END) AS `metric__a_1374`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1374`,
  MIN(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_min END) AS `metric__a_1375`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1375`,
  MAX(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_max END) AS `metric__a_1376`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_1376`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `metric__a_1385`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1385`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.amount_sum END) AS `metric__a_1386`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1386`,
  MIN(CASE WHEN b.card_type = 'DINERS' THEN b.amount_min END) AS `metric__a_1387`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1387`,
  MAX(CASE WHEN b.card_type = 'DINERS' THEN b.amount_max END) AS `metric__a_1388`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_1388`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `metric__a_1397`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1397`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.amount_sum END) AS `metric__a_1398`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1398`,
  MIN(CASE WHEN b.card_type = 'JCB' THEN b.amount_min END) AS `metric__a_1399`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1399`,
  MAX(CASE WHEN b.card_type = 'JCB' THEN b.amount_max END) AS `metric__a_1400`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_1400`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `metric__a_1409`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1409`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_sum END) AS `metric__a_1410`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1410`,
  MIN(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_min END) AS `metric__a_1411`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1411`,
  MAX(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_max END) AS `metric__a_1412`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_1412`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `metric__a_1421`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1421`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_sum END) AS `metric__a_1422`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1422`,
  MIN(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_min END) AS `metric__a_1423`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1423`,
  MAX(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_max END) AS `metric__a_1424`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_1424`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `metric__a_1433`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1433`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_sum END) AS `metric__a_1434`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1434`,
  MIN(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_min END) AS `metric__a_1435`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1435`,
  MAX(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_max END) AS `metric__a_1436`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_1436`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `metric__a_1445`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1445`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_sum END) AS `metric__a_1446`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1446`,
  MIN(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_min END) AS `metric__a_1447`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1447`,
  MAX(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_max END) AS `metric__a_1448`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_1448`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `metric__a_1457`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1457`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_sum END) AS `metric__a_1458`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1458`,
  MIN(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_min END) AS `metric__a_1459`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1459`,
  MAX(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_max END) AS `metric__a_1460`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_1460`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `metric__a_1469`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1469`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.amount_sum END) AS `metric__a_1470`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1470`,
  MIN(CASE WHEN b.card_type = 'GIFT' THEN b.amount_min END) AS `metric__a_1471`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1471`,
  MAX(CASE WHEN b.card_type = 'GIFT' THEN b.amount_max END) AS `metric__a_1472`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_1472`,
  COUNT(DISTINCT b.card_type) AS `metric__a_1888`,
  COUNT(DISTINCT b.entry_method) AS `metric__a_1889`,
  COUNT(DISTINCT b.mt_gateway) AS `metric__a_1890`
FROM (
  SELECT p.mt_gateway, p.transaction_type, p.card_type, p.entry_method, COUNT(*) AS row_count, SUM(p.amount) AS amount_sum, MIN(p.amount) AS amount_min, MAX(p.amount) AS amount_max
  FROM pmt_txn_fact p
  WHERE p.check_bank_routing_number = %s AND p.event_date >= 1772291655354
  GROUP BY p.mt_gateway, p.transaction_type, p.card_type, p.entry_method
) b
HAVING SUM(b.row_count) > 0;
```

### group_a_bundle_007

- Group/filter/window: `A` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `7d`
- Current best: `12.3ms` setting=`hashagg_16_8` scan_sum=`1`
- Best candidate: `group_a_dimension_rollup/default` `11.6ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 11.6 | 1 | False | not_enough_gain |

### group_a_bundle_008

- Group/filter/window: `A` / `p.merchant_account_number = %s` / `7d`
- Current best: `19.3ms` setting=`hashagg_16_8` scan_sum=`58`
- Best candidate: `group_a_dimension_rollup/distinct_pushdown` `18.4ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `distinct_pushdown` | 18.4 | 58 | False | not_enough_gain |

### group_a_bundle_009

- Group/filter/window: `A` / `p.card_holder_number_sha512 = %s` / `30d`
- Current best: `21.3ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`35`
- Best candidate: `group_a_dimension_rollup/distinct_pushdown` `20.7ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `distinct_pushdown` | 20.7 | 35 | False | not_enough_gain |

### group_a_bundle_010

- Group/filter/window: `A` / `p.check_bank_routing_number = %s` / `30d`
- Current best: `84.8ms` setting=`default` scan_sum=`146847`
- Best candidate: `group_a_dimension_rollup/distinct_pushdown` `84.1ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `distinct_pushdown` | 84.1 | 146847 | False | not_enough_gain |

### group_a_bundle_011

- Group/filter/window: `A` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `30d`
- Current best: `8.0ms` setting=`distinct_pushdown` scan_sum=`1`
- Best candidate: `group_a_dimension_rollup/distinct_pushdown` `7.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `distinct_pushdown` | 7.8 | 1 | False | not_enough_gain |

### group_a_bundle_012

- Group/filter/window: `A` / `p.merchant_account_number = %s` / `30d`
- Current best: `120.6ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`31300`
- Best candidate: `group_a_dimension_rollup/default` `30.8ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 30.8 | 31300 | True | >=10pct_faster |

#### Accepted SQL

```sql
SELECT
  SUM(b.row_count) AS `metric__a_0009`,
  SUM(b.amount_sum) AS `metric__a_0010`,
  MIN(b.amount_min) AS `metric__a_0011`,
  MAX(b.amount_max) AS `metric__a_0012`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `metric__a_0073`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_0073`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_sum END) AS `metric__a_0074`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_0074`,
  MIN(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_min END) AS `metric__a_0075`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_0075`,
  MAX(CASE WHEN b.transaction_type = 'Sale' THEN b.amount_max END) AS `metric__a_0076`,
  SUM(CASE WHEN b.transaction_type = 'Sale' THEN b.row_count ELSE 0 END) AS `present__a_0076`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `metric__a_0089`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_0089`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.amount_sum END) AS `metric__a_0090`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_0090`,
  MIN(CASE WHEN b.transaction_type = 'Void' THEN b.amount_min END) AS `metric__a_0091`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_0091`,
  MAX(CASE WHEN b.transaction_type = 'Void' THEN b.amount_max END) AS `metric__a_0092`,
  SUM(CASE WHEN b.transaction_type = 'Void' THEN b.row_count ELSE 0 END) AS `present__a_0092`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `metric__a_0105`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_0105`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_sum END) AS `metric__a_0106`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_0106`,
  MIN(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_min END) AS `metric__a_0107`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_0107`,
  MAX(CASE WHEN b.transaction_type = 'Refund' THEN b.amount_max END) AS `metric__a_0108`,
  SUM(CASE WHEN b.transaction_type = 'Refund' THEN b.row_count ELSE 0 END) AS `present__a_0108`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `metric__a_0121`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_0121`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_sum END) AS `metric__a_0122`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_0122`,
  MIN(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_min END) AS `metric__a_0123`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_0123`,
  MAX(CASE WHEN b.transaction_type = 'Auth' THEN b.amount_max END) AS `metric__a_0124`,
  SUM(CASE WHEN b.transaction_type = 'Auth' THEN b.row_count ELSE 0 END) AS `present__a_0124`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `metric__a_0137`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_0137`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_sum END) AS `metric__a_0138`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_0138`,
  MIN(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_min END) AS `metric__a_0139`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_0139`,
  MAX(CASE WHEN b.transaction_type = 'Capture' THEN b.amount_max END) AS `metric__a_0140`,
  SUM(CASE WHEN b.transaction_type = 'Capture' THEN b.row_count ELSE 0 END) AS `present__a_0140`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `metric__a_0153`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_0153`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_sum END) AS `metric__a_0154`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_0154`,
  MIN(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_min END) AS `metric__a_0155`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_0155`,
  MAX(CASE WHEN b.transaction_type = 'Reversal' THEN b.amount_max END) AS `metric__a_0156`,
  SUM(CASE WHEN b.transaction_type = 'Reversal' THEN b.row_count ELSE 0 END) AS `present__a_0156`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `metric__a_0169`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_0169`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_sum END) AS `metric__a_0170`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_0170`,
  MIN(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_min END) AS `metric__a_0171`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_0171`,
  MAX(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.amount_max END) AS `metric__a_0172`,
  SUM(CASE WHEN b.transaction_type = 'CAPTURE_ORDER' THEN b.row_count ELSE 0 END) AS `present__a_0172`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `metric__a_0185`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_0185`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_sum END) AS `metric__a_0186`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_0186`,
  MIN(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_min END) AS `metric__a_0187`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_0187`,
  MAX(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.amount_max END) AS `metric__a_0188`,
  SUM(CASE WHEN b.transaction_type = 'EMV_Advice' THEN b.row_count ELSE 0 END) AS `present__a_0188`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `metric__a_0201`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_0201`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_sum END) AS `metric__a_0202`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_0202`,
  MIN(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_min END) AS `metric__a_0203`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_0203`,
  MAX(CASE WHEN b.transaction_type = 'Adjustment' THEN b.amount_max END) AS `metric__a_0204`,
  SUM(CASE WHEN b.transaction_type = 'Adjustment' THEN b.row_count ELSE 0 END) AS `present__a_0204`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `metric__a_0217`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_0217`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_sum END) AS `metric__a_0218`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_0218`,
  MIN(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_min END) AS `metric__a_0219`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_0219`,
  MAX(CASE WHEN b.transaction_type = 'Credit' THEN b.amount_max END) AS `metric__a_0220`,
  SUM(CASE WHEN b.transaction_type = 'Credit' THEN b.row_count ELSE 0 END) AS `present__a_0220`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `metric__a_0233`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_0233`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_sum END) AS `metric__a_0234`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_0234`,
  MIN(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_min END) AS `metric__a_0235`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_0235`,
  MAX(CASE WHEN b.transaction_type = 'Debit' THEN b.amount_max END) AS `metric__a_0236`,
  SUM(CASE WHEN b.transaction_type = 'Debit' THEN b.row_count ELSE 0 END) AS `present__a_0236`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `metric__a_0249`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_0249`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_sum END) AS `metric__a_0250`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_0250`,
  MIN(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_min END) AS `metric__a_0251`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_0251`,
  MAX(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.amount_max END) AS `metric__a_0252`,
  SUM(CASE WHEN b.transaction_type = 'AuthOnly' THEN b.row_count ELSE 0 END) AS `present__a_0252`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `metric__a_0265`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_0265`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_sum END) AS `metric__a_0266`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_0266`,
  MIN(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_min END) AS `metric__a_0267`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_0267`,
  MAX(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.amount_max END) AS `metric__a_0268`,
  SUM(CASE WHEN b.transaction_type = 'CaptureOnly' THEN b.row_count ELSE 0 END) AS `present__a_0268`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `metric__a_0281`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_0281`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_sum END) AS `metric__a_0282`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_0282`,
  MIN(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_min END) AS `metric__a_0283`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_0283`,
  MAX(CASE WHEN b.transaction_type = 'PostAuth' THEN b.amount_max END) AS `metric__a_0284`,
  SUM(CASE WHEN b.transaction_type = 'PostAuth' THEN b.row_count ELSE 0 END) AS `present__a_0284`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `metric__a_0297`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_0297`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_sum END) AS `metric__a_0298`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_0298`,
  MIN(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_min END) AS `metric__a_0299`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_0299`,
  MAX(CASE WHEN b.transaction_type = 'PreAuth' THEN b.amount_max END) AS `metric__a_0300`,
  SUM(CASE WHEN b.transaction_type = 'PreAuth' THEN b.row_count ELSE 0 END) AS `present__a_0300`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `metric__a_0313`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_0313`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.amount_sum END) AS `metric__a_0314`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_0314`,
  MIN(CASE WHEN b.transaction_type = 'Return' THEN b.amount_min END) AS `metric__a_0315`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_0315`,
  MAX(CASE WHEN b.transaction_type = 'Return' THEN b.amount_max END) AS `metric__a_0316`,
  SUM(CASE WHEN b.transaction_type = 'Return' THEN b.row_count ELSE 0 END) AS `present__a_0316`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `metric__a_0329`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_0329`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_sum END) AS `metric__a_0330`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_0330`,
  MIN(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_min END) AS `metric__a_0331`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_0331`,
  MAX(CASE WHEN b.transaction_type = 'Chargeback' THEN b.amount_max END) AS `metric__a_0332`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' THEN b.row_count ELSE 0 END) AS `present__a_0332`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `metric__a_0345`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_0345`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_sum END) AS `metric__a_0346`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_0346`,
  MIN(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_min END) AS `metric__a_0347`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_0347`,
  MAX(CASE WHEN b.transaction_type = 'Dispute' THEN b.amount_max END) AS `metric__a_0348`,
  SUM(CASE WHEN b.transaction_type = 'Dispute' THEN b.row_count ELSE 0 END) AS `present__a_0348`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `metric__a_0361`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_0361`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_sum END) AS `metric__a_0362`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_0362`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_min END) AS `metric__a_0363`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_0363`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.amount_max END) AS `metric__a_0364`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_NSF' THEN b.row_count ELSE 0 END) AS `present__a_0364`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `metric__a_0377`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_0377`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_sum END) AS `metric__a_0378`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_0378`,
  MIN(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_min END) AS `metric__a_0379`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_0379`,
  MAX(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.amount_max END) AS `metric__a_0380`,
  SUM(CASE WHEN b.transaction_type = 'Reversal_Timeout' THEN b.row_count ELSE 0 END) AS `present__a_0380`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `metric__a_0393`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_0393`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.amount_sum END) AS `metric__a_0394`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_0394`,
  MIN(CASE WHEN b.card_type = 'VISA' THEN b.amount_min END) AS `metric__a_0395`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_0395`,
  MAX(CASE WHEN b.card_type = 'VISA' THEN b.amount_max END) AS `metric__a_0396`,
  SUM(CASE WHEN b.card_type = 'VISA' THEN b.row_count ELSE 0 END) AS `present__a_0396`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `metric__a_0405`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_0405`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_sum END) AS `metric__a_0406`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_0406`,
  MIN(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_min END) AS `metric__a_0407`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_0407`,
  MAX(CASE WHEN b.card_type = 'MASTERCARD' THEN b.amount_max END) AS `metric__a_0408`,
  SUM(CASE WHEN b.card_type = 'MASTERCARD' THEN b.row_count ELSE 0 END) AS `present__a_0408`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `metric__a_0417`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_0417`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.amount_sum END) AS `metric__a_0418`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_0418`,
  MIN(CASE WHEN b.card_type = 'CHECK' THEN b.amount_min END) AS `metric__a_0419`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_0419`,
  MAX(CASE WHEN b.card_type = 'CHECK' THEN b.amount_max END) AS `metric__a_0420`,
  SUM(CASE WHEN b.card_type = 'CHECK' THEN b.row_count ELSE 0 END) AS `present__a_0420`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `metric__a_0429`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_0429`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.amount_sum END) AS `metric__a_0430`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_0430`,
  MIN(CASE WHEN b.card_type = 'AMEX' THEN b.amount_min END) AS `metric__a_0431`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_0431`,
  MAX(CASE WHEN b.card_type = 'AMEX' THEN b.amount_max END) AS `metric__a_0432`,
  SUM(CASE WHEN b.card_type = 'AMEX' THEN b.row_count ELSE 0 END) AS `present__a_0432`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `metric__a_0441`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_0441`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_sum END) AS `metric__a_0442`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_0442`,
  MIN(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_min END) AS `metric__a_0443`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_0443`,
  MAX(CASE WHEN b.card_type = 'DISCOVER' THEN b.amount_max END) AS `metric__a_0444`,
  SUM(CASE WHEN b.card_type = 'DISCOVER' THEN b.row_count ELSE 0 END) AS `present__a_0444`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `metric__a_0453`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_0453`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.amount_sum END) AS `metric__a_0454`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_0454`,
  MIN(CASE WHEN b.card_type = 'DINERS' THEN b.amount_min END) AS `metric__a_0455`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_0455`,
  MAX(CASE WHEN b.card_type = 'DINERS' THEN b.amount_max END) AS `metric__a_0456`,
  SUM(CASE WHEN b.card_type = 'DINERS' THEN b.row_count ELSE 0 END) AS `present__a_0456`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `metric__a_0465`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_0465`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.amount_sum END) AS `metric__a_0466`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_0466`,
  MIN(CASE WHEN b.card_type = 'JCB' THEN b.amount_min END) AS `metric__a_0467`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_0467`,
  MAX(CASE WHEN b.card_type = 'JCB' THEN b.amount_max END) AS `metric__a_0468`,
  SUM(CASE WHEN b.card_type = 'JCB' THEN b.row_count ELSE 0 END) AS `present__a_0468`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `metric__a_0477`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_0477`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_sum END) AS `metric__a_0478`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_0478`,
  MIN(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_min END) AS `metric__a_0479`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_0479`,
  MAX(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.amount_max END) AS `metric__a_0480`,
  SUM(CASE WHEN b.card_type = 'CARTE_BLANCHE' THEN b.row_count ELSE 0 END) AS `present__a_0480`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `metric__a_0489`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_0489`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_sum END) AS `metric__a_0490`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_0490`,
  MIN(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_min END) AS `metric__a_0491`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_0491`,
  MAX(CASE WHEN b.card_type = 'UNKNOWN' THEN b.amount_max END) AS `metric__a_0492`,
  SUM(CASE WHEN b.card_type = 'UNKNOWN' THEN b.row_count ELSE 0 END) AS `present__a_0492`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `metric__a_0501`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_0501`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_sum END) AS `metric__a_0502`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_0502`,
  MIN(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_min END) AS `metric__a_0503`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_0503`,
  MAX(CASE WHEN b.card_type = 'DEBIT' THEN b.amount_max END) AS `metric__a_0504`,
  SUM(CASE WHEN b.card_type = 'DEBIT' THEN b.row_count ELSE 0 END) AS `present__a_0504`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `metric__a_0513`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_0513`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_sum END) AS `metric__a_0514`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_0514`,
  MIN(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_min END) AS `metric__a_0515`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_0515`,
  MAX(CASE WHEN b.card_type = 'CREDIT' THEN b.amount_max END) AS `metric__a_0516`,
  SUM(CASE WHEN b.card_type = 'CREDIT' THEN b.row_count ELSE 0 END) AS `present__a_0516`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `metric__a_0525`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_0525`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_sum END) AS `metric__a_0526`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_0526`,
  MIN(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_min END) AS `metric__a_0527`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_0527`,
  MAX(CASE WHEN b.card_type = 'PREPAID' THEN b.amount_max END) AS `metric__a_0528`,
  SUM(CASE WHEN b.card_type = 'PREPAID' THEN b.row_count ELSE 0 END) AS `present__a_0528`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `metric__a_0537`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_0537`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.amount_sum END) AS `metric__a_0538`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_0538`,
  MIN(CASE WHEN b.card_type = 'GIFT' THEN b.amount_min END) AS `metric__a_0539`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_0539`,
  MAX(CASE WHEN b.card_type = 'GIFT' THEN b.amount_max END) AS `metric__a_0540`,
  SUM(CASE WHEN b.card_type = 'GIFT' THEN b.row_count ELSE 0 END) AS `present__a_0540`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `metric__a_1733`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1733`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'KEYED' THEN b.amount_sum END) AS `metric__a_1734`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1734`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `metric__a_1745`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1745`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'ECOM' THEN b.amount_sum END) AS `metric__a_1746`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1746`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CHIP' THEN b.row_count ELSE 0 END) AS `metric__a_1757`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CHIP' THEN b.row_count ELSE 0 END) AS `present__a_1757`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CHIP' THEN b.amount_sum END) AS `metric__a_1758`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CHIP' THEN b.row_count ELSE 0 END) AS `present__a_1758`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CONTACTLESS' THEN b.row_count ELSE 0 END) AS `metric__a_1769`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CONTACTLESS' THEN b.row_count ELSE 0 END) AS `present__a_1769`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CONTACTLESS' THEN b.amount_sum END) AS `metric__a_1770`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'CONTACTLESS' THEN b.row_count ELSE 0 END) AS `present__a_1770`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'SWIPED' THEN b.row_count ELSE 0 END) AS `metric__a_1781`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'SWIPED' THEN b.row_count ELSE 0 END) AS `present__a_1781`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'SWIPED' THEN b.amount_sum END) AS `metric__a_1782`,
  SUM(CASE WHEN b.transaction_type = 'Sale' AND b.entry_method = 'SWIPED' THEN b.row_count ELSE 0 END) AS `present__a_1782`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `metric__a_1793`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1793`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'KEYED' THEN b.amount_sum END) AS `metric__a_1794`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1794`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `metric__a_1805`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1805`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'ECOM' THEN b.amount_sum END) AS `metric__a_1806`,
  SUM(CASE WHEN b.transaction_type = 'Refund' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1806`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `metric__a_1817`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1817`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'KEYED' THEN b.amount_sum END) AS `metric__a_1818`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1818`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `metric__a_1829`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1829`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'ECOM' THEN b.amount_sum END) AS `metric__a_1830`,
  SUM(CASE WHEN b.transaction_type = 'Auth' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1830`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `metric__a_1841`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1841`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'KEYED' THEN b.amount_sum END) AS `metric__a_1842`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'KEYED' THEN b.row_count ELSE 0 END) AS `present__a_1842`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `metric__a_1853`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1853`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'ECOM' THEN b.amount_sum END) AS `metric__a_1854`,
  SUM(CASE WHEN b.transaction_type = 'Chargeback' AND b.entry_method = 'ECOM' THEN b.row_count ELSE 0 END) AS `present__a_1854`,
  COUNT(DISTINCT b.card_type) AS `metric__a_1867`,
  COUNT(DISTINCT b.entry_method) AS `metric__a_1868`,
  COUNT(DISTINCT b.mt_gateway) AS `metric__a_1869`
FROM (
  SELECT p.mt_gateway, p.transaction_type, p.card_type, p.entry_method, COUNT(*) AS row_count, SUM(p.amount) AS amount_sum, MIN(p.amount) AS amount_min, MAX(p.amount) AS amount_max
  FROM pmt_txn_fact p
  WHERE p.merchant_account_number = %s AND p.event_date >= 1770304455354
  GROUP BY p.mt_gateway, p.transaction_type, p.card_type, p.entry_method
) b
HAVING SUM(b.row_count) > 0;
```

### group_a_bundle_013

- Group/filter/window: `A` / `p.card_holder_number_sha512 = %s` / `90d`
- Current best: `3.0ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`60`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_a_bundle_014

- Group/filter/window: `A` / `p.check_bank_routing_number = %s` / `90d`
- Current best: `5.5ms` setting=`distinct_pushdown` scan_sum=`1497`
- Best candidate: `group_a_dimension_rollup/default` `5.6ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 5.6 | 1497 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown_hashagg_16_8` | 121.3 | 89821 | False | not_enough_gain |

### group_a_bundle_015

- Group/filter/window: `A` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `90d`
- Current best: `3.1ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`1`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_a_bundle_016

- Group/filter/window: `A` / `p.merchant_account_number = %s` / `90d`
- Current best: `10.1ms` setting=`distinct_pushdown` scan_sum=`135`
- Best candidate: `group_a_dimension_rollup/default` `9.5ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_a_dimension_rollup` | True | `default` | 9.5 | 135 | False | not_enough_gain |

### group_a_bundle_017

- Group/filter/window: `A` / `p.card_holder_number_sha512 = %s` / `180d`
- Current best: `5.0ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`150`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_a_bundle_018

- Group/filter/window: `A` / `p.check_bank_routing_number = %s` / `180d`
- Current best: `6.6ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`1151`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_a_bundle_019

- Group/filter/window: `A` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `180d`
- Current best: `5.0ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`2`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_a_bundle_020

- Group/filter/window: `A` / `p.merchant_account_number = %s` / `180d`
- Current best: `5.3ms` setting=`distinct_pushdown` scan_sum=`360`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_001

- Group/filter/window: `B` / `d.exact_id = %s` / `1d`
- Current best: `80.6ms` setting=`hashagg_16_8` scan_sum=`30934`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown_hashagg_16_8` `572.0ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.5 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown_hashagg_16_8` | 572.0 | 1546701 | False | not_enough_gain |

### group_b_bundle_002

- Group/filter/window: `B` / `d.input_ip = %s` / `1d`
- Current best: `167.9ms` setting=`hashagg_16_8` scan_sum=`101018`
- Best candidate: `filtered_scalar_subqueries/hashagg_16_8` `1858.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.2 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `hashagg_16_8` | 1858.2 | 3939703 | False | not_enough_gain |

### group_b_bundle_003

- Group/filter/window: `B` / `d.smart_id = %s` / `1d`
- Current best: `388.4ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`132338`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown` `2168.4ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.4 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 2168.4 | 3506958 | False | not_enough_gain |

### group_b_bundle_004

- Group/filter/window: `B` / `d.true_ip = %s` / `1d`
- Current best: `209.4ms` setting=`hashagg_16_8` scan_sum=`124246`
- Best candidate: `group_b_numeric_projection/agg_pushdown_hashagg_16_8` `211.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | True | `agg_pushdown_hashagg_16_8` | 211.8 | 124246 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 2337.5 | 4969841 | False | not_enough_gain |

### group_b_bundle_005

- Group/filter/window: `B` / `d.exact_id = %s` / `7d`
- Current best: `7.6ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`149`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown` `143.1ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.4 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 143.1 | 7451 | False | not_enough_gain |

### group_b_bundle_006

- Group/filter/window: `B` / `d.input_ip = %s` / `7d`
- Current best: `222.9ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`135157`
- Best candidate: `filtered_scalar_subqueries/hashagg_16_8` `2635.7ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.1 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `hashagg_16_8` | 2635.7 | 5271124 | False | not_enough_gain |

### group_b_bundle_007

- Group/filter/window: `B` / `d.smart_id = %s` / `7d`
- Current best: `205.2ms` setting=`hashagg_16_8` scan_sum=`83442`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown` `2348.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.6 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 2348.2 | 4088659 | False | not_enough_gain |

### group_b_bundle_008

- Group/filter/window: `B` / `d.true_ip = %s` / `7d`
- Current best: `258.6ms` setting=`hashagg_16_8` scan_sum=`158299`
- Best candidate: `group_b_numeric_projection/hashagg_16_8` `258.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | True | `hashagg_16_8` | 258.8 | 158299 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `agg_pushdown_hashagg_16_8` | 5012.1 | 6331961 | False | not_enough_gain |

### group_b_bundle_009

- Group/filter/window: `B` / `d.exact_id = %s` / `30d`
- Current best: `89.5ms` setting=`default` scan_sum=`35472`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown` `577.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.7 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 577.2 | 1773601 | False | not_enough_gain |

### group_b_bundle_010

- Group/filter/window: `B` / `d.input_ip = %s` / `30d`
- Current best: `717.5ms` setting=`default` scan_sum=`240067`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown` `8908.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.4 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 8908.8 | 9362614 | False | not_enough_gain |

### group_b_bundle_011

- Group/filter/window: `B` / `d.smart_id = %s` / `30d`
- Current best: `444.5ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`149175`
- Best candidate: `filtered_scalar_subqueries/distinct_pushdown_hashagg_16_8` `6132.7ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | False | `default` | 2.5 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown_hashagg_16_8` | 6132.7 | 7309576 | False | not_enough_gain |

### group_b_bundle_012

- Group/filter/window: `B` / `d.true_ip = %s` / `30d`
- Current best: `705.3ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`278963`
- Best candidate: `group_b_numeric_projection/default` `711.3ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_b_numeric_projection` | True | `default` | 711.3 | 278963 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 9168.4 | 11158521 | False | not_enough_gain |

### group_b_bundle_013

- Group/filter/window: `B` / `d.exact_id = %s` / `90d`
- Current best: `3.1ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`423`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_014

- Group/filter/window: `B` / `d.input_ip = %s` / `90d`
- Current best: `81.7ms` setting=`hashagg_16_8` scan_sum=`559237`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_015

- Group/filter/window: `B` / `d.smart_id = %s` / `90d`
- Current best: `3.1ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`482`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_016

- Group/filter/window: `B` / `d.true_ip = %s` / `90d`
- Current best: `3.2ms` setting=`hashagg_16_8` scan_sum=`1007`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_017

- Group/filter/window: `B` / `d.exact_id = %s` / `180d`
- Current best: `8.1ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`1551`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_018

- Group/filter/window: `B` / `d.input_ip = %s` / `180d`
- Current best: `610.8ms` setting=`hashagg_16_8` scan_sum=`768288`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_019

- Group/filter/window: `B` / `d.smart_id = %s` / `180d`
- Current best: `659.7ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`768780`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_b_bundle_020

- Group/filter/window: `B` / `d.true_ip = %s` / `180d`
- Current best: `1023.8ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`1559443`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_c_bundle_001

- Group/filter/window: `C` / `d.exact_id = %s` / `1d`
- Current best: `7.5ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`115`
- Best candidate: `group_c_device_first_join/hashagg_16_8` `7.3ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 7.3 | 115 | False | not_enough_gain |
| `group_c_device_first_join` | True | `hashagg_16_8` | 7.3 | 115 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 204.9 | 4460 | False | not_enough_gain |

### group_c_bundle_002

- Group/filter/window: `C` / `d.input_ip = %s` / `1d`
- Current best: `351.6ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`102586`
- Best candidate: `group_c_device_first_join/distinct_pushdown` `188.6ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `hashagg_16_8` | 217.5 | 102586 | True | >=10pct_faster |
| `group_c_device_first_join` | True | `distinct_pushdown` | 188.6 | 102586 | True | >=10pct_faster |

#### Accepted SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0073`,
  SUM(p.amount) AS `metric__c_0074`,
  MIN(p.amount) AS `metric__c_0075`,
  MAX(p.amount) AS `metric__c_0076`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0077`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0078`,
  COUNT(DISTINCT(p.card_type)) AS `metric__c_0079`
FROM deviceprofile_fact d
JOIN pmt_txn_fact p
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.input_ip = %s AND d.jms_timestamp >= '2026-03-24 09:55:35.825000'
  AND p.event_date >= 1774346135825
HAVING COUNT(*) > 0;
```

### group_c_bundle_003

- Group/filter/window: `C` / `d.smart_id = %s` / `1d`
- Current best: `165.6ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`65884`
- Best candidate: `group_c_device_first_join/agg_pushdown_hashagg_16_8` `146.6ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 147.3 | 65884 | True | >=10pct_faster |
| `group_c_device_first_join` | True | `agg_pushdown_hashagg_16_8` | 146.6 | 65884 | True | >=10pct_faster |
| `filtered_scalar_subqueries` | True | `distinct_pushdown_hashagg_16_8` | 3057.4 | 1382459 | False | not_enough_gain |

#### Accepted SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0041`,
  SUM(p.amount) AS `metric__c_0042`,
  MIN(p.amount) AS `metric__c_0043`,
  MAX(p.amount) AS `metric__c_0044`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0045`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0046`,
  COUNT(DISTINCT(p.card_type)) AS `metric__c_0047`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__c_0048`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__c_0172`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0172`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__c_0173`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0173`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__c_0178`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0178`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__c_0179`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0179`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__c_0184`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0184`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__c_0185`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0185`
FROM deviceprofile_fact d
JOIN pmt_txn_fact p
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.smart_id = %s AND d.jms_timestamp >= '2026-03-19 13:16:13.509000'
  AND p.event_date >= 1773926173509
HAVING COUNT(*) > 0;
```

### group_c_bundle_004

- Group/filter/window: `C` / `d.true_ip = %s` / `1d`
- Current best: `205.7ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`114456`
- Best candidate: `group_c_device_first_join/distinct_pushdown` `192.7ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown` | 197.4 | 114456 | False | not_enough_gain |
| `group_c_device_first_join` | True | `distinct_pushdown` | 192.7 | 114456 | False | not_enough_gain |

### group_c_bundle_005

- Group/filter/window: `C` / `p.card_holder_number_sha512 = %s` / `1d`
- Current best: `8.1ms` setting=`distinct_pushdown` scan_sum=`46`
- Best candidate: `group_c_inner_join/default` `8.1ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `default` | 8.1 | 46 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 96.8 | 751 | False | not_enough_gain |

### group_c_bundle_006

- Group/filter/window: `C` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `1d`
- Current best: `5.8ms` setting=`distinct_pushdown` scan_sum=`3`
- Best candidate: `group_c_inner_join/default` `5.6ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `default` | 5.6 | 3 | False | not_enough_gain |

### group_c_bundle_007

- Group/filter/window: `C` / `p.merchant_account_number = %s` / `1d`
- Current best: `212.6ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`23925`
- Best candidate: `group_c_inner_join/hashagg_16_8` `209.4ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `hashagg_16_8` | 209.4 | 23925 | False | not_enough_gain |
| `group_c_numeric_projection` | False | `default` | 3.1 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `hashagg_16_8` | 2839.2 | 1019851 | False | not_enough_gain |

### group_c_bundle_008

- Group/filter/window: `C` / `d.exact_id = %s` / `7d`
- Current best: `7.1ms` setting=`hashagg_16_8` scan_sum=`59`
- Best candidate: `group_c_device_first_join/default` `7.0ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 7.3 | 59 | False | not_enough_gain |
| `group_c_device_first_join` | True | `default` | 7.0 | 59 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 195.7 | 2297 | False | not_enough_gain |

### group_c_bundle_009

- Group/filter/window: `C` / `d.input_ip = %s` / `7d`
- Current best: `231.9ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`137963`
- Best candidate: `group_c_device_first_join/default` `212.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 212.3 | 137963 | False | not_enough_gain |
| `group_c_device_first_join` | True | `default` | 212.2 | 137963 | False | not_enough_gain |

### group_c_bundle_010

- Group/filter/window: `C` / `d.smart_id = %s` / `7d`
- Current best: `165.2ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`83013`
- Best candidate: `group_c_device_first_join/distinct_pushdown_hashagg_16_8` `162.6ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 163.1 | 83013 | False | not_enough_gain |
| `group_c_device_first_join` | True | `distinct_pushdown_hashagg_16_8` | 162.6 | 83013 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 3327.7 | 1741660 | False | not_enough_gain |

### group_c_bundle_011

- Group/filter/window: `C` / `d.true_ip = %s` / `7d`
- Current best: `296.1ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`162126`
- Best candidate: `group_c_inner_join/default` `293.7ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `default` | 293.7 | 162126 | False | not_enough_gain |
| `group_c_device_first_join` | True | `default` | 296.3 | 162126 | False | not_enough_gain |

### group_c_bundle_012

- Group/filter/window: `C` / `p.card_holder_number_sha512 = %s` / `7d`
- Current best: `7.1ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`28`
- Best candidate: `group_c_inner_join/distinct_pushdown_hashagg_16_8` `6.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 6.8 | 28 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 95.7 | 558 | False | not_enough_gain |

### group_c_bundle_013

- Group/filter/window: `C` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `7d`
- Current best: `5.5ms` setting=`distinct_pushdown` scan_sum=`1`
- Best candidate: `group_c_inner_join/default` `5.3ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `default` | 5.3 | 1 | False | not_enough_gain |

### group_c_bundle_014

- Group/filter/window: `C` / `p.merchant_account_number = %s` / `7d`
- Current best: `167.2ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`29293`
- Best candidate: `group_c_inner_join/default` `146.3ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `default` | 146.3 | 29293 | True | >=10pct_faster |
| `group_c_numeric_projection` | False | `default` | 3.1 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `distinct_pushdown_hashagg_16_8` | 5306.6 | 1229832 | False | not_enough_gain |

#### Accepted SQL

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
JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE p.merchant_account_number = %s AND p.event_date >= 1772291655354
  AND d.jms_timestamp >= '2026-02-28 15:14:15.354000'
HAVING COUNT(*) > 0;
```

### group_c_bundle_015

- Group/filter/window: `C` / `d.exact_id = %s` / `30d`
- Current best: `7.9ms` setting=`distinct_pushdown` scan_sum=`216`
- Best candidate: `group_c_device_first_join/distinct_pushdown` `7.5ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `agg_pushdown_hashagg_16_8` | 7.7 | 216 | False | not_enough_gain |
| `group_c_device_first_join` | True | `distinct_pushdown` | 7.5 | 216 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 211.7 | 8391 | False | not_enough_gain |

### group_c_bundle_016

- Group/filter/window: `C` / `d.input_ip = %s` / `30d`
- Current best: `321.3ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`142227`
- Best candidate: `group_c_device_first_join/agg_pushdown_hashagg_16_8` `242.7ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 274.7 | 142227 | True | >=10pct_faster |
| `group_c_device_first_join` | True | `agg_pushdown_hashagg_16_8` | 242.7 | 142227 | True | >=10pct_faster |

#### Accepted SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0087`,
  SUM(p.amount) AS `metric__c_0088`,
  MIN(p.amount) AS `metric__c_0089`,
  MAX(p.amount) AS `metric__c_0090`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0091`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0092`,
  COUNT(DISTINCT(p.card_type)) AS `metric__c_0093`
FROM deviceprofile_fact d
JOIN pmt_txn_fact p
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.input_ip = %s AND d.jms_timestamp >= '2026-02-22 18:17:38.836000'
  AND p.event_date >= 1771784258836
HAVING COUNT(*) > 0;
```

### group_c_bundle_017

- Group/filter/window: `C` / `d.smart_id = %s` / `30d`
- Current best: `286.8ms` setting=`hashagg_16_8` scan_sum=`157032`
- Best candidate: `group_c_device_first_join/hashagg_16_8` `213.1ms`, accepted=`True`, reason=`>=10pct_faster`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown` | 263.5 | 157032 | False | not_enough_gain |
| `group_c_device_first_join` | True | `hashagg_16_8` | 213.1 | 157032 | True | >=10pct_faster |
| `filtered_scalar_subqueries` | True | `distinct_pushdown_hashagg_16_8` | 4354.5 | 3292116 | False | not_enough_gain |

#### Accepted SQL

```sql
SELECT
  COUNT(*) AS `metric__c_0057`,
  SUM(p.amount) AS `metric__c_0058`,
  MIN(p.amount) AS `metric__c_0059`,
  MAX(p.amount) AS `metric__c_0060`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0061`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0062`,
  COUNT(DISTINCT(p.card_type)) AS `metric__c_0063`,
  COUNT(DISTINCT(p.entry_method)) AS `metric__c_0064`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `metric__c_0176`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0176`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN p.amount END) AS `metric__c_0177`,
  SUM(CASE WHEN p.transaction_type = 'Sale' THEN 1 ELSE 0 END) AS `present__c_0177`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `metric__c_0182`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0182`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN p.amount END) AS `metric__c_0183`,
  SUM(CASE WHEN p.transaction_type = 'Refund' THEN 1 ELSE 0 END) AS `present__c_0183`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `metric__c_0188`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0188`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN p.amount END) AS `metric__c_0189`,
  SUM(CASE WHEN p.transaction_type = 'Chargeback' THEN 1 ELSE 0 END) AS `present__c_0189`
FROM deviceprofile_fact d
JOIN pmt_txn_fact p
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.smart_id = %s AND d.jms_timestamp >= '2026-02-17 20:35:38.629000'
  AND p.event_date >= 1771360538629
HAVING COUNT(*) > 0;
```

### group_c_bundle_018

- Group/filter/window: `C` / `d.true_ip = %s` / `30d`
- Current best: `452.4ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`290660`
- Best candidate: `group_c_device_first_join/distinct_pushdown` `443.5ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 462.0 | 290660 | False | not_enough_gain |
| `group_c_device_first_join` | True | `distinct_pushdown` | 443.5 | 290660 | False | not_enough_gain |

### group_c_bundle_019

- Group/filter/window: `C` / `p.card_holder_number_sha512 = %s` / `30d`
- Current best: `10.5ms` setting=`agg_pushdown_hashagg_16_8` scan_sum=`93`
- Best candidate: `group_c_inner_join/distinct_pushdown_hashagg_16_8` `10.2ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 10.2 | 93 | False | not_enough_gain |
| `filtered_scalar_subqueries` | True | `distinct_pushdown` | 109.7 | 1501 | False | not_enough_gain |

### group_c_bundle_020

- Group/filter/window: `C` / `p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s` / `30d`
- Current best: `5.8ms` setting=`distinct_pushdown` scan_sum=`3`
- Best candidate: `group_c_inner_join/agg_pushdown_hashagg_16_8` `5.8ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `agg_pushdown_hashagg_16_8` | 5.8 | 3 | False | not_enough_gain |

### group_c_bundle_021

- Group/filter/window: `C` / `p.merchant_account_number = %s` / `30d`
- Current best: `161.4ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`51822`
- Best candidate: `group_c_inner_join/distinct_pushdown_hashagg_16_8` `150.1ms`, accepted=`False`, reason=`not_enough_gain`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| `group_c_inner_join` | True | `distinct_pushdown_hashagg_16_8` | 150.1 | 51822 | False | not_enough_gain |
| `group_c_numeric_projection` | False | `default` | 3.0 | 0 | False | result_mismatch |
| `filtered_scalar_subqueries` | True | `default` | 4067.1 | 2069862 | False | not_enough_gain |

### group_c_bundle_022

- Group/filter/window: `C` / `d.exact_id = %s` / `180d`
- Current best: `13.3ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`1059`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_c_bundle_023

- Group/filter/window: `C` / `d.smart_id = %s` / `180d`
- Current best: `1267.5ms` setting=`distinct_pushdown_hashagg_16_8` scan_sum=`586942`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_c_bundle_024

- Group/filter/window: `C` / `p.card_holder_number_sha512 = %s` / `180d`
- Current best: `12.3ms` setting=`distinct_pushdown` scan_sum=`476`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |

### group_c_bundle_025

- Group/filter/window: `C` / `p.merchant_account_number = %s` / `180d`
- Current best: `769.2ms` setting=`hashagg_16_8` scan_sum=`372415`
- Best candidate: `-` `0.0ms`, accepted=`False`, reason=`no_valid_candidate`

| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
