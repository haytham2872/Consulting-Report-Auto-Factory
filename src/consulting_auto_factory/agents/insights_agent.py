from __future__ import annotations

from typing import List

from .. import llm_client
from ..models import AnalysisResult, ChartInfo, KPI, NamedTable


REPORT_PROMPT = """You are a consulting analyst who writes crisp Markdown reports.
Use only the provided quantitative facts and do not invent new numbers.
Return two sections only: 'Executive summary' (2-3 tight paragraphs) and 'Key findings' (3-5 bullets).
"""


class InsightsAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.4, allow_fallback: bool = False) -> None:
        self.model = model
        self.temperature = temperature
        self.allow_fallback = allow_fallback

    @staticmethod
    def _format_number(value: float) -> str:
        return f"{value:,.2f}" if abs(value) >= 1 else f"{value:.4f}"

    def _format_inputs(self, brief: str, analysis_result: AnalysisResult) -> str:
        lines: List[str] = ["Business brief:", brief, "\nData facts (use exactly):"]
        for kpi in analysis_result.kpis:
            lines.append(f"- {kpi.name}: {self._format_number(kpi.value)} ({kpi.explanation})")
        lines.append("\nTables:")
        for table in analysis_result.tables:
            lines.append(f"- {table.title} with columns {table.columns}")
        lines.append("\nCharts:")
        for chart in analysis_result.charts:
            lines.append(f"- {chart.title} -> {chart.filename}")
        return "\n".join(lines)

    def _render_kpis(self, kpis: List[KPI]) -> List[str]:
        return [f"- {kpi.name}: {self._format_number(kpi.value)} — {kpi.explanation}" for kpi in kpis]

    def _render_tables(self, tables: List[NamedTable]) -> List[str]:
        rendered: List[str] = []
        for table in tables:
            rendered.append(f"### {table.title}")
            header = " | ".join(table.columns)
            divider = " | ".join(["---"] * len(table.columns))
            rendered.append(header)
            rendered.append(divider)
            for row in table.rows:
                rendered.append(" | ".join([str(item) for item in row]))
            if table.description:
                rendered.append(f"_Note: {table.description}_")
            rendered.append("")
        return rendered

    def _render_charts(self, charts: List[ChartInfo]) -> List[str]:
        lines: List[str] = []
        for chart in charts:
            lines.append(f"- ![{chart.title}]({chart.filename}) — {chart.description or 'Chart output'}")
        return lines

    def build_data_facts(self, analysis_result: AnalysisResult) -> str:
        facts = []
        for kpi in analysis_result.kpis:
            facts.append(f"- {kpi.name}: {self._format_number(kpi.value)} ({kpi.explanation})")
        for table in analysis_result.tables:
            facts.append(f"- Table {table.title}: columns={table.columns}")
        for chart in analysis_result.charts:
            facts.append(f"- Chart {chart.title}: {chart.filename}")
        return "\n".join(facts)

    def _render_metadata(self, analysis_result: AnalysisResult) -> List[str]:
        lines: List[str] = ["## Run metadata"]
        if analysis_result.metadata:
            meta = analysis_result.metadata
            lines.append(f"- Timestamp (UTC): {meta.run_timestamp}")
            lines.append(f"- Model: {meta.model} @ temperature {meta.temperature}")
            lines.append(f"- Offline fallback: {meta.offline}")
            if meta.input_files:
                lines.append("- Input files:")
                for f in meta.input_files:
                    lines.append(f"  - {f.filename}: rows={f.rows}, cols={f.columns}, sha256={f.sha256[:12]}…")
        return lines

    def generate_report(self, brief: str, analysis_result: AnalysisResult) -> str:
        user = self._format_inputs(brief, analysis_result)
        try:
            narrative = llm_client.chat(REPORT_PROMPT, user, model=self.model, temperature=self.temperature, max_tokens=500)
        except Exception:
            if not self.allow_fallback:
                raise
            # offline fallback
            narrative = "## Executive summary\nOffline mode enabled.\n\n## Key findings\n- Deterministic summary generated without LLM."

        sections: List[str] = ["# Consulting Report"]
        sections.extend(self._render_metadata(analysis_result))
        sections.append("")
        sections.append(narrative.strip())
        sections.append("\n## Data highlights")
        sections.extend(self._render_kpis(analysis_result.kpis))
        if analysis_result.tables:
            sections.append("\n## Tables")
            sections.extend(self._render_tables(analysis_result.tables))
        if analysis_result.charts:
            sections.append("## Charts")
            sections.extend(self._render_charts(analysis_result.charts))
        sections.append("\n## Recommended actions")
        sections.append("- Prioritize initiatives indicated by the strongest KPIs.")
        sections.append("- Validate trends in the provided charts with stakeholders.")
        return "\n".join(sections)

