"""
LV-Analysis MCP Tool wrapper for detailed startup analysis.
"""

from typing import Dict, Any
from datetime import datetime, timezone
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

    def set_llm_client(self, llm_client):
        """Set the LLM client for the analyzer."""
        print(f"[LV-Analysis] Setting LLM client: {type(llm_client).__name__}")
        self.analyzer.llm_client = llm_client

    def analyze_lv_business_note(self, startup_text: str) -> Dict[str, Any]:
        """
        Generate detailed LV-Analysis business note.
        
        Args:
            startup_text: Detailed startup information and description
            
        Returns:
            Comprehensive business analysis in hackathon format
        """
        print(f"[LV-Analysis] Starting analysis with startup_text length: {len(startup_text)}")
        
        try:
            # Check if LLM client is available
            if not self.analyzer.llm_client:
                print("[LV-Analysis] ERROR: No LLM client provided to analyzer")
                return {
                    "category_name": "LV-Analysis",
                    "analysis_type": "detailed_business_note", 
                    "status": "error",
                    "error": "No LLM client available for analysis",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            print("[LV-Analysis] LLM client available, proceeding with analysis")
            
            # Perform the analysis
            result = self.analyzer.analyze(startup_text)
            
            print(f"[LV-Analysis] Analysis completed successfully")
            
            return {
                "category_name": "LV-Analysis",
                "analysis_type": "detailed_business_note",
                "status": "success",
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[LV-Analysis] ERROR: Analysis failed with exception: {str(e)}")
            return {
                "category_name": "LV-Analysis", 
                "analysis_type": "detailed_business_note",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
