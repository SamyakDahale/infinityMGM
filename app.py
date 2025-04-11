import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_title="Pokémon Explainer")

left_image = Image.open("pages/384_f2.png").resize((400, 400))
right_image = Image.open("pages/pika.png").resize((400, 400))


with open("style1.html", "r", encoding="utf-8") as f:
    st.markdown(f.read(), unsafe_allow_html=True)


left, center, right = st.columns([1, 2, 1])

with left:
    st.markdown('<div class="animate-left">', unsafe_allow_html=True)
    st.image(left_image, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown("""
        <div style='text-align: center; margin-top: 3rem;'>
            <h1 class='animate-left' style='color: #ff1a1a; text-shadow: 3px 3px #000; margin-bottom: 1.5rem;'>Welcome to Pokémon Explainer!</h1>
            <p class='animate-right' style='color: #000; text-shadow: 2px 2px #fff; font-size: 16px; margin-bottom: 2rem;'>
                Turn any topic into epic visual learning experiences powered by AI and imagination.
            </p>
            <a href="Topic_Generation" class="start-button">Get Started</a>
        </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="animate-right">', unsafe_allow_html=True)
    st.image(right_image, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)