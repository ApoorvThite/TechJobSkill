import os
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class JobPostingRaw(BaseModel):
    job_id: str
    source: str
    title: Optional[str]
    company: Optional[str]
    location_raw: Optional[str]
    posted_raw: Optional[str]
    description_raw: Optional[str]
    salary_raw: Optional[str]
    job_type: Optional[str]
    url: str
    scraped_at: datetime


class BaseScraper:
    def __init__(self, name: str, base_delay_seconds: float = 1.0, snapshot_root: str = "data/raw", user_agent: Optional[str] = None, timeout_seconds: float = 15.0, max_retries: int = 3) -> None:
        self.name = name
        self.base_delay_seconds = base_delay_seconds
        self.snapshot_root = Path(snapshot_root)
        self.session = httpx.Client(timeout=timeout_seconds, headers={
            "User-Agent": user_agent or os.getenv("SCRAPER_USER_AGENT", "JobSkillTrendsBot/0.1 (+contact: local)"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        self.max_retries = max_retries
        self.log = logging.getLogger(f"scraper.{self.name}")

    def start_urls(self) -> List[str]:
        raise NotImplementedError

    def parse_listing(self, soup: BeautifulSoup) -> List[str]:
        raise NotImplementedError

    def parse_job(self, url: str, soup: BeautifulSoup) -> Optional[JobPostingRaw]:
        raise NotImplementedError

    def _rate_limit(self) -> None:
        jitter = random.uniform(0.2, 0.8)
        time.sleep(self.base_delay_seconds + jitter)

    def fetch_html(self, url: str) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, follow_redirects=True)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code in (429, 500, 502, 503, 504):
                    backoff = min(2 ** (attempt - 1), 8)
                    time.sleep(backoff)
                    continue
                return None
            except Exception:
                backoff = min(2 ** (attempt - 1), 8)
                time.sleep(backoff)
        return None

    def soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def save_snapshot(self, kind: str, name: str, content: str) -> None:
        day = datetime.utcnow().strftime("%Y%m%d")
        outdir = self.snapshot_root / self.name / day
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / f"{kind}_{name}.html"
        try:
            path.write_text(content, encoding="utf-8")
        except Exception:
            pass

    def scrape(self, max_listing_pages: int = 1, max_jobs: Optional[int] = None) -> Iterable[JobPostingRaw]:
        scraped = 0
        for i, list_url in enumerate(self.start_urls()[:max_listing_pages], start=1):
            self._rate_limit()
            html = self.fetch_html(list_url)
            if not html:
                continue
            if i <= 2:
                self.save_snapshot("listing", f"{i}", html)
            try:
                links = self.parse_listing(self.soup(html))
            except Exception:
                continue
            for j, job_url in enumerate(links, start=1):
                if max_jobs is not None and scraped >= max_jobs:
                    return
                self._rate_limit()
                job_html = self.fetch_html(job_url)
                if not job_html:
                    continue
                if j <= 3 and i == 1:
                    self.save_snapshot("job", str(j), job_html)
                try:
                    item = self.parse_job(job_url, self.soup(job_html))
                    if item:
                        scraped += 1
                        yield item
                except Exception:
                    continue
import os
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class JobPostingRaw(BaseModel):
    job_id: str
    source: str
    title: Optional[str]
    company: Optional[str]
    location_raw: Optional[str]
    posted_raw: Optional[str]
    description_raw: Optional[str]
    salary_raw: Optional[str]
    job_type: Optional[str]
    url: str
    scraped_at: datetime


class BaseScraper:
    """Base class for site scrapers with simple rate limiting, retries and snapshotting."""

    def __init__(
        self,
        name: str,
        base_delay_seconds: float = 1.0,
        snapshot_root: str = "data/raw",
        user_agent: Optional[str] = None,
        timeout_seconds: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        self.name = name
        self.base_delay_seconds = base_delay_seconds
        self.snapshot_root = Path(snapshot_root)
        self.session = httpx.Client(timeout=timeout_seconds, headers={
            "User-Agent": user_agent or os.getenv("SCRAPER_USER_AGENT", "JobSkillTrendsBot/0.1 (+contact: local)"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        self.max_retries = max_retries
        self.log = logging.getLogger(f"scraper.{self.name}")

    # ---- Hooks for subclasses ----
    def start_urls(self) -> List[str]:
        raise NotImplementedError

    def parse_listing(self, soup: BeautifulSoup) -> List[str]:
        """Return absolute URLs for job detail pages found on a listing page."""
        raise NotImplementedError

    def parse_job(self, url: str, soup: BeautifulSoup) -> Optional[JobPostingRaw]:
        raise NotImplementedError

    # ---- Utilities ----
    def _rate_limit(self) -> None:
        jitter = random.uniform(0.2, 0.8)
        time.sleep(self.base_delay_seconds + jitter)

    def fetch_html(self, url: str) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, follow_redirects=True)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code in (429, 500, 502, 503, 504):
                    backoff = min(2 ** (attempt - 1), 8)
                    self.log.warning("%s returned %s, retry in %ss", url, resp.status_code, backoff)
                    time.sleep(backoff)
                    continue
                self.log.warning("Unexpected status %s for %s", resp.status_code, url)
                return None
            except Exception as e:
                backoff = min(2 ** (attempt - 1), 8)
                self.log.exception("Error fetching %s (attempt %s/%s): %s", url, attempt, self.max_retries, e)
                time.sleep(backoff)
        return None

    def soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def save_snapshot(self, kind: str, name: str, content: str) -> None:
        day = datetime.utcnow().strftime("%Y%m%d")
        outdir = self.snapshot_root / self.name / day
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / f"{kind}_{name}.html"
        try:
            path.write_text(content, encoding="utf-8")
        except Exception:
            self.log.exception("Failed saving snapshot %s", path)

    # ---- Orchestration ----
    def scrape(self, max_listing_pages: int = 1, max_jobs: Optional[int] = None) -> Iterable[JobPostingRaw]:
        scraped = 0
        for i, list_url in enumerate(self.start_urls()[:max_listing_pages], start=1):
            self._rate_limit()
            html = self.fetch_html(list_url)
            if not html:
                self.log.warning("No HTML for listing %s", list_url)
                continue
            if i <= 2:
                self.save_snapshot("listing", f"{i}", html)
            links = []
            try:
                links = self.parse_listing(self.soup(html))
            except Exception:
                self.log.exception("Failed to parse listing %s", list_url)
                continue
            self.log.info("Found %d job links on %s", len(links), list_url)
            for j, job_url in enumerate(links, start=1):
                if max_jobs is not None and scraped >= max_jobs:
                    return
                self._rate_limit()
                job_html = self.fetch_html(job_url)
                if not job_html:
                    continue
                if j <= 3 and i == 1:
                    safe = str(j)
                    self.save_snapshot("job", safe, job_html)
                try:
                    item = self.parse_job(job_url, self.soup(job_html))
                    if item:
                        scraped += 1
                        yield item
                except Exception:
                    self.log.exception("Failed to parse job %s", job_url)
        self.log.info("Scraped %d jobs from %s", scraped, self.name)
