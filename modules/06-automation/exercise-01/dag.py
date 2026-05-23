"""Airflow ML training DAG with TaskFlow API."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task


DEFAULT = {
    "owner": "ml-platform",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "sla": timedelta(hours=4),
}


@dag(dag_id="ml_training", start_date=datetime(2026, 1, 1),
     schedule="0 4 * * *", catchup=False, default_args=DEFAULT)
def pipeline():
    @task
    def ingest() -> str:
        return "s3://datalake/raw/2026-05-23/"

    @task
    def validate(path: str) -> dict:
        return {"path": path, "rows": 1_000_000, "pass": True}

    @task.branch
    def quality_gate(report: dict) -> str:
        return "train" if report["pass"] else "skip"

    @task
    def train(report: dict) -> str:
        return f"trained on {report['path']}"

    @task
    def skip(): pass

    @task
    def evaluate(model: str) -> dict:
        return {"model": model, "accuracy": 0.91}

    @task
    def deploy(eval_result: dict) -> str:
        return f"deployed: {eval_result['model']}"

    r = validate(ingest())
    g = quality_gate(r)
    g >> [skip(), deploy(evaluate(train(r)))]


pipeline()
