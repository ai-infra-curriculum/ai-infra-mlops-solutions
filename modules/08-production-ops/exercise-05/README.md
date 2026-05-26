# Complete Production Operations — Solution

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/08-production-ops/exercises/exercise-05-complete-production-operations.md).

Composes the four prior exercises into a single ops package:

| Component | Source |
|---|---|
| Readiness gate (CI/CD) | ex-01 checklist as a PR template |
| Capacity model | ex-02 worked example, kept in repo as living doc |
| SLO recording + burn-rate alerts | ex-03 `sli-slo.yml` + Sloth config |
| Runbooks | ex-04 RUNBOOK + one per common alert |
| On-call rotation | PagerDuty schedule managed in Terraform |
| Game days | engineer-solutions/mod-108 ex-09 (quarterly) |
| Postmortem template | engineer-solutions/mod-108 ex-09 |

This is what "Production Operations" looks like as a finished platform deliverable.
