import streamlit as st
import os
import time
import tempfile
from google import genai

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="ProPrompt Maker",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 ProPrompt Maker")
st.caption("Upload video MP4 → AI akan membuat prompt visual detail (English)")

# ================== API KEY ==================
api_key = st.secrets.get("GOOGLE_API_KEY") or st.text_input(
    "Masukkan Google API Key",
    type="password"
)

if not api_key:
    st.warning("Masukkan Google API Key untuk melanjutkan.")
    st.stop()

client = genai.Client(api_key=api_key)

# ================== UPLOAD VIDEO ==================
uploaded = st.file_uploader(
    "Upload video MP4",
    type=["mp4"]
)

if uploaded:
    size_mb = uploaded.size / (1024 * 1024)

    if size_mb < 10:
        st.error("Minimal ukuran video 10MB")
        st.stop()

    st.success(f"Video diterima ({size_mb:.2f} MB)")

    if st.button("Generate AI Prompt ✨"):
        with st.spinner("Menganalisis video..."):
            try:
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
                    f.write(uploaded.read())
                    video_path = f.name

                # Upload video
                video = client.files.upload(file=video_path)

                # Wait until ready
                while video.state.name == "PROCESSING":
                    time.sleep(2)
                    video = client.files.get(name=video.name)

                # Generate prompt
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        video,
                        """Create a highly detailed AI image prompt based on this video.
Include subject, environment, lighting, colors, camera angle, style, mood.
Write in English, optimized for Midjourney / cinematic AI."""
                    ]
                )

                st.subheader("📝 AI Prompt Result")
                st.text_area(
                    "Copy prompt:",
                    response.text,
                    height=250
                )

                os.remove(video_path)

            except Exception as e:
                st.error(f"Gagal memproses video: {e}")
