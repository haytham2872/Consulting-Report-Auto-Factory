from __future__ import annotations

from pathlib import Path
import hashlib
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

from .config import SchemaColumn, SchemaInfo, ColumnStats
from .models import InputFileProfile, ColumnRole


DATE_LIKE = {"date", "_at", "_on"}
HIGH_CARDINALITY_THRESHOLD = 50  # If unique > this, consider it 'text' instead of 'categorical'
TOP_CATEGORIES_LIMIT = 5  # Only show top N categories


def load_csvs(input_dir: str | Path) -> Dict[str, pd.DataFrame]:
    """Load all CSVs in a directory into a dictionary keyed by filename."""
    dataframes: Dict[str, pd.DataFrame] = {}
    for csv_path in Path(input_dir).glob("*.csv"):
        df = pd.read_csv(csv_path)
        dataframes[csv_path.name] = df
    if not dataframes:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    return dataframes


def infer_dtype(series: pd.Series, column_name: str = "") -> str:
    """Infer compact data type for schema with improved heuristics."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Check for ID columns (high uniqueness or "_id" in name)
    col_lower = column_name.lower()
    unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0

    # Boolean-like numeric (only 2 unique values like 0/1)
    if pd.api.types.is_numeric_dtype(series):
        unique_count = series.nunique()
        if unique_count <= 2:
            # Boolean flag -> categorical/dimension
            return "categorical"
        # ID columns: high uniqueness or "_id" suffix
        if unique_ratio > 0.9 or "_id" in col_lower or col_lower.endswith("id"):
            return "text"  # IDs are effectively text for analysis purposes
        return "numeric"

    # String/object columns
    if pd.api.types.is_object_dtype(series):
        unique_count = series.nunique()
        # IDs in string form
        if unique_ratio > 0.9 or "_id" in col_lower or col_lower.endswith("id"):
            return "text"
        # High cardinality text
        if unique_count > HIGH_CARDINALITY_THRESHOLD:
            return "text"

    return "categorical"


def compute_column_stats(series: pd.Series, dtype: str) -> ColumnStats:
    """Compute compact statistics for a column based on its type."""
    total_count = len(series)
    non_null_count = int(series.notna().sum())
    missing_ratio = round((total_count - non_null_count) / total_count, 3) if total_count > 0 else 0.0
    unique_count = int(series.nunique())

    stats = ColumnStats(
        non_null_count=non_null_count,
        missing_ratio=missing_ratio,
        unique_count=unique_count
    )

    if dtype == "numeric" and non_null_count > 0:
        stats.min_value = float(series.min())
        stats.max_value = float(series.max())
        stats.mean_value = round(float(series.mean()), 2)

    elif dtype == "categorical" and non_null_count > 0:
        # Get top N categories
        top_cats = series.value_counts().head(TOP_CATEGORIES_LIMIT).index.tolist()
        stats.top_categories = [str(cat) for cat in top_cats]

    elif dtype == "datetime" and non_null_count > 0:
        try:
            stats.min_date = str(series.min())
            stats.max_date = str(series.max())
        except (TypeError, ValueError):
            pass

    return stats


def coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Attempt to parse date-like columns."""
    for col in df.columns:
        lower = col.lower()
        if any(marker in lower for marker in DATE_LIKE):
            try:
                df[col] = pd.to_datetime(df[col])
            except (TypeError, ValueError):
                continue
    return df


def build_schema(df: pd.DataFrame, filename: str) -> SchemaInfo:
    """Build compact, statistics-rich schema without raw data preview."""
    columns = []
    for col in df.columns:
        dtype = infer_dtype(df[col], column_name=col)
        stats = compute_column_stats(df[col], dtype)
        columns.append(SchemaColumn(name=col, dtype=dtype, stats=stats))

    return SchemaInfo(filename=filename, row_count=len(df), columns=columns)


def assign_column_role(column: SchemaColumn) -> str:
    """
    Deterministically assign a role to a column based on its type.

    Roles:
    - 'time': datetime columns for temporal analysis
    - 'measure': numeric columns that represent quantities/metrics
    - 'dimension': categorical columns for grouping/segmentation
    - 'text': high-cardinality text columns
    """
    if column.dtype == "datetime":
        return "time"
    elif column.dtype == "numeric":
        return "measure"
    elif column.dtype == "categorical":
        return "dimension"
    else:  # text
        return "text"


def assign_all_roles(schemas: Dict[str, SchemaInfo]) -> Dict[str, Dict[str, ColumnRole]]:
    """
    Assign roles to all columns across all schemas.

    Returns a nested dict: filename -> column_name -> ColumnRole
    """
    all_roles: Dict[str, Dict[str, ColumnRole]] = {}

    for filename, schema in schemas.items():
        file_roles: Dict[str, ColumnRole] = {}
        for column in schema.columns:
            role = assign_column_role(column)
            # Update the column's role in-place
            column.role = role
            # Store in the mapping
            file_roles[column.name] = ColumnRole(
                column_name=column.name,
                role=role,
                dtype=column.dtype
            )
        all_roles[filename] = file_roles

    return all_roles


def load_with_schema(input_dir: str | Path) -> Tuple[Dict[str, pd.DataFrame], Dict[str, SchemaInfo]]:
    dataframes = load_csvs(input_dir)
    schemas: Dict[str, SchemaInfo] = {}
    for name, df in dataframes.items():
        df = coerce_dates(df)
        dataframes[name] = df
        schemas[name] = build_schema(df, name)
    return dataframes, schemas


def summarize_input_files(dataframes: Dict[str, pd.DataFrame], input_dir: str | Path) -> List[InputFileProfile]:
    profiles: List[InputFileProfile] = []
    for name, df in dataframes.items():
        csv_path = Path(input_dir) / name
        sha256 = ""
        if csv_path.exists():
            digest = hashlib.sha256()
            digest.update(csv_path.read_bytes())
            sha256 = digest.hexdigest()
        profiles.append(InputFileProfile(filename=name, rows=len(df), columns=len(df.columns), sha256=sha256))
    return profiles
