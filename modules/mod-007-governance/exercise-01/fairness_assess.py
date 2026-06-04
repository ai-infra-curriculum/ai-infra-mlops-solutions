"""Fairness assessment via fairlearn."""
from __future__ import annotations

import numpy as np
from fairlearn.metrics import (MetricFrame, demographic_parity_difference,
                                equalized_odds_difference, selection_rate)
from sklearn.metrics import accuracy_score


def assess(y_true: np.ndarray, y_pred: np.ndarray, sensitive: np.ndarray) -> dict:
    frame = MetricFrame(
        metrics={"accuracy": accuracy_score, "selection_rate": selection_rate},
        y_true=y_true, y_pred=y_pred, sensitive_features=sensitive,
    )
    return {
        "by_group": frame.by_group.to_dict(),
        "demographic_parity_diff": float(demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensitive)),
        "equalized_odds_diff": float(equalized_odds_difference(
            y_true, y_pred, sensitive_features=sensitive)),
    }


if __name__ == "__main__":
    import json
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 2, 1000)
    y_pred = rng.integers(0, 2, 1000)
    sensitive = rng.choice(["a", "b"], 1000)
    print(json.dumps(assess(y_true, y_pred, sensitive), indent=2))
