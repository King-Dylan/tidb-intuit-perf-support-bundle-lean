#!/usr/bin/env python3
"""
Query-template extraction for the Intuit risk demo.

This module reads the shared PDF query catalog, extracts the Group A / B / C SQL
examples, and converts them into reusable parameterized templates for the event
benchmark harness.

Why extract instead of hand-maintain:
  - the PDF already contains the authoritative query families
  - it keeps the template layer aligned to the customer material
  - Group C can still be rewritten to Henry's clarified join path

Default behavior:
  - Group A and Group B stay close to the PDF SQL
  - Group C is rewritten from the literal PDF join to the Henry-style join:
      SUBSTRING_INDEX(p.risk_profile_token, ':', -1) = d.interaction_id
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
import subprocess
from collections import Counter


DEFAULT_PDF_PATH = Path("/Users/ravishpatel/Downloads/TiDB Data Modernization Demo [External].pdf")
DEFAULT_CACHE_PATH = Path(__file__).resolve().parent / "query_templates_cache.json"

GROUP_HEADINGS = {
    "A": "Group A: Transaction Only Table Queries",
    "B": "Group B: Device Only Table Queries",
    "C": "Group C: Join Queries",
}

PDF_LITERAL_BINDINGS = [
    ("merchant_account_number", "'123456789'"),
    ("card_holder_number_sha512", "'abc123sha512'"),
    ("check_bank_routing_number", "'021000021'"),
    ("check_bank_account_number_sha512", "'def456sha512'"),
    ("smart_id", "'smart_abc123'"),
    ("input_ip", "'192.168.1.1'"),
    ("true_ip", "'10.0.0.1'"),
    ("exact_id", "'exact_xyz789'"),
]

GROUP_C_PDF_JOIN = "p.risk_profile_token = d.session_id"
GROUP_C_HENRY_JOIN = "SUBSTRING_INDEX(p.risk_profile_token, ':', -1) = d.interaction_id"


@dataclass(frozen=True)
class QueryTemplate:
    group: str
    index: int
    sql: str
    param_names: tuple[str, ...]
    source: str = "pdf"

    @property
    def template_id(self) -> str:
        return f"{self.group.lower()}_{self.index:04d}"

    def render(self, bindings: dict[str, object]) -> tuple[str, tuple[object, ...]]:
        values = []
        for name in self.param_names:
            if name not in bindings:
                raise KeyError(f"Missing binding for {name!r} in {self.template_id}")
            values.append(bindings[name])
        return self.sql, tuple(values)


def _extract_pdf_text(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    try:
        proc = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("pdftotext is not installed in this environment") from exc
    return proc.stdout


def _save_cache(templates: list[QueryTemplate], cache_path: Path) -> None:
    payload = {
        "templates": [
            {
                "group": tmpl.group,
                "index": tmpl.index,
                "sql": tmpl.sql,
                "param_names": list(tmpl.param_names),
                "source": tmpl.source,
            }
            for tmpl in templates
        ]
    }
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_cache(cache_path: Path) -> list[QueryTemplate]:
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    return [
        QueryTemplate(
            group=item["group"],
            index=item["index"],
            sql=item["sql"],
            param_names=tuple(item["param_names"]),
            source=item.get("source", "pdf-cache"),
        )
        for item in payload["templates"]
    ]


def _slice_group_text(pdf_text: str, group: str) -> str:
    heading = GROUP_HEADINGS[group]
    start = pdf_text.find(heading)
    if start == -1:
        raise ValueError(f"Could not find heading {heading!r}")

    if group == "A":
        end = pdf_text.find(GROUP_HEADINGS["B"], start)
    elif group == "B":
        end = pdf_text.find(GROUP_HEADINGS["C"], start)
    else:
        end = pdf_text.find("Pre-Aggregated Wide-Column Test", start)
        if end == -1:
            end = len(pdf_text)

    if end == -1:
        end = len(pdf_text)
    section = pdf_text[start:end]
    first_select = section.find("SELECT ")
    if first_select != -1:
        section = section[first_select:]
    return section


def _extract_queries(group_text: str) -> list[str]:
    queries = re.findall(r"(SELECT .*?;)", group_text, flags=re.S)
    cleaned = []
    seen = set()
    for q in queries:
        sql = " ".join(q.replace("\f", " ").split())
        if sql not in seen:
            seen.add(sql)
            cleaned.append(sql)
    return cleaned


def _parameterize_query(sql: str, *, group: str, use_henry_group_c: bool) -> QueryTemplate:
    param_names: list[str] = []
    parametrized = sql
    sentinel = "__CODEX_PARAM__"

    # Normalize a small number of malformed PDF expressions into TiDB-valid SQL.
    parametrized = re.sub(r"NOW\(\)\s+INTERVAL\s+(\d+)\s+DAY", r"NOW() - INTERVAL \1 DAY", parametrized)

    if group == "C" and use_henry_group_c:
        parametrized = parametrized.replace(GROUP_C_PDF_JOIN, GROUP_C_HENRY_JOIN)

    for param_name, literal in PDF_LITERAL_BINDINGS:
        if literal in parametrized:
            count = parametrized.count(literal)
            parametrized = parametrized.replace(literal, sentinel)
            param_names.extend([param_name] * count)

    # Escape literal percent signs in SQL patterns such as LIKE '%success%'
    # before turning our internal sentinels into DB-API placeholders.
    parametrized = parametrized.replace("%", "%%").replace(sentinel, "%s")

    return QueryTemplate(
        group=group,
        index=0,
        sql=parametrized,
        param_names=tuple(param_names),
    )


def load_query_templates(
    pdf_path: Path | str = DEFAULT_PDF_PATH,
    *,
    use_henry_group_c: bool = True,
    cache_path: Path | str = DEFAULT_CACHE_PATH,
) -> list[QueryTemplate]:
    pdf_path = Path(pdf_path)
    cache_path = Path(cache_path)

    try:
        pdf_text = _extract_pdf_text(pdf_path)
    except (FileNotFoundError, RuntimeError):
        if cache_path.exists():
            return _load_cache(cache_path)
        raise

    templates: list[QueryTemplate] = []
    for group in ("A", "B", "C"):
        group_text = _slice_group_text(pdf_text, group)
        queries = _extract_queries(group_text)
        for idx, query in enumerate(queries, start=1):
            tmpl = _parameterize_query(query, group=group, use_henry_group_c=use_henry_group_c)
            templates.append(
                QueryTemplate(
                    group=tmpl.group,
                    index=idx,
                    sql=tmpl.sql,
                    param_names=tmpl.param_names,
                    source=tmpl.source,
                )
            )
    _save_cache(templates, cache_path)
    return templates


def group_templates(
    pdf_path: Path | str = DEFAULT_PDF_PATH,
    *,
    use_henry_group_c: bool = True,
    cache_path: Path | str = DEFAULT_CACHE_PATH,
) -> dict[str, list[QueryTemplate]]:
    grouped = {"A": [], "B": [], "C": []}
    for tmpl in load_query_templates(
        pdf_path,
        use_henry_group_c=use_henry_group_c,
        cache_path=cache_path,
    ):
        grouped[tmpl.group].append(tmpl)
    return grouped


def summarize_templates(templates: list[QueryTemplate]) -> dict[str, object]:
    by_group = Counter(t.group for t in templates)
    params = Counter()
    for tmpl in templates:
        params.update(tmpl.param_names)
    return {
        "total": len(templates),
        "by_group": dict(by_group),
        "param_usage": dict(params),
    }


if __name__ == "__main__":
    templates = load_query_templates()
    summary = summarize_templates(templates)
    print("Template summary")
    print(f"  total: {summary['total']}")
    for group, count in summary["by_group"].items():
        print(f"  group {group}: {count}")
    print("  param usage:")
    for name, count in sorted(summary["param_usage"].items()):
        print(f"    {name}: {count}")
    print("\nSample templates:")
    for tmpl in templates[:3]:
        print(f"[{tmpl.template_id}] params={tmpl.param_names}")
        print(tmpl.sql)
        print()
