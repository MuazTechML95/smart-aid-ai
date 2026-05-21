"""
Smart Aid RAG Engine - Gemma 4 Edition
Sentence Transformers + FAISS for retrieval
Gemma 4 (gemma-4-it) for natural language answer generation

Kaggle Setup:
  1. Go to Kaggle > Settings > Secrets
  2. Add secret: HF_TOKEN = your_huggingface_token
  3. Accept Google's Gemma license on HuggingFace first:
     https://huggingface.co/google/gemma-4-it
"""

import json
import numpy as np
import os
import torch
from sentence_transformers import SentenceTransformer
import faiss

# ── HuggingFace token (from Kaggle Secrets or env) ──
HF_TOKEN = os.environ.get("HF_TOKEN", None)  # Set in Kaggle Secrets

# ── Gemma model name ──
GEMMA_MODEL_ID = "google/gemma-4-it"  # 4B instruction-tuned

# ─────────────────────────────────────────────────────
# 1. RETRIEVAL ENGINE (SentenceTransformers + FAISS)
# ─────────────────────────────────────────────────────
print("📐 Loading retrieval model (SentenceTransformers)...")
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "smart_aid_combined.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


def record_to_text(r):
    """Convert a record dict to a flat text string for embedding."""
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


def record_to_context(r):
    """Format a record as readable context for Gemma."""
    lines = [
        f"Name: {r.get('name', 'N/A')}",
        f"Category: {r.get('category_label', 'N/A')}",
        f"City: {r.get('city', 'N/A')}",
        f"Address: {r.get('address', 'N/A')}",
        f"Phone: {r.get('phone', 'N/A')}",
        f"Hours: {r.get('hours', 'N/A')}",
    ]
    if r.get("services"):
        lines.append(f"Services: {r['services']}")
    if r.get("specialties"):
        lines.append(f"Specialties: {r['specialties']}")
    if r.get("focus_areas"):
        lines.append(f"Focus Areas: {r['focus_areas']}")
    if r.get("website") and r["website"] not in ("Not Available", ""):
        lines.append(f"Website: {r['website']}")
    lines.append(f"Verified: {'Yes ✅' if r.get('verified') else 'No ⚠️'}")
    return "\n".join(lines)


texts = [record_to_text(r) for r in data]

print("📐 Building FAISS index...")
embeddings = retriever_model.encode(texts, convert_to_numpy=True).astype(np.float32)
dimension = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension)
faiss_index.add(embeddings)
print(f"✅ FAISS ready! {len(data)} records indexed.")

# ─────────────────────────────────────────────────────
# 2. GEMMA 4 GENERATOR
# ─────────────────────────────────────────────────────
gemma_model = None
gemma_tokenizer = None


def load_gemma():
    """Lazy-load Gemma 4 on first use (saves RAM if only retrieval is needed)."""
    global gemma_model, gemma_tokenizer

    if gemma_model is not None:
        return  # Already loaded

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM

        print(f"🤖 Loading Gemma 4 ({GEMMA_MODEL_ID})... This may take a minute.")

        gemma_tokenizer = AutoTokenizer.from_pretrained(
            GEMMA_MODEL_ID,
            token=HF_TOKEN,
        )

        # Load in 4-bit quantization for Kaggle T4 GPU (15GB VRAM)
        load_kwargs = {
            "token": HF_TOKEN,
            "device_map": "auto",
        }

        if torch.cuda.is_available():
            try:
                from transformers import BitsAndBytesConfig
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )
                load_kwargs["quantization_config"] = bnb_config
                print("  ⚡ Using 4-bit quantization (Kaggle GPU mode)")
            except ImportError:
                load_kwargs["torch_dtype"] = torch.float16
                print("  ⚡ Using float16 (bitsandbytes not available)")
        else:
            load_kwargs["torch_dtype"] = torch.float32
            print("  💻 Running on CPU (slow but works)")

        gemma_model = AutoModelForCausalLM.from_pretrained(
            GEMMA_MODEL_ID,
            **load_kwargs,
        )
        gemma_model.eval()
        print("✅ Gemma 4 loaded!")

    except Exception as e:
        print(f"⚠️ Gemma 4 load failed: {e}")
        print("   Falling back to retrieval-only mode.")
        gemma_model = None
        gemma_tokenizer = None


# ─────────────────────────────────────────────────────
# 3. CORE SEARCH FUNCTIONS
# ─────────────────────────────────────────────────────

def rag_search(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search — returns top_k matching records."""
    q_emb = retriever_model.encode([query], convert_to_numpy=True).astype(np.float32)
    _, I = faiss_index.search(q_emb, top_k)
    return [data[i] for i in I[0] if 0 <= i < len(data)]


def rag_generate(query: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    Full RAG: retrieve relevant records, then ask Gemma 4 to
    generate a helpful natural-language answer.

    Returns:
        (answer_text, retrieved_records)
    """
    # Step 1: Retrieve
    results = rag_search(query, top_k=top_k)

    if not results:
        return "No relevant resources found for your query.", []

    # Step 2: Build context
    context_blocks = []
    for i, r in enumerate(results, 1):
        context_blocks.append(f"[Resource {i}]\n{record_to_context(r)}")
    context_str = "\n\n".join(context_blocks)

    # Step 3: Build Gemma prompt (instruction-tuned chat format)
    system_prompt = (
        "You are Smart Aid AI, a helpful assistant that connects people in Pakistan "
        "with food banks, free clinics, and NGOs. "
        "Using only the resources listed below, give a clear, warm, and helpful answer. "
        "Mention specific names, contact numbers, and hours. "
        "If coordinates are available, mention that Google Maps directions are available. "
        "Answer in the same language the user asked (Urdu or English)."
    )

    user_message = (
        f"User query: {query}\n\n"
        f"Available resources:\n{context_str}\n\n"
        "Please recommend the most relevant resources and explain how they can help."
    )

    # Gemma-4 chat template
    messages = [
        {"role": "user", "content": f"{system_prompt}\n\n{user_message}"}
    ]

    # Step 4: Load Gemma if not yet loaded
    load_gemma()

    if gemma_model is None or gemma_tokenizer is None:
        # Fallback: return a simple formatted answer without LLM
        fallback = _simple_fallback_answer(query, results)
        return fallback, results

    # Step 5: Tokenize + generate
    try:
        input_ids = gemma_tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True,
        )

        device = next(gemma_model.parameters()).device
        input_ids = input_ids.to(device)

        with torch.no_grad():
            output_ids = gemma_model.generate(
                input_ids,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=gemma_tokenizer.eos_token_id,
            )

        # Decode only newly generated tokens
        new_tokens = output_ids[0][input_ids.shape[1]:]
        answer = gemma_tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return answer, results

    except Exception as e:
        print(f"⚠️ Gemma generation error: {e}")
        fallback = _simple_fallback_answer(query, results)
        return fallback, results


def _simple_fallback_answer(query: str, results: list[dict]) -> str:
    """Rule-based fallback when Gemma is unavailable."""
    lines = [f"Here are the top resources matching '{query}':\n"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i}. **{r['name']}** ({r['category_label']})\n"
            f"   📍 {r['city']} — {r['address']}\n"
            f"   📞 {r['phone']}  |  ⏰ {r['hours']}\n"
        )
    return "\n".join(lines)
