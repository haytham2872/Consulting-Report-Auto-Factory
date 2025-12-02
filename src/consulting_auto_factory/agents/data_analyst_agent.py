from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json

import pandas as pd

from .. import analysis_tools
from .. import analysis_tools_v2
from ..models import AnalysisPlan, AnalysisResult, KPI, NamedTable
from .. import llm_client


class DataAnalystAgent:
    def __init__(
        self,
        reports_dir: str | Path = "reports",
        use_tools: bool = True,
        model: str | None = None,
        max_tool_rounds: int = 10
    ) -> None:
        """
        Initialize the Data Analyst Agent.

        Args:
            reports_dir: Directory for reports
            use_tools: If True, use agentic tool-calling mode. If False, use legacy hardcoded analysis.
            model: LLM model to use (only for tool mode)
            max_tool_rounds: Maximum number of tool calling rounds to prevent infinite loops
        """
        self.reports_dir = Path(reports_dir)
        self.use_tools = use_tools
        self.model = model
        self.max_tool_rounds = max_tool_rounds

    def _find_numeric_column(self, df: pd.DataFrame, candidates: List[str]) -> str | None:
        for candidate in candidates:
            for col in df.columns:
                if candidate in col.lower() and pd.api.types.is_numeric_dtype(df[col]):
                    return col
        return None

    def _execute_tool(self, tool_name: str, tool_input: Dict, dataframes: Dict[str, pd.DataFrame]) -> Dict:
        """Execute a tool call and return the result."""
        # Get the dataframe
        df_name = tool_input.get("dataframe_name", "")
        df = dataframes.get(df_name)

        if df is None:
            return {"error": f"Dataframe '{df_name}' not found. Available: {list(dataframes.keys())}"}

        # Call the appropriate tool
        tool_functions = {
            "compute_revenue_summary": analysis_tools_v2.compute_revenue_summary,
            "analyze_top_categories": analysis_tools_v2.analyze_top_categories,
            "calculate_churn_metrics": analysis_tools_v2.calculate_churn_metrics,
            "compute_time_series": analysis_tools_v2.compute_time_series,
            "calculate_customer_ltv": analysis_tools_v2.calculate_customer_ltv,
            "get_dataframe_summary": analysis_tools_v2.get_dataframe_summary,
        }

        func = tool_functions.get(tool_name)
        if not func:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            # Remove dataframe_name from input before passing to function
            func_input = {k: v for k, v in tool_input.items() if k != "dataframe_name"}
            result = func(df, **func_input)
            return result
        except Exception as e:
            return {"error": f"Tool execution error: {str(e)}"}

    def _tool_mode_analysis(self, plan: AnalysisPlan, dataframes: Dict[str, pd.DataFrame]) -> AnalysisResult:
        """Run analysis using agentic tool calling."""
        # Prepare data summary for the LLM
        data_summary = {
            name: {
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
            for name, df in dataframes.items()
        }

        # Create system prompt
        system_prompt = """You are a data analyst agent with access to analysis tools.

Your job is to:
1. Understand the analysis plan and business objectives
2. Inspect the available dataframes using get_dataframe_summary
3. Use the available tools to compute relevant KPIs and statistics
4. Gather insights systematically based on the plan

Guidelines:
- Start by using get_dataframe_summary to understand the data structure
- Use tools strategically based on the analysis objectives
- Focus on the most relevant analyses for the business brief
- When you have gathered sufficient insights, stop and let me compile the results
- Be efficient - don't repeat the same analysis multiple times"""

        # Create user message
        user_message = f"""Analyze the following data to address the business objectives.

**Analysis Plan:**
Title: {plan.title}

Objectives:
{chr(10).join('- ' + obj for obj in plan.objectives)}

**Available Dataframes:**
{json.dumps(data_summary, indent=2)}

**Instructions:**
1. Use get_dataframe_summary to understand each dataframe first
2. Execute relevant analyses using the available tools
3. Focus on computing KPIs and statistics that address the objectives
4. When you've gathered sufficient insights (typically 5-8 tool calls), respond with a summary

Use the tools to gather data. I'll compile the final report from your findings."""

        messages = [{"role": "user", "content": user_message}]

        # Tool calling loop
        all_tool_results = []

        for round_num in range(self.max_tool_rounds):
            response = llm_client.chat_with_tools(
                system_prompt=system_prompt,
                messages=messages,
                tools=analysis_tools_v2.ANALYSIS_TOOLS,
                model=self.model,
                temperature=0.3,
                max_tokens=4000
            )

            # Check if we got a final response (no more tools)
            if response.stop_reason == "end_turn":
                # Agent is done
                break

            # Process tool uses
            if response.stop_reason == "tool_use":
                # Add assistant message to history
                messages.append({"role": "assistant", "content": response.content})

                # Execute tools and collect results
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input, dataframes)
                        all_tool_results.append({
                            "tool": block.name,
                            "input": block.input,
                            "result": result
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                break

        # Convert tool results to KPIs and tables
        kpis = []
        tables = []

        for tool_result in all_tool_results:
            tool_name = tool_result["tool"]
            result = tool_result["result"]

            # Skip errors
            if "error" in result:
                continue

            # Convert results to KPIs and tables based on tool type
            if tool_name == "compute_revenue_summary":
                if "total_revenue" in result:
                    kpis.append(KPI(
                        name="Total Revenue",
                        value=result["total_revenue"],
                        explanation="Total revenue from all transactions",
                        related_columns=[tool_result["input"].get("amount_column", "")]
                    ))
                if "average_revenue" in result:
                    kpis.append(KPI(
                        name="Average Revenue",
                        value=result["average_revenue"],
                        explanation="Average revenue per transaction",
                        related_columns=[tool_result["input"].get("amount_column", "")]
                    ))

            elif tool_name == "analyze_top_categories":
                if "top_categories" in result:
                    top_cats = result["top_categories"]
                    tables.append(NamedTable(
                        title=f"Top {result.get('category_column', 'Categories')}",
                        columns=["Category", "Total"],
                        rows=[[cat["category"], cat["total"]] for cat in top_cats],
                        description=f"Top categories by {result.get('metric_column', 'metric')}"
                    ))

            elif tool_name == "calculate_churn_metrics":
                if "churn_rate" in result:
                    kpis.append(KPI(
                        name="Churn Rate",
                        value=result["churn_rate"],
                        explanation=f"{result.get('churned_customers', 0)} out of {result.get('total_customers', 0)} customers churned",
                        related_columns=[tool_result["input"].get("churn_column", "")]
                    ))

            elif tool_name == "calculate_customer_ltv":
                if "average_ltv" in result:
                    kpis.append(KPI(
                        name="Average Customer LTV",
                        value=result["average_ltv"],
                        explanation=f"Average lifetime value across {result.get('customer_count', 0)} customers",
                        related_columns=[tool_result["input"].get("ltv_column", "")]
                    ))
                tables.append(NamedTable(
                    title="Customer Lifetime Value Distribution",
                    columns=["Metric", "Value"],
                    rows=[
                        ["Average", result.get("average_ltv", 0)],
                        ["Median", result.get("median_ltv", 0)],
                        ["Total", result.get("total_ltv", 0)],
                        ["Min", result.get("min_ltv", 0)],
                        ["Max", result.get("max_ltv", 0)]
                    ],
                    description="LTV statistics"
                ))

            elif tool_name == "compute_time_series":
                if "time_series" in result:
                    ts_data = result["time_series"]
                    if ts_data:
                        tables.append(NamedTable(
                            title=f"Time Series: {result.get('metric', 'Metric')}",
                            columns=["Period", "Value"],
                            rows=[[item["period"], item["value"]] for item in ts_data[:10]],  # Limit to 10 rows
                            description=f"Time series aggregated by {result.get('period_type', 'period')}"
                        ))

        return AnalysisResult(plan=plan, kpis=kpis, tables=tables)

    def _legacy_analysis(self, plan: AnalysisPlan, dataframes: Dict[str, pd.DataFrame]) -> AnalysisResult:
        """Legacy hardcoded analysis (original implementation)."""
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

    def run_analysis(self, plan: AnalysisPlan, dataframes: Dict[str, pd.DataFrame]) -> AnalysisResult:
        """
        Run analysis on the provided dataframes.

        Uses tool-calling mode if use_tools=True, otherwise uses legacy hardcoded analysis.
        """
        if self.use_tools:
            return self._tool_mode_analysis(plan, dataframes)
        else:
            return self._legacy_analysis(plan, dataframes)
