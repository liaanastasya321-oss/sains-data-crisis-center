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
# 🎨 MASTER DESIGN SYSTEM (CSS PRO)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT MODERN (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* RESET & BASE STYLE */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }

    /* BACKGROUND BERSIH */
    .stApp {
        background-color: #f8fafc;
        background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
        background-size: 20px 20px;
    }

    /* SIDEBAR PROFESIONAL */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #e2e8f0 !important;
    }

    /* --- PENGATURAN TAMPILAN ELEMENT --- */
    /* Kita biarkan Header & Menu TETAP MUNCUL */
    /* #MainMenu {visibility: hidden;} */
    /* header {visibility: hidden;} */
    
    /* Cuma Footer bawaan Streamlit yang kita sembunyikan biar bersih */
    footer {visibility: hidden;}

    /* CUSTOM CARDS */
    .pro-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
        transition: transform 0.2s;
    }
    .pro-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }

    /* TYPOGRAPHY */
    h1 { font-weight: 800; letter-spacing: -0.025em; color: #0f172a; }
    h3 { font-weight: 600; color: #334155; }
    
    /* TOMBOL PRIMARY */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        width: 100%; /* Biar tombol full width */
    }
    .stButton > button:hover { background-color: #1d4ed8; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE (DUAL MODE: LOKAL & CLOUD) 🔗
# ==========================================
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # Cek 1: Apakah ada di Streamlit Cloud (Pakai Secrets)?
    if "google_credentials" in st.secrets:
        creds_dict = json.loads(st.secrets["google_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    
    # Cek 2: Apakah ada file lokal credentials.json?
    elif os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    
    # Cek 3: Cek di folder luar (opsional)
    elif os.path.exists("../credentials.json"):
        creds = Credentials.from_service_account_file("../credentials.json", scopes=scopes)
        
    else:
        st.warning("⚠️ File credentials belum ditemukan. Mode offline.")
        creds = None

    if creds:
        client = gspread.authorize(creds)
        sheet = client.open("Database_Advokasi").worksheet("Pengumuman")
        data_pengumuman = sheet.get_all_records()
    else:
        data_pengumuman = []

except Exception as e:
    data_pengumuman = []

# ==========================================
# HERO SECTION (Wajah Utama Website)
# ==========================================
col_spacer_l, col_main, col_spacer_r = st.columns([1, 8, 1])

with col_main:
    # Header
    st.markdown("""
    <div style="text-align: center; padding-top: 40px; padding-bottom: 40px;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">Sains Data <span style="color:#2563eb;">Crisis Center</span></h1>
        <p style="font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 0 auto;">
            Platform Advokasi Terintegrasi Himpunan Mahasiswa Sains Data.<br>
            Transparan. Cepat. Berbasis Data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- MENU NAVIGASI UTAMA (4 KOLOM) ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #ef4444; min-height: 200px;">
            <h3>📝 Lapor</h3>
            <p style="font-size:0.8rem; color:#64748b;">Laporkan kendala akademik & fasilitas.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buat Laporan", key="btn_lapor"):
             st.switch_page("pages/Lapor_Masalah.py")
        
    with c2:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #10b981; min-height: 200px;">
            <h3>🔍 Cek Status</h3>
            <p style="font-size:0.8rem; color:#64748b;">Pantau progres laporanmu di sini.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cek Progres", key="btn_status"):
             st.switch_page("pages/Cek_Status.py")

    with c3:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #3b82f6; min-height: 200px;">
            <h3>📊 Data</h3>
            <p style="font-size:0.8rem; color:#64748b;">Transparansi data advokasi himpunan.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Lihat Data", key="btn_dash"):
             st.switch_page("pages/Dashboard_Publik.py")
        
    with c4:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #f59e0b; min-height: 200px;">
            <h3>🤖 Bot AI</h3>
            <p style="font-size:0.8rem; color:#64748b;">Tanya jawab otomatis 24 jam.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Tanya Bot", key="btn_bot"):
             st.switch_page("pages/Sadas_Bot.py")

    # ==========================================
    # OFFICIAL ANNOUNCEMENTS (Mading Pro)
    # ==========================================
    st.write("---")
    st.subheader("📢 Informasi Resmi Himpunan")

    if len(data_pengumuman) > 0:
        for item in reversed(data_pengumuman):
            tipe = item.get('Tipe', 'Info')
            
            # Warna Badge
            if tipe == "Urgent":
                badge_color = "#fee2e2"; text_color = "#991b1b"; border_l = "#ef4444"
            elif tipe == "Penting":
                badge_color = "#fef3c7"; text_color = "#92400e"; border_l = "#f59e0b"
            else:
                badge_color = "#dbeafe"; text_color = "#1e40af"; border_l = "#3b82f6"

            # Render Kartu HTML
            html_content = f"""
            <div class="pro-card" style="border-left: 5px solid {border_l}; display: flex; flex-direction: column; gap: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="background-color:{badge_color}; color:{text_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">
                        {tipe.upper()}
                    </span>
                    <span style="font-size: 0.85rem; color: #94a3b8; font-weight:500;">📅 {item.get('Tanggal','-')}</span>
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">
                    {item.get('Judul','-')}
                </div>
                <div style="font-size: 0.95rem; color: #475569; line-height: 1.6;">
                    {item.get('Isi','-')}
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pro-card" style="text-align:center; padding: 40px; color: #94a3b8;">
            <p>Tidak ada pengumuman aktif saat ini.</p>
        </div>
        """, unsafe_allow_html=True)
