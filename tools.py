import os
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(..., description="The search query")


class FirecrawlSearchTool(BaseTool):
    name: str = "web_research"
    description: str = "Searches the web with Firecrawl's SERP API and returns page content as markdown."
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/search",
            headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"},
            json={"query": query, "limit": 3, "scrapeOptions": {"formats": ["markdown"]}},
            timeout=120,
        )
        resp.raise_for_status()
        results = resp.json().get("data", [])
        if not results:
            return "No results."
        return "\n\n".join(
            f"[{r.get('title', '')}]({r.get('url', '')})\n"
            f"{(r.get('markdown') or r.get('description') or '')[:3000]}"
            for r in results
        )
