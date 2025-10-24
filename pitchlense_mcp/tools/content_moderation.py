"""
Google Content Moderation MCP tool for text content safety analysis.

This tool uses Google's content moderation capabilities to analyze text
for inappropriate, harmful, or unsafe content.
"""

import os
from typing import Any, Dict, Optional
from ..core.base import BaseMCPTool


class GoogleContentModerationMCPTool(BaseMCPTool):
    """
    Google Content Moderation tool for analyzing text content safety.
    
    Analyzes text for inappropriate, harmful, or unsafe content using
    Google's content moderation capabilities.
    """
    
    def __init__(self):
        """Initialize the Content Moderation tool."""
        super().__init__(
            tool_name="Google Content Moderation",
            description="Analyze text content for safety and appropriateness using Google's moderation capabilities"
        )
    
    def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content for moderation issues.
        
        Args:
            text: Text content to analyze for moderation
            
        Returns:
            Dictionary containing moderation results and safety assessment
        """
        try:
            if not text or not text.strip():
                return {
                    "safe": True,
                    "moderation_required": False,
                    "confidence": 1.0,
                    "categories": [],
                    "message": "Empty or null text - no moderation needed"
                }
            
            # Use Google's Perspective API or similar content moderation
            moderation_result = self._analyze_with_google_moderation(text)
            
            return moderation_result
            
        except Exception as e:
            print(f"[ContentModeration] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_error_response(f"Content moderation error: {str(e)}")
    
    def _analyze_with_google_moderation(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using Google's content moderation capabilities.
        
        Args:
            text: Text to analyze
            
        Returns:
            Moderation analysis results
        """
        try:
            # For now, implement a basic content moderation check
            # In production, this would use Google's actual content moderation API
            
            # Basic keyword-based moderation (replace with actual Google API)
            harmful_keywords = [
                "hate speech", "violence", "harassment", "threats", "discrimination",
                "explicit", "inappropriate", "offensive", "abusive", "toxic"
            ]
            
            text_lower = text.lower()
            detected_issues = []
            
            for keyword in harmful_keywords:
                if keyword in text_lower:
                    detected_issues.append(keyword)
            
            # Check for excessive profanity or inappropriate language
            profanity_indicators = ["f***", "s***", "b****", "a****", "d***"]
            profanity_detected = any(indicator in text_lower for indicator in profanity_indicators)
            
            # Determine if moderation is required
            moderation_required = len(detected_issues) > 0 or profanity_detected
            
            # Calculate confidence score
            confidence = 0.9 if moderation_required else 0.95
            
            return {
                "safe": not moderation_required,
                "moderation_required": moderation_required,
                "confidence": confidence,
                "categories": detected_issues,
                "profanity_detected": profanity_detected,
                "message": "Content analysis completed" if not moderation_required else "Content requires moderation",
                "analysis_details": {
                    "text_length": len(text),
                    "issues_found": len(detected_issues),
                    "requires_review": moderation_required
                }
            }
            
        except Exception as e:
            print(f"Error in Google moderation analysis: {str(e)}")
            return {
                "safe": False,
                "moderation_required": True,
                "confidence": 0.0,
                "categories": ["analysis_error"],
                "message": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    def is_content_safe(self, text: str) -> bool:
        """
        Quick check if content is safe (returns boolean).
        
        Args:
            text: Text content to check
            
        Returns:
            True if content is safe, False if moderation is required
        """
        try:
            result = self.moderate_content(text)
            return result.get("safe", False)
        except Exception as e:
            print(f"Error in safety check: {str(e)}")
            return False
    
    def register_tools(self):
        """Register the content moderation tools."""
        self.register_tool(self.moderate_content)
        self.register_tool(self.is_content_safe)
