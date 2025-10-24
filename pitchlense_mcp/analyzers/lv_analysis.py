"""
LV-Analysis MCP Tool for detailed startup analysis based on hackathon requirements.
"""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from ..core.base import BaseMCPTool


class LVAnalysisAnalyzer:
    """Analyzer for LV-Analysis detailed startup analysis."""

    def __init__(self, llm_client=None, perplexity_tool=None):
        self.llm_client = llm_client
        self.perplexity_tool = perplexity_tool

    def analyze(self, startup_text: str) -> Dict[str, Any]:
        """
        Perform detailed LV-Analysis based on hackathon requirements.
        
        Args:
            startup_text: The startup description and details
            
        Returns:
            Detailed analysis in hackathon format
        """
        # Get additional market information using Perplexity
        market_info = self._get_market_research(startup_text)
        
        # Combine startup text with market research
        enhanced_context = f"""
        Startup Information:
        {startup_text}
        
        Market Research Data:
        {market_info}
        
        Please analyze this startup and provide a detailed business note in the following format:
        """
        
        prompt = self._build_analysis_prompt(enhanced_context)
        
        try:
            response = self.llm_client.predict(
                system_message="You are an expert startup business analyst specializing in detailed business note generation for investment evaluation. Maintain professional language and avoid inappropriate content. Focus strictly on business and investment analysis.",
                user_message=prompt
            )
            analysis_result = response.get("response", "")
            
            # Extract structured data from the response
            structured_analysis = self._extract_structured_data(analysis_result, startup_text, market_info)
            
            return structured_analysis
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "category_name": "LV-Analysis",
                "analysis_type": "detailed_business_note"
            }

    def _get_market_research(self, startup_text: str) -> str:
        """Get market research data using Perplexity."""
        if not self.perplexity_tool:
            return "Market research unavailable: Perplexity tool not provided"
            
        try:
            # Extract key terms for market research
            research_queries = [
                "Indian FMCG market size 2024 healthy food trends",
                "millet based products market India growth statistics",
                "clean label food brands India market analysis",
                "women led startups India FMCG sector trends",
                "B2B food distribution India market opportunities"
            ]
            
            market_data = []
            for query in research_queries:
                try:
                    result = self.perplexity_tool.search_perplexity(query)
                    if result and "answer" in result:
                        market_data.append(f"Query: {query}\nResult: {result['answer']}\n")
                except Exception as e:
                    print(f"Perplexity search failed for {query}: {e}")
                    continue
            
            return "\n".join(market_data)
            
        except Exception as e:
            return f"Market research unavailable: {str(e)}"

    def _build_analysis_prompt(self, context: str) -> str:
        """Build the analysis prompt for the LLM."""
        return f"""
        Based on the following startup information and market research, provide a detailed business analysis in the exact format specified below:

        {context}

        Please provide a comprehensive analysis covering:

        1. Industry and Market Size:
        - Industry Reports - Market Size, Others
        - Technology Reports - Food Innovation with AI, AI in Ops, AI in CPG

        2. Revenue Streams (for each stream include):
        - Name of the Revenue Stream
        - Description (What is it, How does it work)
        - Target Audience (Who is paying)
        - Percentage Contribution (Share of total revenue)

        3. Pricing Strategy:
        - Outline pricing models and tiers
        - Rationale behind pricing (market research, competitor analysis)

        4. Unit Economics:
        - Customer Acquisition Cost (CAC)
        - Lifetime Value (LTV)
        - LTV:CAC Ratio

        5. Recurring vs. One-Time Revenue:
        - Segregate revenue into recurring and one-time
        - Provide details for each

        6. Payment Flow and Terms:
        - How payments are collected and processed
        - Payment frequency
        - Refund and cancellation policies

        7. Scalability of Revenue Model:
        - How the revenue model will scale as business grows

        8. Additional Revenue Opportunities:
        - Future revenue streams to explore

        9. Competitor Analysis Framework:
        - Cover 2-3 competitors with details in table format:
          Category | Competitor 1 | Competitor 2 | Competitor 3
          Company Name, Headquarters, Founding Year, Total Funding, Business Model, Revenue Streams, Target Market, etc.

        10. Founders Profile:
        - Education, Work experience, Details of previously founded companies

        11. Financials:
        - MRR, ARR, Burn, Runway, Gross Margin, CM1%, CM2%, CM3%

        12. Facilities:
        - Office details, Plant details, Warehouses

        13. Technology:
        - Tech stack writeup

        14. Fundraiser:
        - Total funding details till date

        15. Valuation:
        - Valuation rationale

        16. Round Structure:
        - Terms, Pre-Money, Lead, Incoming Investors, Existing Investors

        17. Key Problem Solved:
        - Clear problem statement and solution

        18. Business Model:
        - Detailed business model explanation

        19. Pipeline:
        - Sales Pipeline Value
        - Projected Growth Opportunities

        20. Why Now:
        - Market Trends
        - Competitive Edge
        - Urgency/Opportunity

        21. Financials:
        - Funding Ask
        - Structure
        - Valuation Cap and Floor
        - Current Commitments

        22. Risks and Mitigation:
        - Identified Risks and Proposed Mitigation Strategies in table format

        Provide detailed, specific information for each section based on the startup data provided.
        """

    def _extract_structured_data(self, analysis_result: str, startup_text: str, market_info: str) -> Dict[str, Any]:
        """Extract and structure the analysis data."""
        return {
            "category_name": "LV-Analysis",
            "analysis_type": "detailed_business_note",
            "analysis_result": analysis_result,
            "startup_context": startup_text,
            "market_research": market_info,
            "sections": {
                "industry_market_size": self._extract_section(analysis_result, "Industry and Market Size"),
                "revenue_streams": self._extract_section(analysis_result, "Revenue Streams"),
                "pricing_strategy": self._extract_section(analysis_result, "Pricing Strategy"),
                "unit_economics": self._extract_section(analysis_result, "Unit Economics"),
                "recurring_vs_onetime": self._extract_section(analysis_result, "Recurring vs. One-Time Revenue"),
                "payment_flow": self._extract_section(analysis_result, "Payment Flow and Terms"),
                "scalability": self._extract_section(analysis_result, "Scalability of Revenue Model"),
                "additional_opportunities": self._extract_section(analysis_result, "Additional Revenue Opportunities"),
                "competitor_analysis": self._extract_section(analysis_result, "Competitor Analysis Framework"),
                "founders_profile": self._extract_section(analysis_result, "Founders Profile"),
                "financials": self._extract_section(analysis_result, "Financials"),
                "facilities": self._extract_section(analysis_result, "Facilities"),
                "technology": self._extract_section(analysis_result, "Technology"),
                "fundraiser": self._extract_section(analysis_result, "Fundraiser"),
                "valuation": self._extract_section(analysis_result, "Valuation"),
                "round_structure": self._extract_section(analysis_result, "Round Structure"),
                "key_problem": self._extract_section(analysis_result, "Key Problem Solved"),
                "business_model": self._extract_section(analysis_result, "Business Model"),
                "pipeline": self._extract_section(analysis_result, "Pipeline"),
                "why_now": self._extract_section(analysis_result, "Why Now"),
                "funding_ask": self._extract_section(analysis_result, "Funding Ask"),
                "risks_mitigation": self._extract_section(analysis_result, "Risks and Mitigation")
            }
        }

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the analysis text."""
        try:
            lines = text.split('\n')
            section_start = None
            section_end = None
            
            for i, line in enumerate(lines):
                if section_name.lower() in line.lower():
                    section_start = i
                    break
            
            if section_start is None:
                return f"Section '{section_name}' not found in analysis"
            
            # Find the next section or end of text
            for i in range(section_start + 1, len(lines)):
                if any(keyword in lines[i].lower() for keyword in [
                    "industry and market", "revenue streams", "pricing strategy", 
                    "unit economics", "recurring vs", "payment flow", "scalability",
                    "additional revenue", "competitor analysis", "founders profile",
                    "financials", "facilities", "technology", "fundraiser", "valuation",
                    "round structure", "key problem", "business model", "pipeline",
                    "why now", "funding ask", "risks and mitigation"
                ]) and i > section_start:
                    section_end = i
                    break
            
            if section_end is None:
                section_end = len(lines)
            
            return '\n'.join(lines[section_start:section_end]).strip()
            
        except Exception as e:
            return f"Error extracting section '{section_name}': {str(e)}"


