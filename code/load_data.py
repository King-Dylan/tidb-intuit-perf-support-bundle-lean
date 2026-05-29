#!/usr/bin/env python3 -u
"""
INTUIT RISK POC — Data Generator (v6 — PDF hot-key profile simulator)

Loads two source tables at production-matching shape:
  - `pmt_txn_fact`        — 83,461,494 rows (Oct 2025 → Apr 2026 partial)
  - `deviceprofile_fact`  — 365,744,830 rows (Nov 2025 → Apr 2026 partial)

Faithful to the shared PDF in:
  - per-month row counts (dashboard screenshots)
  - per-column null rates (field profile tables)
  - per-column top-N value frequencies (top10_freq rows)
  - amount distribution deciles (P10…P90, min, max)
  - weekday/weekend skew (Intuit's M-F > weekend statement)
  - modeled intra-day batch-spike + daytime + overnight pattern
  - entity cardinality bounded near PDF sample distinct counts
  - userSessionId 100% null in the shared profile

This loader is not a literal replay of Intuit production data. It is a
profile-driven simulator that uses synthetic long-tail values where the shared
materials only exposed top-N frequencies and summary stats.

Authoritative query-catalog alignment:
  - query-facing columns use snake_case
  - Group A and Group C use p.event_date in epoch millis

Customer clarification applied (Henry, 2026-04-22):
  - risk_profile_token has the form "<sessionID>:<interactionID>"
  - Group C should parse interactionID out of risk_profile_token
  - Group C should join on deviceprofile_fact.interaction_id
  - deviceprofile_fact.user_session_id remains null and is not the join key

Environment:
  - INTUIT_DEMO_SCALE=tiny|small|tenpct|full
    (default: tenpct in v12 — 10% row count with the same skew samplers)

Usage:
  python3 -u load_data.py                            # both tables, 10% profile-faithful load
  INTUIT_DEMO_SCALE=full python3 -u load_data.py     # full profile-faithful load
  python3 -u load_data.py --table pmt                # pmt_txn_fact only
  python3 -u load_data.py --table device             # deviceprofile_fact only
  INTUIT_DEMO_SCALE=small python3 -u load_data.py    # ~3M rows total, smoke
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import argparse
import pymysql
import random
import hashlib
import uuid
import time
import json
import os
import threading
import calendar
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, as_completed, wait
from datetime import datetime, timedelta
from getpass import getpass
from lib.db_config import get_db_config, load_db_config
from lib.transaction_profile import TXN_MONTHLY_COUNTS, FIELD_PROFILES
from lib.device_profile import (
    DEVICE_MONTHLY_COUNTS,
    DEVICE_DAY_WEIGHTS,
    DEVICE_STREAM_LABEL,
    DEVICE_FIELD_PROFILES,
    DEVICE_PROFILE_DRIVEN_COLUMNS,
)

def _env_int(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        print(f"ERROR: {name}={raw!r} must be an integer")
        sys.exit(1)
    if value <= 0:
        print(f"ERROR: {name} must be greater than 0")
        sys.exit(1)
    return value


# ─── Parallel insert config ───
NUM_WRITER_THREADS = _env_int("INTUIT_LOAD_WRITER_THREADS", 8)
BATCH_SIZE = _env_int("INTUIT_LOAD_BATCH_SIZE", 5000)
MAX_PENDING_BATCHES = _env_int("INTUIT_LOAD_MAX_PENDING_BATCHES", NUM_WRITER_THREADS * 4)
INSERT_RETRIES = _env_int("INTUIT_LOAD_INSERT_RETRIES", 5)

# TiDB Cloud/Premium can occasionally reject a large concurrent insert batch while
# internal schema metadata catches up. Retrying keeps one transient error from
# turning into a silent partial-table load.
RETRYABLE_INSERT_ERROR_CODES = {8027, 1105}
RANDOM_SEED = _env_int("INTUIT_RANDOM_SEED", 20260512)
random.seed(RANDOM_SEED)
_db_config_cache = None
_writer_local = threading.local()


_TXN_FULL_COUNT = sum(TXN_MONTHLY_COUNTS.values())
_DEVICE_FULL_COUNT = sum(DEVICE_MONTHLY_COUNTS.values())
ACTIVE_TABLE_KEYS = ('pmt_txn', 'deviceprofile')

# v12 defaults to 10% for the physical-design bakeoff. The generator still uses
# the same top-N/null/distinct samplers, so hot-key skew is preserved
# probabilistically while row counts are reduced.
_SCALES = {
    'tiny':  {'pmt_txn': 500_000, 'deviceprofile': 200_000},
    'small': {'pmt_txn': 2_000_000, 'deviceprofile': 1_000_000},
    'tenpct': {
        'pmt_txn': max(1, _TXN_FULL_COUNT // 10),
        'deviceprofile': max(1, _DEVICE_FULL_COUNT // 10),
    },
    'full':  {'pmt_txn': _TXN_FULL_COUNT, 'deviceprofile': _DEVICE_FULL_COUNT},
}
_scale_name = os.environ.get('INTUIT_DEMO_SCALE', 'tenpct').lower()
if _scale_name not in _SCALES:
    print(f"ERROR: INTUIT_DEMO_SCALE={_scale_name!r} invalid. Use: tiny / small / tenpct / full")
    sys.exit(1)
ROW_COUNTS = _SCALES[_scale_name]
print(f"[load_data] INTUIT_DEMO_SCALE={_scale_name}")
print(f"[load_data] active_tables={ACTIVE_TABLE_KEYS}")
print(f"[load_data] rows={ROW_COUNTS}")
print(
    "[load_data] insert_config="
    f"writer_threads={NUM_WRITER_THREADS}, batch_size={BATCH_SIZE:,}, "
    f"max_pending_batches={MAX_PENDING_BATCHES}"
)
print(f"[load_data] random_seed={RANDOM_SEED}")


def _env_float(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        print(f"ERROR: {name}={raw!r} must be a float")
        sys.exit(1)


def _env_json(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {name} must be valid JSON: {exc}")
        sys.exit(1)


# Henry clarified on 2026-04-29 that the successful Group C match should be
# effectively 1 device row -> 1 payment transaction row. The previous random
# shared-pool model reused 200K interaction IDs across hundreds of millions of
# rows, which created unrealistic many-to-many join fanout.
JOIN_MODEL = os.environ.get("INTUIT_JOIN_MODEL", "one_to_one").lower()
if JOIN_MODEL not in {"one_to_one", "legacy_random_pool"}:
    print("ERROR: INTUIT_JOIN_MODEL must be one_to_one or legacy_random_pool")
    sys.exit(1)

# Default keeps the existing pmt risk_profile_token non-null rate (~65.3%).
# Override this once Intuit provides exact expected joined-payment coverage.
JOIN_PMT_POPULATED_RATE = _env_float("INTUIT_JOIN_PMT_POPULATED_RATE", 0.653)
if not 0.0 <= JOIN_PMT_POPULATED_RATE <= 1.0:
    print("ERROR: INTUIT_JOIN_PMT_POPULATED_RATE must be between 0 and 1")
    sys.exit(1)

# Extra device rows may still have interaction IDs, but in one_to_one mode they
# are generated from a non-matching namespace so they do not create join fanout.
UNMATCHED_DEVICE_INTERACTION_RATE = _env_float("INTUIT_UNMATCHED_DEVICE_INTERACTION_RATE", 0.50)
if not 0.0 <= UNMATCHED_DEVICE_INTERACTION_RATE <= 1.0:
    print("ERROR: INTUIT_UNMATCHED_DEVICE_INTERACTION_RATE must be between 0 and 1")
    sys.exit(1)

JOIN_MATCHED_PAYMENT_ROWS = min(
    ROW_COUNTS["pmt_txn"],
    ROW_COUNTS["deviceprofile"],
    int(ROW_COUNTS["pmt_txn"] * JOIN_PMT_POPULATED_RATE),
)

# Placeholder config for Henry's pending records-per-hot-key numbers. The
# loader does not enforce these caps yet; validation can use them once supplied.
HOT_KEY_ROW_TARGETS = _env_json("INTUIT_HOT_KEY_ROW_TARGETS_JSON", {})
print(
    "[load_data] join_model="
    f"{JOIN_MODEL}, matched_payment_rows={JOIN_MATCHED_PAYMENT_ROWS:,}, "
    f"unmatched_device_interaction_rate={UNMATCHED_DEVICE_INTERACTION_RATE:.3f}"
)
if HOT_KEY_ROW_TARGETS:
    print(f"[load_data] hot_key_row_targets={HOT_KEY_ROW_TARGETS}")

def setup_pools():
    """Generate all entity pools used by data generators."""
    global NUM_EXACT_IDS, NUM_SMART_IDS, NUM_IPS
    global NUM_MERCHANTS, NUM_REALMS, NUM_CARDS, NUM_ROUTING, NUM_CHECK_SHAS
    global exact_ids, smart_ids
    global input_ips, true_ips, proxy_ips
    global merchant_accounts, realm_ids, card_shas, routing_numbers, check_shas
    global NUM_SHARED_INTERACTIONS, shared_interaction_ids, shared_session_prefixes, shared_risk_profile_tokens

    # ─── Entity pool sizes match PDF profile's observed distinct counts ───
    NUM_EXACT_IDS = 500_000
    NUM_SMART_IDS = 400_000
    NUM_IPS = 200_000
    NUM_MERCHANTS = 316_459   # accountNumber distinct
    NUM_REALMS = 316_219      # realmId distinct
    NUM_CARDS = 524_635       # cardHolderNumberSha512 distinct
    NUM_ROUTING = 7_373       # checkBankRoutingNumber distinct
    NUM_CHECK_SHAS = 150_000  # modeled override so routing+account Group A queries hit rows

    # ─── Lookup pools (generated once, reused) ───
    exact_ids = [hashlib.md5(f"exact_{i}".encode()).hexdigest() for i in range(NUM_EXACT_IDS)]
    smart_ids = [hashlib.md5(f"smart_{i}".encode()).hexdigest() for i in range(NUM_SMART_IDS)]
    input_ips = [f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(NUM_IPS)]
    true_ips = [f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(NUM_IPS)]
    proxy_ips = [f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(5000)]
    merchant_accounts = [5000000000000000 + i for i in range(NUM_MERCHANTS)]
    realm_ids = [str(120000000000000 + i) for i in range(NUM_REALMS)]
    card_shas = [hashlib.sha512(f"card_{i}".encode()).hexdigest()[:64] for i in range(NUM_CARDS)]
    routing_numbers = [f"{random.randint(100000000, 399999999)}" for _ in range(NUM_ROUTING)]
    check_shas = [hashlib.sha512(f"check_{i}".encode()).hexdigest()[:64] for i in range(NUM_CHECK_SHAS)]

    # ─── Shared Group C join pool: "<sessionID>:<interactionID>" ↔ interaction_id ───
    # Henry clarified the production semantics:
    #   risk_profile_token = "<sessionID>:<interactionID>"
    #   parse interactionID from risk_profile_token
    #   join to deviceprofile_fact.interaction_id
    NUM_SHARED_INTERACTIONS = 200_000
    shared_interaction_ids = [f"bfsId{10000 + i}" for i in range(NUM_SHARED_INTERACTIONS)]
    shared_session_prefixes = [hashlib.md5(f"shared_sess_{i}".encode()).hexdigest()[:32] for i in range(NUM_SHARED_INTERACTIONS)]
    shared_risk_profile_tokens = [
        f"{shared_session_prefixes[i]}:{shared_interaction_ids[i]}"
        for i in range(NUM_SHARED_INTERACTIONS)
    ]


_TXN_MONTH_SEQUENCE = [
    (int(month.split("-")[0]), int(month.split("-")[1]), count)
    for month, count in TXN_MONTHLY_COUNTS.items()
]
_TXN_MONTH_TOTAL = sum(count for _, _, count in _TXN_MONTH_SEQUENCE)
_TXN_MONTH_CUMULATIVE = []
_running = 0
for year, month, count in _TXN_MONTH_SEQUENCE:
    _running += count
    _TXN_MONTH_CUMULATIVE.append((year, month, _running / _TXN_MONTH_TOTAL))


def _profile_top_freq(field_name):
    return FIELD_PROFILES[field_name].get('top10_freq', {})


def _profile_null_pct(field_name):
    return FIELD_PROFILES.get(field_name, {}).get('null_pct', 0.0) / 100.0


def sample_profile_value(field_name, fallback=None):
    """Sample a categorical value according to the exact visible profile weights."""
    top = _profile_top_freq(field_name)
    if not top:
        return fallback

    values = list(top.keys())
    weights = list(top.values())
    total = sum(weights)
    if total <= 0:
        return fallback

    norm = [w / total for w in weights]
    return random.choices(values, weights=norm, k=1)[0]


def sample_profile_bool(field_name, fallback=False):
    val = sample_profile_value(field_name, fallback)
    return fallback if val is None else val


def sample_with_tail(field_name, tail_fn, fallback=None):
    """Sample using PDF top-N at their exact frequencies, falling back to
    tail_fn() for the remaining long tail. Used for high-cardinality columns
    like cardNumberLeft / mtIpAddress / mtCardHolderName where the PDF shows
    a few hot values at specific rates + a long tail of unique values.

    Example: cardNumberLeft has top-10 covering ~46% of rows; the remaining
    54% need to come from the 17,316-value BIN pool.
    """
    top = _profile_top_freq(field_name)
    if not top:
        return tail_fn()
    r = random.random()
    cum = 0.0
    for value, weight in top.items():
        cum += weight
        if r < cum:
            return value
    # Beyond top-N cumulative → long tail
    return tail_fn()


def sample_profile_key_with_tail(field_name, tail_fn, cast_fn=lambda value: value):
    """Sample a query-facing hot key using the PDF top10_freq as absolute mass.

    Henry clarified that top10_freq is the percent of rows in the source window
    with that value. For key columns we therefore sample top values at their
    absolute frequency, then draw the remaining non-null mass from the long tail.
    """
    value = sample_with_tail(field_name, tail_fn)
    return cast_fn(value) if value is not None else None


def sample_nullable_tail(field_name, tail_fn):
    """Sample null rate from the PDF for fields that do not expose real top keys."""
    if random.random() < _profile_null_pct(field_name):
        return None
    return tail_fn()


def sample_amount_from_profile():
    """Piecewise sample using the exact visible deciles from the transaction profile."""
    p = FIELD_PROFILES['amount']
    anchors = [
        p['min'], p['p10'], p['p20'], p['p30'], p['p40'],
        p['p50'], p['p60'], p['p70'], p['p80'], p['p90'], p['max'],
    ]
    bucket = random.randint(0, 9)
    lo = anchors[bucket]
    hi = anchors[bucket + 1]
    if bucket == 9:
        # long upper tail — bias toward lower end inside final bucket
        r = random.random() ** 2.0
    else:
        r = random.random()
    return round(lo + (hi - lo) * r, 2)


_BASE36_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def _to_base36(num):
    if num == 0:
        return "0"
    out = []
    n = num
    while n:
        n, rem = divmod(n, 36)
        out.append(_BASE36_ALPHABET[rem])
    return "".join(reversed(out))


def _to_epoch_ms(dt):
    return int(dt.timestamp() * 1000)


def _matched_interaction_id(row_index):
    return f"bfsIdP{row_index:012d}"


def _unmatched_device_interaction_id(row_index):
    return f"unmatchedBfsIdD{row_index:012d}"


def _matched_session_prefix(row_index):
    return hashlib.md5(f"matched_sess_{row_index}".encode()).hexdigest()[:32]


def _matched_risk_profile_token(row_index):
    return f"{_matched_session_prefix(row_index)}:{_matched_interaction_id(row_index)}"


def payment_join_values(row_index):
    """Return (risk_profile_token, parsed_interaction_id, session_id).

    In one_to_one mode, payment row i and device row i share a unique
    interaction_id for the configured matched prefix. In legacy mode, keep the
    old random shared-pool behavior for reproducibility.
    """
    if JOIN_MODEL == "legacy_random_pool":
        rpt = random.choice(shared_risk_profile_tokens) if random.random() >= 0.347 else None
        return (
            rpt,
            rpt.rsplit(":", 1)[-1] if rpt else None,
            rpt.split(":", 1)[0] if rpt else None,
        )

    if row_index >= JOIN_MATCHED_PAYMENT_ROWS:
        return None, None, None
    rpt = _matched_risk_profile_token(row_index)
    return rpt, _matched_interaction_id(row_index), _matched_session_prefix(row_index)


def device_interaction_id_for_row(row_index):
    """Return deviceprofile_fact.interaction_id without creating join fanout."""
    if JOIN_MODEL == "legacy_random_pool":
        return random.choice(shared_interaction_ids) if random.random() < 0.50 else None

    if row_index < JOIN_MATCHED_PAYMENT_ROWS:
        return _matched_interaction_id(row_index)
    if random.random() < UNMATCHED_DEVICE_INTERACTION_RATE:
        return _unmatched_device_interaction_id(row_index)
    return None


def sample_transaction_status_id():
    # Profile shows 15504 dominates nearly every percentile with min 15503 and max 15516.
    return random.choices(
        [15504, 15503, 15516, 15505, 15506, 15507, 15508, 15509],
        weights=[980, 8, 3, 3, 2, 2, 1, 1],
        k=1,
    )[0]


def sample_hk_source_id():
    # PDF profile: distinct=4, min=7000, p10-p70=7000, p80=p90=7100, max=25000.
    # Only 7000 / 7100 / 25000 are directly visible in the shared material.
    # We infer a 4th low-frequency value (13200) by fitting the screenshot's
    # printed distinct count, mean (7276.9114), stddev (2106.4136), and
    # percentile shape. This is still a modeling assumption, not a confirmed
    # Intuit value, and should be replaced if Intuit provides the real 4th ID.
    return random.choices(
        [7000, 7100, 13200, 25000],
        weights=[8670, 1159, 36, 135],
        k=1,
    )[0]


_TXN_APR_LAST_DAY = 10  # dashboard's 2026-04 only covers through Apr 10


def sample_transaction_timestamp():
    """Sample payment timestamps using the exact monthly volume profile from the source doc."""
    r = random.random()
    chosen_year, chosen_month = _TXN_MONTH_SEQUENCE[-1][0], _TXN_MONTH_SEQUENCE[-1][1]
    for year, month, cutoff in _TXN_MONTH_CUMULATIVE:
        if r <= cutoff:
            chosen_year, chosen_month = year, month
            break

    if chosen_year == 2026 and chosen_month == 4:
        days_in_month = _TXN_APR_LAST_DAY  # partial month (Apr 1-10)
    else:
        days_in_month = calendar.monthrange(chosen_year, chosen_month)[1]
    day_weights = []
    for day_num in range(1, days_in_month + 1):
        weekday = datetime(chosen_year, chosen_month, day_num).weekday()
        day_weights.append(DEVICE_DAY_WEIGHTS[weekday])
    day = random.choices(range(1, days_in_month + 1), weights=day_weights, k=1)[0]

    # Approximate the visual eventbus TPS graph: low overnight baseline, daytime hum, one sharp daily spike.
    hour = random.choices(
        list(range(24)),
        weights=[2, 2, 2, 2, 2, 3, 4, 6, 5, 4, 3, 3, 3, 4, 5, 7, 6, 5, 4, 3, 3, 2, 2, 2],
        k=1,
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    microsecond = random.randint(0, 999999)
    return datetime(chosen_year, chosen_month, day, hour, minute, second, microsecond)


_DEVICE_MONTH_SEQUENCE = [
    (int(month.split("-")[0]), int(month.split("-")[1]), count)
    for month, count in DEVICE_MONTHLY_COUNTS.items()
]
_DEVICE_MONTH_TOTAL = sum(count for _, _, count in _DEVICE_MONTH_SEQUENCE)
_DEVICE_MONTH_CUMULATIVE = []
_running_dev = 0
for _year, _month, _count in _DEVICE_MONTH_SEQUENCE:
    _running_dev += _count
    _DEVICE_MONTH_CUMULATIVE.append((_year, _month, _running_dev / _DEVICE_MONTH_TOTAL))

# Partial-month cap for 2026-04 (PDF dashboard ends around Apr 10)
_DEVICE_APR_LAST_DAY = 10


def sample_device_timestamp():
    """Sample device timestamps using the exact monthly volume profile from
    the dashboard (2025-11 → 2026-04). Matches the steep growth trend seen
    in the PDF (45.6M → 90.7M over 6 months).
    """
    r = random.random()
    chosen_year, chosen_month = _DEVICE_MONTH_SEQUENCE[-1][0], _DEVICE_MONTH_SEQUENCE[-1][1]
    for year, month, cutoff in _DEVICE_MONTH_CUMULATIVE:
        if r <= cutoff:
            chosen_year, chosen_month = year, month
            break

    if chosen_year == 2026 and chosen_month == 4:
        days_in_month = _DEVICE_APR_LAST_DAY  # partial month
    else:
        days_in_month = calendar.monthrange(chosen_year, chosen_month)[1]

    day_weights = []
    for day_num in range(1, days_in_month + 1):
        weekday = datetime(chosen_year, chosen_month, day_num).weekday()
        day_weights.append(DEVICE_DAY_WEIGHTS[weekday])
    day = random.choices(range(1, days_in_month + 1), weights=day_weights, k=1)[0]

    hour = random.choices(
        list(range(24)),
        weights=[2, 2, 2, 2, 2, 3, 4, 5, 5, 4, 4, 4, 4, 4, 5, 6, 6, 5, 4, 4, 3, 2, 2, 2],
        k=1,
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    microsecond = random.randint(0, 999999)
    return datetime(
        chosen_year, chosen_month, day,
        hour, minute, second, microsecond,
    )


# ──────────────────────────────────────────────────────────────────────────
# Device-profile sampling — mirrors sample_profile_value / sample_profile_bool
# but reads from DEVICE_FIELD_PROFILES so exact PDF frequencies apply.
# ──────────────────────────────────────────────────────────────────────────
def _device_profile_top_freq(field_name):
    prof = DEVICE_FIELD_PROFILES.get(field_name, {})
    return prof.get('top10_freq', {})


def _device_profile_null_pct(field_name):
    return DEVICE_FIELD_PROFILES.get(field_name, {}).get('null_pct', 0.0) / 100.0


def sample_device_profile_value(field_name, fallback=None):
    top = _device_profile_top_freq(field_name)
    if not top:
        return fallback
    values = list(top.keys())
    weights = list(top.values())
    total = sum(weights)
    if total <= 0:
        return fallback
    norm = [w / total for w in weights]
    return random.choices(values, weights=norm, k=1)[0]


def sample_device_with_tail(field_name, tail_fn, fallback=None):
    """Device top-N + long-tail sampler. Uses PDF top10 cumulative frequencies
    and falls back to tail_fn() for distribution mass beyond the top-N —
    preserves high-cardinality distinct counts (e.g. browserString distinct=1629,
    trueIpIsp distinct=2789, requestDuration distinct=266)."""
    top = _device_profile_top_freq(field_name)
    if not top:
        return tail_fn() if tail_fn else fallback
    r = random.random()
    cum = 0.0
    for value, weight in top.items():
        cum += weight
        if r < cum:
            return value
    return tail_fn() if tail_fn else fallback


def sample_device_key_with_tail(field_name, tail_fn):
    """Sample device hot keys from the 1-month device profile top10_freq table."""
    top = _device_profile_top_freq(field_name)
    if top:
        return sample_device_with_tail(field_name, tail_fn)
    if random.random() < _device_profile_null_pct(field_name):
        return None
    return tail_fn()


# ─── Synthetic long-tail generators for high-distinct device columns ───
# These are called when a device-field sampler falls beyond the PDF's top-N
# frequencies. They produce synthetic values at the approximate cardinality
# the PDF profile reports, so SELECT COUNT(DISTINCT …) lines up with PDF.
def _device_tail_score_0_20():
    return str(random.randint(0, 20))

def _device_tail_score_neg():
    return str(random.randint(-100, -1))

def _device_tail_geo():
    return random.choice(['FR','DE','JP','BR','RU','IT','ES','KR','TR','PL','SE','NO','FI','DK','IE','NZ','ZA','AR','CL','PE'])

def _device_tail_isp():
    return f"isp_{random.randint(1000, 9999)}"

def _device_tail_language():
    base = random.choice(['fr','de','es','ja','zh','pt','it','ko','ru','nl','sv','pl','tr'])
    return f"{base},en;q=0.{random.randint(1,9)}"

def _device_tail_browser_string():
    ua = random.choice(['Chrome','Firefox','Safari','Edge','Opera'])
    v = random.randint(100, 200)
    return f"Mozilla/5.0 Synthetic AppleWebKit/537.36 {ua}/{v}.0.0.0"

def _device_tail_request_duration():
    return str(random.randint(0, 500))


def device_is_null(field_name):
    """True if this row should be null for this column, per PDF null rate."""
    prof = DEVICE_FIELD_PROFILES.get(field_name, {})
    null_pct = prof.get('null_pct', 0.0) / 100.0
    return random.random() < null_pct


# ─── Entity selection (matches PDF's near-uniform long-tail distribution) ───
# PDF column-profile screenshots show top-10 values of high-cardinality columns
# (accountNumber, realmId, cardHolderNumberSha512, etc.) ALL at ~0.1% each —
# meaning the top 10 entities together account for ~1% of traffic and the
# remaining 99% is uniformly spread across 316K+ entities. This is a very
# mild hotspot, essentially uniform.
#
# The previous tier-based implementation forced the top 0.1% to receive 10% of
# traffic (100x over-concentrated). Using uniform random.choice here to match
# the near-uniform shape the PDF actually shows.
def weighted_choice(pool, hot_pct=0.01, hot_weight=50):
    """Pick from pool uniformly. Matches PDF's observed long-tail-near-uniform
    shape where the top-10 entities each get ~0.1% of traffic and the rest are
    roughly uniformly sampled. The `hot_pct` / `hot_weight` parameters are
    kept for backward compatibility but no longer alter the distribution.
    """
    n = len(pool)
    if n == 0:
        return None
    return pool[random.randint(0, n - 1)]


# ─── Event type distributions ───
RSS_EVENT_TYPES = ['ASSERTION', 'ASSERTION', 'ASSERTION', 'ASSERTION',  # 40%
                   'LOGIN', 'LOGIN', 'LOGIN',                           # 30%
                   'CREATION', 'CREATION',                              # 20%
                   'LOOKUP', 'UPDATE']                                  # 10%

TRANSACTIONS = ['auth_passed', 'auth_passed', 'auth_passed', 'auth_passed',
                'auth_passed', 'auth_passed', 'auth_passed',           # 70% pass
                'challenge_passed', 'challenge_passed',                 # 20%
                'auth_failed']                                          # 10%

CHALLENGE_TYPES = ['password', 'password', 'password', 'password',     # 40%
                   'sms', 'sms',                                        # 20%
                   'email', 'email',                                    # 20%
                   'known_device',                                      # 10%
                   'totp', 'idp', 'voice']                              # 10%

CHANNELS = ['QBO_SPA', 'QBO_SPA', 'QBO_SPA',                          # 30%
            'QBSE', 'QBSE',                                            # 20%
            'QBP', 'QBP',                                              # 20%
            'MINT',                                                     # 10%
            'TTO',                                                      # 10%
            'MAILCHIMP']                                                # 10%

# PDF 2 query predicates filter on card_type IN (CREDIT, PREPAID, GIFT) —
# these must appear in the data for those queries to return non-zero rows.
# Real Intuit distribution (PDF 2 profile): CHECK ("C") 73.7%, null 26.3%.
# Demo blends both: Check-heavy real distribution + rare values for query coverage.
CARD_TYPES = ['CHECK'] * 70 + [  # ~70% CHECK matches real Intuit distribution
    'VISA', 'VISA', 'VISA', 'VISA', 'VISA',                           # 5%
    'MC', 'MC', 'MC', 'MC',                                           # 4%
    'AMEX', 'AMEX',                                                    # 2%
    'DISCOVER',                                                        # 1%
    'CREDIT', 'CREDIT', 'CREDIT', 'CREDIT',                            # 4% — PDF Group A predicate
    'DEBIT', 'DEBIT',                                                  # 2% — PDF Group A predicate
    'PREPAID', 'PREPAID',                                              # 2% — PDF Group A predicate
    'GIFT',                                                            # 1% — PDF Group A predicate
    'ACH', 'ACH',                                                      # 2%
    'UNKNOWN',                                                         # 1%
]

# PDF 2 query predicates span ~20 transaction_type values. Real Intuit
# distribution is dominated by Sale (99.6%), but we include rare occurrences
# of every predicate value so Group A queries return non-zero rows.
# Weighted: Sale ≈ 80%, Refund ≈ 5%, everything else ≈ 0.5-1% each.
TXN_TYPES = (
    ['Sale'] * 80  # ~80% — real Intuit dominant value (PDF shows 99.6%)
    + ['Refund'] * 5
    + ['Capture'] * 2
    + ['Void'] * 2
    + ['Auth'] * 2
    + ['Chargeback'] * 1
    + ['Dispute'] * 1
    + ['Credit'] * 1
    + ['Debit'] * 1
    + ['AuthOnly'] * 1
    + ['CaptureOnly'] * 1
    + ['PostAuth'] * 1
    + ['PreAuth'] * 1
    + ['Return'] * 1
    + ['Reversal'] * 1
    + ['Reversal_NSF']
    + ['Reversal_Timeout']
    + ['CAPTURE_ORDER']
    + ['EMV_Advice']
    + ['Adjustment']
)

RISK_RECS = ['PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS',
             'PASS', 'PASS', 'REVIEW', 'DENY']

OFFERING_IDS = [
    'intuit.smallbusiness.highvaluehub.hvchubsignin',
    'intuit.smallbusiness.qbo.spa',
    'intuit.cto.iam.ticket',
    'intuit.smallbusiness.payments.webapp',
    'intuit.turbotax.web',
    'intuit.mint.web'
]

BIZ_TRANSACTIONS = ['Invoice Payment', 'Invoice Payment', 'Invoice Payment',
                     'CP Invoice Payment', 'CP Invoice Payment',
                     'Recurring Payment', 'Deposit', 'Refund']

COUNTRIES = ['US', 'US', 'US', 'US', 'US', 'US', 'US',               # 70% US
             'CA', 'GB', 'AU', 'IN', 'DE', 'FR', 'MX',
             'JP', 'BR', 'KR', 'SG', 'NL', 'SE']

SIC_CODES = ['7299', '5411', '5812', '5999', '8011', '7230', '5944',
             '5541', '7311', '5311', '5661', '5651', '8099']


def _get_writer_conn():
    """Get or create one reusable DB connection per writer thread."""
    global _db_config_cache
    if _db_config_cache is None:
        _db_config_cache = load_db_config()
        _db_config_cache['autocommit'] = True
    conn = getattr(_writer_local, 'conn', None)
    if conn is None or not conn.open:
        conn = pymysql.connect(**_db_config_cache)
        _writer_local.conn = conn
    return conn


def _insert_batch(sql, batch):
    """Insert a batch using the writer thread's reusable connection."""
    for attempt in range(INSERT_RETRIES + 1):
        conn = _get_writer_conn()
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, batch)
            return len(batch)
        except pymysql.err.OperationalError as exc:
            code = exc.args[0] if exc.args else None
            if code not in RETRYABLE_INSERT_ERROR_CODES or attempt >= INSERT_RETRIES:
                raise
            try:
                conn.close()
            except Exception:
                pass
            _writer_local.conn = None
            sleep_s = min(30.0, 1.0 * (2 ** attempt)) + random.random()
            print(
                f"  retryable insert error {code}; retrying batch "
                f"{attempt + 1}/{INSERT_RETRIES} after {sleep_s:.1f}s"
            )
            time.sleep(sleep_s)
        finally:
            cursor.close()


