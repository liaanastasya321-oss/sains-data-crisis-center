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
# 2. GLOBAL CSS (MODERN & MOBILE FRIENDLY)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
.stApp { background: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

/* HERO SECTION */
.hero-container {
    display: flex; flex-direction: row; align-items: center; justify-content: space-between;
    padding: 2rem 1rem; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
    border-radius: 24px; border: 1px solid #dbeafe; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.hero-text { flex: 1; padding-right: 20px; }
.hero-title {
    font-size: 42px; font-weight: 800; margin: 0; line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-subtitle { font-size: 16px; color: #64748b; margin-top: 10px; }
.hero-logo { width: 130px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); }

@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; }
    .hero-text { padding-right: 0; margin-top: 15px; }
    .hero-title { font-size: 28px; }
    .hero-logo { width: 100px; }
}

/* CARDS */
.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; text-align: center; height: 100%; transition: all 0.3s ease; }
.glass-card:hover { transform: translateY(-5px); border-color: #bfdbfe; }

/* CHAT BUBBLES */
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; font-size: 15px; border: 1px solid #e2e8f0; }
.chat-message.user { background-color: #eff6ff; border-color: #bfdbfe; color: #1e3a8a; }
.chat-message.bot { background-color: #ffffff; color: #334155; }

/* FORM & BUTTON */
div.stButton > button { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; border-radius: 10px; font-weight: 700; width: 100%; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & AI SETUP
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
        return client.open_by_key(ID_SPREADSHEET)
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

def panggil_ai(prompt_system, user_input):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"{prompt_system}\n\nUser: {user_input}")
        return response.text.strip()
    except Exception as e:
        return f"Gagal terhubung ke AI. Error: {str(e)}"

# =========================================================
# 4. PDF GENERATOR
# =========================================================
def create_pdf(no_surat, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25)
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12)
    pdf.set_x(0); pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_x(0); pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.set_x(0); pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.set_font("Times", '', 10)
    pdf.set_x(0); pdf.cell(210, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung,", 0, 1, 'C')
    part1, part2 = "Lampung 35131 ", "Email: himasda.radenintan@gmail.com"
    w1, w2 = pdf.get_string_width(part1), pdf.get_string_width(part2)
    pdf.set_x((210 - (w1 + w2)) / 2)
    pdf.set_text_color(0, 0, 0); pdf.cell(w1, 5, part1, 0, 0, 'L')
    pdf.set_text_color(0, 0, 255); pdf.cell(w2, 5, part2, 0, 1, 'L')
    pdf.set_text_color(0, 0, 0); pdf.ln(2); pdf.set_line_width(0.6); pdf.line(30, pdf.get_y(), 185, pdf.get_y())
    pdf.set_line_width(0.2); pdf.line(30, pdf.get_y()+1, 185, pdf.get_y()+1); pdf.ln(6)
    pdf.set_font("Times", '', 12)
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, "1 Berkas", 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1); pdf.ln(4)
    pdf.cell(0, 6, "Kepada Yth.", 0, 1); pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1)
    pdf.set_font("Times", '', 12); pdf.cell(0, 6, "di Tempat", 0, 1); pdf.ln(6)
    pdf.multi_cell(0, 6, isi_surat); pdf.ln(8)
    if pdf.get_y() > 220: pdf.add_page()
    now = datetime.datetime.now()
    bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    pdf.set_x(120); pdf.cell(0, 5, f"Bandar Lampung, {now.day} {bulan[now.month-1]} {now.year}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C'); pdf.ln(25)
    pdf.set_x(120); pdf.set_font("Times", 'BU', 12); pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 5. HALAMAN UTAMA
# =========================================================
selected = option_menu(menu_title=None, options=["Home", "Lapor Masalah", "Cek Status", "Sadas Bot", "Admin"], icons=["house", "exclamation-triangle", "search", "robot", "lock"], orientation="horizontal")

if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f'<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1><p class="hero-subtitle">Pusat Layanan Aspirasi Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Lapor</h3><p>Fasilitas & Akademik.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Pantau</h3><p>Status real-time.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 AI</h3><p>Chatbot 24/7.</p></div>', unsafe_allow_html=True)

elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("form_lapor"):
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        kategori = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan"])
        keluhan = st.text_area("Detail Keluhan")
        submitted = st.form_submit_button("🚀 Kirim Laporan")
        if submitted:
            if not keluhan: st.warning("Isi keluhan!")
            else:
                with st.spinner("Mengirim..."):
                    try:
                        sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y"), nama, npm, jurusan, kategori, keluhan, "Pending", "-"])
                        st.success("Terkirim!")
                    except: st.error("Gagal konek Sheet.")

elif selected == "Cek Status":
    npm_input = st.text_input("Masukkan NPM Anda:")
    if st.button("Cek"):
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        hasil = df[df['NPM'] == npm_input]
        if not hasil.empty:
            for _, r in hasil.iterrows():
                st.info(f"Kategori: {r['Kategori']} | Status: {r['Status']}\n\nLaporan: {r['Detail Keluhan']}")
        else: st.warning("Data tidak ditemukan.")

elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)
    if prompt := st.chat_input("Tanya Sadas..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.spinner("Berpikir..."):
            ans = panggil_ai("Jawab sebagai asisten ramah mahasiswa Sains Data.", prompt)
            st.session_state.msgs.append({"role": "bot", "content": ans})
        st.rerun()

elif selected == "Admin":
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        with st.form("login"):
            if st.text_input("Password Admin", type="password") == "RAHASIA PIKM😭" and st.form_submit_button("Masuk"):
                st.session_state.auth = True; st.rerun()
    else:
        if st.button("Keluar"): st.session_state.auth = False; st.rerun()
        raw = sheet.get_all_values()
        if len(raw) > 1:
            options = [f"{i} | {r[1]}" for i, r in enumerate(raw[1:], 2) if r[0].strip()]
            laporan = st.selectbox("Pilih Laporan:", options)
            idx = int(laporan.split(" | ")[0])
            data = raw[idx-1]
            if st.button("✨ Generate Surat (AI)"):
                with st.spinner("AI Menulis..."):
                    raw_ai = panggil_ai("Buat surat formal. Format: PERIHAL|||TUJUAN|||ISI", f"Nama: {data[1]}, Keluhan: {data[5]}")
                    st.session_state.p, st.session_state.t, st.session_state.i = raw_ai.split("|||") if "|||" in raw_ai else ("Aspirasi", "Ketua Prodi", raw_ai)
            if 'i' in st.session_state:
                per = st.text_input("Perihal", value=st.session_state.get('p',''))
                tuj = st.text_input("Tujuan", value=st.session_state.get('t',''))
                isi = st.text_area("Isi", value=st.session_state.get('i',''), height=300)
                if st.button("🖨️ Cetak PDF"):
                    st.download_button("📥 Download", create_pdf("001/PIKM/2026", per, tuj, isi), f"Surat_{data[1]}.pdf")
