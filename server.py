"""MCP server exposing the deep research crew to Cursor / Claude Desktop (stdio transport)."""
import contextlib
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parent / ".env")

from research_crew import run_research  # noqa: E402

mcp = FastMCP("deep-researcher")


@mcp.tool()
def crew_research(query: str) -> str:
    """Run deep web research on a topic with a team of agents (searcher, analyst, writer).

    Returns a markdown report with inline citations and a list of sources.
    """
    # stdout carries the MCP protocol, so send any crew logging to stderr
    with contextlib.redirect_stdout(sys.stderr):
        return run_research(query, verbose=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
