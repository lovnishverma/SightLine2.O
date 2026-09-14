"""High-Fidelity Mock Research Provider for offline development, CI/CD, and fallback testing.
Provides deterministic, source-backed responses for appliances, documents, and medicines.
"""

import time
from typing import List, Dict, Any, Optional

from src.insights.providers.base import ResearchProvider
from src.insights.models import (
    ResearchResult,
    Source,
    EvidenceChunk,
    KnowledgeCluster,
)

class MockResearchProvider(ResearchProvider):
    """Offline development and test mock provider."""

    @property
    def name(self) -> str:
        return "iNSIGHTS Research (Mock Adapter)"

    def research(
        self,
        query: str,
        entity: str = "",
        visual_scene: str = "",
        ocr_text: str = "",
        previous_facts: Optional[List[str]] = None,
        language: str = "en"
    ) -> ResearchResult:
        t_start = time.time()
        q_lower = query.lower()
        e_lower = (entity + " " + visual_scene + " " + ocr_text).lower()

        # 1. Appliance / Washing Machine match
        if any(w in q_lower or w in e_lower for w in ["bosch", "washing machine", "washer", "quick wash", "cycle", "appliance"]):
            if "hi" in language.lower():
                voice_answer = "यह बॉश सीरीज 6 फ्रंट-लोड वाशिंग मशीन है। इसमें 15 मिनट का सुपर क्विक वॉश प्रोग्राम और इको-साइलेंस मोटर मौजूद है। शुरू करने के लिए मुख्य डायल को सुपर 15 पर घुमाएं और स्टार्ट बटन दबाएं।"
            else:
                voice_answer = "This is a Bosch Series 6 front-load washing machine. It features a 15-minute quick wash program and an EcoSilence motor. Turn the dial to Super 15 and press the Start button to begin."

            sources = [
                Source(
                    title="Bosch Series 6 Washing Machine User Manual",
                    url="https://media3.bosch-home.com/docs/manuals/bosch-series-6.pdf",
                    source_type="manual",
                    confidence_score=0.98,
                    snippet="Program selector with integrated On/Off switch. Super 15'/30' short program."
                ),
                Source(
                    title="Bosch Home Appliances Official Specification Sheet",
                    url="https://www.bosch-home.in/specifications/series-6-washer",
                    source_type="official_docs",
                    confidence_score=0.96,
                    snippet="EcoSilence Drive brushless motor with ActiveWater Plus load management."
                ),
                Source(
                    title="Home Appliance Troubleshooting Guide",
                    url="https://support.bosch-home.com/troubleshooting/washing-machines",
                    source_type="technical",
                    confidence_score=0.91,
                    snippet="Error E18 indicates drain pump blockage or obstructed filter."
                )
            ]

            evidence = [
                EvidenceChunk(
                    chunk_text="Turn rotary dial to 'Super 15' / 'Super 30' for quick wash. Ensure tap is open and door is latched.",
                    source_title="Bosch Series 6 Washing Machine User Manual",
                    relevance_score=0.99
                ),
                EvidenceChunk(
                    chunk_text="AntiVibration design provides increased stability and quiet operation.",
                    source_title="Bosch Home Appliances Official Specification Sheet",
                    relevance_score=0.92
                )
            ]

            key_facts = [
                "Identified model: Bosch Series 6 Front-Loader with 8-9 kg drum capacity.",
                "Quick Programs: Super 15' (15 min) and Super 30' (30 min) for light loads.",
                "Control layout: Central rotary dial for cycle selection, capacitive touch panel on right.",
                "Safety: Child lock can be engaged by holding the SpeedPerfect button for 3 seconds."
            ]

            kc = KnowledgeCluster(
                entity_name="Bosch Series 6 Washing Machine",
                category="appliance",
                attributes={
                    "brand": "Bosch",
                    "model": "Series 6 (WGG244ARAU / Equivalent)",
                    "controls": "Rotary program selector with digital LED touch screen",
                    "programs": ["Super 15/30", "Cottons Eco", "Delicates", "AllergyPlus", "Drum Clean"],
                    "safety": "Child lock, overflow protection, AntiVibration side panels",
                    "maintenance": "Clean drain pump filter quarterly at bottom-right compartment",
                    "manual_url": "https://media3.bosch-home.com/docs/manuals/bosch-series-6.pdf"
                },
                verified_facts=key_facts
            )

            return ResearchResult(
                query=query,
                entity="Bosch Washing Machine",
                answer=voice_answer,
                confidence=0.96,
                sources=sources,
                evidence_chunks=evidence,
                key_facts=key_facts,
                research_summary="Verified Bosch Series 6 operating specifications, quick-wash parameters, and control layout from official documentation.",
                provider=self.name,
                suggested_followups=["How do I run the drum cleaning cycle?", "What does error E18 mean?", "How do I activate child lock?"],
                suggested_actions=["Turn dial to Super 15", "Press capacitive Start button"],
                knowledge_cluster=kc,
                language=language,
                latency_seconds=round(time.time() - t_start, 2)
            )

        # 2. Medicine / Paracetamol match
        elif any(w in q_lower or w in e_lower for w in ["medicine", "paracetamol", "tablet", "pill", "syrup", "dosage"]):
            if "hi" in language.lower():
                voice_answer = "यह पैरासिटामोल 500 मिलीग्राम प्रतीत होता है, जो दर्द और बुखार के लिए प्रयोग किया जाता है। कृपया इसे लेने से पहले किसी डॉक्टर या फार्मासिस्ट से लेबल की पुष्टि अवश्य कर लें।"
            else:
                voice_answer = "This appears to be Paracetamol 500 mg, commonly used for mild-to-moderate pain and fever. Please verify the label and proper dosage with a doctor or pharmacist before consumption."

            sources = [
                Source(
                    title="NHS Medicine Guides - Paracetamol for Adults",
                    url="https://www.nhs.uk/medicines/paracetamol-for-adults/",
                    source_type="government",
                    confidence_score=0.99,
                    snippet="Paracetamol is a common painkiller for treating aches and pain and reducing fever."
                ),
                Source(
                    title="World Health Organization Model List of Essential Medicines",
                    url="https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02",
                    source_type="research_paper",
                    confidence_score=0.97,
                    snippet="Analgesic and antipyretic agent recommended for first-line pain management."
                )
            ]

            key_facts = [
                "Primary use: Pain relief (analgesic) and fever reduction (antipyretic).",
                "Standard adult dose: 500 mg to 1000 mg every 4 to 6 hours (maximum 4000 mg in 24 hours).",
                "Safety warning: High risk of liver damage if combined with other paracetamol products or alcohol."
            ]

            return ResearchResult(
                query=query,
                entity="Paracetamol 500mg",
                answer=voice_answer,
                confidence=0.91,
                sources=sources,
                key_facts=key_facts,
                research_summary="Retrieved clinical indications and safety warnings for Paracetamol from authoritative health registries.",
                provider=self.name,
                suggested_followups=["What are common side effects?", "Can I take this with food?"],
                language=language,
                latency_seconds=round(time.time() - t_start, 2)
            )

        # 3. Generic fallback
        else:
            ent = entity or "Target Object"
            if "hi" in language.lower():
                voice_answer = f"मैंने {ent} के बारे में जानकारी प्राप्त की है। क्या आप इसके उपयोग या सुरक्षा के बारे में विस्तार से जानना चाहते हैं?"
            else:
                voice_answer = f"I retrieved verified documentation for {ent}. Would you like me to explain how to operate it or check safety instructions?"

            sources = [
                Source(
                    title=f"{ent} Technical Documentation & Overview",
                    url="https://docs.insights-ai.info/verified-entity",
                    source_type="official_docs",
                    confidence_score=0.88,
                    snippet=f"Authoritative specifications and user guidance for {ent}."
                )
            ]

            key_facts = [
                f"Identified entity: {ent}",
                "General operational guidance retrieved from verified public databases.",
                "Ready for contextual follow-up questions."
            ]

            return ResearchResult(
                query=query,
                entity=ent,
                answer=voice_answer,
                confidence=0.89,
                sources=sources,
                key_facts=key_facts,
                research_summary=f"Contextual intelligence retrieved for {ent}.",
                provider=self.name,
                suggested_followups=["How does this work?", "Is this safe?", "Explain in Hindi"],
                language=language,
                latency_seconds=round(time.time() - t_start, 2)
            )

    def analyze_document(
        self,
        ocr_text: str,
        document_type: str = "general",
        language: str = "en"
    ) -> ResearchResult:
        t_start = time.time()
        text_lower = ocr_text.lower()

        # University / Scholarship Notice match
        if any(w in text_lower for w in ["scholarship", "university", "admission", "deadline", "application", "chitkara", "bharat"]):
            if "hi" in language.lower():
                voice_summary = "यह छात्रवृत्ति आवेदन की सूचना है। आवेदन जमा करने की अंतिम तिथि 20 सितंबर है। आवश्यक दस्तावेजों में मार्कशीट, पहचान पत्र और बैंक विवरण शामिल हैं।"
            else:
                voice_summary = "This notice announces a merit scholarship application. The deadline is September 20th. Required documents include your academic marksheet, identity proof, and bank passbook."

            deadlines = [{"event": "Online Application Submission", "date": "September 20, 2026"}]
            req_docs = ["Academic Marksheet", "Government ID Proof (Aadhaar / Voter ID)", "Bank Account Details"]
            action = "Submit online application form with required documents before 5 PM on September 20."

            kc = KnowledgeCluster(
                entity_name="University Scholarship Notice",
                category="document",
                attributes={
                    "document_type": "university_notice",
                    "deadlines": deadlines,
                    "required_documents": req_docs,
                    "action_required": action
                },
                verified_facts=[
                    "Notice Type: Merit-cum-Means Scholarship circular.",
                    "Final Deadline: September 20, 2026 at 17:00 IST.",
                    "Mandatory attachments: Marksheet, Student ID, Bank Passbook."
                ]
            )

            return ResearchResult(
                query="Analyze Document",
                entity="Scholarship Application Notice",
                answer=voice_summary,
                confidence=0.97,
                sources=[Source(title="Physical Notice OCR Scan", url="#local-notice", source_type="official_docs")],
                key_facts=kc.verified_facts,
                research_summary=f"**Type:** Scholarship Notice\n\n**Deadline:** September 20, 2026\n\n**Action:** {action}",
                provider=self.name,
                suggested_followups=["What are the eligibility criteria?", "Where do I submit the hard copy?"],
                suggested_actions=[action],
                knowledge_cluster=kc,
                language=language,
                latency_seconds=round(time.time() - t_start, 2)
            )

        else:
            # Generic Document
            if "hi" in language.lower():
                voice_summary = "यह एक आधिकारिक दस्तावेज प्रतीत होता है। इसमें आवश्यक निर्देश और दिशानिर्देश शामिल हैं।"
            else:
                voice_summary = "This document contains official notices and guidelines. Please review the highlighted deadlines and instructions."

            return ResearchResult(
                query="Analyze Document",
                entity="Scanned Document",
                answer=voice_summary,
                confidence=0.90,
                sources=[Source(title="Document OCR Scan", url="#document", source_type="official_docs")],
                key_facts=["Document text processed via high-precision OCR."],
                research_summary="OCR extraction complete.",
                provider=self.name,
                language=language,
                latency_seconds=round(time.time() - t_start, 2)
            )

    def search(self, query: str, limit: int = 5) -> List[Source]:
        res = self.research(query=query)
        return res.sources[:limit]

    def create_knowledge_context(
        self,
        entity: str,
        facts: List[str],
        attributes: Optional[Dict[str, Any]] = None
    ) -> KnowledgeCluster:
        return KnowledgeCluster(entity_name=entity, attributes=attributes or {}, verified_facts=facts)
