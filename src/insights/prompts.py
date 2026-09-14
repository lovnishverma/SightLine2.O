"""Prompt templates and structured JSON schemas for iNSIGHTS DeepSearch and Document Intelligence.
Follows the official iNSIGHTS Base44 Core InvokeLLM specification.
"""

from typing import Dict, Any

# Official DeepSearch JSON Schema for iNSIGHTS Core API
DEEP_SEARCH_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "voice_answer": {
            "type": "string",
            "description": "Short, natural, 2-3 sentence answer specifically formatted for voice text-to-speech without raw markdown or URLs."
        },
        "executive_summary": {
            "type": "string",
            "description": "Clear structured summary of findings for display on screen."
        },
        "key_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-5 verified bullet points of important factual takeaways."
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "source_type": {
                        "type": "string",
                        "enum": ["official_docs", "manual", "technical", "government", "research_paper", "news", "company", "community", "other"]
                    },
                    "confidence_score": {"type": "number"},
                    "snippet": {"type": "string"}
                },
                "required": ["title", "url"]
            }
        },
        "evidence_chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "chunk_text": {"type": "string"},
                    "source_title": {"type": "string"},
                    "relevance_score": {"type": "number"}
                }
            }
        },
        "knowledge_cluster": {
            "type": "object",
            "properties": {
                "model_or_brand": {"type": "string"},
                "category": {"type": "string"},
                "controls": {"type": "string"},
                "programs_or_modes": {"type": "array", "items": {"type": "string"}},
                "safety_guidelines": {"type": "string"},
                "troubleshooting": {"type": "string"},
                "manual_url": {"type": "string"}
            }
        },
        "confidence_score": {
            "type": "number",
            "description": "Confidence between 0.0 and 1.0"
        },
        "safety_disclaimer": {
            "type": "string",
            "description": "Safety or medical verification note if applicable, else empty string."
        },
        "suggested_followups": {
            "type": "array",
            "items": {"type": "string"}
        },
        "suggested_actions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["voice_answer", "key_facts", "sources", "confidence_score"]
}

# Document Intelligence JSON Schema for Notices, Circulars, and Forms
DOCUMENT_INTELLIGENCE_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": ["university_notice", "government_order", "application_form", "bill_or_receipt", "user_manual", "medical_prescription", "general_document"]
        },
        "title": {"type": "string"},
        "issuing_authority": {"type": "string"},
        "voice_summary": {
            "type": "string",
            "description": "Concise 2-3 sentence verbal overview emphasizing what the document is, key deadline, and required action."
        },
        "key_dates_and_deadlines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "event": {"type": "string"},
                    "date": {"type": "string"}
                }
            }
        },
        "required_documents_or_items": {
            "type": "array",
            "items": {"type": "string"}
        },
        "eligibility_or_criteria": {"type": "string"},
        "key_points": {
            "type": "array",
            "items": {"type": "string"}
        },
        "action_required": {
            "type": "string",
            "description": "Immediate next step for the user."
        },
        "confidence_score": {"type": "number"}
    },
    "required": ["document_type", "voice_summary", "key_dates_and_deadlines", "action_required", "confidence_score"]
}

def build_research_prompt(
    query: str,
    entity: str = "",
    visual_scene: str = "",
    ocr_text: str = "",
    previous_facts: list = None,
    language: str = "en"
) -> str:
    """Construct structured research prompt for iNSIGHTS DeepSearch."""
    facts_str = "\n".join(f"- {f}" for f in (previous_facts or [])) if previous_facts else "None"
    
    return f"""You are the iNSIGHTS DeepSearch engine powering SightLine, an assistive AI for blind and low-vision users.
Your goal is to conduct authoritative research on the user's inquiry based on visual context, OCR text, and web knowledge.

USER QUERY: "{query}"
DETECTED ENTITY / BRAND: "{entity}"
VISUAL SCENE: "{visual_scene}"
OCR TEXT DETECTED: "{ocr_text}"
PREVIOUSLY VERIFIED CONTEXT:
{facts_str}
REQUESTED OUTPUT LANGUAGE: {language}

CORE OPERATING PRINCIPLES:
1. VOICE-FIRST CLARITY: The 'voice_answer' MUST be concise, spoken-friendly (2-3 natural sentences max), free of markdown asterisks, hashes, brackets, or raw URLs.
2. EVIDENCE & SOURCES: Search and cite legitimate sources with real URLs and accurate titles. Distinguish official manufacturer documentation, government portals, or user manuals.
3. CONTEXTUAL APPLIANCES & HARDWARE: If the item is an appliance (e.g., washing machine, microwave, printer, AC), extract its model, common programs, control dial layout, and how to operate it safely.
4. SAFETY & MEDICAL CAUTION: Never provide medical diagnoses or guarantee safety. If medication or potential hazard is mentioned, explicitly include caution advising verification with a professional or pharmacist.
5. EXPLAIN IN REQUESTED LANGUAGE: If language is 'hi' (Hindi), ensure 'voice_answer' is rendered in natural spoken Hindi.
"""

def build_document_prompt(ocr_text: str, language: str = "en") -> str:
    """Construct document intelligence prompt for notices and papers."""
    return f"""You are the iNSIGHTS Document Intelligence engine powering SightLine for visually impaired users.
Analyze the following OCR text extracted from a physical notice, circular, form, or document.

OCR TEXT DETECTED:
\"\"\"
{ocr_text}
\"\"\"
REQUESTED LANGUAGE: {language}

TASK:
1. Identify the document type and issuing authority.
2. Synthesize a concise verbal summary ('voice_summary') in 2-3 sentences highlighting: What this is, any urgent deadlines/dates, and what the user must do next.
3. Extract all explicit dates, deadlines, and required documents as structured items.
4. If Hindi ('hi') is requested, provide the 'voice_summary' in clear Hindi.
"""
