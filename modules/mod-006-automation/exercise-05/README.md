# Production Pipeline — Solution

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-006-automation/exercises/exercise-05-production-ml-pipeline.md).

Full pipeline: validate (GE) → train → evaluate (with floor) → promote → deploy → smoke test.

Each task raises `AirflowFailException` for unrecoverable errors (skip retry).
Use `BranchPythonOperator` / `@task.branch` if you want conditional skip-paths instead.
