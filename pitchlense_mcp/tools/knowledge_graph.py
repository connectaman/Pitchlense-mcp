"""
Knowledge Graph MCP tool for building dependency graphs.

This tool builds a knowledge graph with:
- Root node: The company being analyzed (center)
- Left side nodes: Dependencies (what the company depends on)
- Right side nodes: Dependents (who/what depends on the company)

For each node, it fetches:
- Latest news
- Stock prices (when applicable)
- Export/Import rates for major markets (India, US, China)

Tools used:
- Perplexity for dependency analysis and market data
- SerpAPI for latest news URLs
- Gemini LLM to structure the final knowledge graph JSON
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.base import BaseMCPTool
from .perplexity_search import PerplexityMCPTool
from .serp_news import SerpNewsMCPTool
from ..core.gemini_client import GeminiLLM
from ..utils.json_extractor import extract_json_from_response


class KnowledgeGraphMCPTool(BaseMCPTool):
    """MCP tool to build a comprehensive knowledge graph for a startup.
    
    The knowledge graph structure:
    - Center: Company being analyzed
    - Left side: Dependencies (suppliers, technologies, resources)
    - Right side: Dependents (customers, industries, sectors)
    
    Each node includes:
    - Entity name and type
    - Dependency relationship
    - Latest news (URLs and summaries)
    - Stock prices (if applicable)
    - Export/Import data for India, US, China
    """

    def __init__(self):
        super().__init__(
            "Knowledge Graph Builder",
            "Build a comprehensive dependency knowledge graph for a startup with market data"
        )
        self.perplexity = PerplexityMCPTool()
        self.serp_news = SerpNewsMCPTool()
        self.llm_client = None

    def set_llm_client(self, llm_client):
        """Set the LLM client for knowledge graph generation."""
        self.llm_client = llm_client

    def _identify_dependencies(self, startup_text: str) -> Dict[str, Any]:
        """Identify what the company depends on (left side nodes).
        
        Args:
            startup_text: Description of the startup
            
        Returns:
            Dictionary with dependency information
        """
        dependency_prompt = f"""
        Analyze the following startup description and identify its key dependencies.
        
        Dependencies include:
        - Technology dependencies (e.g., AI companies depend on GPUs, cloud providers)
        - Resource dependencies (e.g., coffee shops depend on coffee bean suppliers)
        - Infrastructure dependencies (e.g., logistics, energy, raw materials)
        - Service dependencies (e.g., payment processors, hosting providers)
        
        For each dependency, identify:
        1. The specific entity/company (if known, e.g., "NVIDIA" for GPUs)
        2. The broader category (e.g., "GPU Manufacturers", "Coffee Bean Suppliers")
        3. The relationship type (e.g., "technology provider", "raw material supplier")
        
        Return your analysis as a structured list of 5-8 key dependencies.
        
        Startup Description:
        {startup_text}
        
        Provide your response in a clear, structured format.
        """
        
        result = self.perplexity.search_perplexity(dependency_prompt)
        return result

    def _identify_dependents(self, startup_text: str) -> Dict[str, Any]:
        """Identify who/what depends on the company (right side nodes).
        
        Args:
            startup_text: Description of the startup
            
        Returns:
            Dictionary with dependent information
        """
        dependent_prompt = f"""
        Analyze the following startup description and identify who or what depends on this company.
        
        Dependents include:
        - Direct customers (B2B companies, industries, sectors)
        - Industries that would benefit from this solution
        - Downstream sectors that rely on this product/service
        - Economic sectors impacted by this startup
        
        For each dependent, identify:
        1. The specific entity/company (if identifiable)
        2. The broader sector/industry (e.g., "Healthcare Industry", "E-commerce Sector")
        3. The dependency relationship (e.g., "uses product for X", "relies on service for Y")
        
        Return your analysis as a structured list of 5-8 potential dependents.
        
        Startup Description:
        {startup_text}
        
        Provide your response in a clear, structured format.
        """
        
        result = self.perplexity.search_perplexity(dependent_prompt)
        return result

    def _fetch_node_news(self, entity_name: str) -> List[Dict[str, Any]]:
        """Fetch news for a single entity (parallel-friendly)."""
        try:
            news_result = self.serp_news.fetch_google_news(entity_name, num_results=5)
            if not news_result.get("error"):
                return news_result.get("results", [])
        except Exception as e:
            print(f"Error fetching news for {entity_name}: {str(e)}")
        return []

    def _fetch_node_market_data(self, entity_name: str) -> Dict[str, Any]:
        """Fetch market data for a single entity (parallel-friendly)."""
        try:
            market_prompt = f"""
            Provide the following information about {entity_name}:
            
            1. Current stock price (if publicly traded)
            2. Stock ticker symbol (if applicable)
            3. 52-week high/low (if applicable)
            4. Export/Import data for India, US, and China (if it's a commodity or traded good)
            5. Market size and value
            
            Return the data in a structured format with clear labels.
            If {entity_name} is not a publicly traded company, state that clearly.
            If export/import data is not applicable, state that as well.
            """
            
            market_result = self.perplexity.search_perplexity(market_prompt)
            if not market_result.get("error"):
                return {
                    "market_info": market_result.get("answer", ""),
                    "market_sources": market_result.get("sources", [])
                }
        except Exception as e:
            print(f"Error fetching market data for {entity_name}: {str(e)}")
        
        return {"market_info": "", "market_sources": []}

    def _fetch_node_data(self, entity_name: str, entity_type: str, is_dependency: bool) -> Dict[str, Any]:
        """Fetch comprehensive data for a graph node.
        
        Args:
            entity_name: Name of the entity (company, sector, resource)
            entity_type: Type of entity (company, sector, technology, resource)
            is_dependency: True if this is a dependency node (left), False if dependent (right)
            
        Returns:
            Dictionary with news, stock data, and trade information
        """
        node_data = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "position": "left" if is_dependency else "right",
            "news": [],
            "stock_data": None,
            "trade_data": {
                "india": None,
                "us": None,
                "china": None
            }
        }
        
        # Fetch latest news and market data in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks simultaneously
            news_future = executor.submit(self._fetch_node_news, entity_name)
            market_future = executor.submit(self._fetch_node_market_data, entity_name)
            
            # Get results
            node_data["news"] = news_future.result()
            market_data = market_future.result()
            node_data.update(market_data)
        
        return node_data

    def _fetch_multiple_nodes_data(
        self, 
        entities_list: List[Dict[str, Any]], 
        is_dependency: bool,
        max_workers: int = 4
    ) -> List[Dict[str, Any]]:
        """Fetch data for multiple nodes in parallel.
        
        Args:
            entities_list: List of entity dictionaries
            is_dependency: True if these are dependency nodes
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of node data dictionaries
        """
        results = []
        
        def fetch_single_node(entity_info):
            """Wrapper function for parallel execution."""
            try:
                node_data = self._fetch_node_data(
                    entity_info["entity_name"],
                    entity_info["entity_type"],
                    is_dependency
                )
                node_data["relationship"] = entity_info.get("relationship", "")
                return node_data
            except Exception as e:
                print(f"Error processing entity {entity_info.get('entity_name', 'unknown')}: {str(e)}")
                return None
        
        # Use ThreadPoolExecutor for parallel data fetching
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_entity = {
                executor.submit(fetch_single_node, entity): entity 
                for entity in entities_list
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_entity):
                result = future.result()
                if result is not None:
                    results.append(result)
        
        return results

    def _build_knowledge_graph_json(
        self, 
        company_name: str,
        company_description: str,
        dependencies_data: List[Dict[str, Any]],
        dependents_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use Gemini LLM to structure the final knowledge graph JSON.
        
        Args:
            company_name: Name of the company at the center
            company_description: Description of the company
            dependencies_data: List of dependency nodes with their data
            dependents_data: List of dependent nodes with their data
            
        Returns:
            Structured knowledge graph JSON
        """
        if not self.llm_client or not isinstance(self.llm_client, GeminiLLM):
            # Fallback: return raw structure without LLM processing
            return {
                "root": {
                    "name": company_name,
                    "description": company_description,
                    "type": "company"
                },
                "dependencies": dependencies_data,
                "dependents": dependents_data,
                "metadata": {
                    "total_dependencies": len(dependencies_data),
                    "total_dependents": len(dependents_data),
                    "llm_processed": False
                }
            }
        
        system_prompt = """
        You are a knowledge graph expert. Structure the provided dependency data into a clean JSON format.
        
        The JSON should follow this structure:
        {
          "root": {
            "id": "company_root",
            "name": "Company Name",
            "type": "company",
            "description": "Brief description",
            "position": {"x": 0, "y": 0}
          },
          "nodes": [
            {
              "id": "node_1",
              "name": "Node Name",
              "type": "dependency|dependent",
              "category": "technology|resource|sector|company",
              "position": {"x": -1, "y": 0},  // left for dependencies, right for dependents
              "relationship": "description of relationship",
              "news": [{"title": "", "link": "", "date": "", "source": ""}],
              "market_data": {
                "stock_ticker": "NVDA",
                "stock_price": "$XXX",
                "market_info": "...",
                "trade_data": {
                  "india": "...",
                  "us": "...",
                  "china": "..."
                }
              },
              "hover_info": "Summary to show on hover"
            }
          ],
          "edges": [
            {
              "from": "company_root",
              "to": "node_1",
              "relationship": "depends on",
              "strength": 0.8
            }
          ]
        }
        
        Respond ONLY with valid JSON wrapped in <JSON></JSON> tags.
        """
        
        user_prompt = f"""
        Build a knowledge graph for the following company and its dependencies/dependents.
        
        Company: {company_name}
        Description: {company_description}
        
        Dependencies (what the company depends on):
        {dependencies_data}
        
        Dependents (who/what depends on the company):
        {dependents_data}
        
        Create a complete knowledge graph JSON with proper node positioning:
        - Root node at center (x: 0, y: 0)
        - Dependencies on the left side (x: -1 to -3, varying y)
        - Dependents on the right side (x: 1 to 3, varying y)
        
        Include all available data for each node.
        """
        
        try:
            llm_response = self.llm_client.predict(
                system_message=system_prompt,
                user_message=user_prompt
            )
            
            response_text = llm_response.get("response", "")
            knowledge_graph = extract_json_from_response(response_text)
            
            if isinstance(knowledge_graph, dict):
                knowledge_graph["metadata"] = {
                    "llm_processed": True,
                    "model": self.llm_client.model
                }
                return knowledge_graph
        except Exception as e:
            print(f"Error in LLM processing: {str(e)}")
        
        # Fallback if LLM processing fails
        return {
            "root": {
                "name": company_name,
                "description": company_description,
                "type": "company"
            },
            "dependencies": dependencies_data,
            "dependents": dependents_data,
            "metadata": {
                "total_dependencies": len(dependencies_data),
                "total_dependents": len(dependents_data),
                "llm_processed": False
            }
        }

    def generate_knowledge_graph(
        self, 
        startup_text: str,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete knowledge graph for a startup.
        
        Args:
            startup_text: Complete description of the startup
            company_name: Optional company name (extracted if not provided)
            
        Returns:
            Complete knowledge graph with dependencies, dependents, and market data
        """
        try:
            # Extract company name if not provided
            if not company_name:
                print("[KG] Extracting company name...")
                extract_prompt = f"""
                Extract the company name from this startup description. 
                Respond with ONLY the company name, nothing else.
                
                {startup_text[:500]}
                """
                name_result = self.perplexity.search_perplexity(extract_prompt)
                company_name = name_result.get("answer", "Unknown Company").strip()
            
            print(f"[KG] Building knowledge graph for: {company_name}")
            
            # PARALLEL: Identify dependencies and dependents simultaneously
            print("[KG] Identifying dependencies and dependents in parallel...")
            
            def identify_deps_and_deps():
                """Run dependency and dependent identification in parallel."""
                with ThreadPoolExecutor(max_workers=2) as executor:
                    # Submit both Perplexity calls simultaneously
                    deps_future = executor.submit(self._identify_dependencies, startup_text)
                    depes_future = executor.submit(self._identify_dependents, startup_text)
                    
                    # Get results
                    dependencies_raw = deps_future.result()
                    dependents_raw = depes_future.result()
                    
                    return dependencies_raw, dependents_raw
            
            dependencies_raw, dependents_raw = identify_deps_and_deps()
            
            # PARALLEL: Parse both dependency and dependent analyses
            print("[KG] Parsing entities in parallel...")
            
            def parse_entities_parallel():
                """Parse dependency and dependent entities in parallel."""
                if self.llm_client and isinstance(self.llm_client, GeminiLLM):
                    # Use LLM for parsing both in parallel
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        deps_future = executor.submit(
                            self._parse_entities_from_perplexity,
                            dependencies_raw.get("answer", ""),
                            True
                        )
                        depes_future = executor.submit(
                            self._parse_entities_from_perplexity,
                            dependents_raw.get("answer", ""),
                            False
                        )
                        
                        dependencies_list = deps_future.result()
                        dependents_list = depes_future.result()
                        
                        return dependencies_list, dependents_list
                else:
                    # Fallback: return empty lists if no LLM client
                    return [], []
            
            dependencies_list, dependents_list = parse_entities_parallel()
            
            # PARALLEL: Fetch data for all nodes simultaneously
            total_nodes = len(dependencies_list) + len(dependents_list)
            if total_nodes > 0:
                print(f"[KG] Fetching data for {len(dependencies_list)} dependencies and {len(dependents_list)} dependents in parallel...")
                
                def fetch_all_node_data():
                    """Fetch data for all nodes in parallel."""
                    max_workers = min(8, max(2, total_nodes))  # Adaptive worker count
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # Submit all dependency and dependent fetching tasks
                        futures = []
                        
                        # Dependencies
                        for dep in dependencies_list:
                            future = executor.submit(self._fetch_node_data, dep["entity_name"], dep["entity_type"], True)
                            futures.append((future, dep, True))
                        
                        # Dependents  
                        for dept in dependents_list:
                            future = executor.submit(self._fetch_node_data, dept["entity_name"], dept["entity_type"], False)
                            futures.append((future, dept, False))
                        
                        # Collect results
                        dependencies_data = []
                        dependents_data = []
                        
                        for future, entity_info, is_dependency in futures:
                            try:
                                node_data = future.result()
                                node_data["relationship"] = entity_info.get("relationship", "")
                                
                                if is_dependency:
                                    dependencies_data.append(node_data)
                                else:
                                    dependents_data.append(node_data)
                            except Exception as e:
                                print(f"Error fetching data for {entity_info.get('entity_name', 'unknown')}: {str(e)}")
                    
                    return dependencies_data, dependents_data
            
                dependencies_data, dependents_data = fetch_all_node_data()
            else:
                dependencies_data, dependents_data = [], []
            
            # Build final knowledge graph using Gemini
            print("[KG] Structuring knowledge graph with Gemini...")
            knowledge_graph = self._build_knowledge_graph_json(
                company_name,
                startup_text[:300],  # Brief description
                dependencies_data,
                dependents_data
            )
            
            print(f"[KG] Knowledge graph complete! {len(dependencies_data)} dependencies, {len(dependents_data)} dependents")
            return knowledge_graph
            
        except Exception as e:
            print(f"[KG] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_error_response(f"Knowledge graph generation error: {str(e)}")

    def _parse_entities_from_perplexity(
        self, 
        perplexity_answer: str,
        is_dependency: bool
    ) -> List[Dict[str, Any]]:
        """Parse entity information from Perplexity's answer.
        
        Args:
            perplexity_answer: Raw answer from Perplexity
            is_dependency: Whether these are dependencies or dependents
            
        Returns:
            List of parsed entities with name, type, and relationship
        """
        # Use Gemini to parse the unstructured text into structured entities
        if not self.llm_client or not isinstance(self.llm_client, GeminiLLM):
            # Fallback: basic parsing
            return []
        
        parse_prompt = f"""
        Parse the following text and extract entity information.
        
        For each entity mentioned, extract:
        1. entity_name: The specific name (e.g., "NVIDIA", "Coffee Bean Suppliers")
        2. entity_type: Category (e.g., "company", "sector", "technology", "resource")
        3. relationship: How it relates to the main company
        
        Text to parse:
        {perplexity_answer}
        
        Return ONLY valid JSON in this format wrapped in <JSON></JSON> tags:
        [
          {{
            "entity_name": "Name",
            "entity_type": "type",
            "relationship": "relationship description"
          }}
        ]
        """
        
        try:
            result = self.llm_client.predict(
                system_message="You are a data extraction expert. Extract structured data from text and return only valid JSON.",
                user_message=parse_prompt
            )
            
            entities = extract_json_from_response(result.get("response", ""))
            if isinstance(entities, list):
                return entities[:8]  # Limit to 8 entities per side
        except Exception as e:
            print(f"Error parsing entities: {str(e)}")
        
        return []

    def register_tools(self):
        """Register the knowledge graph tool."""
        self.register_tool(self.generate_knowledge_graph)

