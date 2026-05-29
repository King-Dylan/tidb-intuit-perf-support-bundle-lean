#!/usr/bin/env python3 -u
"""Enable and wait for TiFlash replicas after a data load."""

import sys
sys.stdout.reconfigure(line_buffering=True)

import time

import pymysql

from lib.db_config import get_db_config


TABLES = ("pmt_txn_fact", "deviceprofile_fact")


def main():
    cfg = get_db_config("enable_tiflash")
    conn = pymysql.connect(**cfg)
    try:
        with conn.cursor() as cursor:
            print("Enabling TiFlash replicas...")
            for table in TABLES:
                cursor.execute(f"ALTER TABLE {table} SET TIFLASH REPLICA 1")
                print(f"  TiFlash replica set on {table}")

            print("Waiting for TiFlash replicas to sync...")
            while True:
                cursor.execute(
                    """
                    SELECT TABLE_NAME, PROGRESS
                    FROM information_schema.tiflash_replica
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME IN ('pmt_txn_fact', 'deviceprofile_fact')
                      AND PROGRESS < 1
                    """
                )
                pending = cursor.fetchall()
                if not pending:
                    print("  ✅ All TiFlash replicas are synced.")
                    return
                for table_name, progress in pending:
                    print(f"  {table_name}: {float(progress) * 100:.1f}% synced")
                time.sleep(10)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
