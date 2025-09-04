"""
Competitive Risk Analyzer for PitchLense MCP Package.

Analyzes competitive risks including incumbent strength, entry barriers, and defensibility.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import COMPETITIVE_RISK_PROMPT


class CompetitiveRiskAnalyzer(BaseRiskAnalyzer):
    """Competitive risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the competitive risk analyzer."""
        super().__init__(llm_client, "Competitive Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of competitive risk indicators."""
        return [
            "Incumbent Competition Risk",
            "Entry Barriers Risk",
            "Defensibility Risk",
            "Competitive Differentiation Risk",
            "Market Saturation Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for competitive risks."""
        return COMPETITIVE_RISK_PROMPT


class CompetitiveRiskMCPTool(BaseMCPTool):
    """MCP tool for competitive risk analysis."""
    
    def __init__(self):
        """Initialize the competitive risk MCP tool."""
        super().__init__("Competitive Risk Analyzer", "Analyze competitive risks for startups")
        self.analyzer = CompetitiveRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_competitive_risks(self, startup_data: str) -> dict:
        """
        Analyze competitive risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with competitive risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_competitive_risks)