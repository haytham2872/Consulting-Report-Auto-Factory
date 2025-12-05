from __future__ import annotations

from typing import List, Dict, Optional

from .. import llm_client
from ..models import AnalysisResult, KPI, NamedTable, ColumnRole


REPORT_PROMPT = """You are a data analyst writing concise, generic insights from tabular data analysis.

You will receive:
1. A business brief (context)
2. Column roles (measure/dimension/time/text) showing what each column represents structurally
3. Quantitative facts (KPIs and tables)

CRITICAL RULES:
1. Use ONLY the provided quantitative facts - do NOT invent numbers
2. Structure insights around column roles:
   - "Measures" for numeric metrics/quantities
   - "Dimensions" for categorical groupings
   - "Time columns" for temporal patterns
3. Stay domain-agnostic: use role terminology unless the brief provides specific business terms
4. Keep it concise: 2-3 tight paragraphs for executive summary, 3-5 bullets for key findings
5. Focus on the strongest patterns and contrasts in the data
6. Reference actual column names when discussing specific findings

Return exactly TWO sections:
- Executive summary (2-3 paragraphs)
- Key findings (3-5 bullet points)

Write in a professional consulting style but remain generic and data-driven.
"""


class InsightsAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.4) -> None:
        self.model = model
        self.temperature = temperature

    @staticmethod
    def _format_number(value: float) -> str:
        return f"{value:,.2f}" if abs(value) >= 1 else f"{value:.4f}"

    def _format_column_roles(self, column_roles: Optional[Dict[str, Dict[str, ColumnRole]]]) -> str:
        """Format column roles compactly."""
        if not column_roles:
            return "No column role information available."

        lines = ["Column roles:"]
        for filename, roles in column_roles.items():
            role_groups: Dict[str, List[str]] = {"measure": [], "dimension": [], "time": [], "text": []}
            for col_name, role_info in roles.items():
                if role_info.role in role_groups:
                    role_groups[role_info.role].append(col_name)

            parts = []
            for role, cols in role_groups.items():
                if cols:
                    parts.append(f"{role}s: {', '.join(cols)}")
            if parts:
                lines.append(f"  {filename}: {' | '.join(parts)}")

        return "\n".join(lines)

    def _format_inputs(
        self, brief: str, analysis_result: AnalysisResult, column_roles: Optional[Dict[str, Dict[str, ColumnRole]]]
    ) -> str:
        lines: List[str] = [
            "Business brief:",
            brief,
            "",
            self._format_column_roles(column_roles),
            "",
            "Quantitative facts (use exactly):",
        ]
        for kpi in analysis_result.kpis:
            lines.append(f"- {kpi.name}: {self._format_number(kpi.value)} ({kpi.explanation})")
        lines.append("\nTables:")
        for table in analysis_result.tables:
            lines.append(f"- {table.title} with columns: {', '.join(table.columns)}")
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

    def build_data_facts(self, analysis_result: AnalysisResult) -> str:
        facts = []
        for kpi in analysis_result.kpis:
            facts.append(f"- {kpi.name}: {self._format_number(kpi.value)} ({kpi.explanation})")
        for table in analysis_result.tables:
            facts.append(f"- Table {table.title}: columns={table.columns}")
        return "\n".join(facts)

    def _render_metadata(self, analysis_result: AnalysisResult) -> List[str]:
        lines: List[str] = ["## Run metadata"]
        if analysis_result.metadata:
            meta = analysis_result.metadata
            lines.append(f"- Timestamp (UTC): {meta.run_timestamp}")
            lines.append(f"- Model: {meta.model} @ temperature {meta.temperature}")
            if meta.input_files:
                lines.append("- Input files:")
                for f in meta.input_files:
                    lines.append(f"  - {f.filename}: rows={f.rows}, cols={f.columns}, sha256={f.sha256[:12]}…")
        return lines

    def generate_report(
        self, brief: str, analysis_result: AnalysisResult, column_roles: Optional[Dict[str, Dict[str, ColumnRole]]] = None
    ) -> str:
        """Generate a role-aware consulting report."""
        user = self._format_inputs(brief, analysis_result, column_roles)
        narrative = llm_client.chat(REPORT_PROMPT, user, model=self.model, temperature=self.temperature, max_tokens=600)

        sections: List[str] = ["# Consulting Report"]
        sections.extend(self._render_metadata(analysis_result))
        sections.append("")
        sections.append(narrative.strip())
        sections.append("\n## Data highlights")
        sections.extend(self._render_kpis(analysis_result.kpis))
        if analysis_result.tables:
            sections.append("\n## Tables")
            sections.extend(self._render_tables(analysis_result.tables))
        sections.append("\n## Recommended actions")
        sections.append("- Prioritize initiatives indicated by the strongest patterns in measures.")
        sections.append("- Investigate temporal trends and dimensional segments for opportunities.")
        sections.append("- Validate findings with stakeholders and refine analysis as needed.")
        return "\n".join(sections)
