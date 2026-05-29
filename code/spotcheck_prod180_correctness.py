#!/usr/bin/env python3
"""Compare raw runtime 180d bundle results against prod-180 pre-agg results.

This is a correctness guard, not a benchmark. It selects one populated key per
180d bundle from the pre-agg tables, runs the raw bundle SQL and the prod180
pre-agg SQL for the same binding/reference time, and requires exact equality.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import json
import math
from pathlib import Path
import time

import pymysql

from demo import (
    cluster_group_a_templates,
    cluster_group_b_templates,
    cluster_group_c_templates,
)
from lib.db_config import get_db_config
from mixed_traffic_test import bundle_params, render_bundle_sql


ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "results" / "prod180_spotcheck_full.json"


def all_180_bundles():
    for group, factory in (
        ("A", cluster_group_a_templates),
        ("B", cluster_group_b_templates),
        ("C", cluster_group_c_templates),
    ):
        for bundle in factory():
            if bundle.window_days == 180:
                yield group, bundle


def normalize(value):
    if isinstance(value, Decimal):
        return float(value) if value % 1 else int(value)
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return round(value, 8)
    return value


def row_values(rows):
    return [[normalize(value) for value in row.values()] for row in rows]


def not_blank_predicate(alias: str, column: str) -> str:
    return f"{alias}.`{column}` IS NOT NULL AND {alias}.`{column}` <> ''"


def choose_key(conn, group: str, bundle):
    # Pick keys from the base tables, not the pre-agg tables. That keeps this
    # correctness check independent of whether a pre-agg table is empty/partial.
    columns = list(bundle.param_names)
    with conn.cursor() as cur:
        if group == "A":
            select_list = ", ".join(f"p.`{column}` AS `{column}`" for column in columns)
            where_clause = " AND ".join(not_blank_predicate("p", column) for column in columns)
            cur.execute(
                f"""
                SELECT {select_list}
                FROM pmt_txn_fact p
                WHERE {where_clause}
                ORDER BY p.event_date DESC
                LIMIT 1
                """
            )
        elif group == "B":
            column = columns[0]
            cur.execute(
                f"""
                SELECT d.`{column}` AS `{column}`
                FROM deviceprofile_fact d
                WHERE {not_blank_predicate("d", column)}
                ORDER BY d.jms_timestamp DESC
                LIMIT 1
                """
            )
        elif group == "C":
            column = columns[0]
            source_alias = bundle.group_by_fields[0].split(".", 1)[0]
            where_predicate = not_blank_predicate(source_alias, column)
            cur.execute(
                f"""
                SELECT {source_alias}.`{column}` AS `{column}`
                FROM pmt_txn_fact p
                JOIN deviceprofile_fact d
                  ON p.parsed_interaction_id = d.interaction_id
                WHERE p.parsed_interaction_id IS NOT NULL
                  AND p.parsed_interaction_id <> ''
                  AND {where_predicate}
                ORDER BY p.event_date DESC
                LIMIT 1
                """
            )
        else:
            raise ValueError(f"Unsupported group: {group}")

        row = cur.fetchone()
        if row:
            key1 = row[columns[0]]
            key2 = row[columns[1]] if len(columns) > 1 else ""
            return key1, key2

    return None, None


def bindings_for(bundle, key1, key2):
    values = [key1]
    if len(bundle.param_names) > 1:
        values.append(key2)
    return dict(zip(bundle.param_names, values, strict=True))


def get_reference_time(conn) -> datetime:
    with conn.cursor() as cur:
        cur.execute("SELECT FROM_UNIXTIME(MAX(event_date)/1000) AS ts FROM pmt_txn_fact")
        pmax = cur.fetchone()["ts"]
        cur.execute("SELECT MAX(jms_timestamp) AS ts FROM deviceprofile_fact")
        dmax = cur.fetchone()["ts"]
    # Keep the real timestamp so the spotcheck exercises the boundary-day
    # correction path, not just a convenient midnight cutoff.
    return min(pmax, dmax)


def main() -> int:
    cfg = get_db_config(save_msg="prod180 spotcheck")
    cfg["cursorclass"] = pymysql.cursors.DictCursor

    conn = pymysql.connect(**cfg)
    reference_time = get_reference_time(conn)
    print(f"reference_time={reference_time}", flush=True)

    bundles = list(all_180_bundles())
    preagg_bundles = {bundle.bundle_id for _, bundle in bundles}
    results = []
    failures = []

    for group, bundle in bundles:
        key1, key2 = choose_key(conn, group, bundle)
        if key1 is None:
            failures.append({"bundle_id": bundle.bundle_id, "error": "no preagg key found"})
            print(f"FAIL {bundle.bundle_id} no preagg key found", flush=True)
            continue

        event = {"bindings": bindings_for(bundle, key1, key2)}
        raw_sql = render_bundle_sql(bundle, group, reference_time, set(), set(), "none")
        raw_params = bundle_params(bundle, reference_time, event["bindings"], set())
        preagg_sql = render_bundle_sql(bundle, group, reference_time, set(), preagg_bundles, "prod180")
        preagg_params = bundle_params(bundle, reference_time, event["bindings"], preagg_bundles, "prod180")

        with conn.cursor() as cur:
            started = time.perf_counter()
            cur.execute(raw_sql, raw_params)
            raw_rows = cur.fetchall()
            raw_ms = (time.perf_counter() - started) * 1000.0

        with conn.cursor() as cur:
            started = time.perf_counter()
            cur.execute(preagg_sql, preagg_params)
            preagg_rows = cur.fetchall()
            preagg_ms = (time.perf_counter() - started) * 1000.0

        raw_values = row_values(raw_rows)
        preagg_values = row_values(preagg_rows)
        ok = raw_values == preagg_values
        row = {
            "bundle_id": bundle.bundle_id,
            "group": group,
            "templates": len(bundle.templates),
            "key1": str(key1),
            "key2": str(key2),
            "raw_ms": round(raw_ms, 1),
            "preagg_ms": round(preagg_ms, 1),
            "ok": ok,
            "raw": raw_values,
            "preagg": preagg_values,
        }
        results.append(row)

        status = "PASS" if ok else "FAIL"
        print(
            f"{status} {bundle.bundle_id} group={group} "
            f"raw={raw_ms:.1f}ms preagg={preagg_ms:.1f}ms "
            f"key1={str(key1)[:48]} key2={str(key2)[:48]}",
            flush=True,
        )
        if not ok:
            failures.append(row)

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "reference_time": reference_time.isoformat(sep=" "),
                "checked_bundles": len(results),
                "passes": sum(1 for row in results if row["ok"]),
                "failures": failures,
                "results": results,
            },
            indent=2,
            default=str,
        )
    )
    print(f"WROTE {OUT_PATH}", flush=True)
    if failures:
        print(f"FAILURES={len(failures)}", flush=True)
        return 1
    print("ALL_PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
