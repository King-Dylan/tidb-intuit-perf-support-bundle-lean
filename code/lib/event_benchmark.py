#!/usr/bin/env python3
"""
Event-level benchmark harness for the Intuit risk demo.

This script runs the naive baseline:
  - choose one representative event from the loaded synthetic dataset
  - bind that event's entities into all Group A / B / C query templates
  - execute the full fan-out in parallel
  - measure end-to-end event latency
  - optionally write the full result bundle to JSON for later comparison

The intent is to establish a correctness ground truth before we build a
bundled/fat-query TiDB-native version.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import statistics
import threading
import time
from decimal import Decimal
from typing import Any

try:
    import pymysql
except ImportError:  # pragma: no cover - environment-specific dependency
    pymysql = None

try:
    from .db_config import get_db_config
    from .query_templates import QueryTemplate, load_query_templates
except ImportError:
    from db_config import get_db_config
    from query_templates import QueryTemplate, load_query_templates


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "benchmark_results"
HENRY_GROUP_C_JOIN = "SUBSTRING_INDEX(p.risk_profile_token, ':', -1) = d.interaction_id"
WINDOW_EXPR_RE = re.compile(
    r"unix_timestamp\(current_timestamp\s*-\s*interval\s+(\d+)\s+day\)\s*\*\s*1000",
    re.IGNORECASE,
)
DATETIME_WINDOW_EXPR_RE = re.compile(
    r"NOW\(\)\s*-\s*INTERVAL\s+(\d+)\s+DAY",
    re.IGNORECASE,
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    idx = (len(ordered) - 1) * pct
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


@dataclass(frozen=True)
class SampleEvent:
    invoice_number: str
    bindings: dict[str, Any]
    reference_time: datetime


class ConnectionPool:
    """Simple thread-local connection manager for pymysql."""

    def __init__(self, db_config: dict[str, Any]):
        self._db_config = dict(db_config)
        self._local = threading.local()
        self._connections: list[Any] = []
        self._lock = threading.Lock()

    def connection(self) -> Any:
        if pymysql is None:
            raise RuntimeError(
                "pymysql is not installed in this environment. Install it where you "
                "plan to run the benchmark, or run the harness on the EC2/TiDB host."
            )
        conn = getattr(self._local, "conn", None)
        if conn is None or not conn.open:
            conn = pymysql.connect(**self._db_config)
            self._local.conn = conn
            with self._lock:
                self._connections.append(conn)
        return conn

    def close(self) -> None:
        with self._lock:
            conns = list(self._connections)
            self._connections.clear()
        for conn in conns:
            try:
                conn.close()
            except Exception:
                pass


class EventBenchmark:
    def __init__(self, db_config: dict[str, Any], max_workers: int):
        self.db_config = dict(db_config)
        self.max_workers = max_workers
        self.pool = ConnectionPool(self.db_config)

    def close(self) -> None:
        self.pool.close()

    def sample_event(
        self,
        required_fields: set[str],
        *,
        invoice_number: str | None = None,
    ) -> SampleEvent:
        conn = self.pool.connection()
        with conn.cursor() as cursor:
            if invoice_number:
                sql = f"""
                    SELECT
                        p.invoice_number,
                        p.merchant_account_number,
                        p.card_holder_number_sha512,
                        p.check_bank_routing_number,
                        p.check_bank_account_number_sha512,
                        d.smart_id,
                        d.input_ip,
                        d.true_ip,
                        d.exact_id,
                        p.event_date
                    FROM pmt_txn_fact p
                    JOIN deviceprofile_fact d
                      ON {HENRY_GROUP_C_JOIN}
                    WHERE p.invoice_number = %s
                      AND p.risk_profile_token IS NOT NULL
                      AND p.merchant_account_number IS NOT NULL
                      AND p.card_holder_number_sha512 IS NOT NULL
                      AND p.check_bank_routing_number IS NOT NULL
                      AND p.check_bank_account_number_sha512 IS NOT NULL
                      AND d.smart_id IS NOT NULL
                      AND d.input_ip IS NOT NULL
                      AND d.true_ip IS NOT NULL
                      AND d.exact_id IS NOT NULL
                    LIMIT 1
                """
                cursor.execute(sql, (invoice_number,))
            else:
                # Pick a "rich" representative event so all bound query families
                # have meaningful entity values instead of defaulting to NULL.
                sql = f"""
                    SELECT
                        p.invoice_number,
                        p.merchant_account_number,
                        p.card_holder_number_sha512,
                        p.check_bank_routing_number,
                        p.check_bank_account_number_sha512,
                        d.smart_id,
                        d.input_ip,
                        d.true_ip,
                        d.exact_id,
                        p.event_date
                    FROM pmt_txn_fact p
                    JOIN deviceprofile_fact d
                      ON {HENRY_GROUP_C_JOIN}
                    WHERE p.risk_profile_token IS NOT NULL
                      AND p.invoice_number NOT LIKE 'RESEED_GC_%'
                      AND p.merchant_account_number IS NOT NULL
                      AND p.card_holder_number_sha512 IS NOT NULL
                      AND p.check_bank_routing_number IS NOT NULL
                      AND p.check_bank_account_number_sha512 IS NOT NULL
                      AND d.smart_id IS NOT NULL
                      AND d.input_ip IS NOT NULL
                      AND d.true_ip IS NOT NULL
                      AND d.exact_id IS NOT NULL
                    LIMIT 1
                """
                cursor.execute(sql)

            row = cursor.fetchone()

        if not row:
            raise RuntimeError(
                "Could not find a representative event in the loaded data. "
                "Load the dataset first, or pass --invoice-number for a known event."
            )

        bindings = {
            "merchant_account_number": row[1],
            "card_holder_number_sha512": row[2],
            "check_bank_routing_number": row[3],
            "check_bank_account_number_sha512": row[4],
            "smart_id": row[5],
            "input_ip": row[6],
            "true_ip": row[7],
            "exact_id": row[8],
        }
        missing = sorted(name for name in required_fields if bindings.get(name) in (None, ""))
        if missing:
            raise RuntimeError(
                f"Selected event {row[0]!r} is missing required bindings: {', '.join(missing)}"
            )
        reference_time = datetime.fromtimestamp(int(row[9]) / 1000.0)
        return SampleEvent(invoice_number=row[0], bindings=bindings, reference_time=reference_time)

    def run_template(
        self,
        template: QueryTemplate,
        bindings: dict[str, Any],
        reference_time: datetime,
    ) -> dict[str, Any]:
        sql, params = template.render(bindings)
        sql = WINDOW_EXPR_RE.sub(
            lambda match: str(
                int(reference_time.timestamp() * 1000) - (int(match.group(1)) * 86400 * 1000)
            ),
            sql,
        )
        sql = DATETIME_WINDOW_EXPR_RE.sub(
            lambda match: "'"
            + (reference_time - timedelta(days=int(match.group(1)))).strftime("%Y-%m-%d %H:%M:%S.%f")
            + "'",
            sql,
        )
        conn = self.pool.connection()
        started = time.perf_counter()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "template_id": template.template_id,
            "group": template.group,
            "param_names": list(template.param_names),
            "sql": sql,
            "params": [_json_safe(v) for v in params],
            "elapsed_ms": elapsed_ms,
            "row_count": len(rows),
            "columns": columns,
            "rows": [[_json_safe(v) for v in row] for row in rows],
        }

    def run_event(
        self,
        templates: list[QueryTemplate],
        event: SampleEvent,
    ) -> dict[str, Any]:
        reference_time = event.reference_time
        started = time.perf_counter()
        results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {
                executor.submit(self.run_template, template, event.bindings, reference_time): template
                for template in templates
            }
            for future in as_completed(future_map):
                template = future_map[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    errors.append(
                        {
                            "template_id": template.template_id,
                            "group": template.group,
                            "param_names": list(template.param_names),
                            "error": str(exc),
                        }
                    )

        event_elapsed_ms = (time.perf_counter() - started) * 1000.0
        results.sort(key=lambda item: item["template_id"])
        errors.sort(key=lambda item: item["template_id"])

        by_group = {
            group: len([r for r in results if r["group"] == group])
            for group in ("A", "B", "C")
        }
        per_query = [r["elapsed_ms"] for r in results]

        return {
            "event": {
                "invoice_number": event.invoice_number,
                "bindings": {k: _json_safe(v) for k, v in event.bindings.items()},
                "reference_time": event.reference_time.isoformat(),
            },
            "summary": {
                "template_count": len(templates),
                "completed": len(results),
                "errors": len(errors),
                "by_group_completed": by_group,
                "event_elapsed_ms": event_elapsed_ms,
                "per_query_ms": {
                    "min": min(per_query) if per_query else 0.0,
                    "p50": _percentile(per_query, 0.50),
                    "p95": _percentile(per_query, 0.95),
                    "p99": _percentile(per_query, 0.99),
                    "max": max(per_query) if per_query else 0.0,
                    "mean": statistics.fmean(per_query) if per_query else 0.0,
                },
            },
            "results": results,
            "errors": errors,
            "run_at": reference_time.isoformat(),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the naive event-level benchmark across all A/B/C templates."
    )
    parser.add_argument(
        "--pdf-path",
        default=None,
        help="Optional alternate PDF path for template extraction.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=128,
        help="Max parallel query workers for the naive fan-out baseline.",
    )
    parser.add_argument(
        "--invoice-number",
        default=None,
        help="Use a specific invoice_number instead of sampling a representative event.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path. Defaults to benchmark_results/naive_baseline_<ts>.json",
    )
    parser.add_argument(
        "--groups",
        nargs="+",
        choices=["A", "B", "C"],
        default=["A", "B", "C"],
        help="Subset of template groups to run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if pymysql is None:
        raise SystemExit(
            "pymysql is not installed in this environment. Install it first or run "
            "event_benchmark.py in the same environment as the TiDB demo scripts."
        )
    db_config = get_db_config(save_msg="benchmark runs")
    pdf_path = Path(args.pdf_path) if args.pdf_path else None

    print("\n" + "=" * 60)
    print(" INTUIT RISK POC — Event Benchmark (Naive Baseline)")
    print("=" * 60)
    print(" Loading templates...")
    templates = load_query_templates(pdf_path) if pdf_path else load_query_templates()
    templates = [tmpl for tmpl in templates if tmpl.group in set(args.groups)]
    required_fields = {name for tmpl in templates for name in tmpl.param_names}
    print(
        f"  Loaded {len(templates)} templates "
        f"({', '.join(f'{g}={sum(1 for t in templates if t.group == g)}' for g in ('A', 'B', 'C') if g in args.groups)})"
    )
    print(f"  Required event bindings: {', '.join(sorted(required_fields))}")
    print(f"  Max workers: {args.max_workers}")

    benchmark = EventBenchmark(db_config, max_workers=args.max_workers)
    try:
        event = benchmark.sample_event(required_fields, invoice_number=args.invoice_number)
        print(f"\n Selected event: {event.invoice_number}")
        for key in sorted(event.bindings):
            print(f"   {key}: {event.bindings[key]}")

        print("\n Running naive full fan-out...")
        payload = benchmark.run_event(templates, event)
    finally:
        benchmark.close()

    summary = payload["summary"]
    print("\n Results")
    print(f"  Completed: {summary['completed']}/{summary['template_count']}")
    print(f"  Errors:    {summary['errors']}")
    print(f"  Event ms:  {summary['event_elapsed_ms']:.2f}")
    print("  Per-query ms:")
    print(f"    p50:  {summary['per_query_ms']['p50']:.2f}")
    print(f"    p95:  {summary['per_query_ms']['p95']:.2f}")
    print(f"    p99:  {summary['per_query_ms']['p99']:.2f}")
    print(f"    max:  {summary['per_query_ms']['max']:.2f}")

    output_path = Path(args.output) if args.output else (
        DEFAULT_OUTPUT_DIR / f"naive_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\n  Saved baseline results to {output_path}")

    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
