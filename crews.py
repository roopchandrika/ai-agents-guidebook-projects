import os

from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

from tools import ListRepoFilesTool, ReadRepoFileTool


def get_llm(temperature: float = 0.2) -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": temperature}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


# Pydantic schemas for robust structured output
class DocItem(BaseModel):
    title: str = Field(..., description="Title of the document, e.g. 'Getting Started'")
    description: str = Field(..., description="What the document should cover")
    prerequisites: str = Field("", description="What the reader needs to know or install first")
    examples: list[str] = Field(default_factory=list, description="Code examples or use cases to include")
    goal: str = Field(..., description="What the reader will be able to do after reading")


class DocPlan(BaseModel):
    overview: str = Field(..., description="One-paragraph overview of the project")
    docs: list[DocItem]


def build_planning_crew(repo_root: str) -> Crew:
    """Inputs: repo_url. Output: DocPlan."""
    llm = get_llm()
    code_explorer = Agent(
        role="Code Explorer",
        goal="Understand the codebase structure, key components, patterns and relationships",
        backstory="You are a senior engineer who quickly maps unfamiliar codebases.",
        tools=[ListRepoFilesTool(repo_root=repo_root), ReadRepoFileTool(repo_root=repo_root)],
        llm=llm,
        verbose=True,
    )
    analyze_task = Task(
        description=(
            "Analyze the repository cloned from {repo_url}. List its files, then read the README, "
            "dependency files and the most important source files. Identify the purpose, "
            "architecture, main modules, public APIs, configuration and how to run it."
        ),
        expected_output="A detailed technical analysis of the codebase.",
        agent=code_explorer,
    )
    doc_planner = Agent(
        role="Documentation Planner",
        goal="Plan clear, complete documentation for the project",
        backstory="You are a technical writer who designs documentation sets developers love.",
        llm=llm,
        verbose=True,
    )
    plan_task = Task(
        description=(
            "Based on the codebase analysis, plan the documentation for {repo_url}. "
            "Plan 3 to {max_docs} documents (e.g. overview, getting started, architecture, "
            "API/usage reference, configuration). Specify each document's title, description, "
            "prerequisites, examples and goal."
        ),
        expected_output="A documentation plan.",
        agent=doc_planner,
        context=[analyze_task],
        output_pydantic=DocPlan,
    )
    return Crew(agents=[code_explorer, doc_planner], tasks=[analyze_task, plan_task], process=Process.sequential)


def build_documentation_crew(repo_root: str) -> Crew:
    """Inputs: repo_url, overview, title, description, prerequisites, examples, goal."""
    llm = get_llm(0.3)
    tools = [ListRepoFilesTool(repo_root=repo_root), ReadRepoFileTool(repo_root=repo_root)]
    doc_writer = Agent(
        role="Documentation Writer",
        goal="Write accurate, practical documentation grounded in the actual code",
        backstory="You write clear docs and always check the source code before stating facts.",
        tools=tools,
        llm=llm,
        verbose=True,
    )
    write_task = Task(
        description=(
            "Write the document '{title}' for the project {repo_url}.\n"
            "Project overview: {overview}\n"
            "Description: {description}\nPrerequisites: {prerequisites}\n"
            "Examples to include: {examples}\nGoal: {goal}\n"
            "Read the relevant source files first. Use markdown with headings, code blocks and, "
            "where helpful, a mermaid diagram."
        ),
        expected_output="A complete markdown draft of the document.",
        agent=doc_writer,
    )
    doc_reviewer = Agent(
        role="Documentation Reviewer",
        goal="Make the documentation consistent, accurate and complete",
        backstory="You are a meticulous reviewer who checks docs against the code.",
        tools=tools,
        llm=llm,
        verbose=True,
    )
    review_task = Task(
        description=(
            "Review the draft of '{title}'. Verify claims against the code, fix inaccuracies, "
            "fill gaps and improve clarity. Return the final, polished document only."
        ),
        expected_output="The final markdown document (no commentary).",
        agent=doc_reviewer,
        context=[write_task],
    )
    return Crew(agents=[doc_writer, doc_reviewer], tasks=[write_task, review_task], process=Process.sequential)
