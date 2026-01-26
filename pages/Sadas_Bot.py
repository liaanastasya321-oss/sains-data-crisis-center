import streamlit as st
import time

st.set_page_config(page_title="Sadas Bot AI", page_icon="🤖")
# --- AWAL BAGIAN DESAIN (COPY DARI SINI) ---
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

    /* Kartu Metric (Kotak Angka) */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3b82f6; /* Aksen Biru */
    }
    
    /* Judul Besar */
    h1 {
        color: #1e3a8a;
        font-family: 'Helvetica', sans-serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Tombol Cantik */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #0ea5e9);
        color: white;
        border-radius: 25px;
        height: 50px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
    }

    /* Input Box Lebih Modern */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)
# --- AKHIR BAGIAN DESAIN ---
# --- BAGIAN DESAIN (CSS CHAT WHATSAPP STYLE) 🎨 ---
st.markdown("""
<style>
    /* Background Gradient */
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    
    /* Bubble Chat User (Kanan, Biru) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #dbeafe;
        border-radius: 20px 20px 0 20px;
        border: 1px solid #bfdbfe;
    }
    
    /* Bubble Chat Bot (Kiri, Putih) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border-radius: 20px 20px 20px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Tombol Kirim */
    .stChatInput button {
        background-color: #2563eb !important;
        color: white !important;
    }
    
    /* Tombol Hapus di Sidebar */
    div.stButton > button:first-child {
        background-color: #ef4444; /* Merah */
        color: white;
        border-radius: 10px;
        width: 100%;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #dc2626;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)
# -----------------------------------------------------

# === FITUR HAPUS CHAT (SIDEBAR) 🗑️ ===
with st.sidebar:
    st.header("⚙️ Pengaturan")
    st.write("Kalau chat sudah kepenuhan, klik tombol di bawah ini:")
    
    # Tombol Reset
    if st.button("🗑️ Bersihkan Riwayat Chat"):
        st.session_state.messages = [] # Kosongkan memori
        st.session_state.messages.append({"role": "assistant", "content": "Halo! Chat sudah dibersihkan. Ada yang bisa Sadas Bot bantu lagi? (KIP, UKT, Nilai)"})
        st.rerun() # Refresh otomatis

# === JUDUL UTAMA ===
st.title("🤖 Sadas Bot")
st.caption("Asisten Pintar Himpunan Mahasiswa Sains Data - Siap Bantu 24 Jam!")

# === KAMUS JAWABAN ===
kamus_jawaban = {
    "kip": "Info **KIP Kuliah**: Pastikan berkas SKTM & Slip Gaji siap. Cek: kip-kuliah.kemdikbud.go.id",
    "ukt": "Soal **UKT**: Banding UKT dibuka awal semester. Syarat: Surat PHK/Keterangan Tidak Mampu.",
    "cuti": "**Cuti Akademik** maksimal H-2 minggu sebelum KRS. Hubungi Dosen PA dulu ya.",
    "nilai": "Jika **Nilai Error**, lapor via menu 'Lapor Masalah' di kiri. Lampirkan bukti screenshot.",
    "skripsi": "Semangat pejuang **Skripsi**! Syarat sempro: Lulus 110 SKS & Tidak ada nilai D.",
    "lab": "Jadwal **Lab Komputer** ada di mading Lt. 3 atau tanya Kak Aslab."
}

# === INISIALISASI CHAT ===
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa Sadas Bot bantu? (Tanya soal: KIP, UKT, Nilai, dll)"}]

# === TAMPILKAN HISTORY CHAT ===
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# === LOGIKA JAWAB OTOMATIS ===
if prompt := st.chat_input("Ketik pertanyaanmu di sini..."):
    # 1. Tampilkan Chat User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Bot Mikir & Jawab
    with st.chat_message("assistant"):
        with st.spinner("Sadas Bot sedang mengetik..."):
            time.sleep(1) # Delay biar natural
            
            response = "Maaf, saya belum paham. Coba kata kunci: KIP, UKT, Nilai, Lab."
            
            # Cari kata kunci
            prompt_lower = prompt.lower()
            for key, val in kamus_jawaban.items():
                if key in prompt_lower:
                    response = val
                    break
            
            st.markdown(response)
            
    # 3. Simpan Jawaban Bot
    st.session_state.messages.append({"role": "assistant", "content": response})