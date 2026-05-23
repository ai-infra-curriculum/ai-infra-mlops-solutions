"""FastAPI serving wrapper exposing /predict + /metrics."""
import os

import mlflow
import numpy as np
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, make_asgi_app

PREDICTIONS = Counter("predictions_total", "predictions")
LATENCY = Histogram("prediction_latency_seconds", "latency")

app = FastAPI()
app.mount("/metrics", make_asgi_app())

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
model = mlflow.sklearn.load_model("models:/iris-baseline/Production")


@app.get("/health")
def health(): return {"ok": True}


@app.get("/predict")
def predict(value: float):
    with LATENCY.time():
        x = np.array([[value, value, value, value]])
        pred = int(model.predict(x)[0])
        PREDICTIONS.inc()
        return {"prediction": pred}
