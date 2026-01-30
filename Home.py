import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os, json
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
# CSS + JS (ANTI BUG, ANTI MUTER)
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
    padding: 28px;
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
    text-align:center;
}
.hero h1 {
    font-size:56px;
    font-weight:800;
    background: linear-gradient(90deg,#3b82f6,#06b6d4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
#typewriter {
    font-size:22px;
    margin-top:14px;
    color:#06b6d4;
}

/* BUTTON */
.stButton > button {
    width:100%;
    border-radius:14px;
    border:none;
    background: linear-gradient(135deg,#3b82f6,#06b6d4);
    padding:14px;
    color:white;
    font-weight:600;
    transition:.3s;
}
.stButton > button:hover {
    transform:scale(1.06);
    box-shadow:0 0 25px rgba(6,182,212,.7);
}

/* LOADER */
#loader {
    position:fixed;
    inset:0;
    background:#020617;
    display:flex;
    align-items:center;
    justify-content:center;
    z-index:9999;
}
.spinner {
    width:70px;height:70px;
    border:6px solid #1e293b;
    border-top:6px solid #06b6d4;
    border-radius:50%;
    animation:spin 1s linear infinite;
}
@keyframes spin {100%{transform:rotate(360deg)}}
</style>

<div id="loader"><div class="spinner"></div></div>

<script>
(function () {
  const removeLoader = () => {
    const loader = document.getElementById("loader");
    if (loader) {
      loader.style.opacity = "0";
      setTimeout(() => loader.remove(), 400);
      sessionStorage.setItem("loaderDone", "1");
    }
  };

  if (sessionStorage.getItem("loaderDone")) {
    removeLoader();
  } else {
    window.onload = () => {
      setTimeout(removeLoader, 900);
    };
  }

  // fallback anti-streamlit-rerun
  setInterval(removeLoader, 2000);

  // TYPEWRITER (AMAN)
  const text = "Platform Advokasi & Krisis Data Berbasis Teknologi";
  let i = 0;
  const target = document.getElementById("typewriter");
  if (target && !target.dataset.done) {
    target.dataset.done = "1";
    const type = () => {
      if (i < text.length) {
        target.innerHTML += text.charAt(i++);
        setTimeout(type, 50);
      }
    };
    setTimeout(type, 300);
  }
})();
</script>
""", unsafe_allow_html=True)

# ======================================================
# DATABASE (AMAN, TIDAK BLOK UI)
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
# NAVIGATION
# ======================================================
selected = option_menu(
    None,
    ["Home", "Lapor", "Status", "Dashboard", "Admin"],
    icons=["house", "exclamation-circle", "search", "bar-chart", "lock"],
    orientation="horizontal",
    styles={
        "container": {"background": "rgba(2,6,23,.6)"},
        "nav-link": {"color": "#94a3b8", "font-size": "15px"},
        "nav-link-selected": {"color": "#06b6d4", "font-weight": "600"}
    }
)

# ======================================================
# HOME
# ======================================================
if selected == "Home":
    st.markdown("""
    <div class="hero">
        <h1>Sains Data Crisis Center</h1>
        <div id="typewriter"></div>
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
