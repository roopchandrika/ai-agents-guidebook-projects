"""Documentation Flow: clone repo -> plan docs -> write + review each doc -> save to docs/<repo>/.

Usage: python flow.py https://github.com/owner/repo
"""
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from pydantic import BaseModel

from crews import DocItem, build_documentation_crew, build_planning_crew

load_dotenv()


class DocState(BaseModel):
    repo_url: str = ""
    repo_root: str = ""
    overview: str = ""
    plan: list[DocItem] = []
    saved_files: list[str] = []


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


class DocumentationFlow(Flow[DocState]):
    @start()
    def clone_repo(self):
        name = self.state.repo_url.rstrip("/").removesuffix(".git").split("/")[-1]
        target = Path("repos") / name
        if target.exists():
            # git marks object files read-only, which blocks deletion on Windows
            shutil.rmtree(target, onerror=lambda fn, p, _: (os.chmod(p, stat.S_IWRITE), fn(p)))
        target.parent.mkdir(exist_ok=True)
        print(f"📥 Cloning {self.state.repo_url}")
        subprocess.run(["git", "clone", "--depth", "1", self.state.repo_url, str(target)], check=True)
        self.state.repo_root = str(target.resolve())

    @listen(clone_repo)
    def plan_docs(self):
        print("🗺️  Planning documentation")
        result = build_planning_crew(self.state.repo_root).kickoff(
            inputs={"repo_url": self.state.repo_url, "max_docs": int(os.getenv("MAX_DOCS", "5"))}
        )
        self.state.overview = result.pydantic.overview
        self.state.plan = result.pydantic.docs

        out = self.output_dir()
        plan_md = "\n".join(f"- **{d.title}** — {d.description}" for d in self.state.plan)
        (out / "_plan.md").write_text(f"# Documentation plan\n\n{self.state.overview}\n\n{plan_md}\n", encoding="utf-8")

    @listen(plan_docs)
    def write_docs(self):
        out = self.output_dir()
        for i, doc in enumerate(self.state.plan, 1):
            print(f"✍️  [{i}/{len(self.state.plan)}] {doc.title}")
            result = build_documentation_crew(self.state.repo_root).kickoff(
                inputs={
                    "repo_url": self.state.repo_url,
                    "overview": self.state.overview,
                    "title": doc.title,
                    "description": doc.description,
                    "prerequisites": doc.prerequisites or "None",
                    "examples": "; ".join(doc.examples) or "Use your judgement",
                    "goal": doc.goal,
                }
            )
            text = re.sub(r"<think>.*?</think>", "", result.raw, flags=re.S).strip()
            text = re.sub(r"^```(?:markdown|md)?\s*\n(.*)\n```$", r"\1", text, flags=re.S)
            path = out / f"{i:02d}-{slugify(doc.title)}.md"
            path.write_text(text + "\n", encoding="utf-8")
            self.state.saved_files.append(str(path))
        print(f"📚 Saved {len(self.state.saved_files)} documents to {out}")

    def output_dir(self) -> Path:
        out = Path("docs") / Path(self.state.repo_root).name
        out.mkdir(parents=True, exist_ok=True)
        return out


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/pallets/itsdangerous"
    DocumentationFlow().kickoff(inputs={"repo_url": url})
