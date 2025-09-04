"""
Operational Risk Analyzer for PitchLense MCP Package.

Analyzes operational risks including supply chain, go-to-market strategy, operational efficiency, and execution history.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import OPERATIONAL_RISK_PROMPT


class OperationalRiskAnalyzer(BaseRiskAnalyzer):
    """Operational risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the operational risk analyzer."""
        super().__init__(llm_client, "Operational Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of operational risk indicators."""
        return [
            "Supply Chain Risk",
            "Go-to-Market Strategy Risk",
            "Operational Efficiency Risk",
            "Execution History Risk",
            "Process Maturity Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for operational risks."""
        return OPERATIONAL_RISK_PROMPT


class OperationalRiskMCPTool(BaseMCPTool):
    """MCP tool for operational risk analysis."""
    
    def __init__(self):
        """Initialize the operational risk MCP tool."""
        super().__init__("Operational Risk Analyzer", "Analyze operational risks for startups")
        self.analyzer = OperationalRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_operational_risks(self, startup_data: str) -> dict:
        """
        Analyze operational risks for a startup.
        
        Args:
            startup_data: String containing comprehensive startup information including
                         company details, business model, financial data, market info,
                         team details, news articles, pitch deck content, and web research
        
        Returns:
            JSON response with operational risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format - must be a non-empty string")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_operational_risks)