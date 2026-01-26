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

    /* HILANGKAN ELEMENT MENGGANGGU */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

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
    }
    .stButton > button:hover { background-color: #1d4ed8; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE (DUAL MODE: LOKAL & CLOUD) 🔗
# ==========================================
# Ini bagian penting biar gak error di GitHub atau Lokal
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
    # Kalau error koneksi, jangan bikin web mati, tapi kosongkan data aja
    # st.error(f"Error Database: {e}") # Aktifkan ini kalau mau liat errornya
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

    # Menu Cepat
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #ef4444;">
            <h3>📝 Lapor Masalah</h3>
            <p style="font-size:0.9rem; color:#64748b;">Punya kendala akademik atau fasilitas? Laporkan di sini secara aman.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buka Lapor Masalah", key="btn_lapor", use_container_width=True):
             st.switch_page("pages/1_📝_Lapor_Masalah.py")
        
    with c2:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #3b82f6;">
            <h3>📊 Dashboard</h3>
            <p style="font-size:0.9rem; color:#64748b;">Pantau status penanganan masalah secara real-time dan transparan.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Lihat Dashboard", key="btn_dash", use_container_width=True):
             st.switch_page("pages/2_📊_Dashboard_Publik.py")
        
    with c3:
        st.markdown("""
        <div class="pro-card" style="text-align:center; border-top: 4px solid #f59e0b;">
            <h3>🤖 Sadas Bot</h3>
            <p style="font-size:0.9rem; color:#64748b;">Asisten AI 24 jam. Tanya info beasiswa, UKT, dan akademik.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Tanya Bot", key="btn_bot", use_container_width=True):
             st.switch_page("pages/4_🤖_Sadas_Bot.py")

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
