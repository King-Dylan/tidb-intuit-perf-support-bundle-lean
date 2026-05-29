# Residual Group B Optimization Attempts

- Generated: `2026-05-29T00:18:52`
- Scope: only `group_b_bundle_018` and `group_b_bundle_020`
- All runs force `tidb_isolation_read_engines='tikv,tidb'`.

## group_b_bundle_018

- Key: `input_ip = 135.232.20.92`
- Previous original/best: `1496.6 ms` / `695.3 ms`

### Helper Rows

| Template | Min day | Max day | Rows | Count time |
| --- | --- | --- | ---: | ---: |
| `b_0146` | `2025-11-01` | `2026-04-10` | 261396 | 211.7 ms |
| `b_0150` | `2025-11-01` | `2026-04-10` | 259560 | 538.3 ms |
| `b_0154` | `2025-11-01` | `2026-04-10` | 246339 | 196.6 ms |
| `b_0158` | `2025-11-01` | `2026-04-10` | 467 | 31.4 ms |

### Candidate Timings

| Shape | Settings | Time | Result |
| --- | --- | ---: | --- |
| `split_union_distinct_countstar` | `agg_pd_hash16` | 754.2 ms | ok |
| `split_scalar_union_all` | `base` | 845.6 ms | ok |
| `split_union_distinct_countstar` | `agg_pd` | 872.0 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_distinct_pd_hash16` | 881.8 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_scan30_exec10` | 909.0 ms | ok |
| `split_union_distinct_countstar` | `base` | 963.6 ms | ok |
| `split_scalar_union_all` | `agg_pd_scan30_exec10` | 970.6 ms | ok |
| `split_scalar_union_all` | `agg_pd` | 972.7 ms | ok |
| `split_scalar_union_all` | `agg_pd_hash16` | 987.4 ms | ok |
| `split_scalar_union_all` | `agg_pd_distinct_pd_hash16` | 987.6 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_paging_off` | 991.1 ms | ok |
| `split_union_distinct_countstar` | `distinct_pd_hash16` | 992.8 ms | ok |
| `helper_dedup_first` | `agg_pd_distinct_pd_hash16` | 1020.3 ms | ok |
| `helper_dedup_first` | `agg_pd_hash16` | 1027.4 ms | ok |
| `split_scalar_union_all` | `agg_pd_paging_off` | 1033.5 ms | ok |
| `helper_dedup_first` | `distinct_pd_hash16` | 1036.1 ms | ok |
| `group_by_template` | `base` | 1041.1 ms | ok |
| `helper_dedup_first` | `agg_pd_scan30_exec10` | 1044.3 ms | ok |
| `current_case_distinct` | `distinct_pd_hash16` | 1045.9 ms | ok |
| `two_stage_dedup` | `distinct_pd_hash16` | 1057.1 ms | ok |
| `split_scalar_union_all` | `distinct_pd_hash16` | 1060.1 ms | ok |
| `two_stage_dedup` | `agg_pd_scan30_exec10` | 1066.0 ms | ok |
| `two_stage_dedup` | `agg_pd_paging_off` | 1110.8 ms | ok |
| `two_stage_dedup` | `agg_pd_hash16` | 1113.3 ms | ok |
| `two_stage_dedup` | `agg_pd_distinct_pd_hash16` | 1129.3 ms | ok |
| `helper_dedup_first` | `agg_pd` | 1164.4 ms | ok |
| `group_by_template` | `agg_pd_scan30_exec10` | 1169.7 ms | ok |
| `helper_dedup_first` | `base` | 1176.2 ms | ok |
| `two_stage_dedup` | `base` | 1185.9 ms | ok |
| `current_case_distinct` | `agg_pd_scan30_exec10` | 1186.5 ms | ok |
| `current_case_distinct` | `base` | 1191.9 ms | ok |
| `current_case_distinct` | `agg_pd_distinct_pd_hash16` | 1217.9 ms | ok |
| `current_case_distinct` | `agg_pd_hash16` | 1218.8 ms | ok |
| `group_by_template` | `agg_pd_hash16` | 1238.2 ms | ok |
| `group_by_template` | `agg_pd_distinct_pd_hash16` | 1280.0 ms | ok |
| `two_stage_dedup` | `agg_pd` | 1292.5 ms | ok |
| `group_by_template` | `agg_pd` | 1329.8 ms | ok |
| `helper_dedup_first` | `agg_pd_paging_off` | 1338.2 ms | ok |
| `group_by_template` | `agg_pd_paging_off` | 1343.8 ms | ok |
| `current_case_distinct` | `agg_pd_paging_off` | 1350.3 ms | ok |
| `current_case_distinct` | `agg_pd` | 1497.1 ms | ok |
| `group_by_template` | `distinct_pd_hash16` | 2543.1 ms | ok |

### Best Attempt

- Shape: `split_union_distinct_countstar`
- Settings: `agg_pd_hash16` / `{'tidb_opt_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}`
- Time: `754.2 ms`

#### SQL

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

#### Params

```json
[
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92",
  "135.232.20.92"
]
```

#### EXPLAIN ANALYZE

```text
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

### All Attempt SQL

#### current_case_distinct

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

#### group_by_template

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
),
counts AS (
  SELECT template_id, COUNT(DISTINCT distinct_value) AS distinct_count
  FROM distinct_values
  GROUP BY template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0146' THEN distinct_count END), 0) AS `metric__b_0146`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0150' THEN distinct_count END), 0) AS `metric__b_0150`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0154' THEN distinct_count END), 0) AS `metric__b_0154`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0158' THEN distinct_count END), 0) AS `metric__b_0158`
FROM counts;
```

#### two_stage_dedup

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
),
dedup AS (
  SELECT template_id, distinct_value
  FROM distinct_values
  GROUP BY template_id, distinct_value
), counts AS (
  SELECT template_id, COUNT(*) AS distinct_count
  FROM dedup
  GROUP BY template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0146' THEN distinct_count END), 0) AS `metric__b_0146`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0150' THEN distinct_count END), 0) AS `metric__b_0150`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0154' THEN distinct_count END), 0) AS `metric__b_0154`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0158' THEN distinct_count END), 0) AS `metric__b_0158`
