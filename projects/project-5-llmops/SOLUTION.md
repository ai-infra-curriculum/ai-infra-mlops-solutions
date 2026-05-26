# SOLUTION — LLMOps Production System

> The runnable implementation lives in the **learning** repo at
> `ai-infra-mlops-learning/projects/project-5-llmops`. This file
> explains the design reasoning.

## What problem this solves

LLMs introduce failure modes that classical model serving doesn't:

1. **Prompt injection** — adversarial input changes the model's
   behavior or extracts data.
2. **PII leakage** — both into the model (from prompts) and out of
   the model (in responses).
3. **Unbounded cost** — a long-running, repeated, or runaway prompt
   can produce four-figure bills per session.
4. **No ground truth at inference** — you cannot validate the answer
   against a label; the system has to detect when its answer is
   suspect.

The reference implementation addresses all four with named
components in a single composable pipeline.

## Architectural decisions and *why*

### The full request pipeline: rate-limit → input-guard →
semantic-cache → RAG → vLLM upstream → output-guard → cost meter

Each stage is independently disable-able and instrumented. This is the
single most important property: when something is wrong in
production, you can disable one stage at a time to isolate the cause,
and the metrics on each stage tell you which one was responsible.

### vLLM as the upstream, isolated behind a clean interface

vLLM is the current best-of-breed inference backend, but the
architecture should survive replacing it with TGI, TensorRT-LLM, or a
managed API. The upstream interface is a thin adapter; the rest of
the pipeline is upstream-agnostic.

### Guardrails as regex *and* model — not either-or

Regex catches the obvious patterns at near-zero cost. A second
model-based check catches the patterns regex can't. Both are
operationally meaningful; choosing one is a false economy.

### Exact cache first, semantic cache as an upgrade seam

Exact cache (hash of prompt → response) is high-precision but
low-recall. Semantic cache (embedding similarity) trades precision
for recall and is much harder to get right (false hits are toxic for
quality). The reference ships exact and leaves the semantic upgrade
as a clearly-marked seam.

### tiktoken-based cost metering, in USD, per call

A cost figure that arrives at the end of the month is not actionable.
Per-call cost metering exported as a Prometheus metric makes cost a
*first-class operational signal*, same as latency.

### TTFT (time-to-first-token) as a first-class metric, not just
end-to-end latency

For streaming LLM responses, TTFT is what the user perceives. A 200ms
TTFT with 2s total feels fast; a 1.5s TTFT with 1.6s total feels
broken. Measuring only end-to-end hides the perceived-quality story.

## How to study

1. Read the learning project README.
2. `make up` to bring the stack up; `make vllm` to start the GPU
   upstream.
3. Read the gateway code top-down. The composition order in the
   pipeline is the most important thing to internalize.
4. `make test` for the guard + cost + API smoke tests.
5. Try adding a layer: upgrade exact cache to semantic, or add a new
   guard rule.

## What's deliberately simplified

- **No agent / tool-use architecture.** Single-shot RAG only.
- **No retrieval reranking.** Single-stage vector retrieval; the
  two-stage retrieval pattern lives in the architect-track LLM
  platform project.
- **No production-grade adversarial corpus.** The guard rules cover
  common patterns; a real deployment needs a maintained corpus.
- **No tenant-level cost ceilings.** The cost meter measures; it
  doesn't yet *limit*.
- **No model rotation strategy.** Single upstream model assumed; a
  real deployment routes per request class.

## Cross-references

| Topic | Deeper reference |
|---|---|
| Full LLM-infra module (14 exercises) | `engineer-solutions/mod-110` |
| Minimal vLLM launcher | `mlops-solutions/modules/10-advanced-topics/exercise-01/` |
| Minimal RAG | `mlops-solutions/modules/10-advanced-topics/exercise-02/` |
| LLM platform architecture | `architect-solutions/projects/project-303-llm-rag-platform/` |
| Adversarial-defense framing | `security-solutions/project-3-adversarial-defense/` |

## Production gap checklist

- [ ] Tenant-level cost ceilings with enforcement, not just metering
- [ ] Retrieval reranker (cross-encoder) between vector store and LLM
- [ ] Adversarial-corpus maintenance cadence
- [ ] Per-prompt-class request routing (cheap model → expensive
      fallback)
- [ ] Hallucination detection tied to retrieval evidence
- [ ] Conversation-level state and memory governance
- [ ] PII detection on the *retrieval corpus*, not just on prompts

## Time budget

- **Skim**: 1 hour.
- **Deep**: 1–2 weeks — bring up the full stack, replace vLLM with
  a managed API behind the same interface, observe what breaks and
  what doesn't (the metrics on each stage tell you).
