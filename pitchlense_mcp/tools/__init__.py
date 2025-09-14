"""
Tools package for PitchLense MCP.

Exports:
- SerpNewsMCPTool: Google News via SerpAPI
- SerpPdfSearchMCPTool: PDF document search via SerpAPI
- PerplexityMCPTool: Perplexity search and synthesis
- UploadExtractor: File extractor and Perplexity synthesis for startup_text
- VertexAIRAGMCPTool: Google Vertex AI RAG for document search and Q&A
- VertexAIAgentBuilderMCPTool: Google Vertex AI Agent Builder for conversational AI
"""

from .serp_news import SerpNewsMCPTool  # noqa: F401
from .serp_pdf_search import SerpPdfSearchMCPTool  # noqa: F401
from .perplexity_search import PerplexityMCPTool  # noqa: F401
from .upload_extractor import UploadExtractor  # noqa: F401

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
]

# Add Vertex AI tools to __all__ if available
if VERTEX_AI_AVAILABLE:
    __all__.extend([
        "VertexAIRAGMCPTool",
        "VertexAIAgentBuilderMCPTool",
    ])


