# TiKV vs TiFlash Candidate A/B

- Generated: `2026-05-29T23:33:00`
- Mixed JSON: `/home/ec2-user/tidb_intuit_perf_support_bundle_lean/code/results/mixed_traffic_1780092771.json`
- Pre-agg layout: `prod180`
- Pre-agg bundle count: `12`
- Session knobs: distinct_pushdown=`True`, force_inline_cte=`0`, hashagg_final=`16`, hashagg_partial=`8`

## Summary

| bundle | group | event | variant | engines | elapsed | storage tasks | result |
|---|---:|---|---|---|---:|---|---|
| group_b_bundle_012 | B | hot_true_ip:true_ip | tikv | tikv,tidb | 2537.2 ms | cop[tikv], root | ok |
| group_b_bundle_012 | B | hot_true_ip:true_ip | cost | tikv,tiflash,tidb | 2468.5 ms | cop[tikv], root | ok |
| group_b_bundle_012 | B | hot_true_ip:true_ip | tiflash_hint | tikv,tiflash,tidb | 5293.2 ms | mpp[tiflash], root | ok |
| group_b_bundle_012 | B | hot_true_ip:true_ip | tiflash_only | tiflash,tidb | 621.8 ms | mpp[tiflash], root | ok |
| group_b_bundle_018 | B | hot_input_ip:input_ip | tikv | tikv,tidb | 1115.7 ms | cop[tikv], root | ok |
| group_b_bundle_018 | B | hot_input_ip:input_ip | cost | tikv,tiflash,tidb | 1110.2 ms | cop[tikv], root | ok |
| group_b_bundle_018 | B | hot_input_ip:input_ip | tiflash_hint | tikv,tiflash,tidb | 1155.2 ms | cop[tikv], root | ok |
| group_b_bundle_018 | B | hot_input_ip:input_ip | tiflash_only | tiflash,tidb | 2.3 ms |  | (1815, "Internal : No access path for table 'x' is found with 'tidb_isolation_read_engines' = 'tiflash,tidb', valid valu |
| group_b_bundle_020 | B | hot_true_ip:true_ip | tikv | tikv,tidb | 1167.1 ms | cop[tikv], root | ok |
| group_b_bundle_020 | B | hot_true_ip:true_ip | cost | tikv,tiflash,tidb | 1151.0 ms | cop[tikv], root | ok |
| group_b_bundle_020 | B | hot_true_ip:true_ip | tiflash_hint | tikv,tiflash,tidb | 1133.6 ms | cop[tikv], root | ok |
| group_b_bundle_020 | B | hot_true_ip:true_ip | tiflash_only | tiflash,tidb | 2.6 ms |  | (1815, "Internal : No access path for table 'x' is found with 'tidb_isolation_read_engines' = 'tiflash,tidb', valid valu |
| group_c_bundle_018 | C | hot_true_ip:true_ip | tikv | tikv,tidb | 331.8 ms | cop[tikv], root | ok |
| group_c_bundle_018 | C | hot_true_ip:true_ip | cost | tikv,tiflash,tidb | 329.8 ms | cop[tikv], root | ok |
| group_c_bundle_018 | C | hot_true_ip:true_ip | tiflash_hint | tikv,tiflash,tidb | 1731.9 ms | mpp[tiflash], root | ok |
| group_c_bundle_018 | C | hot_true_ip:true_ip | tiflash_only | tiflash,tidb | 219.3 ms | mpp[tiflash], root | ok |

## 1. group_b_bundle_012

- Group/window/filter: `B` / `30d` / `d.true_ip = %s`
- Preagg applied: `False`
- Event: invoice=`INV0007589128` kind=`hot_true_ip` hot_field=`true_ip` hot_count=`738824` ref=`2026-04-10T23:06:57.563000`

### Params

```json
[
  "72.153.231.69"
]
```

### tikv

- Engines: `tikv,tidb`
- Elapsed: `2537.2 ms`
- Storage tasks: `cop[tikv], root`

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
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=2537.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:2.53s, open:1.48ms, close:14.2µs, loops:2, RU:892.55, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	38.7 KB	N/A
└─Selection_9	0.80	1	root		time:2.53s, open:1.47ms, close:11.7µs, loops:2	gt(Column#60, ?)	38.7 KB	N/A
  └─HashAgg_16	1.00	1	root		time:2.53s, open:1.45ms, close:11.2µs, loops:3	funcs:count(Column#141)->Column#60, funcs:sum(Column#142)->Column#61, funcs:sum(Column#143)->Column#62, funcs:sum(Column#144)->Column#63, funcs:sum(Column#145)->Column#64, funcs:sum(Column#146)->Column#65, funcs:sum(Column#147)->Column#66, funcs:count(distinct intuit_risk.deviceprofile_fact.exact_id)->Column#67, funcs:count(distinct intuit_risk.deviceprofile_fact.smart_id)->Column#68, funcs:count(distinct intuit_risk.deviceprofile_fact.input_ip)->Column#69, funcs:count(distinct intuit_risk.deviceprofile_fact.proxy_ip)->Column#70, funcs:count(distinct intuit_risk.deviceprofile_fact.agent_type)->Column#71, funcs:min(Column#148)->Column#72, funcs:sum(Column#149)->Column#73, funcs:max(Column#150)->Column#74, funcs:avg(Column#151, Column#152)->Column#75, funcs:min(Column#153)->Column#76, funcs:sum(Column#154)->Column#77, funcs:max(Column#155)->Column#78, funcs:avg(Column#156, Column#157)->Column#79, funcs:min(Column#158)->Column#80, funcs:sum(Column#159)->Column#81, funcs:max(Column#160)->Column#82, funcs:avg(Column#161, Column#162)->Column#83, funcs:min(Column#163)->Column#84, funcs:sum(Column#164)->Column#85, funcs:max(Column#165)->Column#86, funcs:avg(Column#166, Column#167)->Column#87, funcs:min(Column#168)->Column#88, funcs:sum(Column#169)->Column#89, funcs:max(Column#170)->Column#90, funcs:avg(Column#171, Column#172)->Column#91	152.0 MB	0 Bytes
    └─IndexReader_17	1.00	167600	root	partition:p20260401,p20260501,p20260601,pmax	time:2.24s, open:1.41ms, close:10.7µs, loops:11, cop_task: {num: 12, max: 2.33s, min: 1.87ms, avg: 268.7ms, p95: 2.33s, max_proc_keys: 116680, p95_proc_keys: 116680, tot_proc: 803ms, tot_wait: 2.51ms, copr_cache: disabled, build_task_duration: 1.34ms, max_distsql_concurrency: 4}, fetch_resp_duration: 2.24s, rpc_info:{Cop:{num_rpc:12, total_time:3.22s}}	index:HashAgg_11	147.1 MB	N/A
      └─HashAgg_11	1.00	167600	cop[tikv]		tikv_task:{proc max:1.09s, min:0s, avg: 135.8ms, p80:150ms, p95:1.09s, iters:171, tasks:12}, scan_detail: {total_process_keys: 172346, total_process_keys_size: 40578683, total_keys: 55677, get_snapshot_time: 2.88ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 803ms, total_suspend_time: 535.7µs, total_wait_time: 2.51ms, total_kv_read_wall_time: 90ms}	group by:intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.smart_id, funcs:count(?)->Column#141, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#142, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#143, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#144, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#145, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#146, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#147, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#148, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?))->Column#149, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#150, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#151, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#152, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#153, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?))->Column#154, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#155, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#156, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#157, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#158, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?))->Column#159, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#160, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#161, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#162, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#163, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?))->Column#164, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#165, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#166, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#167, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#168, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?))->Column#169, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#170, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#171, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#172	N/A	N/A
        └─IndexRangeScan_15	359561.64	172346	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:150ms, min:0s, avg: 20ms, p80:20ms, p95:150ms, iters:171, tasks:12}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### cost

- Engines: `tikv,tiflash,tidb`
- Elapsed: `2468.5 ms`
- Storage tasks: `cop[tikv], root`

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
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=2468.5
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:2.46s, open:118µs, close:12.5µs, loops:2, RU:864.89, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	26.5 KB	N/A
└─Selection_9	0.80	1	root		time:2.46s, open:114.4µs, close:10.1µs, loops:2	gt(Column#60, ?)	38.7 KB	N/A
  └─HashAgg_17	1.00	1	root		time:2.46s, open:111.3µs, close:9.59µs, loops:3	funcs:count(Column#141)->Column#60, funcs:sum(Column#142)->Column#61, funcs:sum(Column#143)->Column#62, funcs:sum(Column#144)->Column#63, funcs:sum(Column#145)->Column#64, funcs:sum(Column#146)->Column#65, funcs:sum(Column#147)->Column#66, funcs:count(distinct intuit_risk.deviceprofile_fact.exact_id)->Column#67, funcs:count(distinct intuit_risk.deviceprofile_fact.smart_id)->Column#68, funcs:count(distinct intuit_risk.deviceprofile_fact.input_ip)->Column#69, funcs:count(distinct intuit_risk.deviceprofile_fact.proxy_ip)->Column#70, funcs:count(distinct intuit_risk.deviceprofile_fact.agent_type)->Column#71, funcs:min(Column#148)->Column#72, funcs:sum(Column#149)->Column#73, funcs:max(Column#150)->Column#74, funcs:avg(Column#151, Column#152)->Column#75, funcs:min(Column#153)->Column#76, funcs:sum(Column#154)->Column#77, funcs:max(Column#155)->Column#78, funcs:avg(Column#156, Column#157)->Column#79, funcs:min(Column#158)->Column#80, funcs:sum(Column#159)->Column#81, funcs:max(Column#160)->Column#82, funcs:avg(Column#161, Column#162)->Column#83, funcs:min(Column#163)->Column#84, funcs:sum(Column#164)->Column#85, funcs:max(Column#165)->Column#86, funcs:avg(Column#166, Column#167)->Column#87, funcs:min(Column#168)->Column#88, funcs:sum(Column#169)->Column#89, funcs:max(Column#170)->Column#90, funcs:avg(Column#171, Column#172)->Column#91	152.0 MB	0 Bytes
    └─IndexReader_18	1.00	167600	root	partition:p20260401,p20260501,p20260601,pmax	time:2.18s, open:98.9µs, close:8.98µs, loops:11, cop_task: {num: 12, max: 2.26s, min: 1.08ms, avg: 255.5ms, p95: 2.26s, max_proc_keys: 116680, p95_proc_keys: 116680, tot_proc: 720ms, tot_wait: 516.5µs, copr_cache: disabled, build_task_duration: 21.2µs, max_distsql_concurrency: 4}, fetch_resp_duration: 2.18s, rpc_info:{Cop:{num_rpc:12, total_time:3.07s}}	index:HashAgg_11	147.1 MB	N/A
      └─HashAgg_11	1.00	167600	cop[tikv]		tikv_task:{proc max:1.08s, min:0s, avg: 131.7ms, p80:140ms, p95:1.08s, iters:171, tasks:12}, scan_detail: {total_process_keys: 172346, total_process_keys_size: 40578683, total_keys: 55677, get_snapshot_time: 265µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 720ms, total_suspend_time: 416.2µs, total_wait_time: 516.5µs, total_kv_read_wall_time: 30ms}	group by:intuit_risk.deviceprofile_fact.agent_type, intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.smart_id, funcs:count(?)->Column#141, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#142, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#143, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#144, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#145, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#146, funcs:sum(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?))->Column#147, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#148, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?))->Column#149, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#150, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#151, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY)))->Column#152, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#153, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?))->Column#154, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#155, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#156, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY)))->Column#157, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#158, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?))->Column#159, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#160, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#161, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY)))->Column#162, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#163, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?))->Column#164, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#165, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#166, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY)))->Column#167, funcs:min(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#168, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?))->Column#169, funcs:max(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#170, funcs:count(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#171, funcs:sum(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY)))->Column#172	N/A	N/A
        └─IndexRangeScan_16	359561.64	172346	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:120ms, min:0s, avg: 12.5ms, p80:10ms, p95:120ms, iters:171, tasks:12}	range:[? ?,? +inf], keep order:false	N/A	N/A
```

### tiflash_hint

- Engines: `tikv,tiflash,tidb`
- Elapsed: `5293.2 ms`
- Storage tasks: `mpp[tiflash], root`

```sql
SELECT /*+ READ_FROM_STORAGE(TIFLASH[d]) */
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
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=5293.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:5.29s, open:19.2ms, close:8.53µs, loops:2, RU:36440.10, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	38.7 KB	N/A
└─TableReader_34	0.80	1	root	partition:p20260401,p20260501,p20260601,pmax	time:5.29s, open:19.2ms, close:5.82µs, loops:2, cop_task: {num: 2, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache: disabled}, fetch_resp_duration: 5.27s	MppVersion: 3, data:ExchangeSender_33	3.04 KB	N/A
  └─ExchangeSender_33	0.80	1	mpp[tiflash]		tiflash_task:{time:5.26s, loops:1, threads:1}, tiflash_network: {inner_zone_send_bytes: 1355}	ExchangeType: PassThrough	N/A	N/A
    └─Selection_10	0.80	1	mpp[tiflash]		tiflash_task:{time:5.26s, loops:1, threads:1}	gt(Column#60, ?)	N/A	N/A
      └─Projection_29	1.00	1	mpp[tiflash]		tiflash_task:{time:5.26s, loops:1, threads:1}	Column#60, Column#61, Column#62, Column#63, Column#64, Column#65, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, div(Column#75, cast(case(eq(Column#177, ?), ?, Column#177), decimal(20,0) BINARY))->Column#75, Column#76, Column#77, Column#78, div(Column#79, cast(case(eq(Column#178, ?), ?, Column#178), decimal(20,0) BINARY))->Column#79, Column#80, Column#81, Column#82, div(Column#83, cast(case(eq(Column#179, ?), ?, Column#179), decimal(20,0) BINARY))->Column#83, Column#84, Column#85, Column#86, div(Column#87, cast(case(eq(Column#180, ?), ?, Column#180), decimal(20,0) BINARY))->Column#87, Column#88, Column#89, Column#90, div(Column#91, cast(case(eq(Column#181, ?), ?, Column#181), decimal(20,0) BINARY))->Column#91	N/A	N/A
        └─HashAgg_30	1.00	1	mpp[tiflash]		tiflash_task:{time:5.26s, loops:1, threads:1}	funcs:sum(Column#182)->Column#60, funcs:sum(Column#183)->Column#61, funcs:sum(Column#184)->Column#62, funcs:sum(Column#185)->Column#63, funcs:sum(Column#186)->Column#64, funcs:sum(Column#187)->Column#65, funcs:sum(Column#188)->Column#66, funcs:count(distinct intuit_risk.deviceprofile_fact.exact_id)->Column#67, funcs:count(distinct intuit_risk.deviceprofile_fact.smart_id)->Column#68, funcs:count(distinct intuit_risk.deviceprofile_fact.input_ip)->Column#69, funcs:count(distinct intuit_risk.deviceprofile_fact.proxy_ip)->Column#70, funcs:count(distinct intuit_risk.deviceprofile_fact.agent_type)->Column#71, funcs:min(Column#189)->Column#72, funcs:sum(Column#190)->Column#73, funcs:max(Column#191)->Column#74, funcs:sum(Column#192)->Column#177, funcs:sum(Column#193)->Column#75, funcs:min(Column#194)->Column#76, funcs:sum(Column#195)->Column#77, funcs:max(Column#196)->Column#78, funcs:sum(Column#197)->Column#178, funcs:sum(Column#198)->Column#79, funcs:min(Column#199)->Column#80, funcs:sum(Column#200)->Column#81, funcs:max(Column#201)->Column#82, funcs:sum(Column#202)->Column#179, funcs:sum(Column#203)->Column#83, funcs:min(Column#204)->Column#84, funcs:sum(Column#205)->Column#85, funcs:max(Column#206)->Column#86, funcs:sum(Column#207)->Column#180, funcs:sum(Column#208)->Column#87, funcs:min(Column#209)->Column#88, funcs:sum(Column#210)->Column#89, funcs:max(Column#211)->Column#90, funcs:sum(Column#212)->Column#181, funcs:sum(Column#213)->Column#91	N/A	N/A
          └─ExchangeReceiver_32	1.00	167603	mpp[tiflash]		tiflash_task:{time:5.24s, loops:63, threads:63}, tiflash_network: {inner_zone_receive_bytes: 13247572}		N/A	N/A
            └─ExchangeSender_31	1.00	167603	mpp[tiflash]		tiflash_task:{time:5.22s, loops:768, threads:189}, tiflash_network: {inner_zone_send_bytes: 13247572}	ExchangeType: PassThrough, Compression: FAST	N/A	N/A
              └─HashAgg_28	1.00	167603	mpp[tiflash]		tiflash_task:{time:5.22s, loops:768, threads:189}	group by:Column#245, Column#246, Column#247, Column#248, Column#249, funcs:count(?)->Column#182, funcs:sum(Column#214)->Column#183, funcs:sum(Column#215)->Column#184, funcs:sum(Column#216)->Column#185, funcs:sum(Column#217)->Column#186, funcs:sum(Column#218)->Column#187, funcs:sum(Column#219)->Column#188, funcs:min(Column#220)->Column#189, funcs:sum(Column#221)->Column#190, funcs:max(Column#222)->Column#191, funcs:count(Column#223)->Column#192, funcs:sum(Column#224)->Column#193, funcs:min(Column#225)->Column#194, funcs:sum(Column#226)->Column#195, funcs:max(Column#227)->Column#196, funcs:count(Column#228)->Column#197, funcs:sum(Column#229)->Column#198, funcs:min(Column#230)->Column#199, funcs:sum(Column#231)->Column#200, funcs:max(Column#232)->Column#201, funcs:count(Column#233)->Column#202, funcs:sum(Column#234)->Column#203, funcs:min(Column#235)->Column#204, funcs:sum(Column#236)->Column#205, funcs:max(Column#237)->Column#206, funcs:count(Column#238)->Column#207, funcs:sum(Column#239)->Column#208, funcs:min(Column#240)->Column#209, funcs:sum(Column#241)->Column#210, funcs:max(Column#242)->Column#211, funcs:count(Column#243)->Column#212, funcs:sum(Column#244)->Column#213	N/A	N/A
                └─Projection_38	359561.64	172346	mpp[tiflash]		tiflash_task:{time:5.2s, loops:1872, threads:189}	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#214, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#215, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#216, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#217, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#218, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#222, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#223, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#225, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#226, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#227, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#228, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#229, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#230, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#232, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#234, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#235, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#236, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#237, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#238, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#239, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#240, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#241, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#242, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#243, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#244, intuit_risk.deviceprofile_fact.exact_id->Column#245, intuit_risk.deviceprofile_fact.smart_id->Column#246, intuit_risk.deviceprofile_fact.input_ip->Column#247, intuit_risk.deviceprofile_fact.proxy_ip->Column#248, intuit_risk.deviceprofile_fact.agent_type->Column#249	N/A	N/A
                  └─Selection_21	359561.64	172346	mpp[tiflash]		tiflash_task:{time:5.2s, loops:1872, threads:189}	ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)	N/A	N/A
                    └─TableFullScan_20	738823.99	236398	mpp[tiflash]	table:d	tiflash_task:{time:5.2s, loops:1873, threads:189}, tiflash_network: {inner_zone_send_bytes: 30770, inter_zone_send_bytes: 2143919, inner_zone_receive_bytes: 30770, inter_zone_receive_bytes: 2143919}, tiflash_scan:{mvcc_input_rows:63397, mvcc_input_bytes:1077749, mvcc_output_rows:63397, local_regions:0, remote_regions:74, tot_learner_read:0ms, region_balance:{instance_num: 3, max/min: 27/22=1.227273}, delta_rows:0, delta_bytes:0, segments:372, stale_read_regions:0, tot_build_snapshot:0ms, tot_build_bitmap:2245ms, tot_build_inputstream:744171ms, min_local_stream:0ms, max_local_stream:0ms, min_remote_stream:3849ms, max_remote_stream:4880ms, dtfile:{data_scanned_rows:118605233, data_skipped_rows:118756589, mvcc_scanned_rows:56738, mvcc_skipped_rows:3121866, lm_filter_scanned_rows:118615540, lm_filter_skipped_rows:4262438, tot_rs_index_check:25174ms, tot_read:165477ms, disagg_cache_hit_bytes: 41181302474, disagg_cache_miss_bytes: 10262255019}}	pushed down filter:eq(intuit_risk.deviceprofile_fact.true_ip, ?), keep order:false, PartitionTableScan:true	N/A	N/A
```

### tiflash_only

- Engines: `tiflash,tidb`
- Elapsed: `621.8 ms`
- Storage tasks: `mpp[tiflash], root`

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
WHERE d.true_ip = %s AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=621.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Projection_7	0.80	1	root		time:615.7ms, open:3.3ms, close:7.5µs, loops:2, RU:36076.77, Concurrency:OFF	Column#60->Column#92, Column#61->Column#93, Column#61->Column#94, Column#62->Column#95, Column#62->Column#96, Column#63->Column#97, Column#63->Column#98, Column#64->Column#99, Column#64->Column#100, Column#65->Column#101, Column#65->Column#102, Column#66->Column#103, Column#66->Column#104, Column#67->Column#105, Column#68->Column#106, Column#69->Column#107, Column#70->Column#108, Column#71->Column#109, Column#72->Column#110, Column#73->Column#111, Column#74->Column#112, Column#73->Column#113, Column#75->Column#114, Column#73->Column#115, Column#76->Column#116, Column#77->Column#117, Column#78->Column#118, Column#77->Column#119, Column#79->Column#120, Column#77->Column#121, Column#80->Column#122, Column#81->Column#123, Column#82->Column#124, Column#81->Column#125, Column#83->Column#126, Column#81->Column#127, Column#84->Column#128, Column#85->Column#129, Column#86->Column#130, Column#85->Column#131, Column#87->Column#132, Column#85->Column#133, Column#88->Column#134, Column#89->Column#135, Column#90->Column#136, Column#89->Column#137, Column#91->Column#138, Column#89->Column#139	26.5 KB	N/A
└─TableReader_34	0.80	1	root	partition:p20260401,p20260501,p20260601,pmax	time:615.6ms, open:3.29ms, close:4.85µs, loops:2, cop_task: {num: 2, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache: disabled}, fetch_resp_duration: 612.3ms	MppVersion: 3, data:ExchangeSender_33	3.04 KB	N/A
  └─ExchangeSender_33	0.80	1	mpp[tiflash]		tiflash_task:{time:611.4ms, loops:1, threads:1}, tiflash_network: {inner_zone_send_bytes: 1355}	ExchangeType: PassThrough	N/A	N/A
    └─Selection_10	0.80	1	mpp[tiflash]		tiflash_task:{time:611.4ms, loops:1, threads:1}	gt(Column#60, ?)	N/A	N/A
      └─Projection_29	1.00	1	mpp[tiflash]		tiflash_task:{time:611.4ms, loops:1, threads:1}	Column#60, Column#61, Column#62, Column#63, Column#64, Column#65, Column#66, Column#67, Column#68, Column#69, Column#70, Column#71, Column#72, Column#73, Column#74, div(Column#75, cast(case(eq(Column#177, ?), ?, Column#177), decimal(20,0) BINARY))->Column#75, Column#76, Column#77, Column#78, div(Column#79, cast(case(eq(Column#178, ?), ?, Column#178), decimal(20,0) BINARY))->Column#79, Column#80, Column#81, Column#82, div(Column#83, cast(case(eq(Column#179, ?), ?, Column#179), decimal(20,0) BINARY))->Column#83, Column#84, Column#85, Column#86, div(Column#87, cast(case(eq(Column#180, ?), ?, Column#180), decimal(20,0) BINARY))->Column#87, Column#88, Column#89, Column#90, div(Column#91, cast(case(eq(Column#181, ?), ?, Column#181), decimal(20,0) BINARY))->Column#91	N/A	N/A
        └─HashAgg_30	1.00	1	mpp[tiflash]		tiflash_task:{time:611.4ms, loops:1, threads:1}	funcs:sum(Column#182)->Column#60, funcs:sum(Column#183)->Column#61, funcs:sum(Column#184)->Column#62, funcs:sum(Column#185)->Column#63, funcs:sum(Column#186)->Column#64, funcs:sum(Column#187)->Column#65, funcs:sum(Column#188)->Column#66, funcs:count(distinct intuit_risk.deviceprofile_fact.exact_id)->Column#67, funcs:count(distinct intuit_risk.deviceprofile_fact.smart_id)->Column#68, funcs:count(distinct intuit_risk.deviceprofile_fact.input_ip)->Column#69, funcs:count(distinct intuit_risk.deviceprofile_fact.proxy_ip)->Column#70, funcs:count(distinct intuit_risk.deviceprofile_fact.agent_type)->Column#71, funcs:min(Column#189)->Column#72, funcs:sum(Column#190)->Column#73, funcs:max(Column#191)->Column#74, funcs:sum(Column#192)->Column#177, funcs:sum(Column#193)->Column#75, funcs:min(Column#194)->Column#76, funcs:sum(Column#195)->Column#77, funcs:max(Column#196)->Column#78, funcs:sum(Column#197)->Column#178, funcs:sum(Column#198)->Column#79, funcs:min(Column#199)->Column#80, funcs:sum(Column#200)->Column#81, funcs:max(Column#201)->Column#82, funcs:sum(Column#202)->Column#179, funcs:sum(Column#203)->Column#83, funcs:min(Column#204)->Column#84, funcs:sum(Column#205)->Column#85, funcs:max(Column#206)->Column#86, funcs:sum(Column#207)->Column#180, funcs:sum(Column#208)->Column#87, funcs:min(Column#209)->Column#88, funcs:sum(Column#210)->Column#89, funcs:max(Column#211)->Column#90, funcs:sum(Column#212)->Column#181, funcs:sum(Column#213)->Column#91	N/A	N/A
          └─ExchangeReceiver_32	1.00	167603	mpp[tiflash]		tiflash_task:{time:591.4ms, loops:63, threads:63}, tiflash_network: {inner_zone_receive_bytes: 13240037}		N/A	N/A
            └─ExchangeSender_31	1.00	167603	mpp[tiflash]		tiflash_task:{time:559.1ms, loops:768, threads:189}, tiflash_network: {inner_zone_send_bytes: 13240037}	ExchangeType: PassThrough, Compression: FAST	N/A	N/A
              └─HashAgg_28	1.00	167603	mpp[tiflash]		tiflash_task:{time:559.1ms, loops:768, threads:189}	group by:Column#245, Column#246, Column#247, Column#248, Column#249, funcs:count(?)->Column#182, funcs:sum(Column#214)->Column#183, funcs:sum(Column#215)->Column#184, funcs:sum(Column#216)->Column#185, funcs:sum(Column#217)->Column#186, funcs:sum(Column#218)->Column#187, funcs:sum(Column#219)->Column#188, funcs:min(Column#220)->Column#189, funcs:sum(Column#221)->Column#190, funcs:max(Column#222)->Column#191, funcs:count(Column#223)->Column#192, funcs:sum(Column#224)->Column#193, funcs:min(Column#225)->Column#194, funcs:sum(Column#226)->Column#195, funcs:max(Column#227)->Column#196, funcs:count(Column#228)->Column#197, funcs:sum(Column#229)->Column#198, funcs:min(Column#230)->Column#199, funcs:sum(Column#231)->Column#200, funcs:max(Column#232)->Column#201, funcs:count(Column#233)->Column#202, funcs:sum(Column#234)->Column#203, funcs:min(Column#235)->Column#204, funcs:sum(Column#236)->Column#205, funcs:max(Column#237)->Column#206, funcs:count(Column#238)->Column#207, funcs:sum(Column#239)->Column#208, funcs:min(Column#240)->Column#209, funcs:sum(Column#241)->Column#210, funcs:max(Column#242)->Column#211, funcs:count(Column#243)->Column#212, funcs:sum(Column#244)->Column#213	N/A	N/A
                └─Projection_38	359561.64	172346	mpp[tiflash]		tiflash_task:{time:549.1ms, loops:1872, threads:189}	cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#214, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#215, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#216, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#217, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#218, cast(case(eq(intuit_risk.deviceprofile_fact.agent_type, ?), ?, ?), decimal(20,0) BINARY)->Column#219, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#220, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#221, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#222, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#223, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_score)), ne(intuit_risk.deviceprofile_fact.device_score, ?)), cast(intuit_risk.deviceprofile_fact.device_score, decimal(10,2) BINARY))->Column#224, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#225, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#226, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#227, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#228, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_fingerprint_score)), ne(intuit_risk.deviceprofile_fact.device_fingerprint_score, ?)), cast(intuit_risk.deviceprofile_fact.device_fingerprint_score, decimal(10,2) BINARY))->Column#229, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#230, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#231, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#232, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#233, case(and(not(isnull(intuit_risk.deviceprofile_fact.device_worst_score)), ne(intuit_risk.deviceprofile_fact.device_worst_score, ?)), cast(intuit_risk.deviceprofile_fact.device_worst_score, decimal(10,2) BINARY))->Column#234, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#235, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#236, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#237, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#238, case(and(not(isnull(intuit_risk.deviceprofile_fact.true_ip_score)), ne(intuit_risk.deviceprofile_fact.true_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.true_ip_score, decimal(10,2) BINARY))->Column#239, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#240, cast(case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), ?, ?), decimal(20,0) BINARY)->Column#241, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#242, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#243, case(and(not(isnull(intuit_risk.deviceprofile_fact.input_ip_score)), ne(intuit_risk.deviceprofile_fact.input_ip_score, ?)), cast(intuit_risk.deviceprofile_fact.input_ip_score, decimal(10,2) BINARY))->Column#244, intuit_risk.deviceprofile_fact.exact_id->Column#245, intuit_risk.deviceprofile_fact.smart_id->Column#246, intuit_risk.deviceprofile_fact.input_ip->Column#247, intuit_risk.deviceprofile_fact.proxy_ip->Column#248, intuit_risk.deviceprofile_fact.agent_type->Column#249	N/A	N/A
                  └─Selection_21	359561.64	172346	mpp[tiflash]		tiflash_task:{time:549.1ms, loops:1872, threads:189}	ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?)	N/A	N/A
                    └─TableFullScan_20	738823.99	236398	mpp[tiflash]	table:d	tiflash_task:{time:549.1ms, loops:1873, threads:189}, tiflash_network: {inner_zone_send_bytes: 30770, inter_zone_send_bytes: 86960, inner_zone_receive_bytes: 30770, inter_zone_receive_bytes: 86960}, tiflash_scan:{mvcc_input_rows:63397, mvcc_input_bytes:1077749, mvcc_output_rows:63397, local_regions:0, remote_regions:74, tot_learner_read:0ms, region_balance:{instance_num: 3, max/min: 27/22=1.227273}, delta_rows:0, delta_bytes:0, segments:372, stale_read_regions:0, tot_build_snapshot:0ms, tot_build_bitmap:12ms, tot_build_inputstream:26976ms, min_local_stream:0ms, max_local_stream:0ms, min_remote_stream:139ms, max_remote_stream:509ms, dtfile:{data_scanned_rows:118605233, data_skipped_rows:118756589, mvcc_scanned_rows:56738, mvcc_skipped_rows:3121866, lm_filter_scanned_rows:118615540, lm_filter_skipped_rows:4262438, tot_rs_index_check:7ms, tot_read:27921ms, disagg_cache_hit_bytes: 17462118983, disagg_cache_miss_bytes: 446992926}}	pushed down filter:eq(intuit_risk.deviceprofile_fact.true_ip, ?), keep order:false, PartitionTableScan:true	N/A	N/A
```

## 2. group_b_bundle_018

- Group/window/filter: `B` / `180d` / `d.input_ip = %s`
- Preagg applied: `True`
- Event: invoice=`INV0019249439` kind=`hot_input_ip` hot_field=`input_ip` hot_count=`719377` ref=`2026-04-10T22:19:54.592000`

### Params

```json
[
  "74.179.68.52",
  "74.179.68.52"
]
```

### tikv

- Engines: `tikv,tidb`
- Elapsed: `1115.7 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.true_ip AS `raw_distinct_2`,
    d.agent_type AS `raw_distinct_3`
  FROM deviceprofile_fact d
  WHERE d.input_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 22:19:54.592000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
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

```text
-- explain_analyze_elapsed_ms=1115.7
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_63	1.00	1	root		time:1.11s, open:10.3µs, close:65.2µs, loops:2, RU:3433.47	funcs:count(distinct Column#161)->Column#128, funcs:count(distinct Column#162)->Column#129, funcs:count(distinct Column#163)->Column#130, funcs:count(distinct Column#164)->Column#131	56.9 MB	0 Bytes
└─Projection_106	2340270.98	1533348	root		time:497.3ms, open:2.98µs, close:64.2µs, loops:1502, Concurrency:5	case(eq(Column#126, ?), Column#127)->Column#161, case(eq(Column#126, ?), Column#127)->Column#162, case(eq(Column#126, ?), Column#127)->Column#163, case(eq(Column#126, ?), Column#127)->Column#164	893.3 KB	N/A
  └─Union_65	2340270.98	1533348	root		time:504.3ms, open:919ns, close:43.3µs, loops:1502		N/A	N/A
    ├─Projection_67	2340266.27	1533348	root		time:504.3ms, open:995.4µs, close:26.1µs, loops:1502, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#126, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	910.8 KB	N/A
    │ └─IndexReader_70	2340266.27	1533348	root		time:507.9ms, open:993.7µs, close:10.9µs, loops:1502, cop_task: {num: 29, max: 536.5ms, min: 934.5µs, avg: 82.4ms, p95: 481.7ms, max_proc_keys: 345056, p95_proc_keys: 289760, tot_proc: 1.03s, tot_wait: 5.85ms, copr_cache: disabled, build_task_duration: 938.9µs, max_distsql_concurrency: 4}, fetch_resp_duration: 501.8ms, rpc_info:{Cop:{num_rpc:29, total_time:2.39s}}	index:IndexRangeScan_69	96.2 MB	N/A
    │   └─IndexRangeScan_69	2340266.27	1533348	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:190ms, min:0s, avg: 35.2ms, p80:40ms, p95:190ms, iters:1610, tasks:29}, scan_detail: {total_process_keys: 1533348, total_process_keys_size: 201682727, total_keys: 169419, get_snapshot_time: 5.49ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.03s, total_suspend_time: 461.9µs, total_wait_time: 5.85ms, total_kv_read_wall_time: 210ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_71	1.18	0	root		time:3.17ms, open:1.38ms, close:10.2µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_73	1.18	0	root		time:3.16ms, open:1.38ms, close:7.94µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	2.48 KB	N/A
    │   └─CTEFullScan_75	1.47	0	root	CTE:raw_boundary	time:3.15ms, open:1.37ms, close:6.8µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_79	1.18	0	root		time:3.15ms, open:3.15ms, close:1.67µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_81	1.18	0	root		time:3.15ms, open:3.15ms, close:762ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	2.48 KB	N/A
    │   └─CTEFullScan_83	1.47	0	root	CTE:raw_boundary	time:3.14ms, open:3.14ms, close:185ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_87	1.18	0	root		time:3.16ms, open:3.16ms, close:1.94µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_89	1.18	0	root		time:3.16ms, open:3.16ms, close:757ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	2.48 KB	N/A
    │   └─CTEFullScan_91	1.47	0	root	CTE:raw_boundary	time:3.14ms, open:3.14ms, close:159ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_95	1.18	0	root		time:3.11ms, open:3.11ms, close:2.2µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
      └─Selection_97	1.18	0	root		time:3.11ms, open:3.1ms, close:664ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	2.48 KB	N/A
        └─CTEFullScan_99	1.47	0	root	CTE:raw_boundary	time:3.1ms, open:3.1ms, close:175ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.47	0	root		time:3.15ms, open:1.37ms, close:6.8µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_50(Seed Part)	1.47	0	root		time:3.08ms, open:1.36ms, close:4.95µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.agent_type	3.48 KB	N/A
  └─IndexReader_55	1.83	0	root	partition:p20251101	time:3.07ms, open:1.36ms, close:3.44µs, loops:1, cop_task: {num: 1, max: 1.68ms, proc_keys: 0, tot_proc: 28.9µs, tot_wait: 653.7µs, copr_cache: disabled, build_task_duration: 1.32ms, max_distsql_concurrency: 1}, fetch_resp_duration: 1.69ms, rpc_info:{Cop:{num_rpc:1, total_time:1.67ms}}	index:Selection_54	255 Bytes	N/A
    └─Selection_54	1.83	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 628µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.9µs, total_wait_time: 653.7µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type))))	N/A	N/A
      └─IndexRangeScan_53	1.84	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### cost

- Engines: `tikv,tiflash,tidb`
- Elapsed: `1110.2 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.true_ip AS `raw_distinct_2`,
    d.agent_type AS `raw_distinct_3`
  FROM deviceprofile_fact d
  WHERE d.input_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 22:19:54.592000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
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

```text
-- explain_analyze_elapsed_ms=1110.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_72	1.00	1	root		time:1.1s, open:8.72µs, close:69.9µs, loops:2, RU:3417.54	funcs:count(distinct Column#161)->Column#128, funcs:count(distinct Column#162)->Column#129, funcs:count(distinct Column#163)->Column#130, funcs:count(distinct Column#164)->Column#131	56.9 MB	0 Bytes
└─Projection_115	2340270.98	1533348	root		time:512.7ms, open:2.07µs, close:68.8µs, loops:1502, Concurrency:5	case(eq(Column#126, ?), Column#127)->Column#161, case(eq(Column#126, ?), Column#127)->Column#162, case(eq(Column#126, ?), Column#127)->Column#163, case(eq(Column#126, ?), Column#127)->Column#164	891.9 KB	N/A
  └─Union_74	2340270.98	1533348	root		time:520.9ms, open:809ns, close:49.4µs, loops:1502		N/A	N/A
    ├─Projection_76	2340266.27	1533348	root		time:519.4ms, open:97.7µs, close:28.7µs, loops:1502, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#126, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	911.3 KB	N/A
    │ └─IndexReader_79	2340266.27	1533348	root		time:522.8ms, open:96.8µs, close:12.5µs, loops:1502, cop_task: {num: 29, max: 497.6ms, min: 868.2µs, avg: 80ms, p95: 485.4ms, max_proc_keys: 345056, p95_proc_keys: 289760, tot_proc: 977.5ms, tot_wait: 766.6µs, copr_cache: disabled, build_task_duration: 28.4µs, max_distsql_concurrency: 4}, fetch_resp_duration: 518.2ms, rpc_info:{Cop:{num_rpc:29, total_time:2.32s}}	index:IndexRangeScan_78	96.2 MB	N/A
    │   └─IndexRangeScan_78	2340266.27	1533348	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:200ms, min:0s, avg: 32.8ms, p80:30ms, p95:180ms, iters:1610, tasks:29}, scan_detail: {total_process_keys: 1533348, total_process_keys_size: 201682727, total_keys: 169419, get_snapshot_time: 413.3µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 977.5ms, total_suspend_time: 402µs, total_wait_time: 766.6µs, total_kv_read_wall_time: 150ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_80	1.18	0	root		time:1.22ms, open:77.5µs, close:11.9µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_82	1.18	0	root		time:1.21ms, open:74.7µs, close:9.16µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	2.48 KB	N/A
    │   └─CTEFullScan_84	1.47	0	root	CTE:raw_boundary	time:1.2ms, open:71.5µs, close:7.97µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_88	1.18	0	root		time:1.22ms, open:1.21ms, close:3.14µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_90	1.18	0	root		time:1.21ms, open:1.21ms, close:1.11µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	2.48 KB	N/A
    │   └─CTEFullScan_92	1.47	0	root	CTE:raw_boundary	time:1.21ms, open:1.2ms, close:131ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_96	1.18	0	root		time:1.22ms, open:1.21ms, close:2.24µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	3.11 KB	N/A
    │ └─Selection_98	1.18	0	root		time:1.22ms, open:1.21ms, close:669ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	6.48 KB	N/A
    │   └─CTEFullScan_100	1.47	0	root	CTE:raw_boundary	time:1.21ms, open:1.21ms, close:127ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_104	1.18	0	root		time:1.23ms, open:1.22ms, close:2.25µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	41.7 KB	N/A
      └─Selection_106	1.18	0	root		time:1.22ms, open:1.22ms, close:671ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	18.2 KB	N/A
        └─CTEFullScan_108	1.47	0	root	CTE:raw_boundary	time:1.22ms, open:1.22ms, close:105ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.47	0	root		time:1.2ms, open:71.5µs, close:7.97µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_50(Seed Part)	1.47	0	root		time:1.19ms, open:68.4µs, close:6.3µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.agent_type	3.48 KB	N/A
  └─IndexReader_59	1.83	0	root	partition:p20251101	time:1.18ms, open:64.2µs, close:4.48µs, loops:1, cop_task: {num: 1, max: 1.09ms, proc_keys: 0, tot_proc: 31.4µs, tot_wait: 50.5µs, copr_cache: disabled, build_task_duration: 19.2µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.11ms, rpc_info:{Cop:{num_rpc:1, total_time:1.08ms}}	index:Selection_58	255 Bytes	N/A
    └─Selection_58	1.83	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 24.1µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 31.4µs, total_wait_time: 50.5µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type))))	N/A	N/A
      └─IndexRangeScan_57	1.84	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### tiflash_hint

- Engines: `tikv,tiflash,tidb`
- Elapsed: `1155.2 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.true_ip AS `raw_distinct_2`,
    d.agent_type AS `raw_distinct_3`
  FROM deviceprofile_fact d
  WHERE d.input_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 22:19:54.592000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
), distinct_values AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
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

```text
-- explain_analyze_elapsed_ms=1155.2
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_72	1.00	1	root		time:1.15s, open:9.82µs, close:70.2µs, loops:2, RU:3428.98	funcs:count(distinct Column#161)->Column#128, funcs:count(distinct Column#162)->Column#129, funcs:count(distinct Column#163)->Column#130, funcs:count(distinct Column#164)->Column#131	56.9 MB	0 Bytes
└─Projection_115	2340270.98	1533348	root		time:542ms, open:2.9µs, close:69.3µs, loops:1502, Concurrency:5	case(eq(Column#126, ?), Column#127)->Column#161, case(eq(Column#126, ?), Column#127)->Column#162, case(eq(Column#126, ?), Column#127)->Column#163, case(eq(Column#126, ?), Column#127)->Column#164	891.1 KB	N/A
  └─Union_74	2340270.98	1533348	root		time:552.2ms, open:800ns, close:45.7µs, loops:1502		N/A	N/A
    ├─Projection_76	2340266.27	1533348	root		time:552.6ms, open:95.5µs, close:26.5µs, loops:1502, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#126, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	908.1 KB	N/A
    │ └─IndexReader_79	2340266.27	1533348	root		time:559.7ms, open:94.2µs, close:12.6µs, loops:1502, cop_task: {num: 29, max: 480.6ms, min: 970.4µs, avg: 78.3ms, p95: 471.4ms, max_proc_keys: 345056, p95_proc_keys: 289760, tot_proc: 1.01s, tot_wait: 712.7µs, copr_cache: disabled, build_task_duration: 29.1µs, max_distsql_concurrency: 4}, fetch_resp_duration: 555ms, rpc_info:{Cop:{num_rpc:29, total_time:2.27s}}	index:IndexRangeScan_78	96.2 MB	N/A
    │   └─IndexRangeScan_78	2340266.27	1533348	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:190ms, min:0s, avg: 34.5ms, p80:40ms, p95:190ms, iters:1610, tasks:29}, scan_detail: {total_process_keys: 1533348, total_process_keys_size: 201682727, total_keys: 169419, get_snapshot_time: 373.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.01s, total_suspend_time: 415.1µs, total_wait_time: 712.7µs, total_kv_read_wall_time: 160ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_80	1.18	0	root		time:1.35ms, open:76.8µs, close:10.4µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_82	1.18	0	root		time:1.34ms, open:73.1µs, close:8.19µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	2.48 KB	N/A
    │   └─CTEFullScan_84	1.47	0	root	CTE:raw_boundary	time:1.33ms, open:70.1µs, close:6.83µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_88	1.18	0	root		time:1.35ms, open:1.34ms, close:2.82µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	2.48 KB	N/A
    │ └─Selection_90	1.18	0	root		time:1.34ms, open:1.34ms, close:1.2µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	2.48 KB	N/A
    │   └─CTEFullScan_92	1.47	0	root	CTE:raw_boundary	time:1.34ms, open:1.34ms, close:176ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_96	1.18	0	root		time:1.35ms, open:1.35ms, close:2.03µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.true_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	3.11 KB	N/A
    │ └─Selection_98	1.18	0	root		time:1.35ms, open:1.34ms, close:1µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.true_ip))	6.48 KB	N/A
    │   └─CTEFullScan_100	1.47	0	root	CTE:raw_boundary	time:1.34ms, open:1.34ms, close:123ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_104	1.18	0	root		time:1.36ms, open:1.35ms, close:2.47µs, loops:1, Concurrency:OFF	?->Column#126, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#127	24.1 KB	N/A
      └─Selection_106	1.18	0	root		time:1.35ms, open:1.35ms, close:1.09µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	18.1 KB	N/A
        └─CTEFullScan_108	1.47	0	root	CTE:raw_boundary	time:1.35ms, open:1.35ms, close:71ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.47	0	root		time:1.33ms, open:70.1µs, close:6.83µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_50(Seed Part)	1.47	0	root		time:1.32ms, open:67.3µs, close:5.28µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.true_ip, intuit_risk.deviceprofile_fact.agent_type	3.48 KB	N/A
  └─IndexReader_59	1.83	0	root	partition:p20251101	time:1.31ms, open:63.4µs, close:3.89µs, loops:1, cop_task: {num: 1, max: 1.22ms, proc_keys: 0, tot_proc: 28.1µs, tot_wait: 45.7µs, copr_cache: disabled, build_task_duration: 18.3µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.24ms, rpc_info:{Cop:{num_rpc:1, total_time:1.21ms}}	index:Selection_58	255 Bytes	N/A
    └─Selection_58	1.83	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 23.2µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.1µs, total_wait_time: 45.7µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.true_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type))))	N/A	N/A
      └─IndexRangeScan_57	1.84	0	cop[tikv]	table:d, index:idx_dev_input_runtime_cov(input_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip_score, smart_id, true_ip, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### tiflash_only

- Engines: `tiflash,tidb`
- Elapsed: `2.3 ms`
- Error: `(1815, "Internal : No access path for table 'x' is found with 'tidb_isolation_read_engines' = 'tiflash,tidb', valid values can be 'tikv'.")`

## 3. group_b_bundle_020

- Group/window/filter: `B` / `180d` / `d.true_ip = %s`
- Preagg applied: `True`
- Event: invoice=`INV0007589128` kind=`hot_true_ip` hot_field=`true_ip` hot_count=`738824` ref=`2026-04-10T23:06:57.563000`

### Params

```json
[
  "72.153.231.69",
  "72.153.231.69"
]
```

### tikv

- Engines: `tikv,tidb`
- Elapsed: `1167.1 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.input_ip AS `raw_distinct_2`,
    d.proxy_ip AS `raw_distinct_3`,
    d.agent_type AS `raw_distinct_4`
  FROM deviceprofile_fact d
  WHERE d.true_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 23:06:57.563000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
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

```text
-- explain_analyze_elapsed_ms=1167.1
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_71	1.00	1	root		time:1.16s, open:11µs, close:69.9µs, loops:2, RU:3549.89	funcs:count(distinct Column#188)->Column#150, funcs:count(distinct Column#189)->Column#151, funcs:count(distinct Column#190)->Column#152, funcs:count(distinct Column#191)->Column#153, funcs:count(distinct Column#192)->Column#154	57.1 MB	0 Bytes
└─Projection_122	2121046.92	1557792	root		time:487.5ms, open:1.98µs, close:68.9µs, loops:1526, Concurrency:5	case(eq(Column#148, ?), Column#149)->Column#188, case(eq(Column#148, ?), Column#149)->Column#189, case(eq(Column#148, ?), Column#149)->Column#190, case(eq(Column#148, ?), Column#149)->Column#191, case(eq(Column#148, ?), Column#149)->Column#192	998.9 KB	N/A
  └─Union_73	2121046.92	1557792	root		time:496.8ms, open:725ns, close:47.7µs, loops:1526		N/A	N/A
    ├─Projection_75	2121041.42	1557792	root		time:497ms, open:810.2µs, close:26.5µs, loops:1526, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#148, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	915.9 KB	N/A
    │ └─IndexReader_78	2121041.42	1557792	root		time:502.6ms, open:806.9µs, close:10.7µs, loops:1526, cop_task: {num: 38, max: 483.9ms, min: 1.04ms, avg: 64.1ms, p95: 468.5ms, max_proc_keys: 341984, p95_proc_keys: 286688, tot_proc: 1.07s, tot_wait: 5.68ms, copr_cache: disabled, build_task_duration: 737.4µs, max_distsql_concurrency: 5}, fetch_resp_duration: 496.7ms, rpc_info:{Cop:{num_rpc:38, total_time:2.44s}}	index:IndexRangeScan_77	96.1 MB	N/A
    │   └─IndexRangeScan_77	2121041.42	1557792	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:180ms, min:0s, avg: 27.1ms, p80:20ms, p95:180ms, iters:1668, tasks:38}, scan_detail: {total_process_keys: 1557792, total_process_keys_size: 208062197, total_keys: 198097, get_snapshot_time: 5.14ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.07s, total_suspend_time: 490.8µs, total_wait_time: 5.68ms, total_kv_read_wall_time: 220ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_79	1.10	0	root		time:1.42ms, open:89.7µs, close:11.1µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_81	1.10	0	root		time:1.41ms, open:87.4µs, close:9.24µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	3.11 KB	N/A
    │   └─CTEFullScan_83	1.37	0	root	CTE:raw_boundary	time:1.41ms, open:83.8µs, close:7.82µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_87	1.10	0	root		time:1.43ms, open:1.43ms, close:2.58µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_89	1.10	0	root		time:1.43ms, open:1.43ms, close:607ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	3.11 KB	N/A
    │   └─CTEFullScan_91	1.37	0	root	CTE:raw_boundary	time:1.42ms, open:1.42ms, close:123ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_95	1.10	0	root		time:1.44ms, open:1.44ms, close:2.18µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_97	1.10	0	root		time:1.44ms, open:1.43ms, close:847ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	3.11 KB	N/A
    │   └─CTEFullScan_99	1.37	0	root	CTE:raw_boundary	time:1.43ms, open:1.43ms, close:154ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_103	1.10	0	root		time:1.45ms, open:1.44ms, close:1.92µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_105	1.10	0	root		time:1.44ms, open:1.44ms, close:647ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	3.11 KB	N/A
    │   └─CTEFullScan_107	1.37	0	root	CTE:raw_boundary	time:1.44ms, open:1.44ms, close:163ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_111	1.10	0	root		time:15.1µs, open:10.1µs, close:1.76µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
      └─Selection_113	1.10	0	root		time:10.1µs, open:7.51µs, close:727ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.11 KB	N/A
        └─CTEFullScan_115	1.37	0	root	CTE:raw_boundary	time:1.59µs, open:442ns, close:82ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.37	0	root		time:1.41ms, open:83.8µs, close:7.82µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_58(Seed Part)	1.37	0	root		time:1.39ms, open:80.5µs, close:5.79µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type	4.10 KB	N/A
  └─IndexReader_63	1.71	0	root	partition:p20251101	time:1.38ms, open:74.6µs, close:4.27µs, loops:1, cop_task: {num: 1, max: 1.27ms, proc_keys: 0, tot_proc: 28.5µs, tot_wait: 52.6µs, copr_cache: disabled, build_task_duration: 22.7µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.29ms, rpc_info:{Cop:{num_rpc:1, total_time:1.25ms}}	index:Selection_62	255 Bytes	N/A
    └─Selection_62	1.71	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 26.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 28.5µs, total_wait_time: 52.6µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type)))))	N/A	N/A
      └─IndexRangeScan_61	1.72	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### cost

- Engines: `tikv,tiflash,tidb`
- Elapsed: `1151.0 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.input_ip AS `raw_distinct_2`,
    d.proxy_ip AS `raw_distinct_3`,
    d.agent_type AS `raw_distinct_4`
  FROM deviceprofile_fact d
  WHERE d.true_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 23:06:57.563000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
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

```text
-- explain_analyze_elapsed_ms=1151.0
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_80	1.00	1	root		time:1.14s, open:10.3µs, close:59.2µs, loops:2, RU:3538.41	funcs:count(distinct Column#188)->Column#150, funcs:count(distinct Column#189)->Column#151, funcs:count(distinct Column#190)->Column#152, funcs:count(distinct Column#191)->Column#153, funcs:count(distinct Column#192)->Column#154	57.1 MB	0 Bytes
└─Projection_131	2121046.92	1557792	root		time:462.7ms, open:3.12µs, close:58µs, loops:1527, Concurrency:5	case(eq(Column#148, ?), Column#149)->Column#188, case(eq(Column#148, ?), Column#149)->Column#189, case(eq(Column#148, ?), Column#149)->Column#190, case(eq(Column#148, ?), Column#149)->Column#191, case(eq(Column#148, ?), Column#149)->Column#192	996.1 KB	N/A
  └─Union_82	2121046.92	1557792	root		time:471.9ms, open:878ns, close:39.6µs, loops:1527		N/A	N/A
    ├─Projection_84	2121041.42	1557792	root		time:471.1ms, open:94.9µs, close:19.5µs, loops:1527, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#148, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	915.2 KB	N/A
    │ └─IndexReader_87	2121041.42	1557792	root		time:477.9ms, open:93.9µs, close:9.97µs, loops:1527, cop_task: {num: 38, max: 473.7ms, min: 1.01ms, avg: 61.1ms, p95: 450.1ms, max_proc_keys: 341984, p95_proc_keys: 286688, tot_proc: 1.04s, tot_wait: 1.06ms, copr_cache: disabled, build_task_duration: 33µs, max_distsql_concurrency: 5}, fetch_resp_duration: 472.2ms, rpc_info:{Cop:{num_rpc:38, total_time:2.32s}}	index:IndexRangeScan_86	96.1 MB	N/A
    │   └─IndexRangeScan_86	2121041.42	1557792	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:200ms, min:0s, avg: 27.1ms, p80:20ms, p95:180ms, iters:1668, tasks:38}, scan_detail: {total_process_keys: 1557792, total_process_keys_size: 208062197, total_keys: 198097, get_snapshot_time: 537.6µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.04s, total_suspend_time: 460.4µs, total_wait_time: 1.06ms, total_kv_read_wall_time: 220ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_88	1.10	0	root		time:1.22ms, open:76.8µs, close:10µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_90	1.10	0	root		time:1.21ms, open:74.1µs, close:8.13µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	3.11 KB	N/A
    │   └─CTEFullScan_92	1.37	0	root	CTE:raw_boundary	time:1.2ms, open:70.4µs, close:6.97µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_96	1.10	0	root		time:1.22ms, open:1.21ms, close:2.6µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_98	1.10	0	root		time:1.22ms, open:1.21ms, close:1.05µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	3.11 KB	N/A
    │   └─CTEFullScan_100	1.37	0	root	CTE:raw_boundary	time:1.21ms, open:1.21ms, close:113ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_104	1.10	0	root		time:1.22ms, open:1.22ms, close:1.86µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.98 KB	N/A
    │ └─Selection_106	1.10	0	root		time:1.22ms, open:1.22ms, close:591ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	8.61 KB	N/A
    │   └─CTEFullScan_108	1.37	0	root	CTE:raw_boundary	time:1.22ms, open:1.21ms, close:104ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_112	1.10	0	root		time:1.23ms, open:1.22ms, close:2.67µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	62.0 KB	N/A
    │ └─Selection_114	1.10	0	root		time:1.22ms, open:1.22ms, close:913ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	3.11 KB	N/A
    │   └─CTEFullScan_116	1.37	0	root	CTE:raw_boundary	time:1.22ms, open:1.22ms, close:131ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_120	1.10	0	root		time:9.47µs, open:5.23µs, close:1.78µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
      └─Selection_122	1.10	0	root		time:5.44µs, open:3.41µs, close:540ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.11 KB	N/A
        └─CTEFullScan_124	1.37	0	root	CTE:raw_boundary	time:1.06µs, open:305ns, close:123ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.37	0	root		time:1.2ms, open:70.4µs, close:6.97µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_58(Seed Part)	1.37	0	root		time:1.19ms, open:67.1µs, close:5.43µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type	4.10 KB	N/A
  └─IndexReader_67	1.71	0	root	partition:p20251101	time:1.18ms, open:61.8µs, close:4.09µs, loops:1, cop_task: {num: 1, max: 1.1ms, proc_keys: 0, tot_proc: 29.5µs, tot_wait: 51.5µs, copr_cache: disabled, build_task_duration: 19µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.11ms, rpc_info:{Cop:{num_rpc:1, total_time:1.08ms}}	index:Selection_66	255 Bytes	N/A
    └─Selection_66	1.71	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 25.5µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 29.5µs, total_wait_time: 51.5µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type)))))	N/A	N/A
      └─IndexRangeScan_65	1.72	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### tiflash_hint

- Engines: `tikv,tiflash,tidb`
- Elapsed: `1133.6 ms`
- Storage tasks: `cop[tikv], root`

```sql
WITH raw_boundary AS (
  SELECT
    d.exact_id AS `raw_distinct_0`,
    d.smart_id AS `raw_distinct_1`,
    d.input_ip AS `raw_distinct_2`,
    d.proxy_ip AS `raw_distinct_3`,
    d.agent_type AS `raw_distinct_4`
  FROM deviceprofile_fact d
  WHERE d.true_ip = %s AND d.jms_timestamp IS NOT NULL AND d.jms_timestamp >= '2025-10-12 23:06:57.563000' AND d.jms_timestamp < '2025-10-13 00:00:00.000000'
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

```text
-- explain_analyze_elapsed_ms=1133.6
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_80	1.00	1	root		time:1.13s, open:8.96µs, close:67.5µs, loops:2, RU:3541.21	funcs:count(distinct Column#188)->Column#150, funcs:count(distinct Column#189)->Column#151, funcs:count(distinct Column#190)->Column#152, funcs:count(distinct Column#191)->Column#153, funcs:count(distinct Column#192)->Column#154	57.1 MB	0 Bytes
└─Projection_131	2121046.92	1557792	root		time:450.3ms, open:1.79µs, close:66.6µs, loops:1526, Concurrency:5	case(eq(Column#148, ?), Column#149)->Column#188, case(eq(Column#148, ?), Column#149)->Column#189, case(eq(Column#148, ?), Column#149)->Column#190, case(eq(Column#148, ?), Column#149)->Column#191, case(eq(Column#148, ?), Column#149)->Column#192	997.3 KB	N/A
  └─Union_82	2121046.92	1557792	root		time:458.4ms, open:743ns, close:44.7µs, loops:1526		N/A	N/A
    ├─Projection_84	2121041.42	1557792	root		time:459.3ms, open:99.2µs, close:26µs, loops:1526, Concurrency:5	intuit_risk.group_b_180d_daily_distinct.template_id->Column#148, cast(intuit_risk.group_b_180d_daily_distinct.distinct_value, varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	919.6 KB	N/A
    │ └─IndexReader_87	2121041.42	1557792	root		time:466.5ms, open:97.7µs, close:10.5µs, loops:1526, cop_task: {num: 38, max: 467.9ms, min: 860.9µs, avg: 60.3ms, p95: 454.3ms, max_proc_keys: 341984, p95_proc_keys: 286688, tot_proc: 1.04s, tot_wait: 1.02ms, copr_cache: disabled, build_task_duration: 37.6µs, max_distsql_concurrency: 5}, fetch_resp_duration: 461.4ms, rpc_info:{Cop:{num_rpc:38, total_time:2.29s}}	index:IndexRangeScan_86	96.1 MB	N/A
    │   └─IndexRangeScan_86	2121041.42	1557792	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:200ms, min:0s, avg: 27.4ms, p80:10ms, p95:190ms, iters:1668, tasks:38}, scan_detail: {total_process_keys: 1557792, total_process_keys_size: 208062197, total_keys: 198097, get_snapshot_time: 515.4µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.04s, total_suspend_time: 461.6µs, total_wait_time: 1.02ms, total_kv_read_wall_time: 220ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
    ├─Projection_88	1.10	0	root		time:1.31ms, open:73.8µs, close:10.4µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.exact_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_90	1.10	0	root		time:1.3ms, open:70.2µs, close:8.16µs, loops:1	not(isnull(intuit_risk.deviceprofile_fact.exact_id))	3.11 KB	N/A
    │   └─CTEFullScan_92	1.37	0	root	CTE:raw_boundary	time:1.3ms, open:66.5µs, close:7.15µs, loops:1	data:CTE_0	0 Bytes	0 Bytes
    ├─Projection_96	1.10	0	root		time:1.32ms, open:1.31ms, close:2.28µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.smart_id, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
    │ └─Selection_98	1.10	0	root		time:1.31ms, open:1.31ms, close:907ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.smart_id))	3.11 KB	N/A
    │   └─CTEFullScan_100	1.37	0	root	CTE:raw_boundary	time:1.31ms, open:1.31ms, close:84ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_104	1.10	0	root		time:1.32ms, open:1.32ms, close:1.7µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.input_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.98 KB	N/A
    │ └─Selection_106	1.10	0	root		time:1.32ms, open:1.32ms, close:722ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.input_ip))	8.61 KB	N/A
    │   └─CTEFullScan_108	1.37	0	root	CTE:raw_boundary	time:1.31ms, open:1.31ms, close:87ns, loops:1	data:CTE_0	N/A	N/A
    ├─Projection_112	1.10	0	root		time:1.33ms, open:1.32ms, close:1.87µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.proxy_ip, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	62.0 KB	N/A
    │ └─Selection_114	1.10	0	root		time:1.32ms, open:1.32ms, close:854ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.proxy_ip))	3.11 KB	N/A
    │   └─CTEFullScan_116	1.37	0	root	CTE:raw_boundary	time:1.32ms, open:1.32ms, close:135ns, loops:1	data:CTE_0	N/A	N/A
    └─Projection_120	1.10	0	root		time:10.8µs, open:6.67µs, close:1.39µs, loops:1, Concurrency:OFF	?->Column#148, cast(cast(intuit_risk.deviceprofile_fact.agent_type, var_string(256)), varchar(257) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)->Column#149	3.11 KB	N/A
      └─Selection_122	1.10	0	root		time:7.5µs, open:4.87µs, close:778ns, loops:1	not(isnull(intuit_risk.deviceprofile_fact.agent_type))	3.11 KB	N/A
        └─CTEFullScan_124	1.37	0	root	CTE:raw_boundary	time:1.29µs, open:326ns, close:76ns, loops:1	data:CTE_0	N/A	N/A
