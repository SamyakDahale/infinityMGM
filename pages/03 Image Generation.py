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
    num_images = round(duration / 5)
    subt = st.session_state.get("subt")


# --- Prompt input ---
user_ip = st.text_input("Search Prompt:", st.session_state["topic"]) # change to topic if needed

all_image_urls = []
num_images = max(1, round(duration / 5))  # Minimum of 1 image
urls = search_google_images(user_ip)[:num_images]
all_image_urls.extend(urls)

valid_urls = []
cols = st.columns(2)

for i, url in enumerate(all_image_urls):
    try:
        response = requests.get(url, timeout=5)  # Set a timeout
        img = Image.open(BytesIO(response.content))

        with cols[i % 2]:
            st.image(img, caption=f"Image {i + 1}", use_container_width=True)
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            
        valid_urls.append(url)

    except Exception as e:
  
        # Retry by fetching a new image
        retry_urls = search_google_images(user_ip)
        for retry_url in retry_urls:
            if retry_url not in all_image_urls:
                try:
                    retry_response = requests.get(retry_url, timeout=5)
                    retry_img = Image.open(BytesIO(retry_response.content))

                    with cols[i % 2]:
                        st.image(retry_img, caption=f"Retry Image {i + 1}", use_container_width=True)
                        retry_buffer = BytesIO()
                        retry_img.save(retry_buffer, format="PNG")
                     
                    valid_urls.append(retry_url)
                    break
                except:
                    continue  # Skip if even retry fails

# Store only the successfully loaded image URLs
st.session_state["image_urls"] = valid_urls


if st.button("➡️ Continue to Video Generation"):
    if "audio_data" in st.session_state:
     st.session_state["audio_data"] = st.session_state["audio_data"]
     st.session_state["audio_filename"] = st.session_state.get("audio_filename", "natural_voice.mp3")
     st.session_state["duration"] = duration
     st.session_state["subt"] = subt
     st.switch_page("pages/04 Video Generation.py")