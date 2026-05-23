# Vault + ESO Secret Management — Solution

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/09-security/exercises/exercise-02-secrets-management-with-hashicorp-vault.md).

Two files:
- `vault-policy.hcl` — least-privilege HCL policy (read kv prefix + DB creds, no writes)
- `external-secret.yaml` — ESO ClusterSecretStore + ExternalSecret syncing into native Kubernetes Secrets

Result: app reads from `iris-api-secrets`, never knows Vault exists. Rotation
happens in Vault; ESO refreshes every 15m.

Companion: [engineer-solutions/mod-109 ex-07](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-109-infrastructure-as-code/exercise-07-secret-management).
