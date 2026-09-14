"""Official Live Integration Provider for iNSIGHTS Platform.
Targets the verified Core InvokeLLM endpoint on Base44:
https://insights-ai.info/api/apps/6960af55d740f6d891a60e24/integration-endpoints/Core/InvokeLLM
"""

import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

from src.config import CONFIG
from src.insights.providers.base import ResearchProvider
from src.insights.models import (
    ResearchResult,
    Source,
    EvidenceChunk,
    KnowledgeCluster,
)
from src.insights.prompts import (
    build_research_prompt,
    build_document_prompt,
    DEEP_SEARCH_JSON_SCHEMA,
    DOCUMENT_INTELLIGENCE_JSON_SCHEMA,
)
from src.insights.exceptions import (
    InsightsError,
    InsightsTimeoutError,
    InsightsRateLimitError,
    InsightsUnavailableError,
    InsightsResponseError,
    InsightsAuthenticationError,
)

class InsightsLiveProvider(ResearchProvider):
    """Official live implementation of ResearchProvider for the iNSIGHTS platform."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        app_id: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 2
    ):
        self.endpoint = endpoint or CONFIG.INSIGHTS_ENDPOINT
        self.api_key = api_key if api_key is not None else CONFIG.INSIGHTS_API_KEY
        self.app_id = app_id or CONFIG.INSIGHTS_APP_ID
        self.timeout = timeout if timeout is not None else CONFIG.INSIGHTS_TIMEOUT
        self.max_retries = max_retries

    @property
    def name(self) -> str:
        return "iNSIGHTS DeepSearch (Official Core API)"

    def _post(self, payload: Dict[str, Any]) -> Any:
        """Execute HTTP POST with timeout, retries, exponential backoff, and typed exception mapping."""
        headers = {
            "Content-Type": "application/json",
            "X-App-Id": self.app_id,
            "User-Agent": "SightLine-Assistant/2.0 (Chitkara BuildWithBharat)"
        }
        if self.api_key and self.api_key.strip():
            headers["Authorization"] = f"Bearer {self.api_key.strip()}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=data, headers=headers, method="POST")

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        raw_body = resp.read().decode("utf-8")
                        try:
                            return json.loads(raw_body)
                        except json.JSONDecodeError as jde:
                            raise InsightsResponseError(f"Malformed JSON response: {jde}") from jde
                    elif resp.status in (401, 403):
                        raise InsightsAuthenticationError(f"HTTP {resp.status}: Unauthorized")
                    elif resp.status == 429:
                        raise InsightsRateLimitError("HTTP 429: Rate limit exceeded")
                    else:
                        raise InsightsUnavailableError(f"HTTP {resp.status} from iNSIGHTS")

            except urllib.error.HTTPError as he:
                if he.code in (401, 403):
                    raise InsightsAuthenticationError(f"Auth failed: {he.reason}") from he
                elif he.code == 429:
                    if attempt < self.max_retries:
                        time.sleep(1.0 * (attempt + 1))
                        continue
                    raise InsightsRateLimitError(f"Rate limited: {he.reason}") from he
                elif he.code in (500, 502, 503, 504):
                    last_error = InsightsUnavailableError(f"Server error {he.code}: {he.reason}")
                    if attempt < self.max_retries:
                        time.sleep(0.8 * (attempt + 1))
                        continue
                else:
                    last_error = InsightsError(f"HTTP Error {he.code}: {he.reason}")

            except urllib.error.URLError as ue:
                if "timed out" in str(ue.reason).lower():
                    last_error = InsightsTimeoutError(f"Request timeout ({self.timeout}s): {ue.reason}")
                else:
                    last_error = InsightsUnavailableError(f"Network error: {ue.reason}")
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue

            except TimeoutError as te:
                last_error = InsightsTimeoutError(f"Timeout ({self.timeout}s)")
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue

            except Exception as ex:
                if isinstance(ex, InsightsError):
                    raise ex
                last_error = InsightsError(f"Unexpected error calling iNSIGHTS: {ex}")

        if last_error:
            raise last_error
        raise InsightsUnavailableError("Failed to reach iNSIGHTS after retries")

    def research(
        self,
        query: str,
        entity: str = "",
        visual_scene: str = "",
        ocr_text: str = "",
        previous_facts: Optional[List[str]] = None,
        language: str = "en"
    ) -> ResearchResult:
        """Perform authoritative contextual research using iNSIGHTS DeepSearch with web context."""
        t_start = time.time()
        prompt = build_research_prompt(
            query=query,
            entity=entity,
            visual_scene=visual_scene,
            ocr_text=ocr_text,
            previous_facts=previous_facts,
            language=language
        )

        payload = {
            "model": CONFIG.INSIGHTS_MODEL,
            "add_context_from_internet": True,
            "prompt": prompt,
            "response_json_schema": DEEP_SEARCH_JSON_SCHEMA
        }

        raw = self._post(payload)
        latency = round(time.time() - t_start, 2)

        # Base44 Core InvokeLLM may return the structured object directly or inside a string
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                # If plain text returned
                return ResearchResult(
                    query=query,
                    entity=entity,
                    answer=raw.strip(),
                    confidence=0.85,
                    research_summary=raw.strip(),
                    latency_seconds=latency,
                    provider=self.name,
                    language=language
                )

        if not isinstance(raw, dict):
            raw = {}

        voice_answer = raw.get("voice_answer") or raw.get("answer") or "I analyzed the item and retrieved information."
        key_facts = raw.get("key_facts") or []
        exec_summary = raw.get("executive_summary") or voice_answer
        confidence = float(raw.get("confidence_score", 0.92))
        safety_note = raw.get("safety_disclaimer", "")

        if safety_note:
            voice_answer = f"{voice_answer} {safety_note}".strip()

        # Parse sources
        sources_list: List[Source] = []
        for s in raw.get("sources", [])[:CONFIG.INSIGHTS_MAX_SOURCES]:
            if isinstance(s, dict) and s.get("title") and s.get("url"):
                sources_list.append(Source(
                    title=s["title"],
                    url=s["url"],
                    author=s.get("author"),
                    publish_date=s.get("publish_date"),
                    source_type=s.get("source_type", "official_docs"),
                    confidence_score=float(s.get("confidence_score", 0.9)),
                    snippet=s.get("snippet")
                ))

        # Parse evidence chunks
        evidence_list: List[EvidenceChunk] = []
        for c in raw.get("evidence_chunks", []):
            if isinstance(c, dict) and c.get("chunk_text"):
                evidence_list.append(EvidenceChunk(
                    chunk_text=c["chunk_text"],
                    source_title=c.get("source_title", "Verified Source"),
                    relevance_score=float(c.get("relevance_score", 0.95))
                ))

        # Parse knowledge cluster
        kc_data = raw.get("knowledge_cluster") or {}
        kc = None
        if entity or kc_data:
            kc = KnowledgeCluster(
                entity_name=entity or kc_data.get("model_or_brand", "Target Object"),
                category=kc_data.get("category", "general"),
                attributes=kc_data,
                verified_facts=key_facts
            )

        return ResearchResult(
            query=query,
            entity=entity,
            answer=voice_answer,
            confidence=confidence,
            sources=sources_list,
            evidence_chunks=evidence_list,
            key_facts=key_facts,
            research_summary=exec_summary,
            provider=self.name,
            suggested_followups=raw.get("suggested_followups", []),
            suggested_actions=raw.get("suggested_actions", []),
            knowledge_cluster=kc,
            language=language,
            latency_seconds=latency
        )

    def analyze_document(
        self,
        ocr_text: str,
        document_type: str = "general",
        language: str = "en"
    ) -> ResearchResult:
        """Process document OCR text with iNSIGHTS Document Intelligence."""
        t_start = time.time()
        prompt = build_document_prompt(ocr_text=ocr_text, language=language)

        payload = {
            "model": CONFIG.INSIGHTS_MODEL,
            "add_context_from_internet": False,  # Local document RAG
            "prompt": prompt,
            "response_json_schema": DOCUMENT_INTELLIGENCE_JSON_SCHEMA
        }

        raw = self._post(payload)
        latency = round(time.time() - t_start, 2)

        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                raw = {"voice_summary": raw, "key_points": [], "key_dates_and_deadlines": []}

        if not isinstance(raw, dict):
            raw = {}

        voice_summary = raw.get("voice_summary") or "Document scanned."
        doc_type = raw.get("document_type", "Document")
        action = raw.get("action_required", "")
        if action:
            voice_summary = f"{voice_summary} Next step: {action}."

        key_facts = raw.get("key_points") or []
        deadlines = raw.get("key_dates_and_deadlines") or []
        req_docs = raw.get("required_documents_or_items") or []

        attributes = {
            "document_type": doc_type,
            "issuing_authority": raw.get("issuing_authority", "Unknown"),
            "deadlines": deadlines,
            "required_documents": req_docs,
            "action_required": action
        }

        kc = KnowledgeCluster(
            entity_name=raw.get("title") or doc_type.replace("_", " ").title(),
            category="document",
            attributes=attributes,
            verified_facts=key_facts
        )

        return ResearchResult(
            query="Analyze Document",
            entity=kc.entity_name,
            answer=voice_summary,
            confidence=float(raw.get("confidence_score", 0.92)),
            sources=[Source(title="Physical Document Scan (OCR)", url="#local-document", source_type="official_docs")],
            key_facts=key_facts,
            research_summary=f"**Type:** {doc_type}\n\n**Summary:** {voice_summary}",
            provider=self.name,
            suggested_followups=["What documents do I need to submit?", "When is the final deadline?"],
            suggested_actions=[action] if action else [],
            knowledge_cluster=kc,
            language=language,
            latency_seconds=latency
        )

    def search(self, query: str, limit: int = 5) -> List[Source]:
        """Search query to retrieve verified sources."""
        res = self.research(query=query)
        return res.sources[:limit]

    def create_knowledge_context(
        self,
        entity: str,
        facts: List[str],
        attributes: Optional[Dict[str, Any]] = None
    ) -> KnowledgeCluster:
        """Create structured KnowledgeCluster."""
        return KnowledgeCluster(
            entity_name=entity,
            attributes=attributes or {},
            verified_facts=facts
        )
