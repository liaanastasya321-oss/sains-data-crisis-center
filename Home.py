import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os
import requests
import datetime
import base64
import google.generativeai as genai
import plotly.graph_objects as go

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
# 2. DESIGN SYSTEM (MODERN CLEAN UI - NO GLASS) ✨
# =========================================================
st.markdown("""
<style>
    /* IMPORT FONT KEREN (Plus Jakarta Sans - Ala Startup) */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0f172a; /* Warna teks gelap elegan */
    }
    
    /* BACKGROUND BERSIH (ABU MUDA) */
    .stApp {
        background-color: #f1f5f9; 
    }

    /* HAPUS ELEMEN BAWAAN */
    #MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
    .stApp > header { display: none !important; }
    div[data-testid="stDecoration"] { display: none; }

    /* --- NAVBAR STICKY YANG RAPI --- */
    iframe[title="streamlit_option_menu.option_menu"] {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05); /* Bayangan tipis banget */
        padding: 5px 0;
    }

    /* --- JARAK KONTEN (ANTI KEPOTONG - DINAMIS) --- */
    /* Laptop */
    .block-container {
        padding-top: 110px !important; 
        padding-bottom: 50px !important;
        max-width: 1200px !important;
    }
    
    /* HP (Mobile) */
    @media (max-width: 600px) {
        .block-container {
            padding-top: 100px !important; /* Jarak pas buat HP */
            padding-left: 15px !important;
            padding-right: 15px !important;
        }
    }

    /* --- KARTU MENU (SOLID WHITE - BUKAN KACA) --- */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0; /* Garis pinggir tipis */
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        height: 100%;
        text-align: center;
        transition: transform 0.2s;
    }
    
    /* Efek Hover (Gerak dikit pas disentuh) */
    .feature-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
    }

    .card-icon { font-size: 32px; margin-bottom: 12px; display: block; }
    .card-title { font-weight: 800; font-size: 18px; color: #1e293b; margin-bottom: 6px; display: block; }
    .card-desc { font-size: 13px; color: #64748b; line-height: 1.5; }

    /* --- HEADER IDENTITY (LOGO & JUDUL) --- */
    .brand-box {
        background: white;
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .brand-logo { height: 80px; width: auto; margin-bottom: 15px; }
    
    .brand-title {
        font-size: 28px;
        font-weight: 800;
        /* Gradient Text Biru */
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    
    .brand-subtitle {
        font-size: 14px;
        color: #64748b;
        font-weight: 500;
    }

    /* Penyesuaian Header di HP */
    @media (max-width: 600px) {
        .brand-box { padding: 20px 15px; margin-bottom: 20px; }
        .brand-logo { height: 50px; }
        .brand-title { font-size: 22px; }
        .brand-subtitle { font-size: 12px; }
        
        /* Grid Menu jadi 1 kolom otomatis */
        .feature-card { padding: 15px; margin-bottom: 10px; }
    }

    /* --- INPUT FORM YANG RAPI --- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px !important;
        background-color: white !important;
        color: #334155 !important;
    }
    
    /* Tombol Utama (Biru Tua - Professional) */
    .stButton > button {
        background-color: #1e293b !important; 
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #334155 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Pesan Chat */
    .chat-bubble {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.5;
        border: 1px solid #e2e8f0;
    }
    .user-msg { background-color: #eff6ff; color: #1e3a8a; border-left: 4px solid #2563eb; }
    .bot-msg { background-color: #ffffff; color: #334155; border-left: 4px solid #94a3b8; }

</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. SETUP & FUNCTIONS
# =========================================================
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
        sh = client.open_by_key(ID_SPREADSHEET)
        return sh
    except: return None

sh = get_spreadsheet()
try: sheet = sh.worksheet("Laporan") if sh else None
except: sheet = None
try: sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None
except: sheet_pengumuman = None

if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

# =========================================================
# 4. NAVIGATION (NAMA PENDEK BIAR MUAT DI HP)
# =========================================================
if 'selected_menu' not in st.session_state: st.session_state.selected_menu = "Home"

selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor", "Status", "Data", "SadasBot", "Admin"], # NAMA MENU SINGKAT
    icons=["house", "send", "search", "bar-chart", "robot", "shield-lock"],
    default_index=0,
    orientation="horizontal",
    key="nav_menu",
    styles={
        "container": {"padding": "0", "background-color": "white"},
        "nav-link": {"font-size": "11px", "color": "#64748b", "margin": "0px", "padding": "10px 5px"},
        "nav-link-selected": {"background-color": "#eff6ff", "color": "#2563eb", "font-weight": "bold"},
    }
)

# =========================================================
# 5. HEADER COMPONENT (FUNGSI PEMANGGIL)
# =========================================================
def render_header():
    # Ganti 'logo_uin.png' dengan nama file logomu yang benar
    img_uin = get_img_as_base64("logo_uin.png") 
    
    # Header Putih Bersih di Tengah
    st.markdown(f"""
    <div class="brand-box">
        <div style="display: flex; justify-content: center; align-items: center; gap: 15px;">
            {'<img src="data:image/png;base64,' + img_uin + '" class="brand-logo">' if img_uin else ''}
        </div>
        <div style="margin-top: 15px;">
            <div class="brand-title">SAINS DATA CRISIS CENTER</div>
            <div class="brand-subtitle">Pusat Advokasi & Layanan Mahasiswa Terpadu</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# HALAMAN: HOME
# =========================================================
if selected == "Home":
    render_header()
    
    st.markdown("### 👋 Layanan Cepat")
    
    # Grid Menu yang Rapi
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="card-icon">📢</span>
            <span class="card-title">Pelaporan</span>
            <span class="card-desc">Laporkan kendala akademik & fasilitas secara resmi.</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="card-icon">📊</span>
            <span class="card-title">Transparansi</span>
            <span class="card-desc">Pantau statistik penyelesaian masalah prodi.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="card-icon">🤖</span>
            <span class="card-title">Sadas Bot</span>
            <span class="card-desc">Tanya jawab seputar akademik 24 jam non-stop.</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### 📌 Pengumuman Terbaru")
    
    if sheet_pengumuman:
        try:
            data = sheet_pengumuman.get_all_records()
            if data:
                for item in reversed(data[-3:]): # Ambil 3 terakhir
                    st.info(f"**{item['Judul']}** \n\n {item['Isi']}")
            else: st.caption("Belum ada pengumuman.")
        except: st.warning("Gagal koneksi database.")

# =========================================================
# HALAMAN: LAPOR
# =========================================================
elif selected == "Lapor":
    render_header()
    
    # Container Putih untuk Form
    with st.container():
        st.markdown("<div style='background:white; padding:20px; border-radius:12px; border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("### 📝 Form Pengaduan")
        st.caption("Identitas pelapor akan dijaga kerahasiaannya.")
        
        with st.form("form_lapor"):
            nama = st.text_input("Nama Lengkap")
            col1, col2 = st.columns(2)
            with col1: npm = st.text_input("NPM")
            with col2: angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025", "Lainnya"])
            
            kategori = st.selectbox("Jenis Masalah", ["Akademik (Nilai/KRS)", "Fasilitas Kampus", "Keuangan/UKT", "Bullying/Kekerasan", "Lainnya"])
            keluhan = st.text_area("Jelaskan Masalahmu", height=150)
            file = st.file_uploader("Lampiran Bukti (Opsional)", type=["jpg", "png", "pdf"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Kirim Laporan"):
                if not nama or not keluhan:
                    st.error("Nama dan Isi keluhan wajib diisi.")
                else:
                    with st.spinner("Mengirim data..."):
                        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        link = "-"
                        # Upload Image logic (Simplified)
                        if file:
                             try:
                                files = {"image": file.getvalue()}
                                params = {"key": API_KEY_IMGBB}
                                res = requests.post("https://api.imgbb.com/1/upload", params=params, files=files)
                                data_res = res.json()
                                if data_res.get("success"): link = data_res["data"]["url"]
                             except: pass

                        try:
                            sheet.append_row([waktu, nama, npm, angkatan, kategori, keluhan, "Menunggu", link])
                            st.success("✅ Laporan berhasil dikirim! Pantau di menu Status.")
                        except: st.error("Gagal menyimpan. Coba lagi.")
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# HALAMAN: STATUS
# =========================================================
elif selected == "Status":
    render_header()
    st.markdown("### 🔍 Cek Status Laporan")
    
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        npm_input = st.text_input("Masukkan NPM", placeholder="Contoh: 2117xxx", label_visibility="collapsed")
    with col_btn:
        cek = st.button("Lacak")
        
    if cek and npm_input:
        if sheet:
            try:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                df['NPM'] = df['NPM'].astype(str)
                hasil = df[df['NPM'] == npm_input]
                
                if not hasil.empty:
                    for idx, row in hasil.iterrows():
                        bg_color = "#fff7ed" if row['Status'] == "Menunggu" else "#f0fdf4"
                        border_color = "#f97316" if row['Status'] == "Menunggu" else "#22c55e"
                        
                        st.markdown(f"""
                        <div style="background:{bg_color}; padding:15px; border-radius:10px; border-left:5px solid {border_color}; margin-bottom:10px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                            <small style="color:#64748b">{row['Waktu Lapor']}</small>
                            <h4 style="margin:5px 0;">{row['Kategori Masalah']}</h4>
                            <p style="color:#334155; font-size:14px;">"{row['Detail Keluhan']}"</p>
                            <div style="margin-top:10px;">
                                <span style="background:{border_color}; color:white; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:bold;">{row['Status']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada laporan ditemukan untuk NPM ini.")
            except: st.error("Gagal ambil data.")

# =========================================================
# HALAMAN: SADAS BOT
# =========================================================
elif selected == "SadasBot":
    st.markdown("<div style='text-align:center; margin-bottom:20px;'><h3>🤖 Sadas Bot AI</h3><p style='color:#64748b; font-size:14px;'>Asisten Akademik Virtual 24/7</p></div>", unsafe_allow_html=True)
    
    # Input di atas biar gampang di HP
    if prompt := st.chat_input("Ketik pertanyaanmu..."):
        if "messages" not in st.session_state: st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Logic AI
        response = "Maaf, API Key belum disetting."
        if "GEMINI_API_KEY" in st.secrets:
            try:
                # Auto-Detect Logic Sederhana
                try: model = genai.GenerativeModel('gemini-1.5-flash')
                except: model = genai.GenerativeModel('gemini-pro')
                
                system_prompt = "Kamu Sadas Bot, asisten mahasiswa Data Science UIN. Jawab sopan, singkat, padat."
                res = model.generate_content(f"{system_prompt}\nUser: {prompt}")
                response = res.text
            except Exception as e: response = f"Error: {e}"
            
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Render Chat
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            tipe = "user-msg" if msg['role'] == "user" else "bot-msg"
            align = "right" if msg['role'] == "user" else "left"
            st.markdown(f"""
            <div style="display:flex; justify-content:{align};">
                <div class="chat-bubble {tipe}" style="max-width: 85%;">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
                
    if st.button("🗑️ Bersihkan Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()

# =========================================================
# HALAMAN: DATA
# =========================================================
elif selected == "Data":
    render_header()
    st.markdown("### 📊 Statistik Laporan")
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            # Simple Metrics
            c1, c2 = st.columns(2)
            c1.metric("Total Laporan", len(df))
            c2.metric("Selesai", len(df[df['Status']=='Selesai']))
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data laporan masuk.")

elif selected == "Admin":
    st.markdown("### 🔐 Halaman Admin")
    pwd = st.text_input("Password", type="password")
    if pwd == "RAHASIA PIKM😭":
        st.success("Login Berhasil!")
