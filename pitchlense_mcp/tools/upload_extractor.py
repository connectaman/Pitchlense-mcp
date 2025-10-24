"""
Upload extractor tool that uses Gemini LLM analyzers and Perplexity to build startup_text.

Workflow:
- Accepts a list of local files with metadata (name/type/extension/path).
- Uses the appropriate Gemini analyzer (text, image, audio, video, document) to extract
  structured textual context per file.
- Calls Perplexity multiple times to synthesize a comprehensive startup_text string from
  the collected contexts.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from ..core.gemini_client import GeminiLLM
from .perplexity_search import PerplexityMCPTool


def _guess_mime_from_extension(ext: str) -> str:
    ext = (ext or "").lower().lstrip(".")
    if ext in {"pdf"}:
        return "application/pdf"
    if ext in {"docx"}:
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if ext in {"pptx"}:
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    if ext in {"txt", "md", "csv", "json"}:
        return "text/plain"
    if ext in {"jpg", "jpeg"}:
        return "image/jpeg"
    if ext in {"png"}:
        return "image/png"
    if ext in {"mp3"}:
        return "audio/mp3"
    if ext in {"wav"}:
        return "audio/wav"
    if ext in {"mp4"}:
        return "video/mp4"
    if ext in {"mov"}:
        return "video/quicktime"
    return "application/octet-stream"


class UploadExtractor:
    """Extracts textual context from uploaded files and synthesizes startup_text."""

    def __init__(self, llm_client: GeminiLLM):
        self.llm = llm_client

    def _extract_text_from_plainfile(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
        except Exception:
            raw = ""
        if not raw:
            return ""
        prompt = (
            "Extract key startup-relevant details from the following text. "
            "Return a concise summary covering company, product, customers, metrics, risks, and plans.\n\n" + raw
        )
        resp = self.llm.predict(
            system_message="You are a precise analyst extracting startup-relevant context. Maintain professional language and avoid inappropriate content. Focus strictly on business information.",
            user_message=prompt,
        )
        return resp.get("response", "")

    def _extract_from_document(self, file_path: str, mime_type: str) -> str:
        try:
            result = self.llm.document_analyzer.predict(
                document_path=file_path,
                prompt=(
                    "Extract ALL text content from this document completely. Perform OCR on any images, "
                    "charts, tables, or visual elements to extract text. Present tables in a structured "
                    "text format with clear column headers and data. For charts and graphs, describe "
                    "the data and extract any visible text or numbers. Include all headers, footers, "
                    "captions, and annotations. After extracting all content, provide a comprehensive "
                    "summary focusing on startup-relevant details: company information, market analysis, "
                    "product details, traction metrics, financials, team information, risks, and roadmap. "
                    "Maintain professional language and avoid inappropriate content. Focus strictly on business information."
                ),
                mime_type=mime_type or "application/pdf",
            )
            return result.get("text", "")
        except Exception as e:
            return f"Document analysis failed: {str(e)}"

    def _extract_from_image(self, file_path: str, mime_type: str) -> str:
        try:
            result = self.llm.image_analyzer.predict(
                image_input=file_path,
                prompt=(
                    "Perform OCR to extract ALL text visible in this image, including text overlays, "
                    "labels, captions, and any written content. If there are tables, present them in "
                    "a structured text format with clear column headers and data. If there are charts, "
                    "graphs, or diagrams, describe the visual data and extract any numbers, percentages, "
                    "or metrics shown. Identify and describe all visual elements including: product screenshots, "
                    "logos, team photos, charts, graphs, tables, infographics, and any other visual content. "
                    "Provide a comprehensive analysis focusing on startup-relevant information: company details, "
                    "product features, metrics, team information, and business data. "
                    "Maintain professional language and avoid inappropriate content. Focus strictly on business information."
                ),
                mime_type=mime_type or "image/jpeg",
            )
            return result.get("text", "")
        except Exception as e:
            return f"Image analysis failed: {str(e)}"

    def _extract_from_audio(self, file_path: str, mime_type: str) -> str:
        try:
            result = self.llm.audio_analyzer.predict(
                audio_input=file_path,
                prompt=(
                    "Transcribe this audio content completely. Provide a word-for-word transcription "
                    "of all spoken content, including any pauses, speaker changes, or background audio. "
                    "If multiple speakers are present, identify them clearly. After the transcription, "
                    "provide a summary focusing on startup-relevant details: company information, "
                    "product details, traction metrics, financials, risks, and future roadmap."
                ),
                mime_type=mime_type or "audio/mp3",
            )
            return result.get("text", "")
        except Exception as e:
            return f"Audio analysis failed: {str(e)}"

    def _extract_from_video(self, file_path: str, mime_type: str) -> str:
        try:
            result = self.llm.video_analyzer.predict(
                video_input=file_path,
                prompt=(
                    "First, transcribe all spoken content in this video completely. Provide a word-for-word "
                    "transcription of all dialogue, including speaker identification if multiple speakers are present. "
                    "Then, analyze and describe all visual information including: text overlays, charts, graphs, "
                    "tables, diagrams, slides, product screenshots, logos, and any other visual elements. "
                    "Present tables and charts in a structured text format. Extract any text visible in the video. "
                    "Finally, provide a comprehensive summary focusing on startup-relevant details: company information, "
                    "product details, traction metrics, financials, risks, and future roadmap."
                ),
                mime_type=mime_type or "video/mp4",
            )
            return result.get("text", "")
        except Exception as e:
            return f"Video analysis failed: {str(e)}"

    def extract_documents(self, uploads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract content from a list of uploaded local files.

        Each upload dict should have keys: filename, file_extension, local_path, filetype (optional).
        """
        documents: List[Dict[str, Any]] = []
        for u in uploads:
            filename = u.get("filename") or os.path.basename(u.get("local_path", ""))
            ext = (u.get("file_extension") or os.path.splitext(filename or "")[1].lstrip(".")).lower()
            local_path = u.get("local_path")
            filetype = u.get("filetype") or ""
            mime = _guess_mime_from_extension(ext)

            extracted = ""
            if mime.startswith("image/"):
                extracted = self._extract_from_image(local_path, mime)
            elif mime.startswith("video/"):
                extracted = self._extract_from_video(local_path, mime)
            elif mime.startswith("audio/"):
                extracted = self._extract_from_audio(local_path, mime)
            elif mime == "text/plain":
                extracted = self._extract_text_from_plainfile(local_path)
            else:
                # Treat as document by default
                extracted = self._extract_from_document(local_path, mime)

            documents.append({
                "name": filename,
                "type": filetype or mime,
                "extension": ext,
                "mime_type": mime,
                "content": extracted,
            })

        return documents

    def synthesize_startup_text(self, documents: List[Dict[str, Any]]) -> str:
        """Run 10 Perplexity calls in parallel (one per section) and concatenate results."""
        if not documents:
            return ""
        # Build a compact context string
        pieces: List[str] = []
        for doc in documents:
            name = doc.get("name")
            dtype = doc.get("type")
            content = (doc.get("content") or "").strip()
            if not content:
                continue
            pieces.append(f"Document: {name} (type: {dtype})\nContent:\n{content}\n---\n")
        base_context = "\n".join(pieces)
        try:
            print(f"[Extractor] Documents with content: {len(pieces)}; base_context_len={len(base_context)}")
        except Exception:
            pass

        sections: List[Tuple[int, str, str]] = [
            (
                1,
                "Startup name, industry, founder names, Founded year, Location, Stage, Industry",
                (
                    "Provide a precise, structured paragraph covering these fields. Include known brand names, "
                    "legal entity (if any), website/domain, and short one-line positioning."
                ),
            ),
            (
                2,
                "Business model",
                (
                    "Explain clearly how the startup makes money (pricing, plans, ARPU, sales motion, channels). "
                    "Include ICP (ideal customer profile), buyer persona, and key activation/retention levers."
                ),
            ),
            (
                3,
                "Product or what that startup is about",
                (
                    "Describe the product and problem-solution. List core features, notable differentiators, "
                    "tech stack (if known), key integrations/APIs, and deployment (cloud/on-prem/mobile)."
                ),
            ),
            (
                4,
                "Financial Information",
                (
                    "Summarize revenue (MRR/ARR), growth, gross margin (if known), burn, runway, funding history, "
                    "valuation (if public), unit economics (CAC, LTV, payback), and notable KPIs."
                ),
            ),
            (
                5,
                "Traction & Customers",
                (
                    "Cover users/customers, cohorts, growth rates, churn, NRR, expansion/upsell, notable logos, "
                    "use cases, and adoption by segment/geo where known."
                ),
            ),
            (
                6,
                "Team",
                (
                    "Summarize founders and key team (names, prior roles/companies), headcount by function, "
                    "hiring plan, board/advisors (if any), and organizational strengths."
                ),
            ),
            (
                7,
                "Market & Competition",
                (
                    "Summarize TAM/SAM/SOM (with sources if available), market growth, demand drivers, "
                    "competitors (direct/indirect), a brief competition matrix, and differentiation/moat."
                ),
            ),
            (
                8,
                "Recent News & Updates",
                (
                    "List notable news, launches, partnerships, regulatory items, and product updates with dates "
                    "and links where possible."
                ),
            ),
            (
                9,
                "Challenges & Risks",
                (
                    "Identify top risks across product, market, competitive, legal, operational, financial, "
                    "and team categories, with 1-2 actionable recommendations each."
                ),
            ),
            (
                10,
                "Future Plans",
                (
                    "Summarize roadmap (near/medium term), GTM plans, hiring, geographic expansion, "
                    "and key milestones/OKRs."
                ),
            ),
        ]

        # Build prompts per section
        def build_prompt(title: str, instruction: str) -> str:
            return (
                "You are a research assistant with web access. Using the context below and web search where helpful, "
                f"write the section: {title}. {instruction} If unknown, state unknown. Prefer precise data. "
                "Keep to 200-300 words. Provide inline URLs if citing external info.\n\n"
                "Context:\n" + base_context
            )

        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Require Perplexity and do not fallback to Gemini
        if not os.getenv("PERPLEXITY_API_KEY"):
            raise RuntimeError("PERPLEXITY_API_KEY not set; cannot synthesize with Perplexity")

        results_map: Dict[int, str] = {}
        # Run Perplexity calls in parallel
        with ThreadPoolExecutor(max_workers=len(sections)) as executor:
            future_to_idx = {}
            for idx, title, instruction in sections:
                prompt = build_prompt(title, instruction)
                # Create a new tool per call to avoid shared state
                ppx = PerplexityMCPTool()
                future = executor.submit(lambda p=prompt, t=ppx: t.search_perplexity(p))
                future_to_idx[future] = idx

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    resp = future.result()
                    err = resp.get("error") if isinstance(resp, dict) else None
                    ans = (resp.get("answer") or "").strip() if isinstance(resp, dict) else ""
                    results_map[idx] = ans
                    try:
                        print(f"[Extractor] Section {idx}: answer_len={len(ans)} error={bool(err)}")
                    except Exception:
                        pass
                except Exception as exc:
                    results_map[idx] = ""

        # If Perplexity produced no content at all, raise an error
        non_empty_sections = sum(1 for v in results_map.values() if (v or "").strip())
        if non_empty_sections == 0:
            raise RuntimeError("Perplexity returned no answers for any section")

        # Concatenate in order with headings
        ordered: List[str] = []
        for idx, title, _ in sections:
            section_text = results_map.get(idx, "")
            header = f"{idx}. {title}"
            ordered.append(header + "\n" + section_text)

        synthesized_text = "\n\n".join(ordered).strip()

        # Combine extracted content + synthesized sections to build final startup_text
        combined = (
            "Extracted Document Content\n" + base_context.strip() +
            "\n\n---\n\n" +
            "Synthesis\n" + synthesized_text
        ).strip()
        return combined