def parallel_insert(sql, row_generator, target, label):
    """Generate rows and insert them in parallel using a thread pool.
    row_generator is a callable that yields tuples.
    """
    count = 0
    batch = []
    start = time.time()
    futures = set()
    report_interval = max(50000, target // 20)

    with ThreadPoolExecutor(max_workers=NUM_WRITER_THREADS) as executor:
        for row in row_generator(target):
            batch.append(row)
            if len(batch) >= BATCH_SIZE:
                futures.add(executor.submit(_insert_batch, sql, batch))
                batch = []

                # Collect completed futures and report progress
                done = {f for f in futures if f.done()}
                for f in done:
                    count += f.result()
                    futures.remove(f)

                # Keep memory bounded when using aggressive writer settings.
                if len(futures) >= MAX_PENDING_BATCHES:
                    done, futures = wait(futures, return_when=FIRST_COMPLETED)
                    for f in done:
                        count += f.result()

                if count > 0 and count % report_interval < BATCH_SIZE:
                    elapsed = time.time() - start
                    rate = count / elapsed if elapsed > 0 else 0
                    print(f"  {count:>12,}/{target:,}  ({rate:,.0f} rows/sec)")

        # Submit remaining batch
        if batch:
            futures.add(executor.submit(_insert_batch, sql, batch))

        # Wait for all remaining
        for f in as_completed(futures):
            count += f.result()

    elapsed = time.time() - start
    print(f"  ✅ Done: {count:,} rows in {elapsed:.1f}s ({count/elapsed:,.0f} rows/sec)\n")


def generate_pmt_txn(conn, start_index=0, row_count=None):
    """Generate payment transaction events (500K per scale factor)"""
    target = row_count if row_count is not None else ROW_COUNTS['pmt_txn']
    end_index = start_index + target
    print(f"\n\n{'─'*60}")
    print(f"  [1/2] Generating {target:,} payment transactions")
    print(f"  Row index range: [{start_index:,}, {end_index:,})")
    print(f"  Source: ihub-cassandra-sync Kafka topic (35 TPS)")
    print(f"  What it is: Payment amounts, card types, merchant accounts.")
    print(f"  Using {NUM_WRITER_THREADS} parallel writers, batch size {BATCH_SIZE}")
    print(f"{'─'*60}")

    INSERT_SQL = """
        INSERT INTO pmt_txn_fact
        (merchant_account_number, authorization_date, batch_date, transaction_id,
         realm_id, invoice_number, mas_transaction_netted, transaction_status_id,
         mt_result_code, amount, authorization_code, cutoff_date,
         transaction_type, mt_invoice_id, mt_gateway, entry_method,
         currency_code, number_type_code, deposit_id, is_ready_for_risk,
         transaction_date, event_date, mt_avs_street_match, application_type,
         pts_intuit_qual_code, hk_modified, pos_entry_mode_code,
         mt_vendor_result_code, mt_response_message, mt_card_country_code,
         mt_avs_zip_match, mt_card_holder_name, mt_ip_address,
         card_holder_number_sha512, card_number_left,
         check_bank_routing_number, check_bank_account_number_sha512,
         card_type, risk_profile_token, parsed_interaction_id, interaction_id, session_id,
         is_swiped, orig_batch_date, hk_source_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    def gen_rows(target):
        for local_i in range(target):
            i = start_index + local_i
            ts = sample_transaction_timestamp()
            acct = sample_profile_key_with_tail(
                'accountNumber',
                tail_fn=lambda: random.choice(merchant_accounts),
                cast_fn=int,
            )
            rid = sample_profile_key_with_tail(
                'realmId',
                tail_fn=lambda: random.choice(realm_ids),
                cast_fn=str,
            )
            # Sequential invoiceNumber to guarantee PK uniqueness across all
            # 83.5M rows. Random 8-digit would collide ~38M times.
            inv = f"INV{i:010d}"
            # Keep transactionId unique but in a different ID space from invoiceNumber.
            txn_id = _to_base36(i + 36**9).rjust(10, "0")

            amt = sample_amount_from_profile()
            curr = sample_profile_value('currencyCode', 'USD')

            txn_type = sample_profile_value('transactionType', 'Sale')
            status = sample_transaction_status_id()
            mas_netted = 0
            mt_result = 0
            auth_code = f"{random.randint(0, 0xFFFFFF):06X}D" if random.random() >= 0.015 else None

            card_type = sample_profile_value('cardType', 'C')
            number_type = sample_profile_value('numberTypeCode', 'C')
            card_sha = sample_nullable_tail(
                'cardHolderNumberSha512',
                tail_fn=lambda: random.choice(card_shas),
            )
            # cardNumberLeft: top-10 BINs at PDF rates (424631 3.4%, 414720 2.7%, …)
            # + long tail of 17,316 BIN prefixes. 27.8% null and 7.1% blank baked in.
            card_left = sample_with_tail(
                'cardNumberLeft',
                tail_fn=lambda: f"{random.randint(400000, 499999)}",
            )
            # mtCardHolderName: top-10 at PDF rates ("Visa Cardholder" 2.2%, …)
            # + long tail of synthetic names. 4% null baked in.
            card_name = sample_with_tail(
                'mtCardHolderName',
                tail_fn=lambda: f"NAME_{random.randint(1000, 9999)}",
            )
            # checkBankRoutingNumber: top-10 real routings at PDF rates
            # (322271627 0.8%, …) + long tail from the 7,373-value pool.
            routing = sample_with_tail(
                'checkBankRoutingNumber',
                tail_fn=lambda: random.choice(routing_numbers),
            )
            card_country = sample_profile_value('mtCardCountryCode', 'USA') or 'USA'
            entry = sample_profile_value('entryMethod', None)
            pos_mode = sample_profile_value('posEntryMode', 'T1')
            is_swiped = sample_profile_bool('isSwiped', False)
            gateway = sample_profile_value('mtGateway', 'MM-MerchantLink')
            qual_code = sample_profile_value('ptsIntuitQualCode', None)

            # Henry confirmed this hash is populated only for ACH transactions.
            # The ACH/check subset is represented by rows with a routing number,
            # so keep account hashes aligned with check_bank_routing_number.
            check_sha = random.choice(check_shas) if routing is not None else None

            avs_street = sample_profile_value('mtAvsStreetMatch', None)
            avs_zip = sample_profile_value('mtAvsZipMatch', None)
            vendor_result = sample_profile_value('mtVendorResultCode', '100')
            response_msg = sample_profile_value('mtResponseMessage', 'Approved')

            # mtIpAddress: "1.1.1.1" hot at 2.5% per PDF, rest uniform from pool.
            # 37.5% null baked in.
            ip = sample_with_tail(
                'mtIpAddress',
                tail_fn=lambda: random.choice(input_ips),
            )
            mt_inv_id = None  # PDF: 100% null

            auth_date = ts - timedelta(seconds=random.randint(0, 300))
            batch_date = ts.replace(hour=0, minute=0, second=0, microsecond=0)
            # The shared profile shows these columns with only ~182/183 distinct
            # day values over six months, so keep them day-granular.
            txn_date = batch_date
            event_date = _to_epoch_ms(ts)
            orig_batch = batch_date
            cutoff = ts.replace(hour=23, minute=59, second=59, microsecond=0) if random.random() >= 0.737 else None
            ready_risk = batch_date
            hk_mod = batch_date

            deposit = f"DEP{i:010d}" if random.random() >= 0.002 else None
            hk_src = sample_hk_source_id()

            # applicationType: PDF shows distinct=483, top-10 dominated by
            # "56936934210892107390" at 56.4%. Now profile-driven.
            app_type = sample_profile_value('applicationType', None)

            # Henry clarified the production path:
            #   risk_profile_token = "<sessionID>:<interactionID>"
            #   parse interactionID and join to d.interaction_id
            # In one_to_one mode this avoids synthetic many-to-many fanout.
            rpt, parsed_int_id, sess = payment_join_values(i)
            int_id = None

            yield (
                acct, auth_date, batch_date, txn_id,
                rid, inv, mas_netted, status,
                mt_result, amt, auth_code, cutoff,
                txn_type, mt_inv_id, gateway, entry,
                curr, number_type, deposit, ready_risk,
                txn_date, event_date, avs_street, app_type,
                qual_code, hk_mod, pos_mode,
                vendor_result, response_msg, card_country,
                avs_zip, card_name, ip,
                card_sha, card_left,
                routing, check_sha,
                card_type, rpt, parsed_int_id, int_id, sess,
                is_swiped, orig_batch, hk_src
            )

    parallel_insert(INSERT_SQL, gen_rows, target, "PMT txn")


def generate_deviceprofile(conn, start_index=0, row_count=None):
    """Generate device profile events, driven by DEVICE_FIELD_PROFILES from the PDF.

    Null rates, top-N frequencies, and per-column distinct counts all come from
    the PDF's column profile screenshot. For unbounded fields (intuitTid,
    messageId, requestId, transactionId, IPs, device hashes) we generate
    synthetic unique values at the PDF's observed density.
    """
    target = row_count if row_count is not None else ROW_COUNTS['deviceprofile']
    end_index = start_index + target
    print(f"\n\n{'─'*60}")
    print(f"  [2/2] Generating {target:,} device profile events")
    print(f"  Row index range: [{start_index:,}, {end_index:,})")
    print(f"  Source: platform-identity-deviceprofile Kafka topic (40 TPS)")
    print(f"  Distribution follows DEVICE_FIELD_PROFILES from device_profile.py")
    print(f"  (PDF column-profile screenshot, ~90,821-row sample).")
    print(f"  user_session_id: 100% null (matches shared profile)")
    print(f"  interaction_id: {JOIN_MODEL} mode for Henry-style Group C joins")
    print(f"  Using {NUM_WRITER_THREADS} parallel writers, batch size {BATCH_SIZE}")
    print(f"{'─'*60}")

    INSERT_SQL = """
        INSERT INTO deviceprofile_fact
        (intuit_tid, realm_id, message_id, request_id,
         event_type, app_id, api_name, api_result, offering_id,
         transaction_id, org_id, user_session_id, request_duration, request_result,
         business_transaction, jms_timestamp, interaction_id, session_id, intuit_jmsbodyapiname,
         exact_id, smart_id, input_ip, true_ip, proxy_ip,
         agent_type, agent_os, browser_language, browser_string, device_match_result,
         dns_ip, input_ip_geo, input_ip_isp, input_ip_score,
         true_ip_geo, true_ip_isp, true_ip_result, true_ip_score,
         proxy_ip_geo, proxy_ip_isp, proxy_type, proxy_ip_score,
         device_score, device_fingerprint_score, device_worst_score,
         fuzzy_device_score, true_ip_worst_score, proxy_ip_worst_score,
         device_fingerprint_result, device_result, proxy_ip_result, fuzzy_device_result,
         dns_ip_hosting_facility, proxy_ip_hosting_facility, true_ip_hosting_facility,
         browser_anomaly, screen_res_anomaly, os_anomaly, dns_ip_assert_history)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    def _fresh_ip():
        return (f"{random.randint(1,223)}.{random.randint(0,255)}."
                f"{random.randint(0,255)}.{random.randint(1,254)}")

    def gen_rows(target):
        for local_i in range(target):
            i = start_index + local_i
            # ── Envelope / identifiers (unbounded unique fields) ─────
            intuit_tid  = f"tid-{uuid.uuid4().hex[:16]}"
            realm_id    = str(random.randint(100000000, 999999999))
            message_id  = str(uuid.uuid4())
            request_id  = str(uuid.uuid4())
            txn_id      = f"txn-{uuid.uuid4().hex[:12]}"
            jms_ts      = sample_device_timestamp()

            # ── Top-10 driven fields (exact PDF distributions) ────────
            event_type   = sample_device_profile_value('eventType', 'payment')
            app_id       = sample_device_profile_value('appId', 'intuit.secfraud.fraudrisk.riskvendorsvc')
            api_name     = sample_device_profile_value('apiName', 'DEVICE_PROFILE')
            api_result   = sample_device_profile_value('apiResult', 200)
            offering_id  = sample_device_profile_value('offeringId', '')
            org_id       = sample_device_profile_value('orgId', 'v60nf4oj')
            # Long-tail fields — sample_device_with_tail preserves PDF distinct counts
            # for columns where top-N doesn't cover all distribution mass.
            req_duration = sample_device_with_tail('requestDuration', _device_tail_request_duration)
            req_result   = sample_device_profile_value('requestResult', 'success')
            biz_txn      = sample_device_profile_value('businessTransaction', 'Invoice Payment')
            jms_api      = sample_device_profile_value('intuit_jmsbodyapiname', 'DEVICE_PROFILE')
            agent_type   = sample_device_profile_value('agentType', None)
            agent_os     = sample_device_profile_value('agentOs', None)
            browser_lang = sample_device_with_tail('browserLanguage', _device_tail_language)
            browser_str  = sample_device_with_tail('browserString', _device_tail_browser_string)
            match_result = sample_device_profile_value('deviceMatchResult', None)
            igeo         = sample_device_with_tail('inputIpGeo', _device_tail_geo)
            iip_isp      = sample_device_with_tail('inputIpIsp', _device_tail_isp)
            iip_score    = sample_device_with_tail('inputIpScore', _device_tail_score_0_20)
            tgeo         = sample_device_with_tail('trueIpGeo', _device_tail_geo)
            tip_isp      = sample_device_with_tail('trueIpIsp', _device_tail_isp)
            tip_result   = sample_device_profile_value('trueIpResult', None)
            tip_score    = sample_device_with_tail('trueIpScore', _device_tail_score_0_20)
            pgeo         = sample_device_with_tail('proxyIpGeo', _device_tail_geo)
            pip_isp      = sample_device_with_tail('proxyIpIsp', _device_tail_isp)
            p_type       = sample_device_profile_value('proxyType', None)
            pip_score    = sample_device_with_tail('proxyIpScore', _device_tail_score_0_20)
            dscore       = sample_device_with_tail('deviceScore', _device_tail_score_0_20)
            dfp_score    = sample_device_with_tail('deviceFingerprintScore', _device_tail_score_0_20)
            dworst       = sample_device_with_tail('deviceWorstScore', _device_tail_score_neg)
            fuzzy_dscore = sample_device_with_tail('fuzzyDeviceScore', _device_tail_score_0_20)
            tip_worst    = sample_device_with_tail('trueIpWorstScore', _device_tail_score_neg)
            pip_worst    = sample_device_with_tail('proxyIpWorstScore', _device_tail_score_neg)
            dfp_result   = sample_device_profile_value('deviceFingerprintResult', None)
            d_result     = sample_device_profile_value('deviceResult', None)
            pip_result   = sample_device_profile_value('proxyIpResult', None)
            fuzzy_d_res  = sample_device_profile_value('fuzzyDeviceResult', None)
            dns_hosting  = sample_device_profile_value('dnsIpHostingFacility', None)
            proxy_hosting= sample_device_profile_value('proxyIpHostingFacility', None)
            true_hosting = sample_device_profile_value('trueIpHostingFacility', None)
            b_anomaly    = sample_device_profile_value('browserAnomaly', None)
            sr_anomaly   = sample_device_profile_value('screenResAnomaly', None)
            os_anom      = sample_device_profile_value('osAnomaly', None)
            dns_assert   = None  # PDF: always null

            # ── Null-rate driven fields (unbounded unique values) ─────
            eid = sample_device_key_with_tail('exactId', lambda: weighted_choice(exact_ids))
            sid = sample_device_key_with_tail('smartId', lambda: weighted_choice(smart_ids))
            iip = sample_device_key_with_tail('inputIp', lambda: random.choice(input_ips))
            tip = sample_device_key_with_tail('trueIp', lambda: random.choice(true_ips))
            pip = sample_device_key_with_tail('proxyIp', lambda: random.choice(proxy_ips))
            dns_ip = None if device_is_null('dnsIp') else _fresh_ip()

            # user_session_id remains null to match the shared profile.
            user_session_id = None

            # Henry-style join target. In one_to_one mode only the configured
            # matched prefix shares IDs with pmt_txn_fact; extra device rows use
            # non-matching IDs or NULL, so Group C joins do not explode.
            int_id = device_interaction_id_for_row(i)
            session_id = None

            yield (
                intuit_tid, realm_id, message_id, request_id,
                event_type, app_id, api_name, api_result, offering_id,
                txn_id, org_id, user_session_id, req_duration, req_result,
                biz_txn, jms_ts, int_id, session_id, jms_api,
                eid, sid, iip, tip, pip,
                agent_type, agent_os, browser_lang, browser_str, match_result,
                dns_ip, igeo, iip_isp, iip_score,
                tgeo, tip_isp, tip_result, tip_score,
                pgeo, pip_isp, p_type, pip_score,
                dscore, dfp_score, dworst,
                fuzzy_dscore, tip_worst, pip_worst,
                dfp_result, d_result, pip_result, fuzzy_d_res,
                dns_hosting, proxy_hosting, true_hosting,
                b_anomaly, sr_anomaly, os_anom, dns_assert
            )

    parallel_insert(INSERT_SQL, gen_rows, target, "Device profile")


