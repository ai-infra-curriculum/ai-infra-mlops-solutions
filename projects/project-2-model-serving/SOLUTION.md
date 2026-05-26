# SOLUTION — Production Model Serving

> The runnable implementation lives in the **learning** repo at
> `ai-infra-mlops-learning/projects/project-2-model-serving`. This
> file explains the design reasoning behind that implementation.

## What problem this solves

"Run a model behind an HTTP endpoint" is a one-day exercise. *Operating*
a model behind an HTTP endpoint in production is a multi-quarter
problem with predictable failure modes:

1. **Cold-start latency** — model file is large, first request blocks.
2. **Resource contention** — Python's GIL and process model interact
   badly with CPU-bound inference.
3. **Silent staleness** — the model file in the container is from
   three months ago and nobody noticed.
4. **No way to roll back** — there is one deployment, you push or you
   suffer.

The reference implementation makes each of these visible and
addressable.

## Architectural decisions and *why*

### FastAPI + Uvicorn + lifespan-managed model load

Lifespan loads the model once at startup, not per request. The
alternative — lazy-loading on first request — produces a cold-start
spike that is invisible until you have load. Lifespan moves the cost
to deploy time where it's expected.

### Multi-stage Dockerfile, non-root user

Multi-stage means the final image ships only the runtime, not the
build chain (smaller, fewer CVEs). Non-root is non-negotiable for
admission controllers in a real cluster — building it in from the
start avoids late-stage rework.

### Prometheus metrics keyed on **request properties**, not just
**system properties**

CPU and memory aren't enough. The reference exposes per-endpoint
latency histograms, per-prediction confidence distributions, and a
request-classification surface so you can answer "the latency spike is
in fraud-detection requests, not the recommender" without grepping
logs.

### Grafana dashboards as code (in repo, not clicked together)

A dashboard that exists only in the production Grafana is a
single-point-of-failure dashboard. Dashboards-as-code travel with the
service and survive Grafana migrations.

### Integration tests *and* load tests

Integration tests cover correctness; load tests cover the failure mode
the integration tests can't see (the model is correct but the API
falls over at 500 RPS).

## How to study

The learning repo has the full implementation. Study path:

1. Read the [learning project README](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-2-model-serving/README.md).
2. Try to build it from the
   [REQUIREMENTS.md](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-2-model-serving/REQUIREMENTS.md)
   first, without looking at the implementation.
3. Compare your code against the reference. Differences are the
   learning.

## Cross-references

| Topic | Deeper reference |
|---|---|
| Production model serving (factory + lifespan + Prom) | `engineer-solutions/mod-101 exercise-08` |
| Helm-chartified deployment | `engineer-solutions/mod-104 exercise-07` |
| Deployment strategies (rolling / canary / blue-green / shadow) | `engineer-solutions/mod-106 exercise-08` |
| Alert routing for serving | `engineer-solutions/mod-108 exercise-07` |

## Production gap checklist

- [ ] Helm-chartified deployment with values per environment
- [ ] Canary / shadow strategy with traffic split
- [ ] PodDisruptionBudget + HPA wired to a meaningful metric
- [ ] Per-tenant rate limits if multi-tenant
- [ ] Request-trace propagation (OpenTelemetry) end-to-end
- [ ] Model-file signature verification at startup

## Time budget

- **Skim**: 45 min.
- **Deep**: 3–4 days — build from scratch using REQUIREMENTS.md, then
  compare.
