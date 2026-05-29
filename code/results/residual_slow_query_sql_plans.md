# Residual Slow Query SQL And EXPLAIN ANALYZE

Source: `results/final_before_after_optimization_report.md`

## Summary

| Bundle | Filter | Window | Optimized ms | Scan sum | Scan max | Best variant | Indexes |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `group_b_bundle_020` | `d.true_ip = %s` | `180d` | 1128.5 | 1559443 | 1559443 | `optimized_distinct_pushdown_hashagg_16_8` | `x: PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)`<br>`d: idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, ` |
| `group_b_bundle_018` | `d.input_ip = %s` | `180d` | 669.3 | 767762 | 767762 | `optimized_distinct_pushdown` | `x: PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)`<br>`d: idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score` |
| `group_c_bundle_018` | `d.true_ip = %s` | `30d` | 988.6 | 177323 | 172835 | `optimized_distinct_pushdown_hashagg_16_8` | `d: idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, `<br>`p: idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha51` |
| `group_b_bundle_012` | `d.true_ip = %s` | `30d` | 502.1 | 172835 | 172835 | `optimized_default` | `d: idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, ` |


## group_b_bundle_020

- Filter/window: `d.true_ip = %s` / `180d`
- Optimization tried/kept: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown_hashagg_16_8
- Latest optimized EXPLAIN ANALYZE elapsed: `1128.5 ms`
- Optimized plan scan total_process_keys sum/max: `1559443` / `1559443`
- Main indexes: `x: PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)`, `d: idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, `

### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 3034.6 ms | ok |
| `optimized_default` | `{}` | 1196.5 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 1128.8 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 1129.1 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 1154.9 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 1128.5 ms | ok |

### Current Optimized SQL

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

### Current Optimized Params

```json
[
  "74.179.68.52",
  "74.179.68.52"
]
```

### Current Optimized EXPLAIN ANALYZE

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

### Original SQL

