# Full 65/65 Event Optimization Follow-Up

Generated on 2026-05-30 after the clarification that all 65 bundle SQLs are required for one event decision. `score_ready` / deferred-bundle experiments are diagnostic only and are not counted as acceptable optimizations in this report.

## Summary

| Run | Shape | Target eps | Achieved eps | Event p99 | Full 65/65 by 500ms | Full 65/65 p99 | Result |
|---|---|---:|---:|---:|---:|---:|---|
| `mixed_traffic_1780124733.json` | previous prod180, TiKV/TiDB | 12 | 12.03 | 652.7ms | 333/361 (92.2%) | 428.9ms | current full-event baseline |
| `mixed_traffic_1780125314.json` | B019 shared distinct rewrite, TiKV/TiDB | 12 | 12.03 | 652.6ms | 332/361 (92.0%) | 463.7ms | B019 hot tail improved, overall still limited by other bundles/errors |
| `mixed_traffic_1780125638.json` | B019 rewrite, cost engines `tikv,tiflash,tidb` | 12 | 12.00 | 698.4ms | 331/360 (91.9%) | 388.5ms | lower successful full65 p99, slightly worse coverage/tails |
| `mixed_traffic_1780125507.json` | B019 rewrite, TiKV/TiDB | 13 | 12.97 | 2926.3ms | 25/389 (6.4%) | 2837.5ms | still crosses the queueing knee |
| `mixed_traffic_1780125572.json` | B019 rewrite, TiKV/TiDB, pool 450 | 13 | 13.03 | 3100.8ms | 18/391 (4.6%) | 3092.9ms | lowering client concurrency did not recover 13 eps |

## Accepted Script Changes

- `preagg_rollups.py`: rewrote prod180 distinct-only bundles that mix filtered and unfiltered distinct metrics. The new form shares one helper-table scan for unfiltered distinct template_ids and keeps filtered distinct/presence metrics on the scalar exact path.
- `mixed_traffic_test.py`: added matching parameter binding for that SQL shape and added event-completion bundle coverage, so the report distinguishes query runtime from true event completion time.
- `run_final_mixed_preagg.sh`: added diagnostic env hooks for `SCORE_READY_*` and `EXCLUDE_BUNDLE_IDS`. These are not used for final full-event runs.

## B019 Single SQL Verification

For hot `smart_id`, `group_b_bundle_019` improved materially:

| Variant | Before | After shared distinct rewrite |
|---|---:|---:|
| TiKV/TiDB | 2199.2ms | 722.8ms |
| Cost engines | 1433.8ms | 710.3ms |
| Hashagg/concurrency knobs on rewritten SQL | n/a | 688.6ms TiKV/TiDB, 700.3ms cost |

This is a real SQL rewrite win, but it is not enough to make the full 65-query event meet 500ms because B018/B020 helper distinct scans and hot Group C/Group A runtime paths still create errors or tails under the 500ms guard.

## Remaining Blockers

The 10s detailed full-event run `mixed_traffic_1780125439.json` captured concrete error bundles under `max_execution_time=500ms`:

| Bundle | Error count | Typical issue |
|---|---:|---|
| `group_b_bundle_020` | 3 | 180d helper distinct for hot `true_ip`; context deadline / max execution |
| `group_b_bundle_019` | 2 | improved but still can exceed 500ms on hot `smart_id` |
| `group_b_bundle_018` | 2 | 180d helper distinct for hot `input_ip` |
| `group_b_bundle_012` | 2 | 30d hot `true_ip` runtime path |
| Group C 30d/180d joins | several | hot join paths near or over 500ms |

## Conclusion

With all 65 SQLs required, the current environment does not reach the target. The best reproducible full-event point is still around 12 events/sec, and even that is below the 500ms full-65 SLA at roughly 92% completion within 500ms. 13 events/sec causes second-level queueing.

To approach 100 events/sec / 1000 events/sec with 65/65 required, the remaining options are architecture-level rather than simple parameter tuning:

- Broader exact pre-aggregation for hot 30d/90d/180d distinct features, especially B018/B020-style rolling distincts.
- A TiFlash replica or alternate serving layout for the large helper distinct table, if storage budget allows.
- Batch multiple events per bundle query to reduce 65 round trips per event.
- Feature cache / hot-key cache for high-cardinality hot keys.
- Approximate distinct sketches if exact `COUNT(DISTINCT)` can be relaxed.
