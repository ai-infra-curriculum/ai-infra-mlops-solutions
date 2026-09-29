# SOLUTION — Exercise 1: ML Threat Modeling & OWASP ML Top 10

Reference solution for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-009-security/exercises/exercise-01-ml-threat-modeling-owasp-ml-top-10.md).

## 1. Solution overview

The exercise asks learners to walk a real-shaped MLOps system
(the `iris-api` used across this module) through the ten OWASP
Machine Learning Security Top 10 categories, decide which threats
actually apply, assign severity, and pick the top items worth
mitigating first.

The reference threat model is in [`THREAT_MODEL.md`](THREAT_MODEL.md);
this file is the grading companion — what "good" looks like, how
to check it, and where the model connects to the rest of the
module (ex-03 signing, ex-04 hardened pod, ex-05 composition).

## 2. Worked answer & Implementation

The full threat table lives in [`THREAT_MODEL.md`](THREAT_MODEL.md).
Key structural moves in that model, and why each one is deliberate:

- **One row per OWASP ML category (ML01–ML10).** Full coverage is
  the point; a threat model that quietly skips categories is a
  threat model with blind spots.
- **Severity is `iris-api`-specific, not category-generic.** For
  a low-stakes classifier served internally, model inversion
  (ML03) and membership inference (ML04) are low; supply-chain
  tampering (ML06, ML10) is high. A different system would
  reorder these — the reasoning is what matters, not the labels.
- **Every mitigation names a concrete control**, not a slogan.
  "Rate limiting" not "protect the endpoint"; "cosign +
  Kyverno admission" not "supply-chain hygiene".
- **Top-3 prioritization is by severity × tractability.** ML10,
  ML02, ML06 all trace to signature/provenance controls the
  learner will actually implement in ex-03. Prioritization is
  about what leads to real work, not a full backlog.

The three items the reference elevates:
1. **ML10 (deployment)** — admission policy for signed images
   (Kyverno) — implemented in ex-03.
2. **ML02 (data poisoning)** — dataset provenance via DVC +
   signed training sets.
3. **ML06 (corrupted model output)** — safetensors + cosign for
   model artifacts — implemented in ex-03.

## 3. Validation steps

Grade a learner submission by walking these checks:

1. Do rows exist for **all ten** OWASP ML categories? Missing
   categories are the most common failure.
2. For each row, is the threat phrased **against this system**,
   not restated from the category description?
3. Does every row name a **concrete mitigation** the learner
   could point at in code, config, or process?
4. Is severity **justified** by system context (data
   sensitivity, exposure, blast radius) rather than copied from
   the OWASP category?
5. Are the **top 3** picks defensible? A learner who prioritizes
   three low-severity items should be able to explain why.
6. Optional bridge: MITRE ATLAS tactics (Reconnaissance,
   ML Attack Staging, Exfiltration, etc.) and NIST AI RMF
   functions (Govern / Map / Measure / Manage) can be layered on
   top for a fuller model, but the exercise scope is OWASP ML.

## 4. Rubric

| Dimension | Weight | Pass criteria |
|---|---|---|
| Category coverage | 25% | All ten OWASP ML categories addressed. |
| System-specific framing | 20% | Each threat described in terms of `iris-api`, not the category abstract. |
| Mitigation concreteness | 20% | Every mitigation names a control (tool, policy, or process step). |
| Severity justification | 15% | Severity ties to data sensitivity, exposure, or blast radius. |
| Top-3 prioritization | 15% | Selection is defended; picks route to real implementation work. |
| Cross-reference discipline | 5% | Links to ex-03/ex-04/ex-05 where mitigations actually land. |

## 5. Common mistakes

- **Restating the OWASP category as the threat.** "Model
  inversion could happen" is not a threat model; describe how
  inversion applies to *this* endpoint's logit precision and
  request volume.
- **Uniform severity.** Marking every row "high" hides the
  prioritization signal — the point of severity is to force a
  choice.
- **Slogan mitigations.** "Improve security posture" is not a
  control. Name a tool, policy, or step.
- **Skipping training-data threats.** Learners tend to focus on
  the inference surface. ML02 (poisoning) and ML07 (transfer
  learning) matter and are often the most tractable to mitigate
  via provenance.
- **Ignoring the deployment path.** ML10 (unsigned artifact
  deployed to prod) is a supply-chain problem that connects
  directly to ex-03; skipping it isolates the threat model from
  the rest of the module.

## 6. References

- OWASP Machine Learning Security Top 10 (official project) —
  https://owasp.org/www-project-machine-learning-security-top-10/
- MITRE ATLAS (adversary tactics against ML systems) —
  https://atlas.mitre.org/
- NIST AI Risk Management Framework (Govern / Map / Measure /
  Manage functions) — https://www.nist.gov/itl/ai-risk-management-framework
- Local: [`THREAT_MODEL.md`](THREAT_MODEL.md) — reference
  threat table for `iris-api`.
- Local: [`../SOLUTION.md`](../SOLUTION.md) — module-level
  rationale (why signing, hashing, rate limits, PII redaction,
  and least-privilege model access are the reference controls).
- Local: [`../exercise-03/`](../exercise-03/) — where the top-3
  mitigations from this model are implemented.
