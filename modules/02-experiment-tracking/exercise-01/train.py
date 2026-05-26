"""MLflow tracking fundamentals: autolog + custom metrics + signature."""
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import train_test_split


mlflow.set_experiment("iris-tracking")
mlflow.sklearn.autolog()


def main():
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

    with mlflow.start_run(run_name="rf-200-12"):
        model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=0)
        model.fit(Xtr, ytr)
        preds = model.predict(Xte)

        mlflow.log_metric("f1_macro", f1_score(yte, preds, average="macro"))
        mlflow.log_metric("accuracy", accuracy_score(yte, preds))

        sig = infer_signature(Xte, preds)
        mlflow.sklearn.log_model(model, "model", signature=sig,
                                  input_example=Xte[:3],
                                  registered_model_name="iris-rf")


if __name__ == "__main__":
    main()
