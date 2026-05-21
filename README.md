# 🤖 Smart Aid AI
> AI-powered web app to find free Food Banks, Clinics, and NGOs in Pakistan — powered by **Gemma 4**

---

## 📌 What is Smart Aid AI?

Smart Aid AI helps people in need find:

- 🍽️ **Food Banks** — Free meals, langar, ration packages
- 🏥 **Clinics** — Free or low-cost medical care
- 🤝 **NGOs** — Welfare organizations across Pakistan

Just type what you need in simple English or Urdu — the AI finds the best match!

---

## 🧠 How it Works (RAG + Gemma 4)

```
User Query → Sentence Transformers → FAISS Search → Gemma 4 → AI Answer
```

- Uses **RAG (Retrieval Augmented Generation)**
- **Semantic search** — understands meaning, not just keywords
- **Gemma 4** (`google/gemma-4-it`) generates natural language answers
- Works with Urdu-style English too (e.g. "mujhe khana chahiye")

---

## 🗂️ Project Files

| File | Description |
|------|-------------|
| `model.py` | Streamlit UI — main app |
| `rag_engine.py` | RAG engine — FAISS + Sentence Transformers + Gemma 4 |
| `smart_aid_handler.py` | Search & generate handler |
| `smart_aid_combined.json` | Dataset — Food Banks, Clinics, NGOs |
| `smart_aid_data_handler.py` | Data cleaning & processing pipeline |
| `kaggle_setup.py` | Kaggle notebook setup for Gemma 4 GPU |

---

## 🚀 How to Run

**1. Install requirements:**
```bash
pip install streamlit sentence-transformers faiss-cpu transformers accelerate
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

## ⚡ Tech Stack

| Technology | Purpose |
|------------|---------|
| `google/gemma-4-it` | AI answer generation (LLM) |
| `sentence-transformers` | Semantic embeddings |
| `FAISS` | Vector similarity search |
| `Streamlit` | Web UI |
| `Python` | Backend |

---

## 📊 Dataset

| Category | Records |
|----------|---------|
| 🍽️ Food Banks | 6 |
| 🏥 Clinics | 7 |
| 🤝 NGOs | 5 |
| **Total** | **18** |

**Cities covered:** Karachi, Lahore, Islamabad, Multan, Peshawar

---

## 👨‍💻 Built By

**Muhammad Muaz** — Solo Developer

- 🧠 AI & RAG Pipeline (Gemma 4 + FAISS)
- 💾 Data Collection & Cleaning
- 🎨 UI Design (Streamlit)
- 🚀 Deployment & GitHub

---

## 🏫 Submission

**GIAIC — Governor Initiative for AI & Computing**  
Smart Aid AI — Helping people find aid through Artificial Intelligence 🇵🇰
