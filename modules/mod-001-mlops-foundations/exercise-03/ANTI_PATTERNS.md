# MLOps Anti-Patterns Review — Reference

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-03-spot-the-mlops-anti-patterns.md).

## The 8 anti-patterns + fixes

| # | Anti-pattern | Why it's a problem | Fix |
|---|---|---|---|
| 1 | Manual data copy to laptop | Source-of-truth bypass; data leaves the security perimeter | Stage in a versioned warehouse; train against it |
| 2 | Notebook training | No code review, no CI, hard to reproduce | Convert to a script; gate via PR + tests |
| 3 | Google-Drive model store | No versioning, no access control, no audit | Model registry (MLflow / Vertex / etc.) |
| 4 | Manual `.pkl` → prod | No traceability ("which model is in prod?") | Registry-driven deploys with stages |
| 5 | "Container up" as monitoring | Misses degradation; you only learn about outages | Prometheus model metrics + drift dashboard |
| 6 | No data lineage | Can't reproduce or retrain | Capture dataset hash + DVC + lineage |
| 7 | No retraining cadence | Model degrades silently over months | Scheduled retrain + drift-triggered retrain |
| 8 | No automated tests on model code | Regressions sneak in | CI: lint + unit + integration tests on the training pipeline |

## Ordered by blast radius

1. **No data lineage** — if (4) blocks deployment, (6) blocks recovery
2. **Manual `.pkl` deploy** — single-point human bottleneck and source of incidents
3. **No monitoring** — slow-burn user impact
4. **Notebook training** — slows iteration; root cause of many secondary issues
5. ...

## One-pager (case for fixing #1 first)

> Without lineage we can't reproduce a model. Without reproduction we can't retrain
> safely. Without safe retraining the model drifts until it embarrasses us. A
> 2-week investment in DVC + MLflow buys us reproducibility forever.

## Companion

[engineer-solutions/mod-106 ex-13 (reproducibility-audit)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-13-reproducibility-audit)
has a working `audit_runner.py` that scores reproducibility per model.
