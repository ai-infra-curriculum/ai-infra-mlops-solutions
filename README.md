# AI Infrastructure MLOps Engineer — Solutions Repository

<!-- aicg:site-banner -->
> 🎓 Part of the free, open-source **AI Career Curriculum** ecosystem — [Infrastructure](https://github.com/ai-infra-curriculum) · [ML Engineering](https://github.com/ml-engineering-curriculum) · [AI Engineering](https://github.com/ai-engineering-curriculum) · [Governance](https://github.com/ai-governance-curriculum). Live cohorts &amp; team programs: **[ai-infra-curriculum.github.io](https://ai-infra-curriculum.github.io/)**.
<!-- /aicg:site-banner -->

<!-- aicg:sponsor -->
> 💜 **[Sponsor this curriculum](https://github.com/sponsors/AI-Infra-Curriculum)** — sponsorships keep the whole open-source AI Career Curriculum free and moving.
<!-- /aicg:sponsor -->

> **Status**: ✅ **Published** — 10 modules, 5 projects, 50 reference solutions live as of 2026-05.
> Content is AI-assisted and undergoing human review; treat as a learning reference, cross-check with primary sources.

Reference implementations for the **AI Infrastructure MLOps Engineer** learning track ([ai-infra-mlops-learning](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning)).

For the authoritative list of what is covered, see [`SOLUTIONS_INDEX.md`](./SOLUTIONS_INDEX.md).

## What's new — 2026-05-27

Module-level `SOLUTION.md` design-rationale docs for all 10 modules (`01-mlops-foundations` through `10-advanced-topics`) explain *why* the reference implementations are shaped the way they are — the registry / monitoring / governance patterns that scale from one model to many. Audit score: 65 → 67.

## What's in here

- **`modules/`** — Worked solutions for module-level exercises, organized one directory per module slug (`01-mlops-foundations` through `10-advanced-topics`).
- **`projects/`** — Production-grade reference implementations for the 5 capstone projects:
  - `project-1-ml-pipeline` — end-to-end training, deployment, monitoring
  - `project-2-model-serving` — multi-environment serving and rollout
  - `project-3-experimentation` — experiment tracking and A/B test infra
  - `project-4-governance` — model registry, lineage, compliance
  - `project-5-llmops` — LLM-focused operations and observability
- **`guides/`** — Implementation notes and troubleshooting walkthroughs.
- **`resources/`** — Shared references used across modules and projects.
- **[`LEARNING_GUIDE.md`](./LEARNING_GUIDE.md)** — Recommended path through the solutions.
- **[`CURRICULUM.md`](./CURRICULUM.md)** — Mapping back to the learning track's module structure.

## How to use this repository

1. **Attempt the exercise yourself first** in the learning repo — solutions only help if you've struggled with the problem.
2. **Compare your approach** to the solution. Look at structure, error handling, and test coverage rather than just whether the code "works."
3. **Read the SOLUTION notes** where present — they explain *why* a particular pattern was chosen.
4. **Extend the solution.** Try the bonus challenges or harden the production surface (rate limiting, observability, SLOs).

## Prerequisites

You should have completed (or be working through):

- The [Engineer track](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) — production ML systems, distributed training, MLOps fundamentals.
- The corresponding module in [ai-infra-mlops-learning](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning) for the exercise you are reviewing.

**Experience level**: Intermediate (2–4 years of engineering experience).
**Time commitment**: 580 hours total across the track.

## Learning objectives

The MLOps Engineer track prepares you to:

- Design and operate end-to-end MLOps pipelines (training → deployment → monitoring).
- Automate ML model deployment and rollback safely.
- Build feature stores, experiment tracking, and model registry systems.
- Implement model governance, lineage, and compliance frameworks.
- Detect data and prediction drift in production.
- Enable data scientists to ship models without platform-team bottlenecks.

## Related repositories

- [ai-infra-mlops-learning](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning) — the companion learning materials.
- [ai-infra-engineer-learning](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) — recommended prerequisite track.
- [ai-infra-ml-platform-learning](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning) — natural follow-on track for platform-builder paths.

## Known limitations

- **Content is AI-assisted and partly under human review.** Cross-check with vendor docs and production references before adopting patterns wholesale.
- Some `Dockerfile`/`compose`/`k8s` manifests are illustrative rather than fully runnable in your environment without configuration.
- Where a solution is intentionally schematic, the relevant `SOLUTION.md` (or top-of-file comment) explains what is real vs. what is stubbed.

## Contributing

Issues, corrections, and pull requests are welcome. See [`CONTRIBUTING.md`](./CONTRIBUTING.md). The most useful contributions right now are:

- Fixing factual errors or stale references.
- Adding `SOLUTION.md` notes that explain the *why* behind a reference implementation.
- Improving runnable validation for the project-level reference architectures.

## License

See [`LICENSE`](./LICENSE).

---

**Last updated**: 2026-05-25
**Maintainer**: AI Infrastructure Curriculum Project

---

<!-- aicg:maintained-by -->
Maintained by [VeriSwarm.ai](https://veriswarm.ai)
