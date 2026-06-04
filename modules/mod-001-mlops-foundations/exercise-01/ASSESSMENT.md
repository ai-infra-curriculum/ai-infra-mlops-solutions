# MLOps Maturity Assessment — Reference

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-01-mlops-maturity-assessment.md).

See the equivalent deep dive in
[engineer-solutions/mod-106 exercise-01-mlops-maturity-assessment](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-01-mlops-maturity-assessment)
for a filled-in assessment + 6-month roadmap.

## Sample (abbreviated)

**Team profile:** mid-size data team, 4 ML engineers, 3 prod models, deploys via manual notebooks.

### Current level: **1 (Manual ML pipeline)**

| Capability | Current | Target (12mo) |
|---|---|---|
| Data validation | manual | automated (Great Expectations) |
| Feature engineering | per-notebook | feature store (Feast) |
| Experiment tracking | spreadsheet | MLflow |
| Model registry | filesystem | MLflow registry |
| CI/CD for models | none | GitHub Actions + canary |
| Production monitoring | latency only | drift + bias + slice metrics |
| Triggered retraining | manual | event + cron driven |

### Top 5 next investments (priority order)

1. **MLflow tracking server** (2 weeks) — foundation for everything else
2. **DVC for data + model versioning** (3 weeks)
3. **Model registry + promotion workflow** (2 weeks)
4. **CI for model code** (2 weeks)
5. **Production drift monitoring** (4 weeks)

### 6-month roadmap

| Month | Investment | Owner | Outcome |
|---|---|---|---|
| 1 | MLflow + tracking server | platform | every training run logged |
| 1-2 | DVC pipeline (proof) | ML eng A | reproducible training |
| 2 | Model registry workflow | ML eng B | manual promotion w/ history |
| 3 | CI pipeline | platform | regressions caught at PR time |
| 3-4 | Feature store | ML eng C | skew eliminated |
| 4-5 | Drift + monitoring | platform | dashboard + alerts |
| 6 | Canary deployments | platform | safer rollouts |
