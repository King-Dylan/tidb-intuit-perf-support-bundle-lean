#!/usr/bin/env python3
"""Create the verified covering indexes on an existing database if missing."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pymysql

from lib.db_config import get_db_config
from optimized_config import OPTIMIZED_INDEXES, create_index_sql


def existing_indexes(cur) -> set[tuple[str, str]]:
    cur.execute(
        """
SELECT table_name, index_name
FROM information_schema.statistics
WHERE table_schema = DATABASE()
  AND table_name IN ('pmt_txn_fact', 'deviceprofile_fact')
GROUP BY table_name, index_name
"""
    )
    return {(str(table), str(index)) for table, index in cur.fetchall()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually create missing indexes. Without this, only prints DDL.")
    args = parser.parse_args()

    cfg = get_db_config(save_msg="apply optimized covering indexes")
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)
    try:
        with conn.cursor() as cur:
            present = existing_indexes(cur)
            missing: list[tuple[str, str, tuple[str, ...]]] = []
            for table, indexes in OPTIMIZED_INDEXES.items():
                for index_name, columns in indexes.items():
                    if (table, index_name) not in present:
                        missing.append((table, index_name, columns))

            if not missing:
                print("All optimized covering indexes already exist.")
                return

            for table, index_name, columns in missing:
                ddl = create_index_sql(table, index_name, columns)
                print(ddl + ";", flush=True)
                if args.execute:
                    started = time.perf_counter()
                    cur.execute(ddl)
                    print(f"created {index_name} in {(time.perf_counter() - started):.1f}s", flush=True)

            if not args.execute:
                print("\nDry run only. Re-run with --execute to create these indexes.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
