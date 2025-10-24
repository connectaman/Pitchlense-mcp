from __future__ import annotations
"""
Google Cloud Function HTTP entrypoint to run MCP analyses in parallel.

Usage (Cloud Functions):
  - Runtime: Python 3.12+
  - Entry point: mcp_analyze
  - Trigger: HTTP

POST JSON body shape:
{
  "company_name": "Sia",
  "uploads": [{'filetype': 'pitch deck', 'filename': 'Invoice-Aug.pdf', 'file_extension': 'pdf', 'filepath': 'gs://pitchlense-object-storage/uploads/a181cd09-095e-49d6-bb6f-4ee7b01b8678/Invoice-Aug.pdf'}],
  "startup_text": "<all startup info as a single organized text string>",
  "use_mock": false,                 # optional; default: auto based on GEMINI_API_KEY
  "categories": ["Market Risk Analysis", ...],  # optional; subset of analyses to run
  "destination_gcs": "gs://bucket/path/to/output.json"  # optional; write results to GCS
}

{
  "uploads": [
    {"filetype": "pitch deck", "filename": "(1) Aman Ulla _ LinkedIn.pdf", "file_extension": "pdf", "filepath": "gs://pitchlense-object-storage/uploads/test/(1) Aman Ulla _ LinkedIn.pdf"},
    {"filetype": "pitch deck", "filename": "Novalad Deck.pdf", "file_extension": "pdf", "filepath": "gs://pitchlense-object-storage/uploads/test/Novalad Deck.pdf"}
    ],
  "destination_gcs": "gs://pitchlense-object-storage/runs/test_output.json"
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

in GCP Cloud Function add below in the requirements.txt 

functions-framework==3.*
pitchlense-mcp
flask
google-cloud-storage
serpapi

"""
import functions_framework

import os
import json
from datetime import datetime, timezone
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
    LVAnalysisMCPTool,
    GeminiLLM,
    SerpNewsMCPTool,
    SerpPdfSearchMCPTool,
    PerplexityMCPTool,
    UploadExtractor,
    KnowledgeGraphMCPTool,
    LinkedInAnalyzerMCPTool,
    GoogleContentModerationMCPTool
)
from pitchlense_mcp.core.mock_client import MockLLM
from pitchlense_mcp.utils.json_extractor import extract_json_from_response


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
        "LV-Analysis": (LVAnalysisMCPTool(), "analyze_lv_business_note"),
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


