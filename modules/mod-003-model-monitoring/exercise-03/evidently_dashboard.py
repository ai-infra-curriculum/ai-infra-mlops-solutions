"""Evidently AI: build drift + performance report + serve a dashboard."""
import numpy as np
import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset


def main():
    rng = np.random.default_rng(0)
    ref = pd.DataFrame({
        "feat_a": rng.normal(0, 1, 1000),
        "feat_b": rng.normal(5, 2, 1000),
        "target": rng.integers(0, 2, 1000),
        "prediction": rng.integers(0, 2, 1000),
    })
    cur = pd.DataFrame({
        "feat_a": rng.normal(0.3, 1, 1000),    # mild drift
        "feat_b": rng.normal(7, 2, 1000),       # significant drift
        "target": rng.integers(0, 2, 1000),
        "prediction": rng.integers(0, 2, 1000),
    })

    mapping = ColumnMapping(target="target", prediction="prediction",
                             numerical_features=["feat_a", "feat_b"])

    report = Report(metrics=[DataDriftPreset(), ClassificationPreset()])
    report.run(reference_data=ref, current_data=cur, column_mapping=mapping)
    report.save_html("report.html")
    print("wrote report.html — open in a browser")


if __name__ == "__main__":
    main()
