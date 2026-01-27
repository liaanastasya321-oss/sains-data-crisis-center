import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import os
import json
import time
import io

# ==========================================
# 👇 ID PASTI (ANTI NYASAR)
# ==========================================
# ID Spreadsheet yang kamu kasih tadi
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 

# ID Folder Drive (Tempat simpan foto)
ID_FOLDER_DRIVE = "1GZkCVwmJ16RFmKGPnIMSHpJyI8JHYiVS"

# 1. SETUP HALAMAN
st.set_page_config(page_title="Lapor Masalah", page_icon="📝")

# 2. CSS (Tampilan)
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

# 3. KONEKSI GOOGLE (METODE ID)
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
    
    # Buka Spreadsheet pakai ID (Pasti Ketemu)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(ID_SPREADSHEET).worksheet("Laporan")
    
    # Siapkan Drive API
    service_drive = build('drive', 'v3', credentials=creds)
    
except Exception as e:
    st.error(f"⚠️ Koneksi Gagal: {e}")
    st.info("Tips: Pastikan email robot sudah di-SHARE sebagai EDITOR di Spreadsheet & Folder Drive.")
    st.stop()

# 4. FORMULIR
st.title("📝 Form Pengaduan")

# Cek pesan sukses dari reload sebelumnya
if 'pesan_sukses' in st.session_state:
    st.success(st.session_state['pesan_sukses'])
    del st.session_state['pesan_sukses']

with st.form("form_lapor", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
    with c2:
        kategori = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        bukti_file = st.file_uploader("Upload Bukti", type=["png", "jpg", "jpeg", "pdf"])
        
    keluhan = st.text_area("Deskripsi Masalah", height=150)
    tombol = st.form_submit_button("Kirim Laporan 🚀")

    if tombol:
        if not keluhan:
            st.warning("Mohon isi deskripsi masalah.")
        else:
            with st.spinner("Sedang mengirim..."):
                waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                link_bukti = "-" 
                
                # --- LOGIKA UPLOAD DRIVE (FIX BYTESIO) ---
                if bukti_file:
                    try:
                        # Convert file biar Drive mau terima
                        file_buffer = io.BytesIO(bukti_file.getvalue())
                        ext = bukti_file.name.split('.')[-1]
                        
                        # Metadata File
                        nama_file = f"Bukti_{nama}_{waktu.replace('/','-').replace(':','-')}.{ext}"
                        meta = {'name': nama_file, 'parents': [ID_FOLDER_DRIVE]}
                        
                        # Upload
                        media = MediaIoBaseUpload(file_buffer, mimetype=bukti_file.type)
                        up = service_drive.files().create(
                            body=meta, 
                            media_body=media, 
                            fields='webViewLink', 
                            supportsAllDrives=True
                        ).execute()
                        
                        link_bukti = up.get('webViewLink')
                        
                    except Exception as e:
                        st.error(f"❌ Gagal Upload Drive: {e}")
                        st.stop()
                
                # --- SIMPAN KE SHEETS ---
                try:
                    sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                    
                    # Simpan pesan & reload
                    st.session_state['pesan_sukses'] = "✅ Laporan Berhasil Terkirim!"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Gagal Simpan Sheets: {e}")
