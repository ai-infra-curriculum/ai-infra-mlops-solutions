# Production Readiness Checklist (ML Service)

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/08-production-ops/exercises/exercise-01-production-readiness-checklist.md).

## Architecture + design
- [ ] Architecture diagram exists + reviewed by 1 peer
- [ ] Capacity model documented (RPS, latency budget, growth)
- [ ] Failure modes enumerated with detection + mitigation

## Code + tests
- [ ] CI green (lint + type + tests; ≥80% coverage)
- [ ] Integration test against staging env
- [ ] Load test demonstrates target RPS at target latency

## Deployment
- [ ] CI-built image (no manual builds)
- [ ] Reproducible model artifact (DVC or registry)
- [ ] Rollback procedure documented + tested

## Observability
- [ ] Metrics: RPS, latency p50/p95/p99, error rate, model drift
- [ ] Dashboards: per-service overview + drill-down
- [ ] Alerts: SLO burn-rate + drift + dependency failure
- [ ] Logs: structured JSON with trace_id

## Reliability
- [ ] SLOs defined (availability + latency)
- [ ] Error budget tracking enabled
- [ ] Graceful degradation when dependencies fail
- [ ] Circuit breaker on flaky downstream

## Security
- [ ] Secrets in vault (not env vars committed)
- [ ] Image scanned (Trivy/Grype) + signed (cosign)
- [ ] Network policy: deny-all egress + explicit allow
- [ ] Authentication on every endpoint

## Operations
- [ ] Runbook for top 5 alerts
- [ ] On-call rotation set up
- [ ] Postmortem template ready
- [ ] DR plan documented + last rehearsal < 6 months ago
