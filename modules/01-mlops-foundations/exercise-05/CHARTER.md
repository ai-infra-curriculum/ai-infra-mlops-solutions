# MLOps Team Charter — Reference

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/01-mlops-foundations/exercises/exercise-05-write-an-mlops-team-charter.md).

See the more detailed charter at
[engineer-solutions/mod-106 ex-14 (ml-platform-operating-model)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-14-ml-platform-operating-model/CHARTER.md).

## Abbreviated charter

### Mission
Make it easy and safe for data scientists + product engineers to ship and operate ML in production.

### What we own
- Tracking + registry (MLflow)
- Feature store (Feast)
- Serving runtime (standardized container + autoscaling)
- Pipeline framework (Airflow + templates)
- Drift + bias monitoring (dashboards + alerts)
- CI/CD plumbing (GHA templates for ML)
- Cost attribution + budgets

### What we DO NOT own
- Model architecture / hyperparameter choices (data scientists)
- Business metric definitions (product + analytics)
- Feature semantics / data correctness (data eng + product)
- Quarterly model retraining schedules (model owners)

### Engagement model
- **Self-serve** (60%): existing templates, zero tickets
- **Office hours** (30%): weekly 1hr drop-in
- **Project intake** (10%): >2-week effort; ~6-week SLA

### Support tiers
- **Tier 1 (on-call)**: 24/7 paging for outages; 30min response
- **Tier 2 (working hours)**: Slack; same-day
- **Tier 3 (project queue)**: feature requests; quarterly planning

### Success metrics
| Metric | Target |
|---|---|
| Time "trained" → "in prod" using platform | < 1 week |
| MTBF for serving infra | > 30 days |
| MTTR for platform incidents | < 1 hour |
| Self-serve adoption | > 80% of new models |
| Platform model coverage with cost tags | 100% |

### Failure modes
- Gatekeeper trap
- Custom-everywhere
- Slow batching (6-month roadmap, no quick wins)
