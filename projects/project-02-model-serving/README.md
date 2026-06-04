# Project 2 Solution — Production Model Serving

Reference for [learning project 2](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-02-model-serving).

The learning repo already contains a fully-built implementation:
- FastAPI + Uvicorn + lifespan-managed model load
- Prometheus metrics + Grafana dashboards
- Multi-stage Dockerfile (non-root)
- docker-compose stack (API + Prometheus + Grafana)
- Integration + load tests

This solution-side directory points back to it rather than duplicating files.

## How to study

1. Read the [learning project README](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-02-model-serving/README.md).
2. Try to build it from scratch using [REQUIREMENTS.md](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-02-model-serving/REQUIREMENTS.md).
3. Compare your implementation against the reference in the learning repo.

## Cross-references in engineer-solutions

- [mod-101 ex-08 (production-model-serving)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-101-foundations/exercise-08-production-model-serving) — factory pattern + lifespan + rate-limit + Prometheus
- [mod-104 ex-07 (helm-chart-authoring)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-104-kubernetes/exercise-07-helm-chart-authoring) — Helm-chartified deployment
- [mod-106 ex-08 (deployment-strategies)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-08-deployment-strategies) — rolling / blue-green / canary / shadow

These cover, between them, every detail of production model serving at a deeper
level than any single project README.
