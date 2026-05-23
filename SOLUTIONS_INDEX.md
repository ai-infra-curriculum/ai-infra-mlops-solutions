# Solutions Index

Reference implementations for [ai-infra-mlops-learning](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning).
**Coverage: 100% (all 10 modules + all 5 projects).** Last updated 2026-05-23.

## Repository Layout

- `modules/`: module-level exercise solutions (one directory per module slug)
- `projects/`: project-grade solutions
- `guides/`: troubleshooting and implementation notes
- `resources/`: supporting references and shared assets

## Module coverage

| Module | Topic | Exercises | Status |
|---|---|---|---|
| 01 | MLOps Foundations | 5 | ✅ |
| 02 | Experiment Tracking & MLflow | 5 | ✅ |
| 03 | Model Monitoring | 5 | ✅ |
| 04 | Data Quality | 5 | ✅ |
| 05 | Experimentation | 5 | ✅ |
| 06 | Automation | 5 | ✅ |
| 07 | Governance | 5 | ✅ |
| 08 | Production Ops | 5 | ✅ |
| 09 | Security | 5 | ✅ |
| 10 | Advanced Topics | 5 | ✅ |
| **Total** | | **50** | **50/50** |

## Project coverage

| # | Slug | Status | Implementation home |
|---|------|--------|---------------------|
| 1 | `project-1-ml-pipeline` | ✅ | this repo |
| 2 | `project-2-model-serving` | ✅ | learning repo |
| 3 | `project-3-experimentation` | ✅ | learning repo |
| 4 | `project-4-governance` | ✅ | learning repo |
| 5 | `project-5-llmops` | ✅ | learning repo |

For projects 2-5 the full implementation ships with the learning repo's
project directory (one `make up` away from a working stack). The
solutions-side pointer pages cross-reference deeper engineer-solutions
material.

## Cross-references

Many MLOps exercises overlap engineering-track topics:

| MLOps topic | Engineering-track deep dive |
|---|---|
| Experiment tracking | engineer-solutions/mod-106 ex-02 |
| Model registry promotion | engineer-solutions/mod-106 ex-03 |
| Feature store | engineer-solutions/mod-106 ex-07 |
| Deployment strategies | engineer-solutions/mod-106 ex-08 |
| A/B testing | engineer-solutions/mod-106 ex-09 |
| Governance / model cards | engineer-solutions/mod-106 ex-10 |
| Cost attribution | engineer-solutions/mod-106 ex-12 |
| Pipeline orchestration | engineer-solutions/mod-105 ex-02 |
| Data quality (GE) | engineer-solutions/mod-105 ex-07 |
| SLO / burn-rate alerts | engineer-solutions/mod-108 ex-08 |
| Incident response | engineer-solutions/mod-108 ex-09 |
| LLM serving (vLLM) | engineer-solutions/mod-110 ex-03 |
| LLM cost routing | engineer-solutions/mod-110 ex-08 |
| LLM guardrails | engineer-solutions/mod-110 ex-11 |
| RAG | engineer-solutions/mod-110 ex-14 |
| Secret management | engineer-solutions/mod-109 ex-07 |
| Policy as code | engineer-solutions/mod-109 ex-08 |

## Synchronization Rules

- Module slugs MUST match the paired learning repository.
- Every learner-facing exercise should have a corresponding solution path here.
- Operational reports belong in the workspace `_meta/`, not the repo root.
