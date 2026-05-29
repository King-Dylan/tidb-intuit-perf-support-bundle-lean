#!/usr/bin/env python3 -u
"""Build production-style consolidated 180d daily pre-aggregation tables.

This intentionally avoids one physical table per bundle. The six-table shape is:

  group_a_180d_daily_rollup      group_a_180d_daily_distinct
  group_b_180d_daily_rollup      group_b_180d_daily_distinct
  group_c_180d_daily_rollup      group_c_180d_daily_distinct

The runner can query these tables with PREAGG_LAYOUT=prod180.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.db_config import get_db_config
from preagg_rollups import (
    all_bundles,
    build_distinct_insert_sql,
    build_daily_insert_sql,
    bundle_rollup_metrics,
    configure_build_session,
    day_filter,
    execute_sql,
    is_avg_helper,
    key_not_null_predicates,
    metric_expr,
    prod180_distinct_table,
    prod180_rollup_metrics,
    prod180_rollup_table,
    quote_ident,
    source_parts,
    sql_literal,
    presence_column,
)

sys.stdout.reconfigure(line_buffering=True)

TABLE_OPTIONS = (
    f"SHARD_ROW_ID_BITS = {os.environ.get('INTUIT_PREAGG_SHARD_ROW_ID_BITS', '4')} "
    f"PRE_SPLIT_REGIONS = {os.environ.get('INTUIT_PREAGG_PRE_SPLIT_REGIONS', '3')}"
)

GROUPS = ("A", "B", "C")


def parse_groups(value: str | None) -> tuple[str, ...]:
    if not value:
        return GROUPS
    groups = tuple(part.strip().upper() for part in value.split(",") if part.strip())
    invalid = [group for group in groups if group not in GROUPS]
    if invalid:
        raise SystemExit(f"Invalid --groups value(s): {invalid}. Expected A,B,C.")
    return groups


def selected_180d_items() -> list[tuple[str, str, object]]:
    items: list[tuple[str, str, object]] = []
    for bundle_id, (group, bundle) in sorted(all_bundles().items()):
        if bundle.window_days == 180:
            items.append((bundle_id, group, bundle))
    return items


def metric_columns(group: str) -> list[str]:
    seen: set[str] = set()
    cols: list[str] = []
    for _, item_group, bundle in selected_180d_items():
        if item_group != group:
            continue
        rollups = prod180_rollup_metrics(group, bundle)
        for metric in rollups:
            if is_avg_helper(metric):
                candidates = [
                    f"{quote_ident(metric.output_column + '__sum')} DECIMAL(38,6) DEFAULT NULL",
                    f"{quote_ident(metric.output_column + '__count')} BIGINT DEFAULT NULL",
                ]
            else:
                candidates = [f"{quote_ident(metric.output_column)} DECIMAL(38,6) DEFAULT NULL"]
            if metric.extra_predicate and not metric.output_column.startswith("present__"):
                candidates.append(f"{quote_ident(presence_column(metric.template_id))} BIGINT DEFAULT NULL")
            for col in candidates:
                name = col.split()[0]
                if name not in seen:
                    seen.add(name)
                    cols.append(col)
    if not cols:
        # Some 180d groups are entirely exact-distinct today. Keep the rollup
        # table present so the production shape remains stable.
        cols.append("metric_placeholder BIGINT DEFAULT NULL")
    return cols


def create_rollup_sql(group: str) -> str:
    day_cols = (
        ["p_event_day DATE NOT NULL", "d_event_day DATE NOT NULL"]
        if group == "C"
        else ["event_day DATE NOT NULL"]
    )
    pk_day_cols = "p_event_day, d_event_day" if group == "C" else "event_day"
    day_indexes = "INDEX idx_event_day (p_event_day, d_event_day)" if group == "C" else "INDEX idx_event_day (event_day)"
    cols = [
        "bundle_id VARCHAR(64) NOT NULL",
        *day_cols,
        "key1 VARCHAR(128) NOT NULL",
        "key2 VARCHAR(128) NOT NULL DEFAULT ''",
        *metric_columns(group),
    ]
    return f"""
