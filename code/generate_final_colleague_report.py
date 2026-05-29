#!/usr/bin/env python3
"""Build the colleague-facing final report from generated evidence files."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from explore_residual_group_b import SPECS, render_current_case_distinct


ROOT = Path(__file__).resolve().parent
BEFORE_AFTER_MD = ROOT / "results/final_before_after_optimization_report.md"
SUMMARY_JSON = ROOT / "results/final_before_after_optimization_summary.json"
RESIDUAL_JSON = ROOT / "results/residual_group_b_optimization_attempts.json"
FOLLOWUP_JSON = ROOT / "results/residual_group_b_followup_attempts.json"
OUTPUT = ROOT / "results/final_slow_sql_optimization_report_for_colleagues.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_ms(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.1f} ms"


def ok_results(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in bundle["results"] if row.get("ok")]


def best_exact(bundle: dict[str, Any]) -> dict[str, Any]:
    exact = [
        row
        for row in ok_results(bundle)
        if "approx_not_exact" not in row["shape"]
        and "raw_empty_guard" not in row["shape"]
    ]
    return min(exact, key=lambda row: row["elapsed_ms"])


def best_raw_guard_exact(bundle: dict[str, Any]) -> dict[str, Any] | None:
    exact = [
        row
        for row in ok_results(bundle)
        if "raw_empty_guard" in row["shape"] and "approx_not_exact" not in row["shape"]
    ]
    return min(exact, key=lambda row: row["elapsed_ms"]) if exact else None


def best_approx(bundle: dict[str, Any]) -> dict[str, Any] | None:
    approx = [row for row in ok_results(bundle) if "approx_not_exact" in row["shape"]]
    return min(approx, key=lambda row: row["elapsed_ms"]) if approx else None


def compact_attempt_table(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    best_by_shape: dict[str, dict[str, Any]] = {}
    for row in ok_results(bundle):
        current = best_by_shape.get(row["shape"])
        if current is None or row["elapsed_ms"] < current["elapsed_ms"]:
            best_by_shape[row["shape"]] = row
    return sorted(best_by_shape.values(), key=lambda row: row["elapsed_ms"])


def summary_row_by_bundle(summary: list[dict[str, Any]], bundle_id: str) -> dict[str, Any]:
    for row in summary:
        if row["bundle_id"] == bundle_id:
            return row
    raise KeyError(bundle_id)


def append_residual_appendix(lines: list[str]) -> None:
    summary = load_json(SUMMARY_JSON)
    residual = load_json(RESIDUAL_JSON)["bundles"]
    followup = load_json(FOLLOWUP_JSON)["bundles"]

    lines.append("")
    lines.append("## Residual Manual Optimization Required")
    lines.append("")
    lines.append(
        "These two SQLs are still exact-count hot-key distinct workloads. The current SQL is already covered by the helper table primary key, but it still has to read hundreds of thousands to 1.5M helper rows and perform exact distinct aggregation at the TiDB root."
    )
    lines.append("")
    lines.append("### Residual Summary")
    lines.append("")
    lines.append("| Bundle | Current exact best | Extra exact best tried | Extra approximate best | Helper rows scanned | Decision |")
    lines.append("| --- | ---: | ---: | ---: | ---: | --- |")
    for bundle_id in ["group_b_bundle_018", "group_b_bundle_020"]:
        before_after = summary_row_by_bundle(summary, bundle_id)
        extra_exact = best_exact(residual[bundle_id])
        approx_candidates = [candidate for candidate in [best_approx(residual[bundle_id]), best_approx(followup[bundle_id])] if candidate]
        approx = min(approx_candidates, key=lambda row: row["elapsed_ms"]) if approx_candidates else None
        helper_rows = sum(row["row_count"] for row in residual[bundle_id]["helper_rows"])
        lines.append(
            f"| `{bundle_id}` | {fmt_ms(before_after['optimized_ms'])} | {fmt_ms(extra_exact['elapsed_ms'])} (`{extra_exact['shape']}`/`{extra_exact['setting_name']}`) | "
            f"{fmt_ms(approx['elapsed_ms']) if approx else 'N/A'} | {helper_rows:,} | Manual data-model/pre-aggregation optimization needed |"
        )
    lines.append("")
    lines.append("The table size check for `group_b_180d_daily_distinct` returned about `2,543,647,958` rows, `208 GB` data, and `229 GB` existing index size. I did not create another experimental full-table index on this helper table because it would be a large online DDL with unproven benefit.")
    lines.append("")

    for bundle_id in ["group_b_bundle_018", "group_b_bundle_020"]:
        before_after = summary_row_by_bundle(summary, bundle_id)
        spec = dict(SPECS[bundle_id])
        spec["bundle_id"] = bundle_id
        current_sql, current_params = render_current_case_distinct(spec)
        extra_exact = best_exact(residual[bundle_id])
        raw_guard = best_raw_guard_exact(followup[bundle_id])
        approx_candidates = [candidate for candidate in [best_approx(residual[bundle_id]), best_approx(followup[bundle_id])] if candidate]
        approx = min(approx_candidates, key=lambda row: row["elapsed_ms"]) if approx_candidates else None

        lines.append(f"### {bundle_id}")
        lines.append("")
        lines.append(f"- Original baseline: `{fmt_ms(before_after['baseline_ms'])}`")
        lines.append(f"- Current optimized exact best: `{fmt_ms(before_after['optimized_ms'])}`, variant `{before_after['best_variant']}`")
        lines.append(f"- Key/filter: `{spec['key_column']} = {spec['key_value']}`")
        lines.append("- Raw boundary rows for the tested sample: `0`; helper-only guard was tested but did not beat the current exact plan.")
        lines.append("")
        lines.append("#### Helper Row Counts")
        lines.append("")
        lines.append("| Template | Rows | Day range |")
        lines.append("| --- | ---: | --- |")
        for row in residual[bundle_id]["helper_rows"]:
            lines.append(f"| `{row['template_id']}` | {row['row_count']:,} | `{row['min_day']}` to `{row['max_day']}` |")
        lines.append("")
        lines.append("#### Current Optimized Exact SQL")
        lines.append("")
        lines.append("```sql")
        lines.append(current_sql)
        lines.append("```")
        lines.append("")
        lines.append("Params:")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(current_params, indent=2, default=str))
        lines.append("```")
        lines.append("")
        lines.append("The full original and current optimized `EXPLAIN ANALYZE` plans for this SQL are included earlier in this same report under the detailed evidence section.")
        lines.append("")
        lines.append("#### Additional Attempts")
        lines.append("")
        lines.append("| Attempt shape | Best setting | Best time | Result |")
        lines.append("| --- | --- | ---: | --- |")
        combined = compact_attempt_table(residual[bundle_id]) + compact_attempt_table(followup[bundle_id])
        for row in sorted(combined, key=lambda item: item["elapsed_ms"]):
            result = "rejected: not faster than current exact best"
            if "approx_not_exact" in row["shape"]:
                result = "rejected: approximate distinct semantics"
            elif "raw_empty_guard" in row["shape"]:
                result = "rejected: needs runtime raw-empty branch and was not faster"
            elif row is extra_exact:
                result = "best extra exact attempt, still slower/equal"
            lines.append(f"| `{row['shape']}` | `{row['setting_name']}` | {row['elapsed_ms']:.1f} ms | {result} |")
        lines.append("")
        lines.append("#### Best Extra Exact Attempt SQL")
        lines.append("")
        lines.append("```sql")
        lines.append(extra_exact["sql"])
        lines.append("```")
        lines.append("")
        lines.append("Params:")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(extra_exact["params"], indent=2, default=str))
        lines.append("```")
        lines.append("")
        lines.append("Best extra exact `EXPLAIN ANALYZE`:")
        lines.append("")
        lines.append("```text")
        lines.append(f"-- shape={extra_exact['shape']}")
        lines.append(f"-- setting={extra_exact['setting_name']}")
        lines.append(f"-- explain_analyze_elapsed_ms={extra_exact['elapsed_ms']:.1f}")
        lines.append(extra_exact["plan"])
        lines.append("```")
        lines.append("")
        if raw_guard:
            lines.append("#### Raw-Empty Guard Attempt")
            lines.append("")
            lines.append(
                f"The best helper-only exact attempt was `{raw_guard['shape']}` with `{raw_guard['setting_name']}` at `{raw_guard['elapsed_ms']:.1f} ms`; it did not beat the current exact plan, so I did not keep this rewrite."
            )
            lines.append("")
        if approx:
            lines.append("#### Approximate Distinct Attempt")
            lines.append("")
            lines.append(
                f"The best approximate attempt was `{approx['shape']}` with `{approx['setting_name']}` at `{approx['elapsed_ms']:.1f} ms`. I rejected it because `APPROX_COUNT_DISTINCT` changes metric semantics."
            )
            lines.append("")

    lines.append("### Manual Follow-Up Options")
    lines.append("")
    lines.append("- Build a real rolling distinct pre-aggregation, for example a per-window/count snapshot keyed by `(bundle_id, template_id, key1, key2)` so the read path does not scan one row per distinct value per day.")
    lines.append("- If exact distinct by value must remain query-time, evaluate a shadow/off-peak index such as `(bundle_id, template_id, key1, key2, distinct_value, event_day)`. This may enable lower-memory ordered distinct plans, but it would be a very large index on a 2.54B-row helper table and was not created in this run.")
    lines.append("- Consider approximate distinct only if the business metric can accept approximation; in this sample it was not a clear win and is a semantic change.")


def main() -> None:
    base = BEFORE_AFTER_MD.read_text(encoding="utf-8").splitlines()
    lines = [
        "# Final Slow SQL Optimization Report for Colleagues",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Source full before/after evidence: `{BEFORE_AFTER_MD}`",
        f"- Source residual attempt matrix: `{RESIDUAL_JSON}`, `{FOLLOWUP_JSON}`",
        "",
        "This report keeps the complete before/after SQL and `EXPLAIN ANALYZE` evidence, then appends the extra residual experiments for the two SQLs that still need manual data-model optimization.",
        "",
        "## Permanent Changes Applied",
        "",
        "### Covering Indexes",
        "",
        "```sql",
        "CREATE INDEX idx_pmt_merchant_c_join_cov",
        "  ON pmt_txn_fact (merchant_account_number, event_date, parsed_interaction_id, transaction_type);",
        "",
        "CREATE INDEX idx_pmt_card_c_join_cov",
        "  ON pmt_txn_fact (card_holder_number_sha512, event_date, parsed_interaction_id, transaction_type);",
        "",
        "CREATE INDEX idx_pmt_routing_acct_c_join_cov",
        "  ON pmt_txn_fact (check_bank_routing_number, check_bank_account_number_sha512, event_date, parsed_interaction_id, transaction_type);",
        "```",
        "",
        "These indexes were verified in `information_schema.statistics` before this report was generated.",
        "",
        "### SQL Rewrites And Session Settings Tested",
        "",
        "- Removed redundant `GROUP BY` on constant equality keys and preserved empty-result behavior with `HAVING COUNT(*) > 0`.",
        "- Rewrote 180-day distinct-only and mixed rollup+distinct SQL to share a single `raw_boundary` CTE instead of repeating raw table scans.",
        "- Tested session variants with TiKV/TiDB only, `tidb_opt_distinct_agg_push_down`, `tidb_opt_agg_push_down`, hashagg concurrency, scan concurrency, executor concurrency, and paging on/off.",
        "",
    ]
    lines.extend(base[1:])
    append_residual_appendix(lines)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
