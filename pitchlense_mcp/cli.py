"""
Command-line interface for PitchLense MCP Package.

Provides CLI tools for running the MCP server and performing risk analysis.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

from .core.comprehensive_scanner import ComprehensiveRiskScanner
from .models.risk_models import StartupData


def load_startup_data(file_path: str) -> Dict[str, Any]:
    """Load startup data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def save_results(results: Dict[str, Any], output_file: str):
    """Save analysis results to JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")


def run_comprehensive_analysis(args):
    """Run comprehensive risk analysis."""
    print("🚀 Starting Comprehensive Startup Risk Analysis...")
    
    # Load startup data
    startup_data = load_startup_data(args.input_file)
    
    # Initialize scanner
    scanner = ComprehensiveRiskScanner(api_key=args.api_key)
    
    # Run analysis
    print("📊 Analyzing startup risks across all categories...")
    results = scanner.comprehensive_startup_risk_analysis(startup_data)
    
    # Display results
    print(f"\n✅ Analysis Complete!")
    print(f"📈 Overall Risk Level: {results.get('overall_risk_level', 'Unknown')}")
    print(f"📊 Overall Risk Score: {results.get('overall_score', 0)}/10")
    print(f"💡 Investment Recommendation: {results.get('investment_recommendation', 'N/A')}")
    print(f"🎯 Confidence Score: {results.get('confidence_score', 0.0):.2f}")
    
    print("\n🚨 Key Concerns:")
    for i, concern in enumerate(results.get('key_concerns', [])[:3], 1):
        print(f"   {i}. {concern}")
    
    print("\n📋 Risk Categories Analyzed:")
    for category in results.get('risk_categories', []):
        print(f"   • {category.get('category_name', 'Unknown')}: {category.get('overall_risk_level', 'Unknown')} ({category.get('category_score', 0)}/10)")
    
    # Save results if output file specified
    if args.output_file:
        save_results(results, args.output_file)


def run_quick_assessment(args):
    """Run quick risk assessment."""
    print("⚡ Starting Quick Risk Assessment...")
    
    # Load startup data
    startup_data = load_startup_data(args.input_file)
    
    # Initialize scanner
    scanner = ComprehensiveRiskScanner(api_key=args.api_key)
    
    # Run quick assessment
    print("📊 Analyzing critical risk areas...")
    results = scanner.quick_risk_assessment(startup_data)
    
    # Display results
    print(f"\n✅ Quick Assessment Complete!")
    print(f"📈 Overall Risk Level: {results.get('overall_risk_level', 'Unknown')}")
    print(f"📊 Overall Risk Score: {results.get('overall_score', 0)}/10")
    print(f"📝 Note: {results.get('note', 'N/A')}")
    
    # Save results if output file specified
    if args.output_file:
        save_results(results, args.output_file)


def run_mcp_server(args):
    """Run the MCP server."""
    print("🚀 Starting PitchLense MCP Server...")
    print("📊 Available Tools:")
    print("   • comprehensive_startup_risk_analysis - Full risk assessment across all categories")
    print("   • quick_risk_assessment - Quick assessment of critical risk areas")
    print("🔧 Make sure to set your GEMINI_API_KEY environment variable")
    print("=" * 60)
    
    try:
        scanner = ComprehensiveRiskScanner(api_key=args.api_key)
        scanner.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down MCP server...")
    except Exception as e:
        print(f"❌ Error running MCP server: {e}")
        sys.exit(1)


def create_sample_data(args):
    """Create sample startup data file."""
    sample_data = {
        "name": "TechFlow Solutions",
        "description": "AI-powered workflow automation platform for small businesses",
        "industry": "SaaS/Productivity Software",
        "stage": "Early Growth",
        "team_size": 8,
        "founders": ["Sarah Johnson", "Mike Chen"],
        "funding_raised": 2500000.0,
        "revenue": 180000.0,
        "customers": 150,
        "market_size": "Global SMB productivity market estimated at $15B",
        "competitors": ["Zapier", "Microsoft Power Automate", "Automation Anywhere"],
        "additional_info": {
            "founded": "2022",
            "headquarters": "San Francisco, CA",
            "key_features": ["No-code automation", "AI integration", "Multi-platform support"],
            "target_customers": "Small to medium businesses with 10-500 employees"
        }
    }
    
    output_file = args.output_file or "sample_startup_data.json"
    save_results(sample_data, output_file)
    print(f"📝 Sample startup data created: {output_file}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PitchLense MCP - Professional Startup Risk Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run comprehensive analysis
  pitchlense-mcp analyze --input startup_data.json --output results.json
  
  # Run quick assessment
  pitchlense-mcp quick --input startup_data.json
  
  # Start MCP server
  pitchlense-mcp server
  
  # Create sample data
  pitchlense-mcp sample --output my_startup.json
        """
    )
    
    parser.add_argument(
        "--api-key",
        help="Gemini API key (defaults to GEMINI_API_KEY environment variable)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Comprehensive analysis command
    analyze_parser = subparsers.add_parser("analyze", help="Run comprehensive risk analysis")
    analyze_parser.add_argument("--input", "-i", required=True, help="Input JSON file with startup data")
    analyze_parser.add_argument("--output", "-o", help="Output JSON file for results")
    analyze_parser.set_defaults(func=run_comprehensive_analysis)
    
    # Quick assessment command
    quick_parser = subparsers.add_parser("quick", help="Run quick risk assessment")
    quick_parser.add_argument("--input", "-i", required=True, help="Input JSON file with startup data")
    quick_parser.add_argument("--output", "-o", help="Output JSON file for results")
    quick_parser.set_defaults(func=run_quick_assessment)
    
    # MCP server command
    server_parser = subparsers.add_parser("server", help="Start MCP server")
    server_parser.set_defaults(func=run_mcp_server)
    
    # Sample data command
    sample_parser = subparsers.add_parser("sample", help="Create sample startup data file")
    sample_parser.add_argument("--output", "-o", help="Output JSON file for sample data")
    sample_parser.set_defaults(func=create_sample_data)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check for API key
    if not args.api_key and not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY='your_api_key_here'")
        print("   Or use --api-key argument")
        print()
    
    # Run the selected command
    args.func(args)


if __name__ == "__main__":
    main()
