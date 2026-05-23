"""Kubeflow Pipeline (KFP v2) — typed components + ParallelFor."""
from __future__ import annotations

from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model, Metrics


@dsl.component(packages_to_install=["pandas", "scikit-learn"])
def ingest_op(out: Output[Dataset]):
    import pandas as pd
    from sklearn.datasets import load_iris
    df = pd.DataFrame(load_iris(as_frame=True).frame)
    df.to_csv(out.path, index=False)


@dsl.component(packages_to_install=["pandas", "scikit-learn", "joblib"])
def train_op(data: Input[Dataset], model: Output[Model], metrics: Output[Metrics]):
    import pandas as pd
    from joblib import dump
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(data.path)
    X = df.drop(columns="target")
    y = df["target"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0)
    clf = RandomForestClassifier(n_estimators=200).fit(Xtr, ytr)
    dump(clf, model.path)
    metrics.log_metric("accuracy", float(accuracy_score(yte, clf.predict(Xte))))


@dsl.pipeline(name="iris-pipeline")
def iris_pipeline():
    data = ingest_op()
    train_op(data=data.outputs["out"])


if __name__ == "__main__":
    from kfp import compiler
    compiler.Compiler().compile(iris_pipeline, "iris_pipeline.yaml")
