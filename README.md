# Multi-agent Brand Monitoring System (Bright Data + CrewAI Flows + Ollama)

Scrapes web mentions of a brand across X, Instagram, YouTube, LinkedIn and the open web, then
runs a **platform-specific crew** (Analysis agent + Writer agent) for each source in parallel and
merges everything into one report.

```
CrewAI Flow
  @start  scrape_search_results  -> Bright Data SERP API (one query per platform)
  @listen scrape_platforms       -> Bright Data platform scrapers (optional enrichment)
  @listen analyze_platforms      -> X crew | Instagram crew | YouTube crew | ... (parallel)
  @listen merge_reports          -> final markdown report
```

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or `MODEL=openai/gpt-4o-mini`)
- A [Bright Data](https://brightdata.com) account:
  1. Create a **SERP API** zone (Proxies & Scraping → Add → SERP API) and put its name in `BRIGHTDATA_SERP_ZONE`
  2. Copy your **API key** into `BRIGHTDATA_API_KEY`
  3. *(Optional)* For richer data, open the Web Scrapers library (X posts, Instagram posts, YouTube
     videos, LinkedIn posts — "collect by URL") and paste each scraper's dataset ID into `.env`

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # then fill in keys
```

## Run
```bash
streamlit run app.py
```
or from the terminal (writes `brand_report.md`):
```bash
python flow.py "Lightning AI"
```

## Files
| File | Purpose |
|---|---|
| `brightdata.py` | SERP API search and dataset (platform scraper) helpers |
| `crews.py` | Platform crew factory: Analyst agent + Writer agent |
| `flow.py` | CrewAI Flow orchestrating scrape → enrich → parallel crews → merge |
| `app.py` | Streamlit UI |
