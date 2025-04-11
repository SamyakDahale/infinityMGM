import streamlit as st
import requests
from io import BytesIO
from PIL import Image

import json

with open('config.json') as f:
    config = json.load(f)
# Configure  API
API_KEY = config['IMGAPI_KEY']
CSE_ID =  config['CSE_ID']



# --- Google Image Search Function ---
def search_google_images(query, num_images=8):
    search_url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": CSE_ID,
        "key": API_KEY,
        "searchType": "image",
        "num": num_images,
        # "rights": "cc_publicdomain"  # Optional: fetch copyright-free images
    }

    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        results = response.json()
        return [item["link"] for item in results.get("items", [])]
    else:
        st.error(f"❌ Error {response.status_code}: {response.text}")
        return []
    
variation_tags = [
    "infographic style with labels",
    "chalkboard diagram illustration",
    "educational poster layout",
    "simple colorful cartoon style",
    "whiteboard sketch style",
    "scientific illustration with annotations",
    "hand-drawn classroom diagram",
    "3D isometric educational scene"
]
def enhance_prompt(topic):
    return (
        f"A highly detailed, realistic digital illustration representing the concept of '{topic}', "
        f" and rich color contrast."
    )

with open("style.html", "r") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

# -- UI ---
st.title("🔍 Topic-Based Image Search")
st.markdown("This tool fetches educational images based on your topic using Google Custom Search API.")

# --- Check if topic exists ---
if "topic" not in st.session_state or not st.session_state["topic"].strip():
    st.warning("⚠️ No topic found. Please go back and enter a topic first.")
    st.stop()
else:
    duration = st.session_state.get("duration", 60)
    num_images = round(duration / 7)
    subt = st.session_state.get("subt")


# --- Prompt input ---
user_ip = st.text_input("Search Prompt:", st.session_state["topic"]) # change to topic if needed

# --- Trigger Image Search ---
if st.button("🔎 Search Images"):
    with st.spinner("Searching Images..."):
        all_image_urls = []

        # Dynamically determine number of images
        num_images = max(1, round(duration / 7))  # Minimum of 1 image
        urls = search_google_images(user_ip)[:num_images]
        all_image_urls.extend(urls)

        if all_image_urls:
            st.success(f"✅ Retrieved {len(all_image_urls)} image(s)!")

            cols = st.columns(2)
            for i, url in enumerate(all_image_urls):
                try:
                    response = requests.get(url)
                    img = Image.open(BytesIO(response.content))

                    with cols[i % 2]:
                        st.image(img, caption=f"Image {i + 1}", use_container_width=True)
                        img_buffer = BytesIO()
                        img.save(img_buffer, format="PNG")
                        st.download_button(
                            label="📥 Download",
                            data=img_buffer.getvalue(),
                            file_name=f"image_{i+1}.png",
                            mime="image/png",
                            key=f"download_{i}"
                        )
                except Exception as e:
                    st.warning(f"⚠️ Could not load image {i + 1}: {e}")

            st.session_state["image_urls"] = all_image_urls



if st.button("➡️ Continue to Video Generation"):
    if "audio_data" in st.session_state:
     st.session_state["audio_data"] = st.session_state["audio_data"]
     st.session_state["audio_filename"] = st.session_state.get("audio_filename", "natural_voice.mp3")
     st.session_state["duration"] = duration
     st.session_state["subt"] = subt
     st.switch_page("pages/04 Video Generation.py")