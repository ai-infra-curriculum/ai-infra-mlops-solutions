"""Minimal RAG: Chroma embedding + vLLM completion with citations."""
from __future__ import annotations

import httpx
from sentence_transformers import SentenceTransformer
import chromadb


ENCODER = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
CHROMA = chromadb.Client()
COL = CHROMA.create_collection("docs")


def ingest(docs: list[dict]):
    embeddings = ENCODER.encode([d["text"] for d in docs]).tolist()
    COL.add(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        embeddings=embeddings,
    )


def answer(question: str, k: int = 4) -> dict:
    q_emb = ENCODER.encode(question).tolist()
    r = COL.query(query_embeddings=[q_emb], n_results=k)
    sources = "\n\n".join(f"[{id_}] {text[:300]}"
                           for id_, text in zip(r["ids"][0], r["documents"][0]))
    prompt = (
        "Answer the question using ONLY the provided sources. Cite each fact "
        f"with [source_id].\n\nSources:\n{sources}\n\nQuestion: {question}\n\nAnswer:"
    )
    resp = httpx.post("http://localhost:8000/v1/completions", json={
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "prompt": prompt, "max_tokens": 300, "temperature": 0,
    })
    return {
        "answer": resp.json()["choices"][0]["text"],
        "cited_sources": r["ids"][0],
    }
