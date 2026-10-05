"""Deep researcher crew: Web Searcher -> Research Analyst -> Technical Writer."""
import os
import re
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from linkup import LinkupClient
from pydantic import BaseModel, Field


def get_llm() -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": 0.2}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


class LinkupSearchInput(BaseModel):
    query: str = Field(..., description="The search query")


class LinkupSearchTool(BaseTool):
    name: str = "linkup_web_search"
    description: str = "Deep web search via Linkup. Returns up-to-date results with source URLs."
    args_schema: Type[BaseModel] = LinkupSearchInput

    def _run(self, query: str) -> str:
        client = LinkupClient(api_key=os.environ["LINKUP_API_KEY"])
        response = client.search(
            query=query,
            depth=os.getenv("LINKUP_DEPTH", "standard"),  # "standard" or "deep"
            output_type="searchResults",
        )
        results = getattr(response, "results", []) or []
        if not results:
            return "No results."
        return "\n\n".join(
            f"[{getattr(r, 'name', '')}]({getattr(r, 'url', '')})\n{(getattr(r, 'content', '') or '')[:1500]}"
            for r in results[:8]
        )


def build_crew(verbose: bool = True) -> Crew:
    llm = get_llm()

    web_searcher = Agent(
        role="Web Researcher",
        goal="Find the most relevant, up-to-date information on: {query}",
        backstory="You are an expert at crafting search queries and finding authoritative sources.",
        tools=[LinkupSearchTool()],
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )
    search_task = Task(
        description=(
            "Research the topic: {query}. Run several focused searches covering different angles. "
            "Collect facts, figures and quotes together with their source URLs."
        ),
        expected_output="Raw research findings, each with its source URL.",
        agent=web_searcher,
    )

    analyst = Agent(
        role="Research Analyst",
        goal="Verify, deduplicate and structure the research findings",
        backstory=(
            "You are a rigorous analyst. You cross-check claims, remove duplicates and "
            "contradictions, and can ask the Web Researcher to fact-check anything doubtful."
        ),
        llm=llm,
        verbose=verbose,
        allow_delegation=True,  # can delegate verification back to the web searcher
    )
    analysis_task = Task(
        description=(
            "Analyze the raw findings for '{query}'. Verify key claims, remove duplicates, "
            "and organize everything into structured insights. Keep every source URL."
        ),
        expected_output="Structured, verified insights grouped by theme, each with source URLs.",
        agent=analyst,
        context=[search_task],
    )

    writer = Agent(
        role="Technical Writer",
        goal="Write a clear, well-cited research report on: {query}",
        backstory="You write precise, readable technical reports with proper citations.",
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )
    writing_task = Task(
        description=(
            "Write the final research report on '{query}' using the verified insights. "
            "Use markdown: an executive summary, sections per theme, and a numbered "
            "'Sources' list. Cite sources inline like [1], [2]."
        ),
        expected_output="A markdown research report with inline citations and a Sources list.",
        agent=writer,
        context=[analysis_task],
    )

    return Crew(
        agents=[web_searcher, analyst, writer],
        tasks=[search_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=verbose,
    )


def run_research(query: str, verbose: bool = True) -> str:
    result = build_crew(verbose=verbose).kickoff(inputs={"query": query})
    return re.sub(r"<think>.*?</think>", "", result.raw, flags=re.S).strip()


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    load_dotenv()
    print(run_research(" ".join(sys.argv[1:]) or "What are the latest breakthroughs in solid-state batteries?"))
