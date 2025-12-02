"""
Analysis tools that the DataAnalystAgent can use to perform data analysis.
Each tool is a function that takes dataframes and returns structured results.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime


def compute_revenue_summary(df: pd.DataFrame, amount_column: str) -> Dict[str, Any]:
    """
    Compute revenue statistics from a dataframe.

    Args:
        df: DataFrame containing revenue data
        amount_column: Name of the column containing revenue amounts

    Returns:
        Dictionary with revenue statistics (total, mean, median, min, max)
    """
    if amount_column not in df.columns:
        return {"error": f"Column '{amount_column}' not found in dataframe"}

    try:
        revenue_data = pd.to_numeric(df[amount_column], errors='coerce').dropna()

        return {
            "total_revenue": float(revenue_data.sum()),
            "average_revenue": float(revenue_data.mean()),
            "median_revenue": float(revenue_data.median()),
            "min_revenue": float(revenue_data.min()),
            "max_revenue": float(revenue_data.max()),
            "count": int(len(revenue_data))
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_top_categories(
    df: pd.DataFrame,
    category_column: str,
    metric_column: str,
    top_n: int = 5
) -> Dict[str, Any]:
    """
    Analyze top N categories by a metric (e.g., top products by revenue).

    Args:
        df: DataFrame containing categorical data
        category_column: Column with categories
        metric_column: Column with metric to sum
        top_n: Number of top categories to return

    Returns:
        Dictionary with top categories and their totals
    """
    if category_column not in df.columns:
        return {"error": f"Column '{category_column}' not found"}
    if metric_column not in df.columns:
        return {"error": f"Column '{metric_column}' not found"}

    try:
        result = df.groupby(category_column)[metric_column].sum().nlargest(top_n)

        return {
            "top_categories": [
                {"category": str(cat), "total": float(val)}
                for cat, val in result.items()
            ],
            "category_column": category_column,
            "metric_column": metric_column
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_churn_metrics(df: pd.DataFrame, churn_column: str) -> Dict[str, Any]:
    """
    Calculate churn-related metrics.

    Args:
        df: DataFrame with customer data
        churn_column: Column indicating churn status (boolean or 1/0)

    Returns:
        Dictionary with churn rate and counts
    """
    if churn_column not in df.columns:
        return {"error": f"Column '{churn_column}' not found"}

    try:
        # Convert to boolean
        churn_data = df[churn_column].astype(bool)
        total = len(churn_data)
        churned = churn_data.sum()

        return {
            "total_customers": int(total),
            "churned_customers": int(churned),
            "active_customers": int(total - churned),
            "churn_rate": float((churned / total * 100) if total > 0 else 0)
        }
    except Exception as e:
        return {"error": str(e)}


def compute_time_series(
    df: pd.DataFrame,
    date_column: str,
    metric_column: str,
    period: str = 'M'
) -> Dict[str, Any]:
    """
    Compute time series aggregation (e.g., monthly revenue).

    Args:
        df: DataFrame with time series data
        date_column: Column with dates
        metric_column: Column with metric to aggregate
        period: Pandas period code ('D'=daily, 'W'=weekly, 'M'=monthly)

    Returns:
        Dictionary with time series data
    """
    if date_column not in df.columns:
        return {"error": f"Column '{date_column}' not found"}
    if metric_column not in df.columns:
        return {"error": f"Column '{metric_column}' not found"}

    try:
        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
        df_copy = df_copy.dropna(subset=[date_column])

        # Set date as index and resample
        df_copy = df_copy.set_index(date_column)
        resampled = df_copy[metric_column].resample(period).sum()

        return {
            "time_series": [
                {"period": str(date.date()), "value": float(val)}
                for date, val in resampled.items() if pd.notna(val)
            ],
            "period_type": period,
            "metric": metric_column
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_customer_ltv(
    df: pd.DataFrame,
    ltv_column: str
) -> Dict[str, Any]:
    """
    Calculate customer lifetime value statistics.

    Args:
        df: DataFrame with customer data
        ltv_column: Column containing lifetime value

    Returns:
        Dictionary with LTV statistics
    """
    if ltv_column not in df.columns:
        return {"error": f"Column '{ltv_column}' not found"}

    try:
        ltv_data = pd.to_numeric(df[ltv_column], errors='coerce').dropna()

        return {
            "average_ltv": float(ltv_data.mean()),
            "median_ltv": float(ltv_data.median()),
            "total_ltv": float(ltv_data.sum()),
            "min_ltv": float(ltv_data.min()),
            "max_ltv": float(ltv_data.max()),
            "customer_count": int(len(ltv_data))
        }
    except Exception as e:
        return {"error": str(e)}


def get_dataframe_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get basic summary of a dataframe structure.

    Args:
        df: DataFrame to summarize

    Returns:
        Dictionary with dataframe info
    """
    try:
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": [
                {
                    "name": col,
                    "dtype": str(df[col].dtype),
                    "null_count": int(df[col].isna().sum()),
                    "sample_values": df[col].dropna().head(3).tolist() if len(df) > 0 else []
                }
                for col in df.columns
            ]
        }
    except Exception as e:
        return {"error": str(e)}


