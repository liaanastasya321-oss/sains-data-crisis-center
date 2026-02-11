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
    background: #f8fafc; /* Light Gray Clean */
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

/* --- 2. HEADER HERO SECTION (RESPONSIVE) --- */
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

.hero-text {
    flex: 1;
    padding-right: 20px;
}

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

.hero-subtitle {
    font-size: 16px;
    color: #64748b;
    margin-top: 10px;
    font-weight: 500;
}

.hero-logo {
    width: 140px; /* Ukuran Logo Desktop */
    height: auto;
    filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1));
    transition: transform 0.3s ease;
}

.hero-logo:hover {
    transform: scale(1.05) rotate(2deg);
}

/* --- MOBILE TWEAKS --- */
@media (max-width: 768px) {
    .hero-container {
        flex-direction: column-reverse; /* Logo di atas Text */
        text-align: center;
        padding: 1.5rem;
    }
    .hero-text { padding-right: 0; margin-top: 15px; }
    .hero-title { font-size: 28px; } /* Font HP lebih kecil tapi kebaca */
    .hero-subtitle { font-size: 14px; }
    .hero-logo { width: 100px; } /* Logo HP */
}

/* --- 3. CARDS (KARTU MENU) --- */
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
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    border-color: #bfdbfe;
}
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
    transition: opacity 0.3s;
}
div.stButton > button:hover { opacity: 0.9; }

/* --- 5. CHAT BUBBLE --- */
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; line-height: 1.5; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; justify-content: flex-end; text-align: right; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }

/* Hide Streamlit Elements */
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

# Konfigurasi Awal Gemini
if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

# --- FUNGSI AI DRAFTER (AUTO-SWITCH MODEL) ---
def draft_surat_with_ai(kategori, keluhan, nama):
    perihal_backup = "Tindak Lanjut Keluhan Mahasiswa"
    tujuan_backup = "Ketua Program Studi Sains Data"
    if "Fasilitas" in kategori: tujuan_backup = "Kepala Bagian Umum"
    if "Keuangan" in kategori: tujuan_backup = "Bagian Keuangan"
    
    isi_backup = f"""Assalamu'alaikum Warahmatullahi Wabarakatuh,
Dengan hormat,

Kami dari Himpunan Mahasiswa Sains Data (PIKM) menyampaikan laporan mahasiswa:

Nama : {nama}
Kategori : {kategori}
Keluhan : "{keluhan}"

Mohon kiranya dapat ditindaklanjuti. Terima kasih.

Wassalamu'alaikum Warahmatullahi Wabarakatuh."""

    if "GEMINI_API_KEY" in st.secrets:
        # Coba beberapa nama model yang umum didukung
        for model_name in ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-pro']:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"Buat draft surat formal HMSD. Nama: {nama}, Kategori: {kategori}, Keluhan: {keluhan}. Format: PERIHAL|||TUJUAN|||ISI"
                response = model.generate_content(prompt)
                parts = response.text.split("|||")
                if len(parts) >= 3:
                    return parts[0].strip(), parts[1].strip(), parts[2].strip()
                break 
            except:
                continue 

    return perihal_backup, tujuan_backup, isi_backup

