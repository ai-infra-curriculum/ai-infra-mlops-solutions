# Threat Model — iris-api (OWASP ML Top 10)

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-009-security/exercises/exercise-01-ml-threat-modeling-owasp-ml-top-10.md).

| # | OWASP ML | Threat against iris-api | Severity | Mitigation |
|---|---|---|---|---|
| ML01 | Input manipulation | Crafted feature vector → adversarial misclassification | medium | input bounds + adversarial training |
| ML02 | Data poisoning | Compromised training data → backdoor model | high | data provenance (DVC) + signed datasets |
| ML03 | Model inversion | Extract training samples from logits | low | restrict logit precision; rate limit |
| ML04 | Membership inference | Determine if a user was in training set | low | differential privacy (DP-SGD) at training |
| ML05 | Model stealing | Replicate model via queries | medium | rate limiting + output rounding |
| ML06 | Corrupted output | Tampered model file on disk | high | signed safetensors + cosign verification |
| ML07 | Transfer learning attack | Hostile fine-tuning of public base | medium | only fine-tune trusted bases; verify hashes |
| ML08 | Model skewing | Slow drift introduced via biased feedback | medium | drift monitoring + bias review |
| ML09 | Output integrity attack | Output post-processing tampered | medium | sign serving outputs; client verifies |
| ML10 | Model deployment | Unsigned image deployed to prod | high | cosign + Kyverno admission policy |

## Top 3 to act on
1. **ML10** — admission policy enforcing signed images (Kyverno) — see ex-03
2. **ML02** — DVC + signed training datasets — see mlops-learning module 06
3. **ML06** — safetensors + cosign for model artifacts — see ex-03
