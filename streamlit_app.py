import streamlit as st
import requests, xmltodict
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor

# ========== CONFIG ==========
NUM_PAPERS = 5  # Reduced for speed
SUMMARIZER_MODEL = "sshleifer/distilbart-cnn-12-6"
summarizer = pipeline("summarization", model=SUMMARIZER_MODEL)

st.set_page_config(page_title="LitSurvey - Gift for Sohini", page_icon="🎓", layout="centered")
st.title("🎉 Happy Birthday Dr. Sohini! ❤️")
st.markdown("I'm your personal literature survey assistant, crafted by your geeky husband. Type a topic below, and I’ll whip up a research‑style review for you!")

topic = st.text_input("Enter your research topic:", placeholder="e.g., Electrochemistry for wearable sensors")

# ========== FETCH PAPERS ==========
def fetch_pubmed(topic, max_results=NUM_PAPERS):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={topic}&retmax={max_results}&retmode=json"
    ids = requests.get(url).json().get("esearchresult", {}).get("idlist", [])
    papers = []
    for pid in ids:
        abs_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&rettype=abstract&retmode=xml"
        paper_xml = xmltodict.parse(requests.get(abs_url).content)
        try:
            article = paper_xml['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['Article']
            title = article['ArticleTitle']
            abstract = article['Abstract']['AbstractText'][0]
            papers.append({"title": title, "abstract": abstract, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
        except:
            continue
    return papers

def summarize_paper(paper):
    summary = summarizer(paper['abstract'], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
    return {**paper, "summary": summary}

# ========== GENERATE LIT REVIEW ==========
if st.button("Generate Literature Survey"):
    if not topic:
        st.warning("Please enter a topic first.")
    else:
        st.info("Brewing your quick literature review… ☕ This will take ~20–30 seconds.")
        papers = fetch_pubmed(topic)

        if not papers:
            st.error("No papers found. Try a different topic.")
        else:
            # Summarize in parallel
            with ThreadPoolExecutor() as executor:
                summarized_papers = list(executor.map(summarize_paper, papers))

            # Stitch review
            review = "### Literature Review\n\n"
            for p in summarized_papers:
                review += f"**{p['title']}**\n\n{p['summary']}\n\n[Read more]({p['url']})\n\n"

            st.markdown(review)
            st.download_button("📥 Copy Full Review", review, file_name="literature_survey.txt")
