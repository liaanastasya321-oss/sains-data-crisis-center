import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json, os, datetime, base64
import requests
import google.generativeai as genai

# =========================================================
# 1. PAGE CONFIG (WAJIB PALING ATAS)
# =========================================================
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. CLEAN MODERN CSS (STYLE DARI GPT - DIPERTAHANKAN) 🎨
# =========================================================
st.markdown("""
<style>
/* Font Keren */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hapus Elemen Bawaan */
#MainMenu, footer, header { display:none !important; }
div[data-testid="stDecoration"] { display:none; }
.stApp > header { display: none !important; }

/* Background Bersih */
.stApp {
    background-color: #f8fafc;
}

/* Container Rapih (Tengah) */
.block-container {
    max-width: 1000px;
    padding-top: 20px;
    padding-bottom: 40px;
}

/* HEADER STYLE (Mobile Friendly) */
.app-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 32px;
    padding: 20px 24px;
    background: white;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.app-title {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
}

.app-subtitle {
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
}

/* STYLE TOMBOL KEREN */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    padding: 14px;
    font-weight: 600;
    border: none;
    background: #0f172a; /* Warna Gelap Elegan */
    color: white;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #334155;
    transform: translateY(-2px);
}

/* STYLE CHAT */
.chat-user {
    background: #eff6ff;
    color: #1e3a8a;
    padding: 12px 16px;
    border-radius: 12px 12px 0 12px;
    margin-bottom: 10px;
    max-width: 85%;
    margin-left: auto;
    font-size: 14px;
    border: 1px solid #dbeafe;
}

.chat-bot {
    background: #ffffff;
    color: #334155;
    padding: 12px 16px;
    border-radius: 12px 12px 12px 0;
    margin-bottom: 10px;
    max-width: 85%;
    font-size: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* INPUT FIELD */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    color: #0f172a !important;
}

/* MENU NAVIGASI */
iframe[title="streamlit_option_menu.option_menu"] {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI DATABASE & AI
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g"
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_sheet():
    try:
        if "google_credentials" in st.secrets:
            creds = Credentials.from_service_account_info(
                json.loads(st.secrets["google_credentials"]), scopes=SCOPES
            )
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        else: return None
        client = gspread.authorize(creds)
        sh = client.open_by_key(ID_SPREADSHEET)
        return sh
    except: return None

sh = get_sheet()
sheet_laporan = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

# Setup Gemini
if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

# Helper Gambar
def get_img_base64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# Helper Header (Biar Rapi di HP)
def render_header():
    logo = get_img_base64("logo_uin.png")
    st.markdown(f"""
    <div class="app-header">
        {f'<img src="data:image/png;base64,{logo}" height="60" style="object-fit:contain;">' if logo else ''}
        <div>
            <div class="app-title">SAINS DATA CRISIS CENTER</div>
            <div class="app-subtitle">Pusat Advokasi & Layanan Mahasiswa</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 4. NAVIGASI (DIPERBAIKI BIAR TOMBOL HOME BERFUNGSI)
# =========================================================
# Gunakan session state untuk sinkronisasi tombol Home dengan Navbar
if 'nav_menu' not in st.session_state:
    st.session_state.nav_menu = "Home"

menu = option_menu(
    None,
    ["Home", "Lapor", "Status", "Data", "SadasBot", "Admin"],
    icons=["house", "send", "search", "bar-chart", "robot", "shield-lock"],
    orientation="horizontal",
    key="nav_menu", # Kunci ini penting biar tombol di Home bisa ngubah menu
    styles={
        "container": {"padding": "0!important", "background-color": "white", "border-radius": "12px", "border": "1px solid #e2e8f0"},
        "icon": {"color": "#64748b", "font-size": "14px"}, 
        "nav-link": {"font-size": "12px", "text-align": "center", "margin": "0px", "color": "#475569"},
        "nav-link-selected": {"background-color": "#eff6ff", "color": "#2563eb", "font-weight": "800"},
    }
)

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if menu == "Home":
    render_header()
    st.markdown("##### 👋 Layanan Cepat")

    col1, col2, col3 = st.columns(3)

    # Tombol ini sekarang BENAR-BENAR berfungsi memindah halaman
    with col1:
        if st.button("📢 Pelaporan"):
            st.session_state.nav_menu = "Lapor"
            st.rerun()

    with col2:
        if st.button("🔍 Cek Status"):
            st.session_state.nav_menu = "Status"
            st.rerun()

    with col3:
        if st.button("🤖 Sadas Bot"):
            st.session_state.nav_menu = "SadasBot"
            st.rerun()

    st.write("")
    st.markdown("##### 📌 Info Terbaru")
    
    if sheet_pengumuman:
        try:
            data = sheet_pengumuman.get_all_records()
            if data:
                for item in reversed(data[-3:]):
                    # Style Card Pengumuman Simple
                    st.markdown(f"""
                    <div style="background:white; padding:16px; border-radius:12px; border:1px solid #e2e8f0; margin-bottom:10px;">
                        <div style="font-weight:700; color:#0f172a; margin-bottom:4px;">{item['Judul']}</div>
                        <div style="font-size:13px; color:#64748b;">{item['Isi']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.caption("Belum ada pengumuman.")
        except: st.warning("Gagal memuat pengumuman.")

# =========================================================
# 6. HALAMAN: LAPOR
# =========================================================
elif menu == "Lapor":
    render_header()
    st.markdown("##### 📝 Form Pengaduan")
    
    with st.container():
        with st.form("lapor"):
            nama = st.text_input("Nama Lengkap")
            col_a, col_b = st.columns(2)
            with col_a: npm = st.text_input("NPM")
            with col_b: angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025"])
            
            kategori = st.selectbox("Kategori", ["Akademik", "Fasilitas", "Keuangan", "Lainnya"])
            isi = st.text_area("Detail Masalah", height=120)
            file = st.file_uploader("Bukti (Opsional)", type=["jpg","png","pdf"])

            if st.form_submit_button("Kirim Laporan"):
                if not nama or not isi:
                    st.error("Nama & Detail masalah wajib diisi.")
                elif sheet_laporan:
                    with st.spinner("Mengirim..."):
                        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        link = "-"
                        # Upload Image (Simple ImgBB)
                        if file:
                            try:
                                files = {"image": file.getvalue()}
                                res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files=files)
                                if res.json().get("success"): link = res.json()["data"]["url"]
                            except: pass
                        
                        sheet_laporan.append_row([waktu, nama, npm, kategori, isi, "Menunggu", link])
                        st.success("Berhasil! Laporanmu sudah masuk.")
                else:
                    st.error("Database error.")

# =========================================================
# 7. HALAMAN: STATUS (YANG TADI HILANG)
# =========================================================
elif menu == "Status":
    render_header()
    st.markdown("##### 🔍 Cek Status Laporan")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        cari_npm = st.text_input("Masukkan NPM", placeholder="2117xxx", label_visibility="collapsed")
    with col_s2:
        btn_cari = st.button("Cari")
        
    if btn_cari and cari_npm:
        if sheet_laporan:
            try:
                data = sheet_laporan.get_all_records()
                df = pd.DataFrame(data)
                df['NPM'] = df['NPM'].astype(str)
                hasil = df[df['NPM'] == cari_npm]
                
                if not hasil.empty:
                    for idx, row in hasil.iterrows():
                        # Style Status Card Clean
                        st.markdown(f"""
                        <div style="background:white; padding:16px; border-radius:12px; border:1px solid #e2e8f0; margin-bottom:10px; border-left: 4px solid #2563eb;">
                            <div style="font-size:12px; color:#94a3b8; margin-bottom:4px;">{row['Waktu Lapor']} • {row['Kategori Masalah']}</div>
                            <div style="font-size:14px; color:#334155; margin-bottom:8px;">"{row['Detail Keluhan']}"</div>
                            <div style="background:#eff6ff; color:#2563eb; display:inline-block; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700;">{row['Status']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("NPM tidak ditemukan.")
            except: st.error("Gagal koneksi.")

# =========================================================
# 8. HALAMAN: SADAS BOT
# =========================================================
elif menu == "SadasBot":
    st.markdown("<div style='text-align:center; margin-bottom:20px;'><h3>🤖 Sadas Bot</h3><p style='color:#64748b; font-size:13px;'>Asisten Pintar 24/7</p></div>", unsafe_allow_html=True)

    if "chat" not in st.session_state: st.session_state.chat = []

    # Render Chat
    for c in st.session_state.chat:
        tipe = "chat-user" if c['role'] == 'user' else "chat-bot"
        st.markdown(f"<div class='{tipe}'>{c['msg']}</div>", unsafe_allow_html=True)

    # Input
    if q := st.chat_input("Ketik pertanyaan..."):
        st.session_state.chat.append({"role": "user", "msg": q})
        st.rerun()

    # Generate Reply (Setelah rerun biar smooth)
    if st.session_state.chat and st.session_state.chat[-1]['role'] == 'user':
        q = st.session_state.chat[-1]['msg']
        reply = "Maaf, API Key error."
        
        if "GEMINI_API_KEY" in st.secrets:
            try:
                # Auto Detect Model
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else 'models/gemini-pro'
                
                model = genai.GenerativeModel(target)
                res = model.generate_content(f"Kamu Sadas Bot, asisten mahasiswa ramah. Jawab: {q}")
                reply = res.text
            except Exception as e: reply = f"Error: {str(e)}"
        
        st.session_state.chat.append({"role": "bot", "msg": reply})
        st.rerun()
        
    if st.button("Hapus Chat", type="secondary"):
        st.session_state.chat = []
        st.rerun()

# =========================================================
# 9. HALAMAN: DATA
# =========================================================
elif menu == "Data":
    render_header()
    st.markdown("##### 📊 Data Laporan")
    if sheet_laporan:
        df = pd.DataFrame(sheet_laporan.get_all_records())
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Data masih kosong.")

# =========================================================
# 10. HALAMAN: ADMIN
# =========================================================
elif menu == "Admin":
    render_header()
    st.markdown("##### 🔐 Admin Login")
    pwd = st.text_input("Password", type="password")
    if pwd == "RAHASIA PIKM😭":
        st.success("Login Berhasil!")
        # Isi fitur admin disini
