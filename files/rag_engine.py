"""
Smart Aid RAG Engine
Sentence Transformers + FAISS based semantic search
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

# ── Model load ──
print("🤖 RAG Engine loading...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# ── Data load ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "smart_aid_combined.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ── Har record ka text banao (embedding ke liye) ──
def record_to_text(r):
    parts = [
        r.get("name", ""),
        r.get("city", ""),
        r.get("category_label", ""),
        r.get("services", ""),
        r.get("specialties", ""),
        r.get("focus_areas", ""),
        r.get("address", ""),
    ]
    return " ".join([p for p in parts if p])

texts = [record_to_text(r) for r in data]

# ── Embeddings banao ──
print("📐 Embeddings ban rahi hain...")
embeddings = model.encode(texts, convert_to_numpy=True)
embeddings = np.array(embeddings).astype(np.float32)

# ── FAISS index banao ──
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
print(f"✅ RAG ready! {len(data)} records indexed.")

# ── Search function ──
def rag_search(query, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    query_embedding = np.array(query_embedding).astype(np.float32)
    D, I = index.search(query_embedding, top_k)
    results = []
    for i in I[0]:
        if 0 <= i < len(data):
            results.append(data[i])
    return results