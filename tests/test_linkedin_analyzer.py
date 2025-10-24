"""
Test suite for LinkedInAnalyzerMCPTool
"""

import pytest
from unittest.mock import Mock, patch
from pitchlense_mcp.tools.linkedin_analyzer import LinkedInAnalyzerMCPTool


class TestLinkedInAnalyzerMCPTool:
    """Test suite for LinkedInAnalyzerMCPTool"""
    
    def test_initialization(self):
        """Test that the tool initializes correctly"""
        tool = LinkedInAnalyzerMCPTool()
        assert tool.tool_name == "LinkedIn Profile Analyzer"
        assert tool.description == "Analyze LinkedIn profiles for comprehensive founder evaluation and VC assessment"
        assert tool.llm_client is None
    
    def test_set_llm_client(self):
        """Test setting LLM client"""
        tool = LinkedInAnalyzerMCPTool()
        mock_llm = Mock()
        tool.set_llm_client(mock_llm)
        assert tool.llm_client == mock_llm
    
    def test_create_analysis_prompt(self):
        """Test analysis prompt creation"""
        tool = LinkedInAnalyzerMCPTool()
        prompt = tool._create_analysis_prompt()
        
        assert isinstance(prompt, str)
        assert "elite venture capital analyst" in prompt
        assert "JSON Schema" in prompt
        assert "overallScore" in prompt
        assert "scores" in prompt
        assert "detailedKPIs" in prompt
    
    @patch('pitchlense_mcp.tools.linkedin_analyzer.GeminiDocumentAnalyzer')
    def test_analyze_linkedin_profile_success(self, mock_doc_analyzer_class):
        """Test successful LinkedIn profile analysis with GeminiDocumentAnalyzer"""
        tool = LinkedInAnalyzerMCPTool()
        mock_llm = Mock()
        tool.llm_client = mock_llm
        
        # Mock GeminiDocumentAnalyzer
        mock_doc_analyzer = Mock()
        mock_doc_analyzer.predict.return_value = {
            "text": """
            {
              "overallScore": 85,
              "overallRating": "Strong Founder",
              "overallSummary": "Experienced technical founder with strong background",
              "summary": "Experienced founder with technical expertise and leadership skills.",
              "scores": [
                {
                  "competency": "Technical Expertise",
                  "score": 90,
                  "justification": "Strong technical background in software engineering"
                }
              ],
              "detailedKPIs": [
                {
                  "icon": "📊",
                  "metric": "Years of Experience",
                  "value": "10",
                  "description": "Total years in the workforce"
                }
              ],
              "keyStrengths": ["Strong technical background", "Leadership experience"],
              "potentialRisks": ["Limited startup experience"],
              "investmentRecommendation": "Strong candidate for early-stage investment"
            }
            """
        }
        mock_doc_analyzer_class.return_value = mock_doc_analyzer
        
        result = tool.analyze_linkedin_profile("test.pdf")
        
        assert isinstance(result, dict)
        assert result.get("overallScore") == 85
        assert result.get("overallRating") == "Strong Founder"
        assert "scores" in result
        assert "detailedKPIs" in result
        mock_doc_analyzer.predict.assert_called_once()
    
    def test_analyze_linkedin_profile_no_llm(self):
        """Test analysis without LLM client"""
        tool = LinkedInAnalyzerMCPTool()
        tool.llm_client = None
        
        result = tool.analyze_linkedin_profile("test.pdf")
        assert "error" in result
        assert "LLM client not configured" in result["error"]
    
    @patch('pitchlense_mcp.tools.linkedin_analyzer.GeminiDocumentAnalyzer')
    def test_analyze_linkedin_profile_json_parse_error(self, mock_doc_analyzer_class):
        """Test analysis with JSON parsing error"""
        tool = LinkedInAnalyzerMCPTool()
        mock_llm = Mock()
        tool.llm_client = mock_llm
        
        # Mock GeminiDocumentAnalyzer with invalid JSON
        mock_doc_analyzer = Mock()
        mock_doc_analyzer.predict.return_value = {
            "text": "Invalid JSON response"
        }
        mock_doc_analyzer_class.return_value = mock_doc_analyzer
        
        result = tool.analyze_linkedin_profile("test.pdf")
        
        assert "error" in result
        assert "Failed to parse analysis JSON" in result["error"]
    
    def test_analyze_linkedin_profile_exception(self):
        """Test analysis with exception"""
        tool = LinkedInAnalyzerMCPTool()
        mock_llm = Mock()
        tool.llm_client = mock_llm
        
        # Mock exception during analysis
        with patch.object(tool, '_extract_pdf_text', side_effect=Exception("Test error")):
            result = tool.analyze_linkedin_profile("test.pdf")
            
            assert "error" in result
            assert "LinkedIn analysis error" in result["error"]
    
    def test_register_tools(self):
        """Test tool registration"""
        tool = LinkedInAnalyzerMCPTool()
        # This should not raise an exception
        tool.register_tools()
