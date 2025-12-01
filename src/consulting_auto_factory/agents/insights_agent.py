from __future__ import annotations

from typing import List

from .. import llm_client
from ..models import AnalysisResult, ChartInfo, KPI, NamedTable


REPORT_PROMPT = """You are a consulting analyst who writes crisp Markdown reports.
Use the provided KPIs, tables, and chart descriptions to draft a client-ready narrative.
Include: title, executive summary, key findings, analysis sections, risks & opportunities, recommended actions.
"""


class InsightsAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.4) -> None:
        self.model = model
        self.temperature = temperature

    def _format_inputs(self, brief: str, analysis_result: AnalysisResult) -> str:
        lines: List[str] = ["Business brief:", brief, "\nKPIs:"]
        for kpi in analysis_result.kpis:
            lines.append(f"- {kpi.name}: {kpi.value:.2f} ({kpi.explanation})")
        lines.append("\nTables:")
        for table in analysis_result.tables:
            lines.append(f"- {table.title} with columns {table.columns}")
        lines.append("\nCharts:")
        for chart in analysis_result.charts:
            lines.append(f"- {chart.title} -> {chart.filename}")
        return "\n".join(lines)

    def generate_report(self, brief: str, analysis_result: AnalysisResult) -> str:
        user = self._format_inputs(brief, analysis_result)
        try:
            return llm_client.chat(REPORT_PROMPT, user, model=self.model, temperature=self.temperature)
        except Exception:
            # offline fallback
            sections = [
                "# Consulting Report",
                "## Executive summary",
                "Data-driven highlights based on provided KPIs and tables.",
                "## Key findings",
            ]
            for kpi in analysis_result.kpis[:5]:
                sections.append(f"- {kpi.name}: {kpi.value:.2f}")
            sections.append("## Charts")
            for chart in analysis_result.charts:
                sections.append(f"![{chart.title}]({chart.filename})")
            sections.append("## Recommended actions\n- Deep dive into growth categories\n- Test retention offers for at-risk customers")
            return "\n".join(sections)

