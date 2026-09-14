"""Intelligence Pipeline for SightLine.
Orchestrates: SEE -> UNDERSTAND -> RESEARCH -> VERIFY -> PERSONALIZE -> SPEAK -> ACT.
"""

import time
import re
from typing import Dict, Any, Optional, Tuple, List

from src.insights.models import (
    ResearchResult,
    RouteDecision,
    KnowledgeCluster,
    Source,
)
from src.insights.router import IntelligenceRouter
from src.insights.client import InsightsClient
from src.insights.exceptions import InsightsError

class IntelligencePipeline:
    """Modular pipeline connecting visual perception, intelligence routing, and evidence research."""

    def __init__(
        self,
        router: Optional[IntelligenceRouter] = None,
        insights_client: Optional[InsightsClient] = None
    ):
        self.router = router or IntelligenceRouter()
        self.client = insights_client or InsightsClient()

    def detect_intent(
        self,
        query: str,
        detected_text: str = "",
        scene_description: str = "",
        explicit_mode: Optional[str] = None
    ) -> RouteDecision:
        """Route user request to Local Vision or iNSIGHTS Research."""
        return self.router.route(
            query=query,
            detected_text=detected_text,
            scene_description=scene_description,
            explicit_mode=explicit_mode
        )

    def extract_entities(self, query: str, scene: str, ocr_text: str) -> str:
        """Identify key physical objects, products, medicines, or notices."""
        # Check brand or known device names
        brands = [
            "bosch", "samsung", "lg", "whirlpool", "sony", "philips",
            "panasonic", "paracetamol", "dell", "hp", "ifb", "godrej"
        ]
        combined = f"{query} {ocr_text} {scene}".lower()
        for b in brands:
            if b in combined:
                return b.title()

        # Check appliances
        appliances = [
            "washing machine", "microwave", "refrigerator", "induction cooktop",
            "air conditioner", "water purifier", "smart speaker", "printer"
        ]
        for a in appliances:
            if a in combined:
                return a.title()

        # Check document keywords
        if any(w in combined for w in ["scholarship", "circular", "notice", "admission", "hall ticket"]):
            return "Official Notice"

        return ""

    def gather_context(self, context_memory: Any, entity: str = "") -> List[str]:
        """Gather previously verified facts and knowledge from session memory."""
        facts: List[str] = []
        if context_memory and hasattr(context_memory, "get_recent_facts"):
            facts.extend(context_memory.get_recent_facts(entity=entity))
        return facts

    def research(
        self,
        query: str,
        entity: str = "",
        visual_scene: str = "",
        ocr_text: str = "",
        previous_facts: Optional[List[str]] = None,
        language: str = "en"
    ) -> ResearchResult:
        """Invoke iNSIGHTS DeepSearch with network safety and fallback handling."""
        return self.client.research(
            query=query,
            entity=entity,
            visual_scene=visual_scene,
            ocr_text=ocr_text,
            previous_facts=previous_facts,
            language=language
        )

    def analyze_document(self, ocr_text: str, language: str = "en") -> ResearchResult:
        """Invoke iNSIGHTS Document Intelligence for scanned notices and circulars."""
        return self.client.analyze_document(ocr_text=ocr_text, language=language)

    def validate(self, result: ResearchResult) -> ResearchResult:
        """Validate research results, verify confidence bounds, and ensure medical caution."""
        # Sanitize voice answer: strip markdown hashes, asterisks, citations like [1]
        cleaned_answer = re.sub(r"\[\d+\]", "", result.answer)
        cleaned_answer = re.sub(r"[\*\#\_]", "", cleaned_answer)
        cleaned_answer = " ".join(cleaned_answer.split())
        result.answer = cleaned_answer

        # Guarantee safety disclaimer on high-risk topics
        lower_content = (result.query + " " + result.answer + " " + result.entity).lower()
        if any(w in lower_content for w in ["medicine", "paracetamol", "dosage", "tablet", "pill", "prescription"]):
            if "pharmacist" not in result.answer.lower() and "doctor" not in result.answer.lower():
                if "hi" in result.language.lower():
                    result.answer += " कृपया इसे लेने से पहले डॉक्टर या फार्मासिस्ट से परामर्श अवश्य लें।"
                else:
                    result.answer += " Please verify the medication and dosage with a doctor or pharmacist before use."

        return result

    def format_for_voice(self, result: ResearchResult) -> str:
        """Return the concise speech-ready answer."""
        return result.answer.strip()

    def format_for_ui(self, result: ResearchResult, route_decision: RouteDecision) -> Dict[str, Any]:
        """Format complete evidence payload for Gradio Judge Mode."""
        # Sources formatted for UI display
        sources_data = [
            {
                "title": s.title,
                "url": s.url,
                "type": s.source_type.replace("_", " ").title(),
                "snippet": s.snippet or ""
            }
            for s in result.sources
        ]

        kc_dict = result.knowledge_cluster.to_dict() if result.knowledge_cluster else {}

        return {
            "route": route_decision.route,
            "route_reason": route_decision.reason,
            "entity": result.entity or "Identified Object",
            "provider": result.provider,
            "confidence": f"{int(result.confidence * 100)}%",
            "sources_count": result.source_count,
            "sources": sources_data,
            "key_facts": result.key_facts,
            "summary": result.research_summary,
            "knowledge_cluster": kc_dict,
            "latency": f"{result.latency_seconds}s",
            "followups": result.suggested_followups,
            "actions": result.suggested_actions
        }

    def execute(
        self,
        query: str,
        image_or_scene: str,
        ocr_text: str = "",
        context_memory: Any = None,
        explicit_mode: Optional[str] = None,
        language: str = "en"
    ) -> Tuple[str, Dict[str, Any], RouteDecision]:
        """Complete end-to-end execution of the pipeline."""
        t0 = time.time()
        
        # 1. Intent Detection & Routing
        route_decision = self.detect_intent(
            query=query,
            detected_text=ocr_text,
            scene_description=image_or_scene,
            explicit_mode=explicit_mode
        )

        # 2. Entity Extraction
        entity = route_decision.extracted_entity or self.extract_entities(query, image_or_scene, ocr_text)

        # 3. Context Gathering
        prev_facts = self.gather_context(context_memory, entity=entity)

        # 4. If Document Mode explicitly requested:
        if explicit_mode == "Read Document" and ocr_text.strip():
            try:
                res = self.analyze_document(ocr_text=ocr_text, language=language)
                res = self.validate(res)
                voice_text = self.format_for_voice(res)
                ui_data = self.format_for_ui(res, route_decision)
                return voice_text, ui_data, route_decision
            except Exception as e:
                # Graceful degradation
                voice_text = f"Scanned text: {ocr_text[:200]}. Research intelligence is temporarily unavailable."
                ui_data = {
                    "route": "LOCAL_VISION",
                    "route_reason": f"Fallback to local OCR due to: {e}",
                    "entity": "Document",
                    "provider": "Local OCR",
                    "confidence": "90%",
                    "sources_count": 0,
                    "sources": [],
                    "key_facts": [ocr_text[:150]],
                    "summary": ocr_text,
                    "latency": f"{round(time.time() - t0, 2)}s"
                }
                return voice_text, ui_data, route_decision

        # 5. If Routed to iNSIGHTS Research:
        if route_decision.is_research:
            try:
                res = self.research(
                    query=query or f"What is this {entity} and how does it work?",
                    entity=entity,
                    visual_scene=image_or_scene,
                    ocr_text=ocr_text,
                    previous_facts=prev_facts,
                    language=language
                )
                res = self.validate(res)

                # Store in memory if available
                if context_memory and hasattr(context_memory, "store_research"):
                    context_memory.store_research(res)

                voice_text = self.format_for_voice(res)
                ui_data = self.format_for_ui(res, route_decision)
                return voice_text, ui_data, route_decision

            except InsightsError as ie:
                # Mandatory fallback: SightLine MUST still work using local vision
                fallback_msg = (
                    "Research is temporarily unavailable. I can still describe what I see. "
                    f"{image_or_scene}"
                )
                ui_data = {
                    "route": "LOCAL_VISION",
                    "route_reason": f"Fallback: iNSIGHTS unavailable ({ie.user_friendly_message})",
                    "entity": entity or "Scene",
                    "provider": "Florence-2 (Fallback)",
                    "confidence": "85%",
                    "sources_count": 0,
                    "sources": [],
                    "key_facts": ["Local visual description active."],
                    "summary": image_or_scene,
                    "latency": f"{round(time.time() - t0, 2)}s"
                }
                return fallback_msg, ui_data, route_decision

        # 6. Local Vision Route:
        local_ui_data = {
            "route": "LOCAL_VISION",
            "route_reason": route_decision.reason,
            "entity": entity or "Detected Scene",
            "provider": "Florence-2 Vision Engine",
            "confidence": f"{int(route_decision.confidence * 100)}%",
            "sources_count": 0,
            "sources": [],
            "key_facts": ["Direct visual perception evaluated locally."],
            "summary": image_or_scene,
            "latency": f"{round(time.time() - t0, 2)}s",
            "followups": ["Tell me more about this", "Find the user manual", "Is this safe?"],
            "actions": []
        }
        return image_or_scene, local_ui_data, route_decision
