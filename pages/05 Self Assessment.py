import streamlit as st
import google.generativeai as genai
import json
import re

with open('config.json') as f:
    config = json.load(f)

# Configure Gemini API
API_KEY = config['API_KEY']
genai.configure(api_key=API_KEY)

with open("style.html", "r") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

st.title("🧠 Self Assessment")
st.markdown("Answer the questions based on the content you've learned.")

# Ensure the script exists
if "script" not in st.session_state or not st.session_state["script"]:
    st.error("No content found from previous page. Please go back and generate content first.")
    st.stop()

script_content = st.session_state["script"]

# Generate MCQs once per session
if "mcqs" not in st.session_state:
    prompt = f"""
    Generate 3 multiple-choice questions based on the following content:
    ---
    {script_content}
    ---
    Format:
    Q1. <question>
    A. Option A
    B. Option B
    C. Option C
    D. Option D
    Answer: C
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # Extract MCQs using regex
    question_blocks = re.findall(r'(Q\d+\..*?)(?=\nQ\d+\.|\Z)', raw_output, flags=re.DOTALL)
    questions = []

    for block in question_blocks:
        try:
            lines = block.strip().split("\n")
            q_text = lines[0].split(". ", 1)[1].strip()
            options = [line[3:].strip() for line in lines[1:5]]
            answer_line = [line for line in lines if line.startswith("Answer")][0]
            correct = answer_line.split(":")[-1].strip().upper().replace(".", "")
            questions.append({
                "question": q_text,
                "options": options,
                "correct": correct
            })
        except Exception as e:
            st.warning(f"Skipping malformed question block due to error: {e}")

    if len(questions) < 1:
        st.error("❌ Could not parse any questions from Gemini's response.")
        st.stop()

    st.session_state["mcqs"] = questions

# Show questions
score = 0
responses = []

with st.form("mcq_form"):
    for i, q in enumerate(st.session_state["mcqs"]):
        user_choice = st.radio(f"**Q{i+1}. {q['question']}**", q["options"], key=f"q_{i}")
        responses.append(user_choice)

    submitted = st.form_submit_button("Submit Answers")

# Calculate score
if submitted:
    for i, response in enumerate(responses):
        correct_index = ord(st.session_state["mcqs"][i]["correct"]) - 65
        if correct_index < len(st.session_state["mcqs"][i]["options"]):
            correct_option = st.session_state["mcqs"][i]["options"][correct_index]
            if response == correct_option:
                score += 1

    st.success(f"🎉 You scored {score}/{len(st.session_state['mcqs'])}!")
