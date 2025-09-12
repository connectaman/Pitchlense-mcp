"""
SerpAPI PDF Document Search MCP tool.

This tool queries Google Search via SerpAPI to find PDF documents related to a company
and returns a normalized list of PDF links with metadata.

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


def _map_pdf_result(item: Dict[str, Any]) -> Dict[str, Any]:
    """Map SerpAPI result to normalized PDF document format."""
    return {
        "title": item.get("title"),
        "link": item.get("link"),
        "snippet": item.get("snippet"),
        "displayed_link": item.get("displayed_link"),
        "file_format": "PDF",
    }


class SerpPdfSearchMCPTool(BaseMCPTool):
    """MCP tool to search for PDF documents via SerpAPI.

    Usage example:
        >>> from pitchlense_mcp import SerpPdfSearchMCPTool
        >>> tool = SerpPdfSearchMCPTool()
        >>> result = tool.search_pdf_documents("OpenAI filetype:pdf", num_results=10)
        >>> print(result["results"][0]["link"])  # first PDF URL
    """

    def __init__(self):
        super().__init__(
            "SerpAPI PDF Search",
            "Search for PDF documents related to a company using Google Search via SerpAPI",
        )

    def _get_client(self):
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise RuntimeError("SERPAPI_API_KEY not set")
        if GoogleSearch is None:
            raise RuntimeError("serpapi package not installed. Run: pip install google-search-results")
        return api_key

    def search_pdf_documents(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Search for PDF documents using Google Search via SerpAPI.

        Args:
            query: Search query string (should include "filetype:pdf").
            num_results: Maximum number of results to return (default: 10).

        Returns:
            A dictionary with keys:
                - "query": The original query string.
                - "results": List of PDF documents, each containing:
                    {"title", "link", "snippet", "displayed_link", "file_format"}.

        Error handling:
            Returns a standardized error dict via create_error_response on failures
            (e.g., missing API key, network error, or invalid input).
        """
        if not isinstance(query, str) or not query.strip():
            return self.create_error_response("Invalid query: must be a non-empty string")

        try:
            api_key = self._get_client()
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "hl": "en",
                "gl": "us",
                "num": num_results or 10,
            }
            search = GoogleSearch(params)
            results = search.get_dict() or {}
            organic_results: List[Dict[str, Any]] = results.get("organic_results") or []
            
            # Filter for PDF results and map to normalized format
            pdf_results = []
            for item in organic_results:
                link = item.get("link", "")
                if link.lower().endswith(".pdf") or "filetype:pdf" in query.lower():
                    pdf_results.append(_map_pdf_result(item))
            
            return {"query": query, "results": pdf_results}
        except Exception as e:
            return self.create_error_response(f"SerpAPI PDF search error: {str(e)}")

    def register_tools(self):
        self.register_tool(self.search_pdf_documents)
