# HPO with Tracking — Solution

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-002-experiment-tracking/exercises/exercise-03-hyperparameter-optimization-with-tracking.md).

Optuna sweep with every trial nested under a parent MLflow run. Use the UI's
parallel-coordinates plot to explore parameter vs metric relationships.

```bash
pip install optuna mlflow
python hpo.py
mlflow ui   # → experiments → iris-hpo → compare runs
```
