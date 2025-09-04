"""
Pydantic models for startup risk analysis data structures.

Provides type-safe models for risk indicators, categories, and analysis results.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class RiskLevel(str, Enum):
    """Enumeration of risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class RiskIndicator(BaseModel):
    """Model for individual risk indicators."""
    indicator: str = Field(description="The specific risk indicator")
    risk_level: RiskLevel = Field(description="Risk level assessment")
    score: int = Field(description="Risk score from 1-10", ge=1, le=10)
    description: str = Field(description="Detailed description of the risk")
    recommendation: str = Field(description="Recommended action to mitigate risk")


class RiskCategory(BaseModel):
    """Model for risk categories containing multiple indicators."""
    category_name: str = Field(description="Name of the risk category")
    overall_risk_level: RiskLevel = Field(description="Overall risk level for this category")
    category_score: int = Field(description="Average risk score for this category", ge=1, le=10)
    indicators: List[RiskIndicator] = Field(description="List of risk indicators in this category")
    summary: str = Field(description="Summary of risks in this category")


class StartupRiskAnalysis(BaseModel):
    """Model for comprehensive startup risk analysis results."""
    startup_name: str = Field(description="Name of the startup being analyzed")
    overall_risk_level: RiskLevel = Field(description="Overall risk level assessment")
    overall_score: int = Field(description="Overall risk score from 1-10", ge=1, le=10)
    risk_categories: List[RiskCategory] = Field(description="List of risk categories analyzed")
    key_concerns: List[str] = Field(description="Top 5 key concerns identified")
    investment_recommendation: str = Field(description="Investment recommendation based on analysis")
    confidence_score: float = Field(description="Confidence in the analysis (0.0-1.0)", ge=0.0, le=1.0)
    analysis_metadata: Optional[Dict[str, Any]] = Field(description="Additional analysis metadata", default=None)


class StartupData(BaseModel):
    """Model for startup input data."""
    name: str = Field(description="Startup name")
    description: str = Field(description="Business description")
    industry: str = Field(description="Industry/sector")
    stage: str = Field(description="Development stage (idea, MVP, growth, etc.)")
    team_size: Optional[int] = Field(description="Number of team members", default=None)
    founders: Optional[List[str]] = Field(description="List of founder names", default=None)
    funding_raised: Optional[float] = Field(description="Total funding raised in USD", default=None)
    revenue: Optional[float] = Field(description="Annual revenue in USD", default=None)
    customers: Optional[int] = Field(description="Number of customers/users", default=None)
    market_size: Optional[str] = Field(description="Target market size description", default=None)
    competitors: Optional[List[str]] = Field(description="List of main competitors", default=None)
    additional_info: Optional[Dict[str, Any]] = Field(description="Additional relevant information", default=None)
