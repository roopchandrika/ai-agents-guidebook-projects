"""News generator: Senior Research Analyst (Serper web search) -> Content Writer."""
import os

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import SerperDevTool


def build_crew(temperature: float = 0.7) -> Crew:
    # Cohere's fast Command R7B. Reads COHERE_API_KEY from the environment.
    llm = LLM(model=os.getenv("MODEL", "cohere_chat/command-r7b-12-2024"), temperature=temperature)
    search_tool = SerperDevTool(n_results=10)  # reads SERPER_API_KEY

    senior_research_analyst = Agent(
        role="Senior Research Analyst",
        goal="Research, analyze and synthesize comprehensive, up-to-date information on {topic} from reliable sources",
        backstory=(
            "You're an expert research analyst with advanced web research skills. You excel at "
            "finding, analyzing and synthesizing information from across the internet, "
            "distinguishing reliable sources from unreliable ones, and fact-checking claims."
        ),
        tools=[search_tool],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
    research_task = Task(
        description=(
            "1. Search the web for the latest news and developments on {topic}.\n"
            "2. Evaluate source credibility and fact-check claims across multiple sources.\n"
            "3. Organize findings into a structured research brief.\n"
            "4. Include all relevant citations and source URLs."
        ),
        expected_output=(
            "A research report with an executive summary, key findings, verified facts and "
            "statistics, and a list of all sources with URLs."
        ),
        agent=senior_research_analyst,
    )

    content_writer = Agent(
        role="Content Writer",
        goal="Transform research findings into an engaging, publication-ready news article",
        backstory=(
            "You're a skilled journalist who turns complex information into clear, accurate "
            "and engaging articles while keeping every claim attributed to its source."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
    writing_task = Task(
        description=(
            "Using the research brief, write a news article on {topic}:\n"
            "- A compelling headline and an engaging introduction\n"
            "- Well-structured body sections with subheadings\n"
            "- Inline citations as [Source: URL] for key claims\n"
            "- A short conclusion and a References section listing all sources"
        ),
        expected_output="A polished, publication-ready news article in markdown with citations.",
        agent=content_writer,
        context=[research_task],
    )

    return Crew(
        agents=[senior_research_analyst, content_writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )


def generate_article(topic: str, temperature: float = 0.7) -> str:
    return build_crew(temperature).kickoff(inputs={"topic": topic}).raw


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    load_dotenv()
    print(generate_article(" ".join(sys.argv[1:]) or "Latest developments in AI agents"))
