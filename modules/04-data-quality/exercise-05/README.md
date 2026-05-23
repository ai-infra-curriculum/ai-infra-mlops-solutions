# End-to-End DQ Pipeline — Solution

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/04-data-quality/exercises/exercise-05-end-to-end-data-quality-pipeline.md).

Chains schema → GE → stats → profile-diff. Fail fast at the first failing stage,
warn on soft signals (drift), pass through otherwise. Wire into Airflow as a
short-circuit task before training.
