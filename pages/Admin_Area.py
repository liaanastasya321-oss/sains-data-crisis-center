import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import time

st.set_page_config(page_title="Admin Area", page_icon="🔐", layout="wide")

# ==========================================
# 👇 ID SPREADSHEET (WAJIB ADA)
# ==========================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g"

# ==========================================
# 🔐 SESSION STATE (Login System)
# ==========================================
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

if 'kahim_logged_in' not in st.session_state:
    st.session_state['kahim_logged_in'] = False

# Password Admin & Password Khusus Pimpinan/Kahim
PASSWORD_ADMIN = "RAHASIA PIKM😭"
PASSWORD_KAHIM = "RAHASIA_KAHIM2026"  # Bisa kamu ubah sesuai keinginan

# ==========================================
# 🎨 CSS PREMIUM
# ==========================================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    [data-testid="stSidebar"] {background-color: #0f172a; border-right: 2px solid #334155;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}
    h1 {color: #1e3a8a; font-family: 'Helvetica', sans-serif;}
    div[data-testid="stDataFrame"] {background: white; border-radius: 10px; overflow: hidden;}
    div.stButton > button {
        background-color: #2563eb; color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNGSI LOGIN/LOGOUT
# ==========================================
def login():
    st.session_state['is_logged_in'] = True
    st.rerun()

def logout():
    st.session_state['is_logged_in'] = False
    st.session_state['kahim_logged_in'] = False
    st.rerun()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("🔐 Admin Panel")
    if not st.session_state['is_logged_in']:
        input_pass = st.text_input("Password Admin Umum", type="password")
        if st.button("Login Admin"):
            if input_pass == PASSWORD_ADMIN:
                login()
            else:
                st.error("Password Salah!")
    else:
        st.success("Halo, Admin Terautentikasi!")
        if st.button("🚪 Logout Semua"):
            logout()

# ==========================================
# KONEKSI GOOGLE SHEETS HELPER
# ==========================================
def get_google_sheet(sheet_name):
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else:
            return None
        client = gspread.authorize(creds)
        return client.open_by_key(ID_SPREADSHEET).worksheet(sheet_name)
    except:
        return None

# ==========================================
# DASHBOARD UTAMA ADMIN
# ==========================================
if st.session_state['is_logged_in']:
    st.title("⚡ Dashboard Admin & Pimpinan HMSD")

    # Membuat Sistem Tab di dalam Admin Area agar rapi
    tab_laporan, tab_aspirasi = st.tabs(["📋 Manajemen Laporan Publik", "👑 Aspirasi & Kritik Pejabat (Suara Kahim)"])

    # ==========================================
    # TAB 1: MANAJEMEN LAPORAN PUBLIK
    # ==========================================
    with tab_laporan:
        st.subheader("Kelola Pengaduan Fasilitas & Akademik")
        sheet_laporan = get_google_sheet("Laporan")

        if st.button("🔄 Refresh Data Laporan"):
            st.rerun()

        if sheet_laporan:
            try:
                data = sheet_laporan.get_all_records()
                df = pd.DataFrame(data)
            except:
                df = pd.DataFrame()

            if not df.empty:
                df['No. Baris'] = range(2, len(df) + 2)
                if 'Waktu Lapor' in df.columns:
                    df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]
                cols = ['No. Baris'] + [c for c in df.columns if c != 'No. Baris']
                df = df[cols]

                c1, c2, c3 = st.columns(3)
                c1.metric("Total Laporan", len(df))
                if 'Status' in df.columns:
                    c2.metric("Pending", len(df[df['Status'] == 'Pending']))
                    c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
                
                st.write("---")
                st.dataframe(df, use_container_width=True)

                st.write("### ✏️ Edit Status Laporan")
                if 'Status' in df.columns:
                    try:
                        headers = sheet_laporan.row_values(1) 
                        col_status_idx = headers.index("Status") + 1 
                    except:
                        col_status_idx = None

                    if col_status_idx:
                        with st.form("form_edit_laporan"):
                            c_pilih, c_status = st.columns([2, 1])
                            with c_pilih:
                                nomor_dipilih = st.selectbox("Pilih No. Baris:", df['No. Baris'].tolist())
                                row_data = df[df['No. Baris'] == nomor_dipilih].iloc[0]
                                nama_pelapor = row_data['Nama'] if 'Nama' in row_data else "Tanpa Nama"
                                st.info(f"Mengedit Data: **{nama_pelapor}** (NPM: {row_data.get('NPM', '-')})")
                            with c_status:
                                status_sekarang = row_data['Status'] if 'Status' in row_data else "Pending"
                                opsi = ["Pending", "Proses", "Selesai", "Ditolak"]
                                idx_awal = opsi.index(status_sekarang) if status_sekarang in opsi else 0
                                status_baru = st.selectbox("Ubah Status:", opsi, index=idx_awal)

                            if st.form_submit_button("💾 Simpan Perubahan Status"):
                                try:
                                    sheet_laporan.update_cell(nomor_dipilih, col_status_idx, status_baru)
                                    st.success(f"✅ Berhasil! Laporan {nama_pelapor} diubah jadi '{status_baru}'")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Gagal Simpan: {e}")
            else:
                st.info("Belum ada data laporan publik.")
        else:
            st.error("Gagal terhubung ke worksheet 'Laporan'.")

    # ==========================================
    # TAB 2: ASPIRASI & KRITIK PEJABAT (SUARA KAHIM) - DENGAN PASSWORD KKHUSUS
    # ==========================================
    with tab_aspirasi:
        st.subheader("🔒 Kotak Aspirasi & Kritik Rahasia Pejabat HMSD")
        st.markdown("Area ini khusus memuat kritik, saran, dan aspirasi mahasiswa yang ditujukan kepada Kahim, Wakahim, dan pengurus inti.")

        # Cek apakah sudah login khusus kahim/pimpinan
        if not st.session_state['kahim_logged_in']:
            st.markdown("<div style='max-width: 400px; padding: 20px; background: white; border-radius: 10px; border: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
            with st.form("form_login_kahim"):
                st.write("#### Autentikasi Khusus Pimpinan")
                pwd_kahim = st.text_input("Masukkan Password Khusus Pejabat/Kahim", type="password")
                btn_kahim_login = st.form_submit_button("Buka Kotak Aspirasi")
                
                if btn_kahim_login:
                    if pwd_kahim == PASSWORD_KAHIM:
                        st.session_state['kahim_logged_in'] = True
                        st.rerun()
                    else:
                        st.error("Password Pejabat Salah!")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            col_inf, col_out = st.columns([6, 1])
            with col_out:
                if st.button("🔒 Kunci Lagi"):
                    st.session_state['kahim_logged_in'] = False
                    st.rerun()

            sheet_aspirasi = get_google_sheet("Aspirasi_Kahim")
            if sheet_aspirasi:
                try:
                    data_asp = sheet_aspirasi.get_all_records()
                    df_asp = pd.DataFrame(data_asp)
                except:
                    df_asp = pd.DataFrame()

                if not df_asp.empty:
                    st.success("✅ Berhasil memuat data Aspirasi & Kritik Pejabat.")
                    
                    # Filter berdasarkan tujuan pejabat jika kolomnya ada
                    if 'Tujuan Pejabat' in df_asp.columns:
                        list_tujuan = ["Semua Pimpinan"] + list(df_asp['Tujuan Pejabat'].unique())
                        pilih_tujuan = st.selectbox("Filter Berdasarkan Tujuan Pimpinan:", list_tujuan)
                        if pilih_tujuan != "Semua Pimpinan":
                            df_asp_filtered = df_asp[df_asp['Tujuan Pejabat'] == pilih_tujuan]
                        else:
                            df_asp_filtered = df_asp
                    else:
                        df_asp_filtered = df_asp

                    st.dataframe(df_asp_filtered, use_container_width=True, hide_index=True)
                    st.metric("Total Aspirasi Masuk ke Pimpinan", len(df_asp))
                else:
                    st.info("Belum ada aspirasi atau kritik rahasia yang masuk ke worksheet 'Aspirasi_Kahim'.")
            else:
                st.warning("⚠️ Worksheet dengan nama 'Aspirasi_Kahim' tidak ditemukan di Google Sheets. Pastikan kamu sudah membuatnya.")

else:
    st.warning("⚠️ Silakan login menggunakan Password Admin di sidebar sebelah kiri untuk mengakses panel ini.")
