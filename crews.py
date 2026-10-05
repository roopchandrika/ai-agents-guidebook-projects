import os

from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

from tools import FirecrawlSearchTool


def get_llm(temperature: float = 0.5) -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": temperature}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


class ChapterOutline(BaseModel):
    title: str = Field(..., description="Chapter title")
    description: str = Field(..., description="2-3 sentences on what the chapter covers")


class BookOutline(BaseModel):
    chapters: list[ChapterOutline]


class Chapter(BaseModel):
    title: str
    content: str = Field(..., description="Full chapter text in markdown")


def build_outline_crew() -> Crew:
    """Inputs: title, num_chapters. Output: BookOutline (pydantic)."""
    llm = get_llm(0.3)
    researcher = Agent(
        role="Book Researcher",
        goal="Research the topic '{title}' thoroughly to inform a book outline",
        backstory="You are a seasoned non-fiction researcher who finds the latest, most relevant material.",
        tools=[FirecrawlSearchTool()],
        llm=llm,
        verbose=True,
    )
    research_task = Task(
        description="Research '{title}'. Find key concepts, recent developments and interesting angles.",
        expected_output="Research notes with the main themes, facts and sources.",
        agent=researcher,
    )
    outliner = Agent(
        role="Book Outliner",
        goal="Create a logical, engaging chapter outline for the book '{title}'",
        backstory="You are an experienced editor who structures books so each chapter builds on the last.",
        llm=llm,
        verbose=True,
    )
    outline_task = Task(
        description=(
            "Using the research, create an outline for the book '{title}' with exactly "
            "{num_chapters} chapters. Each chapter needs a title and a short description."
        ),
        expected_output="The list of chapters with titles and descriptions.",
        agent=outliner,
        context=[research_task],
        output_pydantic=BookOutline,
    )
    return Crew(agents=[researcher, outliner], tasks=[research_task, outline_task], process=Process.sequential)


def build_writer_crew() -> Crew:
    """Inputs: title, chapter_title, chapter_description, outline, words. Output: Chapter (pydantic)."""
    llm = get_llm(0.6)
    researcher = Agent(
        role="Chapter Researcher",
        goal="Gather detailed material for the chapter '{chapter_title}' of '{title}'",
        backstory="You dig up specific facts, examples and stories that make a chapter come alive.",
        tools=[FirecrawlSearchTool()],
        llm=llm,
        verbose=True,
    )
    research_task = Task(
        description=(
            "Research material for the chapter '{chapter_title}' ({chapter_description}) "
            "of the book '{title}'."
        ),
        expected_output="Detailed research notes for the chapter.",
        agent=researcher,
    )
    writer = Agent(
        role="Chapter Writer",
        goal="Write an engaging, well-structured chapter '{chapter_title}' for the book '{title}'",
        backstory="You are an award-winning non-fiction author with a clear, vivid style.",
        llm=llm,
        verbose=True,
    )
    write_task = Task(
        description=(
            "Write the chapter '{chapter_title}' for the book '{title}'.\n"
            "Chapter brief: {chapter_description}\n"
            "Full book outline (for context, do not repeat other chapters):\n{outline}\n"
            "Aim for about {words} words, use markdown subheadings, and do not include the "
            "chapter title as a heading."
        ),
        expected_output="The chapter title and full chapter content in markdown.",
        agent=writer,
        context=[research_task],
        output_pydantic=Chapter,
    )
    return Crew(agents=[researcher, writer], tasks=[research_task, write_task], process=Process.sequential)
