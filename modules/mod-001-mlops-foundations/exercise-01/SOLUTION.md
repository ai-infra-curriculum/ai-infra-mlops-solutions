# Exercise 01 — MLOps Maturity Assessment

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-01-mlops-maturity-assessment.md).
Companion artifact: [`ASSESSMENT.md`](ASSESSMENT.md).

## 1. Solution overview

The exercise asks the learner to place a team on a maturity ladder, then justify the next
5 investments and lay them out on a 6-month roadmap. The reference answer treats the
assessment as a *forcing function* for prioritization: capabilities are compared side by
side (current vs. 12-month target) so the roadmap flows from the largest current gaps
that also unblock later work.

Cross-repo companion: see
[engineer-solutions/mod-106 exercise-01-mlops-maturity-assessment](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-01-mlops-maturity-assessment)
for the deeper, filled-in version.

## 2. Worked answer & implementation

The complete worked answer lives in [`ASSESSMENT.md`](ASSESSMENT.md). Its structure:

- A one-line **team profile** (size, models in prod, current deploy method).
- A **current level** call (1 – Manual, in the sample).
- A **capability matrix** with a row per practice area (data validation, feature
  engineering, tracking, registry, CI/CD, monitoring, retraining) and columns for
  *current* and *12-month target*.
- A **top-5 next investments** list in priority order, each with a rough duration.
- A **6-month roadmap** table with month, investment, owner, and expected outcome.

### Decision rationale

The reference is deliberately opinionated about ordering. Two rules drive it:

1. **Foundations before feedback loops.** MLflow tracking, DVC versioning, and the
   model registry come before drift monitoring because without lineage you cannot act
   on a drift signal — you cannot reproduce the training run to compare against.
2. **Manual → gated → automated.** Every capability is promoted through a gated middle
   step (manual promotion with history) before being fully automated, so review
   discipline is in place before the tooling removes humans from the loop.

## 3. Validation steps

Grader / self-review:

1. Open [`ASSESSMENT.md`](ASSESSMENT.md) and confirm every capability row has both a
   *current* and *target* value — no blanks.
2. Confirm the top-5 investments each appear in the 6-month roadmap; roadmap items
   without a rationale in the top-5 list are a smell.
3. Confirm the ordering respects "foundations before feedback loops" — tracking /
   versioning / registry appear before drift monitoring, canary, or triggered retraining.
4. Confirm each roadmap row names an **owner** and an **outcome** (not just a task).

## 4. Rubric

| Area | Pass | Common failure mode |
|---|---|---|
| Level call | Level 0–4 named, with 1-sentence justification | Level asserted without evidence |
| Capability matrix | ≥ 6 rows, current *and* target filled | Only "target" filled — no baseline |
| Top-5 investments | Ordered, each with duration | List of 10+ things, no order |
| Roadmap | Month, owner, outcome per row | Task list only, no owners / outcomes |
| Sequencing | Tracking / versioning / registry precede drift + retraining | Drift monitoring in month 1 |
| Realism | Total effort fits the stated headcount over 6 months | 20 person-months of work in 6 |

## 5. Common mistakes

Drawn from the module-level "common mistakes graders see" list plus this exercise's
sequencing risks:

- **Tracking locally, never centrally** — a top-5 investment that keeps MLflow on a
  laptop; no one else can compare runs.
- **Skipping the registry step** — jumping from tracking straight to CI/CD, so promoted
  models still lack a canonical location.
- **Drift monitoring in month 1** — signals with no ability to retrain / redeploy.
- **Roadmap without owners** — the plan reads as a wish list rather than a commitment.
- **Ignoring the "12-month target" column** — top-5 items don't map to any target in
  the matrix.

## 6. References

- Learning exercise:
  `lessons/mod-001-mlops-foundations/exercises/exercise-01-mlops-maturity-assessment.md`
  (ai-infra-mlops-learning).
- Local companion artifact: [`ASSESSMENT.md`](ASSESSMENT.md).
- Deeper filled-in reference:
  [engineer-solutions/mod-106 exercise-01-mlops-maturity-assessment](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-01-mlops-maturity-assessment).
- Module-level rationale: [`../SOLUTION.md`](../SOLUTION.md).
