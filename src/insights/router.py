"""Deterministic, explainable, and testable Intelligence Router.
Decides whether a request is handled locally by SightLine's Florence-2 vision engine
or routed to iNSIGHTS DeepSearch research.
"""

import re
from typing import Optional
from src.insights.models import RouteDecision

class IntelligenceRouter:
    """Classifies user inquiries into Local Vision vs. iNSIGHTS DeepSearch Research."""

    # Explicit patterns indicating local perception questions
    LOCAL_PERCEPTION_PATTERNS = [
        r"\b(what|which)\s+color\b",
        r"\bis\s+the\s+(traffic\s+light|light|door|window|screen)\s+(red|green|yellow|open|closed|on|off)\b",
        r"\bhow\s+many\s+(people|chairs|doors|cars|cups|bottles|objects|items|stairs)\b",
        r"\bwhere\s+(is|are)\s+my\s+(keys|phone|wallet|glasses|cup|cane|bag|backpack)\b",
        r"\bis\s+there\s+any\s+(obstacle|step|stairs|curb|person|car|danger)\b",
        r"\bdescribe\s+(the\s+)?(room|scene|view|surroundings|environment)\b",
        r"\bwhat\s+(do\s+you\s+see|is\s+in\s+front\s+of\s+me)\b",
        r"\bread\s+this\s+text\b",
        r"\bjust\s+read\b",
        r"\bread\s+out\s+loud\b",
    ]

    # Explicit patterns requiring deep contextual knowledge / web research / manual inspection
    RESEARCH_INTENT_PATTERNS = [
        r"\bhow\s+do\s+i\s+(use|operate|start|turn\s+on|run|clean|fix|set\s+up)\b",
        r"\bhow\s+does\s+this\s+(work|operate|function)\b",
        r"\bfind\s+(the\s+)?(manual|guide|instructions|documentation)\b",
        r"\btell\s+me\s+more\s+about\b",
        r"\bwhat\s+does\s+(this\s+)?.*?(label|notice|circular|order|symbol|icon|error|code)\s+mean\b",
        r"\bwhat\s+does\s+this\s+mean\b",
        r"\b(meaning|purpose|implication)\s+of\b",
        r"\bis\s+this\s+(safe|dangerous|expired|toxic|edible)\b",
        r"\bmedicine|dosage|paracetamol|side\s+effect|tablet|prescription\b",
        r"\b(history|origin|background|specifications|features)\s+of\b",
        r"\bwhat\s+is\s+this\s+(historical|monument|landmark|building|heritage)\b",
        r"\bwhat\s+should\s+i\s+do\s+next\b",
        r"\bdeadline|last\s+date|eligibility|requirements|scholarship\b",
        r"\b(wash\s+program|cycle|error\s+e18|drain\s+pump|troubleshoot)\b",
        r"\bdeep\s+search|research\b",
        r"\bexplain\s+this\s+(notice|document|bill|receipt|form)\b",
    ]

    # Hindi patterns for research intent
    HINDI_RESEARCH_PATTERNS = [
        r"(kaise\s+use\s+kare|kaise\s+chalu\s+kare|kaise\s+chalaye|kaise\s+kaam\s+karta)",
        r"(iske\s+baare\s+mein\s+batao|aur\s+batao|vistaar\s+se\s+samjhao)",
        r"(yeh\s+surakshit\s+hai|kya\s+yeh\s+safe\s+hai)",
        r"(dawa|dawaii|paracetamol|khurak)",
        r"(antim\s+tithi|last\s+date|aavedan)",
        r"(manual\s+dhundo|instruction\s+batao)"
    ]

    def route(
        self,
        query: str,
        detected_text: str = "",
        scene_description: str = "",
        explicit_mode: Optional[str] = None
    ) -> RouteDecision:
        """Deterministically determine execution route: LOCAL_VISION vs. INSIGHTS_RESEARCH."""
        query_clean = query.strip()
        q_lower = query_clean.lower()
        dt_lower = detected_text.lower()
        sd_lower = scene_description.lower()

        # 1. Check explicit UI mode overrides
        if explicit_mode == "Research":
            return RouteDecision(
                route="INSIGHTS_RESEARCH",
                confidence=1.0,
                reason="Explicit 'Research' mode selected by user.",
                suggested_task_token="<VQA>"
            )
        elif explicit_mode == "Quick Glance":
            return RouteDecision(
                route="LOCAL_VISION",
                confidence=1.0,
                reason="Explicit 'Quick Glance' mode selected by user.",
                suggested_task_token="<CAPTION>"
            )
        elif explicit_mode == "Read Document":
            # If query asks for meaning/deadlines, use research; else local OCR
            if any(w in q_lower for w in ["deadline", "mean", "summary", "require", "explain", "next step", "samjhao"]):
                return RouteDecision(
                    route="INSIGHTS_RESEARCH",
                    confidence=0.95,
                    reason="Document analysis with deadline & requirement synthesis requested.",
                    suggested_task_token="<OCR>"
                )
            return RouteDecision(
                route="LOCAL_VISION",
                confidence=0.95,
                reason="Document reading mode for direct text extraction.",
                suggested_task_token="<OCR>"
            )

        # 2. Check for Local Perception inquiries (Colors, light status, spatial counting, presence)
        for pattern in self.LOCAL_PERCEPTION_PATTERNS:
            if re.search(pattern, q_lower):
                return RouteDecision(
                    route="LOCAL_VISION",
                    confidence=0.98,
                    reason=f"Direct visual observation requested: '{query_clean}' is best answered immediately via local vision sensors.",
                    suggested_task_token="<VQA>"
                )

        # 3. Check for Research Inquiries (Manuals, operations, medicine safety, notices, detailed context)
        for pattern in self.RESEARCH_INTENT_PATTERNS:
            if re.search(pattern, q_lower):
                # Extract potential entity from query, scene, or OCR
                entity = self.extract_entity_hint(q_lower, dt_lower, sd_lower)
                return RouteDecision(
                    route="INSIGHTS_RESEARCH",
                    confidence=0.96,
                    reason=f"Contextual inquiry requiring external knowledge: '{query_clean}' requires iNSIGHTS DeepSearch intelligence.",
                    extracted_entity=entity,
                    suggested_task_token="<VQA>"
                )

        # 4. Check Hindi research patterns
        for pattern in self.HINDI_RESEARCH_PATTERNS:
            if re.search(pattern, q_lower):
                entity = self.extract_entity_hint(q_lower, dt_lower, sd_lower)
                return RouteDecision(
                    route="INSIGHTS_RESEARCH",
                    confidence=0.95,
                    reason=f"Hindi contextual research inquiry: '{query_clean}' requires iNSIGHTS DeepSearch.",
                    extracted_entity=entity,
                    suggested_task_token="<VQA>"
                )

        # 5. Check contextual signals: if OCR detects an appliance or brand and user asks "What is this?" or "Tell me more"
        brand_match = re.search(r"\b(bosch|samsung|lg|whirlpool|sony|philips|panasonic|dell|hp|lenovo|ifb|godrej)\b", dt_lower + " " + sd_lower)
        if brand_match and any(w in q_lower for w in ["what", "this", "more", "how", "it"]):
            return RouteDecision(
                route="INSIGHTS_RESEARCH",
                confidence=0.92,
                reason=f"Identified appliance/brand '{brand_match.group(0).title()}'. Routing to iNSIGHTS to provide operating documentation and specifications.",
                extracted_entity=brand_match.group(0).title(),
                suggested_task_token="<VQA>"
            )

        # 6. Default fallback
        # If query is non-empty and starts with "why", "how", "explain", route to research
        if q_lower.startswith(("how", "why", "explain", "can i", "is it")):
            return RouteDecision(
                route="INSIGHTS_RESEARCH",
                confidence=0.88,
                reason=f"Inquiry '{query_clean}' requires explanatory reasoning and external verification.",
                suggested_task_token="<VQA>"
            )

        # Otherwise answer locally via Florence-2 VQA / captioning
        return RouteDecision(
            route="LOCAL_VISION",
            confidence=0.85,
            reason="Standard visual inquiry suited for local Florence-2 inference.",
            suggested_task_token="<VQA>" if query_clean else "<DETAILED_CAPTION>"
        )

    @staticmethod
    def extract_entity_hint(query: str, ocr_text: str, scene: str) -> str:
        """Extract primary entity candidate from text signals."""
        # Check brand or product name in OCR or scene
        brands = ["bosch", "samsung", "lg", "whirlpool", "sony", "philips", "panasonic", "paracetamol", "dell", "hp", "ifb"]
        for b in brands:
            if b in ocr_text or b in scene or b in query:
                return b.title()
        
        # Check if appliance words exist
        appliances = ["washing machine", "microwave", "refrigerator", "oven", "dishwasher", "air conditioner", "router", "printer"]
        for app in appliances:
            if app in scene or app in query or app in ocr_text:
                return app.title()

        return ""
