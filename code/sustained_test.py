"""Small background writer used by the mixed traffic benchmark."""

from __future__ import annotations

import time
from queue import Queue
from typing import Any, Callable


def writer_thread(
    stop_evt,
    pool: Queue,
    table: str,
    sql: str,
    params_fn: Callable[[], tuple[Any, ...]],
    tps: float,
    results: list[dict[str, Any]],
) -> None:
    """Run a steady insert stream until ``stop_evt`` is set."""

    interval = 1.0 / tps if tps > 0 else 1.0
    next_fire = time.monotonic()
    while not stop_evt.is_set():
        now = time.monotonic()
        if now < next_fire:
            time.sleep(min(0.005, next_fire - now))
            continue

        started = time.perf_counter()
        conn = pool.get()
        ok = True
        error = None
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params_fn())
        except Exception as exc:  # Background writes should not stop read tests.
            ok = False
            error = str(exc)[:300]
        finally:
            pool.put(conn)

        row = {
            "table": table,
            "ts": time.time(),
            "ms": (time.perf_counter() - started) * 1000.0,
            "ok": ok,
        }
        if error:
            row["error"] = error
        results.append(row)
        next_fire += interval
