#!/usr/bin/env python3
"""Generate a per-event detail report from a mixed traffic benchmark JSON.

The mixed traffic benchmark stores sampled event bindings separately from the
per-event timing rows. This script joins those two sections back together and
emits a CSV that answers the common review questions:

* which event ID ran;
* which eight binding values were used;
* which key, if any, was intentionally top-hot;
* how many of the 65 bundles returned by 350ms / 500ms;
* how many runtime vs pre-agg bundles returned by those cutoffs;
* which bundles were slowest for that event.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

PAYMENT_FIELDS = [
    "merchant_account_number",
    "card_holder_number_sha512",
    "check_bank_routing_number",
    "check_bank_account_number_sha512",
]

DEVICE_FIELDS = [
    "exact_id",
    "smart_id",
    "input_ip",
    "true_ip",
]

ALL_FIELDS = PAYMENT_FIELDS + DEVICE_FIELDS
HISTOGRAM_CUTOFFS_MS = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
DROPOFF_WINDOWS_MS = [
    ("0-50ms", 0, 50),
    ("50-100ms", 50, 100),
    ("100-150ms", 100, 150),
    ("150-200ms", 150, 200),
    ("200-350ms", 200, 350),
    ("350-500ms", 350, 500),
]

FIELD_SOURCES = {
    "merchant_account_number": ("pmt_txn_fact", "merchant_account_number"),
    "card_holder_number_sha512": ("pmt_txn_fact", "card_holder_number_sha512"),
    "check_bank_routing_number": ("pmt_txn_fact", "check_bank_routing_number"),
    "check_bank_account_number_sha512": ("pmt_txn_fact", "check_bank_account_number_sha512"),
    "exact_id": ("deviceprofile_fact", "exact_id"),
    "smart_id": ("deviceprofile_fact", "smart_id"),
    "input_ip": ("deviceprofile_fact", "input_ip"),
    "true_ip": ("deviceprofile_fact", "true_ip"),
}


def resolve_path(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def pct(vals: list[float], p: float) -> float:
    if not vals:
        return 0.0
    vals = sorted(vals)
    k = (len(vals) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    return vals[f] * (c - k) + vals[c] * (k - f)


def summarize(vals: list[float]) -> dict[str, float]:
    return {
        "p50": pct(vals, 50),
        "p95": pct(vals, 95),
        "p99": pct(vals, 99),
        "max": max(vals) if vals else 0.0,
    }


def fmt_pct(numerator: int, denominator: int) -> str:
    return f"{(numerator / denominator * 100):.1f}%" if denominator else "0.0%"


def sampled_event_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    events: dict[str, dict[str, Any]] = {}
    for key in ("sampled_normal_events", "sampled_hot_events"):
        for event in data.get(key, []):
            events[event["invoice_number"]] = event
    return events


def bundle_stats(bundles: list[dict[str, Any]], preagg: bool | None = None) -> dict[str, int]:
    selected = [b for b in bundles if preagg is None or bool(b.get("preagg_applied")) == preagg]
    return {
        "total": len(selected),
        "by350": sum(1 for b in selected if 0 <= float(b["ms"]) <= 350),
        "by500": sum(1 for b in selected if 0 <= float(b["ms"]) <= 500),
        "over350": sum(1 for b in selected if float(b["ms"]) > 350),
        "over500": sum(1 for b in selected if float(b["ms"]) > 500),
        "errors": sum(1 for b in selected if float(b["ms"]) < 0),
    }


def bundle_count_by_cutoff(bundles: list[dict[str, Any]], cutoff_ms: int) -> int:
    return sum(1 for b in bundles if 0 <= float(b["ms"]) <= cutoff_ms)


def bundle_return_histogram(rows: list[dict[str, Any]]) -> list[list[Any]]:
    output: list[list[Any]] = []
    for cutoff in HISTOGRAM_CUTOFFS_MS:
        counts = [int(r[f"bundles_by{cutoff}"]) for r in rows]
        output.append(
            [
                f"<={cutoff}ms",
                f"{(sum(counts) / len(counts)):.1f}/65" if counts else "0.0/65",
                f"{pct(counts, 50):.0f}" if counts else "0",
                f"{sum(c >= 60 for c in counts)}/{len(rows)}",
                f"{sum(c >= 65 for c in counts)}/{len(rows)}",
            ]
        )
    over500_or_error = sum(int(r["bundles_over500"]) + int(r["bundle_errors"]) for r in rows)
    output.append([">500ms or error", "", "", "", over500_or_error])
    return output


def bundle_return_dropoff(rows: list[dict[str, Any]]) -> list[list[Any]]:
    output: list[list[Any]] = []
    event_count = len(rows)
    for label, start_ms, end_ms in DROPOFF_WINDOWS_MS:
        if start_ms == 0:
            total = sum(int(r[f"bundles_by{end_ms}"]) for r in rows)
        else:
            total = sum(int(r[f"bundles_by{end_ms}"]) - int(r[f"bundles_by{start_ms}"]) for r in rows)
        output.append([label, f"{(total / event_count):.1f}" if event_count else "0.0", f"{total:,}"])
    over500_or_error = sum(int(r["bundles_over500"]) + int(r["bundle_errors"]) for r in rows)
    output.append([">500/error", f"{(over500_or_error / event_count):.2f}" if event_count else "0.00", f"{over500_or_error:,}"])
    return output


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return lines


def text_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    string_rows = [[str(x) for x in row] for row in rows]
    widths = [
        max([len(str(header))] + [len(row[i]) for row in string_rows])
        for i, header in enumerate(headers)
    ]
    lines = ["```text", "  ".join(str(header).ljust(widths[i]) for i, header in enumerate(headers))]
    for row in string_rows:
        lines.append("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))
    lines.append("```")
    return lines


def slowest_bundle_text(bundles: list[dict[str, Any]], limit: int) -> str:
    slowest = sorted(
        [b for b in bundles if float(b.get("ms", -1)) >= 0],
        key=lambda b: float(b["ms"]),
        reverse=True,
    )[:limit]
    parts = []
    for b in slowest:
        mode = "preagg" if b.get("preagg_applied") else "runtime"
        parts.append(
            f"{b.get('bundle_id')}:{float(b.get('ms', 0)):.1f}ms:{mode}:"
            f"{b.get('window_days')}d:{b.get('base_filter')}"
        )
    return " | ".join(parts)


def hot_matches(bindings: dict[str, Any], hot_fields: dict[str, Any]) -> list[str]:
    matches = []
    for field in ALL_FIELDS:
        info = hot_fields.get(field) or {}
        if info and str(bindings.get(field)) == str(info.get("value")):
            matches.append(field)
    return matches


def fetch_actual_key_counts(data: dict[str, Any]) -> dict[tuple[str, str], int]:
    import pymysql

    from lib.db_config import get_db_config

    event_index = sampled_event_index(data)
    values_by_field: dict[str, set[str]] = {field: set() for field in ALL_FIELDS}
    for event in event_index.values():
        bindings = event.get("bindings", {})
        for field in ALL_FIELDS:
            value = bindings.get(field)
            if value not in (None, ""):
                values_by_field[field].add(str(value))

    cfg = get_db_config("event detail key-count lookup")
    counts: dict[tuple[str, str], int] = {}
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)
    try:
        with conn.cursor() as cur:
            for field, values in values_by_field.items():
                table, column = FIELD_SOURCES[field]
                for value in values:
                    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = %s", (value,))
                    counts[(field, value)] = int(cur.fetchone()[0])
    finally:
        conn.close()
    return counts


def build_rows(data: dict[str, Any], slowest_limit: int, actual_counts: dict[tuple[str, str], int] | None = None) -> list[dict[str, Any]]:
    event_index = sampled_event_index(data)
    hot_fields = data.get("profile", {}).get("hot_fields", {})
    rows = []
    for result in data["read_results"]:
        event_id = result["event"]
        sampled = event_index.get(event_id, {})
        bindings = sampled.get("bindings", {})
        bundles = result.get("bundle_results", [])
        all_stats = bundle_stats(bundles)
        runtime_stats = bundle_stats(bundles, preagg=False)
        preagg_stats = bundle_stats(bundles, preagg=True)
        explicit_hot_field = result.get("hot_field") or sampled.get("hot_field") or ""
        explicit_hot_count = result.get("hot_count") or sampled.get("hot_count") or ""
        matches = hot_matches(bindings, hot_fields)
        row = {
            "event": event_id,
            "kind": result.get("kind"),
            "event_ms": round(float(result["ms"]), 3),
            "explicit_hot_field": explicit_hot_field,
            "explicit_hot_count": explicit_hot_count,
            "top_hot_binding_matches": ",".join(matches),
            "top_hot_binding_match_count": len(matches),
            "device_top_hot_binding_matches": ",".join([m for m in matches if m in DEVICE_FIELDS]),
            "device_top_hot_binding_match_count": len([m for m in matches if m in DEVICE_FIELDS]),
            "payment_top_hot_binding_matches": ",".join([m for m in matches if m in PAYMENT_FIELDS]),
            "payment_top_hot_binding_match_count": len([m for m in matches if m in PAYMENT_FIELDS]),
            "total_bundles": all_stats["total"],
            "bundles_by350": all_stats["by350"],
            "bundles_by500": all_stats["by500"],
            "bundles_over350": all_stats["over350"],
            "bundles_over500": all_stats["over500"],
            "bundle_errors": all_stats["errors"],
            "passes_60_by350": all_stats["by350"] >= 60,
            "passes_60_by500": all_stats["by500"] >= 60,
            "runtime_total": runtime_stats["total"],
            "runtime_by350": runtime_stats["by350"],
            "runtime_by500": runtime_stats["by500"],
            "runtime_over350": runtime_stats["over350"],
            "runtime_over500": runtime_stats["over500"],
            "runtime_errors": runtime_stats["errors"],
            "preagg_total": preagg_stats["total"],
            "preagg_by350": preagg_stats["by350"],
            "preagg_by500": preagg_stats["by500"],
            "preagg_over350": preagg_stats["over350"],
            "preagg_over500": preagg_stats["over500"],
            "preagg_errors": preagg_stats["errors"],
            "slowest_bundles": slowest_bundle_text(bundles, slowest_limit),
        }
        for cutoff in HISTOGRAM_CUTOFFS_MS:
            row[f"bundles_by{cutoff}"] = bundle_count_by_cutoff(bundles, cutoff)
        for field in ALL_FIELDS:
            row[field] = bindings.get(field, "")
            info = hot_fields.get(field) or {}
            row[f"{field}_is_profile_top_hot"] = str(bindings.get(field)) == str(info.get("value"))
            row[f"{field}_profile_top_rows"] = info.get("count", "")
            if actual_counts is not None:
                value = bindings.get(field)
                row[f"{field}_actual_rows"] = "" if value in (None, "") else actual_counts.get((field, str(value)), "")
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, data: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    vals = [float(r["event_ms"]) for r in rows]
    stats = summarize(vals)
    kind_counts = Counter(r["kind"] for r in rows)
    explicit_hot = Counter(r["explicit_hot_field"] for r in rows if r["explicit_hot_field"])
    top_hot_match_counts = Counter(int(r["top_hot_binding_match_count"]) for r in rows)
    device_top_hot_match_counts = Counter(int(r["device_top_hot_binding_match_count"]) for r in rows)
    full_binding_sets = {tuple(str(r.get(field, "")) for field in ALL_FIELDS) for r in rows}
    events_60_by350 = sum(r["passes_60_by350"] for r in rows)
    events_60_by500 = sum(r["passes_60_by500"] for r in rows)
    events_65_by350 = sum(int(r["bundles_by350"]) >= 65 for r in rows)
    events_65_by500 = sum(int(r["bundles_by500"]) >= 65 for r in rows)
    avg_by350 = sum(int(r["bundles_by350"]) for r in rows) / len(rows) if rows else 0.0
    avg_by500 = sum(int(r["bundles_by500"]) for r in rows) / len(rows) if rows else 0.0
    binding_reuse = []
    for field in ALL_FIELDS:
        counts = Counter(str(r.get(field, "")) for r in rows)
        binding_reuse.append([field, len(counts), max(counts.values()) if counts else 0])
    lines = [
        "# Per-Event Detail Report",
        "",
        "## Summary",
        "",
        f"- Events: {len(rows)}",
        f"- Unique event IDs: {len(set(r['event'] for r in rows))}",
        f"- Event latency: p50 {stats['p50']:.1f} ms, p95 {stats['p95']:.1f} ms, p99 {stats['p99']:.1f} ms, max {stats['max']:.1f} ms",
        "",
        "Henry's 60/65 rule: can the event proceed?",
        "",
        f"- By 350ms: {events_60_by350}/{len(rows)} events passed ({fmt_pct(events_60_by350, len(rows))})",
        f"- By 500ms: {events_60_by500}/{len(rows)} events passed ({fmt_pct(events_60_by500, len(rows))})",
        "",
        "Andrew's 65/65 view: did we get every feature?",
        "",
        f"- By 350ms: {events_65_by350}/{len(rows)} events were complete ({fmt_pct(events_65_by350, len(rows))})",
        f"- By 500ms: {events_65_by500}/{len(rows)} events were complete ({fmt_pct(events_65_by500, len(rows))})",
        "",
        "Average bundle coverage across all events:",
        "",
        f"- By 350ms: {avg_by350:.1f}/65 bundles back on average",
        f"- By 500ms: {avg_by500:.1f}/65 bundles back on average",
        "",
        "## Binding Reuse / Test Realism",
        "",
        f"This run used {len(set(r['event'] for r in rows))} unique event IDs, and the full 8-ID binding set was unique for {len(full_binding_sets)}/{len(rows)} events.",
        "",
    ]
    lines.extend(markdown_table(["Field", f"Distinct values / {len(rows)} events", "Max repeat"], binding_reuse))
    lines.extend([
        "",
        "## Bundle Return-Time Drop-Off",
        "",
        "This shows how many additional bundle results land in each time window.",
        "",
    ])
    lines.extend(text_table(["Window", "Avg bundles/event", "Total bundle executions"], bundle_return_dropoff(rows)))
    lines.extend([
        "",
        "## Bundle Return-Time CDF",
        "",
        "This shows how quickly bundle results become available across events.",
        "",
    ])
    lines.extend(text_table(["Cutoff", "Avg bundles returned", "Median returned", "Events >=60/65", "Events 65/65"], bundle_return_histogram(rows)))
    lines.extend([
        "",
        "## Event Mix",
        "",
    ])
    for kind, count in sorted(kind_counts.items()):
        lines.append(f"- {kind}: {count}")
    lines.extend(["", "## Explicit Top-Hot Event Tags", ""])
    if explicit_hot:
        for field, count in sorted(explicit_hot.items()):
            lines.append(f"- {field}: {count}")
    else:
        lines.append("- none")
    lines.extend(["", "## Top-Hot Binding Matches Per Event", ""])
    lines.append("This checks whether an event binding exactly equals the profile's #1 hot value for that field.")
    lines.append("")
    lines.append("All 8 fields:")
    for count, events in sorted(top_hot_match_counts.items()):
        lines.append(f"- {count} top-hot field matches: {events} events")
    lines.append("")
    lines.append("Device fields only:")
    for count, events in sorted(device_top_hot_match_counts.items()):
        lines.append(f"- {count} top-hot device-field matches: {events} events")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mixed-json", required=True)
    parser.add_argument("--csv-output")
    parser.add_argument("--md-output")
    parser.add_argument("--slowest-limit", type=int, default=5)
    parser.add_argument("--include-db-counts", action="store_true", help="Query TiDB for actual row counts for every event binding value.")
    args = parser.parse_args()

    mixed_path = resolve_path(args.mixed_json)
    data = json.loads(mixed_path.read_text())
    actual_counts = fetch_actual_key_counts(data) if args.include_db_counts else None
    rows = build_rows(data, slowest_limit=args.slowest_limit, actual_counts=actual_counts)
    csv_output = resolve_path(args.csv_output) if args.csv_output else ROOT / "results" / f"event_detail_{mixed_path.stem}.csv"
    md_output = resolve_path(args.md_output) if args.md_output else ROOT / "results" / f"event_detail_{mixed_path.stem}.md"
    write_csv(csv_output, rows)
    write_markdown(md_output, data, rows)
    print(csv_output)
    print(md_output)


if __name__ == "__main__":
    main()
