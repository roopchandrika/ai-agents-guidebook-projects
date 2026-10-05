"""One crew per platform, each with an Analysis agent and a Writer agent."""
import os

from crewai import LLM, Agent, Crew, Process, Task


def get_llm() -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": 0.3}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


def build_platform_crew(platform: str) -> Crew:
    """Inputs at kickoff: brand, platform, data."""
    llm = get_llm()

    analyst = Agent(
        role=f"{platform} Brand Analyst",
        goal=f"Analyze how {{brand}} is being discussed on {platform}",
        backstory=(
            f"You are a social listening expert specialised in {platform}. You read raw "
            "mentions and identify sentiment, recurring themes, influential sources and risks."
        ),
        llm=llm,
        verbose=True,
    )
    analysis_task = Task(
        description=(
            "Here are recent {platform} mentions of the brand '{brand}':\n\n{data}\n\n"
            "Analyze them: overall sentiment (positive/neutral/negative with rough %), "
            "top themes, notable posts/sources (with links), and any risks or opportunities."
        ),
        expected_output="Structured analysis notes with links to the most important mentions.",
        agent=analyst,
    )

    writer = Agent(
        role=f"{platform} Insights Writer",
        goal=f"Write a concise, actionable {platform} brand report for {{brand}}",
        backstory="You turn social listening analysis into crisp reports for marketing leaders.",
        llm=llm,
        verbose=True,
    )
    writing_task = Task(
        description=(
            "Write the {platform} section of the brand report for '{brand}' using the analysis. "
            "Use markdown with: Summary, Sentiment, Key Themes, Notable Mentions (linked), "
            "Recommendations."
        ),
        expected_output="A markdown report section.",
        agent=writer,
        context=[analysis_task],
    )

    return Crew(agents=[analyst, writer], tasks=[analysis_task, writing_task], process=Process.sequential)
