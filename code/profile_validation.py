#!/usr/bin/env python3
"""Validate the v12 synthetic data shape for the Intuit benchmark.

This script captures the facts Intuit keeps asking about:

* row counts;
* null / blank rates;
* distinct counts;
* top-10 hot values;
* Group C join path and fanout.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
import os

import pymysql

from lib.db_config import get_db_config


ROOT = Path(__file__).resolve().parent

PROFILE_COLUMNS = {
    "pmt_txn_fact": [
        "merchant_account_number",
        "card_holder_number_sha512",
        "check_bank_routing_number",
        "check_bank_account_number_sha512",
        "risk_profile_token",
        "parsed_interaction_id",
        "event_date",
    ],
    "deviceprofile_fact": [
        "interaction_id",
        "user_session_id",
        "exact_id",
        "smart_id",
        "input_ip",
        "true_ip",
        "jms_timestamp",
    ],
}


def qident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def run_one(cur, sql: str, params: tuple[Any, ...] = ()) -> tuple[Any, ...]:
    cur.execute(sql, params)
    return cur.fetchone()


def table_count(cur, table: str) -> int:
    return int(run_one(cur, f"SELECT COUNT(*) FROM {qident(table)}")[0])


def column_profile(cur, table: str, column: str) -> dict[str, Any]:
    total = table_count(cur, table)
    col = qident(column)
    null_or_blank = int(
        run_one(
            cur,
            f"SELECT COUNT(*) FROM {qident(table)} WHERE {col} IS NULL OR CAST({col} AS CHAR) = ''",
        )[0]
    )
    distinct = int(
        run_one(
            cur,
            f"SELECT COUNT(DISTINCT {col}) FROM {qident(table)} WHERE {col} IS NOT NULL AND CAST({col} AS CHAR) <> ''",
        )[0]
    )
    cur.execute(
        f"""
        SELECT CAST({col} AS CHAR) AS value, COUNT(*) AS row_count
        FROM {qident(table)}
        WHERE {col} IS NOT NULL AND CAST({col} AS CHAR) <> ''
        GROUP BY {col}
        ORDER BY row_count DESC
        LIMIT 10
        """
    )
    top10 = [(str(value), int(rows)) for value, rows in cur.fetchall()]
    return {
        "table": table,
        "column": column,
        "rows": total,
        "null_or_blank": null_or_blank,
        "null_or_blank_pct": (null_or_blank / total * 100.0) if total else 0.0,
        "distinct": distinct,
        "top10": top10,
    }


def group_c_fanout(cur) -> dict[str, Any]:
    joined = run_one(
        cur,
        """
        SELECT
          COUNT(*) AS joined_rows,
          COUNT(DISTINCT p.invoice_number) AS distinct_payment_rows,
          COUNT(DISTINCT p.parsed_interaction_id) AS distinct_payment_join_keys,
          COUNT(DISTINCT d.interaction_id) AS distinct_device_join_keys
        FROM pmt_txn_fact p
        JOIN deviceprofile_fact d
          ON p.parsed_interaction_id = d.interaction_id
        WHERE p.parsed_interaction_id IS NOT NULL
          AND d.interaction_id IS NOT NULL
        """,
    )
    cur.execute(
        """
        SELECT p.parsed_interaction_id, COUNT(*) AS fanout
        FROM pmt_txn_fact p
        JOIN deviceprofile_fact d
          ON p.parsed_interaction_id = d.interaction_id
        WHERE p.parsed_interaction_id IS NOT NULL
          AND d.interaction_id IS NOT NULL
        GROUP BY p.parsed_interaction_id
        ORDER BY fanout DESC
        LIMIT 20
        """
    )
    top_fanout = [(str(key), int(count)) for key, count in cur.fetchall()]
    return {
        "joined_rows": int(joined[0]),
        "distinct_payment_rows": int(joined[1]),
        "distinct_payment_join_keys": int(joined[2]),
        "distinct_device_join_keys": int(joined[3]),
        "top_fanout": top_fanout,
    }


def add_table(lines: list[str], headers: list[str], rows: list[list[Any]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")


def write_markdown(path: Path, profiles: list[dict[str, Any]], fanout: dict[str, Any]) -> None:
    lines: list[str] = [
        "# v12 Data Shape Validation",
        "",
        "## Join Assumptions",
        "",
        "- All A + B + C bundles fire for each event.",
        "- Group C join key is `p.parsed_interaction_id = d.interaction_id`.",
        "- `risk_profile_token` is modeled as `<sessionID>:<interactionID>` and `parsed_interaction_id` stores the parsed suffix.",
        "- `user_session_id` is expected to be null in the shared profile and is not the Group C join key.",
        "- `check_bank_account_number_sha512` is populated only for ACH/check rows with a routing number.",
        "",
        "## Column Profiles",
        "",
    ]
    profile_rows = [
        [
            p["table"],
            p["column"],
            f"{p['rows']:,}",
            f"{p['null_or_blank']:,}",
            f"{p['null_or_blank_pct']:.1f}%",
            f"{p['distinct']:,}",
        ]
        for p in profiles
    ]
    add_table(lines, ["Table", "Column", "Rows", "Null/blank", "Null/blank %", "Distinct"], profile_rows)
    lines.append("")
    lines.append("## Top-10 Frequencies")
    for p in profiles:
        lines.extend(["", f"### {p['table']}.{p['column']}", ""])
        add_table(lines, ["Value", "Rows"], [[value, f"{rows:,}"] for value, rows in p["top10"]])
    lines.extend(
        [
            "",
            "## Group C 1:1 Join Fanout",
            "",
            f"- Joined rows: {fanout['joined_rows']:,}",
            f"- Distinct payment rows joined: {fanout['distinct_payment_rows']:,}",
            f"- Distinct payment join keys: {fanout['distinct_payment_join_keys']:,}",
            f"- Distinct device join keys: {fanout['distinct_device_join_keys']:,}",
            "",
            "Top join-key fanout:",
            "",
        ]
    )
    add_table(lines, ["parsed_interaction_id", "Joined rows"], [[k, f"{v:,}"] for k, v in fanout["top_fanout"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/v12_data_shape_validation.md")
    args = parser.parse_args()

    conn = pymysql.connect(**get_db_config(save_msg="v12 profile validation"))
    conn.autocommit(True)
    try:
        with conn.cursor() as cur:
            read_engine = os.environ.get("INTUIT_VALIDATION_READ_ENGINE", "tikv").lower()
            if read_engine in {"tikv", "tiflash"}:
                cur.execute(f"SET SESSION tidb_isolation_read_engines='{read_engine}'")
            profiles = [
                column_profile(cur, table, column)
                for table, columns in PROFILE_COLUMNS.items()
                for column in columns
            ]
            fanout = group_c_fanout(cur)
    finally:
        conn.close()

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    write_markdown(output, profiles, fanout)
    print(output)


if __name__ == "__main__":
    main()
