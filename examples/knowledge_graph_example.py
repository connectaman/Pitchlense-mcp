"""
Knowledge Graph Generation Example

This example demonstrates how to build a comprehensive dependency knowledge graph
for a startup, including:
- Center node: The company
- Left side: Dependencies (what the company depends on)
- Right side: Dependents (who/what depends on the company)

For each node, the tool fetches:
- Latest news
- Stock prices (if applicable)
- Export/Import data for major markets (India, US, China)
"""

import os
import json
from pitchlense_mcp import KnowledgeGraphMCPTool, GeminiLLM

# Sample startup descriptions for different industries

AI_COMPANY_EXAMPLE = """
NeuralTech AI is a cutting-edge artificial intelligence startup developing 
large language models for enterprise applications. The company leverages 
NVIDIA's latest H100 GPUs for training and inference, hosted on AWS cloud 
infrastructure. Their proprietary LLM helps Fortune 500 companies automate 
customer service, content generation, and data analysis.

The company's technology stack includes:
- GPU Computing: NVIDIA H100 GPUs
- Cloud Infrastructure: AWS (Amazon Web Services)
- Training Data: Web scraping and licensed datasets
- Model Architecture: Transformer-based neural networks

Key customers include healthcare providers, financial institutions, and 
e-commerce platforms who use the AI for various automation tasks.

Funding: $50M Series B
Team: 75 employees
Location: San Francisco, CA
"""

COFFEE_STARTUP_EXAMPLE = """
BrewCraft is a premium coffee chain startup that sources specialty coffee 
beans directly from farmers in Ethiopia, Colombia, and Brazil. The company 
operates 25 locations across major US cities and plans to expand to 100 
stores by 2026.

Supply Chain:
- Coffee Beans: Direct relationships with coffee farmers in Ethiopia, Colombia, Brazil
- Roasting Equipment: Probat roasting machines (Germany)
- Packaging: Biodegradable packaging from EcoPack Solutions
- Milk Supply: Local dairy cooperatives
- Payment Processing: Square POS systems

The company's sustainability model includes fair-trade pricing, carbon-neutral 
shipping, and investment in farmer education programs. Their customer base 
includes urban professionals, remote workers, and coffee enthusiasts.

Export/Import considerations:
- Coffee beans imported from origin countries (subject to agricultural tariffs)
- Roasting equipment imported from Europe
- Dependent on global coffee commodity prices

Funding: $15M Series A
Team: 120 employees (including baristas)
Location: Seattle, WA
"""

FINTECH_EXAMPLE = """
PayFlow is a fintech startup providing B2B payment solutions for small and 
medium businesses. The platform enables instant payments, automated invoicing, 
and working capital financing.

Technology Stack:
- Payment Processing: Stripe API integration
- Banking Infrastructure: Plaid for bank connections
- Cloud Services: Google Cloud Platform
- Security: Auth0 for authentication
- Data Analytics: Snowflake data warehouse

The company serves over 10,000 SMBs across retail, restaurants, professional 
services, and logistics sectors. Their payment rails connect to major banks 
like Chase, Bank of America, and Wells Fargo.

Key Dependencies:
- Payment processors (Stripe, Plaid)
- Banking partners for liquidity
- Regulatory compliance (FinCEN, state regulators)

Industries that benefit:
- Retail sector (faster checkout)
- Restaurant chains (simplified payments)
- B2B suppliers (improved cash flow)

Funding: $30M Series B
Team: 90 employees
Location: New York, NY
"""


