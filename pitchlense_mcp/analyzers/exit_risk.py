"""
Exit Risk Analyzer for PitchLense MCP Package.

Analyzes exit risks including exit pathways, sector exit activity, and late-stage investor appeal.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import EXIT_RISK_PROMPT


class ExitRiskAnalyzer(BaseRiskAnalyzer):
    """Exit risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the exit risk analyzer."""
        super().__init__(llm_client, "Exit Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of exit risk indicators."""
        return [
            "Exit Pathways Risk",
            "Sector Exit Activity Risk",
            "Late-stage Appeal Risk",
            "Scalability for Exit Risk",
            "Market Timing Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for exit risks."""
        return EXIT_RISK_PROMPT


class ExitRiskMCPTool(BaseMCPTool):
    """MCP tool for exit risk analysis."""
    
    def __init__(self):
        """Initialize the exit risk MCP tool."""
        super().__init__("Exit Risk Analyzer", "Analyze exit risks for startups")
        self.analyzer = ExitRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_exit_risks(self, startup_data: str) -> dict:
        """
        Analyze exit risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with exit risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_exit_risks)