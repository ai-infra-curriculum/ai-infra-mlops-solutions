# SOLUTION — Experimentation Platform

> The runnable implementation lives in the **learning** repo at
> `ai-infra-mlops-learning/projects/project-03-experimentation`. This
> file explains the design reasoning.

## What problem this solves

Most ML changes ship without a real comparison. The team measures
"does the new model look better on the holdout set?" and ships it.
Production ML experimentation answers a *different* question:

> Does the new model make the system measurably better for the business
> on real traffic, in a way that survives noise, novelty, and seasonality?

That requires four pieces this platform implements: stable assignment,
honest exposure logging, statistical analysis that respects the
sequential nature of online testing, and an exploration option for
cases where the action space is too large for traditional A/B.

## Architectural decisions and *why*

### Hash-based deterministic assignment, keyed on a stable identifier

A user must get the same variant across requests, sessions, devices.
Random-per-request assignment looks fine in a smoke test and produces
unanalyzable data in production.

### Separate exposure logging from prediction logging

Exposure = "this user was eligible for this experiment and assigned to
this variant." Prediction = "this model was called for this user and
returned this output." These are different events with different
retention, different privacy implications, and different consumers.
Conflating them produces unanalyzable logs.

### Significance analysis as a module, not a notebook

Notebook-based analysis is unreproducible. The `analyze.py` module
takes exposure + outcome logs and produces a reviewable significance
report — same code path every time, diffable in version control.

### Thompson sampling as an *opt-in* bandit alternative

Multi-armed bandits are not "smarter A/B testing" — they're a
different statistical tool for cases where (a) the action space is
large, (b) you can tolerate non-stationary exploration, and (c) you
have a credible reward signal. The reference design makes Thompson
sampling available without making it the default.

### Gateway-level routing, not client-level routing

If clients choose variants, you cannot trust the assignment. The
gateway pattern keeps assignment server-side and auditable.

## How to study

1. Read the [learning project README](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-03-experimentation).
2. Read the sample composition diagram in the project README
   (gateway → variants → exposure log → analysis).
3. Build a minimal version yourself before reading the reference.

## What's deliberately simplified

- **No sequential testing (mSPRT, group sequential bounds).** Tests
  are run to a pre-registered duration; early stopping is mentioned
  but not implemented. Sequential analysis is a research area on its
  own.
- **No interaction-effects detection.** Concurrent experiments may
  interact; the platform does not flag this.
- **No causal-effect estimation beyond difference-in-means.** No
  CUPED, no synthetic control, no DiD.
- **No fairness checks per group.** A real platform must verify the
  effect is not concentrated in or against a protected subgroup; the
  hooks are there but the rules are not encoded.

## Cross-references

| Topic | Deeper reference |
|---|---|
| A/B testing infrastructure | `engineer-solutions/mod-106 exercise-09` |
| Per-exercise platform components | `mlops-solutions/modules/mod-005-experimentation/` |
| Per-prediction audit log | `mlops-learning/projects/project-04-governance/src/audit/log.py` |

## Production gap checklist

- [ ] Sequential testing with valid early-stopping bounds
- [ ] Interaction-effect detection across concurrent experiments
- [ ] Subgroup analysis with multiple-comparisons correction
- [ ] CUPED / variance reduction for low-power tests
- [ ] Holdout reservation across experiment families
- [ ] Pre-registration workflow (hypothesis, primary metric, duration
      locked before launch)

## Time budget

- **Skim**: 45 min.
- **Deep**: 1 week — build a minimal hash-assignment + exposure log,
  then run a real test with synthetic outcomes and verify the
  significance analysis matches your hand calculation.
