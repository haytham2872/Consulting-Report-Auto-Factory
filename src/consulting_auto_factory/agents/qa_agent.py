from __future__ import annotations

from typing import Optional, Dict

from .. import llm_client
from ..models import AnalysisResult, ColumnRole


QA_PROMPT = """You are a professional data analyst answering follow-up questions about an analysis you just completed.

You will receive:
1. A summary of the analysis results (KPIs, tables, column roles)
2. A user's question

CRITICAL RULES:
1. Answer ONLY based on the provided analysis results - do NOT invent or assume additional information
2. Reference specific numbers, KPIs, or table findings when relevant
3. If the answer is not derivable from the analysis, say so clearly and suggest what additional analysis would help
4. Be concise (2-3 paragraphs maximum) and professional
5. Use business language appropriate for executives
6. If referencing column names or metrics, use the exact names from the analysis

Your answer should be direct, grounded in the data, and helpful.
"""


class QAAgent:
    """Lightweight Q&A agent that answers questions from existing analysis results."""

    def __init__(self, model: str | None = None, temperature: float = 0.3) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = 500  # Keep answers concise

    def _build_context(
        self,
        analysis_result: AnalysisResult,
        column_roles: Optional[Dict[str, Dict[str, ColumnRole]]] = None,
    ) -> str:
        """Build compact context from analysis result for Q&A."""
        lines = []

        # Analysis plan summary
        if analysis_result.plan:
            lines.append(f"Analysis: {analysis_result.plan.title}")
            if analysis_result.plan.objectives:
                lines.append(f"Objectives: {', '.join(analysis_result.plan.objectives[:3])}")

        # Column roles (compact)
        if column_roles:
            lines.append("\nData structure:")
            for filename, roles in column_roles.items():
                role_groups: Dict[str, list[str]] = {"measure": [], "dimension": [], "time": [], "text": []}
                for col_name, role_info in roles.items():
                    # role_info may be a ColumnRole instance or a plain dict (when loaded from JSON)
                    if isinstance(role_info, dict):
                        role = role_info.get("role")
                    else:
                        role = getattr(role_info, "role", None)

                    if role in role_groups:
                        role_groups[role].append(col_name)

                parts = []
                for role, cols in role_groups.items():
                    if cols:
                        # Truncate if too many columns
                        col_list = cols[:5]
                        if len(cols) > 5:
                            col_list.append(f"(+{len(cols)-5} more)")
                        parts.append(f"{role}s: {', '.join(col_list)}")
                if parts:
                    lines.append(f"  {filename}: {' | '.join(parts)}")

        # KPIs (key findings)
        if analysis_result.kpis:
            lines.append("\nKey metrics:")
            for kpi in analysis_result.kpis[:10]:  # Limit to top 10
                value_str = f"{kpi.value:,.2f}" if abs(kpi.value) >= 1 else f"{kpi.value:.4f}"
                lines.append(f"  - {kpi.name}: {value_str} ({kpi.explanation})")
            if len(analysis_result.kpis) > 10:
                lines.append(f"  (and {len(analysis_result.kpis) - 10} more metrics)")

        # Tables (compact summary)
        if analysis_result.tables:
            lines.append("\nAnalysis tables:")
            for table in analysis_result.tables[:5]:  # Limit to first 5 tables
                row_count = len(table.rows)
                lines.append(f"  - {table.title}: {row_count} rows, columns: {', '.join(table.columns)}")
                if table.description:
                    lines.append(f"    ({table.description})")
            if len(analysis_result.tables) > 5:
                lines.append(f"  (and {len(analysis_result.tables) - 5} more tables)")

        return "\n".join(lines)

    def answer_question(
        self,
        question: str,
        analysis_result: AnalysisResult,
        column_roles: Optional[Dict[str, Dict[str, ColumnRole]]] = None,
    ) -> str:
        """
        Answer a user question based on the analysis results.

        Args:
            question: User's question
            analysis_result: The completed analysis with KPIs, tables, etc.
            column_roles: Optional column role mapping for context

        Returns:
            A concise answer grounded in the analysis
        """
        if not question or not question.strip():
            return "Please provide a question."

        # Build compact context
        context = self._build_context(analysis_result, column_roles)

        # Build user message
        user_message = f"""Analysis context:
{context}

User question: {question}

Provide a concise, professional answer based only on the analysis results shown above."""

        # Call LLM
        answer = llm_client.chat(
            system_prompt=QA_PROMPT,
            user_content=user_message,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return answer.strip()
