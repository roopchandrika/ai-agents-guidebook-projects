# Multi-agent Book Writer (Firecrawl + CrewAI Flows + Ollama)

Writes a full book from a 3–5 word title.

```
BookFlow
  @start  generate_outline -> Outline Crew  (Research agent + Outline agent -> BookOutline pydantic)
  @listen write_chapters   -> N Writer Crews in parallel (Research agent + Writer agent)
  @listen save_book        -> books/<title>.md
```
Both crews use a Firecrawl SERP search tool to research before writing.

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or `MODEL=openai/gpt-4o-mini`)
- A [Firecrawl](https://firecrawl.dev) API key

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

## Run
```bash
python flow.py "Astronomy in 2025"
```
The book is saved to `books/astronomy_in_2025.md`. Control length with `NUM_CHAPTERS` and
`WORDS_PER_CHAPTER` in `.env` (local models often write shorter than asked).

> Running chapters in parallel against a single local Ollama instance is limited by your GPU/CPU;
> set `OLLAMA_NUM_PARALLEL=4` before `ollama serve` to let Ollama process requests concurrently.

## Hosting on Lightning AI (optional)
Create a Studio on [lightning.ai](https://lightning.ai), clone this repo, install Ollama inside
the Studio (`curl -fsSL https://ollama.com/install.sh | sh`), pull the model, and run the same commands.
