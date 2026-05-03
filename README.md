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
