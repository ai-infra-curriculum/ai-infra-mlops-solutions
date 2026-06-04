# SOLUTION — Automation

> Read this *after* you have built the reference automation
> stack. This document explains *why* the automation patterns are
> what they are.

## What this module is really teaching

ML automation has two failure modes:
1. **Under-automation**: every promotion is manual, slow, and
   inconsistent.
2. **Over-automation**: deploys auto-promote on noisy signals,
   bad models slip into production.

The reference solutions land between them with explicit human-
in-the-loop gates for high-stakes promotions.

## Architectural decisions and *why*

### Decision 1: CI/CD for both code and models

The reference CD pipeline treats models as deployable artifacts.
Pushing a registered model triggers the same kind of pipeline
that pushing code does, with quality gates.

### Decision 2: Canary deployment driven by model-quality metrics

Canary stages monitor model-quality metrics (accuracy on a
shadow eval set, latency, error rate). Promotion is gated on
all-clear; rollback is gated on a single failure.

### Decision 3: Manual approval for production promotion

The final canary -> production step requires human approval.
The reason: the cost of a bad production deploy is high enough
that the human in the loop is worth it.

### Decision 4: Auto-rollback on quality regression

If canary metrics fall below a threshold, auto-rollback fires
immediately. The reason: humans are slow to react during
incidents; auto-rollback is faster and consistent.

### Decision 5: Reproducible builds

Every model has a reproducibility record: training code SHA,
data hash, hyperparameters, environment. The reference's
reproducibility script can regenerate any registered model.

## Trade-offs we deliberately accepted

- Manual gate for production (a tax we accept).
- Argo Workflows / Argo CD as the orchestration stack.
- Reproducibility is best-effort; perfect bit-for-bit reproduction
  isn't always achievable (e.g., nondeterministic GPU ops).

## Common mistakes graders see

1. **Auto-promotion based on training metrics**: training metric
   doesn't predict production metric.
2. **No rollback path**: deploys are one-way.
3. **Manual gate that's always rubber-stamped**: the gate
   provides no actual signal.
4. **Reproducibility documented but never tested**: when
   needed, doesn't work.

## When to go beyond this implementation

- Adopt **shadow deployments** before canary.
- Move to **GitOps-driven model promotion** (the model
  promotion is a Git commit).
- Add **change-management integration** (ServiceNow,
  Jira-Service-Management) for compliance-heavy orgs.

## Related curriculum touchpoints

- ``senior-engineer/mod-208-iac-gitops`` — GitOps foundations.
- ``mlops/mod-008-production-ops`` — operational layer.
