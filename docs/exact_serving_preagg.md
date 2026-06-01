# Exact Serving Pre-Aggregation

This adds a targeted final serving layer for the 180-day hot-key tail bundles.
The existing prod180 helper tables are still useful, but some distinct-heavy
queries can still scan hundreds of thousands or millions of helper rows at event
time. The serving table stores final bundle output metrics for a key/as-of
combination, so the benchmark path becomes a point lookup plus a small pivot.

Default serving bundles:

- `group_b_bundle_018`
- `group_b_bundle_019`
- `group_b_bundle_020`
- `group_c_bundle_023`
- `group_c_bundle_025`

Create the table:

```bash
python3 exact_serving.py create --execute
```

Build rows from the reused benchmark event sample:

```bash
python3 exact_serving.py build \
  --source-events-json results/mixed_traffic_1780094259.json \
  --as-of-grain day \
  --execute \
  --output results/exact_serving_build.json
```

Run the benchmark with serving overlay:

```bash
PREAGG_MODE=serving \
SERVING_AS_OF_GRAIN=day \
./run_v15_prod180_benchmark.sh 12 60
```

Use `SERVING_BUNDLE_IDS` for a narrower or broader test:

```bash
PREAGG_MODE=serving \
SERVING_BUNDLE_IDS="group_b_bundle_018 group_b_bundle_019 group_b_bundle_020" \
./run_v15_prod180_benchmark.sh 12 60
```

`day` grain is the reusable high-EPS serving shape. `timestamp` grain preserves
the exact event reference timestamp for correctness probes, but it has much
lower serving-row reuse.
