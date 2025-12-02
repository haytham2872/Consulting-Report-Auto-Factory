from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PlanStep(BaseModel):
    id: str
    description: str
    required_columns: Optional[List[str]] = None
    output_type: str = "kpi_table"

    @field_validator("id", mode="before")
    @classmethod
    def cast_id_to_str(cls, value: object) -> str:
        """Ensure plan step identifiers are strings even if the model returns integers."""
        return str(value)


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
    metadata: Optional["RunMetadata"] = None


class InputFileProfile(BaseModel):
    filename: str
    rows: int
    columns: int
    sha256: str


class RunMetadata(BaseModel):
    run_timestamp: str
    model: str
    temperature: float
    input_files: List[InputFileProfile] = Field(default_factory=list)
