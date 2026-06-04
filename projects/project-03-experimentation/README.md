# Project 3 Solution — Experimentation Platform

Reference for [learning project 3](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-03-experimentation).

The learning repo's project-3 already has a fully-built implementation:
- A/B assignment service + exposure log
- Bandit option (Thompson sampling)
- Statistical-significance analysis module
- docker-compose stack

This solution-side directory points back. Study using the same process as project-2.

## Cross-references

- [engineer-solutions/mod-106 ex-09 (ab-testing-infrastructure)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-09-ab-testing-infrastructure)
- [mlops-solutions modules/mod-005-experimentation](../../modules/mod-005-experimentation/) — the per-exercise solutions in this repo

## Sample composition

The pieces shown in modules/mod-005-experimentation come together in the learning
project as:

```
                      ┌─── gateway (FastAPI) ─────────┐
                      │   - ab.assign() per user_id   │
                      │   - route to variant endpoint │
                      │   - exposure log → Kafka      │
                      └───────────────────────────────┘
                                       │
                                       ▼
              ┌────────────────────┐       ┌──────────────────┐
              │  control variant   │       │ treatment variant │
              │  (recs:v5)         │       │ (recs:v6)         │
              └────────────────────┘       └──────────────────┘

   analyze.py ←── exposure log + business metrics → significance report
   bandit.py  ←── exposure log                     → Thompson posterior
```