def generate_knowledge_graph(startup_text: str, company_name: str):
    """Generate a knowledge graph for a startup.
    
    Args:
        startup_text: Description of the startup
        company_name: Name of the company
        
    Returns:
        Knowledge graph JSON structure
    """
    # Initialize the tool
    kg_tool = KnowledgeGraphMCPTool()
    
    # Set up Gemini LLM client (requires GEMINI_API_KEY env var)
    try:
        llm_client = GeminiLLM()
        kg_tool.set_llm_client(llm_client)
        print(f"✓ Gemini LLM client initialized")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize Gemini LLM: {str(e)}")
        print("  Continuing with basic functionality...")
    
    # Generate the knowledge graph
    print(f"\n{'='*70}")
    print(f"Generating Knowledge Graph for: {company_name}")
    print(f"{'='*70}\n")
    
    try:
        result = kg_tool.generate_knowledge_graph(
            startup_text=startup_text,
            company_name=company_name
        )
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return None
        
        print(f"✓ Knowledge graph generated successfully!\n")
        
        # Display summary
        if "metadata" in result:
            metadata = result["metadata"]
            print(f"Summary:")
            print(f"  - Dependencies: {metadata.get('total_dependencies', 0)}")
            print(f"  - Dependents: {metadata.get('total_dependents', 0)}")
            print(f"  - LLM Processed: {metadata.get('llm_processed', False)}")
        
        # Display some nodes
        if "nodes" in result:
            print(f"\n{'='*70}")
            print(f"Sample Nodes:")
            print(f"{'='*70}")
            for i, node in enumerate(result["nodes"][:5], 1):
                print(f"\n{i}. {node.get('name', 'Unknown')}")
                print(f"   Type: {node.get('type', 'N/A')}")
                print(f"   Category: {node.get('category', 'N/A')}")
                print(f"   Relationship: {node.get('relationship', 'N/A')}")
                if node.get('news'):
                    print(f"   News Articles: {len(node.get('news', []))}")
        
        return result
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run knowledge graph generation examples."""
    
    # Check for required API keys
    required_keys = ["GEMINI_API_KEY", "PERPLEXITY_API_KEY", "SERPAPI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("⚠ Warning: Missing API keys:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\nSome features may not work. Set these environment variables to enable full functionality.\n")
    else:
        print("✓ All API keys found\n")
    
    # Choose an example
    examples = {
        "1": ("AI Company", AI_COMPANY_EXAMPLE, "NeuralTech AI"),
        "2": ("Coffee Startup", COFFEE_STARTUP_EXAMPLE, "BrewCraft"),
        "3": ("Fintech", FINTECH_EXAMPLE, "PayFlow"),
    }
    
    print("Select an example:")
    for key, (name, _, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nEnter choice (1-3) or press Enter for AI Company: ").strip() or "1"
    
    if choice not in examples:
        print("Invalid choice, using AI Company example")
        choice = "1"
    
    example_name, startup_text, company_name = examples[choice]
    print(f"\n{'='*70}")
    print(f"Selected: {example_name} ({company_name})")
    print(f"{'='*70}\n")
    
    # Generate knowledge graph
    result = generate_knowledge_graph(startup_text, company_name)
    
    if result:
        # Save to file
        output_file = f"knowledge_graph_{company_name.lower().replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Full knowledge graph saved to: {output_file}")
        
        # Display visualization instructions
        print(f"\n{'='*70}")
        print("Visualization Instructions:")
        print(f"{'='*70}")
        print("""
To visualize this knowledge graph:

1. Frontend Implementation (React/Vue/Angular):
   - Use D3.js or vis.js for graph rendering
   - Position nodes based on x, y coordinates
   - Add hover tooltips showing news and market data
   
2. Key Features to Implement:
   - Center node (root): Company
   - Left side nodes: Dependencies (x < 0)
   - Right side nodes: Dependents (x > 0)
   - Hover effects: Show news, stock prices, trade data
   - Clickable nodes: Expand to see more details
   
3. Sample D3.js structure:
   ```javascript
   const nodes = knowledgeGraph.nodes;
   const edges = knowledgeGraph.edges;
   
   // Create force-directed graph
   const simulation = d3.forceSimulation(nodes)
     .force("link", d3.forceLink(edges))
     .force("charge", d3.forceManyBody())
     .force("center", d3.forceCenter(width/2, height/2));
   ```

4. Hover Info Display:
   - Show dependency relationship
   - Latest news headlines with links
   - Stock ticker and current price
   - Export/Import data for India, US, China
        """)


if __name__ == "__main__":
    main()

