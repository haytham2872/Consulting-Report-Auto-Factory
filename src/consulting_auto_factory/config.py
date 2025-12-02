from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Settings(BaseModel):
    model: str = Field(default="claude-3-haiku-20240307", description="Default Claude model")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reports_dir: Path = Path("reports")
    input_dir: Path = Path("data/input")
    brief_path: Path = Path("config/business_brief.txt")
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SchemaColumn(BaseModel):
    name: str
    dtype: str


class SchemaInfo(BaseModel):
    filename: str
    columns: list[SchemaColumn]
    preview_rows: list[dict]
