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

__version__ = "1.1.0"
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
from .analyzers.lv_analysis import LVAnalysisAnalyzer
from .tools.lv_analysis_tool import LVAnalysisMCPTool

# Import comprehensive scanner
from .core.comprehensive_scanner import ComprehensiveRiskScanner
from .tools.serp_news import SerpNewsMCPTool
from .tools.serp_pdf_search import SerpPdfSearchMCPTool
from .tools.perplexity_search import PerplexityMCPTool
from .tools.upload_extractor import UploadExtractor
from .tools.knowledge_graph import KnowledgeGraphMCPTool
from .tools.linkedin_analyzer import LinkedInAnalyzerMCPTool
from .tools.content_moderation import GoogleContentModerationMCPTool

# Conditional imports for Google Cloud tools
try:
    from .tools.vertex_ai_rag import VertexAIRAGMCPTool
    from .tools.vertex_ai_agent_builder import VertexAIAgentBuilderMCPTool
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

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
    "LVAnalysisAnalyzer",
    
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
    "LVAnalysisMCPTool",
    
    # Comprehensive scanner
    "ComprehensiveRiskScanner",
    "SerpNewsMCPTool",
    "SerpPdfSearchMCPTool",
    "PerplexityMCPTool",
    "UploadExtractor",
    "KnowledgeGraphMCPTool",
    "LinkedInAnalyzerMCPTool",
    "GoogleContentModerationMCPTool",
]

# Add Vertex AI tools to __all__ if available
if VERTEX_AI_AVAILABLE:
    __all__.extend([
        "VertexAIRAGMCPTool",
        "VertexAIAgentBuilderMCPTool",
    ])
