"""
LV-Analysis MCP Tool wrapper for detailed startup analysis.
"""

from typing import Dict, Any
from ..core.base import BaseMCPTool
from ..analyzers.lv_analysis import LVAnalysisAnalyzer


class LVAnalysisMCPTool(BaseMCPTool):
    """MCP Tool for LV-Analysis."""

    def __init__(self):
        super().__init__(
            tool_name="lv_analysis",
            description="Detailed LV-Analysis business note generation for startup evaluation"
        )
        # Import Perplexity tool here to avoid circular imports
        from .perplexity_search import PerplexityMCPTool
        perplexity_tool = PerplexityMCPTool()
        self.analyzer = LVAnalysisAnalyzer(perplexity_tool=perplexity_tool)

    def analyze_lv_business_note(self, startup_text: str) -> Dict[str, Any]:
        """
        Generate detailed LV-Analysis business note.
        
        Args:
            startup_text: Detailed startup information and description
            
        Returns:
            Comprehensive business analysis in hackathon format
        """
        try:
            # Perform the analysis
            result = self.analyzer.analyze(startup_text)
            
            return {
                "category_name": "LV-Analysis",
                "analysis_type": "detailed_business_note",
                "status": "success",
                "result": result,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "category_name": "LV-Analysis", 
                "analysis_type": "detailed_business_note",
                "status": "error",
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
