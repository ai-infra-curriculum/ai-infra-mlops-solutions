# Minimal MLOps Stack — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-04-build-a-minimal-mlops-stack-with-free-tools.md).

## Layout

```
exercise-04/
├── README.md
├── docker-compose.yaml      # MLflow + Postgres + MinIO + Prometheus + Grafana
├── train.py                  # logs to MLflow
├── app.py                    # FastAPI + /metrics
└── grafana-dashboard.json
```

## Run

```bash
docker compose up -d
export MLFLOW_TRACKING_URI=http://localhost:5000
python train.py
uvicorn app:app --host 0.0.0.0 --port 8000
curl localhost:8000/predict?value=1.5
open http://localhost:3000  # Grafana
```
