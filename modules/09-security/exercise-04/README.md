# Container Runtime Security — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/09-security/exercises/exercise-04-container-runtime-security.md).

- `podsecurity.yaml` — hardened pod spec (non-root, read-only fs, drop caps, seccomp)
- `networkpolicy.yaml` — default-deny + explicit egress for DNS + DB + S3 only

Combine with [Kyverno require-resource-limits / disallow-host-namespace](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-109-infrastructure-as-code/exercise-08-policy-as-code/kyverno) to enforce these patterns cluster-wide.
