"""
Tests for Knowledge Graph MCP Tool
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pitchlense_mcp.tools.knowledge_graph import KnowledgeGraphMCPTool


class TestKnowledgeGraphMCPTool:
    """Test suite for KnowledgeGraphMCPTool"""
    
    def test_initialization(self):
        """Test that the tool initializes correctly"""
        tool = KnowledgeGraphMCPTool()
        assert tool.name == "Knowledge Graph Builder"
        assert tool.description == "Build a comprehensive dependency knowledge graph for a startup with market data"
        assert tool.perplexity is not None
        assert tool.serp_news is not None
    
    def test_set_llm_client(self):
        """Test setting LLM client"""
        tool = KnowledgeGraphMCPTool()
        mock_llm = Mock()
        tool.set_llm_client(mock_llm)
        assert tool.llm_client == mock_llm
    
    @patch('pitchlense_mcp.tools.knowledge_graph.PerplexityMCPTool')
    def test_identify_dependencies(self, mock_perplexity_class):
        """Test dependency identification"""
        tool = KnowledgeGraphMCPTool()
        
        # Mock Perplexity response
        mock_perplexity = Mock()
        mock_perplexity.search_perplexity.return_value = {
            "answer": "Dependencies: NVIDIA (GPU), AWS (Cloud Infrastructure)",
            "sources": []
        }
        tool.perplexity = mock_perplexity
        
        startup_text = "AI company using GPUs for training"
        result = tool._identify_dependencies(startup_text)
        
        assert "answer" in result
        assert "NVIDIA" in result["answer"] or "GPU" in result["answer"]
    
    @patch('pitchlense_mcp.tools.knowledge_graph.PerplexityMCPTool')
    def test_identify_dependents(self, mock_perplexity_class):
        """Test dependent identification"""
        tool = KnowledgeGraphMCPTool()
        
        # Mock Perplexity response
        mock_perplexity = Mock()
        mock_perplexity.search_perplexity.return_value = {
            "answer": "Dependents: Healthcare Industry, Finance Sector",
            "sources": []
        }
        tool.perplexity = mock_perplexity
        
        startup_text = "AI company providing ML solutions"
        result = tool._identify_dependents(startup_text)
        
        assert "answer" in result
        assert "Healthcare" in result["answer"] or "Finance" in result["answer"]
    
    @patch('pitchlense_mcp.tools.knowledge_graph.SerpNewsMCPTool')
    @patch('pitchlense_mcp.tools.knowledge_graph.PerplexityMCPTool')
    def test_fetch_node_data(self, mock_perplexity_class, mock_serp_class):
        """Test fetching node data"""
        tool = KnowledgeGraphMCPTool()
        
        # Mock SERP news response
        mock_serp = Mock()
        mock_serp.fetch_google_news.return_value = {
            "results": [
                {
                    "title": "NVIDIA Q3 Earnings",
                    "link": "https://example.com",
                    "source": "Reuters",
                    "date": "2024-10-14"
                }
            ]
        }
        tool.serp_news = mock_serp
        
        # Mock Perplexity response
        mock_perplexity = Mock()
        mock_perplexity.search_perplexity.return_value = {
            "answer": "Stock price: $450.25, Ticker: NVDA",
            "sources": []
        }
        tool.perplexity = mock_perplexity
        
        result = tool._fetch_node_data("NVIDIA", "company", is_dependency=True)
        
        assert result["entity_name"] == "NVIDIA"
        assert result["entity_type"] == "company"
        assert result["position"] == "left"
        assert len(result["news"]) > 0
        assert "market_info" in result
    
    def test_parse_entities_from_perplexity_no_llm(self):
        """Test parsing entities without LLM client"""
        tool = KnowledgeGraphMCPTool()
        tool.llm_client = None
        
        perplexity_answer = "Dependencies include NVIDIA for GPUs and AWS for cloud"
        result = tool._parse_entities_from_perplexity(perplexity_answer, is_dependency=True)
        
        # Should return empty list when no LLM client
        assert isinstance(result, list)
    
    @patch('pitchlense_mcp.tools.knowledge_graph.GeminiLLM')
    def test_parse_entities_from_perplexity_with_llm(self, mock_gemini_class):
        """Test parsing entities with LLM client"""
        tool = KnowledgeGraphMCPTool()
        
        # Mock LLM client
        mock_llm = Mock()
        mock_llm.predict.return_value = {
            "response": """
            <JSON>
            [
              {
                "entity_name": "NVIDIA",
                "entity_type": "company",
                "relationship": "provides GPU infrastructure"
              }
            ]
            </JSON>
            """
        }
        tool.llm_client = mock_llm
        
        perplexity_answer = "Dependencies include NVIDIA for GPUs"
        result = tool._parse_entities_from_perplexity(perplexity_answer, is_dependency=True)
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert "entity_name" in result[0]
    
    def test_build_knowledge_graph_json_no_llm(self):
        """Test building knowledge graph without LLM (fallback)"""
        tool = KnowledgeGraphMCPTool()
        tool.llm_client = None
        
        dependencies = [{"entity_name": "NVIDIA", "entity_type": "company"}]
        dependents = [{"entity_name": "Healthcare", "entity_type": "sector"}]
        
        result = tool._build_knowledge_graph_json(
            "TestCo",
            "A test company",
            dependencies,
            dependents
        )
        
        assert "root" in result
        assert result["root"]["name"] == "TestCo"
        assert "dependencies" in result
        assert "dependents" in result
        assert result["metadata"]["llm_processed"] == False
    
    @patch('pitchlense_mcp.tools.knowledge_graph.GeminiLLM')
    def test_build_knowledge_graph_json_with_llm(self, mock_gemini_class):
        """Test building knowledge graph with LLM"""
        tool = KnowledgeGraphMCPTool()
        
        # Mock LLM client
        mock_llm = MagicMock()
        mock_llm.model = "gemini-2.5-flash"
        mock_llm.predict.return_value = {
            "response": """
            <JSON>
            {
              "root": {
                "id": "company_root",
                "name": "TestCo",
                "type": "company"
              },
              "nodes": [
                {
                  "id": "node_1",
                  "name": "NVIDIA",
                  "type": "dependency"
                }
              ],
              "edges": []
            }
            </JSON>
            """
        }
        tool.llm_client = mock_llm
        
        # Check if it's a GeminiLLM instance (mock it)
        from pitchlense_mcp.core.gemini_client import GeminiLLM
        mock_llm.__class__ = GeminiLLM
        
        dependencies = [{"entity_name": "NVIDIA", "entity_type": "company"}]
        dependents = [{"entity_name": "Healthcare", "entity_type": "sector"}]
        
        result = tool._build_knowledge_graph_json(
            "TestCo",
            "A test company",
            dependencies,
            dependents
        )
        
        assert "root" in result
        assert result["metadata"]["llm_processed"] == True
    
    @patch('pitchlense_mcp.tools.knowledge_graph.PerplexityMCPTool')
    @patch('pitchlense_mcp.tools.knowledge_graph.SerpNewsMCPTool')
    def test_generate_knowledge_graph_full_flow(self, mock_serp_class, mock_perplexity_class):
        """Test full knowledge graph generation flow"""
        tool = KnowledgeGraphMCPTool()
        
        # Mock Perplexity for company name extraction
        mock_perplexity = Mock()
        mock_perplexity.search_perplexity.return_value = {
            "answer": "TestCo",
            "sources": []
        }
        tool.perplexity = mock_perplexity
        
        # Mock SERP news
        mock_serp = Mock()
        mock_serp.fetch_google_news.return_value = {"results": []}
        tool.serp_news = mock_serp
        
        # Mock LLM to return empty list for entity parsing
        mock_llm = Mock()
        mock_llm.predict.return_value = {"response": "<JSON>[]</JSON>"}
        tool.llm_client = mock_llm
        
        startup_text = "TestCo is an AI company"
        result = tool.generate_knowledge_graph(startup_text)
        
        # Should not have an error
        assert "error" not in result or result.get("error") is None
        assert "root" in result or "metadata" in result
    
    def test_generate_knowledge_graph_with_error(self):
        """Test knowledge graph generation with error handling"""
        tool = KnowledgeGraphMCPTool()
        
        # Force an error by passing None
        result = tool.generate_knowledge_graph(None)
        
        # Should return error response
        assert "error" in result
    
    def test_register_tools(self):
        """Test tool registration"""
        tool = KnowledgeGraphMCPTool()
        
        # Call register_tools (should not raise)
        try:
            tool.register_tools()
        except Exception as e:
            pytest.fail(f"register_tools raised {e}")


class TestKnowledgeGraphIntegration:
    """Integration tests for knowledge graph in cloud function"""
    
    def test_import_in_cloud_function(self):
        """Test that knowledge graph tool can be imported in cloud function"""
        try:
            from pitchlense_mcp import KnowledgeGraphMCPTool
            assert KnowledgeGraphMCPTool is not None
        except ImportError as e:
            pytest.fail(f"Failed to import KnowledgeGraphMCPTool: {e}")
    
    def test_knowledge_graph_in_package_exports(self):
        """Test that knowledge graph is exported from package"""
        import pitchlense_mcp
        assert hasattr(pitchlense_mcp, 'KnowledgeGraphMCPTool')
        assert 'KnowledgeGraphMCPTool' in pitchlense_mcp.__all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

