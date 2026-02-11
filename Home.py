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
# 2. MODERN & PREMIUM UI CSS
# =========================================================
st.markdown("""
<style>
/* --- SETUP FONT & BACKGROUND --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

.stApp { 
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

/* Hide Streamlit Header & Footer */
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }

/* --- HERO SECTION --- */
.hero-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 3rem;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    margin-bottom: 40px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
}

.hero-title {
    font-size: 50px;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -2px;
}

.hero-subtitle {
    font-size: 18px;
    color: #64748b;
    margin-top: 15px;
    font-weight: 400;
}

.hero-logo {
    width: 160px;
    filter: drop-shadow(0 15px 25px rgba(59, 130, 246, 0.2));
    transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.hero-logo:hover {
    transform: scale(1.1) rotate(5deg);
}

/* --- CARDS & STATS --- */
.glass-card { 
    background: #ffffff; 
    border-radius: 20px; 
    padding: 30px; 
    border: 1px solid #e2e8f0; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02); 
    text-align: center; 
    height: 100%; 
    transition: all 0.4s ease;
}
.glass-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
    border-color: #3b82f6;
}

.metric-value { font-size: 42px; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
.metric-label { font-size: 13px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }

/* --- ANNOUNCEMENT --- */
.announce-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    border: 1px solid #f1f5f9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* --- BUTTONS --- */
div.stButton > button { 
    background: linear-gradient(90deg, #2563eb, #1d4ed8); 
    color: white; 
    border: none; 
    padding: 14px 28px; 
    border-radius: 12px; 
    font-weight: 600; 
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
}

/* --- CHAT BOT BUBBLES --- */
.chat-message { 
    padding: 1.2rem; 
    border-radius: 18px; 
    margin-bottom: 15px; 
    max-width: 85%;
    font-size: 15px;
}
.chat-message.user { 
    background: #2563eb; 
    color: white; 
    margin-left: auto; 
    border-bottom-right-radius: 4px;
}
.chat-message.bot { 
    background: white; 
    color: #1e293b; 
    margin-right: auto; 
    border-bottom-left-radius: 4px;
    border: 1px solid #e2e8f0;
}

/* --- RESPONSIVE MOBILE --- */
@media (max-width: 768px) {
    .hero-container {
        flex-direction: column-reverse;
        text-align: center;
        padding: 2rem 1.5rem;
    }
    .hero-title { font-size: 32px; }
    .hero-logo { width: 110px; margin-bottom: 20px; }
    .hero-subtitle { font-size: 15px; }
}

/* Nav Bar Styling */
iframe[title="streamlit_option_menu.option_menu"] { border-radius: 15px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONEKSI & FUNGSI (LOGIC TETAP SAMA)
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

def get_available_model():
    if "GEMINI_API_KEY" not in st.secrets: return "gemini-pro"
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except: return "gemini-pro"
    return "gemini-pro"

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

    pdf.set_y(20) 
    pdf.set_font("Times", 'B', 12) 
    pdf.cell(0, 5, "HIMPUNAN MAHASISWA SAINS DATA", 0, 1, 'C')
    pdf.cell(0, 5, "FAKULTAS SAINS DAN TEKNOLOGI", 0, 1, 'C')
    pdf.cell(0, 5, "UNIVERSITAS ISLAM NEGERI RADEN INTAN LAMPUNG", 0, 1, 'C')
    pdf.set_font("Times", '', 10) 
    pdf.cell(0, 5, "Sekretariat: Jl. Letkol Endro Suratmin, Sukarame, Bandar Lampung, 35131", 0, 1, 'C')
    pdf.ln(2)
    pdf.set_line_width(0.6)
    pdf.line(30, pdf.get_y(), 185, pdf.get_y()) 
    pdf.ln(6) 
    pdf.set_font("Times", '', 12) 
    pdf.cell(25, 6, "Nomor", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, no_surat, 0, 1)
    pdf.cell(25, 6, "Lampiran", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, lampiran, 0, 1)
    pdf.cell(25, 6, "Perihal", 0, 0); pdf.cell(5, 6, ":", 0, 0); pdf.cell(0, 6, perihal, 0, 1)
    pdf.ln(4); pdf.cell(0, 6, "Kepada Yth.", 0, 1)
    pdf.set_font("Times", 'B', 12); pdf.cell(0, 6, tujuan, 0, 1)
    pdf.set_font("Times", '', 12); pdf.cell(0, 6, "di Tempat", 0, 1); pdf.ln(6) 
    pdf.multi_cell(0, 6, isi_surat); pdf.ln(8) 

    now = datetime.datetime.now()
    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    tanggal_str = f"{now.day} {bulan_indo[now.month-1]} {now.year}"
    pdf.set_x(120); pdf.cell(0, 5, f"Bandar Lampung, {tanggal_str}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Hormat Kami,", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(0, 5, "Ketua Departemen PIKM", 0, 1, 'C'); pdf.ln(20) 
    pdf.set_x(120); pdf.set_font("Times", 'BU', 12); pdf.cell(0, 5, "LIA ANASTASYA", 0, 1, 'C')
    pdf.set_x(120); pdf.set_font("Times", '', 12); pdf.cell(0, 5, "NPM. 247103001", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. NAVIGASI
# =========================================================
selected = option_menu(
    menu_title=None,
    options=["Home", "Lapor Masalah", "Cek Status", "Dashboard", "Sadas Bot", "Admin"],
    icons=["house-door", "megaphone", "search", "pie-chart", "robot", "shield-lock"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "10px", "background-color": "#ffffff", "border-radius": "15px", "box-shadow": "0 2px 10px rgba(0,0,0,0.05)"},
        "nav-link": {"font-size": "14px", "font-weight": "600", "padding": "10px"},
        "nav-link-selected": {"background": "linear-gradient(90deg, #2563eb, #3b82f6)", "border-radius": "10px"},
    }
)

# =========================================================
# 5. HOME
# =========================================================
if selected == "Home":
    img_him = get_img_as_base64("logo_him.png")
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-text">
            <h1 class="hero-title">SAINS DATA <br> CRISIS CENTER</h1>
            <p class="hero-subtitle">Platform analisis aspirasi dan respon cepat Mahasiswa PIKM.</p>
        </div>
        <img src="data:image/png;base64,{img_him}" class="hero-logo">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h3 style="color:#2563eb; margin:0;">📢 Lapor</h3><p style="color:#64748b; font-size:14px;">Pengaduan masalah fasilitas & akademik.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h3 style="color:#0891b2; margin:0;">📊 Pantau</h3><p style="color:#64748b; font-size:14px;">Statistik & status penyelesaian real-time.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h3 style="color:#7c3aed; margin:0;">🤖 Asisten</h3><p style="color:#64748b; font-size:14px;">Sadas Bot siap menjawab keluhanmu.</p></div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown("### 📰 Pengumuman Terbaru")
    if sheet_pengumuman:
        try:
            data_info = sheet_pengumuman.get_all_records()
            if data_info:
                for item in reversed(data_info):
                    tipe = item.get('Tipe', 'Info')
                    color = "#ef4444" if tipe == "Urgent" else ("#f59e0b" if tipe == "Penting" else "#3b82f6")
                    st.markdown(f"""
                    <div class="announce-card" style="border-left: 6px solid {color};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="background:{color}15; color:{color}; padding:4px 12px; border-radius:20px; font-weight:bold; font-size:11px;">{tipe.upper()}</span>
                            <span style="color:#94a3b8; font-size:12px;">{item.get('Tanggal', '-')}</span>
                        </div>
                        <h4 style="margin: 10px 0 5px 0;">{item.get('Judul', '-')}</h4>
                        <p style="margin:0; font-size:14px; color:#475569;">{item.get('Isi', '-')}</p>
                    </div>""", unsafe_allow_html=True)
            else: st.info("Belum ada pengumuman.")
        except: st.warning("Database pengumuman tidak terbaca.")

# =========================================================
# 6. LAPOR MASALAH
# =========================================================
elif selected == "Lapor Masalah":
    st.markdown("<h2 style='text-align:center;'>📝 Form Pengaduan</h2>", unsafe_allow_html=True)
    with st.container():
        col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
        with col_f2:
            st.markdown('<div class="glass-card" style="text-align:left;">', unsafe_allow_html=True)
            with st.form("form_lapor", clear_on_submit=True):
                nama = st.text_input("Nama Lengkap", placeholder="Nama Anda")
                c_a, c_b = st.columns(2)
                npm = c_a.text_input("NPM", placeholder="NPM")
                jurusan = c_b.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
                kategori = st.selectbox("Kategori Masalah", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
                keluhan = st.text_area("Deskripsi Keluhan", placeholder="Ceritakan detail masalahmu...")
                bukti_file = st.file_uploader("Lampiran Foto (Opsional)", type=["png", "jpg", "jpeg"])
                
                submitted = st.form_submit_button("🚀 KIRIM LAPORAN")
                if submitted:
                    if not keluhan or not nama: st.error("Nama dan Keluhan wajib diisi!")
                    else:
                        with st.spinner("Mengirim ke database..."):
                            waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            link_bukti = "-"
                            if bukti_file:
                                try:
                                    files = {"image": bukti_file.getvalue()}
                                    res = requests.post("https://api.imgbb.com/1/upload", params={"key": API_KEY_IMGBB}, files=files)
                                    if res.json().get("success"): link_bukti = res.json()["data"]["url"]
                                except: pass
                            if sheet:
                                sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                                st.success("Laporan berhasil terkirim! Pantau status di menu Cek Status.")
            st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7. CEK STATUS
# =========================================================
elif selected == "Cek Status":
    st.markdown("<h2 style='text-align:center;'>🔍 Lacak Laporan</h2>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        npm_input = st.text_input("Masukkan NPM Anda", placeholder="Cari laporan berdasarkan NPM")
        if st.button("Lacak Sekarang") and npm_input:
            if sheet:
                raw = sheet.get_all_values()
                if len(raw) > 1:
                    df = pd.DataFrame(raw[1:], columns=raw[0])
                    res = df[df['NPM'] == npm_input]
                    if not res.empty:
                        for _, row in res.iterrows():
                            s = row['Status']
                            c = "#f59e0b" if s == "Pending" else ("#10b981" if s == "Selesai" else "#3b82f6")
                            st.markdown(f"""
                            <div class="glass-card" style="border-left:8px solid {c}; text-align:left; margin-bottom:15px;">
                                <div style="display:flex; justify-content:space-between;">
                                    <strong>{row['Kategori Masalah']}</strong>
                                    <span style="color:{c}; font-weight:bold;">{s}</span>
                                </div>
                                <p style="font-size:14px; margin:10px 0;">{row['Detail Keluhan']}</p>
                                <small style="color:#94a3b8;">Diterima: {row['Waktu Lapor']}</small>
                            </div>""", unsafe_allow_html=True)
                    else: st.warning("Data tidak ditemukan.")

# =========================================================
# 8. DASHBOARD
# =========================================================
elif selected == "Dashboard":
    st.markdown("<h2 style='text-align:center;'>📊 Analisis Data Crisis</h2>", unsafe_allow_html=True)
    if sheet:
        raw = sheet.get_all_values()
        if len(raw) > 1:
            df = pd.DataFrame(raw[1:], columns=raw[0])
            df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="glass-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Aduan</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="glass-card"><div class="metric-value" style="color:#f59e0b;">{len(df[df["Status"]=="Pending"])}</div><div class="metric-label">Menunggu</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="glass-card"><div class="metric-value" style="color:#10b981;">{len(df[df["Status"]=="Selesai"])}</div><div class="metric-label">Tuntas</div></div>', unsafe_allow_html=True)
            
            st.write("---")
            col_a, col_b = st.columns(2)
            with col_a:
                pie = df['Kategori Masalah'].value_counts()
                fig = go.Figure(data=[go.Pie(labels=pie.index, values=pie.values, hole=.4)])
                fig.update_layout(title="Sebaran Masalah", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                bar = df['Status'].value_counts()
                fig2 = go.Figure([go.Bar(x=bar.index, y=bar.values, marker_color='#3b82f6')])
                fig2.update_layout(title="Status Penyelesaian", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# 9. SADAS BOT
# =========================================================
elif selected == "Sadas Bot":
    st.markdown("<div style='max-width: 800px; margin: auto;'>", unsafe_allow_html=True)
    c_h, c_b = st.columns([4, 1])
    c_h.markdown("<h2 style='margin:0;'>🤖 Sadas Bot</h2><p style='color:#64748b;'>Asisten Virtual Sains Data</p>", unsafe_allow_html=True)
    if c_b.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.write("---")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="chat-message {role}">{m["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Apa yang bisa saya bantu?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-message user">{prompt}</div>', unsafe_allow_html=True)
        
        with st.spinner("Mengetik..."):
            try:
                model = genai.GenerativeModel(get_available_model())
                res = model.generate_content(f"Kamu Sadas Bot, asisten Sains Data UIN RIL. User tanya: {prompt}")
                resp_text = res.text
                st.session_state.messages.append({"role": "assistant", "content": resp_text})
                st.markdown(f'<div class="chat-message bot">{resp_text}</div>', unsafe_allow_html=True)
            except: st.error("AI Error.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 10. ADMIN
# =========================================================
elif selected == "Admin":
    st.markdown("<h2 style='text-align:center;'>🔐 Panel Admin</h2>", unsafe_allow_html=True)
    if not st.session_state.get('is_logged_in', False):
        _, mid, _ = st.columns([1,1,1])
        with mid:
            pwd = st.text_input("Password", type="password")
            if st.button("Masuk"):
                if pwd == "RAHASIA PIKM😭":
                    st.session_state.is_logged_in = True
                    st.rerun()
                else: st.error("Salah!")
    else:
        if st.button("Logout"):
            st.session_state.is_logged_in = False
            st.rerun()
        
        if sheet:
            raw = sheet.get_all_values()
            if len(raw) > 1:
                df = pd.DataFrame(raw[1:], columns=raw[0])
                st.dataframe(df, use_container_width=True)
                
                st.write("### Tindak Lanjut")
                opt = [f"{i} | {r[1]} - {r[4]}" for i, r in enumerate(raw[1:], 2) if r[0]]
                pick = st.selectbox("Pilih Laporan", opt)
                idx = int(pick.split(" | ")[0])
                
                t1, t2 = st.tabs(["Update Status", "AI Letter Generator"])
                with t1:
                    stat = st.selectbox("Status", ["Pending", "Sedang Diproses", "Selesai"])
                    if st.button("Update"):
                        sheet.update_cell(idx, 7, stat)
                        st.success("Updated!")
                with t2:
                    if st.button("Draft with AI"):
                        p, t, i = draft_surat_with_ai(raw[idx-1][4], raw[idx-1][5], raw[idx-1][1])
                        st.session_state.p, st.session_state.t, st.session_state.i = p, t, i
                    
                    per = st.text_input("Perihal", value=st.session_state.get('p',''))
                    tuj = st.text_input("Tujuan", value=st.session_state.get('t',''))
                    isi = st.text_area("Isi", value=st.session_state.get('i',''), height=200)
                    
                    if st.button("Generate PDF"):
                        pdf = create_pdf("001/HMSD/2026", "1 Berkas", per, tuj, isi)
                        st.download_button("Download PDF", pdf, "surat.pdf", "application/pdf")