FROM counts;
```

#### helper_dedup_first

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
helper_dedup AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
  GROUP BY x.template_id, x.distinct_value
), all_dedup AS (
  SELECT template_id, distinct_value FROM helper_dedup
  UNION
  SELECT 'b_0146' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION
  SELECT 'b_0150' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION
  SELECT 'b_0154' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION
  SELECT 'b_0158' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
), counts AS (
  SELECT template_id, COUNT(*) AS distinct_count
  FROM all_dedup
  GROUP BY template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0146' THEN distinct_count END), 0) AS `metric__b_0146`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0150' THEN distinct_count END), 0) AS `metric__b_0150`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0154' THEN distinct_count END), 0) AS `metric__b_0154`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0158' THEN distinct_count END), 0) AS `metric__b_0158`
FROM counts;
```

#### split_scalar_union_all

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
  SELECT 'b_0146' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0146'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION ALL
    SELECT CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0150' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0150'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION ALL
    SELECT CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0154' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0154'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION ALL
    SELECT CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0158' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id = 'b_0158'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11'
    UNION ALL
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

#### split_union_distinct_countstar

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

## group_b_bundle_020

- Key: `true_ip = 74.179.68.52`
- Previous original/best: `2884.2 ms` / `1128.4 ms`

### Helper Rows