CTE_0	1.37	0	root		time:1.3ms, open:66.5µs, close:7.15µs, loops:1	Non-Recursive CTE	0 Bytes	0 Bytes
└─Projection_58(Seed Part)	1.37	0	root		time:1.28ms, open:63µs, close:5.62µs, loops:1, Concurrency:OFF	intuit_risk.deviceprofile_fact.exact_id, intuit_risk.deviceprofile_fact.smart_id, intuit_risk.deviceprofile_fact.input_ip, intuit_risk.deviceprofile_fact.proxy_ip, intuit_risk.deviceprofile_fact.agent_type	4.10 KB	N/A
  └─IndexReader_67	1.71	0	root	partition:p20251101	time:1.28ms, open:59.3µs, close:4.22µs, loops:1, cop_task: {num: 1, max: 1.19ms, proc_keys: 0, tot_proc: 26.2µs, tot_wait: 56.4µs, copr_cache: disabled, build_task_duration: 18.9µs, max_distsql_concurrency: 1}, fetch_resp_duration: 1.2ms, rpc_info:{Cop:{num_rpc:1, total_time:1.18ms}}	index:Selection_66	255 Bytes	N/A
    └─Selection_66	1.71	0	cop[tikv]		tikv_task:{time:0s, loops:1}, scan_detail: {total_keys: 1, get_snapshot_time: 26.8µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 26.2µs, total_wait_time: 56.4µs}	or(or(not(isnull(intuit_risk.deviceprofile_fact.exact_id)), not(isnull(intuit_risk.deviceprofile_fact.smart_id))), or(not(isnull(intuit_risk.deviceprofile_fact.input_ip)), or(not(isnull(intuit_risk.deviceprofile_fact.proxy_ip)), not(isnull(intuit_risk.deviceprofile_fact.agent_type)))))	N/A	N/A
      └─IndexRangeScan_65	1.72	0	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{time:0s, loops:1}	range:[? ?,? ?), keep order:false	N/A	N/A
