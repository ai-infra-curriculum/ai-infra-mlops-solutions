# SOLUTION — MLOps Governance

> Read this *after* you have set up the reference governance
> infrastructure. This document explains *why* model governance
> at this tier is what it is.

## What this module is really teaching

Model governance is the discipline of making model deployments
reviewable and auditable. The reference solutions establish:
- Model cards as a registry-promotion gate.
- Audit logs that capture every promotion decision.
- Risk classification driving review depth.
- Approval workflows tied to risk class.

## Architectural decisions and *why*

### Decision 1: Model cards required for production promotion

Every model promoted to Production stage requires a model card
documenting intended use, limitations, training data, evaluation
metrics, known biases. The reason: governance without
documentation produces opacity; documentation without governance
produces dusty PDFs.

### Decision 2: Risk classification per model

Models are classified high/medium/low risk based on:
- Decision impact (financial / safety / regulatory).
- User population affected.
- Reversibility of decisions.

Risk class determines: review depth, deployment cadence, audit
frequency.

### Decision 3: Append-only audit log

Every promotion, rollback, and access decision is logged to an
append-only store (S3 with object lock, or equivalent). The
reason: tamper-evident audit logs are a hard requirement in
regulated industries.

### Decision 4: Approval workflows in code

Approval workflows are defined declaratively (YAML / Cue) and
versioned. The reason: workflow changes need their own audit
trail; rubber-stamping is impossible to detect in ad-hoc
approval flows.

### Decision 5: Separation of duties

The person who trained the model can't approve their own
promotion. The reason: most ML production incidents trace back
to insufficient external review.

## Trade-offs we deliberately accepted

- Manual review adds latency (we accept it).
- Model cards take time to write (we accept it).
- Audit log storage costs (small but real).

## Common mistakes graders see

1. **Model cards filled in by template, not thought through**:
   passes the gate; provides no value.
2. **Risk classification omitted or always "low"**: governance
   becomes theater.
3. **Audit log without retention policy**: too short = compliance
   gap; too long = expensive.
4. **Approval workflow with single approver**: bypass single
   person and the whole gate is gone.

## When to go beyond this implementation

- Adopt **policy-as-code** (OPA / Rego) for approval rules.
- Integrate with **GRC platforms** (OneTrust, ServiceNow).
- Add **algorithmic audit** for high-risk models.

## Related curriculum touchpoints

- ``senior-engineer/mod-209-security-compliance`` —
  compliance posture.
- ``architect/projects/project-301-enterprise-mlops`` — the
  architect-level governance frame.
