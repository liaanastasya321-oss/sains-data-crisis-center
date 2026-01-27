import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import time

st.set_page_config(page_title="Admin Area", page_icon="🔐", layout="wide")

# ==========================================
# 🔐 SESSION STATE
# ==========================================
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

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
        st.success(f"Halo, {PASSWORD_ADMIN}!")
        if st.button("🚪 Logout"):
            logout()

# ==========================================
# DASHBOARD ADMIN
# ==========================================
if st.session_state['is_logged_in']:
    st.title("⚡ Dashboard Admin")

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

    # 2. AMBIL & BERSIHKAN DATA (LOGIKA BARU)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    # --- 🧹 PROSES PEMBERSIHAN DATA ---
    if not df.empty:
        # 1. Simpan Index Asli (No. Baris Google Sheet) SEBELUM filter
        #    Supaya walaupun baris kosong dibuang, nomor baris data asli tetap benar (2, 3, dst)
        df['No. Baris'] = range(2, len(df) + 2)

        # 2. FILTER: Buang baris yang 'Waktu Lapor'-nya kosong
        if 'Waktu Lapor' in df.columns:
            df = df[df['Waktu Lapor'].astype(str).str.strip() != ""]

        # 3. Pindahkan 'No. Baris' ke kolom paling depan biar enak dilihat
        cols = ['No. Baris'] + [c for c in df.columns if c != 'No. Baris']
        df = df[cols]

    # --- TAMPILKAN STATISTIK (Angka pasti 1 sekarang) ---
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Laporan", len(df)) # Pasti sesuai jumlah data asli
        if 'Status' in df.columns:
            c2.metric("Pending", len(df[df['Status'] == 'Pending']))
            c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
        
        st.write("---")
        
        # --- TAMPILAN TABEL ---
        st.dataframe(df, use_container_width=True)

        # --- FITUR UPDATE STATUS ---
        st.write("### ✏️ Edit Status Laporan")
        
        if 'Status' in df.columns:
            # Cari kolom Status index-nya berapa di Google Sheets (Asli)
            # Karena di df kita sudah geser-geser kolom, kita cari manual aja yang aman
            # Biasanya di Google Sheet kamu: A=Waktu, B=Nama... G=Status (Kolom ke-7)
            # Tapi biar aman kita cari nama header di sheet langsung kalau bisa, 
            # atau pake asumsi data yang ditarik.
            
            # Cara paling aman: Cari index 'Status' dari dataframe RAW data (sebelum ditambah kolom No Baris)
            # Tapi karena df sudah berubah, kita pakai logika df.columns aja tapi dikurangi 1 (karena ada No Baris)
            # ATAU: Kita cari posisi "Status" di list headers
            headers = sheet.row_values(1) # Ambil baris pertama (Judul)
            try:
                # +1 karena gspread mulai hitung dari 1
                col_status_idx = headers.index("Status") + 1 
            except:
                st.error("Kolom 'Status' tidak ditemukan di Google Sheets!")
                st.stop()

            with st.form("form_edit"):
                c_pilih, c_status = st.columns([2, 1])
                
                with c_pilih:
                    # Dropdown Pilih No Baris (Hanya muncul yang datanya ada!)
                    nomor_dipilih = st.selectbox(
                        "Pilih No. Baris (Lihat kolom pertama tabel):", 
                        df['No. Baris'].tolist()
                    )
                    
                    # Ambil Nama untuk Konfirmasi
                    # Kita cari di dataframe baris mana yang punya No. Baris tersebut
                    row_data = df[df['No. Baris'] == nomor_dipilih].iloc[0]
                    nama_pelapor = row_data['Nama'] if 'Nama' in row_data else "Tanpa Nama"
                    st.info(f"Mengedit Data: **{nama_pelapor}**")

                with c_status:
                    status_sekarang = row_data['Status'] if 'Status' in row_data else "Pending"
                    opsi = ["Pending", "Proses", "Selesai", "Ditolak"]
                    idx_awal = opsi.index(status_sekarang) if status_sekarang in opsi else 0
                    
                    status_baru = st.selectbox("Ubah Status:", opsi, index=idx_awal)

                tombol = st.form_submit_button("💾 Simpan Perubahan")

                if tombol:
                    try:
                        # UPDATE LANGSUNG KE ALAMAT YANG TEPAT
                        sheet.update_cell(nomor_dipilih, col_status_idx, status_baru)
                        st.success(f"✅ Berhasil! Status {nama_pelapor} (Baris {nomor_dipilih}) jadi '{status_baru}'")
                        time.sleep(1)
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal Simpan: {e}")
    else:
        st.info("Belum ada data laporan yang masuk.")

else:
    st.warning("Silakan login di sidebar.")