```

### tiflash_only

- Engines: `tiflash,tidb`
- Elapsed: `2.6 ms`
- Error: `(1815, "Internal : No access path for table 'x' is found with 'tidb_isolation_read_engines' = 'tiflash,tidb', valid values can be 'tikv'.")`

## 4. group_c_bundle_018

- Group/window/filter: `C` / `30d` / `d.true_ip = %s`
- Preagg applied: `False`
- Event: invoice=`INV0007589128` kind=`hot_true_ip` hot_field=`true_ip` hot_count=`738824` ref=`2026-04-10T23:06:57.563000`

### Params

```json
[
  "72.153.231.69"
]
```

### tikv

- Engines: `tikv,tidb`
- Elapsed: `331.8 ms`
- Storage tasks: `cop[tikv], root`

```sql
SELECT
  COUNT(*) AS `metric__c_0102`,
  SUM(p.amount) AS `metric__c_0103`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0104`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0105`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1773270417563
  AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=331.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Selection_13	0.80	1	root		time:327.4ms, open:97.5µs, close:9.12µs, loops:2, RU:938.68	gt(Column#106, ?)	2.52 KB	N/A
└─HashAgg_17	1.00	1	root		time:327.3ms, open:94.9µs, close:8.55µs, loops:3	funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	537.4 KB	0 Bytes
  └─IndexHashJoin_28	380878.24	4558	root		time:325.7ms, open:84.7µs, close:7.92µs, loops:8, inner:{total:623.6ms, concurrency:5, task:7, construct:82.7ms, fetch:536.4ms, build:13.3ms, join:4.42ms}	inner join, inner:IndexReader_56, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	15.2 MB	N/A
    ├─IndexReader_53(Build)	243544.67	98842	root	partition:p20260401,p20260501,p20260601,pmax	time:164.2ms, open:83.3µs, close:5.75µs, loops:99, cop_task: {num: 11, max: 163.5ms, min: 1.7ms, avg: 21ms, p95: 163.5ms, max_proc_keys: 116680, p95_proc_keys: 116680, tot_proc: 146.6ms, tot_wait: 3.95ms, copr_cache: disabled, build_task_duration: 28.4µs, max_distsql_concurrency: 4}, fetch_resp_duration: 162.5ms, rpc_info:{Cop:{num_rpc:11, total_time:231.1ms}}	index:Selection_52	4.77 MB	N/A
    │ └─Selection_52	243544.67	98842	cop[tikv]		tikv_task:{proc max:130ms, min:0s, avg: 17.3ms, p80:20ms, p95:130ms, iters:205, tasks:11}, scan_detail: {total_process_keys: 172346, total_process_keys_size: 40578683, total_keys: 55676, get_snapshot_time: 5.43ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 146.6ms, total_suspend_time: 135.3µs, total_wait_time: 3.95ms, total_kv_read_wall_time: 60ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_51	359561.64	172346	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:100ms, min:0s, avg: 14.5ms, p80:20ms, p95:100ms, iters:205, tasks:11}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_56(Probe)	380878.24	4558	root	partition:p20260401,p20260501,p20260601,pmax	total_time:500.5ms, total_open:190.1ms, total_close:66.5µs, loops:16, cop_task: {num: 122, max: 64.8ms, min: 711.7µs, avg: 10.2ms, p95: 37.3ms, max_proc_keys: 224, p95_proc_keys: 159, tot_proc: 555.7ms, tot_wait: 13.8ms, copr_cache: disabled, build_task_duration: 55.2ms, max_distsql_concurrency: 15}, fetch_resp_duration: 305.5ms, rpc_info:{Cop:{num_rpc:124, total_time:1.24s}, rpc_errors:{bucket_version_not_match:2}}, backoff{regionMiss: 4ms}	index:Selection_55	12.5 KB	N/A
      └─Selection_55	380878.24	4558	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 4.26ms, p80:10ms, p95:10ms, iters:176, tasks:122}, scan_detail: {total_process_keys: 4558, total_process_keys_size: 1393733, total_keys: 50643, get_snapshot_time: 11.7ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 555.7ms, total_suspend_time: 828.8µs, total_wait_time: 13.8ms, total_kv_read_wall_time: 340ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_54	516115.01	4558	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:50ms, min:0s, avg: 4.26ms, p80:10ms, p95:10ms, iters:176, tasks:122}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### cost

