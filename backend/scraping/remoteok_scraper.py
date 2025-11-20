from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, JobPostingRaw

REMOTEOK_BASE = "https://remoteok.com"


class RemoteOKScraper(BaseScraper):
    def __init__(self, start_paths: Optional[List[str]] = None, **kwargs):
        super().__init__(name="remoteok", **kwargs)
        self._start_paths = start_paths or [
            "/remote-dev-jobs",
            "/remote-data-jobs",
            "/remote-machine-learning-jobs",
        ]

    def start_urls(self) -> List[str]:
        return [urljoin(REMOTEOK_BASE, p) for p in self._start_paths]

    def parse_listing(self, soup: BeautifulSoup) -> List[str]:
        links: List[str] = []
        for a in soup.select("a[href]"):
            href = a.get("href") or ""
            if href.startswith("/remote-jobs/") or href.startswith(f"{REMOTEOK_BASE}/remote-jobs/"):
                abs_url = urljoin(REMOTEOK_BASE, href)
                if abs_url not in links:
                    links.append(abs_url)
        return links

    def parse_job(self, url: str, soup: BeautifulSoup) -> Optional[JobPostingRaw]:
        def first_text(selectors: List[str]) -> Optional[str]:
            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    txt = el.get_text(" ", strip=True)
                    if txt:
                        return txt
            return None

        title = first_text(["h1", ".company h1", ".company h2", "h2", "h3"])
        company = first_text([".company", "a.companyLink", ".companyLink h3", "[data-company]", "span.company"])
        location = first_text([".location", "span.location", "div.location", "[data-location]"])
        description = first_text(["#job-description", ".description", "article", "section#job"])

        if not description:
            longest = ""
            for c in soup.find_all(["article", "section", "div"], recursive=True):
                txt = c.get_text(" ", strip=True)
                if len(txt) > len(longest):
                    longest = txt
            description = longest or None

        salary = None
        job_type = None

        job_id = urlparse(url).path.rsplit("/", 1)[-1] or url
        return JobPostingRaw(
            job_id=job_id,
            source="remoteok",
            title=title,
            company=company,
            location_raw=location,
            posted_raw=None,
            description_raw=description,
            salary_raw=salary,
            job_type=job_type,
            url=url,
            scraped_at=datetime.utcnow(),
        )
