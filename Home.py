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
# 2. GLOBAL CSS (FIX: CHAT VERTIKAL & UI)
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
.hero-title { font-size: 42px; font-weight: 800; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-logo { width: 140px; height: auto; }

/* CARDS */
.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; text-align: center; height: 100%; transition: all 0.3s ease; }
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; }

/* CSS CHAT BIAR RAPI KE BAWAH (VERTIKAL) */
.chat-container { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; width: 100%; }
.message-box { padding: 12px 18px; border-radius: 15px; max-width: 80%; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
.user-msg { align-self: flex-end; background-color: #2563eb; color: white; border-bottom-right-radius: 2px; }
.bot-msg { align-self: flex-start; background-color: #ffffff; color: #334155; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; }

div.stButton > button { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border-radius: 10px; font-weight: 700; width: 100%; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI DATASET (ASLI PUNYA LIA)
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
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

def panggil_ai_mesin(prompt_system, user_input):
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else 'models/gemini-pro'
        model = genai.GenerativeModel(target)
        res = model.generate_content(f"{prompt_system}\n\nUser: {user_input}")
        return res.text.strip()
    except: return "AI sedang sibuk, Lia."

def draft_surat_with_ai(kategori, keluhan, nama):
    sys = "Kamu Sekretaris Himpunan. Buatkan surat formal. Output: PERIHAL|||TUJUAN|||ISI. Gunakan Assalamu'alaikum."
    hasil = panggil_ai_mesin(sys, f"Nama: {nama}, Kat: {kategori}, Keluhan: {keluhan}")
    if "|||" in hasil: return hasil.split("|||")
    return ["Tindak Lanjut", "Ketua Prodi", hasil]

def create_pdf(no, lamp, per, tuj, isi):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.add_page(); pdf.set_y(20); pdf.set_font("Times", 'B', 12)
    pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.set_font("Times", '', 10); pdf.cell(210, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung", 0, 1, 'C')
    pdf.ln(5); pdf.set_font("Times", '', 12)
    pdf.cell(0, 6, f"Nomor: {no}", 0, 1); pdf.cell(0, 6, f"Perihal: {per}", 0, 1); pdf.ln(5)
    pdf.cell(0, 6, f"Kepada Yth. {tuj}", 0, 1); pdf.ln(5); pdf.multi_cell(0, 6, isi)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU
# =========================================================
selected = option_menu(None, ["Home", "Lapor Masalah", "Dashboard", "Sadas Bot", "Admin"], icons=["house", "exclamation-triangle", "bar-chart", "robot", "lock"], orientation="horizontal")

if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f'<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA CRISIS CENTER</h1><p>Pusat Aspirasi dan Respon Cepat Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="glass-card"><h3>📢 Lapor</h3><p>Fasilitas & Akademik</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="glass-card"><h3>📊 Dashboard</h3><p>Statistik Real-time</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="glass-card"><h3>🤖 Sadas Bot</h3><p>AI Assistant 24/7</p></div>', unsafe_allow_html=True)

elif selected == "Lapor Masalah":
    with st.form("lapor", clear_on_submit=True):
        nama, npm = st.text_input("Nama"), st.text_input("NPM")
        jur, kat = st.selectbox("Prodi", ["Sains Data", "Lainnya"]), st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan"])
        kel = st.text_area("Keluhan")
        if st.form_submit_button("🚀 Kirim"):
            sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, npm, jur, kat, kel, "Pending", "-"])
            st.success("Terkirim!")

# =========================================================
# 5. DASHBOARD (FULL VISUALISASI & TRANSPARANSI)
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="glass-card"><div class="metric-value" style="color:#d97706;">{len(df[df["Status"]=="Pending"])}</div><div class="metric-label">Menunggu</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="glass-card"><div class="metric-value" style="color:#059669;">{len(df[df["Status"]=="Selesai"])}</div><div class="metric-label">Selesai</div></div>', unsafe_allow_html=True)
            
            # DUA VISUALISASI
            v1, v2 = st.columns(2)
            with v1: st.plotly_chart(go.Figure(data=[go.Pie(labels=df['Kategori'].value_counts().index, values=df['Kategori'].value_counts().values, hole=.3, title="Berdasarkan Kategori")], layout=dict(height=350)), use_container_width=True)
            with v2: st.plotly_chart(go.Figure(data=[go.Bar(x=df['Status'].value_counts().index, y=df['Status'].value_counts().values, marker_color=['#d97706','#059669'], title="Berdasarkan Status")], layout=dict(height=350)), use_container_width=True)
            
            # TRANSPARANSI DATA (TANPA IDENTITAS & BUKTI)
            st.write("### 📢 Transparansi Laporan Publik")
            # Hanya kolom Waktu, Prodi, Kategori, Status
            df_publik = df[['Waktu Lapor', 'Prodi', 'Kategori', 'Status']]
            st.dataframe(df_publik, use_container_width=True, hide_index=True)
        else: st.info("Data kosong.")

# =========================================================
# 6. SADAS BOT (VERTIKAL & HISTORY)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    if "chat_memori" not in st.session_state: st.session_state.chat_memori = []
    if "chat_tampilan" not in st.session_state: st.session_state.chat_tampilan = []
    
    if st.button("🗑️ Reset Chat"): st.session_state.chat_memori = []; st.session_state.chat_tampilan = []; st.rerun()

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_tampilan:
        cls = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f'<div class="message-box {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesan..."):
        st.session_state.chat_tampilan.append({"role": "user", "content": prompt})
        try:
            model = genai.GenerativeModel('gemini-pro')
            chat = model.start_chat(history=st.session_state.chat_memori)
            response = chat.send_message(prompt)
            st.session_state.chat_memori.append({"role": "user", "parts": [prompt]})
            st.session_state.chat_memori.append({"role": "model", "parts": [response.text]})
            st.session_state.chat_tampilan.append({"role": "bot", "content": response.text})
            st.rerun()
        except: st.error("AI Error.")

elif selected == "Admin":
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login") and pwd == "RAHASIA PIKM😭": st.session_state.auth = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()
        raw = sheet.get_all_values()
        if len(raw) > 1:
            opts = [f"{i} | {r[1]}" for i, r in enumerate(raw[1:], 2) if r[0].strip()]
            laporan = st.selectbox("Pilih Laporan:", opts)
            idx = int(laporan.split(" | ")[0]); data_t = raw[idx - 1]
            
            tab1, tab2 = st.tabs(["⚙️ Status", "🖨️ Surat AI"])
            with tab1:
                stat = st.selectbox("Ubah Status:", ["Pending", "Proses", "Selesai"])
                if st.button("Simpan"): sheet.update_cell(idx, 7, stat); st.success("Ok!"); st.rerun()
            with tab2:
                if st.button("✨ Buat Draft AI"):
                    p, t, i = draft_surat_with_ai(data_t[4], data_t[5], data_t[1])
                    st.session_state.p, st.session_state.t, st.session_state.i = p, t, i
                if 'i' in st.session_state:
                    p = st.text_input("Perihal", value=st.session_state.p)
                    t = st.text_input("Tujuan", value=st.session_state.t)
                    isi = st.text_area("Isi", value=st.session_state.i, height=300)
                    if st.button("🖨️ Cetak PDF"):
                        pdf_b = create_pdf("001/PIKM/2026", "1 Berkas", p, t, isi)
                        st.download_button("📥 Download", pdf_b, f"Surat_{data_t[1]}.pdf")
