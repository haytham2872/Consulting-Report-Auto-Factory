from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


def summarize_numeric(df: pd.DataFrame, column: str) -> Dict[str, float]:
    series = df[column].dropna()
    return {
        "total": float(series.sum()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "max": float(series.max()),
        "min": float(series.min()),
    }


def aggregate_by_time(df: pd.DataFrame, date_col: str, value_col: str, freq: str = "ME") -> pd.DataFrame:
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    grouped = (
        df.set_index(date_col)
        .resample(freq)[value_col]
        .sum()
        .reset_index()
        .rename(columns={value_col: "total"})
    )
    return grouped


def top_categories(df: pd.DataFrame, category_col: str, value_col: Optional[str] = None, n: int = 5) -> pd.DataFrame:
    if value_col:
        grouped = df.groupby(category_col)[value_col].sum().reset_index()
        return grouped.sort_values(value_col, ascending=False).head(n)
    counts = df[category_col].value_counts().reset_index()
    counts.columns = [category_col, "count"]
    return counts.head(n)


def churn_rate(customers: pd.DataFrame, churn_col: str = "is_churned") -> float:
    if churn_col not in customers.columns:
        return 0.0
    total = len(customers)
    if total == 0:
        return 0.0
    return float(customers[churn_col].sum() / total)

