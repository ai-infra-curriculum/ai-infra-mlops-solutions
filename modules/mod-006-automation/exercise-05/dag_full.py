"""Production pipeline: validate → train → eval → promote → deploy → smoke test."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException


@dag(dag_id="ml_production",
     start_date=datetime(2026, 1, 1),
     schedule="0 5 * * *",
     catchup=False,
     default_args={"owner": "ml-platform", "retries": 3,
                    "retry_delay": timedelta(minutes=2),
                    "sla": timedelta(hours=4)})
def pipeline():

    @task
    def validate():
        # Run GE checkpoint; raise AirflowFailException on failure
        return {"status": "ok"}

    @task
    def train(_validated):
        return {"run_id": "abc123", "accuracy": 0.91}

    @task
    def evaluate(model):
        if model["accuracy"] < 0.85:
            raise AirflowFailException(f"accuracy {model['accuracy']} below floor 0.85")
        return model

    @task
    def promote(model):
        return {"version": 42}

    @task
    def deploy(version):
        return {"deploy_status": "ok"}

    @task
    def smoke_test(_deployed):
        import httpx
        r = httpx.post("https://iris-api.prod/predict",
                        json={"features": [5.1, 3.5, 1.4, 0.2]}, timeout=10)
        if r.status_code != 200:
            raise AirflowFailException(f"smoke test failed: {r.status_code}")

    smoke_test(deploy(promote(evaluate(train(validate())))))


pipeline()
