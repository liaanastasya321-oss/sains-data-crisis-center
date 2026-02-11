# --- FUNGSI AI DRAFTER (VERSI JUJUR/DEBUG) ---
def draft_surat_with_ai(kategori, keluhan, nama):
    # Cek dulu apakah kuncinya ada
    if "GEMINI_API_KEY" not in st.secrets:
        return "ERROR: API KEY HILANG", "ERROR", "Kunci 'GEMINI_API_KEY' belum dipasang di Secrets Streamlit. Cek pengaturan Settings > Secrets kamu."
    
    try:
        # Panggil AI
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Bertindaklah sebagai Sekretaris Himpunan Mahasiswa.
        Buatkan draft surat formal untuk menindaklanjuti keluhan mahasiswa.
        
        Data Pelapor:
        - Nama: {nama}
        - Kategori: {kategori}
        - Keluhan: {keluhan}
        
        Tugasmu:
        1. Buat PERIHAL surat yang singkat & formal.
        2. Tentukan TUJUAN JABATAN (misal: Kepala Bagian Umum / Kajur Sains Data).
        3. Buat ISI SURAT LENGKAP (Pembuka, Inti masalah yang dibahasakan ulang dengan sopan/formal, dan Penutup).
        
        Format output WAJIB menggunakan pemisah '|||' :
        PERIHAL|||TUJUAN|||ISI_LENGKAP
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Pecah hasilnya
        parts = text.split("|||")
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        else:
            # Kalau AI-nya jawab tapi formatnya salah, tetap tampilin jawabannya biar bisa diedit
            return "Pengajuan Tindak Lanjut", "Ketua Program Studi Sains Data", text
            
    except Exception as e:
        # INI YANG PENTING: Tampilkan Error Aslinya
        return "ERROR TEKNIS", "Admin", f"Gagal generate AI. Pesan Error Asli: {str(e)}"
