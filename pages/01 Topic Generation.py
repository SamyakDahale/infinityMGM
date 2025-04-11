import streamlit as st
import google.generativeai as genai
import json

with open('config.json') as f:
    config = json.load(f)

st.set_page_config(layout="centered")
st.title("📽️ Topic Generation")

# Configure Gemini API
API_KEY = config['API_KEY']
genai.configure(api_key=API_KEY)

with open("style.html", "r") as f:
    st.markdown(f.read(), unsafe_allow_html=True)


user_input = st.text_area("Enter your prompt here:")
generated_text = ""

language_dict = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "German": "de",
    "Tamil": "ta",
    "Gujarati": "gu"
    
}

selected_lang = st.selectbox("Select your language:", list(language_dict.keys()))


# Keyword-based logic for suggestions
def get_dynamic_options(prompt):
    prompt = prompt.lower()
    tone, purpose, audience = set(), set(), set()

    if any(word in prompt for word in ["learn", "education", "explain", "study", "understand"]):
        tone.update(["Informative", "Educational"])
        purpose.update(["Explanation", "Tutorial", "Research"])
        audience.update(["Beginners", "Students", "Researchers"])

    if any(word in prompt for word in ["promote", "ad", "marketing", "sales"]):
        tone.update(["Promotional", "Enthusiastic"])
        purpose.update(["Marketing", "Demo"])
        audience.update(["Businesses", "General Public"])

    if any(word in prompt for word in ["developer", "code", "software", "technical"]):
        tone.update(["Technical", "Detailed"])
        purpose.update(["Explanation", "Demo", "Research"])
        audience.update(["Developers", "Tech Enthusiasts", "Researchers"])

    if not tone:
        tone = {"Informative", "Educational", "Technical", "Promotional"}
        purpose = {"Explanation", "Tutorial", "Demo", "Marketing"}
        audience = {"School Students", "Sophomores", "Researchers", "Business leaders", "General Public"}

    return list(tone), list(purpose), list(audience)

# 🚀 Get dynamic options
with st.container():
    tone_opts, purpose_opts, audience_opts = get_dynamic_options(user_input) if user_input else (
        ["Informative", "Educational", "Technical", "Promotional"],
        ["Explanation", "Tutorial", "Demo", "Marketing"],
        ["School Students", "Sophomores", "Researchers", "Business leaders", "General Public"]
    )

    st.markdown("### ⏲️ Select Duration for Video (in seconds)")
    duration = st.slider("Audio Duration", min_value=30, max_value=300, value=30, step=15)

    st.markdown("### 🎯 Select Tone")
    selected_tone = []
    cols = st.columns(len(tone_opts))
    for i, opt in enumerate(tone_opts):
        if cols[i].checkbox(opt, key=f"tone_{opt}"):
            selected_tone.append(opt)

    st.markdown("### 🎯 Select Purpose")
    selected_purpose = []
    cols = st.columns(len(purpose_opts))
    for i, opt in enumerate(purpose_opts):
        if cols[i].checkbox(opt, key=f"purpose_{opt}"):
            selected_purpose.append(opt)

    st.markdown("### 🎯 Select Audience")
    selected_audience = []
    cols = st.columns(len(audience_opts))
    for i, opt in enumerate(audience_opts):
        if cols[i].checkbox(opt, key=f"audience_{opt}"):
            selected_audience.append(opt)

# 📩 Generate
if st.button("Generate"):
    if user_input.strip():
        with st.spinner("Generating..."):
            try:

                 # 🧠 Create dynamic system instruction
                instruction = (
                f"You are tasked with explaining the concept of {user_input}. Generate clear, well-structured content "
                f"in {selected_lang}. Avoid excessive formatting such as markdown, bold text, or special characters. "
            )

            # Tone: Defines the voice/style of explanation
                if selected_tone:
                    instruction += (
                        f"The explanation must adopt a {', '.join(selected_tone)} tone, "
                        f"ensuring consistency throughout the content. "
                    )

                # Purpose: Defines the **intent** of the explanation
                if selected_purpose:
                    instruction += (
                        f"The content must fulfill the purpose of {', '.join(selected_purpose)}. "
                        f"Focus accordingly—for example, if the purpose is Marketing, highlight key selling points and advantages. "
                        f"If it is a Tutorial or Demo, ensure a step-by-step approach with examples. "
                    )

                # Audience: Controls the **depth and complexity**
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


                # 🔁 Reinitialize model with updated instruction
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

# ⏭️ Navigation
if st.button("➡️ Continue to Audio Generation"):
    st.switch_page("pages/02 Audio Generation.py")

