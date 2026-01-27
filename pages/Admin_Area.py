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

# Password Admin (Bisa diganti sesuka hati)
PASSWORD_ADMIN = "RAHASIA PIKM😭"

# ==========================================
# 🎨 CSS PREMIUM
# ==========================================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    [data-testid="stSidebar"] {background-color: #1e293b; border-right: 2px solid #334155;}
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
    st.rerun()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("🔐 Admin Panel")
    if not st.session_state['is_logged_in']:
        input_pass = st.text_input("Masukkan Password", type="password")
        if st.button("Login Masuk"):
            if input_pass == PASSWORD_ADMIN:
                login()
            else:
                st.error("Password Salah!")
    else:
        st.success(f"Halo, Admin!")
        if st.button("🚪 Logout"):
            logout()

# ==========================================
# DASHBOARD ADMIN
# ==========================================
if st.session_state['is_logged_in']:
    st.title("⚡ Dashboard Admin")

    # 1. KONEKSI DATABASE (METODE ID)
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else:
            st.error("⚠️ File Credentials tidak ditemukan!")
            st.stop()

        client = gspread.authorize(creds)
        
        # --- PERBAIKAN DI SINI (PAKAI ID) ---
        sheet = client.open_by_key(ID_SPREADSHEET).worksheet("Laporan")

    except Exception as e:
        st.error(f"Database Error: {e}")
        st.stop()

    # 2. AMBIL DATA
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Kita ambil semua data
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    # --- 🧹 PROSES PEMBERSIHAN DATA ---
    if not df.empty:
        # 1. Simpan No. Baris Asli (Excel mulai dari baris 2 karena header baris 1)
        # Ini penting biar pas diedit gak salah kamar
        df['No. Baris'] = range(2, len(df) + 2)

        # 2. FILTER: Buang baris yang kosong (Waktu Lapor kosong)
        if 'Waktu Lapor' in df.columns:
            # Pastikan jadi string dulu biar aman
            df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]

        # 3. Rapikan urutan kolom (No Baris di depan)
        cols = ['No. Baris'] + [c for c in df.columns if c != 'No. Baris']
        df = df[cols]

    # --- TAMPILKAN STATISTIK ---
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Laporan", len(df))
        if 'Status' in df.columns:
            c2.metric("Pending", len(df[df['Status'] == 'Pending']))
            c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
        
        st.write("---")
        
        # --- TABEL DATA ---
        st.dataframe(df, use_container_width=True)

        # --- FITUR UPDATE STATUS ---
        st.write("### ✏️ Edit Status Laporan")
        
        if 'Status' in df.columns:
            # Cari posisi kolom 'Status' di Spreadsheet (buat update_cell)
            try:
                headers = sheet.row_values(1) 
                col_status_idx = headers.index("Status") + 1 
            except:
                st.error("Kolom 'Status' tidak ditemukan di Google Sheets!")
                st.stop()

            with st.form("form_edit"):
                c_pilih, c_status = st.columns([2, 1])
                
                with c_pilih:
                    # Dropdown pilih nomor baris
                    nomor_dipilih = st.selectbox(
                        "Pilih No. Baris (Lihat kolom pertama tabel):", 
                        df['No. Baris'].tolist()
                    )
                    
                    # Tampilkan Nama biar admin yakin
                    row_data = df[df['No. Baris'] == nomor_dipilih].iloc[0]
                    nama_pelapor = row_data['Nama'] if 'Nama' in row_data else "Tanpa Nama"
                    st.info(f"Mengedit Data: **{nama_pelapor}** (NPM: {row_data.get('NPM', '-')})")

                with c_status:
                    status_sekarang = row_data['Status'] if 'Status' in row_data else "Pending"
                    opsi = ["Pending", "Proses", "Selesai", "Ditolak"]
                    
                    # Set default value dropdown sesuai status sekarang
                    idx_awal = opsi.index(status_sekarang) if status_sekarang in opsi else 0
                    
                    status_baru = st.selectbox("Ubah Status:", opsi, index=idx_awal)

                tombol = st.form_submit_button("💾 Simpan Perubahan")

                if tombol:
                    try:
                        # UPDATE KE GOOGLE SHEET
                        sheet.update_cell(nomor_dipilih, col_status_idx, status_baru)
                        
                        st.success(f"✅ Berhasil! Laporan {nama_pelapor} diubah jadi '{status_baru}'")
                        time.sleep(1)
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal Simpan: {e}")
    else:
        st.info("Belum ada data laporan yang masuk.")

else:
    st.warning("Silakan login di sidebar sebelah kiri.")
