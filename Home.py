import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os
import requests
import datetime
import time
import google.generativeai as genai 

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
# 2. MODERN CSS (FIX MENU TERPOTONG & STYLING)
# =========================================================
st.markdown("""
<style>
/* FONT & BASE */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #f8fafc; color: #1e293b; }

/* HIDE UI DEFAULT */
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stSidebar"] {display: none;}

/* --- FIX MENU TERPOTONG --- */
/* Bungkus menu dalam div tetap di atas */
.nav-container {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #e2e8f0;
    padding: 10px 2%;
}

/* Dorong konten ke bawah agar tidak tertutup menu */
.main .block-container {
    padding-top: 100px !important;
    max-width: 1200px;
}

/* CARDS & COMPONENTS */
.glass-card {
    background: #ffffff; border-radius: 20px; padding: 25px;
    border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px; transition: 0.3s;
}
.glass-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-color: #3b82f6; }

/* CHAT STYLING */
.chat-message { padding: 1rem; border-radius: 15px; margin-bottom: 10px; display: flex; align-items: center; }
.chat-message.user { background-color: #e0f2fe; border-left: 5px solid #0284c7; }
.chat-message.bot { background-color: #f1f5f9; border-left: 5px solid #475569; }

/* BUTTONS */
div.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border-radius: 10px;
    font-weight: 700; border: none; transition: 0.3s; width: 100%;
}
.hapus-chat-btn button { background: #ef4444 !important; width: auto !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI GOOGLE SHEETS & GEMINI (LOGIKA ASLI)
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
        return client.open_by_key(ID_SPREADSHEET)
    except: return None

sh = get_spreadsheet()
try: sheet = sh.worksheet("Laporan") if sh else None
except: sheet = None
try: sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None
except: sheet_pengumuman = None

if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

# =========================================================
# 4. MENU NAVIGASI (FIXED AT TOP)
# =========================================================
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house-fill", "exclamation-triangle-fill", "search", "bar-chart-steps", "robot", "shield-lock-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "transparent"},
        "nav-link": {"font-size": "14px", "color": "#64748b", "font-weight": "600"},
        "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
    }
)
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if selected == "Home":
    col_logo1, col_text, col_logo2 = st.columns([1, 4, 1])
    with col_text:
        st.markdown("""<div style="text-align:center;">
            <h1 style="font-size:42px; font-weight:800; background:linear-gradient(90deg, #1e3a8a, #2563eb); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">SAINS DATA CRISIS CENTER</h1>
            <p style="font-size:18px; color:#64748b; margin-top:-10px;">Pusat Analisis dan Respon Cepat Mahasiswa</p>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Pelaporan</h3><p>Saluran resmi pengaduan masalah akademik & fasilitas.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Transparansi</h3><p>Pantau data statistik keluhan mahasiswa secara real-time.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sadas Bot</h3><p>Asisten AI cerdas siap menjawab pertanyaanmu 24/7.</p></div>', unsafe_allow_html=True)

    st.subheader("📰 Informasi Terbaru")
    if sheet_pengumuman:
        try:
            data_info = sheet_pengumuman.get_all_records()
            for item in reversed(data_info):
                tipe = item.get('Tipe', 'Info')
                color = "#ef4444" if tipe == "Urgent" else "#3b82f6"
                st.markdown(f"""<div class="glass-card" style="border-left: 5px solid {color};">
                    <small style="color:#94a3b8;">{item.get('Tanggal', '-')} | <strong>{tipe}</strong></small>
                    <h4>{item.get('Judul', '-')}</h4><p>{item.get('Isi', '-')}</p>
                </div>""", unsafe_allow_html=True)
        except: st.info("Belum ada pengumuman.")

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card" style="max-width:800px; margin:auto;">', unsafe_allow_html=True)
        with st.form("form_lapor_keren", clear_on_submit=True):
            nama = st.text_input("Nama Lengkap")
            col_a, col_b = st.columns(2)
            with col_a: npm = st.text_input("NPM")
            with col_b: jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
            kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
            keluhan = st.text_area("Deskripsi Detail")
            bukti_file = st.file_uploader("Upload Bukti (JPG/PNG)", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("🚀 Kirim Laporan")
            
            if submitted:
                if not keluhan: st.warning("Mohon isi deskripsi.")
                else:
                    with st.spinner("Mengirim laporan..."):
                        waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        link_bukti = "-"
                        if bukti_file:
                            try:
                                res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files={"image": bukti_file.getvalue()})
                                link_bukti = res.json()["data"]["url"]
                            except: pass
                        try:
                            sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                            st.success("✅ Laporan berhasil terkirim!")
                        except: st.error("Database Gagal Terhubung.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Lacak Laporan</h2>", unsafe_allow_html=True)
    col_x, col_y, col_z = st.columns([1,2,1])
    with col_y:
        npm_input = st.text_input("Masukkan NPM Anda")
        if st.button("Cari Data"):
            if sheet:
                data = pd.DataFrame(sheet.get_all_records())
                data['NPM'] = data['NPM'].astype(str)
                hasil = data[data['NPM'] == npm_input]
                if not hasil.empty:
                    for _, row in hasil.iterrows():
                        color = "#d97706" if row['Status'] == "Pending" else "#059669"
                        st.markdown(f"""<div class="glass-card" style="border-left:5px solid {color};">
                            <h4>{row['Kategori Masalah']}</h4><p>{row['Detail Keluhan']}</p>
                            <span style="background:{color}22; color:{color}; padding:4px 10px; border-radius:5px; font-weight:bold;">{row['Status']}</span>
                        </div>""", unsafe_allow_html=True)
                else: st.warning("Data tidak ditemukan.")

# =========================================================
# 8. HALAMAN: SADAS BOT
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot AI</h2>", unsafe_allow_html=True)
    if st.button("🗑️ Hapus Chat", key="del", help="Klik untuk meriset percakapan"):
        st.session_state.messages = []
        st.rerun()

    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role_class}"><b>{msg["role"].upper()}:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Tanyakan sesuatu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Sadas Bot sedang berpikir..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Kamu adalah Sadas Bot dari Prodi Sains Data. Jawab user: {prompt}").text
            except: response = "Maaf, sistem AI sedang sibuk."
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# =========================================================
# 9. HALAMAN: DASHBOARD & ADMIN (TINGGAL COPAS LOGIKA LAMA ANDA)
# =========================================================
elif selected == "Dashboard":
    st.info("Dashboard Analisis Data Real-time")
    # Logika Dashboard Plotly Anda masukkan kembali di sini...

elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Panel Admin</h2>", unsafe_allow_html=True)
    # Logika Login Admin Anda masukkan kembali di sini...
