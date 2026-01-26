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
# 🎨 MASTER DESIGN SYSTEM (WEBSITE STYLE)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT (Source Sans 3) */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

    /* RESET STYLE */
    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
        color: #334155;
    }

    /* HILANGKAN PADDING ATAS BAWAAN STREAMLIT BIAR FULL SCREEN */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }

    /* --- HERO SECTION (BAGIAN ATAS BIRU) --- */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 4rem 2rem;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        border-bottom: 5px solid #fbbf24; /* Garis emas di bawah header */
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
        color: #ffffff !important;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        color: #e2e8f0 !important;
        max-width: 800px;
        margin: 0 auto;
    }

    /* --- KARTU MENU --- */
    .nav-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #cbd5e1; /* Default border */
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        text-align: center;
    }
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* WARNA BORDE KARTU */
    .border-red { border-top-color: #ef4444; }
    .border-green { border-top-color: #10b981; }
    .border-blue { border-top-color: #3b82f6; }
    .border-orange { border-top-color: #f59e0b; }

    /* TOMBOL BUTTON */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
        margin-top: 10px;
    }

    /* --- PENGUMUMAN --- */
    .announce-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0 8px 8px 0;
    }
    
    /* FOOTER */
    .custom-footer {
        text-align: center;
        padding: 2rem;
        background-color: #f1f5f9;
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #e2e8f0;
    }
    
    /* HIDE DEFAULT ELEMENTS */
    header {visibility: hidden;}
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
# 1. HERO SECTION (HTML MURNI)
# ==========================================
# Ini trik biar header nempel di atas kayak website beneran
st.markdown("""
<div class="hero-container">
    <div class="hero-title">SAINS DATA CRISIS CENTER</div>
    <div class="hero-subtitle">
        Sistem Layanan Advokasi Terpadu & Terintegrasi<br>
        Himpunan Mahasiswa Sains Data UIN Raden Intan Lampung
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. MENU NAVIGATION GRID
# ==========================================
# Kita kasih container biar tidak terlalu lebar
with st.container():
    col_l, col_content, col_r = st.columns([1, 10, 1])
    
    with col_content:
        # Baris Menu
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown("""
            <div class="nav-card border-red">
                <h3 style="margin:0; color:#1e293b;">📝 Lapor</h3>
                <p style="font-size:0.85rem; color:#64748b; margin-bottom:0;">Layanan pengaduan akademik & fasilitas.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Buat Laporan", key="btn_lapor"):
                st.switch_page("pages/Lapor_Masalah.py")

        with c2:
            st.markdown("""
            <div class="nav-card border-green">
                <h3 style="margin:0; color:#1e293b;">🔍 Tracking</h3>
                <p style="font-size:0.85rem; color:#64748b; margin-bottom:0;">Cek status tindak lanjut laporan Anda.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Cek Status", key="btn_status"):
                st.switch_page("pages/Cek_Status.py")

        with c3:
            st.markdown("""
            <div class="nav-card border-blue">
                <h3 style="margin:0; color:#1e293b;">📊 Data</h3>
                <p style="font-size:0.85rem; color:#64748b; margin-bottom:0;">Dashboard transparansi data advokasi.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Lihat Data", key="btn_dash"):
                st.switch_page("pages/Dashboard_Publik.py")

        with c4:
            st.markdown("""
            <div class="nav-card border-orange">
                <h3 style="margin:0; color:#1e293b;">🤖 Bot AI</h3>
                <p style="font-size:0.85rem; color:#64748b; margin-bottom:0;">Asisten virtual 24 jam (Tanya Jawab).</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Mulai Chat", key="btn_bot"):
                st.switch_page("pages/Sadas_Bot.py")

        # ==========================================
        # 3. PENGUMUMAN SECTION
        # ==========================================
        st.write("")
        st.write("")
        st.markdown("<h3 style='border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-top: 30px;'>📢 Papan Informasi Terbaru</h3>", unsafe_allow_html=True)

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
                # Gunakan satu baris panjang atau f-string tanpa indentasi di dalam tag
                st.markdown(f"""
<div style="background: white; border-left: 5px solid {border_color}; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px;">
    <div style="display:flex; justify-content:space-between; margin-bottom: 10px;">
        <span style="background:{bg_badge}; color:{txt_badge}; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">{tipe.upper()}</span>
        <span style="font-size: 0.85rem; color: #64748b;">{item.get('Tanggal','-')}</span>
    </div>
    <div style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 5px;">{item.get('Judul','-')}</div>
    <div style="font-size: 0.95rem; color: #475569; line-height: 1.5;">{item.get('Isi','-')}</div>
</div>
""", unsafe_allow_html=True)

        else:
            st.info("Belum ada pengumuman resmi.")

# ==========================================
# 4. FOOTER (KAKI WEBSITE)
# ==========================================
st.markdown("""
<div class="custom-footer">
    &copy; 2026 Sains Data Crisis Center - UIN Raden Intan Lampung<br>
    <small>Dibuat dengan ❤️ oleh Divisi Advokasi</small>
</div>
""", unsafe_allow_html=True)