```sql
SELECT
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0162' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.exact_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0162`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0166' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.smart_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.smart_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0166`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0170' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.input_ip AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.input_ip IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0170`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0174' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.proxy_ip AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.proxy_ip IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0174`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_020' AND x.template_id = 'b_0178' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-12' UNION ALL SELECT CAST(d.agent_type AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.true_ip = %s AND d.agent_type IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 19:16:29.762000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000') u) AS `metric__b_0178`;
```

### Original EXPLAIN ANALYZE

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

## group_b_bundle_018

- Filter/window: `d.input_ip = %s` / `180d`
- Optimization tried/kept: SQL rewrite: materialize raw cutoff boundary once via CTE and share it across distinct metrics; Session tuning: optimized_distinct_pushdown
- Latest optimized EXPLAIN ANALYZE elapsed: `669.3 ms`
- Optimized plan scan total_process_keys sum/max: `767762` / `767762`
- Main indexes: `x: PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)`, `d: idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id`

### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 1495.0 ms | ok |
| `optimized_default` | `{}` | 708.6 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 671.7 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 694.6 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 669.3 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 679.2 ms | ok |

### Current Optimized SQL

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

### Current Optimized Params

```json
[
  "135.232.20.92",
  "135.232.20.92"
]
```

### Current Optimized EXPLAIN ANALYZE

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

### Original SQL

```sql
SELECT
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0146' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.exact_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0146`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0150' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.smart_id AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.smart_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0150`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0154' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.true_ip AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.true_ip IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0154`,
  (SELECT COUNT(DISTINCT u.distinct_value) FROM (SELECT x.distinct_value FROM `group_b_180d_daily_distinct` x WHERE x.bundle_id = 'group_b_bundle_018' AND x.template_id = 'b_0158' AND x.key1 = %s AND x.key2 = '' AND x.event_day > '2025-10-11' UNION ALL SELECT CAST(d.agent_type AS CHAR(256)) AS distinct_value FROM deviceprofile_fact d WHERE d.input_ip = %s AND d.agent_type IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-11 09:39:36.398000' AND d.jms_timestamp < '2025-10-12 00:00:00.000000') u) AS `metric__b_0158`;
```

### Original EXPLAIN ANALYZE

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

## group_c_bundle_018

- Filter/window: `d.true_ip = %s` / `30d`
- Optimization tried/kept: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0; Session tuning: optimized_distinct_pushdown_hashagg_16_8
- Latest optimized EXPLAIN ANALYZE elapsed: `988.6 ms`
- Optimized plan scan total_process_keys sum/max: `177323` / `172835`
- Main indexes: `d: idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, `, `p: idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt`

### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 2511.5 ms | ok |
| `optimized_default` | `{}` | 1601.4 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 2433.7 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 1918.7 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 1057.0 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 988.6 ms | ok |

### Current Optimized SQL

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

### Current Optimized Params

```json
[
  "74.179.68.52"
]
```

### Current Optimized EXPLAIN ANALYZE

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

### Original SQL

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

### Original EXPLAIN ANALYZE

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

## group_b_bundle_012

- Filter/window: `d.true_ip = %s` / `30d`
- Optimization tried/kept: SQL rewrite: remove redundant GROUP BY on constant key, keep empty-result semantics with HAVING COUNT(*) > 0
- Latest optimized EXPLAIN ANALYZE elapsed: `502.1 ms`
- Optimized plan scan total_process_keys sum/max: `172835` / `172835`
- Main indexes: `d: idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, `

### Candidate Timings

| Candidate | Settings | Time | Result |
| --- | --- | ---: | --- |
| `original_baseline` | `{'tidb_isolation_read_engines': 'tikv,tidb', 'tidb_opt_force_inline_cte': 0, 'tidb_opt_distinct_agg_push_down': 0, 'tidb_hashagg_final_concurrency': 4, 'tidb_hashagg_partial_concurrency': 4}` | 507.2 ms | ok |
| `optimized_default` | `{}` | 502.1 ms | ok |
| `optimized_hashagg_16_8` | `{'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 504.2 ms | ok |
| `optimized_hashagg_32_8` | `{'tidb_hashagg_final_concurrency': 32, 'tidb_hashagg_partial_concurrency': 8}` | 505.0 ms | ok |
| `optimized_distinct_pushdown` | `{'tidb_opt_distinct_agg_push_down': 1}` | 2490.2 ms | ok |
| `optimized_distinct_pushdown_hashagg_16_8` | `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}` | 2410.0 ms | ok |

### Current Optimized SQL

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

### Current Optimized Params

```json
[
  "74.179.68.52"
]
```

### Current Optimized EXPLAIN ANALYZE

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

### Original SQL

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

### Original EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=507.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_5	187.67	1	root		time:472.4ms, open:113.8µs, close:43.9µs, loops:2, RU:722.46, Concurrency:OFF	Column#60, Column#61, Column#61, Column#62, Column#62, Column#63, Column#63, Column#64, Column#64, Column#65, Column#65, Column#66, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, Column#73, Column#75, Column#73, Column#76, Column#77, Column#78, Column#77, Column#79, Column#77, Column#80, Column#81, Column#82, Column#81, Column#83, Column#81, Column#84, Column#85, Column#86, Column#85, Column#87, Column#85, Column#88, Column#89, Column#90, Column#89, Column#91, Column#89	99.7 KB	N/A
└─HashAgg_9	187.67	1	root		time:472.3ms, open:110.5µs, close:42µs, loops:2	group by:Column#223, funcs:count(?)->Column#60, funcs:sum(Column#192)->Column#61, funcs:sum(Column#193)->Column#62, funcs:sum(Column#194)->Column#63, funcs:sum(Column#195)->Column#64, funcs:sum(Column#196)->Column#65, funcs:sum(Column#197)->Column#66, funcs:count(distinct Column#198)->Column#67, funcs:count(distinct Column#199)->Column#68, funcs:count(distinct Column#200)->Column#69, funcs:count(distinct Column#201)->Column#70, funcs:count(distinct Column#202)->Column#71, funcs:min(Column#203)->Column#72, funcs:sum(Column#204)->Column#73, funcs:max(Column#205)->Column#74, funcs:avg(Column#206)->Column#75, funcs:min(Column#207)->Column#76, funcs:sum(Column#208)->Column#77, funcs:max(Column#209)->Column#78, funcs:avg(Column#210)->Column#79, funcs:min(Column#211)->Column#80, funcs:sum(Column#212)->Column#81, funcs:max(Column#213)->Column#82, funcs:avg(Column#214)->Column#83, funcs:min(Column#215)->Column#84, funcs:sum(Column#216)->Column#85, funcs:max(Column#217)->Column#86, funcs:avg(Column#218)->Column#87, funcs:min(Column#219)->Column#88, funcs:sum(Column#220)->Column#89, funcs:max(Column#221)->Column#90, funcs:avg(Column#222)->Column#91	23.3 MB	0 Bytes
  └─Projection_29	346177.19	172835	root		time:166.8ms, open:96µs, close:41µs, loops:172, Concurrency:5	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#192, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#193, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#194, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#195, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#196, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#197, intuit_risk.deviceprofile_fact.exact_id->Column#198, intuit_risk.deviceprofile_fact.smart_id->Column#199, intuit_risk.deviceprofile_fact.input_ip->Column#200, intuit_risk.deviceprofile_fact.proxy_ip->Column#201, intuit_risk.deviceprofile_fact.agent_type->Column#202, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#203, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#204, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#205, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#206, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#207, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#208, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#209, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#210, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#211, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#212, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#213, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#214, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#215, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#216, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#217, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#218, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#219, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#220, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#222, intuit_risk.deviceprofile_fact.true_ip->Column#223	6.73 MB	N/A
    └─IndexReader_21	346177.19	172835	root	partition:p20260401,p20260501,p20260601,pmax	time:184.6ms, open:95.1µs, close:12.6µs, loops:172, cop_task: {num: 18, max: 248.7ms, min: 962.2µs, avg: 19.5ms, p95: 248.7ms, max_proc_keys: 105587, p95_proc_keys: 105587, tot_proc: 189.8ms, tot_wait: 4.4ms, copr_cache: disabled, build_task_duration: 36.1µs, max_distsql_concurrency: 4}, fetch_resp_duration: 182.3ms, rpc_info:{Cop:{num_rpc:18, total_time:351.3ms}}	index:IndexRangeScan_20	21.0 MB	N/A
      └─IndexRangeScan_20	346177.19	172835	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:120ms, min:0s, avg: 8.89ms, p80:10ms, p95:120ms, iters:233, tasks:18}, scan_detail: {total_process_keys: 172835, total_process_keys_size: 42640965, total_keys: 67265, get_snapshot_time: 4.1ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 189.8ms, total_suspend_time: 171.8µs, total_wait_time: 4.4ms, total_kv_read_wall_time: 40ms}	range:[? ?,? +inf], keep order:false	N/A	N/A
```
