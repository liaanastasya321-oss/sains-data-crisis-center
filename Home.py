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
# 2. GLOBAL CSS (Sesuai SOP Tampilan Lia)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
.stApp { background: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.hero-container {
    display: flex; flex-direction: row; align-items: center; justify-content: space-between;
    padding: 2rem 1rem; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
    border-radius: 24px; border: 1px solid #dbeafe; margin-bottom: 30px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.hero-title {
    font-size: 42px; font-weight: 800; margin: 0; line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-logo { width: 140px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); }
.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; text-align: center; height: 100%; transition: all 0.3s ease; }
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; justify-content: flex-end; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }
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
        return gspread.authorize(creds).open_by_key(ID_SPREADSHEET)
    except: return None

sh = get_spreadsheet()
sheet = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

# Auto-Detect Model Active
def get_active_model():
    if "GEMINI_API_KEY" not in st.secrets: return None
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return 'gemini-1.5-flash'
    return None

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- FUNGSI AI DRAFTER OTOMATIS (SOP PIKM) ---
def draft_surat_with_ai(kategori, keluhan, nama):
    model_name = get_active_model()
    if model_name:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"""
            Buatkan draf surat formal resmi dari Himpunan Mahasiswa Sains Data (Departemen PIKM).
            Data Laporan Mahasiswa: Nama {nama}, Kategori {kategori}, Isi Keluhan: "{keluhan}".
            
            Format Output WAJIB (Pisahkan dengan |||):
            PERIHAL|||TUJUAN SURAT (Yth. Ketua Prodi/Bagian terkait)|||ISI SURAT LENGKAP
            
            Gunakan bahasa Indonesia formal (SOP Kampus). Isi surat harus memuat Pembukaan (Assalamu'alaikum), Inti (Melaporkan keluhan tersebut), dan Penutup.
            """
            response = model.generate_content(prompt)
            parts = response.text.split("|||")
            if len(parts) >= 3:
                return parts[0].strip(), parts[1].strip(), parts[2].strip()
        except: pass
    return "Tindak Lanjut Keluhan", "Ketua Program Studi Sains Data", f"Menyampaikan keluhan dari {nama} terkait {kategori}."

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.add_page()
    if os.path.exists("logo_uin.png"): pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12)
    pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_font("Times", '', 12); pdf.ln(10)
    pdf.cell(25, 6, f"Nomor : {no_surat}", 0, 1)
    pdf.cell(25, 6, f"Perihal : {perihal}", 0, 1)
    pdf.ln(5); pdf.cell(0, 6, f"Yth. {tujuan}", 0, 1); pdf.ln(5)
    pdf.multi_cell(0, 6, isi_surat)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0, orientation="horizontal",
    styles={"container": {"background-color": "#ffffff"}, "nav-link-selected": {"background-color": "#2563eb"}}
)

# =========================================================
# 5. HALAMAN: HOME (TAMPILAN ASLI)
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f"""<div class="hero-container"><div class="hero-text"><h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1>
    <p class="hero-subtitle">Pusat Layanan Aspirasi Mahasiswa PIKM.</p></div>
    <img src="data:image/png;base64,{img_him}" class="hero-logo"></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Pelaporan</h3></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Transparansi</h3></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sadas Bot</h3></div>', unsafe_allow_html=True)

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("lapor"):
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        kat = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        kel = st.text_area("Detail Keluhan")
        if st.form_submit_button("🚀 Kirim"):
            if sheet:
                sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y"), nama, npm, "Sains Data", kat, kel, "Pending", "-"])
                st.success("Laporan Terkirim!")

# =========================================================
# 7. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status</h2>", unsafe_allow_html=True)
    npm_cek = st.text_input("NPM kamu")
    if st.button("Lacak") and sheet:
        df = pd.DataFrame(sheet.get_all_records())
        res = df[df['NPM'].astype(str) == npm_cek]
        if not res.empty: st.dataframe(res)
        else: st.warning("Data tidak ditemukan.")

# =========================================================
# 8. HALAMAN: DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            st.plotly_chart(go.Figure(data=[go.Pie(labels=df['Kategori Masalah'].value_counts().index, values=df['Kategori Masalah'].value_counts().values, hole=.5)]))
            st.dataframe(df[['Waktu Lapor', 'Kategori Masalah', 'Status']], use_container_width=True)

# =========================================================
# 9. HALAMAN: SADAS BOT (DENGAN MEMORI)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    st.subheader("🤖 Sadas Bot")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)
    if prompt := st.chat_input("Tanya apa saja..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        m_active = get_active_model()
        if m_active:
            try:
                model = genai.GenerativeModel(m_active)
                # History Chat
                history = [{"role": ("user" if msg["role"] == "user" else "model"), "parts": [msg["content"]]} for msg in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                res = chat.send_message(f"Jawab sopan sebagai Sadas Bot HMSD: {prompt}")
                ans = res.text
            except: ans = "Maaf, sistem sedang sibuk."
        else: ans = "API Key belum aktif."
        st.session_state.messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"): st.markdown(ans)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 10. HALAMAN: ADMIN (AI AUTOMATION)
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
        if sheet:
            data = sheet.get_all_values()
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                st.dataframe(df, use_container_width=True)
                pilihan = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(data[1:], 2) if r[0].strip()]
                lapor_pilih = st.selectbox("Pilih Laporan untuk Surat:", pilihan)
                n_baris = int(lapor_pilih.split(" | ")[0])
                data_p = data[n_baris-1]
                
                t1, t2 = st.tabs(["⚙️ Status", "🖨️ Generator Surat AI"])
                with t1:
                    s_baru = st.selectbox("Ubah Status:", ["Pending", "Proses", "Selesai"])
                    if st.button("Simpan"): sheet.update_cell(n_baris, 7, s_baru); st.rerun()
                with t2:
                    st.info(f"Mengolah data: {data_p[1]} ({data_p[4]})")
                    if st.button("✨ Generate Draft Otomatis"):
                        with st.spinner("AI sedang menyusun surat..."):
                            p, t, i = draft_surat_with_ai(data_p[4], data_p[5], data_p[1])
                            st.session_state.draft_p = p; st.session_state.draft_t = t; st.session_state.draft_i = i
                    
                    # Form Editor Surat
                    per = st.text_input("Perihal", value=st.session_state.get('draft_p', ''))
                    tujuan = st.text_input("Tujuan (Yth.)", value=st.session_state.get('draft_t', ''))
                    isi = st.text_area("Isi Lengkap", value=st.session_state.get('draft_i', ''), height=200)
                    
                    if st.button("🖨️ Download PDF Resmi"):
                        pdf = create_pdf("001/PIKM/2026", "1 Berkas", per, tujuan, isi)
                        st.download_button("📥 Unduh Surat", pdf, f"Surat_{data_p[1]}.pdf")
