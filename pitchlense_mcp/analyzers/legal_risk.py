"""
Legal Risk Analyzer for PitchLense MCP Package.

Analyzes legal and regulatory risks including regulatory environment, compliance issues, and legal disputes.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import LEGAL_RISK_PROMPT


class LegalRiskAnalyzer(BaseRiskAnalyzer):
    """Legal risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the legal risk analyzer."""
        super().__init__(llm_client, "Legal & Regulatory Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of legal risk indicators."""
        return [
            "Regulatory Environment Risk",
            "Compliance Risk",
            "Legal Disputes Risk",
            "IP Protection Risk",
            "Regulatory Changes Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for legal risks."""
        return LEGAL_RISK_PROMPT


class LegalRiskMCPTool(BaseMCPTool):
    """MCP tool for legal risk analysis."""
    
    def __init__(self):
        """Initialize the legal risk MCP tool."""
        super().__init__("Legal Risk Analyzer", "Analyze legal and regulatory risks for startups")
        self.analyzer = LegalRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_legal_risks(self, startup_data: str) -> dict:
        """
        Analyze legal risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with legal risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_legal_risks)