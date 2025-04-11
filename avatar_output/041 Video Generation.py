import streamlit as st
import requests
import json
import time

# Load D-ID API key
with open('config.json') as f:
    config = json.load(f)

DID_API_KEY = config['DID_API_KEY']
DID_BASE_URL = "https://api.d-id.com"

headers = {
    "Authorization": f"Basic {DID_API_KEY}",
    "Content-Type": "application/json"
}

st.title("🧠 Talking Avatar Video Generator")

# Validate session data
if "audio_data" not in st.session_state or "subt" not in st.session_state:
    st.error("⚠️ Audio not found. Please generate speech first.")
    st.stop()

# Use a default D-ID avatar or upload a custom image
st.markdown("Choose or upload an avatar image:")
avatar_option = st.radio("Avatar Source", ["Use default avatar", "Upload custom avatar"])
avatar_url = "https://create.d-id.com/images/default-avatar.jpeg"  # Change to your desired avatar

if avatar_option == "Upload custom avatar":
    uploaded_img = st.file_uploader("Upload a portrait image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_img:
        files = {
            'image': uploaded_img.getvalue()
        }
        res = requests.post(f"{DID_BASE_URL}/images", headers={"Authorization": f"Basic {DID_API_KEY}"}, files=files)
        if res.status_code == 200:
            avatar_url = res.json()['url']
        else:
            st.error(f"Image upload failed: {res.text}")
            st.stop()

# Generate video
if st.button("🎥 Generate Talking Video"):
    with st.spinner("Generating video..."):

        # Step 1: Upload the audio
        audio = st.session_state["audio_data"]
        audio_upload = requests.post(
            f"{DID_BASE_URL}/audios",
            headers={"Authorization": f"Basic {DID_API_KEY}"},
            files={"audio": ("voice.mp3", audio, "audio/mpeg")}
        )

        if audio_upload.status_code != 200:
            st.error("❌ Audio upload failed.")
            st.stop()

        audio_url = audio_upload.json()["url"]

        # Step 2: Request video generation
        payload = {
            "source_url": avatar_url,
            "script": {
                "type": "audio",
                "audio_url": audio_url
            }
        }

        video_res = requests.post(
            f"{DID_BASE_URL}/talks",
            headers=headers,
            json=payload
        )

        if video_res.status_code != 200:
            st.error(f"❌ Failed to start video generation: {video_res.text}")
            st.stop()

        video_id = video_res.json()["id"]

        # Step 3: Polling until video is ready
        status_url = f"{DID_BASE_URL}/talks/{video_id}"
        video_url = None

        for _ in range(30):  # wait max ~30 seconds
            time.sleep(2)
            poll = requests.get(status_url, headers=headers)
            if poll.status_code == 200 and poll.json().get("result_url"):
                video_url = poll.json()["result_url"]
                break

        if video_url:
            st.success("✅ Video generated!")
            st.video(video_url)
            st.markdown(f"[🔗 Download Video]({video_url})", unsafe_allow_html=True)
        else:
            st.error("❌ Video generation timed out. Please try again.")
