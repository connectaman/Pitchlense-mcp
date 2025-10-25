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
        self.analyzer = SocialCoverageRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for analysis."""
        try:
            self.analyzer.llm_client = llm_client
            print(f"[SocialCoverage] LLM client set successfully on analyzer")
        except Exception as e:
            print(f"[SocialCoverage] Error setting LLM client: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def analyze_social_coverage_risks(self, startup_data: str) -> Dict[str, Any]:
        """
        Analyze social coverage risks for a startup.
        
        Args:
            startup_data: Comprehensive startup information including social media data
            
        Returns:
            Social coverage risk analysis results
        """
        try:
            print(f"[SocialCoverage] Starting analysis, analyzer LLM client is None: {self.analyzer.llm_client is None}")
            if not self.analyzer.llm_client:
                print("[SocialCoverage] Analyzer LLM client is None, returning error response")
                return self.create_error_response("LLM client not configured for social coverage risk analysis")
            print("[SocialCoverage] Analyzer LLM client is available, proceeding with analysis")
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            print(f"[SocialCoverage] Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_error_response(f"Social coverage risk analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register the social coverage risk analysis tool."""
        self.register_tool(self.analyze_social_coverage_risks)
