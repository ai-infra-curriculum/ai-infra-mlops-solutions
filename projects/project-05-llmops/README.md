# Project 5 Solution — LLMOps Production System

Reference for [learning project 5](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/tree/main/projects/project-05-llmops).

Also just built out to full implementation (this session):
- `src/api/app.py` — gateway composing: rate-limit → input-guard → semantic-cache → RAG → vLLM upstream → output-guard → cost meter, with full Prometheus instrumentation
- `src/config.py` — pydantic-settings env-driven config
- `src/guardrails.py` — injection + PII regex + size cap (in + out)
- `src/cache.py` — Redis-backed exact cache (with TTL); seam for semantic upgrade
- `src/cost.py` — tiktoken-based token counts + per-call USD estimation
- `src/rag/store.py` — Chroma-backed doc store with sentence-transformers embeddings
- `src/metrics.py` — TTFT + tokens-by-direction + cost USD + cache hit/miss + guard blocks
- `tests/` — guard (injection/PII/oversize/clean) + cost + API smoke
- Dockerfile + docker-compose (chroma + redis + api + prometheus) + Makefile with `make vllm` GPU target

## Cross-references

- [engineer-solutions/mod-110 LLM infrastructure (all 14 exercises)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-110-llm-infrastructure) — every component from vLLM tuning to multi-tenant gateway, in deeper detail
- [mlops-solutions modules/mod-010-advanced-topics/exercise-01](../../modules/mod-010-advanced-topics/exercise-01/) — minimal vLLM launcher
- [mlops-solutions modules/mod-010-advanced-topics/exercise-02](../../modules/mod-010-advanced-topics/exercise-02/) — minimal RAG

## How to study

1. Read the learning project README.
2. Bring up the stack: `make up` (note: needs vLLM on host; `make vllm` to start one).
3. Read the gateway code top-down to see how the pipeline composes.
4. Run `make test`.
5. Try adding a layer (semantic cache instead of exact; new guard rule).
