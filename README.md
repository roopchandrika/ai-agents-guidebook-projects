# Agentic RAG (CrewAI + Firecrawl + LitServe)

A RAG pipeline with agentic capabilities: a **Retriever agent** decides whether to pull context
from a local **vector DB** (your documents) or from the **web** (Firecrawl), and a **Writer agent**
turns that into the final answer. The crew is deployed as an API with **LitServe**.

```
user query ─► LitServe /predict ─► Retriever Agent ──► knowledge_base_search (Qdrant + FastEmbed)
                                         │        └──► web_search (Firecrawl)
                                         ▼
                                   Writer Agent ─► JSON response
```

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download) with a model pulled: `ollama pull qwen3:8b`
  (or set `MODEL=openai/gpt-4o-mini` and `OPENAI_API_KEY` in `.env`)
- A [Firecrawl](https://firecrawl.dev) API key

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        # macOS/Linux: cp .env.example .env  -> then fill in keys
```

## Run
1. Put your `.txt`, `.md` or `.pdf` files in `data/` (a sample is included) and index them:
   ```bash
   python ingest.py
   ```
2. Start the server (port 8000):
   ```bash
   python server.py
   ```
3. In a second terminal, query it:
   ```bash
   python client.py "What is agentic RAG?"
   python client.py "What were the biggest AI announcements this week?"   # forces web search
   ```
   Or with curl: `curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"query\": \"What is RAG?\"}"`

> Qdrant runs in embedded mode and locks `qdrant_data/` while the server is running — stop the
> server before re-running `ingest.py`.

## Files
| File | Purpose |
|---|---|
| `server.py` | LitServe API: sets up the crew in `setup()`, then `decode_request → predict → encode_response` |
| `tools.py` | `knowledge_base_search` (vector DB) and `web_search` (Firecrawl) CrewAI tools |
| `vectordb.py` | Embedded Qdrant + FastEmbed helper |
| `ingest.py` | Chunks and indexes documents from `data/` |
| `client.py` | Minimal client calling the API |
| `llm.py` | LLM factory (Ollama by default, any LiteLLM model via `MODEL`) |
