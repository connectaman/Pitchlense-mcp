"""
SerpAPI Google News MCP tool.

This tool queries Google News via SerpAPI and returns a normalized list of
news results (first page) containing title, link, source, date, snippet, and
thumbnail when available.

Environment variables:
    SERPAPI_API_KEY: API key for SerpAPI (required).
"""

import os
from typing import Dict, Any, List
from ..core.base import BaseMCPTool

try:
    from serpapi import GoogleSearch
except Exception:  # pragma: no cover
    GoogleSearch = None


def _map_news_result(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": item.get("title"),
        "link": item.get("link"),
        "source": item.get("source"),
        "date": item.get("date"),
        "snippet": item.get("snippet"),
        "thumbnail": (item.get("thumbnail") or item.get("image")),
    }


class SerpNewsMCPTool(BaseMCPTool):
    """MCP tool to fetch Google News via SerpAPI for a query.

    Usage example:
        >>> from pitchlense_mcp import SerpNewsMCPTool
        >>> tool = SerpNewsMCPTool()
        >>> result = tool.fetch_google_news("OpenAI funding round", num_results=10)
        >>> print(result["results"][0]["link"])  # first news URL
    """

    def __init__(self):
        super().__init__(
            "SerpAPI Google News",
            "Fetch first-page Google News results (url, thumbnail, metadata) for a query",
        )

    def _get_client(self):
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise RuntimeError("SERPAPI_API_KEY not set")
        if GoogleSearch is None:
            raise RuntimeError("serpapi package not installed. Run: pip install google-search-results")
        return api_key

    def fetch_google_news(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Fetch Google News first page for a query.

        Args:
            query: Search query string.
            num_results: Maximum number of results to return (default: 10).

        Returns:
            A dictionary with keys:
                - "query": The original query string.
                - "results": List of news items, each containing:
                    {"title", "link", "source", "date", "snippet", "thumbnail"}.

        Error handling:
            Returns a standardized error dict via create_error_response on failures
            (e.g., missing API key, network error, or invalid input).
        """
        if not isinstance(query, str) or not query.strip():
            return self.create_error_response("Invalid query: must be a non-empty string")

        try:
            api_key = self._get_client()
            params = {
                "engine": "google_news",
                "q": query,
                "api_key": api_key,
                "hl": "en",
                "gl": "us",
            }
            search = GoogleSearch(params)
            results = search.get_dict() or {}
            news_items: List[Dict[str, Any]] = results.get("news_results") or []
            mapped = [_map_news_result(item) for item in news_items[: num_results or 10]]
            return {"query": query, "results": mapped}
        except Exception as e:
            return self.create_error_response(f"SerpAPI error: {str(e)}")

    def register_tools(self):
        self.register_tool(self.fetch_google_news)


