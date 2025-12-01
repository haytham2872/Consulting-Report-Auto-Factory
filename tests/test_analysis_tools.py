import pandas as pd

from consulting_auto_factory import analysis_tools


def test_summarize_numeric():
    df = pd.DataFrame({"value": [1, 2, 3, 4]})
    summary = analysis_tools.summarize_numeric(df, "value")
    assert summary["total"] == 10.0
    assert summary["mean"] == 2.5


def test_aggregate_by_time_monthly():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-10", "2024-01-20", "2024-02-01"]),
            "revenue": [100, 50, 200],
        }
    )
    grouped = analysis_tools.aggregate_by_time(df, "date", "revenue", freq="ME")
    assert grouped.shape[0] == 2
    assert grouped.iloc[0]["total"] == 150


def test_top_categories_counts_and_values():
    df = pd.DataFrame({"cat": ["a", "a", "b"], "value": [10, 5, 1]})
    counts = analysis_tools.top_categories(df, "cat")
    assert counts.iloc[0]["cat"] == "a"
    values = analysis_tools.top_categories(df, "cat", "value")
    assert values.iloc[0]["value"] == 15


def test_churn_rate():
    df = pd.DataFrame({"is_churned": [True, False, True]})
    assert analysis_tools.churn_rate(df) == 2 / 3
