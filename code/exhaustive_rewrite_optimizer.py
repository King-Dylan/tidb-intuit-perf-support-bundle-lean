#!/usr/bin/env python3
"""Exhaustively A/B test semantics-preserving SQL rewrites per bundle.

This is a validation harness, not a benchmark hot path. It renders the current
65-bundle SQL shape, generates conservative rewrite candidates, verifies the
candidate result matches the current result for representative events, and then
runs EXPLAIN ANALYZE under a small matrix of TiDB session settings.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pymysql

from demo import (
    GroupABundleSpec,
    GroupBBundleSpec,
    GroupCBundleSpec,
    build_group_a_metric_expr,
    build_group_b_metric_expr,
    build_group_c_metric_expr,
    build_presence_expr,
    cluster_group_a_templates,
    cluster_group_b_templates,
    cluster_group_c_templates,
    metric_column,
    presence_column,
)
from explore_scan_pruning_rewrites import (
    NUMERIC_SCORE_COLUMNS,
    render_group_a_dimension_rollup_sql,
    render_group_b_numeric_projection_sql,
)
from explain_problem_bundles import PREAGG_BUNDLES, choose_record, summarize_bundle, tabular
from final_compare_optimization_report import load_records
from lib.db_config import get_db_config
from mixed_traffic_test import bundle_params, render_bundle_sql


ROOT = Path(__file__).resolve().parent

SETTINGS: list[tuple[str, dict[str, Any]]] = [
    ("default", {}),
    ("hashagg_16_8", {"tidb_hashagg_final_concurrency": 16, "tidb_hashagg_partial_concurrency": 8}),
    ("distinct_pushdown", {"tidb_opt_distinct_agg_push_down": 1}),
    (
        "distinct_pushdown_hashagg_16_8",
        {
            "tidb_opt_distinct_agg_push_down": 1,
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
    (
        "agg_pushdown_hashagg_16_8",
        {
            "tidb_opt_agg_push_down": 1,
            "tidb_hashagg_final_concurrency": 16,
            "tidb_hashagg_partial_concurrency": 8,
        },
    ),
]

BASE_SESSION: dict[str, Any] = {
    "tidb_isolation_read_engines": "tikv,tidb",
    "tidb_opt_force_inline_cte": 0,
    "tidb_opt_distinct_agg_push_down": 0,
    "tidb_opt_agg_push_down": 0,
    "tidb_hashagg_final_concurrency": 4,
    "tidb_hashagg_partial_concurrency": 4,
}


@dataclass(frozen=True)
class Candidate:
    name: str
    method: str
    sql: str
    params: tuple[Any, ...]


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


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


def normalize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value.normalize())
    if isinstance(value, (int, float)):
        return str(Decimal(str(value)).normalize())
    if isinstance(value, str) and re.fullmatch(r"-?\d+(?:\.\d+)?(?:E[+-]?\d+)?", value, flags=re.I):
        return str(Decimal(value).normalize())
    return value


def normalize_rows(rows: tuple[tuple[Any, ...], ...]) -> list[list[Any]]:
    return [[normalize_value(cell) for cell in row] for row in rows]


def extract_plan_metrics(plan_text: str) -> dict[str, Any]:
    keys = [int(value) for value in re.findall(r"total_process_keys: (\d+)", plan_text)]
    tasks = sorted(set(re.findall(r"\b(root|cop\[tikv\]|mpp\[tiflash\])\b", plan_text)))
    access_objects: list[str] = []
    for line in plan_text.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 6 and parts[5].strip():
            access_objects.append(parts[5].strip())
    return {
        "total_process_keys_sum": sum(keys),
        "total_process_keys_max": max(keys) if keys else 0,
        "total_process_keys": keys,
        "tasks": tasks,
        "access_objects": access_objects[:12],
    }


def apply_session(cur, settings: dict[str, Any], max_execution_time_ms: int) -> None:
    combined = dict(BASE_SESSION)
    combined.update(settings)
    cur.execute("SET SESSION tidb_isolation_read_engines = %s", (combined["tidb_isolation_read_engines"],))
    cur.execute(f"SET SESSION tidb_opt_force_inline_cte = {int(combined['tidb_opt_force_inline_cte'])}")
    cur.execute(f"SET SESSION tidb_opt_distinct_agg_push_down = {int(combined['tidb_opt_distinct_agg_push_down'])}")
    cur.execute(f"SET SESSION tidb_opt_agg_push_down = {int(combined['tidb_opt_agg_push_down'])}")
    cur.execute(f"SET SESSION tidb_hashagg_final_concurrency = {int(combined['tidb_hashagg_final_concurrency'])}")
    cur.execute(f"SET SESSION tidb_hashagg_partial_concurrency = {int(combined['tidb_hashagg_partial_concurrency'])}")
    if "tidb_distsql_scan_concurrency" in combined:
        cur.execute(f"SET SESSION tidb_distsql_scan_concurrency = {int(combined['tidb_distsql_scan_concurrency'])}")
    if "tidb_executor_concurrency" in combined:
        cur.execute(f"SET SESSION tidb_executor_concurrency = {int(combined['tidb_executor_concurrency'])}")
    cur.execute("SET SESSION max_execution_time = %s", (max_execution_time_ms,))


def query_rows(cur, sql: str, params: tuple[Any, ...], max_execution_time_ms: int) -> dict[str, Any]:
    apply_session(cur, {}, max_execution_time_ms)
    started = time.perf_counter()
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        columns = tuple(desc[0] for desc in cur.description)
        return {
            "ok": True,
            "elapsed_ms": (time.perf_counter() - started) * 1000.0,
            "columns": columns,
            "rows": normalize_rows(rows),
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_ms": (time.perf_counter() - started) * 1000.0,
            "error": repr(exc),
        }


def explain_analyze(
    cur,
    sql: str,
    params: tuple[Any, ...],
    settings: dict[str, Any],
    max_execution_time_ms: int,
) -> dict[str, Any]:
    apply_session(cur, settings, max_execution_time_ms)
    started = time.perf_counter()
    try:
        cur.execute("EXPLAIN ANALYZE " + sql.rstrip().rstrip(";"), params)
        rows = cur.fetchall()
        columns = tuple(desc[0] for desc in cur.description)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        plan = tabular(rows, columns)
        return {
            "ok": True,
            "elapsed_ms": elapsed_ms,
            "plan": plan,
            **extract_plan_metrics(plan),
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_ms": (time.perf_counter() - started) * 1000.0,
            "error": repr(exc),
            "plan": "",
            "total_process_keys_sum": 0,
            "total_process_keys_max": 0,
            "total_process_keys": [],
            "tasks": [],
            "access_objects": [],
        }


def build_bundle_catalog() -> dict[str, tuple[Any, str]]:
    catalog: dict[str, tuple[Any, str]] = {}
    for bundle in cluster_group_a_templates():
        catalog[bundle.bundle_id] = (bundle, "A")
    for bundle in cluster_group_b_templates():
        catalog[bundle.bundle_id] = (bundle, "B")
    for bundle in cluster_group_c_templates():
        catalog[bundle.bundle_id] = (bundle, "C")
    return catalog


def selected_bundle_ids(args, catalog: dict[str, tuple[Any, str]], mixed: dict[str, Any]) -> list[str]:
    if args.bundle_id:
        return args.bundle_id
    if args.slow_only:
        records = load_records(mixed, list(catalog))
        return sorted(
            [
                bundle_id
                for bundle_id, rows in records.items()
                if rows and (summarize_bundle(rows)["over350"] > 0 or summarize_bundle(rows)["errors"] > 0)
            ]
        )
    return sorted(catalog)


def events_by_invoice(mixed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        event["invoice_number"]: event
        for event in mixed.get("sampled_normal_events", []) + mixed.get("sampled_hot_events", [])
    }


def choose_event_for_bundle(mixed: dict[str, Any], bundle_id: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    records = load_records(mixed, [bundle_id]).get(bundle_id, [])
    by_invoice = events_by_invoice(mixed)
    if records:
        chosen = choose_record(records)
        if chosen["event"] in by_invoice:
            return by_invoice[chosen["event"]], chosen
    samples = mixed.get("sampled_hot_events", []) + mixed.get("sampled_normal_events", [])
    if not samples:
        raise RuntimeError("Mixed JSON has no sampled events")
    return samples[0], None


def has_numeric_score_work(bundle: Any) -> bool:
    text = "\n".join(t.select_expr + "\n" + (t.extra_predicate or "") for t in bundle.templates)
    return any(f".{column}" in text for column in NUMERIC_SCORE_COLUMNS)


def render_group_c_inner_join_sql(bundle: GroupCBundleSpec, reference_time: datetime) -> str:
    return bundle.render_sql(reference_time).replace("LEFT OUTER JOIN", "JOIN")


def render_group_c_device_first_join_sql(bundle: GroupCBundleSpec, reference_time: datetime) -> str:
    cutoff_ms = int(reference_time.timestamp() * 1000) - (bundle.window_days * 86400 * 1000)
    cutoff_dt = datetime.fromtimestamp(cutoff_ms / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")
    select_parts: list[str] = []
    for tmpl in bundle.templates:
        select_parts.append(f"{build_group_c_metric_expr(tmpl)} AS `{metric_column(tmpl.template_id)}`")
        if tmpl.extra_predicate:
            select_parts.append(f"{build_presence_expr(tmpl.extra_predicate)} AS `{presence_column(tmpl.template_id)}`")
    sql = (
        "SELECT\n  "
        + ",\n  ".join(select_parts)
        + "\nFROM deviceprofile_fact d\nJOIN pmt_txn_fact p"
        + "\n  ON p.parsed_interaction_id = d.interaction_id"
        + f"\nWHERE {bundle.base_filter} AND d.jms_timestamp >= '{cutoff_dt}'"
        + f"\n  AND p.event_date >= {cutoff_ms}"
    )
    if bundle.base_filter.lower().startswith("d.") and set(bundle.group_by_fields) <= {bundle.base_filter.split("=", 1)[0].strip()}:
        return sql + "\nHAVING COUNT(*) > 0;"
    return sql + "\nGROUP BY " + ", ".join(bundle.group_by_fields) + ";"


def rewrite_numeric_score_expr(expr: str) -> str:
    rewritten = expr
    for column in NUMERIC_SCORE_COLUMNS:
        rewritten = rewritten.replace(f"CAST(d.{column} AS DECIMAL(10,2))", f"d.{column}__num")
        rewritten = rewritten.replace(
            f"d.{column} IS NOT NULL AND d.{column} != ''",
            f"d.{column}__num IS NOT NULL",
        )
    return rewritten


def render_group_c_numeric_projection_sql(bundle: GroupCBundleSpec, reference_time: datetime) -> str:
    cutoff_ms = int(reference_time.timestamp() * 1000) - (bundle.window_days * 86400 * 1000)
    cutoff_dt = datetime.fromtimestamp(cutoff_ms / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")
    select_parts: list[str] = []
    for tmpl in bundle.templates:
        metric_expr = rewrite_numeric_score_expr(build_group_c_metric_expr(tmpl))
        select_parts.append(f"{metric_expr} AS `{metric_column(tmpl.template_id)}`")
        if tmpl.extra_predicate:
            select_parts.append(
                f"{rewrite_numeric_score_expr(build_presence_expr(tmpl.extra_predicate))} AS `{presence_column(tmpl.template_id)}`"
            )

    device_columns = [
        "interaction_id",
        "exact_id",
        "smart_id",
        "input_ip",
        "true_ip",
        "proxy_ip",
        "agent_type",
    ]
    projected_columns = [f"d.{column}" for column in device_columns]
    projected_columns.extend(
        f"CASE WHEN d.{column} IS NOT NULL AND d.{column} != '' THEN CAST(d.{column} AS DECIMAL(10,2)) END AS `{column}__num`"
        for column in NUMERIC_SCORE_COLUMNS
    )
    inner_where = [f"d.jms_timestamp >= '{cutoff_dt}'"]
    outer_where = [f"p.event_date >= {cutoff_ms}"]
    if bundle.base_filter.lower().startswith("d."):
        inner_where.insert(0, bundle.base_filter)
    else:
        outer_where.insert(0, bundle.base_filter)

    sql = (
        "SELECT\n  "
        + ",\n  ".join(select_parts)
        + "\nFROM pmt_txn_fact p\nJOIN (\n"
        + "  SELECT "
        + ", ".join(projected_columns)
        + "\n  FROM deviceprofile_fact d\n"
        + "  WHERE "
        + " AND ".join(inner_where)
        + "\n) d\n"
        + "  ON p.parsed_interaction_id = d.interaction_id\n"
        + "WHERE "
        + " AND ".join(outer_where)
    )
    if bundle.base_filter.lower().startswith("d.") and set(bundle.group_by_fields) <= {bundle.base_filter.split("=", 1)[0].strip()}:
        return sql + "\nHAVING COUNT(*) > 0;"
    return sql + "\nGROUP BY " + ", ".join(bundle.group_by_fields) + ";"


def render_scalar_subquery_sql(bundle: Any, group: str, reference_time: datetime) -> tuple[str, tuple[Any, ...]]:
    if group == "A":
        table_sql = "pmt_txn_fact p"
        time_pred = f"p.event_date >= {int((reference_time.timestamp() - (bundle.window_days * 86400)) * 1000)}"
        metric_builder = build_group_a_metric_expr
    elif group == "B":
        table_sql = "deviceprofile_fact d"
        cutoff = (reference_time - timedelta(days=bundle.window_days)).strftime("%Y-%m-%d %H:%M:%S.%f")
        time_pred = f"d.jms_timestamp >= '{cutoff}'"
        metric_builder = build_group_b_metric_expr
    else:
        cutoff_ms = int(reference_time.timestamp() * 1000) - (bundle.window_days * 86400 * 1000)
        cutoff_dt = datetime.fromtimestamp(cutoff_ms / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")
        table_sql = "pmt_txn_fact p JOIN deviceprofile_fact d ON p.parsed_interaction_id = d.interaction_id"
        time_pred = f"p.event_date >= {cutoff_ms} AND d.jms_timestamp >= '{cutoff_dt}'"
        metric_builder = build_group_c_metric_expr

    key_params = tuple(bindings_placeholder for bindings_placeholder in bundle.param_names)
    del key_params

    base_where = f"{bundle.base_filter} AND {time_pred}"
    base_params = tuple(bundle.param_names)
    del base_params

    select_parts: list[str] = []
    param_repeats = 0
    for tmpl in bundle.templates:
        metric_where = base_where
        if tmpl.extra_predicate:
            metric_where += f" AND ({tmpl.extra_predicate})"
        # With the predicate moved into WHERE, the aggregate expression can use
        # the original select expression directly.
        metric_expr = tmpl.select_expr
        if tmpl.extra_predicate and tmpl.select_expr == "COUNT(*)":
            metric_expr = "COUNT(*)"
        elif tmpl.extra_predicate:
            metric_expr = re.sub(r"COUNT\(DISTINCT\((.*?)\)\)", r"COUNT(DISTINCT \1)", tmpl.select_expr, flags=re.I)
        select_parts.append(
            f"(SELECT {metric_expr} FROM {table_sql} WHERE {metric_where}) AS `{metric_column(tmpl.template_id)}`"
        )
        param_repeats += 1
        if tmpl.extra_predicate:
            select_parts.append(
                f"(SELECT COUNT(*) FROM {table_sql} WHERE {metric_where}) AS `{presence_column(tmpl.template_id)}`"
            )
            param_repeats += 1
    exists_sql = f"EXISTS (SELECT 1 FROM {table_sql} WHERE {base_where} LIMIT 1)"
    sql = "SELECT\n  " + ",\n  ".join(select_parts) + f"\nWHERE {exists_sql};"
    param_names = tuple(bundle.param_names) * (param_repeats + 1)
    return sql, param_names


def expand_param_names(param_names: tuple[str, ...], bindings: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(bindings.get(name) for name in param_names)


def candidate_sqls(
    bundle: Any,
    group: str,
    reference_time: datetime,
    bindings: dict[str, Any],
    current_params: tuple[Any, ...],
    preagg_bundles: set[str],
    preagg_layout: str,
) -> list[Candidate]:
    del preagg_layout
    candidates: list[Candidate] = []
    is_preagg = bundle.bundle_id in preagg_bundles

    if group == "A" and not is_preagg:
        try:
            candidates.append(
                Candidate(
                    "group_a_dimension_rollup",
                    "CASE pruning: pre-aggregate low-cardinality dimensions, then pivot CASE metrics from compact rows",
                    render_group_a_dimension_rollup_sql(bundle, reference_time),
                    current_params,
                )
            )
        except Exception:
            pass

    if group == "B" and not is_preagg and has_numeric_score_work(bundle):
        candidates.append(
            Candidate(
                "group_b_numeric_projection",
                "Expression pruning: compute score casts once in a derived table and reuse them",
                render_group_b_numeric_projection_sql(bundle, reference_time),
                current_params,
            )
        )

    if group == "C" and not is_preagg:
        candidates.append(
            Candidate(
                "group_c_inner_join",
                "Join rewrite: LEFT JOIN is semantically INNER because WHERE predicates require d-side rows",
                render_group_c_inner_join_sql(bundle, reference_time),
                current_params,
            )
        )
        if str(bundle.base_filter).lower().startswith("d."):
            candidates.append(
                Candidate(
                    "group_c_device_first_join",
                    "Join order rewrite: start from filtered device rows, then join payment rows",
                    render_group_c_device_first_join_sql(bundle, reference_time),
                    current_params,
                )
            )
        if has_numeric_score_work(bundle):
            candidates.append(
                Candidate(
                    "group_c_numeric_projection",
                    "Expression pruning: project numeric device scores once before join aggregation",
                    render_group_c_numeric_projection_sql(bundle, reference_time),
                    current_params,
                )
            )

    if not is_preagg and any(t.extra_predicate for t in bundle.templates) and len(bundle.templates) <= 45:
        try:
            scalar_sql, scalar_param_names = render_scalar_subquery_sql(bundle, group, reference_time)
            candidates.append(
                Candidate(
                    "filtered_scalar_subqueries",
                    "Predicate pushdown: move CASE predicates into independent WHERE clauses for selective metrics",
                    scalar_sql,
                    expand_param_names(scalar_param_names, bindings),
                )
            )
        except Exception:
            pass

    return candidates


def acceptance(current_best: dict[str, Any], candidate_best: dict[str, Any], same_result: bool) -> tuple[bool, str]:
    if not same_result:
        return False, "result_mismatch"
    if not current_best.get("ok") or not candidate_best.get("ok"):
        return False, "explain_failed"
    current_ms = float(current_best["elapsed_ms"])
    candidate_ms = float(candidate_best["elapsed_ms"])
    if candidate_ms < current_ms * 0.90:
        return True, ">=10pct_faster"
    if (
        candidate_ms < current_ms * 0.97
        and candidate_best.get("total_process_keys_sum", 0) < current_best.get("total_process_keys_sum", 0) * 0.90
    ):
        return True, "scan_reduced"
    return False, "not_enough_gain"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mixed-json", default="results/mixed_traffic_1780186589.json")
    parser.add_argument("--output", default="results/exhaustive_rewrite_optimizer.md")
    parser.add_argument("--summary-json", default="results/exhaustive_rewrite_optimizer.json")
    parser.add_argument("--bundle-id", action="append", default=[])
    parser.add_argument("--slow-only", action="store_true")
    parser.add_argument("--explain-timeout-ms", type=int, default=12000)
    parser.add_argument("--accept-threshold-ms", type=float, default=0.0)
    args = parser.parse_args()

    mixed_path = resolve_path(args.mixed_json)
    output_path = resolve_path(args.output)
    summary_path = resolve_path(args.summary_json)
    mixed = json.loads(mixed_path.read_text(encoding="utf-8"))
    catalog = build_bundle_catalog()
    bundle_ids = selected_bundle_ids(args, catalog, mixed)
    preagg_layout = mixed.get("preagg_layout", "prod180")

    cfg = get_db_config(save_msg="exhaustive rewrite optimizer")
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)

    summaries: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    lines: list[str] = [
        "# Exhaustive Bundle Rewrite Optimizer",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Mixed JSON: `{mixed_path}`",
        f"- Bundle count: `{len(bundle_ids)}`",
        "- Rule: candidates must return the same columns and normalized row values as the current optimized SQL.",
        "",
        "## Summary",
        "",
        "| Bundle | Group | Current Best | Best Candidate | Candidate Best | Gain | Accepted | Reason |",
        "| --- | --- | ---: | --- | ---: | ---: | --- | --- |",
    ]

    try:
        with conn.cursor() as cur:
            for index, bundle_id in enumerate(bundle_ids, start=1):
                bundle, group = catalog[bundle_id]
                event, record = choose_event_for_bundle(mixed, bundle_id)
                reference_time = datetime.fromisoformat(event["reference_time"])
                current_sql = render_bundle_sql(
                    bundle,
                    group,
                    reference_time,
                    hinted_a=set(),
                    preagg_bundles=PREAGG_BUNDLES,
                    preagg_layout=preagg_layout,
                )
                current_params = bundle_params(bundle, reference_time, event["bindings"], PREAGG_BUNDLES, preagg_layout)
                candidates = candidate_sqls(
                    bundle,
                    group,
                    reference_time,
                    event["bindings"],
                    current_params,
                    PREAGG_BUNDLES,
                    preagg_layout,
                )

                print(f"[{index}/{len(bundle_ids)}] {bundle_id} current + {len(candidates)} candidates", flush=True)
                current_rows = query_rows(cur, current_sql, current_params, args.explain_timeout_ms)
                current_results = []
                for setting_name, settings in SETTINGS:
                    result = explain_analyze(cur, current_sql, current_params, settings, args.explain_timeout_ms)
                    result.update({"setting": setting_name, "settings": settings})
                    current_results.append(result)
                ok_current = [item for item in current_results if item["ok"]]
                current_best = min(ok_current, key=lambda item: item["elapsed_ms"]) if ok_current else current_results[0]

                candidate_details: list[dict[str, Any]] = []
                best_candidate: dict[str, Any] | None = None
                for candidate in candidates:
                    print(f"[{index}/{len(bundle_ids)}] {bundle_id} candidate {candidate.name}", flush=True)
                    candidate_rows = query_rows(cur, candidate.sql, candidate.params, args.explain_timeout_ms)
                    same_result = (
                        current_rows.get("ok")
                        and candidate_rows.get("ok")
                        and current_rows.get("columns") == candidate_rows.get("columns")
                        and current_rows.get("rows") == candidate_rows.get("rows")
                    )
                    candidate_results = []
                    for setting_name, settings in SETTINGS:
                        result = explain_analyze(cur, candidate.sql, candidate.params, settings, args.explain_timeout_ms)
                        result.update({"setting": setting_name, "settings": settings})
                        candidate_results.append(result)
                    ok_results = [item for item in candidate_results if item["ok"]]
                    candidate_best = min(ok_results, key=lambda item: item["elapsed_ms"]) if ok_results else candidate_results[0]
                    accepted, reason = acceptance(current_best, candidate_best, bool(same_result))
                    item = {
                        "name": candidate.name,
                        "method": candidate.method,
                        "same_result": bool(same_result),
                        "select_ok": candidate_rows.get("ok"),
                        "select_ms": candidate_rows.get("elapsed_ms"),
                        "select_error": candidate_rows.get("error"),
                        "best": candidate_best,
                        "accepted": accepted,
                        "reason": reason,
                        "sql": candidate.sql,
                        "params": candidate.params,
                        "results": candidate_results,
                    }
                    candidate_details.append(item)
                    if accepted and (best_candidate is None or candidate_best["elapsed_ms"] < best_candidate["best"]["elapsed_ms"]):
                        best_candidate = item

                if best_candidate:
                    gain = (current_best["elapsed_ms"] - best_candidate["best"]["elapsed_ms"]) / current_best["elapsed_ms"] * 100.0
                    best_name = best_candidate["name"] + "/" + best_candidate["best"]["setting"]
                    best_ms = best_candidate["best"]["elapsed_ms"]
                    accepted_label = "yes"
                    reason = best_candidate["reason"]
                else:
                    ranked = [
                        item for item in candidate_details
                        if item["same_result"] and item["best"].get("ok")
                    ]
                    ranked.sort(key=lambda item: item["best"]["elapsed_ms"])
                    top = ranked[0] if ranked else None
                    gain = ((current_best["elapsed_ms"] - top["best"]["elapsed_ms"]) / current_best["elapsed_ms"] * 100.0) if top else 0.0
                    best_name = (top["name"] + "/" + top["best"]["setting"]) if top else "-"
                    best_ms = top["best"]["elapsed_ms"] if top else 0.0
                    accepted_label = "no"
                    reason = top["reason"] if top else "no_valid_candidate"

                rows = load_records(mixed, [bundle_id]).get(bundle_id, [])
                stats = summarize_bundle(rows) if rows else {}
                summary = {
                    "bundle_id": bundle_id,
                    "group": group,
                    "window_days": getattr(bundle, "window_days", None),
                    "filter": getattr(bundle, "base_filter", None),
                    "preagg": bundle_id in PREAGG_BUNDLES,
                    "chosen_event": event.get("invoice_number"),
                    "chosen_record": record,
                    "current_best_ms": current_best.get("elapsed_ms"),
                    "current_best_setting": current_best.get("setting"),
                    "current_best_scan_sum": current_best.get("total_process_keys_sum"),
                    "best_candidate": best_name,
                    "best_candidate_ms": best_ms,
                    "gain_pct": gain,
                    "accepted": accepted_label == "yes",
                    "reason": reason,
                    "stats": stats,
                }
                summaries.append(summary)
                details.append(
                    {
                        "summary": summary,
                        "current_sql": current_sql,
                        "current_params": current_params,
                        "current_rows": current_rows,
                        "current_results": current_results,
                        "current_best": current_best,
                        "candidates": candidate_details,
                    }
                )
                if args.accept_threshold_ms and summary["current_best_ms"] < args.accept_threshold_ms and not summary["accepted"]:
                    reason = "below_threshold"
                lines.append(
                    f"| `{bundle_id}` | {group} | {float(current_best.get('elapsed_ms', 0.0)):.1f} | `{best_name}` | {float(best_ms):.1f} | {gain:.1f}% | {accepted_label} | {reason} |"
                )
    finally:
        conn.close()

    accepted = [item for item in summaries if item["accepted"]]
    unresolved = [item for item in summaries if not item["accepted"] and float(item.get("current_best_ms") or 0) >= max(args.accept_threshold_ms, 350)]
    lines.extend(
        [
            "",
            f"- Accepted rewrites: `{len(accepted)}`",
            f"- Unresolved >= threshold: `{len(unresolved)}`",
            "",
            "## Accepted Rewrites",
            "",
        ]
    )
    if accepted:
        lines.append("| Bundle | Method | Current | New | Gain |")
        lines.append("| --- | --- | ---: | ---: | ---: |")
        for item in accepted:
            method = "-"
            for detail in details:
                if detail["summary"]["bundle_id"] != item["bundle_id"]:
                    continue
                for candidate in detail["candidates"]:
                    if item["best_candidate"].startswith(candidate["name"] + "/"):
                        method = candidate["method"]
                        break
            lines.append(
                f"| `{item['bundle_id']}` | {method} | {float(item['current_best_ms']):.1f} | {float(item['best_candidate_ms']):.1f} | {float(item['gain_pct']):.1f}% |"
            )
    else:
        lines.append("No candidate met the acceptance rule.")

    lines.extend(["", "## Per-Bundle Details", ""])
    for detail in details:
        summary = detail["summary"]
        lines.append(f"### {summary['bundle_id']}")
        lines.append("")
        lines.append(
            f"- Group/filter/window: `{summary['group']}` / `{summary['filter']}` / `{summary['window_days']}d`"
        )
        lines.append(
            f"- Current best: `{float(summary['current_best_ms'] or 0):.1f}ms` setting=`{summary['current_best_setting']}` scan_sum=`{summary['current_best_scan_sum']}`"
        )
        lines.append(
            f"- Best candidate: `{summary['best_candidate']}` `{float(summary['best_candidate_ms'] or 0):.1f}ms`, accepted=`{summary['accepted']}`, reason=`{summary['reason']}`"
        )
        lines.append("")
        lines.append("| Candidate | Same Result | Best Setting | Best Time | Scan Sum | Accepted | Reason |")
        lines.append("| --- | --- | --- | ---: | ---: | --- | --- |")
        for candidate in detail["candidates"]:
            best = candidate["best"]
            lines.append(
                f"| `{candidate['name']}` | {candidate['same_result']} | `{best.get('setting', '-')}` | {float(best.get('elapsed_ms', 0.0)):.1f} | {int(best.get('total_process_keys_sum', 0))} | {candidate['accepted']} | {candidate['reason']} |"
            )
        lines.append("")
        if summary["accepted"]:
            lines.append("#### Accepted SQL")
            lines.append("")
            accepted_detail = next(
                candidate for candidate in detail["candidates"]
                if summary["best_candidate"].startswith(candidate["name"] + "/")
            )
            lines.append("```sql")
            lines.append(accepted_detail["sql"])
            lines.append("```")
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    summary_path.write_text(json.dumps({"summaries": summaries, "details": details}, indent=2, default=str), encoding="utf-8")
    print(output_path)
    print(summary_path)


if __name__ == "__main__":
    main()
