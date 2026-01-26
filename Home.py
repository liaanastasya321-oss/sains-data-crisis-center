import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# 1. SETUP HALAMAN (Wajib Paling Atas)
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 MASTER DESIGN SYSTEM (CORPORATE STYLE)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT PREMIUM (Source Sans 3 - Standar Adobe/Professional) */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800&display=swap');

    /* RESET & BASE STYLE */
    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
        color: #111827; /* Gray-900: Hampir hitam, sangat tegas */
    }

    /* BACKGROUND BERSIH (Tanpa Motif Mainan) */
    .stApp {
        background-color: #f3f4f6; /* Gray-100: Abu-abu sangat muda, elegan */
    }

    /* SIDEBAR (Warna Kampus/Solid) */
    [data-testid="stSidebar"] {
        background-color: #0f172a; /* Slate-900: Deep Navy */
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #f8fafc !important;
    }

    /* KARTU PROFESIONAL (Shadow Lebih Halus & Border Tipis) */
    .pro-card {
        background: #ffffff;
        padding: 24px;
        border-radius: 8px; /* Sudut tidak terlalu bulat (lebih kotak/serius) */
        border: 1px solid #e5e7eb; /* Border abu tipis */
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); /* Shadow tipis standar korporat */
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .pro-card:hover {
        border-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* TYPOGRAPHY YANG LEBIH TEGAS */
    h1 {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 800; 
        letter-spacing: -0.5px;
        color: #111827; /* Hitam tegas */
    }
    h2, h3 {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 700;
        color: #1f2937; /* Gray-800 */
    }
    p, div {
        color: #374151; /* Gray-700: Teks isi lebih gelap biar terbaca jelas */
        line-height: 1.6;
    }
    
    /* TOMBOL PRIMARY (Solid Blue - No Gradient) */
    .stButton > button {
        background-color: #1d4ed8; /* Biru BUMN/Korporat */
        color: white;
        border: none;
        border-radius: 6px; /* Sudut tajam dikit */
        font-weight: 600;
        padding: 0.6rem 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        width: 100%;
        font-family: 'Source Sans 3', sans-serif;
    }
    .stButton > button:hover { 
        background-color: #1e40af; /* Biru lebih gelap saat hover */
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE (DUAL MODE) 🔗
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

except Exception:
    data_pengumuman = []

# ==========================================
# HERO SECTION
# ==========================================
col_spacer_l, col_main, col_spacer_r = st.columns([1, 8, 1])

with col_main:
    st.markdown("""
    <div style="text-align: center; padding-top: 50px; padding-bottom: 50px;">
        <h1 style="font-size: 3.2rem; margin-bottom: 15px; color: #0f172a;">SAINS DATA <span style="color:#2563eb;">CRISIS CENTER</span></h1>
        <p style="font-size: 1.25rem; color: #4b5563; max-width: 700px; margin: 0 auto; font-weight: 400;">
            Platform Advokasi Terintegrasi Himpunan Mahasiswa Sains Data.<br>
            <span style="font-weight: 600; color: #1f2937;">Transparan. Responsif. Berbasis Data.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- MENU NAVIGASI (4 KOLOM) ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #dc2626; min-height: 190px;">
            <h3 style="margin-top:0;">📝 Lapor</h3>
            <p style="font-size:0.9rem;">Sampaikan kendala akademik & fasilitas secara resmi.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buat Laporan", key="btn_lapor"):
             st.switch_page("pages/Lapor_Masalah.py")
        
    with c2:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #059669; min-height: 190px;">
            <h3 style="margin-top:0;">🔍 Cek Status</h3>
            <p style="font-size:0.9rem;">Pantau tindak lanjut laporan Anda di sini.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cek Progres", key="btn_status"):
             st.switch_page("pages/Cek_Status.py")

    with c3:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #2563eb; min-height: 190px;">
            <h3 style="margin-top:0;">📊 Statistik</h3>
            <p style="font-size:0.9rem;">Transparansi data advokasi himpunan (Dashboard).</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Lihat Data", key="btn_dash"):
             st.switch_page("pages/Dashboard_Publik.py")
        
    with c4:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #d97706; min-height: 190px;">
            <h3 style="margin-top:0;">🤖 AI Help</h3>
            <p style="font-size:0.9rem;">Layanan informasi otomatis 24 jam (Chatbot).</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Chat", key="btn_bot"):
             st.switch_page("pages/Sadas_Bot.py")

    # ==========================================
    # PENGUMUMAN
    # ==========================================
    st.write("---")
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>📢 Informasi Resmi Himpunan</h2>", unsafe_allow_html=True)

    if len(data_pengumuman) > 0:
        for item in reversed(data_pengumuman):
            tipe = item.get('Tipe', 'Info')
            
            # Warna Badge (Lebih Solid)
            if tipe == "Urgent":
                badge_bg = "#fee2e2"; badge_txt = "#991b1b"; border_l = "#dc2626"
            elif tipe == "Penting":
                badge_bg = "#fef3c7"; badge_txt = "#92400e"; border_l = "#d97706"
            else:
                badge_bg = "#dbeafe"; badge_txt = "#1e40af"; border_l = "#2563eb"

            # Render HTML Rapat Kiri (Penting!)
            html_content = f"""
<div class="pro-card" style="border-left: 5px solid {border_l}; display: flex; flex-direction: column; gap: 10px; padding: 25px;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="background-color:{badge_bg}; color:{badge_txt}; padding: 5px 15px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{tipe}</span>
<span style="font-size: 0.9rem; color: #6b7280; font-weight: 600;">{item.get('Tanggal','-')}</span>
</div>
<div style="font-size: 1.25rem; font-weight: 700; color: #111827; margin-top: 5px;">{item.get('Judul','-')}</div>
<div style="font-size: 1rem; color: #374151; line-height: 1.6;">{item.get('Isi','-')}</div>
</div>
"""
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pro-card" style="text-align:center; padding: 50px;">
            <h3 style="color: #9ca3af; margin:0;">Belum ada informasi terbaru</h3>
        </div>
        """, unsafe_allow_html=True)