# --- FUNGSI PDF GENERATOR ---
def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25) 
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    
    if os.path.exists("logo_uin.png"):
        pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"):
        pdf.image("logo_him.png", x=163, y=20, w=22)

    pdf.set_y(20) 
    pdf.set_font("Times", 'B', 12) 
    pdf.set_x(0) 
    pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_x(0)
    pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.set_x(0)
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    
    pdf.set_font("Times", '', 10) 
    pdf.set_x(0)
    pdf.cell(210, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung,", 0, 1, 'C')
    
    part1 = "Lampung 35131 "
    part2 = "Email: himasda.radenintan@gmail.com"
    w1 = pdf.get_string_width(part1)
    w2 = pdf.get_string_width(part2)
    start_x = (210 - (w1 + w2)) / 2
    
    pdf.set_x(start_x)
    pdf.set_text_color(0, 0, 0) 
    pdf.cell(w1, 5, part1, 0, 0, 'L')
    pdf.set_text_color(0, 0, 255) 
    pdf.cell(w2, 5, part2, 0, 1, 'L')
    pdf.set_text_color(0, 0, 0) 
    
    pdf.ln(2)
    pdf.set_line_width(0.6)
    pdf.line(30, pdf.get_y(), 185, pdf.get_y()) 
    pdf.set_line_width(0.2)
    pdf.line(30, pdf.get_y()+1, 185, pdf.get_y()+1)
    pdf.ln(6) 

    pdf.set_font("Times", '', 12) 
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, lampiran, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(4)

    pdf.cell(0, 6, "Kepada Yth.", 0, 1)
    pdf.set_font("Times", 'B', 12) 
    pdf.cell(0, 6, tujuan, 0, 1)
    pdf.set_font("Times", '', 12) 
    pdf.cell(0, 6, "di Tempat", 0, 1)
    pdf.ln(6) 

    pdf.multi_cell(0, 6, isi_surat)
    pdf.ln(8) 

    if pdf.get_y() > 220: pdf.add_page()
    now = datetime.datetime.now()
    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    tanggal_str = f"{now.day} {bulan_indo[now.month-1]} {now.year}"
    posisi_ttd = 120 
    pdf.set_x(posisi_ttd)
    pdf.cell(0, 5, f"Bandar Lampung, {tanggal_str}", 0, 1, 'C')
    pdf.set_x(posisi_ttd)
    pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C')
    pdf.set_x(posisi_ttd)
    pdf.cell(0, 5, "Ketua Departemen PIKM", 0, 1, 'C')
    pdf.ln(25) 
    pdf.set_x(posisi_ttd)
    pdf.set_font("Times", 'BU', 12) 
    pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    pdf.set_x(posisi_ttd)
    pdf.set_font("Times", '', 12)
    pdf.cell(0, 5, "NPM. 247103001", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
if 'selected_menu' not in st.session_state: st.session_state.selected_menu = "Home"

selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0,
    orientation="horizontal",
    key="nav_menu",
    styles={
        "container": {"padding": "5px", "background-color": "#ffffff", "border-radius": "12px", "border": "1px solid #e2e8f0"},
        "nav-link": {"font-size": "12px", "color": "#64748b", "margin": "0px", "padding": "5px"}, 
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
            <p class="hero-subtitle">Pusat Layanan Aspirasi, Analisis Data, dan Respon Cepat Mahasiswa PIKM.</p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb;">📢 Pelaporan</h3><p style="color:#64748b; font-size:14px;">Saluran resmi pengaduan masalah fasilitas & akademik.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2;">📊 Transparansi</h3><p style="color:#64748b; font-size:14px;">Pantau statistik dan status penyelesaian secara real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Sadas Bot</h3><p style="color:#64748b; font-size:14px;">Asisten AI cerdas yang siap menjawab pertanyaanmu 24/7.</p></div>""", unsafe_allow_html=True)

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("form_lapor_keren", clear_on_submit=True):
            nama = st.text_input("Nama Lengkap")
            col_a, col_b = st.columns(2)
            with col_a: npm = st.text_input("NPM")
            with col_b: jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
            kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
            keluhan = st.text_area("Deskripsi Detail")
            bukti_file = st.file_uploader("Upload Bukti (JPG/PNG)", type=["png", "jpg", "jpeg"])
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 Kirim Laporan")
            
            if submitted:
                if not keluhan: st.warning("Mohon isi deskripsi laporan.")
                else:
                    with st.spinner("Mengirim..."):
                        waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        link_bukti = "-"
                        if bukti_file:
                            try:
                                files = {"image": bukti_file.getvalue()}
                                params = {"key": API_KEY_IMGBB}
                                res = requests.post("https://api.imgbb.com/1/upload", params=params, files=files)
                                if res.json().get("success"): link_bukti = res.json()["data"]["url"]
                            except: pass
                        if sheet:
                            sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                            st.success("✅ Terkirim!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status</h2>", unsafe_allow_html=True)
    col_x, col_y, col_z = st.columns([1,2,1])
    with col_y:
        npm_input = st.text_input("Masukkan NPM")
        if st.button("Lacak") and npm_input:
            if sheet:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                hasil = df[df['NPM'].astype(str) == npm_input]
                if not hasil.empty:
                    for _, row in hasil.iterrows():
                        st.markdown(f"""<div class="glass-card" style="text-align:left; margin-bottom:10px;">
                        <h4>{row['Kategori Masalah']}</h4>
                        <p>{row['Detail Keluhan']}</p>
                        <strong>Status: {row['Status']}</strong></div>""", unsafe_allow_html=True)
                else: st.warning("NPM tidak ditemukan.")

# =========================================================
# 8. HALAMAN: DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Laporan", len(df))
            c2.metric("Pending", len(df[df['Status'] == 'Pending']))
            c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
            st.dataframe(df, use_container_width=True)

# =========================================================
# 9. HALAMAN: SADAS BOT (FIX MODEL NOT FOUND)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.markdown(f"<h2 style='text-align:left; margin:0;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:left; color:#64748b; margin-top:0px;'>Asisten Akademik Virtual</p>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🗑️ Hapus Chat"):
            st.session_state.messages = []
            st.rerun()

    st.write("---")
    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "bot"
        st.markdown(f"""<div class="chat-message {role_class}"><div>{msg['content']}</div></div>""", unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesanmu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        response = ""
        if "GEMINI_API_KEY" in st.secrets:
            # AUTO-CHECK MODEL: Mencoba model yang tersedia di API v1/v1beta
            available_models = ['gemini-pro', 'gemini-1.5-flash', 'models/gemini-pro']
            success = False
            
            with st.spinner("Sadas Bot sedang mengetik..."):
                for m_name in available_models:
                    try:
                        model = genai.GenerativeModel(m_name)
                        ai_res = model.generate_content(f"Kamu Sadas Bot HMSD. Jawab santai: {prompt}")
                        response = ai_res.text
                        success = True
                        break 
                    except:
                        continue
                
                if not success:
                    response = "🙏 Maaf, terjadi sinkronisasi model di server. Coba beberapa saat lagi."
        else:
            response = "⚠️ API Key belum dikonfigurasi."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 10. HALAMAN: ADMIN
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Admin Area</h2>", unsafe_allow_html=True)
    if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False

    if not st.session_state['is_logged_in']:
        with st.form("login"):
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login") and pwd == "RAHASIA PIKM😭":
                st.session_state['is_logged_in'] = True
                st.rerun()
    else:
        if st.button("Logout"): st.session_state['is_logged_in'] = False; st.rerun()
        if sheet:
            data = sheet.get_all_values()
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                st.dataframe(df)
                
                # Fitur Cetak Surat tetap ada di sini
                st.write("---")
                idx = st.number_input("Pilih Baris Laporan untuk Surat (Mulai dari 2)", min_value=2, max_value=len(data))
                if st.button("✨ Buat Draft & PDF"):
                    row = data[idx-1]
                    p, t, i = draft_surat_with_ai(row[4], row[5], row[1])
                    pdf_bytes = create_pdf("001/HMSD/2026", "1 Berkas", p, t, i)
                    st.download_button("📥 Download PDF", pdf_bytes, f"Surat_{row[1]}.pdf")
