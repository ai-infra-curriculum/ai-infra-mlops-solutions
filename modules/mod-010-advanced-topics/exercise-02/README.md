# RAG System — Solution

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-010-advanced-topics/exercises/exercise-02-rag-system-implementation.md).

Companion: [engineer-solutions/mod-110 ex-14 (hybrid-retrieval-reranking)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-110-llm-infrastructure/exercise-14-hybrid-retrieval-reranking) for BM25 + dense fusion + cross-encoder reranking.

```bash
pip install chromadb sentence-transformers httpx
python -c "import rag; rag.ingest([{'id':'1','text':'Saturn has 146 moons.'}]); print(rag.answer('How many moons does Saturn have?'))"
```
