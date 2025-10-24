"""
Peer Benchmark Analyzer and MCP tool.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..prompts import PEER_BENCHMARK_PROMPT
from ..utils.json_extractor import extract_json_from_response


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
    
    def analyze(self, startup_data: str) -> Dict[str, Any]:
        """
        Perform peer benchmarking analysis for the given startup data.
        
        Args:
            startup_data: String containing comprehensive startup information
            
        Returns:
            Dictionary containing peer benchmarking analysis results
        """
        try:
            prompt = self.get_analysis_prompt()
            # Format the prompt with the startup data
            full_prompt = prompt.format(startup_data=startup_data)
            
            # Use the LLM client to generate analysis
            result = self.llm_client.predict(
                system_message="You are an expert venture analyst specializing in benchmarking startups against sector peers. Maintain professional language and avoid inappropriate content. Focus strictly on business and investment analysis.",
                user_message=full_prompt
            )
            
            # Parse the response using the JSON extractor
            response_text = result.get("response", "")
            analysis_result = extract_json_from_response(response_text)
            
            if analysis_result is not None:
                # Transform the peer benchmark result to match the expected structure
                return self._transform_to_standard_format(analysis_result)
            else:
                return self._create_fallback_response(response_text, "JSON extraction failed")
                
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _transform_to_standard_format(self, benchmark_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform peer benchmark result to match the standard risk analyzer format.
        
        Args:
            benchmark_result: Raw peer benchmark analysis result
            
        Returns:
            Transformed result in standard format
        """
        # Map benchmark_level to risk_level
        benchmark_level = benchmark_result.get("overall_benchmark_level", "unknown")
        risk_level_mapping = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "critical"
        }
        overall_risk_level = risk_level_mapping.get(benchmark_level, "unknown")
        
        # Get benchmark score and convert to category score
        benchmark_score = benchmark_result.get("benchmark_score", 5)
        category_score = benchmark_score
        
        # Create indicators from comparison table
        indicators = []
        comparison_table = benchmark_result.get("comparison_table", [])
        for comparison in comparison_table:
            metric = comparison.get("metric", "")
            startup_value = comparison.get("startup", "N/A")
            peer_median = comparison.get("peer_median", "N/A")
            status = comparison.get("status", "unknown")
            
            # Convert status to risk level
            status_risk_mapping = {
                "overvalued": "high",
                "undervalued": "low",
                "inline": "low"
            }
            risk_level = status_risk_mapping.get(status, "medium")
            
            # Calculate score based on status
            if status == "overvalued":
                score = 8
            elif status == "undervalued":
                score = 3
            else:  # inline
                score = 5
            
            indicators.append({
                "indicator": f"{metric} Benchmark",
                "risk_level": risk_level,
                "score": score,
                "description": f"Startup {metric}: {startup_value} vs Peer Median: {peer_median} ({status})",
                "recommendation": f"Focus on improving {metric} to align with peer benchmarks"
            })
        
        # If no comparison table, create default indicators
        if not indicators:
            indicators = [
                {
                    "indicator": "Peer Benchmarking Analysis",
                    "risk_level": overall_risk_level,
                    "score": category_score,
                    "description": benchmark_result.get("summary", "Peer benchmarking analysis completed"),
                    "recommendation": "Review peer benchmarks and adjust strategy accordingly"
                }
            ]
        
        return {
            "category_name": "Peer Benchmarking",
            "overall_risk_level": overall_risk_level,
            "category_score": category_score,
            "indicators": indicators,
            "summary": benchmark_result.get("summary", "Peer benchmarking analysis completed"),
            # Include original peer benchmark data for reference
            "peer_benchmark_data": {
                "peer_benchmarks": benchmark_result.get("peer_benchmarks", {}),
                "startup_metrics": benchmark_result.get("startup_metrics", {}),
                "comparison_table": comparison_table,
                "recommendations": benchmark_result.get("recommendations", [])
            }
        }


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


