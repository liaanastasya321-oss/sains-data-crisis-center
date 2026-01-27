import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import time

st.set_page_config(page_title="Admin Area", page_icon="🔐", layout="wide")

# ==========================================
# 🔐 SESSION STATE (BIAR GAK LOGOUT SENDIRI)
# ==========================================
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

# Password Hardcode (Sesuai requestmu)
PASSWORD_ADMIN = "GHUFRON"

# ==========================================
# 🎨 CSS PREMIUM
# ==========================================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    [data-testid="stSidebar"] {background-color: #1e293b; border-right: 2px solid #334155;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}
    h1 {color: #1e3a8a; font-family: 'Helvetica', sans-serif; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);}
    div[data-testid="stDataFrame"] {border: 1px solid #cbd5e1; border-radius: 10px; overflow: hidden; background: white;}
    div.stButton > button {
        background-color: #2563eb; color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNGSI LOGIN & LOGOUT
# ==========================================
def login():
    st.session_state['is_logged_in'] = True
    st.rerun()

def logout():
    st.session_state['is_logged_in'] = False
    st.rerun()

# ==========================================
# HALAMAN LOGIN (SIDEBAR)
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
        st.success(f"Halo, {PASSWORD_ADMIN}!")
        if st.button("🚪 Logout"):
            logout()

# ==========================================
# LOGIKA UTAMA (HANYA MUNCUL JIKA LOGIN)
# ==========================================
if st.session_state['is_logged_in']:
    st.title("⚡ Dashboard Admin")
    st.markdown("Kelola data laporan masuk dan update status penanganan.")

    # 1. KONEKSI DATABASE
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        elif os.path.exists("../credentials.json"):
            creds = Credentials.from_service_account_file("../credentials.json", scopes=scopes)
        else:
            st.error("⚠️ File Credentials tidak ditemukan!")
            st.stop()

        client = gspread.authorize(creds)
        sheet = client.open("Database_Advokasi").worksheet("Laporan")

    except Exception as e:
        st.error(f"Database Error: {e}")
        st.stop()

    # 2. AMBIL DATA
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        # Tampilkan Statistik
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Laporan", len(df))
        if 'Status' in df.columns:
            c2.metric("Pending", len(df[df['Status'] == 'Pending']))
            c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))

        st.write("---")
        
        # 3. PERSIAPAN DATA UPDATE (PENTING!)
        # Kita simpan index kolom 'Status' YANG ASLI sebelum tabel dimodifikasi buat tampilan
        # +1 karena Google Sheets mulai dari kolom 1, bukan 0
        if 'Status' in df.columns:
            kolom_status_index_asli = df.columns.get_loc("Status") + 1
        else:
            st.error("Kolom 'Status' tidak ditemukan di Database!")
            st.stop()

        # Modifikasi Tampilan (Tambah Nomor Baris untuk User)
        df_display = df.copy()
        # Baris di GSheets mulai dari 2 (karena 1 itu Header)
        df_display.insert(0, 'No. Baris', range(2, len(df) + 2)) 
        
        st.dataframe(df_display, use_container_width=True)

        # 4. FORM UPDATE STATUS
        st.write("### ✏️ Edit Status Laporan")
        
        with st.form("form_edit"):
            c_pilih, c_status = st.columns([2, 1])
            
            with c_pilih:
                # User memilih berdasarkan Nomor Baris
                nomor_pilihan = st.selectbox(
                    "Pilih Nomor Baris (Lihat kolom paling kiri):", 
                    df_display['No. Baris'].tolist()
                )
                
                # Cari data nama untuk preview
                # Kita kurangi 2 untuk dapat index Python (Baris 2 -> Index 0)
                idx_python = nomor_pilihan - 2
                nama_pelapor = df.iloc[idx_python]['Nama'] if 'Nama' in df.columns else "Tanpa Nama"
                keluhan_pelapor = df.iloc[idx_python]['Detail Keluhan'] if 'Detail Keluhan' in df.columns else "-"
                
                st.info(f"Mengedit: **{nama_pelapor}** - {keluhan_pelapor}")

            with c_status:
                status_opsi = ["Pending", "Proses", "Selesai", "Ditolak"]
                status_sekarang = df.iloc[idx_python]['Status']
                
                # Pastikan status sekarang ada di list opsi biar gak error
                index_default = 0
                if status_sekarang in status_opsi:
                    index_default = status_opsi.index(status_sekarang)
                
                status_baru = st.selectbox("Status Baru:", status_opsi, index=index_default)

            tombol_simpan = st.form_submit_button("💾 Simpan Perubahan ke Database")

            if tombol_simpan:
                try:
                    # UPDATE KE GOOGLE SHEETS
                    # nomor_pilihan = Baris (Row)
                    # kolom_status_index_asli = Kolom (Col)
                    sheet.update_cell(nomor_pilihan, kolom_status_index_asli, status_baru)
                    
                    st.success(f"✅ Berhasil! Data {nama_pelapor} diubah jadi '{status_baru}'")
                    st.cache_data.clear()
                    time.sleep(1) # Jeda dikit biar user baca suksesnya
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan: {e}")

    else:
        st.info("Data kosong.")

else:
    # TAMPILAN JIKA BELUM LOGIN
    st.title("⛔ Akses Ditolak")
    st.warning("Silakan login melalui Sidebar di sebelah kiri.")
