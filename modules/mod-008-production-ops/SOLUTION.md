# SOLUTION — Production Operations (module index)

> Read this *after* you have stood up the reference production-ops
> infrastructure. This file is the module-level index; the
> exercise-specific worked answers, rubrics, and validation steps
> live in each `exercise-*/SOLUTION.md`.

## Per-exercise solutions

| Exercise | Topic | Solution |
|---|---|---|
| 01 | Production readiness checklist | [exercise-01/SOLUTION.md](exercise-01/SOLUTION.md) |
| 02 | Capacity planning + resource management | [exercise-02/SOLUTION.md](exercise-02/SOLUTION.md) |
| 03 | SLO / SLI definition + monitoring | [exercise-03/SOLUTION.md](exercise-03/SOLUTION.md) |
| 04 | Incident response | [exercise-04/](exercise-04/) |
| 05 | Complete production operations | [exercise-05/](exercise-05/) |

## What this module is really teaching

The day-2 ops layer is where MLOps differs most from generic ops:

- Inference SLOs that span model quality + latency + throughput.
- Capacity planning that accounts for GPU economics.
- On-call patterns tuned for ML failure modes.
- Cost attribution per model / team.

## Architectural decisions and *why*

Each decision is referenced by the exercise where it is
instantiated; the per-exercise SOLUTION.md files carry the worked
detail.

### Decision 1: SLOs per registered model

Each production model has its own SLO (latency p95, error rate,
inference accuracy on a shadow set). Models have different cost /
quality / latency profiles; one global SLO is wrong for any of
them. → Exercise 03.

### Decision 2: GPU capacity planning per quarter

GPU capacity is planned quarterly with explicit demand forecasts
per model. Spot GPU availability is volatile; long-lead
reservations save materially over one-week-ahead provisioning.
→ Exercise 02.

### Decision 3: ML-specific on-call playbook

The on-call playbook has dedicated runbooks for model quality
regression, inference latency degradation, inference cluster OOM,
training job stuck / failed, and data pipeline freshness alarm.
Generic SRE playbooks miss these. → Exercises 01 and 04.

### Decision 4: Cost attribution down to the model level

Every inference and training cost is attributed to a model + team +
environment. ML costs grow fast; without attribution the cost
conversation devolves into mystery. → Exercise 02.

### Decision 5: Capacity utilization alerting

Two alerts: high utilization (over 80% sustained) signals
saturation; low utilization (under 30% sustained) signals waste.
The reference alerts on both because both matter at scale.
→ Exercise 02.

## Trade-offs we deliberately accepted

- Per-model SLOs are a maintenance tax (we pay it).
- Capacity planning requires forecasting (sometimes wrong).
- Cost attribution depends on tagging discipline.

## Common mistakes graders see

1. **Generic SLOs** that don't distinguish models with different
   shapes.
2. **No GPU capacity forecasting** — emergency provisioning at
   sticker price.
3. **Cost attribution missing the GPU bill** — training jobs show
   up as a single line item, not per-team.
4. **On-call without ML-specific runbooks** — SRE picks up the
   page and has no idea what an "AUC regression" alert means.

## When to go beyond this implementation

- Adopt **FinOps for ML** as a discipline with dedicated ownership.
- Move to **multi-region** for latency-sensitive global users.
- Add **chaos engineering** specific to ML failure modes.

## Related curriculum touchpoints

- ``senior-engineer/mod-207-observability-sre`` — the SRE
  foundations.
- ``architect/projects/project-304-cost-finops`` — architectural
  FinOps.
