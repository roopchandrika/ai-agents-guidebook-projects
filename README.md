# Multi-agent Content Creation System (Motia + Firecrawl + Ollama + Typefully)

Turn any URL into social media posts and draft them in Typefully.

```
POST /generate-content {url}
   │  (API step)
   ▼
ScrapeArticle ── Firecrawl → markdown
   │  emits generate-content
   ├──► TwitterAgent  ─┐   (run in parallel)
   └──► LinkedInAgent ─┤
                       ▼  emits schedule-content
               ScheduleTypefully → Typefully draft + output/*.md
```

In Motia every **step** has a `config` object (how Motia wires it: type, topics, schema) and a
`handler` function (the step's logic).

## Prerequisites
- Node.js 18+ (20 LTS recommended)
- [Ollama](https://ollama.com/download): `ollama pull deepseek-r1:7b` (or point `LLM_*` at OpenAI)
- A [Firecrawl](https://firecrawl.dev) API key
- *(Optional)* a [Typefully](https://typefully.com) API key

## Setup
```bash
npm install
copy .env.example .env        # macOS/Linux: cp .env.example .env -> fill in keys
```

## Run
```bash
npm run dev
```
Open the **Motia Workbench** at http://localhost:3000 to see the flow diagram, logs and traces.
Trigger the workflow (from the Workbench's API endpoint panel, or a terminal):
```bash
curl -X POST http://localhost:3000/generate-content -H "Content-Type: application/json" -d "{\"url\": \"https://blog.dailydoseofds.com/p/5-agentic-ai-design-patterns\"}"
```
Generated posts are written to `output/` and, if `TYPEFULLY_API_KEY` is set, drafted in Typefully.

### Troubleshooting `npm install` on Windows
Motia's dev server starts an embedded Redis (`redis-memory-server`), which on Windows downloads
and extracts a Memurai/Redis MSI during `npm install`. If that step fails:
- run the terminal as a normal user (not inside a restricted sandbox) and retry, or
- run this project inside **WSL** (Ubuntu): `wsl`, `cd` to the folder, then `npm install && npm run dev`.

> The project pins `motia@0.13.0`, the last 0.x release, whose step API (`config` + `handler`,
> `emits` / `subscribes`) matches the guidebook. Motia 1.x changed the API.
