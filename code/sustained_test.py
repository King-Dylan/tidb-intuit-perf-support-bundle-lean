"""Compatibility shim for the lean support bundle.

The packaged mixed-traffic reader imports ``writer_thread`` at module load time,
but this lean bundle does not include the original write workload helper. The
read-only validation path passes ``--no-writes``, so this function should not be
called during our SQL-pattern check.
"""


def writer_thread(*_args, **_kwargs):
    raise RuntimeError("writer_thread is unavailable in the lean bundle; run with --no-writes")
