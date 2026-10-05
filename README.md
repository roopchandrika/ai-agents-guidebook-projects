# AI Agent with Human-like Memory (Zep + Microsoft AutoGen + Ollama)

A memory-less agent treats every conversation as a blank slate. This agent:
1. Saves every conversation turn to **Zep Cloud**
2. Zep extracts **facts** about the user into a temporal knowledge graph
3. Before every LLM call, a custom AutoGen `Memory` (`ZepMemory`) injects those facts
4. The agent answers using both the current chat history and long-term memory — **across sessions**

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or any OpenAI-compatible API)
- A free [Zep Cloud](https://app.getzep.com) API key

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

## Run
```bash
streamlit run app.py
```
Try this to see memory working:
1. Click **Start new session** and say: *"Hi, I'm Alex. I'm vegetarian, I live in Berlin and I'm training for a marathon."*
2. Chat a bit more, then click **Start new session** again (fresh chat history).
3. Ask: *"Suggest a dinner for me tonight."* — it should remember you're a vegetarian runner in Berlin.
4. Click **Show what Zep remembers** to see the extracted facts.

## Visualize the knowledge graph
Open the [Zep dashboard](https://app.getzep.com) → **Users** → your user → **Graph** to explore how
facts evolve across sessions.

## Files
| File | Purpose |
|---|---|
| `memory_agent.py` | LLM client, Zep client, user/thread setup, `ZepMemory`, chat turn |
| `app.py` | Streamlit chat UI |
