import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import re # Library buat bersih-bersih teks

st.set_page_config(page_title="Dashboard Publik", page_icon="📊", layout="wide")

# --- BAGIAN DESAIN (CSS) BIAR TETEP GANTENG ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    [data-testid="stSidebar"] {background-color: #1e293b; border-right: 2px solid #334155;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}
    div[data-testid="stMetric"] {background-color: white; border-radius: 15px; padding: 15px; border-left: 5px solid #3b82f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    h1 {color: #1e3a8a; font-family: 'Helvetica', sans-serif;}
</style>
""", unsafe_allow_html=True)

# --- KONEKSI DATABASE ---
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
    st.error(f"Koneksi Error: {e}")
    st.stop()

# --- DASHBOARD UTAMA ---
st.title("📊 Dashboard Analisis Data")
st.caption("Memantau Aspirasi Mahasiswa secara Real-Time")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Ambil Data
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    # --- METRIK ATAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Laporan", len(df))
    c2.metric("Perlu Tindakan", len(df[df['Status'] == 'Pending']))
    c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    # === GRAFIK 1: PIE CHART (Lingkaran di Tengah) ===
    with col1:
        st.subheader("Peta Masalah")
        fig = px.pie(df, names='Kategori Masalah', hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        
        # Setting biar rapi di tengah
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # === GRAFIK 2: WORD CLOUD (SUDAH DIBERSIHKAN!) ===
    with col2:
        st.subheader("🔥 Isu Terhangat (Word Cloud)")
        
        # 1. Gabungkan semua keluhan jadi satu teks panjang & kecilkan huruf
        text_gabungan = " ".join(df['Detail Keluhan'].astype(str).tolist()).lower()
        
        # 2. Hapus simbol aneh (titik, koma, angka, tanda seru) pake Regex
        text_bersih = re.sub(r'[^a-z\s]', '', text_gabungan)
        
        # 3. DAFTAR KATA SAMPAH (STOPWORDS) INDONESIA
        # Kata-kata ini bakal DIHAPUS dari gambar
        kata_sampah = set([
             # kata hubung & preposisi
    'dan','yang','di','ke','dari','pada','untuk','dengan','oleh','sebagai','dalam',
    'atau','karena','jika','kalau','kalo','agar','supaya','walaupun','meskipun',
    'hingga','sampai','tentang','antara',

    # kata ganti orang
    'saya','aku','kami','kita','anda','kamu','dia','mereka','beliau',
    'gue','gua','loe','lu','elo',

    # kata kerja umum
    'ada','adalah','jadi','menjadi','buat','bikin','punya','menggunakan',
    'pakai','lihat','bilang','kasih','beri','ambil','datang','pergi',

    # waktu & aspek
    'sudah','sudah','telah','sedang','akan','masih','belum','pernah',
    'sekarang','nanti','tadi','kemarin','besok',

    # kata keterangan
    'juga','sangat','banget','sekali','cukup','lebih','paling',
    'aja','saja','doang','cuma','hanya', 'gak','tapi','baik','dapat','tidak','dapat','semua'
        ])
        
        # 4. Cek apakah ada kata tersisa setelah dibersihkan
        if len(text_bersih) > 1:
            # Bikin Word Cloud dengan Filter Stopwords
            wc = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                colormap='Reds', # Warna Merah biar kelihatan 'Urgent'
                stopwords=kata_sampah, # <--- INI FILTERNYA
                min_font_size=10
            ).generate(text_bersih)
            
            # Tampilkan Gambar
            fig_wc, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off") # Hilangkan garis pinggir
            st.pyplot(fig_wc)
        else:
            st.info("Belum cukup data kata kunci untuk ditampilkan.")

    # === TABEL BAWAH ===
    st.divider()
    st.subheader("📋 Detail Data Masuk")
    st.dataframe(df[['Waktu Lapor', 'Kategori Masalah', 'Detail Keluhan', 'Status']].tail(10), use_container_width=True)

else:
    st.info("Data kosong.")