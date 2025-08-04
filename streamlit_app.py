import streamlit as st
import requests
import xmltodict
import os
import google.generativeai as genai

# Load Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# --- Fetch Papers (ArXiv) ---
def fetch_papers(query, max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}"
    data = requests.get(url).content
    feed = xmltodict.parse(data)
    entries = feed.get("feed", {}).get("entry", [])
    if not isinstance(entries, list):
        entries = [entries] if entries else []
    papers = []
    for e in entries:
        papers.append({
            "title": e.get("title", "No title").strip(),
            "summary": e.get("summary", "").strip(),
            "link": e.get("id", "#")
        })
    return papers

# --- Gemini: Generate a real literature survey ---
def create_lit_review_gemini(topic, papers):
    try:
        model = genai.GenerativeModel("gemini-pro")
        abstracts = "\n\n".join([f"Title: {p['title']}\nAbstract: {p['summary']}" for p in papers])
        prompt = f"""
        You are an academic assistant. Write an 800-word structured literature review on the topic '{topic}'.
        Use the following research paper abstracts:
        {abstracts}
        Structure the review with an introduction, thematic grouping of findings, discussion of gaps, and a conclusion.
        Use academic tone and cite the papers inline as [1], [2], etc. Provide references at the end with their titles.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error using Gemini: {e}"

# --- Streamlit UI ---
st.title("❤️ Happy Birthday Dr. Sohini!")
st.write("I'm your personal literature survey assistant created by your geeky husband. 🎂 Ask me for a topic!")

topic = st.text_input("Enter a research topic", placeholder="e.g., Electrochemistry in wearable devices")
if st.button("Generate Literature Survey"):
    with st.spinner("Brewing your literature survey with Gemini... ☕"):
        papers = fetch_papers(topic)
        if not papers:
            st.error("No papers found. Try a different topic.")
        else:
            review = create_lit_review_gemini(topic, papers)
            st.subheader("Literature Review")
            st.write(review)
            st.subheader("References:")
            for i, p in enumerate(papers, 1):
                st.markdown(f"[{i}] [{p['title']}]({p['link']})")
