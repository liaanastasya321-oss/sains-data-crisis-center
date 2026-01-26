import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json # <--- Wajib ada buat baca Secrets

st.set_page_config(page_title="Admin Area", page_icon="🔐", layout="wide")

# ==========================================
# BAGIAN DESAIN (CSS PREMIUM) 🎨
# ==========================================
st.markdown("""
<style>
    /* Background Gradient Halus */
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}

    /* Sidebar Keren */
    [data-testid="stSidebar"] {background-color: #1e293b; border-right: 2px solid #334155;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}

    /* Judul Besar */
    h1 {color: #1e3a8a; font-family: 'Helvetica', sans-serif; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);}

    /* Tabel Data */
    div[data-testid="stDataFrame"] {border: 1px solid #cbd5e1; border-radius: 10px; overflow: hidden;}
    
    /* Tombol Update */
    div.stButton > button {
        background-color: #2563eb; color: white; border-radius: 8px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER HALAMAN
# ==========================================
st.title("🔐 Halaman Khusus Admin")
st.markdown("Kelola data laporan masuk dan update status penanganan.")

# ==========================================
# LOGIN ADMIN
# ==========================================
# Sidebar Login
with st.sidebar:
    st.header("🔑 Verifikasi")
    password = st.text_input("Password Admin", type="password")
    
    # Tombol Logout (Reset)
    if st.button("🚪 Logout"):
        st.cache_data.clear()
        st.rerun() # Ganti experimental_rerun jadi rerun (versi baru streamlit)

# Cek Password
if password == "GHUFRON":
    
    # ==========================================
    # KONEKSI DATABASE (DUAL MODE: CLOUD & LOKAL) 🔗
    # ==========================================
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    try:
        # 1. Cek apakah ada di Streamlit Cloud (Pakai Secrets)
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
        # 2. Cek apakah ada file lokal credentials.json
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        
        # 3. Cek di folder luar (opsional)
        elif os.path.exists("../credentials.json"):
            creds = Credentials.from_service_account_file("../credentials.json", scopes=scopes)
            
        else:
            st.error("⚠️ File Kunci (Credentials) tidak ditemukan!")
            st.stop()

        # Buka Koneksi ke Sheet "Laporan"
        client = gspread.authorize(creds)
        sheet = client.open("Database_Advokasi").worksheet("Laporan")
        
    except Exception as e:
        st.error(f"Gagal koneksi database: {e}")
        st.stop()

    st.success("✅ Akses Diterima: Mode Administrator")

    # ==========================================
    # TAMPILKAN DATA
    # ==========================================
    # Tombol Refresh
    col_ref, col_space = st.columns([1, 5])
    if col_ref.button("🔄 Refresh Data Terbaru"):
        st.cache_data.clear()

    # Ambil Data
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        # Tampilkan Statistik Singkat
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Laporan", len(df))
        # Pastikan kolom Status ada
        if 'Status' in df.columns:
            c2.metric("Perlu Tindakan (Pending)", len(df[df['Status'] == 'Pending']))
            c3.metric("Masalah Selesai", len(df[df['Status'] == 'Selesai']))
        
        st.write("### 📋 Database Lengkap")
        
        # Tambahkan kolom 'Nomor Baris' biar gampang update
        # (Google Sheets mulai dari baris 2 untuk data, karena baris 1 itu Header)
        df['Nomor Baris'] = range(2, len(df) + 2)
        
        # Pindahkan kolom 'Nomor Baris' ke paling depan
        cols = ['Nomor Baris'] + [col for col in df.columns if col != 'Nomor Baris']
        df = df[cols]
        
        st.dataframe(df, use_container_width=True)
        
        st.write("---")
        
        # ==========================================
        # FITUR UPDATE STATUS (ACTION) ⚡
        # ==========================================
        st.subheader("⚡ Update Status Laporan")
        with st.form("form_update"):
            c_id, c_status = st.columns(2)
            
            with c_id:
                # Pilih Nomor Baris
                nomor_baris = st.selectbox("Pilih Nomor Baris (Lihat tabel di atas):", df['Nomor Baris'].tolist())
                
                # Tampilkan info singkat baris yang dipilih
                if not df[df['Nomor Baris'] == nomor_baris].empty:
                    # Ambil nama kolom secara dinamis biar gak error kalau nama kolom beda dikit
                    col_nama = 'Nama' if 'Nama' in df.columns else 'Nama Mahasiswa'
                    col_masalah = 'Kategori' if 'Kategori' in df.columns else 'Kategori Masalah'
                    
                    # Cek keberadaan kolom sebelum akses
                    val_nama = df[df['Nomor Baris'] == nomor_baris][col_nama].values[0] if col_nama in df.columns else "Tanpa Nama"
                    val_masalah = df[df['Nomor Baris'] == nomor_baris][col_masalah].values[0] if col_masalah in df.columns else "-"
                    
                    st.info(f"Mengedit Data: **{val_nama}** - {val_masalah}")
                
            with c_status:
                status_baru = st.selectbox("Ubah Status Menjadi:", ["Pending", "Proses", "Selesai"])
            
            tombol_update = st.form_submit_button("Simpan Perubahan 💾")
            
            if tombol_update:
                try:
                    # Cari lokasi Kolom 'Status' (Index + 1 karena gspread base-1)
                    kolom_status_index = df.columns.get_loc("Status") + 1 
                    
                    # Update Cells di Google Sheets
                    sheet.update_cell(nomor_baris, kolom_status_index, status_baru)
                    
                    st.success(f"Berhasil update status jadi: {status_baru}")
                    st.cache_data.clear() # Reset cache biar tabel update
                    st.rerun() # Refresh otomatis
                    
                except Exception as e:
                    st.error(f"Gagal update: {e}")

    else:
        st.info("Belum ada data laporan masuk.")

elif password != "":
    st.error("❌ Password Salah! Coba lagi.")
else:
    st.info("👋 Silakan login di menu sebelah kiri (Sidebar) untuk mengakses data.")

