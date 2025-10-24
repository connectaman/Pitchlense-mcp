"""
Tools package for PitchLense MCP.

Exports:
- SerpNewsMCPTool: Google News via SerpAPI
- SerpPdfSearchMCPTool: PDF document search via SerpAPI
- PerplexityMCPTool: Perplexity search and synthesis
- UploadExtractor: File extractor and Perplexity synthesis for startup_text
- LVAnalysisMCPTool: Detailed LV-Analysis business note generation
- KnowledgeGraphMCPTool: Build dependency knowledge graphs with market data
- VertexAIRAGMCPTool: Google Vertex AI RAG for document search and Q&A
- VertexAIAgentBuilderMCPTool: Google Vertex AI Agent Builder for conversational AI
"""

from .serp_news import SerpNewsMCPTool  # noqa: F401
from .serp_pdf_search import SerpPdfSearchMCPTool  # noqa: F401
from .perplexity_search import PerplexityMCPTool  # noqa: F401
from .upload_extractor import UploadExtractor  # noqa: F401
from .lv_analysis_tool import LVAnalysisMCPTool  # noqa: F401
from .knowledge_graph import KnowledgeGraphMCPTool  # noqa: F401
from .linkedin_analyzer import LinkedInAnalyzerMCPTool  # noqa: F401
from .content_moderation import GoogleContentModerationMCPTool  # noqa: F401

# Conditional imports for Google Cloud tools
try:
    from .vertex_ai_rag import VertexAIRAGMCPTool  # noqa: F401
    from .vertex_ai_agent_builder import VertexAIAgentBuilderMCPTool  # noqa: F401
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

__all__ = [
    "SerpNewsMCPTool",
    "SerpPdfSearchMCPTool",
    "PerplexityMCPTool",
    "UploadExtractor",
    "LVAnalysisMCPTool",
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


