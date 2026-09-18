import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests 
from datetime import datetime
import os
import json

# ==========================================
# 👇 SETTING PENTING
# ==========================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 

# 👇 PASTE API KEY IMGBB KAMU DI SINI
API_KEY_IMGBB  = "b70c3878ae0cf53cf64650f8c012efa2" 

# 1. SETUP HALAMAN
st.set_page_config(page_title="Lapor Masalah", page_icon="📝")

# 2. CSS (TAMPILAN RAPI)
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); font-family: 'Source Sans 3', sans-serif;}
    [data-testid="stSidebar"] {background-color: #0f172a; border-right: 1px solid #1e293b;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}
    
    /* Kotak Input Putih Bersih */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        background-color: white !important;
        color: #334155 !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 8px !important;
    }
    
    .stButton > button {background-color: #2563eb; color: white; border-radius: 8px; height: 50px; width: 100%; font-weight: bold;}
    .stButton > button:hover {background-color: #1d4ed8;}
</style>
""", unsafe_allow_html=True)

# 3. KONEKSI GOOGLE SHEETS CREDENTIALS
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
    spreadsheet_utama = client.open_by_key(ID_SPREADSHEET)
    
except Exception as e:
    st.error(f"⚠️ Koneksi Database Gagal: {e}")
    st.stop()

# 4. FORMULIR
st.title("📝 Form Pengaduan")

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
        bukti_file = st.file_uploader("Upload Foto Bukti (JPG/PNG)", type=["png", "jpg", "jpeg"])
        
    keluhan = st.text_area("Deskripsi Masalah", height=150)
    tombol = st.form_submit_button("Kirim Laporan 🚀")

    if tombol:
        if not keluhan:
            st.warning("Mohon isi deskripsi masalah.")
        else:
            with st.spinner("Mengirim laporan..."):
                waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                link_bukti = "-" 
                
                # --- UPLOAD KE IMGBB ---
                if bukti_file:
                    try:
                        params_data = {"key": API_KEY_IMGBB}
                        files_data = {"image": bukti_file.getvalue()}
                        
                        response = requests.post(
                            "https://api.imgbb.com/1/upload", 
                            data=params_data, 
                            files=files_data
                        )
                        hasil = response.json()
                        
                        if response.status_code == 200 and hasil.get("success"):
                            link_bukti = hasil["data"]["url"]
                        else:
                            pesan_error = hasil.get("error", {}).get("message", "Unknown Error")
                            st.error(f"❌ Gagal Upload Gambar: {pesan_error}")
                            st.stop()
                    except Exception as e:
                        st.error(f"❌ Error Sistem Upload: {e}")
                        st.stop()
                
                # ==========================================
                # 🔍 OTOMATIS PEMILAHAN DATA (KAHIM / AZWAR)
                # ==========================================
                teks_gabungan = (kategori + " " + keluhan).lower()
                
                try:
                    if "kahim" in teks_gabungan or "azwar" in teks_gabungan:
                        # Masuk otomatis ke sheet Aspirasi_Kahim
                        sheet_kahim = spreadsheet_utama.worksheet("Aspirasi_Kahim")
                        sheet_kahim.append_row([waktu, nama, npm, jurusan, "Azwar Kurniawan Syah (Kahim)", keluhan, "Masuk"])
                        st.session_state['pesan_sukses'] = "✅ Aspirasi khusus pimpinan berhasil dikirim secara rahasia!"
                    else:
                        # Masuk ke sheet Laporan publik biasa
                        sheet_laporan = spreadsheet_utama.worksheet("Laporan")
                        sheet_laporan.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                        st.session_state['pesan_sukses'] = "✅ Laporan Berhasil Dikirim!"

                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Gagal Simpan Database: {e}")
