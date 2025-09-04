"""
Google Cloud Function HTTP entrypoint to run MCP analyses in parallel.

Usage (Cloud Functions) 2nd gen 8cores 16GB RAM:
  - Runtime: Python 3.12+
  - Entry point: mcp_analyze
  - Trigger: HTTP

POST JSON body shape:
{
  "startup_text": "<all startup info as a single organized text string>",
  "use_mock": false,                 # optional; default: auto based on GEMINI_API_KEY
  "categories": ["Market Risk Analysis", ...],  # optional; subset of analyses to run
  "destination_gcs": "gs://bucket/path/to/output.json"  # optional; write results to GCS
}

Response:
{
  "startup_analysis": { ... },
  "errors": { "<analysis>": "<error message>" }
}

Notes:
  - Analyses are executed in parallel using a thread pool. This is appropriate because
    the workload is dominated by network-bound LLM/API calls rather than CPU-bound work.
  - If GEMINI_API_KEY is not set or use_mock=true, a mock LLM client is used.
"""

from __future__ import annotations

import os
import json
from datetime import datetime
from urllib.parse import urlparse
from typing import Any, Dict, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cloud Functions provides a Flask-like request object
try:
    # Only for typing; Cloud Functions provides the object at runtime
    from flask import Request
except Exception:  # pragma: no cover - for local static analysis
    Request = Any  # type: ignore

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
    GeminiLLM,
)
from pitchlense_mcp.core.mock_client import MockLLM


def _build_tools_and_methods() -> Dict[str, Tuple[Any, str]]:
    """Create MCP tools and map them to their analysis method names.

    Returns:
        Mapping of human-readable analysis name to (tool instance, method name).
    """
    tools: Dict[str, Tuple[Any, str]] = {
        "Customer Risk Analysis": (CustomerRiskMCPTool(), "analyze_customer_risks"),
        "Financial Risk Analysis": (FinancialRiskMCPTool(), "analyze_financial_risks"),
        "Market Risk Analysis": (MarketRiskMCPTool(), "analyze_market_risks"),
        "Team Risk Analysis": (TeamRiskMCPTool(), "analyze_team_risks"),
        "Operational Risk Analysis": (OperationalRiskMCPTool(), "analyze_operational_risks"),
        "Competitive Risk Analysis": (CompetitiveRiskMCPTool(), "analyze_competitive_risks"),
        "Exit Risk Analysis": (ExitRiskMCPTool(), "analyze_exit_risks"),
        "Legal Risk Analysis": (LegalRiskMCPTool(), "analyze_legal_risks"),
        "Product Risk Analysis": (ProductRiskMCPTool(), "analyze_product_risks"),
        "Peer Benchmarking": (PeerBenchmarkMCPTool(), "analyze_peer_benchmark"),
    }
    return tools


def _select_llm_client(use_mock: bool | None = None):
    """Select LLM client based on environment and input flag."""
    if use_mock is True:
        return MockLLM(), "mock"
    if os.getenv("GEMINI_API_KEY"):
        return GeminiLLM(), "gemini"
    return MockLLM(), "mock"


