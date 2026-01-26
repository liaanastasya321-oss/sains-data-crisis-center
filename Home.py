import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# 1. SETUP HALAMAN
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar sembunyi biar full screen
)

# ==========================================
# 💎 MASTER DESIGN SYSTEM (GLASSMORPHISM)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT (Poppins - Font paling populer untuk UI Modern) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* BACKGROUND GRADASI BERGERAK (ANIMATED GRADIENT) */
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

    /* HILANGKAN ATRIBUT BAWAAN */
    header, footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 5rem;}

    /* JUDUL HERO UTAMA */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-align: center;
        text-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin-bottom: 0;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
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
    }
    
    .glass-card:hover {
        transform: translateY(-10px); /* Efek melayang saat disentuh */
        background: rgba(255, 255, 255, 0.35);
    }

    .glass-card h3 { color: white; font-weight: 700; margin-bottom: 5px;}
    .glass-card p { color: rgba(255,255,255,0.8); font-size: 0.9rem;}

    /* TOMBOL BUTTON (MODERN PILL SHAPE) */
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
    }
    .stButton > button:hover {
        background: #f8fafc;
        transform: scale(1.05);
        color: #23a6d5;
    }

    /* PENGUMUMAN LIST */
    .announce-item {
        background: rgba(0, 0, 0, 0.3); /* Hitam transparan */
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #23d5ab;
        color: white;
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
# 1. HERO SECTION
# ==========================================
st.markdown('<div class="hero-title">SAINS DATA <br>CRISIS CENTER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Platform Advokasi & Pelayanan Mahasiswa Terintegrasi</div>', unsafe_allow_html=True)

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
st.markdown("<h3 style='color:white; text-align:center; margin-bottom: 20px;'>📢 Update Terbaru</h3>", unsafe_allow_html=True)

col_spacer_l, col_news, col_spacer_r = st.columns([1, 6, 1])

with col_news:
    if len(data_pengumuman) > 0:
        for item in reversed(data_pengumuman):
            tipe = item.get('Tipe', 'Info')
            
            # Warna Border Kiri
            if tipe == "Urgent": border = "#ff4757"
            elif tipe == "Penting": border = "#ffa502"
            else: border = "#2ed573"

            # HTML Rapat Kiri (NO INDENTATION)
            st.markdown(f"""
<div class="announce-item" style="border-left: 5px solid {border};">
<div style="display:flex; justify-content:space-between; margin-bottom:5px;">
<strong style="text-transform:uppercase; color:#f1f2f6;">{tipe}</strong>
<small style="color:#dfe4ea;">{item.get('Tanggal','-')}</small>
</div>
<h3 style="margin:0; font-size:1.2rem; color:white;">{item.get('Judul','-')}</h3>
<p style="margin-top:5px; color:#f1f2f6; line-height:1.5;">{item.get('Isi','-')}</p>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <p>Belum ada pengumuman.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer Spacing
st.write("")
st.write("")
st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.6); font-size:0.8rem;'>© 2026 Sains Data Crisis Center</div>", unsafe_allow_html=True)
