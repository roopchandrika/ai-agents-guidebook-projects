import os
from typing import Optional, Type

from bs4 import BeautifulSoup
from browserbase import Browserbase
from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field


class KayakFlightInput(BaseModel):
    departure: str = Field(..., description="Departure airport IATA code, e.g. SFO")
    arrival: str = Field(..., description="Arrival airport IATA code, e.g. JFK")
    date: str = Field(..., description="Departure date in YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="Return date YYYY-MM-DD for round trips")


class KayakFlightTool(BaseTool):
    name: str = "kayak_flight_url_generator"
    description: str = (
        "Builds a Kayak flight search URL from airport codes and dates. "
        "Call this before browsing."
    )
    args_schema: Type[BaseModel] = KayakFlightInput

    def _run(self, departure: str, arrival: str, date: str, return_date: Optional[str] = None) -> str:
        url = f"https://www.kayak.com/flights/{departure.upper()}-{arrival.upper()}/{date}"
        if return_date:
            url += f"/{return_date}"
        return url + "?currency=USD&sort=bestflight_a"


class BrowserInput(BaseModel):
    url: str = Field(..., description="The URL to load")


class BrowserbaseTool(BaseTool):
    name: str = "browserbase_web_loader"
    description: str = (
        "Opens a URL in a real headless browser (Browserbase), waits for the page "
        "to render and returns its visible text."
    )
    args_schema: Type[BaseModel] = BrowserInput

    def _run(self, url: str) -> str:
        bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
        session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(10_000)  # Kayak streams results in after load
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "head"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text[:12_000] or "Page returned no text."
