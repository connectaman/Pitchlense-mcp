"""
Product Risk Analyzer for PitchLense MCP Package.

Analyzes product-related risks including development stage, market fit, technical feasibility, IP protection, and scalability.
"""

from typing import List, Dict, Any
from ..core.base import BaseRiskAnalyzer, BaseMCPTool
from ..models.risk_models import RiskLevel
from ..prompts import PRODUCT_RISK_PROMPT


class ProductRiskAnalyzer(BaseRiskAnalyzer):
    """Product risk analyzer implementation."""
    
    def __init__(self, llm_client):
        """Initialize the product risk analyzer."""
        super().__init__(llm_client, "Product Risks")
        self.risk_indicators = self.get_risk_indicators()
    
    def get_risk_indicators(self) -> List[str]:
        """Get the list of product risk indicators."""
        return [
            "Development Stage Risk",
            "Product-Market Fit Risk",
            "Technical Uncertainty Risk",
            "IP Protection Risk",
            "Scalability Risk"
        ]
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt for product risks."""
        return PRODUCT_RISK_PROMPT


class ProductRiskMCPTool(BaseMCPTool):
    """MCP tool for product risk analysis."""
    
    def __init__(self):
        """Initialize the product risk MCP tool."""
        super().__init__("Product Risk Analyzer", "Analyze product-related risks for startups")
        self.analyzer = ProductRiskAnalyzer(None)  # Will be set when LLM client is available
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        self.analyzer.llm_client = llm_client
    
    def analyze_product_risks(self, startup_data: str) -> dict:
        """
        Analyze product-related risks for a startup.
        
        Args:
            startup_data: Dictionary containing startup information
        
        Returns:
            JSON response with product risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            return self.analyzer.analyze(startup_data)
        except Exception as e:
            return self.create_error_response(f"Analysis failed: {str(e)}")
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.analyze_product_risks)
