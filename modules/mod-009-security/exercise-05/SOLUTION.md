# SOLUTION — Exercise 5: Complete MLOps Security Framework

Reference solution for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-009-security/exercises/exercise-05-complete-mlops-security-framework.md).

## 1. Solution overview

The exercise asks learners to *compose* the four prior module
exercises into one defense-in-depth deployment for the
`iris-api` system, rather than treat each control as standalone.
The reference composition is captured in
[`FRAMEWORK.md`](FRAMEWORK.md); this file is the grading and
review companion — what a coherent stack looks like, and where
learners tend to lose the layering.

Nothing new is invented at this step. The exercise is a
correctness check: does the deploy path actually chain
threat model → secrets → supply chain → runtime → operate?

## 2. Worked answer & Implementation

The composed pipeline diagram and phase table live in
[`FRAMEWORK.md`](FRAMEWORK.md). The structural moves that make it
a *framework* rather than a checklist:

- **The threat model (ex-01) is the driver.** Every layer downstream
  answers a specific OWASP ML row (ML02, ML06, ML10 in
  particular). If a control isn't traceable to a threat, it's
  ceremony.
- **Secrets (ex-02) sit outside the pipeline artifacts.** Vault +
  ESO sync at deploy time, so no credential ever lands in an
  image or a git commit. This is what makes the rest of the
  chain safe to inspect openly.
- **Supply chain (ex-03) is the *gate*, not the audit.** Build-time
  signing + SBOM + scan feeds a Kyverno admission policy that
  refuses unsigned images at deploy time. The signature only has
  value because the admission gate enforces it.
- **Runtime (ex-04) assumes the artifact is trusted but the
  workload can still be attacked.** Pod hardening + NetworkPolicy
  keeps a compromised container from turning into lateral
  movement.
- **Operate is a first-class phase.** Drift monitoring, bias
  review, and a tamper-evident audit log (see mod-07 ex-04)
  close the loop on ML02 (poisoning showing up as drift) and
  ML08 (skewing).

Phase mapping (from [`FRAMEWORK.md`](FRAMEWORK.md)):

| Phase | Defense | Source |
|---|---|---|
| Code | SAST + dep scanning | engineer-solutions/mod-103 ex-12 |
| Build | image scan + SBOM + sign | ex-03 |
| Deploy | admission policy | ex-03 + engineer-solutions/mod-109 ex-08 |
| Runtime | hardened pod + netpol | ex-04 |
| Operate | drift + bias + audit log | mod-07 ex-04 + mod-03 |

## 3. Validation steps

Grade a learner submission by walking these checks:

1. **Traceability**: pick any three controls in the submission
   and confirm each one maps back to an OWASP ML row from ex-01.
   A control with no threat is a red flag.
2. **Gate, not just sign**: signing (ex-03) is only credit if the
   submission also names the enforcement point (Kyverno
   admission or equivalent). Signed-but-not-enforced is a common
   miss.
3. **Secret flow**: no secrets in image layers, git history, or
   manifest YAML committed to the repo — verify by inspecting
   the deploy manifests and confirming ESO is the source.
4. **Runtime hardening**: pod spec has non-root user, read-only
   root filesystem, dropped capabilities; NetworkPolicy exists
   and is default-deny for the namespace.
5. **Operate loop**: at least one runtime signal (drift, bias,
   or model output integrity) is wired to the audit log.
6. **NIST AI RMF alignment (optional but common)**: the
   Govern / Map / Measure / Manage functions each have at least
   one control from the framework attached.

## 4. Rubric

| Dimension | Weight | Pass criteria |
|---|---|---|
| Threat-to-control traceability | 25% | Every layer maps back to a specific OWASP ML row. |
| Supply-chain enforcement | 20% | Sign step *and* admission gate both present. |
| Secret handling | 15% | Vault/ESO flow used; no secrets in artifacts. |
| Runtime hardening | 15% | Pod spec hardened; NetworkPolicy default-deny. |
| Operate loop | 15% | Drift, bias, or output integrity monitoring routes to audit log. |
| Composition clarity | 10% | Framework reads as one deploy path, not five detached ex-N summaries. |

## 5. Common mistakes

Grader-visible failure patterns, mostly inherited from the
module-level rationale:

- **Signed but not enforced.** Cosign at build time with no
  admission policy = the same attack surface as unsigned. This
  is the single most common gap in a "complete" framework.
- **Secrets sneaking into ConfigMaps or Helm values.** Learners
  who use ESO for the app secrets but hard-code the registry pull
  token in a manifest still fail the secret-handling check.
- **Runtime hardening treated as optional.** A hardened pipeline
  that ships to a permissive pod spec surrenders most of the
  gain from ex-03.
- **No Operate phase.** Framework ends at deploy. ML02
  (poisoning) and ML08 (skewing) only show up post-deploy — no
  drift monitoring means these threats are effectively unmitigated.
- **Restated ex-01–ex-04 side by side without composition.** A
  framework is a *chain* — the output of each phase is the input
  to the next. Four disconnected write-ups don't clear the bar.
- **Same account credentials across training + serving + dev.**
  Called out in the module-level rationale; still shows up in
  learner submissions.

## 6. References

- OWASP Machine Learning Security Top 10 (official project) —
  https://owasp.org/www-project-machine-learning-security-top-10/
- MITRE ATLAS (adversary tactics against ML systems) —
  https://atlas.mitre.org/
- NIST AI Risk Management Framework (Govern / Map / Measure /
  Manage) — https://www.nist.gov/itl/ai-risk-management-framework
- Local: [`FRAMEWORK.md`](FRAMEWORK.md) — composed pipeline
  diagram and phase table.
- Local: [`../SOLUTION.md`](../SOLUTION.md) — module-level
  rationale for signing, hashing, rate limits, PII redaction,
  and least-privilege model access.
- Local: [`../exercise-01/SOLUTION.md`](../exercise-01/SOLUTION.md)
  — the threat model this framework is answering.
- Local: [`../exercise-02/`](../exercise-02/),
  [`../exercise-03/`](../exercise-03/),
  [`../exercise-04/`](../exercise-04/) — the individual layers
  being composed here.
- Companion projects: `projects/project-04-governance`
  (audit trail + GDPR) and `projects/project-05-llmops`
  (guardrails, rate-limit, cost-meter).
