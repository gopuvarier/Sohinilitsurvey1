import streamlit as st
import requests
import xmltodict
import os

# ---- CONFIG ----
HF_API_KEY = os.getenv("HF_API_KEY")  # Add this in Streamlit secrets
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ---- HELPER FUNCTIONS ----
def query_hf_api(text):
    payload = {"inputs": text, "max_length": 150}
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    return response.json()[0]['summary_text'] if response.status_code == 200 else "Error in summarization."

def fetch_papers_arxiv(topic, max_results=5):
    url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&start=0&max_results={max_results}"
    data = requests.get(url).text
    parsed = xmltodict.parse(data)
    papers = parsed.get("feed", {}).get("entry", [])
    if isinstance(papers, dict): papers = [papers]
    return [{"title": p["title"], "summary": p.get("summary", ""), "link": p["id"]} for p in papers]

def fetch_papers_pubmed(topic, max_results=5):
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={topic}&retmode=json&retmax={max_results}"
    search_res = requests.get(search_url).json()
    ids = ",".join(search_res.get("esearchresult", {}).get("idlist", []))
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    fetch_res = xmltodict.parse(requests.get(fetch_url).text)
    articles = fetch_res.get("PubmedArticleSet", {}).get("PubmedArticle", [])
    if isinstance(articles, dict): articles = [articles]
    results = []
    for article in articles:
        art = article["MedlineCitation"]["Article"]
        title = art["ArticleTitle"]
        abstract = art.get("Abstract", {}).get("AbstractText", "")
        link = f"https://pubmed.ncbi.nlm.nih.gov/{article['MedlineCitation']['PMID']}/"
        results.append({"title": title, "summary": abstract, "link": link})
    return results

def create_lit_review(topic):
    # Collect papers
    arxiv = fetch_papers_arxiv(topic, 5)
    pubmed = fetch_papers_pubmed(topic, 5)
    papers = arxiv + pubmed

    # Generate individual summaries
    lit_summaries = []
    for p in papers:
        summary = query_hf_api(p["summary"][:1000]) if p["summary"] else "No summary available."
        lit_summaries.append({"title": p["title"], "summary": summary, "link": p["link"]})

    # Combine into a narrative
    intro = f"Research on **{topic}** has evolved rapidly in recent years, with multiple studies exploring diverse dimensions of this field. "
    body = " ".join([s['summary'] for s in lit_summaries])
    conclusion = "Collectively, these studies contribute to a deeper understanding of the topic and highlight promising directions for future research."

    narrative = f"{intro}{body} {conclusion}"

    # Add references
    references = "\n\n**References:**\n" + "\n".join([f"- [{p['title']}]({p['link']})" for p in lit_summaries])

    return narrative + references

# ---- UI ----
st.title("❤️ Happy Birthday Dr. Sohini!")
st.write("I'm your personal literature survey assistant created by your geeky husband. 🎂 Ask me for a topic!")

topic = st.text_input("Enter a research topic", placeholder="e.g., Antimicrobial resistance in wearable devices")
if st.button("Generate Literature Survey"):
    with st.spinner("Brewing your Nature-style literature review..."):
        review = create_lit_review(topic)
        st.markdown(review)
        st.success("Done! 🎉")