- Engines: `tikv,tiflash,tidb`
- Elapsed: `329.8 ms`
- Storage tasks: `cop[tikv], root`

```sql
SELECT
  COUNT(*) AS `metric__c_0102`,
  SUM(p.amount) AS `metric__c_0103`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0104`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0105`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1773270417563
  AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=329.8
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
Selection_13	0.80	1	root		time:325.3ms, open:86.5µs, close:11.7µs, loops:2, RU:916.41	gt(Column#106, ?)	5.57 KB	N/A
└─HashAgg_17	1.00	1	root		time:325.3ms, open:84.4µs, close:11.1µs, loops:3	funcs:count(?)->Column#106, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	537.4 KB	0 Bytes
  └─IndexHashJoin_28	380878.24	4558	root		time:323.5ms, open:76.2µs, close:10.6µs, loops:8, inner:{total:584ms, concurrency:5, task:7, construct:83.4ms, fetch:495.9ms, build:13.4ms, join:4.65ms}	inner join, inner:IndexReader_69, outer key:intuit_risk.deviceprofile_fact.interaction_id, inner key:intuit_risk.pmt_txn_fact.parsed_interaction_id, equal cond:eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)	15.2 MB	N/A
    ├─IndexReader_66(Build)	243544.67	98842	root	partition:p20260401,p20260501,p20260601,pmax	time:156.5ms, open:74.9µs, close:7.3µs, loops:99, cop_task: {num: 11, max: 155.7ms, min: 702.7µs, avg: 19.4ms, p95: 155.7ms, max_proc_keys: 116680, p95_proc_keys: 116680, tot_proc: 173.5ms, tot_wait: 349.3µs, copr_cache: disabled, build_task_duration: 24µs, max_distsql_concurrency: 4}, fetch_resp_duration: 155ms, rpc_info:{Cop:{num_rpc:11, total_time:213.3ms}}	index:Selection_65	4.77 MB	N/A
    │ └─Selection_65	243544.67	98842	cop[tikv]		tikv_task:{proc max:130ms, min:0s, avg: 15.5ms, p80:10ms, p95:130ms, iters:205, tasks:11}, scan_detail: {total_process_keys: 172346, total_process_keys_size: 40578683, total_keys: 55676, get_snapshot_time: 177µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 173.5ms, total_suspend_time: 123.4µs, total_wait_time: 349.3µs, total_kv_read_wall_time: 40ms}	not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
    │   └─IndexRangeScan_64	359561.64	172346	cop[tikv]	table:d, index:idx_dev_true_runtime_cov(true_ip, jms_timestamp, interaction_id, agent_type, device_fingerprint_score, device_score, device_worst_score, exact_id, input_ip, input_ip_score, proxy_ip, smart_id, true_ip_score)	tikv_task:{proc max:130ms, min:0s, avg: 15.5ms, p80:10ms, p95:130ms, iters:205, tasks:11}	range:[? ?,? +inf], keep order:false	N/A	N/A
    └─IndexReader_69(Probe)	380878.24	4558	root	partition:p20260401,p20260501,p20260601,pmax	total_time:453.9ms, total_open:191.7ms, total_close:72.4µs, loops:16, cop_task: {num: 122, max: 60.9ms, min: 515.4µs, avg: 8.98ms, p95: 41.8ms, max_proc_keys: 224, p95_proc_keys: 159, tot_proc: 464.8ms, tot_wait: 3.46ms, copr_cache: disabled, build_task_duration: 38.7ms, max_distsql_concurrency: 15}, fetch_resp_duration: 256ms, rpc_info:{Cop:{num_rpc:122, total_time:1.09s}}	index:Selection_68	12.5 KB	N/A
      └─Selection_68	380878.24	4558	cop[tikv]		tikv_task:{proc max:50ms, min:0s, avg: 3.85ms, p80:10ms, p95:10ms, iters:176, tasks:122}, scan_detail: {total_process_keys: 4558, total_process_keys_size: 1393733, total_keys: 50643, get_snapshot_time: 1.37ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 464.8ms, total_suspend_time: 661.9µs, total_wait_time: 3.46ms, total_kv_read_wall_time: 300ms}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
        └─IndexRangeScan_67	516115.01	4558	cop[tikv]	table:p, index:idx_pmt_join_runtime_cov(parsed_interaction_id, event_date, amount, merchant_account_number, card_holder_number_sha512, card_type, entry_method, mt_gateway, check_bank_routing_number, transaction_type)	tikv_task:{proc max:50ms, min:0s, avg: 3.85ms, p80:10ms, p95:10ms, iters:176, tasks:122}	range: decided by [eq(intuit_risk.pmt_txn_fact.parsed_interaction_id, intuit_risk.deviceprofile_fact.interaction_id) ge(intuit_risk.pmt_txn_fact.event_date, ?)], keep order:false	N/A	N/A
```

