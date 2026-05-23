# Complete MLOps Security Framework — Reference

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/09-security/exercises/exercise-05-complete-mlops-security-framework.md).

Composes the four prior exercises into a defense-in-depth deployment.

```
                    ┌── Vault ──┐
                    │  (ex-02)  │
                    └─────┬─────┘
                          ▼ ESO syncs at deploy time
┌─── PR ──→ CI ──→ build + cosign sign + SBOM + scan (ex-03) ──→ GHCR ───┐
│                                                                          │
│         │   admission gate (Kyverno: require signed) (ex-03)            │
│         ▼                                                                │
│   Kubernetes ─→ Pod spec hardened (ex-04) + NetworkPolicy (ex-04) ─────┘
│                       │
│                       ▼
│              Runtime threats (ex-01 OWASP) mitigated by:
│                - input bounds + rate limit
│                - signed model artifacts
│                - drift + bias monitoring
│
└── Audit trail in tamper-evident log (mod-07 ex-04)
```

## Layered defenses by phase

| Phase | Defense | Source |
|---|---|---|
| Code | SAST + dep scanning | engineer-solutions/mod-103 ex-12 |
| Build | image scan + SBOM + sign | ex-03 |
| Deploy | admission policy | ex-03 + engineer-solutions/mod-109 ex-08 |
| Runtime | hardened pod + netpol | ex-04 |
| Operate | drift + bias + audit log | mod-07 ex-04 + mod-03 |

Companion projects: [project-4-governance](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-4-governance) (audit trail + GDPR) + [project-5-llmops](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-5-llmops) (guardrails + rate-limit + cost-meter).
