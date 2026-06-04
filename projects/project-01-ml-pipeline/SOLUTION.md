# SOLUTION — Customer Churn ML Pipeline

> Read this *after* attempting the learning-side project. This file
> explains the architectural reasoning behind the reference
> implementation and the deliberate trade-offs.

## What problem this solves

A churn-prediction system at any non-trivial scale fails for one of three
reasons more often than the modeling itself:

1. **Data quality drift** — the training-time distribution and
   serving-time distribution disagree, and you only notice when the
   business notices.
2. **Feature/serving skew** — the SQL that produced training features
   and the Python that produces serving features quietly diverge.
3. **Model rot** — the model degrades because the world changed (a new
   product launched, a pricing change shifted behavior), not because
   the code did.

The reference implementation addresses all three explicitly, with named
modules and verifiable checkpoints.

## Architectural decisions and *why*

### Multi-source ingestion (CSV / Postgres / REST / Kafka) behind a
common interface

Each connector returns to the same canonical schema before downstream
code touches it. This is the only realistic way to keep the pipeline
testable: the rest of the system has one input shape regardless of
where the data came from.

### Great Expectations for validation, not custom asserts

Hand-rolled validation tends to grow brittle. GE expectations are
versioned, diffed in code review, and produce a structured report
artifact you can store in the run record. The 23 rules in the
reference are a *floor*, not a target.

### Feature engineering in 7 categories, fed through a feature store

Putting feature transforms in a feature store (rather than inline in
the training script) is the single best defense against
training/serving skew. The serving API reads the same feature
definitions as the training job.

### Four-algorithm bake-off with Optuna, not a single chosen algorithm

Modelers should not pre-decide between LR, RF, XGBoost, LightGBM until
they have evidence on *this* dataset. The bake-off shows the cost of
"obvious" choices and produces a comparison artifact for stakeholder
review.

### Evidently for drift detection, separate from prediction monitoring

Data drift and prediction drift are different signals. The pipeline
treats them as separate alerts with separate thresholds, because they
imply different remediations (re-collect data vs. retrain).

### docker-compose as the runtime, not Kubernetes

This project is a *pipeline*, not a platform. Adding Kubernetes here
trades reproducibility cost for operational complexity that doesn't
serve the learning goal. The platform-style deployment lives in the
engineer-solutions Helm/k8s exercises.

## How to read the code

Execution-order reading path:

1. `src/data/` — ingestion + GE validation.
2. `src/features/` — feature transforms + the feature-store contract.
3. `src/models/` — training loop, Optuna tuning, the bake-off harness.
4. `src/monitoring/` — drift detection wiring.
5. `src/api/` — serving surface that reads the same feature definitions
   as `src/features/`.
6. `tests/` — pay attention to the integration tests; they cover the
   training/serving skew case.

## What's deliberately simplified

- **No feature backfill story.** New features cannot be added with
  historical coverage without re-running pipelines; the production
  pattern (backfill jobs, point-in-time correctness) is covered in
  `engineer-solutions/mod-105 exercise-09-backfill-safety`.
- **No model registry promotion gate.** The model is registered but
  there is no human-in-the-loop approval step. See
  `mlops-solutions/modules/mod-007-governance/` for the missing piece.
- **No multi-environment promotion.** Single environment only.

## Cross-references

| Topic | Deeper reference |
|---|---|
| Pipeline architecture | `engineer-solutions/mod-105 exercise-01` |
| Backfill safety | `engineer-solutions/mod-105 exercise-09` |
| Production model serving | `engineer-solutions/mod-101 exercise-08` |
| Deployment strategies (canary/blue-green) | `engineer-solutions/mod-106 exercise-08` |
| Model governance | `mlops-solutions/modules/mod-007-governance/` |

## Production gap checklist

- [ ] Feature backfill workflow with point-in-time correctness
- [ ] Multi-environment promotion (dev → staging → prod)
- [ ] Model registry promotion gate with human approval
- [ ] Per-tenant model isolation if multi-tenant
- [ ] Cost attribution per training run
- [ ] Automated retraining cadence tied to drift thresholds

## Time budget

- **Skim**: 1 hour.
- **Deep**: 1 week — bring the stack up, intentionally break the
  feature schema, observe how GE + drift detection catch it.
