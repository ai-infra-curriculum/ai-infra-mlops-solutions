# SOLUTION — MLOps Foundations

> Read this *after* you have built the reference foundations. This
> document explains *why* the MLOps starting point is shaped the
> way it is.

## What this module is really teaching

MLOps foundations are deceptively simple. The patterns set here —
how you version data, where the model registry lives, how
experiments connect to deployments — determine what's painful in
year 2. The reference solutions pick the choices that scale.

## Architectural decisions and *why*

### Decision 1: One MLflow per organization, not per team

The reference deploys a single MLflow tracking server with
per-team experiment namespaces. The reason: cross-team
experiment search and model comparison are the most valuable
queries; per-team MLflow instances make those queries impossible.

### Decision 2: Data versioning via DVC + content-addressed storage

Datasets live behind DVC pointers, with the actual files stored
at content-hashed paths in S3 / GCS. The reason: content hashing
gives automatic deduplication and lets DVC validate file
integrity. Path-based versioning (``v1/``, ``v2/``) is fragile
and gets out of sync.

### Decision 3: ``mlflow.models`` for serialization, not raw object dumps

Models are serialized via ``mlflow.pyfunc`` or framework-specific
flavors. The reason: raw object dumps tie the artifact to a
specific Python version and library set; ``mlflow.models``
packages the dependencies along with the weights.

### Decision 4: Three-stage registry: None / Staging / Production

The reference registry uses three stages. Anything more nuanced
(Development / QA / Pre-Prod / Production / Archived) becomes
process theater. Three stages cover the real promotion path.

### Decision 5: Run IDs as deployment artifacts

Production deployments reference an MLflow run ID, not just a
model version number. The reason: when production behaves
oddly, you need to be able to retrieve the *full* lineage —
training data, hyperparameters, environment — and the run ID is
the key.

## Trade-offs we deliberately accepted

- MLflow over W&B / Comet for OSS friendliness.
- DVC over LakeFS / Delta Lake for gentler setup.
- Self-hosted by default, not SaaS.

## Common mistakes graders see

1. **Tracking locally, never centrally**: nobody can compare.
2. **Forgetting to log the model**: experiments without
   ``mlflow.log_model()`` produce metrics but no artifacts.
3. **Putting prod credentials in the experiment server**:
   experiment-server breach exposes prod.
4. **Same MLflow for experiments and registry without
   tag-based separation**: pollutes the model catalog.

## When to go beyond this implementation

- Add **model cards** as a registry-promotion requirement.
- Adopt a **feature store** alongside the registry.
- Move to **continuous training** triggered by signals.

## Related curriculum touchpoints

- ``engineer/mod-106-mlops`` — engineering-side MLOps.
- ``ml-platform/mod-006-model-management`` — platform-level
  model lifecycle.
