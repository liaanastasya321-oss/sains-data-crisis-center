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
# 2. MODERN & PREMIUM CSS (Laptop & Mobile Optimized)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp { background-color: #f1f5f9; font-family: 'Plus Jakarta Sans', sans-serif; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }

.main-container { max-width: 1200px; margin: auto; padding: 20px; }

.hero-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    border-radius: 30px; padding: 40px; color: white;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 30px; box-shadow: 0 20px 25px -5px rgba(30, 58, 138, 0.2);
}
.hero-title { font-size: 48px; font-weight: 800; line-height: 1.1; margin: 0; }
.hero-logo-img { width: 150px; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.2)); }

.feature-card {
    background: white; padding: 30px; border-radius: 24px; border: 1px solid #e2e8f0;
    text-align: center; transition: all 0.4s ease; height: 100%;
}
.feature-card:hover { transform: translateY(-10px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); }

.stat-box {
    background: white; padding: 25px; border-radius: 20px;
    border-left: 6px solid #2563eb; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.stat-val { font-size: 32px; font-weight: 800; color: #1e293b; }
.stat-lbl { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; }

.chat-row { display: flex; margin-bottom: 15px; width: 100%; }
.chat-row.user { justify-content: flex-end; }
.chat-bubble { max-width: 80%; padding: 12px 18px; border-radius: 20px; font-size: 15px; }
.chat-bubble.bot { background: white; border: 1px solid #e2e8f0; color: #334155; border-bottom-left-radius: 4px; }
.chat-bubble.user { background: #2563eb; color: white; border-bottom-right-radius: 4px; }

@media (max-width: 768px) {
    .hero-card { flex-direction: column-reverse; text-align: center; padding: 30px 20px; }
    .hero-title { font-size: 32px; }
    .hero-logo-img { width: 100px; margin-bottom: 20px; }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & ENGINE
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b" 

def get_spreadsheet():
    try:
        if "google_credentials" in st.secrets:
            creds = Credentials.from_service_account_info(json.loads(st.secrets["google_credentials"]), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
            return gspread.authorize(creds).open_by_key(ID_SPREADSHEET)
    except: return None

sh = get_spreadsheet()
sheet = sh.worksheet("Laporan") if sh else None
sheet_info = sh.worksheet("Pengumuman") if sh else None

def get_active_model():
    if "GEMINI_API_KEY" not in st.secrets: return "gemini-pro"
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return 'gemini-1.5-flash'
    return 'gemini-pro'

def get_img_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def ai_generate_letter(kat, kel, nama):
    m_name = get_active_model()
    try:
        model = genai.GenerativeModel(m_name)
        prompt = f"Buat draf surat formal PIKM HMSD. Pelapor: {nama}, Kategori: {kat}, Keluhan: {kel}. Output: PERIHAL|||TUJUAN|||ISI_LENGKAP"
        res = model.generate_content(prompt)
        parts = res.text.split("|||")
        if len(parts) >= 3: return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except: pass
    return "Tindak Lanjut", "Ketua Prodi", f"Laporan {nama}."

def create_pdf(no, lamp, per, tuj, isi):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.add_page()
    pdf.set_font("Times", 'B', 12); pdf.cell(0, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_font("Times", '', 12); pdf.ln(10); pdf.multi_cell(0, 6, isi)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. NAVIGATION
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["grid-fill", "megaphone-fill", "search", "bar-chart-steps", "robot", "shield-lock-fill"],
    default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "10px", "background-color": "white", "border-radius": "0 0 20px 20px"},
        "nav-link-selected": {"background-color": "#2563eb"}
    }
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# =========================================================
# 5. HOME
# =========================================================
if selected == "Home":
    logo = get_img_base64("logo_him.png")
    st.markdown(f"""
    <div class="hero-card">
        <div><h1 class="hero-title">Sains Data<br>Crisis Center</h1><p>Platform aspirasi mahasiswa terintegrasi AI.</p></div>
        <img src="data:image/png;base64,{logo}" class="hero-logo-img">
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="feature-card">📢<h3>Lapor</h3></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="feature-card">📊<h3>Pantau</h3></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="feature-card">🤖<h3>Bot AI</h3></div>', unsafe_allow_html=True)

# =========================================================
# 6. LAPOR (FITUR BUKTI SUDAH KEMBALI)
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan Resmi</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:40px; border-radius:30px; border:1px solid #e2e8f0;">', unsafe_allow_html=True)
        with st.form("lapor_sop_fixed", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nama = col1.text_input("Nama Lengkap")
            npm = col2.text_input("NPM")
            prodi = col1.selectbox("Program Studi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
            kat = col2.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
            detail = st.text_area("Deskripsi Laporan Secara Detail")
            
            # --- FITUR BUKTI (DIBALIKIN) ---
            bukti_file = st.file_uploader("Upload Bukti (Gambar JPG/PNG)", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("Kirim Laporan Sekarang"):
                if not detail: st.warning("Isi detail laporan dulu ya.")
                else:
                    with st.spinner("Mengirim..."):
                        link_bukti = "-"
                        if bukti_file:
                            try:
                                res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files={"image": bukti_file.getvalue()})
                                if res.json().get("success"): link_bukti = res.json()["data"]["url"]
                            except: pass
                        
                        if sheet:
                            sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, npm, prodi, kat, detail, "Pending", link_bukti])
                            st.success("✅ Laporan dan Bukti berhasil diterima!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 8. DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f'<div class="stat-box"><div class="stat-lbl">Total</div><div class="stat-val">{len(df)}</div></div>', unsafe_allow_html=True)
            with k2: st.markdown(f'<div class="stat-box" style="border-color:#f59e0b;"><div class="stat-lbl">Proses</div><div class="stat-val">{len(df[df["Status"]!="Selesai"])}</div></div>', unsafe_allow_html=True)
            with k3: st.markdown(f'<div class="stat-box" style="border-color:#10b981;"><div class="stat-lbl">Selesai</div><div class="stat-val">{len(df[df["Status"]=="Selesai"])}</div></div>', unsafe_allow_html=True)
            st.plotly_chart(go.Figure(data=[go.Pie(labels=df['Kategori Masalah'].value_counts().index, values=df['Kategori Masalah'].value_counts().values, hole=.5)]), use_container_width=True)

# =========================================================
# 9. SADAS BOT (DENGAN MEMORI)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot AI</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-row {role}"><div class="chat-bubble {role}">{m["content"]}</div></div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Tanya apa saja..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        m_active = get_active_model()
        try:
            model = genai.GenerativeModel(m_active)
            history = [{"role": ("user" if x["role"]=="user" else "model"), "parts": [x["content"]]} for x in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            res = chat.send_message(f"Instruksi: Kamu Sadas Bot HMSD. Jawab ramah: {prompt}")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except: st.error("AI sibuk.")
        st.rerun()

# =========================================================
# 10. ADMIN
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Admin Area</h2>", unsafe_allow_html=True)
    if 'logged' not in st.session_state: st.session_state.logged = False
    if not st.session_state.logged:
        with st.form("login"):
            if st.form_submit_button("Login") and st.text_input("Password", type="password") == "RAHASIA PIKM😭":
                st.session_state.logged = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state.logged = False; st.rerun()
        if sheet:
            data = sheet.get_all_values()
            df = pd.DataFrame(data[1:], columns=data[0])
            st.dataframe(df, use_container_width=True)
            lapor_list = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(data[1:], 2) if r[0].strip()]
            if lapor_list:
                pilih = st.selectbox("Pilih Laporan:", lapor_list)
                idx = int(pilih.split(" | ")[0])
                row = data[idx-1]
                t1, t2 = st.tabs(["Status", "Surat AI"])
                with t1:
                    if st.button("Set Selesai"): sheet.update_cell(idx, 7, "Selesai"); st.rerun()
                with t2:
                    if st.button("Generate Surat"):
                        p, t, i = ai_generate_letter(row[4], row[5], row[1])
                        st.session_state.dp, st.session_state.dt, st.session_state.di = p, t, i
                    st.text_area("Pratinjau", value=st.session_state.get('di', ''))

st.markdown('</div>', unsafe_allow_html=True)
