#!/usr/bin/env python3
"""Targeted experiments for residual slow Group B 180d distinct bundles."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pymysql

from explain_problem_bundles import tabular
from lib.db_config import get_db_config


ROOT = Path(__file__).resolve().parent

SPECS: dict[str, dict[str, Any]] = {
    "group_b_bundle_018": {
        "key_column": "input_ip",
        "key_value": "135.232.20.92",
        "helper_cutoff_day": "2025-10-11",
        "raw_start": "2025-10-11 09:39:36.398000",
        "raw_end": "2025-10-12 00:00:00.000000",
        "templates": [
            ("b_0146", "exact_id"),
            ("b_0150", "smart_id"),
            ("b_0154", "true_ip"),
            ("b_0158", "agent_type"),
        ],
        "previous_original_ms": 1496.6,
        "previous_best_ms": 695.3,
    },
    "group_b_bundle_020": {
        "key_column": "true_ip",
        "key_value": "74.179.68.52",
        "helper_cutoff_day": "2025-10-12",
        "raw_start": "2025-10-12 19:16:29.762000",
        "raw_end": "2025-10-13 00:00:00.000000",
        "templates": [
            ("b_0162", "exact_id"),
            ("b_0166", "smart_id"),
            ("b_0170", "input_ip"),
            ("b_0174", "proxy_ip"),
            ("b_0178", "agent_type"),
        ],
        "previous_original_ms": 2884.2,
        "previous_best_ms": 1128.4,
    },
}

BASE_SESSION: dict[str, Any] = {
    "tidb_isolation_read_engines": "tikv,tidb",
    "tidb_opt_force_inline_cte": 0,
    "tidb_opt_distinct_agg_push_down": 0,
    "tidb_opt_agg_push_down": 0,
    "tidb_hashagg_final_concurrency": 4,
    "tidb_hashagg_partial_concurrency": 4,
    "tidb_distsql_scan_concurrency": 15,
    "tidb_executor_concurrency": 5,
    "tidb_enable_paging": "ON",
}

SETTINGS = [
    ("base", {}),
    (
        "distinct_pd_hash16",
        {
            "tidb_opt_distinct_agg_push_down": 1,
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
    ("agg_pd", {"tidb_opt_agg_push_down": 1}),
    (
        "agg_pd_hash16",
        {
            "tidb_opt_agg_push_down": 1,
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
    (
        "agg_pd_distinct_pd_hash16",
        {
            "tidb_opt_agg_push_down": 1,
            "tidb_opt_distinct_agg_push_down": 1,
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
    (
        "agg_pd_scan30_exec10",
        {
            "tidb_opt_agg_push_down": 1,
            "tidb_distsql_scan_concurrency": 30,
            "tidb_executor_concurrency": 10,
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
    (
        "agg_pd_paging_off",
        {
            "tidb_opt_agg_push_down": 1,
            "tidb_enable_paging": "OFF",
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
]


def quote_ident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def metric_name(template_id: str) -> str:
    return "metric__" + template_id


def raw_boundary_sql(spec: dict[str, Any]) -> str:
    select_cols = [
        f"    d.{quote_ident(col)} AS {quote_ident(f'raw_distinct_{idx}')}"
        for idx, (_, col) in enumerate(spec["templates"])
    ]
    return (
        "raw_boundary AS (\n"
        "  SELECT\n"
        + ",\n".join(select_cols)
        + "\n"
        "  FROM deviceprofile_fact d\n"
        f"  WHERE d.{quote_ident(spec['key_column'])} = %s\n"
        "    AND d.jms_timestamp IS NOT NULL\n"
        f"    AND d.jms_timestamp >= '{spec['raw_start']}'\n"
        f"    AND d.jms_timestamp < '{spec['raw_end']}'\n"
        ")"
    )


def helper_predicate(spec: dict[str, Any], template_clause: str) -> str:
    return (
        "x.bundle_id = "
        + sql_literal(spec["bundle_id"])
        + "\n    AND "
        + template_clause
        + "\n    AND x.key1 = %s AND x.key2 = ''\n"
        f"    AND x.event_day > '{spec['helper_cutoff_day']}'"
    )


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def raw_union_parts(spec: dict[str, Any]) -> list[str]:
    parts = []
    for idx, (template_id, _) in enumerate(spec["templates"]):
        raw_col = quote_ident(f"raw_distinct_{idx}")
        parts.append(
            f"  SELECT '{template_id}' AS template_id, CAST({raw_col} AS CHAR(256)) AS distinct_value "
            f"FROM raw_boundary WHERE {raw_col} IS NOT NULL"
        )
    return parts


def distinct_values_cte(spec: dict[str, Any]) -> str:
    template_list = ", ".join(sql_literal(tid) for tid, _ in spec["templates"])
    parts = [
        (
            "  SELECT x.template_id, x.distinct_value\n"
            "  FROM `group_b_180d_daily_distinct` x\n"
            "  WHERE "
            + helper_predicate(spec, f"x.template_id IN ({template_list})")
        )
    ] + raw_union_parts(spec)
    return "distinct_values AS (\n" + "\n  UNION ALL\n".join(parts) + "\n)"


def pivot_from_counts(spec: dict[str, Any]) -> str:
    parts = [
        f"  COALESCE(MAX(CASE WHEN template_id = '{template_id}' THEN distinct_count END), 0) AS {quote_ident(metric_name(template_id))}"
        for template_id, _ in spec["templates"]
    ]
    return "SELECT\n" + ",\n".join(parts) + "\nFROM counts"


def select_case_distinct(spec: dict[str, Any]) -> str:
    parts = [
        f"  COUNT(DISTINCT CASE WHEN template_id = '{template_id}' THEN distinct_value END) AS {quote_ident(metric_name(template_id))}"
        for template_id, _ in spec["templates"]
    ]
    return "SELECT\n" + ",\n".join(parts) + "\nFROM distinct_values"


def select_case_approx(spec: dict[str, Any]) -> str:
    parts = [
        f"  APPROX_COUNT_DISTINCT(CASE WHEN template_id = '{template_id}' THEN distinct_value END) AS {quote_ident(metric_name(template_id))}"
        for template_id, _ in spec["templates"]
    ]
    return "SELECT\n" + ",\n".join(parts) + "\nFROM distinct_values"


def render_current_case_distinct(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql = f"WITH {raw_boundary_sql(spec)},\n{distinct_values_cte(spec)}\n{select_case_distinct(spec)};"
    return sql, (spec["key_value"], spec["key_value"])


def render_current_case_distinct_stream_hint(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql, params = render_current_case_distinct(spec)
    return sql.replace("SELECT\n  COUNT(DISTINCT", "SELECT /*+ STREAM_AGG() */\n  COUNT(DISTINCT", 1), params


def render_current_approx(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql = f"WITH {raw_boundary_sql(spec)},\n{distinct_values_cte(spec)}\n{select_case_approx(spec)};"
    return sql, (spec["key_value"], spec["key_value"])


def helper_only_where(spec: dict[str, Any]) -> str:
    template_list = ", ".join(sql_literal(tid) for tid, _ in spec["templates"])
    return (
        "FROM `group_b_180d_daily_distinct` x\n"
        "WHERE "
        + helper_predicate(spec, f"x.template_id IN ({template_list})")
    )


def render_helper_only_case_distinct(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    parts = [
        f"  COUNT(DISTINCT CASE WHEN x.template_id = '{template_id}' THEN x.distinct_value END) AS {quote_ident(metric_name(template_id))}"
        for template_id, _ in spec["templates"]
    ]
    sql = "SELECT\n" + ",\n".join(parts) + "\n" + helper_only_where(spec) + ";"
    return sql, (spec["key_value"],)


def render_helper_only_case_distinct_stream_hint(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql, params = render_helper_only_case_distinct(spec)
    return sql.replace("SELECT\n  COUNT(DISTINCT", "SELECT /*+ STREAM_AGG() */\n  COUNT(DISTINCT", 1), params


def render_helper_only_group_by_template(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql = (
        "WITH counts AS (\n"
        "  SELECT x.template_id, COUNT(DISTINCT x.distinct_value) AS distinct_count\n"
        "  "
        + helper_only_where(spec).replace("\n", "\n  ")
        + "\n"
        "  GROUP BY x.template_id\n"
        ")\n"
        f"{pivot_from_counts(spec)};"
    )
    return sql, (spec["key_value"],)


def render_helper_only_approx(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    parts = [
        f"  APPROX_COUNT_DISTINCT(CASE WHEN x.template_id = '{template_id}' THEN x.distinct_value END) AS {quote_ident(metric_name(template_id))}"
        for template_id, _ in spec["templates"]
    ]
    sql = "SELECT\n" + ",\n".join(parts) + "\n" + helper_only_where(spec) + ";"
    return sql, (spec["key_value"],)


def render_group_by_template(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql = (
        f"WITH {raw_boundary_sql(spec)},\n"
        f"{distinct_values_cte(spec)},\n"
        "counts AS (\n"
        "  SELECT template_id, COUNT(DISTINCT distinct_value) AS distinct_count\n"
        "  FROM distinct_values\n"
        "  GROUP BY template_id\n"
        ")\n"
        f"{pivot_from_counts(spec)};"
    )
    return sql, (spec["key_value"], spec["key_value"])


def render_two_stage_dedup(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql = (
        f"WITH {raw_boundary_sql(spec)},\n"
        f"{distinct_values_cte(spec)},\n"
        "dedup AS (\n"
        "  SELECT template_id, distinct_value\n"
        "  FROM distinct_values\n"
        "  GROUP BY template_id, distinct_value\n"
        "), counts AS (\n"
        "  SELECT template_id, COUNT(*) AS distinct_count\n"
        "  FROM dedup\n"
        "  GROUP BY template_id\n"
        ")\n"
        f"{pivot_from_counts(spec)};"
    )
    return sql, (spec["key_value"], spec["key_value"])


def render_helper_dedup_first(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    template_list = ", ".join(sql_literal(tid) for tid, _ in spec["templates"])
    sql = (
        f"WITH {raw_boundary_sql(spec)},\n"
        "helper_dedup AS (\n"
        "  SELECT x.template_id, x.distinct_value\n"
        "  FROM `group_b_180d_daily_distinct` x\n"
        "  WHERE "
        + helper_predicate(spec, f"x.template_id IN ({template_list})")
        + "\n"
        "  GROUP BY x.template_id, x.distinct_value\n"
        "), all_dedup AS (\n"
        "  SELECT template_id, distinct_value FROM helper_dedup\n"
        "  UNION\n"
        + "\n  UNION\n".join(raw_union_parts(spec))
        + "\n), counts AS (\n"
        "  SELECT template_id, COUNT(*) AS distinct_count\n"
        "  FROM all_dedup\n"
        "  GROUP BY template_id\n"
        ")\n"
        f"{pivot_from_counts(spec)};"
    )
    return sql, (spec["key_value"], spec["key_value"])


def render_split_scalar_union_all(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    count_parts = []
    params: list[Any] = [spec["key_value"]]
    for idx, (template_id, _) in enumerate(spec["templates"]):
        raw_col = quote_ident(f"raw_distinct_{idx}")
        count_parts.append(
            "  SELECT "
            + sql_literal(template_id)
            + " AS template_id, COUNT(DISTINCT u.distinct_value) AS distinct_count\n"
            "  FROM (\n"
            "    SELECT x.distinct_value\n"
            "    FROM `group_b_180d_daily_distinct` x\n"
            "    WHERE "
            + helper_predicate(spec, f"x.template_id = '{template_id}'")
            + "\n"
            "    UNION ALL\n"
            f"    SELECT CAST({raw_col} AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE {raw_col} IS NOT NULL\n"
            "  ) u"
        )
        params.append(spec["key_value"])
    sql = (
        f"WITH {raw_boundary_sql(spec)},\n"
        "counts AS (\n"
        + "\n  UNION ALL\n".join(count_parts)
        + "\n)\n"
        f"{pivot_from_counts(spec)};"
    )
    return sql, tuple(params)


def render_split_union_distinct_countstar(spec: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    count_parts = []
    params: list[Any] = [spec["key_value"]]
    for idx, (template_id, _) in enumerate(spec["templates"]):
        raw_col = quote_ident(f"raw_distinct_{idx}")
        count_parts.append(
            "  SELECT "
            + sql_literal(template_id)
            + " AS template_id, COUNT(*) AS distinct_count\n"
            "  FROM (\n"
            "    SELECT x.distinct_value\n"
            "    FROM `group_b_180d_daily_distinct` x\n"
            "    WHERE "
            + helper_predicate(spec, f"x.template_id = '{template_id}'")
            + "\n"
            "    UNION\n"
            f"    SELECT CAST({raw_col} AS CHAR(256)) AS distinct_value FROM raw_boundary WHERE {raw_col} IS NOT NULL\n"
            "  ) u"
        )
        params.append(spec["key_value"])
    sql = (
        f"WITH {raw_boundary_sql(spec)},\n"
        "counts AS (\n"
        + "\n  UNION ALL\n".join(count_parts)
        + "\n)\n"
        f"{pivot_from_counts(spec)};"
    )
    return sql, tuple(params)


SHAPES = [
    ("current_case_distinct", render_current_case_distinct),
    ("current_case_distinct_stream_hint", render_current_case_distinct_stream_hint),
    ("current_approx_not_exact", render_current_approx),
    ("helper_only_case_distinct_raw_empty_guard", render_helper_only_case_distinct),
    ("helper_only_case_distinct_stream_hint_raw_empty_guard", render_helper_only_case_distinct_stream_hint),
    ("helper_only_group_by_template_raw_empty_guard", render_helper_only_group_by_template),
    ("helper_only_approx_not_exact_raw_empty_guard", render_helper_only_approx),
    ("group_by_template", render_group_by_template),
    ("two_stage_dedup", render_two_stage_dedup),
    ("helper_dedup_first", render_helper_dedup_first),
    ("split_scalar_union_all", render_split_scalar_union_all),
    ("split_union_distinct_countstar", render_split_union_distinct_countstar),
]


def apply_session(cur: pymysql.cursors.Cursor, settings: dict[str, Any], timeout_ms: int) -> None:
    combined = dict(BASE_SESSION)
    combined.update(settings)
    cur.execute("SET SESSION tidb_isolation_read_engines = %s", (combined["tidb_isolation_read_engines"],))
    for name in [
        "tidb_opt_force_inline_cte",
        "tidb_opt_distinct_agg_push_down",
        "tidb_opt_agg_push_down",
        "tidb_hashagg_final_concurrency",
        "tidb_hashagg_partial_concurrency",
        "tidb_distsql_scan_concurrency",
        "tidb_executor_concurrency",
    ]:
        cur.execute(f"SET SESSION {name} = {int(combined[name])}")
    cur.execute("SET SESSION tidb_enable_paging = %s", (combined["tidb_enable_paging"],))
    cur.execute("SET SESSION max_execution_time = %s", (timeout_ms,))


def explain_analyze(
    cur: pymysql.cursors.Cursor,
    sql: str,
    params: tuple[Any, ...],
    settings: dict[str, Any],
    timeout_ms: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        apply_session(cur, settings, timeout_ms)
        cur.execute("EXPLAIN ANALYZE " + sql.rstrip().rstrip(";"), params)
        rows = cur.fetchall()
        columns = tuple(desc[0] for desc in cur.description)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        cur.execute("SHOW WARNINGS")
        warnings = cur.fetchall()
        return {
            "ok": True,
            "elapsed_ms": elapsed_ms,
            "plan": tabular(rows, columns),
            "warnings": [list(w) for w in warnings],
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {"ok": False, "elapsed_ms": elapsed_ms, "error": repr(exc), "plan": "", "warnings": []}


def helper_row_counts(cur: pymysql.cursors.Cursor, spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for template_id, _ in spec["templates"]:
        started = time.perf_counter()
        cur.execute(
            """
