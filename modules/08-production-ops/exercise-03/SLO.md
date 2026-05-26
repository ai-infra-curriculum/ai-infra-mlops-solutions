# SLOs — iris-api

| SLO | Target | Window | Source |
|---|---|---|---|
| Availability (non-5xx) | 99.5% | 30 days | http_requests_total |
| Latency (p95 < 200ms) | 95% | 30 days | http_request_duration_seconds |

## Error budget

For availability: `(1 - 0.995) = 0.5%` of monthly requests can fail.

For ~10M requests/month, that's 50K failed responses before budget is exhausted.

## Alerts (multi-window burn rate)

- **Page** (`severity: critical`): 1h + 5m burning > 14.4x → 30d budget exhausted in ~2d
- **Ticket** (`severity: warning`): 6h + 30m burning > 6x → budget exhausted in ~5d

See `sli-slo.yml` for the Prometheus rules.

Companion: [engineer-solutions/mod-108 ex-08](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-108-monitoring-observability/exercise-08-slo-and-error-budgets) for the full Sloth-format SLO spec + quarterly review template.
