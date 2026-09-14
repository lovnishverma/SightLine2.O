"""Tests for Document Intelligence and notice parsing.
"""

from src.insights.providers.mock import MockResearchProvider

def test_scholarship_notice_extraction():
    provider = MockResearchProvider()
    ocr_sample = """
    CHITKARA UNIVERSITY - SCHOLARSHIP CELL
    MERIT SCHOLARSHIP APPLICATION NOTICE 2026-2027
    Deadline for submission: September 20, 2026
    Required Documents: Marksheet, Aadhaar Card, Bank Details
    """

    res = provider.analyze_document(ocr_sample)

    assert "September 20" in res.answer or "scholarship" in res.answer.lower()
    assert res.knowledge_cluster is not None
    assert res.knowledge_cluster.category == "document"
    
    attrs = res.knowledge_cluster.attributes
    assert "deadlines" in attrs
    assert "required_documents" in attrs
    assert len(attrs["required_documents"]) >= 2

def test_generic_document_extraction():
    provider = MockResearchProvider()
    ocr_sample = "General Office Memo: Please keep the conference room clean."
    res = provider.analyze_document(ocr_sample)

    assert res.answer is not None
    assert res.confidence >= 0.8
