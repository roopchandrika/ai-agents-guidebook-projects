# AI Agents Guidebook - 12 Projects

Implementations of the 12 projects

**Each project lives on its own branch** of this repository. Every branch is self-contained, with
its own `README.md`, `requirements.txt` (or `package.json`), `.env.example` and `.gitignore`.
This `main` branch is the index.

| # | Project | Branch | Stack | Needs API keys |
|---|---|---|---|---|
| 01 | Agentic RAG | [`01-agentic-rag`](../../tree/01-agentic-rag) | CrewAI, Firecrawl, Qdrant, LitServe | Firecrawl |
| 02 | Voice RAG Agent | [`02-voice-rag-agent`](../../tree/02-voice-rag-agent) | LiveKit, AssemblyAI, Cartesia, LlamaIndex | AssemblyAI, Cartesia, OpenAI (+LiveKit for web) |
| 03 | Flight Finder | [`03-flight-finder`](../../tree/03-flight-finder) | CrewAI, Browserbase, Kayak, Streamlit | Browserbase |
| 04 | Financial Analyst (MCP) | [`04-financial-analyst-mcp`](../../tree/04-financial-analyst-mcp) | CrewAI, MCP, yfinance, Cursor | none |
| 05 | Brand Monitoring | [`05-brand-monitoring`](../../tree/05-brand-monitoring) | Bright Data, CrewAI Flows, Streamlit | Bright Data |
| 06 | Hotel Finder | [`06-hotel-finder`](../../tree/06-hotel-finder) | CrewAI, Browserbase, Kayak, Streamlit | Browserbase |
| 07 | Deep Researcher (MCP) | [`07-deep-researcher-mcp`](../../tree/07-deep-researcher-mcp) | Linkup, CrewAI, MCP | Linkup |
| 08 | Agent Memory | [`08-agent-memory-zep`](../../tree/08-agent-memory-zep) | Zep, Microsoft AutoGen, Streamlit | Zep |
| 09 | Book Writer | [`09-book-writer`](../../tree/09-book-writer) | Firecrawl, CrewAI Flows | Firecrawl |
| 10 | Content Creation | [`10-content-creation-motia`](../../tree/10-content-creation-motia) | Motia (TypeScript), Firecrawl, Typefully | Firecrawl (+Typefully optional) |
| 11 | Documentation Writer | [`11-documentation-writer`](../../tree/11-documentation-writer) | CrewAI Flows | none |
| 12 | News Generator | [`12-news-generator`](../../tree/12-news-generator) | CrewAI, Cohere, Serper, Streamlit | Cohere, Serper |

## Get one project
```bash
git clone -b 01-agentic-rag --single-branch https://github.com/roopchandrika/ai-agents-guidebook-projects.git agentic-rag
cd agentic-rag
```
Or, in an existing clone: `git switch 01-agentic-rag`.

## One-time setup
1. **Python 3.10 – 3.13** (CrewAI does not support 3.14 yet) and **git**
2. **Ollama** for local LLMs — https://ollama.com/download, then:
   ```bash
   ollama pull qwen3:8b
   ollama pull deepseek-r1:7b
   ```
   No GPU, or want faster/better results? Set `MODEL=openai/gpt-4o-mini` and `OPENAI_API_KEY`
   in a project's `.env`. Any [LiteLLM model string](https://docs.litellm.ai/docs/providers) works.
3. **Node.js 20 LTS** (only for project 10)

## Running any Python project
On the project's branch:
```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env  -> fill in keys
```
Then follow the **Run** section of that branch's README. `.env` files are git-ignored, so API keys
are never committed.
