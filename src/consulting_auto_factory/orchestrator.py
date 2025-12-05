from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from .agents.data_analyst_agent import DataAnalystAgent
from .agents.insights_agent import InsightsAgent
from .agents.planner_agent import PlannerAgent
from .config import Settings
from .data_loader import load_with_schema, summarize_input_files, assign_all_roles
from .models import AnalysisResult, RunMetadata


def read_brief(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def run_pipeline(
    input_dir: str = "data/input", brief_path: str = "config/business_brief.txt", reports_dir: str = "reports"
) -> None:
    settings = Settings(input_dir=Path(input_dir), brief_path=Path(brief_path), reports_dir=Path(reports_dir))
    dataframes, schemas = load_with_schema(settings.input_dir)
    brief = read_brief(settings.brief_path)

    # Assign column roles based on types
    column_roles = assign_all_roles(schemas)

    planner = PlannerAgent(model=settings.model, temperature=settings.temperature)
    plan = planner.create_plan(brief, schemas)

    analyst = DataAnalystAgent(reports_dir=settings.reports_dir, use_tools=True, model=settings.model)
    analysis_result: AnalysisResult = analyst.run_analysis(plan, dataframes)
    analysis_result.metadata = RunMetadata(
        run_timestamp=datetime.now(timezone.utc).isoformat(),
        model=settings.model,
        temperature=settings.temperature,
        input_files=summarize_input_files(dataframes, settings.input_dir),
    )
    # Store column roles in result for downstream use
    analysis_result.column_roles = column_roles

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    with open(settings.reports_dir / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result.model_dump(), f, indent=2)

    insights = InsightsAgent(model=settings.model, temperature=settings.temperature)
    report_md = insights.generate_report(brief, analysis_result, column_roles=column_roles)
    with open(settings.reports_dir / "consulting_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)


def plan_only(input_dir: str = "data/input", brief_path: str = "config/business_brief.txt"):
    settings = Settings(input_dir=Path(input_dir), brief_path=Path(brief_path))
    _, schemas = load_with_schema(settings.input_dir)
    # Assign roles for schema-driven planning
    assign_all_roles(schemas)
    brief = read_brief(settings.brief_path)
    planner = PlannerAgent(model=settings.model, temperature=settings.temperature)
    plan = planner.create_plan(brief, schemas)
    return plan

