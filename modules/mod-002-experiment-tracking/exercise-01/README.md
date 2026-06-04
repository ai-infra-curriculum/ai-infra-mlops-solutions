# MLflow Tracking Fundamentals — Solution

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-002-experiment-tracking/exercises/exercise-01-mlflow-tracking-fundamentals.md).

Companion: [engineer-solutions/mod-106 ex-02](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-02-mlflow-tracking-deep-dive) for full Postgres + MinIO compose stack.

```bash
docker compose -f ../../mod-001-mlops-foundations/exercise-04/docker-compose.yaml up -d
export MLFLOW_TRACKING_URI=http://localhost:5000
python train.py
```
