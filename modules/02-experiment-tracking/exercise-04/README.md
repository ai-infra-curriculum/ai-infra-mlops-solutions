# Advanced MLflow (Pyfunc) — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/02-experiment-tracking/exercises/exercise-04-advanced-mlflow-features.md).

Pyfunc lets a model carry custom preprocessing with it; downstream serving code
doesn't need to know about input clipping or feature transforms.

```bash
python pyfunc_model.py
mlflow models serve -m models:/iris-pyfunc/Production --port 5001
```
