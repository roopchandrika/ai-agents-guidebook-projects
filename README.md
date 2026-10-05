# Multi-agent News Generator (CrewAI + Cohere Command R7B + Serper)

Takes a topic, searches the web, and turns it into a well-crafted news article with citations.

- **Senior Research Analyst** – searches the web with the Serper tool and consolidates the results
- **Content Writer** – turns the research into a polished, publication-ready article

## Prerequisites
- Python 3.10 – 3.13
- A [Cohere](https://dashboard.cohere.com/api-keys) API key and a [Serper](https://serper.dev) API key

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # then fill in both keys
```

## Run
```bash
streamlit run app.py
```
or
```bash
python news_crew.py "Latest developments in quantum computing"
```
