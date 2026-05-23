"""KS-test-based data drift detection for numerical features."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class DriftResult:
    feature: str
    ks_statistic: float
    p_value: float
    is_drifted: bool


class KSDriftDetector:
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha

    def detect(self, reference: pd.DataFrame, current: pd.DataFrame) -> list[DriftResult]:
        results = []
        for col in reference.select_dtypes(include="number").columns:
            stat, p = stats.ks_2samp(reference[col].dropna(), current[col].dropna())
            results.append(DriftResult(col, float(stat), float(p), p < self.alpha))
        return results


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    ref = pd.DataFrame({"feat_a": rng.normal(0, 1, 5000), "feat_b": rng.normal(5, 2, 5000)})
    cur = pd.DataFrame({"feat_a": rng.normal(0, 1, 5000), "feat_b": rng.normal(7, 2, 5000)})
    for r in KSDriftDetector().detect(ref, cur):
        flag = "⚠ DRIFT" if r.is_drifted else "ok"
        print(f"{r.feature:<10}  ks={r.ks_statistic:.3f}  p={r.p_value:.4f}  {flag}")
