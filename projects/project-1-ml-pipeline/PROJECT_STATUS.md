# PROJECT_STATUS — Project 1: Customer Churn ML Pipeline

> **Living document.** New contributors should read this **before** the README. The README
> is aspirational marketing copy; this file is the source of truth for what actually exists,
> what works, what is half-built, and what to do next.
>
> **Last reviewed:** 2026-05-23
> **Document owner:** MLOps curriculum maintainers (`ai-infra-curriculum@joshua-ferguson.com`)
> **Cadence:** Update every PR that changes the implementation surface; review monthly.

---

## 1. Executive snapshot

| Dimension              | Reality (2026-05-23)                                                                 |
|------------------------|--------------------------------------------------------------------------------------|
| Overall maturity       | **Walking skeleton + reference implementation.** Not production. Not "complete."     |
| Code that runs locally | Training, inference, drift detection, data ingestion (CSV path)                      |
| Code that runs in prod | None of it. There is no production deployment target wired up.                       |
| Test coverage          | **0%.** `tests/unit/`, `tests/integration/`, `tests/e2e/` are empty directories.     |
| CI                     | `.github/` exists; no validated workflows. Treat CI as unproven.                     |
| Infrastructure         | `infrastructure/docker/`, `infrastructure/kubernetes/`, `infrastructure/terraform/` are empty placeholders. Only the root `docker-compose.yml` is real. |
| Airflow                | `airflow/dags/` and `airflow/plugins/` are empty. The Makefile targets reference compose files that do not exist (`infrastructure/docker/docker-compose.airflow.yml`). |
| Documentation accuracy | README/PROJECT_COMPLETE overstate completion. This file corrects the record.         |

**One-line summary:** A useful pedagogical reference for the *components* of an MLOps pipeline,
but several of the operational claims in `PROJECT_COMPLETE.md` and `README.md` are aspirational.
Treat any "✅ Complete" badge in those files as "the happy-path script exists" not "the system
has been verified."

---

## 2. What actually exists (verified, file-by-file)

The repository layout under `src/` is real and the Python modules import without errors against
the pinned `requirements.txt` (Python 3.9 / 3.10 / 3.11):

### 2.1 Core utilities — `src/utils/` (≈ 950 LOC)

| File           | Status     | Notes                                                                      |
|----------------|------------|----------------------------------------------------------------------------|
| `config.py`    | Working    | YAML + env-var overlay via `pydantic-settings==2.1.0`.                     |
| `logger.py`    | Working    | `loguru==0.7.2` configured with JSON sink for prod, pretty sink for dev.   |
| `database.py`  | Working    | SQLAlchemy 2.0.25 engine + session factory, Postgres only.                 |
| `metrics.py`   | Working    | `prometheus_client==0.19.0` counters/histograms; not wired to a scraper.   |
| `cache.py`     | Working    | `redis==5.0.1` client with TTL helpers and a decorator. No cluster mode.   |

### 2.2 Data layer — `src/data/`

| File                                | Status              | Notes                                                                                              |
|-------------------------------------|---------------------|----------------------------------------------------------------------------------------------------|
| `connectors/base.py`                | Working             | Abstract `BaseConnector`.                                                                          |
| `connectors/csv_connector.py`       | Working             | Reads local CSV + S3 via `pyarrow==14.0.2`. S3 path is **untested**.                              |
| `connectors/database_connector.py`  | Working (Postgres)  | Pooled reads. No write path. Other dialects unverified.                                            |
| `connectors/api_connector.py`       | Working (synthetic) | Pagination + bearer-token auth; never exercised against a real API in CI.                          |
| `connectors/kafka_connector.py`     | Skeleton            | `kafka-python==2.0.2` consumer. No retry/back-off, no offset commit strategy, no DLQ.              |
| `ingestion.py`                      | Working             | Orchestrates connector → DataFrame → staging. No idempotency keys.                                 |
| `validation.py`                     | Working             | 23 Great Expectations rules (`great-expectations==0.18.8`). Suite is hard-coded, not data-docs-driven. |

### 2.3 Feature layer — `src/features/`

