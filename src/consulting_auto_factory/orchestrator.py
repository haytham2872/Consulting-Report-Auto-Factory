from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .agents.data_analyst_agent import DataAnalystAgent
from .agents.insights_agent import InsightsAgent
from .agents.planner_agent import PlannerAgent
from .agents.slide_outline_agent import SlideOutlineAgent
from .config import Settings
from .data_loader import load_with_schema
from .models import AnalysisResult


def read_brief(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def run_pipeline(input_dir: str = "data/input", brief_path: str = "config/business_brief.txt", reports_dir: str = "reports") -> None:
    settings = Settings(input_dir=Path(input_dir), brief_path=Path(brief_path), reports_dir=Path(reports_dir))
    dataframes, schemas = load_with_schema(settings.input_dir)
    brief = read_brief(settings.brief_path)

    planner = PlannerAgent(model=settings.model, temperature=settings.temperature)
    plan = planner.create_plan(brief, schemas)

    analyst = DataAnalystAgent(reports_dir=settings.reports_dir)
    analysis_result: AnalysisResult = analyst.run_analysis(plan, dataframes)

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    (settings.reports_dir / "charts").mkdir(parents=True, exist_ok=True)
    with open(settings.reports_dir / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result.model_dump(), f, indent=2)

    insights = InsightsAgent(model=settings.model, temperature=settings.temperature)
    report_md = insights.generate_report(brief, analysis_result)
    with open(settings.reports_dir / "consulting_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    slide_agent = SlideOutlineAgent(model=settings.model, temperature=settings.temperature)
    outline = slide_agent.generate_outline(report_md)
    with open(settings.reports_dir / "slides_outline.md", "w", encoding="utf-8") as f:
        f.write("# Slide Outline\n\n")
        if outline.overview:
            f.write(outline.overview + "\n\n")
        for slide in outline.slides:
            f.write(f"## {slide.title}\n")
            for bullet in slide.bullets:
                f.write(f"- {bullet}\n")
            if slide.visual:
                f.write(f"Visual: {slide.visual}\n")
            if slide.notes:
                f.write(f"Notes: {slide.notes}\n")
            f.write("\n")


def plan_only(input_dir: str = "data/input", brief_path: str = "config/business_brief.txt"):
    _, schemas = load_with_schema(input_dir)
    brief = read_brief(brief_path)
    planner = PlannerAgent()
    plan = planner.create_plan(brief, schemas)
    return plan

