"""
Test script for cloud function with knowledge graph generation

IMPORTANT: Set your API keys as environment variables before running this script:

Windows:
set GEMINI_API_KEY=your_gemini_key_here
set PERPLEXITY_API_KEY=your_perplexity_key_here  
set SERPAPI_API_KEY=your_serpapi_key_here

Linux/Mac:
export GEMINI_API_KEY=your_gemini_key_here
export PERPLEXITY_API_KEY=your_perplexity_key_here
export SERPAPI_API_KEY=your_serpapi_key_here

Or create a .env file (remember to add it to .gitignore!)
"""
import os
import sys
import json

# Check for required environment variables
required_env_vars = [
    "GEMINI_API_KEY",
    "PERPLEXITY_API_KEY", 
    "SERPAPI_API_KEY"
]

missing_vars = []
for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print("❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nPlease set these environment variables before running the test.")
    print("See the docstring at the top of this file for instructions.")
    sys.exit(1)
else:
    print("✅ All required API keys found")

# Now import the cloud function
from gcp_cloud_function import mcp_analyze

def test_with_pdf_upload():
    """Test with PDF upload"""
    print("=" * 80)
    print("TEST 1: PDF Upload with Knowledge Graph")
    print("=" * 80)
    
    request_json = {
        'uploads': [
            {
                'filetype': 'pitch deck',
                'filename': 'CyberSwarm_PitchDeck_sep 26.pdf',
                'file_extension': 'pdf',
                'filepath': 'gs://pitchlense-object-storage/uploads/3f8d2791-cfbd-4627-b707-6fe2df47ca30/CyberSwarm_PitchDeck_sep 26.pdf'
            }
        ],
        'destination_gcs': 'gs://pitchlense-object-storage/runs/3f8d2791-cfbd-4627-b707-6fe2df47ca30.json'
    }
    
    try:
        response_json, status, headers = mcp_analyze(request_json)
        print(f"\nStatus Code: {status}")
        
        # Parse response
        response = json.loads(response_json)
        
        # Check for errors
        if "error" in response:
            print(f"\n❌ Error: {response['error']}")
            return False
        
        # Check knowledge graph
        if "knowledge_graph" in response:
            kg = response["knowledge_graph"]
            print(f"\n✓ Knowledge Graph Generated!")
            
            if "error" in kg:
                print(f"  ⚠ Knowledge Graph Error: {kg['error']}")
            elif "metadata" in kg:
                print(f"  - Dependencies: {kg['metadata'].get('total_dependencies', 0)}")
                print(f"  - Dependents: {kg['metadata'].get('total_dependents', 0)}")
                print(f"  - LLM Processed: {kg['metadata'].get('llm_processed', False)}")
            
            if "root" in kg:
                print(f"  - Company: {kg['root'].get('name', 'Unknown')}")
        else:
            print("\n⚠ No knowledge graph in response")
        
        # Check startup analysis
        if "startup_analysis" in response:
            analysis = response["startup_analysis"]
            print(f"\n[SUCCESS] Startup Analysis:")
            print(f"  - Total Analyses: {analysis.get('total_analyses', 0)}")
            print(f"  - LLM Type: {analysis.get('llm_client_type', 'unknown')}")
        
        # Save full response
        output_file = "test_output.json"
        with open(output_file, 'w') as f:
            json.dump(response, f, indent=2)
        print(f"\n✓ Full response saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_text_input():
    """Test with direct text input"""
    print("\n" + "=" * 80)
    print("TEST 2: Direct Text Input with Knowledge Graph")
    print("=" * 80)
    
    request_json = {
        "startup_text": """
        CyberSwarm is a revolutionary cybersecurity AI platform that protects 
        enterprise networks using swarm intelligence algorithms. The company 
        leverages NVIDIA GPUs for real-time threat detection and analysis, 
        hosted on AWS infrastructure.
        
        Technology Stack:
        - GPU Computing: NVIDIA A100 GPUs for AI inference
        - Cloud Infrastructure: AWS (Amazon Web Services)
        - Machine Learning: TensorFlow and PyTorch
        - Security Tools: Integration with Splunk, CrowdStrike
        
        The platform serves Fortune 500 companies in finance, healthcare, and 
        technology sectors who need advanced threat protection.
        
        Key Dependencies:
        - NVIDIA for GPU hardware
        - AWS for cloud infrastructure
        - Security data feeds from threat intelligence providers
        
        Target Customers:
        - Financial institutions (banks, insurance)
        - Healthcare providers (hospitals, clinics)
        - Technology companies (SaaS, cloud providers)
        
        Funding: $25M Series A
        Team: 45 employees
        Location: Austin, TX
        """,
        "use_mock": False
    }
    
    try:
        response_json, status, headers = mcp_analyze(request_json)
        print(f"\nStatus Code: {status}")
        
        # Parse response
        response = json.loads(response_json)
        
        # Check for errors
        if "error" in response:
            print(f"\n❌ Error: {response['error']}")
            return False
        
        # Check knowledge graph
        if "knowledge_graph" in response:
            kg = response["knowledge_graph"]
            print(f"\n✓ Knowledge Graph Generated!")
            
            if "error" in kg:
                print(f"  ⚠ Knowledge Graph Error: {kg['error']}")
            elif "metadata" in kg:
                print(f"  - Dependencies: {kg['metadata'].get('total_dependencies', 0)}")
                print(f"  - Dependents: {kg['metadata'].get('total_dependents', 0)}")
                print(f"  - LLM Processed: {kg['metadata'].get('llm_processed', False)}")
            
            if "root" in kg:
                print(f"  - Company: {kg['root'].get('name', 'Unknown')}")
            
            # Show sample nodes
            if "nodes" in kg:
                print(f"\n  Sample Nodes:")
                for i, node in enumerate(kg["nodes"][:3], 1):
                    print(f"    {i}. {node.get('name', 'Unknown')}")
                    print(f"       Type: {node.get('type', 'N/A')}")
                    print(f"       Relationship: {node.get('relationship', 'N/A')}")
                    if node.get('news'):
                        print(f"       News: {len(node['news'])} articles")
        else:
            print("\n⚠ No knowledge graph in response")
        
        # Save full response
        output_file = "test_output_text.json"
        with open(output_file, 'w') as f:
            json.dump(response, f, indent=2)
        print(f"\n✓ Full response saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CLOUD FUNCTION KNOWLEDGE GRAPH TESTS")
    print("=" * 80)
    print("\nAPI Keys loaded from environment")
    print(f"GEMINI_API_KEY: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")
    print(f"PERPLEXITY_API_KEY: {'YES' if os.getenv('PERPLEXITY_API_KEY') else 'NO'}")
    print(f"SERPAPI_API_KEY: {'YES' if os.getenv('SERPAPI_API_KEY') else 'NO'}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {'YES' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else 'NO'}")
    
    results = []
    
    # Test 1: PDF Upload
    # results.append(("PDF Upload", test_with_pdf_upload()))
    
    # Test 2: Direct Text (faster for testing knowledge graph)
    results.append(("Text Input", test_with_text_input()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    return all(r[1] for r in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

