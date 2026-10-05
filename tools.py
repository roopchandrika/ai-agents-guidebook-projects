import os
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

import vectordb


class QueryInput(BaseModel):
    query: str = Field(..., description="The search query")


class VectorDBSearchTool(BaseTool):
    name: str = "knowledge_base_search"
    description: str = (
        "Searches the private knowledge base built from the user's documents. "
        "Always try this first. Returns the most relevant passages with their source."
    )
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:
        hits = vectordb.search(query, k=4)
        if not hits:
            return "No relevant passages found in the knowledge base."
        return "\n\n".join(
            f"[source: {h['source']} | score: {h['score']}]\n{h['text']}" for h in hits
        )


class FirecrawlSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Searches the internet with Firecrawl. Use this when the knowledge base "
        "does not contain the answer or the question needs fresh information."
    )
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/search",
            headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"},
            json={"query": query, "limit": 4, "scrapeOptions": {"formats": ["markdown"]}},
            timeout=90,
        )
        resp.raise_for_status()
        results = resp.json().get("data", [])
        if not results:
            return "No web results."
        return "\n\n".join(
            f"[{r.get('title', '')}]({r.get('url', '')})\n"
            f"{(r.get('markdown') or r.get('description') or '')[:2500]}"
            for r in results
        )
