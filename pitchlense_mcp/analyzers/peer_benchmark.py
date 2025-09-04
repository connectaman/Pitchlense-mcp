"""
Peer Benchmark Analyzer and MCP tool.
"""

from typing import List
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..prompts import PEER_BENCHMARK_PROMPT


class PeerBenchmarkAnalyzer(BaseRiskAnalyzer):
    """Analyzer for peer benchmarking."""

    def __init__(self, llm_client):
        super().__init__(llm_client, "Peer Benchmarking")
        self.risk_indicators = self.get_risk_indicators()

    def get_risk_indicators(self) -> List[str]:
        return [
            "EV/Revenue Multiple",
            "Gross Margin",
            "CAC/LTV",
            "Burn Multiple",
            "Headcount Growth QoQ",
            "Revenue Growth MoM",
        ]

    def get_analysis_prompt(self) -> str:
        return PEER_BENCHMARK_PROMPT


class PeerBenchmarkMCPTool(BaseMCPTool):
    """MCP tool for peer benchmarking analysis."""

    def __init__(self):
        super().__init__(
            "Peer Benchmark Analyzer",
            "Benchmark the startup against sector peers using key metrics",
        )
        self.analyzer = PeerBenchmarkAnalyzer(None)

    def set_llm_client(self, llm_client):
        self.analyzer.llm_client = llm_client

    def analyze_peer_benchmark(self, startup_data: str) -> dict:
        """Run peer benchmarking analysis."""
        if not self.validate_startup_data(startup_data):
            return self.create_error_response(
                "Invalid startup data format - must be a non-empty string"
            )
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")

    def register_tools(self):
        self.register_tool(self.analyze_peer_benchmark)


