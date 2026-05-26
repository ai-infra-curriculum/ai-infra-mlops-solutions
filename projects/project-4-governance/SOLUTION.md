# SOLUTION — ML Governance & Compliance System

> The runnable implementation lives in the **learning** repo at
> `ai-infra-mlops-learning/projects/project-4-governance`. This file
> explains the design reasoning.

## What problem this solves

Governance is the layer that lets you answer four questions about a
production ML system, on demand:

1. **What does it do?** — model cards.
2. **Who can it harm?** — fairness metrics with subgroup analysis.
3. **What happened?** — tamper-evident audit log.
4. **Can it be undone?** — subject-rights handling (GDPR delete /
   export / explain).

If you cannot answer any of these convincingly, you cannot ship into
regulated environments — and increasingly, you cannot ship into
*unregulated* environments where users care.

## Architectural decisions and *why*

### Fairlearn-style metrics, not "is this model fair"

"Fair" is not a metric. The reference exposes demographic parity,
equalized odds, disparate impact (with the four-fifths-rule
threshold), and the mitigation primitives (per-group thresholds,
reweighting). The team picks which metric is operationally meaningful
for the use case; the platform measures and surfaces it.

### SHA-256 hash chain over a tamper-evident database

Database integrity controls protect against accidental change. A hash
chain protects against *intentional* change by a privileged insider.
Each entry's hash includes the previous entry's hash, so any
post-hoc edit invalidates everything downstream. `verify()` walks the
chain and reports the first break.

This is a deliberate choice over blockchain (overkill for an internal
log) and over append-only databases (cloud providers can ultimately
edit those).

### Jinja-templated model card from training metadata

Hand-written model cards drift; auto-generated cards from training
metadata stay current. The Jinja template is reviewable; the
generation step is part of the training pipeline.

### GDPR subject-request handler as one endpoint with three verbs
(delete / export / explain)

Combining the three keeps the audit trail clean — a delete that
isn't logged isn't a delete — and forces the platform to think about
*all three* rights, not just the easy one (export).

### FastAPI surface, not a vendor compliance product

A vendor product gives you a UI but ties governance to a
non-portable system. The FastAPI surface is yours, integrates with
the rest of the platform, and produces machine-readable artifacts
your auditor can ingest.

## How to study

1. Read the [learning project README](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-4-governance).
2. Bring up the stack: `make up && make test`.
3. Read source in order: `fairness/` → `audit/` → `model_cards/` →
   `compliance/` → `api/`.
4. Walk a subject-erasure scenario end-to-end: ingest data, train,
   request erasure, verify deletion artifact in the chain.

## What's deliberately simplified

- **Single hash-chain anchor.** Production uses multiple independent
  timestamp authorities (RFC 3161, OpenTimestamps).
- **No formal control-mapping matrix.** The system covers the
  *controls this curriculum touches*; mapping to a specific
  regulation (SOC 2 / HIPAA / GDPR / EU AI Act) is per-engagement.
- **Stub explainability.** The "explain" verb returns a deterministic
  stub; integrating SHAP / Anchor / Integrated Gradients is left as
  an extension.
- **No retention-hold workflow** (legal hold).
- **No automated PII detection in *output* logs.**

## Cross-references

| Topic | Deeper reference |
|---|---|
| Per-exercise solutions | `mlops-solutions/modules/07-governance/` |
| Model governance templates | `engineer-solutions/mod-106 exercise-10` |
| Compliance framework architecture | `architect-solutions/projects/project-305-security-framework/` |
| Security operations integration | `security-solutions/project-5-security-operations/` |

## Production gap checklist

- [ ] Multi-authority timestamp anchoring (RFC 3161)
- [ ] Control-mapping matrix per target regulation, signed off by
      auditor
- [ ] Real explainability surface (SHAP or equivalent)
- [ ] Retention-hold workflow with legal-team integration
- [ ] PII detection in output logs (not just input features)
- [ ] Differential-privacy budget per subject
- [ ] Independent attestation of deletion (third-party verifier)

## Time budget

- **Skim**: 1 hour.
- **Deep**: 1–2 weeks — re-implement the hash chain from scratch on
  a different DB backend, prove tamper-evidence on your
  implementation.
