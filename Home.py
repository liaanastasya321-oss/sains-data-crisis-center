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
/* SETUP DASAR */
.stApp { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); color: #0f172a; }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

/* FONT & INPUT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important; border: 1px solid #94a3b8 !important; 
    color: #334155 !important; border-radius: 8px;
}
label, div[data-testid="stWidgetLabel"] p { color: #0f172a !important; font-weight: 700 !important; }

/* MENU STICKY */
iframe[title="streamlit_option_menu.option_menu"] {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999999;
    width: 100%; background: #f8fafc; padding: 5px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

/* JARAK KONTEN (Responsive) */
.block-container { padding-top: 100px !important; padding-bottom: 50px !important; margin-top: 0 !important; max-width: 1200px; }
@media (max-width: 600px) {
    .block-container { padding-top: 180px !important; padding-left: 1rem !important; padding-right: 1rem !important; }
}

/* HEADER */
.header-container { display: flex; flex-direction: row; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 30px; width: 100%; }
.logo-img { width: 90px; height: auto; object-fit: contain; }
.title-text { flex: 1; text-align: center; }
.title-text h1 { font-size: 32px; margin: 0; font-weight: 800; line-height: 1.2; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.title-text p { font-size: 14px; margin: 5px 0 0 0; color: #64748b; }
@media (max-width: 600px) {
    .header-container { margin-bottom: 15px; }
    .logo-img { width: 45px !important; }
    .title-text h1 { font-size: 18px !important; }
    .title-text p { font-size: 10px !important; margin-top: 2px; }
}

/* COMPONENTS */
.glass-card { background: #ffffff; border-radius: 16px; padding: 20px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 15px; text-align: center; height: 100%; }
.announce-card { background: #ffffff; border-radius: 12px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
div.stButton > button { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; width: 100%; }
.hapus-chat-btn button { background: #ef4444 !important; font-size: 12px !important; padding: 5px 10px !important; width: auto !important; float: right; }
.chat-message { padding: 1rem; border-radius: 8px; margin-bottom: 10px; display: flex; font-size: 14px;}
.chat-message.user { background-color: #e0f2fe; border-left: 4px solid #0284c7; }
.chat-message.bot { background-color: #f1f5f9; border-left: 4px solid #475569; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI GOOGLE SHEETS (MODE "JURUS BODO AMAT") 🛡️
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b" 
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
        sh = client.open_by_key(ID_SPREADSHEET)
        return sh
    except: return None

sh = get_spreadsheet()

# --- JURUS ANTI ERROR: AMBIL SHEET PERTAMA ---
sheet = None
sheet_pengumuman = None

if sh:
    try:
        # Coba ambil tab "Laporan"
        sheet = sh.worksheet("Laporan")
    except:
        try:
            # KALAU GAGAL, AMBIL TAB PERTAMA (INDEX 0)
            sheet = sh.get_worksheet(0)
        except: 
            sheet = None

    try:
        sheet_pengumuman = sh.worksheet("Pengumuman")
    except:
        # Kalau gak nemu pengumuman, ambil sheet kedua (Index 1) kalau ada
        try: sheet_pengumuman = sh.get_worksheet(1)
        except: sheet_pengumuman = None

# --- KONFIGURASI AI ---
if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

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
    img_uin = get_img_as_base64("logo_uin.png")
    img_him = get_img_as_base64("logo_him.png")
    
    header_html = f"""
    <div class="header-container">
        <img src="data:image/png;base64,{img_uin}" class="logo-img">
        <div class="title-text">
            <h1>SAINS DATA CRISIS CENTER</h1>
            <p>Pusat Analisis, Respon Cepat, dan Mitigasi Krisis Mahasiswa</p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="logo-img">
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.write("---") 

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb;">📢 Pelaporan</h3><p>Saluran resmi pengaduan masalah.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2;">📊 Transparansi</h3><p>Pantau data statistik real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed;">🤖 Sadas Bot</h3><p>Asisten AI cerdas 24/7.</p></div>""", unsafe_allow_html=True)

    st.write("")
    st.subheader("📰 Informasi Terbaru")
    if sheet_pengumuman:
        try:
            data_info = sheet_pengumuman.get_all_records()
            if len(data_info) > 0:
                for item in reversed(data_info):
                    tipe = item.get('Tipe', 'Info')
                    border_color = "#ef4444" if tipe == "Urgent" else ("#f59e0b" if tipe == "Penting" else "#3b82f6")
                    st.markdown(f"""
                    <div class="announce-card" style="border-left: 5px solid {border_color};">
                        <div style="display:flex; justify-content:space-between;"><span style="font-weight:bold; color:{border_color}; font-size:12px;">{tipe}</span><span style="color:#94a3b8; font-size:12px;">{item.get('Tanggal', '-')}</span></div>
                        <h4 style="margin: 5px 0; color:#1e293b;">{item.get('Judul', '-')}</h4><p style="margin:0; font-size:13px; color:#475569;">{item.get('Isi', '-')}</p>
                    </div>""", unsafe_allow_html=True)
            else: st.info("Belum ada pengumuman.")
        except: st.warning("Gagal memuat pengumuman.")
    else: st.warning("Tab 'Pengumuman' tidak ditemukan.")

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
            
            # --- TOMBOL ---
            submitted = st.form_submit_button("🚀 Kirim Laporan")
            
            # --- LOGIKA ---
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
                                data_res = res.json()
                                if data_res.get("success"): link_bukti = data_res["data"]["url"]
                            except: pass
                        
                        try:
                            # CEK KONEKSI SHEET TERAKHIR KALI
                            if sheet is None:
                                st.error("❌ Gagal Konek Database. Pastikan 'credentials.json' benar dan Email Robot sudah diinvite ke Sheet.")
                            else:
                                sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                                st.success("✅ Terkirim! Laporanmu berhasil disimpan.")
                        except Exception as e:
                            st.error(f"Error Teknis: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status</h2>", unsafe_allow_html=True)
    col_x, col_y, col_z = st.columns([1,2,1])
    with col_y:
        npm_input = st.text_input("Masukkan NPM", placeholder="Contoh: 2117041xxx")
        cek_btn = st.button("Lacak")
        if cek_btn and npm_input:
            if sheet:
                try:
                    data = sheet.get_all_records()
                    df = pd.DataFrame(data)
                    if 'Waktu Lapor' in df.columns: df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                    df['NPM'] = df['NPM'].astype(str)
                    hasil = df[df['NPM'] == npm_input]
                    if not hasil.empty:
                        for idx, row in hasil.iterrows():
                            status = row['Status']
                            color = "#d97706" if status == "Pending" else ("#059669" if status == "Selesai" else "#2563eb")
                            st.markdown(f"""<div class="glass-card" style="border-left:5px solid {color}; text-align:left;"><h4 style="margin:0;">{row['Kategori Masalah']}</h4><small style="color:#64748b;">{row['Waktu Lapor']}</small><p style="margin-top:10px;">"{row['Detail Keluhan']}"</p><div style="background:{color}22; color:{color}; padding: 5px 10px; border-radius:8px; display:inline-block; font-weight:bold; margin-top:5px;">{status}</div></div>""", unsafe_allow_html=True)
                    else: st.warning("Belum ada laporan.")
                except: st.error("Gagal mengambil data.")

# =========================================================
# 8. HALAMAN: DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        try:
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            if not df.empty and 'Waktu Lapor' in df.columns: df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
            
            if not df.empty:
                col1, col2, col3 = st.columns(3)
                with col1: st.markdown(f"""<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total</div></div>""", unsafe_allow_html=True)
                with col2: st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#d97706;">{len(df[df['Status'] == 'Pending'])}</div><div class="metric-label">Menunggu</div></div>""", unsafe_allow_html=True)
                with col3: st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#059669;">{len(df[df['Status'] == 'Selesai'])}</div><div class="metric-label">Selesai</div></div>""", unsafe_allow_html=True)
                
                c_a, c_b = st.columns(2)
                with c_a:
                    if 'Kategori Masalah' in df.columns:
                        pie = df['Kategori Masalah'].value_counts()
                        fig = go.Figure(data=[go.Pie(labels=pie.index, values=pie.values, hole=.5)])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b")
                        st.plotly_chart(fig, use_container_width=True)
                with c_b: 
                    fig2 = go.Figure(go.Scatter(x=["Senin","Selasa","Rabu"], y=[3,7,2], line=dict(color="#2563eb", width=4)))
                    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#1e293b", height=300)
                    st.plotly_chart(fig2, use_container_width=True)
            else: st.info("Belum ada data.")
        except: st.error("Error memuat dashboard.")

# =========================================================
# 9. HALAMAN: SADAS BOT
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.markdown(f"<h2 style='text-align:left; margin:0;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:left; color:#64748b; margin-top:0px;'>Asisten Akademik Virtual</p>", unsafe_allow_html=True)
    
    with col_btn:
        st.markdown('<div class="hapus-chat-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Hapus Chat"):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    
    if "messages" not in st.session_state: st.session_state.messages = []

    for message in st.session_state.messages:
        role_class = "user" if message["role"] == "user" else "bot"
        st.markdown(f"""<div class="chat-message {role_class}"><div><strong>{message['role'].capitalize()}:</strong> <br> {message['content']}</div></div>""", unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesanmu di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        response = ""
        # --- LOGIKA BOT (ERROR HANDLING RAPI) ---
        if "GEMINI_API_KEY" in st.secrets:
            try:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                target_model = 'gemini-1.5-flash' 
                found_flash = False
                for m in available_models:
                    if 'flash' in m: target_model = m; found_flash = True; break
                
                if not found_flash:
                    for m in available_models:
                        if 'pro' in m: target_model = m; break
                
                model = genai.GenerativeModel(target_model)
                system_prompt = "Kamu adalah Sadas Bot, asisten virtual dari Sains Data UIN Raden Intan Lampung. Jawab sopan dan santai."
                full_prompt = f"{system_prompt}\nUser: {prompt}"
                
                with st.spinner("Sadas Bot sedang mengetik..."):
                    ai_response = model.generate_content(full_prompt)
                    response = ai_response.text

            except Exception as e:
                err_msg = str(e)
                if "403" in err_msg or "suspended" in err_msg:
                    response = "⚠️ **API Key Bermasalah.** Tolong ganti API Key Gemini di pengaturan Secrets ya."
                else:
                    response = f"⚠️ Maaf ada error: {err_msg}"
        else:
            response = "⚠️ API Key Gemini belum dipasang di Secrets."

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
        st.markdown("<div style='max-width:400px; margin:auto;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Password Admin", type="password")
            if st.form_submit_button("Login"):
                if pwd == "RAHASIA PIKM😭":
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else: st.error("Password Salah")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.button("Logout"):
            st.session_state['is_logged_in'] = False
            st.rerun()
        if sheet:
            try:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                if not df.empty and 'Waktu Lapor' in df.columns:
                     df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                     df.reset_index(drop=True, inplace=True)
                st.dataframe(df, use_container_width=True)
            except: st.error("Data kosong")

# =========================================================
# 👇 TEMPEL INI DI PALING BAWAH FILE Home.py 👇
# =========================================================
st.divider()
st.subheader("🕵️‍♂️ DETEKTIF DATABASE")

try:
    # 1. Cek Email Robotnya Siapa?
    if "google_credentials" in st.secrets:
        creds_dict = json.loads(st.secrets["google_credentials"])
    else:
        creds_dict = json.load(open("credentials.json"))
    
    email_robot = creds_dict['client_email']
    st.info(f"📧 **Email Robot Aplikasi Ini:**\n\n`{email_robot}`")
    st.warning("👉 **TUGAS KAMU:** Copy email di atas, Buka Google Sheet > Share > Paste Email itu > Jadikan Editor.")

    # 2. Cek Isi Google Sheetnya Apa?
    client = gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scopes))
    sh_cek = client.open_by_key(ID_SPREADSHEET)
    
    daftar_tab = [ws.title for ws in sh_cek.worksheets()]
    st.success(f"✅ **Koneksi Berhasil!** Nama Tab yang ditemukan: {daftar_tab}")
    
    if "Laporan" not in daftar_tab:
        st.error("❌ **MASALAH DITEMUKAN:** Tab 'Laporan' tidak ada! Ganti nama tab di Google Sheet kamu sesuai nama di atas.")
    else:
        st.balloons()
        st.success("🎉 SEMUA AMAN! Harusnya fitur Lapor sudah bisa dipakai.")

except Exception as e:
    st.error(f"💀 **MATI TOTAL:** Kodingan gak bisa nyentuh Google Sheet sama sekali.\n\nPesan Error Asli: {str(e)}")
