"""
Smart Aid Handler - RAG version
Ab simple keyword search nahi, semantic search hoga!
"""

import os
from rag_engine import rag_search

def search(query):
    results = rag_search(query, top_k=5)
    return results