def mcp_analyze(data: dict):
    """HTTP Cloud Function entrypoint to run MCP analyses in parallel.

    - Accepts POST with JSON body containing `startup_text` and optional `use_mock`, `categories`.
    - Returns structured JSON with results and radar chart data.
    """
    try:
        startup_text: str = (data.get("startup_text") or "").strip()
        request_company_name: str = (data.get("company_name") or "").strip()
        extracted_files_info: list[dict] = []
        if not startup_text:
            # Try to build startup_text from uploads if provided
            uploads = data.get("uploads") or []
            if not uploads:
                return (
                    json.dumps({"error": "Missing 'startup_text' or 'uploads' in request body"}),
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

        # If startup_text is empty but uploads present, download files and extract
        if not startup_text:
            # Support local paths or gs:// URIs in uploads.filepath
            prepared: list[dict] = []
            for u in uploads:
                fp = (u.get("filepath") or "").strip()
                if not fp:
                    continue
                local_path = fp
                if fp.startswith("gs://"):
                    # Download to tmp from GCS
                    parsed = urlparse(fp)
                    bucket_name = parsed.netloc
                    blob_path = parsed.path.lstrip("/")
                    from google.cloud import storage  # lazy import
                    client = storage.Client()
                    bucket = client.bucket(bucket_name)
                    blob = bucket.blob(blob_path)
                    local_dir = os.path.join("/tmp", os.path.dirname(blob_path))
                    os.makedirs(local_dir, exist_ok=True)
                    local_path = os.path.join("/tmp", blob_path)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    blob.download_to_filename(local_path)

                prepared.append({
                    "filename": u.get("filename"),
                    "file_extension": u.get("file_extension"),
                    "local_path": local_path,
                    "filetype": u.get("filetype"),
                    "filepath": fp,  # Store original GCS filepath
                })

            extractor = UploadExtractor(llm_client if isinstance(llm_client, GeminiLLM) else GeminiLLM())
            docs = extractor.extract_documents(prepared)
            synthesized = extractor.synthesize_startup_text(docs)
            startup_text = (synthesized or "").strip()
            try:
                print(f"[CloudFn] Extracted docs: {len(docs)}; synthesized_len={len(startup_text)}")
            except Exception:
                pass
            # Build files array for response (filename, extension, filetype, content, filepath)
            try:
                for original, doc in zip(prepared, docs):
                    extracted_files_info.append({
                        "filetype": original.get("filetype") or doc.get("type"),
                        "filename": doc.get("name"),
                        "file_extension": doc.get("extension"),
                        "content": doc.get("content"),
                        "filepath": original.get("filepath"),  # Include GCS filepath
                    })
            except Exception:
                extracted_files_info = []
            if not startup_text:
                return (
                    json.dumps({"error": "Failed to synthesize startup_text from uploads"}),
                    400,
                    {"Content-Type": "application/json"},
                )

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

        # LLM-driven metadata extraction for news query
        extracted_metadata = None
        llm_extracted_metadata = None
        try:
            system_msg = "You extract concise company metadata. Respond with JSON only within <JSON></JSON> tags."
            user_msg = (
                "From the following startup description, extract the following fields strictly as JSON: "
                "{\"company_name\": string, \"domain\": short industry/domain, \"area\": product area/category}.\n"
                "Keep values short (1-6 words). If unknown, use an empty string.\n"
                "Text:\n" + startup_text
            )
            llm_resp = llm_client.predict(system_message=system_msg, user_message=user_msg)
            print("LLM Response", llm_resp)
            extracted_metadata = extract_json_from_response(llm_resp.get("response", ""))
            if not isinstance(extracted_metadata, dict):
                raise ValueError("Failed to parse JSON metadata from LLM response")

            # Build news query strictly from the extracted JSON
            news_query_terms = [
                (extracted_metadata.get("company_name") or "").strip(),
                (extracted_metadata.get("domain") or "").strip(),
                (extracted_metadata.get("area") or "").strip(),
            ]
            news_query = " ".join([t for t in news_query_terms if t])
            company_name = extracted_metadata.get("company_name") or None
            domain = extracted_metadata.get("domain") or None
            area = extracted_metadata.get("area") or None
            serp_news_tool = SerpNewsMCPTool()
            if company_name:
                news_fetch_company = serp_news_tool.fetch_google_news(company_name, num_results=10)
                print(f"[CloudFn] News links for '{company_name}': {len(news_fetch_company.get('results', []))} results")
            if domain:
                news_fetch_domain = serp_news_tool.fetch_google_news(domain, num_results=10)
                print(f"[CloudFn] News links for '{domain}': {len(news_fetch_domain.get('results', []))} results")
            if area:
                news_fetch_area = serp_news_tool.fetch_google_news(area, num_results=10)
                print(f"[CloudFn] News links for '{area}': {len(news_fetch_area.get('results', []))} results")
            news_fetch = news_fetch_company or news_fetch_domain or news_fetch_area
            print(f"[CloudFn] News links for '{company_name}', '{domain}', '{area}': {len(news_fetch.get('results', []))} results")
        except Exception as e:
            print(f"[CloudFn] Error in LLM JSON extraction: {str(e)}")
            import traceback
            traceback.print_exc()
            extracted_metadata = {}
            news_query = ""
            news_fetch = {"results": [], "error": None}

        # Internet documents search for PDFs using company name
        internet_documents = {"results": [], "error": None}
        try:
            company_name = (extracted_metadata.get("company_name") or request_company_name or "").strip() if isinstance(extracted_metadata, dict) else request_company_name
            if company_name:
                pdf_query = f"{company_name} filetype:pdf"
                serp_pdf_tool = SerpPdfSearchMCPTool()
                pdf_fetch = serp_pdf_tool.search_pdf_documents(pdf_query, num_results=10)
                internet_documents = pdf_fetch
                print(f"[CloudFn] PDF search for '{company_name}': {len(pdf_fetch.get('results', []))} results")
            else:
                print("[CloudFn] No company name extracted, skipping PDF search")
        except Exception as e:
            print(f"[CloudFn] Error in PDF document search: {str(e)}")
            internet_documents = {"results": [], "error": str(e)}

        # Market value and market size via Perplexity (based on extracted LLM metadata)
        market_value = []  # list of {"year": int, "value_usd_billion": float}
        market_size = []   # list of {"segment": str, "share_percent": number}
        try:
            domain = (extracted_metadata.get("domain") or "").strip() if isinstance(extracted_metadata, dict) else ""
            area = (extracted_metadata.get("area") or "").strip() if isinstance(extracted_metadata, dict) else ""
            if domain or area:
                ppx = PerplexityMCPTool()
                market_prompt = (
                    "You are a market research assistant. Based on the following domain and area, "
                    "return ONLY JSON inside <JSON></JSON> tags with this exact shape:\n"
                    "{\n"
                    "  \"market_value\": [ { \"year\": 2021, \"value_usd_billion\": 0.0 } ],\n"
                    "  \"market_size\": [ { \"segment\": \"SMB\", \"share_percent\": 0 } ]\n"
                    "}\n"
                    "- market_value should be a yearly time series (past 10 years and next 5 years forecast)\n"
                    "- Use numeric values only; omit currency symbols; values are in USD billions\n"
                    "- market_size should include a few key segments with percentage share totaling ~100\n"
                    f"\nDomain: {domain}\nArea: {area}\n"
                )
                ppx_resp = ppx.search_perplexity(market_prompt)
                if isinstance(ppx_resp, dict) and not ppx_resp.get("error"):
                    answer_text = (ppx_resp.get("answer") or "").strip()
                    market_json = extract_json_from_response(answer_text)
                    if isinstance(market_json, dict):
                        mv = market_json.get("market_value")
                        ms = market_json.get("market_size")
                        if isinstance(mv, list):
                            market_value = mv
                        if isinstance(ms, list):
                            market_size = ms
        except Exception:
            market_value = []
            market_size = []

        # Knowledge Graph generation
        knowledge_graph = {}
        try:
            # Extract company name from metadata if available, otherwise use request data
            final_company_name = ""
            if isinstance(extracted_metadata, dict) and extracted_metadata.get("company_name"):
                final_company_name = extracted_metadata.get("company_name").strip()
            elif request_company_name:
                final_company_name = request_company_name
            
            print(f"[CloudFn] Company name: {final_company_name}")
            print(f"[CloudFn] Startup text length: {len(startup_text)}")
            
            # Generate knowledge graph if we have startup text
            if startup_text and len(startup_text) > 100:
                print(f"[CloudFn] Generating knowledge graph...")
                if final_company_name:
                    print(f"[CloudFn] Using company name: {final_company_name}")
                else:
                    print(f"[CloudFn] Company name will be extracted by KG tool")
                
                kg_tool = KnowledgeGraphMCPTool()
                kg_tool.set_llm_client(llm_client if isinstance(llm_client, GeminiLLM) else GeminiLLM())
                knowledge_graph = kg_tool.generate_knowledge_graph(
                    startup_text=startup_text,
                    company_name=final_company_name if final_company_name else None
                )
                if knowledge_graph.get("error"):
                    print(f"[CloudFn] Knowledge graph error: {knowledge_graph.get('error')}")
                else:
                    print(f"[CloudFn] Knowledge graph generated successfully")
            else:
                print(f"[CloudFn] Skipping knowledge graph generation: startup_text too short ({len(startup_text)} chars)")
        except Exception as e:
            print(f"[CloudFn] Error generating knowledge graph: {str(e)}")
            import traceback
            traceback.print_exc()
            knowledge_graph = {"error": str(e)}

        # LinkedIn Profile Analysis (if LinkedIn PDFs are provided)
        linkedin_analysis = {}
        try:
            # Check if any uploaded files are LinkedIn profiles
            linkedin_files = []
            for file_info in extracted_files_info:
                filename = file_info.get("filename", "").lower()
                filetype = file_info.get("filetype", "").lower()
                
                # Check for LinkedIn profile filetypes
                linkedin_filetypes = ["founder profile", "linkedin", "profile", "linkedin profile","resume", "curriculum vitae"]
                is_linkedin_file = (
                    any(ft in filetype for ft in linkedin_filetypes) or
                    (filename.startswith("linkedin") or filename.endswith("linkedin.pdf") or "linkedin_" in filename) or 
                    (filename.endswith("profile.pdf") or filename.startswith("profile_"))
                )
                
                if is_linkedin_file:
                    print(f"[CloudFn] Detected LinkedIn profile: {file_info.get('filename')} (filetype: {filetype})")
                    linkedin_files.append(file_info)
            
            if linkedin_files:
                print(f"[CloudFn] Found {len(linkedin_files)} LinkedIn profile files - analyzing in parallel...")
                
                def analyze_single_linkedin_file(file_info):
                    """Analyze a single LinkedIn file and return results."""
                    try:
                        filepath = file_info.get("filepath", "")
                        filename = file_info.get("filename", "unknown")
                        
                        if filepath and filepath.startswith("gs://"):
                            # Download from GCS first
                            from google.cloud import storage
                            parsed = urlparse(filepath)
                            bucket_name = parsed.netloc
                            blob_path = parsed.path.lstrip("/")
                            client = storage.Client()
                            bucket = client.bucket(bucket_name)
                            blob = bucket.blob(blob_path)
                            local_path = os.path.join("/tmp", f"{filename}_{os.path.basename(blob_path)}")
                            blob.download_to_filename(local_path)
                            
                            print(f"[CloudFn] Downloaded {filename} to: {local_path}")
                            analyzer = LinkedInAnalyzerMCPTool()
                            result = analyzer.analyze_linkedin_profile(local_path, api_key=os.getenv("GEMINI_API_KEY"))
                            
                            # Clean up temporary file
                            try:
                                os.remove(local_path)
                            except:
                                pass
                                
                            return {
                                "filename": filename,
                                "filepath": filepath,
                                "analysis": result,
                                "success": True
                            }
                        else:
                            # Local file path
                            analyzer = LinkedInAnalyzerMCPTool()
                            result = analyzer.analyze_linkedin_profile(filepath, api_key=os.getenv("GEMINI_API_KEY"))
                            return {
                                "filename": filename,
                                "filepath": filepath,
                                "analysis": result,
                                "success": True
                            }
                            
                    except Exception as e:
                        print(f"[CloudFn] Error analyzing {file_info.get('filename', 'unknown')}: {str(e)}")
                        return {
                            "filename": file_info.get("filename", "unknown"),
                            "filepath": file_info.get("filepath", ""),
                            "analysis": {"error": str(e)},
                            "success": False
                        }
                
                # Analyze all LinkedIn files in parallel
                with ThreadPoolExecutor(max_workers=min(4, len(linkedin_files))) as executor:
                    # Submit all analysis tasks
                    future_to_file = {
                        executor.submit(analyze_single_linkedin_file, file_info): file_info 
                        for file_info in linkedin_files
                    }
                    
                    # Collect results
                    linkedin_analyses = []
                    for future in as_completed(future_to_file):
                        file_info = future_to_file[future]
                        try:
                            result = future.result()
                            linkedin_analyses.append(result)
                            if result["success"]:
                                print(f"[CloudFn] Successfully analyzed: {result['filename']}")
                            else:
                                print(f"[CloudFn] Failed to analyze: {result['filename']}")
                        except Exception as e:
                            print(f"[CloudFn] Unexpected error analyzing {file_info.get('filename', 'unknown')}: {str(e)}")
                            linkedin_analyses.append({
                                "filename": file_info.get("filename", "unknown"),
                                "filepath": file_info.get("filepath", ""),
                                "analysis": {"error": str(e)},
                                "success": False
                            })
                
                # Structure the final response
                successful_analyses = [a for a in linkedin_analyses if a["success"]]
                failed_analyses = [a for a in linkedin_analyses if not a["success"]]
                
                linkedin_analysis = {
                    "total_files": len(linkedin_files),
                    "successful_analyses": len(successful_analyses),
                    "failed_analyses": len(failed_analyses),
                    "analyses": linkedin_analyses,
                    "primary_analysis": successful_analyses[0]["analysis"] if successful_analyses else None,
                    "all_analyses": [a["analysis"] for a in successful_analyses]
                }
                
                print(f"[CloudFn] LinkedIn analysis complete: {len(successful_analyses)}/{len(linkedin_files)} successful")
            else:
                print("[CloudFn] No LinkedIn profile files detected")
        except Exception as e:
            print(f"[CloudFn] Error in LinkedIn analysis: {str(e)}")
            linkedin_analysis = {"error": str(e)}

        # Radar chart data from category scores (exclude LV-Analysis as it's not a risk analysis)
        radar_dimensions = []
        radar_scores = []
        for name, result in analysis_results.items():
            # Skip LV-Analysis for radar chart as it's a detailed business note, not a risk analysis
            if name == "LV-Analysis":
                continue
            if isinstance(result, dict) and "category_score" in result and "error" not in result:
                radar_dimensions.append(name)
                radar_scores.append(result.get("category_score", 0))
            else:
                try:
                    print(f"[CloudFn] Analysis result missing or error for {name}: keys={list(result.keys()) if isinstance(result, dict) else type(result)}")
                except Exception:
                    pass

        response_payload: Dict[str, Any] = {
            "files": extracted_files_info,
            "startup_analysis": {
                "llm_client_type": llm_type,
                "total_analyses": len(analysis_results),
                "analyses": analysis_results,
                "radar_chart": {
                    "dimensions": radar_dimensions,
                    "scores": radar_scores,
                    "scale": 10,
                },
                "market_value": market_value,
                "market_size": market_size,
            },
            "knowledge_graph": knowledge_graph,
            "linkedin_analysis": linkedin_analysis,
            "news": {
                "metadata": extracted_metadata,
                "query": news_query,
                "results": news_fetch.get("results") if isinstance(news_fetch, dict) else [],
                "error": news_fetch.get("error") if isinstance(news_fetch, dict) else None,
            },
            "internet_documents": internet_documents,
            "content_moderation" : False,
            "moderation_details" : {},
            "errors": analysis_errors,
        }

        # Content Moderation Check
        print("[CloudFn] Performing content moderation check...")
        try:
            # Convert the entire response to JSON string for moderation
            response_json_string = json.dumps(response_payload, ensure_ascii=False, indent=2)
            
            # Initialize content moderation tool
            content_moderator = GoogleContentModerationMCPTool()
            
            # Check if content requires moderation
            moderation_result = content_moderator.moderate_content(response_json_string)
            
            if moderation_result.get("moderation_required", False):
                print("[CloudFn] Content moderation issues detected - marking response")
                response_payload["content_moderation"] = True
                response_payload["moderation_details"] = {
                    "safe": moderation_result.get("safe", False),
                    "confidence": moderation_result.get("confidence", 0.0),
                    "categories": moderation_result.get("categories", []),
                    "message": moderation_result.get("message", "Content requires moderation")
                }
            else:
                print("[CloudFn] Content moderation check passed - content is safe")
                
        except Exception as e:
            print(f"[CloudFn] Error in content moderation: {str(e)}")
            # Don't fail the entire response due to moderation errors
            response_payload["content_moderation"] = False
            response_payload["moderation_error"] = str(e)

        # If a GCS destination was provided, write the JSON there
        if destination_gcs:
            try:
                _write_json_to_gcs(destination_gcs, response_payload)
            except Exception as gcs_exc:
                # Include GCS error in response but do not fail the analysis results
                print(gcs_exc)
                response_payload.setdefault("errors", {})["gcs_write_error"] = str(gcs_exc)

        return (json.dumps(response_payload), 200, {"Content-Type": "application/json"})

    except Exception as exc:  # pragma: no cover - defensive path
        error_payload = {"error": f"Unhandled error: {str(exc)}"}
        print(error_payload)
        return (json.dumps(error_payload), 500, {"Content-Type": "application/json"})

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


@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)

    print("Request Payload :",request_json)

    _, status, __ = mcp_analyze(request_json)
    return {
        "status" : status
    }