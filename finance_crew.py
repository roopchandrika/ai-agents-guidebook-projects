"""Financial analyst crew: Query Parser -> Code Writer -> Code Executor."""
import os
import re
import subprocess
import sys
import tempfile
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def get_llm() -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": 0.1}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


class QueryAnalysisOutput(BaseModel):
    """Structured output of the query parser agent."""

    symbols: list[str] = Field(..., description="Stock ticker symbols, e.g. ['TSLA', 'AAPL']")
    timeframe: str = Field(..., description="yfinance period, e.g. '1mo', '6mo', '1y', 'ytd'")
    action: str = Field(..., description="What to do, e.g. 'plot closing price', 'compare returns'")


class CodeInput(BaseModel):
    code: str = Field(..., description="The complete Python script to run")


class PythonExecutorTool(BaseTool):
    """Runs a script in a separate Python process (temp dir, timeout, headless matplotlib).

    Note: this executes LLM-generated code on your machine, like the guidebook's run step does.
    """

    name: str = "python_code_executor"
    description: str = (
        "Executes a complete Python script and returns its stdout/stderr. "
        "pandas, matplotlib and yfinance are installed."
    )
    args_schema: Type[BaseModel] = CodeInput

    def _run(self, code: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            script = os.path.join(tmp, "script.py")
            with open(script, "w", encoding="utf-8") as f:
                f.write(extract_code(code))
            try:
                proc = subprocess.run(
                    [sys.executable, script],
                    cwd=tmp,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env={**os.environ, "MPLBACKEND": "Agg"},
                )
            except subprocess.TimeoutExpired:
                return "Execution timed out after 120 seconds."
        status = "SUCCESS" if proc.returncode == 0 else f"FAILED (exit code {proc.returncode})"
        return f"{status}\nSTDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}"


def build_crew(verbose: bool = True) -> Crew:
    llm = get_llm()

    query_parser_agent = Agent(
        role="Stock Data Analyst",
        goal="Extract stock details and the requested analysis from the user query: {query}",
        backstory="You are a financial analyst who turns vague requests into precise data specs.",
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )
    query_parsing_task = Task(
        description="Analyze the user query and extract stock details: {query}",
        expected_output="Ticker symbols, a yfinance period string and the requested action.",
        output_pydantic=QueryAnalysisOutput,
        agent=query_parser_agent,
    )

    code_writer_agent = Agent(
        role="Senior Python Developer",
        goal="Write clean Python code that visualizes stock market data",
        backstory="You are an expert in pandas, matplotlib and the yfinance library.",
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )
    code_writer_task = Task(
        description=(
            "Write a complete, standalone Python script based on the parsed query.\n"
            "Requirements:\n"
            "- Use yfinance (yf.download or yf.Ticker(...).history) with the given period.\n"
            "- Use pandas and matplotlib; add a title, axis labels, legend and grid.\n"
            "- Save the figure with plt.savefig('stock_plot.png', dpi=150, bbox_inches='tight') "
            "and then call plt.show().\n"
            "- Print a short text summary (start/end price, % change) for each symbol.\n"
            "Return ONLY the code in a single ```python block."
        ),
        expected_output="A single python code block.",
        agent=code_writer_agent,
        context=[query_parsing_task],
    )

    code_execution_agent = Agent(
        role="Senior Code Reviewer and Executor",
        goal="Review and run the generated code, fixing any errors",
        backstory="You make sure generated scripts actually run and produce the expected plot.",
        tools=[PythonExecutorTool()],
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )
    code_execution_task = Task(
        description=(
            "Review the script. Run it with the python_code_executor tool. "
            "If it fails, fix it and run again. "
            "Return the final working script ONLY, in a single ```python block."
        ),
        expected_output="The final, working python code block.",
        agent=code_execution_agent,
        context=[code_writer_task],
    )

    return Crew(
        agents=[query_parser_agent, code_writer_agent, code_execution_agent],
        tasks=[query_parsing_task, code_writer_task, code_execution_task],
        process=Process.sequential,
        verbose=verbose,
    )


def extract_code(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, flags=re.S)
    return (blocks[-1] if blocks else text).strip()


def run_financial_analysis(query: str, verbose: bool = True) -> str:
    result = build_crew(verbose=verbose).kickoff(inputs={"query": query})
    return extract_code(result.raw)


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    load_dotenv()
    q = " ".join(sys.argv[1:]) or "Plot YTD stock gains of Tesla and Apple"
    code = run_financial_analysis(q)
    os.makedirs("output", exist_ok=True)
    with open("output/stock_analysis.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("\n=== Generated code saved to output/stock_analysis.py ===\n")
    print(code)
