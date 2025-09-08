"""
Perplexity search MCP tool.

This tool calls Perplexity's Chat Completions API with a user query and
returns a JSON containing the synthesized answer and a list of source URLs
(and titles when available).

Environment variables:
    PERPLEXITY_API_KEY: API key for Perplexity (required).
"""

import os
from typing import Any, Dict, List, Optional
import httpx

from ..core.base import BaseMCPTool


def _extract_sources(resp: Dict[str, Any]) -> List[Dict[str, Optional[str]]]:
    """Extract source attributions from a Perplexity response robustly."""
    sources: List[Dict[str, Optional[str]]] = []

    # Common location: choices[0].message.citations (array of urls)
    try:
        choices = resp.get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            # newer API sometimes includes 'citations' as list[str]
            citations = msg.get("citations") or []
            for url in citations:
                sources.append({"url": url, "title": None})

            # some responses include 'source_attributions'
            attributions = msg.get("source_attributions") or []
            for src in attributions:
                sources.append({
                    "url": src.get("url"),
                    "title": src.get("title"),
                })
    except Exception:
        pass

    # Fallback: top-level 'citations'
    try:
        top_citations = resp.get("citations") or []
        for url in top_citations:
            sources.append({"url": url, "title": None})
    except Exception:
        pass

    # Deduplicate by url
    seen = set()
    deduped: List[Dict[str, Optional[str]]] = []
    for s in sources:
        url = s.get("url")
        if url and url not in seen:
            seen.add(url)
            deduped.append(s)
    return deduped


class PerplexityMCPTool(BaseMCPTool):
    """MCP tool that queries Perplexity and returns answer with source URLs.

    Args:
        query: User query string to search on Perplexity.
        model: Perplexity model to use (default: "sonar").

    Returns:
        A dictionary with keys:
            - "query": original query string
            - "answer": synthesized answer (str or None)
            - "sources": list of {"url", "title"}
    """

    API_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(self):
        super().__init__(
            "Perplexity Search",
            "Query Perplexity and return answer with source URLs",
        )

    def _headers(self) -> Dict[str, str]:
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise RuntimeError("PERPLEXITY_API_KEY not set")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _payload(self, query: str, model: str = "sonar") -> Dict[str, Any]:
        # standard chat.completions style payload
        return {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "max_tokens": 800,
        }

    def search_perplexity(self, query: str, model: str = "sonar") -> Dict[str, Any]:
        """
        Query Perplexity for a given query.

        Args:
            query: user query string
            model: Perplexity model (default: sonar)

        Returns:
            dict with keys: query, answer, sources (list of {url, title})
        """
        if not isinstance(query, str) or not query.strip():
            return self.create_error_response("Invalid query: must be a non-empty string")

        try:
            headers = self._headers()
            payload = self._payload(query, model=model)
            with httpx.Client(timeout=90) as client:
                r = client.post(self.API_URL, headers=headers, json=payload)
                try:
                    r.raise_for_status()
                except httpx.HTTPStatusError as http_exc:
                    # Include response text to help diagnose 400 errors
                    raise httpx.HTTPError(f"{str(http_exc)} | response_body={r.text}")
                data = r.json()

            # Extract answer
            answer = None
            try:
                choices = data.get("choices") or []
                if choices:
                    answer = (choices[0].get("message") or {}).get("content")
            except Exception:
                answer = None

            sources = _extract_sources(data)
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
            }
        except httpx.HTTPError as e:
            return self.create_error_response(f"HTTP error: {str(e)}")
        except Exception as e:
            return self.create_error_response(f"Perplexity error: {str(e)}")

    def register_tools(self):
        self.register_tool(self.search_perplexity)


