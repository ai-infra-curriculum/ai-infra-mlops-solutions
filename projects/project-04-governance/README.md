# Project 4 Solution — ML Governance & Compliance System

Reference for [learning project 4](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-04-governance).

The learning project was just built out to full implementation (this session):
- `src/fairness` — Fairlearn-style metrics (demographic parity, equalized odds, disparate impact + four-fifths rule) + mitigation (per-group thresholds, reweighting)
- `src/audit` — tamper-evident SHA-256 hash chain with `verify()`
- `src/model_cards` — Jinja-templated model card from training metadata
- `src/compliance/gdpr.py` — subject-request handler (delete / export / explain) tied to audit log
- `src/api/app.py` — FastAPI exposing /v1/fairness, /v1/model-cards, /v1/audit, /v1/audit/verify
- `tests/` — fairness + audit + API smoke tests
- Dockerfile + docker-compose (Postgres + API + Prom) + Makefile

This solution-side directory points back to it. Study by:
1. Reading [learning project-4 README](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-04-governance/README.md)
2. Cloning + `make up && make test`
3. Reading the source modules in order: `fairness/` → `audit/` → `model_cards/` → `compliance/` → `api/`

## Cross-references

- [engineer-solutions/mod-106 ex-10 (model-governance)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-10-model-governance) — templates
- [mlops-solutions modules/mod-007-governance/](../../modules/mod-007-governance/) — per-exercise solutions in this repo
