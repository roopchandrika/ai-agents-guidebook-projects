import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from news_crew import generate_article  # noqa: E402

st.set_page_config(page_title="AI News Generator", page_icon="📰", layout="wide")
st.title("📰 AI News Generator")
st.caption("CrewAI + Cohere Command R7B + Serper web search")

with st.sidebar:
    topic = st.text_area("Topic", "Latest developments in AI agents", height=100)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    go = st.button("Generate article", type="primary", use_container_width=True)

if go and topic:
    with st.spinner("Researching and writing... (about a minute)"):
        try:
            article = generate_article(topic, temperature)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
    st.markdown(article)
    st.download_button("Download article (.md)", article, file_name="article.md")
else:
    st.info("Enter a topic in the sidebar and click **Generate article**.")
