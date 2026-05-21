<<<<<<< HEAD
# Smart Aid AI — Gemma 4 Edition 🤖

A RAG (Retrieval-Augmented Generation) system that helps people in Pakistan
find food banks, free clinics, and NGOs — now powered by **Google Gemma 4**.

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│  SentenceTransformers Retrieval │  ← all-MiniLM-L6-v2 + FAISS
│  Finds top-K relevant records   │
└────────────┬────────────────────┘
             │ top-K records as context
             ▼
┌─────────────────────────────────┐
│       Gemma 4 Generator         │  ← google/gemma-4-it (4B params)
│  Generates a helpful answer     │  ← 4-bit quantized for Kaggle GPU
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│      Streamlit Frontend         │
│  Shows AI answer + result cards │
└─────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `rag_engine.py` | FAISS retrieval + Gemma 4 generation |
| `smart_aid_handler.py` | Clean API: `search()` and `generate()` |
| `model.py` | Streamlit UI with Gemma AI answer toggle |
| `smart_aid_combined.json` | Dataset: food banks, clinics, NGOs |
| `kaggle_setup.py` | Kaggle notebook cells to run everything |
| `requirements.txt` | Python dependencies |

## Kaggle Setup (Step by Step)

### 1. Accept Gemma License
Go to: https://huggingface.co/google/gemma-4-it  
Click **"Agree and access repository"** (free, just needs a HuggingFace account)

### 2. Get your HuggingFace Token
Go to: https://huggingface.co/settings/tokens  
Create a **Read** token.

### 3. Add Kaggle Secrets
In your Kaggle notebook → **Add-ons → Secrets**:
- `HF_TOKEN` = your HuggingFace token
- `NGROK_TOKEN` = your ngrok token (from https://dashboard.ngrok.com)

### 4. Upload Project Files
Create a Kaggle Dataset with these files:
- `rag_engine.py`
- `smart_aid_handler.py`  
- `model.py`
- `smart_aid_combined.json`

### 5. Run kaggle_setup.py cells in order
Copy each cell from `kaggle_setup.py` into your Kaggle notebook and run.

### 6. GPU Settings
- Accelerator: **GPU T4 x2** (recommended) or GPU T4 x1
- Internet: **On** (needed to download Gemma from HuggingFace)

## Memory Requirements

| Mode | RAM | VRAM |
|------|-----|------|
| Retrieval only (no Gemma) | ~1 GB | 0 |
| Gemma 4 (4-bit, T4 GPU) | ~4 GB | ~6 GB |
| Gemma 4 (float16, T4 GPU) | ~4 GB | ~10 GB |

Kaggle T4 has 15 GB VRAM — 4-bit quantization is recommended.

## Usage in Code

```python
from smart_aid_handler import search, generate

# Fast retrieval only (no Gemma)
results = search("free food Lahore", top_k=5)

# Full RAG: retrieval + Gemma 4 answer
answer, results = generate("mujhe khana chahiye Karachi mein")
print(answer)
```

## Kaggle Competition Tips

- The toggle in the sidebar lets judges switch between retrieval-only
  and Gemma-4-powered answers — great for demonstrating both modes.
- The Gemma answer supports Urdu queries automatically.
- FAISS retrieval works offline; Gemma generation needs the model downloaded once.
=======
# 🤖 Smart Aid AI

> AI-powered web app to find free Food Banks, Clinics, and NGOs in Pakistan

---

## 📌 What is Smart Aid AI?

Smart Aid AI helps people in need find:
- 🍽️ **Food Banks** — Free meals, langar, ration packages
- 🏥 **Clinics** — Free or low-cost medical care
- 🤝 **NGOs** — Welfare organizations across Pakistan

Just type what you need in simple English — the AI finds the best match!

---

## 🧠 How it Works (RAG)

```
User Query → Sentence Transformers → FAISS Search → Best Results
```

- Uses **RAG (Retrieval Augmented Generation)**
- **Semantic search** — understands meaning, not just keywords
- Works with Urdu-style English too (e.g. "mujhe khana chahiye")

---

## 🗂️ Project Files

| File | Description |
|------|-------------|
| `model.py` | Streamlit UI — main app |
| `rag_engine.py` | RAG engine — FAISS + Sentence Transformers |
| `smart_aid_handler.py` | Search handler |
| `smart_aid_combined.json` | Dataset — Food Banks, Clinics, NGOs |

---

## 🚀 How to Run

**1. Install requirements:**
```bash
pip install streamlit sentence-transformers faiss-cpu
```

**2. Run the app:**
```bash
streamlit run model.py
```

**3. Open browser:**
```
http://localhost:8501
```

---

## 📊 Dataset

| Category | Records |
|----------|---------|
| 🍽️ Food Banks | 9 |
| 🏥 Clinics | 9 |
| 🤝 NGOs | 7 |
| **Total** | **25** |

**Cities covered:** Karachi, Lahore, Islamabad, Multan, Peshawar, Faisalabad, Rawalpindi

---

## 👩‍💻 Built By

**Smart Aid Project Team**
- 👑 **Lead** — Muaz
- 💾 **Data Collection & RAG** — Muaz and Iqra
- 🧠 **AI & Research** — Aroba
- 🎨 **Design & Content** — Maham

---

## 🏫 Submission

**GIAIC — Governor Initiative for AI & Computing**  
Smart Aid AI — Helping people find aid through Artificial Intelligence 🇵🇰
>>>>>>> 7e637ab09a1f10962e6166d2fd28228bc8c36641
