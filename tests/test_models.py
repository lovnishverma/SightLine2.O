"""Tests for data models and schema serialization.
"""

from src.insights.models import Source, EvidenceChunk, KnowledgeCluster, ResearchResult, RouteDecision

def test_source_model():
    s = Source(
        title="Official Manual",
        url="https://example.com/manual.pdf",
        source_type="manual",
        confidence_score=0.98,
        snippet="Turn dial clockwise."
    )
    d = s.to_dict()
    assert d["title"] == "Official Manual"
    assert d["url"] == "https://example.com/manual.pdf"
    assert d["source_type"] == "manual"

def test_knowledge_cluster():
    kc = KnowledgeCluster(
        entity_name="Bosch Washing Machine",
        category="appliance",
        attributes={"controls": "dial", "programs": ["Quick 15", "Cottons"]},
        verified_facts=["8kg capacity", "EcoSilence drive"]
    )
    d = kc.to_dict()
    assert d["entity_name"] == "Bosch Washing Machine"
    assert len(d["verified_facts"]) == 2
    assert d["attributes"]["controls"] == "dial"

def test_research_result_reliability():
    res = ResearchResult(
        query="Paracetamol",
        entity="Paracetamol",
        answer="Analgesic medicine",
        confidence=0.92,
        sources=[Source(title="NHS Guide", url="https://nhs.uk")]
    )
    assert res.source_count == 1
    assert res.is_reliable is True

    unreliable = ResearchResult(
        query="Unknown",
        entity="Unknown",
        answer="No info",
        confidence=0.4,
        sources=[]
    )
    assert unreliable.is_reliable is False

def test_route_decision():
    rd = RouteDecision(
        route="INSIGHTS_RESEARCH",
        confidence=0.95,
        reason="Manual lookup requested",
        extracted_entity="Bosch"
    )
    assert rd.is_research is True
    assert rd.to_dict()["extracted_entity"] == "Bosch"