# Tool definitions for Claude
ANALYSIS_TOOLS = [
    {
        "name": "compute_revenue_summary",
        "description": "Compute revenue statistics (total, average, median, min, max) from a dataframe column containing revenue/amount data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of the dataframe to analyze (e.g., 'orders', 'customers')"
                },
                "amount_column": {
                    "type": "string",
                    "description": "Name of the column containing revenue/amount values"
                }
            },
            "required": ["dataframe_name", "amount_column"]
        }
    },
    {
        "name": "analyze_top_categories",
        "description": "Find top N categories by a metric. Useful for finding top products, regions, or segments by revenue or other metrics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of the dataframe to analyze"
                },
                "category_column": {
                    "type": "string",
                    "description": "Column containing categories (e.g., 'product_category', 'country', 'segment')"
                },
                "metric_column": {
                    "type": "string",
                    "description": "Column with metric to sum (e.g., 'total_amount', 'quantity')"
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of top categories to return",
                    "default": 5
                }
            },
            "required": ["dataframe_name", "category_column", "metric_column"]
        }
    },
    {
        "name": "calculate_churn_metrics",
        "description": "Calculate churn rate and customer retention metrics from a churn indicator column.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of the dataframe (typically 'customers')"
                },
                "churn_column": {
                    "type": "string",
                    "description": "Column indicating churn status (boolean or 1/0)"
                }
            },
            "required": ["dataframe_name", "churn_column"]
        }
    },
    {
        "name": "compute_time_series",
        "description": "Compute time-based aggregation of a metric (e.g., monthly revenue trends).",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of the dataframe"
                },
                "date_column": {
                    "type": "string",
                    "description": "Column containing dates"
                },
                "metric_column": {
                    "type": "string",
                    "description": "Column with metric to aggregate over time"
                },
                "period": {
                    "type": "string",
                    "description": "Period for aggregation: 'D' (daily), 'W' (weekly), 'M' (monthly)",
                    "default": "M"
                }
            },
            "required": ["dataframe_name", "date_column", "metric_column"]
        }
    },
    {
        "name": "calculate_customer_ltv",
        "description": "Calculate customer lifetime value statistics (average, median, total, min, max).",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of the dataframe (typically 'customers')"
                },
                "ltv_column": {
                    "type": "string",
                    "description": "Column containing lifetime value data"
                }
            },
            "required": ["dataframe_name", "ltv_column"]
        }
    },
    {
        "name": "get_dataframe_summary",
        "description": "Get basic summary of dataframe structure including columns, types, null counts, and sample values. Use this first to understand the data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of the dataframe to summarize"
                }
            },
            "required": ["dataframe_name"]
        }
    }
]
