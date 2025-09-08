"""
PitchLense MCP - Professional Startup Risk Analysis Package

A comprehensive Model Context Protocol (MCP) package for analyzing startup 
investment risks using AI-powered assessment across multiple risk categories.

Key Features:
- 9 specialized risk analysis tools
- Comprehensive risk scanner
- AI-powered analysis using Google Gemini
- Structured JSON outputs
- Professional package architecture
"""

__version__ = "1.0.0"
__author__ = "Aman Ulla"
__email__ = "connectamanulla@gmail.com"

from .core.base import BaseRiskAnalyzer, BaseMCPTool
from .core.gemini_client import GeminiLLM
from .models.risk_models import (
    RiskLevel, 
    RiskIndicator, 
    RiskCategory, 
    StartupRiskAnalysis,
    StartupData
)

# Import all analyzers
from .analyzers.market_risk import MarketRiskAnalyzer, MarketRiskMCPTool
from .analyzers.product_risk import ProductRiskAnalyzer, ProductRiskMCPTool
from .analyzers.team_risk import TeamRiskAnalyzer, TeamRiskMCPTool
from .analyzers.financial_risk import FinancialRiskAnalyzer, FinancialRiskMCPTool
from .analyzers.customer_risk import CustomerRiskAnalyzer, CustomerRiskMCPTool
from .analyzers.operational_risk import OperationalRiskAnalyzer, OperationalRiskMCPTool
from .analyzers.competitive_risk import CompetitiveRiskAnalyzer, CompetitiveRiskMCPTool
from .analyzers.legal_risk import LegalRiskAnalyzer, LegalRiskMCPTool
from .analyzers.exit_risk import ExitRiskAnalyzer, ExitRiskMCPTool
from .analyzers.peer_benchmark import PeerBenchmarkAnalyzer, PeerBenchmarkMCPTool

# Import comprehensive scanner
from .core.comprehensive_scanner import ComprehensiveRiskScanner
from .tools.serp_news import SerpNewsMCPTool
from .tools.perplexity_search import PerplexityMCPTool
from .tools.upload_extractor import UploadExtractor

__all__ = [
    # Core classes
    "BaseRiskAnalyzer",
    "BaseMCPTool", 
    "GeminiLLM",
    
    # Models
    "RiskLevel",
    "RiskIndicator", 
    "RiskCategory",
    "StartupRiskAnalysis",
    "StartupData",
    
    # Individual analyzers
    "MarketRiskAnalyzer",
    "ProductRiskAnalyzer",
    "TeamRiskAnalyzer", 
    "FinancialRiskAnalyzer",
    "CustomerRiskAnalyzer",
    "OperationalRiskAnalyzer",
    "CompetitiveRiskAnalyzer",
    "LegalRiskAnalyzer",
    "ExitRiskAnalyzer",
    "PeerBenchmarkAnalyzer",
    
    # MCP Tools
    "MarketRiskMCPTool",
    "ProductRiskMCPTool",
    "TeamRiskMCPTool",
    "FinancialRiskMCPTool",
    "CustomerRiskMCPTool",
    "OperationalRiskMCPTool",
    "CompetitiveRiskMCPTool",
    "LegalRiskMCPTool",
    "ExitRiskMCPTool",
    "PeerBenchmarkMCPTool",
    
    # Comprehensive scanner
    "ComprehensiveRiskScanner",
    "SerpNewsMCPTool",
    "PerplexityMCPTool",
    "UploadExtractor",
]
