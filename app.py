# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time

# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="ProPrompt Maker",
    layout="centered"
)

st.title("ProPrompt Maker")
st.write(
    "Upload video MP4 Anda, lalu aplikasi akan menghasilkan "
    "prompt AI image/video yang detail (bahasa Inggris)."
)

# ==============================
# AMBIL API KEY DARI SECRETS
# ==============================
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error(
        "API Key tidak ditemukan.\n\n"
        "Silakan tambahkan GOOGLE_API_KEY di Streamlit Secrets."
    )
    st.stop()

genai.configure(api_key=API_KEY)

# ==============================
# UPLOAD VIDEO
# ==============================
uploaded_file = st.file_uploader(
    "Upload video MP4",
    type=["mp4"]
)

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb < 10:
        st.error(
            f"Ukuran video terlalu kecil ({file_size_mb:.2f} MB). "
            "Minimal 10 MB."
        )
    else:
        st.success(f"Video diterima ({file_size_mb:.2f} MB)")

        if st.button("Generate Prompt"):
            with st.spinner("Menganalisis video, mohon tunggu..."):
                try:
                    # ==============================
                    # SIMPAN FILE SEMENTARA
                    # ==============================
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".mp4"
                    ) as tmp:
                        tmp.write(uploaded_file.read())
                        video_path = tmp.name

                    # ==============================
                    # UPLOAD KE GEMINI
                    # ==============================
                    video_file = genai.upload_file(path=video_path)

                    while video_file.state.name == "PROCESSING":
                        time.sleep(3)
                        video_file = genai.get_file(video_file.name)

                    # ==============================
                    # GENERATE PROMPT
                    # ==============================
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash"
                    )

                    instruction = (
                        "Create a highly detailed AI image prompt based on "
                        "the visual elements, lighting, colors, camera angle, "
                        "and atmosphere of this video. "
                        "Write in English. "
                        "Optimize for Midjourney or similar AI image generators."
                    )

                    response = model.generate_content(
                        [video_file, instruction]
                    )

                    result_prompt = response.text.strip()

                    # ==============================
                    # OUTPUT
                    # ==============================
                    st.divider()
                    st.subheader("Generated Prompt")

                    st.text_area(
                        "Copy the prompt below:",
                        value=result_prompt,
                        height=220
                    )

                    st.caption(
                        "Tip: tap & hold the text to copy on mobile."
                    )

                    # ==============================
                    # CLEAN UP
                    # ==============================
                    os.remove(video_path)

                except Exception as e:
                    st.error("Terjadi kesalahan saat memproses video.")
                    st.exception(e)

# ==============================
# FOOTER
# ==============================
st.divider()
st.caption("Powered by Gemini 1.5 Flash")