import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import re 
import json

st.set_page_config(page_title="Dashboard Publik", page_icon="📊", layout="wide")

# ==========================================
# 💎 MASTER DESIGN SYSTEM (DEEP TECH THEME)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT (Poppins) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* BACKGROUND GRADASI TEKNOLOGI (Dark Blue - Cyan) */
    .stApp {
        background: linear-gradient(-45deg, #020024, #0f172a, #090979, #00d4ff);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Poppins', sans-serif;
        color: white;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* METRIK CARDS (KOTAK ANGKA) */
    div[data-testid="stMetric"] {
        background-color: rgba(15, 23, 42, 0.6);
        border-radius: 15px;
        padding: 15px;
        border-left: 5px solid #00d4ff; /* Neon Cyan */
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        color: white !important;
    }
    div[data-testid="stMetric"] label { color: #cbd5e1 !important; }
    div[data-testid="stMetric"] div { color: white !important; }

    /* JUDUL */
    h1 {
        color: white; 
        font-family: 'Poppins', sans-serif; 
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* TABLE */
    div[data-testid="stDataFrame"] {
        background-color: rgba(15, 23, 42, 0.8);
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE (DUAL MODE) 🔗
# ==========================================
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
        st.error("⚠️ File Kunci (Credentials) tidak ditemukan!")
        st.stop()

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
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # === 🛑 FILTER PENTING: BUANG BARIS KOSONG ===
    # Ini kuncinya supaya diagram tidak berantakan!
    if not df.empty and 'Waktu Lapor' in df.columns:
        # Hanya ambil data yang 'Waktu Lapor'-nya TIDAK kosong
        df = df[df['Waktu Lapor'] != ""]
        # Pastikan juga kategori tidak kosong
        df = df[df['Kategori Masalah'] != ""]

except:
    df = pd.DataFrame()

if not df.empty:
    # --- METRIK ATAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Laporan", len(df))
    
    if 'Status' in df.columns:
        # Hitung status
        pending = len(df[df['Status'] == 'Pending'])
        selesai = len(df[df['Status'] == 'Selesai'])
        proses = len(df[df['Status'] == 'Proses']) # Tambahan jika ada status Proses
        
        c2.metric("Perlu Tindakan", pending)
        c3.metric("Selesai Ditangani", selesai)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    # === GRAFIK 1: PIE CHART (DARK MODE) ===
    with col1:
        st.subheader("Peta Masalah")
        if 'Kategori Masalah' in df.columns:
            # Siapkan data agregat
            pie_data = df['Kategori Masalah'].value_counts().reset_index()
            pie_data.columns = ['Kategori', 'Jumlah']
            
            fig = px.pie(pie_data, values='Jumlah', names='Kategori', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Cyan) # Warna Cyan biar neon
            
            # Update Layout biar transparan (Dark Mode Friendly)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Menunggu data kategori...")
    
    # === GRAFIK 2: WORD CLOUD (DARK MODE) ===
    with col2:
        st.subheader("🔥 Isu Terhangat")
        
        if 'Detail Keluhan' in df.columns:
            text_gabungan = " ".join(df['Detail Keluhan'].astype(str).tolist()).lower()
            text_bersih = re.sub(r'[^a-z\s]', '', text_gabungan)
            
            kata_sampah = set([
                'dan','yang','di','ke','dari','pada','untuk','dengan','oleh','sebagai','dalam',
                'atau','karena','jika','kalau','kalo','agar','supaya','walaupun','meskipun',
                'hingga','sampai','tentang','antara','saya','aku','kami','kita','anda','kamu',
                'dia','mereka','beliau','gue','gua','loe','lu','elo','ada','adalah','jadi',
                'menjadi','buat','bikin','punya','menggunakan','pakai','lihat','bilang','kasih',
                'beri','ambil','datang','pergi','sudah','telah','sedang','akan','masih','belum',
                'pernah','sekarang','nanti','tadi','kemarin','besok','juga','sangat','banget',
                'sekali','cukup','lebih','paling','aja','saja','doang','cuma','hanya', 'gak',
                'tapi','baik','dapat','tidak','semua','tolong','mohon','min','admin','lapor',
                'kak','pak','bu','assalamualaikum','bapak','ibu'
            ])
            
            if len(text_bersih) > 1:
                # Wordcloud Background Hitam biar nyatu
                wc = WordCloud(width=800, height=400, background_color='#0f172a', 
                               colormap='cool', # Warna dingin/neon
                               stopwords=kata_sampah, min_font_size=10).generate(text_bersih)
                
                fig_wc, ax = plt.subplots(figsize=(10, 5))
                # Set background plot transparan
                fig_wc.patch.set_alpha(0)
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc)
            else:
                st.info("Belum cukup data kata kunci untuk ditampilkan.")
        else:
            st.info("Menunggu data keluhan...")

    # === TABEL BAWAH ===
    st.divider()
    st.subheader("📋 Detail Data Masuk")
    kolom_tampil = [col for col in ['Waktu Lapor', 'Kategori Masalah', 'Detail Keluhan', 'Status'] if col in df.columns]
    if kolom_tampil:
        st.dataframe(df[kolom_tampil].tail(10), use_container_width=True)

else:
    st.info("Data masih kosong atau belum ada laporan yang masuk.")
