# SOLUTION — Exercise 1: Production Readiness Checklist (75 min)

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-008-production-ops/exercises/exercise-01-production-readiness-checklist.md).

## 1. Solution overview

Produce a production readiness checklist tailored to an ML inference
service and demonstrate that a candidate service either passes each
item or has an explicit exception. The checklist covers seven areas
that map to the ways ML services fail in production: architecture,
code/tests, deployment, observability, reliability, security, and
operations.

The worked answer is the checklist in [CHECKLIST.md](CHECKLIST.md).
Learners run through it against their own service (or the reference
`iris-api`) and record pass / fail / N/A + evidence.

## 2. Worked answer

See [CHECKLIST.md](CHECKLIST.md) for the full list. Highlights that
distinguish an ML readiness checklist from a generic web-service
readiness checklist:

- **Model artifact reproducibility** (`DVC or registry`) — a rollback
  is meaningless if the previous model binary is not addressable.
- **Model drift metric on the observability line** — service-level
  latency + error rate are necessary but not sufficient; a healthy
  service can be silently regressed on quality.
- **Load test at target RPS *and* target latency** — inference
  latency degrades non-linearly with concurrency (batch effects,
  GPU queueing), so pass/fail must be measured at the SLO point.
- **Runbook for the top 5 alerts** — the on-call playbook must
  include ML-specific failure modes (quality regression, latency
  degradation, OOM, stuck training, stale features), because
  generic SRE runbooks do not cover them (see module-level
  SOLUTION.md, "Decision 3").

### How to use the checklist

1. Copy the file next to the service's runbook.
2. For each item, record `pass` / `fail` / `N/A` with a one-line
   evidence pointer (dashboard URL, PR link, or waived-by).
3. Any `fail` blocks the go-live review; any `N/A` needs a reason.
4. Re-run at every major release and quarterly for drift.

## Implementation

The concrete implementation of this exercise is the artifact at
[CHECKLIST.md](CHECKLIST.md) plus the process for running it:

- **Where it lives** — the checklist file is committed next to the
  service it audits (e.g. `services/<name>/CHECKLIST.md`), not in a
  central wiki, so that the audit trail moves with the code.
- **Who fills it in** — the service owner completes the checklist
  before the go-live review; the reviewer verifies each `pass` has
  an evidence pointer that resolves.
- **Automation hooks** — the observability, security, and
  deployment groups map to CI checks that can pre-populate `pass`
  entries: image scan (Trivy) → security row, load test job at
  target RPS → reliability row, artifact URI recorded at build
  time → code/tests row.
- **Cadence** — the checklist is re-run at every major release and
  quarterly for drift; the completed copy is kept in the service's
  repo so waived (`N/A`) items remain visible in the audit trail.

## 3. Validation steps

- The checklist file is present at
  `modules/mod-008-production-ops/exercise-01/CHECKLIST.md`.
- Every group (Architecture, Code, Deployment, Observability,
  Reliability, Security, Operations) has at least one checkbox.
- ML-specific items are present: model artifact reproducibility,
  model drift metric, load test at target latency.
- The learner's completed checklist (their copy) has evidence
  attached to every non-N/A item.

## 4. Rubric / review checklist

| Weight | Criterion | Evidence |
|---|---|---|
| 25% | All seven groups covered, no group left blank | Section headings present |
| 20% | ML-specific items present (drift, artifact reproducibility, latency-aware load test) | Items visible in the observability + code/tests + deployment groups |
| 20% | Each item has a way to *verify* it, not just assert it | Evidence pointer per item on the learner's copy |
| 15% | Rollback procedure is documented **and tested**, not just described | Link to a rehearsal record or a documented drill date |
| 10% | Alerts include SLO burn-rate (multi-window), not only static thresholds | Alert group in observability references burn-rate |
| 10% | Runbook covers ML-specific alerts, not only generic web-service alerts | Runbook file listed with entries for quality regression / drift / OOM |

Pass = 80% weighted score with no missing group.

## 5. Common mistakes

- Treating the checklist as a generic web-service checklist and
  dropping the model-drift + artifact-reproducibility items.
- Marking "Rollback procedure documented" without having ever
  rehearsed one — documentation without a drill is aspirational.
- Skipping the "load test at target RPS *and* target latency" line
  because a single-RPS smoke test passed.
- Alerts on CPU/RAM only, no SLO burn-rate — pages fire late or
  never.
- No `N/A` justification, so waived items disappear from the audit
  trail.

## 6. References

- OWASP Machine Learning Security Top 10 —
  <https://owasp.org/www-project-machine-learning-security-top-10/>
  (informs the Security group: image scan, network policy, auth on
  every endpoint).
- NIST AI Risk Management Framework —
  <https://www.nist.gov/itl/ai-risk-management-framework> (Govern +
  Manage functions frame the Operations group: runbooks, on-call,
  DR).
- Module-level rationale: [../SOLUTION.md](../SOLUTION.md), esp.
  "Decision 3: ML-specific on-call playbook".
- Companion checklist artifact: [CHECKLIST.md](CHECKLIST.md).
