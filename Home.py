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
# 2. GLOBAL CSS (ASLI LIA + CHAT VERTIKAL RAPI)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
.stApp { background: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

.hero-container { display: flex; flex-direction: row; align-items: center; justify-content: space-between; padding: 2rem 1rem; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); border-radius: 24px; border: 1px solid #dbeafe; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.hero-text { flex: 1; padding-right: 20px; }
.hero-title { font-size: 42px; font-weight: 800; margin: 0; line-height: 1.1; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-subtitle { font-size: 16px; color: #64748b; margin-top: 10px; font-weight: 500; }
.hero-logo { width: 140px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); }

@media (max-width: 768px) { .hero-container { flex-direction: column-reverse; text-align: center; padding: 1.5rem; } .hero-text { padding-right: 0; margin-top: 15px; } .hero-title { font-size: 28px; } .hero-logo { width: 100px; } }

.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; height: 100%; transition: all 0.3s ease; }
.glass-card:hover { transform: translateY(-5px); border-color: #bfdbfe; }
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
.metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; }

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border: 1px solid #94a3b8 !important; color: #1e293b !important; border-radius: 10px; padding: 10px; }
div.stButton > button { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; padding: 12px 24px; border-radius: 10px; font-weight: 700; width: 100%; }

/* CHAT VERTIKAL RAPI */
.chat-container { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; width: 100%; }
.message-box { padding: 12px 18px; border-radius: 15px; max-width: 85%; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
.user-msg { align-self: flex-end; background-color: #2563eb; color: white; border-bottom-right-radius: 2px; }
.bot-msg { align-self: flex-start; background-color: #ffffff; color: #334155; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; }

iframe[title="streamlit_option_menu.option_menu"] { width: 100%; background: transparent; }
.block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & FUNGSI BANTUAN (ASLI DATA SET LIA)
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

# --- FUNGSI AI PINTAR (ANTI ERROR) ---
def panggil_ai_mesin(prompt_system, user_input):
    if "GEMINI_API_KEY" not in st.secrets:
        return "⚠️ API Key belum dipasang di Secrets."
    try:
        # OTOMATIS CARI MODEL AGAR GAK ERROR
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else ('models/gemini-pro' if 'models/gemini-pro' in available else available[0])
        model = genai.GenerativeModel(target)
        res = model.generate_content(f"{prompt_system}\n\nUser: {user_input}")
        return res.text.strip()
    except Exception as e:
        return f"🙏 Maaf Lia, AI-nya lagi sibuk banget. (Error: {str(e)})"

# --- FUNGSI DRAFT SURAT (OTOMATIS AI) ---
def draft_surat_with_ai(kategori, keluhan, nama):
    sys_prompt = "Kamu Sekretaris Himpunan. Buatkan isi surat formal berdasarkan keluhan mahasiswa. Output WAJIB format: PERIHAL|||TUJUAN|||ISI_LENGKAP. Gunakan Assalamu'alaikum dan bahasa baku."
    user_p = f"Nama: {nama}, Kategori: {kategori}, Keluhan: {keluhan}"
    hasil = panggil_ai_mesin(sys_prompt, user_p)
    if "|||" in hasil:
        parts = hasil.split("|||")
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    else:
        return "Tindak Lanjut Laporan", "Ketua Program Studi", hasil

# --- FUNGSI PDF ---
def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.set_auto_page_break(auto=True, margin=25); pdf.add_page()
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12); pdf.set_x(0); pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.set_font("Times", '', 10); pdf.cell(210, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung,", 0, 1, 'C')
    part1, part2 = "Lampung 35131 ", "Email: himasda.radenintan@gmail.com"
    pdf.set_x((210 - (pdf.get_string_width(part1) + pdf.get_string_width(part2))) / 2)
    pdf.set_text_color(0, 0, 0); pdf.cell(pdf.get_string_width(part1), 5, part1, 0, 0, 'L')
    pdf.set_text_color(0, 0, 255); pdf.cell(pdf.get_string_width(part2), 5, part2, 0, 1, 'L')
    pdf.set_text_color(0, 0, 0); pdf.ln(2); pdf.set_line_width(0.6); pdf.line(30, pdf.get_y(), 185, pdf.get_y()); pdf.set_line_width(0.2); pdf.line(30, pdf.get_y()+1, 185, pdf.get_y()+1); pdf.ln(6)
    pdf.set_font("Times", '', 12); pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, lampiran, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1); pdf.ln(4)
    pdf.cell(0, 6, "Kepada Yth.", 0, 1); pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1); pdf.set_font("Times", '', 12); pdf.cell(0, 6, "di Tempat", 0, 1); pdf.ln(6); pdf.multi_cell(0, 6, isi_surat); pdf.ln(8)
    if pdf.get_y() > 220: pdf.add_page()
    now = datetime.datetime.now(); bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    pdf.set_x(120); pdf.cell(0, 5, f"Bandar Lampung, {now.day} {bulan_indo[now.month-1]} {now.year}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C'); pdf.set_x(120); pdf.cell(0, 5, "Ketua Departemen PIKM", 0, 1, 'C'); pdf.ln(25); pdf.set_x(120); pdf.set_font("Times", 'BU', 12); pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C'); pdf.set_x(120); pdf.set_font("Times", '', 12); pdf.cell(0, 5, "NPM. 247103001", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
if 'selected_menu' not in st.session_state: st.session_state.selected_menu = "Home"

selected = option_menu(None, ["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"], 
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"], 
    default_index=0, orientation="horizontal", key="nav_menu")

# =========================================================
# 5. HALAMAN UTAMA & KONTEN
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f'<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1><p class="hero-subtitle">Pusat Layanan Aspirasi dan Respon Cepat Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb;">📢 Pelaporan</h3><p style="color:#64748b; font-size:14px;">Saluran resmi pengaduan masalah fasilitas & akademik.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2;">📊 Transparansi</h3><p style="color:#64748b; font-size:14px;">Pantau statistik dan status penyelesaian secara real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Sadas Bot</h3><p style="color:#64748b; font-size:14px;">Asisten AI cerdas yang siap menjawab pertanyaanmu 24/7.</p></div>""", unsafe_allow_html=True)

elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("form_lapor", clear_on_submit=True):
        nama = st.text_input("Nama"); npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        kategori = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        keluhan = st.text_area("Keluhan")
        if st.form_submit_button("🚀 Kirim"):
            sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, npm, jurusan, kategori, keluhan, "Pending", "-"])
            st.success("Terkirim!")

elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="glass-card"><div class="metric-value" style="color:#d97706;">{len(df[df["Status"] == "Pending"])}</div><div class="metric-label">Menunggu</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="glass-card"><div class="metric-value" style="color:#059669;">{len(df[df["Status"] == "Selesai"])}</div><div class="metric-label">Selesai</div></div>', unsafe_allow_html=True)
            
            va, vb = st.columns(2)
            with va: 
                f_pie = go.Figure(data=[go.Pie(labels=df['Kategori Masalah'].value_counts().index, values=df['Kategori Masalah'].value_counts().values, hole=.5)])
                f_pie.update_layout(title="Berdasarkan Kategori", height=350)
                st.plotly_chart(f_pie, use_container_width=True)
            with vb: 
                f_bar = go.Figure(data=[go.Bar(x=df['Status'].value_counts().index, y=df['Status'].value_counts().values, marker_color=['#d97706','#059669'])])
                f_bar.update_layout(title="Berdasarkan Status", height=350)
                st.plotly_chart(f_bar, use_container_width=True)
            st.write("### 📢 Transparansi Laporan Publik")
            st.dataframe(df[['Waktu Lapor', 'Prodi', 'Kategori Masalah', 'Status']], use_container_width=True, hide_index=True)

# --- SADAS BOT DENGAN MEMORY & VERTIKAL ---
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    if "chat_display" not in st.session_state: st.session_state.chat_display = []
    
    if st.button("🗑️ Hapus Chat"): 
        st.session_state.chat_history = []; st.session_state.chat_display = []; st.rerun()

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_display:
        cls = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f'<div class="message-box {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesan..."):
        st.session_state.chat_display.append({"role": "user", "content": prompt})
        with st.spinner("Berpikir..."):
            try:
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_name = 'models/gemini-pro' if 'models/gemini-pro' in available else available[0]
                model = genai.GenerativeModel(model_name)
                chat = model.start_chat(history=st.session_state.chat_history)
                response = chat.send_message(prompt)
                st.session_state.chat_history.append({"role": "user", "parts": [prompt]})
                st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
                st.session_state.chat_display.append({"role": "bot", "content": response.text})
                st.rerun()
            except: st.error("AI Sibuk.")

elif selected == "Admin":
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pwd = st.text_input("Password", type="password")
        if st.button("Masuk") and pwd == "RAHASIA PIKM😭": st.session_state.auth = True; st.rerun()
    else:
        raw_data = sheet.get_all_values()
        if len(raw_data) > 1:
            opts = [f"{i} | {r[1]}" for i, r in enumerate(raw_data[1:], 2) if r[0].strip()]
            sel = st.selectbox("Laporan:", opts); idx = int(sel.split(" | ")[0]); data_t = raw_data[idx - 1]
            if st.button("✨ Buat Draft AI"):
                p, t, i = draft_surat_with_ai(data_t[4], data_t[5], data_t[1])
                st.session_state.p, st.session_state.t, st.session_state.i = p, t, i
            if 'i' in st.session_state:
                p_in = st.text_input("Perihal", st.session_state.p)
                t_in = st.text_input("Tujuan", st.session_state.t)
                i_in = st.text_area("Isi", st.session_state.i, height=300)
                if st.button("Cetak"):
                    st.download_button("Download", create_pdf("001/2026", "1 Berkas", p_in, t_in, i_in), f"Surat_{data_t[1]}.pdf")
