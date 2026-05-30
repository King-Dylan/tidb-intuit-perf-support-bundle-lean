# TiKV vs TiFlash Candidate A/B

- Generated: `2026-05-30T07:13:40`
- Mixed JSON: `/home/ec2-user/tidb_intuit_perf_support_bundle_lean/code/results/mixed_traffic_1780124733.json`
- Pre-agg layout: `prod180`
- Pre-agg bundle count: `12`
- Session knobs: distinct_pushdown=`True`, force_inline_cte=`0`, hashagg_final=`16`, hashagg_partial=`8`

## Summary

| bundle | group | event | variant | engines | elapsed | storage tasks | result |
|---|---:|---|---|---|---:|---|---|
| group_b_bundle_019 | B | hot_smart_id:smart_id | tikv | tikv,tidb | 688.6 ms | cop[tikv], root | ok |
| group_b_bundle_019 | B | hot_smart_id:smart_id | cost | tikv,tiflash,tidb | 700.3 ms | cop[tikv], root | ok |

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
- Elapsed: `688.6 ms`
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
-- explain_analyze_elapsed_ms=688.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_413	1.00	1	root		time:664.3ms, open:23.1µs, close:88.1µs, loops:2, RU:1908.40, Concurrency:OFF	Column#1131, Column#1280, Column#760, Column#761, Column#762, Column#763, Column#764, Column#765	4 KB	N/A
└─Projection_415	1.00	1	root		time:664.2ms, open:20.8µs, close:86.2µs, loops:2, Concurrency:OFF	Column#760, Column#761, Column#762, Column#763, Column#764, Column#765, Column#1131, Column#1280	4 KB	N/A
  └─HashJoin_430	1.00	1	root		time:664.2ms, open:15.4µs, close:85.5µs, loops:2, build_hash_table:{total:664ms, fetch:664ms, build:5.58µs}, probe:{concurrency:10, total:6.64s, max:664ms, probe:6.85µs, fetch and wait:6.64s}	CARTESIAN inner join	50.7 KB	0 Bytes
    ├─HashAgg_450(Build)	1.00	1	root		time:664ms, open:11.8µs, close:73.3µs, loops:2	funcs:count(distinct Column#1339)->Column#760, funcs:count(distinct Column#1340)->Column#761, funcs:count(distinct Column#1341)->Column#762, funcs:count(distinct Column#1342)->Column#763, funcs:count(distinct Column#1343)->Column#764, funcs:count(distinct Column#1344)->Column#765	31.5 MB	0 Bytes
    │ └─Projection_510	572762.11	768780	root		time:344.2ms, open:1.41µs, close:71.7µs, loops:755, Concurrency:10	case(eq(Column#758, ?), Column#759)->Column#1339, case(eq(Column#758, ?), Column#759)->Column#1340, case(eq(Column#758, ?), Column#759)->Column#1341, case(eq(Column#758, ?), Column#759)->Column#1342, case(eq(Column#758, ?), Column#759)->Column#1343, case(eq(Column#758, ?), Column#759)->Column#1344	1.93 MB	N/A
    │   └─Union_452	572762.11	768780	root		time:361.1ms, open:688ns, close:45.7µs, loops:755		N/A	N/A
    │     ├─Projection_454	572755.74	768780	root		time:360.1ms, open:99.4µs, close:25.8µs, loops:755, Concurrency:10	intuit_risk.group_b_180d_daily_distinct.template_id->Column#758, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	1.91 MB	N/A
    │     │ └─IndexReader_457	572755.74	768780	root		time:362.3ms, open:98.3µs, close:10.2µs, loops:755, cop_task: {num: 33, max: 445.1ms, min: 1.25ms, avg: 38.1ms, p95: 346ms, max_proc_keys: 246752, p95_proc_keys: 234495, tot_proc: 485.3ms, tot_wait: 4.15ms, copr_cache: disabled, build_task_duration: 48.4µs, max_distsql_concurrency: 6}, fetch_resp_duration: 359.1ms, rpc_info:{Cop:{num_rpc:33, total_time:1.26s}}	index:IndexRangeScan_456	58.3 MB	N/A
    │     │   └─IndexRangeScan_456	572755.74	768780	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:140ms, min:0s, avg: 14.8ms, p80:10ms, p95:140ms, iters:877, tasks:33}, scan_detail: {total_process_keys: 768780, total_process_keys_size: 113149312, total_keys: 68132, get_snapshot_time: 3.69ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 485.3ms, total_suspend_time: 167.9µs, total_wait_time: 4.15ms, total_kv_read_wall_time: 80ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │     ├─Projection_458	1.06	0	root		time:1.19ms, open:1.18ms, close:10.3µs, loops:1, Concurrency:OFF	?->Column#758, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	3.73 KB	N/A
    │     │ └─Selection_460	1.06	0	root		time:1.18ms, open:1.17ms, close:8.17µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_462	1.33	0	root	CTE:raw_boundary	time:1.18ms, open:1.17ms, close:7.02µs, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_466	1.06	0	root		time:1.15ms, open:64.4µs, close:1.5µs, loops:1, Concurrency:OFF	?->Column#758, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	3.73 KB	N/A
    │     │ └─Selection_468	1.06	0	root		time:1.14ms, open:61.1µs, close:482ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_470	1.33	0	root	CTE:raw_boundary	time:1.14ms, open:57µs, close:110ns, loops:1	data:CTE_0	0 Bytes	0 Bytes
    │     ├─Projection_474	1.06	0	root		time:1.16ms, open:1.16ms, close:1.92µs, loops:1, Concurrency:OFF	?->Column#758, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	3.73 KB	N/A
    │     │ └─Selection_476	1.06	0	root		time:1.16ms, open:1.15ms, close:756ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_478	1.33	0	root	CTE:raw_boundary	time:1.15ms, open:1.15ms, close:166ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_482	1.06	0	root		time:1.17ms, open:1.17ms, close:1.42µs, loops:1, Concurrency:OFF	?->Column#758, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	3.73 KB	N/A
    │     │ └─Selection_484	1.06	0	root		time:1.17ms, open:1.16ms, close:431ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	3.73 KB	N/A
    │     │   └─CTEFullScan_486	1.33	0	root	CTE:raw_boundary	time:1.16ms, open:1.16ms, close:175ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_490	1.06	0	root		time:1.19ms, open:1.18ms, close:1.56µs, loops:1, Concurrency:OFF	?->Column#758, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	3.73 KB	N/A
    │     │ └─Selection_492	1.06	0	root		time:1.18ms, open:1.18ms, close:509ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.73 KB	N/A
    │     │   └─CTEFullScan_494	1.33	0	root	CTE:raw_boundary	time:1.18ms, open:1.18ms, close:125ns, loops:1	data:CTE_0	N/A	N/A
    │     └─Projection_498	1.06	0	root		time:1.19ms, open:1.19ms, close:1.44µs, loops:1, Concurrency:OFF	?->Column#758, cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#759	3.73 KB	N/A
    │       └─Selection_500	1.06	0	root		time:1.19ms, open:1.19ms, close:500ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	3.73 KB	N/A
    │         └─CTEFullScan_502	1.33	0	root	CTE:raw_boundary	time:1.18ms, open:1.18ms, close:87ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_436(Probe)	1.00	1	root		time:13.2µs, open:2.12µs, close:1.14µs, loops:2, Concurrency:OFF	?->Column#1131, ?->Column#1280	0 Bytes	N/A
      └─TableDual_438	1.00	1	root		time:3.58µs, open:207ns, close:204ns, loops:2	rows:1	N/A	N/A
CTE_0	1.33	0	root		time:1.18ms, open:1.17ms, close:7.02µs, loops:1	Non-Recursive CTE	N/A	N/A
└─Projection_402(Seed Part)	1.33	0	root		time:1.12ms, open:50.3µs, close:5.32µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.agent_os	4.72 KB	N/A
  └─IndexReader_407	1.65	0	root	partition:p20251101	time:1.11ms, open:45.2µs, close:3.85µs, loops:1, cop_task: {num: 1, max: 1.04ms, proc_keys: 0, tot_proc: 12.8µs, tot_wait: 33.6µs, copr_cache: disabled, build_task_duration: 12.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.05ms, rpc_info:{Cop:{num_rpc:1, total_time:1.04ms}}	index:Selection_406	280 Bytes	N/A
    └─Selection_406	1.65	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 15.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 12.8µs, total_wait_time: 33.6µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)))), or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(not(isnull(intuit_risk.deviceprofile_fact.agent_type)), not(isnull(intuit_risk.deviceprofile_fact.agent_os)))))	N/A	N/A
      └─IndexRangeScan_405	1.66	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_128	N/A	0	root			Output: ScalarQueryCol#544	N/A	N/A
