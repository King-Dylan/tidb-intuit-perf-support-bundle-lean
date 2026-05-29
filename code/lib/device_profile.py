"""
Device-fingerprint source-of-truth profile copied from the Intuit materials.

Scope:
  - monthly event counts / approximate size from 2025-11 to 2026-04
  - field-level null/distinct/top10-frequency values visible in the shared
    column-profile screenshot (~90,821 sampled rows)

Important:
  - This file is intentionally faithful to the provided artifacts.
  - Values here come directly from the PDF's field profile table; null rates
    and top-N percentages are encoded as seen in the screenshot.
"""

# ──────────────────────────────────────────────────────────────────────────
# Per-month row counts (from the shared dashboard screenshot)
# ──────────────────────────────────────────────────────────────────────────
DEVICE_MONTHLY_COUNTS = {
    "2025-11": 45_606_999,
    "2025-12": 50_848_722,
    "2026-01": 70_500_405,
    "2026-02": 80_194_367,
    "2026-03": 90_668_467,
    "2026-04": 27_925_870,  # partial month, ~10 days
}

DEVICE_MONTHLY_SIZE_GB = {
    "2025-11": 11.64,
    "2025-12": 12.98,
    "2026-01": 17.99,
    "2026-02": 20.46,
    "2026-03": 23.14,
    "2026-04": 7.13,
}

# High-level descriptors (still used by the loader summary output)
DEVICE_STREAM_LABEL = "platform-identity-deviceprofile"
DEVICE_HISTORY_DAYS = 161  # 2025-11-01 → 2026-04-10

# Weekday/weekend weight shape (keep for consistency with transaction profile)
DEVICE_DAY_WEIGHTS = {
    0: 1.20,  # Monday
    1: 1.15,  # Tuesday
    2: 1.10,  # Wednesday
    3: 1.10,  # Thursday
    4: 1.20,  # Friday
    5: 0.70,  # Saturday
    6: 0.65,  # Sunday
}

# Legacy compat: AVG_DAILY_EVENTS is now derived from the exact monthly counts
DEVICE_AVG_DAILY_EVENTS = int(sum(DEVICE_MONTHLY_COUNTS.values()) / DEVICE_HISTORY_DAYS)


