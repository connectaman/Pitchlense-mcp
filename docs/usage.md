# Usage

## Install

```bash
pip install pitchlense-mcp
```

## Quick start (text input)

```python
from pitchlense_mcp import ComprehensiveRiskScanner

scanner = ComprehensiveRiskScanner()
startup_info = """
Name: TechFlow Solutions
Industry: SaaS/Productivity Software
Stage: Series A
"""
results = scanner.comprehensive_startup_risk_analysis(startup_info)
print(results["overall_risk_level"])  # e.g., "medium"
```

