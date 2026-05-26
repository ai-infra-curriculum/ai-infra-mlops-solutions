"""Statistical data-quality checks: nulls, range, outliers, cardinality."""
from __future__ import annotations

import numpy as np
import pandas as pd


def null_rate(df: pd.DataFrame) -> pd.Series:
    return df.isna().mean()


def out_of_range(series: pd.Series, lo: float, hi: float) -> float:
    """Fraction of values outside [lo, hi]."""
    if series.empty:
        return 0.0
    return float(((series < lo) | (series > hi)).mean())


def outlier_rate_iqr(series: pd.Series, k: float = 1.5) -> float:
    """Fraction of values outside [Q1 - k*IQR, Q3 + k*IQR]."""
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return out_of_range(series, q1 - k * iqr, q3 + k * iqr)


def cardinality_drift(reference: pd.Series, current: pd.Series) -> float:
    """Symmetric Jaccard distance between unique value sets."""
    a, b = set(reference.dropna().unique()), set(current.dropna().unique())
    if not (a | b):
        return 0.0
    return 1 - len(a & b) / len(a | b)


def report(df: pd.DataFrame, ref: pd.DataFrame | None = None) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        row = {"column": col, "null_rate": null_rate(df)[col]}
        if pd.api.types.is_numeric_dtype(s):
            row["outlier_iqr"] = outlier_rate_iqr(s.dropna())
        if ref is not None and col in ref.columns:
            if not pd.api.types.is_numeric_dtype(s):
                row["card_drift"] = cardinality_drift(ref[col], s)
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "amt": rng.normal(100, 20, 1000),
        "category": rng.choice(["a", "b", "c"], 1000),
    })
    df.loc[:10, "amt"] = np.nan
    df.loc[50, "amt"] = 1e6           # outlier
    print(report(df).to_string(index=False))
