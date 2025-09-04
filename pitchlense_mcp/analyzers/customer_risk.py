"""
Customer Risk Analyzer for PitchLense MCP Package.

Analyzes customer and traction-related risks including traction levels, churn rate, retention, and customer concentration.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import CUSTOMER_RISK_PROMPT


class CustomerRiskAnalyzer(BaseRiskAnalyzer):
    """Customer risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the customer risk analyzer."""
        super().__init__(llm_client, "Customer & Traction Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of customer risk indicators."""
        return [
            "Traction Level Risk",
            "Churn Rate Risk",
            "Retention/Engagement Risk",
            "Customer Quality Risk",
            "Customer Concentration Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for customer risks."""
        return CUSTOMER_RISK_PROMPT


class CustomerRiskMCPTool(BaseMCPTool):
    """MCP tool for customer risk analysis."""
    
    def __init__(self):
        """Initialize the customer risk MCP tool."""
        super().__init__("Customer Risk Analyzer", "Analyze customer and traction risks for startups")
        self.analyzer = CustomerRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_customer_risks(self, startup_data: str) -> dict:
        """
        Analyze customer-related risks for a startup.
        
        Args:
            startup_data: String containing comprehensive startup information including
                         company details, business model, financial data, market info,
                         team details, news articles, pitch deck content, and web research
        
        Returns:
            JSON response with customer risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format - must be a non-empty string")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_customer_risks)