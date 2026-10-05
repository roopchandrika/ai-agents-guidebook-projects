"""MCP server exposing the financial analyst crew to Cursor / Claude Desktop (stdio transport)."""
import contextlib
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
SCRIPT_PATH = OUTPUT_DIR / "stock_analysis.py"

load_dotenv(BASE_DIR / ".env")

from finance_crew import run_financial_analysis  # noqa: E402

mcp = FastMCP("financial-analyst")


@mcp.tool()
def analyze_stock(query: str) -> str:
    """Analyze stock market data for a natural-language query (e.g. "Plot YTD gains of TSLA vs AAPL").

    Runs a multi-agent crew that parses the query, writes Python visualization code
    and verifies it. Returns the generated Python code.
    """
    # stdout carries the MCP protocol, so send any crew logging to stderr
    with contextlib.redirect_stdout(sys.stderr):
        return run_financial_analysis(query, verbose=False)


@mcp.tool()
def save_code(code: str) -> str:
    """Save Python code to output/stock_analysis.py so it can be executed later."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    SCRIPT_PATH.write_text(code, encoding="utf-8")
    return f"Code saved to {SCRIPT_PATH}"


@mcp.tool()
def run_code_and_show_plot() -> str:
    """Run output/stock_analysis.py, save output/stock_plot.png and open it in the default image viewer."""
    if not SCRIPT_PATH.exists():
        return "No saved code found. Call analyze_stock and save_code first."
    proc = subprocess.run(
        [sys.executable, SCRIPT_PATH.name],
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "MPLBACKEND": "Agg"},  # render headless so plt.show() doesn't block
    )
    if proc.returncode != 0:
        return f"Script failed:\n{proc.stderr[-3000:]}"
    plot = OUTPUT_DIR / "stock_plot.png"
    if plot.exists():
        open_file(plot)
    return f"Plot saved to {plot}\n\nScript output:\n{proc.stdout[-3000:]}"


def open_file(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])


if __name__ == "__main__":
    mcp.run(transport="stdio")
