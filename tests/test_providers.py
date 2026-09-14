"""Tests for iNSIGHTS Research Providers (Mock and Live error handling).
"""

import pytest
from unittest.mock import patch, MagicMock
import urllib.error

from src.insights.providers.mock import MockResearchProvider
from src.insights.providers.live import InsightsLiveProvider
from src.insights.exceptions import (
    InsightsTimeoutError,
    InsightsUnavailableError,
    InsightsRateLimitError,
    InsightsAuthenticationError,
)

def test_mock_appliance_research():
    provider = MockResearchProvider()
    result = provider.research("How do I use quick wash on this Bosch machine?", entity="Bosch")
    
    assert "Bosch" in result.entity or "Bosch" in result.answer
    assert result.confidence >= 0.9
    assert len(result.sources) >= 1
    assert any("manual" in s.title.lower() or "bosch" in s.title.lower() for s in result.sources)
    assert result.knowledge_cluster is not None
    assert "programs" in result.knowledge_cluster.attributes

def test_mock_medicine_caution():
    provider = MockResearchProvider()
    result = provider.research("Tell me about this medicine paracetamol")
    
    assert "paracetamol" in result.answer.lower()
    assert any(w in result.answer.lower() for w in ["doctor", "pharmacist", "verify"])
    assert len(result.sources) >= 1

def test_mock_hindi_response():
    provider = MockResearchProvider()
    result = provider.research("Yeh machine kaise kaam karti hai?", entity="Bosch", language="hi")
    
    # Verify Devanagari characters in answer
    assert any('\u0900' <= c <= '\u097f' for c in result.answer)

def test_mock_document_analysis():
    provider = MockResearchProvider()
    result = provider.analyze_document("Chitkara University Scholarship Circular 2026. Deadline September 20.")
    
    assert result.knowledge_cluster is not None
    assert result.knowledge_cluster.category == "document"
    assert "September 20" in result.answer

@patch("urllib.request.urlopen")
def test_live_provider_timeout_exception(mock_urlopen):
    mock_urlopen.side_effect = TimeoutError("Connection timed out")
    provider = InsightsLiveProvider(timeout=0.1, max_retries=0)
    
    with pytest.raises(InsightsTimeoutError):
        provider.research("Test query")

@patch("urllib.request.urlopen")
def test_live_provider_401_auth_error(mock_urlopen):
    err = urllib.error.HTTPError("http://test", 401, "Unauthorized", {}, None)
    mock_urlopen.side_effect = err
    provider = InsightsLiveProvider(timeout=1.0, max_retries=0)
    
    with pytest.raises(InsightsAuthenticationError):
        provider.research("Test query")

@patch("urllib.request.urlopen")
def test_live_provider_429_ratelimit_error(mock_urlopen):
    err = urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None)
    mock_urlopen.side_effect = err
    provider = InsightsLiveProvider(timeout=1.0, max_retries=0)
    
    with pytest.raises(InsightsRateLimitError):
        provider.research("Test query")

@patch("urllib.request.urlopen")
def test_live_provider_500_unavailable_error(mock_urlopen):
    err = urllib.error.HTTPError("http://test", 500, "Internal Server Error", {}, None)
    mock_urlopen.side_effect = err
    provider = InsightsLiveProvider(timeout=1.0, max_retries=0)
    
    with pytest.raises(InsightsUnavailableError):
        provider.research("Test query")