### tiflash_hint

- Engines: `tikv,tiflash,tidb`
- Elapsed: `1731.9 ms`
- Storage tasks: `mpp[tiflash], root`

```sql
SELECT /*+ READ_FROM_STORAGE(TIFLASH[p,d]) */
  COUNT(*) AS `metric__c_0102`,
  SUM(p.amount) AS `metric__c_0103`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0104`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0105`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1773270417563
  AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=1731.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
TableReader_74	0.80	1	root	partition:p20260401,p20260501,p20260601,pmax of d, partition:p20260401,p20260501,p20260601,pmax of p	time:1.73s, open:6.85ms, close:6.2µs, loops:2, RU:58961.55, cop_task: {num: 2, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache: disabled}, fetch_resp_duration: 1.72s	MppVersion: 3, data:ExchangeSender_73	4.66 KB	N/A
└─ExchangeSender_73	0.80	1	mpp[tiflash]		tiflash_task:{time:1.71s, loops:1, threads:1}, tiflash_network: {inner_zone_send_bytes: 104}	ExchangeType: PassThrough	N/A	N/A
  └─Selection_72	0.80	1	mpp[tiflash]		tiflash_task:{time:1.71s, loops:1, threads:1}	gt(Column#106, ?)	N/A	N/A
    └─Projection_66	1.00	1	mpp[tiflash]		tiflash_task:{time:1.71s, loops:1, threads:1}	Column#106, Column#107, Column#108, Column#109	N/A	N/A
      └─HashAgg_67	1.00	1	mpp[tiflash]		tiflash_task:{time:1.71s, loops:1, threads:1}	funcs:sum(Column#116)->Column#106, funcs:sum(Column#117)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	N/A	N/A
        └─ExchangeReceiver_69	1.00	4557	mpp[tiflash]		tiflash_task:{time:1.71s, loops:3, threads:63}, tiflash_network: {inner_zone_receive_bytes: 166942}		N/A	N/A
          └─ExchangeSender_68	1.00	4557	mpp[tiflash]		tiflash_task:{time:1.72s, loops:3, threads:3}, tiflash_network: {inner_zone_send_bytes: 166942}	ExchangeType: PassThrough, Compression: FAST	N/A	N/A
            └─HashAgg_65	1.00	4557	mpp[tiflash]		tiflash_task:{time:1.72s, loops:3, threads:3}	group by:intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.pmt_txn_fact.merchant_account_number, funcs:count(?)->Column#116, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#117	N/A	N/A
              └─Projection_55	380878.24	4558	mpp[tiflash]		tiflash_task:{time:1.72s, loops:323, threads:189}	intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.card_holder_number_sha512	N/A	N/A
                └─HashJoin_54	380878.24	4558	mpp[tiflash]		tiflash_task:{time:1.72s, loops:355, threads:189}	inner join, equal:[eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)], runtime filter:0[IN] <- intuit_risk.deviceprofile_fact.interaction_id	N/A	N/A
                  ├─ExchangeReceiver_40(Build)	243544.67	296526	mpp[tiflash]		tiflash_task:{time:518.5ms, loops:187, threads:189}, tiflash_network: {inner_zone_receive_bytes: 3423698}		N/A	N/A
                  │ └─ExchangeSender_39	243544.67	98842	mpp[tiflash]		tiflash_task:{time:513.7ms, loops:1870, threads:189}, tiflash_network: {inner_zone_send_bytes: 3423698}	ExchangeType: Broadcast, Compression: FAST	N/A	N/A
                  │   └─Selection_38	243544.67	98842	mpp[tiflash]		tiflash_task:{time:513.7ms, loops:1870, threads:189}	ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?), not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
                  │     └─TableFullScan_37	738823.99	236398	mpp[tiflash]	table:d	tiflash_task:{time:513.7ms, loops:1873, threads:189}, tiflash_network: {inner_zone_send_bytes: 30770, inter_zone_send_bytes: 86960, inner_zone_receive_bytes: 30770, inter_zone_receive_bytes: 86960}, tiflash_scan:{mvcc_input_rows:63397, mvcc_input_bytes:1077749, mvcc_output_rows:63397, local_regions:0, remote_regions:74, tot_learner_read:0ms, region_balance:{instance_num: 3, max/min: 27/22=1.227273}, delta_rows:0, delta_bytes:0, segments:372, stale_read_regions:0, tot_build_snapshot:0ms, tot_build_bitmap:15ms, tot_build_inputstream:58017ms, min_local_stream:0ms, max_local_stream:0ms, min_remote_stream:379ms, max_remote_stream:459ms, dtfile:{data_scanned_rows:118605233, data_skipped_rows:118756589, mvcc_scanned_rows:56738, mvcc_skipped_rows:3121866, lm_filter_scanned_rows:118615540, lm_filter_skipped_rows:4262438, tot_rs_index_check:9ms, tot_read:10641ms, disagg_cache_hit_bytes: 5875777324, disagg_cache_miss_bytes: 484164700}}	pushed down filter:eq(intuit_risk.deviceprofile_fact.true_ip, ?), keep order:false, PartitionTableScan:true	N/A	N/A
                  └─Selection_42(Probe)	11178124.80	9865189	mpp[tiflash]		tiflash_task:{time:1.72s, loops:355, threads:189}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
                    └─TableFullScan_41	15147092.62	15075597	mpp[tiflash]	table:p	tiflash_task:{time:1.72s, loops:355, threads:189}, tiflash_wait: {pipeline_breaker_wait: 239ms}, tiflash_network: {inner_zone_send_bytes: 3114116, inter_zone_send_bytes: 1369, inner_zone_receive_bytes: 3114116, inter_zone_receive_bytes: 1369}, tiflash_scan:{mvcc_input_rows:93579, mvcc_input_bytes:1590843, mvcc_output_rows:93579, local_regions:0, remote_regions:18, tot_learner_read:0ms, region_balance:{instance_num: 3, max/min: 7/4=1.750000}, delta_rows:0, delta_bytes:0, segments:50, stale_read_regions:0, tot_build_snapshot:0ms, tot_build_bitmap:636ms, tot_build_inputstream:18555ms, min_local_stream:0ms, max_local_stream:0ms, min_remote_stream:669ms, max_remote_stream:1439ms, dtfile:{data_scanned_rows:20471680, data_skipped_rows:5302699, mvcc_scanned_rows:24576, mvcc_skipped_rows:2287120, lm_filter_scanned_rows:20471680, lm_filter_skipped_rows:5157204, tot_rs_index_check:2325ms, tot_read:5957ms, disagg_cache_hit_bytes: 1782029575, disagg_cache_miss_bytes: 918185281}}	pushed down filter:ge(intuit_risk.pmt_txn_fact.event_date, ?), keep order:false, PartitionTableScan:true, runtime filter:0[IN] -> intuit_risk.pmt_txn_fact.parsed_interaction_id	N/A	N/A
```

