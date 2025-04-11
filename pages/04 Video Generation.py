

# --- Generate Animated Avatar Video with D-ID ---
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import tempfile
import os
import json
import time
import base64

# --- Load API config ---
with open("config.json") as f:
    config = json.load(f)
    
DID_API_KEY = config["DID_API_KEY"]
DID_BASE_URL = "https://api.d-id.com" 



headers_did = {
    "Authorization": f"Basic {DID_API_KEY}",
    "Content-Type": "application/json"
}

AVATAR_URL = "https://create-images-results.d-id.com/DefaultPresenters/amy-white.jpeg"  # Optional: make dynamic later

with open("style.html", "r") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

# --- UI ---
st.title("🎞️ Video Generator Current ")
st.markdown("This page creates a video using your images and generated audio.")

# --- Session Validation ---
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

# --- Create video from images ---
if st.button("🎬 Generate Video"):
    st.info("📷 Loading images from URLs...")

    image_duration = duration / len(image_urls)
    clips = []

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            img_clip = ImageClip(np.array(img)).set_duration(image_duration)
            clips.append(img_clip)
        except Exception as e:
            st.warning(f"⚠️ Could not load image {i + 1}: {e}")

    if not clips:
        st.error("⚠️ No valid images to use.")
        st.stop()

    video_clip = concatenate_videoclips(clips, method="compose")

    # Save audio to temp file
    audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(audio_temp.name, "wb") as f:
        f.write(audio_data)

    audio_clip = AudioFileClip(audio_temp.name)
    video_clip = video_clip.set_audio(audio_clip).set_fps(24)

    output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_path = output_temp.name

    st.info("🎬 Rendering final video...")
    video_clip.write_videofile(video_path, codec="libx264", audio_codec="aac")

    with open(video_path, "rb") as f:
        video_bytes = f.read()
        st.video(video_bytes)
        st.download_button("📥 Download Video", video_bytes, file_name="final_video.mp4", mime="video/mp4")

# --- Generate Animated Avatar Video with D-ID ---
if st.button("🔁 Generate Animated Avatar Video"):
    st.info("📡 Sending audio to D-ID and generating avatar...")

    # Convert audio to base64 string
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")

    payload = {
        "script": {
            "type": "audio",
            "audio": audio_b64,
            "driver_url": "bank://lively"
        },
        "source_url": AVATAR_URL,
        "config": {
            "fluent": True,
            "pad_audio": 0.5
        }
    }

    talk_response = requests.post(
    f"{DID_BASE_URL}/talks", 
    headers=headers_did, 
    json=payload)

    if talk_response.status_code != 200:
        st.error("❌ Failed to generate D-ID video.")
        st.text(talk_response.text)
        st.stop()

    talk_id = talk_response.json().get("id")
    st.success("✅ Video generation started. Waiting for result...")

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
        st.error("⚠️ Timed out waiting for D-ID video. Try again.")
        st.stop()

    st.video(video_url)
    st.markdown(f"[📥 Download Animated Video]({video_url})", unsafe_allow_html=True)

# --- Go to Self-Assessment ---
if st.button("➡️ Go to to Self Assessment"):
    if "subt" in st.session_state:
        st.session_state["script"] = subt
        st.switch_page("pages/05 Self Assessment.py")

