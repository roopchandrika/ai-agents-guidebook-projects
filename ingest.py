"""Index every .txt / .md / .pdf file in ./data into the local vector DB.

Usage: python ingest.py [folder]
"""
import sys
from pathlib import Path

from pypdf import PdfReader

import vectordb

CHUNK_SIZE = 800
OVERLAP = 100


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk(text: str) -> list[str]:
    text = " ".join(text.split())
    step = CHUNK_SIZE - OVERLAP
    return [text[i : i + CHUNK_SIZE] for i in range(0, max(len(text), 1), step) if text[i:].strip()]


def main(folder: str = "data") -> None:
    files = [p for p in Path(folder).rglob("*") if p.suffix.lower() in {".txt", ".md", ".pdf"}]
    if not files:
        sys.exit(f"No .txt/.md/.pdf files found in {folder}/")
    chunks = [{"text": c, "source": f.name} for f in files for c in chunk(read_file(f))]
    n = vectordb.index_chunks(chunks)
    print(f"Indexed {n} chunks from {len(files)} file(s) into {vectordb.QDRANT_PATH}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
