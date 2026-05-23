# Recs Training Pipeline Design — Reference

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/01-mlops-foundations/exercises/exercise-02-design-an-mlops-pipeline.md).

Cross-references the deeper design exercise in
[engineer-solutions/mod-105 exercise-01-pipeline-architecture-design](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-105-data-pipelines/exercise-01-pipeline-architecture-design).

## High-level diagram

```
    Sources                  Storage                 Processing                Serving
─────────────────         ─────────────         ───────────────────       ─────────────────
events (Kafka) ─┐  ┌── S3 raw landing ──┐    ┌── Flink (streaming) ──┐  ┌── Online (Redis) ──┐
catalog (CDC)   │──│   warehouse        │────│   Spark (daily)       │──│   Batch (S3)       │──→ recs API
users (CDC)     │  └── feature store    ┘    └── Airflow orchestrate ┘  └── Model registry   ┘
inventory (Kafka)┘
                                ↓ monitoring
                       Prometheus + Grafana + Evidently
                                ↓ governance
                                Marquez (lineage) + audit log
```

## Choices + trade-offs (abbreviated)

| Layer | Choice | Rejected | Why |
|---|---|---|---|
| Ingest | Kafka + Debezium CDC | hourly batch poll | streaming needed for fresh features |
| Processing | Airflow + Spark | Dagster | team Airflow expertise |
| Online store | Redis (TTL 24h) | DynamoDB | latency-critical |
| Tracking | MLflow | W&B | OSS-first stance |
| Drift | Evidently + Prom | Arize | no vendor budget |

## Failure modes

| Mode | Detection | Recovery |
|---|---|---|
| Source schema break | Schema Registry rejection + DLQ | manual triage; alert |
| Late-arriving data | Watermarks + 10-min lateness window in Flink | next batch corrects |
| GE quality fail mid-DAG | Airflow task fails fast | alert; investigate |
| Training over SLA (4h) | sla_miss_callback | page on-call |
| Warehouse cost spike | Budget alarm | throttle concurrency |

## Capacity + cost

~$1,100/mo — full breakdown in the engineer-solutions reference.
