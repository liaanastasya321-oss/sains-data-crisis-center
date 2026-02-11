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
# 2. GLOBAL CSS (FIXED TOP SPACING & MODERN UI)
# =========================================================
st.markdown("""
<style>
/* --- 1. SETUP DASAR & FIX TOP SPACE --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

/* Menghilangkan padding bawaan Streamlit agar menu naik ke atas */
.block-container { 
    padding-top: 1rem !important; 
    padding-bottom: 5rem !important; 
    max-width: 1200px; 
}

/* Menghilangkan header default Streamlit */
[data-testid="stHeader"] {
    display: none !important;
}

.stApp { 
    background: #f8fafc; 
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

#MainMenu, footer { display: none !important; }

/* --- 2. HEADER HERO SECTION --- */
.hero-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 2.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%);
    border-radius: 24px;
    border: 1px solid #e2e8f0;
    margin-bottom: 30px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 16px;
    color: #64748b;
    margin-top: 10px;
}

.hero-logo {
    width: 130px;
    transition: transform 0.3s ease;
}

.hero-logo:hover {
    transform: scale(1.05);
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
.glass-card:hover {
    transform: translateY(-5px);
    border-color: #3b82f6;
}

.metric-value { font-size: 36px; font-weight: 800; color: #1e3a8a; }
.metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; }

/* --- 4. ANNOUNCEMENT CARDS --- */
.announce-card {
    background: white;
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid #f1f5f9;
}

/* --- 5. CHAT BUBBLE --- */
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; font-size: 15px; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; text-align: right; margin-left: auto; width: fit-content; max-width: 80%; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; width: fit-content; max-width: 80%; }

/* Mobile Tweaks */
@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; padding: 1.5rem; }
    .hero-title { font-size: 28px; }
    .hero-logo { width: 100px; margin-bottom: 15px; }
}
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
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except: return "gemini-pro"
    return "gemini-pro"

def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" in st.secrets:
        try:
            model_active = get_available_model()
            model = genai.GenerativeModel(model_active) 
            prompt = f"Buatkan draf surat formal HMSD UIN Raden Intan. Pelapor: {nama}, Kategori: {kategori}, Keluhan: {keluhan}. Output: PERIHAL|||TUJUAN|||ISI"
            response = model.generate_content(prompt)
            parts = response.text.strip().split("|||")
            if len(parts) >= 3: return parts[0].strip(), parts[1].strip(), parts[2].strip()
        except: pass 
    return "Tindak Lanjut Laporan", "Ketua Prodi Sains Data", f"Menyampaikan laporan dari {nama}."

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25)
    pdf.add_page()
    if os.path.exists("logo_uin.png"): pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(0, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(0, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.ln(10); pdf.set_font("Times", '', 12)
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(5); pdf.cell(0, 6, "Kepada Yth.", 0, 1); pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 6, tujuan, 0, 1); pdf.set_font("Times", '', 12); pdf.cell(0, 6, "di Tempat", 0, 1)
    pdf.ln(5); pdf.multi_cell(0, 6, isi_surat)
    pdf.ln(20); pdf.set_x(120); pdf.cell(0, 5, "Bandar Lampung, " + str(datetime.datetime.now().day), 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C'); pdf.ln(15)
    pdf.set_x(120); pdf.set_font("Times", 'BU', 12); pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI (LANGSUNG DI ATAS)
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house", "megaphone", "search", "bar-chart", "robot", "lock"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#ffffff", "border-radius": "12px", "border": "1px solid #e2e8f0"},
        "nav-link": {"font-size": "13px", "color": "#64748b", "padding": "10px"}, 
        "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
    }
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
            <p class="hero-subtitle">Platform resmi pengaduan dan analisis mahasiswa PIKM.</p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb;">📢 Lapor</h3><p style="color:#64748b;">Sampaikan keluhan fasilitas & akademik.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2;">📊 Pantau</h3><p style="color:#64748b;">Lihat statistik laporan masuk.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Bot</h3><p style="color:#64748b;">Tanya Sadas Bot untuk info cepat.</p></div>""", unsafe_allow_html=True)

    st.write("### 📰 Pengumuman")
    if sheet_pengumuman:
        try:
            items = sheet_pengumuman.get_all_records()
            for item in reversed(items):
                t = item.get('Tipe', 'Info')
                c = "#ef4444" if t == "Urgent" else "#3b82f6"
                st.markdown(f'<div class="announce-card" style="border-left: 5px solid {c};"><strong>{item.get("Judul")}</strong><br><small>{item.get("Tanggal")}</small><p>{item.get("Isi")}</p></div>', unsafe_allow_html=True)
        except: st.info("Belum ada pengumuman.")

# =========================================================
# 6. LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown('<div class="glass-card" style="text-align:left;">', unsafe_allow_html=True)
        with st.form("lapor_form", clear_on_submit=True):
            nama = st.text_input("Nama Lengkap")
            npm = st.text_input("NPM")
            prodi = st.selectbox("Prodi", ["Sains Data", "Lainnya"])
            kat = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Lainnya"])
            det = st.text_area("Detail Keluhan")
            up = st.file_uploader("Bukti (Opsional)", type=["jpg","png"])
            if st.form_submit_button("🚀 Kirim Laporan"):
                if det and nama:
                    waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    if sheet:
                        sheet.append_row([waktu, nama, npm, prodi, kat, det, "Pending", "-"])
                        st.success("Laporan terkirim!")
                else: st.warning("Isi semua bidang!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7. CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status</h2>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        npm_input = st.text_input("Masukkan NPM")
        if st.button("Lacak") and npm_input:
            if sheet:
                df = pd.DataFrame(sheet.get_all_records())
                res = df[df['NPM'].astype(str) == npm_input]
                if not res.empty:
                    for _, r in res.iterrows():
                        st.markdown(f'<div class="glass-card" style="text-align:left; margin-bottom:10px;"><strong>{r["Kategori Masalah"]}</strong><br><span style="color:blue;">{r["Status"]}</span><p>{r["Detail Keluhan"]}</p></div>', unsafe_allow_html=True)
                else: st.error("NPM tidak ditemukan.")

# =========================================================
# 8. DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="glass-card"><div class="metric-value" style="color:orange;">{len(df[df["Status"]=="Pending"])}</div><div class="metric-label">Pending</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="glass-card"><div class="metric-value" style="color:green;">{len(df[df["Status"]=="Selesai"])}</div><div class="metric-label">Selesai</div></div>', unsafe_allow_html=True)
            
            pie = df['Kategori Masalah'].value_counts()
            fig = go.Figure(data=[go.Pie(labels=pie.index, values=pie.values, hole=.3)])
            st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 9. SADAS BOT
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Tanya sesuatu..."):
        st.session_state.messages.append({"role": "user", "content": p})
        st.rerun()

# =========================================================
# 10. ADMIN
# =========================================================
elif selected == "Admin":
    if not st.session_state.get('logged_in'):
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if pwd == "RAHASIA PIKM😭":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.subheader("Database Laporan")
        if sheet:
            df = pd.DataFrame(sheet.get_all_records())
            st.dataframe(df)
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()
