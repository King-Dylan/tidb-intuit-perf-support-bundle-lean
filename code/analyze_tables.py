#!/usr/bin/env python3 -u
"""Run ANALYZE TABLE after each v12 load.

Bulk-loaded rebuilds need fresh stats before benchmark runs, otherwise the
optimizer can pick poor plans and make physical-design comparisons invalid.
"""

from __future__ import annotations

import sys
import time

import pymysql

from lib.db_config import get_db_config

sys.stdout.reconfigure(line_buffering=True)

TABLES = ("pmt_txn_fact", "deviceprofile_fact")


def main() -> None:
    cfg = get_db_config("v12 analyze tables")
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)
    try:
        with conn.cursor() as cur:
            for table in TABLES:
                started = time.time()
                print(f"ANALYZE TABLE {table} ...")
                cur.execute(f"ANALYZE TABLE {table}")
                rows = cur.fetchall()
                elapsed = time.time() - started
                print(f"Done {table} in {elapsed:.1f}s")
                for row in rows:
                    print("  " + " | ".join("" if v is None else str(v) for v in row))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
