#!/usr/bin/env python3
"""Build and query a targeted exact feature-serving table.

The existing prod180 helper tables reduce some 180-day work, but hot-key
distinct bundles can still scan hundreds of thousands or millions of helper
rows at event time. This module adds a final serving layer: precompute the
bundle output columns for selected key/as-of combinations and make the scoring
path a point lookup plus a tiny metric pivot.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo import (
    cluster_group_a_templates,
    cluster_group_b_templates,
    cluster_group_c_templates,
    metric_column,
    presence_column,
)
from optimized_config import EXACT_SERVING_BUNDLES, PROD180_PREAGG_BUNDLES
from preagg_rollups import (
    bundle_rollup_metrics,
    key_fields,
    quote_ident,
    render_prod180_runtime_query,
)


ROOT = Path(__file__).resolve().parent
SERVING_TABLE = os.getenv("INTUIT_EXACT_SERVING_TABLE", "risk_feature_serving")
VALID_AS_OF_GRAINS = {"day", "timestamp"}


@dataclass(frozen=True)
class ServingKey:
    bundle_id: str
    group: str
    as_of_grain: str
    as_of_key: str
    reference_time: datetime
    key1: str
    key2: str
    bindings: dict[str, Any]


def all_bundles() -> dict[str, tuple[str, Any]]:
    result: dict[str, tuple[str, Any]] = {}
    for group, bundles in (
        ("A", cluster_group_a_templates()),
        ("B", cluster_group_b_templates()),
        ("C", cluster_group_c_templates()),
    ):
        for bundle in bundles:
            result[bundle.bundle_id] = (group, bundle)
    return result


def metric_names_for_bundle(bundle) -> list[str]:
    names: list[str] = []
    for tmpl in bundle.templates:
        names.append(metric_column(tmpl.template_id))
        if tmpl.extra_predicate:
            names.append(presence_column(tmpl.template_id))
    return names


def validate_as_of_grain(as_of_grain: str) -> str:
    if as_of_grain not in VALID_AS_OF_GRAINS:
        raise ValueError(f"as_of_grain must be one of {sorted(VALID_AS_OF_GRAINS)}, got {as_of_grain!r}")
    return as_of_grain


def serving_lookup_key(reference_time: datetime, as_of_grain: str) -> str:
    validate_as_of_grain(as_of_grain)
    if as_of_grain == "day":
        return reference_time.date().isoformat()
    return reference_time.strftime("%Y-%m-%d %H:%M:%S.%f")


def serving_reference_time(reference_time: datetime, as_of_grain: str) -> datetime:
    """Return the timestamp represented by the serving row.

    Timestamp-grain rows preserve the exact event reference time. Day-grain rows
    intentionally represent the end of that calendar day, which is a serving
    design choice for high reuse rather than per-event rolling timestamp exactness.
    """

    validate_as_of_grain(as_of_grain)
    if as_of_grain == "timestamp":
        return reference_time
    return datetime.combine(reference_time.date(), datetime.max.time()).replace(tzinfo=reference_time.tzinfo)


def create_serving_table_sql(table_name: str = SERVING_TABLE) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {quote_ident(table_name)} (
  as_of_grain VARCHAR(16) NOT NULL,
  as_of_key VARCHAR(32) NOT NULL,
  bundle_id VARCHAR(64) NOT NULL,
  key1 VARCHAR(256) NOT NULL,
  key2 VARCHAR(256) NOT NULL DEFAULT '',
  metric_name VARCHAR(128) NOT NULL,
  metric_value DECIMAL(38,6) DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (as_of_grain, as_of_key, bundle_id, key1, key2, metric_name),
  KEY idx_serving_lookup (bundle_id, key1, key2, as_of_grain, as_of_key)
);
""".strip()


def render_serving_query(bundle, reference_time: datetime, as_of_grain: str = "day", table_name: str = SERVING_TABLE) -> str:
    select_parts = [
        f"MAX(CASE WHEN metric_name = '{name}' THEN metric_value END) AS {quote_ident(name)}"
        for name in metric_names_for_bundle(bundle)
    ]
    key2_predicate = "s.key2 = %s" if len(key_fields(bundle)) > 1 else "s.key2 = ''"
    return f"""
SELECT
  {",\n  ".join(select_parts)}
FROM {quote_ident(table_name)} s
WHERE s.as_of_grain = %s
  AND s.as_of_key = %s
  AND s.bundle_id = '{bundle.bundle_id}'
  AND s.key1 = %s
  AND {key2_predicate};
""".strip()


