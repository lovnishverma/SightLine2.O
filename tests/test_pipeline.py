"""Tests for IntelligencePipeline orchestration and graceful degradation.
"""

from unittest.mock import MagicMock
from src.insights.pipeline import IntelligencePipeline
from src.insights.router import IntelligenceRouter
from src.insights.client import InsightsClient
from src.insights.providers.mock import MockResearchProvider
from src.insights.exceptions import InsightsUnavailableError

def test_pipeline_local_execution():
    pipeline = IntelligencePipeline()
    speech, ui_data, decision = pipeline.execute(
        query="What color is this cup?",
        image_or_scene="A blue ceramic mug on a table."
    )
    assert decision.route == "LOCAL_VISION"
    assert "blue ceramic mug" in speech
    assert ui_data["route"] == "LOCAL_VISION"
    assert ui_data["sources_count"] == 0

def test_pipeline_research_execution():
    mock_provider = MockResearchProvider()
    client = InsightsClient(provider=mock_provider)
    pipeline = IntelligencePipeline(insights_client=client)

    speech, ui_data, decision = pipeline.execute(
        query="How do I operate this Bosch washing machine?",
        image_or_scene="A front-loading appliance.",
        ocr_text="Bosch Serie 6"
    )

    assert decision.route == "INSIGHTS_RESEARCH"
    assert "Bosch" in speech or "washing machine" in speech
    assert ui_data["route"] == "INSIGHTS_RESEARCH"
    assert ui_data["sources_count"] >= 1
    assert "sources" in ui_data

def test_pipeline_validation_strips_citations():
    pipeline = IntelligencePipeline()
    mock_res = MagicMock()
    mock_res.answer = "Turn the dial [1] to Eco mode [2] and press *start*."
    mock_res.query = "test"
    mock_res.entity = "device"
    mock_res.language = "en"

    validated = pipeline.validate(mock_res)
    assert "[1]" not in validated.answer
    assert "[2]" not in validated.answer
    assert "*" not in validated.answer
    assert "Turn the dial to Eco mode and press start." in validated.answer

def test_pipeline_graceful_fallback_on_failure():
    # Simulate broken client that always raises InsightsUnavailableError
    mock_client = MagicMock()
    mock_client.research.side_effect = InsightsUnavailableError("Network connection down")
    
    router = MagicMock()
    mock_decision = MagicMock()
    mock_decision.route = "INSIGHTS_RESEARCH"
    mock_decision.is_research = True
    mock_decision.extracted_entity = "Device"
    mock_decision.reason = "Research requested"
    router.route.return_value = mock_decision

    pipeline = IntelligencePipeline(router=router, insights_client=mock_client)
    speech, ui_data, decision = pipeline.execute(
        query="How do I operate this?",
        image_or_scene="A white microwave on a counter."
    )

    # Must NOT crash: returns polite voice message describing what it sees
    assert "Research is temporarily unavailable" in speech
    assert "microwave" in speech
    assert ui_data["route"] == "LOCAL_VISION"
