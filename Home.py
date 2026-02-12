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
# 2. GLOBAL CSS
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
.hero-title { font-size: 42px; font-weight: 800; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-logo { width: 140px; }
.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; height: 100%; transition: all 0.3s ease; }
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; }
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; line-height: 1.5; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; justify-content: flex-end; text-align: right; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }
@media (max-width: 768px) { .hero-container { flex-direction: column-reverse; text-align: center; } .hero-title { font-size: 28px; } }
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
            client = gspread.authorize(creds)
            return client.open_by_key(ID_SPREADSHEET)
    except: return None
    return None

sh = get_spreadsheet()
sheet = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def get_available_model():
    if "GEMINI_API_KEY" not in st.secrets: return "gemini-pro"
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return "gemini-pro"
    return "gemini-pro"

def draft_surat_with_ai(kategori, keluhan, nama):
    try:
        model = genai.GenerativeModel(get_available_model()) 
        prompt = f"Buatkan draf surat formal resmi PIKM HMSD UIN RIL. Pelapor: {nama}, Kategori: {kategori}, Keluhan: {keluhan}. Format Output WAJIB: PERIHAL SURAT|||TUJUAN SURAT|||ISI LENGKAP SURAT"
        response = model.generate_content(prompt)
        parts = response.text.split("|||")
        if len(parts) >= 3: return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except: pass 
    return "Tindak Lanjut Keluhan", "Ketua Program Studi Sains Data", f"Menyampaikan laporan keluhan dari {nama} terkait {kategori}."

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.add_page()
    if os.path.exists("logo_uin.png"): pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12)
    pdf.cell(210, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(210, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.ln(10); pdf.set_font("Times", '', 12)
    pdf.cell(0, 6, f"Nomor : {no_surat}", 0, 1)
    pdf.cell(0, 6, f"Lampiran : {lampiran}", 0, 1)
    pdf.cell(0, 6, f"Perihal : {perihal}", 0, 1)
    pdf.ln(5); pdf.cell(0, 6, f"Kepada Yth. {tujuan}", 0, 1); pdf.ln(5)
    pdf.multi_cell(0, 6, isi_surat)
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
if 'selected_menu' not in st.session_state: st.session_state.selected_menu = "Home"

selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sasda Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0, orientation="horizontal",
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
            <p style="color: #475569; font-size: 13px; font-weight: 600; margin-top: 5px;">🕒 Pelayanan Admin PIKM: 07.00 - 14.00 WIB</p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb;">📢 Pelaporan</h3><p style="color:#64748b; font-size:14px;">Saluran resmi pengaduan masalah fasilitas & akademik.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2;">📊 Transparansi</h3><p style="color:#64748b; font-size:14px;">Pantau statistik dan status penyelesaian secara real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Sasda Bot</h3><p style="color:#64748b; font-size:14px;">Asisten AI cerdas yang siap menjawab pertanyaanmu 24/7.</p></div>""", unsafe_allow_html=True)

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("form_lapor", clear_on_submit=True):
            nama = st.text_input("Nama Lengkap"); col_a, col_b = st.columns(2); npm = col_a.text_input("NPM"); jurusan = col_b.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
            kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"]); keluhan = st.text_area("Deskripsi Detail"); bukti_file = st.file_uploader("Upload Bukti (JPG/PNG)", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("🚀 Kirim Laporan"):
                if not keluhan: st.warning("Mohon isi deskripsi.")
                else:
                    with st.spinner("Mengirim..."):
                        waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"); link_bukti = "-"
                        if bukti_file:
                            try:
                                res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files={"image": bukti_file.getvalue()})
                                if res.json().get("success"): link_bukti = res.json()["data"]["url"]
                            except: pass
                        if sheet:
                            sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                            st.success("✅ Terkirim!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7, 8. CEK STATUS & DASHBOARD (Tetap Aman)
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status</h2>", unsafe_allow_html=True)
    npm_in = st.text_input("Masukkan NPM")
    if st.button("Lacak") and sheet and npm_in:
        df = pd.DataFrame(sheet.get_all_records())
        res = df[df['NPM'].astype(str) == npm_in]
        for _, row in res.iterrows():
            st.info(f"Kategori: {row['Kategori Masalah']} | Status: {row['Status']}")

elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        st.metric("Total Laporan", len(df))
        st.plotly_chart(go.Figure(data=[go.Pie(labels=df['Kategori Masalah'].value_counts().index, values=df['Kategori Masalah'].value_counts().values, hole=.5)]), use_container_width=True)

# =========================================================
# 9. HALAMAN: SASDA BOT (STABLE MEMORY)
# =========================================================
elif selected == "Sasda Bot":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    col_h, col_b = st.columns([3, 1])
    with col_h: st.markdown("## 🤖 Sasda Bot")
    with col_b: 
        if st.button("🗑️ Reset Chat"): st.session_state.messages = []; st.rerun()

    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesanmu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        final_res = ""
        if "GEMINI_API_KEY" in st.secrets:
            try:
                model = genai.GenerativeModel(get_available_model())
                history = [{"role": ("user" if msg["role"] == "user" else "model"), "parts": [msg["content"]]} for msg in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(f"Instruksi: Kamu Sasda Bot PIKM. Jawab santai: {prompt}")
                final_res = response.text
            except Exception as e:
                final_res = "🙏 Maaf, kuota harian AI penuh. Coba lagi nanti ya."
        
        st.session_state.messages.append({"role": "assistant", "content": final_res})
        with st.chat_message("assistant"): st.markdown(final_res)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 10. HALAMAN: ADMIN (FULL AUTOMATED GENERATOR FIXED)
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Admin Area</h2>", unsafe_allow_html=True)
    if not st.session_state.get('is_logged_in', False):
        with st.form("login_form"):
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login") and pwd == "RAHASIA PIKM😭":
                st.session_state.is_logged_in = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state.is_logged_in = False; st.rerun()
        if sheet:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                df = pd.DataFrame(raw_data[1:], columns=raw_data[0]); st.dataframe(df, use_container_width=True)
                pilihan = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(raw_data[1:], 2) if r[0].strip()]
                lapor_pilih = st.selectbox("Pilih Laporan:", pilihan)
                idx = int(lapor_pilih.split(" | ")[0]); data_t = raw_data[idx-1]
                
                t1, t2 = st.tabs(["⚙️ Status", "🖨️ Generator Surat AI"])
                with t1:
                    if st.button("Simpan Status"): sheet.update_cell(idx, 7, "Selesai"); st.success("Updated!"); st.rerun()
                with t2:
                    if st.button("✨ Hubungkan AI & Generate Draft"):
                        with st.spinner("AI merancang..."):
                            p, t, i = draft_surat_with_ai(data_t[4], data_t[5], data_t[1])
                            st.session_state.draft_perihal, st.session_state.draft_tujuan, st.session_state.draft_isi = p, t, i
                            st.success("Draft siap!")
                    no_surat = st.text_input("Nomor Surat", value="001/PIKM-HMSD/II/2026")
                    per = st.text_input("Perihal", value=st.session_state.get('draft_perihal', ''))
                    tuj = st.text_input("Tujuan", value=st.session_state.get('draft_tujuan', ''))
                    # PERBAIKAN DI SINI: Nama variabel sinkron dengan create_pdf
                    isi_lengkap = st.text_area("Isi Surat Lengkap", value=st.session_state.get('draft_isi', ''), height=300)
                    if st.button("🖨️ Cetak PDF Final"):
                        pdf_bytes = create_pdf(no_surat, "1 Berkas", per, tuj, isi_lengkap)
                        st.download_button("📥 Download PDF", data=pdf_bytes, file_name=f"Surat_{data_t[1]}.pdf")
