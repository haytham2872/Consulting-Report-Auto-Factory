from __future__ import annotations

from pathlib import Path
import hashlib
from typing import Dict, List, Tuple

import pandas as pd

from .config import SchemaColumn, SchemaInfo
from .models import InputFileProfile


DATE_LIKE = {"date", "_at", "_on"}


def load_csvs(input_dir: str | Path) -> Dict[str, pd.DataFrame]:
    """Load all CSVs in a directory into a dictionary keyed by filename."""
    dataframes: Dict[str, pd.DataFrame] = {}
    for csv_path in Path(input_dir).glob("*.csv"):
        df = pd.read_csv(csv_path)
        dataframes[csv_path.name] = df
    if not dataframes:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    return dataframes


def infer_dtype(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    return "categorical"


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
    preview = df.head(5).to_dict(orient="records")
    columns = [SchemaColumn(name=col, dtype=infer_dtype(df[col])) for col in df.columns]
    return SchemaInfo(filename=filename, columns=columns, preview_rows=preview)


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
