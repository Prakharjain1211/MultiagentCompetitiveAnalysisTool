"""
Web page scraper with politeness and anti-blocking measures.

Features:
    - Random User-Agent rotation from a configurable list.
    - robots.txt compliance checked per domain (cached).
    - Truncation of oversized pages at 50 KB.
    - Structured error responses (never throws on HTTP errors).

Usage:
    from src.tools.scraper import WebScraper
    scraper = WebScraper()
    result = scraper.scrape("https://example.com")
    if result["success"]:
        print(result["content"])
"""

import random
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import settings
from src.utils.text import clean_html, truncate

# Maximum page size to download (50 KB). Larger pages are truncated
# to avoid excessive memory use and LLM context costs.
MAX_PAGE_SIZE = 50_000


class WebScraper:
    """Downloads and cleans web page content with politeness features.

    Attributes:
        session: Reusable requests.Session for connection pooling.
        _robot_parsers: Cache of domain -> RobotFileParser instances.
    """

    def __init__(self):
        """Initialise the scraper with a reusable session and empty robots cache."""
        self.session = requests.Session()
        self._robot_parsers: dict[str, RobotFileParser] = {}

    def _get_user_agent(self) -> str:
        """Pick a random User-Agent from the configured list.

        Returns:
            A User-Agent string.
        """
        return random.choice(settings.user_agents)

    def _check_robots(self, url: str) -> bool:
        """Check robots.txt permission for the given URL.

        Parses and caches robots.txt per domain. If the file cannot be
        retrieved (e.g. timeout), defaults to allowing access.

        Args:
            url: The full URL to check.

        Returns:
            True if scraping is allowed, False if blocked by robots.txt.
        """
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # Lazy-load and cache the robot parser for this domain.
        if base not in self._robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
                self._robot_parsers[base] = rp
            except Exception:
                # Cannot read robots.txt — default to allowed.
                return True

        return self._robot_parsers[base].can_fetch(self._get_user_agent(), url)

    def scrape(self, url: str, timeout: int = 10) -> dict:
        """Scrape a URL and return cleaned text content.

        Checks robots.txt, rotates User-Agent, downloads up to 50 KB,
        cleans HTML, and returns a structured result dict.

        Args:
            url: The target URL to scrape.
            timeout: Request timeout in seconds.

        Returns:
            Dict with keys:
                url (str): The requested URL.
                content (str): Cleaned page text (empty on failure).
                success (bool): True if the page was scraped successfully.
                error (str): Error message on failure, empty string on success.
        """
        # Respect robots.txt — fail fast if blocked.
        if not self._check_robots(url):
            return {"url": url, "content": "", "success": False, "error": "Blocked by robots.txt"}

        try:
            # Send GET request with rotating User-Agent.
            headers = {"User-Agent": self._get_user_agent()}
            resp = self.session.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()

            # Truncate oversized responses before parsing.
            raw = resp.text[:MAX_PAGE_SIZE]
            cleaned = clean_html(raw)

            return {"url": url, "content": cleaned, "success": True, "error": ""}

        except requests.RequestException as e:
            # Structured error response — never throw.
            return {"url": url, "content": "", "success": False, "error": str(e)}