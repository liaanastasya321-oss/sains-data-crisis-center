import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from PIL import Image # Import Modul Gambar

# 1. SETUP HALAMAN
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 💎 MASTER DESIGN SYSTEM (GLASSMORPHISM)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT (Poppins) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* BACKGROUND GRADASI BERGERAK */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
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
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    section[data-testid="stSidebar"] * { color: #f1f5f9 !important; }
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
        font-size: 3rem; /* Sedikit dikecilkan biar muat logo */
        font-weight: 800;
        color: white;
        text-align: center;
        text-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin-bottom: 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.95);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
        margin-top: 5px;
    }

    /* LOGO IMAGE STYLE (Biar rata tengah) */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stImage"] img {
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3)); /* Bayangan logo */
        transition: transform 0.3s;
    }
    div[data-testid="stImage"] img:hover {
        transform: scale(1.1); /* Efek zoom dikit pas disentuh */
    }

    /* KARTU KACA (GLASS CARD) */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 25px;
        text-align: center;
        transition: transform 0.3s ease;
        margin-bottom: 20px;
        color: white;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .glass-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.35);
        border-color: white;
    }
    .glass-card h1 { font-size: 3rem; margin: 0; }
    .glass-card h3 { color: white; font-weight: 700; margin: 10px 0 5px 0; font-size: 1.2rem;}
    .glass-card p { color: rgba(255,255,255,0.9); font-size: 0.85rem; line-height: 1.4;}

    /* TOMBOL BUTTON */
    .stButton > button {
        background: white;
        color: #e73c7e;
        border-radius: 50px;
        border: none;
        padding: 10px 20px;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: 100%;
        transition: 0.3s;
        margin-top: -10px;
    }
    .stButton > button:hover {
        background: #f8fafc;
        transform: scale(1.05);
        color: #23a6d5;
    }

    /* PENGUMUMAN LIST */
    .announce-item {
        background: rgba(0, 0, 0, 0.4);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #23d5ab;
        color: white;
        backdrop-filter: blur(5px);
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
# Layout: Logo Kiri (1) - Judul Tengah (6) - Logo Kanan (1)
col_logo1, col_text, col_logo2 = st.columns([1.5, 6, 1.5])

with col_logo1:
    # Cek apakah file logo UIN ada
    if os.path.exists("logo_uin.png"):
        st.image("logo_uin.png", width=130) # Sesuaikan width jika terlalu besar
    else:
        st.write("") # Kosong jika file tidak ada

with col_text:
    st.markdown('<div class="hero-title">SAINS DATA <br>CRISIS CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Platform Advokasi & Pelayanan Mahasiswa Terintegrasi</div>', unsafe_allow_html=True)

with col_logo2:
    # Cek apakah file logo Himpunan ada
    if os.path.exists("logo_him.png"):
        st.image("logo_him.png", width=130)
    else:
        st.write("") 

# ==========================================
# 2. MENU NAVIGATION (GLASS CARDS)
# ==========================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="glass-card">
        <h1>📝</h1>
        <h3>Lapor Aja</h3>
        <p>Ada masalah akademik? Lapor di sini, kerahasiaan terjamin.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Buat Laporan", key="btn1"):
        st.switch_page("pages/Lapor_Masalah.py")

with c2:
    st.markdown("""
    <div class="glass-card">
        <h1>🔍</h1>
        <h3>Pantau Status</h3>
        <p>Cek sejauh mana laporanmu diproses oleh tim kami.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cek Progres", key="btn2"):
        st.switch_page("pages/Cek_Status.py")

with c3:
    st.markdown("""
    <div class="glass-card">
        <h1>📊</h1>
        <h3>Transparansi</h3>
        <p>Lihat data statistik keluhan mahasiswa secara real-time.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Lihat Data", key="btn3"):
        st.switch_page("pages/Dashboard_Publik.py")

with c4:
    st.markdown("""
    <div class="glass-card">
        <h1>🤖</h1>
        <h3>Tanya Bot</h3>
        <p>Bingung soal UKT/KRS? Tanya AI kami, aktif 24 jam.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Chat AI", key="btn4"):
        st.switch_page("pages/Sadas_Bot.py")

# ==========================================
# 3. PENGUMUMAN (GLASS LIST)
# ==========================================
st.write("")
st.write("")
st.markdown("<h3 style='color:white; text-align:center; margin-bottom: 20px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>📢 Update Terbaru</h3>", unsafe_allow_html=True)

col_spacer_l, col_news, col_spacer_r = st.columns([1, 6, 1])

with col_news:
    if len(data_pengumuman) > 0:
        for item in reversed(data_pengumuman):
            tipe = item.get('Tipe', 'Info')
            
            # Warna Border Kiri
            if tipe == "Urgent": border = "#ff4757"
            elif tipe == "Penting": border = "#ffa502"
            else: border = "#2ed573"

            # HTML Rapat Kiri
            st.markdown(f"""
<div class="announce-item" style="border-left: 5px solid {border};">
<div style="display:flex; justify-content:space-between; margin-bottom:5px;">
<strong style="text-transform:uppercase; color:#f1f2f6; font-size:0.8rem; background:rgba(255,255,255,0.2); padding:2px 8px; border-radius:4px;">{tipe}</strong>
<small style="color:#dfe4ea;">{item.get('Tanggal','-')}</small>
</div>
<h3 style="margin:5px 0; font-size:1.3rem; color:white; font-weight:700;">{item.get('Judul','-')}</h3>
<p style="margin-top:5px; color:#f1f2f6; line-height:1.5;">{item.get('Isi','-')}</p>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; height:auto; padding:20px;">
            <p>Belum ada pengumuman.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer Spacing
st.write("")
st.write("")
st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.8); font-size:0.8rem; padding-bottom:20px;'>© 2026 Sains Data Crisis Center</div>", unsafe_allow_html=True)
