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
import base64
import google.generativeai as genai
from fpdf import FPDF

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
# 2. GLOBAL CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

.stApp { 
    background: #f8fafc; 
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

.hero-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
    border-radius: 24px;
    border: 1px solid #dbeafe;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.hero-text { flex: 1; padding-right: 20px; }
.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}
.hero-subtitle { font-size: 16px; color: #64748b; margin-top: 10px; font-weight: 500; }
.hero-logo { width: 140px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); transition: transform 0.3s ease; }

.glass-card { 
    background: #ffffff; 
    border-radius: 16px; 
    padding: 25px; 
    border: 1px solid #e2e8f0; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
    text-align: center; 
    height: 100%; 
    transition: all 0.3s ease;
}
.glass-card:hover { transform: translateY(-5px); border-color: #bfdbfe; }
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
.metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; line-height: 1.5; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; justify-content: flex-end; text-align: right; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }

.block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & FUNGSI BANTUAN
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b" 
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

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
sheet = None
sheet_pengumuman = None

if sh:
    try: sheet = sh.worksheet("Laporan")
    except: 
        try: sheet = sh.get_worksheet(0)
        except: pass
    try: sheet_pengumuman = sh.worksheet("Pengumuman")
    except: pass

if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

def get_available_model():
    if "GEMINI_API_KEY" not in st.secrets: return "gemini-pro"
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return "gemini-pro"
    return "gemini-pro"

def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" in st.secrets:
        try:
            model = genai.GenerativeModel(get_available_model())
            prompt = f"Buatkan draf surat formal dari PIKM UIN RIL. Pelapor: {nama}, Masalah: {kategori}, Keluhan: {keluhan}. Format: PERIHAL|||TUJUAN|||ISI"
            response = model.generate_content(prompt)
            parts = response.text.split("|||")
            if len(parts) >= 3: return parts[0].strip(), parts[1].strip(), parts[2].strip()
        except: pass 
    return "Tindak Lanjut", "Ketua Prodi", "Detail laporan..."

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 10, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_font("Times", '', 12)
    pdf.multi_cell(0, 10, f"Nomor: {no_surat}\nPerihal: {perihal}\n\nKepada: {tujuan}\n\n{isi_surat}")
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sasda Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0,
    orientation="horizontal",
    styles={"nav-link-selected": {"background-color": "#2563eb"}}
)

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-text">
            <h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1>
            <p class="hero-subtitle">Pusat Layanan Aspirasi, Analisis Data, dan Respon Cepat Mahasiswa Sains Data.</p>
            <p style="color: #475569; font-size: 13px; font-weight: 600; margin-top: 5px;">
                🕒 Pelayanan Admin PIKM: 07.00 - 14.00 WIB
            </p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Pelaporan</h3><p>Aspirasi fasilitas & akademik.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Transparansi</h3><p>Pantau status real-time.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sasda Bot</h3><p>Asisten AI 24/7.</p></div>', unsafe_allow_html=True)

    if sheet_pengumuman:
        st.write("---")
        st.subheader("📰 Informasi Terbaru")
        try:
            data_info = sheet_pengumuman.get_all_records()
            for item in reversed(data_info):
                st.info(f"**{item.get('Judul')}** ({item.get('Tanggal')})\n\n{item.get('Isi')}")
        except: pass

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("form_lapor"):
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        kategori = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        keluhan = st.text_area("Deskripsi")
        bukti = st.file_uploader("Upload Bukti", type=["png", "jpg"])
        submit = st.form_submit_button("Kirim Laporan")
        
        if submit and sheet:
            waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", "-"])
            st.success("Laporan terkirim!")

# =========================================================
# 7. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status</h2>", unsafe_allow_html=True)
    npm_cek = st.text_input("Masukkan NPM")
    if st.button("Cek") and sheet:
        data = pd.DataFrame(sheet.get_all_records())
        hasil = data[data['NPM'].astype(str) == npm_cek]
        if not hasil.empty: st.write(hasil[['Waktu Lapor', 'Kategori Masalah', 'Status']])
        else: st.warning("Data tidak ditemukan.")

# =========================================================
# 8. HALAMAN: DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            st.metric("Total Laporan", len(df))
            fig = go.Figure(data=[go.Pie(labels=df['Status'].value_counts().index, values=df['Status'].value_counts().values)])
            st.plotly_chart(fig)

# =========================================================
# 9. HALAMAN: SASDA BOT
# =========================================================
elif selected == "Sasda Bot":
    st.markdown("<h2>🤖 Sasda Bot</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Ada yang bisa Sasda bantu?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        response = "Maaf, AI sedang offline."
        if "GEMINI_API_KEY" in st.secrets:
            try:
                model = genai.GenerativeModel(get_available_model())
                ai_res = model.generate_content(f"Kamu adalah Sasda Bot. User: {prompt}")
                response = ai_res.text
            except: pass
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

# =========================================================
# 10. HALAMAN: ADMIN
# =========================================================
elif selected == "Admin":
    if st.text_input("Password", type="password") == "RAHASIA PIKM😭":
        st.success("Login Berhasil")
        if sheet:
            df = pd.DataFrame(sheet.get_all_records())
            st.dataframe(df)
