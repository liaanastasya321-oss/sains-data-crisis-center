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
# 🎨 DESAIN ASLI (CLEAN STYLE)
# ==========================================
st.markdown("""
<style>
    /* Background Gradient Halus (Tampilan Awal) */
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    
    /* Sidebar Navy */
    [data-testid="stSidebar"] {background-color: #1e293b; border-right: 2px solid #334155;}
    [data-testid="stSidebar"] * {color: #f8fafc !important;}

    /* Metrik Card (Kotak Putih Bersih) */
    div[data-testid="stMetric"] {
        background-color: white; 
        border-radius: 15px; 
        padding: 15px; 
        border-left: 5px solid #3b82f6; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Judul */
    h1 {color: #1e3a8a; font-family: 'Helvetica', sans-serif;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE
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
        st.error("⚠️ File Kunci tidak ditemukan!")
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

    # === 🛠️ PERBAIKAN LOGIKA (PENTING) ===
    # Filter: Membuang baris yang 'Waktu Lapor'-nya kosong
    # Ini supaya diagram tidak error/berantakan karena baris kosong di Excel
    if not df.empty and 'Waktu Lapor' in df.columns:
        df = df[df['Waktu Lapor'] != ""]
        df = df[df['Kategori Masalah'] != ""] 

except:
    df = pd.DataFrame()

if not df.empty:
    # --- METRIK ATAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Laporan", len(df))
    
    if 'Status' in df.columns:
        c2.metric("Perlu Tindakan", len(df[df['Status'] == 'Pending']))
        c3.metric("Selesai", len(df[df['Status'] == 'Selesai']))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    # === GRAFIK 1: PIE CHART ===
    with col1:
        st.subheader("Peta Masalah")
        if 'Kategori Masalah' in df.columns:
            # Hitung manual biar rapi
            pie_data = df['Kategori Masalah'].value_counts().reset_index()
            pie_data.columns = ['Kategori', 'Jumlah']

            fig = px.pie(pie_data, values='Jumlah', names='Kategori', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Menunggu data kategori...")
    
    # === GRAFIK 2: WORD CLOUD ===
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
                wc = WordCloud(width=800, height=400, background_color='white', 
                               colormap='Reds', stopwords=kata_sampah, min_font_size=10).generate(text_bersih)
                
                fig_wc, ax = plt.subplots(figsize=(10, 5))
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
