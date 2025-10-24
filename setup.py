"""
Setup script for PitchLense MCP Package.

A professional Python package for startup risk analysis using Model Context Protocol (MCP)
and Google Gemini AI.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "PitchLense MCP - Professional Startup Risk Analysis MCP Package"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="pitchlense-mcp",
    version="1.1.4",
    author="Aman Ulla",
    author_email="connectamanulla@gmail.com",
    description="Professional startup risk analysis using MCP and Google Gemini AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pitchlense/pitchlense-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "isort>=5.12.0",
            "truffleHog3>=3.0.10",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pitchlense-mcp=pitchlense_mcp.cli:main",
        ],
    },
    keywords=[
        "startup", "risk", "analysis", "investment", "mcp", "model-context-protocol",
        "gemini", "ai", "machine-learning", "due-diligence", "venture-capital"
    ],
    project_urls={
        "Bug Reports": "https://github.com/pitchlense/pitchlense-mcp/issues",
        "Source": "https://github.com/pitchlense/pitchlense-mcp",
        "Documentation": "https://pitchlense-mcp.readthedocs.io/",
        "Homepage": "https://amanulla.in",
        "Author (GitHub)": "https://github.com/connectaman",
        "Articles": "https://hashnode.com/@connectaman",
    },
    include_package_data=True,
    zip_safe=False,
)
