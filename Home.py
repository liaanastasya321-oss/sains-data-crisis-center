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
# 2. GLOBAL CSS (TAMPILAN MODERN & RESPONSIVE)
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
.hero-logo { width: 140px; height: auto; }

@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; }
    .hero-text { padding-right: 0; margin-top: 15px; }
    .hero-title { font-size: 28px; }
}

/* CARDS */
.glass-card { 
    background: #ffffff; border-radius: 16px; padding: 25px; 
    border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
    text-align: center; height: 100%; transition: all 0.3s ease;
}
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; }
.metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; }

/* CHAT AREA - PERBAIKAN TAMPILAN VERTIKAL */
.chat-container { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
.message-box { 
    padding: 15px 20px; border-radius: 15px; max-width: 85%; 
    line-height: 1.6; font-size: 15px; position: relative;
}
.user-msg { 
    align-self: flex-end; background-color: #2563eb; color: white; 
    border-bottom-right-radius: 2px;
}
.bot-msg { 
    align-self: flex-start; background-color: #ffffff; color: #334155; 
    border: 1px solid #e2e8f0; border-bottom-left-radius: 2px;
}

/* BUTTONS */
div.stButton > button { 
    background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; 
    border: none; border-radius: 10px; font-weight: 700; width: 100%;
}
.block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & FUNGSI BANTUAN
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 

def get_spreadsheet():
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
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

# --- FUNGSI PDF GENERATOR ---
def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.set_auto_page_break(auto=True, margin=25); pdf.add_page()
    pdf.set_y(20); pdf.set_font("Times", 'B', 12); pdf.set_x(0); pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.ln(10); pdf.set_font("Times", '', 12); pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1); pdf.ln(5)
    pdf.cell(0, 6, "Kepada Yth.", 0, 1); pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1); pdf.ln(5); pdf.set_font("Times", '', 12); pdf.multi_cell(0, 6, isi_surat)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(None, ["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"], icons=["house", "exclamation-triangle", "search", "bar-chart", "robot", "lock"], orientation="horizontal")

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f'<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1><p class="hero-subtitle">Pusat Layanan Aspirasi Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Lapor</h3><p>Masalah Fasilitas & Akademik</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Dashboard</h3><p>Statistik Real-time</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sadas Bot</h3><p>AI Assistant 24/7</p></div>', unsafe_allow_html=True)

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("form_lapor", clear_on_submit=True):
        nama = st.text_input("Nama"); npm = st.text_input("NPM")
        kat = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Lainnya"])
        kel = st.text_area("Keluhan")
        if st.form_submit_button("Kirim"):
            sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y"), nama, npm, "Sains Data", kat, kel, "Pending", "-"])
            st.success("Terkirim!")

# =========================================================
# 7. HALAMAN: DASHBOARD
# =========================================================
elif selected == "Dashboard":
    data = pd.DataFrame(sheet.get_all_records())
    if not data.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Laporan", len(data))
        c2.metric("Pending", len(data[data['Status'] == 'Pending']))
        c3.metric("Selesai", len(data[data['Status'] == 'Selesai']))
        st.plotly_chart(go.Figure(data=[go.Pie(labels=data['Kategori'].value_counts().index, values=data['Kategori'].value_counts().values)]), use_container_width=True)

# =========================================================
# 8. HALAMAN: SADAS BOT (FIX: VERTICAL & MEMORY)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    
    # Inisialisasi History jika belum ada
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [] # Memori untuk AI
    if "display_history" not in st.session_state:
        st.session_state.display_history = [] # Memori untuk tampilan

    # Tombol Hapus Chat
    col_del1, col_del2 = st.columns([5, 1])
    with col_del2:
        if st.button("🗑️ Hapus"):
            st.session_state.chat_history = []
            st.session_state.display_history = []
            st.rerun()

    # Tampilan Chat (Vertikal)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.display_history:
        cls = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f'<div class="message-box {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Input Chat
    if prompt := st.chat_input("Ketik pesanmu di sini..."):
        # Simpan ke display
        st.session_state.display_history.append({"role": "user", "content": prompt})
        
        with st.spinner("Sadas sedang mengetik..."):
            try:
                # Load Model
                model = genai.GenerativeModel('gemini-pro')
                
                # Start chat with history
                chat = model.start_chat(history=st.session_state.chat_history)
                response = chat.send_message(prompt)
                
                # Simpan history asli untuk konteks AI
                st.session_state.chat_history.append({"role": "user", "parts": [prompt]})
                st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
                
                # Simpan ke display
                st.session_state.display_history.append({"role": "bot", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"Maaf Lia, AI-nya lagi sibuk nih. Coba lagi ya! (Error: {str(e)})")

# =========================================================
# 9. HALAMAN: ADMIN (GENERATE SURAT)
# =========================================================
elif selected == "Admin":
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        with st.form("login"):
            if st.text_input("Password", type="password") == "RAHASIA PIKM😭" and st.form_submit_button("Login"):
                st.session_state.auth = True; st.rerun()
    else:
        raw = sheet.get_all_values()
        if len(raw) > 1:
            options = [f"{i} | {r[1]}" for i, r in enumerate(raw[1:], 2) if r[0].strip()]
            sel = st.selectbox("Pilih Laporan:", options)
            idx = int(sel.split(" | ")[0]); row_data = raw[idx-1]
            
            if st.button("✨ Buat Surat Otomatis"):
                model = genai.GenerativeModel('gemini-pro')
                p_surat = f"Buat draf surat formal dari Himpunan Mahasiswa Sains Data UIN RIL. Mahasiswa: {row_data[1]}, Keluhan: {row_data[5]}. Format: PERIHAL|||TUJUAN|||ISI"
                res = model.generate_content(p_surat).text
                if "|||" in res:
                    parts = res.split("|||")
                    st.session_state.dr_p, st.session_state.dr_t, st.session_state.dr_i = parts[0], parts[1], parts[2]
            
            if 'dr_i' in st.session_state:
                p = st.text_input("Perihal", value=st.session_state.dr_p)
                t = st.text_input("Tujuan", value=st.session_state.dr_t)
                isi = st.text_area("Isi", value=st.session_state.dr_i, height=250)
                if st.button("Cetak PDF"):
                    st.download_button("Download", create_pdf("001/PIKM/2026", "1 Berkas", p, t, isi), "Surat.pdf")
