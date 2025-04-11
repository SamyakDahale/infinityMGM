import streamlit as st
import google.generativeai as genai
import json

# Load API key
with open('config.json') as f:
    config = json.load(f)

# Page setup
st.set_page_config(layout="centered")
st.title("📽️ Topic Generation")

# Apply custom styling
with open("style.html", "r") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

# Configure Gemini API
API_KEY = config['API_KEY']
genai.configure(api_key=API_KEY)

# Input: Prompt
user_input = st.text_area("Enter your prompt here:")

# Input: Language
language_dict = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "German": "de",
    "Tamil": "ta",
    "Gujarati": "gu"
}
selected_lang = st.selectbox("Select your language:", list(language_dict.keys()))

# Input: Duration
duration = st.slider("⏲️ Select Duration for Video (in seconds)", min_value=30, max_value=300, value=30, step=15)

# Fixed options
tone_opts = ["Informative", "Educational", "Technical", "Promotional"]
purpose_opts = ["Explanation", "Tutorial", "Demo", "Marketing"]
audience_opts = ["School Students", "Sophomores", "Researchers", "Business leaders", "General Public"]

# Tone checkboxes
st.markdown("### 🎯 Select Tone")
selected_tone = []
cols = st.columns(len(tone_opts))
for i, opt in enumerate(tone_opts):
    if cols[i].checkbox(opt, key=f"tone_{opt}"):
        selected_tone.append(opt)

# Purpose checkboxes
st.markdown("### 🎯 Select Purpose")
selected_purpose = []
cols = st.columns(len(purpose_opts))
for i, opt in enumerate(purpose_opts):
    if cols[i].checkbox(opt, key=f"purpose_{opt}"):
        selected_purpose.append(opt)

# Audience checkboxes
st.markdown("### 🎯 Select Audience")
selected_audience = []
cols = st.columns(len(audience_opts))
for i, opt in enumerate(audience_opts):
    if cols[i].checkbox(opt, key=f"audience_{opt}"):
        selected_audience.append(opt)

# Generate content
if st.button("Generate"):
    if user_input.strip():
        with st.spinner("Generating..."):
            try:
                instruction = (
                    f"You are tasked with explaining the concept of {user_input}. Generate clear, well-structured content "
                    f"in {selected_lang}. Avoid excessive formatting such as markdown, bold text, or special characters. "
                )

                if selected_tone:
                    instruction += (
                        f"The explanation must adopt a {', '.join(selected_tone)} tone, "
                        f"ensuring consistency throughout the content. "
                    )

                if selected_purpose:
                    instruction += (
                        f"The content must fulfill the purpose of {', '.join(selected_purpose)}. "
                        f"Focus accordingly—for example, if the purpose is Marketing, highlight key selling points and advantages. "
                        f"If it is a Tutorial or Demo, ensure a step-by-step approach with examples. "
                    )

                if selected_audience:
                    instruction += (
                        f"Tailor the depth and vocabulary of the content to suit {', '.join(selected_audience)}. "
                        f"For School Students, keep it very simple, use analogies, and define terms. "
                        f"For Sophomores, use moderate technical depth with relatable examples. "
                        f"For Researchers, provide a comprehensive, in-depth exploration including theory, context, and advanced terms. "
                        f"For Business Leaders, keep it strategic and high-level with use cases and impact. "
                        f"For General Public, maintain clarity and relatability, avoiding jargon. "
                    )

                instruction += (
                    f"The explanation should be concise enough such that its audio version does not exceed {duration} seconds. "
                    f"Prioritize clarity and coherence within that time frame."
                )

                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=instruction
                )

                response = model.generate_content(user_input)
                generated_text = response.text

                st.subheader("Generated Response:")
                st.write(generated_text)

                st.download_button(
                    label="📥 Download as .txt",
                    data=generated_text,
                    file_name="generated_text.txt",
                    mime="text/plain"
                )

                st.session_state["script"] = generated_text
                st.session_state["topic"] = user_input
                st.session_state["duration"] = duration

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a prompt first.")

# Navigation
if st.button("➡️ Continue to Audio Generation"):
    st.switch_page("pages/02 Audio Generation.py")
