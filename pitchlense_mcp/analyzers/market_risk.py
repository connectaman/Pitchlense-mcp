"""
Market Risk Analyzer for PitchLense MCP Package.

Analyzes market-related risks including TAM, growth rate, competition, and differentiation.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import MARKET_RISK_PROMPT


class MarketRiskAnalyzer(BaseRiskAnalyzer):
    """Market risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the market risk analyzer."""
        super().__init__(llm_client, "Market Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of market risk indicators."""
        return [
            "TAM Size Assessment",
            "Industry Growth Rate",
            "Market Competition",
            "Differentiation Analysis",
            "Market Niche Dependence"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for market risks."""
        return MARKET_RISK_PROMPT


class MarketRiskMCPTool(BaseMCPTool):
    """MCP tool for market risk analysis."""
    
    def __init__(self):
        """Initialize the market risk MCP tool."""
        super().__init__("Market Risk Analyzer", "Analyze market-related risks for startups")
        self.analyzer = MarketRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_market_risks(self, startup_data: str) -> dict:
        """
        Analyze market-related risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with market risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_market_risks)
