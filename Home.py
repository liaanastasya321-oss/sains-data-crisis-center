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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
.stApp { background: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.hero-container { display: flex; flex-direction: row; align-items: center; justify-content: space-between; padding: 2rem 1rem; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); border-radius: 24px; border: 1px solid #dbeafe; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.hero-title { font-size: 42px; font-weight: 800; margin: 0; line-height: 1.1; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }
.hero-subtitle { font-size: 16px; color: #64748b; margin-top: 10px; font-weight: 500; }
.hero-logo { width: 140px; height: auto; filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1)); transition: transform 0.3s ease; }
@media (max-width: 768px) { .hero-container { flex-direction: column-reverse; text-align: center; padding: 1.5rem; } .hero-title { font-size: 28px; } .hero-logo { width: 100px; } }
.glass-card { background: #ffffff; border-radius: 16px; padding: 25px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; height: 100%; transition: all 0.3s ease; }
.metric-value { font-size: 36px; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
.metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 10px; display: flex; font-size: 15px; line-height: 1.5; }
.chat-message.user { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; justify-content: flex-end; text-align: right; }
.chat-message.bot { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & FUNGSI BANTUAN
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
API_KEY_IMGBB  = "bb772455cfbcde364472c845947a0fad" 
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
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
sheet = None
sheet_pengumuman = None

if sh:
    try: sheet = sh.worksheet("Laporan")
    except: 
        try: sheet = sh.get_worksheet(0)
        except: pass
    try: sheet_pengumuman = sh.worksheet("Pengumuman")
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

def get_available_model():
    if "GEMINI_API_KEY" not in st.secrets: return "gemini-1.5-flash"
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return "gemini-1.5-flash" # Default stabil
    except: return "gemini-pro"

def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" in st.secrets:
        try:
            model_active = get_available_model()
            model = genai.GenerativeModel(model_active) 
            prompt = f"""
            Buatkan draf surat formal resmi dari Himpunan Mahasiswa Sains Data (PIKM) UIN Raden Intan Lampung.
            Data Pelapor: Nama {nama}, Kategori Masalah: {kategori}, Detail Keluhan: "{keluhan}".
            
            Format Output WAJIB (Pisahkan dengan |||):
            PERIHAL SURAT|||TUJUAN SURAT (Yth. Ketua Prodi/Kepala Bagian Terkait)|||ISI LENGKAP SURAT
            
            SOP Surat: Gunakan bahasa formal Indonesia, ada salam pembuka formal, isi yang menjelaskan laporan mahasiswa secara jelas namun padat, dan salam penutup.
            """
            response = model.generate_content(prompt)
            parts = response.text.strip().split("|||")
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

    pdf.set_y(20) 
    pdf.set_font("Times", 'B', 12) 
    pdf.cell(0, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(0, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(0, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    
    pdf.set_font("Times", '', 10) 
    pdf.cell(0, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung, 35131", 0, 1, 'C')
    pdf.ln(2)
    pdf.set_line_width(0.6); pdf.line(30, pdf.get_y(), 185, pdf.get_y()) 
    pdf.ln(6) 

    pdf.set_font("Times", '', 12) 
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, lampiran, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(4)
    pdf.cell(0, 6, "Kepada Yth.", 0, 1)
    pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1)
    pdf.set_font("Times", '', 12); pdf.cell(0, 6, "di Tempat", 0, 1)
    pdf.ln(6) 
    pdf.multi_cell(0, 6, isi_surat)
    pdf.ln(10) 

    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    now = datetime.datetime.now()
    pdf.set_x(120); pdf.cell(0, 5, f"Bandar Lampung, {now.day} {bulan_indo[now.month-1]} {now.year}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Hormat Kami, Ketua Departemen PIKM", 0, 1, 'C')
    pdf.ln(20) 
    pdf.set_x(120); pdf.set_font("Times", 'BU', 12); pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    pdf.set_x(120); pdf.set_font("Times", '', 12); pdf.cell(0, 5, "NPM. 247103001", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sasda Bot", "Admin"], # Benerin Typo Sadas -> Sasda
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0,
    orientation="horizontal",
    styles={"container": {"background-color": "#ffffff"}, "nav-link-selected": {"background-color": "#2563eb"}}
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
    
    # Render Pengumuman if exist
    if sheet_pengumuman:
        try:
            data_info = sheet_pengumuman.get_all_records()
            for item in reversed(data_info[-3:]): # Ambil 3 terakhir
                st.info(f"**{item.get('Judul')}** - {item.get('Isi')}")
        except: pass

# =========================================================
# 6. HALAMAN: LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.form("form_lapor"):
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        keluhan = st.text_area("Deskripsi Detail")
        bukti_file = st.file_uploader("Upload Bukti", type=["png", "jpg", "jpeg"])
        
        if st.form_submit_button("🚀 Kirim Laporan"):
            if not keluhan or not nama: st.warning("Isi semua data.")
            else:
                with st.spinner("Mengirim..."):
                    waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    link_bukti = "-"
                    if bukti_file:
                        try:
                            res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files={"image": bukti_file.getvalue()})
                            link_bukti = res.json()["data"]["url"]
                        except: pass
                    if sheet:
                        sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                        st.success("Laporan terkirim!")

# =========================================================
# 7. HALAMAN: CEK STATUS & DASHBOARD (LOGIKA ASLI)
# =========================================================
elif selected == "Cek Status":
    npm_input = st.text_input("Masukkan NPM")
    if st.button("Lacak") and npm_input and sheet:
        df = pd.DataFrame(sheet.get_all_records())
        hasil = df[df['NPM'].astype(str) == npm_input]
        if not hasil.empty: st.write(hasil[['Waktu Lapor', 'Kategori Masalah', 'Status']])
        else: st.warning("NPM tidak ditemukan.")

elif selected == "Dashboard":
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())
        st.metric("Total Laporan", len(df))
        st.dataframe(df[['Waktu Lapor', 'Kategori Masalah', 'Status']], use_container_width=True)

# =========================================================
# 9. HALAMAN: SASDA BOT (FIXED SYSTEM INSTRUCTION)
# =========================================================
elif selected == "Sasda Bot":
    st.markdown("## 🤖 Sasda Bot")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    if st.button("🗑️ Hapus Chat"):
        st.session_state.messages = []
        st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Tanya Sasda..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        if "GEMINI_API_KEY" in st.secrets:
            try:
                # Perbaikan: System instruction ditaruh saat inisialisasi model
                model = genai.GenerativeModel(
                    model_name=get_available_model(),
                    system_instruction="Kamu adalah Sasda Bot, asisten virtual dari Sains Data UIN Raden Intan Lampung. Jawab dengan sopan, santai, dan membantu."
                )
                
                # Susun history dari session state
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Sasda sedang mengetik..."):
                    ai_res = chat.send_message(prompt)
                    response = ai_res.text
            except: response = "🙏 Maaf, server sedang sibuk."
        else: response = "API Key belum diset."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

# =========================================================
# 10. HALAMAN: ADMIN (FIXED STATE PERSISTENCE)
# =========================================================
elif selected == "Admin":
    if not st.session_state.get('is_logged_in', False):
        pwd = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if pwd == "RAHASIA PIKM😭":
                st.session_state.is_logged_in = True
                st.rerun()
    else:
        if st.button("Logout"): 
            st.session_state.is_logged_in = False
            st.rerun()
        
        if sheet:
            data = sheet.get_all_values()
            if len(data) > 1:
                pilihan = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(data[1:], 2)]
                terpilih = st.selectbox("Pilih Laporan:", pilihan)
                idx = int(terpilih.split(" | ")[0])
                row_data = data[idx-1]

                tab1, tab2 = st.tabs(["Update Status", "Generator Surat AI"])
                
                with tab1:
                    status_baru = st.selectbox("Ubah Status:", ["Pending", "Sedang Diproses", "Selesai"], index=["Pending", "Sedang Diproses", "Selesai"].index(row_data[6]) if row_data[6] in ["Pending", "Sedang Diproses", "Selesai"] else 0)
                    if st.button("Simpan Status"):
                        sheet.update_cell(idx, 7, status_baru)
                        st.success("Berhasil!")

                with tab2:
                    if st.button("✨ Generate Draft Surat"):
                        p, t, i = draft_surat_with_ai(row_data[4], row_data[5], row_data[1])
                        # Simpan ke session state agar tidak hilang saat rerun
                        st.session_state.d_perihal = p
                        st.session_state.d_tujuan = t
                        st.session_state.d_isi = i

                    # Gunakan 'key' agar Streamlit mengingat inputan meskipun rerun
                    st.write("---")
                    no_s = st.text_input("Nomor Surat", value="001/PIKM-HMSD/II/2026", key="no_s")
                    lamp = st.text_input("Lampiran", value="1 Berkas", key="lamp")
                    peri = st.text_input("Perihal", value=st.session_state.get('d_perihal', ''), key="peri")
                    tuju = st.text_input("Tujuan", value=st.session_state.get('d_tujuan', ''), key="tuju")
                    isii = st.text_area("Isi Surat", value=st.session_state.get('d_isi', ''), height=250, key="isii")

                    if st.button("🖨️ Download PDF"):
                        pdf_bytes = create_pdf(no_s, lamp, peri, tuju, isii)
                        st.download_button("📥 Unduh Surat", data=pdf_bytes, file_name=f"Surat_{row_data[1]}.pdf", mime="application/pdf")
