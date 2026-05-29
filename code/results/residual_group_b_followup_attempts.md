# Residual Group B Optimization Attempts

- Generated: `2026-05-29T00:21:31`
- Scope: only `group_b_bundle_018` and `group_b_bundle_020`
- All runs force `tidb_isolation_read_engines='tikv,tidb'`.

## group_b_bundle_018

- Key: `input_ip = 135.232.20.92`
- Previous original/best: `1496.6 ms` / `695.3 ms`

### Helper Rows

| Template | Min day | Max day | Rows | Count time |
| --- | --- | --- | ---: | ---: |
| `b_0146` | `2025-11-01` | `2026-04-10` | 261396 | 213.5 ms |
| `b_0150` | `2025-11-01` | `2026-04-10` | 259560 | 213.8 ms |
| `b_0154` | `2025-11-01` | `2026-04-10` | 246339 | 178.3 ms |
| `b_0158` | `2025-11-01` | `2026-04-10` | 467 | 32.8 ms |

### Candidate Timings

| Shape | Settings | Time | Result |
| --- | --- | ---: | --- |
| `helper_only_approx_not_exact_raw_empty_guard` | `base` | 783.9 ms | ok |
| `current_approx_not_exact` | `agg_pd_hash16` | 812.2 ms | ok |
| `helper_only_approx_not_exact_raw_empty_guard` | `distinct_pd_hash16` | 831.5 ms | ok |
| `current_approx_not_exact` | `base` | 881.2 ms | ok |
| `current_approx_not_exact` | `distinct_pd_hash16` | 894.6 ms | ok |
| `helper_only_approx_not_exact_raw_empty_guard` | `agg_pd_hash16` | 899.0 ms | ok |
| `helper_only_group_by_template_raw_empty_guard` | `distinct_pd_hash16` | 900.5 ms | ok |
| `helper_only_case_distinct_raw_empty_guard` | `distinct_pd_hash16` | 928.7 ms | ok |
| `current_case_distinct_stream_hint` | `distinct_pd_hash16` | 962.2 ms | ok |
| `helper_only_group_by_template_raw_empty_guard` | `base` | 987.9 ms | ok |
| `current_case_distinct_stream_hint` | `base` | 995.1 ms | ok |
| `helper_only_case_distinct_raw_empty_guard` | `base` | 995.6 ms | ok |
| `helper_only_case_distinct_raw_empty_guard` | `agg_pd_hash16` | 996.1 ms | ok |
| `helper_only_group_by_template_raw_empty_guard` | `agg_pd_hash16` | 1020.4 ms | ok |
| `current_case_distinct_stream_hint` | `agg_pd_hash16` | 1097.0 ms | ok |

### Best Attempt

- Shape: `helper_only_approx_not_exact_raw_empty_guard`
- Settings: `base` / `{}`
- Time: `783.9 ms`

#### SQL

```sql
SELECT
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0146' THEN x.distinct_value END) AS `metric__b_0146`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0150' THEN x.distinct_value END) AS `metric__b_0150`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0154' THEN x.distinct_value END) AS `metric__b_0154`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0158' THEN x.distinct_value END) AS `metric__b_0158`
FROM `group_b_180d_daily_distinct` x
WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11';
```

#### Params

```json
[
  "135.232.20.92"
]
```

#### EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=783.9
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_7	1.00	1	root		time:466.8ms, open:100µs, close:32.9µs, loops:2, RU:1636.81, partial_worker:{wall_time:452.568439ms, concurrency:4, task_num:751, tot_wait:1.532891572s, tot_exec:275.590465ms, tot_time:1.810069946s, max:452.520872ms, p95:452.520872ms}, final_worker:{wall_time:466.6473ms, concurrency:4, task_num:7, tot_wait:5.653µs, tot_exec:14.069821ms, tot_time:1.824220223s, max:466.608846ms, p95:466.608846ms}	funcs:approx_count_distinct(Column#12)->Column#8, funcs:approx_count_distinct(Column#13)->Column#9, funcs:approx_count_distinct(Column#14)->Column#10, funcs:approx_count_distinct(Column#15)->Column#11	7.04 MB	0 Bytes
└─Projection_20	1134674.75	767762	root		time:388.4ms, open:73.9µs, close:29.9µs, loops:752, Concurrency:5	case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#12, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#13, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#14, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#15	1.20 MB	N/A
  └─IndexReader_13	1134674.75	767762	root		time:387.5ms, open:72.6µs, close:11.5µs, loops:752, cop_task: {num: 23, max: 385.4ms, min: 1.34ms, avg: 49.8ms, p95: 383.3ms, max_proc_keys: 249556, p95_proc_keys: 247720, tot_proc: 458ms, tot_wait: 575µs, copr_cache: disabled, build_task_duration: 21.7µs, max_distsql_concurrency: 4}, fetch_resp_duration: 384.6ms, rpc_info:{Cop:{num_rpc:23, total_time:1.15s}}	index:IndexRangeScan_12	55.5 MB	N/A
    └─IndexRangeScan_12	1134674.75	767762	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:150ms, min:0s, avg: 18.7ms, p80:10ms, p95:150ms, iters:837, tasks:23}, scan_detail: {total_process_keys: 767762, total_process_keys_size: 96549666, total_keys: 36007, get_snapshot_time: 268.9µs, rocksdb: {block: {}}}, time_detail: {total_process_time: 458ms, total_suspend_time: 122.8µs, total_wait_time: 575µs, total_kv_read_wall_time: 20ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
```

### All Attempt SQL

#### current_case_distinct_stream_hint

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
SELECT /*+ STREAM_AGG() */
  COUNT(DISTINCT CASE WHEN template_id = 'b_0146' THEN distinct_value END) AS `metric__b_0146`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0150' THEN distinct_value END) AS `metric__b_0150`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0154' THEN distinct_value END) AS `metric__b_0154`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0158' THEN distinct_value END) AS `metric__b_0158`
FROM distinct_values;
```

#### current_approx_not_exact

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
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0146' THEN distinct_value END) AS `metric__b_0146`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0150' THEN distinct_value END) AS `metric__b_0150`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0154' THEN distinct_value END) AS `metric__b_0154`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0158' THEN distinct_value END) AS `metric__b_0158`
FROM distinct_values;
```

#### helper_only_case_distinct_raw_empty_guard

```sql
SELECT
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0146' THEN x.distinct_value END) AS `metric__b_0146`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0150' THEN x.distinct_value END) AS `metric__b_0150`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0154' THEN x.distinct_value END) AS `metric__b_0154`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0158' THEN x.distinct_value END) AS `metric__b_0158`
FROM `group_b_180d_daily_distinct` x
WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11';
```

#### helper_only_group_by_template_raw_empty_guard

```sql
WITH counts AS (
  SELECT x.template_id, COUNT(DISTINCT x.distinct_value) AS distinct_count
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_018'
      AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
      AND x.key1 = %s AND x.key2 = ''
      AND x.event_day > '2025-10-11'
  GROUP BY x.template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0146' THEN distinct_count END), 0) AS `metric__b_0146`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0150' THEN distinct_count END), 0) AS `metric__b_0150`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0154' THEN distinct_count END), 0) AS `metric__b_0154`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0158' THEN distinct_count END), 0) AS `metric__b_0158`
FROM counts;
```

#### helper_only_approx_not_exact_raw_empty_guard

```sql
SELECT
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0146' THEN x.distinct_value END) AS `metric__b_0146`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0150' THEN x.distinct_value END) AS `metric__b_0150`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0154' THEN x.distinct_value END) AS `metric__b_0154`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0158' THEN x.distinct_value END) AS `metric__b_0158`
FROM `group_b_180d_daily_distinct` x
WHERE x.bundle_id = 'group_b_bundle_018'
    AND x.template_id IN ('b_0146', 'b_0150', 'b_0154', 'b_0158')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-11';
