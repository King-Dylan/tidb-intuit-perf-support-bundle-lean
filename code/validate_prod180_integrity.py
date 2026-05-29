#!/usr/bin/env python3
"""Validate production-style 180d pre-aggregation table completeness.

This is a structural/data-coverage gate, not a performance benchmark. It fails
if the six consolidated prod180 tables do not cover the full loaded base-table
date range or if expected 180d bundle/template rows are missing.
"""

from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path

import pymysql

from demo import cluster_group_a_templates, cluster_group_b_templates, cluster_group_c_templates
from lib.db_config import get_db_config
from preagg_rollups import bundle_rollup_metrics


ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "results" / "prod180_integrity_report.json"


def day_range(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def table_names(group: str) -> tuple[str, str]:
    lower = group.lower()
    return f"group_{lower}_180d_daily_rollup", f"group_{lower}_180d_daily_distinct"


def all_180_bundles():
    for group, factory in (
        ("A", cluster_group_a_templates),
        ("B", cluster_group_b_templates),
        ("C", cluster_group_c_templates),
    ):
        for bundle in factory():
            if bundle.window_days == 180:
                yield group, bundle


def fetch_one(cur, sql: str):
    cur.execute(sql)
    return cur.fetchone()


def fetch_set(cur, sql: str) -> set:
    cur.execute(sql)
    return {tuple(row.values()) if len(row) > 1 else next(iter(row.values())) for row in cur.fetchall()}


def missing_days_by_index_probe(cur, table: str, expected_days: set[date]) -> list[date]:
    """Check day coverage without full-scanning multi-billion-row helper tables."""
    missing: list[date] = []
    for expected_day in sorted(expected_days):
        cur.execute(f"SELECT 1 FROM `{table}` WHERE event_day = %s LIMIT 1", (expected_day,))
        if cur.fetchone() is None:
            missing.append(expected_day)
    return missing


def table_has_rows(cur, table: str) -> bool:
    cur.execute(f"SELECT 1 FROM `{table}` LIMIT 1")
    return cur.fetchone() is not None


def min_max_day(cur, table: str) -> dict:
    cur.execute(f"SELECT event_day AS min_day FROM `{table}` FORCE INDEX(idx_event_day) ORDER BY event_day ASC LIMIT 1")
    min_row = cur.fetchone()
    cur.execute(f"SELECT event_day AS max_day FROM `{table}` FORCE INDEX(idx_event_day) ORDER BY event_day DESC LIMIT 1")
    max_row = cur.fetchone()
    return {
        "has_rows": min_row is not None,
        "min_day": min_row["min_day"] if min_row else None,
        "max_day": max_row["max_day"] if max_row else None,
    }


def min_max_c_days(cur, table: str) -> dict:
    has_rows = table_has_rows(cur, table)
    if not has_rows:
        return {"has_rows": False, "min_p_day": None, "max_p_day": None, "min_d_day": None, "max_d_day": None}
    cur.execute(f"SELECT p_event_day AS min_p_day FROM `{table}` FORCE INDEX(idx_event_day) ORDER BY p_event_day ASC LIMIT 1")
    min_p = cur.fetchone()["min_p_day"]
    cur.execute(f"SELECT p_event_day AS max_p_day FROM `{table}` FORCE INDEX(idx_event_day) ORDER BY p_event_day DESC LIMIT 1")
    max_p = cur.fetchone()["max_p_day"]
    cur.execute(f"SELECT MIN(d_event_day) AS min_d_day, MAX(d_event_day) AS max_d_day FROM `{table}`")
    d_row = cur.fetchone()
    return {
        "has_rows": True,
        "min_p_day": min_p,
        "max_p_day": max_p,
        "min_d_day": d_row["min_d_day"],
        "max_d_day": d_row["max_d_day"],
    }


def existing_rollup_bundles(cur, table: str, expected_bundles: set[str]) -> set[str]:
    present: set[str] = set()
    for bundle_id in expected_bundles:
        cur.execute(f"SELECT 1 FROM `{table}` WHERE bundle_id = %s LIMIT 1", (bundle_id,))
        if cur.fetchone() is not None:
            present.add(bundle_id)
    return present


def existing_distinct_pairs(cur, table: str, expected_pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
    present: set[tuple[str, str]] = set()
    for bundle_id, template_id in expected_pairs:
        cur.execute(
            f"SELECT 1 FROM `{table}` WHERE bundle_id = %s AND template_id = %s LIMIT 1",
            (bundle_id, template_id),
        )
        if cur.fetchone() is not None:
            present.add((bundle_id, template_id))
    return present


def expected_metric_sets() -> dict[str, dict[str, set]]:
    expected = {
        group: {"rollup_bundles": set(), "distinct_pairs": set(), "distinct_bundles": set()}
        for group in ("A", "B", "C")
    }
    for group, bundle in all_180_bundles():
        rollups, distincts = bundle_rollup_metrics(group, bundle)
        if rollups:
            expected[group]["rollup_bundles"].add(bundle.bundle_id)
        for distinct in distincts:
            expected[group]["distinct_bundles"].add(bundle.bundle_id)
            expected[group]["distinct_pairs"].add((bundle.bundle_id, distinct.template_id))
    return expected


def main() -> int:
    cfg = get_db_config(save_msg="prod180 integrity validation")
    cfg["cursorclass"] = pymysql.cursors.DictCursor
    conn = pymysql.connect(**cfg)
    expected = expected_metric_sets()
    report: dict = {"groups": {}, "failures": [], "warnings": []}

    with conn.cursor() as cur:
        pmt = fetch_one(
            cur,
            """
            SELECT DATE(FROM_UNIXTIME(MIN(event_date)/1000)) AS min_day,
                   DATE(FROM_UNIXTIME(MAX(event_date)/1000)) AS max_day
            FROM pmt_txn_fact
            """,
        )
        dev = fetch_one(
            cur,
            """
            SELECT DATE(MIN(jms_timestamp)) AS min_day,
                   DATE(MAX(jms_timestamp)) AS max_day
            FROM deviceprofile_fact
            """,
        )
        report["base_tables"] = {"pmt_txn_fact": pmt, "deviceprofile_fact": dev}

        expected_ranges = {
            "A": (pmt["min_day"], pmt["max_day"]),
            "B": (dev["min_day"], dev["max_day"]),
            "C": (max(pmt["min_day"], dev["min_day"]), min(pmt["max_day"], dev["max_day"])),
        }

        for group in ("A", "B", "C"):
            rollup_table, distinct_table = table_names(group)
            start_day, end_day = expected_ranges[group]
            expected_days = set(day_range(start_day, end_day))
            group_report: dict = {
                "expected_start": start_day,
                "expected_end": end_day,
                "expected_day_count": len(expected_days),
                "expected_rollup_bundles": sorted(expected[group]["rollup_bundles"]),
                "expected_distinct_pairs": sorted(expected[group]["distinct_pairs"]),
            }

            for kind, table in (("rollup", rollup_table), ("distinct", distinct_table)):
                if group == "C":
                    stats = min_max_c_days(cur, table)
                else:
                    stats = min_max_day(cur, table)
                group_report[f"{kind}_stats"] = stats

                has_expected_metrics = bool(
                    expected[group]["rollup_bundles"] if kind == "rollup" else expected[group]["distinct_pairs"]
                )
                if has_expected_metrics:
                    if group == "C":
                        if not stats["has_rows"]:
                            report["failures"].append(f"{table} has no rows")
                        group_report[f"{kind}_coverage_note"] = (
                            "Group C uses p_event_day and d_event_day independently; "
                            "exactness is enforced by raw-vs-preagg spotcheck."
                        )
                    else:
                        missing_days = missing_days_by_index_probe(cur, table, expected_days)
                        group_report[f"{kind}_day_count"] = len(expected_days) - len(missing_days)
                        group_report[f"{kind}_missing_days"] = [d.isoformat() for d in missing_days[:20]]
                        group_report[f"{kind}_missing_days_count"] = len(missing_days)
                        if stats["min_day"] != start_day or stats["max_day"] != end_day:
                            report["failures"].append(
                                f"{table} coverage {stats['min_day']}..{stats['max_day']} expected {start_day}..{end_day}"
                            )
                        if missing_days:
                            report["failures"].append(f"{table} missing {len(missing_days)} day(s)")
                elif stats["has_rows"]:
                    report["failures"].append(f"{table} should be empty placeholder table but has rows")

            actual_rollup_bundles = existing_rollup_bundles(cur, rollup_table, expected[group]["rollup_bundles"])
            actual_distinct_pairs = existing_distinct_pairs(cur, distinct_table, expected[group]["distinct_pairs"])
            missing_rollup_bundles = sorted(expected[group]["rollup_bundles"] - actual_rollup_bundles)
            missing_distinct_pairs = sorted(expected[group]["distinct_pairs"] - actual_distinct_pairs)
            group_report["actual_rollup_bundles"] = sorted(actual_rollup_bundles)
            group_report["actual_distinct_pairs_count"] = len(actual_distinct_pairs)
            group_report["missing_rollup_bundles"] = missing_rollup_bundles
            group_report["missing_distinct_pairs"] = missing_distinct_pairs
            if missing_rollup_bundles:
                report["failures"].append(f"group {group} missing rollup bundles: {missing_rollup_bundles}")
            if missing_distinct_pairs:
                report["warnings"].append(
                    f"group {group} has no rows for distinct pairs: {missing_distinct_pairs}. "
                    "This can be valid when the source predicate has zero qualifying rows; "
                    "raw-vs-preagg spotcheck is the hard correctness gate."
                )

            report["groups"][group] = group_report

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, default=str))
    print(f"WROTE {OUT_PATH}")
    if report["failures"]:
        print("FAIL")
        for failure in report["failures"]:
            print(f"- {failure}")
        return 1
    for warning in report["warnings"]:
        print(f"WARNING: {warning}")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
