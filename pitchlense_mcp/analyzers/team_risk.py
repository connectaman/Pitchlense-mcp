"""
Team Risk Analyzer for PitchLense MCP Package.

Analyzes team and founder-related risks including leadership depth, founder stability, skill gaps, and credibility.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import TEAM_RISK_PROMPT


class TeamRiskAnalyzer(BaseRiskAnalyzer):
    """Team risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the team risk analyzer."""
        super().__init__(llm_client, "Team & Founder Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of team risk indicators."""
        return [
            "Leadership Depth Risk",
            "Founder Stability Risk",
            "Skill Gaps Risk",
            "Credibility Issues Risk",
            "Incentive Alignment Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for team risks."""
        return TEAM_RISK_PROMPT


class TeamRiskMCPTool(BaseMCPTool):
    """MCP tool for team risk analysis."""
    
    def __init__(self):
        """Initialize the team risk MCP tool."""
        super().__init__("Team Risk Analyzer", "Analyze team and founder-related risks for startups")
        self.analyzer = TeamRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_team_risks(self, startup_data: str) -> dict:
        """
        Analyze team-related risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with team risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_team_risks)
