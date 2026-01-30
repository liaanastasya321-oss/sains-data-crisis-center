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
# 2. GLOBAL CSS (VERSI LIGHT MODE / TERANG) ☀️
# =========================================================
st.markdown("""
<style>
/* 1. BACKGROUND HALAMAN (PUTIH KEBIRUAN BERSIH) */
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    color: #1e293b; /* Tulisan Utama jadi HITAM/GELAP */
}

/* 2. SEMBUNYIKAN UI BAWAAN */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}

/* 3. FONT IMPORT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* 4. PERBAIKAN WARNA INPUT FORM (KOTAK ISIAN JELAS) */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    color: #334155 !important;           /* Tulisan yang diketik: HITAM KELABU */
    background-color: #ffffff !important; /* Background Kotak: PUTIH BERSIH */
    border: 1px solid #cbd5e1 !important; /* Garis Tepi: ABU-ABU */
    border-radius: 8px !important;
}

/* LABEL JUDUL DI ATAS KOTAK INPUT */
div[data-testid="stWidgetLabel"] p {
    color: #0f172a !important; /* Warna Label: NAVY GELAP (JELAS) */
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* Placeholder (Tulisan samar) */
::placeholder {
    color: #94a3b8 !important;
    opacity: 1;
}

/* Efek Fokus (Pas diklik) */
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #2563eb !important; /* Garis jadi BIRU pas diklik */
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

/* 5. KARTU (CARD STYLE - LIGHT) */
.glass-card {
    background: #ffffff; /* Kartu Putih */
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    margin-bottom: 20px;
    transition: all 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border-color: #3b82f6; /* Garis Biru pas hover */
}

/* 6. TYPOGRAPHY (JUDUL GELAP) */
h1, h2, h3 { color: #0f172a !important; }
p { color: #475569 !important; }

.hero { padding: 60px 20px; text-align: center; }
.hero h1 {
    font-size: 48px;
    font-weight: 800;
    color: #1e3a8a !important; /* Biru Tua */
    margin-bottom: 10px;
}
.hero p {
    font-size: 18px;
    color: #64748b !important;
}

/* 7. TOMBOL */
div.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8); /* Biru Profesional */
    color: white; border: none; padding: 10px 24px;
    border-radius: 8px; font-weight: bold; width: 100%;
}
div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Angka Dashboard */
.metric-value { font-size: 42px; font-weight: 700; color: #2563eb; }
.metric-label { font-size: 14px; color: #64748b; text-transform: uppercase; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI GOOGLE SHEETS
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b" 

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_google_sheet():
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else:
            return None
        client = gspread.authorize(creds)
        sheet = client.open_by_key(ID_SPREADSHEET).worksheet("Laporan")
        return sheet
    except Exception as e:
        return None

sheet = get_google_sheet()

# =========================================================
# 4. MENU NAVIGASI (LIGHT THEME)
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Dashboard", "Lapor Masalah", "Cek Status", "Admin"],
    icons=["house", "bar-chart-fill", "exclamation-triangle-fill", "search", "lock-fill"],
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
    st.markdown("""
    <div class="hero">
        <h1>SAINS DATA CRISIS CENTER</h1>
        <p>Pusat Analisis, Respon Cepat, dan Mitigasi Krisis Mahasiswa</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="glass-card"><h2 style="color:#2563eb;">📢 Pelaporan</h2><p>Saluran resmi pengaduan masalah akademik & fasilitas.</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="glass-card"><h2 style="color:#0891b2;">📊 Transparansi</h2><p>Pantau data statistik keluhan mahasiswa secara real-time.</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="glass-card"><h2 style="color:#7c3aed;">🚀 Responsif</h2><p>Tim advokasi siap menindaklanjuti laporan dengan cepat.</p></div>""", unsafe_allow_html=True)

# =========================================================
# 6. HALAMAN: DASHBOARD (RAPAT KE ATAS)
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        # FILTER PEMBERSIH
        if 'Waktu Lapor' in df.columns:
             df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
        
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"""<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Laporan</div></div>""", unsafe_allow_html=True)
        with col2: st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#d97706;">{len(df[df['Status'] == 'Pending'])}</div><div class="metric-label">Menunggu</div></div>""", unsafe_allow_html=True)
        with col3: st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#059669;">{len(df[df['Status'] == 'Selesai'])}</div><div class="metric-label">Selesai</div></div>""", unsafe_allow_html=True)
        
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("##### Kategori Masalah")
            if 'Kategori Masalah' in df.columns:
                pie_data = df['Kategori Masalah'].value_counts()
                fig = go.Figure(data=[go.Pie(labels=pie_data.index, values=pie_data.values, hole=.5)])
                # Warna Chart disesuaikan Light Mode
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b")
                st.plotly_chart(fig, use_container_width=True)
        with c_chart2:
            st.markdown("##### Tren Harian")
            fig2 = go.Figure(go.Scatter(x=["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], y=[5, 12, 8, 15, 10], line=dict(color="#2563eb", width=4)))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b", height=350)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Data belum tersedia.")

# =========================================================
# 7. HALAMAN: LAPOR MASALAH
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
                if not keluhan:
                    st.warning("Mohon isi deskripsi laporan.")
                else:
                    with st.spinner("Mengirim ke Server..."):
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
                            st.success("✅ Laporan Berhasil Dikirim!")
                        except Exception as e:
                            st.error(f"Error Database: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 8. HALAMAN: CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Cek Status Laporan</h2>", unsafe_allow_html=True)
    col_x, col_y, col_z = st.columns([1,2,1])
    with col_y:
        npm_input = st.text_input("Masukkan NPM Anda", placeholder="Contoh: 2117041xxx")
        cek_btn = st.button("Lacak")
        if cek_btn and npm_input:
            try:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                
                if 'Waktu Lapor' in df.columns:
                    df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]

                df['NPM'] = df['NPM'].astype(str)
                hasil = df[df['NPM'] == npm_input]
                
                if not hasil.empty:
                    for idx, row in hasil.iterrows():
                        status = row['Status']
                        # Warna Status Light Mode
                        color = "#d97706" if status == "Pending" else ("#059669" if status == "Selesai" else "#2563eb")
                        
                        st.markdown(f"""
                        <div class="glass-card" style="border-left: 5px solid {color}; text-align:left;">
                            <h4 style="margin:0; color:#1e293b;">{row['Kategori Masalah']}</h4>
                            <small style="color:#64748b;">{row['Waktu Lapor']}</small>
                            <p style="margin-top:10px; color:#334155;">"{row['Detail Keluhan']}"</p>
                            <div style="background:{color}22; color:{color}; padding: 5px 10px; border-radius:8px; display:inline-block; font-weight:bold; margin-top:5px;">
                                {status}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.warning("Belum ada laporan ditemukan.")
            except: st.error("Gagal mengambil data.")

# =========================================================
# 9. HALAMAN: ADMIN (FIX TABEL RAPI KE ATAS)
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
        try:
            data = sheet.get_all_records()
            df = pd.DataFrame(data)

            # --- LOGIKA PEMBERSIH DATA ADMIN (FIX RAPI) ---
            if not df.empty:
                if 'Waktu Lapor' in df.columns:
                     # 1. Hapus Baris Kosong
                     df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                     # 2. Reset Nomor Urut (Biar tabel naik ke atas)
                     df.reset_index(drop=True, inplace=True)
            # ----------------------------------------------

            st.dataframe(df, use_container_width=True)
        except: st.error("Data kosong")
