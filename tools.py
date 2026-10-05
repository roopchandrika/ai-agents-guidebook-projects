"""Repo exploration tools, sandboxed to the cloned repository."""
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".idea", ".vscode"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".lock", ".woff", ".woff2", ".ttf", ".mp4", ".pyc"}


class ListFilesInput(BaseModel):
    subdirectory: str = Field("", description="Path relative to the repo root ('' for the root)")


class ListRepoFilesTool(BaseTool):
    name: str = "list_repo_files"
    description: str = "Lists files in the repository (recursively) with their sizes."
    args_schema: Type[BaseModel] = ListFilesInput
    repo_root: str

    def _run(self, subdirectory: str = "") -> str:
        root = Path(self.repo_root).resolve()
        base = (root / subdirectory).resolve()
        if not base.is_relative_to(root) or not base.exists():
            return f"Invalid path: {subdirectory}"
        lines = []
        for p in sorted(base.rglob("*")):
            if any(part in IGNORED_DIRS for part in p.relative_to(root).parts) or not p.is_file():
                continue
            lines.append(f"{p.relative_to(root).as_posix()} ({p.stat().st_size} bytes)")
            if len(lines) >= 300:
                lines.append("... (truncated)")
                break
        return "\n".join(lines) or "No files."


class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="File path relative to the repo root")


class ReadRepoFileTool(BaseTool):
    name: str = "read_repo_file"
    description: str = "Reads a text file from the repository (truncated to 8000 characters)."
    args_schema: Type[BaseModel] = ReadFileInput
    repo_root: str

    def _run(self, file_path: str) -> str:
        root = Path(self.repo_root).resolve()
        path = (root / file_path).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            return f"File not found: {file_path}"
        if path.suffix.lower() in BINARY_EXT:
            return "Binary file, skipped."
        return path.read_text(encoding="utf-8", errors="ignore")[:8000]