def serving_params(bundle, reference_time: datetime, bindings: dict[str, Any], as_of_grain: str = "day") -> tuple[Any, ...]:
    fields = key_fields(bundle)
    values = ["" if bindings.get(field) is None else str(bindings.get(field)) for field in fields]
    params: list[Any] = [as_of_grain, serving_lookup_key(reference_time, as_of_grain), values[0]]
    if len(values) > 1:
        params.append(values[1])
    return tuple(params)


def prod180_params_for_bundle(bundle, group: str, reference_time: datetime, bindings: dict[str, Any]) -> tuple[Any, ...]:
    key_values = tuple("" if bindings.get(k) is None else str(bindings.get(k)) for k in key_fields(bundle))
    rollups, distincts = bundle_rollup_metrics(group, bundle)
    params: list[Any] = []
    if rollups == [] and all(not tmpl.extra_predicate for tmpl in bundle.templates):
        params.extend(key_values)
        params.extend(key_values)
        return tuple(params)
    if not rollups and any(distinct.extra_predicate for distinct in distincts) and any(not distinct.extra_predicate for distinct in distincts):
        params.extend(key_values)
        params.extend(key_values)
        for distinct in distincts:
            if distinct.extra_predicate:
                params.extend(key_values)
                params.extend(key_values)
                params.extend(key_values)
                params.extend(key_values)
        return tuple(params)
    if group == "C" and rollups and distincts and all(not tmpl.extra_predicate for tmpl in bundle.templates):
        params.extend(key_values)
        params.extend(key_values)
        params.extend(key_values)
        return tuple(params)
    for tmpl in bundle.templates:
        if not tmpl.select_expr.strip().upper().startswith("COUNT(DISTINCT"):
            continue
        params.extend(key_values)
        params.extend(key_values)
        if tmpl.extra_predicate:
            params.extend(key_values)
            params.extend(key_values)
    if rollups:
        params.extend(key_values)
        params.extend(key_values)
    return tuple(params)


