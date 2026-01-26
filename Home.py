import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from PIL import Image

# 1. SETUP HALAMAN
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="💻", # Ikon ganti jadi Laptop/Tech
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 💎 MASTER DESIGN SYSTEM (DEEP TECH THEME)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT (Poppins) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* BACKGROUND GRADASI TEKNOLOGI (Dark Blue - Cyan) */
    .stApp {
        /* Gradasi dari Gelap (Navy) ke Terang (Cyan/Teal) */
        background: linear-gradient(-45deg, #020024, #0f172a, #090979, #00d4ff);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* --- SIDEBAR DARK NAVY --- */
    section[data-testid="stSidebar"] {
        background-color: #020617 !important; /* Hampir Hitam (Very Dark Blue) */
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    button[kind="header"] { color: white !important; }

    /* --- HEADER TRANSPARAN --- */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
        backdrop-filter: blur(0px) !important;
    }
    header[data-testid="stHeader"] * { color: white !important; }

    /* Layout Spacing */
    .block-container {
        padding-top: 3rem; 
        padding-bottom: 5rem;
    }
    footer {visibility: hidden;}

    /* JUDUL HERO UTAMA */
    .hero-title {
        font-size: 3rem; 
        font-weight: 800;
        color: white;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.6); /* Efek Neon Glow Biru */
        margin-bottom: 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    /* LOGO IMAGE STYLE */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stImage"] img {
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.2)); /* Glow tipis di logo */
        transition: transform 0.3s;
    }
    div[data-testid="stImage"] img:hover {
        transform: scale(1.1);
    }

    /* KARTU KACA (GLASS CARD - TECH STYLE) */
    .glass-card {
        background: rgba(15, 23, 42, 0.6); /* Lebih gelap biar teks putih jelas */
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        color: white;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        background: rgba(30, 41, 59, 0.8);
        border-color: #00d4ff; /* Border nyala biru pas di hover */
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); /* Glow effect */
    }
    .glass-card h1 { font-size: 3rem; margin: 0; }
    .glass-card h3 { color: white; font-weight: 700; margin: 10px 0 5px 0; font-size: 1.2rem;}
    .glass-card p { color: #cbd5e1; font-size: 0.85rem; line-height: 1.4;}

    /* TOMBOL BUTTON (CYBER STYLE) */
    .stButton > button {
        background: transparent;
        color: white;
        border-radius: 50px;
        border: 2px solid #00d4ff; /* Garis tepi Cyan */
        padding: 10px 20px;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        width: 100%;
        transition: 0.3s;
        margin-top: -10px;
    }
    .stButton > button:hover {
        background: #00d4ff; /* Isi penuh pas hover */
        color: #020024; /* Teks jadi gelap */
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); /* Neon Glow */
    }

    /* PENGUMUMAN LIST */
    .announce-item {
        background: rgba(15, 23, 42, 0.7);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #00d4ff; /* Aksen Cyan */
        color: white;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE
# ==========================================
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    if "google_credentials" in st.secrets:
        creds_dict = json.loads(st.secrets["google_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    elif os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    elif os.path.exists("../credentials.json"):
        creds = Credentials.from_service_account_file("../credentials.json", scopes=scopes)
    else:
        creds = None

    if creds:
        client = gspread.authorize(creds)
        sheet = client.open("Database_Advokasi").worksheet("Pengumuman")
        data_pengumuman = sheet.get_all_records()
    else:
        data_pengumuman = []
except:
    data_pengumuman = []

# ==========================================
# 1. HERO SECTION (DENGAN LOGO) 🏛️
# ==========================================
col_logo1, col_text, col_logo2 = st.columns([1.5, 6, 1.5])

with col_logo1:
    if os.path.exists("logo_uin.png"):
        st.image("logo_uin.png", width=130)
    else:
        st.write("") 

with col_text:
    st.markdown('<div class="hero-title">SAINS DATA <br>CRISIS CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Platform Advokasi & Pelayanan Mahasiswa Terintegrasi</div>', unsafe_allow_html=True)

with col_logo2:
    if os.path.exists("logo_him.png"):
        st.image("logo_him.png", width=130)
    else:
        st.write("") 

# ==========================================
# 2. MENU NAVIGATION (TECH CARDS)
# ==========================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="glass-card">
        <h1>📝</h1>
        <h3>Lapor Aja</h3>
        <p>Ada masalah akademik? Lapor di sini, privasi aman.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Buat Laporan", key="btn1"):
        st.switch_page("pages/Lapor_Masalah.py")

with c2:
    st.markdown("""
    <div class="glass-card">
        <h1>🔍</h1>
        <h3>Pantau Status</h3>
        <p>Lacak sejauh mana laporanmu diproses admin.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cek Progres", key="btn2"):
        st.switch_page("pages/Cek_Status.py")

with c3:
    st.markdown("""
    <div class="glass-card">
        <h1>📊</h1>
        <h3>Data Publik</h3>
        <p>Transparansi data statistik keluhan mahasiswa.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Lihat Dashboard", key="btn3"):
        st.switch_page("pages/Dashboard_Publik.py")

with c4:
    st.markdown("""
    <div class="glass-card">
        <h1>🤖</h1>
        <h3>Tanya Bot</h3>
        <p>Asisten AI untuk tanya jawab seputar akademik.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Chat AI", key="btn4"):
        st.switch_page("pages/Sadas_Bot.py")

# ==========================================
# 3. PENGUMUMAN (DARK MODE)
# ==========================================
st.write("")
st.write("")
st.markdown("<h3 style='color:white; text-align:center; margin-bottom: 20px; letter-spacing:1px;'>📢 INFORMASI TERBARU</h3>", unsafe_allow_html=True)

col_spacer_l, col_news, col_spacer_r = st.columns([1, 6, 1])

with col_news:
    if len(data_pengumuman) > 0:
        for item in reversed(data_pengumuman):
            tipe = item.get('Tipe', 'Info')
            
            # Warna Border Kiri (Neon Style)
            if tipe == "Urgent": border = "#ff0055" # Neon Red
            elif tipe == "Penting": border = "#ffaa00" # Neon Orange
            else: border = "#00d4ff" # Neon Blue

            st.markdown(f"""
<div class="announce-item" style="border-left: 4px solid {border};">
<div style="display:flex; justify-content:space-between; margin-bottom:5px;">
<strong style="text-transform:uppercase; color:#fff; font-size:0.75rem; background:rgba(255,255,255,0.1); padding:3px 10px; border-radius:4px; letter-spacing:1px;">{tipe}</strong>
<small style="color:#94a3b8;">{item.get('Tanggal','-')}</small>
</div>
<h3 style="margin:8px 0; font-size:1.2rem; color:white; font-weight:700;">{item.get('Judul','-')}</h3>
<p style="margin-top:5px; color:#cbd5e1; line-height:1.6;">{item.get('Isi','-')}</p>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; height:auto; padding:20px;">
            <p>Belum ada pengumuman.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.write("")
st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.5); font-size:0.8rem; padding-bottom:20px;'>© 2026 Sains Data Crisis Center UIN RIL</div>", unsafe_allow_html=True)
