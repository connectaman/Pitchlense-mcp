"""
Mock LLM client for testing purposes when no API key is available.
"""

from typing import Dict, Any
import json


class MockLLM:
    """
    Mock LLM client that returns sample responses for testing.
    """
    
    def __init__(self):
        """Initialize the mock LLM client."""
        pass
    
    def predict(self, system_message: str, user_message: str, image_base64: str = None) -> Dict[str, Any]:
        """
        Generate a mock prediction response.
        
        Args:
            system_message: System instruction for the model
            user_message: User's input message
            image_base64: Optional base64 encoded image
            
        Returns:
            Dictionary containing a mock response
        """
        # Extract the risk category from the prompt
        category = "Unknown"
        if "customer" in user_message.lower():
            category = "Customer & Traction Risks"
        elif "financial" in user_message.lower():
            category = "Financial Risks"
        elif "market" in user_message.lower():
            category = "Market Risks"
        elif "team" in user_message.lower():
            category = "Team & Founder Risks"
        elif "operational" in user_message.lower():
            category = "Operational Risks"
        elif "competitive" in user_message.lower():
            category = "Competitive Risks"
        elif "exit" in user_message.lower():
            category = "Exit Risks"
        elif "legal" in user_message.lower():
            category = "Legal & Regulatory Risks"
        elif "product" in user_message.lower():
            category = "Product Risks"
        
        # Create a mock JSON response
        mock_response = {
            "category_name": category,
            "overall_risk_level": "medium",
            "category_score": 6,
            "indicators": [
                {
                    "indicator": f"Sample {category.split()[0]} Risk",
                    "risk_level": "medium",
                    "score": 6,
                    "description": "This is a mock analysis for testing purposes. No actual LLM analysis was performed.",
                    "recommendation": "This is a mock recommendation for testing purposes."
                }
            ],
            "summary": f"Mock analysis for {category}. This response was generated for testing when no API key is available."
        }
        
        # Format response with JSON tags
        json_content = json.dumps(mock_response, indent=2)
        formatted_response = f"<JSON>\n{json_content}\n</JSON>"
        
        return {
            "response": formatted_response,
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
    
    async def predict_stream(self, user_message: str):
        """
        Mock streaming prediction (not implemented for testing).
        
        Args:
            user_message: User's input message
            
        Yields:
            Mock streamed response chunks
        """
        yield "Mock streaming response for testing"