def _run_parallel_analyses(
    tools_and_methods: Dict[str, Tuple[Any, str]],
    startup_text: str,
    max_workers: int,
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Run all analyses in parallel.

    Args:
        tools_and_methods: Mapping of analysis name to (tool instance, method name)
        startup_text: The single text input containing all startup details
        max_workers: Thread pool size

    Returns:
        Tuple of (results_by_name, errors_by_name)
    """
    results: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name: Dict[Any, str] = {}
        for analysis_name, (tool, method_name) in tools_and_methods.items():
            analyze_method: Callable[[str], Dict[str, Any]] = getattr(tool, method_name)
            future = executor.submit(analyze_method, startup_text)
            future_to_name[future] = analysis_name

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                results[name] = result
            except Exception as exc:  # pragma: no cover - defensive path
                errors[name] = str(exc)

    return results, errors


def mcp_analyze(request: Request):
    """HTTP Cloud Function entrypoint to run MCP analyses in parallel.

    - Accepts POST with JSON body containing `startup_text` and optional `use_mock`, `categories`.
    - Returns structured JSON with results and radar chart data.
    """
    try:
        if request.method == "GET":
            usage = {
                "message": "Send POST with JSON body containing 'startup_text' string.",
                "example_body": {
                    "startup_text": "Name: AcmeAI\nIndustry: Fintech\nStage: Seed\n...",
                    "use_mock": False,
                    "categories": [
                        "Market Risk Analysis",
                        "Financial Risk Analysis",
                    ],
                },
            }
            return (json.dumps(usage), 200, {"Content-Type": "application/json"})

        data = request.get_json(silent=True) or {}
        startup_text: str = (data.get("startup_text") or "").strip()
        if not startup_text:
            return (
                json.dumps({"error": "Missing 'startup_text' in request body"}),
                400,
                {"Content-Type": "application/json"},
            )

        requested_categories = data.get("categories")
        use_mock_flag = data.get("use_mock")  # may be None
        destination_gcs = (data.get("destination_gcs") or "").strip()

        tools_map = _build_tools_and_methods()
        if requested_categories:
            tools_map = {k: v for k, v in tools_map.items() if k in set(requested_categories)}
            if not tools_map:
                return (
                    json.dumps({"error": "No valid categories requested"}),
                    400,
                    {"Content-Type": "application/json"},
                )

        llm_client, llm_type = _select_llm_client(use_mock=use_mock_flag)

        # Attach the LLM client to each tool
        for _, (tool, _) in tools_map.items():
            try:
                tool.set_llm_client(llm_client)
            except Exception:
                pass

        # Thread pool size: default to 2 * CPU cores, minimum 4, max 16
        cpu_count = os.cpu_count() or 2
        default_workers = max(4, min(16, cpu_count * 2))
        max_workers = int(os.getenv("MCP_PARALLEL_WORKERS", default_workers))

        analysis_results, analysis_errors = _run_parallel_analyses(
            tools_and_methods=tools_map,
            startup_text=startup_text,
            max_workers=max_workers,
        )

        # Radar chart data from category scores
        radar_dimensions = []
        radar_scores = []
        for name, result in analysis_results.items():
            if isinstance(result, dict) and "category_score" in result and "error" not in result:
                radar_dimensions.append(name)
                radar_scores.append(result.get("category_score", 0))

        response_payload: Dict[str, Any] = {
            "startup_analysis": {
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                "llm_client_type": llm_type,
                "total_analyses": len(analysis_results),
                "analyses": analysis_results,
                "radar_chart": {
                    "dimensions": radar_dimensions,
                    "scores": radar_scores,
                    "scale": 10,
                },
            },
            "errors": analysis_errors,
        }

        # If a GCS destination was provided, write the JSON there
        if destination_gcs:
            try:
                _write_json_to_gcs(destination_gcs, response_payload)
            except Exception as gcs_exc:
                # Include GCS error in response but do not fail the analysis results
                response_payload.setdefault("errors", {})["gcs_write_error"] = str(gcs_exc)

        return (json.dumps(response_payload), 200, {"Content-Type": "application/json"})

    except Exception as exc:  # pragma: no cover - defensive path
        error_payload = {"error": f"Unhandled error: {str(exc)}"}
        return (json.dumps(error_payload), 500, {"Content-Type": "application/json"})


# Optional: local testing helper
if __name__ == "__main__":  # pragma: no cover
    # Simple local runner to test with: python gcp_cloud_invocation.py
    class _MockReq:
        method = "POST"

        def __init__(self, body: Dict[str, Any]):
            self._body = body

        def get_json(self, silent: bool = False):
            return self._body

    sample_text = (
        "Name: TechFlow Solutions\nIndustry: SaaS/Productivity Software\nStage: Series A\n"
        "Financials: MRR: $45k; Burn: $35k; Runway: 8 months\n"
        "Traction: 250 customers; 1,200 MAU\n"
    )
    mock_request = _MockReq({"startup_text": sample_text, "use_mock": True})
    body, status, headers = mcp_analyze(mock_request)
    print(status, headers)
    print(json.loads(body))


def _write_json_to_gcs(gcs_uri: str, payload: Dict[str, Any]) -> None:
    """Write payload JSON to a GCS URI like gs://bucket/path/file.json.

    Requires the environment to have credentials with storage write access.
    """
    parsed = urlparse(gcs_uri)
    if parsed.scheme != "gs" or not parsed.netloc or not parsed.path:
        raise ValueError("destination_gcs must be in the form gs://bucket/path/file.json")

    bucket_name = parsed.netloc
    # strip leading slash from path
    blob_path = parsed.path.lstrip("/")

    # Lazy import to keep runtime lean when GCS not used
    from google.cloud import storage  # type: ignore

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(
        data=json.dumps(payload, ensure_ascii=False, indent=2),
        content_type="application/json",
    )


