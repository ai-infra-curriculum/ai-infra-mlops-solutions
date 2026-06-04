# SOLUTION — Experimentation

> Read this *after* you have run the reference experimentation
> infrastructure. This document explains *why* the experimentation
> patterns are what they are.

## What this module is really teaching

Production ML experimentation is harder than it looks:
- A/B test design that actually has statistical power.
- Traffic splitting that's truly random.
- Metrics ladders so secondary effects are visible.
- Holdout populations that survive intervention drift.

## Architectural decisions and *why*

### Decision 1: Frequentist A/B for high-stakes decisions

For revenue-affecting or compliance-affecting decisions, the
reference uses classical fixed-sample-size A/B with
power-analysis-driven sample sizes. The reason: bandits adapt
quickly but make post-hoc statistical claims weaker.

### Decision 2: Multi-armed bandits for model-quality routing

For internal ML-quality routing (which of 3 model versions to
serve), bandits work well — they minimize cumulative regret and
the statistical claims are about ML quality, not business
metrics.

### Decision 3: Holdout population reserved continuously

5-10% of traffic is held out of all experiments. The reason:
the global metric trend needs a clean baseline; experiment
effects pile up otherwise.

### Decision 4: Pre-registration of analysis plans

Each experiment's analysis plan (primary metric, decision rule,
sample size) is committed *before* the experiment starts. The
reason: post-hoc metric shopping inflates false-positive rates.

### Decision 5: Metrics ladder, not single metric

Each experiment tracks a primary metric, secondary metrics, and
guardrail metrics. The reason: optimizing one metric usually
moves another in an undesirable direction; the ladder makes
this visible.

## Trade-offs we deliberately accepted

- Frequentist over Bayesian for the curriculum's primary
  treatment (simpler to teach).
- Holdout traffic costs revenue; we accept this as
  insurance.
- Pre-registration adds friction; we treat the friction as
  feature.

## Common mistakes graders see

1. **Peeking**: looking at experiment results before sample
   size is reached. Inflates false positives.
2. **One-metric experiments**: misses secondary effects.
3. **No guardrails**: an experiment "wins" while latency
   doubles.
4. **Wrong unit of randomization**: user-level vs. session-
   level vs. request-level matters.
5. **Experiments with no decision rule**: continue forever.

## When to go beyond this implementation

- Adopt **stratified sampling** for heterogeneous populations.
- Move to **CUPED** for variance reduction.
- Add **interleaving** for ranking-system A/B tests.

## Related curriculum touchpoints

- ``mlops/mod-006-automation`` — automating experiment lifecycle.
- ``senior-engineer/mod-206-advanced-mlops`` — bandit
  routing.
