
import streamlit as st
import requests, xmltodict
from transformers import pipeline

st.set_page_config(page_title="LitSurvey - Gift for Sohini", page_icon="🎓", layout="centered")
st.title("🎉 Happy Birthday Dr. Sohini! ❤️")
st.markdown("I'm your personal literature survey assistant, crafted by your geeky husband. Type a topic below, and I’ll whip up a research‑style review for you!")

topic = st.text_input("Enter your research topic:", placeholder="e.g., Electrochemistry for wearable sensors")

if st.button("Generate Literature Survey"):
    st.info("Brewing your literature review… ☕")
    st.write("This is where the 800-word Nature-style review will appear.")
    st.download_button("Download as PDF", "Sample PDF content", file_name="literature_survey.pdf")
