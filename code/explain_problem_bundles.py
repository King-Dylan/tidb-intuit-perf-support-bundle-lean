#!/usr/bin/env python3
"""Render and explain problematic mixed-traffic bundle queries.

This is a diagnostic helper for post-benchmark analysis. It reads a mixed
traffic result JSON and slow-bundle CSV, picks one representative event for each
problematic bundle, renders the exact SQL/params used by the benchmark, runs
EXPLAIN ANALYZE with TiFlash excluded from the session, and writes a Markdown
report with full SQL and plan text.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pymysql

from demo import cluster_group_a_templates, cluster_group_b_templates, cluster_group_c_templates
from lib.db_config import get_db_config
from mixed_traffic_test import bundle_params, render_bundle_sql
from optimized_config import PROD180_PREAGG_BUNDLES


ROOT = Path(__file__).resolve().parent


PREAGG_BUNDLES = set(PROD180_PREAGG_BUNDLES)


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def tabular(rows: tuple[tuple[Any, ...], ...], columns: tuple[str, ...]) -> str:
    out = ["\t".join(columns)]
    for row in rows:
        out.append("\t".join("" if value is None else str(value) for value in row))
    return "\n".join(out)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct / 100.0
    lo = math.floor(rank)
    hi = min(lo + 1, len(ordered) - 1)
    frac = rank - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def summarize_bundle(records: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [float(item["ms"]) for item in records if float(item["ms"]) >= 0]
    return {
        "n": len(records),
        "errors": sum(1 for item in records if item.get("error")),
        "over350": sum(1 for item in records if float(item["ms"]) > 350),
        "over500": sum(1 for item in records if float(item["ms"]) > 500),
        "p95": percentile(ok, 95),
        "max": max(ok) if ok else -1.0,
    }


def choose_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    error_records = [item for item in records if item.get("error")]
    if error_records:
        # Prefer the event whose total event latency was worst, because it is
        # most likely to reveal the plan that hurt the user-visible path.
        return max(error_records, key=lambda item: float(item["event_ms"]))
    return max(records, key=lambda item: float(item["ms"]))


def build_bundle_catalog() -> dict[str, tuple[Any, str]]:
    catalog: dict[str, tuple[Any, str]] = {}
    for bundle in cluster_group_a_templates():
        catalog[bundle.bundle_id] = (bundle, "A")
    for bundle in cluster_group_b_templates():
        catalog[bundle.bundle_id] = (bundle, "B")
    for bundle in cluster_group_c_templates():
        catalog[bundle.bundle_id] = (bundle, "C")
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mixed-json", required=True)
    parser.add_argument("--slow-csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--explain-timeout-ms", type=int, default=5000)
    parser.add_argument("--isolation-read-engines", default="tikv,tidb")
    parser.add_argument("--distinct-agg-pushdown", action="store_true")
    parser.add_argument("--force-inline-cte", choices=["0", "1"], default=None)
    parser.add_argument("--bundle-id", action="append", default=[])
    args = parser.parse_args()

    mixed_path = resolve_path(args.mixed_json)
    slow_csv_path = resolve_path(args.slow_csv)
    output_path = resolve_path(args.output)

    mixed = json.loads(mixed_path.read_text(encoding="utf-8"))
    slow_rows = list(csv.DictReader(slow_csv_path.open()))
    problem_bundle_ids = [row["bundle_id"] for row in slow_rows]
    if args.bundle_id:
        selected = set(args.bundle_id)
        problem_bundle_ids = [bundle_id for bundle_id in problem_bundle_ids if bundle_id in selected]

    events_by_invoice: dict[str, dict[str, Any]] = {}
    for event in mixed.get("sampled_normal_events", []) + mixed.get("sampled_hot_events", []):
        events_by_invoice[event["invoice_number"]] = event

    records_by_bundle: dict[str, list[dict[str, Any]]] = {bundle_id: [] for bundle_id in problem_bundle_ids}
    for event_result in mixed["read_results"]:
        for bundle_result in event_result.get("bundle_results", []):
            bundle_id = bundle_result["bundle_id"]
            if bundle_id not in records_by_bundle:
                continue
            records_by_bundle[bundle_id].append(
                {
                    **bundle_result,
                    "event": event_result["event"],
                    "event_ms": event_result["ms"],
                    "kind": event_result["kind"],
                    "hot_field": event_result.get("hot_field"),
                }
            )

    catalog = build_bundle_catalog()
    cfg = get_db_config(save_msg="explain problem bundles")
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)

    lines: list[str] = []
    lines.append("# Problem Bundle SQL Plans")
    lines.append("")
    lines.append(f"- Mixed JSON: `{mixed_path}`")
    lines.append(f"- Slow CSV: `{slow_csv_path}`")
    lines.append(f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Test start epoch: `{mixed.get('test_start')}`")
    lines.append(f"- Session read engines: `{args.isolation_read_engines}`")
    lines.append(f"- Distinct agg pushdown: `{args.distinct_agg_pushdown}`")
    lines.append(f"- Force inline CTE: `{args.force_inline_cte}`")
    lines.append(f"- EXPLAIN ANALYZE max_execution_time: `{args.explain_timeout_ms}ms`")
    lines.append("")

    with conn.cursor() as cur:
        cur.execute("SET SESSION tidb_isolation_read_engines = %s", (args.isolation_read_engines,))
        if args.distinct_agg_pushdown:
            cur.execute("SET SESSION tidb_opt_distinct_agg_push_down = 1")
        if args.force_inline_cte is not None:
            cur.execute(f"SET SESSION tidb_opt_force_inline_cte = {int(args.force_inline_cte)}")
        cur.execute("SET SESSION max_execution_time = %s", (args.explain_timeout_ms,))
        cur.execute("SHOW VARIABLES WHERE Variable_name IN ('tidb_isolation_read_engines', 'tidb_opt_distinct_agg_push_down', 'tidb_opt_force_inline_cte')")
        lines.append("## Session Variables")
        lines.append("")
        lines.append("```text")
        lines.append(tabular(cur.fetchall(), tuple(desc[0] for desc in cur.description)))
        lines.append("```")
        lines.append("")

        for index, bundle_id in enumerate(problem_bundle_ids, start=1):
            records = records_by_bundle[bundle_id]
            if not records:
                continue
            chosen = choose_record(records)
            event = events_by_invoice[chosen["event"]]
            bundle, group = catalog[bundle_id]
            reference_time = datetime.fromisoformat(event["reference_time"])
            sql = render_bundle_sql(
                bundle,
                group,
                reference_time,
                hinted_a=set(),
                preagg_bundles=PREAGG_BUNDLES,
                preagg_layout=mixed.get("preagg_layout", "prod180"),
            )
            params = bundle_params(
                bundle,
                reference_time,
                event["bindings"],
                PREAGG_BUNDLES,
                mixed.get("preagg_layout", "prod180"),
            )
            stats = summarize_bundle(records)
            explain_sql = "EXPLAIN ANALYZE " + sql.rstrip().rstrip(";")

            lines.append(f"## {index}. {bundle_id}")
            lines.append("")
            lines.append(f"- Group/window/filter: `{group}` / `{getattr(bundle, 'window_days', None)}d` / `{getattr(bundle, 'base_filter', None)}`")
            lines.append(f"- Preagg applied: `{bundle_id in PREAGG_BUNDLES}`")
            lines.append(f"- Chosen event: `{chosen['event']}` kind=`{chosen['kind']}` hot_field=`{chosen.get('hot_field')}` event_ms=`{float(chosen['event_ms']):.1f}` bundle_ms=`{float(chosen['ms']):.1f}` error=`{chosen.get('error')}`")
            lines.append(f"- Bundle stats: n=`{stats['n']}` errors=`{stats['errors']}` >350=`{stats['over350']}` >500=`{stats['over500']}` p95=`{stats['p95']:.1f}ms` max=`{stats['max']:.1f}ms`")
            lines.append("")
            lines.append("### SQL")
            lines.append("")
            lines.append("```sql")
            lines.append(sql)
            lines.append("```")
            lines.append("")
            lines.append("### Params")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(params, indent=2, default=str))
            lines.append("```")
            lines.append("")
            lines.append("### EXPLAIN ANALYZE")
            lines.append("")
            lines.append("```text")
            started = time.perf_counter()
            try:
                cur.execute(explain_sql, params)
                rows = cur.fetchall()
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                lines.append(f"-- explain_analyze_elapsed_ms={elapsed_ms:.1f}")
                lines.append(tabular(rows, tuple(desc[0] for desc in cur.description)))
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                lines.append(f"-- EXPLAIN ANALYZE failed after {elapsed_ms:.1f}ms: {exc!r}")
                try:
                    cur.execute("SET SESSION max_execution_time = %s", (args.explain_timeout_ms,))
                    cur.execute("EXPLAIN " + sql.rstrip().rstrip(";"), params)
                    rows = cur.fetchall()
                    lines.append("")
                    lines.append("-- Fallback EXPLAIN")
                    lines.append(tabular(rows, tuple(desc[0] for desc in cur.description)))
                except Exception as explain_exc:
                    lines.append(f"-- Fallback EXPLAIN failed: {explain_exc!r}")
                finally:
                    cur.execute("SET SESSION max_execution_time = %s", (args.explain_timeout_ms,))
            lines.append("```")
            lines.append("")

        test_start = int(float(mixed.get("test_start", 0)))
        lines.append("## Slow Query Samples From The Same Test Window")
        lines.append("")
        lines.append("```text")
        cur.execute(
            """
            SELECT `Time`, ROUND(Query_time, 3) AS query_s, Succ, Index_names,
                   Storage_from_kv, Storage_from_mpp,
                   LEFT(REPLACE(REPLACE(Query, '\n', ' '), '\t', ' '), 900) AS query_prefix,
                   Plan
            FROM information_schema.CLUSTER_SLOW_QUERY
            WHERE UNIX_TIMESTAMP(`Time`) >= %s
              AND DB = 'intuit_risk'
              AND Is_internal = 0
            ORDER BY Query_time DESC
            LIMIT 30
            """,
            (test_start,),
        )
        lines.append(tabular(cur.fetchall(), tuple(desc[0] for desc in cur.description)))
        lines.append("```")

    conn.close()
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