| Template | Min day | Max day | Rows | Count time |
| --- | --- | --- | ---: | ---: |
| `b_0162` | `2025-11-01` | `2026-04-10` | 523720 | 909.9 ms |
| `b_0166` | `2025-11-01` | `2026-04-10` | 519249 | 368.3 ms |
| `b_0170` | `2025-11-01` | `2026-04-10` | 460693 | 646.9 ms |
| `b_0174` | `2025-11-01` | `2026-04-10` | 55302 | 129.9 ms |
| `b_0178` | `2025-11-01` | `2026-04-10` | 479 | 31.0 ms |

### Candidate Timings

| Shape | Settings | Time | Result |
| --- | --- | ---: | --- |
| `split_union_distinct_countstar` | `distinct_pd_hash16` | 1143.0 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_distinct_pd_hash16` | 1158.2 ms | ok |
| `split_scalar_union_all` | `agg_pd_distinct_pd_hash16` | 1209.6 ms | ok |
| `split_union_distinct_countstar` | `agg_pd` | 1216.3 ms | ok |
| `split_scalar_union_all` | `agg_pd_paging_off` | 1222.8 ms | ok |
| `split_scalar_union_all` | `agg_pd` | 1229.1 ms | ok |
| `split_scalar_union_all` | `base` | 1230.8 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_hash16` | 1232.3 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_scan30_exec10` | 1236.9 ms | ok |
| `two_stage_dedup` | `distinct_pd_hash16` | 1241.0 ms | ok |
| `split_union_distinct_countstar` | `agg_pd_paging_off` | 1251.0 ms | ok |
| `helper_dedup_first` | `distinct_pd_hash16` | 1254.5 ms | ok |
| `two_stage_dedup` | `base` | 1290.1 ms | ok |
| `group_by_template` | `distinct_pd_hash16` | 1326.3 ms | ok |
| `current_case_distinct` | `base` | 1331.9 ms | ok |
| `split_union_distinct_countstar` | `base` | 1338.8 ms | ok |
| `split_scalar_union_all` | `distinct_pd_hash16` | 1339.4 ms | ok |
| `group_by_template` | `base` | 1351.4 ms | ok |
| `split_scalar_union_all` | `agg_pd_hash16` | 1354.4 ms | ok |
| `split_scalar_union_all` | `agg_pd_scan30_exec10` | 1365.2 ms | ok |
| `two_stage_dedup` | `agg_pd_hash16` | 1379.6 ms | ok |
| `current_case_distinct` | `distinct_pd_hash16` | 1391.4 ms | ok |
| `two_stage_dedup` | `agg_pd_paging_off` | 1398.8 ms | ok |
| `two_stage_dedup` | `agg_pd_distinct_pd_hash16` | 1407.3 ms | ok |
| `helper_dedup_first` | `agg_pd_hash16` | 1421.5 ms | ok |
| `helper_dedup_first` | `agg_pd_scan30_exec10` | 1425.2 ms | ok |
| `helper_dedup_first` | `base` | 1432.5 ms | ok |
| `helper_dedup_first` | `agg_pd_distinct_pd_hash16` | 1457.7 ms | ok |
| `two_stage_dedup` | `agg_pd_scan30_exec10` | 1466.4 ms | ok |
| `two_stage_dedup` | `agg_pd` | 1498.4 ms | ok |
| `helper_dedup_first` | `agg_pd_paging_off` | 1551.3 ms | ok |
| `group_by_template` | `agg_pd_paging_off` | 1638.0 ms | ok |
| `helper_dedup_first` | `agg_pd` | 1671.2 ms | ok |
| `group_by_template` | `agg_pd_hash16` | 1675.1 ms | ok |
| `group_by_template` | `agg_pd_distinct_pd_hash16` | 1695.9 ms | ok |
| `group_by_template` | `agg_pd_scan30_exec10` | 1780.5 ms | ok |
| `group_by_template` | `agg_pd` | 1789.1 ms | ok |
| `current_case_distinct` | `agg_pd_paging_off` | 2121.1 ms | ok |
| `current_case_distinct` | `agg_pd` | 2128.7 ms | ok |
| `current_case_distinct` | `agg_pd_distinct_pd_hash16` | 2146.4 ms | ok |
| `current_case_distinct` | `agg_pd_hash16` | 2161.6 ms | ok |
| `current_case_distinct` | `agg_pd_scan30_exec10` | 2233.3 ms | ok |

### Best Attempt

- Shape: `split_union_distinct_countstar`
- Settings: `distinct_pd_hash16` / `{'tidb_opt_distinct_agg_push_down': 1, 'tidb_hashagg_final_concurrency': 16, 'tidb_hashagg_partial_concurrency': 8}`
- Time: `1143.0 ms`

#### SQL

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

#### Params

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

#### EXPLAIN ANALYZE

```text
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

