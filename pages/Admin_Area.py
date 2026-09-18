import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import time

st.set_page_config(page_title="Admin Area", page_icon="🔐", layout="wide")

ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g"

if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

if 'kahim_logged_in' not in st.session_state:
    st.session_state['kahim_logged_in'] = False

PASSWORD_ADMIN = "RAHASIA PIKM😭"
PASSWORD_KAHIM = "RAHASIA_KAHIM2026"  # Password untuk membuka laporan khusus kahim

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

with st.sidebar:
    st.header("🔐 Admin Panel")
    if not st.session_state['is_logged_in']:
        input_pass = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if input_pass == PASSWORD_ADMIN:
                st.session_state['is_logged_in'] = True
                st.rerun()
            else:
                st.error("Password Salah!")
    else:
        st.success("Admin Terautentikasi")
        if st.button("🚪 Logout"):
            st.session_state['is_logged_in'] = False
            st.session_state['kahim_logged_in'] = False
            st.rerun()

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

if st.session_state['is_logged_in']:
    st.title("⚡ Dashboard Admin & Pimpinan")

    # Dua Tab Menu Utama di Admin
    tab_publik, tab_kahim = st.tabs(["📋 Laporan Publik", "👑 Laporan Khusus Kahim / Pejabat"])

    with tab_publik:
        st.subheader("Manajemen Pengaduan Publik (Fasilitas & Akademik)")
        sheet = get_google_sheet("Laporan")

        if st.button("🔄 Refresh Data Publik"):
            st.rerun()

        try:
            data = sheet.get_all_records() if sheet else []
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

            st.write("### ✏️ Edit Status Laporan Publik")
            if 'Status' in df.columns:
                try:
                    headers = sheet.row_values(1) 
                    col_status_idx = headers.index("Status") + 1 
                except:
                    col_status_idx = None

                if col_status_idx:
                    with st.form("form_edit_status"):
                        c_pilih, c_status = st.columns([2, 1])
                        with c_pilih:
                            nomor_dipilih = st.selectbox("Pilih No. Baris:", df['No. Baris'].tolist())
                            row_data = df[df['No. Baris'] == nomor_dipilih].iloc[0]
                            nama_pelapor = row_data.get('Nama Mahasiswa', row_data.get('Nama', 'Tanpa Nama'))
                            st.info(f"Mengedit Data: **{nama_pelapor}**")
                        with c_status:
                            status_sekarang = row_data['Status']
                            opsi = ["Pending", "Proses", "Selesai", "Ditolak"]
                            idx_awal = opsi.index(status_sekarang) if status_sekarang in opsi else 0
                            status_baru = st.selectbox("Ubah Status:", opsi, index=idx_awal)

                        if st.form_submit_button("💾 Simpan Status"):
                            sheet.update_cell(nomor_dipilih, col_status_idx, status_baru)
                            st.success("✅ Status berhasil diperbarui!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("Belum ada laporan publik.")

    with tab_kahim:
        st.subheader("🔒 Area Rahasia: Laporan & Aspirasi Terkait Kahim / Azwar")
        st.markdown("Menu ini tersembunyi dan memerlukan **Password Khusus Pimpinan** agar bisa melihat isinya.")

        if not st.session_state['kahim_logged_in']:
            st.markdown("<div style='max-width: 400px; padding: 20px; background: white; border-radius: 10px; border: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
            with st.form("form_pwd_kahim"):
                pass_input = st.text_input("Masukkan Password Khusus Kahim", type="password")
                btn_buka = st.form_submit_button("Buka Data Kahim")
                if btn_buka:
                    if pass_input == PASSWORD_KAHIM:
                        st.session_state['kahim_logged_in'] = True
                        st.rerun()
                    else:
                        st.error("Password Khusus Salah!")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            if st.button("🔒 Kunci Kembali Data Kahim"):
                st.session_state['kahim_logged_in'] = False
                st.rerun()

            st.write("---")
            sheet_kahim = get_google_sheet("Aspirasi_Kahim")
            if sheet_kahim:
                try:
                    data_k = sheet_kahim.get_all_records()
                    df_k = pd.DataFrame(data_k)
                except:
                    df_k = pd.DataFrame()

                if not df_k.empty:
                    st.success("✅ Berhasil memuat data laporan khusus kahim.")
                    st.dataframe(df_k, use_container_width=True, hide_index=True)
                    st.metric("Total Aspirasi/Laporan Kahim", len(df_k))
                else:
                    st.info("Belum ada laporan atau aspirasi yang masuk untuk Kahim/Azwar.")
            else:
                st.warning("⚠️ Worksheet 'Aspirasi_Kahim' belum dibuat di Google Sheets.")

else:
    st.warning("⚠️ Silakan login menggunakan password admin di sidebar sebelah kiri.")
