"""CrewAI Flow: SERP scrape -> platform-specific scrapers -> platform crews (in parallel) -> merged report."""
import asyncio
import json
import os
import re

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from brightdata import scrape_dataset, serp_search
from crews import build_platform_crew

# platform -> (site filter for the SERP query, env var holding an optional Bright Data dataset id)
PLATFORMS = {
    "X": ("site:x.com OR site:twitter.com", "BRIGHTDATA_DATASET_X"),
    "Instagram": ("site:instagram.com", "BRIGHTDATA_DATASET_INSTAGRAM"),
    "YouTube": ("site:youtube.com", "BRIGHTDATA_DATASET_YOUTUBE"),
    "LinkedIn": ("site:linkedin.com", "BRIGHTDATA_DATASET_LINKEDIN"),
    "Web": ("-site:x.com -site:twitter.com -site:instagram.com -site:youtube.com -site:linkedin.com", None),
}


class BrandState(BaseModel):
    brand: str = ""
    raw: dict[str, list[dict]] = {}
    enriched: dict[str, str] = {}
    reports: dict[str, str] = {}
    final_report: str = ""


class BrandMonitoringFlow(Flow[BrandState]):
    @start()
    def scrape_search_results(self):
        """Step 1: find recent mentions on every platform via the SERP API."""
        for platform, (site_filter, _) in PLATFORMS.items():
            try:
                self.state.raw[platform] = serp_search(f'"{self.state.brand}" {site_filter}')
            except Exception as e:  # keep the flow going if one platform fails
                print(f"[{platform}] SERP search failed: {e}")
                self.state.raw[platform] = []

    @listen(scrape_search_results)
    def scrape_platforms(self):
        """Step 2: enrich links with Bright Data's platform-specific scrapers (when configured)."""
        for platform, results in self.state.raw.items():
            text = json.dumps(results, indent=1)
            dataset_env = PLATFORMS[platform][1]
            dataset_id = os.getenv(dataset_env) if dataset_env else None
            if dataset_id and results:
                try:
                    details = scrape_dataset(dataset_id, [r["link"] for r in results[:5]])
                    if details:
                        text = json.dumps(details, indent=1, default=str)
                except Exception as e:
                    print(f"[{platform}] dataset scrape failed, using SERP data: {e}")
            self.state.enriched[platform] = text[:12_000]

    @listen(scrape_platforms)
    async def analyze_platforms(self):
        """Step 3: run one crew per platform, all in parallel."""
        platforms = [p for p, r in self.state.raw.items() if r]
        results = await asyncio.gather(
            *[
                build_platform_crew(p).kickoff_async(
                    inputs={"brand": self.state.brand, "platform": p, "data": self.state.enriched[p]}
                )
                for p in platforms
            ]
        )
        for p, r in zip(platforms, results):
            self.state.reports[p] = re.sub(r"<think>.*?</think>", "", r.raw, flags=re.S).strip()

    @listen(analyze_platforms)
    def merge_reports(self):
        """Step 4: merge all platform insights into the final report."""
        sections = [f"## {p}\n\n{text}" for p, text in self.state.reports.items()]
        self.state.final_report = f"# Brand report: {self.state.brand}\n\n" + "\n\n---\n\n".join(sections)
        return self.state.final_report


def run(brand: str) -> str:
    flow = BrandMonitoringFlow()
    flow.kickoff(inputs={"brand": brand})
    return flow.state.final_report


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    load_dotenv()
    report = run(" ".join(sys.argv[1:]) or "Lightning AI")
    with open("brand_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
