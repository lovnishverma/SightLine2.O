"""Tests for deterministic IntelligenceRouter.
Verifies proper separation between local perception and iNSIGHTS DeepSearch research.
"""

import pytest
from src.insights.router import IntelligenceRouter

@pytest.fixture
def router():
    return IntelligenceRouter()

def test_local_color_query(router):
    decision = router.route("What color is this shirt?")
    assert decision.route == "LOCAL_VISION"
    assert "visual observation" in decision.reason.lower()
    assert decision.confidence >= 0.9

def test_local_traffic_light_query(router):
    decision = router.route("Is the traffic light red?")
    assert decision.route == "LOCAL_VISION"
    assert decision.is_research is False

def test_local_spatial_query(router):
    decision = router.route("Where are my keys?")
    assert decision.route == "LOCAL_VISION"

def test_local_count_query(router):
    decision = router.route("How many people are in the room?")
    assert decision.route == "LOCAL_VISION"

def test_research_appliance_operation(router):
    decision = router.route("How do I operate this washing machine?")
    assert decision.route == "INSIGHTS_RESEARCH"
    assert decision.is_research is True
    assert "iNSIGHTS DeepSearch" in decision.reason

def test_research_manual_lookup(router):
    decision = router.route("Find the manual for this microwave.")
    assert decision.route == "INSIGHTS_RESEARCH"

def test_research_medicine_safety(router):
    decision = router.route("Tell me more about this medicine, is it safe?")
    assert decision.route == "INSIGHTS_RESEARCH"

def test_research_government_notice(router):
    decision = router.route("What does this government notice mean?", detected_text="Scholarship Circular 2026")
    assert decision.route == "INSIGHTS_RESEARCH"

def test_research_brand_detection(router):
    decision = router.route("What is this and what does it do?", detected_text="Bosch Serie 6 EcoSilence")
    assert decision.route == "INSIGHTS_RESEARCH"
    assert "Bosch" in decision.extracted_entity

def test_hindi_research_query(router):
    decision = router.route("Isko kaise use kare?")
    assert decision.route == "INSIGHTS_RESEARCH"

def test_explicit_mode_overrides(router):
    d1 = router.route("What is this?", explicit_mode="Research")
    assert d1.route == "INSIGHTS_RESEARCH"

    d2 = router.route("How do I operate this?", explicit_mode="Quick Glance")
    assert d2.route == "LOCAL_VISION"
