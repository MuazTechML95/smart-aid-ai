import streamlit as st
from smart_aid_handler import search

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Aid AI",
    layout="wide",
    page_icon="🤖"
)

# ---------------- CUSTOM CSS (Website Look) ----------------
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #2E86C1;
    }

    .sub-title {
        text-align: center;
        color: gray;
        font-size: 18px;
        margin-bottom: 20px;
    }

    .card {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }

    .highlight {
        color: #2E86C1;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='main-title'>🤖 Smart Aid AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Find Food, Clinics & NGOs near you</div>", unsafe_allow_html=True)

# ---------------- SIDEBAR FILTER ----------------
st.sidebar.header("🔎 Filters")

category_filter = st.sidebar.selectbox(
    "Choose Category",
    ["All", "Food Bank", "Clinic", "NGO"]
)

city_filter = st.sidebar.text_input("Enter City (optional)")

# ---------------- SEARCH BOX ----------------
query = st.text_input("💬 Enter your need (e.g. free food, clinic, NGO help)")

# ---------------- SEARCH LOGIC ----------------
if query:
    results = search(query)

    # Filters apply
    if category_filter != "All":
        results = [r for r in results if category_filter.lower() in r.get("category_label","").lower()]

    if city_filter:
        results = [r for r in results if city_filter.lower() in r.get("city","").lower()]

    st.success(f"🎯 Found {len(results)} results")

    # ---------------- RESULTS ----------------
    for r in results:

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>🏢 {r['name']}</h3>
                <p>📍 <span class='highlight'>City:</span> {r['city']}</p>
                <p>📌 Address: {r['address']}</p>
                <p>📞 Contact: {r['phone']}</p>
                <p>⏰ Hours: {r['hours']}</p>
            """, unsafe_allow_html=True)

            if "services" in r:
                st.markdown(f"<p>🍽 Services: {r['services']}</p>", unsafe_allow_html=True)

            if "specialties" in r:
                st.markdown(f"<p>🏥 Specialties: {r['specialties']}</p>", unsafe_allow_html=True)

            if "focus_areas" in r:
                st.markdown(f"<p>🤝 Focus: {r['focus_areas']}</p>", unsafe_allow_html=True)

            if r.get("coordinates_available"):
                map_url = f"https://www.google.com/maps?q={r['latitude']},{r['longitude']}"
                st.markdown(f"📍 [Open in Google Maps]({map_url})")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.write("")
            st.write("")
            st.info("Verified ✅" if r.get("verified") else "Not Verified ⚠️")

        st.write("---")