"""Airflow DAG that integrates with MLflow tracking + registry."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(dag_id="ml_training_mlflow",
     start_date=datetime(2026, 1, 1),
     schedule="0 4 * * *",
     catchup=False,
     default_args={"retries": 2, "retry_delay": timedelta(minutes=2)})
def pipeline():

    @task
    def train_log() -> str:
        import mlflow, mlflow.sklearn
        from sklearn.datasets import load_iris
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split

        mlflow.set_experiment("iris-daily")
        X, y = load_iris(return_X_y=True)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
        with mlflow.start_run() as run:
            model = RandomForestClassifier(n_estimators=200).fit(Xtr, ytr)
            mlflow.log_metric("accuracy", model.score(Xte, yte))
            mlflow.sklearn.log_model(model, "model", registered_model_name="iris-rf")
            return run.info.run_id

    @task
    def evaluate_and_promote(run_id: str):
        from mlflow.tracking import MlflowClient
        c = MlflowClient()
        versions = c.search_model_versions(f"run_id='{run_id}'")
        v = max(versions, key=lambda x: int(x.version))
        acc = c.get_run(run_id).data.metrics["accuracy"]
        prod = c.get_latest_versions("iris-rf", stages=["Production"])
        prod_acc = c.get_run(prod[0].run_id).data.metrics["accuracy"] if prod else 0
        if acc >= prod_acc - 0.005:
            c.transition_model_version_stage(
                "iris-rf", v.version, "Production", archive_existing_versions=True,
            )

    evaluate_and_promote(train_log())


pipeline()