### tiflash_only

- Engines: `tiflash,tidb`
- Elapsed: `219.3 ms`
- Storage tasks: `mpp[tiflash], root`

```sql
SELECT
  COUNT(*) AS `metric__c_0102`,
  SUM(p.amount) AS `metric__c_0103`,
  COUNT(DISTINCT(p.merchant_account_number)) AS `metric__c_0104`,
  COUNT(DISTINCT(p.card_holder_number_sha512)) AS `metric__c_0105`
FROM pmt_txn_fact p
LEFT OUTER JOIN deviceprofile_fact d
  ON p.parsed_interaction_id = d.interaction_id
WHERE d.true_ip = %s AND p.event_date >= 1773270417563
  AND d.jms_timestamp >= '2026-03-11 23:06:57.563000'
HAVING COUNT(*) > 0;
```

```text
-- explain_analyze_elapsed_ms=219.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
TableReader_73	0.80	1	root	partition:p20260401,p20260501,p20260601,pmax of d, partition:p20260401,p20260501,p20260601,pmax of p	time:215.5ms, open:2.65ms, close:6.16µs, loops:2, RU:58804.88, cop_task: {num: 2, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache: disabled}, fetch_resp_duration: 212.8ms	MppVersion: 3, data:ExchangeSender_72	4.63 KB	N/A
└─ExchangeSender_72	0.80	1	mpp[tiflash]		tiflash_task:{time:210.6ms, loops:1, threads:1}, tiflash_network: {inner_zone_send_bytes: 104}	ExchangeType: PassThrough	N/A	N/A
  └─Selection_71	0.80	1	mpp[tiflash]		tiflash_task:{time:210.6ms, loops:1, threads:1}	gt(Column#106, ?)	N/A	N/A
    └─Projection_65	1.00	1	mpp[tiflash]		tiflash_task:{time:210.6ms, loops:1, threads:1}	Column#106, Column#107, Column#108, Column#109	N/A	N/A
      └─HashAgg_66	1.00	1	mpp[tiflash]		tiflash_task:{time:210.6ms, loops:1, threads:1}	funcs:sum(Column#116)->Column#106, funcs:sum(Column#117)->Column#107, funcs:count(distinct intuit_risk.pmt_txn_fact.merchant_account_number)->Column#108, funcs:count(distinct intuit_risk.pmt_txn_fact.card_holder_number_sha512)->Column#109	N/A	N/A
        └─ExchangeReceiver_68	1.00	4557	mpp[tiflash]		tiflash_task:{time:210.6ms, loops:3, threads:63}, tiflash_network: {inner_zone_receive_bytes: 167011}		N/A	N/A
          └─ExchangeSender_67	1.00	4557	mpp[tiflash]		tiflash_task:{time:206.8ms, loops:3, threads:3}, tiflash_network: {inner_zone_send_bytes: 167011}	ExchangeType: PassThrough, Compression: FAST	N/A	N/A
            └─HashAgg_64	1.00	4557	mpp[tiflash]		tiflash_task:{time:206.8ms, loops:3, threads:3}	group by:intuit_risk.pmt_txn_fact.card_holder_number_sha512, intuit_risk.pmt_txn_fact.merchant_account_number, funcs:count(?)->Column#116, funcs:sum(intuit_risk.pmt_txn_fact.amount)->Column#117	N/A	N/A
              └─Projection_54	380878.24	4558	mpp[tiflash]		tiflash_task:{time:206.8ms, loops:323, threads:189}	intuit_risk.pmt_txn_fact.merchant_account_number, intuit_risk.pmt_txn_fact.amount, intuit_risk.pmt_txn_fact.card_holder_number_sha512	N/A	N/A
                └─HashJoin_53	380878.24	4558	mpp[tiflash]		tiflash_task:{time:206.8ms, loops:355, threads:189}	inner join, equal:[eq(intuit_risk.deviceprofile_fact.interaction_id, intuit_risk.pmt_txn_fact.parsed_interaction_id)], runtime filter:0[IN] <- intuit_risk.deviceprofile_fact.interaction_id	N/A	N/A
                  ├─ExchangeReceiver_39(Build)	243544.67	296526	mpp[tiflash]		tiflash_task:{time:133.5ms, loops:176, threads:189}, tiflash_wait: {pipeline_queue_wait: 10ms}, tiflash_network: {inner_zone_receive_bytes: 3419652}		N/A	N/A
                  │ └─ExchangeSender_38	243544.67	98842	mpp[tiflash]		tiflash_task:{time:134.3ms, loops:1870, threads:189}, tiflash_network: {inner_zone_send_bytes: 3419652}	ExchangeType: Broadcast, Compression: FAST	N/A	N/A
                  │   └─Selection_37	243544.67	98842	mpp[tiflash]		tiflash_task:{time:134.3ms, loops:1870, threads:189}	ge(intuit_risk.deviceprofile_fact.jms_timestamp, ?), not(isnull(intuit_risk.deviceprofile_fact.interaction_id))	N/A	N/A
                  │     └─TableFullScan_36	738823.99	236398	mpp[tiflash]	table:d	tiflash_task:{time:134.3ms, loops:1873, threads:189}, tiflash_network: {inner_zone_send_bytes: 30770, inter_zone_send_bytes: 86960, inner_zone_receive_bytes: 30770, inter_zone_receive_bytes: 86960}, tiflash_scan:{mvcc_input_rows:63397, mvcc_input_bytes:1077749, mvcc_output_rows:63397, local_regions:0, remote_regions:74, tot_learner_read:0ms, region_balance:{instance_num: 3, max/min: 27/22=1.227273}, delta_rows:0, delta_bytes:0, segments:372, stale_read_regions:0, tot_build_snapshot:0ms, tot_build_bitmap:23ms, tot_build_inputstream:801ms, min_local_stream:0ms, max_local_stream:0ms, min_remote_stream:49ms, max_remote_stream:80ms, dtfile:{data_scanned_rows:118605233, data_skipped_rows:118756589, mvcc_scanned_rows:56738, mvcc_skipped_rows:3121866, lm_filter_scanned_rows:118615540, lm_filter_skipped_rows:4262438, tot_rs_index_check:9ms, tot_read:9388ms, disagg_cache_hit_bytes: 3718384547, disagg_cache_miss_bytes: 0}}	pushed down filter:eq(intuit_risk.deviceprofile_fact.true_ip, ?), keep order:false, PartitionTableScan:true	N/A	N/A
                  └─Selection_41(Probe)	11178124.80	9865189	mpp[tiflash]		tiflash_task:{time:206.8ms, loops:355, threads:189}	not(isnull(intuit_risk.pmt_txn_fact.parsed_interaction_id))	N/A	N/A
                    └─TableFullScan_40	15147092.62	15075597	mpp[tiflash]	table:p	tiflash_task:{time:206.8ms, loops:355, threads:189}, tiflash_wait: {pipeline_breaker_wait: 69ms}, tiflash_network: {inner_zone_send_bytes: 70165, inter_zone_send_bytes: 1369, inner_zone_receive_bytes: 70165, inter_zone_receive_bytes: 1369}, tiflash_scan:{mvcc_input_rows:93579, mvcc_input_bytes:1590843, mvcc_output_rows:93579, local_regions:0, remote_regions:18, tot_learner_read:0ms, region_balance:{instance_num: 3, max/min: 7/4=1.750000}, delta_rows:0, delta_bytes:0, segments:50, stale_read_regions:0, tot_build_snapshot:0ms, tot_build_bitmap:7ms, tot_build_inputstream:26ms, min_local_stream:0ms, max_local_stream:0ms, min_remote_stream:100ms, max_remote_stream:149ms, dtfile:{data_scanned_rows:20471680, data_skipped_rows:5302699, mvcc_scanned_rows:24576, mvcc_skipped_rows:2287120, lm_filter_scanned_rows:20471680, lm_filter_skipped_rows:5157204, tot_rs_index_check:0ms, tot_read:1324ms, disagg_cache_hit_bytes: 1857582633, disagg_cache_miss_bytes: 0}}	pushed down filter:ge(intuit_risk.pmt_txn_fact.event_date, ?), keep order:false, PartitionTableScan:true, runtime filter:0[IN] -> intuit_risk.pmt_txn_fact.parsed_interaction_id	N/A	N/A
```