### All Attempt SQL

#### current_case_distinct

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

#### group_by_template

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
),
counts AS (
  SELECT template_id, COUNT(DISTINCT distinct_value) AS distinct_count
  FROM distinct_values
  GROUP BY template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0162' THEN distinct_count END), 0) AS `metric__b_0162`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0166' THEN distinct_count END), 0) AS `metric__b_0166`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0170' THEN distinct_count END), 0) AS `metric__b_0170`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0174' THEN distinct_count END), 0) AS `metric__b_0174`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0178' THEN distinct_count END), 0) AS `metric__b_0178`
FROM counts;
```

#### two_stage_dedup

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
),
dedup AS (
  SELECT template_id, distinct_value
  FROM distinct_values
  GROUP BY template_id, distinct_value
), counts AS (
  SELECT template_id, COUNT(*) AS distinct_count
  FROM dedup
  GROUP BY template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0162' THEN distinct_count END), 0) AS `metric__b_0162`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0166' THEN distinct_count END), 0) AS `metric__b_0166`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0170' THEN distinct_count END), 0) AS `metric__b_0170`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0174' THEN distinct_count END), 0) AS `metric__b_0174`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0178' THEN distinct_count END), 0) AS `metric__b_0178`
FROM counts;
```

#### helper_dedup_first

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
helper_dedup AS (
  SELECT x.template_id, x.distinct_value
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
  GROUP BY x.template_id, x.distinct_value
), all_dedup AS (
  SELECT template_id, distinct_value FROM helper_dedup
  UNION
  SELECT 'b_0162' AS template_id, CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  UNION
  SELECT 'b_0166' AS template_id, CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  UNION
  SELECT 'b_0170' AS template_id, CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  UNION
  SELECT 'b_0174' AS template_id, CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  UNION
  SELECT 'b_0178' AS template_id, CAST(`raw_distinct_4` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_4` IS NOT NULL
), counts AS (
  SELECT template_id, COUNT(*) AS distinct_count
  FROM all_dedup
  GROUP BY template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0162' THEN distinct_count END), 0) AS `metric__b_0162`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0166' THEN distinct_count END), 0) AS `metric__b_0166`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0170' THEN distinct_count END), 0) AS `metric__b_0170`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0174' THEN distinct_count END), 0) AS `metric__b_0174`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0178' THEN distinct_count END), 0) AS `metric__b_0178`
FROM counts;
```

#### split_scalar_union_all

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
  SELECT 'b_0162' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0162'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION ALL
    SELECT CAST(`raw_distinct_0` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_0` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0166' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0166'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION ALL
    SELECT CAST(`raw_distinct_1` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_1` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0170' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0170'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION ALL
    SELECT CAST(`raw_distinct_2` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_2` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0174' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0174'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION ALL
    SELECT CAST(`raw_distinct_3` AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE `raw_distinct_3` IS NOT NULL
  ) u
  UNION ALL
  SELECT 'b_0178' AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count
  FROM (
    SELECT x.distinct_value
    FROM `group_b_180d_daily_distinct` x
    WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id = 'b_0178'
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12'
    UNION ALL
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

#### split_union_distinct_countstar

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
