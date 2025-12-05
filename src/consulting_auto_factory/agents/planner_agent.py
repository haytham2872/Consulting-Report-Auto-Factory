from __future__ import annotations

import json
from typing import Dict

from .. import llm_client
from ..config import SchemaInfo
from ..models import AnalysisPlan, PlanStep


PLAN_PROMPT = """You are a data analytics planner creating analysis plans for tabular datasets.

Given a business brief and compact schemas (with column types and statistics), propose a concise JSON plan.

CRITICAL RULES:
1. Base your plan ONLY on the column types and statistics provided - make NO assumptions about what the data represents
2. Use type-driven analysis selection:
   - For 'datetime' columns (role: time) → time-series trends, temporal patterns
   - For 'numeric' columns (role: measure) → distributions, summaries, min/max/mean analysis
   - For 'categorical' columns (role: dimension) → group-by aggregations, top categories
   - For 'text' columns → generally skip or simple counts
3. Design 3-5 generic analysis steps that work for ANY tabular dataset
4. Keep step descriptions concise (1 sentence each)
5. Do NOT use domain-specific terms (revenue, customers, orders) unless they appear explicitly in the brief
6. Prefer operations like: "Compute summary statistics for measure columns", "Analyze trends over time columns", "Group measures by top dimensions"

Return ONLY valid JSON with this exact structure:
{
  "title": "brief analysis title",
  "objectives": ["objective 1", "objective 2"],
  "steps": [
    {
      "id": "1",
      "description": "concise generic description",
      "required_columns": ["col1", "col2"],
      "output_type": "kpi_table"
    }
  ]
}
"""


class PlannerAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.3) -> None:
        self.model = model
        self.temperature = temperature

    def _format_schema_compact(self, schema_info: Dict[str, SchemaInfo]) -> str:
        """Format schema in a compact, token-efficient way with type and stats."""
        lines = []
        for filename, schema in schema_info.items():
            lines.append(f"\n{filename} ({schema.row_count} rows):")
            for col in schema.columns:
                parts = [f"  - {col.name} [{col.dtype}]"]

                # Add role
                if col.role:
                    parts.append(f"role={col.role}")

                # Add key stats compactly
                stats = col.stats
                stat_parts = []
                if stats.unique_count:
                    stat_parts.append(f"unique={stats.unique_count}")
                if stats.missing_ratio > 0:
                    stat_parts.append(f"missing={stats.missing_ratio:.1%}")

                # Type-specific stats
                if col.dtype == "numeric" and stats.min_value is not None:
                    stat_parts.append(f"range=[{stats.min_value:.1f}..{stats.max_value:.1f}]")
                    stat_parts.append(f"mean={stats.mean_value:.1f}")
                elif col.dtype == "categorical" and stats.top_categories:
                    top = ", ".join(stats.top_categories[:3])
                    stat_parts.append(f"top=({top})")
                elif col.dtype == "datetime" and stats.min_date:
                    # Truncate dates to just date part
                    min_d = stats.min_date.split("T")[0] if "T" in stats.min_date else stats.min_date[:10]
                    max_d = stats.max_date.split("T")[0] if "T" in stats.max_date else stats.max_date[:10]
                    stat_parts.append(f"range=[{min_d}..{max_d}]")

                if stat_parts:
                    parts.append(", ".join(stat_parts))

                lines.append(" | ".join(parts))

        return "\n".join(lines)

    def create_plan(self, brief: str, schema_info: Dict[str, SchemaInfo]) -> AnalysisPlan:
        schema_summary = self._format_schema_compact(schema_info)
        user = f"Business brief:\n{brief}\n\nData schemas:{schema_summary}\n\nProvide analysis plan as JSON:"
        response = llm_client.chat_json(
            PLAN_PROMPT, user, model=self.model, temperature=self.temperature, max_tokens=1500
        )
        return AnalysisPlan(**response)
