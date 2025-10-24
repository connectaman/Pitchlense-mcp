"""
Social Coverage Risk MCP Tool for PitchLense MCP Package.

MCP tool wrapper for social coverage risk analysis.
"""

from typing import Dict, Any
from ..core.base import BaseMCPTool
from .social_coverage_risk import SocialCoverageRiskAnalyzer


class SocialCoverageRiskMCPTool(BaseMCPTool):
    """
    MCP tool for social coverage risk analysis.
    
    Analyzes social media coverage, complaints, reviews, and sentiment
    for startups, founders, and products.
    """
    
    def __init__(self):
        """Initialize the Social Coverage Risk MCP Tool."""
        super().__init__(
            tool_name="Social Coverage Risk Analysis",
            description="Analyze social media coverage, complaints, reviews, and sentiment risks for startups and founders"
        )
        self.analyzer = SocialCoverageRiskAnalyzer()
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for analysis."""
        self.analyzer.llm_client = llm_client
    
    def analyze_social_coverage_risks(self, startup_data: str) -> Dict[str, Any]:
        """
        Analyze social coverage risks for a startup.
        
        Args:
            startup_data: Comprehensive startup information including social media data
            
        Returns:
            Social coverage risk analysis results
        """
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Social coverage risk analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register the social coverage risk analysis tool."""
        self.register_tool(self.analyze_social_coverage_risks)
