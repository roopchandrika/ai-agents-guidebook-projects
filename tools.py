import os
from typing import Type

from bs4 import BeautifulSoup
from browserbase import Browserbase
from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field


class KayakHotelInput(BaseModel):
    location: str = Field(..., description="City (and optionally country/state), e.g. 'Paris, France'")
    check_in: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    adults: int = Field(2, description="Number of adult guests")
    rooms: int = Field(1, description="Number of rooms")


class KayakHotelTool(BaseTool):
    name: str = "kayak_hotel_url_generator"
    description: str = (
        "Builds a Kayak hotel search URL from a location, dates and guest count. "
        "Call this before browsing."
    )
    args_schema: Type[BaseModel] = KayakHotelInput

    def _run(self, location: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1) -> str:
        loc = ",".join(part.strip().replace(" ", "-") for part in location.split(","))
        url = f"https://www.kayak.com/hotels/{loc}/{check_in}/{check_out}/{adults}adults"
        if rooms > 1:
            url += f"/{rooms}rooms"
        return url + "?currency=USD&sort=rank_a"


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
