# Real-time Voice RAG Agent (LiveKit + AssemblyAI + Cartesia + LlamaIndex)

Talk to your documents. The agent:
1. Listens to real-time audio (Silero VAD detects when you speak)
2. Transcribes it with **AssemblyAI**
3. Answers using your documents via a **LlamaIndex** RAG tool
4. Speaks the answer back with **Cartesia**

Everything is orchestrated by **LiveKit Agents**.

## Prerequisites
- Python 3.10 – 3.13 and a microphone/speakers
- API keys: AssemblyAI, Cartesia, OpenAI (LLM + embeddings)
- For browser/phone mode only: a free [LiveKit Cloud](https://cloud.livekit.io) project

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # then fill in keys
python agent.py download-files
```

## Run
**Option A — terminal mode (simplest, no LiveKit server):**
```bash
python agent.py console
```
Speak into your mic and ask e.g. *"What is the return policy?"* or *"How long does the battery last?"*

**Option B — browser via LiveKit Cloud:**
```bash
python agent.py dev
```
Then open the [LiveKit Agents Playground](https://agents-playground.livekit.io), connect to your
project, and start talking.

## Use your own documents
Put files in `data/`, delete the `storage/` folder, and restart — the index is rebuilt on start.

## Files
| File | Purpose |
|---|---|
| `agent.py` | Env/logging setup, RAG index, VAD prewarm, voice agent + entry point |
| `data/` | Knowledge base documents |
| `storage/` | Persisted LlamaIndex index (auto-created, git-ignored) |
