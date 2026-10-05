"""Bright Data helpers: SERP API search + optional platform-specific dataset scrapers."""
import os
import time
from urllib.parse import quote_plus

import requests

API = "https://api.brightdata.com"


def _headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['BRIGHTDATA_API_KEY']}", "Content-Type": "application/json"}


def serp_search(query: str, num: int = 10) -> list[dict]:
    """Google search through Bright Data's SERP API. Returns [{title, link, description}]."""
    google_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num}&brd_json=1"
    resp = requests.post(
        f"{API}/request",
        headers=_headers(),
        json={"zone": os.environ["BRIGHTDATA_SERP_ZONE"], "url": google_url, "format": "raw"},
        timeout=90,
    )
    resp.raise_for_status()
    data = resp.json()  # brd_json=1 makes Bright Data return parsed JSON instead of HTML
    return [
        {"title": r.get("title", ""), "link": r.get("link", ""), "description": r.get("description", "")}
        for r in data.get("organic", [])
    ]


def scrape_dataset(dataset_id: str, urls: list[str], timeout_s: int = 300) -> list[dict]:
    """Run a Bright Data Web Scraper API dataset (e.g. X posts, YouTube videos) on a list of URLs."""
    if not urls:
        return []
    trigger = requests.post(
        f"{API}/datasets/v3/trigger",
        params={"dataset_id": dataset_id, "include_errors": "true"},
        headers=_headers(),
        json=[{"url": u} for u in urls],
        timeout=60,
    )
    trigger.raise_for_status()
    snapshot_id = trigger.json()["snapshot_id"]

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        progress = requests.get(f"{API}/datasets/v3/progress/{snapshot_id}", headers=_headers(), timeout=30)
        status = progress.json().get("status")
        if status == "ready":
            break
        if status == "failed":
            return []
        time.sleep(10)
    else:
        return []

    snap = requests.get(
        f"{API}/datasets/v3/snapshot/{snapshot_id}", params={"format": "json"}, headers=_headers(), timeout=60
    )
    snap.raise_for_status()
    return snap.json()
