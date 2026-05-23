"""AutoML loop: Optuna over model class + hyperparameters, MLflow-tracked."""
import mlflow
import optuna
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

mlflow.set_experiment("automl-iris")


def build_model(trial: optuna.Trial):
    clf = trial.suggest_categorical("clf", ["rf", "gbm", "logreg"])
    if clf == "rf":
        return RandomForestClassifier(
            n_estimators=trial.suggest_int("n_estimators", 50, 500),
            max_depth=trial.suggest_int("max_depth", 3, 20),
            random_state=0,
        )
    if clf == "gbm":
        return GradientBoostingClassifier(
            n_estimators=trial.suggest_int("n_estimators", 50, 300),
            learning_rate=trial.suggest_float("lr", 0.01, 0.3),
            random_state=0,
        )
    return LogisticRegression(
        C=trial.suggest_float("C", 0.01, 100, log=True), max_iter=1000,
    )


def objective(trial: optuna.Trial) -> float:
    with mlflow.start_run(nested=True):
        model = build_model(trial)
        model.fit(Xtr, ytr)
        acc = accuracy_score(yte, model.predict(Xte))
        mlflow.log_params(trial.params)
        mlflow.log_metric("accuracy", acc)
        return acc


def main():
    with mlflow.start_run(run_name="automl-parent"):
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=30)
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_accuracy", study.best_value)


if __name__ == "__main__":
    main()