SELECT MIN(event_day), MAX(event_day), COUNT(*) AS row_count
FROM group_b_180d_daily_distinct
WHERE bundle_id=%s AND template_id=%s AND key1=%s AND key2=''
""",
            (spec["bundle_id"], template_id, spec["key_value"]),
        )
        min_day, max_day, row_count = cur.fetchone()
        rows.append(
            {
                "template_id": template_id,
                "min_day": str(min_day) if min_day is not None else None,
                "max_day": str(max_day) if max_day is not None else None,
                "row_count": int(row_count),
                "elapsed_ms": (time.perf_counter() - started) * 1000.0,
            }
        )
    return rows


def write_report(output: Path, payload: dict[str, Any]) -> None:
    lines = []
    lines.append("# Residual Group B Optimization Attempts")
    lines.append("")
    lines.append(f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append("- Scope: only `group_b_bundle_018` and `group_b_bundle_020`")
    lines.append("- All runs force `tidb_isolation_read_engines='tikv,tidb'`.")
    lines.append("")
    for bundle_id, bundle in payload["bundles"].items():
        lines.append(f"## {bundle_id}")
        lines.append("")
        lines.append(f"- Key: `{bundle['spec']['key_column']} = {bundle['spec']['key_value']}`")
        lines.append(f"- Previous original/best: `{bundle['spec']['previous_original_ms']} ms` / `{bundle['spec']['previous_best_ms']} ms`")
        lines.append("")
        lines.append("### Helper Rows")
        lines.append("")
        lines.append("| Template | Min day | Max day | Rows | Count time |")
        lines.append("| --- | --- | --- | ---: | ---: |")
        for row in bundle["helper_rows"]:
            lines.append(
                f"| `{row['template_id']}` | `{row['min_day']}` | `{row['max_day']}` | {row['row_count']} | {row['elapsed_ms']:.1f} ms |"
            )
        lines.append("")
        lines.append("### Candidate Timings")
        lines.append("")
        lines.append("| Shape | Settings | Time | Result |")
        lines.append("| --- | --- | ---: | --- |")
        for result in sorted(bundle["results"], key=lambda item: item["elapsed_ms"] if item["ok"] else 1e18):
            status = "ok" if result["ok"] else result["error"]
            lines.append(
                f"| `{result['shape']}` | `{result['setting_name']}` | {result['elapsed_ms']:.1f} ms | {status} |"
            )
        lines.append("")
        best = bundle.get("best")
        if best:
            lines.append("### Best Attempt")
            lines.append("")
            lines.append(f"- Shape: `{best['shape']}`")
            lines.append(f"- Settings: `{best['setting_name']}` / `{best['settings']}`")
            lines.append(f"- Time: `{best['elapsed_ms']:.1f} ms`")
            lines.append("")
            lines.append("#### SQL")
            lines.append("")
            lines.append("```sql")
            lines.append(best["sql"])
            lines.append("```")
            lines.append("")
            lines.append("#### Params")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(best["params"], indent=2, default=str))
            lines.append("```")
            lines.append("")
            lines.append("#### EXPLAIN ANALYZE")
            lines.append("")
            lines.append("```text")
            lines.append(f"-- explain_analyze_elapsed_ms={best['elapsed_ms']:.1f}")
            lines.append(best["plan"])
            lines.append("```")
            lines.append("")
        lines.append("### All Attempt SQL")
        lines.append("")
        for shape_name, sql in bundle["shape_sql"].items():
            lines.append(f"#### {shape_name}")
            lines.append("")
            lines.append("```sql")
            lines.append(sql)
            lines.append("```")
            lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/residual_group_b_optimization_attempts.md")
    parser.add_argument("--json-output", default="results/residual_group_b_optimization_attempts.json")
    parser.add_argument("--timeout-ms", type=int, default=45000)
    parser.add_argument("--shape", action="append", help="Run only this shape name; may be repeated")
    parser.add_argument("--setting", action="append", help="Run only this setting name; may be repeated")
    args = parser.parse_args()

    cfg = get_db_config(save_msg="residual group b optimization attempts")
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)
    payload: dict[str, Any] = {"generated": datetime.now().isoformat(timespec="seconds"), "bundles": {}}
    try:
        with conn.cursor() as cur:
            cur.execute("SET SESSION tidb_isolation_read_engines=%s", ("tikv,tidb",))
            cur.execute("SET SESSION max_execution_time=%s", (args.timeout_ms,))
            for bundle_id, raw_spec in SPECS.items():
                spec = dict(raw_spec)
                spec["bundle_id"] = bundle_id
                print(f"== {bundle_id} helper rows ==", flush=True)
                helper_rows = helper_row_counts(cur, spec)
                for row in helper_rows:
                    print(row, flush=True)

                results = []
                shape_sql: dict[str, str] = {}
                shape_filter = set(args.shape or [])
                setting_filter = set(args.setting or [])
                for shape_name, renderer in SHAPES:
                    if shape_filter and shape_name not in shape_filter:
                        continue
                    sql, params = renderer(spec)
                    shape_sql[shape_name] = sql
                    for setting_name, setting in SETTINGS:
                        if setting_filter and setting_name not in setting_filter:
                            continue
                        print(f"== {bundle_id} {shape_name} {setting_name} ==", flush=True)
                        result = explain_analyze(cur, sql, params, setting, args.timeout_ms)
                        result.update(
                            {
                                "bundle_id": bundle_id,
                                "shape": shape_name,
                                "setting_name": setting_name,
                                "settings": setting,
                                "sql": sql,
                                "params": params,
                            }
                        )
                        print(
                            f"{bundle_id} {shape_name} {setting_name}: "
                            f"{'ok' if result['ok'] else 'failed'} {result['elapsed_ms']:.1f} ms",
                            flush=True,
                        )
                        results.append(result)

                ok_results = [item for item in results if item["ok"]]
                best = min(ok_results, key=lambda item: item["elapsed_ms"]) if ok_results else None
                payload["bundles"][bundle_id] = {
                    "spec": spec,
                    "helper_rows": helper_rows,
                    "shape_sql": shape_sql,
                    "results": results,
                    "best": best,
                }
    finally:
        conn.close()

    output = ROOT / args.output
    json_output = ROOT / args.json_output
    output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    write_report(output, payload)
    print(output)
    print(json_output)


if __name__ == "__main__":
    main()
