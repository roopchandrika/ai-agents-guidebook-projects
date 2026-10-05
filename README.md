# Multi-agent Flight Finder (CrewAI + Browserbase + Ollama)

Type a natural-language request like *"SF to New York on 21st November"* and two agents:
1. **Flight Search agent** – parses the request, builds a Kayak URL (custom Kayak tool) and opens it
   in a real headless browser (Browserbase tool) to extract the top 5 flights.
2. **Summarization agent** – turns the raw results into a comparison table with recommendations.

The crew runs with `planning=True` (the *Planning* agentic design pattern).

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or use `MODEL=openai/gpt-4o-mini`)
- A [Browserbase](https://www.browserbase.com) API key and project ID (free tier available)

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # then fill in keys
```
(Playwright only connects to Browserbase's remote browser, so `playwright install` is not required.)

## Run
Streamlit chat UI:
```bash
streamlit run app.py
```
Or from the command line:
```bash
python main.py "Flights from SFO to JFK on 21 November returning 28 November"
```

## Notes
- Kayak sometimes shows bot checks; Browserbase usually gets through, but if results are empty, retry.
- Small local models can struggle with multi-step tool use. If the agent loops, try a larger model
  (e.g. `ollama/qwen3:14b`) or a hosted one (`openai/gpt-4o-mini`).
