"""Profile a dataset + flag anomalies vs a reference profile."""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ColumnProfile:
    column: str
    dtype: str
    null_rate: float
    n_unique: int
    mean: float | None
    std: float | None
    p01: float | None
    p99: float | None


def profile(df: pd.DataFrame) -> list[ColumnProfile]:
    out = []
    for col in df.columns:
        s = df[col]
        p = ColumnProfile(
            column=col, dtype=str(s.dtype),
            null_rate=float(s.isna().mean()), n_unique=int(s.nunique(dropna=True)),
            mean=float(s.mean()) if pd.api.types.is_numeric_dtype(s) else None,
            std=float(s.std()) if pd.api.types.is_numeric_dtype(s) else None,
            p01=float(s.quantile(0.01)) if pd.api.types.is_numeric_dtype(s) else None,
            p99=float(s.quantile(0.99)) if pd.api.types.is_numeric_dtype(s) else None,
        )
        out.append(p)
    return out


def diff_profiles(ref: list[ColumnProfile], cur: list[ColumnProfile]) -> list[dict]:
    ref_by_col = {p.column: p for p in ref}
    deltas = []
    for c in cur:
        r = ref_by_col.get(c.column)
        if r is None:
            deltas.append({"column": c.column, "alert": "new_column"})
            continue
        d = {"column": c.column}
        if abs((c.null_rate or 0) - (r.null_rate or 0)) > 0.05:
            d["null_rate_delta"] = round((c.null_rate or 0) - (r.null_rate or 0), 3)
        if c.mean is not None and r.mean is not None and r.std and \
                abs(c.mean - r.mean) > 3 * r.std:
            d["mean_shift_sigma"] = round((c.mean - r.mean) / r.std, 2)
        if len(d) > 1:
            deltas.append(d)
    return deltas
