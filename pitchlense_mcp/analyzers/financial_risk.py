"""
Financial Risk Analyzer for PitchLense MCP Package.

Analyzes financial risks including metrics consistency, burn rate, projections, CAC/LTV ratio, and profitability path.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import FINANCIAL_RISK_PROMPT


class FinancialRiskAnalyzer(BaseRiskAnalyzer):
    """Financial risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the financial risk analyzer."""
        super().__init__(llm_client, "Financial Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of financial risk indicators."""
        return [
            "Metrics Consistency Risk",
            "Burn Rate & Runway Risk",
            "Projection Realism Risk",
            "CAC vs LTV Risk",
            "Profitability Path Risk",
            "Funding Dependence Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for financial risks."""
        return FINANCIAL_RISK_PROMPT


class FinancialRiskMCPTool(BaseMCPTool):
    """MCP tool for financial risk analysis."""
    
    def __init__(self):
        """Initialize the financial risk MCP tool."""
        super().__init__("Financial Risk Analyzer", "Analyze financial risks for startups")
        self.analyzer = FinancialRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_financial_risks(self, startup_data: str) -> dict:
        """
        Analyze financial risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with financial risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_financial_risks)