def verify_counts(conn):
    cursor = conn.cursor()
    print("\n\n\n" + "="*60)
    print("  DATA LOAD SUMMARY")
    print("="*60)

    tables = ['pmt_txn_fact', 'deviceprofile_fact']
    for t in tables:
        # Table names from hardcoded list — safe for f-string
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cursor.fetchone()[0]
        print(f"\n  📋 {t} — {cnt:,} rows")

        # Show a full sample row (\G style) so user can see ALL columns
        # Table names from hardcoded list — safe for f-string
        cursor.execute(f"SELECT * FROM {t} LIMIT 1")
        cols = [d[0] for d in cursor.description]
        row = cursor.fetchone()
        if row:
            max_col_len = max(len(c) for c in cols)
            print(f"     *************************** 1. row ***************************")
            for col, val in zip(cols, row):
                print(f"     {col:>{max_col_len}}: {val}")

    print(f"\n{'='*60}")


def validate_synthetic_shape(conn):
    """Optional post-load checks for the customer-validated data shape.

    These queries are intentionally separate from verify_counts because the
    full-scale tables are large. Run with --validate-shape after a realistic
    reload to confirm join fanout and hot-key row counts before benchmarking.
    """
    cursor = conn.cursor()
    print("\n\n\n" + "="*60)
    print("  SYNTHETIC SHAPE VALIDATION")
    print("="*60)
    print(f"  join_model: {JOIN_MODEL}")
    print(f"  expected matched payment rows: {JOIN_MATCHED_PAYMENT_ROWS:,}")

    checks = [
        (
            "payment rows with parsed_interaction_id",
            "SELECT COUNT(*) FROM pmt_txn_fact WHERE parsed_interaction_id IS NOT NULL",
        ),
        (
            "device rows with interaction_id",
            "SELECT COUNT(*) FROM deviceprofile_fact WHERE interaction_id IS NOT NULL",
        ),
        (
            "matched join rows",
            """
            SELECT COUNT(*)
            FROM pmt_txn_fact p
            JOIN deviceprofile_fact d
              ON p.parsed_interaction_id = d.interaction_id
            """,
        ),
        (
            "max device rows per interaction_id",
            """
            SELECT COALESCE(MAX(cnt), 0)
            FROM (
              SELECT interaction_id, COUNT(*) AS cnt
              FROM deviceprofile_fact
              WHERE interaction_id IS NOT NULL
              GROUP BY interaction_id
            ) x
            """,
        ),
        (
            "max payment rows per parsed_interaction_id",
            """
            SELECT COALESCE(MAX(cnt), 0)
            FROM (
              SELECT parsed_interaction_id, COUNT(*) AS cnt
              FROM pmt_txn_fact
              WHERE parsed_interaction_id IS NOT NULL
              GROUP BY parsed_interaction_id
            ) x
            """,
        ),
    ]
    for label, sql in checks:
        started = time.time()
        cursor.execute(sql)
        value = cursor.fetchone()[0]
        elapsed = time.time() - started
        print(f"  {label:<42} {value:>15,}  ({elapsed:.1f}s)")

    hot_key_checks = [
        (
            "pmt max rows per merchant_account_number",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT merchant_account_number, COUNT(*) cnt FROM pmt_txn_fact GROUP BY merchant_account_number) x",
        ),
        (
            "pmt max rows per card_holder_number_sha512",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT card_holder_number_sha512, COUNT(*) cnt FROM pmt_txn_fact WHERE card_holder_number_sha512 IS NOT NULL GROUP BY card_holder_number_sha512) x",
        ),
        (
            "pmt max rows per routing/account",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT check_bank_routing_number, check_bank_account_number_sha512, COUNT(*) cnt FROM pmt_txn_fact WHERE check_bank_routing_number IS NOT NULL AND check_bank_account_number_sha512 IS NOT NULL GROUP BY check_bank_routing_number, check_bank_account_number_sha512) x",
        ),
        (
            "device max rows per exact_id",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT exact_id, COUNT(*) cnt FROM deviceprofile_fact WHERE exact_id IS NOT NULL GROUP BY exact_id) x",
        ),
        (
            "device max rows per smart_id",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT smart_id, COUNT(*) cnt FROM deviceprofile_fact WHERE smart_id IS NOT NULL GROUP BY smart_id) x",
        ),
        (
            "device max rows per input_ip",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT input_ip, COUNT(*) cnt FROM deviceprofile_fact WHERE input_ip IS NOT NULL GROUP BY input_ip) x",
        ),
        (
            "device max rows per true_ip",
            "SELECT COALESCE(MAX(cnt), 0) FROM (SELECT true_ip, COUNT(*) cnt FROM deviceprofile_fact WHERE true_ip IS NOT NULL GROUP BY true_ip) x",
        ),
    ]
    print("\n  Hot-key max row counts")
    for label, sql in hot_key_checks:
        started = time.time()
        cursor.execute(sql)
        value = cursor.fetchone()[0]
        elapsed = time.time() - started
        target = HOT_KEY_ROW_TARGETS.get(label)
        suffix = f" target={target}" if target is not None else ""
        print(f"  {label:<42} {value:>15,}  ({elapsed:.1f}s){suffix}")
    print(f"\n{'='*60}")


