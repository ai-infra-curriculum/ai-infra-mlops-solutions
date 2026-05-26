# Supply Chain (SLSA + SBOM + cosign) — Solution

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/09-security/exercises/exercise-03-supply-chain-security-slsa-sbom-cosign.md).

- `sign.sh` — local build + SBOM + scan + sign + attest
- `kyverno-policy.yaml` — cluster-admission gate requiring keyless cosign signature

Companion: [engineer-solutions/mod-103 ex-10](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-103-containerization/exercise-10-sbom-and-supply-chain) for the full SLSA L2 workflow + GHA.