CREATE TABLE IF NOT EXISTS {quote_ident(prod180_rollup_table(group))} (
  {",\n  ".join(cols)},
  PRIMARY KEY (bundle_id, key1, key2, {pk_day_cols}) NONCLUSTERED,
  {day_indexes}
) {TABLE_OPTIONS};
""".strip()


def create_distinct_sql(group: str) -> str:
    day_cols = (
        ["p_event_day DATE NOT NULL", "d_event_day DATE NOT NULL"]
        if group == "C"
        else ["event_day DATE NOT NULL"]
    )
    pk_day_cols = "p_event_day, d_event_day" if group == "C" else "event_day"
    day_indexes = "INDEX idx_event_day (p_event_day, d_event_day)" if group == "C" else "INDEX idx_event_day (event_day)"
    return f"""
CREATE TABLE IF NOT EXISTS {quote_ident(prod180_distinct_table(group))} (
  bundle_id VARCHAR(64) NOT NULL,
  template_id VARCHAR(64) NOT NULL,
  {",\n  ".join(day_cols)},
  key1 VARCHAR(128) NOT NULL,
  key2 VARCHAR(128) NOT NULL DEFAULT '',
  distinct_value VARCHAR(256) NOT NULL,
  PRIMARY KEY (bundle_id, template_id, key1, key2, {pk_day_cols}, distinct_value) NONCLUSTERED,
  {day_indexes}
) {TABLE_OPTIONS};
""".strip()


def group_key_selects(bundle) -> tuple[str, str]:
    first = bundle.group_by_fields[0]
    second = bundle.group_by_fields[1] if len(bundle.group_by_fields) > 1 else None
    return first, second or "''"


def prod_day_selects(group: str) -> tuple[list[str], list[str], list[str]]:
    if group == "C":
        return (
            [
                "DATE(FROM_UNIXTIME(p.event_date / 1000)) AS p_event_day",
                "DATE(d.jms_timestamp) AS d_event_day",
            ],
            ["p_event_day", "d_event_day"],
            ["p_event_day", "d_event_day"],
        )
    _, day_expr, _ = source_parts(group)
    return ([f"{day_expr} AS event_day"], ["event_day"], ["event_day"])


def prod_build_day_filter(group: str, build_day: date | None) -> str | None:
    if group != "C":
        return day_filter(group, build_day)
    if build_day is None:
        return None
    next_day = build_day + timedelta(days=1)
    start_ms = int(datetime.combine(build_day, datetime.min.time()).timestamp() * 1000)
    end_ms = int(datetime.combine(next_day, datetime.min.time()).timestamp() * 1000)
    return f"p.event_date >= {start_ms} AND p.event_date < {end_ms}"


def build_prod_rollup_insert_sql(group: str, bundle, build_day: date | None = None) -> str | None:
    rollups = prod180_rollup_metrics(group, bundle)
    if not rollups:
        return None

    _, _, from_sql = source_parts(group)
    key1, key2 = group_key_selects(bundle)
    day_selects, day_columns, day_group_parts = prod_day_selects(group)
    select_parts = [
        f"{sql_literal(bundle.bundle_id)} AS bundle_id",
        *day_selects,
        f"{key1} AS key1",
        f"{key2} AS key2",
    ]
    columns = ["bundle_id", *day_columns, "key1", "key2"]
    where_parts = key_not_null_predicates(bundle)
    for metric in rollups:
        if is_avg_helper(metric):
            select_parts.append(metric.daily_expr)
            columns.extend([metric.output_column + "__sum", metric.output_column + "__count"])
        else:
            select_parts.append(f"{metric.daily_expr} AS {quote_ident(metric.output_column)}")
            columns.append(metric.output_column)
        if metric.extra_predicate and metric.output_column.startswith("present__"):
            where_parts.append(f"({metric.extra_predicate})")
        elif metric.extra_predicate:
            select_parts.append(
                f"SUM(CASE WHEN {metric.extra_predicate} THEN 1 ELSE 0 END) AS {quote_ident(presence_column(metric.template_id))}"
            )
            columns.append(presence_column(metric.template_id))
    if group in {"A", "C"}:
        where_parts.append("p.event_date IS NOT NULL")
    if group in {"B", "C"}:
        where_parts.append("d.jms_timestamp IS NOT NULL")
    df = prod_build_day_filter(group, build_day)
    if df:
        where_parts.append(df)

    group_parts = day_group_parts + list(bundle.group_by_fields)
    select_sql = ",\n  ".join(select_parts)
    column_sql = ", ".join(quote_ident(c) for c in columns)
    where_sql = " AND ".join(where_parts)
    group_sql = ", ".join(group_parts)
    return f"""
