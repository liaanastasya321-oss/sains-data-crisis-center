import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json 

# ==========================================
# 👇 ID SPREADSHEET (ANTI NYASAR)
# ==========================================
ID_SPREADSHEET = "1crJl0DsswyMGmq0ej_niIMfhSLdUIUx8u42HEu-sc3g"

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
    .stTextInput > div > div > input {border-radius: 10px; border: 1px solid #cbd5e1; padding: 10px;}
    
    /* Tombol Cari */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white; border-radius: 20px; width: 100%; height: 50px; font-weight: bold;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE (METODE ID) 🔗
# ==========================================
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    if "google_credentials" in st.secrets:
        creds_dict = json.loads(st.secrets["google_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    elif os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    else:
        st.error("⚠️ File Kunci (Credentials) tidak ditemukan!")
        st.stop()

    client = gspread.authorize(creds)
    
    # --- PERBAIKAN UTAMA (PAKAI ID) ---
    sheet = client.open_by_key(ID_SPREADSHEET).worksheet("Laporan")
    
except Exception as e:
    st.error(f"Koneksi Database Gagal: {e}")
    st.stop()

# ==========================================
# HALAMAN PENCARIAN 🔍
# ==========================================
st.title("🔍 Cek Status Laporanmu")
st.markdown("Masukkan NPM untuk melihat progres laporan yang pernah kamu kirim.")

# Kolom Pencarian
col_spacer1, col_input, col_spacer2 = st.columns([0.5, 3, 0.5])

with col_input:
    npm_input = st.text_input("Ketik NPM Kamu di sini:", placeholder="Contoh: 2117041xxx")
    tombol_cari = st.button("Lacak Laporan 🕵️‍♂️")

st.divider()

# Logika Pencarian
if tombol_cari:
    if not npm_input:
        st.warning("⚠️ Isi NPM dulu dong kak! 😅")
    else:
        try:
            with st.spinner("Mencari data di database..."):
                # 1. Ambil Data Terbaru
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                
                # 2. Pastikan kolom NPM dibaca sebagai string biar gak error
                if not df.empty and 'NPM' in df.columns:
                    df['NPM'] = df['NPM'].astype(str)
                    
                    # 3. Filter Data
                    hasil_cari = df[df['NPM'] == npm_input]
                    
                    if not hasil_cari.empty:
                        st.success(f"✅ Ditemukan {len(hasil_cari)} laporan untuk NPM: {npm_input}")
                        
                        # Loop data (Dibalik biar yang baru di atas)
                        for index, row in hasil_cari.iloc[::-1].iterrows():
                            
                            status = row.get('Status', 'Pending') # Default Pending kalau kosong
                            
                            # Tentukan Gaya Kartu
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
                            
                            # Tampilkan Kartu
                            st.markdown(f"""
                            <div class="result-card {css_class}">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-weight:bold; font-size:1.2rem; color:#1e293b;">{row.get('Kategori Masalah', '-')}</span>
                                    <span style="background:#e2e8f0; padding:4px 10px; border-radius:15px; font-size:0.8rem; color:#475569;">
                                        📅 {row.get('Waktu Lapor', '-')}
                                    </span>
                                </div>
                                <hr style="margin:10px 0; border-top: 1px dashed #cbd5e1;">
                                <p style="color:#334155; line-height:1.5;">"{row.get('Detail Keluhan', '-')}"</p>
                                <div style="margin-top:15px; font-weight:bold; color:#0f172a;">
                                    Status: {icon} {ket_status}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    else:
                        st.warning(f"❌ Belum ada laporan ditemukan untuk NPM: **{npm_input}**")
                        st.info("Mungkin salah ketik? Atau coba lapor dulu di menu 'Lapor Masalah'.")
                else:
                    st.info("Database masih kosong.")
                    
        except Exception as e:
            st.error(f"Terjadi kesalahan sistem: {e}")
