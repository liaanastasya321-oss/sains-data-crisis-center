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
# 2. GLOBAL CSS (MODERN & PROFESSIONAL UI)
# =========================================================
st.markdown("""
<style>
/* --- 1. SETUP DASAR --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

.stApp { 
    background: #f8fafc; 
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

/* --- 2. HEADER HERO SECTION --- */
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
.hero-logo:hover { transform: scale(1.05) rotate(2deg); }

@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; padding: 1.5rem; }
    .hero-text { padding-right: 0; margin-top: 15px; }
    .hero-title { font-size: 28px; }
    .hero-logo { width: 100px; }
}

/* --- 3. CARDS --- */
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
.glass-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); border-color: #bfdbfe; }
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
.metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

/* --- 4. FORM & BUTTONS --- */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important; 
    border: 1px solid #cbd5e1 !important; 
    color: #1e293b !important; 
    border-radius: 10px;
    padding: 10px;
}
div.stButton > button { 
    background: linear-gradient(90deg, #2563eb, #1d4ed8); 
    color: white; 
    border: none; 
    padding: 12px 24px; 
    border-radius: 10px; 
    font-weight: 700; 
    width: 100%;
}

/* --- 5. CHAT BUBBLE --- */
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; line-height: 1.5; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; justify-content: flex-end; text-align: right; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }

iframe[title="streamlit_option_menu.option_menu"] { width: 100%; background: transparent; }
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

# --- FUNGSI AUTO-DETECT MODEL ---
def get_available_gen_model():
    if "GEMINI_API_KEY" not in st.secrets: return None
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Mencari model yang mendukung generateContent
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name # Mengembalikan nama model pertama yang aktif
    except:
        # Fallback manual jika list_models gagal
        return 'gemini-1.5-flash'
    return None

# --- FUNGSI AI DRAFTER ---
def draft_surat_with_ai(kategori, keluhan, nama):
    perihal_backup = "Tindak Lanjut Keluhan Mahasiswa"
    tujuan_backup = "Ketua Program Studi Sains Data"
    isi_backup = f"Laporan dari {nama} terkait {kategori}: {keluhan}"
    
    model_name = get_available_gen_model()
    if model_name:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"Buat draft surat formal PIKM. Nama: {nama}, Kategori: {kategori}, Keluhan: {keluhan}. Format: PERIHAL|||TUJUAN|||ISI"
            response = model.generate_content(prompt)
            parts = response.text.split("|||")
            if len(parts) >= 3:
                return parts[0].strip(), parts[1].strip(), parts[2].strip()
        except: pass
    return perihal_backup, tujuan_backup, isi_backup

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25) 
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    if os.path.exists("logo_uin.png"): pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12); pdf.set_x(0) 
    pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_font("Times", '', 12); pdf.ln(10)
    pdf.multi_cell(0, 6, isi_surat)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0,
    orientation="horizontal",
    styles={"container": {"background-color": "#ffffff"}, "nav-link-selected": {"background-color": "#2563eb"}}
)

# =========================================================
# 5 - 8. HALAMAN HOME, LAPOR, CEK, DASHBOARD (TETAP SAMA)
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f'<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1><p class="hero-subtitle">Pusat Layanan Aspirasi Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Pelaporan</h3></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Transparansi</h3></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sadas Bot</h3></div>', unsafe_allow_html=True)

elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("lapor"):
        nama = st.text_input("Nama")
        npm = st.text_input("NPM")
        kat = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan"])
        kel = st.text_area("Keluhan")
        if st.form_submit_button("Kirim") and sheet:
            sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y"), nama, npm, "Sains Data", kat, kel, "Pending", "-"])
            st.success("Terkirim!")

elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Lacak Laporan</h2>", unsafe_allow_html=True)
    npm_cek = st.text_input("NPM kamu")
    if st.button("Cek") and sheet:
        df = pd.DataFrame(sheet.get_all_records())
        res = df[df['NPM'].astype(str) == npm_cek]
        if not res.empty: st.dataframe(res)
        else: st.warning("Data tidak ada.")

elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure(data=[go.Pie(labels=df['Kategori Masalah'].value_counts().index, values=df['Kategori Masalah'].value_counts().values, hole=.5)])
                st.plotly_chart(fig)
            with c2:
                st.metric("Total Laporan", len(df))
            st.dataframe(df)

# =========================================================
# 9. HALAMAN: SADAS BOT (ADAPTIVE MODEL VERSION)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.markdown("<h2 style='margin:0;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b;'>Asisten Otomatis yang Menyesuaikan Sistem</p>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🗑️ Hapus Chat"):
            st.session_state.messages = []
            st.rerun()

    st.write("---")
    if "messages" not in st.session_state: st.session_state.messages = []

    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Tanya apa saja..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # MENDETEKSI MODEL YANG AKTIF SECARA OTOMATIS
        active_model = get_available_gen_model()
        
        if active_model:
            try:
                model = genai.GenerativeModel(active_model)
                with st.spinner(f"Sadas Bot ({active_model.split('/')[-1]}) sedang mengetik..."):
                    res = model.generate_content(f"Kamu asisten HMSD. Jawab santai: {prompt}")
                    ans = res.text
            except Exception as e:
                ans = f"🙏 Maaf, model {active_model} sedang sibuk. Error: {str(e)}"
        else:
            ans = "⚠️ API Key tidak valid atau tidak ada model yang tersedia."

        st.session_state.messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"): st.markdown(ans)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 10. HALAMAN: ADMIN
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Admin Area</h2>", unsafe_allow_html=True)
    if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
    if not st.session_state['is_logged_in']:
        with st.form("login"):
            if st.form_submit_button("Login") and st.text_input("Password", type="password") == "RAHASIA PIKM😭":
                st.session_state['is_logged_in'] = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state['is_logged_in'] = False; st.rerun()
        if sheet: st.dataframe(pd.DataFrame(sheet.get_all_records()))
