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
.stApp { background: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.hero-container {
    display: flex; flex-direction: row; align-items: center; justify-content: space-between;
    padding: 2rem 1rem; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
    border-radius: 24px; border: 1px solid #dbeafe; margin-bottom: 30px;
}
.hero-title {
    font-size: 42px; font-weight: 800; margin: 0; line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-subtitle { font-size: 16px; color: #64748b; margin-top: 10px; font-weight: 500; }
.hero-logo { width: 140px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); }
.glass-card { 
    background: #ffffff; border-radius: 16px; padding: 25px; 
    border: 1px solid #e2e8f0; text-align: center; height: 100%; transition: 0.3s;
}
.glass-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; }
.chat-message.user { background-color: #eff6ff; color: #1e3a8a; justify-content: flex-end; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }
@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; }
    .hero-title { font-size: 28px; }
    .hero-logo { width: 100px; }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & FUNGSI (Sama seperti sebelumnya)
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g"
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b"
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_spreadsheet():
    try:
        if "google_credentials" in st.secrets:
            creds = Credentials.from_service_account_info(json.loads(st.secrets["google_credentials"]), scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else: return None
        return gspread.authorize(creds).open_by_key(ID_SPREADSHEET)
    except: return None

sh = get_spreadsheet()
sheet = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def get_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return "gemini-pro"
    return "gemini-pro"

def draft_surat_with_ai(kategori, keluhan, nama):
    try:
        model = genai.GenerativeModel(get_available_model())
        prompt = f"Buatkan draf surat formal PIKM UIN RIL. Pelapor: {nama}, Kategori: {kategori}, Keluhan: {keluhan}. Format: PERIHAL|||TUJUAN|||ISI"
        parts = model.generate_content(prompt).text.split("|||")
        return parts[0], parts[1], parts[2]
    except: return "Tindak Lanjut", "Ketua Prodi", f"Laporan dari {nama}."

def create_pdf(no, lamp, per, tuj, isi):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 10, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_font("Times", '', 12); pdf.ln(10)
    pdf.multi_cell(0, 6, f"Nomor: {no}\nPerihal: {per}\n\nKepada Yth. {tuj}\n\n{isi}")
    pdf.ln(20); pdf.cell(0, 10, "LIA ANASTASYA", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sasda Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    orientation="horizontal"
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
            <p style="color: #475569; font-size: 13px; font-weight: 600; margin-top: 10px; border-top: 1px solid #e2e8f0; display: inline-block; padding-top: 5px;">
                🕒 Pelayanan Admin PIKM: 07.00 - 14.00 WIB
            </p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Pelaporan</h3><p>Aspirasi fasilitas & akademik.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Transparansi</h3><p>Pantau status real-time.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sasda Bot</h3><p>Asisten AI cerdas 24/7.</p></div>', unsafe_allow_html=True)

# =========================================================
# 6-8. HALAMAN: LAPOR, STATUS, DASHBOARD (Sama seperti kodemu)
# =========================================================
elif selected == "Lapor Masalah":
    st.title("📝 Form Pengaduan")
    with st.form("lapor_form"):
        nama = st.text_input("Nama"); npm = st.text_input("NPM")
        kat = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Lainnya"])
        msg = st.text_area("Keluhan")
        if st.form_submit_button("Kirim"):
            if sheet:
                sheet.append_row([str(datetime.datetime.now()), nama, npm, "Sains Data", kat, msg, "Pending", "-"])
                st.success("Laporan terkirim!")

elif selected == "Cek Status":
    npm_cek = st.text_input("Cek NPM")
    if st.button("Lacak") and sheet:
        df = pd.DataFrame(sheet.get_all_records())
        res = df[df['NPM'].astype(str) == npm_cek]
        st.write(res) if not res.empty else st.warning("Data tidak ditemukan.")

elif selected == "Dashboard":
    st.title("📊 Dashboard")
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        st.metric("Total Laporan", len(df))
        st.bar_chart(df['Status'].value_counts())

# =========================================================
# 9. HALAMAN: SASDA BOT
# =========================================================
elif selected == "Sasda Bot":
    st.title("🤖 Sasda Bot")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Tanya Sasda Bot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        try:
            model = genai.GenerativeModel(get_available_model())
            hist = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=hist)
            response = chat.send_message(f"Kamu adalah Sasda Bot PIKM Sains Data UIN RIL. Jawab santai. User: {prompt}").text
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"): st.markdown(response)
        except: st.error("AI sedang sibuk.")

# =========================================================
# 10. HALAMAN: ADMIN
# =========================================================
elif selected == "Admin":
    pwd = st.text_input("Password", type="password")
    if pwd == "RAHASIA PIKM😭":
        st.success("Welcome, Admin!")
        if sheet:
            st.dataframe(pd.DataFrame(sheet.get_all_records()))