```

## group_b_bundle_020

- Key: `true_ip = 74.179.68.52`
- Previous original/best: `2884.2 ms` / `1128.4 ms`

### Helper Rows

| Template | Min day | Max day | Rows | Count time |
| --- | --- | --- | ---: | ---: |
| `b_0162` | `2025-11-01` | `2026-04-10` | 523720 | 761.2 ms |
| `b_0166` | `2025-11-01` | `2026-04-10` | 519249 | 369.4 ms |
| `b_0170` | `2025-11-01` | `2026-04-10` | 460693 | 321.4 ms |
| `b_0174` | `2025-11-01` | `2026-04-10` | 55302 | 86.1 ms |
| `b_0178` | `2025-11-01` | `2026-04-10` | 479 | 31.3 ms |

### Candidate Timings

| Shape | Settings | Time | Result |
| --- | --- | ---: | --- |
| `helper_only_approx_not_exact_raw_empty_guard` | `base` | 1133.3 ms | ok |
| `current_approx_not_exact` | `base` | 1146.4 ms | ok |
| `helper_only_approx_not_exact_raw_empty_guard` | `distinct_pd_hash16` | 1188.4 ms | ok |
| `helper_only_group_by_template_raw_empty_guard` | `distinct_pd_hash16` | 1191.5 ms | ok |
| `current_approx_not_exact` | `distinct_pd_hash16` | 1197.7 ms | ok |
| `current_approx_not_exact` | `agg_pd_hash16` | 1227.5 ms | ok |
| `helper_only_approx_not_exact_raw_empty_guard` | `agg_pd_hash16` | 1236.4 ms | ok |
| `current_case_distinct_stream_hint` | `base` | 1294.8 ms | ok |
| `current_case_distinct_stream_hint` | `distinct_pd_hash16` | 1322.0 ms | ok |
| `helper_only_case_distinct_raw_empty_guard` | `base` | 1344.4 ms | ok |
| `helper_only_case_distinct_raw_empty_guard` | `distinct_pd_hash16` | 1381.9 ms | ok |
| `helper_only_group_by_template_raw_empty_guard` | `agg_pd_hash16` | 1407.3 ms | ok |
| `helper_only_group_by_template_raw_empty_guard` | `base` | 1448.7 ms | ok |
| `helper_only_case_distinct_raw_empty_guard` | `agg_pd_hash16` | 1468.0 ms | ok |
| `current_case_distinct_stream_hint` | `agg_pd_hash16` | 1524.6 ms | ok |

### Best Attempt

- Shape: `helper_only_approx_not_exact_raw_empty_guard`
- Settings: `base` / `{}`
- Time: `1133.3 ms`

#### SQL

```sql
SELECT
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0162' THEN x.distinct_value END) AS `metric__b_0162`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0166' THEN x.distinct_value END) AS `metric__b_0166`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0170' THEN x.distinct_value END) AS `metric__b_0170`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0174' THEN x.distinct_value END) AS `metric__b_0174`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0178' THEN x.distinct_value END) AS `metric__b_0178`
FROM `group_b_180d_daily_distinct` x
WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12';
```

#### Params

```json
[
  "74.179.68.52"
]
```

#### EXPLAIN ANALYZE

```text
-- explain_analyze_elapsed_ms=1133.3
id	estRows	actRows	task	access object	execution info	operator info	memory	disk
HashAgg_7	1.00	1	root		time:807.2ms, open:105.6µs, close:35.8µs, loops:2, RU:3985.35, partial_worker:{wall_time:793.907844ms, concurrency:4, task_num:1529, tot_wait:2.512326806s, tot_exec:659.85684ms, tot_time:3.17538569s, max:793.857449ms, p95:793.857449ms}, final_worker:{wall_time:807.022053ms, concurrency:4, task_num:7, tot_wait:31.219µs, tot_exec:13.09859ms, tot_time:3.188617391s, max:806.966763ms, p95:806.966763ms}	funcs:approx_count_distinct(Column#13)->Column#8, funcs:approx_count_distinct(Column#14)->Column#9, funcs:approx_count_distinct(Column#15)->Column#10, funcs:approx_count_distinct(Column#16)->Column#11, funcs:approx_count_distinct(Column#17)->Column#12	7.48 MB	0 Bytes
└─Projection_20	2651301.78	1559443	root		time:645.3ms, open:77.4µs, close:31.8µs, loops:1530, Concurrency:5	case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#13, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#14, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#15, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#16, case(eq(intuit_risk.group_b_180d_daily_distinct.template_id, ?), intuit_risk.group_b_180d_daily_distinct.distinct_value)->Column#17	1.29 MB	N/A
  └─IndexReader_13	2651301.78	1559443	root		time:645.1ms, open:76µs, close:11.8µs, loops:1530, cop_task: {num: 51, max: 451.5ms, min: 753.9µs, avg: 40.9ms, p95: 393.9ms, max_proc_keys: 345056, p95_proc_keys: 289760, tot_proc: 1.11s, tot_wait: 2.58ms, copr_cache: disabled, build_task_duration: 24.3µs, max_distsql_concurrency: 6}, fetch_resp_duration: 640.1ms, rpc_info:{Cop:{num_rpc:51, total_time:2.09s}}	index:IndexRangeScan_12	36.4 MB	N/A
    └─IndexRangeScan_12	2651301.78	1559443	cop[tikv]	table:x, index:PRIMARY(bundle_id, template_id, key1, key2, event_day, distinct_value)	tikv_task:{proc max:190ms, min:0s, avg: 20.6ms, p80:20ms, p95:170ms, iters:1720, tasks:51}, scan_detail: {total_process_keys: 1559443, total_process_keys_size: 235292075, total_keys: 417265, get_snapshot_time: 1.8ms, rocksdb: {block: {}}}, time_detail: {total_process_time: 1.11s, total_suspend_time: 821.5µs, total_wait_time: 2.58ms, total_kv_read_wall_time: 350ms}	range:(? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], (? ? ? ? ?,? ? ? ? +inf], keep order:false	N/A	N/A
```

### All Attempt SQL

#### current_case_distinct_stream_hint

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
SELECT /*+ STREAM_AGG() */
  COUNT(DISTINCT CASE WHEN template_id = 'b_0162' THEN distinct_value END) AS `metric__b_0162`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0166' THEN distinct_value END) AS `metric__b_0166`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0170' THEN distinct_value END) AS `metric__b_0170`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0174' THEN distinct_value END) AS `metric__b_0174`,
  COUNT(DISTINCT CASE WHEN template_id = 'b_0178' THEN distinct_value END) AS `metric__b_0178`
FROM distinct_values;
```

#### current_approx_not_exact

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
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0162' THEN distinct_value END) AS `metric__b_0162`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0166' THEN distinct_value END) AS `metric__b_0166`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0170' THEN distinct_value END) AS `metric__b_0170`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0174' THEN distinct_value END) AS `metric__b_0174`,
  APPROX_COUNT_DISTINCT(CASE WHEN template_id = 'b_0178' THEN distinct_value END) AS `metric__b_0178`
