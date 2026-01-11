# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time
from st_copy_to_clipboard import st_copy_to_clipboard

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="ProPrompt Maker", page_icon="🚀", layout="centered")

st.title("🚀 Video to AI Prompt Maker")
st.markdown("""
    Aplikasi ini merubah video Anda menjadi prompt teks detail untuk AI Image Generator.
    * **Format:** MP4
    * **Syarat:** Minimal 10MB
""")

# --- SIDEBAR: KONFIGURASI ---
with st.sidebar:
    st.header("Konfigurasi")
    api_key = st.text_input("AIzaSyA6KCcIIiI59Pac98NbPsJ9ms3mScQz04g", type="password")
    st.info("Dapatkan API Key di [Google AI Studio](https://aistudio.google.com/)")

# --- LOGIKA UTAMA ---
if api_key:
    genai.configure(api_key=api_key)

    uploaded_file = st.file_uploader("Upload Video MP4 Anda", type=["mp4"])

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        # Validasi Minimal 10MB
        if file_size_mb < 10:
            st.error(f"❌ Ukuran file terlalu kecil ({file_size_mb:.2f} MB). Minimal harus 10MB.")
        else:
            st.success(f"✅ Video siap (Ukuran: {file_size_mb:.2f} MB)")
            
            if st.button("Mulai Generate Prompt ✨"):
                with st.spinner("Sedang menganalisis video... (Proses ini memakan waktu tergantung durasi)"):
                    try:
                        # 1. Simpan Temporary
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = tmp.name

                        # 2. Upload ke Google AI
                        video_file = genai.upload_file(path=tmp_path)
                        
                        # 3. Tunggu Proses Server
                        while video_file.state.name == "PROCESSING":
                            time.sleep(3)
                            video_file = genai.get_file(video_file.name)

                        # 4. Generate Konten
                        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                        prompt_request = (
                            "Tuliskan sebuah prompt gambar AI yang sangat mendetail berdasarkan "
                            "elemen visual, warna, pencahayaan, dan subjek dalam video ini. "
                            "Gunakan bahasa Inggris agar optimal di Midjourney/DALL-E."
                        )
                        
                        response = model.generate_content([video_file, prompt_request])
                        hasil_prompt = response.text

                        # 5. Tampilkan Hasil & Tombol Copy
                        st.divider()
                        st.subheader("📝 Hasil Prompt:")
                        st.text_area("Copy prompt di bawah ini:", value=hasil_prompt, height=200)
                        
                        # Fitur Copy to Clipboard
                        st_copy_to_clipboard(hasil_prompt)
                        st.caption("Klik tombol di atas untuk menyalin teks.")

                        # Bersihkan file
                        os.remove(tmp_path)

                    except Exception as e:
                        st.error(f"Terjadi kesalahan teknis: {str(e)}")
else:
    st.warning("⚠️ Harap masukkan API Key di sidebar untuk mengaktifkan aplikasi.")

# --- FOOTER ---
st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Gemini 1.5 Flash")