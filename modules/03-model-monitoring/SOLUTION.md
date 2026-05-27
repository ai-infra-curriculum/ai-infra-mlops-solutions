# SOLUTION — Model Monitoring

> Read this *after* you have wired up the reference model-
> monitoring stack. This document explains *why* the monitoring
> patterns are what they are for production models.

## What this module is really teaching

Model monitoring is a superset of application monitoring. The
extra concerns:

- Performance metrics (accuracy / precision / recall) that need
  ground truth, which arrives days later.
- Data drift detection on the inputs.
- Prediction-distribution monitoring on the outputs.
- Per-segment fairness checks.

The reference solutions wire these into the same observability
stack as application metrics.

## Architectural decisions and *why*

### Decision 1: Real-time + offline monitoring as separate paths

Live latency, error rate, and prediction-rate are tracked in
Prometheus (real-time). Accuracy, drift, and fairness run on
nightly batch (offline). The reason: ground truth arrives
late; real-time accuracy is usually impossible.

### Decision 2: Drift detection on the input distribution, per
feature

Per-feature KS-test (continuous) or chi-square (categorical)
p-values are tracked over rolling windows. Aggregate drift
hides per-feature problems; per-feature drift surfaces them.

### Decision 3: Prediction distribution as a leading indicator

Output-distribution drift (the model is suddenly predicting
99% positive class) often precedes ground-truth-confirmed
quality degradation by days. Alert on it.

### Decision 4: Per-segment fairness checks on labeled samples

The reference computes per-segment (race / region / customer-
tier) accuracy on the labeled-evaluation set, with alerts when
disparities exceed thresholds.

### Decision 5: Single dashboard per registered model

Each model gets its own Grafana dashboard. The reason: shared
dashboards become unreadable past three models.

## Trade-offs we deliberately accepted

- Statistical-test thresholds tuned conservatively (more
  alerts is the safer default than fewer).
- Per-segment fairness on labeled data only (real-time
  unsupervised fairness is unsolved).
- Single dashboard per model means N dashboards to maintain.

## Common mistakes graders see

1. **Monitoring only on real-time signals**: misses concept
   drift completely.
2. **Aggregate drift scores**: hides per-feature problems.
3. **Drift alerts without runbook**: on-caller doesn't know
   what to do.
4. **Fairness checks treated as a one-time audit**: drift
   over time is invisible.

## When to go beyond this implementation

- Adopt **EvidentlyAI** or **Whylogs** for richer drift
  reports.
- Add **counterfactual fairness** analysis for high-stakes
  models.

## Related curriculum touchpoints

- ``engineer/mod-108-monitoring-observability`` — observability
  foundation.
- ``ml-platform/mod-008-observability`` — platform-tier
  observability.
