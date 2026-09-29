# Exercise 02 — Design an MLOps Pipeline

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-02-design-an-mlops-pipeline.md).
Companion artifact: [`PIPELINE_DESIGN.md`](PIPELINE_DESIGN.md).

## 1. Solution overview

The exercise asks the learner to design an end-to-end training + serving pipeline for a
recommendations use case, spanning ingest → storage → processing → serving → monitoring
→ governance. The reference solution walks through the diagram, calls out the accepted
choices per layer along with the *rejected* alternative and the reason, then lists
failure modes with detection and recovery paths.

Cross-repo companion: see
[engineer-solutions/mod-105 exercise-01-pipeline-architecture-design](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-105-data-pipelines/exercise-01-pipeline-architecture-design)
for the deeper cost model and capacity math.

## 2. Worked answer & implementation

The complete worked design lives in [`PIPELINE_DESIGN.md`](PIPELINE_DESIGN.md). It
contains:

- A **layered diagram** (Sources → Storage → Processing → Serving) with a monitoring
  spine (Prometheus + Grafana + Evidently) and a governance spine (Marquez + audit log).
- A **choices + trade-offs table** with columns *Layer / Choice / Rejected / Why*.
- A **failure-modes table** with columns *Mode / Detection / Recovery*.
- A one-line **capacity + cost** anchor (~$1,100/mo) with the detailed breakdown
  deferred to the engineer-solutions companion.

### Decision rationale (from PIPELINE_DESIGN.md)

- **Kafka + Debezium CDC** over hourly batch poll — the freshness need for online
  features rules out batch.
- **Airflow + Spark** over Dagster — driven by existing team expertise, not a
  technology preference.
- **Redis (TTL 24h)** for the online store — latency-critical serving path; DynamoDB
  rejected on latency grounds for this workload.
- **MLflow** for tracking — OSS-first stance (see module-level Decision 1).
- **Evidently + Prometheus** for drift — no vendor budget for a hosted alternative.

The pattern is: prefer the OSS / self-hosted default from the module-level rationale
document unless a workload requirement forces a different call.

## 3. Validation steps

Grader / self-review:

1. Confirm the diagram covers **all six layers**: ingest, storage, processing, serving,
   monitoring, governance. Missing layers are the most common failure.
2. For each row in the choices table, confirm the *Rejected* alternative is a *credible*
   alternative — not a strawman.
3. Confirm each failure-mode row lists both **detection** (how you find out) and
   **recovery** (what happens next); a mode with detection but no recovery is a gap.
4. Confirm the online path (recs API → Redis) and the offline path (batch → S3) are
   both wired to the model registry — a single deploy artifact for both.
5. If the learner produced their own cost estimate, sanity-check its magnitude against
   the ~$1,100/mo anchor.

## 4. Rubric

| Area | Pass | Common failure mode |
|---|---|---|
| Layer coverage | Ingest, storage, processing, serving, monitoring, governance all present | Missing monitoring or governance |
| Choice justification | Every choice paired with a rejected alternative and reason | "We picked X" with no comparison |
| Failure modes | ≥ 5 modes, each with detection + recovery | Modes listed but only detection filled in |
| Serving split | Online (low-latency) and offline (batch) paths distinguished | Single "serving" box conflating both |
| Monitoring | Model metrics *and* drift, not just infra metrics | Prometheus only, no Evidently equivalent |
| Governance | Lineage tool + audit log present | Governance layer omitted entirely |
| Cost | Order-of-magnitude estimate provided | No cost sanity-check |

## 5. Common mistakes

Drawn from the module-level "common mistakes graders see" list plus this exercise's
design risks:

- **Same MLflow for experiments and registry without tag-based separation** — pollutes
  the model catalog with experimental runs.
- **Prod credentials in the experiment server** — an experiment-server breach exposes
  prod.
- **"Container up" as monitoring** — infra-level checks that miss model degradation.
- **Skipping governance entirely** — no lineage / audit log means you cannot answer
  *"which model, trained on which data, produced this recommendation?"*
- **Choosing tools without a rejected alternative** — reads as fashion rather than
  design.

## 6. References

- Learning exercise:
  `lessons/mod-001-mlops-foundations/exercises/exercise-02-design-an-mlops-pipeline.md`
  (ai-infra-mlops-learning).
- Local companion artifact: [`PIPELINE_DESIGN.md`](PIPELINE_DESIGN.md).
- Deeper design + cost model:
  [engineer-solutions/mod-105 exercise-01-pipeline-architecture-design](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-105-data-pipelines/exercise-01-pipeline-architecture-design).
- Module-level rationale: [`../SOLUTION.md`](../SOLUTION.md).
