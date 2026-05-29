# TiFlash After-Scale Results

Generated on 2026-05-29 after TiFlash scale-out.

## TiFlash Topology Observed

The cluster now shows one TiFlash write/data store and three TiFlash compute stores:

- `engine=tiflash`, `engine_role=write`: store `455`
- `engine=tiflash_compute`, `exclusive=no-data`: stores `460`, `527891`, `527892`

Only the two base tables have TiFlash replicas:

- `pmt_txn_fact`: replica 1, available 1, progress 1.0
- `deviceprofile_fact`: replica 1, available 1, progress 1.0

The 180d pre-agg helper tables still do not have TiFlash replicas, so helper-table queries such as `group_b_bundle_018` and `group_b_bundle_020` cannot be fully moved to `tiflash,tidb`.

## Single Query A/B

Source: `results/tiflash_after_scale_residual_hot.md`

| Bundle | TiKV/cost path | TiFlash path | Result |
|---|---:|---:|---|
| `group_b_bundle_012` hot `true_ip` | 2468.5 ms, TiKV | 621.8 ms with session `tiflash,tidb`; 256.6 ms with query-level `SET_VAR` follow-up | TiFlash now helps significantly |
| `group_c_bundle_018` hot `true_ip` | 329.8 ms, TiKV | 219.3 ms with session `tiflash,tidb`; 191.0 ms with query-level `SET_VAR` follow-up | TiFlash helps |
| `group_b_bundle_018` hot `input_ip` | 1110.2 ms, TiKV helper | `tiflash,tidb` fails because helper table has no TiFlash access path | no change |
| `group_b_bundle_020` hot `true_ip` | 1151.0 ms, TiKV helper | `tiflash,tidb` fails because helper table has no TiFlash access path | no change |

MPP memory errors are gone for the tested base-table runtime queries after scale-out.

## Targeted Query-Level TiFlash

I added a benchmark switch to apply this query-level hint to selected runtime bundles:

```sql
/*+ SET_VAR(tidb_isolation_read_engines='tiflash,tidb') SET_VAR(tidb_enforce_mpp=1) */
```

The tested candidate set was:

- `group_a_bundle_006`
- `group_b_bundle_012`
- `group_c_bundle_018`

Group A follow-up showed only `group_a_bundle_006` improved under TiFlash for the hot routing-number case. Most other Group A hot candidates were slower on TiFlash.

## 13 eps Benchmark

### Previous 13 eps, no targeted TiFlash

Source: `results/mixed_traffic_1780094427.json`

- Achieved: 13.03 events/sec
- `>=60/65` by 500ms: 40/391 (10.2%)
- 60/65 p99: 3100.2 ms

### Targeted TiFlash for all events

Source: `results/mixed_traffic_1780097851.json`

- Achieved: 13.03 events/sec
- Targeted bundles: `group_a_bundle_006`, `group_b_bundle_012`, `group_c_bundle_018`
- Policy: all events
- `>=60/65` by 350ms: 377/391 (96.4%)
- `>=60/65` by 500ms: 379/391 (96.9%)
- 60/65 p50: 169.3 ms
- 60/65 p95: 266.4 ms
- 60/65 p99: 326.9 ms

This is a large improvement over the previous 13 eps run, but it is still slightly below the earlier clean 12 eps fallback coverage of 358/361 (99.2%).

### Targeted TiFlash only for matching hot-key events

Source: `results/mixed_traffic_1780097982.json`

- Achieved: 13.03 events/sec
- Policy: matching hot-key events only
- `>=60/65` by 500ms: 37/391 (9.5%)
- 60/65 p99: 2355.4 ms

This did not help because the 13 eps queueing knee is driven by repeated all-event bundle pressure, not only the 5% hot-key events.

## 100 eps High-Load Run

Source: `results/mixed_traffic_1780098117.json`

Configuration:

- Target: 100 events/sec for 60s
- Full fanout: 65 bundle SQL/event
- Client: `POOL_SIZE=1500`, `BUNDLE_WORKERS=1500`, `EVENT_WORKERS=512`, `MAX_PENDING_EVENTS=512`
- Targeted TiFlash bundles: `group_a_bundle_006`, `group_b_bundle_012`, `group_c_bundle_018`
- Targeted policy: all events

Results:

- Achieved submitted-completed rate: 15.07 events/sec
- `>=60/65` by 350ms: 311/904 (34.4%)
- `>=60/65` by 500ms: 625/904 (69.1%)
- 60/65 p50: 36,739 ms
- 60/65 p95: 63,172 ms
- Client backpressure skips: 20
- Read pool connection replacements: 38

Compared with the earlier 100 eps high-load run without targeted TiFlash (`results/mixed_traffic_1780096580.json`):

- Achieved rate stayed about the same: 15.1 eps.
- `>=60/65` by 500ms improved from 430/907 (47.4%) to 625/904 (69.1%).
- Slow query storage path shifted strongly toward TiFlash:
  - before: 34 TiFlash MPP slow-query records, 3965 TiKV slow-query records
  - after: 2179 TiFlash MPP slow-query records, 182 TiKV slow-query records

## Takeaway

TiFlash scale-out fixed the MPP memory blocker and makes selected base-table runtime bundles much faster. It materially improves the 13 eps fallback path and increases TiFlash participation during high-load runs.

It does not by itself reach the 100 events/sec target. The system still saturates around 15 events/sec under the full 65-query fanout at 100 eps target pressure. The remaining blockers are broader fanout/queueing plus helper-table distinct queries that still live on TiKV.