REPLACE INTO {quote_ident(prod180_rollup_table(group))} ({column_sql})
SELECT
  {select_sql}
{from_sql}
WHERE {where_sql}
GROUP BY {group_sql};
""".strip()


def build_prod_distinct_insert_sql(group: str, bundle, distinct, build_day: date | None = None) -> str:
    _, _, from_sql = source_parts(group)
    key1, key2 = group_key_selects(bundle)
    day_selects, day_columns, day_group_parts = prod_day_selects(group)
    select_parts = [
        f"{sql_literal(bundle.bundle_id)} AS bundle_id",
        f"{sql_literal(distinct.template_id)} AS template_id",
        *day_selects,
        f"{key1} AS key1",
        f"{key2} AS key2",
        f"CAST({distinct.distinct_expr} AS CHAR(256)) AS distinct_value",
    ]

    where_parts = key_not_null_predicates(bundle)
    where_parts.append(f"{distinct.distinct_expr} IS NOT NULL")
    if distinct.extra_predicate:
        where_parts.append(f"({distinct.extra_predicate})")
    if group in {"A", "C"}:
        where_parts.append("p.event_date IS NOT NULL")
    if group in {"B", "C"}:
        where_parts.append("d.jms_timestamp IS NOT NULL")
    df = prod_build_day_filter(group, build_day)
    if df:
        where_parts.append(df)

    group_parts = day_group_parts + list(bundle.group_by_fields) + ["distinct_value"]
    select_sql = ",\n  ".join(select_parts)
    where_sql = " AND ".join(where_parts)
    group_sql = ", ".join(group_parts)
    return f"""
