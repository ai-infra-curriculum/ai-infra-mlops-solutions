"""Optuna HPO with every trial logged to MLflow."""
import mlflow
import mlflow.sklearn
import optuna
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

mlflow.set_experiment("iris-hpo")


def objective(trial: optuna.Trial) -> float:
    n = trial.suggest_int("n_estimators", 50, 500)
    d = trial.suggest_int("max_depth", 4, 32)
    leaf = trial.suggest_int("min_samples_leaf", 1, 10)

    with mlflow.start_run(nested=True, run_name=f"trial-{trial.number}"):
        model = RandomForestClassifier(
            n_estimators=n, max_depth=d, min_samples_leaf=leaf, random_state=0,
        )
        model.fit(Xtr, ytr)
        acc = accuracy_score(yte, model.predict(Xte))
        mlflow.log_params({"n_estimators": n, "max_depth": d, "min_samples_leaf": leaf})
        mlflow.log_metric("accuracy", acc)
        return acc


def main():
    with mlflow.start_run(run_name="hpo-parent"):
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=50)
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_accuracy", study.best_value)


if __name__ == "__main__":
    main()
