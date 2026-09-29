# Exercise 03 — Spot the MLOps Anti-Patterns

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-03-spot-the-mlops-anti-patterns.md).
Companion artifact: [`ANTI_PATTERNS.md`](ANTI_PATTERNS.md).

## 1. Solution overview

The exercise gives the learner a workflow narrative and asks them to (a) identify the
MLOps anti-patterns, (b) explain why each is a problem, (c) prescribe the fix, and
(d) rank them by blast radius. The reference solution enumerates 8 anti-patterns, then
argues the ordering from a *recovery* lens: anti-patterns that block the ability to
respond to an incident are ranked ahead of those that merely accelerate incidents.

Cross-repo companion: see
[engineer-solutions/mod-106 ex-13 (reproducibility-audit)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-13-reproducibility-audit),
which has an `audit_runner.py` that scores reproducibility per model.

## 2. Worked answer & implementation

The complete worked answer lives in [`ANTI_PATTERNS.md`](ANTI_PATTERNS.md). It contains:

- A **table of 8 anti-patterns** — each row lists the pattern, *why it's a problem*,
  and the *fix*.
- A **blast-radius ranking** with the reasoning for the top entries.
- A **one-pager** making the case for fixing #1 (data lineage) first, framed as a
  2-week DVC + MLflow investment.

### The 8 anti-patterns (summary)

1. Manual data copy to laptop → stage in a versioned warehouse.
2. Notebook training → convert to script; gate via PR + tests.
3. Google-Drive model store → use a model registry (MLflow / Vertex).
4. Manual `.pkl` → prod → registry-driven deploys with stages.
5. "Container up" as monitoring → Prometheus model metrics + drift dashboard.
6. No data lineage → dataset hash + DVC + lineage capture.
7. No retraining cadence → scheduled retrain + drift-triggered retrain.
8. No automated tests on model code → CI: lint + unit + integration tests.

### Ranking rationale

The reference orders by *ability to recover*, not by *frequency of failure*:

1. **No data lineage** — blocks recovery from every other failure. If manual `.pkl`
   deploys cause an incident, missing lineage prevents rolling back to a known-good
   model or retraining it.
2. **Manual `.pkl` deploy** — single-point human bottleneck and recurring incident
   source.
3. **No monitoring** — the failure is silent, so user impact accumulates.
4. **Notebook training** — slow iteration, root cause of many secondary anti-patterns.

## 3. Validation steps

Grader / self-review:

1. Confirm each identified anti-pattern has all three columns filled: *why*, *fix*, and
   an explicit *fix* tool or practice — not just "add monitoring."
2. Confirm the ranking is justified with reasoning, not just an ordered list.
3. Confirm the "fix #1 first" one-pager frames the investment in **weeks**, not
   quarters — a proposal without a time box will not be prioritized.
4. Cross-check the fixes against the module-level "common mistakes graders see" list to
   catch obvious omissions (e.g., forgetting to log the model, prod creds on the
   experiment server).

## 4. Rubric

| Area | Pass | Common failure mode |
|---|---|---|
| Anti-pattern count | ≥ 6 distinct patterns identified | Only 2–3 patterns; workflow issues missed |
| Why column | Names the concrete failure that follows from the pattern | "It's bad practice" with no mechanism |
| Fix column | Names a specific tool or workflow, not just an abstract principle | "Use DevOps" |
| Ranking | Ordering justified from a recovery or blast-radius lens | Alphabetical or original-list order |
| One-pager | Case for fixing #1 framed with a duration and a clear "buys us" outcome | Aspirational; no time box |
| Cross-cutting | Fixes reflect module-level guardrails (registry-driven deploys, central tracking) | Fixes contradict module rationale |

## 5. Common mistakes

Drawn from [`ANTI_PATTERNS.md`](ANTI_PATTERNS.md) and the module-level "common mistakes
graders see" list:

- **Ranking by frequency, not blast radius** — hides the anti-patterns that block
  recovery.
- **Prescribing "add monitoring" without saying *what*** — infra-level container checks
  do not detect model degradation.
- **Fixing #2 (notebooks) before #6 (lineage)** — you gain iteration speed but still
  cannot reproduce or roll back.
- **Missing the model-registry fix for #3 and #4 together** — they are the same fix.
- **No case for #1 in weeks** — leadership will not fund an open-ended "improve
  lineage" ask.

## 6. References

- Learning exercise:
  `lessons/mod-001-mlops-foundations/exercises/exercise-03-spot-the-mlops-anti-patterns.md`
  (ai-infra-mlops-learning).
- Local companion artifact: [`ANTI_PATTERNS.md`](ANTI_PATTERNS.md).
- Reproducibility scoring reference:
  [engineer-solutions/mod-106 ex-13 (reproducibility-audit)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-13-reproducibility-audit).
- Module-level rationale: [`../SOLUTION.md`](../SOLUTION.md).