REPLACE INTO {quote_ident(prod180_distinct_table(group))} (
  {", ".join(["bundle_id", "template_id", *day_columns, "key1", "key2", "distinct_value"])}
)
SELECT
  {select_sql}
{from_sql}
WHERE {where_sql}
GROUP BY {group_sql};
""".strip()


def date_range(start_day: date, end_day: date):
    day = start_day
    while day <= end_day:
        yield day
        day += timedelta(days=1)


def analyze_sql(group: str) -> list[str]:
    return [
        f"ANALYZE TABLE {quote_ident(prod180_rollup_table(group))};",
        f"ANALYZE TABLE {quote_ident(prod180_distinct_table(group))};",
    ]


def drop_tables(conn, dry_run: bool) -> None:
    for group in GROUPS:
        execute_sql(conn, f"DROP TABLE IF EXISTS {quote_ident(prod180_rollup_table(group))};", dry_run=dry_run)
        execute_sql(conn, f"DROP TABLE IF EXISTS {quote_ident(prod180_distinct_table(group))};", dry_run=dry_run)


def create_tables(conn, dry_run: bool) -> None:
    for group in GROUPS:
        execute_sql(conn, create_rollup_sql(group), dry_run=dry_run)
        execute_sql(conn, create_distinct_sql(group), dry_run=dry_run)


def analyze_tables(conn, dry_run: bool) -> None:
    for group in GROUPS:
        for sql in analyze_sql(group):
            execute_sql(conn, sql, dry_run=dry_run)


def build_one_day(conn, dry_run: bool, build_day: date | None, groups: tuple[str, ...] = GROUPS) -> None:
    label = build_day.isoformat() if build_day else "all-days"
    print(f"\n===== Building production 180d pre-agg day={label} =====")
    day_started = time.perf_counter()
    allowed_groups = set(groups)
    for bundle_id, group, bundle in selected_180d_items():
        if group not in allowed_groups:
            continue
        rollups, distincts = bundle_rollup_metrics(group, bundle)
        print(f"-- {bundle_id} group={group} rollups={len(rollups)} distincts={len(distincts)} day={label}")
        rollup_sql = build_prod_rollup_insert_sql(group, bundle, build_day)
        if rollup_sql:
            execute_sql(conn, rollup_sql, dry_run=dry_run)
        for distinct in distincts:
            execute_sql(conn, build_prod_distinct_insert_sql(group, bundle, distinct, build_day), dry_run=dry_run)
    print(f"===== Completed day={label} in {(time.perf_counter() - day_started):.1f}s =====\n")


def build_range(conn, dry_run: bool, start_day: date, end_day: date, groups: tuple[str, ...] = GROUPS) -> None:
    if start_day > end_day:
        raise SystemExit(f"--start-day must be <= --end-day, got {start_day} > {end_day}")
    total_days = (end_day - start_day).days + 1
    started = time.perf_counter()
    for idx, build_day in enumerate(date_range(start_day, end_day), start=1):
        print(f"\n### Day {idx}/{total_days}: {build_day} ###")
        build_one_day(conn, dry_run, build_day, groups=groups)
    print(f"### Completed {total_days} daily build chunks in {(time.perf_counter() - started):.1f}s ###")


def build_tables(
    conn,
    dry_run: bool,
    build_day: date | None,
    start_day: date | None,
    end_day: date | None,
    groups: tuple[str, ...] = GROUPS,
) -> None:
    if build_day and (start_day or end_day):
        raise SystemExit("Use either --day or --start-day/--end-day, not both.")
    if start_day or end_day:
        if not start_day or not end_day:
            raise SystemExit("Both --start-day and --end-day are required for range builds.")
        build_range(conn, dry_run, start_day, end_day, groups=groups)
        return
    build_one_day(conn, dry_run, build_day, groups=groups)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["drop", "create", "build", "create-build", "analyze", "rebuild"])
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--day", help="Optional single build day, YYYY-MM-DD")
    ap.add_argument("--start-day", help="Optional inclusive start day for daily chunked builds, YYYY-MM-DD")
    ap.add_argument("--end-day", help="Optional inclusive end day for daily chunked builds, YYYY-MM-DD")
    ap.add_argument("--groups", help="Comma-separated groups to operate on. Default: A,B,C")
    args = ap.parse_args()

    build_day = date.fromisoformat(args.day) if args.day else None
    start_day = date.fromisoformat(args.start_day) if args.start_day else None
    end_day = date.fromisoformat(args.end_day) if args.end_day else None
    groups = parse_groups(args.groups)
    conn = None
    if args.execute:
        import pymysql

        conn = pymysql.connect(**get_db_config(save_msg="production 180d pre-agg builder"))
        conn.autocommit(True)
        configure_build_session(conn)

    try:
        dry_run = not args.execute
        if args.action == "drop":
            for group in groups:
                execute_sql(conn, f"DROP TABLE IF EXISTS {quote_ident(prod180_rollup_table(group))};", dry_run=dry_run)
                execute_sql(conn, f"DROP TABLE IF EXISTS {quote_ident(prod180_distinct_table(group))};", dry_run=dry_run)
            return

        if args.action == "create":
            for group in groups:
                execute_sql(conn, create_rollup_sql(group), dry_run=dry_run)
                execute_sql(conn, create_distinct_sql(group), dry_run=dry_run)
            return

        if args.action == "analyze":
            for group in groups:
                for sql in analyze_sql(group):
                    execute_sql(conn, sql, dry_run=dry_run)
            return

        if args.action == "rebuild":
            for group in groups:
                execute_sql(conn, f"DROP TABLE IF EXISTS {quote_ident(prod180_rollup_table(group))};", dry_run=dry_run)
                execute_sql(conn, f"DROP TABLE IF EXISTS {quote_ident(prod180_distinct_table(group))};", dry_run=dry_run)
                execute_sql(conn, create_rollup_sql(group), dry_run=dry_run)
                execute_sql(conn, create_distinct_sql(group), dry_run=dry_run)
            build_tables(conn, dry_run=dry_run, build_day=build_day, start_day=start_day, end_day=end_day, groups=groups)
            for group in groups:
                for sql in analyze_sql(group):
                    execute_sql(conn, sql, dry_run=dry_run)
            return

        if args.action == "create-build":
            for group in groups:
                execute_sql(conn, create_rollup_sql(group), dry_run=dry_run)
                execute_sql(conn, create_distinct_sql(group), dry_run=dry_run)

        if args.action in {"build", "create-build"}:
            build_tables(conn, dry_run=dry_run, build_day=build_day, start_day=start_day, end_day=end_day, groups=groups)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
