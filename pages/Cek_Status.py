import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Cek Status Laporan", page_icon="🔍")

# ==========================================
# BAGIAN DESAIN (CSS PREMIUM) 🎨
# ==========================================
st.markdown("""
<style>
    /* Background Gradient Halus */
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    
    /* Sidebar Navy */
    [data-testid="stSidebar"] {background-color: #1e293b; border-right: 2px solid #334155;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}

    /* Kartu Hasil Pencarian */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 5px solid #ccc;
    }
    
    /* Warna Status */
    .status-pending {border-left-color: #ef4444;} /* Merah */
    .status-proses {border-left-color: #f59e0b;} /* Kuning */
    .status-selesai {border-left-color: #10b981;} /* Hijau */

    /* Input Box */
    .stTextInput > div > div > input {border-radius: 10px; border: 1px solid #cbd5e1;}
    
    /* Tombol Cari */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white; border-radius: 20px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE
# ==========================================
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

if os.path.exists("credentials.json"):
    creds_file = "credentials.json"
else:
    creds_file = "../credentials.json"

try:
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open("Database_Advokasi").worksheet("Laporan")
except Exception as e:
    st.error(f"Koneksi Database Error: {e}")
    st.stop()

# ==========================================
# HALAMAN PENCARIAN 🔍
# ==========================================
st.title("🔍 Cek Status Laporanmu")
st.markdown("Masukkan NPM untuk melihat progres laporan yang pernah kamu kirim.")

# Kolom Pencarian (Biar di tengah)
col_spacer1, col_input, col_spacer2 = st.columns([1, 2, 1])

with col_input:
    npm_input = st.text_input("Ketik NPM Kamu di sini:", placeholder="Contoh: 2117041xxx")
    tombol_cari = st.button("Lacak Laporan 🕵️‍♂️")

st.divider()

# Logika Pencarian
if tombol_cari and npm_input:
    # 1. Ambil Data Terbaru
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # 2. Pastikan kolom NPM dibaca sebagai string (teks) biar akurat
    df['NPM'] = df['NPM'].astype(str)
    
    # 3. Filter Data berdasarkan NPM
    hasil_cari = df[df['NPM'] == npm_input]
    
    if not hasil_cari.empty:
        st.success(f"Ditemukan {len(hasil_cari)} laporan untuk NPM: {npm_input}")
        
        # Tampilkan dalam bentuk Kartu Cantik
        # Kita balik urutannya biar laporan terbaru di paling atas
        for index, row in hasil_cari.iloc[::-1].iterrows():
            
            # Tentukan warna & ikon berdasarkan status
            status = row['Status']
            if status == "Selesai":
                css_class = "status-selesai"
                icon = "✅"
                ket_status = "MASALAH SELESAI"
            elif status == "Proses":
                css_class = "status-proses"
                icon = "⏳"
                ket_status = "SEDANG DITINDAK"
            else: # Pending
                css_class = "status-pending"
                icon = "🔴"
                ket_status = "MENUNGGU ANTREAN"
            
            # Render HTML Kartu
            st.markdown(f"""
            <div class="result-card {css_class}">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:bold; font-size:1.1rem;">{row['Kategori Masalah']}</span>
                    <span style="color:gray; font-size:0.8rem;">📅 {row['Waktu Lapor']}</span>
                </div>
                <p style="margin-top:10px; color:#475569;">"{row['Detail Keluhan']}"</p>
                <div style="margin-top:15px; font-weight:bold;">
                    Status: {icon} {ket_status}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.warning(f"Belum ada laporan ditemukan untuk NPM: **{npm_input}**.")
        st.info("Pastikan NPM yang kamu ketik benar atau coba lapor dulu di menu 'Lapor Masalah'.")

elif tombol_cari and not npm_input:
    st.error("Isi NPM dulu dong kak! 😅")