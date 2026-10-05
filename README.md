# MCP-powered Multi-agent Deep Researcher (Linkup + CrewAI + Ollama)

A 100% local alternative to ChatGPT's *deep research*, usable from Cursor or Claude Desktop.

1. **Web Researcher** – runs deep web searches via [Linkup](https://linkup.so)
2. **Research Analyst** – verifies and deduplicates results (can delegate fact-checks back)
3. **Technical Writer** – writes a coherent report with citations

The crew is exposed as one MCP tool: `crew_research(query)`.

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or `MODEL=openai/gpt-4o-mini`)
- A Linkup API key
- Cursor or Claude Desktop

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

## Run
**Terminal test:**
```bash
python research_crew.py "What are the latest breakthroughs in solid-state batteries?"
```

**MCP Inspector (optional):** `mcp dev server.py`

**Cursor:** *File → Preferences → Cursor Settings → MCP → Add new global MCP server* (absolute paths):
```json
{
  "mcpServers": {
    "deep-researcher": {
      "command": "C:/path/to/07-deep-researcher-mcp/.venv/Scripts/python.exe",
      "args": ["C:/path/to/07-deep-researcher-mcp/server.py"]
    }
  }
}
```
Same JSON works in Claude Desktop's `claude_desktop_config.json`. Then ask:
*"Use crew_research to investigate the state of open-source LLMs in 2026."*

> Research with a local model takes a few minutes. Some MCP hosts time out long tool calls; if
> that happens, use `LINKUP_DEPTH=standard` and a faster model.
