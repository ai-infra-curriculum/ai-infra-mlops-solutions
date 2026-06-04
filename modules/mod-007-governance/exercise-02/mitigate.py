"""Bias mitigation: pre/in/post-processing examples."""
from __future__ import annotations

import numpy as np
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
from sklearn.linear_model import LogisticRegression


def in_process_demographic_parity(X, y, sensitive):
    """Train under a demographic-parity constraint."""
    base = LogisticRegression(max_iter=1000)
    mitigator = ExponentiatedGradient(base, constraints=DemographicParity())
    mitigator.fit(X, y, sensitive_features=sensitive)
    return mitigator


def post_process_threshold(base_model, X_train, y_train, sensitive_train):
    """Post-hoc threshold tuning per group for equalized odds."""
    to = ThresholdOptimizer(
        estimator=base_model,
        constraints="equalized_odds",
        prefit=True,
    )
    to.fit(X_train, y_train, sensitive_features=sensitive_train)
    return to


def reweight_samples(y, sensitive):
    """Sample weights so under-represented (group, label) combos get more weight."""
    import pandas as pd
    df = pd.DataFrame({"y": y, "g": sensitive})
    counts = df.groupby(["g", "y"]).size()
    weights = (1.0 / counts).reindex(list(zip(sensitive, y))).to_numpy()
    return weights / weights.mean()
