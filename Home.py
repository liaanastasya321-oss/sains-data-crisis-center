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
API_KEY_IMGBB  = "bb772455cfbcde364472c845947a0fad" 
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
    return "gemini-pro" # FIX: Pakai model stabil

def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" in st.secrets:
        try:
            model = genai.GenerativeModel('gemini-pro') # FIX: Langsung inisialisasi di sini
            prompt = f"""
            Buatkan draf surat formal resmi dari Himpunan Mahasiswa Sains Data (PIKM) UIN Raden Intan Lampung.
            Data Pelapor: Nama {nama}, Kategori Masalah: {kategori}, Detail Keluhan: "{keluhan}".
            Format Output WAJIB (Pisahkan dengan |||):
            PERIHAL SURAT|||TUJUAN SURAT (Yth. Ketua Prodi/Kepala Bagian Terkait)|||ISI LENGKAP SURAT
            SOP Surat: Gunakan bahasa formal Indonesia, ada salam pembuka formal, isi yang menjelaskan laporan mahasiswa secara jelas namun padat, dan salam penutup.
            """
            response = model.generate_content(prompt)
            text = response.text.strip()
            parts = text.split("|||")
            if len(parts) >= 3:
                return parts[0].strip(), parts[1].strip(), parts[2].strip()
        except: pass 
    return "Tindak Lanjut Keluhan", "Ketua Program Studi Sains Data", f"Menyampaikan laporan keluhan dari {nama} terkait {kategori}."

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25) 
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    if os.path.exists("logo_uin.png"): pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12); pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(210, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Times", '', 12); pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(5); pdf.cell(0, 6, "Kepada Yth.", 0, 1); pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1)
    pdf.ln(5); pdf.set_font("Times", '', 12); pdf.multi_cell(0, 6, isi_surat)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI (FIX: Sadas Bot jadi Sasda Bot sesuai keinginan Lia)
# =========================================================
if 'selected_menu' not in st.session_state: st.session_state.selected_menu = "Home"

selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sasda Bot", "Admin"],
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
# 5-8. HALAMAN HOME, LAPOR, CEK, DASHBOARD (TETAP SAMA)
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f"""<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1><p class="hero-subtitle">Pusat Layanan Aspirasi, Analisis Data, dan Respon Cepat Mahasiswa PIKM.</p></div><img src="data:image/png;base64,{img_him}" class="hero-logo"></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb;">📢 Pelaporan</h3><p style="color:#64748b; font-size:14px;">Saluran resmi pengaduan masalah fasilitas & akademik.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2;">📊 Transparansi</h3><p style="color:#64748b; font-size:14px;">Pantau statistik dan status penyelesaian secara real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Sasda Bot</h3><p style="color:#64748b; font-size:14px;">Asisten AI cerdas yang siap menjawab pertanyaanmu 24/7.</p></div>""", unsafe_allow_html=True)
    if sheet_pengumuman:
        try:
            data_info = sheet_pengumuman.get_all_records()
            for item in reversed(data_info):
                st.info(f"**{item.get('Judul')}** - {item.get('Isi')}")
        except: pass

elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("form_lapor_keren", clear_on_submit=True):
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        keluhan = st.text_area("Deskripsi Detail")
        bukti_file = st.file_uploader("Upload Bukti", type=["png", "jpg", "jpeg"])
        if st.form_submit_button("🚀 Kirim Laporan"):
            if not keluhan: st.warning("Isi deskripsi.")
            elif sheet:
                waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", "-"])
                st.success("Terkirim!")

elif selected == "Cek Status":
    npm_input = st.text_input("Masukkan NPM")
    if st.button("Lacak") and npm_input and sheet:
        df = pd.DataFrame(sheet.get_all_values())
        st.dataframe(df[df[2] == npm_input])

elif selected == "Dashboard":
    if sheet:
        df = pd.DataFrame(sheet.get_all_values())
        st.metric("Total", len(df)-1)
        st.dataframe(df)

# =========================================================
# 9. HALAMAN: SASDA BOT (FIXED AI LOGIC)
# =========================================================
elif selected == "Sasda Bot":
    st.markdown("## 🤖 Sasda Bot")
    if "messages" not in st.session_state: st.session_state.messages = []
    if st.button("🗑️ Hapus Chat"):
        st.session_state.messages = []
        st.rerun()

    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "bot"
        st.markdown(f"""<div class="chat-message {role}"><div>{message['content']}</div></div>""", unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesanmu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        if "GEMINI_API_KEY" in st.secrets:
            try:
                # FIX: Gunakan gemini-pro dan cara panggil v1
                model = genai.GenerativeModel('gemini-pro')
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat_session = model.start_chat(history=history)
                system_instruction = "Kamu adalah Sasda Bot, asisten virtual Himpunan Mahasiswa Sains Data UIN Raden Intan Lampung. Jawab sopan dan santai."
                
                with st.spinner("Sasda sedang mengetik..."):
                    ai_response = chat_session.send_message(f"{system_instruction}\nUser: {prompt}")
                    response = ai_response.text
            except Exception as e: response = f"🙏 Maaf, server sibuk. Error: {str(e)}"
        else: response = "API Key belum dipasang."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

# =========================================================
# 10. HALAMAN: ADMIN (FIXED AI DRAFT & SESSION)
# =========================================================
elif selected == "Admin":
    if not st.session_state.get('is_logged_in', False):
        pwd = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if pwd == "RAHASIA PIKM😭": st.session_state.is_logged_in = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state.is_logged_in = False; st.rerun()
        if sheet:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                pilihan = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(raw_data[1:], 2)]
                laporan_terpilih = st.selectbox("Pilih Laporan:", pilihan)
                idx = int(laporan_terpilih.split(" | ")[0])
                data_row = raw_data[idx - 1]

                tab1, tab2 = st.tabs(["⚙️ Update Status", "🖨️ Generator Surat AI"])
                with tab2:
                    if st.button("✨ Generate Draft"):
                        with st.spinner("AI merancang..."):
                            # FIX: Panggil AI dan simpan ke session state
                            p, t, i = draft_surat_with_ai(data_row[4], data_row[5], data_row[1])
                            st.session_state.d_p = p
                            st.session_state.d_t = t
                            st.session_state.d_i = i

                    # FIX: Pakai 'key' biar gak ilang pas diklik
                    ns = st.text_input("No Surat", value="001/PIKM-HMSD/II/2026", key="adm_ns")
                    ps = st.text_input("Perihal", value=st.session_state.get('d_p', ''), key="adm_ps")
                    ts = st.text_input("Tujuan", value=st.session_state.get('d_t', ''), key="adm_ts")
                    isii = st.text_area("Isi", value=st.session_state.get('d_i', ''), height=200, key="adm_isii")
                    
                    if st.button("🖨️ Download PDF"):
                        pdf_bytes = create_pdf(ns, "1 Berkas", ps, ts, isii)
                        st.download_button("📥 Unduh", data=pdf_bytes, file_name=f"Surat_{data_row[1]}.pdf")
