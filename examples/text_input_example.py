#!/usr/bin/env python3
"""
Example demonstrating text-based input for PitchLense MCP Package.

This example shows how to use the MCP tools with a single text string containing
all startup information instead of structured data.
"""
import sys
sys.path.append(r"/Users/amanulla/Downloads/pitchlense-mcp")


import os
import json
from datetime import datetime
from pitchlense_mcp import (
    CustomerRiskMCPTool,
    FinancialRiskMCPTool,
    MarketRiskMCPTool,
    TeamRiskMCPTool,
    OperationalRiskMCPTool,
    CompetitiveRiskMCPTool,
    ExitRiskMCPTool,
    LegalRiskMCPTool,
    ProductRiskMCPTool,
    PeerBenchmarkMCPTool,
    GeminiLLM
)
from pitchlense_mcp.core.mock_client import MockLLM

def main():
    """Main example function."""
    print("🚀 PitchLense MCP - Text Input Example")
    print("=" * 50)
    
    # Check for API key and use appropriate client
    use_mock = not os.getenv("GEMINI_API_KEY")
    if use_mock:
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   Using mock LLM client for demonstration purposes")
        print("   Set it with: export GEMINI_API_KEY='your_api_key_here' for real analysis")
        print()
    else:
        print("✅ GEMINI_API_KEY found, using real Gemini LLM client")
        print()
    
    # Example startup information as a single text string
    startup_info = """
    Company: TechFlow Solutions
    Industry: SaaS/Productivity Software
    Founded: 2022
    Location: San Francisco, CA
    Stage: Series A
    
    Business Model:
    TechFlow Solutions is a B2B SaaS company that provides workflow automation tools for small to medium businesses. The company offers a subscription-based platform that helps businesses streamline their operations through automated workflows, task management, and team collaboration features.
    
    Product:
    The main product is a cloud-based workflow automation platform that integrates with popular business tools like Slack, Google Workspace, and Microsoft 365. The platform allows users to create custom workflows, set up automated triggers, and manage team tasks efficiently.
    
    Financial Information:
    - Monthly Recurring Revenue (MRR): $45,000
    - Annual Recurring Revenue (ARR): $540,000
    - Customer Acquisition Cost (CAC): $180
    - Customer Lifetime Value (LTV): $2,400
    - LTV/CAC Ratio: 13.3
    - Monthly Burn Rate: $35,000
    - Runway: 8 months
    - Total Funding Raised: $2.5M (Series A)
    
    Traction & Customers:
    - Total Customers: 250 SMBs
    - Monthly Active Users: 1,200
    - Customer Churn Rate: 5% monthly
    - Net Revenue Retention: 110%
    - Average Contract Value: $180/month
    - Top customers include: Local Marketing Agency, Regional Law Firm, Mid-size Manufacturing Company
    
    Team:
    - CEO/Founder: Sarah Chen (ex-Google, 8 years product experience)
    - CTO/Co-founder: Michael Rodriguez (ex-Salesforce, 10 years engineering experience)
    - Head of Sales: Jennifer Park (ex-HubSpot, 6 years sales experience)
    - Total Team Size: 12 employees
    - Engineering Team: 5 developers
    - Sales Team: 3 people
    
    Market & Competition:
    - Total Addressable Market (TAM): $12B (workflow automation market)
    - Serviceable Addressable Market (SAM): $2.4B (SMB segment)
    - Direct Competitors: Zapier, Microsoft Power Automate, IFTTT
    - Competitive Advantage: Focus on SMB market, easier setup than enterprise solutions
    - Market Growth Rate: 15% annually
    
    Recent News & Updates:
    - Featured in TechCrunch for Series A funding announcement
    - Won "Best Productivity Tool" at SMB Tech Awards 2024
    - Partnership announced with Shopify for e-commerce workflow automation
    - Customer case study published showing 40% efficiency improvement for client
    
    Challenges & Risks:
    - High customer acquisition costs due to competitive market
    - Limited runway requiring additional funding within 8 months
    - Dependence on integrations with third-party platforms
    - Small team size limiting rapid scaling capabilities
    - No significant IP protection or patents filed
    
    Future Plans:
    - Expand to enterprise market segment
    - Develop AI-powered workflow recommendations
    - International expansion to European markets
    - Additional funding round planned for Q3 2024
    """
    
    # Initialize all MCP tools
    mcp_tools = {
        "Customer Risk Analysis": CustomerRiskMCPTool(),
        "Financial Risk Analysis": FinancialRiskMCPTool(),
        "Market Risk Analysis": MarketRiskMCPTool(),
        "Team Risk Analysis": TeamRiskMCPTool(),
        "Operational Risk Analysis": OperationalRiskMCPTool(),
        "Competitive Risk Analysis": CompetitiveRiskMCPTool(),
        "Exit Risk Analysis": ExitRiskMCPTool(),
        "Legal Risk Analysis": LegalRiskMCPTool(),
        "Product Risk Analysis": ProductRiskMCPTool(),
        "Peer Benchmarking": PeerBenchmarkMCPTool()
    }
    
    # Set up LLM client (mock or real)
    if use_mock:
        llm_client = MockLLM()
    else:
        llm_client = GeminiLLM()
    
    # Set the client for all tools
    for tool_name, tool in mcp_tools.items():
        tool.set_llm_client(llm_client)
    
    print("📊 Analyzing startup risks with text input...")
    print()
    
    # Dictionary to store all analysis results
    all_analysis_results = {}
    
    # Analyze with all MCP tools
    for analysis_name, tool in mcp_tools.items():
        print(f"🔍 {analysis_name}:")
        try:
            # Get the appropriate analysis method based on tool type
            if hasattr(tool, 'analyze_customer_risks'):
                result = tool.analyze_customer_risks(startup_info)
            elif hasattr(tool, 'analyze_financial_risks'):
                result = tool.analyze_financial_risks(startup_info)
            elif hasattr(tool, 'analyze_market_risks'):
                result = tool.analyze_market_risks(startup_info)
            elif hasattr(tool, 'analyze_team_risks'):
                result = tool.analyze_team_risks(startup_info)
            elif hasattr(tool, 'analyze_operational_risks'):
                result = tool.analyze_operational_risks(startup_info)
            elif hasattr(tool, 'analyze_competitive_risks'):
                result = tool.analyze_competitive_risks(startup_info)
            elif hasattr(tool, 'analyze_exit_risks'):
                result = tool.analyze_exit_risks(startup_info)
            elif hasattr(tool, 'analyze_legal_risks'):
                result = tool.analyze_legal_risks(startup_info)
            elif hasattr(tool, 'analyze_product_risks'):
                result = tool.analyze_product_risks(startup_info)
            else:
                print(f"   ❌ No analysis method found for {analysis_name}")
                continue
            
            # Store the result
            all_analysis_results[analysis_name] = result
            
            # Display summary
            print(f"   Overall Risk Level: {result.get('overall_risk_level', 'Unknown')}")
            print(f"   Category Score: {result.get('category_score', 'N/A')}/10")
            print(f"   Summary: {result.get('summary', 'No summary available')[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error in {analysis_name}: {e}")
            all_analysis_results[analysis_name] = {"error": str(e)}
        
        print()
    
    # Compute radar/spider chart data (normalized 0-10) from category scores
    radar_data = {}
    for name, result in all_analysis_results.items():
        if isinstance(result, dict) and "category_score" in result:
            radar_data[name] = result.get("category_score")

    # Create comprehensive results dictionary
    comprehensive_results = {
        "startup_analysis": {
            "company_name": "TechFlow Solutions",
            "analysis_timestamp": datetime.now().isoformat(),
            "llm_client_type": "mock" if use_mock else "gemini",
            "total_analyses": len(all_analysis_results),
            "analyses": all_analysis_results,
            "radar_chart": {
                "dimensions": list(radar_data.keys()),
                "scores": [radar_data[k] for k in radar_data.keys()],
                "scale": 10
            }
        }
    }
    
    # Save results to JSON file
    output_filename = f"startup_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
    
    print("✅ Comprehensive analysis completed!")
    print(f"📁 Results saved to: {output_filename}")
    print()
    print("💡 Key Benefits of Text Input:")
    print("   - Single string contains all startup information")
    print("   - No need for complex data structures")
    print("   - Easy to integrate with web scraping, document parsing")
    print("   - Flexible format that can include any type of information")
    print("   - Works well with Perplexity and other web research tools")
    print()
    print("📊 Analysis Summary:")
    for analysis_name, result in all_analysis_results.items():
        if "error" not in result:
            risk_level = result.get('overall_risk_level', 'Unknown')
            score = result.get('category_score', 'N/A')
            print(f"   {analysis_name}: {risk_level} ({score}/10)")
        else:
            print(f"   {analysis_name}: Error - {result['error']}")

if __name__ == "__main__":
    main()
