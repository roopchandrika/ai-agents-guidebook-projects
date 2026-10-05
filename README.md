# Multi-agent Hotel Finder (CrewAI + Browserbase + Ollama)

An agentic workflow that parses a travel query, fetches live hotel listings from Kayak, and
summarizes the best options.

1. **Hotel Search agent** – parses location/dates/guests, builds a Kayak hotel URL (custom Kayak
   tool) and opens it in a headless browser (Browserbase tool) to extract the top 5 hotels.
2. **Summarization agent** – produces a comparison table plus budget / best-rated / best-value picks.

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or use `MODEL=openai/gpt-4o-mini`)
- A [Browserbase](https://www.browserbase.com) API key and project ID

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
or
```bash
python main.py "Hotels in Tokyo from 2026-12-10 to 2026-12-14 for 2 adults near Shibuya"
```

## Notes
- If Kayak returns a bot-check page, simply retry.
- If a small local model struggles with tool calls, use a larger or hosted model via `MODEL`.
