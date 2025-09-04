"""
Basic tests for PitchLense MCP Package.

Tests core functionality and basic integration.
"""

import pytest
import json
from unittest.mock import Mock, patch

from pitchlense_mcp import (
    ComprehensiveRiskScanner,
    MarketRiskAnalyzer,
    GeminiLLM,
    RiskLevel,
    StartupData
)


class TestStartupData:
    """Test StartupData model."""
    
    def test_startup_data_creation(self):
        """Test creating StartupData instance."""
        data = StartupData(
            name="Test Startup",
            description="Test description",
            industry="Technology",
            stage="MVP"
        )
        
        assert data.name == "Test Startup"
        assert data.description == "Test description"
        assert data.industry == "Technology"
        assert data.stage == "MVP"
        assert data.team_size is None
        assert data.founders is None


class TestRiskLevel:
    """Test RiskLevel enum."""
    
    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.LOW == "low"
        assert RiskLevel.MEDIUM == "medium"
        assert RiskLevel.HIGH == "high"
        assert RiskLevel.CRITICAL == "critical"
        assert RiskLevel.UNKNOWN == "unknown"


class TestGeminiLLM:
    """Test GeminiLLM integration."""
    
    @patch('pitchlense_mcp.core.gemini_client.genai')
    def test_gemini_llm_initialization(self, mock_genai):
        """Test GeminiLLM initialization."""
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client
        
        llm = GeminiLLM(api_key="test_key")
        
        assert llm.api_key == "test_key"
        assert llm.model == "gemini-2.5-flash"
        # Multiple internal components initialize clients; ensure at least one correct call
        assert mock_genai.Client.call_count >= 1
        for args, kwargs in mock_genai.Client.call_args_list:
            assert kwargs.get("api_key") == "test_key"
    
    @patch('pitchlense_mcp.core.gemini_client.genai')
    def test_gemini_llm_predict(self, mock_genai):
        """Test GeminiLLM predict method."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        llm = GeminiLLM(api_key="test_key")
        result = llm.predict("system", "user")
        
        assert result["response"] == "Test response"
        assert result["usage"]["model"] == "gemini-2.5-flash"
        assert result["usage"]["type"] == "text_generation"


class TestMarketRiskAnalyzer:
    """Test MarketRiskAnalyzer."""
    
    def test_market_risk_analyzer_initialization(self):
        """Test MarketRiskAnalyzer initialization."""
        mock_llm = Mock()
        analyzer = MarketRiskAnalyzer(mock_llm)
        
        assert analyzer.category_name == "Market Risks"
        assert "TAM Size Assessment" in analyzer.get_risk_indicators()
        assert "Industry Growth Rate" in analyzer.get_risk_indicators()
    
    def test_market_risk_analyzer_prompt(self):
        """Test MarketRiskAnalyzer prompt generation."""
        mock_llm = Mock()
        analyzer = MarketRiskAnalyzer(mock_llm)
        prompt = analyzer.get_analysis_prompt()
        
        assert "market risk assessment" in prompt.lower()
        assert "TAM" in prompt
        assert "competition" in prompt.lower()
        assert "<JSON>" in prompt


class TestComprehensiveRiskScanner:
    """Test ComprehensiveRiskScanner."""
    
    @patch('pitchlense_mcp.core.comprehensive_scanner.GeminiLLM')
    def test_comprehensive_scanner_initialization(self, mock_gemini):
        """Test ComprehensiveRiskScanner initialization."""
        mock_llm = Mock()
        mock_gemini.return_value = mock_llm
        
        scanner = ComprehensiveRiskScanner(api_key="test_key")
        
        assert len(scanner.analyzers) == 9
        assert "Market Risks" in scanner.analyzers
        assert "Product Risks" in scanner.analyzers
        assert "Team & Founder Risks" in scanner.analyzers
        assert "Financial Risks" in scanner.analyzers
        assert "Customer & Traction Risks" in scanner.analyzers
        assert "Operational Risks" in scanner.analyzers
        assert "Competitive Risks" in scanner.analyzers
        assert "Legal & Regulatory Risks" in scanner.analyzers
        assert "Exit Risks" in scanner.analyzers
    
    def test_calculate_overall_risk_level(self):
        """Test overall risk level calculation."""
        scanner = ComprehensiveRiskScanner(api_key="test_key")
        
        # Test low risk
        risk_level, score = scanner.calculate_overall_risk_level([1, 2, 3])
        assert risk_level == RiskLevel.LOW
        assert score == 2
        
        # Test medium risk
        risk_level, score = scanner.calculate_overall_risk_level([4, 5, 6])
        assert risk_level == RiskLevel.MEDIUM
        assert score == 5
        
        # Test high risk
        risk_level, score = scanner.calculate_overall_risk_level([7, 8])
        assert risk_level == RiskLevel.HIGH
        assert score == 8
        
        # Test critical risk
        risk_level, score = scanner.calculate_overall_risk_level([9, 10])
        assert risk_level == RiskLevel.CRITICAL
        assert score == 10
        
        # Test empty list
        risk_level, score = scanner.calculate_overall_risk_level([])
        assert risk_level == RiskLevel.UNKNOWN
        assert score == 0
    
    @patch('pitchlense_mcp.core.comprehensive_scanner.GeminiLLM')
    def test_comprehensive_analysis_validation(self, mock_gemini):
        """Test comprehensive analysis input validation."""
        mock_llm = Mock()
        mock_gemini.return_value = mock_llm
        
        scanner = ComprehensiveRiskScanner(api_key="test_key")
        
        # Test invalid data
        invalid_data = {"name": "Test"}  # Missing required fields
        result = scanner.comprehensive_startup_risk_analysis(invalid_data)
        
        assert "error" in result
        assert "Invalid startup data format" in result["error"]
    
    @patch('pitchlense_mcp.core.comprehensive_scanner.GeminiLLM')
    def test_quick_assessment_validation(self, mock_gemini):
        """Test quick assessment input validation."""
        mock_llm = Mock()
        mock_gemini.return_value = mock_llm
        
        scanner = ComprehensiveRiskScanner(api_key="test_key")
        
        # Test invalid data
        invalid_data = {"name": "Test"}  # Missing required fields
        result = scanner.quick_risk_assessment(invalid_data)
        
        assert "error" in result
        assert "Invalid startup data format" in result["error"]


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.integration
    @patch('pitchlense_mcp.core.gemini_client.genai')
    def test_end_to_end_analysis(self, mock_genai):
        """Test end-to-end analysis flow."""
        # Mock Gemini responses
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "category_name": "Market Risks",
            "overall_risk_level": "medium",
            "category_score": 5,
            "indicators": [
                {
                    "indicator": "TAM Size Assessment",
                    "risk_level": "medium",
                    "score": 5,
                    "description": "Test description",
                    "recommendation": "Test recommendation"
                }
            ],
            "summary": "Test summary"
        })
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        # Test data (unstructured text input)
        startup_data = (
            "Name: Test Startup\n"
            "Description: Test description in Technology industry at MVP stage.\n"
            "Highlights: Early traction and growing TAM."
        )
        
        # Run analysis
        scanner = ComprehensiveRiskScanner(api_key="test_key")
        result = scanner.comprehensive_startup_risk_analysis(startup_data)
        
        # Verify result structure
        assert "startup_name" in result
        assert "overall_risk_level" in result
        assert "overall_score" in result
        assert "risk_categories" in result
        assert "key_concerns" in result
        assert "investment_recommendation" in result
        assert "confidence_score" in result


if __name__ == "__main__":
    pytest.main([__file__])