└─MaxOneRow_102	1.00	1	root		time:2.07ms, open:12.9µs, close:16µs, loops:1		N/A	N/A
  └─HashAgg_107	1.00	1	root		time:2.06ms, open:12.3µs, close:15.6µs, loops:2	funcs:count(distinct Column#515)->Column#516	1.59 KB	0 Bytes
    └─Union_109	2.00	0	root		time:2.04ms, open:834ns, close:15µs, loops:1		N/A	N/A
      ├─Projection_111	1.00	0	root		time:1.66ms, open:78.4µs, close:11.6µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	3.48 KB	N/A
      │ └─IndexReader_114	1.00	0	root		time:1.66ms, open:75.5µs, close:9.38µs, loops:1, cop_task: {num: 1, max: 1.54ms, proc_keys: 0, tot_proc: 91.5µs, tot_wait: 852.1µs, copr_cache: disabled, build_task_duration: 25.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.56ms, rpc_info:{Cop:{num_rpc:1, total_time:1.53ms}}	index:IndexRangeScan_113	322 Bytes	N/A
      │   └─IndexRangeScan_113	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 828.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 91.5µs, total_wait_time: 852.1µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_115	1.00	0	root		time:2.01ms, open:135.1µs, close:2.74µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	2.86 KB	N/A
        └─IndexReader_124	1.00	0	root	partition:p20251101	time:2ms, open:129.1µs, close:2µs, loops:1, cop_task: {num: 1, max: 1.83ms, proc_keys: 0, tot_proc: 28.5µs, tot_wait: 523.6µs, copr_cache: disabled, build_task_duration: 20.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.86ms, rpc_info:{Cop:{num_rpc:1, total_time:1.82ms}}	index:Selection_123	282 Bytes	N/A
          └─Selection_123	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 492.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.5µs, total_wait_time: 523.6µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_122	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_214	N/A	0	root			Output: ScalarQueryCol#693	N/A	N/A
└─MaxOneRow_142	1.00	1	root		time:1.51ms, open:6.17µs, close:23.1µs, loops:1		N/A	N/A
  └─StreamAgg_150	1.00	1	root		time:1.5ms, open:5.66µs, close:22.7µs, loops:2	funcs:sum(Column#612)->Column#613	1.45 KB	N/A
    └─Union_185	2.00	1	root		time:1.49ms, open:805ns, close:22.2µs, loops:2		N/A	N/A
      ├─Projection_187	1.00	0	root		time:1.46ms, open:10.2µs, close:14µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#612	3.64 KB	N/A
      │ └─IndexLookUp_192	1.25	0	root		time:1.46ms, open:6.64µs, close:12.5µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_190(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.34ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.3ms, proc_keys: 0, tot_proc: 89.9µs, tot_wait: 41.4µs, copr_cache: disabled, build_task_duration: 16µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.33ms, rpc_info:{Cop:{num_rpc:1, total_time:1.28ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 19.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 89.9µs, total_wait_time: 41.4µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_191(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_193	1.00	1	root		time:1.31ms, open:52.8µs, close:7.48µs, loops:2, Concurrency:OFF	cast(Column#611, decimal(38,6) BINARY)->Column#612	380 Bytes	N/A
        └─StreamAgg_205	1.00	1	root		time:1.3ms, open:50.8µs, close:5.6µs, loops:2	funcs:count(Column#680)->Column#611	388 Bytes	N/A
          └─IndexReader_206	1.00	0	root	partition:p20251101	time:1.29ms, open:48.9µs, close:4.87µs, loops:1, cop_task: {num: 1, max: 1.22ms, proc_keys: 0, tot_proc: 26µs, tot_wait: 36.7µs, copr_cache: disabled, build_task_duration: 15.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.23ms, rpc_info:{Cop:{num_rpc:1, total_time:1.21ms}}	index:StreamAgg_199	290 Bytes	N/A
            └─StreamAgg_199	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26µs, total_wait_time: 36.7µs}	funcs:count(?)->Column#680	N/A	N/A
              └─Selection_204	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_203	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_312	N/A	0	root			Output: ScalarQueryCol#1130	N/A	N/A
└─MaxOneRow_286	1.00	1	root		time:1.29ms, open:8.7µs, close:10.5µs, loops:1		N/A	N/A
  └─HashAgg_291	1.00	1	root		time:1.29ms, open:8.16µs, close:10.3µs, loops:2	funcs:count(distinct Column#1101)->Column#1102	1.59 KB	0 Bytes
    └─Union_293	2.00	0	root		time:1.27ms, open:787ns, close:9.45µs, loops:1		N/A	N/A
      ├─Projection_295	1.00	0	root		time:755µs, open:58.6µs, close:6.17µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1101	3.48 KB	N/A
      │ └─IndexReader_298	1.00	0	root		time:749.6µs, open:55.6µs, close:4.71µs, loops:1, cop_task: {num: 1, max: 658.9µs, proc_keys: 0, tot_proc: 62.6µs, tot_wait: 39.9µs, copr_cache: disabled, build_task_duration: 18.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 680.3µs, rpc_info:{Cop:{num_rpc:1, total_time:645.7µs}}	index:IndexRangeScan_297	322 Bytes	N/A
      │   └─IndexRangeScan_297	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 21.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 62.6µs, total_wait_time: 39.9µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_299	1.00	0	root		time:1.24ms, open:42.7µs, close:2.57µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1101	2.86 KB	N/A
        └─IndexReader_308	1.00	0	root	partition:p20251101	time:1.23ms, open:39.2µs, close:1.77µs, loops:1, cop_task: {num: 1, max: 1.17ms, proc_keys: 0, tot_proc: 18.7µs, tot_wait: 36.5µs, copr_cache: disabled, build_task_duration: 14.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.18ms, rpc_info:{Cop:{num_rpc:1, total_time:1.16ms}}	index:Selection_307	282 Bytes	N/A
          └─Selection_307	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.7µs, total_wait_time: 36.5µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_306	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_398	N/A	0	root			Output: ScalarQueryCol#1279	N/A	N/A
└─MaxOneRow_326	1.00	1	root		time:1.4ms, open:5.2µs, close:8.91µs, loops:1		N/A	N/A
  └─StreamAgg_334	1.00	1	root		time:1.39ms, open:4.79µs, close:8.64µs, loops:2	funcs:sum(Column#1198)->Column#1199	1.45 KB	N/A
    └─Union_369	2.00	1	root		time:1.39ms, open:682ns, close:8.16µs, loops:2		N/A	N/A
      ├─Projection_371	1.00	0	root		time:1.24ms, open:11.9µs, close:3.55µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#1198	3.64 KB	N/A
      │ └─IndexLookUp_376	1.25	0	root		time:1.23ms, open:8.16µs, close:2.38µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_374(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.16ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.13ms, proc_keys: 0, tot_proc: 57.4µs, tot_wait: 27.7µs, copr_cache: disabled, build_task_duration: 14.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.15ms, rpc_info:{Cop:{num_rpc:1, total_time:1.12ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 10µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 57.4µs, total_wait_time: 27.7µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_375(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_377	1.00	1	root		time:1.36ms, open:61.2µs, close:4.08µs, loops:2, Concurrency:OFF	cast(Column#1197, decimal(38,6) BINARY)->Column#1198	380 Bytes	N/A
        └─StreamAgg_389	1.00	1	root		time:1.34ms, open:59.5µs, close:3.25µs, loops:2	funcs:count(Column#1266)->Column#1197	388 Bytes	N/A
          └─IndexReader_390	1.00	0	root	partition:p20251101	time:1.34ms, open:53.7µs, close:2.87µs, loops:1, cop_task: {num: 1, max: 1.27ms, proc_keys: 0, tot_proc: 52µs, tot_wait: 38.2µs, copr_cache: disabled, build_task_duration: 15.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.27ms, rpc_info:{Cop:{num_rpc:1, total_time:1.25ms}}	index:StreamAgg_383	290 Bytes	N/A
            └─StreamAgg_383	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 17.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 52µs, total_wait_time: 38.2µs}	funcs:count(?)->Column#1266	N/A	N/A
              └─Selection_388	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_387	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```

### cost

- Engines: `tikv,tiflash,tidb`
- Elapsed: `700.3 ms`
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
-- explain_analyze_elapsed_ms=700.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_496	1.00	1	root		time:676.1ms, open:17.3µs, close:101.7µs, loops:2, RU:1921.14, Concurrency:OFF	Column#1135, Column#1288, Column#764, Column#765, Column#766, Column#767, Column#768, Column#769	4 KB	N/A
└─Projection_498	1.00	1	root		time:676.1ms, open:14.8µs, close:100µs, loops:2, Concurrency:OFF	Column#764, Column#765, Column#766, Column#767, Column#768, Column#769, Column#1135, Column#1288	4 KB	N/A
  └─HashJoin_513	1.00	1	root		time:676ms, open:11.7µs, close:99.3µs, loops:2, build_hash_table:{total:675.8ms, fetch:675.8ms, build:6.13µs}, probe:{concurrency:10, total:6.76s, max:675.8ms, probe:8.82µs, fetch and wait:6.76s}	CARTESIAN inner join	50.7 KB	0 Bytes
    ├─HashAgg_533(Build)	1.00	1	root		time:675.8ms, open:8.01µs, close:87µs, loops:2	funcs:count(distinct Column#1347)->Column#764, funcs:count(distinct Column#1348)->Column#765, funcs:count(distinct Column#1349)->Column#766, funcs:count(distinct Column#1350)->Column#767, funcs:count(distinct Column#1351)->Column#768, funcs:count(distinct Column#1352)->Column#769	31.5 MB	0 Bytes
    │ └─Projection_593	572762.11	768780	root		time:349.9ms, open:1.19µs, close:86µs, loops:755, Concurrency:10	case(eq(Column#762, ?), Column#763)->Column#1347, case(eq(Column#762, ?), Column#763)->Column#1348, case(eq(Column#762, ?), Column#763)->Column#1349, case(eq(Column#762, ?), Column#763)->Column#1350, case(eq(Column#762, ?), Column#763)->Column#1351, case(eq(Column#762, ?), Column#763)->Column#1352	1.92 MB	N/A
    │   └─Union_535	572762.11	768780	root		time:365.6ms, open:608ns, close:61µs, loops:755		N/A	N/A
    │     ├─Projection_537	572755.74	768780	root		time:364.6ms, open:96µs, close:37.1µs, loops:755, Concurrency:10	intuit_risk.group_b_180d_daily_distinct.template_id->Column#762, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	1.91 MB	N/A
    │     │ └─IndexReader_540	572755.74	768780	root		time:367.3ms, open:94.8µs, close:10.7µs, loops:755, cop_task: {num: 33, max: 435.3ms, min: 1.21ms, avg: 37.5ms, p95: 346ms, max_proc_keys: 246752, p95_proc_keys: 234495, tot_proc: 523.6ms, tot_wait: 869.7µs, copr_cache: disabled, build_task_duration: 44.6µs, max_distsql_concurrency: 6}, fetch_resp_duration: 364.3ms, rpc_info:{Cop:{num_rpc:33, total_time:1.24s}}	index:IndexRangeScan_539	82.8 MB	N/A
    │     │   └─IndexRangeScan_539	572755.74	768780	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:180ms, min:0s, avg: 15.5ms, p80:10ms, p95:140ms, iters:877, tasks:33}, scan_detail: {total_process_keys: 768780, total_process_keys_size: 113149312, total_keys: 68132, get_snapshot_time: 421.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 523.6ms, total_suspend_time: 163.3µs, total_wait_time: 869.7µs, total_kv_read_wall_time: 60ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    │     ├─Projection_541	1.06	0	root		time:1.17ms, open:60.8µs, close:9.9µs, loops:1, Concurrency:OFF	?->Column#762, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	3.73 KB	N/A
    │     │ └─Selection_543	1.06	0	root		time:1.16ms, open:58.5µs, close:7.75µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_545	1.33	0	root	CTE:raw_boundary	time:1.16ms, open:54.6µs, close:6.6µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    │     ├─Projection_549	1.06	0	root		time:1.17ms, open:1.17ms, close:1.81µs, loops:1, Concurrency:OFF	?->Column#762, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	3.73 KB	N/A
    │     │ └─Selection_551	1.06	0	root		time:1.17ms, open:1.16ms, close:499ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	3.73 KB	N/A
    │     │   └─CTEFullScan_553	1.33	0	root	CTE:raw_boundary	time:1.16ms, open:1.16ms, close:80ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_557	1.06	0	root		time:1.18ms, open:1.17ms, close:2.37µs, loops:1, Concurrency:OFF	?->Column#762, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	4.85 KB	N/A
    │     │ └─Selection_559	1.06	0	root		time:1.17ms, open:1.17ms, close:1.06µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	9.23 KB	N/A
    │     │   └─CTEFullScan_561	1.33	0	root	CTE:raw_boundary	time:1.17ms, open:1.17ms, close:168ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_565	1.06	0	root		time:1.18ms, open:1.18ms, close:3.21µs, loops:1, Concurrency:OFF	?->Column#762, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	25.3 KB	N/A
    │     │ └─Selection_567	1.06	0	root		time:1.18ms, open:1.18ms, close:1.44µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	78.2 KB	N/A
    │     │   └─CTEFullScan_569	1.33	0	root	CTE:raw_boundary	time:1.17ms, open:1.17ms, close:178ns, loops:1	data:CTE_0	N/A	N/A
    │     ├─Projection_573	1.06	0	root		time:1.18ms, open:1.18ms, close:2.66µs, loops:1, Concurrency:OFF	?->Column#762, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	3.73 KB	N/A
    │     │ └─Selection_575	1.06	0	root		time:1.18ms, open:1.18ms, close:1.08µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.73 KB	N/A
    │     │   └─CTEFullScan_577	1.33	0	root	CTE:raw_boundary	time:1.18ms, open:1.18ms, close:71ns, loops:1	data:CTE_0	N/A	N/A
    │     └─Projection_581	1.06	0	root		time:1.19ms, open:1.18ms, close:2.04µs, loops:1, Concurrency:OFF	?->Column#762, cast(cast(intuit_risk.deviceprofile_fact.agent_os, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#763	3.73 KB	N/A
    │       └─Selection_583	1.06	0	root		time:1.18ms, open:1.18ms, close:777ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_os))	3.73 KB	N/A
    │         └─CTEFullScan_585	1.33	0	root	CTE:raw_boundary	time:1.18ms, open:1.18ms, close:177ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_519(Probe)	1.00	1	root		time:10.9µs, open:2.42µs, close:1.08µs, loops:2, Concurrency:OFF	?->Column#1135, ?->Column#1288	0 Bytes	N/A
      └─TableDual_521	1.00	1	root		time:3.03µs, open:204ns, close:294ns, loops:2	rows:1	N/A	N/A
CTE_0	1.33	0	root		time:1.16ms, open:54.6µs, close:6.6µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_476(Seed Part)	1.33	0	root		time:1.14ms, open:47.4µs, close:5.01µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.agent_os	4.72 KB	N/A
  └─IndexReader_485	1.65	0	root	partition:p20251101	time:1.13ms, open:44.1µs, close:3.55µs, loops:1, cop_task: {num: 1, max: 1.06ms, proc_keys: 0, tot_proc: 18.7µs, tot_wait: 32.1µs, copr_cache: disabled, build_task_duration: 10.6µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.07ms, rpc_info:{Cop:{num_rpc:1, total_time:1.05ms}}	index:Selection_484	281 Bytes	N/A
    └─Selection_484	1.65	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 13µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 18.7µs, total_wait_time: 32.1µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)))), or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(not(isnull(intuit_risk.deviceprofile_fact.agent_type)), not(isnull(intuit_risk.deviceprofile_fact.agent_os)))))	N/A	N/A
      └─IndexRangeScan_483	1.66	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_136	N/A	0	root			Output: ScalarQueryCol#544	N/A	N/A
└─MaxOneRow_102	1.00	1	root		time:1.51ms, open:9.23µs, close:11.6µs, loops:1		N/A	N/A
  └─HashAgg_107	1.00	1	root		time:1.5ms, open:8.6µs, close:11.3µs, loops:2	funcs:count(distinct Column#515)->Column#516	1.59 KB	0 Bytes
    └─Union_109	2.00	0	root		time:1.49ms, open:684ns, close:10.7µs, loops:1		N/A	N/A
      ├─Projection_111	1.00	0	root		time:767.2µs, open:77.9µs, close:7.72µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	11.3 KB	N/A
      │ └─IndexReader_114	1.00	0	root		time:761.3µs, open:75.6µs, close:5.91µs, loops:1, cop_task: {num: 1, max: 641.4µs, proc_keys: 0, tot_proc: 72.9µs, tot_wait: 36.8µs, copr_cache: disabled, build_task_duration: 25.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 668.6µs, rpc_info:{Cop:{num_rpc:1, total_time:625.8µs}}	index:IndexRangeScan_113	321 Bytes	N/A
      │   └─IndexRangeScan_113	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 72.9µs, total_wait_time: 36.8µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_115	1.00	0	root		time:1.45ms, open:71.7µs, close:2.29µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#515	10.7 KB	N/A
        └─IndexReader_128	1.00	0	root	partition:p20251101	time:1.45ms, open:68.5µs, close:1.58µs, loops:1, cop_task: {num: 1, max: 1.36ms, proc_keys: 0, tot_proc: 29.3µs, tot_wait: 37.8µs, copr_cache: disabled, build_task_duration: 21.8µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.37ms, rpc_info:{Cop:{num_rpc:1, total_time:1.34ms}}	index:Selection_127	282 Bytes	N/A
          └─Selection_127	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 29.3µs, total_wait_time: 37.8µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_126	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_251	N/A	0	root			Output: ScalarQueryCol#697	N/A	N/A
└─MaxOneRow_150	1.00	1	root		time:1.38ms, open:4.12µs, close:20.6µs, loops:1		N/A	N/A
  └─StreamAgg_158	1.00	1	root		time:1.38ms, open:3.61µs, close:20.2µs, loops:2	funcs:sum(Column#612)->Column#613	1.45 KB	N/A
    └─Union_211	2.00	1	root		time:1.37ms, open:631ns, close:19.7µs, loops:2		N/A	N/A
      ├─Projection_213	1.00	0	root		time:1.34ms, open:7.74µs, close:10.6µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#612	3.64 KB	N/A
      │ └─IndexLookUp_218	1.25	0	root		time:1.34ms, open:5.84µs, close:9.06µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_216(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.26ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.23ms, proc_keys: 0, tot_proc: 65.8µs, tot_wait: 32.7µs, copr_cache: disabled, build_task_duration: 15.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.25ms, rpc_info:{Cop:{num_rpc:1, total_time:1.22ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 13.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 65.8µs, total_wait_time: 32.7µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_217(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_219	1.00	1	root		time:1.26ms, open:58.6µs, close:8.1µs, loops:2, Concurrency:OFF	cast(Column#611, decimal(38,6) BINARY)->Column#612	8.24 KB	N/A
        └─StreamAgg_235	1.00	1	root		time:1.25ms, open:57.4µs, close:5.86µs, loops:2	funcs:count(Column#683)->Column#611	8.25 KB	N/A
          └─IndexReader_236	1.00	0	root	partition:p20251101	time:1.24ms, open:54µs, close:5.11µs, loops:1, cop_task: {num: 1, max: 1.16ms, proc_keys: 0, tot_proc: 25.4µs, tot_wait: 34.8µs, copr_cache: disabled, build_task_duration: 16.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.18ms, rpc_info:{Cop:{num_rpc:1, total_time:1.15ms}}	index:StreamAgg_225	289 Bytes	N/A
            └─StreamAgg_225	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 18.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 25.4µs, total_wait_time: 34.8µs}	funcs:count(?)->Column#683	N/A	N/A
              └─Selection_234	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_233	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_357	N/A	0	root			Output: ScalarQueryCol#1134	N/A	N/A
└─MaxOneRow_323	1.00	1	root		time:1.3ms, open:25.9µs, close:9.23µs, loops:1		N/A	N/A
  └─HashAgg_328	1.00	1	root		time:1.3ms, open:25.5µs, close:8.95µs, loops:2	funcs:count(distinct Column#1105)->Column#1106	1.59 KB	0 Bytes
    └─Union_330	2.00	0	root		time:1.27ms, open:647ns, close:8.23µs, loops:1		N/A	N/A
      ├─Projection_332	1.00	0	root		time:705.5µs, open:43.9µs, close:5.4µs, loops:1, Concurrency:OFF	cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1105	11.3 KB	N/A
      │ └─IndexReader_335	1.00	0	root		time:701.2µs, open:42.1µs, close:4.14µs, loops:1, cop_task: {num: 1, max: 637.1µs, proc_keys: 0, tot_proc: 64.6µs, tot_wait: 40.8µs, copr_cache: disabled, build_task_duration: 15.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 648.1µs, rpc_info:{Cop:{num_rpc:1, total_time:625.2µs}}	index:IndexRangeScan_334	322 Bytes	N/A
      │   └─IndexRangeScan_334	1.00	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 21.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 64.6µs, total_wait_time: 40.8µs}	range:(? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
      └─Projection_336	1.00	0	root		time:1.24ms, open:58.8µs, close:2.18µs, loops:1, Concurrency:OFF	cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#1105	2.86 KB	N/A
        └─IndexReader_349	1.00	0	root	partition:p20251101	time:1.23ms, open:55.1µs, close:1.42µs, loops:1, cop_task: {num: 1, max: 1.15ms, proc_keys: 0, tot_proc: 15.6µs, tot_wait: 37.1µs, copr_cache: disabled, build_task_duration: 13.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.17ms, rpc_info:{Cop:{num_rpc:1, total_time:1.14ms}}	index:Selection_348	281 Bytes	N/A
          └─Selection_348	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 16.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 15.6µs, total_wait_time: 37.1µs}	not(isnull(intuit_risk.deviceprofile_fact.exact_id)), or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
            └─IndexRangeScan_347	1.00	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
ScalarSubQuery_472	N/A	0	root			Output: ScalarQueryCol#1287	N/A	N/A
└─MaxOneRow_371	1.00	1	root		time:1.25ms, open:5.05µs, close:15.1µs, loops:1		N/A	N/A
  └─StreamAgg_379	1.00	1	root		time:1.25ms, open:4.69µs, close:14.9µs, loops:2	funcs:sum(Column#1202)->Column#1203	1.45 KB	N/A
    └─Union_432	2.00	1	root		time:1.24ms, open:1.79µs, close:14.5µs, loops:2		N/A	N/A
      ├─Projection_434	1.00	0	root		time:1.22ms, open:8.91µs, close:9.78µs, loops:1, Concurrency:OFF	intuit_risk.group_b_180d_daily_rollup.present__b_0018->Column#1202	3.64 KB	N/A
      │ └─IndexLookUp_439	1.25	0	root		time:1.21ms, open:6.29µs, close:8.79µs, loops:1		442 Bytes	N/A
      │   ├─IndexRangeScan_437(Build)	1.25	0	cop[tikv]	table:x, index:PRIMARY(bundle_id, key1, key2, event_day)	time:1.13ms, open:0s, close:0s, loops:1, cop_task: {num: 1, max: 1.11ms, proc_keys: 0, tot_proc: 57.6µs, tot_wait: 27µs, copr_cache: disabled, build_task_duration: 13.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.13ms, rpc_info:{Cop:{num_rpc:1, total_time:1.1ms}}, tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 10.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 57.6µs, total_wait_time: 27µs}	range:(? ? ? ?,? ? ? +inf], keep order:false, stats:pseudo	N/A	N/A
      │   └─TableRowIDScan_438(Probe)	1.25	0	cop[tikv]	table:x		keep order:false, stats:pseudo	N/A	N/A
      └─Projection_440	1.00	1	root		time:1.2ms, open:42.8µs, close:4.11µs, loops:2, Concurrency:OFF	cast(Column#1201, decimal(38,6) BINARY)->Column#1202	380 Bytes	N/A
        └─StreamAgg_456	1.00	1	root		time:1.19ms, open:41.1µs, close:3.22µs, loops:2	funcs:count(Column#1273)->Column#1201	388 Bytes	N/A
          └─IndexReader_457	1.00	0	root	partition:p20251101	time:1.18ms, open:38.2µs, close:2.57µs, loops:1, cop_task: {num: 1, max: 1.12ms, proc_keys: 0, tot_proc: 51.3µs, tot_wait: 29.9µs, copr_cache: disabled, build_task_duration: 11.4µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.13ms, rpc_info:{Cop:{num_rpc:1, total_time:1.11ms}}	index:StreamAgg_446	289 Bytes	N/A
            └─StreamAgg_446	1.00	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 12.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 51.3µs, total_wait_time: 29.9µs}	funcs:count(?)->Column#1273	N/A	N/A
              └─Selection_455	1.03	0	cop[tikv]		tikv_task:{time:0s, loops:1}	or(like(intuit_risk.deviceprofile_fact.request_result, ?, ?), like(intuit_risk.deviceprofile_fact.request_result, ?, ?)), regexp(intuit_risk.deviceprofile_fact.business_transaction, ?)	N/A	N/A
                └─IndexRangeScan_454	1.28	0	cop[tikv]	table:d, index:idx_dev_smart_runtime_cov(smart_id, jms_timestamp, interaction_id, agent_type, agent_os, request_result, business_transaction, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:(? ?,? ?), keep order:false	N/A	N/A
```
