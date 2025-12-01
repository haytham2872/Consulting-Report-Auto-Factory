from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


plt.switch_backend("Agg")


def generate_time_series(df: pd.DataFrame, date_col: str, value_col: str, title: str, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df[date_col], df[value_col], marker="o")
    ax.set_title(title)
    ax.set_xlabel(date_col)
    ax.set_ylabel(value_col)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def generate_bar_chart(df: pd.DataFrame, category_col: str, value_col: str, title: str, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df[category_col], df[value_col])
    ax.set_title(title)
    ax.set_xlabel(category_col)
    ax.set_ylabel(value_col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path

