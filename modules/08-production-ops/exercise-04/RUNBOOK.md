# Runbook — High Error Rate on iris-api

Triggered by `HighErrorRate` alert (5xx rate > 5% for 5 min).

## Immediate (first 5 min)

1. Acknowledge in PagerDuty.
2. Check dashboard: error rate by status code + by pod.
3. Check recent deploys: `argocd app history iris-api` — was there one in the last 30 min?

## Triage decision tree

- **All pods, single status code (502/504)**: downstream service issue
  - Check feature store / model registry availability
  - Check upstream provider status pages
- **One pod, multi-status**: bad pod
  - `kubectl delete pod <name>` to recycle
  - If repeats, check for image-pull or container-init issue
- **All pods, mixed status**: likely a deploy regression
  - **Rollback** via Argo Rollouts: `kubectl argo rollouts undo iris-api`
  - Or via ArgoCD: `argocd app rollback iris-api <revision>`

## Common causes

| Symptom | Cause | Fix |
|---|---|---|
| 502 spike after deploy | Bad model version | Rollback via registry |
| 504 + downstream slow | Feature store overload | Scale feature-store or enable cache |
| 500 + tracebacks | Code regression | Rollback + open issue |
| 503 + HPA at max | Underprovisioned | Increase HPA max + investigate root cause |

## Postmortem

- Use the [POSTMORTEM_TEMPLATE](../../../projects/project-1-ml-pipeline/docs/POSTMORTEM_TEMPLATE.md) (if available)
  or the [engineer-solutions/mod-108 ex-09 template](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-108-monitoring-observability/exercise-09-incident-response-gameday/POSTMORTEM_TEMPLATE.md).
- Within 1 week of SEV2+ incidents.
- Blameless. Action items have owners + due dates.
