from pathlib import Path

import pandas as pd

from consulting_auto_factory import data_loader


def test_load_with_schema(tmp_path: Path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1, 2], "date": ["2024-01-01", "2024-02-01"]}).to_csv(csv_path, index=False)

    dataframes, schemas = data_loader.load_with_schema(tmp_path)

    assert "sample.csv" in dataframes
    schema = schemas["sample.csv"]
    assert any(col.dtype == "datetime" for col in schema.columns)
    assert len(schema.preview_rows) == 2


def test_infer_dtype_numeric_and_categorical():
    df = pd.DataFrame({"num": [1, 2, 3], "cat": ["a", "b", "c"]})
    assert data_loader.infer_dtype(df["num"]) == "numeric"
    assert data_loader.infer_dtype(df["cat"]) == "categorical"