| File             | Status   | Notes                                                                                |
|------------------|----------|--------------------------------------------------------------------------------------|
| `engineering.py` | Working  | ~50 transforms across 7 categories. No feature schema registry.                      |
| `store.py`       | Working  | Postgres-backed feature store with `feature_set` + `version` columns. No TTL/GC.     |

### 2.4 Training — `src/models/train.py`

- 4 algorithms wired up: `LogisticRegression` (scikit-learn 1.3.2), `RandomForest`,
  `xgboost==2.0.3`, `lightgbm==4.1.0`.
- Optuna 3.5.0 search loop is implemented but uses an in-memory study (loses progress on crash).
- MLflow 2.9.2 logging is correct against a local tracking server; **model registry promotion is
  manual** — there is no `Staging → Production` automation.
- No data versioning (DVC / lakeFS / Delta) — the training set is whatever the latest CSV happens
  to be.

### 2.5 Serving — `src/api/server.py`

- FastAPI 0.108.0 / Uvicorn 0.25.0, 5 endpoints, Pydantic v2 schemas.
- Redis caching wraps `/predict` responses by a hash of the input payload.
- Prometheus `/metrics` exposed via `prometheus_client`.
- Auth: **none.** No API keys, no JWT, no rate limiting.
- Model loading: reads a serialized artifact path from config at startup. No hot-reload on new
  model versions. (The artifact format is joblib/MLflow-managed; do not load artifacts from
  untrusted sources.)

### 2.6 Monitoring — `src/monitoring/drift_detection.py`

- KS test, chi-square, PSI, JS divergence for tabular features.
- `evidently==0.4.11` HTML report generator.
- Thresholds are hard-coded constants in the module; not tunable per feature.
- **No alerting sink.** Drift is detected and written to disk; nobody is paged.

### 2.7 Infrastructure (root only)

- `docker-compose.yml` (root): real, 7 services — Postgres 15, Redis 7, MLflow 2.9, Prometheus,
  Grafana, Kafka (optional profile), API.
- `.env.example`: real.
- `.github/`: present, contents unverified.

---

## 3. What is half-built or misleading

These items are referenced by the README, Makefile, or `PROJECT_COMPLETE.md` but are not
backed by working code:

| Claim in repo                            | Reality                                                                                          |
|------------------------------------------|--------------------------------------------------------------------------------------------------|
| `infrastructure/kubernetes/` deploy      | Directory is empty. `make k8s-deploy` will `kubectl apply` an empty directory and fail silently. |
| `infrastructure/terraform/`              | Empty.                                                                                           |
| `infrastructure/docker/docker-compose.airflow.yml` | Does not exist. `make airflow-init` and `make airflow-up` will fail.                       |
| `airflow/dags/`                          | Empty. No DAGs.                                                                                  |
| `airflow/plugins/`                       | Empty.                                                                                           |
| `tests/unit/`, `tests/integration/`, `tests/e2e/` | All empty. `make test` runs zero tests. `make coverage` reports 0%.                       |
| "✅ >80% test coverage target" (README) | Aspirational target, not a measured value.                                                       |
| `notebooks/`                             | Directory exists; no committed notebooks.                                                        |
| `docs/`                                  | Empty until this changeset — now contains `POSTMORTEM_TEMPLATE.md`.                              |
| `make docs` (`pdoc3 --html …`)           | `pdoc3` is not in `requirements.txt` or `requirements-dev.txt`.                                  |

---

## 4. Known limitations

### 4.1 Correctness

1. **No determinism guarantees.** Training does not set seeds for NumPy / XGBoost / LightGBM
   globally; reruns will produce slightly different models.
2. **Feature/serving skew is not measured.** Training-time feature code (`src/features/engineering.py`)
   and serving-time feature code share a module but diverge silently if a contributor edits one
   path. No contract test.
3. **Validation suite is static.** Adding a new column to the source data does not auto-extend
   the GE suite; the new column will be silently ignored.

### 4.2 Operational

1. No retry/back-off on the Kafka or API connector. A flaky upstream will drop records.
2. The API has no graceful shutdown of in-flight requests on SIGTERM.
3. No request ID propagation; correlating an API log line with a model prediction is manual.
4. Drift detection runs as an ad-hoc script, not on a schedule (no Airflow DAG to invoke it).

### 4.3 Security

