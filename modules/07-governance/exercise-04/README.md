# Audit Logging — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/07-governance/exercises/exercise-04-audit-logging-compliance-tracking.md).

Hash-chain (Merkle-style) audit log:
- Each event references the prior event's hash
- `verify()` walks the chain; tampering with any past event makes its (and successor) hashes invalid

For production, write each event to an append-only store (S3 with object-lock, or a Postgres table with row-level write-once policy).
