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
# 2. GLOBAL CSS (TAMPILAN MODERN & MOBILE FRIENDLY)
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
    border-radius: 24px; border: 1px solid #dbeafe; margin-bottom: 30px;
}
.hero-text { flex: 1; padding-right: 20px; }
.hero-title {
    font-size: 42px; font-weight: 800; margin: 0; line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-subtitle { font-size: 16px; color: #64748b; margin-top: 10px; }
.hero-logo { width: 140px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); }

@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; }
    .hero-text { padding-right: 0; margin-top: 15px; }
    .hero-title { font-size: 28px; }
    .hero-logo { width: 100px; }
}

/* CARDS */
.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; text-align: center; height: 100%; transition: all 0.3s ease; }
.glass-card:hover { transform: translateY(-5px); border-color: #bfdbfe; }

/* INPUT & BUTTON */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 10px;
}
div.stButton > button { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; border-radius: 10px; font-weight: 700; width: 100%; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI GOOGLE SHEETS
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

# KONFIGURASI AI (GEMINI-PRO)
if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

# --- FUNGSI AI UNTUK BUAT SURAT (GEMINI-PRO) ---
def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Error", "Admin", "API Key tidak ditemukan di Secrets."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Kamu adalah Sekretaris Himpunan Mahasiswa Sains Data.
        Buatkan draft surat formal untuk menindaklanjuti keluhan mahasiswa.
        Data Mahasiswa: Nama {nama}, Kategori {kategori}, Keluhan "{keluhan}".
        
        WAJIB gunakan format output seperti ini (pisahkan dengan |||):
        PERIHAL_SURAT|||TUJUAN_SURAT|||ISI_SURAT_LENGKAP
        
        Isi surat harus formal, mulai dengan Assalamu'alaikum, inti keluhan yang diperhalus, dan penutup.
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        parts = text.split("|||")
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        else:
            return "Penyampaian Aspirasi", "Ketua Program Studi", text
    except Exception as e:
        return "Error", "Admin", f"Gagal membuat surat otomatis: {str(e)}"

# --- FUNGSI PDF GENERATOR ---
def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25) 
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    
    # KOP SURAT
    if os.path.exists("logo_him.png"):
        pdf.image("logo_him.png", x=163, y=20, w=22)
    # Foto logo UIN bisa Lia tambahkan di folder jika mau ada logo kiri
    
    pdf.set_y(20) 
    pdf.set_font("Times", 'B', 12) 
    pdf.set_x(0) 
    pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    
    pdf.set_font("Times", '', 10) 
    pdf.cell(210, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung,", 0, 1, 'C')
    
    part1 = "Lampung 35131 "
    part2 = "Email: himasda.radenintan@gmail.com"
    w1, w2 = pdf.get_string_width(part1), pdf.get_string_width(part2)
    start_x = (210 - (w1 + w2)) / 2
    pdf.set_x(start_x)
    pdf.set_text_color(0, 0, 0); pdf.cell(w1, 5, part1, 0, 0, 'L')
    pdf.set_text_color(0, 0, 255); pdf.cell(w2, 5, part2, 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(2); pdf.set_line_width(0.6); pdf.line(30, pdf.get_y(), 185, pdf.get_y())
    pdf.set_line_width(0.2); pdf.line(30, pdf.get_y()+1, 185, pdf.get_y()+1)
    pdf.ln(6)

    # ISI
    pdf.set_font("Times", '', 12) 
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, lampiran, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(4)
    pdf.cell(0, 6, "Kepada Yth.", 0, 1)
    pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1); pdf.set_font("Times", '', 12)
    pdf.cell(0, 6, "di Tempat", 0, 1); pdf.ln(6) 
    pdf.multi_cell(0, 6, isi_surat); pdf.ln(8) 

    if pdf.get_y() > 220: pdf.add_page()
    now = datetime.datetime.now()
    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    pdf.set_x(120); pdf.cell(0, 5, f"Bandar Lampung, {now.day} {bulan_indo[now.month-1]} {now.year}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C'); pdf.set_x(120); pdf.cell(0, 5, "Ketua Departemen PIKM", 0, 1, 'C')
    pdf.ln(25); pdf.set_x(120); pdf.set_font("Times", 'BU', 12); pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    pdf.set_x(120); pdf.set_font("Times", '', 12); pdf.cell(0, 5, "NPM. 247103001", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU UTAMA
# =========================================================
selected = option_menu(menu_title=None, options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"], icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"], orientation="horizontal")

if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f'<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1><p class="hero-subtitle">Pusat Layanan Aspirasi dan Respon Cepat Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3 style="color:#2563eb;">📢 Pelaporan</h3><p>Saluran resmi pengaduan masalah.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3 style="color:#0891b2;">📊 Transparansi</h3><p>Pantau statistik real-time.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Sadas Bot</h3><p>Asisten AI cerdas 24/7.</p></div>', unsafe_allow_html=True)

elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Tanyakan sesuatu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner("Sadas Bot sedang berpikir..."):
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(st.session_state.messages[-1]["content"])
                st.session_state.messages.append({"role": "bot", "content": response.text})
                st.rerun()
            except:
                st.error("Gagal terhubung ke AI.")

elif selected == "Admin":
    if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
    if not st.session_state['is_logged_in']:
        with st.form("login"):
            if st.text_input("Password", type="password") == "RAHASIA PIKM😭" and st.form_submit_button("Login"):
                st.session_state['is_logged_in'] = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state['is_logged_in'] = False; st.rerun()
        if sheet:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                pilihan = [f"{i} | {r[1]}" for i, r in enumerate(raw_data[1:], 2) if r[0].strip()]
                laporan = st.selectbox("Pilih Laporan:", pilihan)
                idx = int(laporan.split(" | ")[0])
                data = raw_data[idx-1]
                
                st.write(f"**Nama Pelapor:** {data[1]} | **Isi:** {data[5]}")
                
                if st.button("✨ Buat Draft Surat Otomatis (AI)"):
                    p, t, i = draft_surat_with_ai(data[4], data[5], data[1])
                    st.session_state.d_p, st.session_state.d_t, st.session_state.d_i = p, t, i
                
                if 'd_i' in st.session_state:
                    per = st.text_input("Perihal", value=st.session_state.d_p)
                    tuj = st.text_input("Tujuan", value=st.session_state.d_t)
                    isi = st.text_area("Isi Surat", value=st.session_state.d_i, height=300)
                    if st.button("🖨️ Cetak PDF"):
                        pdf = create_pdf("001/PIKM/2026", "1 Berkas", per, tuj, isi)
                        st.download_button("📥 Download", pdf, f"Surat_{data[1]}.pdf", "application/pdf")

# (Note: Tambahkan logika halaman lainnya seperti Lapor Masalah dsb seperti biasa)
