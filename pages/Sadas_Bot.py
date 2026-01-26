import streamlit as st
import time

st.set_page_config(page_title="Sadas Bot AI", page_icon="🤖")

# ==========================================
# 🎨 MASTER DESIGN SYSTEM (CHAT STYLE)
# ==========================================
st.markdown("""
<style>
    /* Background Gradient Halus */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Sidebar Navy */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 2px solid #334155;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* BUBBLE CHAT USER (Kanan - Biru) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #dbeafe;
        border-radius: 20px 20px 0 20px;
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
    }

    /* BUBBLE CHAT BOT (Kiri - Putih) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border-radius: 20px 20px 20px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #334155;
    }
    
    /* Tombol Kirim */
    .stChatInput button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 50%;
    }

    /* Tombol Hapus Chat di Sidebar */
    div.stButton > button {
        background-color: #ef4444; 
        color: white; 
        border-radius: 8px; 
        border: none;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #dc2626;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR (OPSI CHAT) ⚙️
# ==========================================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    st.write("Klik tombol di bawah jika ingin menghapus riwayat percakapan.")
    
    if st.button("🗑️ Hapus Riwayat Chat"):
        st.session_state.messages = [] # Reset Chat
        st.session_state.messages.append({"role": "assistant", "content": "Halo! Riwayat chat sudah dibersihkan. Mau tanya apa lagi? 😊"})
        st.rerun()

# ==========================================
# HALAMAN UTAMA (CHATBOT) 🤖
# ==========================================
st.title("🤖 Sadas Bot")
st.caption("Asisten Virtual Himpunan Mahasiswa Sains Data - Siap Bantu 24 Jam!")

# --- KAMUS KECERDASAN BUATAN (SEDERHANA) ---
# Kamu bisa tambah kata kunci di sini sesuka hati!
kamus_jawaban = {
    "kip": "🎓 **Info KIP Kuliah:**\nPastikan kamu menyiapkan berkas SKTM, Slip Gaji Orang Tua, dan Foto Rumah. \nInfo lengkap cek: [kip-kuliah.kemdikbud.go.id](https://kip-kuliah.kemdikbud.go.id)",
    "ukt": "💰 **Info UKT:**\nBanding UKT biasanya dibuka awal semester ganjil. Syarat utamanya adalah surat keterangan penurunan pendapatan orang tua atau PHK.",
    "cuti": "📅 **Cuti Akademik:**\nPengajuan maksimal H-2 minggu sebelum KRSan. Jangan lupa konsultasi ke Dosen Pembimbing Akademik (PA) dulu ya!",
    "nilai": "📈 **Masalah Nilai:**\nJika ada nilai error atau belum keluar, silakan lapor lewat menu **'📝 Lapor Masalah'** di sidebar. Sertakan bukti screenshot siakad.",
    "skripsi": "🎓 **Pejuang Skripsi:**\nSyarat seminar proposal (Sempro) adalah sudah lulus minimal 110 SKS dan tidak ada nilai D. Semangat!",
    "lab": "💻 **Fasilitas Lab:**\nLab Komputer ada di Gedung C Lt. 3. Jadwal praktikum bisa dilihat di mading depan lab atau tanya Asisten Lab.",
    "halo": "Halo juga! 👋 Ada yang bisa Sadas Bot bantu hari ini?",
    "terima kasih": "Sama-sama! Senang bisa membantu. 😊",
    "makasih": "Sama-sama! Jangan sungkan tanya lagi ya. 👍"
}

# --- INISIALISASI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! 👋 Saya Sadas Bot.\n\nSilakan tanya tentang: **KIP, UKT, Cuti, Nilai, atau Skripsi**."}]

# --- TAMPILKAN RIWAYAT CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT USER ---
if prompt := st.chat_input("Ketik pertanyaanmu... (Contoh: Syarat KIP apa?)"):
    
    # 1. Tampilkan Pesan User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Proses Jawaban Bot
    with st.chat_message("assistant"):
        with st.spinner("Sadas Bot sedang berpikir..."):
            time.sleep(1.5) # Efek mikir biar natural
            
            response = "Maaf, saya belum mengerti pertanyaan itu. 🙏\n\nCoba gunakan kata kunci: **KIP, UKT, Nilai, Lab, Skripsi, atau Cuti**."
            
            # Cari kata kunci dalam kalimat user
            prompt_lower = prompt.lower()
            for key, val in kamus_jawaban.items():
                if key in prompt_lower:
                    response = val
                    break
            
            st.markdown(response)
            
    # 3. Simpan Jawaban ke Memori
    st.session_state.messages.append({"role": "assistant", "content": response})
