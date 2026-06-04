# AutoML Pipeline — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-010-advanced-topics/exercises/exercise-04-automl-pipeline.md).

```bash
pip install optuna mlflow scikit-learn
python automl.py
```

This is a minimal AutoML loop. For production, see auto-sklearn, FLAML, or
H2O AutoML — they add ensembling + stacking + warm-starting that handwritten
loops miss.
