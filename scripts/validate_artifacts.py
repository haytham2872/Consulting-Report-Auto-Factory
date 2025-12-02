"""Validate that generated markdown aligns with the JSON summary and that chart files exist."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable

from reporting.rounding import format_currency, format_percent


KPI_FIELDS = {
    "total_revenue": format_currency,
    "average_order_value": format_currency,
    "churn_rate": format_percent,
    "ltv_mean": format_currency,
}


CATEGORY_FIELD = "top_categories"


class ValidationError(RuntimeError):
    pass


def _load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_kpis(markdown: str, kpis: Dict[str, float]) -> Iterable[str]:
    failures = []
    for field, formatter in KPI_FIELDS.items():
        if field not in kpis:
            failures.append(f"Missing KPI in JSON: {field}")
            continue
        expected = formatter(kpis[field])
        if expected not in markdown:
            failures.append(f"Expected KPI '{field}' formatted as '{expected}' not found in markdown")
    return failures


def _check_categories(markdown: str, categories: Dict[str, float]) -> Iterable[str]:
    failures = []
    for name, revenue in categories.items():
        expected = f"{name}: {format_currency(revenue)}"
        if expected not in markdown:
            failures.append(f"Category line '{expected}' not found in markdown")
    return failures


def _check_charts(markdown: str, chart_paths: Iterable[str]) -> Iterable[str]:
    failures = []
    for chart in chart_paths:
        if chart not in markdown:
            failures.append(f"Chart reference '{chart}' missing from markdown")
        if not Path(chart).exists():
            failures.append(f"Chart file missing on disk: {chart}")
    return failures


def _check_metadata(markdown: str, metadata: Dict[str, str]) -> Iterable[str]:
    failures = []
    for key, value in metadata.items():
        if value and str(value) not in markdown:
            failures.append(f"Provenance field '{key}' with value '{value}' missing from markdown")
    return failures


def validate(summary_path: Path, markdown_paths: Iterable[Path]) -> None:
    data = json.loads(summary_path.read_text())
    kpis = data.get("kpis", {})
    categories = {item["category"]: item["revenue"] for item in data.get(CATEGORY_FIELD, []) if "category" in item}
    chart_refs = [c.get("path") for c in data.get("charts", []) if "path" in c]
    metadata = data.get("metadata", {})

    failures = []
    for md_path in markdown_paths:
        markdown = _load_markdown(md_path)
        failures.extend(_check_kpis(markdown, kpis))
        failures.extend(_check_categories(markdown, categories))
        failures.extend(_check_charts(markdown, chart_refs))
        failures.extend(_check_metadata(markdown, metadata))

    if failures:
        raise ValidationError("\n".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated artifacts against JSON summary")
    parser.add_argument("summary", type=Path, help="Path to analysis_summary.json")
    parser.add_argument("markdown", nargs="+", type=Path, help="Markdown files to validate")
    args = parser.parse_args()

    validate(args.summary, args.markdown)


if __name__ == "__main__":
    main()
