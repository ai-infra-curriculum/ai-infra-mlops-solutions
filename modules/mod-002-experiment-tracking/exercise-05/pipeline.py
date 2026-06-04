"""End-to-end pipeline: ingest → train → register → promote → serve."""
import subprocess

import mlflow
from mlflow.tracking import MlflowClient


def train():
    subprocess.run(["python", "../exercise-01/train.py"], check=True)


def promote_if_better():
    c = MlflowClient()
    versions = c.search_model_versions("name='iris-rf'")
    latest = max(versions, key=lambda v: int(v.version))
    new_acc = c.get_run(latest.run_id).data.metrics.get("accuracy", 0)

    prod = c.get_latest_versions("iris-rf", stages=["Production"])
    prod_acc = c.get_run(prod[0].run_id).data.metrics.get("accuracy", 0) if prod else 0

    if new_acc >= prod_acc - 0.005:
        c.transition_model_version_stage(
            name="iris-rf", version=latest.version,
            stage="Production", archive_existing_versions=True,
        )
        print(f"promoted v{latest.version}: {new_acc:.4f} >= {prod_acc:.4f} - 0.005")
    else:
        print(f"NOT promoted: {new_acc:.4f} < {prod_acc:.4f} - 0.005")


if __name__ == "__main__":
    train()
    promote_if_better()
