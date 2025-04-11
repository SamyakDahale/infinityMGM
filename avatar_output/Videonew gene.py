import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import tempfile
import os
import json

with open("config.json") as f:
    config = json.load(f)

    
DID_API_KEY = config["DID_API_KEY"]
DID_BASE_URL = "https://api.d-id.com"

headers_did = {
    "Authorization": f"Bearer {DID_API_KEY}",
    "Content-Type": "application/json"
}

AVATAR_URL = "https://create-images-results.d-id.com/DefaultPresenters/amy-white.jpeg"  # Replace or use selection logic


st.title("🎞️ Video Generator")
st.markdown("This page creates a video using your images and generated audio.")

# --- Validate session state ---
if "image_urls" not in st.session_state or not st.session_state["image_urls"]:
    st.error("❌ No image URLs found in session. Please go back and search for images.")
    st.stop()

if "audio_data" not in st.session_state or not st.session_state["audio_data"]:
    st.error("❌ No audio data found. Please generate audio first.")
    st.stop()

image_urls = st.session_state["image_urls"]
audio_data = st.session_state["audio_data"]
duration = st.session_state["duration"]
subt = st.session_state["subt"]


# --- Generate Video Button ---
if st.button("🎬 Generate Video"):
    st.info("📷 Loading images from URLs...")

    image_duration = duration / len(image_urls)  # Evenly distribute total duration

    clips = []
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            img_clip = ImageClip(np.array(img)).set_duration(image_duration)
            clips.append(img_clip)
        except Exception as e:
            st.warning(f"Could not load image {i + 1}: {e}")

    if not clips:
        st.error("⚠️ No valid images to use.")
        st.stop()

    # --- Combine clips ---
    video_clip = concatenate_videoclips(clips, method="compose")

    # --- Write audio to temporary file ---
    audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(audio_temp.name, "wb") as f:
        f.write(audio_data)

    # --- Load audio clip ---
    audio_clip = AudioFileClip(audio_temp.name)
    video_clip = video_clip.set_audio(audio_clip).set_fps(24)

    # --- Export final video to a temporary file ---
    output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_path = output_temp.name

    st.info("🎬 Rendering final video...")
    video_clip.write_videofile(video_path, codec="libx264", audio_codec="aac")

    # --- Display video ---
    with open(video_path, "rb") as f:
        video_bytes = f.read()
        st.video(video_bytes)
        st.download_button("📥 Download Video", video_bytes, file_name="final_video.mp4", mime="video/mp4")


if st.button("🔁 Generate Animated Avatar Video"):
    st.info("📡 Uploading audio and generating video using D-ID...")

    # Save audio to temp file
    audio_temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    with open(audio_temp_path, "wb") as f:
        f.write(audio_data)

    # Upload audio to D-ID
    with open(audio_temp_path, "rb") as f:
        files = {'audio': f}
        upload_response = requests.post(f"{DID_BASE_URL}/v1/upload", headers={"Authorization": f"Bearer {DID_API_KEY}"}, files=files)

    if upload_response.status_code != 200:
        st.error("❌ Failed to upload audio to D-ID.")
        st.stop()

    audio_url = upload_response.json().get("url")

    payload = {
        "script": {
            "type": "audio",
            "audio_url": audio_url
        },
        "source_url": AVATAR_URL,
        "config": {
            "fluent": True,
            "pad_audio": 0.5
        }
    }

    talk_response = requests.post(f"{DID_BASE_URL}/v1/talks", json=payload, headers=headers_did)

    if talk_response.status_code != 200:
        st.error(f"❌ Error creating D-ID video: {talk_response.text}")
        st.stop()

    talk_id = talk_response.json().get("id")
    st.success("✅ Video generation started. Waiting for final video...")

    # Polling for video completion
    status_url = f"{DID_BASE_URL}/v1/talks/{talk_id}"
    video_url = None
    for _ in range(30):
        poll_response = requests.get(status_url, headers=headers_did)
        result = poll_response.json()
        if result.get("result_url"):
            video_url = result["result_url"]
            break
        time.sleep(2)

    if not video_url:
        st.error("⚠️ Timed out waiting for video. Try again.")
        st.stop()

    st.video(video_url)
    st.markdown(f"[📥 Download Animated Video]({video_url})", unsafe_allow_html=True)


if st.button("➡️ Go to to Self Assessment"):
    if "subt" in st.session_state:
     
     st.session_state["script"] = subt
     st.switch_page("pages/05 Self Assessment.py")