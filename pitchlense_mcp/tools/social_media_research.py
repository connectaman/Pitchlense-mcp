"""
Social Media Research Tool for PitchLense MCP Package.

This tool uses Perplexity API to gather social media data, complaints, reviews,
and sentiment analysis for startups, founders, and products.
"""

import os
from typing import Dict, Any, List, Optional
from ..core.base import BaseMCPTool
from .perplexity_search import PerplexityMCPTool


class SocialMediaResearchMCPTool(BaseMCPTool):
    """
    Social Media Research tool for gathering social coverage data.
    
    Uses Perplexity API to search for social media mentions, complaints,
    reviews, and sentiment analysis for startups and founders.
    """
    
    def __init__(self):
        """Initialize the Social Media Research tool."""
        super().__init__(
            tool_name="Social Media Research",
            description="Research social media coverage, complaints, reviews, and sentiment for startups and founders"
        )
        self.perplexity = PerplexityMCPTool()
    
    def research_social_coverage(self, company_name: str, founder_names: List[str] = None) -> Dict[str, Any]:
        """
        Research social media coverage for a company and its founders.
        
        Args:
            company_name: Name of the startup company
            founder_names: List of founder names to research
            
        Returns:
            Comprehensive social media coverage data
        """
        try:
            print(f"[SocialMedia] Researching social coverage for: {company_name}")
            
            # Research company social media presence
            company_data = self._research_company_social_media(company_name)
            
            # Research founder social media presence
            founder_data = {}
            if founder_names:
                for founder in founder_names:
                    founder_data[founder] = self._research_founder_social_media(founder)
            
            # Research product reviews and complaints
            product_data = self._research_product_reviews(company_name)
            
            # Research social media sentiment
            sentiment_data = self._research_social_sentiment(company_name)
            
            return {
                "company_name": company_name,
                "company_social_media": company_data,
                "founder_social_media": founder_data,
                "product_reviews": product_data,
                "social_sentiment": sentiment_data,
                "research_timestamp": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            print(f"[SocialMedia] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_error_response(f"Social media research error: {str(e)}")
    
    def _research_company_social_media(self, company_name: str) -> Dict[str, Any]:
        """Research company's social media presence and mentions."""
        try:
            # Search for company social media mentions
            mentions_query = f"'{company_name}' social media mentions Twitter LinkedIn Facebook Reddit complaints reviews"
            mentions_result = self.perplexity.search_perplexity(mentions_query)
            
            # Search for company reputation and reviews
            reputation_query = f"'{company_name}' company reputation reviews Trustpilot Google Reviews Yelp complaints"
            reputation_result = self.perplexity.search_perplexity(reputation_query)
            
            # Search for company news and press coverage
            news_query = f"'{company_name}' news coverage press articles media mentions"
            news_result = self.perplexity.search_perplexity(news_query)
            
            return {
                "social_mentions": mentions_result.get("answer", ""),
                "reputation_data": reputation_result.get("answer", ""),
                "news_coverage": news_result.get("answer", ""),
                "sources": {
                    "mentions_sources": mentions_result.get("sources", []),
                    "reputation_sources": reputation_result.get("sources", []),
                    "news_sources": news_result.get("sources", [])
                }
            }
            
        except Exception as e:
            print(f"[SocialMedia] Error researching company social media: {str(e)}")
            return {"error": str(e)}
    
    def _research_founder_social_media(self, founder_name: str) -> Dict[str, Any]:
        """Research founder's social media presence and reputation."""
        try:
            # Search for founder social media presence
            social_query = f"'{founder_name}' LinkedIn Twitter social media profile reputation"
            social_result = self.perplexity.search_perplexity(social_query)
            
            # Search for founder controversies or negative mentions
            controversy_query = f"'{founder_name}' controversies negative mentions complaints social media"
            controversy_result = self.perplexity.search_perplexity(controversy_query)
            
            # Search for founder achievements and positive mentions
            achievements_query = f"'{founder_name}' achievements accomplishments positive mentions"
            achievements_result = self.perplexity.search_perplexity(achievements_query)
            
            return {
                "social_presence": social_result.get("answer", ""),
                "controversies": controversy_result.get("answer", ""),
                "achievements": achievements_result.get("answer", ""),
                "sources": {
                    "social_sources": social_result.get("sources", []),
                    "controversy_sources": controversy_result.get("sources", []),
                    "achievement_sources": achievements_result.get("sources", [])
                }
            }
            
        except Exception as e:
            print(f"[SocialMedia] Error researching founder social media: {str(e)}")
            return {"error": str(e)}
    
    def _research_product_reviews(self, company_name: str) -> Dict[str, Any]:
        """Research product reviews and customer feedback."""
        try:
            # Search for product reviews
            reviews_query = f"'{company_name}' product reviews customer feedback ratings complaints"
            reviews_result = self.perplexity.search_perplexity(reviews_query)
            
            # Search for customer service issues
            service_query = f"'{company_name}' customer service issues complaints support problems"
            service_result = self.perplexity.search_perplexity(service_query)
            
            # Search for product quality issues
            quality_query = f"'{company_name}' product quality issues defects problems recalls"
            quality_result = self.perplexity.search_perplexity(quality_query)
            
            return {
                "product_reviews": reviews_result.get("answer", ""),
                "customer_service": service_result.get("answer", ""),
                "product_quality": quality_result.get("answer", ""),
                "sources": {
                    "reviews_sources": reviews_result.get("sources", []),
                    "service_sources": service_result.get("sources", []),
                    "quality_sources": quality_result.get("sources", [])
                }
            }
            
        except Exception as e:
            print(f"[SocialMedia] Error researching product reviews: {str(e)}")
            return {"error": str(e)}
    
    def _research_social_sentiment(self, company_name: str) -> Dict[str, Any]:
        """Research overall social media sentiment."""
        try:
            # Search for positive sentiment
            positive_query = f"'{company_name}' positive reviews success stories customer satisfaction"
            positive_result = self.perplexity.search_perplexity(positive_query)
            
            # Search for negative sentiment
            negative_query = f"'{company_name}' negative reviews complaints problems issues"
            negative_result = self.perplexity.search_perplexity(negative_query)
            
            # Search for social media crisis or viral content
            crisis_query = f"'{company_name}' social media crisis viral negative content backlash"
            crisis_result = self.perplexity.search_perplexity(crisis_query)
            
            return {
                "positive_sentiment": positive_result.get("answer", ""),
                "negative_sentiment": negative_result.get("answer", ""),
                "crisis_mentions": crisis_result.get("answer", ""),
                "sources": {
                    "positive_sources": positive_result.get("sources", []),
                    "negative_sources": negative_result.get("sources", []),
                    "crisis_sources": crisis_result.get("sources", [])
                }
            }
            
        except Exception as e:
            print(f"[SocialMedia] Error researching social sentiment: {str(e)}")
            return {"error": str(e)}
    
    def register_tools(self):
        """Register the social media research tools."""
        self.register_tool(self.research_social_coverage)
