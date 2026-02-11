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
# 2. GLOBAL CSS (UPGRADED PROFESSIONAL & RESPONSIVE UI)
# =========================================================
st.markdown("""
<style>
/* --- 1. SETUP DASAR & FONT --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp { 
    background: #f1f5f9; /* Soft Slate Gray */
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }

/* --- 2. HERO SECTION (UPGRADED) --- */
.hero-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    border-radius: 24px;
    margin-bottom: 30px;
    box-shadow: 0 20px 25px -5px rgba(30, 58, 138, 0.2);
    color: white;
}

.hero-text { flex: 1; padding-right: 20px; }
.hero-title {
    font-size: 48px;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
    letter-spacing: -1.5px;
}
.hero-subtitle {
    font-size: 18px;
    margin-top: 15px;
    opacity: 0.9;
    font-weight: 500;
}
.hero-logo {
    width: 160px;
    height: auto;
    filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.3));
}

/* --- 3. MODERN CARDS & CONTAINERS --- */
.glass-card { 
    background: #ffffff; 
    border-radius: 20px; 
    padding: 30px; 
    border: 1px solid #e2e8f0; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
    text-align: center; 
    height: 100%; 
    transition: all 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
    border-color: #3b82f6;
}

/* --- 4. CHAT INTERFACE (MODERN BUBBLES) --- */
.chat-message { padding: 1.2rem; border-radius: 18px; margin-bottom: 12px; display: flex; font-size: 15px; line-height: 1.6; }
.chat-message.user { 
    background: #2563eb; 
    color: white; 
    justify-content: flex-end; 
    margin-left: 20%;
    border-bottom-right-radius: 4px;
}
.chat-message.bot { 
    background: white; 
    color: #334155; 
    border: 1px solid #e2e8f0;
    margin-right: 20%;
    border-bottom-left-radius: 4px;
}

/* --- 5. MOBILE RESPONSIVENESS --- */
@media (max-width: 768px) {
    .hero-container { flex-direction: column-reverse; text-align: center; padding: 2rem 1.5rem; }
    .hero-text { padding-right: 0; margin-top: 20px; }
    .hero-title { font-size: 32px; }
    .hero-logo { width: 110px; }
    .chat-message.user { margin-left: 5%; }
    .chat-message.bot { margin-right: 5%; }
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
        return client.open_by_key(ID_SPREADSHEET)
    except: return None

sh = get_spreadsheet()
sheet = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

# Fungsi Deteksi Model Otomatis agar tidak error
def get_available_model():
    if "GEMINI_API_KEY" not in st.secrets: return "gemini-1.5-flash"
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return "gemini-1.5-flash"
    return "gemini-1.5-flash"

def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" in st.secrets:
        try:
            model_active = get_available_model()
            model = genai.GenerativeModel(model_active) 
            prompt = f"Buatkan draf surat formal PIKM HMSD UIN RIL. Pelapor: {nama}, Kategori: {kategori}, Keluhan: {keluhan}. Format: PERIHAL|||TUJUAN|||ISI"
            response = model.generate_content(prompt)
            parts = response.text.split("|||")
            if len(parts) >= 3: return parts[0].strip(), parts[1].strip(), parts[2].strip()
        except: pass 
    return "Tindak Lanjut Keluhan", "Ketua Program Studi", f"Menyampaikan laporan {nama}."

def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.set_margins(30, 25, 25); pdf.add_page()
    if os.path.exists("logo_uin.png"): pdf.image("logo_uin.png", x=25, y=20, w=22)
    if os.path.exists("logo_him.png"): pdf.image("logo_him.png", x=163, y=20, w=22)
    pdf.set_y(20); pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.set_font("Times", '', 12); pdf.ln(10)
    pdf.multi_cell(0, 6, isi_surat)
    return pdf.output(dest='S').encode('latin-1')

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# =========================================================
# 4. MENU NAVIGASI (CLEAN DESIGN)
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house-door-fill", "megaphone-fill", "search-heart-fill", "bar-chart-fill", "robot", "shield-lock-fill"],
    default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "8px", "background-color": "#ffffff", "border-radius": "15px", "margin": "10px"},
        "nav-link-selected": {"background-color": "#2563eb", "color": "white", "border-radius": "10px"},
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
            <h1 class="hero-title">Sains Data<br>Crisis Center</h1>
            <p class="hero-subtitle">Pusat Layanan Aspirasi, Analisis Data, dan Respon Cepat Mahasiswa PIKM HMSD.</p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3>📢 Pelaporan</h3><p>Sampaikan aspirasi anda secara resmi.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3>📊 Transparansi</h3><p>Pantau data statistik laporan mahasiswa.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3>🤖 Sadas Bot</h3><p>Asisten virtual cerdas siap membantu 24/7.</p></div>', unsafe_allow_html=True)

    if sheet_pengumuman:
        st.write("### 📰 Informasi Terbaru")
        data_info = sheet_pengumuman.get_all_records()
        for item in reversed(data_info[-3:]):
            st.info(f"**{item.get('Judul')}** — {item.get('Isi')}")

# =========================================================
# 6. HALAMAN: LAPOR MASALAH (FITUR LENGKAP + BUKTI)
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan Resmi</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card" style="text-align:left;">', unsafe_allow_html=True)
        with st.form("lapor_form", clear_on_submit=True):
            nama = st.text_input("Nama Lengkap")
            col_a, col_b = st.columns(2)
            with col_a: npm = st.text_input("NPM")
            with col_b: jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
            kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
            keluhan = st.text_area("Deskripsi Keluhan")
            bukti_file = st.file_uploader("Upload Bukti (JPG/PNG)", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("🚀 Kirim Laporan"):
                if not keluhan: st.warning("Mohon isi deskripsi keluhan.")
                else:
                    with st.spinner("Mengirim..."):
                        link_bukti = "-"
                        if bukti_file:
                            try:
                                res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files={"image": bukti_file.getvalue()})
                                if res.json().get("success"): link_bukti = res.json()["data"]["url"]
                            except: pass
                        if sheet:
                            sheet.append_row([datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                            st.success("✅ Terkirim! Laporanmu berhasil disimpan.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Lacak Status Laporan</h2>", unsafe_allow_html=True)
    col_x, col_y, col_z = st.columns([1,2,1])
    with col_y:
        npm_input = st.text_input("Masukkan NPM", placeholder="Contoh: 2117041xxx")
        if st.button("Lacak") and sheet:
            df = pd.DataFrame(sheet.get_all_records())
            hasil = df[df['NPM'].astype(str) == npm_input]
            if not hasil.empty:
                for _, row in hasil.iterrows():
                    st.markdown(f'<div class="glass-card" style="text-align:left; margin-bottom:15px;"><h4>{row["Kategori Masalah"]}</h4><p>{row["Detail Keluhan"]}</p><b>Status: {row["Status"]}</b></div>', unsafe_allow_html=True)
            else: st.warning("Data tidak ditemukan.")

# =========================================================
# 8. HALAMAN: DASHBOARD (PROFESSIONAL STATS)
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Laporan", len(df))
            k2.metric("Pending", len(df[df['Status'] == 'Pending']))
            k3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
            
            c_a, c_b = st.columns(2)
            with c_a: st.plotly_chart(go.Figure(data=[go.Pie(labels=df['Kategori Masalah'].value_counts().index, values=df['Kategori Masalah'].value_counts().values, hole=.5)]), use_container_width=True)
            with c_b: st.write("### 📋 Riwayat Laporan"); st.dataframe(df[['Waktu Lapor', 'Kategori Masalah', 'Status']], hide_index=True)

# =========================================================
# 9. HALAMAN: SADAS BOT (MEMORI CHAT + MODERN UI)
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{message["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Tanya apa saja..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        try:
            model = genai.GenerativeModel(get_available_model())
            history = [{"role": ("user" if m["role"] == "user" else "model"), "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            response = chat.send_message(f"Jawab santai sebagai Sadas Bot HMSD: {prompt}")
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except: st.error("AI sedang sibuk.")

# =========================================================
# 10. HALAMAN: ADMIN (FULL AUTOMATED GENERATOR)
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Admin Area</h2>", unsafe_allow_html=True)
    if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
    if not st.session_state['is_logged_in']:
        with st.form("login_form"):
            if st.form_submit_button("Login") and st.text_input("Password", type="password") == "RAHASIA PIKM😭":
                st.session_state['is_logged_in'] = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state['is_logged_in'] = False; st.rerun()
        if sheet:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
                st.dataframe(df, use_container_width=True)
                pilihan = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(raw_data[1:], 2) if r[0].strip()]
                lapor_pilih = st.selectbox("Pilih Laporan untuk Surat:", pilihan)
                idx = int(lapor_pilih.split(" | ")[0])
                data_p = raw_data[idx-1]
                
                t1, t2 = st.tabs(["⚙️ Status", "🖨️ Generator Surat AI"])
                with t1:
                    s_baru = st.selectbox("Update Status:", ["Pending", "Proses", "Selesai"])
                    if st.button("Simpan Status"): sheet.update_cell(idx, 7, s_baru); st.success("Updated!"); st.rerun()
                with t2:
                    if st.button("✨ Generate Draft AI"):
                        p, t, i = draft_surat_with_ai(data_p[4], data_p[5], data_p[1])
                        st.session_state.dp, st.session_state.dt, st.session_state.di = p, t, i
                    
                    per = st.text_input("Perihal", value=st.session_state.get('dp', ''))
                    tuj = st.text_input("Tujuan (Yth.)", value=st.session_state.get('dt', ''))
                    isi = st.text_area("Isi Surat", value=st.session_state.get('di', ''), height=200)
                    if st.button("Cetak PDF"):
                        pdf = create_pdf("001", "1 Berkas", per, tuj, isi)
                        st.download_button("📥 Download PDF", pdf, f"Surat_{data_p[1]}.pdf")
