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

/* MENU */
iframe[title="streamlit_option_menu.option_menu"] { width: 100%; background: transparent; }

/* JARAK KONTEN */
.block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; max-width: 1200px; }

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

if "GEMINI_API_KEY" in st.secrets:
    try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except: pass

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

# --- FUNGSI AI DRAFTER ---
def draft_surat_with_ai(kategori, keluhan, nama):
    if "GEMINI_API_KEY" not in st.secrets:
        return None, None, None
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Buatkan draft surat formal dari Himpunan Mahasiswa Sains Data (PIKM) ke pihak kampus.
        Konteks: Mahasiswa bernama {nama} melapor: '{keluhan}' (Kategori: {kategori}).
        
        Output WAJIB pakai separator '|||' :
        PERIHAL_SINGKAT|||TUJUAN_JABATAN|||ISI_SURAT_LENGKAP_(PEMBUKA_INTI_PENUTUP)
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        parts = text.split("|||")
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        else:
            return "Pengajuan Tindak Lanjut", "Ketua Program Studi Sains Data", text
    except:
        return "Pengajuan Tindak Lanjut", "Ketua Program Studi Sains Data", "Gagal generate AI. Silakan tulis manual."

# --- FUNGSI PDF GENERATOR ---
def create_pdf(no_surat, lampiran, perihal, tujuan, isi_surat):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. KOP SURAT (Priority: kop_surat.png)
    if os.path.exists("kop_surat.png"):
        # Asumsi gambar kop sudah proporsional (A4 width approx 210mm)
        pdf.image("kop_surat.png", x=0, y=0, w=210) 
        pdf.ln(40) # Geser ke bawah melewati gambar kop
    elif os.path.exists("logo_him.png"):
        # Fallback manual kalau gak ada gambar kop
        pdf.image("logo_him.png", x=10, y=10, w=25)
        pdf.set_font("Times", 'B', 16)
        pdf.cell(0, 10, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
        pdf.set_font("Times", 'B', 12)
        pdf.cell(0, 10, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
        pdf.line(10, 35, 200, 35)
        pdf.ln(15)
    else:
        pdf.ln(20)

    # 2. INFO SURAT
    pdf.set_font("Times", '', 12)
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, lampiran, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(5)

    # 3. TUJUAN
    pdf.cell(0, 6, "Kepada Yth.", 0, 1)
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 6, tujuan, 0, 1)
    pdf.set_font("Times", '', 12)
    pdf.cell(0, 6, "di Tempat", 0, 1)
    pdf.ln(10)

    # 4. ISI SURAT (Multi Cell)
    pdf.set_font("Times", '', 12)
    pdf.multi_cell(0, 6, isi_surat)
    pdf.ln(15)

    # 5. TANDA TANGAN
    # Format Tanggal Indo
    now = datetime.datetime.now()
    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    tanggal_str = f"{now.day} {bulan_indo[now.month-1]} {now.year}"

    pdf.set_x(120)
    pdf.cell(0, 5, f"Bandar Lampung, {tanggal_str}", 0, 1, 'C')
    pdf.set_x(120)
    pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C')
    pdf.set_x(120)
    pdf.cell(0, 5, "Ketua Departemen PIKM", 0, 1, 'C')
    
    pdf.ln(25)
    
    pdf.set_x(120)
    pdf.set_font("Times", 'BU', 12)
    pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    pdf.set_x(120)
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
                        
                        try:
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
                    raw_data = sheet.get_all_values()
                    if len(raw_data) > 1:
                        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
                        if 'Waktu Lapor' in df.columns:
                             df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                        
                        hasil = df[df['NPM'] == npm_input]
                        
                        if not hasil.empty:
                            for idx, row in hasil.iterrows():
                                status = row['Status']
                                color = "#d97706" if status == "Pending" else ("#059669" if status == "Selesai" else "#2563eb")
                                st.markdown(f"""<div class="glass-card" style="border-left:5px solid {color}; text-align:left;">
                                <h4 style="margin:0;">{row['Kategori Masalah']}</h4>
                                <small style="color:#64748b;">{row['Waktu Lapor']}</small>
                                <p style="margin-top:10px;">"{row['Detail Keluhan']}"</p>
                                <div style="background:{color}22; color:{color}; padding: 5px 10px; border-radius:8px; display:inline-block; font-weight:bold; margin-top:5px;">{status}</div></div>""", unsafe_allow_html=True)
                        else: st.warning("NPM tidak ditemukan.")
                    else: st.info("Belum ada data di database.")
                except Exception as e: st.error(f"Gagal mengambil data: {e}")

# =========================================================
# 8. HALAMAN: DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard Analisis</h2>", unsafe_allow_html=True)
    if sheet:
        try:
            raw_data = sheet.get_all_values()
            
            if len(raw_data) > 1:
                df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
                if 'Waktu Lapor' in df.columns:
                    df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                
                col1, col2, col3 = st.columns(3)
                with col1: st.markdown(f"""<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total</div></div>""", unsafe_allow_html=True)
                with col2: st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#d97706;">{len(df[df['Status'] == 'Pending'])}</div><div class="metric-label">Menunggu</div></div>""", unsafe_allow_html=True)
                with col3: st.markdown(f"""<div class="glass-card"><div class="metric-value" style="color:#059669;">{len(df[df['Status'] == 'Selesai'])}</div><div class="metric-label">Selesai</div></div>""", unsafe_allow_html=True)
                
                c_a, c_b = st.columns(2)
                with c_a:
                    if 'Kategori Masalah' in df.columns:
                        pie = df['Kategori Masalah'].value_counts()
                        fig = go.Figure(data=[go.Pie(labels=pie.index, values=pie.values, hole=.5)])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b", title="Kategori")
                        st.plotly_chart(fig, use_container_width=True)
                with c_b: 
                    if 'Status' in df.columns:
                        bar = df['Status'].value_counts()
                        fig2 = go.Figure([go.Bar(x=bar.index, y=bar.values, marker_color=['#d97706', '#059669'])])
                        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b", title="Status")
                        st.plotly_chart(fig2, use_container_width=True)

                st.write("---")
                
                st.write("### 📝 Riwayat Laporan (Publik)")
                kolom_rahasia = ['Nama Mahasiswa', 'NPM', 'Jurusan', 'Detail Keluhan', 'Bukti', 'Link Bukti', 'Foto']
                kolom_tampil = [col for col in df.columns if col not in kolom_rahasia]
                
                if not df.empty:
                    st.dataframe(df[kolom_tampil], use_container_width=True, hide_index=True)
                else:
                    st.info("Belum ada data.")
                
            else: 
                st.info("⚠️ Data masih kosong.")
        except Exception as e: 
            st.error(f"Error memuat dashboard: {str(e)}")

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
        if "GEMINI_API_KEY" in st.secrets:
            try:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods: available_models.append(m.name)
                
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
                    response = "⚠️ **API Key Bermasalah.** Tolong ganti API Key Gemini di pengaturan Secrets."
                else:
                    response = f"⚠️ Maaf ada error: {err_msg}"
        else:
            response = "⚠️ API Key Gemini belum dipasang di Secrets."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 10. HALAMAN: ADMIN (SMART AI + EDITOR)
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
        if st.button("Logout", key="logout_btn"):
            st.session_state['is_logged_in'] = False
            st.rerun()
            
        st.write("---")
        
        if sheet:
            try:
                raw_data = sheet.get_all_values()
                
                if len(raw_data) > 1:
                    st.subheader("📋 Database Lengkap")
                    df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
                    if 'Waktu Lapor' in df.columns:
                        df_display = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                        st.dataframe(df_display, use_container_width=True)
                    
                    st.write("---")
                    
                    # --- PILIH LAPORAN ---
                    pilihan_laporan = []
                    for i, row in enumerate(raw_data[1:], start=2):
                        if not row[0].strip(): continue
                        nama_pelapor = row[1] if len(row) > 1 else "Tanpa Nama"
                        kategori_lapor = row[4] if len(row) > 4 else "-"
                        isi_keluhan = row[5][:20] if len(row) > 5 else "-"
                        label = f"{i} | {nama_pelapor} - {kategori_lapor} ({isi_keluhan}...)" 
                        pilihan_laporan.append(label)
                    
                    if pilihan_laporan:
                        laporan_terpilih = st.selectbox("Pilih Laporan:", pilihan_laporan)
                        
                        nomor_baris = int(laporan_terpilih.split(" | ")[0])
                        data_terpilih = raw_data[nomor_baris - 1]
                        
                        # --- DATA PELAPOR ---
                        nama_mhs = data_terpilih[1]
                        npm_mhs = data_terpilih[2]
                        jur_mhs = data_terpilih[3]
                        kat_mhs = data_terpilih[4]
                        kel_mhs = data_terpilih[5]
                        
                        tab_status, tab_surat = st.tabs(["⚙️ Update Status", "🖨️ Generator Surat (AI)"])
                        
                        # --- TAB 1: UPDATE STATUS ---
                        with tab_status:
                            status_baru = st.selectbox("Ubah Status Jadi:", ["Pending", "Sedang Diproses", "Selesai"])
                            if st.button("💾 Simpan Status"):
                                with st.spinner("Menyimpan..."):
                                    try:
                                        sheet.update_cell(nomor_baris, 7, status_baru)
                                        st.success(f"Status berhasil diubah jadi: {status_baru}")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e: st.error(f"Gagal: {e}")

                        # --- TAB 2: SMART SURAT (AI + EDIT MANUSIA) ---
                        with tab_surat:
                            st.write("#### 📝 Generator Surat Otomatis")
                            st.info("Langkah 1: Klik tombol AI untuk bikin draft. \nLangkah 2: Edit teks di kotak bawah sesukamu. \nLangkah 3: Klik Cetak.")
                            
                            if 'draft_perihal' not in st.session_state: st.session_state.draft_perihal = ""
                            if 'draft_tujuan' not in st.session_state: st.session_state.draft_tujuan = ""
                            if 'draft_isi' not in st.session_state: st.session_state.draft_isi = ""

                            if st.button("✨ 1. Buat Draft via AI"):
                                with st.spinner("AI sedang berpikir..."):
                                    p, t, i = draft_surat_with_ai(kat_mhs, kel_mhs, nama_mhs)
                                    st.session_state.draft_perihal = p
                                    st.session_state.draft_tujuan = t
                                    st.session_state.draft_isi = i
                                    st.success("Draft jadi! Silakan edit di bawah.")

                            st.write("---")
                            st.write("##### ✏️ Editor Surat (Silakan Edit Di Sini)")
                            
                            # FORM EDITOR YANG MENGAMBIL NILAI DARI SESSION STATE
                            # APAPUN YANG DIKETIK DI SINI AKAN MASUK KE PDF
                            col_s1, col_s2, col_s3 = st.columns([1, 1, 2])
                            with col_s1:
                                no_surat = st.text_input("Nomor Surat", value="001/PIKM-HMSD/II/2026")
                            with col_s2:
                                lampiran = st.text_input("Lampiran", value="1 Berkas")
                            with col_s3:
                                perihal_surat = st.text_input("Perihal", value=st.session_state.draft_perihal)
                            
                            tujuan_surat = st.text_input("Tujuan Surat (Yth.)", value=st.session_state.draft_tujuan)
                            isi_lengkap = st.text_area("Isi Surat Lengkap", value=st.session_state.draft_isi, height=300)
                            
                            if st.button("🖨️ 2. Cetak PDF Final"):
                                # PDF DIBUAT BERDASARKAN APA YANG ADA DI KOTAK INPUT SAAT INI
                                pdf_bytes = create_pdf(no_surat, lampiran, perihal_surat, tujuan_surat, isi_lengkap)
                                st.download_button(
                                    label="📥 Download Surat (PDF)",
                                    data=pdf_bytes,
                                    file_name=f"Surat_Tindak_Lanjut_{nama_mhs}.pdf",
                                    mime="application/pdf"
                                )
                                st.balloons()
                    else:
                        st.info("Tidak ada laporan valid.")
                else:
                    st.info("Belum ada data laporan.")
            except Exception as e:
                st.error(f"Error Database: {str(e)}")
