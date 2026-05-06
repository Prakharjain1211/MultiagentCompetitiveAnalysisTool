"""
Web search tool with automatic fallback between providers.

Primary search uses DuckDuckGo (free, no API key required).
If DuckDuckGo fails, falls back to Tavily (requires TAVILY_API_KEY).
Both providers return results in a normalized format.

Usage:
    from src.tools.web_search import WebSearchTool
    searcher = WebSearchTool()
    results = searcher.search("NVIDIA competitors 2025", max_results=5)
"""

from typing import Any

from ddgs import DDGS
from tavily import TavilyClient

from config.settings import settings


class WebSearchTool:
    """Aggregated web search with DuckDuckGo primary and Tavily fallback.

    Normalises result dicts from both providers to a common schema:
        {"title": str, "url": str, "snippet": str}
    """

    def __init__(self):
        """Initialise the search tool.

        The Tavily client is only created if TAVILY_API_KEY is set in
        the environment; otherwise fallback is skipped gracefully.
        """
        self.tavily_client = (
            TavilyClient(api_key=settings.tavily_api_key)
            if settings.tavily_api_key
            else None
        )

    def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Execute a web search query against available providers.

        Attempts DuckDuckGo first. On any exception, falls back to Tavily
        if configured. Results are deduplicated and normalised.

        Args:
            query: The search query string.
            max_results: Maximum number of search results to return.

        Returns:
            List of result dicts with keys: title, url, snippet.

        Raises:
            RuntimeError: If DuckDuckGo fails and Tavily is unavailable
                          or also fails.
        """
        # Primary provider: DuckDuckGo (no API key needed).
        try:
            results = list(DDGS().text(query, max_results=max_results))
            return [
                {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in results
            ]
        except Exception:
            # DuckDuckGo failed — try Tavily fallback if configured.
            if self.tavily_client:
                try:
                    response = self.tavily_client.search(query, max_results=max_results)
                    return [
                        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
                        for r in response.get("results", [])
                    ]
                except Exception as e:
                    raise RuntimeError(f"Both DDG and Tavily search failed: {e}") from e
            # No fallback available — surface the error clearly.
            raise RuntimeError("DDG search failed and no Tavily API key configured")
