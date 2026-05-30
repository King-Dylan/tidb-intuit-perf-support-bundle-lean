# TiKV vs TiFlash Candidate A/B

- Generated: `2026-05-30T07:13:27`
- Mixed JSON: `/home/ec2-user/tidb_intuit_perf_support_bundle_lean/code/results/mixed_traffic_1780124733.json`
- Pre-agg layout: `prod180`
- Pre-agg bundle count: `12`
- Session knobs: distinct_pushdown=`False`, force_inline_cte=`0`, hashagg_final=`4`, hashagg_partial=`4`

## Summary

| bundle | group | event | variant | engines | elapsed | storage tasks | result |
|---|---:|---|---|---|---:|---|---|
| group_b_bundle_019 | B | hot_smart_id:smart_id | tikv | tikv,tidb | 722.8 ms | cop[tikv], root | ok |
| group_b_bundle_019 | B | hot_smart_id:smart_id | cost | tikv,tiflash,tidb | 710.3 ms | cop[tikv], root | ok |

## 1. group_b_bundle_019

- Group/window/filter: `B` / `180d` / `d.smart_id = %s`
- Preagg applied: `True`
- Event: invoice=`INV0010730024` kind=`hot_smart_id` hot_field=`smart_id` hot_count=`382582` ref=`2026-04-10T21:03:14.101000`

### Params

```json
[
  "3b452b7fd9bd4ddcb27e0067970d6a1a",
  "3b452b7fd9bd4ddcb27e0067970d6a1a",
  "3b452b7fd9bd4ddcb27e0067970d6a1a",
  "3b452b7fd9bd4ddcb27e0067970d6a1a",
  "3b452b7fd9bd4ddcb27e0067970d6a1a",
  "3b452b7fd9bd4ddcb27e0067970d6a1a"
]
```

### tikv

- Engines: `tikv,tidb`
- Elapsed: `722.8 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.input_ip AS `raw_distinct_0`,
    d.true_ip AS `raw_distinct_1`,
    d.proxy_ip AS `raw_distinct_2`,
    d.exact_id AS `raw_distinct_3`,
    d.agent_type AS `raw_distinct_4`,
    d.agent_os AS `raw_distinct_5`
  FROM deviceprofile_fact d
  WHERE d.smart_id = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 21:03:14.101000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
),
distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_019'
    AND x.template_id IN ('b_0122', 'b_0126', 'b_0130', 'b_0134', 'b_0138', 'b_0142')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
  UNION ALL
  SELECT 'b_0122' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'b_0126' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'b_0130' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'b_0134' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION ALL
  SELECT 'b_0138' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
  UNION ALL
  SELECT 'b_0142' AS template_id, CAST(`raw_distinct_5` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_5` IS NOT NULL
),
unfiltered_counts AS (
  SELECT
    COUNT(DISTINCT CASE WHEN template_id = 'b_0122' THEN distinct_value END) AS `metric__b_0122`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0126' THEN distinct_value END) AS `metric__b_0126`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0130' THEN distinct_value END) AS `metric__b_0130`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0134' THEN distinct_value END) AS `metric__b_0134`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0138' THEN distinct_value END) AS `metric__b_0138`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0142' THEN distinct_value END) AS `metric__b_0142`
  FROM distinct_values
),
filtered_0 AS (
  SELECT
    (SELECT COUNT(DISTINCT u.distinct_value) FROM (
      SELECT x.distinct_value
      FROM `group_b_180d_daily_distinct` x
      WHERE x.bundle_id = 'group_b_bundle_019'
        AND x.template_id = 'b_0018'
        AND x.key1 = %s AND x.key2 = ''
        AND x.event_day > '2025-10-12'
      UNION ALL
      SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value
      FROM deviceprofile_fact d
      WHERE d.smart_id = %s AND d.exact_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 21:03:14.101000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000' AND ((d.request_result LIKE '%%pass%%' OR d.request_result LIKE '%%success%%') AND d.business_transaction REGEXP 'challenge_type=.*idp')
    ) u) AS `metric__b_0018`,
    COALESCE((SELECT SUM(u.presence_count) FROM (
      SELECT x.`present__b_0018` AS presence_count
      FROM `group_b_180d_daily_rollup` x
      WHERE x.bundle_id = 'group_b_bundle_019'
        AND x.key1 = %s AND x.key2 = ''
        AND x.event_day > '2025-10-12'
      UNION ALL
      SELECT COUNT(*) AS presence_count
      FROM deviceprofile_fact d
      WHERE d.smart_id = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 21:03:14.101000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000' AND ((d.request_result LIKE '%%pass%%' OR d.request_result LIKE '%%success%%') AND d.business_transaction REGEXP 'challenge_type=.*idp')
    ) u), 0) AS `present__b_0018`
)
SELECT
  filtered_0.`metric__b_0018`,
  filtered_0.`present__b_0018`,
  unfiltered_counts.`metric__b_0122`,
  unfiltered_counts.`metric__b_0126`,
  unfiltered_counts.`metric__b_0130`,
  unfiltered_counts.`metric__b_0134`,
  unfiltered_counts.`metric__b_0138`,
  unfiltered_counts.`metric__b_0142`
