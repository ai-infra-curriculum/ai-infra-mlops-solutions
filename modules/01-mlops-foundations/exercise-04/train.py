"""Minimal training script logging to MLflow."""
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


mlflow.set_experiment("iris-baseline")


def main():
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

    with mlflow.start_run(run_name="logreg-c1") as run:
        mlflow.log_param("C", 1.0)
        model = LogisticRegression(C=1.0, max_iter=200).fit(Xtr, ytr)
        preds = model.predict(Xte)
        mlflow.log_metric("accuracy", accuracy_score(yte, preds))
        mlflow.sklearn.log_model(model, "model")
        print(f"run_id={run.info.run_id}")


if __name__ == "__main__":
    main()
