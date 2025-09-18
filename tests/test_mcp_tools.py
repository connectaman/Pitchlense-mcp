"""
Tests for MCP tools and analyzers using mocks (Gemini, SerpAPI, Perplexity).
"""

import os
from unittest.mock import Mock, patch

import pytest

from pitchlense_mcp import (
    CustomerRiskMCPTool,
    FinancialRiskMCPTool,
    MarketRiskMCPTool,
    TeamRiskMCPTool,
    OperationalRiskMCPTool,
    CompetitiveRiskMCPTool,
    LegalRiskMCPTool,
    ExitRiskMCPTool,
    ProductRiskMCPTool,
    PeerBenchmarkMCPTool,
    SerpNewsMCPTool,
    PerplexityMCPTool,
)


# -----------------------------
# SerpAPI (Google News) tests
# -----------------------------


@patch.dict(os.environ, {"SERPAPI_API_KEY": "test_key"}, clear=True)
@patch("pitchlense_mcp.tools.serp_news.GoogleSearch")
def test_serp_news_success(mock_search):
    mock_instance = Mock()
    mock_instance.get_dict.return_value = {
        "news_results": [
            {
                "title": "Headline",
                "link": "https://news.google.com/article",
                "source": "Source",
                "date": "1 hour ago",
                "snippet": "Snippet",
                "thumbnail": "https://image/url.jpg",
            }
        ]
    }
    mock_search.return_value = mock_instance

    tool = SerpNewsMCPTool()
    res = tool.fetch_google_news("openai funding", num_results=5)

    assert res["query"] == "openai funding"
    assert isinstance(res.get("results"), list)
    assert res["results"][0]["link"].startswith("https://")


@patch.dict(os.environ, {}, clear=True)
def test_serp_news_missing_key():
    tool = SerpNewsMCPTool()
    res = tool.fetch_google_news("openai")
    assert "error" in res
    assert "SERPAPI_API_KEY" in res["error"]


# -----------------------------
# Perplexity tests
# -----------------------------


@patch.dict(os.environ, {"PERPLEXITY_API_KEY": "ppx_key"}, clear=True)
@patch("httpx.Client.post")
def test_perplexity_success(mock_post):
    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "Answer text",
                            "citations": [
                                "https://example.com/a",
                                "https://example.com/b",
                            ],
                        }
                    }
                ]
            }

    mock_post.return_value = Resp()

    tool = PerplexityMCPTool()
    out = tool.search_perplexity("What is RAG?")
    assert out["query"] == "What is RAG?"
    assert out["answer"] == "Answer text"
    assert {"url": "https://example.com/a", "title": None} in out["sources"]


@patch.dict(os.environ, {}, clear=True)
def test_perplexity_missing_key():
    tool = PerplexityMCPTool()
    res = tool.search_perplexity("Anything")
    assert "error" in res
    assert "PERPLEXITY_API_KEY" in res["error"]


# -----------------------------
# Analyzer MCP tools tests
# -----------------------------


@pytest.mark.parametrize(
    "tool_cls, method_name",
    [
        (CustomerRiskMCPTool, "analyze_customer_risks"),
        (FinancialRiskMCPTool, "analyze_financial_risks"),
        (MarketRiskMCPTool, "analyze_market_risks"),
        (TeamRiskMCPTool, "analyze_team_risks"),
        (OperationalRiskMCPTool, "analyze_operational_risks"),
        (CompetitiveRiskMCPTool, "analyze_competitive_risks"),
        (LegalRiskMCPTool, "analyze_legal_risks"),
        (ExitRiskMCPTool, "analyze_exit_risks"),
        (ProductRiskMCPTool, "analyze_product_risks"),
    ],
)
def test_analyzer_mcp_tools_return(tool_cls, method_name):
    tool = tool_cls()
    # Bypass LLM by stubbing analyze
    tool.analyzer.analyze = Mock(return_value={
        "category_name": getattr(tool.analyzer, "category_name", "Category"),
        "overall_risk_level": "medium",
        "category_score": 5,
        "indicators": [],
        "summary": "Stubbed"
    })

    fn = getattr(tool, method_name)
    out = fn("Some organized startup text")
    assert out.get("overall_risk_level") in {"low", "medium", "high", "critical", "unknown"}
    assert isinstance(out.get("category_score"), int)


def test_peer_benchmark_mcp_tool():
    tool = PeerBenchmarkMCPTool()
    # Mock the raw LLM response that would come from the prompt
    tool.analyzer.llm_client = Mock()
    tool.analyzer.llm_client.predict = Mock(return_value={
        "response": '''<JSON>
{
  "category_name": "Peer Benchmarking",
  "overall_benchmark_level": "medium",
  "benchmark_score": 6,
  "peer_benchmarks": {},
  "startup_metrics": {},
  "comparison_table": [],
  "summary": "OK"
}
</JSON>'''
    })
    res = tool.analyze_peer_benchmark("Startup info text")
    assert res["category_name"] == "Peer Benchmarking"
    assert "category_score" in res
    assert "overall_risk_level" in res
    assert "indicators" in res


