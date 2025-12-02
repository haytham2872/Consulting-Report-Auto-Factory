from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from .. import analysis_tools
from ..models import AnalysisPlan, AnalysisResult, KPI, NamedTable


class DataAnalystAgent:
    def __init__(self, reports_dir: str | Path = "reports") -> None:
        self.reports_dir = Path(reports_dir)

    def _find_numeric_column(self, df: pd.DataFrame, candidates: List[str]) -> str | None:
        for candidate in candidates:
            for col in df.columns:
                if candidate in col.lower() and pd.api.types.is_numeric_dtype(df[col]):
                    return col
        return None

    def run_analysis(self, plan: AnalysisPlan, dataframes: Dict[str, pd.DataFrame]) -> AnalysisResult:
        kpis: List[KPI] = []
        tables: List[NamedTable] = []

        orders_df = dataframes.get("orders.csv")
        customers_df = dataframes.get("customers.csv")

        if orders_df is not None:
            revenue_col = self._find_numeric_column(orders_df, ["total_amount", "revenue", "amount"])
            date_col = None
            for col in orders_df.columns:
                if "date" in col.lower():
                    date_col = col
                    break

            if revenue_col:
                summary = analysis_tools.summarize_numeric(orders_df, revenue_col)
                kpis.extend(
                    [
                        KPI(name="Total revenue", value=summary["total"], explanation=f"Sum of {revenue_col}", related_columns=[revenue_col]),
                        KPI(name="Average order value", value=summary["mean"], explanation="Mean order revenue", related_columns=[revenue_col]),
                    ]
                )
                tables.append(
                    NamedTable(
                        title="Revenue summary",
                        columns=list(summary.keys()),
                        rows=[[summary[k] for k in summary.keys()]],
                        description="Basic revenue distribution",
                    )
                )

                category_col = None
                for candidate in ["product_category", "category", "segment"]:
                    if candidate in orders_df.columns:
                        category_col = candidate
                        break
                if category_col:
                    top = analysis_tools.top_categories(orders_df, category_col, revenue_col, n=5)
                    tables.append(
                        NamedTable(
                            title="Top categories",
                            columns=list(top.columns),
                            rows=top.values.tolist(),
                            description="Categories ranked by revenue",
                        )
                    )

                country_col = "country" if "country" in orders_df.columns else None
                if country_col and revenue_col:
                    country = analysis_tools.top_categories(orders_df, country_col, revenue_col, n=5)
                    tables.append(
                        NamedTable(
                            title="Top regions",
                            columns=list(country.columns),
                            rows=country.values.tolist(),
                            description="Revenue by country",
                        )
                    )

        if customers_df is not None:
            churn = analysis_tools.churn_rate(customers_df)
            kpis.append(
                KPI(
                    name="Churn rate",
                    value=round(churn * 100, 2),
                    explanation="Share of customers flagged as churned",
                    related_columns=["is_churned"],
                )
            )
            if "lifetime_value" in customers_df.columns:
                ltv_summary = analysis_tools.summarize_numeric(customers_df, "lifetime_value")
                tables.append(
                    NamedTable(
                        title="Lifetime value distribution",
                        columns=list(ltv_summary.keys()),
                        rows=[[ltv_summary[k] for k in ltv_summary.keys()]],
                        description="Customer LTV stats",
                    )
                )
        return AnalysisResult(plan=plan, kpis=kpis, tables=tables)

