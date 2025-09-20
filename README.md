# PitchLense MCP - Professional Startup Risk Analysis Package

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Python docs](https://readthedocs.org/projects/pitchlense-mcp/badge/?version=latest)](https://pitchlense-mcp.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/pitchlense-mcp.svg)](https://pypi.org/project/pitchlense-mcp/)
[![Build Status](https://img.shields.io/github/workflow/status/pitchlense/pitchlense-mcp/CI)](https://github.com/connectaman/Pitchlense-mcp/actions)

A comprehensive Model Context Protocol (MCP) package for analyzing startup investment risks using AI-powered assessment across multiple risk categories. Built with FastMCP and Google Gemini AI.

PitchLense is a comprehensive AI-powered startup analysis platform that provides detailed risk assessment and growth potential evaluation for early-stage ventures. The platform analyzes multiple dimensions of startup risk and provides actionable insights for investors, founders, and stakeholders.

## 🔗 Quick Links

- Website Link : https://www.pitchlense.com
- Web App Github Repo: https://github.com/connectaman/PitchLense

<div align="center">

[![YouTube Tutorial](https://img.shields.io/badge/📺_YouTube_Tutorial-red?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/XUuLeXaEIdI)
[![AppWebsite](https://img.shields.io/badge/🌐_Website-black?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.pitchlense.com/)
[![GitHub Repository](https://img.shields.io/badge/💻_GitHub-black?style=for-the-badge&logo=github&logoColor=white)](https://github.com/connectaman/PitchLense)
[![MCP Repository](https://img.shields.io/badge/🔧_MCP_Repository-black?style=for-the-badge&logo=github&logoColor=white)](https://github.com/connectaman/Pitchlense-mcp)
[![PyPI Package](https://img.shields.io/badge/🐍_PyPI_Package-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/pitchlense-mcp/)
[![Documentation](https://img.shields.io/badge/📚_Documentation-FFD43B?style=for-the-badge&logo=readthedocs&logoColor=black)](https://pitchlense-mcp.readthedocs.io/en/latest/api.html)

</div>

### 📖 How to Use PitchLense
Watch our comprehensive tutorial video to learn how to use PitchLense effectively:

[![How to use PitchLense](https://img.youtube.com/vi/XUuLeXaEIdI/0.jpg)](https://youtu.be/XUuLeXaEIdI)

**Click the image above to watch the tutorial on YouTube**

## 🚀 Features

### Individual Risk Analysis Tools
- **Market Risk Analyzer** - TAM, growth rate, competition, differentiation
- **Product Risk Analyzer** - Development stage, market fit, technical feasibility, IP protection
- **Team Risk Analyzer** - Leadership depth, founder stability, skill gaps, credibility
- **Financial Risk Analyzer** - Metrics consistency, burn rate, projections, CAC/LTV
- **Customer Risk Analyzer** - Traction levels, churn rate, retention, customer concentration
- **Operational Risk Analyzer** - Supply chain, GTM strategy, efficiency, execution
- **Competitive Risk Analyzer** - Incumbent strength, entry barriers, defensibility
- **Legal Risk Analyzer** - Regulatory environment, compliance, legal disputes
- **Exit Risk Analyzer** - Exit pathways, sector activity, late-stage appeal

### Comprehensive Analysis Tools & Data Sources
- **Comprehensive Risk Scanner** - Full analysis across all risk categories
- **Quick Risk Assessment** - Fast assessment of critical risk areas
- **Peer Benchmarking** - Compare metrics against sector/stage peers
- **SerpAPI Google News Tool** - Fetches first-page Google News with URLs and thumbnails
- **Perplexity Search Tool** - Answers with cited sources and URLs

## 📊 Risk Categories Covered

| Category | Key risks |
| --- | --- |
| Market | Small/overstated TAM; weak growth; crowded space; limited differentiation; niche dependence |
| Product | Early stage; unclear PMF; technical uncertainty; weak IP; poor scalability |
| Team/Founder | Single-founder risk; churn; skill gaps; credibility; misaligned incentives |
| Financial | Inconsistent metrics; high burn/short runway; optimistic projections; unfavorable CAC/LTV; low margins |
| Customer & Traction | Low traction; high churn; low retention; no marquee customers; concentration risk |
| Operational | Fragile supply chain; unclear GTM; operational inefficiency; poor execution |
| Competitive | Strong incumbents; low entry barriers; weak defensibility; saturation |
| Legal & Regulatory | Grey/untested areas; compliance gaps; disputes; IP risks |
| Exit | Unclear pathways; low sector exit activity; weak late‑stage appeal |

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install pitchlense-mcp
```

### From Source
```bash
git clone https://github.com/pitchlense/pitchlense-mcp.git
cd pitchlense-mcp
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/pitchlense/pitchlense-mcp.git
cd pitchlense-mcp
pip install -e ".[dev]"
```

## 🔑 Setup

### 1. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 2. Create .env
```bash
cp .env.template .env
# edit .env and fill in keys
```
Supported variables:
```
GEMINI_API_KEY=
SERPAPI_API_KEY=
PERPLEXITY_API_KEY=
```

## 🚀 Usage

### Command Line Interface

#### Run Comprehensive Analysis
```bash
# Create sample data
pitchlense-mcp sample --output my_startup.json

# Run comprehensive analysis
pitchlense-mcp analyze --input my_startup.json --output results.json
```

#### Run Quick Assessment
```bash
pitchlense-mcp quick --input my_startup.json --output quick_results.json
```

#### Start MCP Server
```bash
pitchlense-mcp server
```

### Python API

#### Basic Usage (single text input)
```python
from pitchlense_mcp import ComprehensiveRiskScanner

# Initialize scanner (reads GEMINI_API_KEY from env if not provided)
scanner = ComprehensiveRiskScanner()

# Provide all startup info as one organized text string
startup_info = """
Name: TechFlow Solutions
Industry: SaaS/Productivity Software
Stage: Series A

Business Model:
AI-powered workflow automation for SMBs; subscription pricing.

Financials:
MRR: $45k; Burn: $35k; Runway: 8 months; LTV/CAC: 13.3

Traction:
250 customers; 1,200 MAU; Churn: 5% monthly; NRR: 110%

Team:
CEO: Sarah Chen; CTO: Michael Rodriguez; Team size: 12

Market & Competition:
TAM: $12B; Competitors: Zapier, Power Automate; Growth: 15% YoY
"""

# Run comprehensive analysis
results = scanner.comprehensive_startup_risk_analysis(startup_info)

print(f"Overall Risk Level: {results['overall_risk_level']}")
print(f"Overall Risk Score: {results['overall_score']}/10")
print(f"Investment Recommendation: {results['investment_recommendation']}")
```

#### Individual Risk Analysis (text input)
```python
from pitchlense_mcp import MarketRiskAnalyzer, GeminiLLM

# Initialize components
llm_client = GeminiLLM(api_key="your_api_key")
market_analyzer = MarketRiskAnalyzer(llm_client)

# Analyze market risks
market_results = market_analyzer.analyze(startup_info)
print(f"Market Risk Level: {market_results['overall_risk_level']}")
```

### MCP Server Integration

The package provides a complete MCP server that can be integrated with MCP-compatible clients:

```python
from pitchlense_mcp import ComprehensiveRiskScanner

# Start MCP server
scanner = ComprehensiveRiskScanner()
scanner.run()
```

## 📋 Input Data Format

The primary input is a single organized text string containing all startup information (details, metrics, traction, news, competitive landscape, etc.). This is the format used by all analyzers and MCP tools.

Example text input:
```
Name: AcmeAI
Industry: Fintech (Lending)
Stage: Seed

Summary:
Building AI-driven credit risk models for SMB lending; initial pilots with 5 lenders.

Financials:
MRR: $12k; Burn: $60k; Runway: 10 months; Gross Margin: 78%

Traction:
200 paying SMBs; 30% MoM growth; Churn: 3% monthly; CAC: $220; LTV: $2,100

Team:
Founders: Jane Doe (ex-Square), John Lee (ex-Stripe); Team size: 9

Market & Competition:
TAM: $25B; Competitors: Blend, Upstart; Advantage: faster underwriting via proprietary data partnerships
```

Tip: See `examples/text_input_example.py` for a complete end-to-end script and JSON export of results.

## 📊 Output Format

All tools return structured JSON responses with:

```json
{
    "startup_name": "Startup Name",
    "overall_risk_level": "low|medium|high|critical",
    "overall_score": 1-10,
    "risk_categories": [
        {
            "category_name": "Risk Category",
            "overall_risk_level": "low|medium|high|critical",
            "category_score": 1-10,
            "indicators": [
                {
                    "indicator": "Specific risk factor",
                    "risk_level": "low|medium|high|critical",
                    "score": 1-10,
                    "description": "Detailed risk description",
                    "recommendation": "Mitigation action"
                }
            ],
            "summary": "Category summary"
        }
    ],
    "key_concerns": ["Top 5 concerns"],
    "investment_recommendation": "Investment advice",
    "confidence_score": 0.0-1.0,
    "analysis_metadata": {
        "total_categories_analyzed": 9,
        "successful_analyses": 9,
        "analysis_timestamp": "2024-01-01T00:00:00Z"
    }
}
```

## 🎯 Use Cases

- **Investor Due Diligence** - Comprehensive risk assessment for investment decisions
- **Startup Self-Assessment** - Identify and mitigate key risk areas
- **Portfolio Risk Management** - Assess risk across startup portfolio
- **Accelerator/Incubator Screening** - Evaluate startup applications
- **M&A Risk Analysis** - Assess acquisition targets
- **Research & Analysis** - Academic and industry research on startup risks

## 🏗️ Architecture

### Package Structure
```
pitchlense-mcp/
├── pitchlense_mcp/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── base.py           # Base classes
│   │   ├── gemini_client.py  # Gemini AI integration
│   │   └── comprehensive_scanner.py
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   └── risk_models.py
│   ├── analyzers/            # Individual risk analyzers
│   │   ├── __init__.py
│   │   ├── market_risk.py
│   │   ├── product_risk.py
│   │   ├── team_risk.py
│   │   ├── financial_risk.py
│   │   ├── customer_risk.py
│   │   ├── operational_risk.py
│   │   ├── competitive_risk.py
│   │   ├── legal_risk.py
│   │   └── exit_risk.py
│   └── utils/                # Utility functions
├── tests/                    # Test suite
├── docs/                     # Documentation
├── examples/                 # Example usage
├── setup.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Key Components

1. **Base Classes** (`core/base.py`)
   - `BaseLLM` - Abstract base for LLM integrations
   - `BaseRiskAnalyzer` - Base class for all risk analyzers
   - `BaseMCPTool` - Base class for MCP tools

2. **Gemini Integration** (`core/gemini_client.py`)
   - `GeminiLLM` - Main LLM client
   - `GeminiTextGenerator` - Text generation
   - `GeminiImageAnalyzer` - Image analysis
   - `GeminiVideoAnalyzer` - Video analysis
   - `GeminiAudioAnalyzer` - Audio analysis
   - `GeminiDocumentAnalyzer` - Document analysis

3. **Risk Analyzers** (`analyzers/`)
   - Individual analyzers for each risk category
   - Consistent interface and output format
   - Extensible architecture

4. **Models** (`models/risk_models.py`)
   - Pydantic models for type safety
   - Structured data validation
   - Clear data contracts

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/pitchlense/pitchlense-mcp.git
cd pitchlense-mcp
pip install -e ".[dev]"
pre-commit install
```

### Run Tests
```bash
# Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dev extras (pytest, pytest-cov, linters)
pip install -e ".[dev]"

# Run tests with coverage and avoid global plugin conflicts
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p pytest_cov
```

Notes:
- Coverage reports are written to `htmlcov/index.html` and `coverage.xml`.
- If you see errors about unknown `--cov` options, ensure you passed `-p pytest_cov` when `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is set.

### Example Scripts
```bash
python examples/basic_usage.py
python examples/text_input_example.py
```

### Code Formatting
```bash
black pitchlense_mcp/
flake8 pitchlense_mcp/
mypy pitchlense_mcp/
```

### Build Package
```bash
python -m build
```

## 📝 Notes

- All risk scores are on a 1-10 scale (1 = lowest risk, 10 = highest risk)
- Risk levels: low (1-3), medium (4-6), high (7-8), critical (9-10)
- Individual tools can be used independently or combined for comprehensive analysis
- The system handles API failures gracefully with fallback responses
- All tables and structured data are returned in JSON format
- Professional package architecture with proper separation of concerns

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://pitchlense-mcp.readthedocs.io/](https://pitchlense-mcp.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/pitchlense/pitchlense-mcp/issues)
- **Email**: connectamanulla@gmail.com

## 🙏 Acknowledgments

- Google Gemini AI for providing the underlying AI capabilities
- FastMCP for the Model Context Protocol implementation
- The open-source community for inspiration and tools

---

**PitchLense MCP** - Making startup risk analysis accessible, comprehensive, and AI-powered.
