import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import os
import json
import time
import io # <--- INI OBATNYA (Buat bungkus file)

# 1. SETUP HALAMAN
st.set_page_config(page_title="Lapor Masalah", page_icon="📝")

# ==========================================
# 🔄 LOGIKA AUTO-REFRESH & PESAN SUKSES
# ==========================================
if 'pesan_sukses' in st.session_state:
    st.success(st.session_state['pesan_sukses'])
    del st.session_state['pesan_sukses']

# ==========================================
# 🎨 CSS
# ==========================================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); font-family: 'Source Sans 3', sans-serif;}
    [data-testid="stSidebar"] {background-color: #0f172a; border-right: 1px solid #1e293b;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
        border-radius: 8px; border: 1px solid #cbd5e1; background-color: white; color: #334155;
    }
    .stButton > button {background-color: #2563eb; color: white; border-radius: 8px; height: 50px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI GOOGLE
# ==========================================
# Pastikan ID Folder ini BENAR (Cek Link Browser saat buka folder Drive)
ID_FOLDER_DRIVE = "1n7n4NNuQiGMsSjHynqwD-aMRvO0W-K4n" 
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
    service_drive = build('drive', 'v3', credentials=creds)
    
except Exception as e:
    st.error(f"⚠️ Koneksi Gagal: {e}")
    st.stop()

# ==========================================
# FORMULIR
# ==========================================
st.title("📝 Form Pengaduan")

with st.form("form_lapor", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 Data Diri")
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
    with col2:
        st.markdown("### 🚨 Detail")
        kategori = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        bukti_file = st.file_uploader("Upload Bukti", type=["png", "jpg", "jpeg", "pdf"])
        
    keluhan = st.text_area("Deskripsi Masalah", height=150)
    tombol_kirim = st.form_submit_button("Kirim Laporan 🚀")

    if tombol_kirim:
        if not keluhan:
            st.warning("Mohon isi deskripsi keluhan.")
        else:
            with st.spinner("Mengupload data & file..."):
                waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                link_bukti = "-" 
                
                # --- LOGIKA UPLOAD FIX ---
                if bukti_file is not None:
                    try:
                        # 1. Konversi File Streamlit ke Bytes Murni (Biar Drive mau terima)
                        file_buffer = io.BytesIO(bukti_file.getvalue())
                        
                        # 2. Siapkan Metadata
                        ext = bukti_file.name.split('.')[-1]
                        nama_file_drive = f"Bukti_{nama.replace(' ','_')}_{waktu.replace('/','-').replace(':','-')}.{ext}"
                        file_metadata = {'name': nama_file_drive, 'parents': [ID_FOLDER_DRIVE]}
                        
                        # 3. Upload Pakai MediaIoBaseUpload
                        media = MediaIoBaseUpload(file_buffer, mimetype=bukti_file.type)
                        
                        file = service_drive.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id, webViewLink',
                            supportsAllDrives=True
                        ).execute()
                        
                        link_bukti = file.get('webViewLink')
                        
                    except Exception as e:
                        st.error(f"❌ Gagal Upload File: {e}")
                        # Kita stop biar Lia tau kalau gagalnya di sini
                        st.stop() 
                
                # --- SIMPAN KE SHEETS ---
                try:
                    data_baru = [waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti]
                    sheet.append_row(data_baru)
                    
                    # Simpan pesan sukses + Linknya biar bisa dicek
                    pesan = "✅ Laporan Berhasil Dikirim!"
                    if link_bukti != "-":
                        pesan += f" (Bukti Foto Terupload)"
                        
                    st.session_state['pesan_sukses'] = pesan
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Gagal Simpan Database: {e}")
