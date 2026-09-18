with st.form("form_lapor", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        nama = st.text_input("Nama Lengkap")
        npm = st.text_input("NPM")
        jurusan = st.selectbox("Prodi", ["Sains Data", "Biologi", "Fisika", "Matematika"])
    with c2:
        kategori = st.selectbox("Kategori", ["Fasilitas", "Akademik", "Keuangan", "Lainnya"])
        bukti_file = st.file_uploader("Upload Foto Bukti (JPG/PNG)", type=["png", "jpg", "jpeg"])

    keluhan = st.text_area("Deskripsi Masalah", height=150)

    terkait_pimpinan = st.checkbox(
        "Laporan ini menyangkut KAHIM / Ketua Umum secara langsung"
    )
    st.caption("Centang ini kalau laporanmu tentang tindakan atau kebijakan KAHIM/Ketum. Laporan jenis ini diproses lewat jalur khusus dan hanya dibaca panel terbatas, bukan admin advokasi biasa.")

    tombol = st.form_submit_button("Kirim Laporan 🚀")

    if tombol:
        if not keluhan:
            st.warning("Mohon isi deskripsi masalah.")
        else:
            with st.spinner("Mengirim laporan..."):
                waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                link_bukti = "-"

                if bukti_file:
                    try:
                        params_data = {"key": API_KEY_IMGBB}
                        files_data = {"image": bukti_file.getvalue()}
                        response = requests.post("https://api.imgbb.com/1/upload", data=params_data, files=files_data)
                        hasil = response.json()
                        if response.status_code == 200 and hasil.get("success"):
                            link_bukti = hasil["data"]["url"]
                    except:
                        pass

                # Jaring pengaman kedua: tetap cek kata kunci sebagai cadangan,
                # BUKAN sebagai penentu utama. Kalau salah satu terpicu, tetap
                # diarahkan ke jalur khusus (lebih baik salah arah ke sana
                # daripada bocor ke sheet publik).
                teks_gabungan = (str(nama) + " " + str(kategori) + " " + str(keluhan)).lower()
                kata_kunci_khusus = ["kahim", "azwar", "ketum", "ketua umum", "ketua himpunan"]
                terpicu_kata_kunci = any(kata in teks_gabungan for kata in kata_kunci_khusus)

                is_khusus_pimpinan = terkait_pimpinan or terpicu_kata_kunci

                try:
                    if is_khusus_pimpinan:
                        sheet_kahim = spreadsheet_utama.worksheet("Aspirasi_Kahim")
                        sheet_kahim.append_row([waktu, nama, npm, jurusan, "Azwar Kurniawan Syah (Kahim)", keluhan, "Masuk"])
                        st.session_state['pesan_sukses'] = "✅ Aspirasi khusus pimpinan berhasil dikirim secara rahasia dan aman!"
                        st.rerun()
                    else:
                        sheet_laporan = spreadsheet_utama.worksheet("Laporan")
                        sheet_laporan.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                        st.session_state['pesan_sukses'] = "✅ Laporan Berhasil Dikirim!"
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal Simpan Database: {e}")
