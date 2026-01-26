import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# 1. SETUP HALAMAN
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 MASTER DESIGN SYSTEM (OFFICIAL NAVY)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT (Source Sans 3 - Font Resmi) */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700;800&display=swap');

    /* RESET STYLE */
    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
        color: #334155;
        background-color: #f8fafc; /* Background Body Abu Muda Bersih */
    }

    /* HEADER / HERO SECTION (BIRU GELAP) */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); /* Navy ke Royal Blue */
        padding: 3rem 2rem;
        border-radius: 0 0 20px 20px; /* Lengkungan halus di bawah */
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
        margin-top: -3rem; /* Tarik ke atas biar nempel langit-langit */
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        color: #ffffff !important; /* Teks Putih */
        text-transform: uppercase;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 300;
        color: #e2e8f0 !important; /* Teks Abu Terang */
        max-width: 800px;
        margin: 0 auto;
    }

    /* KARTU MENU (PUTIH BERSIH) */
    .nav-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        height: 100%;
        text-align: center;
        transition: transform 0.2s;
    }
    .nav-card:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .nav-icon { font-size: 2.5rem; margin-bottom: 10px; display: block; }
    .nav-title { font-weight: 700; color: #0f172a; margin-bottom: 5px; font-size: 1.2rem; }
    .nav-desc { font-size: 0.85rem; color: #64748b; }

    /* TOMBOL BUTTON */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        margin-top: 10px;
        background-color: #0f172a; /* Tombol warna Navy biar seragam */
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1e3a8a;
    }

    /* PENGUMUMAN */
    .announce-card {
        background: white;
        border-left: 5px solid #3b82f6;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* FOOTER */
    .custom-footer {
        text-align: center;
        padding: 2rem;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        border-top: 1px solid #e2e8f0;
    }
    
    /* PENGATURAN HEADER ASLI */
    /* Kita sembunyikan dekorasi header tapi biarkan tombolnya bisa diakses */
    .block-container { padding-top: 2rem; }
    footer {visibility: hidden;}
    
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
# 1. HERO SECTION (BIRU GELAP)
# ==========================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">SAINS DATA CRISIS CENTER</div>
    <div class="hero-subtitle">
        Sistem Layanan Advokasi & Pelayanan Mahasiswa Terintegrasi<br>
        Himpunan Mahasiswa Sains Data UIN Raden Intan Lampung
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. MENU NAVIGATION
# ==========================================
with st.container():
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="nav-card">
            <span class="nav-icon">📝</span>
            <div class="nav-title">Lapor Aja</div>
            <div class="nav-desc">Layanan pengaduan akademik & fasilitas kampus.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buat Laporan", key="btn_lapor"):
            st.switch_page("pages/Lapor_Masalah.py")

    with c2:
        st.markdown("""
        <div class="nav-card">
            <span class="nav-icon">🔍</span>
            <div class="nav-title">Cek Status</div>
            <div class="nav-desc">Pantau tindak lanjut laporan Anda di sini.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cek Progres", key="btn_status"):
            st.switch_page("pages/Cek_Status.py")

    with c3:
        st.markdown("""
        <div class="nav-card">
            <span class="nav-icon">📊</span>
            <div class="nav-title">Data</div>
            <div class="nav-desc">Dashboard transparansi data advokasi himpunan.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Lihat Data", key="btn_dash"):
            st.switch_page("pages/Dashboard_Publik.py")

    with c4:
        st.markdown("""
        <div class="nav-card">
            <span class="nav-icon">🤖</span>
            <div class="nav-title">Bot AI</div>
            <div class="nav-desc">Asisten virtual 24 jam untuk tanya jawab cepat.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Chat Bot", key="btn_bot"):
            st.switch_page("pages/Sadas_Bot.py")

    # ==========================================
    # 3. PENGUMUMAN SECTION
    # ==========================================
    st.write("")
    st.markdown("<h3 style='border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-top: 30px; color: #0f172a;'>📢 Papan Informasi Terbaru</h3>", unsafe_allow_html=True)

    if len(data_pengumuman) > 0:
        for item in reversed(data_pengumuman):
            tipe = item.get('Tipe', 'Info')
            
            if tipe == "Urgent":
                border_color = "#ef4444"; bg_badge = "#fee2e2"; txt_badge = "#991b1b"
            elif tipe == "Penting":
                border_color = "#f59e0b"; bg_badge = "#fef3c7"; txt_badge = "#92400e"
            else:
                border_color = "#3b82f6"; bg_badge = "#dbeafe"; txt_badge = "#1e40af"

            # HTML Rapat Kiri (PENTING AGAR TIDAK BOCOR)
            st.markdown(f"""
<div class="announce-card" style="border-left: 5px solid {border_color};">
<div style="display:flex; justify-content:space-between; margin-bottom: 8px;">
<span style="background:{bg_badge}; color:{txt_badge}; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform:uppercase;">{tipe}</span>
<span style="font-size: 0.85rem; color: #64748b;">📅 {item.get('Tanggal','-')}</span>
</div>
<div style="font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 5px;">{item.get('Judul','-')}</div>
<div style="font-size: 0.95rem; color: #475569; line-height: 1.5;">{item.get('Isi','-')}</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.info("Belum ada pengumuman resmi.")

# ==========================================
# 4. FOOTER
# ==========================================
st.markdown("""
<div class="custom-footer">
    &copy; 2026 Sains Data Crisis Center - UIN Raden Intan Lampung<br>
    Dibuat dengan ❤️ oleh Divisi Advokasi
</div>
""", unsafe_allow_html=True)
