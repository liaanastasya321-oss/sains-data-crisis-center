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
# 2. GLOBAL CSS + JS INJECTION (THE COOL STUFF)
# =========================================================
st.markdown("""
<style>
/* ================= HIDE STREAMLIT DEFAULT UI ================= */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}

/* ================= GOOGLE FONT ================= */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top, #0f172a, #020617); /* Deep Navy */
    color: #e5e7eb;
}

/* ================= GLASS CARD ================= */
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.glass-card:hover {
    transform: translateY(-5px);
    border-color: rgba(6, 182, 212, 0.5); /* Cyan border on hover */
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.2);
}

/* ================= HERO SECTION ================= */
.hero {
    padding: 80px 20px;
    text-align: center;
}

.hero h1 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* ================= TYPEWRITER ================= */
#typewriter {
    font-size: 20px;
    margin-top: 10px;
    color: #94a3b8;
    font-family: 'Courier New', monospace;
}

/* ================= METRIC ================= */
.metric-value {
    font-size: 42px;
    font-weight: 700;
    color: #06b6d4; /* Cyan */
}
.metric-label {
    font-size: 14px;
    color: #cbd5e1;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ================= CUSTOM INPUTS ================= */
/* Streamlit input boxes styling */
div[data-baseweb="input"] > div {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] > div {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}
p, label {
    color: #e2e8f0 !important;
}

/* ================= BUTTONS ================= */
div.stButton > button {
    background: linear-gradient(90deg, #2563eb, #06b6d4);
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    width: 100%;
    transition: transform 0.2s;
}
div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
}

/* ================= LOADER ANIMATION ================= */
#loader {
    position: fixed; top:0; left:0; width: 100vw; height: 100vh;
    background: #020617; z-index: 9999;
    display: flex; justify-content: center; align-items: center;
}
.spinner {
    width: 50px; height: 50px;
    border: 4px solid #1e293b; border-top: 4px solid #06b6d4;
    border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>

<div id="loader"><div class="spinner"></div></div>

<script>
// Hide Loader after 1.5s
setTimeout(() => {
    document.getElementById("loader").style.display = "none";
}, 1500);

// Typewriter Effect
const text = "Analisis Data. Respon Cepat. Mitigasi Krisis.";
let i = 0;
function typeWriter() {
    if (i < text.length) {
        document.getElementById("typewriter").innerHTML += text.charAt(i);
        i++;
        setTimeout(typeWriter, 50);
    }
}
document.addEventListener("DOMContentLoaded", typeWriter);
</script>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI GOOGLE SHEETS (REAL)
# =========================================================
# Ganti dengan ID Spreadsheet Kamu
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 

# Ganti dengan API Key ImgBB Kamu
API_KEY_IMGBB  = "827ccb0eea8a706c4c34a16891f84e7b" # <--- CONTOH, PASTE YANG ASLI

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
# 4. NAVIGATION (MENU ATAS)
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Dashboard", "Lapor Masalah", "Cek Status", "Admin"],
    icons=["house", "bar-chart-fill", "exclamation-triangle-fill", "search", "lock-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "rgba(15, 23, 42, 0.8)", "border-radius": "12px"},
        "nav-link": {"font-size": "14px", "color": "#cbd5e1", "margin": "0px"},
        "nav-link-selected": {"background-color": "#06b6d4", "color": "white"},
    }
)

# =========================================================
# 5. HALAMAN: HOME
# =========================================================
if selected == "Home":
    st.markdown("""
    <div class="hero">
        <h1>SAINS DATA CRISIS CENTER</h1>
        <div id="typewriter"></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="glass-card">
            <h2 style="color:#3b82f6;">📢 Pelaporan</h2>
            <p>Saluran resmi pengaduan masalah akademik, fasilitas, dan keuangan secara aman.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("""
        <div class="glass-card">
            <h2 style="color:#06b6d4;">📊 Transparansi</h2>
            <p>Pantau data statistik keluhan mahasiswa secara real-time melalui dashboard publik.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="glass-card">
            <h2 style="color:#8b5cf6;">🚀 Responsif</h2>
            <p>Tim advokasi siap menindaklanjuti laporan Anda dengan cepat dan tuntas.</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# 6. HALAMAN: DASHBOARD PUBLIK (DATA ASLI)
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        # Bersihkan data
        if 'Waktu Lapor' in df.columns:
             df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]

        col1, col2, col3 = st.columns(3)
        
        # Metrik Cards
        with col1:
            st.markdown(f"""<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Laporan</div></div>""", unsafe_allow_html=True)
        with col2:
            pending = len(df[df['Status'] == 'Pending'])
            st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#f59e0b;">{pending}</div><div class="metric-label">Sedang Menunggu</div></div>""", unsafe_allow_html=True)
        with col3:
            selesai = len(df[df['Status'] == 'Selesai'])
            st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#10b981;">{selesai}</div><div class="metric-label">Masalah Selesai</div></div>""", unsafe_allow_html=True)

        # Charts
        c_chart1, c_chart2 = st.columns(2)
        
        with c_chart1:
            st.markdown("##### Kategori Masalah")
            if 'Kategori Masalah' in df.columns:
                pie_data = df['Kategori Masalah'].value_counts()
                fig = go.Figure(data=[go.Pie(labels=pie_data.index, values=pie_data.values, hole=.5)])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True)
        
        with c_chart2:
            st.markdown("##### Tren Laporan")
            # Contoh data dummy utk tren (karena data waktu mungkin belum cukup)
            fig2 = go.Figure(go.Scatter(x=["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], y=[5, 12, 8, 15, 10], line=dict(color="#06b6d4", width=4)))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=350)
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Data belum tersedia.")

# =========================================================
# 7. HALAMAN: LAPOR MASALAH (FORM)
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
                        
                        # Upload ImgBB
                        if bukti_file:
                            try:
                                files = {"image": bukti_file.getvalue()}
                                params = {"key": API_KEY_IMGBB}
                                res = requests.post("https://api.imgbb.com/1/upload", params=params, files=files)
                                data_res = res.json()
                                if data_res.get("success"):
                                    link_bukti = data_res["data"]["url"]
                            except:
                                st.error("Gagal upload gambar, tapi laporan tetap dikirim.")

                        # Simpan ke Sheets
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
                df['NPM'] = df['NPM'].astype(str)
                hasil = df[df['NPM'] == npm_input]
                
                if not hasil.empty:
                    for idx, row in hasil.iterrows():
                        status = row['Status']
                        color = "#f59e0b" if status == "Pending" else ("#10b981" if status == "Selesai" else "#3b82f6")
                        
                        st.markdown(f"""
                        <div class="glass-card" style="border-left: 5px solid {color}; text-align:left;">
                            <h4 style="margin:0;">{row['Kategori Masalah']}</h4>
                            <small style="color:#94a3b8">{row['Waktu Lapor']}</small>
                            <p style="margin-top:10px;">"{row['Detail Keluhan']}"</p>
                            <div style="background:{color}33; color:{color}; padding: 5px 10px; border-radius:8px; display:inline-block; font-weight:bold; margin-top:5px;">
                                {status}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Belum ada laporan ditemukan untuk NPM ini.")
            except:
                st.error("Gagal mengambil data.")

# =========================================================
# 9. HALAMAN: ADMIN (SEDERHANA)
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Admin Area</h2>", unsafe_allow_html=True)
    
    if 'is_logged_in' not in st.session_state:
        st.session_state['is_logged_in'] = False

    if not st.session_state['is_logged_in']:
        col_pass, = st.columns(1) # Center? No, use glass card
        st.markdown("<div style='max-width:400px; margin:auto;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Password Admin", type="password")
            if st.form_submit_button("Login"):
                if pwd == "RAHASIA PIKM😭":
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Password Salah")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("Welcome Admin!")
        if st.button("Logout"):
            st.session_state['is_logged_in'] = False
            st.rerun()
        
        # Tampilkan Data Admin
        try:
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            st.dataframe(df)
        except:
            st.error("Data kosong")
