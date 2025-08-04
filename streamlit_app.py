import streamlit as st
import requests
import xmltodict
import os

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Hugging Face summarization API
def query_hf_api(text):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": text[:1024]}  # Limit input size
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]
        else:
            return "Summary unavailable."
    except Exception:
        return "Summary unavailable."

# ArXiv fetch
def fetch_papers(query, max_results=5):
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

# Generate Literature Review
def create_lit_review(topic):
    papers = fetch_papers(topic)
    summaries = []
    for p in papers:
        summary = query_hf_api(p.get("summary", ""))  # Safe access
        summaries.append(summary)
    combined_summary = " ".join(summaries)
    return combined_summary, papers

# Streamlit UI
st.title("❤️ Happy Birthday Dr. Sohini!")
st.write("I'm your personal literature survey assistant created by your geeky husband. 🎂 Ask me for a topic!")

topic = st.text_input("Enter a research topic")
if st.button("Generate Literature Survey"):
    with st.spinner("Brewing your literature survey... ☕"):
        review, papers = create_lit_review(topic)
        st.subheader("Literature Review")
        st.write(review)
        st.subheader("References:")
        for p in papers:
            st.markdown(f"- [{p['title']}]({p['link']})")
