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
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. GLOBAL CSS (THE "REAL APP" LOOK) 💎
# =========================================================
st.markdown("""
<style>
    /* --- FONT KEREN (POPPINS) --- */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #0f172a;
    }

    /* BACKGROUND GRADIENT MEWAH */
    .stApp {
        background: linear-gradient(120deg, #e0f2fe 0%, #f0f9ff 50%, #ffffff 100%);
    }

    /* HAPUS SAMPAH BAWAAN */
    #MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
    .stApp > header { display: none !important; }

    /* --- NAVBAR STICKY --- */
    iframe[title="streamlit_option_menu.option_menu"] {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 999999;
        background: rgba(255, 255, 255, 0.95); /* Putih agak transparan dikit */
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        padding: 5px 0;
    }

    /* --- JARAK KONTEN (SOLUSI BRUTAL BIAR GAK KEPOTONG) --- */
    /* Laptop: Jarak standar */
    .block-container {
        padding-top: 110px !important;
        padding-bottom: 50px !important;
        max-width: 1200px;
    }

    /* HP: JARAKNYA DIBIKIN JAUH BANGET (200px) */
    /* Ini biar judul 'Pengaduan' gak ketutupan menu sama sekali */
    @media (max-width: 600px) {
        .block-container {
            padding-top: 180px !important; 
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* --- HEADER TABLE LAYOUT (ANTI ANCUR DI HP) --- */
    /* Kita pake tabel HTML biar posisinya KUNCI (Logo-Teks-Logo) */
    .header-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 30px;
    }
    .header-table td {
        vertical-align: middle;
        padding: 5px;
        border: none;
    }
    .logo-cell {
        width: 15%; /* Lebar kolom logo */
        text-align: center;
    }
    .text-cell {
        width: 70%; /* Lebar kolom teks */
        text-align: center;
    }
    .main-logo {
        width: 90px; /* Laptop */
        height: auto;
    }
    .main-title {
        font-size: 34px;
        font-weight: 800;
        background: linear-gradient(90deg, #0ea5e9, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .sub-title {
        font-size: 14px; color: #64748b; margin-top: 5px;
    }

    /* Header di HP */
    @media (max-width: 600px) {
        .main-logo { width: 45px; } /* Kecilin logo */
        .main-title { font-size: 18px; } /* Kecilin font */
        .sub-title { font-size: 10px; display: block; } /* Tetap munculin deskripsi */
        .header-table { margin-bottom: 10px; }
    }

    /* --- GLASS CARD (EFEK KACA YANG RAPI) --- */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        text-align: center;
        transition: transform 0.3s ease;
        height: 100%;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
        box-shadow: 0 10px 40px 0 rgba(31, 38, 135, 0.1);
    }
    .card-emoji { font-size: 30px; margin-bottom: 10px; display: block; }
    .card-head { font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 5px; display: block;}
    .card-text { font-size: 13px; color: #64748b; }

    /* --- INPUT FORM --- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 12px !important;
        background: rgba(255,255,255,0.8) !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    }

    /* --- TOMBOL --- */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #0ea5e9);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 0;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3);
    }

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
# 4. NAVIGATION
# =========================================================
if 'selected_menu' not in st.session_state: st.session_state.selected_menu = "Home"

selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor", "Status", "Data", "SadasBot", "Admin"], 
    icons=["house", "send", "search", "bar-chart", "robot", "shield-lock"],
    default_index=0,
    orientation="horizontal",
    key="nav_menu",
    styles={
        "container": {"padding": "0", "background-color": "transparent"},
        "nav-link": {"font-size": "11px", "color": "#475569", "margin": "0px", "padding": "10px 5px"},
        "nav-link-selected": {"background-color": "#eff6ff", "color": "#2563eb", "font-weight": "bold", "border-radius": "10px"},
    }
)

# =========================================================
# 5. HEADER COMPONENT (GRID LAYOUT)
# =========================================================
def render_header():
    img_uin = get_img_as_base64("logo_uin.png")
    img_him = get_img_as_base64("logo_him.png")
    
    # KITA PAKE TABLE HTML BIAR POSISINYA PATEN GAK LARI-LARI
    header_html = f"""
    <table class="header-table">
        <tr>
            <td class="logo-cell">
                {'<img src="data:image/png;base64,' + img_uin + '" class="main-logo">' if img_uin else ''}
            </td>
            <td class="text-cell">
                <h1 class="main-title">SAINS DATA CRISIS CENTER</h1>
                <div class="sub-title">Pusat Advokasi & Layanan Mahasiswa</div>
            </td>
            <td class="logo-cell">
                {'<img src="data:image/png;base64,' + img_him + '" class="main-logo">' if img_him else ''}
            </td>
        </tr>
    </table>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# =========================================================
# HALAMAN: HOME
# =========================================================
if selected == "Home":
    render_header()
    
    st.markdown("<h3 style='text-align:center; margin-bottom:20px;'>✨ Layanan Utama</h3>", unsafe_allow_html=True)
    
    # Grid Menu (Pake columns biasa, CSS akan handle tampilannya)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="glass-card">
            <span class="card-emoji">📢</span>
            <span class="card-head">Pelaporan</span>
            <span class="card-text">Lapor masalah akademik & fasilitas disini.</span>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("""
        <div class="glass-card">
            <span class="card-emoji">📊</span>
            <span class="card-head">Transparansi</span>
            <span class="card-text">Cek data statistik penyelesaian masalah.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="glass-card">
            <span class="card-emoji">🤖</span>
            <span class="card-head">Sadas Bot</span>
            <span class="card-text">Curhat atau tanya seputar akademik 24/7.</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    
    # Pengumuman dengan Style Glass
    if sheet_pengumuman:
        try:
            data = sheet_pengumuman.get_all_records()
            if data:
                st.markdown("### 📌 Info Terbaru")
                for item in reversed(data[-3:]):
                    st.info(f"**{item['Judul']}** — {item['Isi']}")
        except: pass

# =========================================================
# HALAMAN: LAPOR
# =========================================================
elif selected == "Lapor":
    render_header()
    
    # Bungkus Form dalam Glass Card besar
    st.markdown("""
    <div style="background:rgba(255,255,255,0.6); padding:20px; border-radius:20px; border:1px solid white;">
        <h3 style="text-align:center; margin-top:0;">📝 Form Pengaduan</h3>
        <p style="text-align:center; font-size:13px; color:#64748b;">Kami menjamin kerahasiaan identitas pelapor.</p>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    with st.form("form_lapor"):
        nama = st.text_input("Nama Lengkap")
        col1, col2 = st.columns(2)
        with col1: npm = st.text_input("NPM")
        with col2: angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025", "Lainnya"])
        
        kategori = st.selectbox("Kategori", ["Akademik", "Fasilitas", "Keuangan", "Bullying", "Lainnya"])
        keluhan = st.text_area("Detail Masalah", height=120)
        file = st.file_uploader("Bukti Pendukung (Opsional)", type=["jpg", "png", "pdf"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 Kirim Laporan"):
            if not nama or not keluhan:
                st.error("Nama & Keluhan wajib diisi ya!")
            else:
                with st.spinner("Sedang mengirim..."):
                    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    link = "-"
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
                        st.success("Laporan diterima! Cek menu Status untuk update.")
                    except: st.error("Gagal koneksi database.")

# =========================================================
# HALAMAN: STATUS
# =========================================================
elif selected == "Status":
    render_header()
    st.markdown("### 🔍 Lacak Laporan")
    
    c_input, c_btn = st.columns([3, 1])
    with c_input:
        npm_cari = st.text_input("Masukkan NPM", placeholder="2117xxx", label_visibility="collapsed")
    with c_btn:
        cari = st.button("Cari")
        
    if cari and npm_cari:
        if sheet:
            try:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                df['NPM'] = df['NPM'].astype(str)
                hasil = df[df['NPM'] == npm_cari]
                
                if not hasil.empty:
                    for idx, row in hasil.iterrows():
                        st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:15px; border-left:5px solid #2563eb; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                            <small>{row['Waktu Lapor']}</small>
                            <h4 style="margin:5px 0;">{row['Kategori Masalah']}</h4>
                            <p style="font-size:14px;">"{row['Detail Keluhan']}"</p>
                            <span style="background:#eff6ff; color:#2563eb; padding:3px 10px; border-radius:10px; font-size:12px; font-weight:bold;">{row['Status']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Belum ada laporan dengan NPM tersebut.")
            except: st.error("Error database.")

# =========================================================
# HALAMAN: SADAS BOT
# =========================================================
elif selected == "SadasBot":
    st.markdown("<h3 style='text-align:center;'>🤖 Sadas Bot</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:13px; color:#64748b; margin-top:-10px;'>Asisten Pintar Mahasiswa Data Science</p>", unsafe_allow_html=True)
    
    # Chat Input (Di Atas biar gampang di HP)
    prompt = st.chat_input("Tanya jadwal, tugas, atau curhat...")
    
    if "messages" not in st.session_state: st.session_state.messages = []

    # Tampilkan Chat
    for msg in st.session_state.messages:
        role = "user" if msg['role'] == "user" else "assistant"
        avatar = "👤" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.write(msg['content'])

    # Proses Chat
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)
            
        # AI Response
        if "GEMINI_API_KEY" in st.secrets:
            try:
                # Auto switch model
                try: model = genai.GenerativeModel('gemini-1.5-flash')
                except: model = genai.GenerativeModel('gemini-pro')
                
                with st.spinner("Bot sedang mengetik..."):
                    res = model.generate_content(f"Kamu Sadas Bot, teman mahasiswa. Jawab pendek & santai: {prompt}")
                    reply = res.text
            except Exception as e: reply = f"Maaf error: {e}"
        else:
            reply = "API Key belum dipasang."
            
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar="🤖"):
            st.write(reply)
            
    if st.button("Bersihkan Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# =========================================================
# HALAMAN: DATA
# =========================================================
elif selected == "Data":
    render_header()
    st.markdown("### 📊 Statistik")
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Total Laporan", len(df))
            c2.metric("Selesai", len(df[df['Status']=='Selesai']))
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Data masih kosong.")

elif selected == "Admin":
    st.markdown("### 🔐 Admin Login")
    pwd = st.text_input("Password", type="password")
    if pwd == "RAHASIA PIKM😭":
        st.success("Login Berhasil! (Fitur Admin disini)")