FROM distinct_values;
```

#### helper_only_case_distinct_raw_empty_guard

```sql
SELECT
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0162' THEN x.distinct_value END) AS `metric__b_0162`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0166' THEN x.distinct_value END) AS `metric__b_0166`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0170' THEN x.distinct_value END) AS `metric__b_0170`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0174' THEN x.distinct_value END) AS `metric__b_0174`,
  COUNT(DISTINCT CASE WHEN x.template_id = 'b_0178' THEN x.distinct_value END) AS `metric__b_0178`
FROM `group_b_180d_daily_distinct` x
WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12';
```

#### helper_only_group_by_template_raw_empty_guard

```sql
WITH counts AS (
  SELECT x.template_id, COUNT(DISTINCT x.distinct_value) AS distinct_count
  FROM `group_b_180d_daily_distinct` x
  WHERE x.bundle_id = 'group_b_bundle_020'
      AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
      AND x.key1 = %s AND x.key2 = ''
      AND x.event_day > '2025-10-12'
  GROUP BY x.template_id
)
SELECT
  COALESCE(MAX(CASE WHEN template_id = 'b_0162' THEN distinct_count END), 0) AS `metric__b_0162`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0166' THEN distinct_count END), 0) AS `metric__b_0166`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0170' THEN distinct_count END), 0) AS `metric__b_0170`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0174' THEN distinct_count END), 0) AS `metric__b_0174`,
  COALESCE(MAX(CASE WHEN template_id = 'b_0178' THEN distinct_count END), 0) AS `metric__b_0178`
FROM counts;
```

#### helper_only_approx_not_exact_raw_empty_guard

```sql
SELECT
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0162' THEN x.distinct_value END) AS `metric__b_0162`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0166' THEN x.distinct_value END) AS `metric__b_0166`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0170' THEN x.distinct_value END) AS `metric__b_0170`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0174' THEN x.distinct_value END) AS `metric__b_0174`,
  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = 'b_0178' THEN x.distinct_value END) AS `metric__b_0178`
FROM `group_b_180d_daily_distinct` x
WHERE x.bundle_id = 'group_b_bundle_020'
    AND x.template_id IN ('b_0162', 'b_0166', 'b_0170', 'b_0174', 'b_0178')
    AND x.key1 = %s AND x.key2 = ''
    AND x.event_day > '2025-10-12';
```
