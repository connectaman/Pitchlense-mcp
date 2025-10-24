"""
Test suite for GoogleContentModerationMCPTool
"""

import pytest
from unittest.mock import Mock, patch
from pitchlense_mcp.tools.content_moderation import GoogleContentModerationMCPTool


class TestGoogleContentModerationMCPTool:
    """Test suite for GoogleContentModerationMCPTool"""
    
    def test_initialization(self):
        """Test that the tool initializes correctly"""
        tool = GoogleContentModerationMCPTool()
        assert tool.tool_name == "Google Content Moderation"
        assert tool.description == "Analyze text content for safety and appropriateness using Google's moderation capabilities"
    
    def test_moderate_content_safe_text(self):
        """Test moderation with safe content"""
        tool = GoogleContentModerationMCPTool()
        result = tool.moderate_content("This is a safe business document about startup analysis.")
        
        assert isinstance(result, dict)
        assert result.get("safe") == True
        assert result.get("moderation_required") == False
        assert result.get("confidence") > 0.8
        assert "categories" in result
        assert "message" in result
    
    def test_moderate_content_unsafe_text(self):
        """Test moderation with unsafe content"""
        tool = GoogleContentModerationMCPTool()
        result = tool.moderate_content("This contains hate speech and violence.")
        
        assert isinstance(result, dict)
        assert result.get("safe") == False
        assert result.get("moderation_required") == True
        assert result.get("confidence") < 1.0
        assert len(result.get("categories", [])) > 0
    
    def test_moderate_content_empty_text(self):
        """Test moderation with empty text"""
        tool = GoogleContentModerationMCPTool()
        result = tool.moderate_content("")
        
        assert isinstance(result, dict)
        assert result.get("safe") == True
        assert result.get("moderation_required") == False
        assert result.get("message") == "Empty or null text - no moderation needed"
    
    def test_moderate_content_none_text(self):
        """Test moderation with None text"""
        tool = GoogleContentModerationMCPTool()
        result = tool.moderate_content(None)
        
        assert isinstance(result, dict)
        assert result.get("safe") == True
        assert result.get("moderation_required") == False
    
    def test_is_content_safe_safe_text(self):
        """Test is_content_safe with safe content"""
        tool = GoogleContentModerationMCPTool()
        result = tool.is_content_safe("This is safe business content.")
        
        assert result == True
    
    def test_is_content_safe_unsafe_text(self):
        """Test is_content_safe with unsafe content"""
        tool = GoogleContentModerationMCPTool()
        result = tool.is_content_safe("This contains inappropriate content.")
        
        assert result == False
    
    def test_moderate_content_profanity(self):
        """Test moderation with profanity"""
        tool = GoogleContentModerationMCPTool()
        result = tool.moderate_content("This contains f*** words.")
        
        assert isinstance(result, dict)
        assert result.get("profanity_detected") == True
        assert result.get("moderation_required") == True
    
    def test_moderate_content_multiple_issues(self):
        """Test moderation with multiple issues"""
        tool = GoogleContentModerationMCPTool()
        result = tool.moderate_content("This contains hate speech and violence and is inappropriate.")
        
        assert isinstance(result, dict)
        assert result.get("moderation_required") == True
        assert len(result.get("categories", [])) > 1
    
    def test_moderate_content_analysis_details(self):
        """Test that analysis details are included"""
        tool = GoogleContentModerationMCPTool()
        text = "This is a test document for analysis."
        result = tool.moderate_content(text)
        
        assert "analysis_details" in result
        details = result["analysis_details"]
        assert details["text_length"] == len(text)
        assert "issues_found" in details
        assert "requires_review" in details
    
    def test_moderate_content_exception_handling(self):
        """Test exception handling in moderation"""
        tool = GoogleContentModerationMCPTool()
        
        # Mock the internal analysis to raise an exception
        with patch.object(tool, '_analyze_with_google_moderation', side_effect=Exception("Test error")):
            result = tool.moderate_content("Test content")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "Content moderation error" in result["error"]
    
    def test_register_tools(self):
        """Test tool registration"""
        tool = GoogleContentModerationMCPTool()
        # This should not raise an exception
        tool.register_tools()
