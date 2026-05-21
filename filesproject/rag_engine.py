"""
Smart Aid RAG Engine
Sentence Transformers + FAISS — Streamlit Cloud compatible
Gemma 4 is optional (runs on Kaggle GPU only)
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

print("🤖 RAG Engine loading...")
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "smart_aid_combined.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

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

print("📐 Building FAISS index...")
embeddings = retriever_model.encode(texts, convert_to_numpy=True).astype(np.float32)
dimension = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension)
faiss_index.add(embeddings)
print(f"✅ RAG ready! {len(data)} records indexed.")


def rag_search(query: str, top_k: int = 5):
    """Fast semantic search — no LLM needed."""
    q_emb = retriever_model.encode([query], convert_to_numpy=True).astype(np.float32)
    _, I = faiss_index.search(q_emb, top_k)
    return [data[i] for i in I[0] if 0 <= i < len(data)]


def rag_generate(query: str, top_k: int = 5):
    """
    On Streamlit Cloud: returns formatted fallback answer.
    On Kaggle GPU: Gemma 4 generates full answer.
    """
    results = rag_search(query, top_k=top_k)
    if not results:
        return "No resources found for your query.", []

    # Try Gemma 4 (only works on GPU with transformers installed)
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        # If import works, attempt Gemma generation
        answer = _gemma_answer(query, results)
        return answer, results
    except ImportError:
        # Streamlit Cloud — fallback answer
        answer = _fallback_answer(query, results)
        return answer, results


def _fallback_answer(query: str, results: list) -> str:
    """Clean formatted answer without LLM."""
    lines = [f"Here are the top resources matching **'{query}'**:\n"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i}. **{r['name']}** ({r.get('category_label','')})\n"
            f"   📍 {r.get('city','')} — {r.get('address','')}\n"
            f"   📞 {r.get('phone','')}  |  ⏰ {r.get('hours','')}\n"
        )
    return "\n".join(lines)


def _gemma_answer(query: str, results: list) -> str:
    """Gemma 4 generation — only runs on Kaggle GPU."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    HF_TOKEN = os.environ.get("HF_TOKEN", None)
    GEMMA_MODEL_ID = "google/gemma-4-it"

    context = "\n\n".join([
        f"Name: {r['name']}\nCity: {r['city']}\nPhone: {r['phone']}\nHours: {r['hours']}"
        for r in results
    ])

    tokenizer = AutoTokenizer.from_pretrained(GEMMA_MODEL_ID, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        GEMMA_MODEL_ID, token=HF_TOKEN,
        device_map="auto", torch_dtype=torch.float16
    )

    messages = [{"role": "user", "content":
        f"You are Smart Aid AI. Help find resources in Pakistan.\n"
        f"Query: {query}\nResources:\n{context}\n"
        f"Give a warm helpful answer mentioning names and contacts."
    }]

    input_ids = tokenizer.apply_chat_template(
        messages, return_tensors="pt", add_generation_prompt=True
    ).to(model.device)

    with torch.no_grad():
        out = model.generate(input_ids, max_new_tokens=300, temperature=0.7, do_sample=True)

    new_tokens = out[0][input_ids.shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
