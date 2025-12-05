from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict


class Settings(BaseModel):
    model: str = Field(default="claude-3-haiku-20240307", description="Default Claude model")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reports_dir: Path = Path("reports")
    input_dir: Path = Path("data/input")
    brief_path: Path = Path("config/business_brief.txt")
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ColumnStats(BaseModel):
    """Compact statistics for a column."""
    non_null_count: int
    missing_ratio: float
    unique_count: int
    # For numeric columns
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    # For categorical columns (top N)
    top_categories: Optional[list[str]] = None
    # For datetime columns
    min_date: Optional[str] = None
    max_date: Optional[str] = None


class SchemaColumn(BaseModel):
    """Enhanced schema column with type and statistics."""
    name: str
    dtype: str  # 'numeric', 'categorical', 'datetime', 'text'
    stats: ColumnStats
    role: Optional[str] = None  # 'measure', 'dimension', 'time', 'text' - assigned later


class SchemaInfo(BaseModel):
    """Compact schema without raw data preview."""
    filename: str
    row_count: int
    columns: list[SchemaColumn]