FROM unfiltered_counts
CROSS JOIN filtered_0;
```

```text
-- explain_analyze_elapsed_ms=722.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_451	1.00	1	root		time:696.6ms, open:24.4µs, close:78.4µs, loops:2, RU:1917.60, Concurrency:OFF	Column#1179, Column#1328, Column#784, Column#785, Column#786, Column#787, Column#788, Column#789	4 KB	N/A
└─Projection_453	1.00	1	root		time:696.6ms, open:22µs, close:76.2µs, loops:2, Concurrency:OFF	Column#784, Column#785, Column#786, Column#787, Column#788, Column#789, Column#1179, Column#1328	4 KB	N/A
  └─HashJoin_468	1.00	1	root		time:696.5ms, open:17.8µs, close:75.4µs, loops:2, build_hash_table:{total:696.3ms, fetch:696.3ms, build:6.23µs}, probe:{concurrency:5, total:3.48s, max:696.3ms, probe:11.7µs, fetch and wait:3.48s}	CARTESIAN inner join	50.7 KB	0 Bytes
    ├─HashAgg_492(Build)	1.00	1	root		time:696.4ms, open:13.9µs, close:63.8µs, loops:2	funcs:count(distinct Column#1387)->Column#784, funcs:count(distinct Column#1388)->Column#785, funcs:count(distinct Column#1389)->Column#786, funcs:count(distinct Column#1390)->Column#787, funcs:count(distinct Column#1391)->Column#788, funcs:count(distinct Column#1392)->Column#789	31.5 MB	0 Bytes
    │ └─Projection_609	572762.11	768780	root		time:354.5ms, open:2.36µs, close:62.4µs, loops:755, Concurrency:5	case(eq(Column#782, ?), Column#783)->Column#1387, case(eq(Column#782, ?), Column#783)->Column#1388, case(eq(Column#782, ?), Column#783)->Column#1389, case(eq(Column#782, ?), Column#783)->Column#1390, case(eq(Column#782, ?), Column#783)->Column#1391, case(eq(Column#782, ?), Column#783)->Column#1392	986.1 KB	N/A
    │   └─Union_496	572762.11	768780	root		time:365.6ms, open:713ns, close:42.1µs, loops:755		N/A	N/A
    │     ├─Projection_498	572755.74	768780	root		time:366ms, open:83.7µs, close:20.7µs, loops:755, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#782, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	980.8 KB	N/A
    │     │ └─IndexReader_501	572755.74	768780	root		time:371.6ms, open:82.6µs, close:10.4µs, loops:755, cop_task: {num: 33, max: 451.8ms, min: 1.32ms, avg: 39.4ms, p95: 359.9ms, max_proc_keys: 246752, p95_proc_keys: 234495, tot_proc: 511.8ms, tot_wait: 6.83ms, copr_cache: disabled, build_task_duration: 45.3µs, max_distsql_concurrency: 6}, fetch_resp_duration: 368.7ms, rpc_info:{Cop:{num_rpc:33, total_time:1.3s}}	index:IndexRangeScan_500	58.3 MB	N/A
    │     │   └─IndexRangeScan_500	572755.74	768780	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:150ms, min:0s, avg: 15.5ms, p80:10ms, p95:140ms, iters:877, tasks:33}, scan_detail: {total_process_keys: 768780, total_process_keys_size: 113149312, total_keys: 68132, get_snapshot_time: 6.4ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 511.8ms, total_suspend_time: 179.1µs, total_wait_time: 6.83ms, total_kv_read_wall_time: 80ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │     ├─Projection_502	1.06	0	root		time:1.09ms, open:64.8µs, close:9.8µs, loops:1, Concurrency:OFF	?->Column#782, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	3.73 KB	N/A
    │     │ └─Selection_504	1.06	0	root		time:1.09ms, open:62µs, close:7.7µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_506	1.33	0	root	CTE:raw_boundary	time:1.08ms, open:54.3µs, close:6.59µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    │     ├─Projection_510	1.06	0	root		time:1.12ms, open:1.11ms, close:2.57µs, loops:1, Concurrency:OFF	?->Column#782, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	3.73 KB	N/A
    │     │ └─Selection_512	1.06	0	root		time:1.11ms, open:1.11ms, close:987ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_514	1.33	0	root	CTE:raw_boundary	time:1.11ms, open:1.11ms, close:305ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_518	1.06	0	root		time:1.12ms, open:1.12ms, close:1.8µs, loops:1, Concurrency:OFF	?->Column#782, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	3.73 KB	N/A
    │     │ └─Selection_520	1.06	0	root		time:1.12ms, open:1.12ms, close:615ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_522	1.33	0	root	CTE:raw_boundary	time:1.11ms, open:1.11ms, close:180ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_526	1.06	0	root		time:1.13ms, open:1.12ms, close:1.56µs, loops:1, Concurrency:OFF	?->Column#782, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	3.73 KB	N/A
    │     │ └─Selection_528	1.06	0	root		time:1.12ms, open:1.12ms, close:615ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	3.73 KB	N/A
    │     │   └─CTEFullScan_530	1.33	0	root	CTE:raw_boundary	time:1.12ms, open:1.12ms, close:178ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_534	1.06	0	root		time:14µs, open:8.65µs, close:2.3µs, loops:1, Concurrency:OFF	?->Column#782, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	3.73 KB	N/A
    │     │ └─Selection_536	1.06	0	root		time:9.18µs, open:6.14µs, close:919ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.73 KB	N/A
    │     │   └─CTEFullScan_538	1.33	0	root	CTE:raw_boundary	time:1.3µs, open:271ns, close:88ns, loops:1	data:CTE_0	N/A	N/A
    │     └─Projection_542	1.06	0	root		time:12.5µs, open:9.1µs, close:1.43µs, loops:1, Concurrency:OFF	?->Column#782, cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#783	3.73 KB	N/A
    │       └─Selection_544	1.06	0	root		time:5.33µs, open:3.56µs, close:436ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	3.73 KB	N/A
    │         └─CTEFullScan_546	1.33	0	root	CTE:raw_boundary	time:682ns, open:84ns, close:74ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_474(Probe)	1.00	1	root		time:14.2µs, open:2.45µs, close:1.31µs, loops:2, Concurrency:OFF	?->Column#1179, ?->Column#1328	0 Bytes	N/A
      └─TableDual_476	1.00	1	root		time:3.27µs, open:194ns, close:239ns, loops:2	rows:1	N/A	N/A
CTE_0	1.33	0	root		time:1.08ms, open:54.3µs, close:6.59µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_440(Seed Part)	1.33	0	root		time:1.06ms, open:50.7µs, close:4.98µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.agent_os	4.72 KB	N/A
  └─IndexReader_445	1.65	0	root	partition:p20251101	time:1.06ms, open:45.7µs, close:3.52µs, loops:1, cop_task: {num: 1, max: 987.1µs, proc_keys: 0, tot_proc: 24.6µs, tot_wait: 39.8µs, copr_cache: disabled, build_task_duration: 13.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 995.8µs, rpc_info:{Cop:{num_rpc:1, total_time:976.9µs}}	index:Selection_444	282 Bytes	N/A
    └─Selection_444	1.65	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 19µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 24.6µs, total_wait_time: 39.8µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)))), or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(not(isnull(intuit_risk.deviceprofile_fact.agent_type)), not(isnull(intuit_risk.deviceprofile_fact.agent_os)))))	N/A	N/A
      └─IndexRangeScan_443	1.66	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_147	N/A	0	root			Output: ScalarQueryCol#568	N/A	N/A
