"""
Smart Aid Handler - Gemma 4 RAG version
Supports two modes:
  - search(query)    → fast FAISS retrieval only
  - generate(query)  → FAISS retrieval + Gemma 4 answer
"""

from rag_engine import rag_search, rag_generate


def search(query: str, top_k: int = 5) -> list[dict]:
    """Fast semantic search — no LLM, just vector similarity."""
    return rag_search(query, top_k=top_k)


def generate(query: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    Full RAG pipeline: retrieve + Gemma 4 generates a helpful answer.
    Returns (answer_text, source_records)
    """
    return rag_generate(query, top_k=top_k)
