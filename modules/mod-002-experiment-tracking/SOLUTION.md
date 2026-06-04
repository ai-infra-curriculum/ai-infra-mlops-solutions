# SOLUTION — Experiment Tracking

> Read this *after* you have built the reference experiment-
> tracking infrastructure. This document explains *why* the
> tracking choices are what they are.

## What this module is really teaching

Experiment tracking is the line between "research" and
"reproducible engineering." The discipline isn't choosing
MLflow vs. W&B — it's making sure every interesting run is
logged with enough context to be reproduced six months later.

## Architectural decisions and *why*

### Decision 1: Log everything by default, prune later

Reference training scripts log all hyperparameters, all
metrics-of-interest, and key artifacts (model, evaluation
plots, config file). Storage is cheap; missing context is
expensive.

### Decision 2: Parent/child runs for hyperparameter sweeps

Sweeps use MLflow's parent/child run hierarchy rather than flat
runs with a sweep_id tag. The reason: the UI shows the
relationship and aggregate-best is a single query.

### Decision 3: Custom metrics structured as
``{stage}/{metric_name}``

Metric names follow a convention: ``train/loss``,
``val/accuracy``, ``test/f1``. The reason: grouping in the UI
relies on the prefix; ad-hoc naming makes dashboards
unusable.

### Decision 4: Artifact upload, not just paths

Models, evaluation plots, and small reference data files are
uploaded as MLflow artifacts. The reason: paths break when the
data store is reorganized; artifacts survive.

### Decision 5: Git SHA captured in every run

Every run records its source Git commit. The reason: a metric
without its code is uninterpretable.

## Trade-offs we deliberately accepted

- MLflow over W&B (OSS, self-hostable).
- Auto-logging not used (too noisy at scale).
- Per-experiment ACLs not enforced at this tier.

## Common mistakes graders see

1. **Logging only the final metric**: training-curve insight
   is lost.
2. **Hyperparameters logged as a single JSON blob**: makes
   parameter-sweep searches impossible.
3. **No experiment naming convention**: 500 experiments named
   "test" produce a useless catalog.
4. **Logging non-reproducible randomness** (different seed
   per run unrecorded).

## When to go beyond this implementation

- Adopt **Weights & Biases** if the richer UI / sweeps tooling
  justifies the SaaS spend.
- Move to **dataset versioning** alongside experiment tracking.

## Related curriculum touchpoints

- ``mlops/mod-001-mlops-foundations`` — registry foundation.
- ``mlops/mod-003-model-monitoring`` — observability of registered
  models.
