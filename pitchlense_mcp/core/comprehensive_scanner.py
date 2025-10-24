"""
Comprehensive Risk Scanner for PitchLense MCP Package.

Combines all individual risk analyzers to provide comprehensive startup risk analysis.
"""

from typing import Dict, Any, List
import re
from fastmcp import FastMCP
import json

from .base import BaseMCPTool
from .gemini_client import GeminiLLM
from ..models.risk_models import RiskLevel, StartupRiskAnalysis
from ..analyzers import (
    MarketRiskAnalyzer,
    ProductRiskAnalyzer,
    TeamRiskAnalyzer,
    FinancialRiskAnalyzer,
    CustomerRiskAnalyzer,
    OperationalRiskAnalyzer,
    CompetitiveRiskAnalyzer,
    LegalRiskAnalyzer,
    ExitRiskAnalyzer
)


class ComprehensiveRiskScanner(BaseMCPTool):
    """Comprehensive risk scanner that combines all individual analyzers."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the comprehensive risk scanner.
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
        """
        super().__init__("Comprehensive Startup Risk Scanner", "Comprehensive startup risk analysis across all categories")
        
        # Initialize Gemini client
        self.llm_client = GeminiLLM(api_key)
        
        # Initialize all analyzers
        self.analyzers = {
            "Market Risks": MarketRiskAnalyzer(self.llm_client),
            "Product Risks": ProductRiskAnalyzer(self.llm_client),
            "Team & Founder Risks": TeamRiskAnalyzer(self.llm_client),
            "Financial Risks": FinancialRiskAnalyzer(self.llm_client),
            "Customer & Traction Risks": CustomerRiskAnalyzer(self.llm_client),
            "Operational Risks": OperationalRiskAnalyzer(self.llm_client),
            "Competitive Risks": CompetitiveRiskAnalyzer(self.llm_client),
            "Legal & Regulatory Risks": LegalRiskAnalyzer(self.llm_client),
            "Exit Risks": ExitRiskAnalyzer(self.llm_client)
        }
    
    def calculate_overall_risk_level(self, category_scores: List[int]) -> tuple:
        """Calculate overall risk level and score from category scores."""
        if not category_scores:
            return RiskLevel.UNKNOWN, 0
        
        avg_score = sum(category_scores) / len(category_scores)
        
        if avg_score <= 3:
            return RiskLevel.LOW, round(avg_score)
        elif avg_score <= 6:
            return RiskLevel.MEDIUM, round(avg_score)
        elif avg_score <= 8:
            return RiskLevel.HIGH, round(avg_score)
        else:
            return RiskLevel.CRITICAL, round(avg_score)
    
    def comprehensive_startup_risk_analysis(self, startup_data: str) -> dict:
        """
        Perform comprehensive startup risk analysis across all risk categories.
        
        Args:
            startup_data: Unstructured startup information as a single string
        
        Returns:
            JSON response with comprehensive risk analysis
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        try:
            risk_categories = []
            category_scores = []
            all_indicators = []
            
            # Run all individual risk analyses
            for category_name, analyzer in self.analyzers.items():
                try:
                    result = analyzer.analyze(startup_data)
                    
                    if "error" in result:
                        # Create a fallback category for failed analysis
                        risk_categories.append({
                            "category_name": category_name,
                            "overall_risk_level": "unknown",
                            "category_score": 5,
                            "indicators": [],
                            "summary": f"Analysis failed: {result['error']}"
                        })
                        category_scores.append(5)
                    else:
                        risk_categories.append(result)
                        category_scores.append(result.get("category_score", 5))
                        
                        # Collect all indicators for key concerns analysis
                        indicators = result.get("indicators", [])
                        for indicator in indicators:
                            all_indicators.append({
                                "category": category_name,
                                "indicator": indicator.get("indicator", ""),
                                "risk_level": indicator.get("risk_level", "medium"),
                                "score": indicator.get("score", 5),
                                "description": indicator.get("description", "")
                            })
                            
                except Exception as e:
                    # Handle individual analyzer failures gracefully
                    risk_categories.append({
                        "category_name": category_name,
                        "overall_risk_level": "unknown",
                        "category_score": 5,
                        "indicators": [],
                        "summary": f"Analysis failed due to error: {str(e)}"
                    })
                    category_scores.append(5)
            
            # Calculate overall risk assessment
            overall_risk_level, overall_score = self.calculate_overall_risk_level(category_scores)
            
            # Identify key concerns (top 5 highest risk indicators)
            sorted_indicators = sorted(all_indicators, key=lambda x: x["score"], reverse=True)
            key_concerns = [ind["description"] for ind in sorted_indicators[:5]]
            
            # Generate investment recommendation using Gemini
            company_name = self._extract_company_name(startup_data)
            recommendation_prompt = f"""
            Based on the comprehensive risk analysis for {company_name}, provide an investment recommendation.
            
            Overall Risk Level: {overall_risk_level.value}
            Overall Risk Score: {overall_score}/10
            
            Key Concerns:
            {chr(10).join(f"- {concern}" for concern in key_concerns)}
            
            Please provide a concise investment recommendation (1-2 sentences) and confidence score (0.0-1.0).
            
            Return in JSON format:
            {{
                "investment_recommendation": "Your recommendation here",
                "confidence_score": 0.0-1.0
            }}
            """
            
            recommendation_result = self.llm_client.predict(
                system_message="You are an expert investment advisor. Maintain professional language and avoid inappropriate content. Focus strictly on business and investment analysis.",
                user_message=recommendation_prompt
            )
            
            investment_recommendation = "Unable to generate recommendation due to analysis errors"
            confidence_score = 0.5
            
            try:
                rec_text = recommendation_result.get("response", "")
                if rec_text.startswith('```json'):
                    rec_text = rec_text[7:]
                if rec_text.endswith('```'):
                    rec_text = rec_text[:-3]
                
                rec_data = json.loads(rec_text)
                investment_recommendation = rec_data.get("investment_recommendation", investment_recommendation)
                confidence_score = rec_data.get("confidence_score", 0.5)
            except:
                pass
            
            # Create comprehensive analysis result
            comprehensive_analysis = {
                "startup_name": company_name,
                "overall_risk_level": overall_risk_level.value,
                "overall_score": overall_score,
                "risk_categories": risk_categories,
                "key_concerns": key_concerns,
                "investment_recommendation": investment_recommendation,
                "confidence_score": confidence_score,
                "analysis_metadata": {
                    "total_categories_analyzed": len(self.analyzers),
                    "successful_analyses": len([cat for cat in risk_categories if "error" not in cat.get("summary", "")]),
                    "analysis_timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
                }
            }
            
            return comprehensive_analysis
            
        except Exception as e:
            return self.create_error_response(f"Comprehensive analysis failed: {str(e)}")
    
    def quick_risk_assessment(self, startup_data: str) -> dict:
        """
        Perform a quick risk assessment focusing on the most critical risk indicators.
        
        Args:
            startup_data: Unstructured startup information as a single string
        
        Returns:
            JSON response with quick risk assessment
        """
        if not self.validate_startup_data(startup_data):
            return self.create_error_response("Invalid startup data format")
        
        # Focus on the most critical risk categories for quick assessment
        critical_analyzers = {
            "Financial Risks": self.analyzers["Financial Risks"],
            "Team & Founder Risks": self.analyzers["Team & Founder Risks"],
            "Market Risks": self.analyzers["Market Risks"]
        }
        
        quick_results = []
        scores = []
        
        for category_name, analyzer in critical_analyzers.items():
            try:
                result = analyzer.analyze(startup_data)
                quick_results.append(result)
                scores.append(result.get("category_score", 5))
            except:
                scores.append(5)
        
        overall_risk_level, overall_score = self.calculate_overall_risk_level(scores)
        
        return {
            "startup_name": self._extract_company_name(startup_data),
            "assessment_type": "quick",
            "overall_risk_level": overall_risk_level.value,
            "overall_score": overall_score,
            "analyzed_categories": quick_results,
            "note": "Quick assessment covers Financial, Team, and Market risks only"
        }
    
    def register_tools(self):
        """Register MCP tools."""
        self.register_tool(self.comprehensive_startup_risk_analysis)
        self.register_tool(self.quick_risk_assessment)
    
    def run(self):
        """Run the comprehensive risk scanner MCP server."""
        self.register_tools()
        self.mcp.run()

    def _extract_company_name(self, startup_text: str) -> str:
        """Extract company name from unstructured text, if present."""
        try:
            patterns = [
                r"(?im)^name\s*[:\-]\s*(.+)$",
                r"(?im)^company\s*[:\-]\s*(.+)$",
                r"(?im)^company\s+name\s*[:\-]\s*(.+)$",
            ]
            for pattern in patterns:
                match = re.search(pattern, startup_text)
                if match:
                    return match.group(1).strip()
        except Exception:
            pass
        return "Unknown Startup"
