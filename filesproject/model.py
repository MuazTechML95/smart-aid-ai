"""
Smart Aid AI – Streamlit App
Gemma 4 Edition: RAG retrieval + LLM answer generation
"""

import streamlit as st
from smart_aid_handler import search, generate

# ── Page config ──────────────────────────────────────
st.set_page_config(
    page_title="Smart Aid AI",
    layout="wide",
    page_icon="🤖"
)

# ── Custom CSS ───────────────────────────────────────
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #2E86C1;
    margin-bottom: 4px;
}
.sub-title {
    text-align: center;
    color: gray;
    font-size: 18px;
    margin-bottom: 24px;
}
.card {
    background-color: #f9f9f9;
    padding: 16px 20px;
    border-radius: 14px;
    margin-bottom: 16px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
    border-left: 4px solid #2E86C1;
}
.highlight { color: #2E86C1; font-weight: bold; }
.gemma-box {
    background: linear-gradient(135deg, #e8f4fd, #f0fff4);
    border: 1px solid #2E86C1;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 24px;
}
.gemma-label {
    font-size: 13px;
    color: #888;
    margin-bottom: 6px;
}
.model-badge {
    display: inline-block;
    background: #2E86C1;
    color: white;
    font-size: 12px;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────
st.markdown("<div class='main-title'>🤖 Smart Aid AI</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Find Food Banks, Free Clinics & NGOs near you "
    "— powered by <b>Gemma 4</b> + Semantic Search</div>",
    unsafe_allow_html=True
)

# ── Sidebar ──────────────────────────────────────────
st.sidebar.header("⚙️ Settings")

use_gemma = st.sidebar.toggle(
    "🤖 Gemma 4 AI Answer",
    value=True,
    help="Uses Gemma 4 to generate a natural-language answer on top of search results."
)

category_filter = st.sidebar.selectbox(
    "📂 Category Filter",
    ["All", "Food Bank", "Clinic", "NGO"]
)

city_filter = st.sidebar.text_input("🏙️ Filter by City (optional)")

top_k = st.sidebar.slider("🔢 Max Results", 3, 10, 5)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Model:** `google/gemma-4-it`\n\n"
    "**Retrieval:** FAISS + SentenceTransformers\n\n"
    "**Data:** Food Banks, Clinics, NGOs across Pakistan"
)

# ── Search Box ───────────────────────────────────────
query = st.text_input(
    "💬 Describe your need",
    placeholder="e.g. free food in Lahore, eye hospital Karachi, mental health support..."
)

# ── Search Logic ─────────────────────────────────────
if query:
    with st.spinner("🔍 Searching resources..."):
        if use_gemma:
            ai_answer, results = generate(query, top_k=top_k)
        else:
            results = search(query, top_k=top_k)
            ai_answer = None

    # Apply filters
    if category_filter != "All":
        results = [
            r for r in results
            if category_filter.lower() in r.get("category_label", "").lower()
        ]
    if city_filter:
        results = [
            r for r in results
            if city_filter.lower() in r.get("city", "").lower()
        ]

    # ── Gemma AI Answer Box ──────────────────────────
    if use_gemma and ai_answer:
        st.markdown("<div class='gemma-box'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='model-badge'>✨ Gemma 4 AI Answer</div>",
            unsafe_allow_html=True
        )
        st.markdown(ai_answer)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Result Count ─────────────────────────────────
    st.success(f"🎯 Found **{len(results)}** matching resources")

    if not results:
        st.info("Try a different query or remove filters.")

    # ── Result Cards ─────────────────────────────────
    for r in results:
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>🏢 {r['name']}</h3>
                <p>📍 <span class='highlight'>City:</span> {r['city']}</p>
                <p>🗺️ <b>Address:</b> {r['address']}</p>
                <p>📞 <b>Contact:</b> {r['phone']}</p>
                <p>⏰ <b>Hours:</b> {r['hours']}</p>
                <p>🏷️ <b>Category:</b> {r.get('category_label', '')}</p>
            """, unsafe_allow_html=True)

            if r.get("services"):
                st.markdown(f"<p>🍽️ <b>Services:</b> {r['services']}</p>", unsafe_allow_html=True)
            if r.get("specialties"):
                st.markdown(f"<p>🏥 <b>Specialties:</b> {r['specialties']}</p>", unsafe_allow_html=True)
            if r.get("focus_areas"):
                st.markdown(f"<p>🤝 <b>Focus:</b> {r['focus_areas']}</p>", unsafe_allow_html=True)
            if r.get("website") and r["website"] not in ("Not Available", ""):
                st.markdown(f"<p>🌐 <b>Website:</b> <a href='{r['website']}' target='_blank'>{r['website']}</a></p>", unsafe_allow_html=True)

            if r.get("coordinates_available"):
                map_url = f"https://www.google.com/maps?q={r['latitude']},{r['longitude']}"
                st.markdown(
                    f"<p>📍 <a href='{map_url}' target='_blank'>Open in Google Maps</a></p>",
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.write("")
            st.write("")
            if r.get("verified"):
                st.success("Verified ✅")
            else:
                st.warning("Unverified ⚠️")

            if r.get("free_services"):
                st.info("Free 🆓")

        st.write("---")

# ── Empty state ──────────────────────────────────────
else:
    st.info("👆 Enter your need above to find resources near you.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🍽️ Food Banks\nFree meals, ration packages, langar")
    with col2:
        st.markdown("### 🏥 Free Clinics\nOPD, specialists, mental health")
    with col3:
        st.markdown("### 🤝 NGOs\nEmergency relief, education, microfinance")