def main():
    total = sum(ROW_COUNTS[key] for key in ACTIVE_TABLE_KEYS)
    txn_full = f"{_TXN_FULL_COUNT:,}"
    device_full = f"{_DEVICE_FULL_COUNT:,}"
    table_specs = {
        'pmt_txn': ("pmt_txn_fact", ROW_COUNTS['pmt_txn'], "ihub-cassandra-sync (shared monthly source profile)"),
        'deviceprofile': ("deviceprofile_fact", ROW_COUNTS['deviceprofile'], f"{DEVICE_STREAM_LABEL} (~3M/day avg)"),
    }
    table_lines = "\n".join(
        f"   {name:<22} {rows:>12,}   {label}"
        for key, (name, rows, label) in table_specs.items()
        if key in ACTIVE_TABLE_KEYS
    )
    next_step = "source-table validation / benchmark wiring"

    print(f"""
============================================================
 INTUIT RISK POC — Step 2 of 3: Data Generator
============================================================
 This script generates realistic synthetic data based on
 the POC document event structures and latest customer clarifications.

 In your current architecture, data flows like this:

   Kafka topics → Blackbird/Nighthawk → DynamoDB
                                      → downstream serving / ML scoring

 With TiDB, the two core source tables land together in one place:

   Kafka topics → TiDB (raw events, query at read-time)


 Tables being loaded in this run:

   Table                  Rows            Kafka Source (production)
   ─────────────────────────────────────────────────────────────────
{table_lines}
   ─────────────────────────────────────────────────────────────────
   Total                  {total:>12,}

 Source-profile notes:
   - pmt_txn full-scale target follows shared monthly counts: {txn_full} rows
   - deviceprofile full-scale target follows shared monthly counts: {device_full} rows
   - weekday/weekend skew is modeled for both sources

============================================================
""")

    parser = argparse.ArgumentParser(
        description="Intuit v6 loader — loads pmt_txn_fact and/or deviceprofile_fact at query-compatible PDF-matched distributions."
    )
    parser.add_argument(
        "--table",
        choices=["pmt", "device", "both"],
        default="both",
        help="Which table(s) to load (default: both, sequentially).",
    )
    parser.add_argument(
        "--validate-shape",
        action="store_true",
        help="Run expensive post-load join-fanout and hot-key validation queries.",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Global row index to start generating from. Used by parallel segmented loads.",
    )
    parser.add_argument(
        "--row-count",
        type=int,
        default=None,
        help="Number of rows to generate for the selected table. Defaults to the full table target.",
    )
    parser.add_argument(
        "--skip-verify-counts",
        action="store_true",
        help="Skip end-of-run table counts. Useful when many segmented loaders run concurrently.",
    )
    args = parser.parse_args()
    if args.start_index < 0:
        print("ERROR: --start-index must be >= 0")
        sys.exit(1)
    if args.row_count is not None and args.row_count <= 0:
        print("ERROR: --row-count must be > 0")
        sys.exit(1)
    if args.row_count is not None and args.table == "both":
        print("ERROR: --row-count can only be used with --table pmt or --table device")
        sys.exit(1)
    print("[load_data] Group C join path: parse interaction_id from pmt_txn_fact.risk_profile_token")
    print("[load_data] then join to deviceprofile_fact.interaction_id; user_session_id stays null")
    print(f"[load_data] Group C join model: {JOIN_MODEL}")
    if JOIN_MODEL == "one_to_one":
        print("[load_data] matched interaction_id path is generated 1 payment row -> 1 device row")

    DB_CONFIG = get_db_config()
    conn = pymysql.connect(**DB_CONFIG)
    print("Connected to TiDB.\n")

    print("Generating entity pools...")
    setup_pools()
    if args.start_index:
        # Segmented loaders use the same deterministic entity pools but a
        # different row-generation stream per range. Without this, each segment
        # would replay the same random choices and distort distinct/top-N shape.
        random.seed(RANDOM_SEED + args.start_index)

    if args.table in ("pmt", "both"):
        generate_pmt_txn(
            conn,
            start_index=args.start_index if args.table == "pmt" else 0,
            row_count=args.row_count if args.table == "pmt" else None,
        )
    if args.table in ("device", "both"):
        generate_deviceprofile(
            conn,
            start_index=args.start_index if args.table == "device" else 0,
            row_count=args.row_count if args.table == "device" else None,
        )
    if not args.skip_verify_counts:
        verify_counts(conn)
    if args.validate_shape:
        validate_synthetic_shape(conn)

    conn.close()
    print(f"""
============================================================
 ✅ Data generation complete!

 Next step: {next_step}
============================================================""")


if __name__ == '__main__':
    main()
