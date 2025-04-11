import streamlit as st
import requests
import tempfile
import time
import json

with open('config.json') as f:
    config = json.load(f)
# Configure  API
ELEVENLABS_API_KEY = config['ELEVENLABS_API_KEY']


# --- CONFIG ---

VOICE_OPTIONS = {
    "Adam (Male, Neutral)": "pNInz6obpgDQGcFmaJgB",
    "Bella (Female, Friendly)": "EXAVITQu4vr4xnSDxMaL",
    "Elli (Female, Formal)": "MF3mGyEYCl7XYWbV9V6O",
    "Josh (Male, Deep)": "TxGEqnHWrfWFTfGW9XjX",
    "Rachel (Female, Energetic)": "21m00Tcm4TlvDq8ikWAM",
    "Arnold (Male, Dramatic)": "VR6AewLTigWG4xSOukaG"
}

headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}


# ---  Text-to-Speech ---
def text_to_speech_elevenlabs(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        with open(temp_audio.name, "wb") as f:
            f.write(response.content)
        return temp_audio.name
    else:
        st.error(f"❌ Error: {response.status_code} - {response.text}")
        return None

# --- UI ---

with open("style.html", "r") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

st.title("🎧 Natural Speech Generator from Text")
st.markdown("Choose your input source:")

input_choice = st.radio(
    "Choose input source:",
    ("Use script from previous page", "Upload .txt file")
)

text = ""

if input_choice == "Use script from previous page":
    if "script" in st.session_state and st.session_state["script"].strip():
        text = st.session_state["script"]
        topic = st.session_state["topic"]
        duration = st.session_state["duration"]

        st.text_area("📜 Script Preview", text, height=200)
    else:
        st.warning("⚠️ No script found in session. Please enter a topic in the previous step.")

elif input_choice == "Upload .txt file":
    uploaded_file = st.file_uploader("📄 Upload a .txt file", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        st.text_area("📄 File Preview", text, height=200)

# 🔊 Select Voice
selected_voice = st.selectbox("🎙️ Choose Voice", list(VOICE_OPTIONS.keys()))
voice_id = VOICE_OPTIONS[selected_voice]

# ▶️ Generate audio
if text and st.button("🔊 Generate Natural Voice"):
    with st.spinner("Generating speech..."):
        audio_path = text_to_speech_elevenlabs(text, voice_id)
        if audio_path:
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
                st.audio(audio_data, format="audio/mp3")
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_data,
                    file_name="natural_voice.mp3",
                    mime="audio/mpeg"
                )
            st.session_state["audio_data"] = audio_data
            st.session_state["duration"] = duration
            st.session_state["audio_filename"] = "natural_voice.mp3"
            st.session_state["subt"] = text

# ➡️ Move to next
if st.button("➡️ Continue to Image Generation"):
    st.switch_page("pages/03 Image Generation.py")


