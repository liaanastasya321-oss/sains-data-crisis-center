import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os
import requests
import datetime
import google.generativeai as genai 

# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. MODERN CSS CUSTOMIZATION
# =========================================================
st.markdown("""
<style>
    /* Import Font Modern */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background Base */
    .stApp {
        background: #fdfdfd;
        color: #1e293b;
    }

    /* HIDE DEFAULT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    /* --- SOLUSI MENU TERPOTONG --- */
    /* Kita gunakan sticky container di dalam Streamlit */
    .nav-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #e2e8f0;
        padding: 5px 2%;
    }

    /* Berikan padding pada body agar tidak tertutup menu */
    .main .block-container {
        padding-top: 5rem !important;
        max-width: 1200px;
    }

    /* CARD STYLE PROFESSIONAL */
    .glass-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(37, 99, 235, 0.08);
        border-color: #3b82f6;
    }

    /* HERO TEXT */
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    /* INPUT STYLING */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* CHAT BUBBLES */
    .chat-bubble {
        padding: 15px 20px;
        border-radius: 18px;
        margin-bottom: 15px;
        line-height: 1.5;
        font-size: 14px;
    }
    .user-bubble { background-color: #3b82f6; color: white; margin-left: 20%; border-bottom-right-radius: 2px; }
    .bot-bubble { background-color: #f1f5f9; color: #1e293b; margin-right: 20%; border-bottom-left-radius: 2px; border: 1px solid #e2e8f0; }

    /* METRICS */
    .metric-box { text-align: center; padding: 10px; }
    .metric-val { font-size: 32px; font-weight: 800; color: #2563eb; }
    .metric-lab { font-size: 14px; color: #64748b; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. LOGIC & DATA (API/GSheets)
# =========================================================
# (Bagian ini tetap sama dengan logika koneksi Anda)
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b" 
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_spreadsheet():
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else: return None
        client = gspread.authorize(creds)
        return client.open_by_key(ID_SPREADSHEET)
    except: return None

sh = get_spreadsheet()
sheet = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# =========================================================
# 4. NAVBAR (STICKY FIX)
# =========================================================
# Container pembungkus menu agar tidak melayang berantakan
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house-fill", "megaphone-fill", "search-heart", "pie-chart-fill", "robot", "person-badge-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
        "nav-link": {"font-size": "14px", "font-weight": "600", "color": "#64748b", "padding": "10px 15px"},
        "nav-link-selected": {"background-color": "#2563eb", "color": "white", "border-radius": "10px"},
    }
)
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if selected == "Home":
    col_logo1, col_text, col_logo2 = st.columns([1, 4, 1])
    with col_text:
        st.markdown("""<div style="text-align:center; padding: 20px 0;">
            <h1 class="hero-title">Sains Data Crisis Center</h1>
            <p style="color:#64748b; font-size:18px;">Solusi Cepat, Transparan, dan Modern untuk Mahasiswa</p>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3>🚀 Respon Cepat</h3><p>Laporan diproses dalam waktu kurang dari 24 jam oleh tim admin.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3>🛡️ Privasi Aman</h3><p>Data pelapor dienkripsi dan hanya digunakan untuk keperluan resolusi masalah.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3>🤖 Sadas AI</h3><p>Gunakan chatbot cerdas kami untuk bantuan informasi akademik instan.</p></div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📰 Pengumuman Terbaru")
    # Logika pengumuman Anda tetap di sini...
    if sheet_pengumuman:
        try:
            data_info = sheet_pengumuman.get_all_records()
            if data_info:
                for item in reversed(data_info[-3:]): # Ambil 3 terbaru
                    st.markdown(f"""<div class="glass-card" style="padding:15px; border-left: 4px solid #3b82f6;">
                        <small style="color:#94a3b8;">{item.get('Tanggal', '-')}</small>
                        <h4 style="margin:5px 0;">{item.get('Judul', '-')}</h4>
                        <p style="font-size:14px; margin:0;">{item.get('Isi', '-')}</p>
                    </div>""", unsafe_allow_html=True)
        except: st.error("Gagal memuat pengumuman.")

# =========================================================
# 6. HALAMAN: LAPOR MASALAH (PRO LOOK)
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<div style='max-width: 800px; margin: auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Buat Laporan Baru</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("form_lapor", clear_on_submit=True):
            nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama sesuai SIAKAD")
            c1, c2 = st.columns(2)
            npm = c1.text_input("NPM", placeholder="Contoh: 21170...")
            prodi = c2.selectbox("Program Studi", ["Sains Data", "Informatika", "Lainnya"])
            
            kat = st.selectbox("Kategori", ["Akademik", "Fasilitas", "Organisasi", "Lainnya"])
            msg = st.text_area("Detail Masalah", placeholder="Ceritakan kronologi secara singkat dan jelas...")
            file = st.file_uploader("Lampiran Bukti (Opsional)", type=['jpg','png','pdf'])
            
            btn = st.form_submit_button("Kirim Laporan Sekarang")
            if btn:
                # Logika submit Anda...
                st.success("Laporan berhasil dikirim!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7. HALAMAN: SADAS BOT (MODERN CHAT)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Virtual Assistant</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Messages
    for msg in st.session_state.messages:
        role_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        st.markdown(f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Tanyakan sesuatu tentang akademik..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Logika AI Anda...
        response = "Halo! Saya adalah Sadas Bot. Ada yang bisa saya bantu?" # Contoh statis
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# =========================================================
# SECTIONS LAINNYA (CEK STATUS, DASHBOARD, ADMIN)
# =========================================================
# Gunakan pola .glass-card yang sama agar desain konsisten.
