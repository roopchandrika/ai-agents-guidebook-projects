# MCP-powered Financial Analyst (CrewAI + Ollama + Cursor / Claude Desktop)

Ask your IDE *"Plot YTD stock gains of Tesla and Apple"* and a crew of agents fetches, analyzes
and visualizes the data:

1. **Query Parser agent** – extracts tickers / timeframe / action as a Pydantic object
2. **Code Writer agent** – writes pandas + matplotlib + yfinance code
3. **Code Executor agent** – runs the code (separate Python process, 120 s timeout) and fixes errors

The crew is wrapped in an **MCP server** with 3 tools:
`analyze_stock`, `save_code`, `run_code_and_show_plot`.

## Prerequisites
- Python 3.10 – 3.13
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or `MODEL=openai/gpt-4o-mini`)
- [Cursor](https://cursor.com) or [Claude Desktop](https://claude.ai/download) as the MCP host

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

## Run
**1. Test the crew from the terminal:**
```bash
python finance_crew.py "Plot YTD stock gains of Tesla and Apple"
python output/stock_analysis.py
```

**2. Test the MCP server with the MCP Inspector (optional):**
```bash
mcp dev server.py
```

**3. Connect to Cursor:** *File → Preferences → Cursor Settings → MCP → Add new global MCP server*,
then add (use your **absolute** paths):
```json
{
  "mcpServers": {
    "financial-analyst": {
      "command": "C:/path/to/04-financial-analyst-mcp/.venv/Scripts/python.exe",
      "args": ["C:/path/to/04-financial-analyst-mcp/server.py"]
    }
  }
}
```
On macOS/Linux the command is `/path/to/.venv/bin/python`.
For **Claude Desktop**, put the same block in *Settings → Developer → Edit Config*
(`claude_desktop_config.json`) and restart the app.

Then ask in the chat: *"Use the financial analyst to plot TSLA vs AAPL over the last 6 months,
save the code and show the plot."*

> **Note:** the generated code runs on your own machine (same as the guidebook's
> `run_code_and_show_plot` step). Current CrewAI versions removed the built-in Docker code
> interpreter, so this project ships a small `PythonExecutorTool` instead.

## Files
| File | Purpose |
|---|---|
| `finance_crew.py` | LLM, Pydantic schema, code-executor tool, 3 agents/tasks, crew |
| `server.py` | FastMCP server with the 3 tools |
| `output/` | Generated script + `stock_plot.png` (git-ignored) |
