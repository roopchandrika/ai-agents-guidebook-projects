# Documentation Writer Flow (CrewAI Flows + Ollama)

Generates full project documentation from just a GitHub repo URL.

```
DocumentationFlow
  @start  clone_repo  -> git clone --depth 1 into repos/
  @listen plan_docs   -> Planning crew: Code Explorer + Doc Planner -> DocPlan (pydantic)
  @listen write_docs  -> Documentation crew per doc: Doc Writer + Doc Reviewer
                       -> docs/<repo>/NN-<title>.md
```

## Prerequisites
- Python 3.10 – 3.13 and **git** on your PATH
- [Ollama](https://ollama.com/download): `ollama pull qwen3:8b` (or `MODEL=openai/gpt-4o-mini`)

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

## Run
```bash
python flow.py https://github.com/pallets/itsdangerous
```
Output goes to `docs/itsdangerous/` (a `_plan.md` plus one markdown file per document).
Start with a small repository — local models have limited context.

## Files
| File | Purpose |
|---|---|
| `crews.py` | LLM, Pydantic schemas (`DocItem`, `DocPlan`), planning crew, documentation crew |
| `tools.py` | `list_repo_files` / `read_repo_file` tools restricted to the cloned repo |
| `flow.py` | The CrewAI Flow |
