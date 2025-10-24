"""
Base classes for PitchLense MCP risk analysis tools.

Provides abstract base classes and common functionality for all risk analyzers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
import json

from ..models.risk_models import RiskCategory, RiskLevel, StartupData
from ..utils.json_extractor import extract_json_from_response


class BaseLLM(ABC):
    """
    Abstract base class for LLM integrations.
    
    Provides a common interface for different LLM providers.
    """
    
    def __init__(self):
        """Initialize the base LLM."""
        pass
    
    @abstractmethod
    def predict(
        self, 
        system_message: str, 
        user_message: str, 
        image_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate prediction from the LLM.
        
        Args:
            system_message: System instruction for the model
            user_message: User's input message
            image_base64: Optional base64 encoded image
            
        Returns:
            Dictionary containing the response and usage information
        """
        pass
    
    @abstractmethod
    async def predict_stream(self, user_message: str):
        """
        Stream predictions from the LLM.
        
        Args:
            user_message: User's input message
            
        Yields:
            Streamed response chunks
        """
        pass


class BaseRiskAnalyzer(ABC):
    """
    Abstract base class for all risk analyzers.
    
    Provides common functionality and interface for risk analysis tools.
    """
    
    def __init__(self, llm_client, category_name: str):
        """
        Initialize the base risk analyzer.
        
        Args:
            llm_client: LLM client instance for analysis
            category_name: Name of the risk category
        """
        self.llm_client = llm_client
        self.category_name = category_name
        self.risk_indicators = []
    
    @abstractmethod
    def get_analysis_prompt(self) -> str:
        """
        Get the analysis prompt for this risk category.
        
        Returns:
            String containing the analysis prompt
        """
        pass
    
    @abstractmethod
    def get_risk_indicators(self) -> List[str]:
        """
        Get the list of risk indicators for this category.
        
        Returns:
            List of risk indicator names
        """
        pass
    
    def analyze(self, startup_data: str) -> Dict[str, Any]:
        """
        Perform risk analysis for the given startup data.
        
        Args:
            startup_data: String containing comprehensive startup information
            
        Returns:
            Dictionary containing risk analysis results
        """
        try:
            prompt = self.get_analysis_prompt()
            # Format the prompt with the startup data
            full_prompt = prompt.format(startup_data=startup_data)
            
            # Use the LLM client to generate analysis
            result = self.llm_client.predict(
                system_message="You are an expert startup risk analyst. Maintain professional language and avoid inappropriate content. Focus strictly on business and financial risk assessment.",
                user_message=full_prompt
            )
            
            # Parse the response using the JSON extractor
            response_text = result.get("response", "")
            # Extract JSON from the response first; don't treat mere mentions of the word
            # "error" in normal prose as actual failures.
            analysis_result = extract_json_from_response(response_text)
            
            if analysis_result is not None:
                return analysis_result
            else:
                return self._create_fallback_response(response_text, "JSON extraction failed")
                
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _create_fallback_response(self, raw_response: str, error_msg: str = "") -> Dict[str, Any]:
        """
        Create a fallback response when JSON parsing fails.
        
        Args:
            raw_response: Raw response text from LLM
            error_msg: JSON parsing error message
            
        Returns:
            Fallback response dictionary
        """
        return {
            "category_name": self.category_name,
            "overall_risk_level": "unknown",
            "category_score": 5,
            "indicators": [],
            "summary": f"Analysis completed but JSON parsing failed. Error: {error_msg}. Raw response: {raw_response[:200]}..."
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error response when analysis fails.
        
        Args:
            error_message: Error message from the exception
            
        Returns:
            Error response dictionary
        """
        return {
            "error": error_message,
            "category_name": self.category_name,
            "overall_risk_level": "unknown",
            "category_score": 0,
            "indicators": [],
            "summary": f"Analysis failed due to error: {error_message}"
        }


class BaseMCPTool:
    """
    Base class for MCP tools with common functionality.
    
    Provides shared methods and utilities for MCP tool implementations.
    """
    
    def __init__(self, tool_name: str, description: str):
        """
        Initialize the base MCP tool.
        
        Args:
            tool_name: Name of the MCP tool
            description: Description of the tool's purpose
        """
        self.tool_name = tool_name
        self.description = description
        self.mcp = FastMCP(tool_name)
    
    def register_tool(self, func):
        """
        Register a function as an MCP tool.
        
        Args:
            func: Function to register as MCP tool
        """
        return self.mcp.tool()(func)
    
    def run(self):
        """Run the MCP server."""
        self.mcp.run()
    
    def validate_startup_data(self, startup_data: str) -> bool:
        """
        Validate startup data format.
        
        Args:
            startup_data: String containing startup information
            
        Returns:
            True if data is valid, False otherwise
        """
        # Basic validation - check if it's a non-empty string
        return isinstance(startup_data, str) and len(startup_data.strip()) > 0
    
    def create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            error_message: Error message to include
            
        Returns:
            Standardized error response dictionary
        """
        return {
            "error": error_message,
            "timestamp": "2024-01-01T00:00:00Z",  # You might want to use actual timestamp
            "success": False
        }
