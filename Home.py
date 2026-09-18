import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

st.set_page_config(
    page_title="Suara Kahim & Pimpinan",
    page_icon="🔒",
    layout="wide"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .pro-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>🔒 Area Khusus Pimpinan: Suara Kahim</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b;'>Halaman ini berisi daftar kritik, saran, dan aspirasi rahasia yang ditujukan khusus untuk Kahim, Wakahim, dan pengurus inti.</p>", unsafe_allow_html=True)

# --- KONEKSI GOOGLE SHEETS ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
if os.path.exists("credentials.json"):
    creds_file = "credentials.json"
else:
    creds_file = "../credentials.json"

def get_sheet_aspirasi():
    try:
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        client = gspread.authorize(creds)
        # Pastikan kamu sudah membuat tab/worksheet bernama 'Aspirasi_Kahim' di Google Sheets
        return client.open("Database_Advokasi").worksheet("Aspirasi_Kahim")
    except:
        return None

# --- SISTEM LOGIN / PASSWORD ---
if 'kahim_logged_in' not in st.session_state:
    st.session_state['kahim_logged_in'] = False

if not st.session_state['kahim_logged_in']:
    st.markdown("<div style='max-width: 400px; margin: 40px auto;'>", unsafe_allow_html=True)
    with st.form("login_kahim_form"):
        st.subheader("Autentikasi Pimpinan")
        pwd_input = st.text_input("Masukkan Password Khusus Pimpinan", type="password")
        submit_login = st.form_submit_button("Buka Akses")
        
        if submit_login:
            # Ganti password di bawah ini sesuai keinginanmu
            if pwd_input == "RAHASIA_KAHIM2026":
                st.session_state['kahim_logged_in'] = True
                st.rerun()
            else:
                st.error("Password salah! Akses ditolak.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    col_l1, col_l2 = st.columns([6, 1])
    with col_l2:
        if st.button("Keluar"):
            st.session_state['kahim_logged_in'] = False
            st.rerun()

    st.write("---")
    
    sheet_asp = get_sheet_aspirasi()
    if sheet_asp:
        try:
            data = sheet_asp.get_all_records()
            if len(data) > 0:
                df = pd.DataFrame(data)
                st.success("✅ Berhasil memuat data aspirasi rahasia.")
                
                if 'Tujuan Pejabat' in df.columns:
                    list_pejabat = ["Semua Pimpinan"] + list(df['Tujuan Pejabat'].unique())
                    pilih_filter = st.selectbox("Filter Berdasarkan Tujuan Pimpinan:", list_pejabat)
                    
                    if pilih_filter != "Semua Pimpinan":
                        df_filtered = df[df['Tujuan Pejabat'] == pilih_filter]
                    else:
                        df_filtered = df
                else:
                    df_filtered = df

                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                st.metric("Total Aspirasi Masuk", len(df))
                
            else:
                st.info("Belum ada aspirasi atau kritik yang masuk ke database.")
        except Exception as e:
            st.error(f"Gagal mengambil data dari Google Sheets: {e}")
    else:
        st.warning("⚠️ Worksheet 'Aspirasi_Kahim' belum ditemukan di Google Sheets. Pastikan kamu sudah membuatnya.")
