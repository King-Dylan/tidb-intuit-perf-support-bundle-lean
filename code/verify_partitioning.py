#!/usr/bin/env python3 -u
"""Verify both main source tables for v12 physical-design benchmarks."""

from __future__ import annotations

import os
import sys

import pymysql

from lib.db_config import get_db_config

sys.stdout.reconfigure(line_buffering=True)

EXPECTED_TABLES = {
    "pmt_txn_fact": "event_date",
    "deviceprofile_fact": "jms_timestamp",
}

EXPECTED_INDEXES = {
    "pmt_txn_fact": {
        "PRIMARY",
        "idx_merchant_account_number_event_date",
        "idx_card_holder_number_sha512_event_date",
        "idx_check_bank_routing_number_event_date",
        "idx_check_routing_account_event",
        "idx_parsed_interaction_id_event_date",
        "idx_event_date",
    },
    "deviceprofile_fact": {
        "idx_interaction_id_jms_timestamp",
        "idx_exact_id_jms_timestamp",
        "idx_smart_id_jms_timestamp",
        "idx_input_ip_jms_timestamp",
        "idx_true_ip_jms_timestamp",
        "idx_jms_timestamp",
    },
}

EXPECTED_PARTITION_GRAIN = os.environ.get("INTUIT_PARTITION_GRAIN", "weekly").lower()
EXPECTED_SHARD_ROW_ID_BITS = os.environ.get("INTUIT_SHARD_ROW_ID_BITS", "4")
EXPECTED_PRE_SPLIT_REGIONS = os.environ.get("INTUIT_PRE_SPLIT_REGIONS", "3")
MIN_PARTITIONS_BY_GRAIN = {
    "daily": 180,
    "weekly": 25,
    "monthly": 6,
    "none": 0,
}


def main() -> None:
    cfg = get_db_config("partition verification")
    conn = pymysql.connect(**cfg)
    conn.autocommit(True)
    failures: list[str] = []
    try:
        with conn.cursor() as cur:
            for table, partition_col in EXPECTED_TABLES.items():
                cur.execute(
                    """
                    SELECT partition_name, table_rows
                    FROM information_schema.partitions
                    WHERE table_schema = DATABASE()
                      AND table_name = %s
                      AND partition_name IS NOT NULL
                    ORDER BY partition_ordinal_position
                    """,
                    (table,),
                )
                partitions = cur.fetchall()
                cur.execute(f"SHOW CREATE TABLE {table}")
                ddl = cur.fetchone()[1]
                has_partition_col = partition_col in ddl
                if EXPECTED_PARTITION_GRAIN == "none":
                    if partitions:
                        failures.append(f"{table} is partitioned but INTUIT_PARTITION_GRAIN=none")
                        continue
                elif not partitions or not has_partition_col:
                    failures.append(f"{table} is not partitioned by {partition_col}")
                    continue
                min_partitions = MIN_PARTITIONS_BY_GRAIN.get(EXPECTED_PARTITION_GRAIN, 25)
                if len(partitions) < min_partitions:
                    failures.append(
                        f"{table} has only {len(partitions)} partitions; expected {EXPECTED_PARTITION_GRAIN} partitioning"
                    )
                    continue
                ddl_no_spaces = ddl.replace(" ", "")
                expected_shard = f"SHARD_ROW_ID_BITS={EXPECTED_SHARD_ROW_ID_BITS}"
                expected_pre_split = f"PRE_SPLIT_REGIONS={EXPECTED_PRE_SPLIT_REGIONS}"
                if expected_shard not in ddl_no_spaces:
                    failures.append(
                        f"{table} is missing {expected_shard} for write/load hotspot mitigation"
                    )
                if expected_pre_split not in ddl_no_spaces:
                    failures.append(f"{table} is missing {expected_pre_split} for pre-split Regions")
                cur.execute(f"SHOW INDEX FROM {table}")
                actual_indexes = {row[2] for row in cur.fetchall()}
                missing_indexes = EXPECTED_INDEXES[table] - actual_indexes
                if missing_indexes:
                    failures.append(f"{table} is missing expected indexes: {', '.join(sorted(missing_indexes))}")
                if EXPECTED_PARTITION_GRAIN == "none":
                    print(f"{table}: not partitioned")
                else:
                    print(f"{table}: partitioned by {partition_col}")
                for name, approx_rows in partitions:
                    print(f"  {name}: approx {int(approx_rows or 0):,} rows")
        if failures:
            print("\nPartition verification failed:")
            for failure in failures:
                print(f"  - {failure}")
            raise SystemExit(1)
        print(
            "\nPartition verification passed for "
            f"INTUIT_PARTITION_GRAIN={EXPECTED_PARTITION_GRAIN}, "
            f"INTUIT_SHARD_ROW_ID_BITS={EXPECTED_SHARD_ROW_ID_BITS}, "
            f"INTUIT_PRE_SPLIT_REGIONS={EXPECTED_PRE_SPLIT_REGIONS}."
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
