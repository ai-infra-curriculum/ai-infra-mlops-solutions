"""End-to-end monitoring loop: pull predictions, compute drift + perf, expose /metrics."""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
from prometheus_client import Gauge, Histogram, start_http_server

import sys
sys.path.insert(0, "../exercise-02")
from psi import psi


DRIFT_PSI = Gauge("model_drift_psi", "PSI per feature", ["feature"])
PRED_DIST = Histogram("model_prediction_distribution", "Prediction value",
                       buckets=(0, 0.25, 0.5, 0.75, 1.0))


def load_reference() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "feat_a": rng.normal(0, 1, 5000),
        "feat_b": rng.normal(5, 2, 5000),
    })


def load_current_window() -> pd.DataFrame:
    """In production: query the inference log store (e.g., Kafka or warehouse)."""
    rng = np.random.default_rng()
    return pd.DataFrame({
        "feat_a": rng.normal(0.2, 1, 1000),
        "feat_b": rng.normal(6, 2, 1000),
    })


def main():
    start_http_server(8000)
    ref = load_reference()
    while True:
        cur = load_current_window()
        for col in ref.columns:
            DRIFT_PSI.labels(feature=col).set(psi(ref[col].to_numpy(), cur[col].to_numpy()))
        time.sleep(60)


if __name__ == "__main__":
    main()
