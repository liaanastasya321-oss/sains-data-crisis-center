import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import os
import json

# 1. SETUP HALAMAN
st.set_page_config(page_title="Lapor Masalah", page_icon="📝")

# ==========================================
# 🎨 DESIGN SYSTEM (Clean & Professional)
# ==========================================
st.markdown("""
<style>
    /* Background Gradient Halus */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: 'Source Sans 3', sans-serif;
    }

    /* Sidebar Navy */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* Input Box styling */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        background-color: white;
    }

    /* Tombol Kirim (Solid Blue) */
    .stButton > button {
        background-color: #2563eb; /* Royal Blue */
        color: white;
        border-radius: 8px;
        height: 50px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 100%;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
    }
    
    /* Upload Area */
    [data-testid="stFileUploader"] {
        padding: 15px;
        background-color: white;
        border-radius: 8px;
        border: 1px dashed #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONFIGURASI
# ==========================================
ID_FOLDER_DRIVE = "1n7n4NNuQiGMsSjHynqwD-aMRvO0W-K4n"
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# ==========================================
# KONEKSI DATABASE (DUAL MODE)
# ==========================================
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
st.markdown("Silakan lengkapi formulir di bawah ini. Identitas pelapor dijamin kerahasiaannya.")

with st.container():
    with st.form("form_lapor"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Data Diri")
            nama = st.text_input("Nama Lengkap (Boleh Anonim)")
            npm = st.text_input("NPM")
            jurusan = st.selectbox("Program Studi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        
        with col2:
            st.markdown("### 🚨 Detail Laporan")
            kategori = st.selectbox("Kategori Masalah", ["Fasilitas (AC/Lab/Wi-Fi)", "Akademik (Nilai/Dosen)", "Keuangan/UKT", "Lainnya"])
            bukti_file = st.file_uploader("Upload Bukti (Opsional)", type=["png", "jpg", "jpeg", "pdf"])
            
        keluhan = st.text_area("Deskripsi Masalah", height=150, placeholder="Jelaskan kronologi atau masalah secara detail...")
        
        st.write("---")
        tombol_kirim = st.form_submit_button("Kirim Laporan")

        if tombol_kirim:
            if not keluhan:
                st.warning("⚠️ Mohon isi deskripsi keluhan terlebih dahulu.")
            else:
                with st.spinner("Sedang mengirim data..."):
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    link_bukti = "-" 
                    upload_status = "Sukses"
                    
                    # 1. Upload ke Drive
                    if bukti_file is not None:
                        try:
                            ext = bukti_file.name.split('.')[-1]
                            nama_file_drive = f"Bukti_{nama.replace(' ','_')}_{waktu.replace('/','-').replace(':','-')}.{ext}"
                            
                            file_metadata = {'name': nama_file_drive, 'parents': [ID_FOLDER_DRIVE]}
                            media = MediaIoBaseUpload(bukti_file, mimetype=bukti_file.type)
                            
                            file = service_drive.files().create(
                                body=file_metadata,
                                media_body=media,
                                fields='id, webViewLink',
                                supportsAllDrives=True
                            ).execute()
                            
                            link_bukti = file.get('webViewLink')
                        except:
                            upload_status = "Gagal"
                            link_bukti = "Gagal Upload (Limit Drive)"
                    
                    # 2. Simpan ke Sheets
                    try:
                        data_baru = [waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti]
                        sheet.append_row(data_baru)
                        
                        # SUKSES (TANPA BALON)
                        st.success("✅ Laporan berhasil dikirim! Terima kasih atas masukan Anda.")
                        
                        if upload_status == "Gagal" and bukti_file:
                            st.warning("⚠️ Catatan: Bukti foto gagal terupload, namun laporan teks sudah diterima.")
                            
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")