1. **No authentication** on the FastAPI server.
2. Redis and Postgres in `docker-compose.yml` use default credentials from `.env.example`.
3. `bandit` is configured (`make lint`) but has never been run in CI.
4. Pinned versions are from late 2025; several have known CVEs as of 2026-05. Run
   `pip-audit` before any external exposure.
5. Model artifacts must be loaded only from the trusted MLflow store; loading a serialized
   artifact from an untrusted path is unsafe.

### 4.4 Data

1. No PII handling policy. Sample data is synthetic, but the schema treats customer identifiers
   as plain columns.
2. No data retention or right-to-erasure tooling.
3. Feature store has no schema migration story (`alembic` is not configured).

### 4.5 Scale

1. Single-process FastAPI; `make serve-prod` uses `--workers 4` but the model is loaded per
   worker (memory multiplied by N).
2. Optuna study is in-memory; distributed search would require an RDB backend.
3. No batch inference framework — `make predict` reads the entire CSV into memory.

---

## 5. Recommended next steps

Ordered by leverage. Each item is sized for a single contributor pairing session.

### 5.1 Stop the bleeding (this week)

1. **Add a smoke test suite.** One test per module that imports it and runs the happy path on
   the synthetic CSV. Target: get `make coverage` to a real, non-zero number (even 20% is honest).
2. **Fix the Makefile lies.** Either delete `make k8s-deploy` / `make airflow-up` or wire them
   to real artifacts. Half-working targets erode trust.
3. **Run `pip-audit` and `bandit`** and capture the output in this file under §4.3.
4. **Pin Python.** `pyproject.toml` targets 3.9/3.10/3.11; pick one for CI and document it.

### 5.2 Make it trustworthy (next two weeks)

5. **Wire CI** in `.github/workflows/`: `lint → test → coverage → docker build`. Fail the build
   on coverage regression.
6. **Add a feature-skew contract test.** A single test that pulls one row through the training
   transform and the serving transform and asserts equality.
7. **Move Optuna to an RDB-backed study** (`optuna create-study --storage postgresql://…`) so
   tuning can resume after a crash.
8. **Add an API auth layer.** Even a static API-key header is enough to take the project from
   "demo" to "showable."

### 5.3 Make it deployable (next month)

9. **Write one real Kubernetes manifest** in `infrastructure/kubernetes/` for the API service
   (Deployment + Service + HPA). Delete the empty Terraform dir until there is something to
   manage.
10. **Add one Airflow DAG** in `airflow/dags/` for the daily retrain trigger driven by drift
    detection output. This is the missing glue between §2.6 and §2.4.
11. **Add data versioning.** DVC against the local data directory is the lowest-friction option;
    lakeFS if a shared environment is needed.
12. **Add an MLflow registry promotion step** to the retrain DAG: any model that beats the
    current Production model on the holdout set by ≥1 pp AUC gets auto-promoted to Staging
    (Production still requires a human click).

### 5.4 Stretch (quarter+)

13. SLOs and an error budget for the API (`p99 < 200 ms`, `availability ≥ 99.5%`). See
    `docs/POSTMORTEM_TEMPLATE.md` for the postmortem format that pairs with these.
14. A shadow-traffic mode in the API so new model candidates can score live requests without
    affecting the response.
15. A canary deploy story (Argo Rollouts or Flagger) once §5.3.9 lands.

---

## 6. How to verify this document

If you change the implementation, update §2 and §3. A reviewer should be able to:

```bash
# From the project root
make install-dev
make data-generate
make test            # currently runs zero tests — see §3
make coverage        # currently 0% — see §3
docker compose up -d # the only real infra path — see §2.7
```

If any of the above produces a result different from what this file claims, **fix the file in
the same PR.** Drift between PROJECT_STATUS.md and the code is the failure mode this document
exists to prevent.

---

## 7. Pointers

- Architecture and requirements live in the **learning repo**, not this one:
  - https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-1-ml-pipeline/REQUIREMENTS.md
  - https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-1-ml-pipeline/ARCHITECTURE.md
- Step-by-step build narrative: [`STEP_BY_STEP.md`](STEP_BY_STEP.md)
- Postmortem template for incidents that touch this pipeline:
  [`docs/POSTMORTEM_TEMPLATE.md`](docs/POSTMORTEM_TEMPLATE.md)
