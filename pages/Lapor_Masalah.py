import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import os

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Lapor Masalah", page_icon="📝")

# ==========================================
# BAGIAN DESAIN (CSS FULL RAPI) 🎨
# ==========================================
st.markdown("""
<style>
    /* Background Gradient Halus */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Sidebar Keren (Navy Blue) */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 2px solid #334155;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important; /* Teks Sidebar Putih */
    }

    /* Judul Halaman */
    h1 {
        color: #1e3a8a;
        font-family: 'Helvetica', sans-serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Input Box Lebih Modern */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }

    /* Tombol Kirim Keren */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #0ea5e9);
        color: white;
        border-radius: 25px;
        height: 50px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
        width: 100%; /* Tombol lebar penuh */
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
    }
    
    /* Area Upload File */
    [data-testid="stFileUploader"] {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        border: 1px dashed #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONFIGURASI PENTING ⚠️
# ==========================================
# ID Folder dari link yang kamu kirim tadi
ID_FOLDER_DRIVE = "1n7n4NNuQiGMsSjHynqwD-aMRvO0W-K4n"

# ==========================================
# KONEKSI DATABASE & DRIVE 🔗
# ==========================================
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Cek lokasi file credentials (Anti-Nyasar)
if os.path.exists("credentials.json"):
    creds_file = "credentials.json"
else:
    creds_file = "../credentials.json"

try:
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    
    # 1. Koneksi ke Google Sheets (Tulis Data)
    client = gspread.authorize(creds)
    sheet = client.open("Database_Advokasi").worksheet("Laporan")
    
    # 2. Koneksi ke Google Drive (Upload File)
    service_drive = build('drive', 'v3', credentials=creds)
    
except Exception as e:
    st.error(f"⚠️ Koneksi Gagal: {e}")
    st.info("Pastikan file 'credentials.json' ada.")
    st.stop()

# ==========================================
# TAMPILAN FORMULIR 📝
# ==========================================
st.title("📝 Form Pengaduan Mahasiswa")
st.markdown("Sampaikan keluhanmu dengan detail. Identitas aman.")

with st.container():
    with st.form("form_lapor"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Identitas")
            nama = st.text_input("Nama Lengkap (Boleh Anonim)")
            npm = st.text_input("NPM")
            jurusan = st.selectbox("Program Studi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
        
        with col2:
            st.markdown("### 🚨 Detail Masalah")
            kategori = st.selectbox("Kategori Masalah", ["Fasilitas (AC/Lab/Wi-Fi)", "Akademik (Nilai/Dosen)", "Keuangan/UKT", "Lainnya"])
            bukti_file = st.file_uploader("Upload Bukti (Opsional)", type=["png", "jpg", "jpeg", "pdf"], help="Lampirkan screenshot atau foto kondisi.")
            
        keluhan = st.text_area("Kronologi / Deskripsi Keluhan", height=150, placeholder="Contoh: AC di Lab Komputer 3 mati total sejak minggu lalu...")
        
        st.write("---")
        tombol_kirim = st.form_submit_button("Kirim Laporan Sekarang 🚀")

        if tombol_kirim:
            if not keluhan:
                st.warning("⚠️ Eits, jangan lupa isi deskripsi keluhannya ya!")
            else:
                with st.spinner("⏳ Sedang memproses laporan..."):
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    link_bukti = "-" # Default kalau gak upload
                    upload_status = "Sukses"
                    
                    # --- PROSES 1: UPLOAD KE DRIVE (Versi Anti-Macet) ---
                    if bukti_file is not None:
                        try:
                            # Rename file biar rapi: Bukti_Nama_Jam.png
                            ext = bukti_file.name.split('.')[-1]
                            nama_file_drive = f"Bukti_{nama.replace(' ','_')}_{waktu.replace('/','-').replace(':','-')}.{ext}"
                            
                            file_metadata = {
                                'name': nama_file_drive,
                                'parents': [ID_FOLDER_DRIVE] # Masuk ke folder khusus
                            }
                            
                            media = MediaIoBaseUpload(bukti_file, mimetype=bukti_file.type)
                            
                            # Upload!
                            file = service_drive.files().create(
                                body=file_metadata,
                                media_body=media,
                                fields='id, webViewLink',
                                supportsAllDrives=True
                            ).execute()
                            
                            link_bukti = file.get('webViewLink')
                            
                        except Exception as e:
                            # INI BAGIAN PENYELAMATNYA
                            # Kalau upload gagal (kuota penuh), kita CUEKIN errornya, tapi catat.
                            upload_status = "Gagal"
                            link_bukti = "Gagal Upload (Kuota Google Penuh)"
                            # Kita tidak pakai st.stop() biar data teks tetap tersimpan!
                    
                    # --- PROSES 2: SIMPAN KE SHEETS ---
                    # Urutan Kolom: [Waktu, Nama, NPM, Jurusan, Kategori, Keluhan, Status, LINK BUKTI]
                    try:
                        data_baru = [waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti]
                        sheet.append_row(data_baru)
                        
                        # Notifikasi Akhir
                        st.success("✅ Laporan Berhasil Terkirim!")
                        
                        if upload_status == "Gagal" and bukti_file is not None:
                            st.warning("⚠️ Catatan: Foto gagal terupload karena pembatasan Google, TAPI laporan teksmu sudah masuk aman! 👍")
                        elif bukti_file:
                            st.info("📸 Bukti foto juga berhasil tersimpan.")
                            
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Gagal menyimpan ke Database: {e}")