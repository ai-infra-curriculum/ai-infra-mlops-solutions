# Alert Configuration — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-003-model-monitoring/exercises/exercise-04-alert-configuration-and-response.md).

- `alerts.yml` — Prometheus rules (drift, accuracy regression, class imbalance, stalled pipeline)
- `alertmanager.yml` — routing with inhibition + severity-based receivers

See [engineer-solutions/mod-108 ex-07](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-108-monitoring-observability/exercise-07-alertmanager-routing) for the full multi-window burn-rate variant.
