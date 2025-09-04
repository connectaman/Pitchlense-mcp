# Contributing to PitchLense MCP

Thanks for your interest in contributing! We welcome issues and pull requests.

## How to Contribute

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feat/your-feature
   ```
2. Install dev dependencies and pre-commit hooks:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   pre-commit install
   ```
3. Run linters and tests locally:
   ```bash
   black pitchlense_mcp/
   flake8 pitchlense_mcp/
   mypy pitchlense_mcp/
   # Avoid global pytest plugins interfering; enable coverage plugin explicitly
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p pytest_cov
   ```

### Running Tests (quick reference)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p pytest_cov
```
4. Add/Update tests for your changes.
5. Commit with clear messages and open a PR targeting `main`.

## Code Style
- Python 3.8+
- Black, Flake8, and MyPy for formatting and static checks
- Docstrings in Google or NumPy style
- Keep functions small and focused

## Pull Request Checklist
- [ ] Linted and formatted
- [ ] Tests added/updated and passing
- [ ] Docs/README updated (if applicable)
- [ ] Changelog entry (if added later)

## Reporting Issues
Please include:
- Environment (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
- Logs or stack traces when possible

## Security
Do not include secrets in issues or PRs. Use `.env` locally and never commit `.env`.
