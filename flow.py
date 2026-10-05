"""Book writing Flow: Outline crew -> N writer crews in parallel -> save markdown book.

Usage: python flow.py "Astronomy in 2025"
"""
import asyncio
import os
import re
import sys
from pathlib import Path

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from pydantic import BaseModel

from crews import BookOutline, Chapter, ChapterOutline, build_outline_crew, build_writer_crew

load_dotenv()


class BookState(BaseModel):
    title: str = "Astronomy in 2025"
    num_chapters: int = int(os.getenv("NUM_CHAPTERS", "5"))
    words_per_chapter: int = int(os.getenv("WORDS_PER_CHAPTER", "1500"))
    outline: list[ChapterOutline] = []
    chapters: list[Chapter] = []
    output_path: str = ""


class BookFlow(Flow[BookState]):
    @start()
    def generate_outline(self):
        print(f"📝 Creating outline for '{self.state.title}'")
        result = build_outline_crew().kickoff(
            inputs={"title": self.state.title, "num_chapters": self.state.num_chapters}
        )
        outline: BookOutline = result.pydantic
        self.state.outline = outline.chapters
        for i, ch in enumerate(self.state.outline, 1):
            print(f"  {i}. {ch.title}")

    @listen(generate_outline)
    async def write_chapters(self):
        print(f"✍️  Writing {len(self.state.outline)} chapters in parallel...")
        outline_text = "\n".join(f"- {c.title}: {c.description}" for c in self.state.outline)
        crews = [
            build_writer_crew().kickoff_async(
                inputs={
                    "title": self.state.title,
                    "chapter_title": ch.title,
                    "chapter_description": ch.description,
                    "outline": outline_text,
                    "words": self.state.words_per_chapter,
                }
            )
            for ch in self.state.outline
        ]
        results = await asyncio.gather(*crews)
        # keep the outline's order and titles
        self.state.chapters = [
            Chapter(title=ch.title, content=r.pydantic.content if r.pydantic else r.raw)
            for ch, r in zip(self.state.outline, results)
        ]

    @listen(write_chapters)
    def save_book(self):
        parts = [f"# {self.state.title}\n", "## Table of contents\n"]
        parts += [f"{i}. {c.title}" for i, c in enumerate(self.state.chapters, 1)]
        for i, c in enumerate(self.state.chapters, 1):
            content = re.sub(r"<think>.*?</think>", "", c.content, flags=re.S).strip()
            parts.append(f"\n\n## Chapter {i}: {c.title}\n\n{content}")
        book = "\n".join(parts)

        out_dir = Path("books")
        out_dir.mkdir(exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "_", self.state.title.lower()).strip("_")
        path = out_dir / f"{slug}.md"
        path.write_text(book, encoding="utf-8")
        self.state.output_path = str(path)
        print(f"📚 Book saved to {path} (~{len(book.split())} words)")
        return str(path)


if __name__ == "__main__":
    title = " ".join(sys.argv[1:]) or "Astronomy in 2025"
    BookFlow().kickoff(inputs={"title": title})
