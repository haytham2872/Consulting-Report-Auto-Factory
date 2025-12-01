from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    id: str
    description: str
    required_columns: Optional[List[str]] = None
    output_type: str = "kpi_table"


class AnalysisPlan(BaseModel):
    title: str
    objectives: List[str]
    steps: List[PlanStep]


class KPI(BaseModel):
    name: str
    value: float
    explanation: str
    related_columns: List[str] = Field(default_factory=list)


class NamedTable(BaseModel):
    title: str
    columns: List[str]
    rows: List[List[str | float | int]]
    description: Optional[str] = None


class ChartInfo(BaseModel):
    title: str
    chart_type: str
    filename: str
    description: Optional[str] = None


class AnalysisResult(BaseModel):
    plan: AnalysisPlan
    kpis: List[KPI] = Field(default_factory=list)
    tables: List[NamedTable] = Field(default_factory=list)
    charts: List[ChartInfo] = Field(default_factory=list)
    notes: Optional[str] = None


class Slide(BaseModel):
    title: str
    bullets: List[str]
    visual: Optional[str] = None
    notes: Optional[str] = None


class SlideDeckOutline(BaseModel):
    slides: List[Slide]
    overview: Optional[str] = None