# ──────────────────────────────────────────────────────────────────────────
# Per-column profile — mirrors the PDF column-profile table, keyed by field
# name exactly as seen in the screenshot (camelCase, matches schema)
# ──────────────────────────────────────────────────────────────────────────
DEVICE_FIELD_PROFILES = {
    # ── Identity / envelope ─────────────────────────────────────────────
    "intuitTid": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 90807,
        # ~100% unique (UUID-like)
    },
    "realmId": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 90000,  # no exact distinct shown on profile; realmId is effectively per-event
    },
    "messageId": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 90821,
    },
    "requestId": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 90821,
    },
    "eventType": {
        "count": 90817, "null_count": 4, "null_pct": 0.0, "distinct": 1,
        "top10_freq": {
            "payment": 1.0,
        },
    },
    "appId": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 8,
        "top10_freq": {
            "intuit.secfraud.fraudrisk.riskvendorsvc":            0.639,
            "intuit.secfraud.fraudrisk.riskassessmentsvc":        0.356,
            "intuit.moneymovementpayments.underwritingservicev4": 0.003,
            "intuit.moneymovementpayments.realtimerulesengine":   0.001,
            "intuit.account.risk.moneyriskatosvc":                0.001,
            "intuit.money.risk.accounts.risk":                    0.0001,
            "intuit.money.risk.cgriskassessment":                 0.0001,
            "intuit.money.finrisk.unifiedriskdatasvc":            0.0001,
        },
    },
    "apiName": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 1,
        "top10_freq": {
            "DEVICE_PROFILE": 1.0,
        },
    },
    "apiResult": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 1,
        "top10_freq": {
            200: 1.0,
        },
    },
    "offeringId": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 8,
        "top10_freq": {
            "":                                                 0.969,
            "intuit.sales.core.b2bbillpayservice":              0.013,
            "intuit.money.moneyorch.pymtprocessingservice":     0.011,
            "intuit.sales.customerexp.salescheckoutservice":    0.003,
            "intuit.identity.manage.account":                   0.001,
            "intuit.sbe.salsa.platform":                        0.001,
            "intuit.fms.intuitlending":                         0.0001,
            "145258680168756101":                               0.0001,
            "intuit.money.salestransactionservice":             0.0001,
        },
    },
    "transactionId": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 90807,
    },
    "orgId": {
        "count": 90817, "null_count": 4, "null_pct": 0.0, "distinct": 1,
        "top10_freq": {
            "v60nf4oj": 1.0,
        },
    },

    # ── Join / linkage keys ────────────────────────────────────────────
    # CRITICAL: the shared profile shows this as 100% null. Henry clarified
    # that production does not join on this field; the loader keeps it null.
    "userSessionId": {
        "count": 0, "null_count": 90821, "null_pct": 100.0, "distinct": 0,
    },
    "interactionId": {
        "count": 0, "null_count": 90821, "null_pct": 100.0, "distinct": 0,
    },

    # ── Request / biz ──────────────────────────────────────────────────
    "requestDuration": {
        "count": 90817, "null_count": 4, "null_pct": 0.0, "distinct": 266,
        "top10_freq": {
            "7":  0.076,
            "8":  0.076,
            "9":  0.041,
            "38": 0.039,
            "36": 0.038,
            "37": 0.038,
            "6":  0.038,
            "35": 0.038,
            "39": 0.037,
            "34": 0.036,
        },
    },
    "requestResult": {
        "count": 90817, "null_count": 4, "null_pct": 0.0, "distinct": 1,
        "top10_freq": {
            "success": 1.0,
        },
    },
    "businessTransaction": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 7,
        "top10_freq": {
            "Invoice Payment":       0.582,
            "CP Invoice Payment":    0.294,
            "Merchant Payment":      0.091,
            "Bill Pay":              0.025,
            "Merchant Onboarding":   0.004,
            "Merchant Onboarding ":  0.003,  # trailing space observed in PDF
            "signin":                0.0001,
        },
    },
    "intuit_jmsbodyapiname": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 1,
        "top10_freq": {
            "DEVICE_PROFILE": 1.0,
        },
    },

    # ── Device identity ────────────────────────────────────────────────
    "exactId": {
        "count": 65356, "null_count": 25465, "null_pct": 28.1, "distinct": 64754,
        "top10_freq": {
            None: 0.281,
            "b31ad5c6ae5e4538908505ac0b30c406": 0.0001,
            "31e04c7aac0e47059f0342b27108e7e4": 0.0001,
            "aeb2710d142b42ccab34892394560aab": 0.0001,
            "b25548e5b35a4f4f95bcd2245c7e302a": 0.0001,
            "3196d683b95a420394a36143f1613f12": 0.0001,
            "767199c2360746738aa5632b44b4b683": 0.0001,
            "48451809d02c46169caf0e8511e154f9": 0.0001,
            "f8c466ca58094c7ebdbed6892b5f7e1a": 0.0001,
            "cdb0d07f3bda49ca8ad3876c1c57f9f1": 0.0001,
        },
    },
    "smartId": {
        "count": 65356, "null_count": 25465, "null_pct": 28.1, "distinct": 61209,
        "top10_freq": {
            None: 0.281,
            "7fc2e799217248938cbdf5d20d98db3d": 0.001,
            "5b8aa9e575604d2d8298bd4e6e3efc1a": 0.001,
            "3b452b7fd9bd4ddcb27e0067970d6a1a": 0.001,
            "4c2f38e0b4e44bd2a9550ab38de1c82e": 0.001,
            "1fac3ebe170142908de756031849b79d": 0.001,
            "0e04d75e1da545ac88690aec75135b12": 0.001,
            "b23c12ddc64e4571ab2ab34755d127d4": 0.001,
            "2222fa4682e8429498969e3568a2941a": 0.001,
            "6f15672911284cb2a7ae049639e7edfd": 0.0001,
        },
    },

    # ── Network fingerprints ───────────────────────────────────────────
    "inputIp": {
        "count": 58425, "null_count": 32396, "null_pct": 35.7, "distinct": 52279,
        "top10_freq": {
            None: 0.357,
            "72.153.231.69": 0.002,
            "74.179.68.52": 0.002,
            "135.232.19.45": 0.001,
            "9.169.124.16": 0.001,
            "74.179.70.43": 0.001,
            "72.153.153.63": 0.001,
            "72.153.231.49": 0.001,
            "9.169.124.5": 0.001,
            "135.232.20.92": 0.001,
        },
    },
    "trueIp": {
        "count": 62348, "null_count": 28473, "null_pct": 31.4, "distinct": 56499,
        "top10_freq": {
            None: 0.314,
            "72.153.231.69": 0.002,
            "74.179.68.52": 0.002,
            "135.232.19.45": 0.001,
            "9.169.124.16": 0.001,
            "74.179.70.43": 0.001,
            "72.153.153.63": 0.001,
            "72.153.231.49": 0.001,
            "9.169.124.5": 0.001,
            "135.232.20.92": 0.001,
        },
    },
    "proxyIp": {
        "count": 7271, "null_count": 83550, "null_pct": 92.0, "distinct": 6232,
        "top10_freq": {
            None: 0.921,
            "136.179.18.133": 0.0001,
            "146.75.234.49": 0.0001,
            "65.221.106.113": 0.0001,
            "146.75.164.252": 0.0001,
            "207.207.176.17": 0.0001,
            "207.207.179.23": 0.0001,
            "146.75.136.1": 0.0001,
            "146.75.248.0": 0.0001,
            "207.207.179.22": 0.0001,
        },
    },
    "dnsIp": {
        "count": 58879, "null_count": 31942, "null_pct": 35.2, "distinct": 13416,
    },

    # ── Agent info ─────────────────────────────────────────────────────
    "agentType": {
        "count": 65297, "null_count": 25524, "null_pct": 28.1, "distinct": 3,
        "top10_freq": {
            "browser_computer": 0.536,
            None:               0.282,
            "browser_mobile":   0.181,
            "agent_mobile":     0.001,
        },
    },
    "agentOs": {
        "count": 42, "null_count": 90779, "null_pct": 100.0, "distinct": 2,
        "top10_freq": {
            None:      0.9995,
            "iOS":     0.0003,
            "Android": 0.0002,
        },
    },
    "browserLanguage": {
        "count": 62908, "null_count": 27913, "null_pct": 30.7, "distinct": 864,
        "top10_freq": {
            "en-US,en;q=0.9":                                0.609,
            None:                                            0.308,
            "en-US":                                         0.010,
            "en-US,en;q=0.9,en;q=0.9,q=0.8":                 0.009,
            "en-US,en;q=0.9,es;q=0.8":                       0.006,
            "en-CA,en-US;q=0.9,en;q=0.8":                    0.005,
            "en-GB,en-US;q=0.9,en;q=0.8":                    0.005,
            "en-GB,en;q=0.9":                                0.003,
            "en-US,en;q=0.9,en-CA;q=0.8":                    0.003,
            "en-US,en;q=0.5":                                0.002,
        },
    },
    "browserString": {
        "count": 63062, "null_count": 27759, "null_pct": 30.6, "distinct": 1629,
        "top10_freq": {
            None: 0.306,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36":           0.103,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36":           0.076,
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Mobile/15E148 Safari/604.1": 0.056,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0": 0.052,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0": 0.044,
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36":    0.034,
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148":             0.025,
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36":    0.017,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36":           0.014,
        },
    },

    # ── Device-match result / scores ───────────────────────────────────
    "deviceMatchResult": {
        "count": 65359, "null_count": 25462, "null_pct": 28.0, "distinct": 3,
        "top10_freq": {
            "success":              0.569,
            None:                   0.281,
            "new_device":           0.150,
            "not_enough_attribs":   0.0001,
        },
    },

    # ── IP-derived attributes ──────────────────────────────────────────
    "inputIpGeo": {
        "count": 58422, "null_count": 32399, "null_pct": 35.7, "distinct": 138,
        "top10_freq": {
            "US":  0.590, None: 0.357, "CA": 0.027, "GB": 0.007,
            "PH":  0.002, "IN": 0.002, "MX": 0.001, "AU": 0.001,
            "DE":  0.001, "NL": 0.001,
        },
    },
    "inputIpIsp": {
        "count": 58367, "null_count": 32454, "null_pct": 35.7, "distinct": 2606,
        "top10_freq": {
            None:                                        0.357,
            "comcast":                                   0.095,
            "at&t enterprises  llc":                     0.066,
            "verizon":                                   0.051,
            "microsoft corporation":                     0.051,
            "charter communications inc":                0.047,
            "t-mobile":                                  0.025,
            "charter communications llc":                0.023,
            "cox communications inc.":                   0.020,
            "space exploration technologies corporation":0.012,
        },
    },
    "inputIpScore": {
        "count": 58229, "null_count": 32592, "null_pct": 35.9, "distinct": 67,
        "top10_freq": {
            None:  0.359, "0": 0.203, "6": 0.079, "1": 0.065,
            "2":   0.042, "3": 0.040, "4": 0.034, "5": 0.033,
            "7":   0.015, "8": 0.014,
        },
    },
    "trueIpGeo": {
        "count": 62348, "null_count": 28473, "null_pct": 31.4, "distinct": 141,
        "top10_freq": {
            "US":  0.630, None: 0.314, "CA": 0.028, "GB": 0.007,
            "PH":  0.003, "IN": 0.002, "MX": 0.001, "AU": 0.001,
            "PK":  0.001, "NL": 0.001,
        },
    },
    "trueIpIsp": {
        "count": 62292, "null_count": 28529, "null_pct": 31.4, "distinct": 2789,
        "top10_freq": {
            None:                                        0.315,
            "comcast":                                   0.110,
            "at&t enterprises  llc":                     0.075,
            "verizon":                                   0.059,
            "charter communications inc":                0.054,
            "microsoft corporation":                     0.049,
            "t-mobile":                                  0.027,
            "charter communications llc":                0.027,
            "cox communications inc.":                   0.024,
            "space exploration technologies corporation":0.014,
        },
    },
    "trueIpResult": {
        "count": 62348, "null_count": 28473, "null_pct": 31.4, "distinct": 2,
        "top10_freq": {
            "success":   0.684,
            None:        0.314,
            "not found": 0.002,
        },
    },
    "trueIpScore": {
        "count": 62159, "null_count": 28662, "null_pct": 31.6, "distinct": 58,
        "top10_freq": {
            None:  0.316, "0": 0.224, "6": 0.085, "1": 0.071,
            "2":   0.047, "3": 0.047, "4": 0.039, "5": 0.037,
            "7":   0.016, "8": 0.016,
        },
    },

    # ── Proxy attributes (92% null) ────────────────────────────────────
    "proxyIpGeo": {
        "count": 7271, "null_count": 83550, "null_pct": 92.0, "distinct": 54,
        "top10_freq": {
            None: 0.921, "US": 0.075, "CA": 0.002, "GB": 0.0001,
            "DE": 0.0001, "PH": 0.0001, "IN": 0.0001,
            "AU": 0.0001, "BR": 0.0001, "MX": 0.0001,
        },
    },
    "proxyIpIsp": {
        "count": 7270, "null_count": 83551, "null_pct": 92.0, "distinct": 274,
        "top10_freq": {
            None:                        0.921,
            "at&t enterprises  llc":     0.017,
            "t-mobile":                  0.014,
            "fastly  inc.":              0.012,
            "leaseweb usa  inc.":        0.007,
            "zscaler  inc.":             0.005,
            "cloudflare":                0.003,
            "amazon.com  inc.":          0.003,
            "m247 europe srl":           0.002,
            "akamai technologies  inc.": 0.002,
        },
    },
    "proxyType": {
        "count": 7271, "null_count": 83550, "null_pct": 92.0, "distinct": 4,
        "top10_freq": {
            None:                  0.921,
            "transparent":         0.038,
            "apple private relay": 0.017,
            "anonymous":           0.014,
            "hidden":              0.011,
        },
    },
    "proxyIpScore": {
        "count": 7269, "null_count": 83552, "null_pct": 92.0, "distinct": 64,
        "top10_freq": {
            None:  0.921, "0": 0.005, "6": 0.005, "16": 0.005,
            "1":   0.005, "5": 0.004, "14": 0.004, "13": 0.004,
            "17":  0.004, "12": 0.003,
        },
    },

    # ── Device scoring ─────────────────────────────────────────────────
    "deviceScore": {
        "count": 51777, "null_count": 39044, "null_pct": 43.0, "distinct": 23,
        "top10_freq": {
            None:  0.431, "0": 0.274, "3": 0.068, "1": 0.060,
            "5":   0.046, "6": 0.045, "2": 0.041, "4": 0.034,
            "8":   0.0001, "-5": 0.0001,
        },
    },
    "deviceFingerprintScore": {
        "count": 58846, "null_count": 31975, "null_pct": 35.2, "distinct": 19,
        "top10_freq": {
            None:  0.353, "6": 0.248, "5": 0.235, "0": 0.038,
            "4":   0.037, "1": 0.029, "3": 0.029, "2": 0.026,
            "-6":  0.001, "-5": 0.001,
        },
    },
    "deviceWorstScore": {
        "count": 51777, "null_count": 39044, "null_pct": 43.0, "distinct": 18,
        "top10_freq": {
            "0":   0.564, None: 0.431, "-1": 0.002, "-6": 0.001,
            "-4":  0.0001, "-7": 0.0001, "-5": 0.0001,
            "-9":  0.0001, "-10": 0.0001, "-3": 0.0001,
        },
    },
    "fuzzyDeviceScore": {
        "count": 58793, "null_count": 32028, "null_pct": 35.3, "distinct": 32,
        "top10_freq": {
            None:  0.352, "0": 0.309, "6": 0.080, "1": 0.064,
            "3":   0.061, "5": 0.050, "2": 0.044, "4": 0.036,
            "8":   0.001, "7": 0.001,
        },
    },
    "trueIpWorstScore": {
        "count": 62159, "null_count": 28662, "null_pct": 31.6, "distinct": 99,
        "top10_freq": {
            None: 0.316, "0": 0.288, "-1": 0.121, "-6": 0.046,
            "-7": 0.029, "-5": 0.027, "-8": 0.019,
            "-9": 0.018, "-4": 0.018, "-2": 0.013,
        },
    },
    "proxyIpWorstScore": {
        "count": 7269, "null_count": 83552, "null_pct": 92.0, "distinct": 101,
        "top10_freq": {
            None:  0.921, "0": 0.005, "-10": 0.004, "-13": 0.004,
            "-100":0.004, "-11": 0.003, "-12": 0.003, "-9": 0.003,
            "-8":  0.003, "-5": 0.002,
        },
    },

    # ── Result / flag columns ──────────────────────────────────────────
    "deviceFingerprintResult": {
        "count": 59265, "null_count": 31556, "null_pct": 34.7, "distinct": 2,
        "top10_freq": {
            "success":   0.647,
            None:        0.349,
            "not found": 0.004,
        },
    },
    "deviceResult": {
        "count": 65356, "null_count": 25465, "null_pct": 28.0, "distinct": 2,
        "top10_freq": {
            "success":   0.569,
            None:        0.281,
            "not found": 0.151,
        },
    },
    "proxyIpResult": {
        "count": 7271, "null_count": 83550, "null_pct": 92.0, "distinct": 2,
        "top10_freq": {
            None:        0.921,
            "success":   0.079,
            "not found": 0.0001,
        },
    },
    "fuzzyDeviceResult": {
        "count": 65356, "null_count": 25465, "null_pct": 28.0, "distinct": 2,
        "top10_freq": {
            "success":   0.648,
            None:        0.281,
            "not found": 0.072,
        },
    },
    "dnsIpHostingFacility": {
        "count": 4497, "null_count": 86324, "null_pct": 95.0, "distinct": 1,
        "top10_freq": {
            None:   0.952,
            "true": 0.048,
        },
    },
    "proxyIpHostingFacility": {
        "count": 1693, "null_count": 89128, "null_pct": 98.1, "distinct": 1,
        "top10_freq": {
            None:   0.981,
            "true": 0.019,
        },
    },
    "trueIpHostingFacility": {
        "count": 5658, "null_count": 85163, "null_pct": 93.8, "distinct": 1,
        "top10_freq": {
            None:   0.937,
            "true": 0.063,
        },
    },

    # ── Anomaly columns (almost always null) ───────────────────────────
    "browserAnomaly": {
        "count": 42, "null_count": 90779, "null_pct": 100.0, "distinct": 1,
        "top10_freq": {
            None:  1.0,
            "yes": 0.0001,
        },
    },
    "screenResAnomaly": {
        "count": 2909, "null_count": 87912, "null_pct": 96.8, "distinct": 1,
        "top10_freq": {
            None:  0.968,
            "yes": 0.032,
        },
    },
    "osAnomaly": {
        "count": 5643, "null_count": 85178, "null_pct": 93.8, "distinct": 1,
        "top10_freq": {
            None:  0.935,
            "yes": 0.065,
        },
    },
    "dnsIpAssertHistory": {
        "count": 0, "null_count": 90821, "null_pct": 100.0, "distinct": 0,
    },

    # ── jmsTimestamp is handled by timestamp sampler (not a fixed-top10 field)
    "jmsTimestamp": {
        "count": 90821, "null_count": 0, "null_pct": 0.0, "distinct": 90816,
    },
}


