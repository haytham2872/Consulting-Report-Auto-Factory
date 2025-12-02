from __future__ import annotations

import json
from typing import Dict

from .. import llm_client
from ..config import SchemaInfo
from ..models import AnalysisPlan, PlanStep


PLAN_PROMPT = """You are a senior data analytics consultant planning an analysis on business data.
Given a business brief and CSV schemas, propose a concise JSON plan with objectives and 4-6 steps.
Only return JSON with fields: title, objectives (list), steps (list of objects with id, description, required_columns, output_type).
"""


class PlannerAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.3) -> None:
        self.model = model
        self.temperature = temperature

    def create_plan(self, brief: str, schema_info: Dict[str, SchemaInfo]) -> AnalysisPlan:
        schema_summary = []
        for name, schema in schema_info.items():
            columns = ", ".join([f"{c.name} ({c.dtype})" for c in schema.columns])
            schema_summary.append(f"{name}: {columns}")
        user = f"Brief:\n{brief}\n\nSchemas:\n" + "\n".join(schema_summary)
        response = llm_client.chat_json(PLAN_PROMPT, user, model=self.model, temperature=self.temperature, max_tokens=2000)
        return AnalysisPlan(**response)

