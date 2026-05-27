# SOLUTION — Production Operations

> Read this *after* you have stood up the reference production-
> ops infrastructure. This document explains *why* MLOps day-2
> patterns are what they are.

## What this module is really teaching

The day-2 ops layer is where MLOps differs most from generic
ops:
- Inference SLOs that span model quality + latency + throughput.
- Capacity planning that accounts for GPU economics.
- On-call patterns tuned for ML failure modes.
- Cost attribution per model / team.

## Architectural decisions and *why*

### Decision 1: SLOs per registered model

Each production model has its own SLO (latency p95, error rate,
inference accuracy on a shadow set). The reason: models have
different cost / quality / latency profiles; one global SLO is
wrong for any of them.

### Decision 2: GPU capacity planning per quarter

GPU capacity is planned quarterly with explicit demand forecasts
per model. The reason: spot GPU availability is volatile; six-
month-ahead reservations save 30-50%; one-week-ahead provisioning
pays sticker price.

### Decision 3: ML-specific on-call playbook

The on-call playbook has dedicated runbooks for:
- Model quality regression.
- Inference latency degradation.
- Inference cluster OOM.
- Training job stuck / failed.
- Data pipeline freshness alarm.

Generic SRE playbooks miss these.

### Decision 4: Cost attribution down to the model level

Every inference and training cost is attributed to a model + team
+ environment. The reason: ML costs grow fast; without
attribution, the cost conversation devolves into mystery.

### Decision 5: Capacity utilization alerting

Two alerts: high utilization (over 80% sustained) signals
saturation; low utilization (under 30% sustained) signals waste.
The reference alerts on both because both matter at scale.

## Trade-offs we deliberately accepted

- Per-model SLOs are a maintenance tax (we pay it).
- Capacity planning requires forecasting (sometimes wrong).
- Cost attribution depends on tagging discipline.

## Common mistakes graders see

1. **Generic SLOs**: don't distinguish models with different
   shapes.
2. **No GPU capacity forecasting**: emergency provisioning at
   sticker price.
3. **Cost attribution missing the GPU bill**: training jobs
   show up as a single line item, not per-team.
4. **On-call without ML-specific runbooks**: SRE picks up the
   page and has no idea what an "AUC regression" alert means.

## When to go beyond this implementation

- Adopt **FinOps for ML** as a discipline with dedicated
  ownership.
- Move to **multi-region** for latency-sensitive global users.
- Add **chaos engineering** specific to ML failure modes.

## Related curriculum touchpoints

- ``senior-engineer/mod-207-observability-sre`` — the SRE
  foundations.
- ``architect/projects/project-304-cost-finops`` —
  architectural FinOps.
