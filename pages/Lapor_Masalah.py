import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests # <--- Alat buat kirim ke ImgBB
from datetime import datetime
import os
import json
import time

# ==========================================
# 👇 SETTING PENTING
# ==========================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g" 

# 👇👇👇 PASTE KODE IMGBB KAMU DI BAWAH INI 👇👇👇
API_KEY_IMGBB  = "b70c3878ae0cf53cf64650f8c012efa2" 
# 👆👆👆 JANGAN SAMPAI SALAH YA 👆👆👆

# 1. SETUP HALAMAN
st.set_page_config(page_title="Lapor Masalah", page_icon="📝")

# 2. CSS
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); font-family: 'Source Sans 3', sans-serif;}
    [data-testid="stSidebar"] {background-color: #0f172a; border-right: 1px solid #1e293b;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}
    .stButton > button {background-color: #2563eb; color: white; border-radius: 8px; height: 50px; width: 100%;}
</style>
""", unsafe_allow_html=True)

# 3. KONEKSI GOOGLE SHEETS
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    if "google_credentials" in st.secrets:
        creds_dict = json.loads(st.secrets["google_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    elif os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    else:
        st.error("⚠️ File Credentials tidak ditemukan!")
        st.stop()
    
    # Buka Spreadsheet
    client = gspread.authorize(creds)
    sheet = client.open_by_key(ID_SPREADSHEET).worksheet("Laporan")
    
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
        bukti_file = st.file_uploader("Upload Foto Bukti (Wajib JPG/PNG)", type=["png", "jpg", "jpeg"])
        
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
                        # Kirim gambar ke ImgBB
                        payload = {
                            "key": API_KEY_IMGBB,
                            "image": bukti_file.getvalue()
                        }
                        response = requests.post("https://api.imgbb.com/1/upload", data=payload)
                        hasil = response.json()
                        
                        if hasil["success"]:
                            link_bukti = hasil["data"]["url"]
                        else:
                            st.error(f"Gagal Upload Gambar: {hasil.get('error', {}).get('message')}")
                            st.stop()
                            
                    except Exception as e:
                        st.error(f"❌ Gagal Koneksi ImgBB: {e}")
                        st.stop()
                
                # --- SIMPAN KE SHEETS ---
                try:
                    sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                    st.session_state['pesan_sukses'] = "✅ Laporan Berhasil Dikirim!"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Gagal Simpan Database: {e}")
