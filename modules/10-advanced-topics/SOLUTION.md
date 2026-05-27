# SOLUTION — Advanced MLOps Topics

> Read this *after* everything else in the MLOps track. This
> document gives you the vocabulary to read the next 12 months of
> MLOps research and judge which patterns are worth adopting.

## What this module is really teaching

The MLOps frontier in 2026 includes:
- LLMOps as a distinct discipline.
- AgentOps for tool-using agents.
- Continuous learning systems.
- Federated learning + privacy-preserving ML.

The reference solutions touch each — not to master them, but to
make the frontier legible.

## Architectural decisions and *why*

### Decision 1: LLMOps as a superset of MLOps

LLM serving adds prompt management, eval pipelines for natural-
language outputs, hallucination detection, and tool-call
observability. The reference treats these as MLOps extensions,
not replacements.

### Decision 2: Eval-driven LLM development

For LLMs, the equivalent of "test coverage" is "eval coverage."
Every prompt change runs against a curated eval set with
LLM-as-judge or human-rater grading.

### Decision 3: AgentOps requires tool observability

Agents that call tools need their tool calls instrumented as
spans (OpenTelemetry). Without span-level visibility, debugging
agent failures is impossible.

### Decision 4: Continuous learning gated by drift signal

The reference's continuous-learning pipeline retrains on:
- Data drift exceeding threshold.
- Concept drift on labeled samples.
- Explicit "we have new training data" signal.

Calendar-based continuous learning is wasteful; signal-based is
cost-effective.

### Decision 5: Federated learning kept research-stage

Federated learning is genuinely useful for some workloads
(healthcare, mobile). For most production teams, it's not yet
worth the complexity. The reference documents the trade-off
without forcing a deployment.

## Trade-offs we deliberately accepted

- LLM eval is expensive (LLM-as-judge calls cost money).
- AgentOps tooling is immature in 2026.
- Federated learning is research; we don't pretend otherwise.

## Common mistakes graders see

1. **LLM deployments without prompt versioning**: prompt
   drift is invisible.
2. **No eval pipeline for LLMs**: regressions ship.
3. **Agent traces not stored**: debugging is guesswork.
4. **Federated learning chosen for marketing**: cost without
   benefit.

## When to go beyond this implementation

- Adopt **dedicated LLMOps tooling** (Langfuse, Helicone,
  Galileo).
- Build **automated red-teaming** for production agents.
- Move to **on-device inference** for privacy-sensitive
  workloads.

## Related curriculum touchpoints

- ``engineer/mod-110-llm-infrastructure`` — LLM serving
  foundation.
- ``architect/projects/project-303-llm-rag-platform`` —
  enterprise LLM architecture.
