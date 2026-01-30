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
# 2. GLOBAL CSS (LIGHT MODE + DESIGN FIX)
# =========================================================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); color: #0f172a; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stSidebar"] {display: none;}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    color: #334155 !important; background-color: #ffffff !important; border: 1px solid #94a3b8 !important; border-radius: 8px !important;
}
label, .stTextInput label, .stSelectbox label, .stTextArea label, .stFileUploader label, div[data-testid="stWidgetLabel"] p {
    color: #0f172a !important; font-size: 15px !important; font-weight: 700 !important;
}
.glass-card {
    background: #ffffff; border-radius: 16px; padding: 24px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
}
.glass-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-color: #3b82f6; }
.announce-card {
    background: #ffffff; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; transition: transform 0.2s;
}
.announce-card:hover { transform: scale(1.01); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 800 !important; }
p { color: #334155 !important; }
.hero h1 {
    font-size: 42px; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px;
}
div.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: bold; width: 100%;
}
div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
div[data-testid="stImage"] { display: flex; justify-content: center; align-items: center; }
.chat-message { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; }
.chat-message.user { background-color: #e0f2fe; border-left: 5px solid #0284c7; }
.chat-message.bot { background-color: #f1f5f9; border-left: 5px solid #475569; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI GOOGLE SHEETS & GEMINI
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
try: sheet = sh.worksheet("Laporan") if sh else None
except: sheet = None
try: sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None
except: sheet_pengumuman = None

# --- KONFIGURASI AI (SETUP AWAL) ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

# =========================================================
# 4. MENU NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house", "exclamation-triangle-fill", "search", "bar-chart-fill", "robot", "lock-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#ffffff", "border-radius": "12px", "border": "1px solid #e2e8f0"},
        "nav-link": {"font-size": "14px", "color": "#64748b", "margin": "0px"},
        "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
    }
)

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if selected == "Home":
    st.write("") 
    col_logo1, col_text, col_logo2 = st.columns([1.5, 6, 1.5])
    with col_logo1:
        if os.path.exists("logo_uin.png"): st.image("logo_uin.png", width=120)
    with col_text:
        st.markdown("""<div class="hero" style="text-align:center; padding: 10px 0;"><h1>SAINS DATA CRISIS CENTER</h1><p style="font-size:16px; margin-top:-10px;">Pusat Analisis, Respon Cepat, dan Mitigasi Krisis Mahasiswa</p></div>""", unsafe_allow_html=True)
    with col_logo2:
        if os.path.exists("logo_him.png"): st.image("logo_him.png", width=120)
    st.write("---") 

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h2 style="color:#2563eb !important;">📢 Pelaporan</h2><p>Saluran resmi pengaduan masalah akademik & fasilitas.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h2 style="color:#0891b2 !important;">📊 Transparansi</h2><p>Pantau data statistik keluhan mahasiswa secara real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h2 style="color:#7c3aed !important;">🤖 Sadas Bot</h2><p>Asisten AI cerdas siap menjawab pertanyaanmu 24/7.</p></div>""", unsafe_allow_html=True)

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
                        <div style="display:flex; justify-content:space-between;"><span style="font-weight:bold; color:{border_color}; text-transform:uppercase; font-size:12px; background:{border_color}15; padding:2px 8px; border-radius:4px;">{tipe}</span><span style="color:#94a3b8; font-size:12px;">{item.get('Tanggal', '-')}</span></div>
                        <h4 style="margin: 5px 0; color:#1e293b !important;">{item.get('Judul', '-')}</h4><p style="margin:0; font-size:14px; color:#475569 !important;">{item.get('Isi', '-')}</p>
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
                                data_res = res.json()
                                if data_res.get("success"): link_bukti = data_res["data"]["url"]
                            except: pass
                        try:
                            sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                            st.success("✅ Terkirim!")
                        except: st.error("Database Error")
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
                with c_b: # Dummy trend
                    fig2 = go.Figure(go.Scatter(x=["Senin","Selasa","Rabu"], y=[3,7,2], line=dict(color="#2563eb", width=4)))
                    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#1e293b", height=300)
                    st.plotly_chart(fig2, use_container_width=True)
            else: st.info("Belum ada data.")
        except: st.error("Error memuat dashboard.")

# =========================================================
# 9. HALAMAN: SADAS BOT (DETEKTIF MODE) 🕵️‍♂️
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>🤖 Sadas Bot</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Tanya apa saja seputar akademik, tugas, atau curhat!</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state: st.session_state.messages = []

    for message in st.session_state.messages:
        role_class = "user" if message["role"] == "user" else "bot"
        st.markdown(f"""<div class="chat-message {role_class}"><div><strong>{message['role'].capitalize()}:</strong> <br> {message['content']}</div></div>""", unsafe_allow_html=True)

    if prompt := st.chat_input("Ketik pesanmu di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        response = ""
        # --- LOGIKA DETEKTIF MODEL ---
        if "GEMINI_API_KEY" in st.secrets:
            try:
                # 1. Kita cari dulu model apa yang tersedia (LIST MODEL)
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                # 2. Coba pakai 'gemini-1.5-flash' dulu (Prioritas)
                target_model = 'gemini-1.5-flash' # Default
                
                # Cek apakah flash ada di list?
                found_flash = False
                for m in available_models:
                    if 'flash' in m:
                        target_model = m
                        found_flash = True
                        break
                
                # Kalau flash gak ada, cari 'pro'
                if not found_flash:
                    for m in available_models:
                        if 'pro' in m:
                            target_model = m
                            break
                
                # 3. Jalankan Model Terpilih
                model = genai.GenerativeModel(target_model)
                
                system_prompt = "Kamu adalah Sadas Bot, asisten virtual dari Sains Data UIN Raden Intan Lampung. Jawab sopan dan santai."
                full_prompt = f"{system_prompt}\nUser: {prompt}"
                
                with st.spinner(f"Sadas Bot berpikir... (Pakai otak: {target_model})"):
                    ai_response = model.generate_content(full_prompt)
                    response = ai_response.text

            except Exception as e:
                # KALAU MASIH ERROR, TAMPILKAN DAFTAR MODEL YANG ADA
                response = f"⚠️ Masih error kak. \n\n**Daftar Model yang tersedia di akunmu:** {available_models} \n\nDetail Error: {str(e)}"
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
