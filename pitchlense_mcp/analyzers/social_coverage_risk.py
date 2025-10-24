"""
Social Coverage Risk Analyzer for PitchLense MCP Package.

Analyzes social media coverage, complaints, reviews, and sentiment for startups,
founders, and products to identify potential reputation and social media risks.
"""

from typing import Dict, Any, List
from ..core.base import BaseRiskAnalyzer
from ..prompts import SOCIAL_COVERAGE_RISK_PROMPT


class SocialCoverageRiskAnalyzer(BaseRiskAnalyzer):
    """
    Analyzer for social media coverage and reputation risks.
    
    Evaluates social media presence, sentiment, complaints, reviews,
    and overall social coverage for startups and founders.
    """
    
    def __init__(self):
        """Initialize the Social Coverage Risk Analyzer."""
        super().__init__()
        self.risk_category = "Social Coverage Risk"
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for social coverage risks."""
        return SOCIAL_COVERAGE_RISK_PROMPT
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of risk indicators for social coverage risks."""
        return [
            "Negative Social Media Sentiment",
            "High Complaint Volume",
            "Poor Review Ratings",
            "Founder Reputation Issues",
            "Product Review Problems",
            "Social Media Crisis",
            "Low Social Engagement",
            "Negative Press Coverage",
            "Customer Service Issues",
            "Brand Reputation Damage"
        ]