└─MaxOneRow_102	1.00	1	root		time:3.04ms, open:8.29µs, close:14.8µs, loops:1		N/A	N/A
  └─StreamAgg_110	1.00	1	root		time:3.04ms, open:7.63µs, close:14.4µs, loops:2	funcs:count(distinct Column#515)->Column#516	888 Bytes	N/A
    └─Union_129	2.00	0	root		time:3.03ms, open:796ns, close:13.9µs, loops:1		N/A	N/A
      ├─Projection_131	1.00	0	root		time:2.99ms, open:62.4µs, close:9.26µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	3.48 KB	N/A
      │ └─IndexReader_134	1.00	0	root		time:2.99ms, open:59.2µs, close:7.35µs, loops:1, cop_task: {num: 1, max: 2.9ms, proc_keys: 0, tot_proc: 1.32ms, tot_wait: 937µs, copr_cache: disabled, build_task_duration: 20.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 2.91ms, rpc_info:{Cop:{num_rpc:1, total_time:2.89ms}}	index:IndexRangeScan_133	326 Bytes	N/A
      │   └─IndexRangeScan_133	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 918.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.32ms, total_wait_time: 937µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_135	1.00	0	root		time:1.44ms, open:71.2µs, close:3.84µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	2.86 KB	N/A
        └─IndexReader_144	1.00	0	root	partition:p20251101	time:1.43ms, open:64.8µs, close:2.56µs, loops:1, cop_task: {num: 1, max: 1.33ms, proc_keys: 0, tot_proc: 29µs, tot_wait: 42.3µs, copr_cache: disabled, build_task_duration: 19.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.35ms, rpc_info:{Cop:{num_rpc:1, total_time:1.32ms}}	index:Selection_143	282 Bytes	N/A
          └─Selection_143	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 21.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 29µs, total_wait_time: 42.3µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_142	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_233	N/A	0	root			Output: ScalarQueryCol#717	N/A	N/A
└─MaxOneRow_161	1.00	1	root		time:1.42ms, open:5.98µs, close:11µs, loops:1		N/A	N/A
  └─StreamAgg_169	1.00	1	root		time:1.41ms, open:5.54µs, close:10.6µs, loops:2	funcs:sum(Column#636)->Column#637	1.45 KB	N/A
    └─Union_204	2.00	1	root		time:1.4ms, open:789ns, close:10.2µs, loops:2		N/A	N/A
      ├─Projection_206	1.00	0	root		time:1.33ms, open:9.37µs, close:5.08µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#636	3.64 KB	N/A
      │ └─IndexLookUp_211	1.25	0	root		time:1.32ms, open:5.7µs, close:3.28µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_209(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.25ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.2ms, proc_keys: 0, tot_proc: 64.6µs, tot_wait: 33.1µs, copr_cache: disabled, build_task_duration: 13.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.24ms, rpc_info:{Cop:{num_rpc:1, total_time:1.18ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 12µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 64.6µs, total_wait_time: 33.1µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_210(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_212	1.00	1	root		time:1.36ms, open:71.5µs, close:4.57µs, loops:2, Concurrency:OFF	cast(Column#635, decimal(38,6) BINARY)->Column#636	380 Bytes	N/A
        └─StreamAgg_224	1.00	1	root		time:1.35ms, open:65.3µs, close:3.86µs, loops:2	funcs:count(Column#704)->Column#635	388 Bytes	N/A
          └─IndexReader_225	1.00	0	root	partition:p20251101	time:1.34ms, open:61.1µs, close:3.36µs, loops:1, cop_task: {num: 1, max: 1.26ms, proc_keys: 0, tot_proc: 25.7µs, tot_wait: 38.2µs, copr_cache: disabled, build_task_duration: 16.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.27ms, rpc_info:{Cop:{num_rpc:1, total_time:1.25ms}}	index:StreamAgg_218	290 Bytes	N/A
            └─StreamAgg_218	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 19.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 25.7µs, total_wait_time: 38.2µs}	funcs:count(?)->Column#704	N/A	N/A
              └─Selection_223	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_222	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_350	N/A	0	root			Output: ScalarQueryCol#1178	N/A	N/A
└─MaxOneRow_305	1.00	1	root		time:1.43ms, open:5.07µs, close:11µs, loops:1		N/A	N/A
  └─StreamAgg_313	1.00	1	root		time:1.43ms, open:4.71µs, close:10.7µs, loops:2	funcs:count(distinct Column#1125)->Column#1126	888 Bytes	N/A
    └─Union_332	2.00	0	root		time:1.42ms, open:670ns, close:10.1µs, loops:1		N/A	N/A
      ├─Projection_334	1.00	0	root		time:734µs, open:51.8µs, close:7.13µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1125	3.48 KB	N/A
      │ └─IndexReader_337	1.00	0	root		time:725.3µs, open:46.6µs, close:5.01µs, loops:1, cop_task: {num: 1, max: 655.4µs, proc_keys: 0, tot_proc: 63.8µs, tot_wait: 33.9µs, copr_cache: disabled, build_task_duration: 16.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 665.9µs, rpc_info:{Cop:{num_rpc:1, total_time:643.4µs}}	index:IndexRangeScan_336	322 Bytes	N/A
      │   └─IndexRangeScan_336	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 63.8µs, total_wait_time: 33.9µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_338	1.00	0	root		time:1.34ms, open:48.6µs, close:2.31µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1125	2.86 KB	N/A
        └─IndexReader_347	1.00	0	root	partition:p20251101	time:1.33ms, open:44.3µs, close:1.67µs, loops:1, cop_task: {num: 1, max: 1.25ms, proc_keys: 0, tot_proc: 18.7µs, tot_wait: 35.6µs, copr_cache: disabled, build_task_duration: 13µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.28ms, rpc_info:{Cop:{num_rpc:1, total_time:1.24ms}}	index:Selection_346	281 Bytes	N/A
          └─Selection_346	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.7µs, total_wait_time: 35.6µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_345	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_436	N/A	0	root			Output: ScalarQueryCol#1327	N/A	N/A
└─MaxOneRow_364	1.00	1	root		time:1.34ms, open:5.83µs, close:11.9µs, loops:1		N/A	N/A
  └─StreamAgg_372	1.00	1	root		time:1.34ms, open:5.51µs, close:11.6µs, loops:2	funcs:sum(Column#1246)->Column#1247	1.45 KB	N/A
    └─Union_407	2.00	1	root		time:1.33ms, open:759ns, close:11.1µs, loops:2		N/A	N/A
      ├─Projection_409	1.00	0	root		time:1.22ms, open:9.1µs, close:5.65µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#1246	3.64 KB	N/A
      │ └─IndexLookUp_414	1.25	0	root		time:1.21ms, open:6.05µs, close:3.44µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_412(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.14ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.12ms, proc_keys: 0, tot_proc: 43.3µs, tot_wait: 21.6µs, copr_cache: disabled, build_task_duration: 12.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.14ms, rpc_info:{Cop:{num_rpc:1, total_time:1.1ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 6.14µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 43.3µs, total_wait_time: 21.6µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_413(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_415	1.00	1	root		time:1.29ms, open:39.7µs, close:4.82µs, loops:2, Concurrency:OFF	cast(Column#1245, decimal(38,6) BINARY)->Column#1246	380 Bytes	N/A
        └─StreamAgg_427	1.00	1	root		time:1.28ms, open:38.2µs, close:4.13µs, loops:2	funcs:count(Column#1314)->Column#1245	388 Bytes	N/A
          └─IndexReader_428	1.00	0	root	partition:p20251101	time:1.27ms, open:35.5µs, close:3.58µs, loops:1, cop_task: {num: 1, max: 1.22ms, proc_keys: 0, tot_proc: 23.1µs, tot_wait: 29µs, copr_cache: disabled, build_task_duration: 11.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.23ms, rpc_info:{Cop:{num_rpc:1, total_time:1.21ms}}	index:StreamAgg_421	288 Bytes	N/A
            └─StreamAgg_421	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 13.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 23.1µs, total_wait_time: 29µs}	funcs:count(?)->Column#1314	N/A	N/A
              └─Selection_426	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_425	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```

### cost

- Engines: `tikv,tiflash,tidb`
- Elapsed: `710.3 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.input_ip AS `raw_distinct_0`,
    d.true_ip AS `raw_distinct_1`,
    d.proxy_ip AS `raw_distinct_2`,
    d.exact_id AS `raw_distinct_3`,
    d.agent_type AS `raw_distinct_4`,
    d.agent_os AS `raw_distinct_5`
  FROM deviceprofile_fact d
  WHERE d.smart_id = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 21:03:14.101000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
),
distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_019'
    AND x.template_id IN ('b_0122', 'b_0126', 'b_0130', 'b_0134', 'b_0138', 'b_0142')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
  UNION ALL
  SELECT 'b_0122' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION ALL
  SELECT 'b_0126' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION ALL
  SELECT 'b_0130' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION ALL
  SELECT 'b_0134' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION ALL
  SELECT 'b_0138' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
  UNION ALL
  SELECT 'b_0142' AS template_id, CAST(`raw_distinct_5` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_5` IS NOT NULL
),
unfiltered_counts AS (
  SELECT
    COUNT(DISTINCT CASE WHEN template_id = 'b_0122' THEN distinct_value END) AS `metric__b_0122`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0126' THEN distinct_value END) AS `metric__b_0126`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0130' THEN distinct_value END) AS `metric__b_0130`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0134' THEN distinct_value END) AS `metric__b_0134`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0138' THEN distinct_value END) AS `metric__b_0138`,
    COUNT(DISTINCT CASE WHEN template_id = 'b_0142' THEN distinct_value END) AS `metric__b_0142`
  FROM distinct_values
),
filtered_0 AS (
  SELECT
    (SELECT COUNT(DISTINCT u.distinct_value) FROM (
      SELECT x.distinct_value
      FROM `group_b_180d_daily_distinct` x
      WHERE x.bundle_id = 'group_b_bundle_019'
        AND x.template_id = 'b_0018'
        AND x.key1 = %s AND x.key2 = ''
        AND x.event_day > '2025-10-12'
      UNION ALL
      SELECT CAST(d.exact_id AS CHAR(256)) AS distinct_value
      FROM deviceprofile_fact d
      WHERE d.smart_id = %s AND d.exact_id IS NOT NULL AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 21:03:14.101000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000' AND ((d.request_result LIKE '%%pass%%' OR d.request_result LIKE '%%success%%') AND d.business_transaction REGEXP 'challenge_type=.*idp')
    ) u) AS `metric__b_0018`,
    COALESCE((SELECT SUM(u.presence_count) FROM (
      SELECT x.`present__b_0018` AS presence_count
      FROM `group_b_180d_daily_rollup` x
      WHERE x.bundle_id = 'group_b_bundle_019'
        AND x.key1 = %s AND x.key2 = ''
        AND x.event_day > '2025-10-12'
      UNION ALL
      SELECT COUNT(*) AS presence_count
      FROM deviceprofile_fact d
      WHERE d.smart_id = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 21:03:14.101000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000' AND ((d.request_result LIKE '%%pass%%' OR d.request_result LIKE '%%success%%') AND d.business_transaction REGEXP 'challenge_type=.*idp')
    ) u), 0) AS `present__b_0018`
)
SELECT
  filtered_0.`metric__b_0018`,
  filtered_0.`present__b_0018`,
  unfiltered_counts.`metric__b_0122`,
  unfiltered_counts.`metric__b_0126`,
  unfiltered_counts.`metric__b_0130`,
  unfiltered_counts.`metric__b_0134`,
  unfiltered_counts.`metric__b_0138`,
  unfiltered_counts.`metric__b_0142`
FROM unfiltered_counts
CROSS JOIN filtered_0;
```

```text
-- explain_analyze_elapsed_ms=710.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_550	1.00	1	root		time:684.6ms, open:19.8µs, close:79.1µs, loops:2, RU:1914.51, Concurrency:OFF	Column#1183, Column#1336, Column#788, Column#789, Column#790, Column#791, Column#792, Column#793	4 KB	N/A
└─Projection_552	1.00	1	root		time:684.6ms, open:17.3µs, close:76.9µs, loops:2, Concurrency:OFF	Column#788, Column#789, Column#790, Column#791, Column#792, Column#793, Column#1183, Column#1336	4 KB	N/A
  └─HashJoin_567	1.00	1	root		time:684.6ms, open:12.7µs, close:76.1µs, loops:2, build_hash_table:{total:684.4ms, fetch:684.4ms, build:6.32µs}, probe:{concurrency:5, total:3.42s, max:684.4ms, probe:7.36µs, fetch and wait:3.42s}	CARTESIAN inner join	50.7 KB	0 Bytes
    ├─HashAgg_591(Build)	1.00	1	root		time:684.4ms, open:9.07µs, close:64.9µs, loops:2	funcs:count(distinct Column#1395)->Column#788, funcs:count(distinct Column#1396)->Column#789, funcs:count(distinct Column#1397)->Column#790, funcs:count(distinct Column#1398)->Column#791, funcs:count(distinct Column#1399)->Column#792, funcs:count(distinct Column#1400)->Column#793	31.5 MB	0 Bytes
    │ └─Projection_708	572762.11	768780	root		time:343.8ms, open:1.4µs, close:63.2µs, loops:755, Concurrency:5	case(eq(Column#786, ?), Column#787)->Column#1395, case(eq(Column#786, ?), Column#787)->Column#1396, case(eq(Column#786, ?), Column#787)->Column#1397, case(eq(Column#786, ?), Column#787)->Column#1398, case(eq(Column#786, ?), Column#787)->Column#1399, case(eq(Column#786, ?), Column#787)->Column#1400	984.2 KB	N/A
    │   └─Union_595	572762.11	768780	root		time:351ms, open:710ns, close:44.2µs, loops:755		N/A	N/A
    │     ├─Projection_597	572755.74	768780	root		time:352.6ms, open:83.7µs, close:20.8µs, loops:755, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#786, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	982.2 KB	N/A
    │     │ └─IndexReader_600	572755.74	768780	root		time:359.3ms, open:82.5µs, close:10.4µs, loops:755, cop_task: {num: 33, max: 457ms, min: 1.19ms, avg: 38.7ms, p95: 360.4ms, max_proc_keys: 246752, p95_proc_keys: 234495, tot_proc: 503.8ms, tot_wait: 841.4µs, copr_cache: disabled, build_task_duration: 43.7µs, max_distsql_concurrency: 6}, fetch_resp_duration: 356.3ms, rpc_info:{Cop:{num_rpc:33, total_time:1.28s}}	index:IndexRangeScan_599	58.3 MB	N/A
    │     │   └─IndexRangeScan_599	572755.74	768780	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:150ms, min:0s, avg: 14.2ms, p80:10ms, p95:140ms, iters:877, tasks:33}, scan_detail: {total_process_keys: 768780, total_process_keys_size: 113149312, total_keys: 68132, get_snapshot_time: 393.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 503.8ms, total_suspend_time: 163.7µs, total_wait_time: 841.4µs, total_kv_read_wall_time: 40ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │     ├─Projection_601	1.06	0	root		time:1.25ms, open:91.8µs, close:10.9µs, loops:1, Concurrency:OFF	?->Column#786, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	3.73 KB	N/A
    │     │ └─Selection_603	1.06	0	root		time:1.25ms, open:89.4µs, close:8.76µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_605	1.33	0	root	CTE:raw_boundary	time:1.24ms, open:86µs, close:7.41µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    │     ├─Projection_609	1.06	0	root		time:1.22ms, open:1.21ms, close:2.2µs, loops:1, Concurrency:OFF	?->Column#786, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	68.6 KB	N/A
    │     │ └─Selection_611	1.06	0	root		time:1.21ms, open:1.21ms, close:656ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	35.0 KB	N/A
    │     │   └─CTEFullScan_613	1.33	0	root	CTE:raw_boundary	time:1.21ms, open:1.21ms, close:163ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_617	1.06	0	root		time:1.22ms, open:1.22ms, close:2.94µs, loops:1, Concurrency:OFF	?->Column#786, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	3.73 KB	N/A
    │     │ └─Selection_619	1.06	0	root		time:1.22ms, open:1.21ms, close:1.29µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_621	1.33	0	root	CTE:raw_boundary	time:1.21ms, open:1.21ms, close:192ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_625	1.06	0	root		time:1.23ms, open:1.22ms, close:1.85µs, loops:1, Concurrency:OFF	?->Column#786, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	3.73 KB	N/A
    │     │ └─Selection_627	1.06	0	root		time:1.22ms, open:1.22ms, close:852ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	3.73 KB	N/A
    │     │   └─CTEFullScan_629	1.33	0	root	CTE:raw_boundary	time:1.22ms, open:1.22ms, close:176ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_633	1.06	0	root		time:11.4µs, open:6.64µs, close:1.81µs, loops:1, Concurrency:OFF	?->Column#786, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	3.73 KB	N/A
    │     │ └─Selection_635	1.06	0	root		time:6.97µs, open:4.15µs, close:878ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.73 KB	N/A
    │     │   └─CTEFullScan_637	1.33	0	root	CTE:raw_boundary	time:1.34µs, open:388ns, close:71ns, loops:1	data:CTE_0	N/A	N/A
    │     └─Projection_641	1.06	0	root		time:7.52µs, open:3.87µs, close:1.76µs, loops:1, Concurrency:OFF	?->Column#786, cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#787	4.85 KB	N/A
    │       └─Selection_643	1.06	0	root		time:4.28µs, open:2.3µs, close:694ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	9.23 KB	N/A
    │         └─CTEFullScan_645	1.33	0	root	CTE:raw_boundary	time:847ns, open:178ns, close:97ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_573(Probe)	1.00	1	root		time:15µs, open:2.17µs, close:1.93µs, loops:2, Concurrency:OFF	?->Column#1183, ?->Column#1336	0 Bytes	N/A
      └─TableDual_575	1.00	1	root		time:3.5µs, open:182ns, close:487ns, loops:2	rows:1	N/A	N/A
CTE_0	1.33	0	root		time:1.24ms, open:86µs, close:7.41µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_530(Seed Part)	1.33	0	root		time:1.23ms, open:83µs, close:5.37µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.agent_os	4.72 KB	N/A
  └─IndexReader_539	1.65	0	root	partition:p20251101	time:1.22ms, open:78.4µs, close:4.05µs, loops:1, cop_task: {num: 1, max: 1.11ms, proc_keys: 0, tot_proc: 15.9µs, tot_wait: 28.4µs, copr_cache: disabled, build_task_duration: 27.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.13ms, rpc_info:{Cop:{num_rpc:1, total_time:1.1ms}}	index:Selection_538	279 Bytes	N/A
    └─Selection_538	1.65	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 11.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 15.9µs, total_wait_time: 28.4µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)))), or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(not(isnull(intuit_risk.deviceprofile_fact.agent_type)), not(isnull(intuit_risk.deviceprofile_fact.agent_os)))))	N/A	N/A
      └─IndexRangeScan_537	1.66	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_163	N/A	0	root			Output: ScalarQueryCol#568	N/A	N/A
└─MaxOneRow_102	1.00	1	root		time:1.53ms, open:6.06µs, close:11.6µs, loops:1		N/A	N/A
  └─StreamAgg_110	1.00	1	root		time:1.52ms, open:5.38µs, close:11.3µs, loops:2	funcs:count(distinct Column#515)->Column#516	888 Bytes	N/A
    └─Union_137	2.00	0	root		time:1.52ms, open:919ns, close:10.9µs, loops:1		N/A	N/A
      ├─Projection_139	1.00	0	root		time:774.4µs, open:71.4µs, close:8.35µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	11.3 KB	N/A
      │ └─IndexReader_142	1.00	0	root		time:768.7µs, open:69.2µs, close:6.4µs, loops:1, cop_task: {num: 1, max: 665.3µs, proc_keys: 0, tot_proc: 73.4µs, tot_wait: 36.4µs, copr_cache: disabled, build_task_duration: 25.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 682.8µs, rpc_info:{Cop:{num_rpc:1, total_time:646µs}}	index:IndexRangeScan_141	322 Bytes	N/A
      │   └─IndexRangeScan_141	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 73.4µs, total_wait_time: 36.4µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_143	1.00	0	root		time:1.48ms, open:77µs, close:2.01µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	10.7 KB	N/A
        └─IndexReader_156	1.00	0	root	partition:p20251101	time:1.47ms, open:73.6µs, close:1.4µs, loops:1, cop_task: {num: 1, max: 1.37ms, proc_keys: 0, tot_proc: 28.1µs, tot_wait: 41.7µs, copr_cache: disabled, build_task_duration: 24.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.39ms, rpc_info:{Cop:{num_rpc:1, total_time:1.35ms}}	index:Selection_155	282 Bytes	N/A
          └─Selection_155	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 19.7µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.1µs, total_wait_time: 41.7µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_154	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_278	N/A	0	root			Output: ScalarQueryCol#721	N/A	N/A
└─MaxOneRow_177	1.00	1	root		time:1.49ms, open:4.55µs, close:11.9µs, loops:1		N/A	N/A
  └─StreamAgg_185	1.00	1	root		time:1.48ms, open:4.03µs, close:11.6µs, loops:2	funcs:sum(Column#636)->Column#637	1.45 KB	N/A
    └─Union_238	2.00	1	root		time:1.47ms, open:810ns, close:11.1µs, loops:2		N/A	N/A
      ├─Projection_240	1.00	0	root		time:1.36ms, open:9.76µs, close:5.65µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#636	3.64 KB	N/A
      │ └─IndexLookUp_245	1.25	0	root		time:1.35ms, open:7.48µs, close:3.43µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_243(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.24ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.2ms, proc_keys: 0, tot_proc: 73.9µs, tot_wait: 31.4µs, copr_cache: disabled, build_task_duration: 17.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.23ms, rpc_info:{Cop:{num_rpc:1, total_time:1.18ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 14.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 73.9µs, total_wait_time: 31.4µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_244(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_246	1.00	1	root		time:1.41ms, open:50.9µs, close:4.99µs, loops:2, Concurrency:OFF	cast(Column#635, decimal(38,6) BINARY)->Column#636	8.24 KB	N/A
        └─StreamAgg_262	1.00	1	root		time:1.4ms, open:50.1µs, close:4.15µs, loops:2	funcs:count(Column#707)->Column#635	8.25 KB	N/A
          └─IndexReader_263	1.00	0	root	partition:p20251101	time:1.4ms, open:48.3µs, close:3.75µs, loops:1, cop_task: {num: 1, max: 1.33ms, proc_keys: 0, tot_proc: 24.3µs, tot_wait: 36.6µs, copr_cache: disabled, build_task_duration: 15.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.34ms, rpc_info:{Cop:{num_rpc:1, total_time:1.32ms}}	index:StreamAgg_252	290 Bytes	N/A
            └─StreamAgg_252	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 24.3µs, total_wait_time: 36.6µs}	funcs:count(?)->Column#707	N/A	N/A
              └─Selection_261	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_260	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_411	N/A	0	root			Output: ScalarQueryCol#1182	N/A	N/A
└─MaxOneRow_350	1.00	1	root		time:1.26ms, open:5.15µs, close:11.1µs, loops:1		N/A	N/A
  └─StreamAgg_358	1.00	1	root		time:1.26ms, open:4.76µs, close:10.8µs, loops:2	funcs:count(distinct Column#1129)->Column#1130	888 Bytes	N/A
    └─Union_385	2.00	0	root		time:1.25ms, open:864ns, close:10.3µs, loops:1		N/A	N/A
      ├─Projection_387	1.00	0	root		time:626.9µs, open:61.2µs, close:6.95µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1129	3.48 KB	N/A
      │ └─IndexReader_390	1.00	0	root		time:621.2µs, open:58.5µs, close:5.12µs, loops:1, cop_task: {num: 1, max: 530.4µs, proc_keys: 0, tot_proc: 38.7µs, tot_wait: 28.1µs, copr_cache: disabled, build_task_duration: 19.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 549.6µs, rpc_info:{Cop:{num_rpc:1, total_time:517.6µs}}	index:IndexRangeScan_389	321 Bytes	N/A
      │   └─IndexRangeScan_389	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 9.53µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 38.7µs, total_wait_time: 28.1µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_391	1.00	0	root		time:1.21ms, open:44.4µs, close:2.72µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1129	10.7 KB	N/A
        └─IndexReader_404	1.00	0	root	partition:p20251101	time:1.21ms, open:42.1µs, close:1.85µs, loops:1, cop_task: {num: 1, max: 1.15ms, proc_keys: 0, tot_proc: 19.2µs, tot_wait: 35.8µs, copr_cache: disabled, build_task_duration: 11.5µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.16ms, rpc_info:{Cop:{num_rpc:1, total_time:1.14ms}}	index:Selection_403	282 Bytes	N/A
          └─Selection_403	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 19.2µs, total_wait_time: 35.8µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_402	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_526	N/A	0	root			Output: ScalarQueryCol#1335	N/A	N/A
└─MaxOneRow_425	1.00	1	root		time:1.34ms, open:4.22µs, close:11.5µs, loops:1		N/A	N/A
  └─StreamAgg_433	1.00	1	root		time:1.34ms, open:3.9µs, close:11.1µs, loops:2	funcs:sum(Column#1250)->Column#1251	1.45 KB	N/A
    └─Union_486	2.00	1	root		time:1.33ms, open:647ns, close:10.7µs, loops:2		N/A	N/A
      ├─Projection_488	1.00	0	root		time:1.28ms, open:9.37µs, close:5.41µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#1250	3.64 KB	N/A
      │ └─IndexLookUp_493	1.25	0	root		time:1.28ms, open:7.34µs, close:3.42µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_491(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.2ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.17ms, proc_keys: 0, tot_proc: 49.8µs, tot_wait: 25.6µs, copr_cache: disabled, build_task_duration: 12.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.2ms, rpc_info:{Cop:{num_rpc:1, total_time:1.16ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 8.81µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 49.8µs, total_wait_time: 25.6µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_492(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_494	1.00	1	root		time:1.29ms, open:36.4µs, close:4.85µs, loops:2, Concurrency:OFF	cast(Column#1249, decimal(38,6) BINARY)->Column#1250	380 Bytes	N/A
        └─StreamAgg_510	1.00	1	root		time:1.28ms, open:35.1µs, close:4.29µs, loops:2	funcs:count(Column#1321)->Column#1249	388 Bytes	N/A
          └─IndexReader_511	1.00	0	root	partition:p20251101	time:1.28ms, open:32.4µs, close:3.94µs, loops:1, cop_task: {num: 1, max: 1.22ms, proc_keys: 0, tot_proc: 45µs, tot_wait: 39.2µs, copr_cache: disabled, build_task_duration: 9.44µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.23ms, rpc_info:{Cop:{num_rpc:1, total_time:1.21ms}}	index:StreamAgg_500	290 Bytes	N/A
            └─StreamAgg_500	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 45µs, total_wait_time: 39.2µs}	funcs:count(?)->Column#1321	N/A	N/A
              └─Selection_509	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_508	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```
