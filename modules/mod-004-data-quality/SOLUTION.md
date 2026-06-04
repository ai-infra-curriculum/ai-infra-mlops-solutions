# SOLUTION — Data Quality

> Read this *after* you have wired up the reference data-quality
> checks. This document explains *why* the data-quality patterns
> are what they are for ML pipelines.

## What this module is really teaching

Bad data ruins models silently. The reference solutions catch
data quality problems at three layers:

1. **Schema** (Great Expectations / pandera): hard contracts.
2. **Distribution** (statistical drift detection): soft signals.
3. **Lineage** (OpenLineage): provenance for forensic analysis.

## Architectural decisions and *why*

### Decision 1: Great Expectations as the schema authority

GE expectations are version-controlled alongside the pipeline
code. The reason: data schemas drift; co-locating them with the
consuming code means schema changes show up in code review.

### Decision 2: Validation as a fail-fast pipeline stage

Validation runs immediately after ingestion. If validation
fails, downstream tasks don't run — wasted compute is avoided.
The reference DAGs disable retries on validation tasks.

### Decision 3: Sampling, not full-table, for daily checks

Distribution checks run on samples (10-100k rows) rather than
full tables. The reason: cost. Full-table checks at petabyte
scale are infeasible; samples are usually enough.

### Decision 4: Data contracts between teams

Producer and consumer teams sign data contracts (schema +
SLA + ownership) that live in a shared catalog. Breaking changes
require contract version bumps.

### Decision 5: Lineage events emitted automatically

Every transformation emits OpenLineage events. Lineage is then
queryable: "what fed model X?" returns the upstream graph in
seconds.

## Trade-offs we deliberately accepted

- Great Expectations over Soda Core / Monte Carlo (mature OSS).
- Sampling over full validation (cost-bounded).
- Self-managed lineage stack (Marquez).

## Common mistakes graders see

1. **Validation as a soft warning**: nobody reacts; bad data
   flows through.
2. **No data ownership**: when something breaks, nobody owns
   the fix.
3. **Validation suites that never get reviewed**: stale
   expectations accept obviously-bad data.
4. **Lineage as a side project**: built once, abandoned.
   Make it automatic.

## When to go beyond this implementation

- Add **data observability platforms** (Monte Carlo, Bigeye).
- Adopt **contracts as code** with automated breaking-change
  detection.

## Related curriculum touchpoints

- ``engineer/mod-105-data-pipelines`` — the data pipelines
  these checks live in.
- ``mlops/mod-003-model-monitoring`` — downstream consequence
  of bad data.