# ──────────────────────────────────────────────────────────────────────────
# Convenience: which columns the loader should populate via
# sample_profile_value() (dict-top10-driven) vs which need ad-hoc generation.
# Listed here explicitly for auditability.
# ──────────────────────────────────────────────────────────────────────────
DEVICE_PROFILE_DRIVEN_COLUMNS = set([
    "eventType", "appId", "apiName", "apiResult", "offeringId", "orgId",
    "requestDuration", "requestResult", "businessTransaction",
    "intuit_jmsbodyapiname", "agentType", "agentOs",
    "browserLanguage", "browserString", "deviceMatchResult",
    "inputIpGeo", "inputIpIsp", "inputIpScore",
    "trueIpGeo", "trueIpIsp", "trueIpResult", "trueIpScore",
    "proxyIpGeo", "proxyIpIsp", "proxyType", "proxyIpScore",
    "deviceScore", "deviceFingerprintScore", "deviceWorstScore",
    "fuzzyDeviceScore", "trueIpWorstScore", "proxyIpWorstScore",
    "deviceFingerprintResult", "deviceResult", "proxyIpResult",
    "fuzzyDeviceResult", "dnsIpHostingFacility", "proxyIpHostingFacility",
    "trueIpHostingFacility", "browserAnomaly", "screenResAnomaly",
    "osAnomaly",
])
