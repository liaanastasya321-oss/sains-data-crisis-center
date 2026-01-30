import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os, json, time
from streamlit_option_menu import option_menu

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Sains Data Crisis Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# SESSION STATE (KUNCI ANTI LOOP)
# ======================================================
if "app_loaded" not in st.session_state:
    st.session_state.app_loaded = False

# ======================================================
# LOADER / TIRAI (DIKONTROL PYTHON, BUKAN JS)
# ======================================================
if not st.session_state.app_loaded:
    st.markdown("""
    <style>
    #curtain {
        position: fixed;
        inset: 0;
        background: #020617;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeOut 1s ease forwards;
        animation-delay: 1.1s;
    }

    .spinner {
        width: 70px;
        height: 70px;
        border: 6px solid #1e293b;
        border-top: 6px solid #06b6d4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        100% { transform: rotate(360deg); }
    }

    @keyframes fadeOut {
        to {
            opacity: 0;
            visibility: hidden;
        }
    }
    </style>

    <div id="curtain">
        <div class="spinner"></div>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(1.3)          # ⏳ waktu animasi
    st.session_state.app_loaded = True
    st.rerun()

# ======================================================
# GLOBAL CSS (SETELAH TIRAI)
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #020617;
    color: #e5e7eb;
}

#MainMenu, footer, header {visibility: hidden;}
[data-testid="stSidebar"] {display:none;}

.glass {
    background: rgba(15,23,42,.65);
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 26px;
    border: 1px solid rgba(59,130,246,.25);
    box-shadow: 0 0 30px rgba(6,182,212,.15);
    transition: .3s;
}
.glass:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 40px rgba(6,182,212,.4);
}

.hero {
    padding: 90px 60px;
    text-align: center;
}
.hero h1 {
    font-size: 56px;
    font-weight: 800;
    background: linear-gradient(90deg,#3b82f6,#06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: #94a3b8;
    font-size: 20px;
    margin-top: 12px;
}

/* BUTTON */
.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(135deg,#3b82f6,#06b6d4);
    padding: 14px;
    color: white;
    font-weight: 600;
    transition: .3s;
}
.stButton > button:hover {
    transform: scale(1.06);
    box-shadow: 0 0 25px rgba(6,182,212,.7);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATABASE (TETAP AMAN)
# ======================================================
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    if "google_credentials" in st.secrets:
        creds = Credentials.from_service_account_info(
            json.loads(st.secrets["google_credentials"]),
            scopes=scopes
        )
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)

    sheet = gspread.authorize(creds)\
        .open("Database_Advokasi")\
        .worksheet("Pengumuman")

    pengumuman = sheet.get_all_records()
except:
    pengumuman = []

# ======================================================
# NAVIGATION (SaaS STYLE)
# ======================================================
selected = option_menu(
    None,
    ["Home", "Lapor", "Status", "Dashboard", "Admin"],
    icons=["house", "exclamation-circle", "search", "bar-chart", "lock"],
    orientation="horizontal",
    styles={
        "container": {"background": "rgba(2,6,23,.7)"},
        "nav-link": {"color": "#94a3b8", "font-size": "15px"},
        "nav-link-selected": {"color": "#06b6d4", "font-weight": "600"}
    }
)

# ======================================================
# HOME PAGE
# ======================================================
if selected == "Home":
    st.markdown("""
    <div class="hero">
        <h1>Sains Data Crisis Center</h1>
        <p>Platform Advokasi & Krisis Data Berbasis Teknologi</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    menu = [
        ("📝", "Lapor Masalah", "pages/Lapor_Masalah.py"),
        ("🔍", "Cek Status", "pages/Cek_Status.py"),
        ("📊", "Dashboard Publik", "pages/Dashboard_Publik.py"),
        ("🤖", "SADAS Bot", "pages/Sadas_Bot.py"),
    ]

    for col, (ico, title, page) in zip([c1, c2, c3, c4], menu):
        with col:
            st.markdown(
                f"<div class='glass'><h2>{ico}</h2><h4>{title}</h4></div>",
                unsafe_allow_html=True
            )
            if st.button("Buka"):
                st.switch_page(page)
