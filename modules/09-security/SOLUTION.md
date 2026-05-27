# SOLUTION — MLOps Security

> Read this *after* you have implemented the reference MLOps
> security controls. This document explains *why* ML-specific
> security concerns deserve their own module.

## What this module is really teaching

MLOps adds attack surface beyond generic application security:
- Model artifacts (could contain back-doors).
- Training data (could be poisoned).
- Inference endpoints (could leak training data via inversion).
- Supply chain (could ship compromised model weights).

The reference solutions extend standard infra security with
ML-specific controls for these surfaces.

## Architectural decisions and *why*

### Decision 1: Model artifact signing + verification

Every model artifact is signed (cosign) at registration and
verified at deployment. The reason: a compromised registry could
serve poisoned model weights; signature verification makes that
attack visible.

### Decision 2: Training-data integrity hashes

Datasets used in training are hashed; the hash is included in
model metadata. The reason: model behavior depends on training
data; integrity hashes let you prove which data version produced
which model.

### Decision 3: Inference-endpoint rate limiting + auth

Every inference endpoint requires authentication and has rate
limits. The reason: model-inversion attacks need many queries;
rate limits raise the cost dramatically.

### Decision 4: PII redaction at the inference boundary

Inference requests containing PII are redacted before being
logged. The reason: log-aggregation systems become a PII data
store otherwise; that's a compliance problem.

### Decision 5: Restricted model-download permissions

Production model artifacts are only accessible to the inference
service account. Data scientists experimenting can't download
production weights. The reason: weights are valuable IP; over-
permissive access is the most common leak.

## Trade-offs we deliberately accepted

- Signature verification adds deploy-time overhead.
- PII redaction is a moving target.
- Strict access can slow data scientists; we accept it.

## Common mistakes graders see

1. **Model artifacts in unauthenticated S3 buckets**: weights
   exfiltrated.
2. **Inference logs containing PII**: regulatory exposure.
3. **No rate limiting on inference**: model inversion / DOS.
4. **Training data not hashed**: provenance lost.
5. **Same account credentials for training + serving + dev**:
   any compromise affects all.

## When to go beyond this implementation

- Adopt **adversarial-robustness testing** for high-stakes models.
- Add **differential-privacy training** for sensitive data.
- Move to **confidential computing** for very-sensitive
  workloads.

## Related curriculum touchpoints

- ``senior-engineer/mod-209-security-compliance`` — broader
  security frame.
- ``security/projects/project-3-adversarial-defense`` — the
  adversarial-attack side of the same problem.
