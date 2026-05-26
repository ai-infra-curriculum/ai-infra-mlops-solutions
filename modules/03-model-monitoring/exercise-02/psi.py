"""Population Stability Index implementation + interpretation guide.

PSI thresholds (industry convention):
- < 0.1  : no significant change
- 0.1-0.25 : moderate shift; investigate
- > 0.25 : significant shift; act
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """PSI between two 1-D arrays via equal-width bins."""
    bin_edges = np.linspace(reference.min(), reference.max(), bins + 1)
    ref_counts, _ = np.histogram(reference, bins=bin_edges)
    cur_counts, _ = np.histogram(current, bins=bin_edges)
    ref_pct = np.where(ref_counts == 0, 1e-6, ref_counts / ref_counts.sum())
    cur_pct = np.where(cur_counts == 0, 1e-6, cur_counts / cur_counts.sum())
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def psi_report(reference: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in reference.select_dtypes(include="number").columns:
        val = psi(reference[col].dropna().to_numpy(),
                   current[col].dropna().to_numpy())
        status = "no_change" if val < 0.1 else "moderate" if val < 0.25 else "significant"
        rows.append({"feature": col, "psi": round(val, 4), "status": status})
    return pd.DataFrame(rows).sort_values("psi", ascending=False)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    ref = pd.DataFrame({
        "income":  rng.lognormal(mean=10, sigma=0.5, size=5000),
        "age":     rng.normal(40, 10, 5000),
        "balance": rng.normal(1000, 500, 5000),
    })
    cur = pd.DataFrame({
        "income":  rng.lognormal(mean=10.3, sigma=0.5, size=5000),    # drift
        "age":     rng.normal(40, 10, 5000),                            # no change
        "balance": rng.normal(800, 600, 5000),                          # moderate
    })
    print(psi_report(ref, cur).to_string(index=False))
