import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json, os, datetime, base64
import google.generativeai as genai

# =========================================================
# PAGE CONFIG (WAJIB PALING ATAS)
# =========================================================
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CLEAN MODERN CSS (STABLE)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

#MainMenu, footer, header { display:none !important; }
div[data-testid="stDecoration"] { display:none; }

.stApp {
    background-color:#f8fafc;
}

.block-container {
    max-width:1200px;
    padding-top:30px;
    padding-bottom:40px;
}

/* HEADER */
.app-header {
    display:flex;
    align-items:center;
    gap:16px;
    margin-bottom:32px;
    padding:20px 24px;
    background:white;
    border-radius:14px;
    border:1px solid #e5e7eb;
}

.app-title {
    font-size:22px;
    font-weight:800;
    color:#0f172a;
}

.app-subtitle {
    font-size:13px;
    color:#64748b;
}

/* BUTTON */
.stButton > button {
    width:100%;
    border-radius:10px;
    padding:14px;
    font-weight:600;
    border:none;
    background:#0f172a;
    color:white;
}

.stButton > button:hover {
    background:#334155;
}

/* CHAT */
.chat-user {
    background:#dbeafe;
    padding:12px 16px;
    border-radius:12px;
    margin-bottom:10px;
    max-width:80%;
    align-self:flex-end;
}

.chat-bot {
    background:#f1f5f9;
    padding:12px 16px;
    border-radius:12px;
    margin-bottom:10px;
    max-width:80%;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE SHEET SETUP
# =========================================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_sheet():
    try:
        if "google_credentials" in st.secrets:
            creds = Credentials.from_service_account_info(
                json.loads(st.secrets["google_credentials"]),
                scopes=SCOPES
            )
        else:
            creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        client = gspread.authorize(creds)
        sh = client.open_by_key(ID_SPREADSHEET)
        return sh
    except:
        return None

sh = get_sheet()
sheet_laporan = sh.worksheet("Laporan") if sh else None
sheet_pengumuman = sh.worksheet("Pengumuman") if sh else None

# =========================================================
# GEMINI
# =========================================================
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# =========================================================
# UTIL
# =========================================================
def img_base64(path):
    try:
        with open(path,"rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def render_header():
    logo = img_base64("logo_uin.png")
    st.markdown(f"""
    <div class="app-header">
        {f'<img src="data:image/png;base64,{logo}" height="55">' if logo else ''}
        <div>
            <div class="app-title">SAINS DATA CRISIS CENTER</div>
            <div class="app-subtitle">Pusat Advokasi & Layanan Mahasiswa Terpadu</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# NAVBAR (NON-FIXED, STABLE)
# =========================================================
menu = option_menu(
    None,
    ["Home","Lapor","Status","Data","SadasBot","Admin"],
    icons=["house","send","search","bar-chart","robot","shield-lock"],
    orientation="horizontal",
    styles={
        "container":{"padding":"0","background":"white"},
        "nav-link":{"font-size":"13px","color":"#64748b"},
        "nav-link-selected":{"background":"#eff6ff","color":"#2563eb","font-weight":"bold"}
    }
)

# =========================================================
# HOME
# =========================================================
if menu == "Home":
    render_header()
    st.subheader("👋 Layanan Cepat")

    col1,col2,col3 = st.columns(3)

    with col1:
        if st.button("📢 Pelaporan"):
            st.session_state.page = "Lapor"
            st.rerun()

    with col2:
        if st.button("📊 Transparansi"):
            st.session_state.page = "Data"
            st.rerun()

    with col3:
        if st.button("🤖 Sadas Bot"):
            st.session_state.page = "SadasBot"
            st.rerun()

    st.subheader("📌 Pengumuman Terbaru")
    if sheet_pengumuman:
        for p in reversed(sheet_pengumuman.get_all_records()[-3:]):
            st.info(f"**{p['Judul']}**\n\n{p['Isi']}")
    else:
        st.caption("Belum ada pengumuman.")

# =========================================================
# LAPOR
# =========================================================
elif menu == "Lapor":
    render_header()
    st.subheader("📝 Form Pengaduan")

    with st.form("lapor"):
        nama = st.text_input("Nama")
        npm = st.text_input("NPM")
        kategori = st.selectbox("Kategori",[
            "Akademik","Fasilitas","Keuangan","Bullying","Lainnya"
        ])
        isi = st.text_area("Keluhan",height=150)

        if st.form_submit_button("Kirim"):
            if not nama or not isi:
                st.error("Nama & keluhan wajib diisi.")
            elif sheet_laporan:
                sheet_laporan.append_row([
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    nama,npm,kategori,isi,"Menunggu"
                ])
                st.success("Laporan terkirim.")
            else:
                st.error("Database tidak terhubung.")

# =========================================================
# SADAS BOT
# =========================================================
elif menu == "SadasBot":
    render_header()
    st.subheader("🤖 Sadas Bot")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for c in st.session_state.chat:
        st.markdown(
            f"<div class='{'chat-user' if c['role']=='user' else 'chat-bot'}'>{c['msg']}</div>",
            unsafe_allow_html=True
        )

    if q := st.chat_input("Tanya apa saja..."):
        st.session_state.chat.append({"role":"user","msg":q})

        if "GEMINI_API_KEY" in st.secrets:
            model = genai.GenerativeModel("gemini-1.5-flash")
            r = model.generate_content(q).text
        else:
            r = "API Key belum diatur."

        st.session_state.chat.append({"role":"bot","msg":r})
        st.rerun()

# =========================================================
# DATA
# =========================================================
elif menu == "Data":
    render_header()
    st.subheader("📊 Data Laporan")
    if sheet_laporan:
        df = pd.DataFrame(sheet_laporan.get_all_records())
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Tidak ada data.")

# =========================================================
# ADMIN
# =========================================================
elif menu == "Admin":
    render_header()
    pwd = st.text_input("Password", type="password")
    if pwd == "RAHASIA PIKM😭":
        st.success("Login berhasil.")
