# Exercise 05 — Write an MLOps Team Charter

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-001-mlops-foundations/exercises/exercise-05-write-an-mlops-team-charter.md).
Companion artifact: [`CHARTER.md`](CHARTER.md).

## 1. Solution overview

The exercise asks the learner to write a charter for an MLOps / ML platform team.
The reference answer is opinionated: a good charter is short, names both *what the
team owns* and *what it does not*, states an explicit engagement model (self-serve /
office hours / project intake ratios), commits to support tiers with response times,
and picks measurable success metrics.

Cross-repo companion: see
[engineer-solutions/mod-106 ex-14 (ml-platform-operating-model) CHARTER.md](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-14-ml-platform-operating-model/CHARTER.md)
for the fuller version.

## 2. Worked answer & implementation

The complete worked charter lives in [`CHARTER.md`](CHARTER.md). Its sections:

- **Mission** — one sentence: *"Make it easy and safe for data scientists + product
  engineers to ship and operate ML in production."*
- **What we own** — 7 concrete surfaces (tracking + registry, feature store, serving
  runtime, pipeline framework, drift + bias monitoring, CI/CD plumbing, cost
  attribution).
- **What we do NOT own** — model architecture, business metrics, feature semantics,
  retraining cadence choices. Explicit non-ownership is the point.
- **Engagement model** — 60% self-serve, 30% office hours, 10% project intake with
  a ~6-week SLA on intake.
- **Support tiers** — Tier 1 (24/7, 30-min response), Tier 2 (working hours,
  same-day), Tier 3 (quarterly planning).
- **Success metrics** — trained → prod < 1 week; MTBF > 30 days; MTTR < 1 hour;
  self-serve adoption > 80%; 100% cost-tag coverage.
- **Failure modes** — gatekeeper trap, custom-everywhere, slow batching.

### Decision rationale

Two ideas drive the shape:

1. **Ownership is a claim about accountability, not tooling.** The "what we do NOT own"
   section prevents the platform team from being blamed for model behavior it does not
   decide.
2. **The engagement model is a load balancer.** Publishing a 60 / 30 / 10 split with
   an SLA turns interruptions into a queue the team can defend, which is why the
   charter's failure modes name *gatekeeper* and *slow batching* — both are what
   happens when the split drifts.

## 3. Validation steps

Grader / self-review:

1. Confirm the charter fits on a single page — if it does not, it is being read as
   documentation, not as a contract.
2. Confirm every "what we own" item has an implicit owner within the team; nothing
   listed that requires another team.
3. Confirm the "what we do NOT own" section names concrete counter-owners (data
   scientists, product + analytics, data eng), not just "the business."
4. Confirm each success metric is a number the team can measure this quarter — not
   an aspiration.
5. Confirm the support tiers name a response window, not just a channel.

## 4. Rubric

| Area | Pass | Common failure mode |
|---|---|---|
| Mission | One sentence, active voice | Paragraph of buzzwords |
| Owns / does-not-own | Both lists present; counter-owners named | Only "we own" — no boundary |
| Engagement model | Percentages sum to 100 with an intake SLA | "Contact us" with no queue policy |
| Support tiers | Response times attached to each tier | Tier names only |
| Success metrics | Each metric measurable this quarter | "Improve platform quality" |
| Failure modes | Named risks the team is committing to avoid | Absent; charter reads as marketing |

## 5. Common mistakes

Drawn from [`CHARTER.md`](CHARTER.md)'s failure-modes list and the module-level
"common mistakes graders see":

- **Gatekeeper trap** — a charter that centralizes decisions the team should not own,
  slowing every model change to platform review.
- **Custom-everywhere** — accepting every bespoke request; the self-serve ratio
  collapses.
- **Slow batching** — a 6-month roadmap with no quick wins; stakeholders lose faith
  before the platform lands.
- **No non-ownership statement** — the platform gets held responsible for model
  quality, drift, and business metric outcomes it does not control.
- **Unmeasurable metrics** — targets like "improve productivity" that cannot be
  evaluated at quarter-end.

## 6. References

- Learning exercise:
  `lessons/mod-001-mlops-foundations/exercises/exercise-05-write-an-mlops-team-charter.md`
  (ai-infra-mlops-learning).
- Local companion artifact: [`CHARTER.md`](CHARTER.md).
- Fuller charter reference:
  [engineer-solutions/mod-106 ex-14 (ml-platform-operating-model) CHARTER.md](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-14-ml-platform-operating-model/CHARTER.md).
- Module-level rationale: [`../SOLUTION.md`](../SOLUTION.md).
