if submitted:
                if not keluhan: 
                    st.warning("Mohon isi deskripsi laporan.")
                else:
                    # --- BUKA BLOCK DEBUGGING ---
                    with st.spinner("Mengirim..."):
                        waktu = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        link_bukti = "-"
                        
                        # Upload Gambar (Kalau ada)
                        if bukti_file:
                            try:
                                files = {"image": bukti_file.getvalue()}
                                params = {"key": API_KEY_IMGBB}
                                res = requests.post("https://api.imgbb.com/1/upload", params=params, files=files)
                                data_res = res.json()
                                if data_res.get("success"): link_bukti = data_res["data"]["url"]
                            except Exception as e_img:
                                st.warning(f"Gagal upload gambar: {e_img}")

                        # SIMPAN KE DATABASE
                        try:
                            # Cek dulu apakah sheet berhasil terhubung
                            if sheet is None:
                                st.error("❌ Gagal Konek Database! Cek apakah nama Tab di Google Sheet sudah 'Laporan' dan Email Service Account sudah di-invite sebagai Editor.")
                            else:
                                sheet.append_row([waktu, nama, npm, jurusan, kategori, keluhan, "Pending", link_bukti])
                                st.success("✅ Terkirim! Data sudah masuk.")
                        
                        except Exception as e:
                            # INI AKAN MENAMPILKAN ERROR ASLINYA
                            st.error(f"⚠️ Terjadi Error Teknis: {str(e)}")
                            st.write("Coba screenshot pesan error di atas dan kirim ke aku ya.")
