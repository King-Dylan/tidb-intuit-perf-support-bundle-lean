# TiFlash SET_VAR Probe After Scale

Generated on 2026-05-29 from focused `EXPLAIN ANALYZE` probes.

Session baseline:

- `tidb_isolation_read_engines='tikv,tiflash,tidb'`
- `max_execution_time=30000`
- `tidb_opt_force_inline_cte=0`
- `tidb_opt_distinct_agg_push_down=1`

Tested query-level hints:

```sql
/*+ SET_VAR(tidb_isolation_read_engines='tiflash,tidb') */
/*+ SET_VAR(tidb_enforce_mpp=1) */
/*+ SET_VAR(tidb_isolation_read_engines='tiflash,tidb') SET_VAR(tidb_enforce_mpp=1) */
```

## Results

### `group_b_bundle_012`, hot `true_ip`

| Variant | Time | Storage task |
|---|---:|---|
| base cost | 2469.1 ms | `cop[tikv]` |
| `SET_VAR(tidb_isolation_read_engines='tiflash,tidb')` | 403.6 ms | `mpp[tiflash]` |
| `SET_VAR(tidb_enforce_mpp=1)` | 312.0 ms | `mpp[tiflash]` |
| both SET_VAR hints | 256.6 ms | `mpp[tiflash]` |

### `group_c_bundle_018`, hot `true_ip`

| Variant | Time | Storage task |
|---|---:|---|
| base cost | 336.8 ms | `cop[tikv]` |
| `SET_VAR(tidb_isolation_read_engines='tiflash,tidb')` | 196.7 ms | `mpp[tiflash]` |
| `SET_VAR(tidb_enforce_mpp=1)` | 194.2 ms | `mpp[tiflash]` |
| both SET_VAR hints | 191.0 ms | `mpp[tiflash]` |

## Group A Probe

Most Group A hot payment bundles became slower on TiFlash. The useful candidate was `group_a_bundle_006`.

| Bundle | Hot field | Base | TiFlash SET_VAR |
|---|---|---:|---:|
| `group_a_bundle_001` | `card_holder_number_sha512` | 35.3 ms | 2200.9 ms |
| `group_a_bundle_002` | `check_bank_routing_number` | 59.2 ms | 504.9 ms |
| `group_a_bundle_004` | `merchant_account_number` | 37.5 ms | 160.3 ms |
| `group_a_bundle_005` | `card_holder_number_sha512` | 23.2 ms | 235.3 ms |
| `group_a_bundle_006` | `check_bank_routing_number` | 292.1 ms | 165.5 ms |
| `group_a_bundle_008` | `merchant_account_number` | 59.7 ms | 154.0 ms |
| `group_a_bundle_009` | `card_holder_number_sha512` | 23.8 ms | 239.7 ms |
| `group_a_bundle_010` | `check_bank_routing_number` | 107.1 ms | 502.3 ms |
| `group_a_bundle_012` | `merchant_account_number` | 126.2 ms | 187.4 ms |
| `group_a_bundle_014` | `check_bank_routing_number` | 121.6 ms | 471.0 ms |
| `group_a_bundle_016` | `merchant_account_number` | 87.8 ms | 440.1 ms |