def runtime_params_for_bundle(bundle, reference_time: datetime, bindings: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(bindings.get(name) for name in bundle.param_names)


def source_query_and_params(group: str, bundle, reference_time: datetime, bindings: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    if bundle.bundle_id in PROD180_PREAGG_BUNDLES and bundle.window_days == 180:
        return render_prod180_runtime_query(group, bundle, reference_time), prod180_params_for_bundle(
            bundle, group, reference_time, bindings
        )
    return bundle.render_sql(reference_time), runtime_params_for_bundle(bundle, reference_time, bindings)


def iter_events_from_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload.get("sampled_normal_events", [])) + list(payload.get("sampled_hot_events", []))


def collect_serving_keys(
    events: list[dict[str, Any]],
    bundle_ids: list[str],
    as_of_grain: str,
    limit_keys: int | None = None,
) -> list[ServingKey]:
    catalog = all_bundles()
    seen: set[tuple[str, str, str, str, str]] = set()
    keys: list[ServingKey] = []
    for event in events:
        reference_time = datetime.fromisoformat(event["reference_time"])
        build_reference_time = serving_reference_time(reference_time, as_of_grain)
        as_of_key = serving_lookup_key(reference_time, as_of_grain)
        bindings = event["bindings"]
        for bundle_id in bundle_ids:
            group, bundle = catalog[bundle_id]
            fields = key_fields(bundle)
            values = [bindings.get(field) for field in fields]
            if not values or any(value is None for value in values):
                continue
            key1 = str(values[0])
            key2 = str(values[1]) if len(values) > 1 else ""
            dedupe_key = (bundle_id, as_of_grain, as_of_key, key1, key2)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            keys.append(
                ServingKey(
                    bundle_id=bundle_id,
                    group=group,
                    as_of_grain=as_of_grain,
                    as_of_key=as_of_key,
                    reference_time=build_reference_time,
                    key1=key1,
                    key2=key2,
                    bindings=bindings,
                )
            )
            if limit_keys is not None and len(keys) >= limit_keys:
                return keys
    return keys


def upsert_metric_rows(cur, table_name: str, key: ServingKey, columns: list[str], row: tuple[Any, ...]) -> None:
    sql = f"""
REPLACE INTO {quote_ident(table_name)}
  (as_of_grain, as_of_key, bundle_id, key1, key2, metric_name, metric_value)
VALUES (%s, %s, %s, %s, %s, %s, %s)
""".strip()
    rows = [
        (key.as_of_grain, key.as_of_key, key.bundle_id, key.key1, key.key2, column, value)
        for column, value in zip(columns, row)
    ]
    cur.executemany(sql, rows)


def build_serving_rows(conn, keys: list[ServingKey], table_name: str, dry_run: bool = False) -> list[dict[str, Any]]:
    catalog = all_bundles()
    results: list[dict[str, Any]] = []
    for index, key in enumerate(keys, start=1):
        group, bundle = catalog[key.bundle_id]
        sql, params = source_query_and_params(group, bundle, key.reference_time, key.bindings)
        if dry_run:
            print(f"-- [{index}/{len(keys)}] {key.bundle_id} {key.as_of_grain}:{key.as_of_key} key=({key.key1}, {key.key2})")
            print(sql)
            print(f"-- params={params}\n")
            continue
        started = time.perf_counter()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            columns = [desc[0] for desc in cur.description]
            if row is None:
                row = tuple(None for _ in columns)
            upsert_metric_rows(cur, table_name, key, columns, row)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        result = {
            "bundle_id": key.bundle_id,
            "as_of_grain": key.as_of_grain,
            "as_of_key": key.as_of_key,
            "key1": key.key1,
            "key2": key.key2,
            "metric_count": len(columns),
            "elapsed_ms": elapsed_ms,
        }
        results.append(result)
        print(
            f"[{index}/{len(keys)}] {key.bundle_id} {key.as_of_key} "
            f"key=({key.key1}, {key.key2}) metrics={len(columns)} build_ms={elapsed_ms:.1f}",
            flush=True,
        )
    return results


def selected_bundle_ids(raw: list[str] | None) -> list[str]:
    bundle_ids = raw or sorted(EXACT_SERVING_BUNDLES)
    catalog = all_bundles()
    unknown = sorted(set(bundle_ids) - set(catalog))
    if unknown:
        raise SystemExit(f"Unknown bundle ids: {', '.join(unknown)}")
    return bundle_ids


def configure_session(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SET SESSION tidb_isolation_read_engines = %s", (os.getenv("TIDB_ISOLATION_READ_ENGINES", "tikv,tidb"),))
        if os.getenv("INTUIT_FORCE_INLINE_CTE", "0") in {"0", "1"}:
            cur.execute(f"SET SESSION tidb_opt_force_inline_cte = {int(os.getenv('INTUIT_FORCE_INLINE_CTE', '0'))}")
        if os.getenv("INTUIT_DISTINCT_AGG_PUSH_DOWN") == "1":
            cur.execute("SET SESSION tidb_opt_distinct_agg_push_down = 1")
        if os.getenv("READ_MAX_EXECUTION_TIME_MS"):
            cur.execute("SET SESSION max_execution_time = %s", (int(os.environ["READ_MAX_EXECUTION_TIME_MS"]),))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create", "build", "render"])
    parser.add_argument("--bundle", action="append", dest="bundles", help="Bundle id to serve. Repeatable.")
    parser.add_argument("--source-events-json", default="results/mixed_traffic_1780094259.json")
    parser.add_argument("--as-of-grain", choices=sorted(VALID_AS_OF_GRAINS), default=os.getenv("INTUIT_SERVING_AS_OF_GRAIN", "day"))
    parser.add_argument("--table", default=SERVING_TABLE)
    parser.add_argument("--limit-keys", type=int, default=None)
    parser.add_argument("--execute", action="store_true", help="Execute create/build. Without this, print SQL/work only.")
    parser.add_argument("--output", default=None, help="Optional JSON result path for build action.")
    args = parser.parse_args()

    bundle_ids = selected_bundle_ids(args.bundles)
    if args.action == "render":
        catalog = all_bundles()
        now = datetime.now()
        for bundle_id in bundle_ids:
            _, bundle = catalog[bundle_id]
            print(f"-- {bundle_id}")
            print(render_serving_query(bundle, now, args.as_of_grain, args.table))
            print()
        return

    conn = None
    if args.execute:
        import pymysql

        from lib.db_config import get_db_config

        conn = pymysql.connect(**get_db_config(save_msg="exact serving builder"))
        conn.autocommit(True)
        configure_session(conn)

    try:
        if args.action == "create":
            sql = create_serving_table_sql(args.table)
            print(sql)
            if conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
            return

        events = iter_events_from_json(ROOT / args.source_events_json)
        keys = collect_serving_keys(events, bundle_ids, args.as_of_grain, args.limit_keys)
        print(
            f"-- serving build keys={len(keys)} bundles={','.join(bundle_ids)} "
            f"as_of_grain={args.as_of_grain} table={args.table}"
        )
        results = build_serving_rows(conn, keys, args.table, dry_run=not args.execute)
        if args.output:
            out = ROOT / args.output
            out.write_text(json.dumps({"keys": len(keys), "results": results}, indent=2, default=str), encoding="utf-8")
            print(f"Saved: {out}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
